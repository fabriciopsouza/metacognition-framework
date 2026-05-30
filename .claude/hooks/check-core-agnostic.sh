#!/usr/bin/env bash
# check-core-agnostic.sh — paridade POSIX do hook de agnosticismo do núcleo (ADR-020).
# [DESCONHECIDO] não testado em Linux/macOS nesta versão — paridade documentada, não validada
# (consistente com ADR-015/019 §Riscos). Requer python3. Falha soft (exit 0) em qualquer erro.
# Política idêntica ao .ps1: roda o linter; se vazou norma de domínio no núcleo, AVISA (nunca bloqueia).
set -u

emit() { printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' "$1"; exit 0; }
jstr() { python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))' 2>/dev/null || printf '""'; }

cwd="${CLAUDE_PROJECT_DIR:-$PWD}"
linter="$cwd/tools/check_core_agnostic.py"
[ -f "$linter" ] || exit 0                       # repo sem o linter -> silencioso
command -v python3 >/dev/null 2>&1 || exit 0     # sem python -> silencioso

out="$(cd "$cwd" && python3 tools/check_core_agnostic.py 2>&1)"; code=$?
[ "$code" -eq 0 ] && exit 0                       # núcleo limpo -> silencioso

leaks="$(printf '%s\n' "$out" | grep '^LEAK ' || true)"
if [ -z "$leaks" ]; then
  # exit!=0 SEM linhas LEAK = linter nao rodou (denylist ausente/vazia, erro). Aviso preciso, fail-soft.
  printf '# AVISO (ADR-020): o linter de agnosticismo retornou erro (exit %s) sem achados de vazamento. Provavel config (tools/agnostic-denylist.txt ausente/vazia) ou ambiente. Rode: python3 tools/check_core_agnostic.py' "$code" | jstr | { read -r j; emit "$j"; }
fi
printf '# AVISO (ADR-020): vazamento de norma de dominio no NUCLEO\n\nO linter de agnosticismo detectou norma regulatoria de dominio no nucleo (viola Principio 12 / regra #5 do qa-critic):\n\n%s\n\nAcao: remova a mencao (norma de dominio vive em docs/, exemplos/ ou config de aplicacao) OU adicione o sentinela lint-agnostic:allow na linha com justificativa. Rode python tools/check_core_agnostic.py para reverificar.' "$leaks" | jstr | { read -r j; emit "$j"; }
