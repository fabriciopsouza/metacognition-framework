# HISTORICO-ENTREGAS.md

Base de calibração própria. **Precedência máxima**: quando uma linha daqui cobre a demanda
sendo valorada, ela vence o `RATE-CARD.md` e é classificada `[CONFIRMADO]`.

Preencher ao fechar cada entrega, não depois. Horas reais aproximadas valem mais que horas
exatas nunca registradas.

## Como usar

- Três ou mais linhas na mesma disciplina e unidade autorizam substituir a faixa default do
  `RATE-CARD.md` (seção 4) pela média própria.
- Registrar também as entregas que deram errado. Desvio negativo é o dado mais útil.
- Não registrar dado de cliente identificável se este repositório for público. Use apelido
  de cliente (`CLI-01`, `CLI-02`) e mantenha o de-para fora do repositório.

## Registro

| ID | Data | Cliente | Disciplina | Unidade / escopo | Complexidade | h estimadas | h reais | Desvio | Preço praticado | Modelo de suporte | Observação |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H-01 | 29/08/2026 | CLI-01 | Automação/RPA | fluxo de reset de senha e desbloqueio, do chamado ao SAP GUI, com resposta e encerramento no service desk | simples (fluxo) em ambiente regulado | 478 h (v1.0) → **55 h (v2.0)** | não apontadas | **v1.0 errou 8,7x no esforço (478÷55) e 20,8x no preço (270.000÷13.000)** | não praticado — valoração sem contrato | escopo fechado | **fonte NÃO versionada aqui:** a `MEMORIA-CALCULO.md` v2.0 e as 8 falhas vivem no repositório do projeto (`copiloto-automacoes-sap`), não neste. Enquanto não for copiada para esta pasta, estes números são relato, não fonte auditável — ADR-114 §"E ela me pegou também" |
| H-02 | | | | | | | | | | | |
| H-03 | | | | | | | | | | | |

## Médias consolidadas

Recalcular ao adicionar linha. Enquanto houver menos de 3 registros, manter `[INFERIDO]`.

| Disciplina | Unidade | N | Média h reais | Desvio médio vs estimativa | Classificação |
|---|---|---|---|---|---|
| | | 0 | | | `[INFERIDO / BAIXA]` |

## Lições por entrega

Uma linha por aprendizado que muda estimativa futura. Exemplo do formato:

- `H-01` **o esforço foi ancorado em linhas de código e estourou 8,7x.** 17.755 linhas de
  Python viraram 478 h; a faixa de unidade da disciplina dizia 16 a 40 h e foi ignorada como
  "sanidade". Ancorar sempre na unidade de entrega e no número de decisões, nunca no volume
  de artefato — comentário, teste e código gerado com IA desacoplam linha de hora.
- `H-01` **retrabalho do fornecedor entrou no preço.** Cerca de 30% dos commits eram conserto
  de defeito próprio, incluindo 11 achados de uma revisão adversarial interna. Excluir, e
  declarar o volume excluído.
- `H-01` **o benefício por horas economizadas era duas ordens de grandeza menor que o preço.**
  28 chamados/mês × 5 min = ~R$ 1.000/ano contra R$ 13.000 de construção. Quando o cliente
  disser que o trabalhador substituído é barato, calcular `V-02` ANTES de somar horas: ele
  costuma matar a tese de produtividade e mudar a conversa para latência e risco.
- `H-01` **empilhar multiplicadores dobra o preço sem uma linha nova de evidência.** No caso o
  produto foi **1,82**, com cinco fatores. Conferido contra a tabela do Passo 6: com **quatro**
  fatores, todos no piso da própria faixa, o máximo que ela produz é **1,75** — que já estoura o
  teto de 1,50 sem ninguém ter decidido aumentar coisa alguma. É por isso que o teto é do
  PRODUTO e não de cada fator. Escassez só com fonte.
