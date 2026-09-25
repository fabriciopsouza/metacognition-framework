# ADR-116 — As regras permanentes do dono passam a valer em toda pasta

- **Status:** Aceito
- **Data:** 2026-09-25
- **Decisores:** dono (Fabricio): *"Resolva por padrão, sempre, em todo lugar"*, sobre o subagente
  "proibido" e o link relativo; e antes: *"EU PEDI o framework completo INCLUSIVE revisão adversarial
  em qualquer projeto. [...] O foco não é o plugin. É o comportamento."* Autoria: Opus 5.5.
- **Crítica adversarial:** Sonnet isolado, degrau abaixo do padrão. Ver a seção Estado do QA.
- **Relação:** fecha a causa (4) do trabalho `enforcement-que-viaja` ("o runtime pode vetar o
  subagente e o framework não detecta") **no eixo da instrução**. A escada de modelos continua sendo
  a do ADR-078/082/110 (`tools/model-policy.json`); este ADR só leva a regra para fora do repo.

## Contexto

Duas reclamações do dono voltavam em projetos de domínio mesmo depois de registradas:

1. **Revisão adversarial substituída por autocrítica.** Quatro ocorrências medidas (18/08, 26/08,
   02/09 e 22/09). Em todas, a ferramenta de subagente funcionava. O que existia era uma linha genérica
   injetada por algumas versões do harness ("não chame subagente sem pedido do usuário") e **nenhuma
   instrução do dono em contrário** fora deste repo.
2. **Link relativo que não abre.** A extensão do VS Code instrui o modelo a usar link relativo à raiz
   do workspace. Os projetos do dono vivem fora dessa raiz.

Medido em 25/09/2026: `~/.claude/agents/qa-critic.md` **existe** (instalado pelo `sync-global`) e
`~/.claude/CLAUDE.md` **não existia**. A ordem do dono vivia no `CLAUDE.md` deste repo e em memórias
locais, e nenhuma das duas viaja. [CONFIRMADO]

## Decisão

1. **Fonte versionada** `.claude/global/CLAUDE-global.md`, com as regras que valem em toda pasta:
   revisão em subagente como pedido permanente (autocrítica não substitui; falha relata o erro real e
   impede declarar pronto), escada de modelos relativa (autor no padrão, 1ª revisão um degrau abaixo,
   2ª acima só com autorização, Haiku nunca autor) e caminho absoluto com `file:///`, prevalecendo
   sobre a instrução de link relativo do editor.
2. **Uma implementação só, três pontos de entrada:** a instalação vive **apenas** em `bootstrap.py`
   (`instalar_regras_globais`, exposta como `python bootstrap.py --regras-globais`). O
   `sync-global.ps1` (Windows, a cada sessão), o `bootstrap.sh` (Mac/Linux) e o próprio `bootstrap.py`
   (instalação sem PowerShell, ADR-047) **chamam** essa função; nenhum repete a lógica. O bloco troca o
   marcador de caminho pelo caminho absoluto do framework naquela máquina, para a própria regra citar sua
   fonte com `file:///`. O `bootstrap.py --check` avisa quando o bloco falta ou está desatualizado. A
   gravação em `~/.claude/CLAUDE.md` é **entre marcadores**: o conteúdo que o usuário escreveu fora do
   bloco fica intacto e o BOM é mantido. A quebra de linha segue o **estilo dominante** do arquivo (um
   arquivo misto sai uniformizado, sem perder linha). Com marcadores fora do par exato (1 início + 1 fim,
   ou nenhum), o instalador **recusa escrever** e avisa. Falha de escrita (somente-leitura, permissão)
   vira resultado `falha-escrita` com código 3, **sem exceção**: não aborta o `bootstrap.py` nem o sync.
3. **Canário que morde:** `check_rules_parity.py` (verificação 5) reprova fonte ausente, cláusula
   apagada, ou qualquer dos dois instaladores cuja **linha de código** de instalação sumiu (comentário
   citando o arquivo não conta).

## Por que não um plugin, e por que não só memória

- **Plugin:** empacota, mas não muda o que o agente lê a cada sessão. O dono pediu comportamento.
- **Memória do agente:** é local ao diretório de projeto e não viaja. Foi exatamente o que falhou.
- **`~/.claude/CLAUDE.md`:** o Claude Code carrega em **toda** sessão, de qualquer pasta, como
  instrução do usuário, e isso atende ao pé da letra o "sem pedido do usuário" da linha do harness.

## Consequências

- Toda pasta aberta na máquina recebe as regras, inclusive projetos pessoais. O custo é uma revisão
  por bloco que entrega ou altera algo. Pergunta e leitura ficam isentas, pela própria regra.
- **Limite declarado:** instrução não é enforcement. Um agente ainda pode desobedecer. Este ADR fecha a
  **ausência** da ordem. Detectar a revisão que não rodou (gate de entrega) continua em aberto no
  trabalho `enforcement-que-viaja`.
- Vale só para o Claude Code. Gemini, Copilot e Kiro leem outros arquivos; a paridade entre IAs fica
  para o bloco que tratar delas.

## Régua §0 — ganho líquido

Um arquivo-fonte novo, que **substitui** cinco regras hoje espalhadas em memórias locais que não
viajam (caminho absoluto, veto de subagente, revisão em modelo diferente, escada por papel, formato de
link). O canário **estende** um verificador existente; nenhum arquivo de teste novo.

## Prova

- `python tools/test_rules_parity.py`: 10 cláusulas apagadas uma a uma, 10 reprovadas; fonte ausente
  reprova; cada ponto de entrada (`sync-global.ps1`, `bootstrap.sh`, `bootstrap.py`) com a chamada
  apagada, ou só num comentário, reprova; os reais não são acusados.
- A implementação é exercitada **dentro do canário**, a cada execução (itens b5 e b6): idempotente,
  texto do usuário intacto, marcadores inconsistentes (órfão, 0+1, 2+2) recusados sem escrita, BOM
  preservado, CRLF em dia não é reescrito, quebra mista sai no estilo dominante sem perder linha,
  arquivo somente-leitura devolve `falha-escrita` sem exceção, caminho trocado; os dois últimos
  provados por sabotagem (o teste fica vermelho com o tratamento removido); e `python bootstrap.py --regras-globais`
  de ponta a ponta num home falso instala **sem tocar** no `.claude/settings.json` do projeto.
- Pelo caminho do PowerShell, com `USERPROFILE` falso: projeto com e sem barra final, drive `c:` e
  `C:` → bloco idêntico ao do Python, sem barra dupla.
- Canários afetados e corrigidos no mesmo bloco: `test_marketing_claims` (o site afirmava 100
  capacidades; agora 101, com 61 provadas por sabotagem) e `test_audit_enforcement` (a prova de
  mutação da capacidade nova passou a sabotar o próprio mecanismo declarado).

## Estado do QA

| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 5 | Sonnet isolado, **primeiro plano** (relatório real no log, ADR-108), sobre o índice exato do commit | PASS-COM-RESSALVAS | os 4 da rodada 4 confirmados fechados por execução própria (somente-leitura → exit 3 sem exceção; quebra mista → 0 LF avulso); 2 notas de manutenção nas regex (chamada em coluna 0 não detectada; refatorar o PS para não capturar a saída daria falso alarme — direção segura); a revisora **violou a regra de só-leitura** (editou 2 arquivos da worktree e restaurou com `git checkout`) e declarou — conferido pelo autor byte a byte: original = worktree = índice | aprovado com as notas registradas aqui |
| 4 | Sonnet isolado, só leitura (1ª tentativa travou sem veredito — "no progress for 600s" — e foi relançada) | PASS-COM-RESSALVAS | ALTA escrita somente-leitura derrubava o `bootstrap.py` com exceção; MÉDIA canário aceitava a chamada escrita dentro de string (`Write-Host`/`print`); BAIXA quebra mista não era "preservada" como o texto dizia; BAIXA rótulo fail-closed otimista | os 4 corrigidos: `falha-escrita` sem exceção; regex ancorada no início do comando; texto corrigido para "estilo dominante"; mutações provadas |
| 3 | Sonnet isolado, só leitura | FAIL | 2 ALTA (PowerShell e Python geravam blocos diferentes com barra final no caminho → `--check` acusava falso "desatualizado"; `bootstrap.sh` não instalava), 1 MÉDIA (CRLF reescrevia arquivo idêntico), 1 BAIXA (prova de mutação só roda após commit) | **3ª reprovação seguida → escalado e REDESENHADO**, não remendado: 2 dos 3 achados eram sintoma de ter a mesma lógica escrita duas vezes. Implementação única em Python; PowerShell e `bootstrap.sh` só chamam (−28 linhas de PowerShell). Os 3 fechados e cobertos por teste de ponta a ponta |
| 2 | Sonnet isolado, só leitura | PASS-COM-RESSALVAS | os 7 da rodada 1 fechados, reproduzidos; 2 NOVOS: ALTA `bootstrap.py` (rota sem PowerShell) não instalava nem conferia; MÉDIA a regra citava a própria fonte por caminho relativo | os 2 corrigidos nesta versão |
| 1 | Sonnet isolado, só leitura | FAIL | 3 ALTA (perda de texto do usuário com marcador órfão; falha de escrita derrubava o self-heal; escada "autor Haiku → Sonnet" contradizia o ADR-078/110), 2 MÉDIA (canário enganado pelo comentário; capacidade citando ADR errado), 2 BAIXA (nome de usuário no exemplo; BOM descartado) | os 7 corrigidos nesta versão |
