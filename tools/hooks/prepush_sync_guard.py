#!/usr/bin/env python3
"""prepush_sync_guard.py - Hook PreToolUse (Bash): barra push sobre base ATRASADA (ADR-060).

Camada HARD do anti-defasagem no momento de maior dano (empurrar sobre base velha -> divergência/
clobber). Determinístico, NAO-PowerShell (python.exe -> escapa da regra Kaspersky AAC). Só age quando
o comando e `git push`; caso contrario, allow silencioso (overhead mínimo).

Decisoes adversariais:
 - Compara atraso vs `@{upstream}` (a tracking da PROPRIA branch), NAO origin/main — senao bloquearia
   feature-branch normal (que e intencionalmente atras de main). Sem upstream (branch nova) -> allow.
 - Usa permissionDecision **ask** (gate humano), NAO deny dura — rebase-force-push legítimo nao deve
   travar; o humano confirma com a informação na mão.
 - Fail-OPEN: qualquer erro -> allow (um guard nunca trava o usuário pelo seu próprio defeito).

Contrato PreToolUse: le JSON no stdin (tool_input.command, cwd). Emite hookSpecificOutput com
permissionDecision (ask|allow). Uso: python tools/hooks/prepush_sync_guard.py
"""
import json
import os
import re
import subprocess
import sys


def allow():
    sys.exit(0)  # exit 0 sem output = allow


def ask(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                              "permissionDecision": "ask",
                                              "permissionDecisionReason": reason}}, ensure_ascii=True))
    sys.exit(0)


def git(cwd, *args):
    try:
        r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        return r.stdout.strip(), r.returncode
    except Exception:
        return "", 1


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        cmd = str(((payload.get("tool_input") or {}).get("command")) or "")
        cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

        # So age em `git push`. Regex evita casar "git pushd" ou substrings em comentário trivial.
        if not re.search(r"\bgit\s+push\b", cmd):
            allow()

        inside, _ = git(cwd, "rev-parse", "--is-inside-work-tree")
        if inside != "true":
            allow()

        upstream, rc = git(cwd, "rev-parse", "--abbrev-ref", "@{upstream}")
        if rc != 0 or not upstream:
            allow()  # branch nova / sem tracking -> nada a estar atras

        git(cwd, "fetch", "--quiet")  # checagem honesta do estado remoto antes de empurrar
        behind, rc = git(cwd, "rev-list", "--count", f"HEAD..{upstream}")
        if rc == 0 and behind not in ("", "0") and int(behind) > 0:
            ask(f"PRE-PUSH (ADR-060): local esta {behind} commit(s) ATRAS de `{upstream}`. "
                f"Empurrar agora arrisca push sobre base velha / divergencia. "
                f"Recomendado: `git pull --ff-only` (ou rebase) ANTES. Confirmar o push mesmo assim?")
        allow()
    except Exception:
        # Fail-open: guard nunca trava o usuario pelo proprio defeito.
        sys.exit(0)


if __name__ == "__main__":
    main()
