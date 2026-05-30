#!/usr/bin/env bash
# check-repo-sync.sh — paridade POSIX do hook de sync de boot (ADR-019).
# [DESCONHECIDO] não testado em Linux/macOS nesta versão — paridade documentada, não validada
# (consistente com ADR-015 §Riscos). Requer git. Falha soft (exit 0) em qualquer erro.
# Política idêntica ao .ps1: fetch sempre; auto-pull --ff-only só se tree limpo + ff; senão avisa.
set -u

emit() { printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' "$1"; exit 0; }
jstr() { python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))' 2>/dev/null || printf '""'; }

cwd="${CLAUDE_PROJECT_DIR:-$PWD}"
command -v git >/dev/null 2>&1 || emit '""'
[ "$(git -C "$cwd" rev-parse --is-inside-work-tree 2>/dev/null)" = "true" ] || emit '""'

upstream="$(git -C "$cwd" rev-parse --abbrev-ref '@{upstream}' 2>/dev/null || echo origin/main)"
git -C "$cwd" fetch --quiet 2>/dev/null || true

counts="$(git -C "$cwd" rev-list --left-right --count "$upstream...HEAD" 2>/dev/null)" || emit '""'
[ -n "$counts" ] || emit '""'
behind="$(echo "$counts" | awk '{print $1}')"; ahead="$(echo "$counts" | awk '{print $2}')"
[ "${behind:-0}" -eq 0 ] 2>/dev/null && emit '""'

# untracked NAO bloqueia (paridade com .ps1 / qa-critic ADR-019); --ff-only e a trava final.
dirty="$(git -C "$cwd" status --porcelain --untracked-files=no 2>/dev/null)"
ff=1; git -C "$cwd" merge-base --is-ancestor HEAD "$upstream" 2>/dev/null && ff=0

if [ -z "$dirty" ] && [ "$ff" -eq 0 ]; then
  git -C "$cwd" pull --ff-only --quiet 2>/dev/null; rc=$?
  if [ "$rc" -eq 0 ]; then
    printf '# Repo sync (ADR-019)\nOK repo estava %s commit(s) atras de %s e foi AUTO-ATUALIZADO (ff, sem modificacoes rastreadas).' "$behind" "$upstream" | jstr | { read -r j; emit "$j"; }
  else
    printf '# Repo sync (ADR-019)\nAVISO tentei auto-atualizar mas pull --ff-only nao concluiu (rc=%s; ex.: untracked colidiria/lock). Rode git pull manual antes de reconciliar WIP.' "$rc" | jstr | { read -r j; emit "$j"; }
  fi
else
  if [ -n "$dirty" ]; then motivo="modificacoes RASTREADAS"; acao="commit ou stash, depois git pull"; else motivo="historico DIVERGIU (nao-ff)"; acao="rebase/merge manual"; fi
  printf '# Repo sync (ADR-019)\nAVISO repo esta %s atras de %s (%s a frente). NAO auto-atualizei: %s. Resolva (%s) antes de reconciliar WIP.' "$behind" "$upstream" "${ahead:-0}" "$motivo" "$acao" | jstr | { read -r j; emit "$j"; }
fi
