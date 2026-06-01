# ADR 043 — Abrangência regulada: denylist expandida + catálogo de perfis clonáveis (sem quebrar agnosticismo)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: remediação v2 (marco v1.30.0) · Tipo: **novo** (expande denylist + meta-linter + app opt-in) — net-gain: amplia cobertura regulada sem hardcodar norma no núcleo.
- Origem no plano: item 11 (`[CRÍTICA]` + `[GEMINI]`). Relaciona: ADR-020 (linter de agnosticismo), ADR-010 (escopo declarado), `high-stakes-gate`, ADR-023 (apps de domínio).

## Contexto

`agnostic-denylist.txt` era seed de ~12 normas, não-exaustiva (ITIL/COBIT/SOX/ISO-13485/SOC 2/NIST/CLIA
passavam). E o `high-stakes-gate` delega 100% da norma ao discovery, sem catálogo de partida — o caso
regulado (indicador que vai a decisão executiva) não tinha andaime.

## Decisão (1 frase ativa)

**No núcleo (agnóstico):** expandir a denylist (SOX, ISO-13485/27001/9001, COBIT, ITIL, Basel, SOC 2,
NIST, CLIA, Sarbanes-Oxley) + `tools/check_regulatory_coverage.py` (meta-linter advisory que avisa quais
**famílias** reguladas ainda não têm representante, mantendo o aviso "não-exaustiva"). **Fora do núcleo
(opt-in):** `exemplos/dominio-regulado/` com ≥3 perfis clonáveis (`compliance-profile-*.json`: audit
trail, HITL suficiente, retenção, assinatura eletrônica) que o discovery oferece quando "regulado? = sim"
— mantendo `check_core_agnostic` verde (perfis vivem em `exemplos/`, nunca no núcleo).

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** Famílias comuns passam; sem andaime regulado. **Rejeitada — é o gap.**
2. **Hardcodar normas + controles no núcleo.** Viola P12 (domínio no núcleo). **Rejeitada** — denylist é a NEGATIVA (tools/, não-varrida); perfis vão para `exemplos/` (app opt-in).
3. **Só expandir a denylist (sem perfis).** Bloqueia vazamento mas não dá ponto de partida ao caso regulado. **Rejeitada parcialmente** — faz-se ambos.
4. **Denylist expandida + meta-linter + perfis opt-in (ESCOLHIDA).** Prós: cobertura maior, andaime clonável, núcleo agnóstico intacto. Contras: NIST/OWASP são padrões abertos FUNDACIONAIS (REFERENCIAS) citados no núcleo (action-safety) — resolvido com o **sentinela `lint-agnostic:allow`** na citação legítima (auditável), não removendo NIST da denylist.

## Consequências

**Positivas:** ITIL/COBIT/SOX/ISO/SOC 2/CLIA deixam de passar; o caso regulado ganha perfil de partida;
o meta-linter ajuda a manter a lista ampla honestamente. **Negativas:** a citação fundacional de NIST no
`action-safety` precisou de sentinela (1 linha auditável). **Riscos/limite declarado:** "andaime de
conformidade", **não** "pronto para regulado" — adequação à norma concreta é do dono + HITL → `LIMITS.md`.
A denylist permanece **não-exaustiva** por design.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.23-v1.31-remediacao` · `2026-05-31` · grep `check_regulatory_coverage|dominio-regulado`
- Artefatos: `tools/agnostic-denylist.txt` (+11 padrões), `tools/check_regulatory_coverage.py`,
  `tools/test_regulatory_coverage.py`, `exemplos/dominio-regulado/` (README + 3 perfis), sentinela no
  `_shared/action-safety/SKILL.md`, samples em `test_core_agnostic.py`, wiring `discovery/SKILL.md` 6(a).
- DONE quando: denylist expandida + ≥3 perfis + `check_core_agnostic` ainda verde. [CONFIRMADO]
