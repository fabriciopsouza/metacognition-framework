#!/usr/bin/env python3
"""Canary do mission-gate (ADR-022): confirma os 3 modos BRIEFING/ADVANCE/STANDARD.

Alimenta o hook com cwd contendo (ou não) mission.md e confere o additionalContext injetado.
Uso: python tools/test_mission_gate.py   (exit 0 se todos corretos; 1 caso contrário)
Requer pwsh ou powershell no PATH; SKIP se ausente.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "tools", "hooks", "mission-gate.ps1")


def find_pwsh():
    for exe in ("pwsh", "powershell"):
        if shutil.which(exe):
            return exe
    return None


def run_hook(pwsh, cwd):
    payload = {"hook_event_name": "SessionStart", "cwd": cwd}
    proc = subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-File", HOOK],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    out = proc.stdout.strip()
    ctx = ""
    if out:
        try:
            ctx = json.loads(out).get("hookSpecificOutput", {}).get("additionalContext", "")
        except json.JSONDecodeError:
            ctx = out
    return ctx


def main():
    pwsh = find_pwsh()
    if not pwsh:
        print("SKIP: pwsh/powershell ausente no PATH — canary nao executado.", file=sys.stderr)
        return 0
    fails = 0
    with tempfile.TemporaryDirectory() as d:
        # BRIEFING: sem mission.md
        briefing = os.path.join(d, "briefing")
        os.makedirs(briefing)
        # ADVANCE: mission.md sem product_type válido
        advance = os.path.join(d, "advance")
        os.makedirs(advance)
        with open(os.path.join(advance, "mission.md"), "w", encoding="utf-8") as f:
            f.write("# mission\n\n## product_type\n<preencher>\n")
        # STANDARD (inline): mission.md com "product_type: valor"
        standard = os.path.join(d, "standard")
        os.makedirs(standard)
        with open(os.path.join(standard, "mission.md"), "w", encoding="utf-8") as f:
            f.write("# mission\n\nproduct_type: gui-app\n")
        # STANDARD (heading): "## product_type\n<valor>" — formato tolerado (fallback do hook)
        heading = os.path.join(d, "heading")
        os.makedirs(heading)
        with open(os.path.join(heading, "mission.md"), "w", encoding="utf-8") as f:
            f.write("# mission\n\n## product_type\ndata-notebook\n")

        cases = [
            ("sem mission.md", briefing, "BRIEFING"),
            ("mission.md sem product_type", advance, "ADVANCE"),
            ("mission.md inline product_type", standard, "STANDARD"),
            ("mission.md heading product_type (fallback)", heading, "STANDARD"),
        ]
        for desc, cwd, expect in cases:
            ctx = run_hook(pwsh, cwd)
            ok = expect in ctx
            status = "OK  " if ok else "FAIL"
            if not ok:
                fails += 1
            print(f"{status} [esperado {expect:8}] {desc}  ->  {ctx[:70]}")
    print("-" * 40)
    print(f"RESULTADO: {'PASS (BRIEFING/ADVANCE/STANDARD — 4 casos, incl. fallback heading)' if not fails else f'FAIL ({fails} caso(s))'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
