---
description: Abre a sessão pelo PMO — sync + rules + briefing + history + reconciliação WIP + retrospective gate (ADR-024)
---

Execute o **protocolo canônico de abertura de sessão** do framework, seguindo
`.agent/workflows/start-session.md` (fonte única — não duplicar a lógica aqui):

1. **Sincronizar ANTES de ler (ADR-019 — obrigatório, falha-soft):** `git fetch` + checar ahead/behind
   vs `@{upstream}`/`origin/main`. Atrás e seguro → `git pull --ff-only`; atrás e inseguro → avisar e
   **não afirmar estado** até resolver. *File-first sem fetch lê retrato congelado.*
2. **Ler:** `AGENTS.md` → `.agent/rules/*.md` → `docs/briefing.md` → `history.md`
   (últimas 30 + `## Em aberto` + `## Aprendizado`).
3. **Reconciliar WIP:** cruzar `## Em aberto` do `history.md` com branches do git e ADRs em `Proposto`.
4. **Retrospective gate:** revisar o último bloco entregue desde o último PASS do process-critic
   (checklist binário adversarial — assumir que há gap).
5. **STATUS (2-3 linhas):** onde paramos · ADRs aceitos · nomenclaturas · próximo passo · riscos · WIP.
   Responder: "Sessão aberta. [STATUS] Retomar o próximo passo ou mudou direção?"

> Equivalente a dizer **"iniciar"** — ambos disparam este protocolo (ADR-024). No IDE, os hooks de
> SessionStart já rodam sync/modo/agnosticismo automaticamente; este comando garante o protocolo
> completo do PMO sob demanda.
>
> **Não é rígido** — é um guia, não um formulário. O agente pode reunir o contexto por **prosa,
> perguntas e inspeção de pastas**; não exige tudo pré-preenchido. Por projeto, **você preenche só
> 2 arquivos**: `docs/briefing.md` (objetivo · escopo · critério de aceite) e
> `.agent/rules/00-glossario.md` (nomes/termos = fonte da verdade). O resto a IA usa; você só ajusta
> ao decidir mudar uma regra. Sem o briefing/glossário, o agente **elicita por perguntas** em vez de travar.
