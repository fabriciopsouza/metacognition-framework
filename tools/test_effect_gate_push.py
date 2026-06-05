#!/usr/bin/env python3
"""Canário da regra git-push-force do effect-gate (ADR-039).

Bug provado (2026-06-02): `git commit -F - ...; git push ...` num só comando era DENY indevido —
o comando é casado em minúsculas, `-F` (de commit --file) vira `-f`, e o padrão de força antigo
`(^| )-f( |$)` casava esse `-f` em qualquer lugar. Com `git push` presente, o `all` batia → deny.

Fix: ancorar o flag de força AO push (`git +push( +[^ ]+)* +(--force( |$)|-f( |$))`).
Este teste valida a POLÍTICA (effect-rules.json) — parity-agnóstico (.ps1↔.sh usam o mesmo .json).

Uso: python tools/test_effect_gate_push.py   (exit 0 PASS; 1 se algum caso falha)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(ROOT, "tools", "effect-rules.json")


def rule_matches(rule, cmd):
    """Replica o motor: casa se TODOS de 'all' batem E NENHUM de 'none' bate (comando em minúsculas)."""
    low = cmd.lower()
    if not all(re.search(p, low) for p in rule.get("all", [])):
        return False
    if any(re.search(p, low) for p in rule.get("none", [])):
        return False
    return True


# (descrição, comando, deve_disparar_o_deny)
CASES = [
    ("FALSO-POSITIVO: commit -F + push normal (o bug)",
     "git commit -F - <<'EOF'\nmsg\nEOF\ngit push -u origin feat/x", False),
    ("push normal sozinho", "git push -u origin main", False),
    ("push --force", "git push --force", True),
    ("push -f", "git push -f", True),
    ("push -u origin x --force (flag depois)", "git push -u origin x --force", True),
    ("push --force-with-lease (permitido)", "git push --force-with-lease origin main", False),
    ("commit --file + push --force (força real ainda pega)",
     "git commit --file - <<'EOF'\nm\nEOF\ngit push --force origin main", True),
]


def main():
    data = json.load(open(RULES, encoding="utf-8"))
    rules = data["rules"] if isinstance(data, dict) and "rules" in data else data
    rule = next((r for r in rules if r.get("id") == "git-push-force"), None)
    if not rule:
        print("FAIL: regra git-push-force não encontrada")
        return 1

    fails = 0
    for desc, cmd, expect_deny in CASES:
        got = rule_matches(rule, cmd)
        ok = got == expect_deny
        fails += 0 if ok else 1
        print(f"{'OK  ' if ok else 'FAIL'} [esperado {'DENY' if expect_deny else 'ALLOW'}] {desc}")
    print("-" * 60)
    print("RESULTADO:", "PASS (força real pega; commit -F + push normal liberado)"
          if not fails else f"FAIL ({fails} caso(s))")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
