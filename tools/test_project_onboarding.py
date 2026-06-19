#!/usr/bin/env python3
"""Canário do project-onboarding/wayfinding (ADR-090) — prova FERRAMENTAL de que as 4 superfícies
existem e COMPÕEM (não recriam) os geradores existentes:
 (A) discovery/SKILL.md tem o fork greenfield × brownfield (ADR-090);
 (B) workflow generate-project-context existe e REFERENCIA geradores existentes (handoff/capabilities/explorer);
 (C) workflow document-project existe e referencia explorer + docops;
 (D) guia user-facing POR-ONDE-COMECAR existe.
Anti-reinvenção (régua §0): os workflows orquestram o que já existe — o canário falha se um workflow
não citar os geradores que deveria compor (sinal de que recriou em vez de reusar).
Fail-closed (exit 1 se faltar superfície ou composição).

Uso: python tools/test_project_onboarding.py   (exit 0 PASS; 1 se falha)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def read(rel):
    p = os.path.join(ROOT, rel)
    return open(p, encoding="utf-8").read() if os.path.isfile(p) else None


def main():
    fails = []

    # (A) fork greenfield/brownfield no discovery
    disc = read(".agent/skills/discovery/SKILL.md")
    if not disc or not (re.search(r"greenfield", disc, re.I) and re.search(r"brownfield", disc, re.I)
                        and "ADR-090" in disc):
        fails.append("(A) fork greenfield×brownfield (ADR-090) ausente no discovery/SKILL.md")

    # (B) generate-project-context COMPÕE geradores existentes
    gpc = read(".agent/workflows/generate-project-context.md")
    if not gpc:
        fails.append("(B) .agent/workflows/generate-project-context.md ausente")
    else:
        for ref in ("handoff.py", "CAPABILITIES", "explorer", "briefing", "knowledge_catalog"):
            if ref.lower() not in gpc.lower():
                fails.append(f"(B) generate-project-context não compõe '{ref}' (reusar, não recriar)")

    # (C) document-project COMPÕE explorer + docops
    dp = read(".agent/workflows/document-project.md")
    if not dp:
        fails.append("(C) .agent/workflows/document-project.md ausente")
    else:
        for ref in ("explorer", "docops"):
            if ref.lower() not in dp.lower():
                fails.append(f"(C) document-project não compõe '{ref}'")

    # (D) guia user-facing
    if read("guia/POR-ONDE-COMECAR.md") is None:
        fails.append("(D) guia/POR-ONDE-COMECAR.md (wayfinding user-facing) ausente")

    print(f"project-onboarding: 4 superfícies (fork A · workflows B/C compõem · guia D) — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (onboarding/wayfinding por composição; anti-reinvenção)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
