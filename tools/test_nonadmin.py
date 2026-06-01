#!/usr/bin/env python3
"""Canário do perfil NON-ADMIN (ADR-047).

Invariante: o perfil non-admin INICIA sob restrição de scripts → `settings.nonadmin.json` NÃO pode
ter hooks de comando (que invocariam PowerShell). E a doutrina "gates anunciados" deve existir
(automação nunca invisível). Cross-platform (só lê arquivos).

Uso: python tools/test_nonadmin.py   (exit 0 PASS; 1 se o perfil non-admin tiver hooks ou faltar doutrina)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    fails = 0

    # 1. settings.nonadmin.json existe e NÃO tem hooks de comando
    na = os.path.join(ROOT, ".claude", "settings.nonadmin.json")
    if not os.path.isfile(na):
        print("FAIL: .claude/settings.nonadmin.json ausente"); return 1
    data = json.load(open(na, encoding="utf-8-sig"))
    hooks = data.get("hooks") or {}
    no_hooks = len(hooks) == 0
    if not no_hooks:
        fails += 1
    print(f"{'OK  ' if no_hooks else 'FAIL'} settings.nonadmin.json sem hooks de comando ({'inicia sob restrição' if no_hooks else 'TEM hooks!'})")

    # 2. bootstrap.py (instalação sem PowerShell) existe
    bp = os.path.isfile(os.path.join(ROOT, "bootstrap.py"))
    if not bp:
        fails += 1
    print(f"{'OK  ' if bp else 'FAIL'} bootstrap.py presente (setup sem PowerShell/admin)")

    # 3. doutrina "gates anunciados" presente (automação nunca invisível)
    doctrine = False
    for f in ("CLAUDE.md", "AGENTS.md"):
        p = os.path.join(ROOT, f)
        if os.path.isfile(p):
            t = open(p, encoding="utf-8-sig").read().lower()
            if "non-admin" in t and ("anuncia" in t or "anunciados" in t):
                doctrine = True
    if not doctrine:
        fails += 1
    print(f"{'OK  ' if doctrine else 'FAIL'} doutrina 'gates anunciados' em CLAUDE.md/AGENTS.md")

    # 4. guia presente
    guia = os.path.isfile(os.path.join(ROOT, "guia", "MODO-NON-ADMIN.md"))
    if not guia:
        fails += 1
    print(f"{'OK  ' if guia else 'FAIL'} guia/MODO-NON-ADMIN.md presente")

    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (perfil non-admin inicia sob restrição; automação anunciada, não invisível)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
