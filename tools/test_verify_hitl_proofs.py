#!/usr/bin/env python3
"""Canario verify_hitl_proofs (ADR-071 §Pendencias): dispatch correto commit/tag/pr + fail-closed
em assinatura ausente. Usa runner injetado (sem depender de chaves GPG no runner de CI).

Uso: python tools/test_verify_hitl_proofs.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import verify_hitl_proofs as vh

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    fails = []

    # classify
    if vh.classify_proof("commit:abc1234") != ("commit", "abc1234"):
        fails.append("classify commit")
    if vh.classify_proof("tag:v1.2.0") != ("tag", "v1.2.0"):
        fails.append("classify tag")
    if vh.classify_proof("approved-pr:owner#5") != ("pr", "owner#5"):
        fails.append("classify approved-pr")
    if vh.classify_proof("pr:42") != ("pr", "42"):
        fails.append("classify pr")
    if vh.classify_proof("true")[0] != "invalid":
        fails.append("classify invalid (auto-declarado 'true' = teatro)")

    # runner que SIMULA assinatura valida so p/ um sha especifico
    def runner_good(args):
        # args = ['verify-commit', sha] ou ['verify-tag', t]
        ref = args[1]
        if ref == "good":
            return 0, "gpg: Good signature from dono"
        return 1, "gpg: no signature found"

    # commit assinado -> verified True
    r = vh.verify_proof("commit:good", runner_good)
    if not r["verified"]:
        fails.append("commit assinado deveria verificar")
    # commit sem assinatura -> verified False (fail-closed)
    r = vh.verify_proof("commit:bad", runner_good)
    if r["verified"]:
        fails.append("commit sem assinatura deveria FALHAR (fail-closed)")
    # pr -> verified None (declarado, fora do git)
    r = vh.verify_proof("pr:7", runner_good)
    if r["verified"] is not None:
        fails.append("pr deveria ser None (verificacao via API, nao git)")

    # manifest: 1 commit bom + 1 ruim -> ok=False, 1 failed
    man = {"capabilities": [
        {"capability_id": "a", "ai": "claude", "hitl_proof": "commit:good"},
        {"capability_id": "b", "ai": "gemini", "hitl_proof": "commit:bad"},
        {"capability_id": "c", "ai": "claude", "hitl_proof": "pr:9"},
        {"capability_id": "d", "ai": "claude"},  # sem proof -> ignorado
    ]}
    ok, results, failed, pr_proofs = vh.verify_manifest(man, runner_good)
    if ok:
        fails.append("manifest com commit:bad deveria reprovar")
    if len(failed) != 1:
        fails.append(f"esperado 1 failed, veio {len(failed)}")
    if len(pr_proofs) != 1:
        fails.append(f"esperado 1 pr, veio {len(pr_proofs)}")

    # manifest so com commit bom -> ok=True
    man2 = {"capabilities": [{"capability_id": "a", "ai": "claude", "hitl_proof": "commit:good"}]}
    ok2, *_ = vh.verify_manifest(man2, runner_good)
    if not ok2:
        fails.append("manifest so com commit assinado deveria PASS")

    # require-all com pr -> falha (pr nao verificavel no git)
    ok3, *_ = vh.verify_manifest(man2 if False else {"capabilities": [
        {"capability_id": "c", "hitl_proof": "pr:9"}]}, runner_good, require_all=True)
    if ok3:
        fails.append("require-all com pr-based deveria FALHAR")

    print("verify_hitl_proofs:", "OK" if not fails else f"FAIL ({len(fails)})")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (dispatch + fail-closed de assinatura)" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
