#!/usr/bin/env python3
"""Canario process-evidence (ADR-074, parte FAIL-CLOSED determinista): a versao MAIS RECENTE do
CHANGELOG DEVE ter um checkpoint no history.md. Mecaniza o gap RECORRENTE "release sem fechamento
documentado" (ADR-069/070/071 fecharam sem checkpoint; 7 sessoes em 2026-06-02).

FORWARD-ONLY (regua §0): so gateia o release ATUAL — nao exige checkpoint retroativo das 22 versoes
historicas antigas (1.0-1.7 etc. nunca tiveram checkpoint individual; fabricar seria desonesto).

A parte NAO-determinista do process-evidence (qa-critic rodou; relatorios opt-in execution/cross-IA)
e DISCIPLINA + OFERTA no fechamento (ADR-074), nao fail-closed — relatorio opt-in nao pode ser exigido.

Uso: python tools/test_release_checkpoint.py   (exit 0 PASS; 1 se falha)
"""
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
        chg = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8-sig").read()
        hist = open(os.path.join(ROOT, "history.md"), encoding="utf-8-sig").read()
    except Exception as e:
        print(f"RESULTADO: FAIL (CHANGELOG/history ilegivel: {e})")
        return 1

    vers = re.findall(r"## \[(\d+\.\d+\.\d+)\]", chg)
    if not vers:
        print("RESULTADO: FAIL (nenhuma versao no CHANGELOG)")
        return 1
    latest = vers[0]  # topo do CHANGELOG = release atual

    ok = (latest in hist) or (f"v{latest}" in hist)
    if ok:
        print(f"release atual v{latest}: checkpoint presente no history.md — OK")
    else:
        print(f"release atual v{latest}: SEM checkpoint no history.md")
    print("-" * 50)
    print("RESULTADO:", f"PASS (release v{latest} tem fechamento documentado)" if ok
          else f"FAIL (release v{latest} sem checkpoint — documente o fechamento no history.md)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
