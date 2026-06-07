#!/usr/bin/env python3
"""Canário do onboarding (ADR-067 + EMENDA ADR-070). Prova: detecta o repo-framework (assinatura),
NÃO confunde um projeto-que-usa com o instalador, o popup só dispara no MASTER-CANÔNICO (export
public/premium carimbado role=shadow NÃO dispara — anti-vazamento), e o marker é idempotente (1×).

Uso: python tools/test_framework_onboarding.py   (exit 0 PASS; 1 se falha)
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from framework_onboarding import (  # noqa: E402
    is_framework_repo, is_canonical_master, needs_onboarding, mark_onboarded, onboarding_done,
)
import repo_identity  # noqa: E402

# Determinismo CI-safe: o checkout raso do CI (actions/checkout) não deixa origin/main como ref
# completa, então classify() não retorna MASTER-CANONICO no runner. As asserções de MASTER abaixo
# testam a LÓGICA (marker role=master + writable_master), não o estado git do runner -> mock classify.
# O teste de SHADOW continua via veto-do-marker (role=shadow), que NÃO chama classify (env-independente).
repo_identity.classify = lambda: {"verdict": "MASTER-CANONICO", "writable_master": True}


def _make_source_signature(root):
    """Cria a assinatura mínima do repo-fonte (is_framework_repo=True) num diretório de teste."""
    open(os.path.join(root, "AGENT-FRAMEWORK.md"), "w").close()
    os.makedirs(os.path.join(root, "_shared"), exist_ok=True)
    os.makedirs(os.path.join(root, "tools"), exist_ok=True)
    open(os.path.join(root, "tools", "web_export.py"), "w").close()

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
    #    Este repo é o MASTER-CANÔNICO (role=master + origin canônico) -> needs_onboarding=True.
    home = tempfile.mkdtemp(prefix="home_")
    n0 = needs_onboarding(ROOT, home)            # master + sem marker -> True
    mark_onboarded("use", home)
    n1 = needs_onboarding(ROOT, home)            # marcado -> False
    done = onboarding_done(home)
    bad = mark_onboarded("lixo", home)           # modo inválido recusado
    if not (n0 and not n1 and done and not bad):
        fails.append(f"fluxo de marker incorreto (n0={n0} n1={n1} done={done} bad={bad})")

    # 4. ANTI-VAZAMENTO (EMENDA ADR-070): export public/premium carimbado role=shadow tem a
    #    assinatura da fonte MAS NÃO é master -> popup NÃO dispara (não interroga o usuário final).
    shadow = tempfile.mkdtemp(prefix="shadow_")
    _make_source_signature(shadow)
    with open(os.path.join(shadow, ".repo-identity.json"), "w", encoding="utf-8") as fh:
        json.dump({"role": "shadow", "ai_owner": "claude"}, fh)
    home2 = tempfile.mkdtemp(prefix="home2_")
    if not is_framework_repo(shadow):
        fails.append("setup do teste: shadow deveria ter a assinatura da fonte")
    if is_canonical_master(shadow):
        fails.append("is_canonical_master(shadow) deveria ser False (role=shadow é trava física)")
    if needs_onboarding(shadow, home2):
        fails.append("VAZAMENTO: needs_onboarding(shadow) deveria ser False (popup não pode vazar p/ public/premium)")

    # 5. este repo (rodando do master canônico) É master.
    if not is_canonical_master(ROOT):
        fails.append("is_canonical_master(ROOT) deveria ser True (rodando do master canônico)")

    shutil.rmtree(shadow, ignore_errors=True)

    print(f"is_framework_repo(fonte)=True; projeto-que-usa=False; shadow→sem-popup; master(ROOT)=True; "
          f"1x idempotente — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (detecta instalador, ignora projeto, marca 1x)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
