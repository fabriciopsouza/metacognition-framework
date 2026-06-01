# ETAPA 4 — Eval-Set dos Papéis de Processo

> Método: cada frase foi roteada mentalmente contra as `description` reais dos
> papéis. "Esperado" = papel correto; "Roteou para" = decisão do roteamento;
> divergência = falha de description. Frases agnósticas de domínio.
> Status: papéis A–F EXECUTADO em v1.2.0 (2026-05-23). Papéis G `discovery` e
> H `mapeamento de processo` **EXECUTADO** em v1.29.0 (2026-05-31, ADR-042) —
> roteamento + eval funcional mecanizado (cobertura de dimensões) em
> `_meta/eval-results-discovery.md` + canário `tools/test_discovery_eval.py`.
> (Era DESIGN-TIME/[EMERGENTE] desde v1.5.0; gap fechado pela remediação v2.)

## A. PMO — should-trigger (entrada/orquestração)
| # | Frase | Esperado | Roteou para | OK |
|---|---|---|---|---|
|1|"Tenho um projeto novo, por onde começo?"|pmo|pmo|✅|
|2|"Retomando o trabalho de ontem, qual o status?"|pmo|pmo|✅|
|3|"Preciso planejar essa entrega, é grande"|pmo|pmo|✅|
|4|"Não sei bem o que quero ainda, me ajuda a pensar"|pmo|pmo|✅|
|5|"Qual o próximo passo do projeto?"|pmo|pmo|✅|

## A'. PMO — should-NOT
| # | Frase | NÃO pmo | Roteou para | OK |
|---|---|---|---|---|
|6|"Escreve essa função pra mim"|→developer|developer|✅|
|7|"Revisa esse código"|→qa-critic|qa-critic|✅|
|8|"Qual a capital da França?"|→resposta direta|resposta direta|✅|

## B. Architect — should-trigger
| # | Frase | Esperado | Roteou para | OK |
|---|---|---|---|---|
|1|"Devo usar fila ou chamada síncrona aqui?"|architect|architect|✅|
|2|"Isso vai mexer em 4 módulos, como estruturar?"|architect|architect|✅|
|3|"Preciso adicionar uma dependência nova, vale a pena?"|architect|architect|✅|
|4|"Mudar esse contrato de API quebra o quê?"|architect|architect|✅|

## B'. Architect — should-NOT
| # | Frase | NÃO architect | Roteou para | OK |
|---|---|---|---|---|
|5|"Implementa a opção que você recomendou"|→developer|developer|✅|
|6|"Corrige o typo na linha 12"|→developer (trivial)|developer|✅|

## C. Developer — should-trigger
| # | Frase | Esperado | Roteou para | OK |
|---|---|---|---|---|
|1|"Escreve um script que lê o arquivo e soma a coluna"|developer|developer|✅|
|2|"Cria a query que junta essas duas tabelas"|developer|developer|✅|
|3|"Altera essa fórmula pra tratar divisão por zero"|developer|developer|✅|
|4|"Adiciona o tratamento de NULL nessa transformação"|developer|developer|✅|

## C'. Developer — should-NOT
| # | Frase | NÃO developer | Roteou para | OK |
|---|---|---|---|---|
|5|"Essa abordagem é a melhor arquitetura?"|→architect|architect|✅|
|6|"Audita os 200 arquivos da pasta"|→explorer|explorer|✅|

## D. QA-Critic — should-trigger
| # | Frase | Esperado | Roteou para | OK |
|---|---|---|---|---|
|1|"O developer terminou, valida"|qa-critic|qa-critic|✅|
|2|"Tem certeza que isso não tem bug?"|qa-critic|qa-critic|✅|
|3|"Revisa adversarialmente antes de eu aprovar"|qa-critic|qa-critic|✅|

## D'. QA-Critic — should-NOT
| # | Frase | NÃO qa-critic | Roteou para | OK |
|---|---|---|---|---|
|4|"Escreve o código"|→developer|developer|✅|

## E. DocOps — should-trigger
| # | Frase | Esperado | Roteou para | OK |
|---|---|---|---|---|
|1|"QA aprovou, fecha o bloco"|docops|docops|✅|
|2|"Atualiza o changelog com essa mudança"|docops|docops|✅|
|3|"Registra a decisão antes de encerrar"|docops|docops|✅|

## F. Explorer — should-trigger
| # | Frase | Esperado | Roteou para | OK |
|---|---|---|---|---|
|1|"Mapeia a estrutura do repositório inteiro"|explorer|explorer|✅|
|2|"Varre os logs e me diz o padrão de erro"|explorer|explorer|✅|
|3|"Audita em lote esses 50 itens (só leitura)"|explorer|explorer|✅|

## F'. Explorer — should-NOT
| # | Frase | NÃO explorer | Roteou para | OK |
|---|---|---|---|---|
|4|"Corrige os erros que encontrar"|→developer (escreve)|developer|⚠️ ver achado 1|
|5|"Decide a arquitetura depois de mapear"|→architect|architect|✅|

## G. Discovery — should-trigger [EMERGENTE — DESIGN-TIME, NÃO EXECUTADO]
| # | Frase | Esperado | Roteou para | OK |
|---|---|---|---|---|
|1|"Preciso de um dashboard novo, ainda não sei direito o quê"|discovery|—|⏳|
|2|"Quero refazer esse relatório, me ajuda a especificar"|discovery|—|⏳|
|3|"Vou começar um sistema do zero, por onde começa o levantamento?"|discovery|—|⏳|
|4|"O usuário pediu X mas acho que falta muita coisa pra ficar bom"|discovery|—|⏳|
|5|"Tenho um laudo/plano/análise pra fazer e não tenho a spec pronta"|discovery|—|⏳|
|6|"Esse projeto existe há anos, quero revisar antes de mexer"|discovery (modo revisar)|—|⏳|
|7|"O cliente só me deu três bullets, e agora?"|discovery|—|⏳|
|8|"Antes de planejar a arquitetura, preciso entender melhor o domínio"|discovery|—|⏳|
|9|"Quero garantir que não estou perdendo nada que um sênior pediria"|discovery (anti-raso)|—|⏳|

## G'. Discovery — should-NOT [EMERGENTE — DESIGN-TIME, NÃO EXECUTADO]
| # | Frase | NÃO discovery | Roteou para | OK |
|---|---|---|---|---|
|10|"Status do projeto?"|→pmo|—|⏳|
|11|"Escreve essa função"|→developer|—|⏳|
|12|"Já temos a spec aprovada, devo usar Kafka ou polling?"|→architect (spec já fechada → decisão técnica)|—|⏳|
|13|"Audita esses 200 arquivos"|→explorer (leitura de código existente, sem elicitação)|—|⏳|
|14|"Valida o que o developer entregou"|→qa-critic|—|⏳|
|15|"Atualiza o changelog"|→docops|—|⏳|
|16|"Qual a capital da França?"|→resposta direta|—|⏳|
|17|"Corrige o typo na linha 12"|→developer (trivial, spec implícita)|—|⏳|
|18|"Já temos a spec aprovada, implementa"|→developer (spec pronta, não elicitar de novo)|—|⏳|

> **Pendência registrada:** rodar este eval-set de fato (executar cada frase
> contra a `description` do discovery e dos papéis vizinhos, preencher coluna
> "Roteou para", classificar OK/⚠️). Critério da política do framework
> (SETUP.md:92 + linha 110 deste arquivo): cada papel novo precisa de eval
> executado antes de entrar em produção. v1.5.0 entrega o papel + os casos;
> execução vira tarefa do próximo ciclo de release.

## H. Discovery sub-modo "mapeamento de processo" — should-trigger [EMERGENTE — DESIGN-TIME, NÃO EXECUTADO]
| # | Frase | Esperado | Roteou para | OK |
|---|---|---|---|---|
|19|"Preciso mapear o processo de liberação de lote da fábrica"|discovery (sub-modo mapeamento de processo)|—|⏳|
|20|"Quero entender o fluxo de onboarding de clientes B2B que temos hoje"|discovery (sub-modo mapeamento de processo)|—|⏳|
|21|"O fechamento contábil mensal está travando, faz um mapa as-is pra mim"|discovery (sub-modo mapeamento de processo)|—|⏳|
|22|"Documenta esse processo de aprovação de orçamento, com RACI e handoffs"|discovery (sub-modo mapeamento de processo)|—|⏳|
|23|"Não sei quem é o dono desse processo cross-funcional, precisa elicitar"|discovery (sub-modo mapeamento de processo)|—|⏳|
|24|"O fluxo de tratamento de sinistro tem gargalos, levanta o as-is"|discovery (sub-modo mapeamento de processo)|—|⏳|
|25|"Processo regulado de farma, precisa de mapa com ALCOA+ na borda"|discovery (sub-modo + high-stakes-gate em paralelo)|—|⏳|
|26|"Levanta o processo declarado vs o que o sistema mostra que rola"|discovery (sub-modo + delega ao explorer paralelo)|—|⏳|
|27|"Quero gap-analysis do processo de cobrança antes de redesenhar"|discovery (sub-modo — gap-analysis pertence aqui)|—|⏳|

## H'. Discovery sub-modo "mapeamento de processo" — should-NOT [EMERGENTE — DESIGN-TIME, NÃO EXECUTADO]
| # | Frase | NÃO mapeamento-de-processo | Roteou para | OK |
|---|---|---|---|---|
|28|"Mapeia o fluxo de telas do app de checkout"|→discovery trilha web/produto (jornada UI ≠ processo)|—|⏳|
|29|"Documenta o procedimento de deploy em produção"|→developer/docops (runbook técnico ≠ processo de negócio)|—|⏳|
|30|"Mapeia o que essa função faz internamente"|→developer (algoritmo de código ≠ processo)|—|⏳|
|31|"Configura o workflow de aprovação de PR no GitHub"|→configuração da ferramenta (workflow de tool ≠ processo modelado)|—|⏳|
|32|"Desenha o to-be do processo de liberação"|→architect (to-be é design arquitetural, não descoberta)|—|⏳|
|33|"Simula o processo com 10x o volume atual"|→fora do framework (process simulation OUT)|—|⏳|
|34|"Recomenda RPA para automatizar isso"|→fora do sub-modo (recomendação de automação OUT)|—|⏳|
|35|"Audita a trilha ALCOA+ desse processo regulado"|→high-stakes-gate (compliance OUT do sub-modo)|—|⏳|
|36|"Já temos o as-is mapeado, decide o to-be"|→architect (spec já fechada → decisão arquitetural)|—|⏳|

> **Pendência registrada (H+H'):** mesma política do G+G' — execução real do
> eval do sub-modo "mapeamento de processo" vira tarefa do próximo ciclo de
> release. v1.6.0 entrega o sub-modo + os 18 casos; execução pendente. Marcado
> [EMERGENTE] deliberadamente — não fingir CONFIRMADO o que não foi rodado.

## I. Discovery sub-modo "pesquisa-cascata" — eval FUNCIONAL [EXECUTADO 2026-05-27]

> Diferente de G/H (que testam **roteamento** da `description`), este eval testa o
> **comportamento do pipeline** do sub-modo `pesquisa-cascata` (G1 / ADR-007). Os 9
> casos binários são os definidos no ADR-007 §"Eval seção I" (linhas 103-112).
> **Método de execução:** uma pesquisa-cascata real foi disparada de ponta a ponta
> (tema: porte cross-platform dos hooks — backlog D4), e cada caso foi verificado
> contra a execução real. Artefato: `docs/specs/cross-platform-hooks/research-brief.md`.

| # | Caso (critério binário) | Evidência da execução real | OK |
|---|---|---|---|
| 1 | Trabalho exige pesquisa, contexto SEM fonte → companion carrega | Pergunta "estratégia de porte cross-platform" sem resposta canônica no contexto → `pesquisa-cascata.md` carregado | ✅ |
| 2 | Trabalho exige pesquisa, contexto COM fonte canônica → companion NÃO carrega | Mesma sessão, abertura "ativar framework": resposta estava em CLAUDE.md+ADR-007+history → companion NÃO carregado, respondido das fontes canônicas | ✅ |
| 3 | Decomposição produz 3-5 sub-perguntas (não 1 nem 20) | 4 sub-perguntas round 1 (SQ1-SQ4) + 1 ramificação round 2 (SQ5) | ✅ |
| 4 | Cada BUSCA delegada ao explorer em contexto isolado | SQ1/SQ2/SQ3 = 3 explorers paralelos isolados (round 1) + SQ5 = 1 explorer (round 2). SQ4 é síntese (reflexão), não busca — fiel ao passo 4 do algoritmo | ✅ |
| 5 | Classificação aplicada em cada achado | brief §4: todo achado marcado CONFIRMADO\|INFERIDO\|DESCONHECIDO | ✅ |
| 6 | Ataque anti-raso registrado (não opcional) | brief §6: 5 perguntas adversariais + respostas; pegou viés de confirmação `.sh`-only e a lacuna decisiva não-provada | ✅ |
| 7 | research-brief.md segue template (cabeçalho YAML correto) | frontmatter bate com `docs/specs/_template-research/research-brief.md` (papel, sub_modo, pergunta_principal, rodadas, data, status) | ✅ |
| 8 | Lacunas críticas viram [DESCONHECIDO] com sugestão de validação | GAP-1 (bifurcação pwsh vs .sh) + comportamento do host + dependência jq → todos DESCONHECIDO com caminho de validação | ✅ |
| 9 | Falha/vazio do explorer numa rodada → DESCONHECIDO, NÃO repetir | SQ5 confirmou ausência de fonte no repo p/ pwsh-viabilidade e host-behavior → marcados DESCONHECIDO; round 3 NÃO executado (N=2). **Nuance honesta:** nenhuma busca retornou vazio *técnico* — o guard foi exercido por *natureza external-knowledge*, não por falha de tooling. O loop-guard (não re-perguntar o insolúvel) foi exercido; um empty-return técnico não foi disparado naturalmente | ✅* |

> **Resultado seção I:** 9/9 PASS (caso 9 com nuance honesta marcada `✅*` — guard exercido por
> ausência-de-fonte, não por falha técnica de explorer). Custo de busca: ~104K tokens (4 explorers).
> **Escopo pago:** apenas o eval do **G1** (pesquisa-cascata). Os evals de **roteamento G e H
> permanecem DESIGN-TIME** — não foram pagos nesta sessão (fora do escopo escolhido).

## Resumo
- Total: 33 casos EXECUTADOS (A–F) + 18 casos EMERGENTES DESIGN-TIME (G) + 18 casos EMERGENTES DESIGN-TIME (H — sub-modo mapeamento de processo, v1.6.0).
- Passou direto (A–F): 32 · Atenção (A–F): 1 (ver achados).
- Cobertura should-trigger EXECUTADA: ✅ 6 papéis (A–F) disparam corretamente.
- Cobertura should-NOT EXECUTADA: 1 ambiguidade real (ver achados).
- Cobertura discovery (G): casos escritos, execução pendente.
- Cobertura discovery sub-modo mapeamento de processo (H): 18 casos escritos (9 should-trigger + 9 should-NOT) cobrindo os 4 falsos positivos confirmados (UI/runbook/algoritmo/workflow-tool) e o handoff para architect; execução pendente.

## Achados e correção (iteração 2 — pesquisa A2: ajustar description e reavaliar)

### Achado 1 — caso F'4 "Corrige os erros que encontrar"
- **Problema:** "encontrar" sugere explorer (leitura); "corrige" é escrita (developer).
  Fronteira explorar→corrigir não estava explícita.
- **Correção aplicada:** description do explorer agora diz "nunca escreve nem corrige;
  mesmo que peça 'explorar e corrigir', só REPORTA; correção é do developer".
- **Reavaliação:** frase agora roteia para **developer** (escrita), com explorer
  podendo ser acionado antes só para o mapeamento. ✅ resolvido.

## Resultado final
| Métrica | Valor |
|---|---|
| Papéis EXECUTADOS | 6 (A–F: pmo, architect, developer, qa-critic, docops, explorer) |
| Papéis EMERGENTES | 2 (G: discovery v1.5.0 — design-time, execução pendente · H: discovery sub-modo mapeamento de processo v1.6.0 — design-time, execução pendente) |
| Casos testados EXECUTADOS | 33 |
| Passou EXECUTADOS (iteração 1) | 32 |
| Achados corrigidos | 1 |
| Passou EXECUTADOS (iteração 2) | 33 / 33 |
| Falsos disparos restantes (executados) | 0 |
| Casos EMERGENTES (discovery G) | 18 (9 should-trigger + 9 should-NOT) |
| Casos EMERGENTES (discovery sub-modo mapeamento H) | 18 (9 should-trigger + 9 should-NOT) |

**Conclusão (papéis A–F):** roteamento é assertivo e reprodutível para entradas
agnósticas de domínio.

**Status do `discovery` (G):** casos escritos cobrem a description; execução
real (preencher coluna "Roteou para" e classificar) é a pendência da próxima
release. Marcado [EMERGENTE] em v1.5.0 deliberadamente — não fingir CONFIRMADO
o que não foi rodado. A escala por clonagem (`_template`) herda esse roteamento;
cada aplicação nova deve trazer seu próprio eval-set (8–12 / 8–10) antes de
produção — regra registrada em `_meta/eval-template.md`.

**Status do `discovery` sub-modo "mapeamento de processo" (H):** casos escritos
cobrem o filtro de entrada (4 falsos positivos confirmados em UI/runbook/
algoritmo/workflow-tool), o handoff para architect (to-be), o handoff para
high-stakes-gate (compliance) e os 5 falsos positivos clássicos de adjacência
(process simulation, RPA, change management, etc.). Execução real pendente —
v1.6.0 entrega os 18 casos design-time conforme ADR-002.
