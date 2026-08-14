# QA-evidence — release-1.79.0-project-docs-e-squad-gate

- **Data:** 2026-08-14T01:48:52Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas
- **Fecha release:** v1.79.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** inline: CAPABILITIES.md e capabilities.json lidos; nucleos vizinhos inspecionados; corpus do history.md varrido com detector proprio
- **RRC:** PASSA — o critico mediu cada afirmacao verificavel do ADR-105 e do CHANGELOG em vez de aceitar; achou 3 divergencias reais
- **Metodo-senior:** aplicado: docs/adr/105-extracao-de-campo-do-p14-e-decisao-de-desenho.md

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| medio | docs/adr/104:48; history.md:48; run_canaries.py:66; test_squad_gate.py:220 | Numero stale '19 casos de teste' em 4 lugares; o real medido e 20 — CORRIGIDO trocando o numero fixo por CONSULTA, aplicando o principio do ADR-105 |
| medio | CHANGELOG.md entrada [1.79.0] | Nao citava a Parte A.0 de _shared/output-format/SKILL.md; achado da 3a rodada que sobreviveu 7 commits — CORRIGIDO |
| menor | tools/test_squad_gate.py:290 | Comentario datado 2026-08-14, um dia a frente do commit real — CORRIGIDO |

## Verificacoes executadas (anti-fabricacao)

- git diff main -- tools/handoff.py tools/test_handoff.py -> VAZIO (reversao do ADR-105 limpa)
- python tools/handoff.py -> campo Objetivo sai COMPLETO (mitigacao do custo declarado funciona)
- ADR-105 medido afirmacao a afirmacao: template documenta 5 campos (CONFIRMADO); codigo listava 11 (CONFIRMADO); corpus usa 9 rotulos fora da lista (CONFIRMADO EXATO); 'Nomenclaturas:' puro 26x vs 4x da forma canonica (CONFIRMADO EXATO)
- _shared/project-docs/SKILL.md lida na integra: contagens internas batem (7 propriedades, 6 modos de falha, 4 gates, 15 arquivos), marcas de confianca coerentes
- python tools/run_canaries.py -> 64 PASS / 1 SKIP / 2 FAIL (os 2 aguardam este veredito)
- pytest tools/test_squad_gate.py -q -> 20 passed
- python tools/test_consistency_closing.py -> PASS (100 ADRs, 0 duplicata)
- python tools/test_qa_evidence_integrity.py -> PASS (nenhuma divergencia .json x .md)
- matriz do behaviors/manifest.json: 7 entries novos confirmados
- ci.yml:65-82 confirmado continue-on-error: true, so em PR e ubuntu-latest
