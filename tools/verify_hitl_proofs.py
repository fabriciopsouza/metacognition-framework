#!/usr/bin/env python3
"""verify_hitl_proofs.py — passo de CI que VERIFICA A AUTENTICIDADE dos `hitl_proof` do manifest do
hub via `git verify-commit` / `git verify-tag` (ADR-071 §Pendencias: "passo de CI que rode
git verify-commit sobre os hitl_proof"). Fecha o limite honesto do `equivalence_gate.py` (que so
valida FORMA do proof; a criptografia/assinatura humana e verificada AQUI).

hitl_proof (formato do equivalence_gate): commit:<sha> | tag:<t> | pr:<n> | approved-pr:<ref>
  - commit:<sha>  -> `git verify-commit <sha>`  (assinatura GPG/SSH do dono)  [VERIFICAVEL no git]
  - tag:<t>       -> `git verify-tag <t>`                                       [VERIFICAVEL no git]
  - pr:/approved-pr -> autenticidade via API do forge, NAO via git            [DECLARADO: fora do git]

LIMITE HONESTO: `git verify-commit` so prova a assinatura se a chave do dono estiver no keyring do
runner (trusted keys). Sem a chave, o git reporta "no signature"/"can't check" -> tratamos como
FALHA de verificacao (fail-closed): proof nao-verificavel != proof valido. pr-based proofs sao
reportados como NAO-VERIFICADOS-NO-GIT (a CI do forge cobre, declarado — nao mascarado).

CLI:
  python tools/verify_hitl_proofs.py <manifest.json> [--repo <dir>] [--require-all]
    exit 0 = todos os proofs git-verificaveis passaram (ou nao ha proofs git);
    exit 2 = ao menos um proof commit/tag FALHOU verificacao;
    exit 1 = erro de uso/manifest.
"""
import argparse
import json
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def classify_proof(s):
    """-> ('commit'|'tag'|'pr'|'invalid', ref)."""
    s = (s or "").strip()
    for pref, kind in (("commit:", "commit"), ("tag:", "tag"),
                       ("approved-pr:", "pr"), ("pr:", "pr")):
        if s.startswith(pref):
            return kind, s[len(pref):]
    return "invalid", s


def _git_runner(repo):
    def run(args):
        try:
            p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
            return p.returncode, (p.stdout or "") + (p.stderr or "")
        except Exception as e:
            return 127, str(e)
    return run


def verify_proof(proof, runner):
    """runner(args)->(rc, out). Retorna dict {proof, kind, verified(bool|None), detail}."""
    kind, ref = classify_proof(proof)
    if kind == "invalid":
        return {"proof": proof, "kind": kind, "verified": False, "detail": "formato invalido"}
    if kind == "pr":
        return {"proof": proof, "kind": kind, "verified": None,
                "detail": "pr-based: autenticidade via API do forge, NAO via git verify-commit (declarado)"}
    cmd = ["verify-commit", ref] if kind == "commit" else ["verify-tag", ref]
    rc, out = runner(cmd)
    return {"proof": proof, "kind": kind, "verified": rc == 0,
            "detail": (out.strip().splitlines() or [""])[-1][:160]}


def verify_manifest(manifest, runner, require_all=False):
    caps = manifest.get("capabilities", []) if isinstance(manifest, dict) else []
    results = []
    for c in caps:
        proof = c.get("hitl_proof")
        if not proof:
            continue
        r = verify_proof(proof, runner)
        r["capability_id"] = c.get("capability_id")
        r["ai"] = c.get("ai")
        results.append(r)
    git_proofs = [r for r in results if r["kind"] in ("commit", "tag")]
    failed = [r for r in git_proofs if not r["verified"]]
    pr_proofs = [r for r in results if r["kind"] == "pr"]
    unverifiable_pr_fail = require_all and pr_proofs
    ok = not failed and not unverifiable_pr_fail
    return ok, results, failed, pr_proofs


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verifica hitl_proof via git verify-commit/tag (ADR-071).")
    ap.add_argument("manifest")
    ap.add_argument("--repo", default=".", help="repo git onde vivem os commits/tags assinados (hub)")
    ap.add_argument("--require-all", action="store_true",
                    help="exige verificacao git de TODOS (pr-based, nao-git-verificavel, vira falha)")
    args = ap.parse_args(argv)
    try:
        manifest = json.load(open(args.manifest, encoding="utf-8"))
    except Exception as e:
        print(f"RESULTADO: FAIL (manifest ilegivel: {e})")
        return 1
    ok, results, failed, pr_proofs = verify_manifest(manifest, _git_runner(args.repo), args.require_all)
    for r in results:
        mark = {True: "OK", False: "FALHOU", None: "PR/declarado"}[r["verified"]]
        print(f"  [{mark}] {r.get('capability_id')} ({r.get('ai')}): {r['proof']} — {r['detail']}")
    print("-" * 50)
    if not results:
        print("RESULTADO: PASS (nenhum hitl_proof no manifest — nada a verificar)")
        return 0
    print("RESULTADO:", "PASS (proofs git verificados)" if ok
          else f"FAIL ({len(failed)} proof(s) git nao-verificados"
               + (f" + {len(pr_proofs)} pr-based exigidos" if args.require_all and pr_proofs else "") + ")")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
