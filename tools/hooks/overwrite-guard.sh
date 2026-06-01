#!/usr/bin/env bash
# overwrite-guard.sh — paridade POSIX do anti-overwrite-cego (ADR-037). Requer jq.
# PreToolUse(Write|Edit) = gate (exit 2 se sobrescreve arquivo com conteudo nao-lido/criado
# nesta sessao); PostToolUse(Read|Write|Edit|NotebookEdit) = record no manifesto da sessao.
# Manifesto: .agent/brain/session-files.json keyed por session_id. Override: OVERWRITE_GUARD_MANIFEST.
# Fail-open em erro/sem jq (exit 0). Veredito identico ao .ps1 (canario test_overwrite_guard).
set -euo pipefail

raw="$(cat || true)"
[ -z "$raw" ] && exit 0
command -v jq >/dev/null 2>&1 || exit 0

event="$(printf '%s' "$raw" | jq -r '.hook_event_name // empty')"
tool="$(printf '%s' "$raw" | jq -r '.tool_name // empty')"
sid="$(printf '%s' "$raw" | jq -r '.session_id // "default"')"
fp="$(printf '%s' "$raw" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')"
[ -z "$fp" ] && exit 0
cwd="$(printf '%s' "$raw" | jq -r '.cwd // empty')"
[ -z "$cwd" ] && cwd="$PWD"

manifest="${OVERWRITE_GUARD_MANIFEST:-$cwd/.agent/brain/session-files.json}"
case "$fp" in /*) full="$fp";; *) full="$cwd/$fp";; esac

mkdir -p "$(dirname "$manifest")" 2>/dev/null || true
[ -f "$manifest" ] || echo '{}' > "$manifest"

known_has() { jq -e --arg s "$sid" --arg f "$1" '(.[$s] // []) | index($f) != null' "$manifest" >/dev/null 2>&1; }

if [ "$event" = "PreToolUse" ] && { [ "$tool" = "Write" ] || [ "$tool" = "Edit" ]; }; then
  [ -e "$full" ] || exit 0
  [ -s "$full" ] || exit 0
  known_has "$full" && exit 0
  echo "[overwrite-guard ADR-037] BLOQUEADO: '$fp' existe com conteudo e NAO foi lido nem criado nesta sessao. LEIA o arquivo antes de sobrescrever (anti-overwrite cego)." >&2
  exit 2
fi

if [ "$event" = "PostToolUse" ]; then
  if ! known_has "$full"; then
    tmp="$(mktemp)"
    if jq --arg s "$sid" --arg f "$full" '.[$s] = ((.[$s] // []) + [$f])' "$manifest" > "$tmp" 2>/dev/null; then
      mv "$tmp" "$manifest"
    else
      rm -f "$tmp"
    fi
  fi
fi
exit 0
