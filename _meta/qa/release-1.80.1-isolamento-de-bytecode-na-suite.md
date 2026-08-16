# QA-evidence — release-1.80.1-isolamento-de-bytecode-na-suite

- **Data:** 2026-08-16T04:30:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar
- **Fecha release:** v1.80.1

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** leitura das funcoes alteradas e varredura dos writes de todos os canarios antes de afirmar sobre vazamento entre eles
- **RRC:** PASSA — o critico refez a sabotagem no worktree e leu o resultado, em vez de aceitar a mensagem do commit; e derrubou o proprio ataque principal por varredura de codigo, declarando o metodo.
- **Metodo-senior:** N/A: correcao de mecanismo sob ADR ja aceito.

## Problemas

_nenhum_

## Verificacoes executadas (anti-fabricacao)

- worktree isolado em 1da9b74; baseline python tools/test_run_canaries.py -> PASS (5 verificacoes)
- sabotagem por conta propria em run_canaries.py (env sem PYTHONPYCACHEPREFIX) -> o caso comportamental virou [FALHA] com a evidencia 'verificador devolveu 0 com o .pyc envenenado ainda presente no disco', e o canario saiu com codigo 1. A prova do autor NAO e' encenacao
- varredura de write_text e open(...,'w') em todos os tools/test_*.py: nenhum escreve .py sob ROOT; fixtures vao para mkdtemp/TemporaryDirectory unicos por canario
- conferencia de que audit_enforcement.py usa prefixo PROPRIO + PYTHONDONTWRITEBYTECODE, isolado do prefixo do runner
- autor: 3 tentativas de correcao, as duas primeiras REPROVADAS pelo canario novo — proibir escrita nao impede leitura; proibir escrita + prefixo vazio custou 72s -> mais de 2 minutos
- autor: benchmark antes/depois em worktree — 72s (sem isolamento) contra 76s (com prefixo novo por execucao), 5% de custo
- autor: a sabotagem declarada da capacidade nova era NEUTRALIZADA pelo proprio auditor (lia a variavel de ambiente que o auditor define); trocada por uma que remove a chave de forma incondicional
- suite completa 68 PASS / 1 SKIP / 0 FAIL de 69 canarios; capacidades com gate provado 24 -> 28
