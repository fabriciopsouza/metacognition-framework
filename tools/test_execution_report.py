#!/usr/bin/env python3
"""Canário do execution-report (ADR-038, item 6 do plano de remediação v2).

Prova a invariante: encerramento sem report = FAIL; report sem o placar = FAIL; número de token
fabricado quando a telemetria está ausente = FAIL (deve dizer NÃO MEDIDO); report honesto = PASS.
Também confirma que o report auto-gerado (default, sem telemetria) já passa. Zero domínio.

Uso: python tools/test_execution_report.py   (exit 0 PASS; 1 se a validação não distingue honesto de fabricado)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from execution_report import validate_report, build_report  # noqa: E402

REPORT_HONESTO = build_report()  # default: tokens = NÃO MEDIDO

REPORT_FABRICADO = """# Execution-report
- Tokens: 152300
- Tempo (wall-clock): 45 min
- Turnos: 11
- Arquivos tocados: 13
- Testes: 6/6
- Rodadas de retrabalho: 3
## Placar gate × achado
| Achado | Quem pegou | Gate |
|---|---|---|
| bug | agente | qa |
"""

REPORT_TOKEN_COM_FONTE = REPORT_FABRICADO.replace(
    "- Tokens: 152300", "- Tokens: input 100000 + output 52300 (fonte: transcripts ADR-026)")

REPORT_SEM_PLACAR = """# Execution-report
- Tokens: NÃO MEDIDO (sem telemetria exposta)
- Tempo (wall-clock): NÃO MEDIDO
- Turnos: 11
- Arquivos tocados: 13
- Testes: 6/6
- Rodadas de retrabalho: 3
"""

CASES = [
    ("report ausente (encerramento sem report)", "", False),
    ("report auto-gerado honesto (NÃO MEDIDO)", REPORT_HONESTO, True),
    ("report com número de token fabricado (sem fonte)", REPORT_FABRICADO, False),
    ("report com número de token + fonte declarada", REPORT_TOKEN_COM_FONTE, True),
    ("report sem o placar gate × achado", REPORT_SEM_PLACAR, False),
]


def main():
    fails = 0
    for desc, text, expect_ok in CASES:
        ok, problems = validate_report(text)
        correct = ok == expect_ok
        if not correct:
            fails += 1
        status = "OK  " if correct else "FAIL"
        exp = "PASS" if expect_ok else "FAIL"
        detail = "" if ok else f" -> {problems}"
        print(f"{status} [esperado {exp:4}] {desc}{detail}")
    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails} caso(s))" if fails
          else "PASS (valida report; reprova ausência, falta de placar e token fabricado)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
