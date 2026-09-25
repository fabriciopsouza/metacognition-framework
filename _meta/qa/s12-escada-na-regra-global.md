# QA-evidence — s12-escada-na-regra-global

- **Data:** 2026-09-25T21:49:29Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** inline: decisao explicita do dono (S12, 25/09: 'sim todos') sobre recomendacao ja apresentada
- **RRC:** PASSA
- **Metodo-senior:** N/A: acrescimo de clausula a regra global ja revisada no ADR-116

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| BAIXA | CHANGELOG.md | Redundancia de estilo: a 10a clausula e' citada em dois paragrafos vizinhos. Mantido: um descreve a regra, o outro a prova do canario. |
| BAIXA | docs/specs/plano-modo-planejado/PLANO.md S3 | A conferencia de que a pasta aninhada nao tinha nada pendente nao pode ser refeita porque a pasta foi apagada; e' registro do autor feito antes de apagar. Verificavel hoje: o commit dela esta no remoto. |

## Verificacoes executadas (anti-fabricacao)

- python tools/test_rules_parity.py -> PASS; mutacao clausula a clausula usa len(GLOBAL_RULES) dinamico (revisora)
- python tools/check_rules_parity.py -> PASS (revisora)
- python tools/test_capabilities.py -> PASS (revisora)
- len(GLOBAL_RULES) = 10, batendo com CHANGELOG/ADR-116/capabilities (revisora)
- grep 'primeiro degrau que resolve' em .claude e .agent -> 1 ocorrencia, a propria clausula (revisora)
- test -d da pasta aninhada -> ausente; origin/kiro-ide-adapter com 15018a1 presente (revisora)
