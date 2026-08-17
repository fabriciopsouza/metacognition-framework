# QA-evidence — release-1.87.0-alarme-de-deriva-das-distribuicoes

- **Data:** 2026-08-17T03:20:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas
- **Fecha release:** v1.87.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** leitura do historico da deriva antes de julgar o desenho; medicao das tags recentes para avaliar se a tolerancia geraria ruido
- **RRC:** PASSA — o critico nao revisou o que o alarme faz, revisou como ele PODE FICAR CALADO, que e a unica pergunta que importa num alarme; e mediu a tolerancia contra o historico real de releases em vez de opinar sobre ela.
- **Metodo-senior:** N/A: ferramenta nova sob ADR ja aceito.

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| alto | tools/shadow_drift.py (codigo de saida) | CORRIGIDO. Duvida por sombra nao afetava o exit code. Com todas em duvida, o alarme saia zero indefinidamente. |
| alto | tools/shadow_drift.py (leitura do workflow) e tools/test_shadow_drift.py | CORRIGIDO. Aspas simples ou rename zeravam a lista e viravam SKIP; e o canario so exercitava um workflow fake, sem exigir a leitura do real. |
| medio | guia/web/index.html (rotulo do grupo de 27) | CORRIGIDO. O rotulo dizia 'nao-bloqueante (aviso, registro, prosa)' para um grupo que inclui garantia fisica. A contagem fechava; a descricao mentia. |

## Verificacoes executadas (anti-fabricacao)

- R1 reproduziu os dois cenarios mudos por monkeypatch, sem tocar arquivo: gh sem permissao e mensagem sem SHA -> exit 0
- R1 reproduziu o regex falhando com aspas simples: re.findall devolve lista vazia
- R1 mediu a tolerancia contra o historico real: releases empurram 2 a 4 commits, o publish dispara a cada push, em regime normal o atraso e ~0 — tolerancia de 3 nao vira ruido. Sem achado nesta pergunta
- R1 derivou as contagens da vitrine e apontou que o rotulo de um grupo estava impreciso
- correcao do ALTO 1: duvida passa a sair com codigo 2, distinto de 1 (atrasada) e de 0 (em dia). Os codigos estao documentados no cabecalho
- correcao do ALTO 2: workflow que EXISTE mas nao foi entendido deixa de virar SKIP e passa a ser reportado como defeito, com codigo 2 — arquivo local ilegivel nao e' ausencia de dado
- correcao do ALTO 2, parte do canario: caso novo exige que sombras() leia as 5 distribuicoes do workflow REAL deste repositorio, nao so do fake
- correcao do MEDIO: o rotulo passa a dizer 'aviso, registro, prosa, garantia fisica'
- prova de mutacao da guarda nova: sabotando o retorno de duvida para 0, o caso 'todas em DUVIDA sai com codigo 2' fica [FALHA] e o canario sai com 1; restaurado, 19/19
- canario 14 -> 19 verificacoes; medicao real contra as 5 distribuicoes: 2 commits atras, dentro da tolerancia
