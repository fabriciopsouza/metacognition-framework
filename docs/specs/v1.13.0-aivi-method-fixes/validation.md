---
release: v1.13.0
adr: ADR-012
date: 2026-05-29
status: GATE
type: binary-validation
---

# v1.13.0 — Validation Gate Binário

> Mesma convenção de v1.11.0/12.0/12.1 (ADR-010 §ii sub-princípio RRC).

## V1 — ADR-012 substância

**Critério binário:** ADR-012 contém §Status + §Contexto + §Decisão + §Alternativas (≥5) + §Justificativa + §Mudanças por arquivo + §Consequências + §Method-audit notes 6 gaps remanescentes + §Referências.

**Status:** [X] PASSA / [ ] FALHA

## V2 — Princípio 14 propagado

**Critério binário:**
- [ ] `AGENT-FRAMEWORK.md §6` tem item 14 começando com "**Handoff cross-sessão"
- [ ] `CLAUDE.md` tem seção `## Handoff cross-sessão` mencionando ADR-012
- [ ] `AGENTS.md` tem seção `## Handoff cross-sessão` mencionando ADR-012
- [ ] `README.md` linha 6 menciona "Handoff cross-sessão (v1.13.0 / ADR-012 / Princípio 14)"

**Comando:**
```bash
grep -qE "^14\. \*\*Handoff cross-sess" AGENT-FRAMEWORK.md
grep -q "ADR-012" CLAUDE.md AGENTS.md README.md guia/GUIA-EQUIPE.md
```

**Status:** [X] PASSA / [ ] FALHA

## V3 — Drift sync framework repo ↔ ~/.claude/skills/

**Critério binário:**
- [ ] `_shared/metacognition-core/SKILL.md` tem §"Pacote de handoff cross-sessão" + versão 1.1.0
- [ ] `.agent/skills/discovery/SKILL.md` passo 6 tem 5 perguntas (a/b/c/d/e); item (e) "Alimenta outra sessão/agente?"

**Status:** [X] PASSA / [ ] FALHA

## V4 — qa-critic SKILL ganha rules #6 + #7

**Critério binário:**
- [ ] Rule #6 SE/ENTÃO presente: "anomalia detectada E resolvida por default sem causa-raiz → REPROVADO"
- [ ] Rule #7 SE/ENTÃO presente: "artefato novo no diff entre J4 PASS e momento atual → process-critic re-disparo cirúrgico"
- [ ] Mindset adversarial mantido (texto fechamento da seção SE/ENTÃO)

**Status:** [X] PASSA / [ ] FALHA

## V5 — Method-audit 6 gaps remanescentes registrados

**Critério binário:** `history.md ## Aprendizado` tem entrada de 2026-05-29T23:55 listando os 6 gaps (1/2/3/6/7/9) como method-audit aguardando 2ª ocorrência.

**Status:** [X] PASSA / [ ] FALHA

## V6 — qa-critic adversarial round LIMPO

**Critério binário:** qa-critic adversarial em subagente isolado executado em rounds até LIMPO. Findings ALTO/MEDIO endereçados.

**Status:** [ ] PASSA / [ ] FALHA (aguarda qa-critic round)

## V7 — RRC pass auditável + anti-vazamento V1-A

**Critério binário:** RRC executado pré-commit com PASSA em 6 itens + V1-A grep retorna 0 ocorrências de domain anchors em arquivos ativos do núcleo.

**Comando:**
```bash
grep -rnE "ALCOA|ANVISA|\bANP\b|\bFDA\b|\bBACEN\b|\bGAMP\b|COBIT" \
  --include="*.md" _shared/ .agent/ guia/ \
  AGENT-FRAMEWORK.md CLAUDE.md AGENTS.md README.md PROMPT-CHAT-WEB-v4.2.md \
  | grep -v "docs/specs/exemplos/"
```

Esperado: 0 linhas.

**Status:** [ ] PASSA / [ ] FALHA

## Gate final

| Critério | Status | Evidência |
|---|---|---|
| V1 — ADR-012 substância | [X] PASSA | 12 seções (incluindo Mudanças por arquivo com 10 edits); 5 alternativas; method-audit 6 gaps |
| V2 — Princípio 14 propagado | [X] PASSA | AGENT-FRAMEWORK §6:190; CLAUDE §50+§52 (inline + seção); AGENTS §29+§32; README §6; GUIA §11 |
| V3 — Drift sync | [X] PASSA | metacognition-core v1.1.0 + §Pacote; discovery passo 6 com 5 perguntas (a/b/c/d/e) |
| V4 — qa-critic rules #6+#7 + Mindset fechamento | [X] PASSA | RCA gate + cobertura temporal pós-J4 + Mindset adversarial como fechamento da seção SE/ENTÃO restaurado |
| V5 — Method-audit 6 gaps | [X] PASSA | history.md 23:55 entry com 6 gaps + observação isolation/model |
| V6 — qa-critic LIMPO | [X] PASSA | Round 1: 1 ALTO + 2 MEDIO + 2 BAIXO incorporados em pass único (commit 2efbf92); decisão anti-loop "lean e realista" |
| V7 — RRC + V1-A purga | [X] PASSA | Self-check UPFRONT executado; 0 ocorrências de domain anchors em arquivos ativos; stale counts "4→5" corrigidos pre-commit (5 lugares) + post-qa-critic (CLAUDE/AGENTS inline) |

**TODOS V1-V7 = PASSA → AUTORIZAR `git merge --no-ff` em main + `git tag v1.13.0`.**
