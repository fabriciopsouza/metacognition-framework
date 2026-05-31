#!/usr/bin/env bash
# effect-gate.sh — paridade POSIX do motor de regras por EFEITO (ADR-039, estende ADR-015).
# A POLITICA vive em tools/effect-rules.json; este hook INTERPRETA (mesmas regras do .ps1).
# Contrato: le JSON do hook em stdin; deny = stdout JSON permissionDecision:deny; ask = :ask; exit 0.
# So inspeciona Bash/PowerShell. Erro/sem jq/sem rules -> exit 0 (fail-open; managed-settings e a camada
# fail-closed). Regex em subconjunto comum .NET ∩ POSIX-ERE (paridade com o .ps1). Requer jq.
set -euo pipefail

emit() { # $1=decision $2=reason
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"%s","permissionDecisionReason":"effect-gate (ADR-039) [%s]: %s"}}\n' "$1" "$1" "$2"
  exit 0
}

raw="$(cat || true)"
[ -z "$raw" ] && exit 0
command -v jq >/dev/null 2>&1 || exit 0

tool="$(printf '%s' "$raw" | jq -r '.tool_name // empty')"
case "$tool" in Bash|PowerShell) : ;; *) exit 0 ;; esac
cmd="$(printf '%s' "$raw" | jq -r '.tool_input.command // empty')"
[ -z "$cmd" ] && exit 0
c="$(printf '%s' "$cmd" | tr '[:upper:]' '[:lower:]')"

rules="$(dirname "$0")/../effect-rules.json"
[ -f "$rules" ] || { echo "[effect-gate] effect-rules.json ausente — fail-open" >&2; exit 0; }

ask_reason=""
n="$(jq '.rules | length' "$rules")"
i=0
while [ "$i" -lt "$n" ]; do
  decision="$(jq -r ".rules[$i].decision" "$rules")"
  reason="$(jq -r ".rules[$i].reason" "$rules")"
  allok=1
  while IFS= read -r p; do
    [ -z "$p" ] && continue
    printf '%s' "$c" | grep -Eq -- "$p" || { allok=0; break; }
  done < <(jq -r ".rules[$i].all[]? // empty" "$rules")
  if [ "$allok" -eq 1 ]; then
    blocked=0
    while IFS= read -r p; do
      [ -z "$p" ] && continue
      if printf '%s' "$c" | grep -Eq -- "$p"; then blocked=1; break; fi
    done < <(jq -r ".rules[$i].none[]? // empty" "$rules")
    if [ "$blocked" -eq 0 ]; then
      if [ "$decision" = "deny" ]; then
        emit deny "$reason. Requer gate humano (four-eyes fora do canal)."
      elif [ "$decision" = "ask" ] && [ -z "$ask_reason" ]; then
        ask_reason="$reason"
      fi
    fi
  fi
  i=$((i + 1))
done

[ -n "$ask_reason" ] && emit ask "$ask_reason"
exit 0
