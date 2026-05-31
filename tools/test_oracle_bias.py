#!/usr/bin/env python3
"""Canário anti-viés-de-oráculo (ADR-035, item 3 do plano de remediação v2).

Reproduz o MODO de falha com fixtures sintéticas e agnósticas: duas colunas-irmãs ("coluna-a",
"coluna-b", "coluna-total") cujos números ficam perto do alvo. O gate DEVE exigir registro de qual
é a referência e por quê (confirmação do dono + justificativa). Mapeamento por inferência — mesmo
batendo o alvo — DEVE reprovar. Over-correção por rótulo (trocar por uma coluna literal sem prova)
também reprova. Zero termo de domínio.

Uso: python tools/test_oracle_bias.py   (exit 0 PASS; 1 se o gate não exige o registro)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_field_mapping import check_text  # noqa: E402

REGISTRADO = """# Requirements

## Mapeamento de campo-fonte
- referencia -> coluna-total (= coluna-a + coluna-b) | confirmacao: [CONFIRMADO] pelo dono | porque: a referencia do indicador e a soma A+B, provada celula a celula contra o caso validado | irmas descartadas: coluna-a (so um componente)
"""

INFERENCIA = """# Requirements

## Mapeamento de campo-fonte
- referencia -> coluna-a (bate 97% do alvo, deve ser essa)
"""

OVERCORRECTION = """# Requirements

## Mapeamento de campo-fonte
- referencia -> coluna-b | o dono falou "literal" entao troquei para a coluna de mesmo nome, caiu para 95% mas o nome casa
"""

SEM_SECAO = """# Requirements

## Objetivo
Calcular o indicador X. (não há mapeamento de campo-fonte ambíguo a registrar)
"""

CASES = [
    ("mapeamento registrado (confirmação + justificativa)", REGISTRADO, True),
    ("mapeamento por inferência que bate o alvo", INFERENCIA, False),
    ("over-correção por rótulo, sem prova numérica", OVERCORRECTION, False),
    ("sem seção de mapeamento -> nada a registrar", SEM_SECAO, True),
]


def main():
    fails = 0
    for desc, text, expect_pass in CASES:
        has_sec, bad = check_text(text)
        ok = (len(bad) == 0)
        correct = ok == expect_pass
        if not correct:
            fails += 1
        status = "OK  " if correct else "FAIL"
        exp = "PASS" if expect_pass else "FAIL"
        detail = "" if ok else f" -> falta registro em {len(bad)} linha(s)"
        print(f"{status} [esperado {exp:4}] {desc}{detail}")
    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails} caso(s))" if fails
          else "PASS (gate exige registro do mapeamento; reprova inferência/over-correção)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
