# QA-evidence — release-1.85.0-quadro-de-gestao-e-canarios-que-mentiam

- **Data:** 2026-08-16T17:40:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas
- **Fecha release:** v1.85.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** inventario dos guias existentes antes de propor documento novo (nenhum foi criado: o runbook virou secao do SETUP.md); leitura das fontes reais antes de julgar o quadro
- **RRC:** PASSA — o critico mediu o tempo real do verificador em vez de estimar, comparou o quadro contra as fontes item a item, e reportou explicitamente que uma das suas tres sabotagens ficou VERDE, identificando isso como o defeito e nao como falha do metodo dele.
- **Metodo-senior:** N/A: ferramenta de gestao sob ADR ja aceito.

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| alto | tools/test_projeto_docs.py (fixture da nota de higiene) | CORRIGIDO. O caso passava por vacuo: a nota vinha antes do primeiro item, onde o parser a descarta por outro motivo. Sabotar a protecao mantinha o verde. |
| alto | tools/projeto_docs.py (parser e --verificar) | CORRIGIDO. Sub-itens colapsavam num card; o verificador comparava so titulos, entao mudanca em sub-item passava despercebida e CSV editado a mao passava verde. |
| medio | tools/hooks/consistency_gate.py x tools/projeto_docs.py | CORRIGIDO. O --verificar rodava a suite (98,6s) sob timeout de 120s com except-pass — dia lento deixava quadro desatualizado passar em silencio. |
| baixo | tools/projeto_docs.py (fim de secao) | CORRIGIDO. O tracinho apos a secao entrava no detalhe do ultimo item. |
| alto | tools/test_qa_evidence.py (constante duplicada) | CORRIGIDO no mesmo bloco, a pedido do dono. O canario REDEFINIA APPROVING em vez de importar do mecanismo: nao dependia do codigo que devia guardar. Teste que duplica a regra confirma a si mesmo. |
| alto | tools/test_post_canary_status.py (nome do check) | CORRIGIDO no mesmo bloco. Nao cobria o nome do status publicado, unico elo entre o script e a protecao da branch. |

## Verificacoes executadas (anti-fabricacao)

- R1 conferiu o quadro gerado contra as fontes item a item: nenhum item de 1o nivel sumiu ou duplicou; CSV com aspas e virgulas escapadas corretamente, BOM correto para Excel e inocuo para Trello/Planner
- R1 mediu o tempo real do --verificar: 98,6s contra timeout de 120s no gate — margem de ~20%
- R1 provou 2 sabotagens por conta propria e restaurou por copia de backup, sem git, confirmando identidade byte a byte
- R1 reportou que a 3a sabotagem (a do achado 1) ficou VERDE — e o defeito, nao falha da prova
- correcao do achado 1: fixture passa a por a nota DEPOIS do primeiro item, como no history.md real; caso novo confere que a nota tambem nao gruda no detalhe. Sabotando o skip agora: [FALHA], codigo 1
- correcao do achado 2: sub-item indentado vira card proprio (6 -> 15 cards no quadro real) e o --verificar compara os CSV byte a byte contra o que seria gerado agora
- correcao do achado 3: --verificar deixa de montar a secao 'Estado agora', que rodava a suite e era descartada na comparacao
- correcao do achado 4: o tracinho de fim de secao encerra a leitura
- CONSERTO DOS DOIS CANARIOS FRACOS (pedido do dono, nao adiado): test_qa_evidence REDEFINIA a constante APPROVING em vez de importa-la do mecanismo — tinha a propria copia da regra e nao dependia do codigo que devia guardar; passa a importar. test_post_canary_status nao cobria o NOME do status publicado, unico elo com a protecao da branch; sabotando CONTEXT agora: 2 falhas nomeadas, codigo 1
- canario do quadro: 21 -> 22 verificacoes
