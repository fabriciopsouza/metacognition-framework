---
name: validation-reporting
version: 1.0.0
source: ADR-099 (2026-08-02) — bloco de validação real, 8 correções do dono
last_review: 2026-08-02
description: Núcleo SSoT do MÉTODO DE VALIDAÇÃO PONTO A PONTO com reporte legível por humano não-técnico. Carregar sempre que a tarefa for validar dados/migração/cálculo contra uma referência E o resultado for a decisão de alguém — "isto está validado?". Define os 4 níveis por consequência, a distinção validado × não conferido × não obtenível, o veredito VALIDADO-COM-RESSALVA e o conteúdo obrigatório do reporte. NÃO carregar para revisão de código (isso é qa-critic) nem para exploração de repositório (isso é explorer).
---

# Validação ponto a ponto com reporte para humano

> Origem: método derivado de um bloco de validação real (2026-08-02) em que o dono corrigiu
> o executor **oito vezes** até o reporte ficar utilizável. As oito correções estão nomeadas
> nas seções §2, §3, §6, §7 e §9 — as demais seções organizam o método, não derivam de erro.

## §0 — Onde esta skill se encaixa (ponte com o SSoT existente)

Não substitui nem duplica os núcleos vizinhos; **instancia** dois deles para o caso
"validar dado contra referência":

- **`confidence-classification`** continua sendo a única definição de origem de afirmação
  (CONFIRMADO / INFERIDO / DESCONHECIDO). As categorias da §2 são **status do DADO contra
  uma referência**, não origem de afirmação — eixos diferentes. Ponte: `VALIDADO` ⊂ afirmação
  CONFIRMADA; `NÃO CONFERIDO` e `NÃO OBTENÍVEL` são ambos DESCONHECIDO, e a §2 os separa
  porque um é **pendente** e o outro é **fechado** — distinção que a origem não expressa.
- **`high-stakes-gate`** + `tools/risk_score.py` continuam donos da validação **por risco**
  (tiers, gate HITL). Os níveis A/B/C da §3 são a instância **campo a campo** disso: use o
  risk_score para priorizar *o que* validar; use a §3 para decidir *quanto* de diferença
  cada campo admite.

## §1 — Quando carregar

Carregar quando **todas** valerem: (a) há uma **referência externa** contra a qual comparar;
(b) o resultado responde *"isto está validado?"*; (c) quem lê **decide** algo com a resposta.

Não carregar para: revisão de código (`qa-critic`), exploração (`explorer`), ou cálculo sem
referência (aí não há validação, há produção de número).

## §2 — As quatro categorias. Nunca três.

| Categoria | Significado | Erro que evita |
|---|---|---|
| **VALIDADO** | comparado contra referência, dentro do critério | — |
| **NÃO CONFERIDO** | não foi comparado | apresentar não-olhado como "ok" |
| **NÃO OBTENÍVEL** | a fonte **não permite** obter | pendência eterna para o impossível |
| **NÃO SE APLICA** | derivado de campo já validado, ou sem contraparte | poluir o relatório com item vazio |

**"Não conferido" nunca aparece como "ok".** E **"não obtenível" não é pendência** — é
decisão fechada. Registrar o impossível como pendência cria fila que ninguém nunca fecha.

**Cuidado com NÃO SE APLICA:** derivado de campo **validado sem ressalva** não se aplica.
Derivado de campo que passou **com** diferença tolerada é **B-DEC (§3) e tem de ser
medido** — é justamente ele que responde "a diferença altera a decisão?". Classificar um
B-DEC como "não se aplica" descarta a única prova que o nível B exige.

*Correção que originou:* o executor listou como pendência "estender a confirmação para os
demais períodos" quando a fonte não permitia baixá-los. E, depois, alegou impedimento onde
havia **outras duas vias** — a lição virou a §7.

## §3 — Níveis por CONSEQUÊNCIA do campo, não por percentual

| Nível | Campos | Régua |
|---|---|---|
| **A** — dinheiro e documento | valor, quantidade, documento fiscal, pedido, cliente, produto, identificador | **Tolerância zero.** Divergência reprova |
| **B** — operacional | tempos, horários, códigos de estado, local | Aceito se **caracterizado** *e* se **TESTADO** que não altera decisão |
| **C** — descritivo | nome, razão social, cidade, descrição | Tolerância maior, com **cobertura declarada** |
| **B-DEC** — decisão derivada | flag/indicador **calculado** a partir de B | É a **métrica de impacto** de B, não erro independente |

**"Não altera decisão" exige teste, não julgamento.** Recalcular o indicador com e sem a
diferença e contar quantos casos mudam de lado. Um segundo decide caso de borda em métrica
de janela — "parece inócuo" é opinião até virar número.

*Correções que originaram:* (a) o executor classificou uma flag **derivada** como nível A, e
a consequência de uma diferença de fórmula reprovava como se fosse erro de dado
independente; (b) aplicou rigor de nível A a campos de nível B **contrariando a régua que
ele mesmo havia acordado** — rigor incoerente é tão ruim quanto frouxidão.

## §4 — Total agregado NUNCA sozinho

Total é **cego a erro compensatório**: dois registros com valores trocados somam igual. E
fraude e erro operacional tipicamente **preservam** o total. Sempre acompanhar de:

1. **conferência um a um** por chave confiável — dizer se foi **censo ou amostra**;
2. **agregado na granularidade de uso** (por unidade, por período) — um erro que move valor
   entre unidades preserva o total e destrói as duas;
3. **poder do teste**: quantos registros foram *de fato* comparados, não quantos existem.

**Tolerância decide o que é divergência NOMINAL, nunca o que entra no AGREGADO.** Somar só o
que passou da tolerância esconde compensação sub-tolerância.

## §5 — Diferença aceita ≠ diferença tolerada

Divergência conhecida entra **nomeada uma a uma**, com causa, evidência e status
(`CONFIRMADA` / `NÃO CONFIRMADA`), e a **soma delas tem de explicar exatamente** o total
divergente — resíduo zero. Isso é **prestação de contas**, não faixa de aceitação, e é
estritamente mais forte: registro presente nos dois lados com valor diferente não entra no
esperado, e o resíduo o denuncia.

Fail-closed: divergência **fora** da lista reprova; lista ausente **aborta**; item da lista
que **deixou de divergir** reprova (pin obsoleto é passe-livre latente).

**Marcada-sem-causa é débito**, não validação: entra com teto e prazo de revisão.

## §6 — Materialidade é por UNIDADE DE VEREDITO

**Materialidade aplica-se a níveis B e C apenas. Nível A permanece com tolerância zero
(§3), sem limiar.** Sem esse escopo, esta seção contradiria a §3 e a §8, e permitiria
aprovar diferença de dinheiro por ser "pequena" — o defeito exato que esta skill existe
para impedir.

Dentro de B/C: se o veredito é por período, uma unidade com 3 registros de diferença num
período de 90 mil **não torna o período divergente**. Declarar o limiar relativo **antes**
de medir. As diferenças residuais **continuam sendo item da lista da §5** (com causa e
evidência) — não somem, apenas não derrubam o veredito da unidade.

*Correção que originou:* o executor reportou "reprovado" com 0,01% de divergência em uma
única coluna descritiva. O dono: *"foi um único transporte? e validou linha a linha? então
não tá reprovado"*.

## §7 — Antes de declarar impedimento, procurar a segunda via

*"A fonte X não está disponível"* só é impedimento depois de verificar que X é a **única**
via. E **antes de inferir um mapeamento, procurá-lo no código** que faz a transformação:
quem transforma sabe o de-para, e ele costuma estar escrito.

*Correção que originou:* o executor gerou um de-para por **similaridade de nome** e declarou
o resto bloqueado. O mapeamento estava no código dos dois lados. Trabalho evitável, e
conclusão errada sobre o que estava bloqueado.

## §8 — O veredito

**Ressalva tem definição fechada:** é (i) divergência da lista da §5, com causa e evidência,
ou (ii) limitação de **cobertura declarada** — e, nos dois casos, **com impacto medido**.
Nada além disso é ressalva. Em particular, **item NÃO CONFERIDO não vira ressalva**:
empacotar não-conferido como "ressalva nomeada" e carimbar VALIDADO é o pecado que a §2
proíbe, cometido pela porta dos fundos.

| Veredito | Quando |
|---|---|
| **VALIDADO** | nível A com zero divergência, cobertura completa, nenhuma ressalva aberta |
| **VALIDADO COM RESSALVA** | nível A zero; ressalvas conforme a definição acima |
| **REPROVADO** | qualquer divergência em nível A, ou divergência fora da lista da §5 |
| **INCONCLUSIVO** | conferência que **não executou**, **ou campo de nível A NÃO CONFERIDO** — planejado ou não. Ausência de comparação em dinheiro/documento não aprova nada |

**O veredito declara a cobertura por nível** — quantos campos de A, B e C foram de fato
comparados. Veredito sem cobertura é opinião.

**"Validado com ressalva" é validado.** Negá-lo por perfeccionismo desserve quem decide: o
dono precisa saber que pode usar o dado *e* o que observar. O que não pode é a ressalva
sumir — nem virar guarda-chuva do que não se olhou.

## §9 — Formato de entrega (o que tornou este método utilizável)

**O formato abaixo é RECOMENDADO. O obrigatório é o CONTEÚDO:** as categorias da §2, o
veredito da §8 condicionado aos códigos de saída medidos, o poder do teste declarado, número
**derivado** e não digitado, e um nome de arquivo **estável** além do datado. O artefato pode
ser planilha, Markdown ou equivalente — a planilha é instância, não norma, e num ambiente sem
ela um documento que cumpra §2, §8 e as regras abaixo atende igual.

Ordem recomendada, em **linguagem de negócio**:

1. **LEIA PRIMEIRO** — as grandezas que o dono pediu, uma a uma, em três colunas:
   *assunto · o que ESTÁ validado · o que NÃO está e POR QUÊ*. Termina no **veredito**.
2. **Conferências executadas** — cada uma com seu **código de saída**, mais "o que isto
   valida" e "o que isto **não** valida".
3. **Diferenças** — nomeadas, com causa, evidência e se a causa está confirmada.
4. **Detalhe** por asserção · 5. **Indicadores** · 6. **Pendências** (o quê · por que importa
   · como resolver · o que bloqueia).
7. **Regra de validação** — o critério, escrito **antes** de olhar o resultado.
8. **Glossário** — todo termo técnico traduzido.

Regras do artefato:
- **Nenhum número digitado.** Tudo derivado dos artefatos que as conferências gravam.
  Ausência vira `[ARTEFATO AUSENTE]`, nunca um número plausível.
- **Veredito condicionado aos códigos de saída** medidos na própria execução.
- **Nome de arquivo ESTÁVEL** além do datado (ex.: `STATUS-ATUAL.<ext>`) — ninguém deve
  precisar descobrir qual timestamp é o mais novo. A extensão é do formato escolhido; o que
  a regra exige é o nome que não muda.
- Termo técnico traduzido **na primeira menção**. `flag_x`, "guard", IDs de achado não
  significam nada para quem decide.

*Correções que originaram:* o gerador **declarava** "nenhum número é digitado aqui" e tinha
os números fixos no texto, com veredito estático que continuaria dizendo "PASSOU" com o gate
reprovando; e a pasta acumulou três arquivos datados até o dono perguntar *"que Excel?"*.

## §10 — Regra de ouro

**Declarar a regra não a implementa.** Toda regra desta skill precisa de mecanismo que a
exerça, e o mecanismo precisa ter sido **visto reprovar** pelo menos uma vez. Guard testado
só com dado que passa não é guard.
