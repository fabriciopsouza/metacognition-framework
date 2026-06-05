#!/usr/bin/env python3
"""Canário do onboarding (ADR-067). Prova: detecta o repo-framework (assinatura), NÃO confunde um
projeto-que-usa com o instalador, e o marker é idempotente (1× — não re-pergunta).

Uso: python tools/test_framework_onboarding.py   (exit 0 PASS; 1 se falha)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from framework_onboarding import (  # noqa: E402
    is_framework_repo, needs_onboarding, mark_onboarded, onboarding_done,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main():
    fails = []

    # 1. este repo É o framework (assinatura completa).
    if not is_framework_repo(ROOT):
        fails.append("is_framework_repo(ROOT) deveria ser True (este é o repo-fonte)")

    # 2. um PROJETO que só USA (sem AGENT-FRAMEWORK.md/_shared/web_export) NÃO é o instalador (anti-FP).
    proj = tempfile.mkdtemp(prefix="proj_")
    os.makedirs(os.path.join(proj, ".agent", "skills"), exist_ok=True)  # tem skills, mas não é a fonte
    if is_framework_repo(proj):
        fails.append("is_framework_repo(projeto-que-usa) deveria ser False (sem assinatura da fonte)")

    # 3. onboarding 1× idempotente (home temp): precisa -> marca -> não precisa mais.
    home = tempfile.mkdtemp(prefix="home_")
    n0 = needs_onboarding(ROOT, home)            # framework repo + sem marker -> True
    mark_onboarded("use", home)
    n1 = needs_onboarding(ROOT, home)            # marcado -> False
    done = onboarding_done(home)
    bad = mark_onboarded("lixo", home)           # modo inválido recusado
    if not (n0 and not n1 and done and not bad):
        fails.append(f"fluxo de marker incorreto (n0={n0} n1={n1} done={done} bad={bad})")

    print(f"is_framework_repo(fonte)=True; projeto-que-usa=False; 1x idempotente — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (detecta instalador, ignora projeto, marca 1x)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
