#!/usr/bin/env python3
"""Testes do equivalence-gate v2 (ADR-071) — equivalência por CAPACIDADE.
Prova que MORDE divergência não-justificada e que NÃO força import literal.
Roda: python tools/test_equivalence_gate.py
"""
import sys
import equivalence_gate as g

AIS = ["claude", "gemini"]


def _cap(cid, ai, status, **extra):
    r = {"capability_id": cid, "ai": ai, "status": status}
    r.update(extra)
    return r


def run():
    fails = []

    def check(name, manifest, known, expect_ok, must_contain=None):
        flags = g.validate(manifest, known)
        ok = not flags
        if ok != expect_ok:
            fails.append(f"{name}: esperava ok={expect_ok}, deu ok={ok} (flags={flags})")
        elif must_contain and not any(must_contain in x for x in flags):
            fails.append(f"{name}: esperava flag contendo '{must_contain}', deu {flags}")

    # 1) Ambas PROVÊEM a capacidade -> equivalentes. PASS.
    check("ambas_provem", {"capabilities": [
        _cap("anti-loop", "claude", "PROVIDES", mechanism="cross_ai_gate.py"),
        _cap("anti-loop", "gemini", "PROVIDES", mechanism="seu proprio gate"),
    ]}, AIS, expect_ok=True)

    # 2) PROVÊ por MECANISMOS DIFERENTES -> ainda equivalente (NÃO força import literal). PASS.
    #    (Ponto do qa-critic: equivalência é de capacidade, não de id/implementação.)
    check("mecanismos_diferentes", {"capabilities": [
        _cap("identidade-repo", "claude", "PROVIDES", mechanism="repo_identity.py ancestry"),
        _cap("identidade-repo", "gemini", "PROVIDES", mechanism="hook nativo de workspace"),
    ]}, AIS, expect_ok=True)

    # 3) Claude provê, Gemini OMISSA (sem registro). FLAG.
    check("gemini_omissa", {"capabilities": [
        _cap("anti-loop", "claude", "PROVIDES"),
    ]}, AIS, expect_ok=False, must_contain="OMISSA")

    # 4) Gemini ausência JUSTIFICADA completa (ADR + hitl_proof VÁLIDO + motivação). PASS.
    check("ausencia_justificada", {"capabilities": [
        _cap("anti-loop", "claude", "PROVIDES"),
        _cap("anti-loop", "gemini", "JUSTIFIED_ABSENT",
             adr_ref="gemini-adr-040", hitl_proof="commit:a1b2c3d4e5f6",
             motivation="arquitetura Gemini single-agent: loop cross-IA nao se aplica ainda"),
    ]}, AIS, expect_ok=True)

    # 5) Ausência justificada mas SEM hitl_proof. FLAG.
    check("sem_hitl_proof", {"capabilities": [
        _cap("anti-loop", "claude", "PROVIDES"),
        _cap("anti-loop", "gemini", "JUSTIFIED_ABSENT",
             adr_ref="gemini-adr-040", motivation="m"),
    ]}, AIS, expect_ok=False, must_contain="hitl_proof")

    # 5b) hitl_proof FORJADO ('fake') — string não-vazia mas formato inválido. FLAG (mata o teatro da v1).
    check("hitl_proof_forjado", {"capabilities": [
        _cap("anti-loop", "claude", "PROVIDES"),
        _cap("anti-loop", "gemini", "JUSTIFIED_ABSENT",
             adr_ref="g-adr", hitl_proof="fake", motivation="m"),
    ]}, AIS, expect_ok=False, must_contain="hitl_proof")

    # 6) Ausência justificada SEM motivation (só §0 não basta). FLAG.
    check("sem_motivation", {"capabilities": [
        _cap("anti-loop", "claude", "PROVIDES"),
        _cap("anti-loop", "gemini", "JUSTIFIED_ABSENT",
             adr_ref="gemini-adr-040", hitl_proof="pr:42"),
    ]}, AIS, expect_ok=False, must_contain="motivation")

    # 7) status ABSENT (não-justificado) enquanto a outra provê. FLAG.
    check("absent_nao_justificado", {"capabilities": [
        _cap("anti-loop", "claude", "PROVIDES"),
        _cap("anti-loop", "gemini", "ABSENT"),
    ]}, AIS, expect_ok=False, must_contain="sem justificativa")

    # 8) Ninguém provê -> todas iguais (sem capacidade) -> sem divergência. PASS.
    check("ninguem_prove", {"capabilities": [
        _cap("anti-loop", "claude", "ABSENT"),
        _cap("anti-loop", "gemini", "ABSENT"),
    ]}, AIS, expect_ok=True)

    # 9) known_ais NÃO declarado -> não dá p/ detectar omissa. FLAG.
    check("sem_known_ais", {"capabilities": [
        _cap("anti-loop", "claude", "PROVIDES"),
        _cap("anti-loop", "gemini", "PROVIDES"),
    ]}, None, expect_ok=False, must_contain="known_ais")

    # 10) DUPLICATA conflitante (qa-critic ALTO): mesmo (cap,ai) com status divergente. FLAG.
    check("duplicata_conflitante", {"capabilities": [
        _cap("anti-loop", "claude", "PROVIDES"),
        _cap("anti-loop", "gemini", "ABSENT"),
        _cap("anti-loop", "gemini", "PROVIDES"),  # 2o registro forja paridade
    ]}, AIS, expect_ok=False, must_contain="DUPLICADOS")

    # 11) Catálogo canônico (qa-critic ALTO): id fora do catálogo = vocabulário divergente. FLAG.
    check("vocabulario_divergente", {
        "capability_catalog": ["anti-loop", "identidade-repo"],
        "capabilities": [
            _cap("anti-loop", "claude", "PROVIDES"),
            _cap("loop-prevention", "gemini", "PROVIDES"),  # mesmo conceito, id divergente
        ]}, AIS, expect_ok=False, must_contain="catalogo")

    # 12) OMISSA TOTAL: IA em known_ais sem nenhum registro -> 1 flag (sem flood). FLAG.
    check("omissa_total", {"capabilities": [
        _cap("anti-loop", "claude", "PROVIDES"),
        _cap("identidade-repo", "claude", "PROVIDES"),
    ]}, ["claude", "gemini", "nova-ia"], expect_ok=False, must_contain="OMISSA total")

    if fails:
        print("FAIL:")
        for f in fails:
            print("  -", f)
        return 1
    print("OK — 12 casos (capacidade; catalogo, duplicata, hitl_proof-forjado, omissa-total barrados).")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
    sys.exit(run())
