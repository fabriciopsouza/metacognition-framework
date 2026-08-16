# QA-evidence — release-1.80.0-prova-de-mutacao-adr-106

- **Data:** 2026-08-14T02:35:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar
- **Fecha release:** v1.80.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** inline: CAPABILITIES.md e capabilities.json lidos ANTES de projetar (ADR-072); achado que a tecnica de prova por mutacao ja existia no ADR-096 sem ter virado exigencia — o bloco institucionaliza, nao inventa
- **RRC:** PASSA — o critico mediu cada afirmacao verificavel do ADR-106 e do CHANGELOG contra o codigo em vez de aceitar; na rodada 1 achou afirmacao FALSA (fraude sem caso de teste) e reprovou por ela
- **Metodo-senior:** aplicado: docs/adr/106-prova-de-mutacao-para-capacidade-fail-closed.md

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| bloqueante | docs/adr/106-prova-de-mutacao-para-capacidade-fail-closed.md | Rodada 1: o ADR afirmava que as tres fraudes tinham 'cada uma coberta por caso de teste' e a terceira ('canario ja vermelho antes da mutacao') NAO tinha teste. Sabotada a checagem, o canario seguiu 12/12 verde. CORRIGIDO: caso de teste criado, tabela reescrita nomeando o caso de cada fraude, e o episodio registrado no proprio ADR como evidencia de que a norma e' necessaria. |
| bloqueante | tools/test_audit_enforcement.py | Rodada 1: o canario so usava fixtures sinteticas, entao nada no CI auditava o capabilities.json real — o modo (a) era script manual, nao gate. CORRIGIDO: secao que roda o auditor contra o registro real; verificado que run_canaries/CI barram uma capacidade nova sem mutacao. |
| bloqueante | tools/audit_enforcement.py (valida_mutacao) | Rodada 2: o cross-check mutacao x mechanism/test era opt-in ('if mec:' / 'if tst:') e sumia em SILENCIO se a capacidade omitisse os campos — bastava nao declarar mechanism/test para a prova provar qualquer arquivo. CORRIGIDO: ausencia de campo virou falha explicita, com caso de teste dedicado. |
| alto | _meta/enforcement-baseline.json | Rodada 1: escapar do modo (a) bastava acrescentar o proprio id ao passivo. CORRIGIDO: pino BASELINE_N + sha256 no canario; testado que barra adicao e remocao. |
| medio | docs/adr/106 (secao Regua §0) | Rodada 1: o bloco e' adicao pura e nao passa por nenhuma das portas (a)/(b)/(c) do ADR-007. CORRIGIDO: trocado por override explicito do dono, com condicao de quitacao escrita (migrar o passivo). |
| baixo | tools/audit_enforcement.py (--gerar-baseline) | Defeito revelado pela cobertura nova exigida na rodada 1: --gerar-baseline gravava o arquivo e DEPOIS estourava ValueError em relative_to quando o destino ficava fora do repo. CORRIGIDO com try/except e caminho absoluto no fallback. |
| baixo | tools/audit_enforcement.py (modo_provar) e .agent/skills/qa-critic/rules.md | Rodada 1: worktree orfao se o processo morresse no meio (CORRIGIDO com 'git worktree prune' antes de cada prova, e risco declarado no ADR); rule #12 nao nomeava a ferramenta (CORRIGIDO: agora manda rodar tools/audit_enforcement.py --provar). |

## Verificacoes executadas (anti-fabricacao)

- sabotagem 'if antes.returncode != 0' -> 'if False' em copia isolada + rodar o canario: 17/18, FALHA no caso 'canario ja vermelho ANTES da mutacao e' acusado' (achado 1 fechado; reproduzido tambem pelo orquestrador de forma independente antes do registro)
- injecao de capacidade fail-closed sem 'mutacao' no capabilities.json de copia isolada + 'python tools/run_canaries.py test_audit_enforcement': exit 1 — o gate e' real via descoberta automatica do run_canaries e do .github/workflows/ci.yml (achado 2 fechado)
- capacidade fail-closed SEM mechanism/test com mutacao.arquivo para arquivo nao relacionado: antes exit 0 'em conformidade'; depois da correcao exit 1 'sem mechanism e sem test declarado' (bloqueante residual da rodada 2, fechado)
- baseline +1 id -> exit 1 'sha256 DIVERGE'; baseline -1 id -> exit 1 'sha256 DIVERGE' (pino barra adicao E remocao; achado 4 fechado)
- python tools/audit_enforcement.py no capabilities.json real: 24 em conformidade, 0 novas sem prova, 57 no passivo — sem regressao nas 23 fail-closed reais
- python tools/test_audit_enforcement.py: 19/19, exit 0
- conferencia 1:1 dos 6 nomes de caso citados na tabela de fraudes do ADR-106 contra os nomes reais de caso() no canario: todos batem; contagem de resultados.append = 19, bate com '19 verificacoes' do ADR e do CHANGELOG
- APOS o commit: 'python tools/audit_enforcement.py --provar --id enforcement-mutation-audit' -> [PROVADO], a mutacao em tools/audit_enforcement.py deixou tools/test_audit_enforcement.py VERMELHO (codigo 1). Esta prova era impossivel antes do commit (o modo --provar opera sobre o HEAD, por desenho) e estava declarada em 'nao_verificado' na rodada 3 — agora esta EXECUTADA.
