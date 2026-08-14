# QA-evidence — release-1.79.0-project-docs-e-squad-gate

- **Data:** 2026-08-13T23:55:00Z
- **Veredito (passou):** False
- **Recomendacao:** corrigir
- **Fecha release:** v1.79.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** leitura do artefato da rodada 2, do diff main...HEAD (34 arquivos), das ADR-102/103/104 e do ledger de juncoes antes de afirmar qualquer coisa
- **RRC:** PASSA — o critico nao aceitou nenhuma alegacao do autor: rodou squad_gate, handoff, pytest e run_canaries por conta propria, e o orquestrador reproduziu de forma independente os 2 achados antes do registro (inclusive derrubando e depois reconfirmando o achado medio por erro proprio de delimitacao). A reconciliacao encontrada no BLOCO revisado, essa sim, esta incompleta — e o motivo da reprovacao.
- **Metodo-senior:** N/A: revisao adversarial de PROCESSO sobre bloco alheio, sem autoria de norma/spec/ADR nova por parte do critico (fonte_canonica=false).

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| bloqueante | tools/squad_gate.py:147-182 (_release_junction_closed) | O papel `juncao_release` e satisfeito pela PRESENCA de um registro PC/J6 no ledger cujo `bloco` casa com a versao do topo do CHANGELOG, sem checar recencia nem cruzar com o veredito vigente em _meta/qa/. Registro escrito uma vez libera o papel para sempre, mesmo apos reprovacoes posteriores. |
| medio | CHANGELOG.md:18-71 (entrada [1.79.0]) | O commit 6a42ce1 entrega 60 linhas novas em _shared/output-format/SKILL.md (regra de nucleo, Parte A.0) e esta no diff main...HEAD desta release, mas a entrada [1.79.0] do CHANGELOG nao o cita em nenhuma secao. Doc-sync incompleto. |

## Verificacoes executadas (anti-fabricacao)

- python tools/squad_gate.py --paths CHANGELOG.md -> 'OK — evidencia atestada presente para os papeis exigidos' (REPRODUZIDO pelo orquestrador)
- leitura de _meta/qa/junctions/v1.79.0-project-docs-e-squad-gate.jsonl -> 1 unica linha; o campo `evidencia` dela diz literalmente 'REPROVOU a 1a rodada com 2 bloqueantes' — um registro de reprovacao gravado como PASS de juncao
- git log --diff-filter=A -- _meta/qa/junctions/v1.79.0-*.jsonl -> registro introduzido em 4faf971, o PRIMEIRO commit da serie; 10 commits vieram depois, incluindo a rodada 2 que reprovou com 2 bloqueantes novos (REPRODUZIDO)
- leitura de tools/test_squad_gate.py inteiro -> nenhum teste exercita 'reprovar depois de PC registrado'; so match de versao, tipo de juncao e ledger corrompido
- python tools/squad_gate.py --paths-from <34 paths do diff main...HEAD> -> BLOQUEADO fail-closed por falta de qa_critic escopado (comportamento CORRETO para o papel qa_critic)
- delimitacao exata da entrada [1.79.0] do CHANGELOG (linhas 18-71) -> 0 mencoes a 'output-format', embora 6a42ce1 (_shared/output-format/SKILL.md, +60 linhas) esteja no diff da release (REPRODUZIDO; a 1a checagem do orquestrador usou faixa errada e deu falso negativo)
- python tools/handoff.py -> 'Proximo passo' extraido bate com o checkpoint 2026-08-13 do history.md, sem truncar nem engolir o campo seguinte (os defeitos r5/r6/r7 do regex nao reincidem)
- python -m pytest tools/test_handoff.py tools/test_squad_gate.py tools/test_qa_evidence_integrity.py -q -> 19 passed
- python tools/run_canaries.py -> 64 PASS / 1 SKIP / 2 FAIL (test_posture_gate, test_qa_evidence), ambos por ausencia de veredito aprovativo do release — esperado, nao e defeito a corrigir
- python tools/test_capabilities.py -> PASS, incluindo check_tag_enforcement_coerente
- leitura de tools/squad_gate.py + docstring + ADR-103/104 + capabilities.json + CAPABILITIES.md -> o estado declarado (advisory) bate em todos os lugares; a incoerencia das rodadas anteriores nao reincide
- leitura de .github/workflows/ci.yml -> fetch-depth 0, base.sha do evento e --paths-from coerentes com o ADR-104
