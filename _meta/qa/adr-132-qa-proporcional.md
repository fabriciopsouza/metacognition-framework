# QA-evidence — adr-132-qa-proporcional

- **Data:** 2026-10-26
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** —
- **Metodo-senior:** —

## Substitui vereditos anteriores deste bloco

- rodada 2 · 2026-10-26 · **aprovar_com_ressalvas** · sha `d084443+stag` · agentId `aa3b306bdb1abaaae`
  - cobria 15 caminho(s): .agent/skills/qa-critic/SKILL.md, .agent/workflows/checkpoint.md, .agent/workflows/feature-plan.md, .agent/workflows/handoff.md …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| alto | .agent/skills/qa-critic/SKILL.md | r1: F0/F1 sem gatilhos de alto risco |
| alto | .agent/workflows/handoff.md | r1: process-critic mandatorio em todo bloco em 4 textos |
| medio | .claude/global/CLAUDE-global.md | r1: quem decide a faixa / F0 sem freio |
| medio | .claude/global/CLAUDE-global.md | r1: abuso so na skill |
| medio | docs/adr/132-qa-proporcional-por-faixa.md | r1/r2: mapa de impacto (10 textos) |
| baixo | docs/adr/132-qa-proporcional-por-faixa.md | r1: D5 e descartes |
| baixo | .claude/global/CLAUDE-global.md | r2: permissao/credencial sem gatilho |
| baixo | .agent/skills/qa-critic/SKILL.md | r2: frase truncada na skill |

## Verificacoes executadas (anti-fabricacao)

- r1: leitura do diff contra relatorio de pesquisa, ADR-011/110/118 e skill qa-critic
- r2: conferencia dos achados r1; test_adr_changelog_sync.py PASS; check_rules_parity.py PASS; test_capabilities nao barra
