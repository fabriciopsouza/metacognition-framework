---
release: v1.12.0
adr: ADR-011
date: 2026-05-29
status: GATE
type: binary-validation
---

# v1.12.0 — Validation Gate Binário

> Gate de saída do release v1.12.0. Mesma convenção do v1.11.0 (ADR-010 §ii sub-princípio RRC + sub-princípio i validation binária). Todos os critérios devem PASSAR para tag/merge.

## V1 — ADR-011 substância (decisão arquitetural completa)

**Critério binário:** ADR-011 contém:
- [ ] Status field, Data, Decisores, Relaciona-se a, Fonte (cabeçalho completo)
- [ ] §Contexto com diagnóstico do gap (junções informais + risco loop eterno)
- [ ] §Decisão em 1 frase ativa
- [ ] §Alternativas com ≥6 avaliadas + Pros/Contras
- [ ] §Justificativa por critério régua §0 (ADR-007)
- [ ] §Princípio novo (princípio 13)
- [ ] §Topologia 6 junções + 1 process-critic com gates declarados
- [ ] §Mecanismo operacional (dentro da junção + process-critic + SUPLANTA × EMENDA)
- [ ] §Implementação (arquivos editados/criados)
- [ ] §Consequências Positivas + Negativas + Riscos
- [ ] §Pendências e follow-ups
- [ ] §Referências

**Comando:**
```bash
test -f docs/adr/011-qa-bicelular-juncoes-binarias-process-critic-rewind.md
grep -c "^## " docs/adr/011-qa-bicelular-juncoes-binarias-process-critic-rewind.md  # esperado: ≥10 seções top-level
```

**Status:** [ ] PASSA / [ ] FALHA

---

## V2 — Princípio 13 propagado coerentemente

**Critério binário (todos obrigatórios):**
- [ ] `AGENT-FRAMEWORK.md §6` tem item 13 começando com "**Arquitetura bicelular de QA"
- [ ] `CLAUDE.md` tem seção `## Arquitetura bicelular de QA` mencionando ADR-011 + 6 junções
- [ ] `AGENTS.md` tem seção `## QA bicelular` mencionando ADR-011
- [ ] `README.md` linha 5 menciona "QA bicelular (v1.12.0" + ADR-011

**Comando:**
```bash
grep -qE "^13\. \*\*Arquitetura bicelular de QA" AGENT-FRAMEWORK.md && echo "P13=PASSA"
grep -q "ADR-011" CLAUDE.md AGENTS.md README.md && echo "Refs=PASSA"
```

**Status:** [ ] PASSA / [ ] FALHA

---

## V3 — Topologia operacionalizada em `/handoff`

**Critério binário:**
- [ ] `.agent/workflows/handoff.md` tem seção "Junções binárias forward-only (ADR-011..."
- [ ] Tabela operacional com 6 junções J0-J5 + PC declaradas (artefato-gate + critério binário + quem aplica)
- [ ] Invariantes operacionais (forward-only entre junções, binário-com-iterações dentro, etc.) documentadas
- [ ] Bloco de declaração `/handoff B — junção J_n PASS` exemplificado

**Comando:**
```bash
grep -q "Junções binárias forward-only" .agent/workflows/handoff.md
grep -qE "J0.*PMO.*discovery" .agent/workflows/handoff.md
grep -qE "J5.*docops.*release" .agent/workflows/handoff.md
grep -q "junção J_n PASS\|junção <J_n>" .agent/workflows/handoff.md
```

**Status:** [ ] PASSA / [ ] FALHA

---

## V4 — qa-critic SKILL.md formaliza duas modalidades

**Critério binário:**
- [ ] Seção "Duas modalidades (ADR-011..." existe
- [ ] Junction-critic intermediate (J4) descrito
- [ ] Process-critic final (PC com rewind) descrito
- [ ] Disparo do process-critic codificado: (a) BLOCO APROVADO + (b) on-demand + (c) opcional /checkpoint

**Status:** [ ] PASSA / [ ] FALHA

---

## V5 — PMO SKILL.md formaliza junction-check adversarial

**Critério binário:**
- [ ] Seção "Junção-check adversarial (ADR-011..." existe
- [ ] PMO aplica gate binário adversarial em J0-J3 declarado
- [ ] J4/PC ficam com qa-critic em subagente isolado declarado

**Status:** [ ] PASSA / [ ] FALHA

---

## V6 — /checkpoint esclarecido como save-point + RRC (não process-critic automático)

**Critério binário:**
- [ ] `.agent/workflows/checkpoint.md` menciona ADR-011 esclarecimento
- [ ] /checkpoint não invoca process-critic adversarial automaticamente
- [ ] Backstop opcional sob escalação do dono

**Status:** [ ] PASSA / [ ] FALHA

---

## V7 — qa-critic adversarial round LIMPO

**Critério binário:** qa-critic adversarial em subagente isolado executado em rounds até **APROVADO LIMPO**. Findings ALTO/MEDIO endereçados; findings BAIXO/ADV explicitamente justificados se não-incorporados.

**Status:** [ ] PASSA / [ ] FALHA

---

## V8 — RRC pass do agente (ADR-010 §ii — backstop interno)

**Critério binário:** RRC executado antes do `qa-critic round 1` com PASSA em 6 itens (5 dimensões coerência ADR-010 §ii.2 + anti-vazamento). Contagens em sync verificadas (princípios 11/12/13; 6 junções; 9 passos método sênior; etc.).

**Status:** [ ] PASSA / [ ] FALHA

---

## Gate final

| Critério | Status | Evidência |
|---|---|---|
| V1 — ADR-011 substância | [ ] | |
| V2 — Princípio 13 propagado | [ ] | |
| V3 — /handoff operacionalizado | [ ] | |
| V4 — qa-critic SKILL duas modalidades | [ ] | |
| V5 — PMO SKILL junction-check | [ ] | |
| V6 — /checkpoint esclarecido | [ ] | |
| V7 — qa-critic LIMPO | [ ] | |
| V8 — RRC pass auditável | [ ] | |

**TODOS V1-V8 = PASSA → AUTORIZAR `git merge --no-ff` em main + `git tag v1.12.0`.**
**Qualquer FALHA → corrigir + re-rodar este gate. Sem atalho.**

---

## Nota meta (princípios sêniores aplicados)

Este `validation.md` aplica o que foi ABSORVIDO em ADR-010 (gate binário humano-revisável) e operacionaliza o que está sendo ABSORVIDO em ADR-011 (validation.md é o artefato-gate de J5 docops → release). Auto-aplicação do princípio em sua própria release. RRC + qa-critic + validation.md binário = arquitetura completa de garantia de qualidade do framework.
