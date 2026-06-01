#!/usr/bin/env python3
"""Canário do gate de completude pedido × entrega (ADR-034, item 2 do plano de remediação v2).

Reproduz o MODO de falha "entregou subconjunto do pedido" com fixtures **sintéticas e agnósticas**:
o pedido diz "para cada unidade, mês a mês, com acumulado"; uma entrega que valida só um mês /
sem acumulado DEVE falhar; a entrega que valida cada quantificador DEVE passar. Zero termo de domínio.

Uso: python tools/test_completeness.py   (exit 0 PASS; 1 se o gate não barra o subconjunto)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_completeness import check  # noqa: E402

REQ = """# Requirements — Indicador X

## Objetivo
Calcular o indicador X para cada unidade, mês a mês, com o valor acumulado.

## Cobertura exigida pelo pedido
- por unidade (cada unidade do conjunto)
- mês a mês (cada mês do intervalo)
- acumulado (realizado + acumulado)
"""

# validation que cobre TODOS os quantificadores
VAL_COMPLETA = """# validation.md
- V1: para cada unidade, o resultado é produzido e confere com o caso validado.
- V2: o cálculo roda mês a mês ao longo do intervalo, não só um mês.
- V3: o valor acumulado é calculado e exibido junto do realizado.
"""

# validation que cobre SUBCONJUNTO (regressão de campo): só um mês, sem acumulado, sem "cada"
VAL_SUBCONJUNTO = """# validation.md
- V1: o cálculo de um mês confere com o caso validado.
"""

# pedido SEM quantificadores → nada a exigir
REQ_SEM_QUANT = """# Requirements — Indicador X
## Objetivo
Calcular o indicador X para o período informado e exibir o resultado.
"""
VAL_SIMPLES = "# validation.md\n- V1: o resultado confere com o caso validado.\n"

# coverage declara tudo, mas validation valida só um mês (drop silencioso pós-declaração)
REQ_DECLARA = REQ
VAL_SO_DECLARA = """# validation.md
- V1: para cada unidade o resultado confere.
- V2: o acumulado é exibido.
"""  # falta validar "mês a mês" (mes)

CASES = [
    ("entrega cobre cada unidade + mês a mês + acumulado", REQ, VAL_COMPLETA, True),
    ("entrega valida só um mês / sem acumulado — regressão de campo", REQ, VAL_SUBCONJUNTO, False),
    ("pedido sem quantificadores -> nada a exigir", REQ_SEM_QUANT, VAL_SIMPLES, True),
    ("coverage declara tudo mas validation pula 'mês a mês'", REQ_DECLARA, VAL_SO_DECLARA, False),
]


def main():
    fails = 0
    for desc, req, val, expect_pass in CASES:
        quant, miss_cov, miss_val = check(req, val)
        ok = (not miss_cov and not miss_val)
        correct = ok == expect_pass
        if not correct:
            fails += 1
        status = "OK  " if correct else "FAIL"
        exp = "PASS" if expect_pass else "FAIL"
        detail = "" if ok else f" miss_cov={miss_cov} miss_val={miss_val}"
        print(f"{status} [esperado {exp:4}] {desc} (detectado={sorted(quant)}{detail})")
    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails} caso(s))" if fails
          else "PASS (gate barra subconjunto do pedido; aceita entrega completa)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
