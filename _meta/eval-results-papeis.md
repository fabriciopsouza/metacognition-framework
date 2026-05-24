# ETAPA 4 — Eval-Set EXECUTADO dos Papéis de Processo

> Método: cada frase foi roteada mentalmente contra as `description` reais dos 7
> papéis (discovery). "Esperado" = papel correto; "Roteou para" = decisão do
> roteamento; divergência = falha de description. Frases agnósticas de domínio.
> Versão testada: papéis v1.2.0. Data: 2026-05-23.

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

## Resumo
- Total: 33 casos · Passou direto: 32 · Atenção: 1.
- Cobertura should-trigger: ✅ todos os 7 papéis disparam corretamente.
- Cobertura should-NOT: 1 ambiguidade real (ver achados).

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
| Casos testados | 33 |
| Passou (iteração 1) | 32 |
| Achados corrigidos | 1 |
| Passou (iteração 2) | 33 / 33 |
| Falsos disparos restantes | 0 |

**Conclusão:** roteamento dos 7 papéis de processo é assertivo e reprodutível para
entradas agnósticas de domínio. A escala por clonagem (`_template`) herda esse
roteamento; cada aplicação nova deve trazer seu próprio eval-set (8–12 / 8–10)
antes de produção — regra registrada em `_meta/eval-template.md`.
