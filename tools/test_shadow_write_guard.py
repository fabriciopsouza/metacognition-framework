#!/usr/bin/env python3
"""Canario do shadow_write_guard (ADR-070). Prova a TRAVA: shadow (SOMBRA-EXPORT) + `git push` => DENY;
master/outros => allow; comando nao-push => allow. Monkeypatch do verdito (deterministico, sem git real).

Uso: python tools/test_shadow_write_guard.py   (exit 0 PASS; 1 se falha)
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import repo_identity  # noqa: E402
import shadow_write_guard as g  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def run(cmd, verdict):
    """Roda o guard com um comando + verdito mockado; devolve (decision|None)."""
    repo_identity.classify = lambda: {"verdict": verdict}
    payload = {"tool_input": {"command": cmd}, "cwd": ROOT}
    old_in, old_out = sys.stdin, sys.stdout
    sys.stdin = io.StringIO(json.dumps(payload))
    sys.stdout = cap = io.StringIO()
    try:
        g.main()
    except SystemExit:
        pass
    finally:
        sys.stdin, sys.stdout = old_in, old_out
    out = cap.getvalue().strip()
    if not out:
        return None
    try:
        return json.loads(out)["hookSpecificOutput"]["permissionDecision"]
    except Exception:
        return "PARSE_ERROR"


def main():
    fails = []

    # 1. SHADOW + git push => DENY (a trava).
    d = run("git push origin main", "SOMBRA-EXPORT")
    if d != "deny":
        fails.append(f"shadow + push deveria ser DENY, foi {d!r}")

    # 2. SHADOW + push -f => DENY (force tambem).
    if run("git push -f origin main", "SOMBRA-EXPORT") != "deny":
        fails.append("shadow + push -f deveria ser DENY")

    # 3. MASTER + git push => allow (dev normal nao trava).
    if run("git push origin main", "MASTER-CANONICO") is not None:
        fails.append("master + push deveria ser allow (sem output)")

    # 4. AMBIGUO/CLONE + push => allow (conservador: so nega SOMBRA certa).
    if run("git push", "AMBIGUO") is not None:
        fails.append("ambiguo + push deveria ser allow")

    # 5. comando nao-push em shadow => allow (so age em push).
    if run("git status", "SOMBRA-EXPORT") is not None:
        fails.append("nao-push deveria ser allow mesmo em shadow")

    # 6. PROVA WRITE-ISOLATION (subprocess contra o repo REAL): master so empurra pro proprio
    #    canonical_remote; push p/ repo de outra IA/setor => DENY (deterministico).
    import subprocess
    def probe(cmd):
        payload = json.dumps({"tool_input": {"command": cmd}, "cwd": ROOT})
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "hooks", "shadow_write_guard.py")],
                           input=payload, capture_output=True, text=True)
        if not r.stdout.strip():
            return "allow"
        try:
            return json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"]
        except Exception:
            return "PARSE_ERROR"
    try:
        canon = json.load(open(os.path.join(ROOT, ".repo-identity.json"))).get("canonical_remote", "")
    except Exception:
        canon = ""
    if canon:
        if probe("git push git@github.com:fabriciopsouza/metacognition-gemini.git main") != "deny":
            fails.append("push p/ repo do gemini deveria ser DENY (write-isolation)")
        if probe("git push git@github.com:fabriciopsouza/metacognition-framework-premium.git main") != "deny":
            fails.append("push p/ premium online deveria ser DENY (write-isolation)")
        if probe("git push origin main") != "allow":
            fails.append("push p/ origin (proprio canonical) deveria ser allow")

    print(f"shadow+push=DENY; shadow+push-f=DENY; master=allow; ambiguo=allow; nao-push=allow; "
          f"write-isolation(gemini/premium)=DENY · proprio=allow — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (shadow nunca empurra pro online)" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
