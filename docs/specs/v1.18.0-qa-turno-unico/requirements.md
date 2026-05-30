# Requirements — v1.18.0 QA turno único + heterogeneidade (Onda 4)

## Objetivo
Capturar o que o "Conclave" de 3 papéis teria de útil — a custo ~zero — dentro do qa-critic existente:
protocolo de 1 turno (steelman→ataque→veredito) + heterogeneidade de modelo + disparo condicional.
Rejeitar a estrutura de 3 papéis (P6: homogêneo reforça viés; MAD não supera self-consistency).
EMENDA ao Princípio 13. Agnóstico.

## Escopo IN
- +seção no `.agent/skills/qa-critic/SKILL.md` (protocolo 1 turno + heterogeneidade + disparo condicional).
- Nota em `_meta/subagent-isolation.md` (heterogeneidade gerador↔crítico).
- ADR-018.

## Escopo OUT
- Conclave de 3 papéis (gerador/defensor/sintetizador) — **REPROVADO** (P6).
- Calibração do par gerador↔crítico ótimo — [DESCONHECIDO], "a calibrar".
- Mudança no frontmatter de contrato do qa-critic (intacto).

## Requisitos
- REQ-1: Protocolo steelman→ataque→veredito no MESMO turno, sem papéis novos.
- REQ-2: Heterogeneidade de modelo priorizada como alavanca causal (sobre estrutura de debate).
- REQ-3: Disparo condicional honra o Self-Critique Paradox (silenciar em rotina de alta confiança).
- REQ-4: Honestidade ide↔chat — heterogeneidade indisponível no chat declarada, não fingida.
- REQ-5: Veredito binário mantido (APROVADO_LIMPO|REPROVADO) — coerente com J4/ADR-011.
- REQ-6: Régua §0 — densificação (+1 seção + nota), nenhum papel/skill/subagente novo.
- REQ-7: Agnóstico de domínio.

## Bloqueadores honestos (P11)
- Par gerador↔crítico ótimo [DESCONHECIDO] — default = família distinta da do gerador.
- Aceitação regulatória de "subagente heterogêneo = revisor independente" [DESCONHECIDO] (dedução).
- Impacto da indisponibilidade de heterogeneidade no chat [DESCONHECIDO].
