#!/usr/bin/env python3
"""Canario context_budget (ADR-029 doc-intake / pedido do dono 2026-06-08): a decisao LER-INTEIRO vs
FRACIONAR e deterministica e correta nas fronteiras. Mecaniza "usar doc-intake p/ contexto maior".

Uso: python tools/test_context_budget.py   (exit 0 PASS; 1 se falha)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import context_budget as cb

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    fails = []

    # 1) estimativa chars/4 (ceil)
    if cb.estimate_tokens(0) != 0:
        fails.append("estimate_tokens(0) != 0")
    if cb.estimate_tokens(4) != 1:
        fails.append("estimate_tokens(4) != 1")
    if cb.estimate_tokens(5) != 2:
        fails.append("estimate_tokens(5) != 2 (ceil)")

    d = tempfile.mkdtemp()
    # 2) arquivo pequeno -> LER-INTEIRO (exit 0)
    small = os.path.join(d, "small.md")
    open(small, "w", encoding="utf-8").write("x" * 100)
    r = cb.assess(small, budget_tokens=100)
    if r["decision"] != "LER-INTEIRO" or r["over_budget"]:
        fails.append(f"small deveria LER-INTEIRO, veio {r['decision']}")

    # 3) arquivo grande -> FRACIONAR (over budget)
    big = os.path.join(d, "big.md")
    open(big, "w", encoding="utf-8").write("x" * (100 * 4 + 8))  # ~101 tokens > 100
    r = cb.assess(big, budget_tokens=100)
    if r["decision"] != "FRACIONAR" or not r["over_budget"]:
        fails.append(f"big deveria FRACIONAR, veio {r['decision']} (tokens={r['est_tokens']})")
    if "doc_intake" not in r["reason"]:
        fails.append("razao de FRACIONAR nao aponta doc_intake")

    # 4) path inexistente -> ERRO/exit!=0
    r = cb.assess(os.path.join(d, "nope.md"))
    if r.get("exists"):
        fails.append("path inexistente reportado como existente")

    # 5) exit codes da CLI (0 cabe, 3 fracione)
    if cb.main([small, "--budget", "100"]) != 0:
        fails.append("CLI small exit != 0")
    if cb.main([big, "--budget", "100"]) != 3:
        fails.append("CLI big exit != 3")

    print("context_budget:", "OK" if not fails else f"FAIL ({len(fails)})")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (decisao de fracionamento deterministica)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
