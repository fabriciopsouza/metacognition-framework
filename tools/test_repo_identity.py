#!/usr/bin/env python3
"""Canário do repo-identity-gate (ADR-070). Trava a normalização de remote SSH↔HTTPS: sem ela o
master com origin SSH caía em FOREIGN (writable_master=False) — bug que também quebrava o gate de
onboarding (popup nunca dispararia no master real). `_norm_remote` é função pura → testável sem git.

Uso: python tools/test_repo_identity.py   (exit 0 PASS; 1 se falha)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from repo_identity import _norm_remote, is_export_shadow  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main():
    fails = []
    SSH = "git@github.com:fabriciopsouza/metacognition-framework.git"
    HTTPS = "https://github.com/fabriciopsouza/metacognition-framework"

    # 1. SSH e HTTPS do MESMO repo normalizam igual (o coração do bugfix).
    if _norm_remote(SSH) != _norm_remote(HTTPS):
        fails.append(f"SSH != HTTPS após normalizar ({_norm_remote(SSH)} != {_norm_remote(HTTPS)})")

    # 2. forma canônica = host/owner/repo, minúsculo, sem .git/barra.
    if _norm_remote(SSH) != "github.com/fabriciopsouza/metacognition-framework":
        fails.append(f"forma canônica inesperada: {_norm_remote(SSH)!r}")

    # 3. ssh:// explícito também normaliza.
    if _norm_remote("ssh://git@github.com/o/r.git") != "github.com/o/r":
        fails.append("ssh:// não normalizado")

    # 4. repos DIFERENTES continuam diferentes (não colapsa tudo).
    if _norm_remote(SSH) == _norm_remote("https://github.com/outro/repo"):
        fails.append("repos distintos colidiram após normalizar (falso-positivo de master)")

    # 5. vazio é inerte (fail-safe).
    if _norm_remote("") != "" or _norm_remote(None) != "":
        fails.append("entrada vazia/None deveria virar '' (fail-safe)")

    # 6. is_export_shadow — anti-forja (b1) + robusto à ordem FOREIGN (b2) (process-critic 2026-06-08).
    #    Gates fail-closed dependem disto p/ decidir SKIP; testar os 4 vetores.
    master = {"marker_role": "master", "writable_master": True, "marker_conflict": False, "is_export_signal": False}
    if is_export_shadow(master):
        fails.append("master real nao deveria ser export-shadow (enforce)")
    forged = {"marker_role": "shadow", "writable_master": False, "marker_conflict": False, "is_export_signal": False}
    if is_export_shadow(forged):
        fails.append("b1: carimbo shadow forjado SEM commit de export deveria enforce (nao pular)")
    genuine = {"marker_role": "shadow", "writable_master": False, "marker_conflict": False, "is_export_signal": True}
    if not is_export_shadow(genuine):
        fails.append("b2: shadow genuino (carimbo + commit export) deveria pular, mesmo se verdict=FOREIGN")
    conflict = {"marker_role": "shadow", "writable_master": False, "marker_conflict": True, "is_export_signal": True}
    if is_export_shadow(conflict):
        fails.append("marker_conflict declarado deveria enforce (nao confiar no carimbo)")

    print(f"SSH==HTTPS; canônico host/owner/repo; distintos preservados; vazio inerte; "
          f"is_export_shadow anti-forja(b1)/robusto-FOREIGN(b2) — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (normalização de remote SSH↔HTTPS)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
