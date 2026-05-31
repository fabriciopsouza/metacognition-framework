#!/usr/bin/env python3
"""Runner único dos canários do framework (ADR-040 — CI cross-platform).

CONTEXTO: os `tools/test_*.py` deste repo são **canários standalone** (exit 0 = PASS,
exit != 0 = FAIL), NÃO casos pytest-collectáveis — vários executam trabalho em import-time
e chamam `sys.exit()`. Rodar `pytest tools/` quebra na importação. Este runner é o
entrypoint canônico (local e CI): descobre cada `test_*.py`, roda como subprocesso com o
MESMO interpretador, agrega e devolve exit = nº de canários que falharam.

Cross-platform por construção (ADR-040): nenhuma suposição de shell — só `sys.executable`.
Canários que dependem de pwsh/bash/jq se auto-marcam SKIP (exit 0) quando o shell falta,
então o runner nunca falha por ambiente — só por canário que efetivamente reprovou.

Uso:
    python tools/run_canaries.py            # roda todos os test_*.py de tools/
    python tools/run_canaries.py -v         # mostra stdout de cada canário
    python tools/run_canaries.py a b ...     # roda só os nomes/substrings dados

Exit 0 se todos passaram; N>0 = nº de canários que falharam.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
SELF = os.path.basename(__file__)


def discover(filters):
    out = []
    for fn in sorted(os.listdir(TOOLS)):
        if not (fn.startswith("test_") and fn.endswith(".py")):
            continue
        if filters and not any(f in fn for f in filters):
            continue
        out.append(fn)
    return out


def main(argv):
    verbose = "-v" in argv
    filters = [a for a in argv[1:] if not a.startswith("-")]
    canaries = discover(filters)
    if not canaries:
        print("nenhum canário test_*.py encontrado", file=sys.stderr)
        return 1

    failed, skipped, passed = [], [], []
    for fn in canaries:
        path = os.path.join(TOOLS, fn)
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        is_skip = proc.returncode == 0 and "SKIP" in out and "PASS" not in out.upper()
        if proc.returncode == 0:
            (skipped if is_skip else passed).append(fn)
            tag = "SKIP" if is_skip else "PASS"
        else:
            failed.append(fn)
            tag = f"FAIL({proc.returncode})"
        print(f"{tag:9} {fn}")
        if verbose or proc.returncode != 0:
            for line in out.strip().splitlines():
                print(f"    | {line}")

    print("-" * 50)
    print(f"RESULTADO: {len(passed)} PASS · {len(skipped)} SKIP · {len(failed)} FAIL "
          f"(de {len(canaries)} canários)")
    if failed:
        print("FALHARAM: " + ", ".join(failed))
    return len(failed)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
