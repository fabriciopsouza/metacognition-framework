# /start-session — Abertura canônica (genérico)

Primeiro turno de cada sessão. Obrigatório.

## Sequência (PMO)
1. Ler: AGENTS.md → .agent/rules/*.md → docs/briefing.md → history.md (últimas 30 + `## Em aberto` + `## Aprendizado`).
2. **Reconciliar WIP** (ex-G11 / ADR-007 — modo squad apenas): cruzar `## Em aberto` do history.md com branches do git e ADRs em status `Proposto`. Apontar inconsistências (item em aberto sem branch; branch sem item; ADR `Proposto` sem decisão).
3. Produzir STATUS: onde paramos · ADRs aceitos · nomenclaturas · próximo passo · riscos · **WIP** (itens em aberto reconciliados).
4. Responder: "Sessão aberta. [STATUS 2-3 linhas] Retomar o próximo passo ou mudou direção?"

## Bloqueios
Sem briefing.md → primeira tarefa é criá-lo. Sem 00-glossario.md → bloquear
(sem source of truth o squad é inviável). Sem AGENTS.md → instalar via framework.

## WIP-limit (ADR-007 — modo squad)
**Finalizar antes de iniciar.** Item em `## Em aberto` só muda de status (planejado→ativo→pausado→bloqueado→fechado) com razão registrada. Reconciliação no passo 2 acima é o gate operacional. Se STATUS infla > 4 linhas, refatorar.
