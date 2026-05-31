#!/usr/bin/env python3
"""Canário de PARIDADE cross-platform .ps1 ↔ .sh (ADR-040, item 8 do plano de remediação v2).

GAP que fecha: toda a cadeia de hooks nasceu PowerShell-first; os `.sh` eram paridade
*declarada* não-validada (headers `[DESCONHECIDO]`). Sem prova de veredito idêntico, o teto
regulado é limitado (validação em Linux herda gate não-testado).

ESTE canário exige **veredito idêntico** entre o hook `.ps1` e o `.sh` para CADA payload de
decisão binária. Hoje cobre o `effect-gate` (deny/allow), o único hook cuja saída é um
veredito binário comparável célula-a-célula. Hooks que só injetam `additionalContext`
(mission/route/compaction) não têm veredito deny/allow — sua paridade é estrutural, coberta
pelos próprios canários, não aqui.

Requer, no MESMO host: (pwsh|powershell) E (bash + jq). Falta de qualquer um → SKIP (exit 0):
o ambiente local Windows tipicamente não tem jq; a prova real roda na matriz CI (ubuntu+macos+
windows com pwsh+jq pré-instalados). SKIP NUNCA falha o build — só divergência real falha.

Uso: python tools/test_parity.py     (exit 0 PASS/SKIP; 1 se .sh e .ps1 divergem)
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "tools", "hooks")

# Importa os casos do canário do effect-gate (fonte única — régua §0, não duplicar a matriz).
sys.path.insert(0, os.path.join(ROOT, "tools"))
from test_effect_gate import CASES  # noqa: E402  (descrição, tool, command, espera_deny)


def find_pwsh():
    for exe in ("pwsh", "powershell"):
        if shutil.which(exe):
            return exe
    return None


def deny_from_output(out):
    out = (out or "").strip()
    if not out:
        return False
    try:
        data = json.loads(out)
        return data.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
    except json.JSONDecodeError:
        return '"deny"' in out


def run_ps1(pwsh, payload):
    proc = subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-File", os.path.join(HOOKS, "effect-gate.ps1")],
        input=json.dumps(payload), capture_output=True, text=True,
    )
    return deny_from_output(proc.stdout)


def run_sh(bash, payload):
    proc = subprocess.run(
        [bash, os.path.join(HOOKS, "effect-gate.sh")],
        input=json.dumps(payload), capture_output=True, text=True,
    )
    return deny_from_output(proc.stdout)


def main():
    pwsh = find_pwsh()
    bash = shutil.which("bash")
    jq = shutil.which("jq")
    missing = [n for n, v in (("pwsh/powershell", pwsh), ("bash", bash), ("jq", jq)) if not v]
    if missing:
        print(f"SKIP: paridade não avaliada — ausente no host: {', '.join(missing)}. "
              f"A prova roda na matriz CI (ADR-040).", file=sys.stderr)
        return 0

    fails = 0
    for desc, tool, cmd, expect_deny in CASES:
        payload = {"tool_name": tool, "tool_input": {"command": cmd} if cmd else {}}
        ps = run_ps1(pwsh, payload)
        sh = run_sh(bash, payload)
        agree = ps == sh
        correct = ps == expect_deny  # se concordam, basta um lado bater o esperado
        ok = agree and correct
        if not ok:
            fails += 1
        status = "OK  " if ok else "FAIL"
        print(f"{status} ps1={'deny' if ps else 'allow':5} sh={'deny' if sh else 'allow':5} "
              f"exp={'deny' if expect_deny else 'allow':5} | {desc}")
    print("-" * 50)
    if fails:
        print(f"RESULTADO: FAIL ({fails} divergência(s) .ps1↔.sh ou veredito errado)")
        return 1
    print(f"RESULTADO: PASS (paridade .ps1↔.sh 100% em {len(CASES)} payloads do effect-gate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
