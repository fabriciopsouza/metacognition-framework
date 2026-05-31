#!/usr/bin/env bash
# mission-gate.sh — paridade POSIX do gate de product_type/escopo (ADR-022). SessionStart.
# [DESCONHECIDO] nao testado em Linux/macOS. Injeta additionalContext; fail-soft (exit 0).
# Agnostico (P12): taxonomia/mapa tipo->papel vem da app (product-types.txt); ausente -> default.
set -euo pipefail

emit() {
  local c="${1//\"/\\\"}"
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$c"
  exit 0
}

raw="$(cat || true)"
cwd="$PWD"
if [ -n "$raw" ] && command -v jq >/dev/null 2>&1; then
  c="$(printf '%s' "$raw" | jq -r '.cwd // empty')"; [ -n "$c" ] && cwd="$c"
fi

mode="default"
mf="$HOME/.claude/framework-mode.json"
if [ -f "$mf" ] && command -v jq >/dev/null 2>&1; then
  m="$(jq -r '.mode // empty' "$mf")"; [ -n "$m" ] && mode="$m"
fi
if [ "$mode" = "autosuficiente" ]; then conf="autonomia (product_type ja confirmado no briefing)."
else conf="confirme product_type com o dono antes de avancar (J2+)."; fi

mission=""
for f in "$cwd/mission.md" "$cwd/docs/mission.md" "$cwd/docs/specs/mission.md"; do
  [ -f "$f" ] && { mission="$f"; break; }
done
[ -z "$mission" ] && emit "[mission-gate ADR-022] BRIEFING: sem mission.md. PMO deve declarar product_type + escopo antes de J2+. Modo=$mode -> $conf"

# Formato canonico (inline): "product_type: <valor>".
pt="$(grep -E '^[[:space:]]*product_type:' "$mission" | head -1 | sed -E 's/^[[:space:]]*product_type:[[:space:]]*//; s/[[:space:]]*$//')"
# Fallback tolerante: heading "## product_type" + valor na proxima linha nao-vazia.
if [ -z "$pt" ] || printf '%s' "$pt" | grep -Eq '^<.*>$'; then
  pt="$(awk 'tolower($0) ~ /^#+[[:space:]]*product_type[[:space:]]*$/{f=1;next} f&&NF{print;exit}' "$mission" | sed -E 's/^[[:space:]]*//; s/[[:space:]]*$//')"
fi
if [ -z "$pt" ] || printf '%s' "$pt" | grep -Eq '^<.*>$'; then
  emit "[mission-gate ADR-022] ADVANCE: mission.md sem product_type valido. Declare 'product_type: <tipo>' antes de J2+. Modo=$mode -> $conf"
fi

# Mapa tipo->papel: 1o product-types.txt sob exemplos/*/ (convencao, nao acoplado a uma distribuicao).
roles=""
mapfile=""
for m in "$cwd"/exemplos/*/product-types.txt; do [ -f "$m" ] && { mapfile="$m"; break; }; done
if [ -n "$mapfile" ] && [ -f "$mapfile" ]; then
  line="$(grep -E "^[[:space:]]*${pt}[[:space:]]*[:=]" "$mapfile" | head -1 || true)"
  [ -n "$line" ] && roles=" Papeis ativados (app): $(printf '%s' "$line" | sed -E 's/^[^:=]*[:=][[:space:]]*//')."
fi

emit "[mission-gate ADR-022] STANDARD: product_type='$pt' declarado. Modo=$mode -> $conf$roles"
