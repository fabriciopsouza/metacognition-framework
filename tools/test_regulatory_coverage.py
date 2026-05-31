#!/usr/bin/env python3
"""Canário do meta-linter de cobertura regulada (ADR-043, item 11 do plano de remediação v2).

Prova: (a) a denylist expandida cobre as famílias reguladas conhecidas; (b) o linter DETECTA uma
família sem representante (não dá falso "tudo coberto"); (c) o disclaimer "não-exaustiva" permanece.

Uso: python tools/test_regulatory_coverage.py   (exit 0 PASS; 1 se a cobertura não é detectada corretamente)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_regulatory_coverage import coverage, FAMILIES, DISCLAIMER, load_denylist_text  # noqa: E402


def main():
    fails = 0

    # (a) denylist REAL expandida cobre todas as famílias conhecidas
    cobertas, descobertas = coverage()
    if descobertas:
        fails += 1
    print(f"{'OK  ' if not descobertas else 'FAIL'} denylist real cobre as {len(FAMILIES)} famílias "
          f"({len(cobertas)} cobertas; descobertas: {descobertas})")

    # (b) denylist sintética SEM o token financeiro -> família financeira é flagada
    deny_real = load_denylist_text()
    deny_sem_fin = "\n".join(l for l in deny_real.splitlines()
                             if not any(t in l for t in ("SOX", "Sarbanes", "BACEN", "Basel")))
    _, desc2 = coverage(deny_sem_fin)
    detecta = "financeiro/contábil" in desc2
    if not detecta:
        fails += 1
    print(f"{'OK  ' if detecta else 'FAIL'} remover tokens financeiros -> família flagada como FALTA "
          f"({'detectou' if detecta else 'NÃO detectou (falso tudo-coberto!)'})")

    # (c) disclaimer não-exaustiva presente
    tem_disc = "NÃO-EXAUSTIVA" in DISCLAIMER.upper() or "NAO-EXAUSTIVA" in DISCLAIMER.upper()
    if not tem_disc:
        fails += 1
    print(f"{'OK  ' if tem_disc else 'FAIL'} disclaimer 'não-exaustiva' mantido")

    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (cobertura detectada; lacuna flagada; disclaimer honesto)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
