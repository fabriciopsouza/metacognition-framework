# ADR-120 — Biblioteca de conhecimento: método de construir e consultar, modelo e verificador

- **Status:** Aceito
- **Data:** 2026-09-26
- **Decisores:** dono (Fabricio). Plano B3, decisão D9 (26/09). Pedido de 26/09 de consultas reutilizáveis entre
  projetos (débito DB1), com respostas D1–D6. Ordem de 26/09: "siga no plano", depois de o autor apontar que o
  DB1 duplicava o D9. Ordem de 26/09: trabalhar só no agnóstico ("o MÉTODO"). Autoria: Opus 5.5.
- **Relação:** executa o B3e do plano `docs/specs/b3-documentacao-regulada/spec.md` (REQ-16 a REQ-18,
  critérios 17 a 19). Reusa o `knowledge_catalog` (ADR-068, BM25), o arquivo único (ADR-117), o banco de dimensões
  (ADR-033) e a regra global (ADR-116). Quita o débito DB1 (`docs/_backlog/gaps-otimizacao.md`) na parte agnóstica.

## Contexto

1. Consultas, fatos medidos e termos confirmados num projeto eram refeitos em outro, porque cada um vivia só na
   pasta do projeto que o criou.
2. O D9 já tinha aprovado um dicionário por perfil, empresa e projeto, com relações e índice de projetos.
3. "Consultar antes" escrito como prosa não segura, e o framework tem casos registrados disso.
4. O framework já tem uma busca (`knowledge_catalog`); uma segunda criaria duas respostas para a mesma pergunta.

## Decisão

1. **Modelo agnóstico** em `exemplos/conhecimento/_modelo/`, com a estrutura:
   - `perfis/<p>/DICIONARIO.md`;
   - `empresas/<e>/DICIONARIO.md`;
   - `empresas/<e>/<área>/<assunto>.md`;
   - `INDICE-PROJETOS.md`;
   - `conhecimento.json`.

   Entrada é um bloco `## <nome>` com campos fixos. Os tipos são termo, consulta, fato, pesquisa e runbook. O
   README do modelo é o método (POP), com as seções consultar, construir e quando refazer.
2. **Validade por classe:**
   - estrutura: até mudar a versão do sistema declarada em `conhecimento.json`;
   - configuração: 6 meses;
   - regra de negócio e conceito: 12 meses;
   - retrato (número medido): não vence e é citado sempre com a data;
   - qualquer classe: **Contestado em:** vira "a reverificar" na hora.
3. **`tools/conhecimento.py`:**
   - `verificar` acusa: campos obrigatórios por tipo; data inválida ou no futuro; confiança "CONFIRMADO" sem quem;
     relação de tipo desconhecido ou para termo inexistente; termo em dois níveis ou repetido; estrutura sem
     sistema e versão, ou com versão atual não declarada; consulta sem texto pronto; formato não reconhecido;
     arquivo fora da estrutura; ponteiro para caminho inexistente; credencial ou documento de identificação;
     índice com caminho inexistente; projeto com trabalho aberto em `trabalhos.py` sem linha no índice;
   - `vencidos` lista o que deve ser refeito.
4. **Uma busca só:** `knowledge_catalog --recall --conhecimento <raiz>` lê a biblioteca ao vivo. Sem a opção, nada é
   carregado. Retrato sai com "em dd/mm/aaaa:".
5. **Método nas peças existentes:**
   - discovery, item 0: consultar antes; perguntar empresa e perfil; termo confirmado entra no ato;
   - docops, passo 7: registrar ao fechar o bloco, ou declarar "nada a registrar";
   - regra global, seção 9, com 2 cláusulas novas no `check_rules_parity`;
   - regra global, seção 6: comando permanente `status` (tabela checklist com % por bloco + 3 linhas),
     pedido repetido do dono em 26/09, mais 1 cláusula (19 no total);
   - dimensão `biblioteca-consultada` no banco com `obr=unico`: obrigatória só no arquivo único de especificação.
     O formato antigo não muda de veredito, e ninguém inventa resposta para especificação anterior à regra.
6. **Instância do dono:** `docs/_private/conhecimento/` (D9), criada vazia de conteúdo. O conteúdo é das sessões de
   domínio.

## Alternativas descartadas

- Plano e estrutura próprios para consultas (primeira versão do DB1): duplicava o D9.
- `conhecimento.py buscar`: segunda busca ao lado do `knowledge_catalog`.
- Dimensão `biblioteca-consultada` obrigatória em todo formato: reprovaria especificações anteriores à regra, e a
  saída seria preencher com texto de exceção copiável.
- Validade só por tempo: não pega mudança de sistema nem contradição.

## Régua §0

Critério (c): o banco de dimensões e o `knowledge_catalog`, que já existiam, passam a medir o que era prosa. Critério
(a): o DB1 foi fundido ao B3e em vez de virar plano e estrutura próprios. Adiciona 1 verificador e 1 canário.

## Prova

- `tools/test_conhecimento.py`: modelo passa; 34 sabotagens reprovam com o achado esperado (6 delas vindas das
  rodadas 1 e 2 do QA); 8 exceções legítimas passam (valor em R$, campo dentro de bloco de código, prosa que
  descreve um campo chamado "token", sub-título só com texto, campo depois do bloco de código da consulta, índice
  com caminho existente, trabalho tratado, trabalho do próprio framework); biblioteca vazia responde "nada
  encontrado" sem erro; vencidos por versão, por prazo e por contestação; retrato não vence; busca devolve a entrada
  com a data; sem `--conhecimento` nada é lido; modelo e verificador sem termo de domínio.
- Mutação do verificador e da busca (script de sessão, não versionado): 38 mutações, 38 mortas. As 2 que
  sobreviveram na primeira passada levaram a um caso novo no canário e à remoção de uma linha redundante.
- `tools/test_spec_unico.py` caso (j): arquivo único sem `biblioteca-consultada` reprova; formato antigo não; a
  equivalência (a)/(b) compara só o contrato comum.
- `tools/test_spec_depth.py`, `tools/test_discovery_eval.py`, `tools/test_knowledge_catalog.py`,
  `tools/test_rules_parity.py` (19 cláusulas), `tools/check_core_agnostic.py`: PASS.

## Limites

- Campos fixos tornam a biblioteca legível por máquina; relações entre termos são as 5 do D9. Não é uma ontologia
  formal.
- O verificador prova forma, rastro e validade, não a verdade do conteúdo.
- Credencial: pega "chave: valor" no fim da linha (com comentário ou anotação), parâmetro de URL e cabeçalho de
  autorização. Segredo no meio de uma frase comum escapa. Afrouxar mais acusaria a prosa que descreve campos.
- A checagem cruzada com `trabalhos.py` acusa todo projeto de domínio com trabalho aberto enquanto o índice estiver
  vazio. É a pendência de preenchimento, das sessões de domínio.
- "Consultar antes" é cobrado pela dimensão só no arquivo único. Em conversa sem especificação, continua sendo
  regra (seção 9 da regra global).

## Estado do QA

| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 3 | Sonnet isolado, segundo plano (a1c73b1fdf84cdf66) | PASS | nenhum: correções da rodada 2 reproduzidas; rodada 1 não reaberta; sem falso positivo de credencial em prosa ("o campo senha: definido pelo usuário (obrigatório)", "token: veja o manual # seção 3") | — |
| 2 | Sonnet isolado, segundo plano (ab523c78962d0b793) | PASS-COM-RESSALVAS | as 6 correções da rodada 1 confirmadas. 1 ALTA nova: campo depois do bloco de código da consulta era acusado e descartado (falso positivo criado pela correção da rodada 1). 1 MÉDIA: "senha: abc123 (trocar)" e "Authorization: Bearer" escapavam | só prosa marca o corpo (código não); credencial aceita comentário/anotação à direita e cabeçalho de autorização; limite declarado; 3 casos novos |
| 1 | Sonnet isolado, primeiro plano (ae8eb988d9d5e2a16) | PASS-COM-RESSALVAS | 2 ALTA: campos antes do 1º `##` sumiam sem achado; entrada com `###` se fundia à anterior. 3 MÉDIA: prosa "o campo token: armazena…" acusada como credencial; rótulo "9/9" no arquivo único com 10 obrigatórias; busca com biblioteca vazia dava erro e mandava rodar `--build`. 1 BAIXA: caminho relativo na seção 9 da regra global | campos no topo da entrada, campo depois do corpo e campo antes do 1º `##` acusados; credencial = valor único no fim da linha ou parâmetro de URL; contagem por especificação; biblioteca vazia responde "nada encontrado" (exit 0); `{{FRAMEWORK_ROOT}}` na seção 9. 6 casos novos no canário |

## Emenda 1 — isolamento entre empresas (27/09/2026)

- **Status:** Aceita nos itens a–e do pedido do dono; decisões D1–D5 pendentes (`docs/specs/isolamento-empresas-biblioteca/spec.md`).
- **Origem:** pedido do dono de 27/09/2026, com a regra: "conhecimento de uma empresa (processo, centros, códigos,
  valores, consultas, nomes) nunca aparece no trabalho de outra. Só o saber puro de assunto pode ser compartilhado".
- **Problema:** `--recall` e `verificar` liam a raiz inteira; relações resolvidas num dicionário global; caminho de
  outra empresa, guardado em outra máquina, reprovava a biblioteca de quem trabalhava.

### Decisão
1. **Camada `assuntos/<assunto>/`** (`DICIONARIO.md` e `<tema>.md`), compartilhada, sem dado de empresa.
2. **Recorte por empresa** em `conhecimento.py verificar | vencidos` e `knowledge_catalog --recall`:
   - `--empresa <e>` lê só `empresas/<e>/`, `assuntos/` e `perfis/`; os arquivos de outra empresa não são abertos;
   - `--empresa nenhuma` lê só `assuntos/` e `perfis/`; `--empresa todas` é a manutenção;
   - sem `--empresa`, vale o projeto do `INDICE-PROJETOS.md` cujo Caminho contém o diretório atual: o mais
     específico, com separador de pasta, sem diferença de maiúsculas;
   - sem projeto, ou com projetos de duas empresas no mesmo caminho, o comando RECUSA (exit 2) sem ler nada.
3. **Relações e caminhos:**
   - empresa aponta para a própria, para assunto e para perfil;
   - assunto e perfil não apontam para empresa;
   - relação para termo de outra empresa e caminho de projeto de outra empresa são achados bloqueantes;
   - a mensagem não cita a outra empresa;
   - o mesmo termo em duas empresas não é achado.
4. **`assuntos/` sem dado de empresa.** Reprovam:
   - nome de empresa presente;
   - **Valores:** da entrada `## Identificadores` (tipo novo, só no DICIONARIO.md da empresa, fora da busca);
   - caminho e repositório de projeto do índice;
   - objeto Z*/Y*, campo ZZ*/YY*, tipo de movimento 9xx ou X/Y/Z com rótulo, caminho de usuário.

   O valor de empresa fora do recorte não aparece na mensagem.
5. **Fica no recorte:**
   - caminhos do índice conferidos só nas linhas da empresa;
   - trabalho aberto sem linha no índice só na manutenção (a mensagem traz o nome do repositório);
   - `empresas/<e>/conhecimento.json` opcional, com as versões de sistema da empresa, que prevalece sobre o da raiz.

### Limites
- **Filtro não é isolamento físico:** a biblioteca inteira continua no repositório clonado em toda máquina (D1).
- **Empresa ausente da máquina:** o verificador de `assuntos/` só conhece as empresas presentes nela (D2). Os padrões
  de cliente valem em qualquer máquina.
- A lista de palavras comuns em maiúsculas que não são objeto de cliente não é exaustiva. Objeto de cliente escrito
  em minúsculas escapa.
- **Relatórios de sessão:** entram no `--recall` sem recorte (D3).
- **Identificador de empresa:** precisa de 4 ou mais caracteres, ou de um dígito, para não reprovar sigla de módulo
  ("MM"). Um código real de 3 letras sem dígito (ex.: "ABC") não é protegido em `assuntos/`; declare um alias mais
  longo.
- **Pasta com maiúscula:** é achado. Enquanto não for renomeada, em sistema de arquivos que diferencia maiúsculas o
  `conhecimento.json` próprio da empresa não é encontrado e vale o da raiz, nunca o de outra empresa.

### Prova
- `tools/test_conhecimento_isolamento.py`, com duas empresas falsas, alfa e beta.
- `tools/test_conhecimento.py`, com os comandos atualizados.
- Suíte completa: 95 PASS, 1 SKIP, 0 FAIL de 96.

## Emenda 2 — isolamento físico, identificadores em hash e relatórios (27/09/2026)

- **Status:** Aceita.
- **Decisores:** dono (Fabricio), 27/09/2026:
  - D1, D2, D3 e D5 do plano do isolamento: "todas a";
  - forma da separação: "b", repositório-pai com submódulo por empresa (`conhecimento-negocio`);
  - Vibra: "e o mesmo para o conhecimento vibra, quando ocorrer".

### Decisão
1. **D1:** a biblioteca de cada empresa sai do framework para um repositório privado próprio, submódulo
   `empresas/<empresa>` do repositório privado `conhecimento-negocio`.
   - Em cada máquina, só o submódulo da empresa daquela máquina é inicializado.
   - O framework acha a biblioteca pelo marcador `.conhecimento-empresa`, nas pastas de `"bibliotecas"` do
     `conhecimento.json` da raiz; pasta ausente é ignorada.
   - O índice e a versão de sistema da empresa vão junto com ela.
   - A Natulab foi movida para `conhecimento-natulab`; a Vibra segue o mesmo caminho quando houver conteúdo dela.
2. **D2:** `conhecimento.py publicar --empresa <e>` grava em `assuntos/_identificadores/` o sha256 dos identificadores
   da empresa.
   - Em `assuntos/`, token cujo hash está na lista de uma empresa ausente da máquina reprova, sem mostrar o valor.
   - O `verificar` acusa lista não publicada ou desatualizada.
3. **D3:** no recorte de uma empresa, o `--recall` omite relatório de sessão que cita outra empresa (nome, identificador
   em claro ou em hash).
4. **D5:** a versão do S/4HANA da Natulab saiu da raiz para o `conhecimento.json` da biblioteca dela.

### Limites
- **Histórico:** o git do framework ainda tem a Natulab nos commits anteriores a 27/09. Tirar exige reescrever o
  histórico com push forçado: decisão do dono.
- **Hash:** identificador curto (4 dígitos) é adivinhável por força bruta. O hash impede a leitura casual, não um
  ataque. Identificador de várias palavras só é pego palavra a palavra.
- **Filtro de relatório:** depende da lista de identificadores publicada; relatório que cita a empresa por
  apelido escapa.
- **Caminho relativo:** `"bibliotecas"` supõe o repositório-pai como pasta irmã do framework; em worktree do
  framework noutro lugar, a biblioteca externa não é achada. Nesse caso o `verificar --empresa <e>` reprova
  ("biblioteca não encontrada nesta máquina") e o `--recall` avisa que só leu assuntos e perfis.

### Prova
- `tools/test_conhecimento_isolamento.py`:
  - biblioteca externa achada pelo marcador e lida só no recorte dela;
  - lista em hash exigida e aceita depois de publicada;
  - empresa ausente reprovada por hash, sem valor;
  - relatórios filtrados.

### Estado do QA da emenda
| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| plano | Sonnet isolado (a222cd5cfd0828201) | PASS-COM-RESSALVAS | 1 ALTA (`conhecimento.json` global), 3 MÉDIA, 1 BAIXA; aceite RATIFICADO-COM-AJUSTES | `conhecimento.json` por empresa, D5, critérios 3, 6 e 8 |
| código 1 | Sonnet isolado (a45475faecd088181) | PASS-COM-RESSALVAS | sem vazamento. 1 ALTA: pasta com maiúscula dava falso PASS. 2 MÉDIA: sem caso alfa/alfa2; sigla "MM" reprovava assunto | escopo em minúsculas e achado de pasta; caso alfa2; identificador de 4+ caracteres ou com dígito |
| código 2 | Sonnet isolado (addd6d7a6db4e5278) | PASS-COM-RESSALVAS | correções conferidas; 3 mutações e a declarada, mortas. 1 MÉDIA e 1 BAIXA: limites não declarados | declarados em Limites |
| emenda 2, 1 | Sonnet isolado (a0421ad803ee9eb90; travou 600 s e foi retomado) | PASS-COM-RESSALVAS | 2 ALTA: filtro D3 não olhava o nome do arquivo do relatório; biblioteca ausente dava PASS sem ler nada. 1 MÉDIA: marcador lido duas vezes | nome do arquivo no filtro; `verificar` reprova e `--recall` avisa; leitura única; 3 casos novos |
| emenda 2, 2 | Sonnet isolado (aede2a2d99a0f1c53) | PASS-COM-RESSALVAS | ALTAs fechadas; mudança sem perda (9 arquivos idênticos, índice, 27 achados iguais); README do pai confere; mutações 3 de 4 mortas. 1 BAIXA: `_hash` sem teste direto de maiúsculas | caso direto acrescentado |

## Emenda 3 — empresa da pasta no boot, regra superada e registro cobrado no fechamento (04/10/2026)

- **Status:** Aceita.
- **Decisores:** dono (Fabricio), 04/10/2026: débito `framework-contexto-empresa-automatico` ("resolver empresa,
  domínio e assunto pela pasta; gravar o conhecimento no repositório certo sem pedido, superando o desatualizado");
  "produto próprio" = lista configurável, começando só pela pasta do framework; fechamento cobrado pelo comando no
  docops, sem hook novo. Autoria: Opus 5.5.
- **Problema:** (1) o recorte por pasta da emenda 1 nunca funcionou com o índice real: o `~\` dos caminhos não era
  expandido; (2) o boot não dizia a empresa nem onde ler/gravar; (3) entrada superada no projeto continuava valendo
  na biblioteca (caso de 03/10/2026: regra antiga sem a fonte única); (4) o registro no fechamento era prosa.

### Decisão
1. `~\` e `~/` expandem para a pasta do usuário, nos dois separadores, no índice e nos ponteiros.
2. `conhecimento.py contexto [--cwd]` → EMPRESA · PRODUTO-PRÓPRIO · FORA-DO-ÍNDICE · AMBÍGUO · SEM-BIBLIOTECA.
   - PRODUTO-PRÓPRIO: a pasta deste framework, ou uma pasta de `conhecimento.json` → `"sem_empresa"` da raiz.
   - FORA-DO-ÍNDICE manda perguntar a empresa no 1º turno e indexar.
   - O `boot_check` roda o `contexto` na pasta da sessão (check `contexto-empresa`; alerta fora do índice ou com
     entrada a reverificar) e a linha da empresa traz o comando de `encerramento` com caminhos absolutos.
   - O passo 0.7 do `start-session.md` chama o `boot_check` por `{{FRAMEWORK_ROOT}}`, que o `sync-global.ps1`
     troca pelo caminho absoluto do framework ao espelhar os workflows: o comando injetado numa pasta de projeto
     resolve lá (ADR-098). Em pasta de projeto, o passo manda rodar sempre.
3. `vencidos` acusa a entrada cuja **Fonte:** cita arquivo local alterado (último commit; fora do git, data de
   modificação) depois do **Verificado em:**. Retrato não entra; arquivo ausente na máquina não acusa.
4. `conhecimento.py encerramento --desde dd/mm/aaaa [hh:mm] [--declarar "<motivo>"]`: 0 com commit + push na biblioteca da
   empresa desde a data, sem alteração pendente, ou com declaração; 1 sem registro, com pendência ou sem push;
   2 empresa não resolvida. Produto próprio passa. O passo 7 do docops cobra o comando.

### Régua §0
Critério (c): o recorte por pasta da emenda 1, que existia e não funcionava, passa a funcionar; o passo 7 do docops,
que era prosa, vira comando com código de saída. Sem hook e sem arquivo novos: 2 comandos e 1 critério no
verificador existente, 1 check no `boot_check` existente, casos no canário existente.

### Limites
- **Fonte alterada ≠ regra contraditória:** qualquer commit no arquivo citado depois da verificação acusa, mesmo
  numa seção que a entrada não usa. É pedido de reverificação, não prova de erro. Commit no mesmo dia da
  verificação não acusa.
- **O fechamento só é cobrado se o docops rodar:** sem hook, pular o passo 7 não é barrado.
- **O boot só mostra a empresa se o agente rodar o `boot_check`** (passo 0.7). Nenhum hook roda Python no boot
  das pastas de projeto.
- **O espelho global só muda quando o `sync-global.ps1` roda.** Ele não roda sozinho: em 04/10/2026 o
  `~\.claude\workflows\start-session.md` desta máquina era de 08/08/2026. Até o próximo sync, as pastas de projeto
  recebem o texto antigo. Lido direto no repositório do framework, `{{FRAMEWORK_ROOT}}` = a raiz deste repositório.
- **Mudança na fonte** = último commit do arquivo; com edição não commitada (ou fora do git), a data de modificação.
- **Push:** só é conferido quando há commit desde a data; commit antigo sem push, com declaração, passa.
- **"Registro" = qualquer commit na pasta da biblioteca** desde `--desde` (que aceita hora), inclusive índice ou
  correção de digitação. O comando prova que algo foi gravado e publicado, não que o conteúdo é o conhecimento
  novo do bloco; `--desde` vem de quem fecha o bloco.
- **A biblioteca precisa ser repositório git nesta máquina;** senão o fechamento reprova sem provar nada.
- **Fora do índice** a mensagem mostra só quantas bibliotecas de empresa existem na máquina, nunca os nomes.
- Sem caso de canário com biblioteca externa dentro de repositório-pai real (provado só na biblioteca real da
  máquina e pelo crítico em cenário montado).

### Prova
- `tools/test_conhecimento.py` (g): expansão de `~`; EMPRESA por subpasta e não por prefixo de nome; FORA,
  PRODUTO-PRÓPRIO (framework e `sem_empresa`), AMBÍGUO, SEM-BIBLIOTECA; célula com dois caminhos; fonte alterada
  depois e antes da verificação, retrato e fonte ausente; fechamento sem registro, com declaração, com pendência,
  sem push, com push, produto próprio e fora do índice.
- Biblioteca real (04/10/2026): `verificar --empresa vibra` 56 → 24 achados (os 24 são reais, da biblioteca da
  empresa); `vencidos` passou a mostrar 3 entradas com fonte alterada; `encerramento` mostrou 1 commit sem push.

### Estado do QA da emenda 3
| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| código 1 | Sonnet isolado (ad63fbe9c8b6622b0) | PASS-COM-RESSALVAS | sem ALTA. 4 MÉDIA: push contava commit de outra pasta do repositório-pai; "registro" fraco (commit anterior ao trabalho no mesmo dia contava); produto próprio antes do índice dava falso PASS para projeto sob a pasta do framework; FORA citava nome de empresa. 2 BAIXA: sem caso com biblioteca externa em repositório-pai; boot_check 6,8 s | `rev-list -- .`; `--desde` com hora + limite declarado; índice antes de produto próprio; só a contagem; BAIXAs declaradas em Limites. 4 casos novos no canário |
| fechamento, padrão | Sonnet isolado (a28f70ad1837bbbce) | PASS-COM-RESSALVAS | 4 correções conferidas no código e no canário; sem ALTA. 3 BAIXA: `--desde ... 14:30` sem aspas virava raiz; hora inválida virava meia-noite; `"sem_empresa": [""]` valia a raiz inteira | as 3 corrigidas, com caso no canário |
| fechamento, acima | Fable isolado (ab54e0aea4b53b769) | FAIL | 1 ALTA: `boot_check` por caminho relativo só resolve no framework (sempre PRODUTO-PRÓPRIO) — na pasta de projeto nunca rodava. 2 MÉDIA: docops com caminho relativo; fonte com espaço no caminho nunca vencia. BAIXA: edição não commitada não acusava; `data_da_fonte` reimplementava `_git` | `{{FRAMEWORK_ROOT}}` no 0.7 + substituição no `sync-global`; comando absoluto na linha do boot e no docops; regex aceita espaço e tira palavras do fim; edição não commitada usa a data de modificação; `_git` único; 4 casos novos |
| fechamento, acima, 2 | Fable isolado (a0e02b81a46b52da7) | PASS-COM-RESSALVAS | ALTA fechado, conferido no caminho real (hook → espelho → comando absoluto; sync rodado com perfil temporário); substituição sem BOM, CRLF preservado, workflow sem marcador byte-idêntico. 2 BAIXA: Fonte "A e B" só conferia o 1º; sem canário contra o comando relativo voltar | `e`/`ou` separam arquivos; trava no canário (g); 2 casos novos |
