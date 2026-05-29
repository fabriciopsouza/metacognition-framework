---
release: v1.11.0
adr: ADR-010
date: 2026-05-28
status: GATE
type: binary-validation
---

# v1.11.0 — Validation Gate Binário

> Gate de saída do release v1.11.0. **Todos os critérios devem PASSAR** para tag/merge. Falha em qualquer = corrigir e re-rodar. Aplica princípio sênior absorvido (ADR-010 RRC §ii) — sem este gate, "merge LIMPO" é auto-declarado pelo agente, sem auditoria binária.

## V1 — Purga estrita de domain-anchors em prompts/regras/docs do núcleo

**Comando:**
```bash
grep -rnE "ALCOA|ANVISA|\bANP\b|\bFDA\b|\bBACEN\b|\bGAMP\b|COBIT|CSV/CSA" \
  --include="*.md" \
  _shared/ .agent/ AGENT-FRAMEWORK.md CLAUDE.md AGENTS.md README.md PROMPT-CHAT-WEB-v4.2.md \
  | grep -v "docs/specs/exemplos/"
```

**Critério binário:** output **0 linhas** (saída vazia).

**Exceções explícitas (NÃO contam como falha):**
- `CHANGELOG.md` — registro histórico do que foi purgado (meta-referência aceita).
- `docs/specs/exemplos/H1-farma-*` — diretório rotulado como exemplo didático regulado-pharma; intenção explícita.

**Status:** [ ] PASSA / [ ] FALHA

---

## V2 — Versões em sync (anti-drift)

**Verificações:**
```bash
grep -E "1\.[0-9]+\.0" README.md guia/web/index.html CLAUDE.md AGENTS.md CHANGELOG.md | head -10
```

**Critério binário:** TODAS as referências de versão atual = **1.11.0** (≠ drift de v1.4.0/v1.6.1/v1.10.0):
- `README.md` linha 3: `Versão: 1.11.0`
- `guia/web/index.html` title: `v1.11.0`
- `guia/web/index.html` `.ver` div: `<b>1.11.0</b>`
- `guia/web/index.html` footer: `v1.11.0`
- `CHANGELOG.md` bloco mais recente: `[1.11.0]`
- `CLAUDE.md` + `AGENTS.md`: mencionam `v1.11.0 — ADR-010`

**Status:** [ ] PASSA / [ ] FALHA

---

## V3 — Refs cruzadas válidas (anti-broken-link)

**Verificações:**
- `ADR-010` referenciado em N arquivos; arquivo `docs/adr/010-framework-agnostico-discovery-declara-escopo.md` existe.
- `Princípio 12` referenciado em CLAUDE/AGENTS/README/CHANGELOG; existe em `AGENT-FRAMEWORK.md §6`.
- `ADR-005`/`ADR-007`/`ADR-009` citados em ADR-010 — todos existem em `docs/adr/`.
- `Memória [[senior-discovery-method]]` referenciada; arquivo na memory existe (fora do repo, mas validável).

**Comando:**
```bash
grep -l "ADR-010" --include="*.md" -r . | grep -v ".claude/"
# E verificar:
test -f docs/adr/010-framework-agnostico-discovery-declara-escopo.md
test -f docs/adr/009-metodo-senior-discovery-auto-melhoria-framework.md
test -f docs/adr/007-regua-ganho-liquido-discovery-cascata-aprendizado-wip.md
test -f docs/adr/005-niveis-de-execucao-framework.md
grep -q "Princípio 12\|principio 12\|princípio 12" AGENT-FRAMEWORK.md
```

**Critério binário:** todos os ADRs referenciados existem; princípio 12 está em AGENT-FRAMEWORK; sem referência órfã.

**Status:** [ ] PASSA / [ ] FALHA

---

## V4 — Substância dos princípios introduzidos (semântica)

**Critério binário — todos obrigatórios:**

- [ ] **Princípio 12 (agnóstico):** texto em `AGENT-FRAMEWORK.md §6` contém: framework não carrega listas hardcoded + discovery declara via 4 perguntas + anti-vazamento cross-projeto + gaps não-bloqueantes flagados.
- [ ] **Princípio 11 honesto:** reescrito de "auto-observação" para "observação meta-cognitiva (captura estruturada de feedback)" + nota sobre auto-detecção falível + firewall ADR-007 preservado.
- [ ] **Sub-princípio ii-a (briefing determinístico):** ADR-010 contém modo Transcribe vs modo Interview com critério binário de 4 itens.
- [ ] **Sub-princípio ii-b (skill via discovery+gate):** ADR-010 contém canal de proposta + gate régua §0 + firewall.
- [ ] **Sub-princípio ii (RRC):** ADR-010 contém pass auditável + 3 passos + gate em `/checkpoint`.
- [ ] **Sub-princípio i (gaps flagados):** ADR-010 contém regra de não-silenciar + integração no output de `metodo-senior.md`.

**Status:** [ ] PASSA / [ ] FALHA

---

## V5 — Operacionalização nas skills (não só no ADR)

**Critério binário — todos obrigatórios:**

- [ ] `.agent/skills/discovery/SKILL.md` passo 6 contém Modo A (Transcribe) + Modo B (Interview) com 4 perguntas + candidate-skill surface.
- [ ] `.agent/skills/discovery/metodo-senior.md` lista 9 passos auditáveis (8 originais + passo 9 Coherence Pass) + seção "Gaps não-bloqueantes" no Output esperado.
- [ ] `.agent/workflows/checkpoint.md` contém gate RRC obrigatório com checklist binário de 5 itens.
- [ ] `_shared/high-stakes-gate/SKILL.md` carrega SOB DECLARAÇÃO do discovery (não por sinal semântico).
- [ ] `.agent/rules/04-confidence-routing.md` desacopla HITL/regulado (HITL via ADR-005).

**Status:** [ ] PASSA / [ ] FALHA

---

## V6 — qa-critic adversarial round LIMPO

**Critério binário:** qa-critic adversarial em subagente isolado executado em rounds até **APROVADO LIMPO** (sem ressalvas residuais bloqueantes). Findings ALTO/MEDIO endereçados; findings BAIXO/ADV explicitamente justificados se não-incorporados.

**Comando:**
```
/agents qa-critic → adversarial review do v1.11.0 (ADR-010 + edits)
→ iterar até PASS LIMPO
```

**Status:** [ ] PASSA / [ ] FALHA

---

## V7 — RRC pass do agente (auto-aplicado antes de declarar "pronto")

**Critério binário:** `/checkpoint` final do release contém bloco RRC com **PASSA em todos os 5 itens**:
- Versões em sync
- Refs cruzadas válidas
- Nomenclatura consistente
- Sem contradições semânticas entre documentos
- Anti-vazamento cross-projeto

**Status:** [ ] PASSA / [ ] FALHA

---

## Gate final

**Para promover ao merge main + tag v1.11.0:**

| Critério | Status |
|---|---|
| V1 — Purga de domain-anchors | [ ] |
| V2 — Versões em sync | [ ] |
| V3 — Refs cruzadas válidas | [ ] |
| V4 — Substância dos princípios | [ ] |
| V5 — Operacionalização nas skills | [ ] |
| V6 — qa-critic LIMPO | [ ] |
| V7 — RRC pass auditável | [ ] |

**TODOS V1-V7 = PASSA → autorizar `git merge --no-ff` em main + `git tag v1.11.0`.**
**Qualquer FALHA → corrigir + re-rodar este gate. Sem atalho.**

---

## Nota meta (princípio sênior absorvido)

Este `validation.md` aplica o que foi ABSORVIDO em ADR-010: **gate binário humano-revisável é o que separa "auto-declarado pronto" (agent self-validation, falível) de "pronto auditável" (binary external gate)**. O RRC é boa prática do agente; `validation.md` é o backstop externo. Os dois juntos > ou-um-ou-outro. Princípio 11 honestamente reescrito reconhece isto.
