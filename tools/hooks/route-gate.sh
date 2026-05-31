#!/usr/bin/env bash
# route-gate.sh — UserPromptSubmit hook: roteamento determinístico (ADR-027)
# Equivalente POSIX de route-gate.ps1 (ver cabeçalho de lá para o porquê).
#
# Injeta lembrete de ROTA a cada prompt não-trivial, 1x por sessão. Universal.
# Fail-OPEN: qualquer erro -> exit 0 sem bloquear. Desativação via session.lock.
# Requer: jq (se ausente, degrada para sempre-injeta — melhor pecar por lembrar).

set +e

emit_silent() {
  printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":""}}\n'
  exit 0
}

emit_route() {
  # $1 = contexto. jq monta o JSON com escaping correto; sem jq, fallback simples.
  if command -v jq >/dev/null 2>&1; then
    jq -n --arg ctx "$1" \
      '{hookSpecificOutput:{hookEventName:"UserPromptSubmit",additionalContext:$ctx}}'
  else
    printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":%s}}\n' \
      "$(printf '%s' "$1" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))' 2>/dev/null || printf '""')"
  fi
  exit 0
}

RAW="$(cat)"
SESSION_ID=""; CWD="$PWD"; PROMPT=""
if command -v jq >/dev/null 2>&1 && [ -n "$RAW" ]; then
  SESSION_ID="$(printf '%s' "$RAW" | jq -r '.session_id // empty' 2>/dev/null)"
  CWD="$(printf '%s' "$RAW" | jq -r '.cwd // empty' 2>/dev/null)"; [ -z "$CWD" ] && CWD="$PWD"
  PROMPT="$(printf '%s' "$RAW" | jq -r '.prompt // empty' 2>/dev/null)"
fi

# Desativação (locks). Memória da desativação vive no projeto.
[ -f "$CWD/.claude/session.lock" ] && emit_silent
[ -f "$HOME/.claude/session.lock" ] && emit_silent

# Triviais não merecem rota.
TRIMMED="$(printf '%s' "$PROMPT" | tr -s '[:space:]' ' ' | sed 's/^ //;s/ $//')"
[ "${#TRIMMED}" -lt 12 ] && emit_silent
case "$(printf '%s' "$TRIMMED" | tr '[:upper:]' '[:lower:]')" in
  ok|okay|sim|nao|não|valeu|obrigado|obrigada|certo|isso|segue|siga|continua|continuar|prossiga|beleza|blz|pode|vai|go|yes|no|thanks|thank*) emit_silent ;;
esac

# Uma vez por sessão.
if [ -n "$SESSION_ID" ]; then
  STATE_DIR="$HOME/.claude/.route-state"
  mkdir -p "$STATE_DIR" 2>/dev/null
  SAFE="$(printf '%s' "$SESSION_ID" | tr -c 'A-Za-z0-9_.-' '_')"
  MARKER="$STATE_DIR/$SAFE.routed"
  [ -f "$MARKER" ] && emit_silent
  printf '%s' "$CWD" > "$MARKER" 2>/dev/null
fi

read -r -d '' CTX <<'EOF'
# [route-gate ADR-027] Declare a ROTA antes de executar

Antes de QUALQUER tool call de domínio (escrever/calcular/transformar/buscar dados),
declare a rota em 1 linha e carregue a skill correspondente:

  ROTA: pontual -> metacognição
      | multi-etapa -> squad (pmo -> discovery -> architect -> developer -> qa-critic -> docops)
      | alto-risco/regulado/irreversível/número-que-vai-a-decisão -> + high-stakes-gate

Classifique a tarefa (contexto × complexidade) e ATIVE a(s) skill(s) ANTES de agir.
Output-style governa o TOM/formato, nunca substitui o processo (roteamento/gates).
Se você JÁ roteou nesta sessão, ignore. Desativar aqui: criar .claude/session.lock.
EOF

emit_route "$CTX"
