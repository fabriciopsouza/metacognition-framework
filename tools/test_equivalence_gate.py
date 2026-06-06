#!/usr/bin/env python3
"""Testes do equivalence-gate (ADR-071) — prova que MORDE divergência não-justificada.
Roda: python tools/test_equivalence_gate.py
"""
import sys
import equivalence_gate as g

AIS = ["claude", "gemini"]


def run():
    fails = []

    def check(name, manifest, expect_ok, must_contain=None):
        flags = g.validate(manifest, AIS)
        ok = not flags
        if ok != expect_ok:
            fails.append(f"{name}: esperava ok={expect_ok}, deu ok={ok} (flags={flags})")
        elif must_contain and not any(must_contain in x for x in flags):
            fails.append(f"{name}: esperava flag contendo '{must_contain}', deu {flags}")

    # 1) Ambas adotaram -> equivalentes. PASS.
    check("ambas_adotam", {"adoptions": [
        {"improvement_id": "adr069", "ai": "claude", "verdict": "ADOTADO"},
        {"improvement_id": "adr069", "ai": "gemini", "verdict": "ADOTADO"},
    ]}, expect_ok=True)

    # 2) Claude adotou, Gemini SEM decisão -> divergência implícita. FLAG.
    check("gemini_sem_decisao", {"adoptions": [
        {"improvement_id": "adr070", "ai": "claude", "verdict": "ADOTADO"},
    ]}, expect_ok=False, must_contain="SEM decisao")

    # 3) Gemini não-adota COM justificativa completa (categoria+ADR+HITL+motivação). PASS.
    check("nao_adota_justificado", {"adoptions": [
        {"improvement_id": "adr070", "ai": "claude", "verdict": "ADOTADO"},
        {"improvement_id": "adr070", "ai": "gemini", "verdict": "JA_COBERTO",
         "adr_ref": "gemini-adr-012", "hitl": True,
         "motivation": "arquitetura Gemini ja tem enforcement nativo equivalente"},
    ]}, expect_ok=True)

    # 4) Não-adota mas SEM HITL -> divergência não-ratificada. FLAG.
    check("nao_adota_sem_hitl", {"adoptions": [
        {"improvement_id": "adr070", "ai": "claude", "verdict": "ADOTADO"},
        {"improvement_id": "adr070", "ai": "gemini", "verdict": "NAO_APLICAVEL",
         "adr_ref": "gemini-adr-012", "hitl": False, "motivation": "nao se aplica"},
    ]}, expect_ok=False, must_contain="sem HITL")

    # 5) Não-adota mas SEM motivation (só §0 não basta). FLAG.
    check("nao_adota_sem_motivacao", {"adoptions": [
        {"improvement_id": "adr070", "ai": "claude", "verdict": "ADOTADO"},
        {"improvement_id": "adr070", "ai": "gemini", "verdict": "REJEITADO",
         "adr_ref": "gemini-adr-013", "hitl": True},
    ]}, expect_ok=False, must_contain="motivation")

    # 6) Ninguém adotou ainda -> sem paridade a forçar. PASS (não flaga).
    check("ninguem_adotou", {"adoptions": [
        {"improvement_id": "adrX", "ai": "claude", "verdict": "REJEITADO",
         "adr_ref": "c-adr-1", "hitl": True, "motivation": "m"},
    ]}, expect_ok=True)

    if fails:
        print("FAIL:")
        for f in fails:
            print("  -", f)
        return 1
    print("OK — 6 casos (gate MORDE: divergencia implicita, sem-HITL, sem-motivacao barrados).")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
    sys.exit(run())
