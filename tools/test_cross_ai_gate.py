#!/usr/bin/env python3
"""Testes do cross-ai-gate (ADR-069) — prova que o gate MORDE (rejeita loops), não só que passa.
Sem deps externas; roda: python tools/test_cross_ai_gate.py
"""
import sys
import cross_ai_gate as g


def _msg(rid, topic, rnd, claims=None, verdicts=None, status="open", **extra):
    m = {"report_id": rid, "topic_fingerprint": topic, "round": rnd,
         "from": "claude", "to": ["gemini"], "status": status,
         "claims": claims or [], "verdict_per_claim": verdicts or {}}
    m.update(extra)
    return m


def run():
    fails = []

    def check(name, manifest, expect_ok, must_contain=None):
        v = g.validate(manifest)
        ok = not v
        if ok != expect_ok:
            fails.append(f"{name}: esperava ok={expect_ok}, deu ok={ok} (violacoes={v})")
        elif must_contain and not any(must_contain in x for x in v):
            fails.append(f"{name}: esperava violacao contendo '{must_contain}', deu {v}")

    # 1) Convergência limpa: claim aberta -> resolvida -> selada. PASS.
    check("convergencia_limpa", {"messages": [
        _msg("r1", "T1", 1, claims=[{"claim_id": "c1", "evidence_sha256": "e1"}], verdicts={"c1": "OPEN"}),
        _msg("r2", "T1", 2, verdicts={"c1": "ACEITO"}, status="sealed"),
    ]}, expect_ok=True)

    # 2) LOOP / restating: round 2 repete sem progresso (mesma claim, sem resolver, sem evidencia nova). FAIL.
    check("loop_restating", {"messages": [
        _msg("r1", "T2", 1, claims=[{"claim_id": "c1", "evidence_sha256": "e1"}], verdicts={"c1": "OPEN"}),
        _msg("r2", "T2", 2, claims=[{"claim_id": "c1", "evidence_sha256": "e1"}], verdicts={"c1": "OPEN"}),
    ]}, expect_ok=False, must_contain="SEM PROGRESSO")

    # 3) Persuasão -> nova rodada COM evidência nova: progresso legítimo. PASS (não é loop).
    check("progresso_evidencia_nova", {"messages": [
        _msg("r1", "T3", 1, claims=[{"claim_id": "c1", "evidence_sha256": "e1"}], verdicts={"c1": "OPEN"}),
        _msg("r2", "T3", 2, claims=[{"claim_id": "c1", "evidence_sha256": "e2"}], verdicts={"c1": "OPEN"}),
        _msg("r3", "T3", 3, verdicts={"c1": "REJEITADO"}, status="sealed"),
    ]}, expect_ok=True)

    # 4) Convergiu mas NÃO selou: todas resolvidas, status open. FAIL.
    check("convergiu_nao_selou", {"messages": [
        _msg("r1", "T4", 1, claims=[{"claim_id": "c1", "evidence_sha256": "e1"}], verdicts={"c1": "ACEITO"}),
    ]}, expect_ok=False, must_contain="NAO esta sealed")

    # 5) Reabrir tópico SELADO sem chave humana nem evidência inédita. FAIL (finalidade).
    check("reabre_selado_sem_chave", {"messages": [
        _msg("r1", "T5", 1, claims=[{"claim_id": "c1", "evidence_sha256": "e1"}], verdicts={"c1": "ACEITO"}, status="sealed"),
        _msg("r2", "T5", 2, claims=[{"claim_id": "c1", "evidence_sha256": "e1"}], verdicts={"c1": "OPEN"}),
    ]}, expect_ok=False, must_contain="TOPICO SELADO")

    # 6) Reabrir SELADO com chave humana. PASS (e depois re-sela).
    check("reabre_com_chave_humana", {"messages": [
        _msg("r1", "T6", 1, claims=[{"claim_id": "c1", "evidence_sha256": "e1"}], verdicts={"c1": "ACEITO"}, status="sealed"),
        _msg("r2", "T6", 2, claims=[{"claim_id": "c1", "evidence_sha256": "e9"}], verdicts={"c1": "REJEITADO"},
             status="sealed", reopen_token="dono:2026-06-06"),
    ]}, expect_ok=True)

    # 7) Teto por tópico estourado sem escalada. FAIL.
    check("teto_sem_escalada", {"messages": [
        _msg("r1", "T7", 1, claims=[{"claim_id": "c1", "evidence_sha256": "e1"}], verdicts={"c1": "OPEN"}),
        _msg("r2", "T7", 2, claims=[{"claim_id": "c2", "evidence_sha256": "e2"}], verdicts={"c2": "OPEN"}),
        _msg("r3", "T7", 3, claims=[{"claim_id": "c3", "evidence_sha256": "e3"}], verdicts={"c3": "OPEN"}),
        _msg("r4", "T7", 4, claims=[{"claim_id": "c4", "evidence_sha256": "e4"}], verdicts={"c4": "OPEN"}),
    ]}, expect_ok=False, must_contain="teto")

    # 8) Teto estourado COM escalada a humano. PASS no eixo do teto (claims abertas seguem, mas escalou).
    check("teto_com_escalada", {"messages": [
        _msg("r1", "T8", 1, claims=[{"claim_id": "c1", "evidence_sha256": "e1"}], verdicts={"c1": "OPEN"}),
        _msg("r2", "T8", 2, claims=[{"claim_id": "c2", "evidence_sha256": "e2"}], verdicts={"c2": "OPEN"}),
        _msg("r3", "T8", 3, claims=[{"claim_id": "c3", "evidence_sha256": "e3"}], verdicts={"c3": "OPEN"}),
        _msg("r4", "T8", 4, claims=[{"claim_id": "c4", "evidence_sha256": "e4"}], verdicts={"c4": "OPEN"},
             escalation="pending"),
    ]}, expect_ok=True)

    # 9) GHOST CLAIM (qa-critic ALTO): veredito sobre claim nunca declarada em claims[] -> seal falso. FAIL.
    check("ghost_claim", {"messages": [
        _msg("r1", "T9", 1, claims=[], verdicts={"fantasma": "ACEITO"}, status="sealed"),
    ]}, expect_ok=False, must_contain="GHOST CLAIM")

    # 10) Claim NOVA sem evidência não conta como progresso (qa-critic MÉDIO). FAIL.
    check("claim_nova_sem_evidencia", {"messages": [
        _msg("r1", "T10", 1, claims=[{"claim_id": "c1", "evidence_sha256": "e1"}], verdicts={"c1": "OPEN"}),
        _msg("r2", "T10", 2, claims=[{"claim_id": "c2"}], verdicts={"c2": "OPEN"}),  # sem evidence_sha256
    ]}, expect_ok=False, must_contain="SEM PROGRESSO")

    if fails:
        print("FAIL:")
        for f in fails:
            print("  -", f)
        return 1
    print("OK — 10 casos (gate MORDE: loop, restating, finalidade, teto, ghost-claim, claim-sem-evidencia).")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
    sys.exit(run())
