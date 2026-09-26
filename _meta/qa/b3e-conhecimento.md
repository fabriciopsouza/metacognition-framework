# QA-evidence — b3e-conhecimento

- **Data:** 2026-09-26T18:10:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** docs/specs/b3-documentacao-regulada/spec.md (REQ-16 a 18, criterios 17 a 19, Replanejamento 26/09)
- **RRC:** PASSA
- **Metodo-senior:** aplicado: cada achado reproduzido em copia

## Substitui vereditos anteriores deste bloco

- rodada 1 · 2026-09-26T16:40:00Z · **corrigir** · sha `6f247369cbdc` · agentId `ae8eb988d9d5e2a16`
  - cobria 31 caminho(s): .agent/skills/discovery/SKILL.md, .agent/skills/docops/SKILL.md, .claude/global/CLAUDE-global.md, CAPABILITIES.md …
- rodada 2 · 2026-09-26T17:30:00Z · **corrigir** · sha `6f247369cbdc` · agentId `ab523c78962d0b793`
  - cobria 31 caminho(s): .agent/skills/discovery/SKILL.md, .agent/skills/docops/SKILL.md, .claude/global/CLAUDE-global.md, CAPABILITIES.md …
- rodada 3 · 2026-09-26T18:10:00Z · **aprovar** · sha `6f247369cbdc` · agentId `a1c73b1fdf84cdf66`
  - cobria 31 caminho(s): .agent/skills/discovery/SKILL.md, .agent/skills/docops/SKILL.md, .claude/global/CLAUDE-global.md, CAPABILITIES.md …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/conhecimento.py:_blocos | campos antes do primeiro ## somem sem achado |
| ALTA | tools/conhecimento.py:_blocos | entrada escrita com ### se funde a anterior |
| MEDIA | tools/conhecimento.py:PROIBIDOS | prosa que descreve campo 'token' acusada como credencial |
| MEDIA | tools/check_spec_depth.py:main | rotulo n/n global no arquivo unico |
| MEDIA | tools/knowledge_catalog.py:cmd_recall | biblioteca vazia da exit 2 e manda rodar --build |
| BAIXA | .claude/global/CLAUDE-global.md secao 9 | caminho relativo para knowledge_catalog |
| ALTA | tools/conhecimento.py:_ler_entradas | campo depois do bloco de codigo de uma consulta e acusado e descartado |
| MEDIA | tools/conhecimento.py:PROIBIDOS | credencial com texto a direita ou em cabecalho Authorization escapa |

## Verificacoes executadas (anti-fabricacao)

- reproducao das correcoes da rodada 2 em copia
- regressao da rodada 1 conferida
- falso positivo de credencial em prosa: nenhum
- test_conhecimento, test_spec_unico, check_rules_parity, check_core_agnostic, test_marketing_claims, test_capabilities -> PASS
