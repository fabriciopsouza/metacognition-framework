# RATE-CARD (exemplo) — a estrutura, sem os números

> **Este arquivo não precifica nada.** Ele é o molde do `RATE-CARD.md` que a skill
> `service-valuation` procura no Passo 0 (ordem de resolução no §12 da skill). Todo valor aqui é
> `[DESCONHECIDO]` de propósito: um rate card com número inventado é pior que rate card ausente,
> porque a ausência para o método e o número inventado o deixa seguir.
>
> **Como usar:** copie para `.claude/skills/service-valuation/RATE-CARD.md` no seu projeto, ou
> para `docs/_private/service-valuation/RATE-CARD.md` se for o seu rate card pessoal e o
> repositório for exportado. Preencha com cotação, proposta recebida ou contrato — e registre a
> origem de cada linha. **Não preencha por estimativa apresentada como fato.**
>
> As faixas de unidade de entrega (§4) nascem `[INFERIDO / BAIXA]`. Elas só deixam de ser chute
> quando o `HISTORICO-ENTREGAS.md` acumula três registros da mesma disciplina e unidade.

## 1. Taxas por perfil e disciplina

Moeda e período: **declare aqui** (ex.: R$/hora, USD/hora). Sem isso, nenhuma linha é utilizável.

| ID | Disciplina | Perfil | Mín | Provável | Máx | Origem | Confiança |
|---|---|---|---|---|---|---|---|
| T-01 | ERP funcional | Consultor pleno | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |
| T-02 | ERP funcional | Consultor sênior | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |
| T-03 | ERP técnico | Desenvolvedor | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |
| T-04 | Analytics/BI | Analista | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |
| T-05 | Engenharia de dados | Engenheiro | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |
| T-06 | Automação/RPA | Desenvolvedor de automação | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |
| T-07 | Integração/API | Especialista de integração | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |
| T-08 | IA/ML/LLM | Cientista de dados | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |
| T-09 | Cloud/infra | Engenheiro cloud | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |
| T-10 | Qualidade e validação | QA / validação | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |
| T-11 | Gestão/PMO | Gerente de projeto | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |
| T-12 | Treinamento | Instrutor (hora de aula) | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |
| T-13 | Consultoria de processo | Consultor de negócio | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[DESCONHECIDO]` | `[BAIXA]` |

Acrescente perfis do seu mercado. **Ambiente regulado é linha de perfil só se a norma exigir
qualificação específica** — e qual norma é declaração do projeto, não do núcleo (ADR-010).

## 2. Derivação usada nas faixas acima

Escreva de onde saiu cada faixa: cotação recebida, proposta de concorrente, tabela pública,
derivação salarial com encargos e ocupação. **Derivação salarial é `[INFERIDO]`, nunca
`[CONFIRMADO]`** — e é a mais fraca das origens, porque não sabe o que o mercado cobra, só o
que custa produzir.

## 3. Ajuste por modelo de suporte

| Modelo | Ajuste | Por quê |
|---|---|---|
| AMS por chamado | `[DESCONHECIDO]` | — |
| Bolsa de horas | `[DESCONHECIDO]` | — |
| Projeto com escopo fechado | `[DESCONHECIDO]` | fornecedor absorve variação |
| Body shop | `[DESCONHECIDO]` | — |
| Consultoria pontual | `[DESCONHECIDO]` | — |
| Plantão / on-call | `[DESCONHECIDO]` | — |
| Garantia pós-entrega | `[DESCONHECIDO]` | — |

## 4. Unidades de entrega por disciplina

A trava do Passo 2. Se o bottom-up sair desta faixa, **o bottom-up é o suspeito** (regra 8 da
skill), não a faixa.

| ID | Disciplina | Unidade | Faixa de horas | Confiança |
|---|---|---|---|---|
| U-01 | Automação/RPA | um fluxo simples de ponta a ponta | `[DESCONHECIDO]` | `[BAIXA]` |
| U-02 | Analytics/BI | um painel com N visuais e uma fonte | `[DESCONHECIDO]` | `[BAIXA]` |
| U-03 | Engenharia de dados | uma ingestão nova com carga incremental | `[DESCONHECIDO]` | `[BAIXA]` |
| U-04 | Integração/API | uma integração ponto a ponto | `[DESCONHECIDO]` | `[BAIXA]` |
| U-05 | ERP funcional | uma configuração de processo | `[DESCONHECIDO]` | `[BAIXA]` |

## 4.1 Preço de resultado equivalente — a alternativa do cliente

**Esta seção vale mais que a tabela inteira de taxas**, e a razão é de classificação: uma cotação
real aqui é `[CONFIRMADO]` e vence o rate card por precedência, enquanto toda a §1 é, no melhor
caso, `[INFERIDO]`.

É a pergunta do Passo 4 que quase sempre é esquecida: **quanto custaria comprar este RESULTADO
pronto?** Não a hora — o resultado. É contra isso que o cliente julga o seu preço.

| ID | Alternativa | Preço | Origem | Classificação |
|---|---|---|---|---|
| RE-01 | Integrador da disciplina que faria o mesmo escopo | `[DESCONHECIDO]` | — | — |
| RE-02 | Plataforma com licença que resolve o mesmo problema | `[DESCONHECIDO]` | — | — |
| RE-03 | Módulo ou produto de mercado equivalente | `[DESCONHECIDO]` | — | — |
| RE-04 | Custo de **não fazer** (manter o processo como está) | `[DESCONHECIDO]` | — | — |

Enquanto as quatro estiverem `[DESCONHECIDO]`, **a Lente B não existe** (regra 9): a triangulação
perde uma perna e o resultado é faixa, nunca ponto.

## 5. Custo-hora interno do cliente

Usado para calcular benefício por horas economizadas (`V-nn`). **Calcule antes de somar horas de
esforço:** quando o trabalho substituído é barato, a tese de produtividade morre cedo e a conversa
muda para latência e risco — foi a terceira lição do caso `H-01`.

| Perfil substituído | Custo-hora carregado | Origem |
|---|---|---|
| — | `[DESCONHECIDO]` | — |

## 6. Premissas globais editáveis

| Premissa | Valor | Origem |
|---|---|---|
| Moeda e data-base | `[DESCONHECIDO]` | — |
| Horas úteis por mês | `[DESCONHECIDO]` | — |
| Ocupação faturável assumida | `[DESCONHECIDO]` | — |
| Teto do produto de multiplicadores | 1,50 | regra do método (§ Passo 6 da skill) |

## 7. Registro de calibração

A cada revisão: data, o que mudou, e **contra que evidência**. Rate card revisado sem evidência
nova é o mesmo número com carimbo mais recente.

| Data | O que mudou | Evidência |
|---|---|---|
| — | — | — |
