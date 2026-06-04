#!/usr/bin/env python3
"""Canário do execution-report dois-tiers (ADR-038 + ADR-052).

Prova as invariantes:
  OWNER (ADR-038): encerramento sem report = FAIL; sem placar = FAIL; token fabricado = FAIL; honesto = PASS.
  EXTERNAL (ADR-052): whitelist barra texto livre/PII; só passa schema codificado; opt-out e detector funcionam.
Hipótese adversarial (qa-critic): o whitelist VAZA até prova em contrário. Zero domínio.

Uso: python tools/test_execution_report.py   (exit 0 PASS; 1 se qualquer caso falha)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from execution_report import (  # noqa: E402
    validate_report, build_report, build_external_report, validate_external_report,
    detect_tier, telemetry_enabled, learnings_public,
)

# ----------------------------------------------------------------- OWNER (compat ADR-038)
REPORT_HONESTO = build_report()  # default tier=owner; tokens = NÃO MEDIDO

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
REPORT_TOKEN_COM_FONTE = build_report(  # ADR-062: via build_owner_report -> inclui seções de aprendizado
    tokens_line="input 100000 + output 52300 (fonte: transcripts ADR-026)")
# ADR-062: report completo MENOS as seções de aprendizado -> deve FALHAR (obrigação nova).
REPORT_SEM_APRENDIZADO = REPORT_FABRICADO.replace("- Tokens: 152300", "- Tokens: NÃO MEDIDO")
REPORT_SEM_PLACAR = """# Execution-report
- Tokens: NÃO MEDIDO (sem telemetria exposta)
- Tempo (wall-clock): NÃO MEDIDO
- Turnos: 11
- Arquivos tocados: 13
- Testes: 6/6
- Rodadas de retrabalho: 3
"""

# ----------------------------------------------------------------- EXTERNAL (ADR-052)
EXT_HONESTO = build_external_report(framework_version="1.39.0", execution_mode="default",
                                    route="squad", turnos="11", retrabalho="2", session_id="a1b2c3",
                                    gates_fired=[("route-gate", "pass"), ("mission-gate", "override")],
                                    failure_points=[("hook", "compaction-gate", "missed", "j4")],
                                    correction_events=[("rewind", "j3", "7")])

# Ataques que o whitelist DEVE reprovar:
# token de cliente FICTÍCIO de propósito (não usar nome real — seria o próprio vazamento que testamos)
EXT_TEXTO_LIVRE = EXT_HONESTO + "\n## notas\n- O cliente ACME-FICTICIO pediu uma mudanca no calculo.\n"
EXT_EMAIL = EXT_HONESTO.replace("session_id: a1b2c3", "session_id: joao@cliente.com")
EXT_CPF = EXT_HONESTO + "\n- id: 123.456.789-00; mechanism: gate; failure: missed; junction: na\n"
EXT_PROSA_COMO_VALOR = EXT_HONESTO.replace(
    "- type: rewind; junction: j3; turn: 7",
    "- type: rewind; junction: j3; turn: porque o usuario reclamou bastante do resultado")
EXT_ENUM_INVALIDO = EXT_HONESTO.replace("failure: missed", "failure: explodiu")
EXT_SEM_TIER = EXT_HONESTO.replace("tier: external\n", "")
EXT_SECAO_FORJADA = EXT_HONESTO + '\n## payload_secreto\n- dado: "informacao sensivel do cliente aqui"\n'

CASES = [
    # (desc, validador, texto, espera_ok)
    ("OWNER ausente", validate_report, "", False),
    ("OWNER honesto (NÃO MEDIDO)", validate_report, REPORT_HONESTO, True),
    ("OWNER token fabricado", validate_report, REPORT_FABRICADO, False),
    ("OWNER token + fonte", validate_report, REPORT_TOKEN_COM_FONTE, True),
    ("OWNER sem placar", validate_report, REPORT_SEM_PLACAR, False),
    ("OWNER sem seção de aprendizado (ADR-062)", validate_report, REPORT_SEM_APRENDIZADO, False),
    ("EXTERNAL honesto (schema)", validate_external_report, EXT_HONESTO, True),
    ("EXTERNAL com texto livre (cliente)", validate_external_report, EXT_TEXTO_LIVRE, False),
    ("EXTERNAL com e-mail em campo", validate_external_report, EXT_EMAIL, False),
    ("EXTERNAL com CPF", validate_external_report, EXT_CPF, False),
    ("EXTERNAL prosa como valor", validate_external_report, EXT_PROSA_COMO_VALOR, False),
    ("EXTERNAL enum inválido", validate_external_report, EXT_ENUM_INVALIDO, False),
    ("EXTERNAL sem tier", validate_external_report, EXT_SEM_TIER, False),
    ("EXTERNAL seção forjada c/ texto", validate_external_report, EXT_SECAO_FORJADA, False),
    # validate_report deve INFERIR external e barrar (não tratar como owner)
    ("dispatch infere external e barra texto livre", validate_report, EXT_TEXTO_LIVRE, False),
    ("dispatch infere external honesto", validate_report, EXT_HONESTO, True),
]


def main():
    fails = 0
    for desc, fn, text, expect_ok in CASES:
        ok, problems = fn(text)
        correct = ok == expect_ok
        fails += 0 if correct else 1
        status = "OK  " if correct else "FAIL"
        exp = "PASS" if expect_ok else "FAIL"
        detail = "" if ok else f" -> {problems[:2]}"
        print(f"{status} [esperado {exp:4}] {desc}{detail}")

    # detector de tier: este repo TEM docs/_private/ -> owner
    tier = detect_tier(ROOT)
    det_ok = tier == "owner"
    fails += 0 if det_ok else 1
    print(f"{'OK  ' if det_ok else 'FAIL'} detect_tier(repo do dono) == owner (got {tier!r})")

    # ADR-062: learnings_public no report OWNER limpo -> publicavel (sem problems) + header presente.
    pub, problems = learnings_public(REPORT_HONESTO, ROOT)
    lp_ok = (not problems) and "PÚBLICO ANONIMIZADO" in pub
    fails += 0 if lp_ok else 1
    print(f"{'OK  ' if lp_ok else 'FAIL'} learnings_public (report limpo -> publicavel) "
          f"{'' if lp_ok else problems[:2]}")

    # opt-out: env desliga o tier external
    os.environ["FRAMEWORK_NO_TELEMETRY"] = "1"
    off = telemetry_enabled(ROOT) is False
    del os.environ["FRAMEWORK_NO_TELEMETRY"]
    fails += 0 if off else 1
    print(f"{'OK  ' if off else 'FAIL'} opt-out via FRAMEWORK_NO_TELEMETRY desliga geração")

    print("-" * 60)
    print("RESULTADO:", f"FAIL ({fails} caso(s))" if fails else
          "PASS (owner ADR-038 + whitelist external ADR-052 + detector + opt-out)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
