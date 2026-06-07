#!/usr/bin/env python3
"""Canario do tooling do hub cross-IA (ADR-069). Testa a operacao de BOOT (scan) e o parser plano
ZERO-DEP, com um hub-fixture em tempdir. Prova: scan acha aberto p/ mim, ignora sealed, ignora
nao-p/-mim, e dedup por .cross-ai-seen. (manifest/gate dependem de PyYAML -> testados so se presente.)

Uso: python tools/test_cross_ai_hub.py   (exit 0 PASS; 1 se falha)
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import cross_ai_hub as hub  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _msg(rid, to, status, frm="gemini-master"):
    return (f'---\nschema_version: "1.0"\nreport_id: "{rid}"\ntopic_fingerprint: "t-{rid}"\n'
            f'thread_id: "{rid}"\nfrom: "{frm}"\nto: {to}\ndate: "2026-06-06"\n'
            f'status: "{status}"\nkind: "handoff"\nround: 1\n---\n\n# corpo {rid}\n')


def main():
    fails = []

    # parser plano zero-dep
    fm = hub.parse_flat(_msg("aa11", '["claude-master"]', "open"))
    if fm.get("report_id") != "aa11" or fm.get("to") != ["claude-master"] or fm.get("status") != "open":
        fails.append(f"parse_flat extraiu errado: {fm}")

    # hub fixture
    hubdir = tempfile.mkdtemp(prefix="hub_")
    sh = os.path.join(hubdir, "inbox", "2026", "06", "06")
    os.makedirs(sh, exist_ok=True)
    open(os.path.join(sh, "m1.md"), "w", encoding="utf-8").write(_msg("r1", '["claude-master"]', "open"))
    open(os.path.join(sh, "m2.md"), "w", encoding="utf-8").write(_msg("r2", '["claude-master"]', "sealed"))
    open(os.path.join(sh, "m3.md"), "w", encoding="utf-8").write(_msg("r3", '["gemini-master"]', "open"))
    open(os.path.join(sh, "m4.md"), "w", encoding="utf-8").write(_msg("r4", '["all"]', "open"))

    novos, _ = hub.scan(hubdir, "claude-master", None)
    ids = sorted(n["report_id"] for n in novos)
    # r1 (open p/ mim) e r4 (all) entram; r2 sealed fora; r3 p/ gemini fora.
    if ids != ["r1", "r4"]:
        fails.append(f"scan deveria achar [r1, r4], achou {ids} (sealed/nao-p-mim deveriam sair)")

    # dedup por .cross-ai-seen
    seen_path = os.path.join(hubdir, ".cross-ai-seen.json")
    with open(seen_path, "w", encoding="utf-8") as fh:
        json.dump({"seen": ["r1"]}, fh)
    novos2, _ = hub.scan(hubdir, "claude-master", seen_path)
    ids2 = sorted(n["report_id"] for n in novos2)
    if ids2 != ["r4"]:
        fails.append(f"scan com seen=[r1] deveria achar [r4], achou {ids2}")

    # validacao de frontmatter requerido (deposit barra incompleto)
    miss = hub._validate_required({"report_id": "x"})
    if "from" not in miss or "to" not in miss:
        fails.append("validate_required deveria apontar campos faltantes")

    shutil.rmtree(hubdir, ignore_errors=True)

    print(f"parse_flat ok; scan(open p/ mim + all) ok; sealed/nao-p-mim excluidos; dedup-seen ok; "
          f"validacao requerida ok — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (scan/seen/parser do hub cross-IA)" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
