#!/usr/bin/env bash
# effect-gate.sh — paridade POSIX do deny-backstop T3 por EFEITO (ADR-015).
# [DESCONHECIDO] não testado em Linux/macOS nesta onda — paridade documentada, não validada (ADR-015 §Riscos).
# Contrato Claude Code (P1): lê JSON do hook em stdin; bloquear = stdout JSON permissionDecision:deny + exit 0.
# Erro interno -> exit 0 (não bloqueia; managed-settings é a camada fail-closed). Requer jq.
set -euo pipefail

deny() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"effect-gate (ADR-015) T3 negado: %s. Requer gate humano."}}\n' "$1"
  exit 0
}

raw="$(cat || true)"
[ -z "$raw" ] && exit 0
command -v jq >/dev/null 2>&1 || exit 0   # sem jq, não bloqueia (degrada para managed-settings)

tool="$(printf '%s' "$raw" | jq -r '.tool_name // empty')"
case "$tool" in Bash|PowerShell) : ;; *) exit 0 ;; esac
cmd="$(printf '%s' "$raw" | jq -r '.tool_input.command // empty')"
[ -z "$cmd" ] && exit 0
c="$(printf '%s' "$cmd" | tr '[:upper:]' '[:lower:]')"

echo "$c" | grep -Eq 'rm +(-[a-z]* +)*-[a-z]*[rf]{1,2}[a-z]* +(/|~|\$home|/\*)' && deny 'rm recursivo-forcado em raiz/home/~ (E1+E2)'
echo "$c" | grep -Eq '\bmkfs(\.[a-z0-9]+)?\b|dd +.*of=/dev/(sd|nvme|disk|hd)|format +[a-z]:' && deny 'format/mkfs/dd em device (E1+E2)'
echo "$c" | grep -Eq 'git +push +.*(--force([^-]|$)|-f([^a-z]|$))' && ! echo "$c" | grep -q 'with-lease' && deny 'git push --force sem --force-with-lease (E2+E3)'
printf '%s' "$cmd" | grep -Eq ':\(\) *\{ *:\|:& *\} *;:' && deny 'fork bomb (E2)'
echo "$c" | grep -Eq 'netsh +advfirewall +set +allprofiles +state +off|iptables +-f' && deny 'desligamento de firewall (E5)'

exit 0
