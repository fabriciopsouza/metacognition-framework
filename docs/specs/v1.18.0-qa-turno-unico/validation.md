# Validation — v1.18.0 QA turno único + heterogeneidade (gate binário)

| # | Critério | Como verificar | V/F |
|---|---|---|---|
| V1 | qa-critic SKILL tem protocolo 1 turno steelman→ataque→veredito | grep "STEELMAN\|ATAQUE\|VEREDITO" | — |
| V2 | NÃO instancia defensor/sintetizador; Conclave 3 papéis REPROVADO explicitamente (P6) | leitura | — |
| V3 | Heterogeneidade de modelo declarada como a alavanca que paga (priorizar sobre debate) | grep "heterogene" | — |
| V4 | Disparo condicional silencia só o QA *reforçado*, NÃO o adversarial básico — reconciliação explícita com "default=bug" (ADR-011) | qa-critic SKILL nota "Não revoga..." | — |
| V5 | Honestidade ide↔chat: heterogeneidade indisponível no chat é declarada, não fingida | leitura | — |
| V6 | ADR-018 cita P6 + lit (Zhang 2025, Snorkel, When Debate Fails) e é EMENDA ao Princípio 13 | leitura | — |
| V7 | `_meta/subagent-isolation.md` ganha nota de heterogeneidade gerador↔crítico | grep "Heterogeneidade" | — |
| V8 | Régua §0: +1 seção no qa-critic + nota; nenhum papel/subagente/arquivo de skill novo | git diff --stat | — |
| V9 | Veredito HERDA vocabulário da modalidade (J4=APROVADO_LIMPO/itera; PC=APROVADO_LIMPO/REPROVADO_REWIND) — não inventa termo | qa-critic SKILL nota "Veredito herda..." | — |
| V10 | Agnóstico de domínio | leitura | — |
| V11 | Auto-aplicação tem evidência DURÁVEL: `history.md ## Telemetria` 17-A registra rounds qa-critic heterogêneos (O0-O3) | grep history | — |
| V12 | (regressão) Contrato Onda 0: 7/7 PASS (qa-critic frontmatter intacto) | `python tools/validate_skills.py` | — |
