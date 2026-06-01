#!/usr/bin/env python3
"""Canário do dicionário-contrato de entrada (ADR-046).

Fixtures sintéticas e agnósticas (CSV genérico, sem domínio): arquivo obrigatório presente com as
colunas obrigatórias → PASS; coluna obrigatória ausente → FAIL; arquivo obrigatório ausente → FAIL;
arquivo opcional ausente → PASS (não-bloqueante). Prova a auto-detecção+validação.

Uso: python tools/test_input_contract.py   (exit 0 PASS; 1 se o gate não distingue)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_input_contract import check  # noqa: E402

DICT = """# Dicionário-contrato (sintético)

## Contrato de entrada
### arquivo: fonte_*.csv | obrigatório
| coluna | tipo | obrigatória |
|---|---|---|
| chave | string | sim |
| periodo | int | sim |
| valor | float | sim |

### arquivo: dimensao_*.csv | opcional
| coluna | tipo | obrigatória |
|---|---|---|
| chave | string | sim |
"""

FONTE_OK = "chave,periodo,valor\nA,202501,0.1\n"
FONTE_SEM_VALOR = "chave,periodo\nA,202501\n"


def write(d, name, content):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(content)
    return p


def run_case(dict_text, files):
    with tempfile.TemporaryDirectory() as d:
        dp = write(d, "data-dictionary.md", dict_text)
        for name, content in files.items():
            write(d, name, content)
        return check(dp, d)


CASES = [
    ("fonte obrigatória presente com todas as colunas", {"fonte_2025.csv": FONTE_OK}, True),
    ("coluna obrigatória 'valor' ausente", {"fonte_2025.csv": FONTE_SEM_VALOR}, False),
    ("arquivo obrigatório ausente (nenhum fonte_*)", {"dimensao_x.csv": "chave\nA\n"}, False),
    ("opcional ausente, obrigatório ok", {"fonte_2025.csv": FONTE_OK}, True),
]


def main():
    fails = 0
    for desc, files, expect_ok in CASES:
        ok, problems = run_case(DICT, files)
        correct = ok == expect_ok
        if not correct:
            fails += 1
        status = "OK  " if correct else "FAIL"
        detail = "" if ok else f" -> {[p for p in problems if 'FALTA' not in p][:1] or problems[:1]}"
        print(f"{status} [esperado {'PASS' if expect_ok else 'FAIL'}] {desc}{detail}")
    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (auto-detecta arquivos + valida colunas obrigatórias; opcional não bloqueia)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
