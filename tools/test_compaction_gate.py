#!/usr/bin/env python3
"""Canary do compaction-gate (ADR-021): confirma BLOCK no caso catastrófico e ALLOW no normal.

Critério de aceite (espelha test_effect_gate): existe teste que TENTA compactar sem digest e
confirma que o gate BLOQUEIA; e confirma que NÃO bloqueia quando há checkpoint (anti-falso-positivo).

Uso: python tools/test_compaction_gate.py   (exit 0 se todos corretos; 1 caso contrário)
Requer pwsh ou powershell no PATH. Se ausente, SKIP (não falha o CI por ambiente).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "tools", "hooks", "compaction-gate.ps1")


def find_pwsh():
    for exe in ("pwsh", "powershell"):
        if shutil.which(exe):
            return exe
    return None


def run_hook(pwsh, cwd):
    payload = {"trigger": "auto", "cwd": cwd}
    proc = subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-File", HOOK],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    out = proc.stdout.strip()
    is_block = False
    if out:
        try:
            is_block = json.loads(out).get("decision") == "block"
        except json.JSONDecodeError:
            is_block = '"block"' in out
    return is_block


def main():
    pwsh = find_pwsh()
    if not pwsh:
        print("SKIP: pwsh/powershell ausente no PATH — canary nao executado.", file=sys.stderr)
        return 0
    fails = 0
    with tempfile.TemporaryDirectory() as d:
        # caso 1: history.md COM checkpoint -> ALLOW (não bloqueia)
        ok_dir = os.path.join(d, "ok")
        os.makedirs(ok_dir)
        with open(os.path.join(ok_dir, "history.md"), "w", encoding="utf-8") as f:
            f.write("# history\n\n## 2026-01-01T10:00 — Sessao: exemplo\nconteudo persistido\n")
        # caso 2: diretório SEM history.md -> BLOCK
        empty_dir = os.path.join(d, "empty")
        os.makedirs(empty_dir)
        # caso 3: history.md SEM nenhum checkpoint -> BLOCK
        nochk_dir = os.path.join(d, "nochk")
        os.makedirs(nochk_dir)
        with open(os.path.join(nochk_dir, "history.md"), "w", encoding="utf-8") as f:
            f.write("# history\n\nnotas livres sem heading de sessao\n")

        cases = [
            ("history.md com checkpoint", ok_dir, False),
            ("sem history.md (nada persistido)", empty_dir, True),
            ("history.md sem checkpoint", nochk_dir, True),
        ]
        for desc, cwd, expect_block in cases:
            got = run_hook(pwsh, cwd)
            ok = got == expect_block
            verb = "block" if got else "allow"
            exp = "block" if expect_block else "allow"
            status = "OK  " if ok else "FAIL"
            if not ok:
                fails += 1
            print(f"{status} [{exp:5}->{verb:5}] {desc}")
    print("-" * 40)
    print(f"RESULTADO: {'PASS (bloqueia o catastrofico; nao trava o normal)' if not fails else f'FAIL ({fails} caso(s))'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
