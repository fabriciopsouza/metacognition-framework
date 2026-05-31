#!/usr/bin/env bash
# compaction-gate.sh — paridade POSIX do backstop de digest (ADR-021).
# [DESCONHECIDO] nao testado em Linux/macOS nesta onda — paridade documentada, nao validada.
# Backstop conservador: bloqueia SO o caso catastrofico (history.md ausente ou sem checkpoint).
# Contrato PreCompact: bloquear = stdout {"decision":"block","reason":...} + exit 0; allow = exit 0.
# Erro/ausencia de jq -> exit 0 (fail-open; mesma filosofia do effect-gate / ADR-015).
set -euo pipefail

block() {
  # escapa aspas duplas do reason para JSON valido
  local r="${1//\"/\\\"}"
  printf '{"decision":"block","reason":"%s"}\n' "$r"
  exit 0
}

raw="$(cat || true)"
cwd="$PWD"
if [ -n "$raw" ] && command -v jq >/dev/null 2>&1; then
  c="$(printf '%s' "$raw" | jq -r '.cwd // empty')"
  [ -n "$c" ] && cwd="$c"
fi

hist=""
for f in "$cwd/history.md" "$cwd/HISTORY.md" "$cwd/.claude/memory/HISTORY.md"; do
  [ -f "$f" ] && { hist="$f"; break; }
done
[ -z "$hist" ] && block "history.md nao encontrado em $cwd: nada persistido nesta sessao. Rode /checkpoint antes de compactar (ADR-016/021)."

grep -Eq '^##[[:space:]]+[0-9]{4}-[0-9]{2}-[0-9]{2}' "$hist" \
  || block "history.md sem nenhum checkpoint (## YYYY-MM-DD): rode /checkpoint antes de compactar (ADR-016/021)."

printf '[compaction-gate] compaction prestes a ocorrer — confirme que o digest reflete o WIP (ADR-016). Nao-bloqueante.\n' >&2
exit 0
