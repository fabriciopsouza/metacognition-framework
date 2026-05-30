# Requirements — v1.19.0 Sync de repo no boot (ADR-019)

## Objetivo
Fechar — como **mecanismo em runtime** (não prosa) — o gap confirmado em campo: o `/start-session`
operava sobre clone local sem `git fetch`, lendo retrato congelado (caso real: 41 commits atrás de
origin/main). Dívida cobrada explicitamente pelo dono. EMENDA (Princípios 8, 11).

## Escopo IN
- Hook `.claude/hooks/check-repo-sync.ps1` (+ `.sh` paridade): SessionStart; fetch sempre; auto-pull
  --ff-only só quando seguro; avisa sem tocar caso contrário; falha soft.
- Canary `tools/test_repo_sync.py`.
- Registro em `.claude/settings.json` (SessionStart, antes do inject-start-session).
- Espelho em `sync-global.ps1` (disponibilidade global).
- `start-session.md` passo 1 (superfície universal, inclui chat).

## Escopo OUT
- Registro do hook no SessionStart **global** (outros repos, via bootstrap.ps1) — follow-up
  trigger-gated [DESCONHECIDO se vale para todo repo].
- Validação do `.sh` em Linux/macOS — [DESCONHECIDO], paridade documentada não testada (como ADR-015).
- Auto-pull incondicional — rejeitado (perigoso em tree sujo/não-ff).

## Requisitos
- REQ-1: `git fetch` é sempre executado (read-only).
- REQ-2: Auto-pull SOMENTE com tree limpo E fast-forward; nunca em tree sujo ou não-ff.
- REQ-3: Caso inseguro → aviso explícito no contexto de boot; nunca silencia o risco.
- REQ-4: Em dia → silencioso (sem ruído).
- REQ-5: Falha soft em qualquer erro (não-repo, offline) — nunca bloqueia a sessão.
- REQ-6: O canary prova os 3 caminhos (auto-update / aviso-sujo / silêncio) com efeito verificado.
- REQ-7: `start-session.md` cobre o chat (sem hook) como passo manual.
- REQ-8: Régua §0 — 1 hook de propósito único; nenhum papel/subsistema novo.

## Bloqueadores honestos (P11)
- Registro global (bootstrap.ps1) [DESCONHECIDO] — follow-up.
- Paridade `.sh` não testada [DESCONHECIDO].
