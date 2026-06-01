#!/usr/bin/env python3
"""Canário "porta do usuário" (ADR-036, item 4 do plano de remediação v2).

Reproduz o MODO de falha com entry-points sintéticos: um com `input()` bloqueante como única
via DEVE reprovar sem TTY; um que lê de argv DEVE passar; o guardado por argv passa COM args e
reprova SEM args. Zero domínio.

Uso: python tools/test_entrypoint_no_tty.py   (exit 0 PASS; 1 se o gate não barra o input bloqueante)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_entrypoint_tty import run_no_tty  # noqa: E402

EP_INPUT = "x = input('mes? ')\nprint('calculou', x)\n"                       # FAIL sem TTY
EP_ARGV = "import sys\nprint('calculou', sys.argv[1:] or 'default')\n"          # PASS
EP_GUARD = (
    "import sys\n"
    "if len(sys.argv) > 1:\n"
    "    mes = sys.argv[1]\n"
    "else:\n"
    "    mes = input('mes? ')\n"
    "print('calculou', mes)\n"
)


def write(tmp, name, content):
    p = os.path.join(tmp, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(content)
    return p


def main():
    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        ep_input = write(tmp, "ep_input.py", EP_INPUT)
        ep_argv = write(tmp, "ep_argv.py", EP_ARGV)
        ep_guard = write(tmp, "ep_guard.py", EP_GUARD)
        cases = [
            ("input() bloqueante como única via", run_no_tty(ep_input, timeout=8), "FAIL"),
            ("entry-point lê de argv (não-interativo)", run_no_tty(ep_argv, timeout=8), "PASS"),
            ("input() guardado, rodado COM args", run_no_tty(ep_guard, ["07"], timeout=8), "PASS"),
            ("input() guardado, rodado SEM args", run_no_tty(ep_guard, timeout=8), "FAIL"),
        ]
        for desc, (verdict, detail), expect in cases:
            ok = verdict == expect
            if not ok:
                fails += 1
            print(f"{'OK  ' if ok else 'FAIL'} [esperado {expect:4} -> {verdict}] {desc}  ({detail})")
    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails} caso(s))" if fails
          else "PASS (gate barra input() bloqueante; aceita entry-point não-interativo)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
