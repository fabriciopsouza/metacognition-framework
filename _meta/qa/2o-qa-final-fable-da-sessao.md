# QA-evidence — 2o-qa-final-fable-da-sessao

- **Data:** 2026-08-20T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** —
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/test_handoff.py + tools/model-policy.json:roles | precedencia SEGURANCA > autoral declarada e nao testada: mover a regra qa/critic para o fim mantinha a suite verde com QA composto resolvendo para o modelo do autor. Cartesiano QA x demais adicionado; a mutacao acusa 210 composicoes. |
| ALTA | docs/adr/111 (Contexto x Alternativas recusadas) | o ADR afirmava, em dois lugares, coisas incompativeis sobre o que o dono mandou desfazer — e a versao errada era a que sustentava a recusa da alternativa enxuta. Reconciliado com o que de fato ocorreu: tres decisoes revisitadas, so uma era regra. |
| MEDIA | tools/model-policy.json:qa_final_duplo.passo_2 | a autorizacao do degrau acima era verificada por SUBSTRING em prosa; inverter o sentido mantendo as palavras-chave passava verde. A decisao saiu da prosa e virou booleano `roda_sem_resposta`, que o canario checa por identidade. |
| MEDIA | CHANGELOG.md | o gate de procedencia narrativa (commit 4c19a6c) nao estava no CHANGELOG, e a decisao do dono sobre a calibragem so vivia em comentario de codigo. |
| MEDIA | tools/model-policy.json:model_ids.sonnet | dizia claude-sonnet-4-6 enquanto as atestacoes registravam claude-sonnet-5 — o irmao do defeito anotado no opus horas antes. A licao nao foi propagada aos irmaos na mesma iteracao; foi preciso outro critico. |
| BAIXA | docs/adr/110 | a frase que o proprio ADR declara falsificada ressuscitava verbatim mais adiante no mesmo documento — efeito de contar a mesma historia em cinco lugares. |

## Verificacoes executadas (anti-fabricacao)

- moveu a regra qa/critic para o fim de roles em copia e provou suite verde com QA no modelo do autor
- inverteu o sentido de passo_2.autorizacao mantendo palavras-chave e provou exit 0
- conferiu 5 alegacoes narrativas dos ADR contra a fonte: 112, 96, canario do cross-ai, caso inventado nunca commitado, contagem de achados do ledger — todas batem
- reproduziu as mutacoes do 1o critico e confirmou que as correcoes dele sao honestas
- leu ADR-109, ADR-110 e ADR-111 em sequencia procurando contradicao entre pecas
- conferiu model_ids contra o modelo realmente registrado nas atestacoes
- rodou run_canaries: 80 PASS, 1 SKIP, 0 FAIL
- autor apos as correcoes: mutacao da regra de seguranca -> 210 composicoes acusadas
- autor apos as correcoes: inversao semantica -> reprova pelo booleano
