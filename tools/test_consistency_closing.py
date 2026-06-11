#!/usr/bin/env python3
"""Canario de consistencia de fechamento FAIL-CLOSED no CI (emenda ADR-030 / plano anti-bypass E2).

O `consistency-gate.ps1` (ADR-030) e **fail-soft** E e **hook PowerShell** -> vetado pelo Kaspersky
nesta maquina -> "nao disparou em ~7 fechamentos" (falha real, execution-report 2026-06-08). O gate
EXISTE mas nao e enforcado. Aqui as dimensoes CI-decidiveis viram **FAIL-CLOSED em Python**
(nao-vetoavel, roda na suite run_canaries): mecaniza o gap "gate existe mas nao disparou".

NAO duplica (regua §0) — estas dims ja sao enforcadas por outros canarios:
  - checkpoint-no-history        -> test_release_checkpoint.py
  - ADR Aceito presente no CHANGELOG -> test_adr_changelog_sync.py
  - versao README x CHANGELOG x vitrine -> test_marketing_claims.py

Aqui ficam as dims do consistency-gate AINDA nao enforcadas em lugar nenhum:
  (1) numero de ADR DUPLICADO (dim 'contagens')
  (2) ADR citado no CHANGELOG (= mudanca entregue) mas ainda `Status: Proposto` — bug RECORRENTE
      (ADR-051 mergeado-como-Proposto; complementa o sentido inverso do adr_changelog_sync).
Dims nao-decidiveis no CI (unpushed: CI e pos-push; transients _intake) sao ADVISORY: informa, nao reprova.

Uso: python tools/test_consistency_closing.py   (exit 0 PASS; 1 se falha)
"""
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    fails = []
    try:
        chg = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8-sig").read().lower()
    except Exception as e:
        print(f"RESULTADO: FAIL (CHANGELOG.md ilegivel: {e})")
        return 1

    nums = {}
    proposto_shipped = []
    for a in sorted(glob.glob(os.path.join(ROOT, "docs", "adr", "*.md"))):
        name = os.path.basename(a)
        if "template" in name.lower():
            continue
        m = re.match(r"(\d+)-", name)
        if not m:
            continue
        n = m.group(1)
        nums.setdefault(n, []).append(name)
        txt = open(a, encoding="utf-8").read()
        # ancora na LINHA do campo Status (como consistency-gate.ps1) — senao casa a palavra
        # "Proposto" no corpo do ADR (ex.: "ADRs em 'Proposto'") e gera falso-positivo.
        is_proposto = bool(re.search(r"(?im)^\s*-?\s*Status:\s*(?:\*\*)?\s*proposto", txt))
        # (2) entregue (citado no CHANGELOG) mas ainda Proposto = o bug recorrente ADR-051
        if is_proposto and f"adr-{n}" in chg:
            proposto_shipped.append(name)

    # (1) numeros de ADR duplicados (dim 'contagens')
    dups = {n: fs for n, fs in nums.items() if len(fs) > 1}
    for n, fs in sorted(dups.items()):
        fails.append(f"ADR numero {n} DUPLICADO: {', '.join(fs)}")
    for name in proposto_shipped:
        fails.append(f"{name} citado no CHANGELOG (entregue) mas ainda Status: Proposto "
                     f"(flip para Aceito ou remova do CHANGELOG — bug recorrente ADR-051)")

    # --- ADVISORY (nao reprova): dims que o CI nao decide ---
    try:
        cnt = subprocess.run(["git", "-C", ROOT, "rev-list", "--count", "@{upstream}..HEAD"],
                             capture_output=True, text=True).stdout.strip()
        if cnt.isdigit() and int(cnt) > 0:
            print(f"[advisory] {cnt} commit(s) nao-pushado(s) (recovery real = conta GitHub; push antes de fechar)")
    except Exception:
        pass
    intake = os.path.join(ROOT, "docs", "_intake")
    if os.path.isdir(intake):
        leftover = [f for f in os.listdir(intake) if os.path.isfile(os.path.join(intake, f))]
        if leftover:
            print(f"[advisory] {len(leftover)} transiente(s) em docs/_intake/ (remover no fechamento): {', '.join(leftover)}")

    print(f"{len(nums)} ADR(s); duplicatas: {len(dups)}; entregue-mas-Proposto: {len(proposto_shipped)} — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (fechamento consistente: sem duplicata de ADR; nada entregue ainda Proposto)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
