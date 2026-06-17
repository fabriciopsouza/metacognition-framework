# ADR 086 — Gating determinístico por risco (`risk_score`): recast (B) do TEA/BMAD sob P15

- Status: **Aceito** (2026-06-17 — gate: qa-critic heterogêneo Sonnet em worktree isolado, PASS *aprovar_com_ressalvas*; canário provado não-teatro; 3 ressalvas BAIXO corrigidas) · Decisores: dono ("siga em modo autônomo") + squad
- Tipo: **adição que mecaniza prosa** (P15). Régua §0 (ADR-007): adição de tool, mas satisfaz a cláusula (c) — *destrava decisão hoje implícita/subjetiva* ("quanto de QA/rigor gastar") tornando-a mecanismo determinístico + integra (não duplica) com gates existentes. +1 capability `risk-gate`. Override declarado.
- Relaciona: **ADR-085** (recast (B); P15/P12), ADR-007 (§0), ADR-011/074 (QA bicelular / qa-evidence), ADR-022 (mission/high-stakes), ADR-010 (agnosticismo)

## Contexto

O recast (B) do ADR-085: o `bmad-method-test-architecture-enterprise` (TEA) tem **gating determinístico por risco** (`risco = probabilidade × impacto` → gate + tier de cobertura). Nosso QA bicelular (J0–J6) é **binário** (PASS/FAIL) e **não tem dial de profundidade** — "quanto rigor gastar em quê" era julgamento implícito do agente. P15 (determinismo-primeiro) exige mecanizar isso.

**Correção de premissa (verificada empiricamente nesta sessão):** o ADR-085 declarou que (B) **dependia** de evoluir o `check_core_agnostic.py` (forma-vs-conteúdo), senão o linter barraria o mecanismo de risco no núcleo. **Falso, por reflexo (afirmei sem ler o linter).** O linter é **denylist-based** (`tools/agnostic-denylist.txt` = só normas regulatórias: ANVISA/ANP/FDA/LGPD/ISO…); um arquivo de núcleo com o mecanismo de risco (`probabilidade/impacto/score/gate/P0–P3`) **passa** (`python tools/check_core_agnostic.py <arquivo>` = PASS). O linter **já encarna** "bloqueia conteúdo, permite forma" por construção. **Logo o ADR-086-linter cai; (B) estava desbloqueado.** Ganho líquido: trave inútil não construída.

## Decisão

**(B1)** `tools/risk_score.py` — FORMA agnóstica no núcleo: `score_item(prob,impact)` → `{score=prob×impact, gate, tier}` por matriz fixa; `aggregate_gate` (worst-case); `evaluate(items)`. Determinístico, fail-closed (prob/impacto fora de 1–3 ⇒ ValueError/exit 1). **Categorias de risco NÃO hardcoded** (TECH/SEC/PERF… são CONTEÚDO/blueprint, input livre `cat` — P12/ADR-085).

**(B2)** Matriz (recast desambiguado do TEA): score ∈ **{1,2,3,4,6,9}** (5/7/8 impossíveis como produto). `gate`: 9→FAIL · 6→CONCERNS · 4→ADVISORY · 1–3→NONE. `tier` (disjunto por prioridade-mais-alta — desambigua as faixas SOBREPOSTAS do TEA, que não eram determinísticas): 6–9→P0 · 4–5→P1 · 2–3→P2 · 1→P3.

**(B3)** Canário `tools/test_risk_score.py` (fail-closed): tabela-verdade EXAUSTIVA dos 9 combos + conjunto de scores == {1,2,3,4,6,9} + fail-closed (range/campos/CLI) + agregação + determinismo.

**(B4)** Wire (onde usar, não duplicar mecanismo): `high-stakes-gate/SKILL.md` referencia `risk_score` para priorizar profundidade de validação por score; `qa-evidence`/`readiness-gate` podem consumir o `gate_agregado` como dado. +1 capability `risk-gate` (`fail-closed`, test = o canário).

## Alternativas consideradas

1. **Manter o dial de QA implícito (prosa).** Viola P15. **Rejeitada — é o gap.**
2. **Evoluir o linter forma-vs-conteúdo primeiro (como o ADR-085 declarou).** **Rejeitada — dependência FALSA**, verificada: o linter (denylist) já permite a forma; não barra o mecanismo.
3. **Hardcodar categorias de risco (TECH/SEC/…) no tool.** Viola P12 (conteúdo no núcleo). **Rejeitada** — categorias são input/blueprint; o tool é só forma.
4. **Classificador "inteligente" de risco (LLM).** Não-determinístico; um gate de segurança deve ser previsível/auditável. **Rejeitada** (mesmo motivo do ADR-039).

## Consequências

**Positivas:** o "quanto de QA" vira mecanismo determinístico e auditável (P15); integra com high-stakes/qa-evidence sem duplicar; forma no núcleo, conteúdo (categorias/limiares-de-domínio) fora (P12 intacto). **Negativas/limite (declarado):** +1 tool + 1 capability (`risk-gate`); a *interpretação* de prob/impacto por item ainda é julgamento humano na ENTRADA (a porta do P15: o tool mecaniza o cálculo→gate, não a estimativa — declarado). **Não-feito:** o oracle de cobertura 4-tier do `trace` (B' do ADR-085) e os recasts C/H seguem como blocos futuros.
