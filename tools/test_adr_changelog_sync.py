#!/usr/bin/env python3
"""Canario doc-sync ADR<->CHANGELOG (mecaniza falha RECORRENTE). Toda ADR com Status Aceito DEVE
estar mencionada no CHANGELOG.md ('ADR-NNN'). Falha-recorrente observada: ADR-069/070/071 (e antes,
7 sessoes em 2026-06-02) Aceito/mergeado SEM entrada de CHANGELOG (consistency-gate fail-soft nao
disparou). Aqui vira FAIL-CLOSED: o gap nao pode mais passar silencioso (cerne prosa->mecanismo).

Uso: python tools/test_adr_changelog_sync.py   (exit 0 PASS; 1 se falha)
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    try:
        chg = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8-sig").read().lower()
    except Exception as e:
        print(f"RESULTADO: FAIL (CHANGELOG.md ilegivel: {e})")
        return 1

    missing, total = [], 0
    for a in sorted(glob.glob(os.path.join(ROOT, "docs", "adr", "*.md"))):
        name = os.path.basename(a)
        if "template" in name.lower():
            continue
        m = re.match(r"(\d+)-", name)
        if not m:
            continue
        txt = open(a, encoding="utf-8").read()
        if not re.search(r"status[:* ]+.*aceito", txt, re.I):  # so ADRs Aceito
            continue
        total += 1
        n = m.group(1)
        if f"adr-{n}" not in chg:
            missing.append(n)

    print(f"{total} ADR(s) Aceito; mencionadas no CHANGELOG: {total - len(missing)} — "
          f"{'OK' if not missing else 'FAIL'}")
    for n in missing:
        print(f"  - ADR-{n} Aceito mas AUSENTE do CHANGELOG (doc-sync: registre a mudanca)")
    print("-" * 50)
    print("RESULTADO:", "PASS (toda ADR Aceito esta no CHANGELOG)" if not missing
          else f"FAIL ({len(missing)} ADR sem doc-sync)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
