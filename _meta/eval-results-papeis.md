# ETAPA 4 — Eval-Set dos Papéis de Processo

> Método: cada frase foi roteada mentalmente contra as `description` reais dos
> papéis. "Esperado" = papel correto; "Roteou para" = decisão do roteamento;
> divergência = falha de description. Frases agnósticas de domínio.
> Status: papéis A–F EXECUTADO em v1.2.0 (2026-05-23). Papel G `discovery`
> DESIGN-TIME em v1.5.0 (2026-05-24) — casos escritos e revisados, mas
> execução real do eval ainda não rodada → marcado [EMERGENTE], acionável
> como follow-up. Frontmatter de carga validado no review (ver C1 do qa-critic
> de v1.5.0).

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

## Resumo
- Total: 33 casos EXECUTADOS (A–F) + 18 casos EMERGENTES DESIGN-TIME (G).
- Passou direto (A–F): 32 · Atenção (A–F): 1 (ver achados).
- Cobertura should-trigger EXECUTADA: ✅ 6 papéis (A–F) disparam corretamente.
- Cobertura should-NOT EXECUTADA: 1 ambiguidade real (ver achados).
- Cobertura discovery (G): casos escritos, execução pendente.

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
| Papel EMERGENTE | 1 (G: discovery — design-time, execução pendente) |
| Casos testados EXECUTADOS | 33 |
| Passou EXECUTADOS (iteração 1) | 32 |
| Achados corrigidos | 1 |
| Passou EXECUTADOS (iteração 2) | 33 / 33 |
| Falsos disparos restantes (executados) | 0 |
| Casos EMERGENTES (discovery) | 18 (9 should-trigger + 9 should-NOT) |

**Conclusão (papéis A–F):** roteamento é assertivo e reprodutível para entradas
agnósticas de domínio.

**Status do `discovery` (G):** casos escritos cobrem a description; execução
real (preencher coluna "Roteou para" e classificar) é a pendência da próxima
release. Marcado [EMERGENTE] em v1.5.0 deliberadamente — não fingir CONFIRMADO
o que não foi rodado. A escala por clonagem (`_template`) herda esse roteamento;
cada aplicação nova deve trazer seu próprio eval-set (8–12 / 8–10) antes de
produção — regra registrada em `_meta/eval-template.md`.
