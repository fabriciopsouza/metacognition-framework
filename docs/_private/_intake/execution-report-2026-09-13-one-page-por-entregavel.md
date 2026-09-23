# Execution report — 2026-09-13 — one page por entregável (Agidesk/Natulab)

> Rota: **squad** + `high-stakes-gate`. QA: **Opus adversarial isolado, primeiro plano** — reprovou.
> Entrega: `natulab-agidesk-projetos` PR #2 **merged** (`f0ad61d` → `66ec6c2`).
> Segundo bloco do dia; o primeiro foi o PR #1 (painel).

## Placar

| | bloco 1 | bloco 2 |
|---|---|---|
| Testes | 172 | **230** |
| Mutações | 39 | **67 — todas PEGAS** |
| Achados do QA | 6 ALTA | **4 ALTA + 7 MÉDIA + 6 BAIXA** |

## A lição central: erro que só engana numa direção

Dois dos quatro ALTA tinham a mesma assinatura, e é a mais perigosa que existe
num relatório de gestão:

- **A entrega reportava o prazo previsto como data real de conclusão.** Entrega
  atrasada *sumia* de "Últimas entregas" justamente por ter atrasado.
- **Data invertida zerava o planejado** mantendo o peso no denominador: item que
  a ferramenta já classificava como *"Atrasada, nunca começou"* virava "nada era
  esperado" para a curva.

Um bug simétrico se revela na primeira semana. Um que sempre favorece o projeto
passa meses sendo lido como boa notícia. **Procurar por assimetria de direção
deveria ser um passo do checklist do qa-critic**, não um achado de sorte.

## Lições por skill

### architect
- **`entrega` ≠ `fase` foi a decisão que destravou tudo.** `fase` é o quadro do
  Agidesk (onde o cartão vive); `entrega` é o que o projeto entrega. Eram o mesmo
  campo, e por isso a visão macro não existia. Confundir o eixo de *fluxo* com o
  eixo de *escopo* é um erro de modelagem que nenhum ajuste de apresentação corrige.
- **Separar `situacao` (do conjunto) de `pior_filho` (ponteiro de ação)** — eram
  a mesma coisa, e o resultado era entrega 83% pronta rotulada "Não iniciada".
  Priorizar e nomear são funções diferentes.

### developer
- **Rótulo trocado sem trocar o dado.** Renomeei `iniciam_nesta_semana` para
  "Próxima semana" no HTML e não mudei a fonte. Em relatório de domingo, a janela
  era inteiramente passada. Renomear é mudança de contrato, não de cosmética.
- **Ramo morto que se declara vivo.** `datas.append(hoje)` antes do teste de lista
  vazia tornava o tratamento "sem datas suficientes" inalcançável.
- **`.replace(".", ",")` para vírgula decimal** trocou todos os pontos e produziu
  `-4,0 p,p,`. Formatação de número nunca é busca-e-substitui no texto inteiro.
- **Dado realista descobre o que teste unitário não vê.** "fase execucao trava 5
  itens" só apareceu rodando com 16 itens; com 2 ou 3 do `tmp_path` a regra
  parecia boa. Teste unitário prova que a regra **funciona**; dado realista mostra
  se ela **serve**.

### qa-critic
- **O achado mais duro: seis mutações do QA passaram por 211 testes.** Barras
  trocadas de lugar, gantt com metade da largura, donut que não fecha, card lendo
  outra lista — todas verdes. Os testes checavam **presença de substring**, nunca
  **conteúdo**. Para artefato visual, asserção tem de ser sobre posição, ordem e
  valor.
- **`html.count('class="humano"') == 2` é satisfeito por qualquer par.** Contagem
  não é contrato. O QA marcou o farol *derivado* como humano, apagou QUALIDADE,
  e o teste seguiu verde.
- **Mutação obsoleta não conta como passada.** Duas das minhas apontavam para
  trechos já reescritos; o verificador reportou "trecho não encontrado — mutação
  inválida", e é esse comportamento que faz o número significar algo.
- **Âncora de mutação precisa ser única.** `if p["alertas_humanos"]:` existe em
  duas funções; sabotar a primeira mediria a função errada.
- **O QA atacou por fora** — rodou o CLI com destino inválido, JSON quebrado,
  `--hoje` mal formatado, e criou um `subst` para testar caminho equivalente.
  Foi assim que achou o que duas rodadas minhas não acharam.

### docops
- **Dois documentos do mesmo bloco com molduras opostas.** `PENDENTE-QA.md` dizia
  honestamente que o canário de dinheiro é *"rede, não muro"*; `ONE-PAGE.md`
  vendia como *"mecânico, não promessa"*. Quem lesse o segundo concluiria que
  cifra não escapa. Corrigido: o que é mecânico (o bloco do farol) está separado
  do que é rede (cifra em prosa), com as formas medidas que a rede não pega.

## O que fica aberto

A maior dívida do repo **não** é deste bloco e segue intacta: o ledger de
procedência de existência (tarefa manual pode ser apagada), o diagnóstico cego de
escrita (nada mapeia 401/403), e o espelho bidirecional. O bloco 3 ataca os três
de uma vez, porque todos dependem da ponte com o portal.

**Decisão do dono ainda aberta:** qual fonte de estado morre — `backlog.json` ou
`estado.json`. Recomendação registrada: `estado.json`, absorvendo de
`backlog.json` os campos que faltam, com migração sem big bang.
