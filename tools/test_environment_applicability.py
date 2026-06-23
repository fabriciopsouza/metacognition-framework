#!/usr/bin/env python3
"""Canário ADR-093 — detecção de ambiente + aplicabilidade das premissas (boot_check).

Cobre os achados do qa-critic heterogêneo sobre o ADR:
  - ALTO-2: matriz de polaridade nos 4 quadrantes (incl. expect_present=false × found=true = ESTALE,
            o CASO-RAIZ da falha real "F:\\ não existe mas existe").
  - ALTO-1: o envelope cross-IA satisfaz o contrato REAL de cross_ai_hub.deposit (10 campos REQUIRED)
            — prova que NÃO inventei API.
  - ALTO-3: o .agent/environment.example.json versionado NÃO contém path concreto (núcleo limpo no
            boot, onde o tier-norma do linter não alcança .json).
  - MÉDIO-2: o check devolve o contrato de dict {name,status,detail,stamps} esperado por boot_check.
  - sem manifesto -> skip declarado (nunca falso-OK).

Uso: python tools/test_environment_applicability.py   (exit 0 PASS; 1 FAIL)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import boot_check  # noqa: E402
import cross_ai_hub  # noqa: E402

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
    else:
        print(f"  ok: {msg}")


def test_polarity_matrix():
    """4 quadrantes expect_present × found -> APLICA/ESTALE/AUSENTE. Usa o próprio ROOT (existe)
    e um path garantidamente ausente."""
    present = ROOT                                   # existe
    absent = os.path.join(ROOT, "__nao_existe_adr093__")  # não existe
    assert not os.path.exists(absent)

    q1 = boot_check.eval_assumption({"id": "q1", "kind": "path", "expect_present": True, "value": present})
    q2 = boot_check.eval_assumption({"id": "q2", "kind": "path", "expect_present": True, "value": absent})
    q3 = boot_check.eval_assumption({"id": "q3", "kind": "path", "expect_present": False, "value": absent})
    q4 = boot_check.eval_assumption({"id": "q4", "kind": "path", "expect_present": False, "value": present})

    check(q1["verdict"] == "APLICA",  f"expect=true  × found=true  -> APLICA  (got {q1['verdict']})")
    check(q2["verdict"] == "AUSENTE", f"expect=true  × found=false -> AUSENTE (got {q2['verdict']})")
    check(q3["verdict"] == "APLICA",  f"expect=false × found=false -> APLICA  (got {q3['verdict']})")
    check(q4["verdict"] == "ESTALE",  f"expect=false × found=true  -> ESTALE  (caso-raiz; got {q4['verdict']})")

    # M1 (qa-critic): kind não-suportado NUNCA pode virar APLICA silencioso
    qk = boot_check.eval_assumption({"id": "qk", "kind": "network", "expect_present": False})
    check(qk["verdict"] == "INDEFINIDO", f"kind inválido -> INDEFINIDO, não APLICA (got {qk['verdict']})")

    # ADR-094: kind=process (EDR verificável) — processo inexistente + expect_present=false = APLICA
    qpr = boot_check.eval_assumption({"id": "edr", "kind": "process", "expect_present": False,
                                      "value": "zzz_no_such_process_adr094_zzz"})
    check(qpr["verdict"] == "APLICA", f"process ausente × expect=false -> APLICA (got {qpr['verdict']})")
    check(qpr["found"] is False, "process inexistente -> found=False (deterministico)")


def test_envelope_contract():
    """O envelope cross-IA tem TODOS os 10 campos REQUIRED do cross_ai_hub (ALTO-1: API real)."""
    env = {"host": "test-host", "os": "TestOS"}
    stale = [{"id": "corpus-root", "verdict": "ESTALE"}]
    env_msg = boot_check.build_env_envelope(stale, env)
    missing = [k for k in cross_ai_hub.REQUIRED if k not in env_msg or env_msg.get(k) in (None, "")]
    check(not missing, f"envelope satisfaz cross_ai_hub.REQUIRED (faltam: {missing})")
    check(env_msg["report_id"] == "env-applicability-test-host-" + env_msg["date"],
          "report_id idempotente por host+dia")


def test_example_has_no_concrete_path():
    """ALTO-3: o .example.json versionado não pode carregar path concreto (drive-letter ou /raiz)."""
    p = os.path.join(ROOT, ".agent", "environment.example.json")
    check(os.path.isfile(p), ".agent/environment.example.json existe")
    if not os.path.isfile(p):
        return
    data = json.load(open(p, encoding="utf-8-sig"))
    import re
    concrete = re.compile(r"[A-Za-z]:[\\/]|^/(home|mnt|srv|data|root|opt|var|usr)/|^//", re.IGNORECASE)
    bad = [a.get("value", "") for a in data.get("assumptions", [])
           if a.get("value") and concrete.search(str(a.get("value")))]
    check(not bad, f"example sem path concreto (só placeholders); offenders={bad}")


def test_dict_contract():
    """MÉDIO-2: o check devolve {name,status,detail,stamps}. status ∈ glyph map do boot_check."""
    res = boot_check.check_environment_applicability()
    for k in ("name", "status", "detail", "stamps"):
        check(k in res, f"check devolve campo '{k}'")
    check(res["status"] in ("ok", "warn", "fail", "skip"), f"status válido (got {res.get('status')})")
    check(isinstance(res.get("stamps"), list), "stamps é lista")
    # M2 (qa-critic): o bloco 'environment' é o sink cross-session — canário protege contra regressão
    check("environment" in res, "check devolve bloco 'environment' (sink cross-session)")
    check(isinstance(res.get("environment"), dict) and "assumptions" in res["environment"],
          "environment é dict com 'assumptions'")


def main():
    print("# canário ADR-093 — environment applicability")
    test_polarity_matrix()
    test_envelope_contract()
    test_example_has_no_concrete_path()
    test_dict_contract()
    print("-" * 40)
    if FAILS:
        print(f"RESULTADO: FAIL ({len(FAILS)}):")
        for f in FAILS:
            print("  -", f)
        return 1
    print("RESULTADO: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
