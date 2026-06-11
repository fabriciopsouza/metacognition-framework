#!/usr/bin/env python3
"""effect_gate.py — PreToolUse hook: deny/ask-backstop por efeito (ADR-039, porta 1:1 de effect-gate.ps1).

So inspeciona Bash/PowerShell. Politica em tools/effect-rules.json (dado, nao logica).
Fail-open em erro interno (exit 0). A camada fail-closed e o managed-settings (ADR-015).
ASCII-safe: sem emoji no codigo (o .json pode ter, mas os matches sao no comando — lowercase ASCII).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def emit(decision, reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": f"effect-gate (ADR-039) [{decision}]: {reason}",
        }
    }))
    sys.exit(0)


try:
    raw = sys.stdin.read()
    if not raw:
        sys.exit(0)

    hook = json.loads(raw)
    tool = str(hook.get("tool_name") or "")
    if tool not in ("Bash", "PowerShell"):
        sys.exit(0)

    cmd = str((hook.get("tool_input") or {}).get("command") or "")
    if not cmd:
        sys.exit(0)
    c = cmd.lower()

    rules_path = os.path.join(ROOT, "tools", "effect-rules.json")
    if not os.path.isfile(rules_path):
        print("[effect-gate] effect-rules.json ausente - fail-open (allow)", file=sys.stderr)
        sys.exit(0)

    policy = json.loads(open(rules_path, encoding="utf-8").read())

    ask_reason = None
    for rule in policy.get("rules", []):
        all_pats = [p for p in (rule.get("all") or []) if p]
        none_pats = [p for p in (rule.get("none") or []) if p]

        if not all(re.search(p, c) for p in all_pats):
            continue
        if any(re.search(p, c) for p in none_pats):
            continue

        if rule.get("decision") == "deny":
            emit("deny", f"{rule.get('reason', '')}. Requer gate humano (four-eyes fora do canal).")
        elif rule.get("decision") == "ask" and ask_reason is None:
            ask_reason = str(rule.get("reason") or "")

    if ask_reason is not None:
        emit("ask", ask_reason)
    sys.exit(0)

except Exception as e:
    print(f"[effect-gate] warning (nao-bloqueante): {e}", file=sys.stderr)
    sys.exit(0)
