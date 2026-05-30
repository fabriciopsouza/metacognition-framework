#!/usr/bin/env python3
"""Canary do effect-gate (ADR-015): tenta furar a política e confirma que falha em furar.

Critério de aceite P1: existe teste que TENTA furar o gate e NÃO consegue.
Alimenta o hook (PowerShell) com payloads T3 via stdin e confirma permissionDecision=deny;
alimenta payloads benignos e confirma que NÃO bloqueia (anti-falso-positivo / anti-fail-open).

Uso: python tools/test_effect_gate.py    (exit 0 se todos os casos corretos; 1 caso contrário)
Requer pwsh ou powershell no PATH. Se ausente, marca SKIP (não falha o CI silenciosamente).
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "tools", "hooks", "effect-gate.ps1")

# (descrição, tool, command, espera_deny)
CASES = [
    # --- DEVE bloquear (T3 inequívoco) ---
    ("rm -rf / ", "Bash", "rm -rf /", True),
    ("rm -rf ~/", "Bash", "rm -rf ~/", True),
    ("rm -rf ~ (home)", "Bash", "sudo rm -rf ~", True),
    ("rm -fr /*", "Bash", "rm -fr /*", True),
    ("mkfs.ext4", "Bash", "mkfs.ext4 /dev/sda1", True),
    ("Format-Volume", "PowerShell", "Format-Volume -DriveLetter D", True),
    ("dd of=/dev/sda", "Bash", "dd if=/dev/zero of=/dev/sda bs=1M", True),
    ("push --force main", "Bash", "git push --force origin main", True),
    ("push -f", "Bash", "git push -f origin master", True),
    ("fork bomb", "Bash", ":(){ :|:& };:", True),
    ("firewall off", "PowerShell", "netsh advfirewall set allprofiles state off", True),
    # --- NÃO deve bloquear (benigno / reversível) ---
    ("ls", "Bash", "ls -la", False),
    ("git status", "Bash", "git status", False),
    ("git push normal", "Bash", "git push origin feat/x", False),
    ("push --force-with-lease", "Bash", "git push --force-with-lease origin feat/x", False),
    ("rm arquivo local", "Bash", "rm build/tmp.txt", False),
    ("rm -rf node_modules", "Bash", "rm -rf node_modules", False),
    ("mkdir", "Bash", "mkdir -p docs/new", False),
    ("read tool nao-shell", "Read", "", False),
]


def find_pwsh():
    for exe in ("pwsh", "powershell"):
        if shutil.which(exe):
            return exe
    return None


def run_hook(pwsh, tool, command):
    payload = {"tool_name": tool, "tool_input": {"command": command} if command else {}}
    proc = subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-File", HOOK],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    out = proc.stdout.strip()
    is_deny = False
    if out:
        try:
            data = json.loads(out)
            is_deny = data.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
        except json.JSONDecodeError:
            is_deny = '"deny"' in out
    return is_deny


def main():
    pwsh = find_pwsh()
    if not pwsh:
        print("SKIP: pwsh/powershell ausente no PATH — canary nao executado.", file=sys.stderr)
        return 0  # não falha o build por ambiente sem PowerShell; documentado no ADR-015
    fails = 0
    for desc, tool, cmd, expect_deny in CASES:
        got = run_hook(pwsh, tool, cmd)
        ok = got == expect_deny
        verb = "deny" if got else "allow"
        exp = "deny" if expect_deny else "allow"
        status = "OK  " if ok else "FAIL"
        if not ok:
            fails += 1
        print(f"{status} [{exp:5}->{verb:5}] {desc}")
    print("-" * 40)
    print(f"RESULTADO: {'PASS (gate fura nada do que devia bloquear; nao trava benigno)' if not fails else f'FAIL ({fails} caso(s))'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
