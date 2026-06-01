#!/usr/bin/env python3
"""Canário: check_delivery_floor mecaniza o piso runbook (premium). Exit 0 PASS.

SKIP (exit 0) se check_delivery_floor ausente — é premium, stripado do baseline.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "check_delivery_floor.py")


def _mk(root, rel):
    p = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write("x")


def _run(path, *extra):
    return subprocess.run([sys.executable, TOOL, path, *extra], capture_output=True).returncode


def run():
    if not os.path.isfile(TOOL):
        print("SKIP: check_delivery_floor.py ausente (premium stripado do baseline).")
        return 0
    fails = []
    with tempfile.TemporaryDirectory() as d:
        com = os.path.join(d, "com-runbook")
        _mk(com, "docs/runbook-de-validacao.md")
        if _run(com) != 0:
            fails.append("entrega COM runbook deveria PASS")

        sem = os.path.join(d, "sem-runbook")
        _mk(sem, "docs/relatorio.pdf")
        if _run(sem) == 0:
            fails.append("entrega SEM runbook deveria FAIL (exit 1)")

        # REGRESSÃO (qa-critic v1.37.0): substring NÃO pode passar como runbook
        fp = os.path.join(d, "falso-positivo")
        _mk(fp, "docs/invalidacao-de-proposta.md")
        _mk(fp, "docs/revalidacao-ambiental.md")
        if _run(fp) == 0:
            fails.append("'invalidacao'/'revalidacao' NÃO são runbook — não pode PASS (token exato)")
        if _run(fp, "--regulated") == 0:
            fails.append("falso-positivo em REGULADO é o pior caso — deve FAIL")
        if _run(sem, "--allow-skip", "caso trivial") != 0:
            fails.append("dispensa consciente deveria PASS fora de regulado")
        if _run(sem, "--allow-skip", "x", "--regulated") == 0:
            fails.append("dispensa NÃO pode valer em domínio regulado")

    if fails:
        print("FAIL:\n  - " + "\n  - ".join(fails))
        return 1
    print("PASS: piso runbook mecanizado (presente=PASS; ausente=FAIL; skip consciente; regulado bloqueia skip).")
    return 0


if __name__ == "__main__":
    sys.exit(run())
