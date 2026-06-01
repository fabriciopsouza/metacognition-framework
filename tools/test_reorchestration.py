#!/usr/bin/env python3
"""Canário do gate de re-orquestração de bloco (ADR-045, opção C — emenda ao ADR-011).

Fixtures sintéticas e agnósticas: bloco fechado COM a decisão do PMO -> PASS; bloco fechado SEM
decisão -> FAIL (o maestro não conduziu); sem bloco fechado -> PASS (nada a auditar). Prova que o
gate audita só o último bloco e exige a decisão registrada.

Uso: python tools/test_reorchestration.py   (exit 0 PASS; 1 se o gate não distingue)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_reorchestration import check_text  # noqa: E402

H_OK = """# history
## bloco N
process-critic: APROVADO_LIMPO
RE-ORQUESTRAÇÃO: prosseguir para o próximo bloco (sem re-priorização)
"""

H_REWIND = """# history
## bloco N
process-critic: APROVADO_LIMPO
RE-ORQUESTRAÇÃO: rewind J3 — re-priorizar o item X antes de seguir
"""

H_MISSING = """# history
## bloco N
process-critic: APROVADO_LIMPO
(o PMO não registrou a decisão de condução do bloco)
"""

H_NO_BLOCK = """# history
## bloco N (em andamento)
trabalho em progresso; bloco ainda aberto
"""

# Bloco antigo sem decisão + bloco recente COM decisão -> audita só o último -> PASS
H_ONLY_LAST = """# history
## bloco antigo
process-critic: APROVADO_LIMPO
(convenção ainda não existia aqui)
## bloco recente
process-critic: APROVADO_LIMPO
RE-ORQUESTRAÇÃO: prosseguir
"""

CASES = [
    ("bloco fechado com decisão (prosseguir)", H_OK, True),
    ("bloco fechado com decisão (rewind)", H_REWIND, True),
    ("bloco fechado SEM decisão do PMO", H_MISSING, False),
    ("sem bloco fechado -> nada a auditar", H_NO_BLOCK, True),
    ("audita só o último bloco (antigo sem, recente com)", H_ONLY_LAST, True),
]


def main():
    fails = 0
    for desc, text, expect_ok in CASES:
        ok, motivo = check_text(text)
        correct = ok == expect_ok
        if not correct:
            fails += 1
        status = "OK  " if correct else "FAIL"
        print(f"{status} [esperado {'PASS' if expect_ok else 'FAIL'}] {desc}")
    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (audita o último bloco; exige a decisão de re-orquestração do PMO)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
