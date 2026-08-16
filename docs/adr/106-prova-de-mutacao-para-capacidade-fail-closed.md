# ADR-106 — Prova de mutação para capacidade `fail-closed`: verde só conta depois de saber ficar vermelho

- **Status:** Aceito
- **Data:** 2026-08-14
- **Decisores:** dono (Fabricio), após auditoria de um gate num projeto que usa o framework
- **Tipo:** **EMENDA** ao `docs/adr/015-enforcement-executavel-fail-closed.md` — o ADR-015 exigiu
  que enforcement fosse executável; esta emenda exige que a **execução seja verificada**.
- **Relaciona:** ADR-072 (índice de capacidades), ADR-077 (ledger de evidência), ADR-096
  (primeiro uso de prova por mutação, sem institucionalizar), rule **#12** do `qa-critic`.

## Contexto — a mesma falha, três vezes, e a técnica já estava na casa

O ADR-015 estabeleceu que enforcement sem mecanismo é prosa. Ele não previu o degrau seguinte:
**mecanismo cujo teste não sabe reprovar** também é prosa — só que com um número verde na frente,
o que é pior, porque produz confiança.

Três ocorrências confirmadas, o bastante para o critério de rule nova do `qa-critic`:

| # | onde | o que aconteceu |
|---|---|---|
| 1 | **ADR-096, achado A2** (2026-07) | o canário aferia só o `returncode`, nunca o `stdout`; a mutação que removia `hitl_requerido` do JSON **passava** |
| 2 | **v1.79.0** (2026-08) | o canário fazia *monkeypatch da própria função* que deveria testar e ficava verde com a extração quebrada — 3 defeitos passaram por ali |
| 3 | **projeto externo `agente-copilot-studio`** (2026-08-14) | um teste que anunciava *"9/9 — o gate BLOQUEIA mesmo"* continuou **9/9 com toda a lógica do gate apagada**, porque conferia só `rc != 0` e outra checagem já derrubava o processo |

O ADR-096 registra, com todas as letras, *"provado por mutação"*. **A técnica foi usada, funcionou,
achou defeito real — e nunca virou exigência.** Ficou como boa prática de um bloco. Esta emenda não
inventa nada: institucionaliza o que já sabíamos fazer e paramos de fazer.

O passivo medido em 2026-08-14, antes desta emenda: **80 capacidades, 35 sem nenhum campo
`enforcement`, 22 declaradas `fail-closed` sem que ninguém jamais tivesse verificado que o canário
correspondente sabe ficar vermelho, e zero ferramentas cruzando declaração com realidade.**

## A decisão

**Capacidade que declara `enforcement: fail-closed` declara também a mutação que faz o canário dela
falhar** — em campos executáveis por máquina (`arquivo`, `de`, `para`, `canario`), não em prosa.
O auditor aplica a mutação num worktree isolado e **exige** que o canário fique vermelho.

Três exigências:

1. **Prova de mutação.** Canário que continua verde sob mutação não sustenta capacidade.
2. **Falha pelo motivo certo.** O teste confere a mensagem ou o código específico, nunca só
   "saiu diferente de zero". Sem isso, duas falhas distintas se confundem e uma mascara a outra —
   foi exatamente o mecanismo da ocorrência #3.
3. **Declaração honesta.** `prose` e `advisory` são valores legítimos; o que não se admite é
   descrever como vinculante o que está marcado assim.

### Escopo — a divisão que o dono decidiu

| modo | a quem se aplica | efeito |
|---|---|---|
| **(a) fail-closed** | capacidade **nova** — id fora do baseline congelado | sem `mutacao` declarada, o auditor sai 1 e barra |
| **(b) advisory** | as 80 do passivo, congeladas em `_meta/enforcement-baseline.json` | relatório por `--passivo`; não barra o CI |

A divisão existe porque a alternativa — fail-closed retroativo — reprovaria 57 capacidades de uma
vez e o time desligaria o auditor no primeiro dia. Passivo migra por decisão, não por susto.

## Emenda 1 (2026-08-15 — a exigência 2 estava no texto e não no código)

Ao começar a migrar o passivo, a primeira coisa medida foi o próprio auditor. Resultado:

    # mutação que só quebra a sintaxe do mecanismo, sem tocar na lógica do gate
    de:   "import argparse"    para: "imprt argparse"
    → [PROVADO] mutacao em tools/risk_score.py deixou tools/test_risk_score.py vermelho

O auditor conferia **apenas o código de saída**. É a ocorrência #1 da tabela de contexto deste
mesmo ADR — *"o canário aferia só o `returncode`"* — reencarnada dentro do mecanismo criado para
combatê-la. A exigência 2 ("falha pelo motivo certo") estava escrita na decisão e **não existia
em código**: prosa dentro do ADR que institui o fim da prosa.

**O que muda.** `mutacao` ganha um quinto campo obrigatório, `espera`: a mensagem que a saída do
canário tem de conter **depois** da sabotagem. A prova passa a exigir três coisas, não uma:

1. o canário está **verde antes** da mutação;
2. fica **vermelho depois**;
3. com a mensagem de `espera` na saída — e essa mensagem **não podia já aparecer antes**, senão
   bastaria declarar uma palavra do cabeçalho e a checagem seria vazia.

Mais uma recusa explícita: **vermelho por crash não é prova**. Se o canário morre ao carregar o
arquivo sabotado (`SyntaxError` e afins citando o próprio arquivo), a prova é inválida. Quebrar um
arquivo não demonstra que o gate detecta coisa alguma — demonstra que Python não lê código inválido.

**Custo da migração:** uma linha. Só uma capacidade tinha `mutacao` quando a emenda foi escrita —
o próprio `enforcement-mutation-audit`. As outras 22 `fail-closed` do passivo entram já sob a
regra nova, o que é a razão de a emenda vir antes da migração e não depois.

**Cobertura:** `tools/test_audit_enforcement.py` passa de 19 para 23 verificações, com um caso
nomeado para cada nova recusa — sem `espera`, `espera` que já aparecia antes, vermelho pelo motivo
errado, e vermelho por crash. O caso do crash exige uma fixture em que o canário **importa** o
mecanismo; com a fixture antiga, que só lia o arquivo como texto, a sabotagem de sintaxe não
matava ninguém e o caso não seria falsificável.

## Emenda 2 (2026-08-15 — a recusa de crash não valia para mecanismo que não é Python)

Reprovada pelo qa-critic (Sonnet isolado, autor Opus), dois achados ALTOS, ambos reproduzidos:

1. **A recusa de "vermelho por crash" exigia o nome do arquivo no traceback.** Mecanismo `.json`
   ou `.md` quebra com `JSONDecodeError`, cujo traceback cita `json/decoder.py` e **nunca** o
   arquivo de dados. A recusa não disparava e o crash passava como prova. Não era hipotético:
   `model-policy` tem mecanismo `tools/model-policy.json`.
2. **Nada validava o conteúdo de `espera`.** Declarar `espera: "Error"` casa com o texto de quase
   toda exceção. Somado ao achado 1, devolvia `[PROVADO]` para exatamente a fraude da Emenda 1.

**O que muda.** Crash passa a ser detectado por **delta** — marca que aparece depois e não
aparecia antes —, sem depender do nome do arquivo. E `espera` ganha piso de 12 caracteres e é
proibida de conter sinal de crash: o campo declara a mensagem que o gate imprime ao **detectar**,
não a exceção que ele levanta ao engasgar.

**Limitação aceita** (achado MÉDIO do mesmo crítico): capacidade cujo gate sinaliza legitimamente
por `ImportError` fica improvável por este auditor. É falso-negativo, lado seguro, registrado e
não mascarado.

## Emenda 3 (2026-08-15 — a prova era anulável por cache de bytecode, de forma intermitente)

Achado durante a migração, medido e não suposto. `autonomy-retry-policy` foi recusado com
*"o canário continuou VERDE"* — mas a mesma sabotagem, aplicada à mão no mesmo worktree, deixava
o canário **vermelho**.

**Causa.** O Python decide reusar um `.pyc` comparando **tamanho** e **horário** do fonte, e o
horário tem resolução de **um segundo**. A execução "antes" compila o mecanismo; se a sabotagem
for gravada dentro do mesmo segundo **e** mantiver o mesmo número de bytes, o interpretador roda o
bytecode velho — o código sabotado nunca executa. A mutação testada trocava a ordem de quatro
nomes numa lista: 48 bytes antes, 48 bytes depois.

Prova determinística, congelando o `mtime` com `os.utime` para simular o mesmo segundo:

    cache ligado    → canário VERDE   (prova perdida)
    cache desligado → canário VERMELHO (correto)

**Gravidade.** A prova era **intermitente**: dependia de a máquina ganhar ou perder a corrida do
relógio. Prova que funciona às vezes é pior que prova ausente, porque parece funcionar. O
mecanismo criado para impedir que "verde" signifique nada estava sendo enganado por um verde falso.

**O que muda.** Duas travas, porque uma só seria confiança: `PYTHONDONTWRITEBYTECODE=1` nas duas
execuções do canário, e purga de todo `__pycache__` do worktree antes da execução sabotada.

**Cobertura:** 26 → 28 verificações. Uma exercita mutação do mesmo tamanho em mecanismo
**importado** — a fixture `x.py` nunca pegou esta classe porque **lê** o arquivo como texto, e
cache de bytecode só afeta importação. A outra confere as duas travas de forma determinística,
porque a primeira só reprova quando a corrida é perdida, e canário que depende de sorte não é
canário.

**Achado colateral, não corrigido aqui.** O mesmo cache derrubou `test_autonomy_policy` na árvore
principal com o fonte **idêntico ao commit** — o `.pyc` guardava o bytecode de uma sondagem.
Qualquer canário da suíte pode reportar verde ou vermelho por cache velho, não só os deste
auditor. Fica como pendência nomeada, para decisão do dono.

## Emenda 4 (2026-08-16 — o mesmo defeito valia para a suíte inteira, e o executor não tinha canário)

A emenda 3 fechou o cache de bytecode **dentro** do auditor. O achado colateral que ela deixou
registrado — *"qualquer canário da suíte pode reportar verde ou vermelho por bytecode velho"* —
foi fechado aqui, junto com uma lacuna maior: **`run_canaries.py`, que decide PASS/FAIL dos 67
canários, não tinha canário próprio**.

**Duas correções foram reprovadas pelo canário novo antes de a terceira valer:**

1. `PYTHONDONTWRITEBYTECODE=1`. Reprovada: impede **escrever**, não impede **ler** um `.pyc`
   pré-existente. Era a ressalva MÉDIA da emenda 2, levantada como suspeita pelo crítico e aqui
   confirmada por execução.
2. Proibir escrita **e** apontar `PYTHONPYCACHEPREFIX` para um diretório vazio. Correta e cara:
   cada subprocesso recompilava a biblioteca padrão inteira, e a suíte saltou de **72s para mais
   de dois minutos**.
3. A que ficou: prefixo **novo por execução da suíte**, com escrita liberada. Nada de antes pode
   ser lido; o custo é pago uma vez. Suíte **72s → 76s**, 5%.

A mesma correção completa voltou para o `audit_enforcement.py`, fechando a ressalva MÉDIA da
emenda 2.

**O canário se corrigiu duas vezes.** Passava sozinho e reprovava dentro da suíte, porque
herdava o ambiente já corrigido do executor — media o chamador, não o código. E a sabotagem
declarada da capacidade nova era **neutralizada pelo próprio auditor**: ela lia a variável de
ambiente que o auditor define, então o isolamento continuava em pé. Sabotagem que depende do
ambiente de quem a aplica não é sabotagem.

**Cobertura:** capacidade `canary-runner-bytecode-isolation`, 5 verificações, com o caso central
**comportamental e determinístico** — monta a corrida de propósito (mesmo tamanho, `mtime`
congelado) e exige que o ambiente do executor detecte o que o ambiente padrão deixa passar.
Registro de capacidades 81 → 82; com gate provado 24 → 28.

## Alternativas consideradas

- **Fail-closed para tudo, já.** Rejeitada: 57 reprovações imediatas, incluindo o
  `squad-enforcement-gate`, que está em disputa no v1.79.0. Norma que ninguém consegue cumprir vira
  norma que todo mundo contorna.
- **Só relatório periódico (modo b para tudo).** Rejeitada como regime único: volta a depender de
  alguém lembrar, que é precisamente como esta dívida nasceu. Fica valendo apenas para o passivo.
- **Cobertura de teste como métrica.** Rejeitada: cobertura mede linha executada, não defeito
  detectado. Um canário que executa a linha e não confere o resultado tem 100% de cobertura e zero
  poder — é literalmente a ocorrência #1.

## Como isto pode virar teatro — e a salvaguarda

Levantado pelo crítico adversarial desta rodada, e é o risco central: *"prova que bloqueia"* pode
ser operacionalizada como *"N/N verde no canário"* — e acabamos de reproduzir 9/9 verde com a lógica
central apagada. Um autor sob pressão satisfaz a **letra** citando o ledger sem satisfazer o
**espírito**, porque ninguém audita o auditor.

**Salvaguarda:** a evidência aceita não é o número verde. É o **par** *(mutação aplicada, canário
vermelho)*, executável e reproduzível por terceiro. O auditor recusa seis formas de fraude. Cada
uma tem caso de teste nomeado em `tools/test_audit_enforcement.py` — a lista abaixo foi escrita
**depois** de os testes existirem, não antes:

| fraude | caso de teste |
|---|---|
| mutação que não sabota nada (`de` == `para`) | *"`mutacao` com `de` == `para`"* |
| mutação **obsoleta** — o trecho `de` já não existe, logo nunca foi aplicada | *"mutacao obsoleta e' acusada"* |
| canário que já estava vermelho **antes** da mutação, caso em que a prova não diz nada | *"canario ja vermelho ANTES da mutacao e' acusado"* |
| mutação apontando para arquivo que **não é o mecanismo** da capacidade — provaria outra coisa | *"`mutacao.arquivo` diferente do `mechanism` declarado"* |
| canário declarado na mutação diferente do `test` da capacidade | *"`mutacao.canario` diferente do `test` declarado"* |
| capacidade que **omite** `mechanism`/`test`, desligando o cross-check em silêncio | *"`fail-closed` sem `mechanism`/`test` declarados"* |

**Como a rodada 1 deste próprio ADR caiu na armadilha.** A versão inicial afirmava três fraudes
*"cada uma coberta por caso de teste"* — e a terceira **não tinha teste**. O crítico adversarial
sabotou aquela checagem no auditor e o canário seguiu 12/12 verde. A afirmação tinha vindo antes da
verificação: exatamente o defeito que este ADR institui norma para impedir, cometido no texto que o
institui. Fica registrado porque o caso é a melhor evidência de que a norma é necessária.

**Segundo vetor, mais óbvio que os seis acima: mexer no passivo.** Bastaria acrescentar o próprio
id à lista de `_meta/enforcement-baseline.json` para a capacidade nova virar "herdada" e escapar do
modo (a). Mitigado por **pino**: `tools/test_audit_enforcement.py` fixa a contagem e o `sha256` dos
ids do passivo; alterar a lista quebra o canário e exige atualizar o pino no mesmo commit, com
motivo. Migração de passivo passa a ser decisão declarada, não edição silenciosa.

## Consequências

**Positivas.** O índice de capacidades passa a distinguir o que prende do que apenas se anuncia.
A rule #12 dá ao `qa-critic` um critério binário onde antes havia julgamento.

**Negativas, declaradas.** O índice encolhe antes de crescer: 57 capacidades entram como passivo
reconhecido. Toda capacidade nova custa mais — escrever a mutação e prová-la. O modo `--provar`
opera sobre o **HEAD commitado**, não sobre a árvore de trabalho: capacidade recém-escrita e ainda
não commitada não é provável, por desenho. E se o processo morrer no meio de uma prova, resta um
worktree órfão — mitigado com `git worktree prune` antes de cada execução, não eliminado.

**Régua §0 (ADR-007) — override explícito, não porta.** Este bloco **adiciona** três arquivos e não
funde nem remove nada; não reduz tokens nem latência. Nenhuma das portas (a)/(b)/(c) se aplica, e
alegá-las seria a racionalização que o ADR-099 cometeu. Segue por **override do dono**, declarado em
2026-08-14 ao aprovar a divisão (a)/(b). **Condição de quitação:** o override se quita quando o
passivo for migrado — cada capacidade herdada ou ganha `mutacao` provada, ou é rebaixada ao
`enforcement` que de fato tem. Enquanto isso não ocorrer, o bloco é dívida reconhecida, não entrega
fechada.

**O que esta emenda NÃO mecaniza.** A exigência 3 (declaração honesta) segue sem auditor: nada
impede, hoje, o `CAPABILITIES.md` descrever como vinculante uma capacidade marcada `advisory`.
Fica registrado como pendência, não como entrega.

## Artefatos

- `tools/audit_enforcement.py` — auditor. Modos `--declaracao` (padrão), `--passivo`, `--provar`.
- `tools/test_audit_enforcement.py` — canário, **19 verificações**. Além das fixtures, ele roda o
  auditor contra o `capabilities.json` **real** e pina o passivo — é essa chamada que transforma o
  modo (a) em gate de CI (via `tools/run_canaries.py`) em vez de script que alguém precisa lembrar
  de rodar. Traz também a **prova de mutação de si mesmo**.
- `_meta/enforcement-baseline.json` — passivo congelado (80 ids).
- `.agent/skills/qa-critic/rules.md` — rule #12.
- Dívida de origem: `docs/_private/handoffs/2026-08-14-divida-gate-que-nao-barra-nao-conta.md`.

## Pendências

- Migrar o passivo: 35 capacidades sem `enforcement` e 22 `fail-closed` sem `mutacao`.
- Mecanizar a exigência 3 (coerência entre o adjetivo no índice e o campo `enforcement`).
- Revisão adversarial deste bloco por modelo diferente do autor — **não realizada até o registro**.
