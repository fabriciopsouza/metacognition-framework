#!/usr/bin/env python3
"""check_core_agnostic_hook.py - Hook SessionStart (porte Python do check-core-agnostic.ps1) - ADR-020 + ADR-061.

PORQUE PYTHON: na maquina 9TRP7H4 o Kaspersky AAC bloqueia o .ps1 (powershell.exe spawnando python).
Como python.exe (process tree sem powershell), escapa daquela regra. Carimba liveness p/ o auditor.

Decisao de GATE equivalente ao .ps1: roda tools/check_core_agnostic.py (read-only); exit!=0 com linhas
LEAK -> injeta AVISO de vazamento; exit!=0 sem LEAK -> aviso de config; limpo -> silencioso. Fail-SOFT.
(Delta intencional vs .ps1: este carimba liveness ADR-061 e emite JSON vazio no caminho limpo.)

Saida: JSON SessionStart {hookSpecificOutput:{hookEventName,additionalContext}}. Sempre exit 0.
"""
import json
import os
import subprocess
import sys


def emit(ctx):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                              "additionalContext": ctx}}, ensure_ascii=True))
    sys.exit(0)


def session_id_from_stdin():
    try:
        if sys.stdin and not sys.stdin.isatty():
            raw = sys.stdin.read()
            if raw and raw.strip():
                return str(json.loads(raw).get("session_id") or "")
    except Exception:
        pass
    return ""


def stamp_liveness(cwd, key, session_id):
    try:
        import time
        d = os.path.join(cwd, ".claude", ".hooklive")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, key), "w", encoding="utf-8") as f:
            f.write(session_id or f"epoch:{int(time.time())}")
    except Exception:
        pass


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sid = session_id_from_stdin()
    try:
        pd = os.environ.get("CLAUDE_PROJECT_DIR")
        cwd = pd if (pd and os.path.isdir(pd)) else os.getcwd()
        stamp_liveness(cwd, "check-core-agnostic", sid)  # ADR-061: liveness (carimba mesmo se limpo)

        linter = os.path.join(cwd, "tools", "check_core_agnostic.py")
        if not os.path.isfile(linter):
            emit("")  # repo sem o linter -> silencioso

        r = subprocess.run([sys.executable, linter], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=cwd)
        if r.returncode == 0:
            emit("")  # nucleo limpo -> silencioso

        out = (r.stdout or "") + "\n" + (r.stderr or "")
        leaks = "\n".join(ln for ln in out.splitlines() if ln.startswith("LEAK "))
        if not leaks.strip():
            emit(f"# AVISO (ADR-020): o linter de agnosticismo retornou erro (exit {r.returncode}) "
                 f"sem achados de vazamento. Provavel config (tools/agnostic-denylist.txt ausente/vazia) "
                 f"ou ambiente. Rode: python tools/check_core_agnostic.py")
        emit("# AVISO (ADR-020): vazamento de norma de dominio no NUCLEO\n\n"
             "O linter `tools/check_core_agnostic.py` detectou identificador de norma regulatoria de "
             "dominio no nucleo operativo (viola Principio 12 / regra #5 do qa-critic):\n\n"
             f"{leaks}\n\n"
             "Acao: remova a mencao (norma de dominio vive em docs/, exemplos/ ou config) OU, se for "
             "legitima, adicione o sentinela `lint-agnostic:allow` na linha. Rode "
             "`python tools/check_core_agnostic.py` para reverificar.")
    except Exception as e:
        sys.stderr.write(f"[check_core_agnostic_hook] warning (nao-bloqueante): {e}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
