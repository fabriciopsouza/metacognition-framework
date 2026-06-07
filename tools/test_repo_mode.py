#!/usr/bin/env python3
"""Canario do repo_mode (ADR-070/072). Prova: SOMBRA-EXPORT => 'user' (shadow nao desenvolve);
MASTER-CANONICO => 'dev'; clone/foreign/ambiguo => 'user' (conservador). Monkeypatch do verdito.

Uso: python tools/test_repo_mode.py   (exit 0 PASS; 1 se falha)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import repo_mode as rm  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    fails = []
    cases = {
        "SOMBRA-EXPORT": "user",
        "MASTER-CANONICO": "dev",
        "CLONE-VELHO/DIVERGENTE": "user",
        "FOREIGN": "user",
        "AMBIGUO": "user",
    }
    for verdict, expected in cases.items():
        got = rm.mode(lambda v=verdict: {"verdict": v})
        if got != expected:
            fails.append(f"verdict {verdict}: esperado '{expected}', veio '{got}'")

    # fail-safe: classify que explode -> 'user' (nunca 'dev' por defeito)
    def boom():
        raise RuntimeError("x")
    if rm.mode(boom) != "user":
        fails.append("classify com erro deveria cair em 'user' (conservador, nunca dev)")

    print(f"shadow=user; master=dev; clone/foreign/ambiguo=user; erro=user — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (modo por identidade: shadow nunca desenvolve)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
