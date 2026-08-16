# QA-evidence — release-1.84.0-conformance-de-topologia

- **Data:** 2026-08-16T16:10:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas
- **Fecha release:** v1.84.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** leitura do ADR-097 e do modelo formal antes de julgar o verificador; construcao dos traces a partir das regras declaradas, nao de intuicao
- **RRC:** PASSA — o critico nao aceitou a demonstracao do autor: escolheu de proposito sabotar uma regra que o teste do autor NAO cobria, e foi assim que mediu se o canario tinha valor real.
- **Metodo-senior:** N/A: implementacao de ADR ja desenhado, sem autoria de norma nova.

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| critico | tools/conformance.py (avaliar_trace) | CORRIGIDO. A flag `rewind: true` isolada desligava forward-only E sem-salto em qualquer direcao, contando o passo como aceito. Esvaziava o proposito central do ADR. |
| medio | tools/conformance.py (avaliar_trace) | CORRIGIDO. `status` nao era validado contra conjunto fechado; string arbitraria escapava das comparacoes e o passo contava como aceito. |
| medio | tools/qa_evidence.py (_validar_prova) | CORRIGIDO NO TEXTO, nao no comportamento — por decisao. A validacao confere que o ponteiro RESOLVE, nao que seja relevante nem que o digest corresponda a algo. Conferir relevancia exigiria semantica; conferir digest exigiria a fonte. O docstring passou a declarar as duas ausencias, porque chamar de 'ponteiro verificavel' sem elas era overclaim. |
| baixo | tools/conformance.py (fitness de trace vazio) | CORRIGIDO. Trace sem nenhum passo devolvia 1.0, indistinguivel de fluxo inteiro bem executado. |

## Verificacoes executadas (anti-fabricacao)

- R1 construiu os traces adversariais e reproduziu cada um por chamada direta a avaliar_trace
- R1 provou a falsificabilidade do canario sabotando uma regra DIFERENTE da que o autor ja cobria (sem-salto em vez de forward-only): 3 falhas especificas, exit 1; restaurou por copia de backup, sem git, e confirmou identidade byte a byte
- R1 confirmou que a arvore ficou identica ao inicio, sem arquivo espurio
- correcao do CRITICO: rewind so' vale declarado no `status` E regredindo em ordem; flag sem status e' violacao nomeada; rewind que nao regride e' salto mascarado, tambem violacao
- correcao: STATUS_VALIDOS como conjunto fechado; status fora dele e' violacao
- correcao: trace vazio devolve fitness 0.0 e violacao `vacuo` — ausencia de dado nao e' conformidade
- correcao: o teto real da validacao de prova passou a ser declarado nos dois arquivos, e o canario deixou de usar o mesmo arquivo como prova de todas as juncoes
- canario 15 -> 20 verificacoes; suite 75 PASS / 1 SKIP / 0 FAIL de 76
- primeira execucao sobre o ledger real: 6 blocos, um com fitness 0.0 (juncao final sem nenhuma anterior)
