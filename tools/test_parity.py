#!/usr/bin/env python3
"""Canário de PARIDADE cross-platform .ps1 ↔ .sh (ADR-040 + ADR-039, item 8 do plano v2).

GAP que fecha: os hooks `.sh` eram paridade DECLARADA não-validada (`[DESCONHECIDO]`). Este canário
exige **decisão idêntica** (deny/ask/allow) entre `effect-gate.ps1` e `.sh` para CADA payload da
política `effect-rules.json` (fonte única: importa `CASES` do `test_effect_gate`).

Requer no MESMO host: (pwsh|powershell) E (bash + jq). Falta de qualquer um → SKIP (exit 0): o host
Windows local tipicamente não tem jq; a prova real roda na matriz CI (ubuntu+macos+windows). SKIP
NUNCA falha o build — só divergência real falha.

Uso: python tools/test_parity.py     (exit 0 PASS/SKIP; 1 se .sh e .ps1 divergem)
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "tools", "hooks")

sys.path.insert(0, os.path.join(ROOT, "tools"))
from test_effect_gate import CASES  # noqa: E402  (descrição, tool, command, decisão_esperada)


def find_pwsh():
    for exe in ("pwsh", "powershell"):
        if shutil.which(exe):
            return exe
    return None


def decision_from_output(out):
    out = (out or "").strip()
    if not out:
        return "allow"
    try:
        data = json.loads(out)
        return data.get("hookSpecificOutput", {}).get("permissionDecision", "allow")
    except json.JSONDecodeError:
        for d in ("deny", "ask"):
            if f'"{d}"' in out:
                return d
        return "allow"


def run(cmd_list, payload):
    proc = subprocess.run(cmd_list, input=json.dumps(payload), capture_output=True, text=True)
    return decision_from_output(proc.stdout)


def main():
    # O .sh e hook POSIX. No Windows ele so existe via git-bash e recebe paths estilo Windows
    # (backslash) que quebram a resolucao de caminho — fora do contrato. A paridade .ps1<->.sh e
    # validada nos runners POSIX (ubuntu+macos), onde o .sh roda de verdade; no Windows o .ps1 e
    # testado diretamente por test_effect_gate. Logo: SKIP no Windows (nao e divergencia real).
    if os.name == "nt":
        print("SKIP: paridade .sh validada nos runners POSIX (ubuntu/macos); no Windows o hook nativo "
              "e o .ps1 (test_effect_gate).", file=sys.stderr)
        return 0
    pwsh = find_pwsh()
    bash = shutil.which("bash")
    jq = shutil.which("jq")
    missing = [n for n, v in (("pwsh/powershell", pwsh), ("bash", bash), ("jq", jq)) if not v]
    if missing:
        print(f"SKIP: paridade não avaliada — ausente no host: {', '.join(missing)}. "
              f"A prova roda na matriz CI (ADR-040).", file=sys.stderr)
        return 0

    ps1 = os.path.join(HOOKS, "effect-gate.ps1")
    sh = os.path.join(HOOKS, "effect-gate.sh")
    fails = 0
    for desc, tool, cmd, expect in CASES:
        payload = {"tool_name": tool, "tool_input": {"command": cmd} if cmd else {}}
        ps = run([pwsh, "-NoProfile", "-NonInteractive", "-File", ps1], payload)
        shd = run([bash, sh], payload)
        agree = ps == shd
        correct = ps == expect
        ok = agree and correct
        if not ok:
            fails += 1
        status = "OK  " if ok else "FAIL"
        print(f"{status} ps1={ps:5} sh={shd:5} exp={expect:5} | {desc}")
    print("-" * 50)
    if fails:
        print(f"RESULTADO: FAIL ({fails} divergência(s) .ps1↔.sh ou decisão errada)")
        return 1
    print(f"RESULTADO: PASS (paridade .ps1↔.sh 100% em {len(CASES)} payloads do effect-gate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
