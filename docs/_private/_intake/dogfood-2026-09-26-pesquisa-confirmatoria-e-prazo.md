# Dogfood 26/09/2026 — pesquisa confirmatória e prazo (programa de faixa de lote, MRP)

**Tipo:** análise e proposta para decisão do dono. Nada foi alterado em skill, regra, workflow ou ADR.
**Autor:** sessão Opus 5.5 do framework · 26/09/2026.
**Fonte avaliada:** `C:\Users\fabriciosouza\Downloads\2026-09-11-MRP\_analise-agente-2026-09-22\programa-faixa-lote\REGISTRO-CONVERSA-DOGFOOD.md`
(26/09 11:09), escrito por outra IA no papel de desenvolvedora. Tratado como dado externo, não como verdade.
**Evidência consultada (mesma pasta, salvo indicação):** `00-COMECE-AQUI-desenvolvimento.md`, `01-PESQUISA.md` (25/09
19:00), `02-ESPECIFICACAO.md` (25/09 23:58), `04-RESPOSTAS-PRE-VOO.md` (26/09 01:14);
`C:\Users\fabriciosouza\Downloads\2026-09-11-MRP\_analise-agente-2026-09-22\FILA-PENDENCIAS.md` (T25),
`...\HANDOFF.md`, `...\PLANO-MRP.md`; no framework: `.agent/skills/discovery/SKILL.md`,
`.agent/skills/discovery/metodo-senior.md`, `.agent/skills/discovery/pesquisa-cascata.md`,
`.agent/skills/architect/SKILL.md`, `_shared/discovery/elicitation-dimensions.md`, `tools/check_spec_depth.py`,
`tools/test_discovery_eval.py`.
Classificação: **C** confirmado no arquivo citado · **I** inferido · **D** desconhecido.

## 1. Veredito por achado

| # | Achado do registro | Veredito | Evidência |
|---|---|---|---|
| 0 | (seção 1) "`04-RESPOSTAS-PRE-VOO.md` está inteiramente vazio, as 8 respostas em branco" | **NÃO PROCEDE** contra o arquivo atual | O `04` foi gravado em 26/09 01:14, antes do registro (11:09), e traz as respostas 1 a 4 preenchidas em parte (linhas 22–25) (C). Qual versão a outra IA leu: **D**. A parada continua correta por outro motivo: a linha 1 diz "INCOMPLETA" e a 8 "DECISÃO PENDENTE", e `00-COMECE-AQUI` §1 (linha 11) manda parar nos dois casos (C). |
| 1 | Pesquisa confirmatória, não divergente | **PROCEDE PARCIAL** | Procede: a pergunta de `01-PESQUISA.md` (linha 7) já parte da solução, e a tabela de caminhos (linhas 16–21) compara só *meios* de gravar (C). Não procede como erro da pesquisa: o escopo estreito **já tinha sido aprovado pelo dono** antes da pesquisa (`FILA-PENDENCIAS.md`, T25: "Programa 1 (aprovado pelo dono em 25/09) [...] Programa 2 [...] só se pedirem") (C); a especificação declara o que fica fora (`02` §2) (C); e o motivo técnico do recorte é real: só a versão de produção tem caminho liberado confirmado (`01`, linha 18; receita/lista técnica em massa = D) (C). A falha real é mais estreita: nenhum artefato mostrou ao dono o nível de escopo **imediatamente acima**, de baixo custo e relevante em GxP (retrato do estado anterior reimportável = plano de volta). O "antes" existe só como log (`02` U5), sem restauração (C). |
| 2 | O gate de início funcionou | **PROCEDE** | A IA parou sem escrever código e sem inventar nomes (C, registro §1 e §4). O motivo que ela declarou estava errado (achado 0), mas a decisão estava certa. |
| 3 | Restrição de prazo não elicitada; "não estava nos artefatos até o dono mencionar" | **NÃO PROCEDE** como escrito · **PROCEDE** num ponto mais estreito | O prazo estava registrado antes da pesquisa: `HANDOFF.md` linha 3 (23/09: "Go-live: 01/12/2026 · Marco real: 01/11/2026") e `PLANO-MRP.md` linha 8 (C). A falha real: `01-PESQUISA.md` e `02-ESPECIFICACAO.md` não citam o marco nem dizem onde o programa fica no caminho crítico (C, lidos por completo). A restrição **conhecida** não foi levada para dentro do entregável; não houve falha de elicitação. |
| 4 | Não separar bloqueio de escopo de bloqueio de execução | **NÃO PROCEDE** como falha observada | O próprio agente manteve o bloqueio de execução à vista durante o debate de escopo: registro §2.4 ("o bloqueio de hoje não é escopo, é o pré-voo vazio") e §4 ("Bloqueio único e acionável") (C). Achado hipotético, sem caso. |
| 5 | Correção de caminho por file-first | **PROCEDE** | Registro §1 (C). Caso positivo; nada a mudar. |

**Achado que o registro não fez:** o próprio registro afirma um fato que o arquivo contradiz (achado 0). O relatório de
uma IA sobre outra também precisa ser validado arquivo a arquivo, como o dono fez aqui.

## 2. Crítica da sugestão

1. **Concordo em parte com "confirmatória".** O recorte foi decidido pelo dono e tem razão técnica e de prazo. Ampliar para "exportar e importar todas as características" e "revisão de receitas em massa" (N3 do registro) seria erro de projeto: não há caminho liberado confirmado (D), o objeto é o mais regulado em GMP e o marco real é 01/11. O que faltou foi pouco: uma linha que mostrasse ao dono "um nível acima custaria X e caberia ou não no marco".
2. **"Não elicitou o prazo" erra o diagnóstico.** O prazo era conhecido, e elicitá-lo de novo não mudaria nada. O que muda é obrigar o entregável a declarar o marco e a posição dele no caminho crítico.
3. **A proposta do registro (passo novo de "enquadramento de escopo" na skill) duplica o que existe:**
   - `metodo-senior.md` linha 78 já manda listar "alternativas não-avaliadas" nas Antecipações;
   - `architect/SKILL.md` linha 27 exige 3 alternativas ou mais, uma podendo ser "não fazer";
   - `pesquisa-cascata.md` linha 38 cobra "viés de confirmação";
   - `discovery/SKILL.md` linhas 80 e 82 listam prazo em "Não-funcional" e "Restrições".

   Tudo isso é prosa. Nenhum gate lê as Antecipações (grep em `tools/*.py`: nenhum leitor) (C). Pela lição "regra escrita não vincula sem mecanismo", acrescentar outro parágrafo repetiria a falha.
4. **O achado 4 não justifica mudança:** não houve falha observada.

## 3. Mudanças propostas (régua de ganho líquido aplicada)

| # | Mudança | Onde (arquivo existente) | Critério da régua | Decisão |
|---|---|---|---|---|
| M1 | Uma linha no banco de dimensões: `escopo-e-prazo`, obrigatória. Pergunta-guia: "Qual o marco que governa e onde este entregável fica no caminho crítico? Um nível de escopo acima e um abaixo do pedido, com custo e se cabe no marco." Aliases: `prazo, marco, caminho-critico, escopo-alternativo`. Funde os achados 1 e 3 numa só dimensão, porque é o prazo que decide entre os níveis. | `_shared/discovery/elicitation-dimensions.md` (1 linha da tabela lida pelo gate) + `docs/specs/_template-spec-unico/spec.md` (1 linha na lista de dimensões) | **(c)**: faz o `check_spec_depth` medir o que hoje é prosa em 4 lugares, editando o banco existente, sem arquivo novo | **✅ aprovada pelo dono (26/09) e implementada**: emenda 2 do ADR-033; prova no `test_spec_unico` (j), com o conjunto esperado escrito literalmente (apagar a linha do banco deixa o canário vermelho) |
| M2 | A dimensão de M1 é cobrada **só no arquivo único de especificação** (`spec.md` com a marca do ADR-117), que é o formato de todo trabalho novo; o formato antigo não muda de veredito | `tools/check_spec_depth.py` (a obrigatoriedade passa a poder valer só para o arquivo único) | consequência de M1: evita decisão inventada para o passado e não deixa frase de exceção que uma especificação nova poderia copiar | **✅ implementada** (valor `obr=unico`, ADR-120) |
| M3 | Passo novo de "framing" na skill (proposta do registro) | — | nenhum: é adição pura e duplica o existente (crítica 3) | **descartada** |
| M4 | Sinalizar o gate de execução aberto durante debate de escopo | — | nenhum: sem falha observada (achado 4) | **descartada** |

**Estado medido do gate (revisão isolada, 26/09):** `python tools/check_spec_depth.py` sem argumento já reprova 9
das 11 especificações antigas, que não têm a seção de dimensões. A varredura sem argumento não é gate hoje; o gate é
a aplicação especificação a especificação na junção J1. Por isso a correção de M2 não depende de mexer no passado.

**Alternativas descartadas:**
- dimensão opcional (`obr: nao`): só gera aviso, e gate que não barra não conta (ADR-106);
- linha "não elicitado" nas especificações antigas: não resolve (elas já falham por outro motivo) e cria uma frase
  de exceção que qualquer especificação nova poderia copiar;
- apelido numa dimensão existente: `escopo-temporal` trata da janela dos dados do produto, não do prazo do projeto.
  Apelido frouxo já gerou PASS falso nesse parser (`check_spec_depth.py`, comentário das linhas 135–136).

**ADR:** M1 muda o contrato do gate J1 para todas as especificações, então pede uma **emenda ao ADR-033** (banco de
dimensões). Nenhum ADR novo.

## 4. Canário que provaria a mudança (M1)

Em `tools/test_discovery_eval.py`, sem arquivo novo:
1. A saída sênior sintética ganha `- escopo-e-prazo: marco 01/11 (plano de dezembro); acima: retrato reimportável, +2 dias, cabe; abaixo: carga manual` e continua **PASS**.
2. A mesma saída **sem** a linha dá **FAIL** no `check_spec_depth` com `escopo-e-prazo` na lista de faltantes.
3. Com a linha em placeholder (`escopo-e-prazo: <...>`), dá **FAIL**.
4. Mutação: apagar a linha do banco faz o caso 2 passar, e então o canário tem de ficar vermelho.

**Limite declarado:** o gate prova que a decisão foi registrada, não que ela é boa (mesmo limite do ADR-033). A
qualidade do "nível acima" continua a cargo da revisão adversarial.

**Escopo desta análise:** só o comportamento agnóstico do framework. Nenhuma recomendação ao projeto de domínio.

## 5. Revisões adversariais

| Rodada | Revisor | Veredito | Achados | O que mudou |
|---|---|---|---|---|
| 1 | Sonnet isolado, segundo plano (a4fa7f555844f7165) | PASS-COM-RESSALVAS | ALTA: justificativa de M2 falsa (9 das 11 especificações já reprovam hoje, sem relação com M1). MÉDIA: frase de exceção de M2 copiável por especificação nova. BAIXA: citação 80–82 incluía linha irrelevante | M2 refeita (cobrança só no arquivo único); estado medido do gate declarado; alternativas descartadas registradas; citação corrigida. Citações, vereditos, M1 e canário confirmados pela revisora |
