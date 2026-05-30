# /start-session — Abertura canônica (genérico)

Primeiro turno de cada sessão. Obrigatório.

## Sequência (PMO)
1. **Sincronizar ANTES de ler (ADR-019 — obrigatório; falha-soft em erro de rede):** `git fetch` + checar ahead/behind vs `@{upstream}`/`origin/main`. Se atrás e seguro (sem modificações rastreadas + fast-forward) → `git pull --ff-only` (untracked não bloqueia); se atrás e inseguro (modificações rastreadas/divergiu) → **avisar e NÃO afirmar estado até resolver**. No IDE o hook `check-repo-sync.ps1` já faz isso no SessionStart; no chat (sem hook) é passo manual. *File-first sem fetch lê retrato congelado — caso real: sessão operou 41 commits atrás de main (method-audit 2026-05-30).* **Depois** ler: AGENTS.md → .agent/rules/*.md → docs/briefing.md → history.md (últimas 30 + `## Em aberto` + `## Aprendizado`).
2. **Reconciliar WIP** (ex-G11 / ADR-007 — modo squad apenas): cruzar `## Em aberto` do history.md com branches do git e ADRs em status `Proposto`. Apontar inconsistências (item em aberto sem branch; branch sem item; ADR `Proposto` sem decisão).
2.5. **Retrospective gate (v1.12.1 — refinamento operacional do J0 adversarial ADR-011; method-audit 2026-05-29; ADR-012 v1.13.0 adicionou handoff cross-sessão como princípio 14 separado — retrospective gate continua sem ADR dedicado próprio):** revisar último bloco entregue desde último PASS do process-critic. Checklist binário adversarial (PMO assume há gap):
   - Process seguido (J0-J5 com gates declarados em `/handoff`)? `[PASSA/FALHA]`
   - RRC executado no `/checkpoint` final do bloco anterior? `[PASSA/FALHA]`
   - Debt deferido registrado explicitamente em `## Em aberto` ou ADR §Pendências? `[PASSA/FALHA]`
   - Polish post-release com surface estrutural > 5 linhas (Mermaid, seção nova, refactor skill/workflow) recebeu process-critic OU foi auto-classificado "não-bloco"? Se SIM segundo → **debt detectado**.

   **Se qualquer FALHA → primeira ação é tratar debt antes de novo escopo.** Sem retrospective gate, polish-skipped-process-critic acumula (padrão observado 2026-05-29). **Flexibilidade:** dono pode escalar "skip retrospective" se contexto é pergunta isolada/trivial — decisão consciente, não default.
3. Produzir STATUS: onde paramos · ADRs aceitos · nomenclaturas · próximo passo · riscos · **WIP** (itens em aberto reconciliados) · **debt retrospective** (gaps detectados no 2.5, se houver).
4. Responder: "Sessão aberta. [STATUS 2-3 linhas] Retomar o próximo passo ou mudou direção?"

## Bloqueios
Sem briefing.md → primeira tarefa é criá-lo. Sem 00-glossario.md → bloquear
(sem source of truth o squad é inviável). Sem AGENTS.md → instalar via framework.

## WIP-limit (ADR-007 — modo squad)
**Finalizar antes de iniciar.** Item em `## Em aberto` só muda de status (planejado→ativo→pausado→bloqueado→fechado) com razão registrada. Reconciliação no passo 2 acima é o gate operacional. Se STATUS infla > 4 linhas, refatorar.
