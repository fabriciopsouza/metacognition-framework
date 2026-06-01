#!/usr/bin/env python3
"""Canário de ambiente limpo (ADR-036, item 4 do plano de remediação v2).

Prova a lógica de resolução offline (pip --dry-run --no-index): requirements vazio resolve (PASS);
requirements com pacote inexistente NÃO resolve sem índice (FAIL). Zero domínio. Se o pip do host
não suportar --dry-run, SKIP (ambiente não reprova build; a prova real roda no CI).

Uso: python tools/test_clean_env.py   (exit 0 PASS/SKIP; 1 se a resolução não distingue resolvível de não)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_clean_env import resolve_only  # noqa: E402


def main():
    with tempfile.TemporaryDirectory() as tmp:
        empty = os.path.join(tmp, "req_empty.txt")
        open(empty, "w").close()
        bogus = os.path.join(tmp, "req_bogus.txt")
        with open(bogus, "w", encoding="utf-8") as fh:
            # nome improvável de existir como pacote — e, com --no-index, nada resolve sem índice
            fh.write("pacote-que-nao-existe-zzz-framework-canary==9.9.9\n")

        ok_empty, out_empty = resolve_only(empty, no_network=True)
        if not ok_empty and ("no such option" in out_empty.lower() or "--dry-run" in out_empty.lower()
                             or "pip indisponível" in out_empty.lower()):
            print(f"SKIP: pip do host não suporta --dry-run/--no-index. CI prova. ({out_empty.strip()[:80]})",
                  file=sys.stderr)
            return 0
        ok_bogus, _ = resolve_only(bogus, no_network=True)

        fails = 0
        for desc, ok, expect in [
            ("requirements vazio resolve", ok_empty, True),
            ("requirements com pacote inexistente NÃO resolve (sem índice)", ok_bogus, False),
        ]:
            correct = ok == expect
            if not correct:
                fails += 1
            print(f"{'OK  ' if correct else 'FAIL'} [esperado {'PASS' if expect else 'FAIL'}] {desc}")
    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (resolução distingue requirements resolvível de não-resolvível)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
