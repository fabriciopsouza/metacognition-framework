#!/usr/bin/env python3
"""Canario do shadow_sync (ADR-070). Prova: SOMBRA-EXPORT divergente => reset --hard origin/<branch>;
SOMBRA ja-em-sync => sem reset; master/dev => NO-OP absoluto (nunca reset --hard onde ha trabalho).
git mockado (deterministico, sem repo real).

Uso: python tools/test_shadow_sync.py   (exit 0 PASS; 1 se falha)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import shadow_sync as s  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def make_git(head, target, calls):
    """git mockado: registra chamadas; devolve head/target p/ rev-parse."""
    def _g(*args):
        calls.append(args)
        if args[:1] == ("rev-parse",):
            ref = args[1]
            if ref == "HEAD":
                return head, 0
            return target, 0
        return "", 0
    return _g


def main():
    fails = []

    # 1. SHADOW divergente => reset --hard emitido.
    calls = []
    r = s.sync(lambda: {"verdict": "SOMBRA-EXPORT", "canonical_branch": "main"},
               make_git("aaaaaaaa", "bbbbbbbb", calls))
    if r["action"] != "synced":
        fails.append(f"shadow divergente deveria 'synced', foi {r}")
    if ("reset", "--hard", "origin/main") not in calls:
        fails.append("shadow divergente deveria emitir reset --hard origin/main")

    # 2. SHADOW ja em sync => sem reset.
    calls2 = []
    r2 = s.sync(lambda: {"verdict": "SOMBRA-EXPORT", "canonical_branch": "main"},
                make_git("cccccccc", "cccccccc", calls2))
    if r2["action"] != "already":
        fails.append(f"shadow em-sync deveria 'already', foi {r2}")
    if any(c[:2] == ("reset", "--hard") for c in calls2):
        fails.append("shadow em-sync NAO deveria resetar")

    # 3. MASTER => NO-OP absoluto (nenhum git, nenhum reset).
    calls3 = []
    r3 = s.sync(lambda: {"verdict": "MASTER-CANONICO"}, make_git("x", "y", calls3))
    if r3["action"] != "noop":
        fails.append(f"master deveria 'noop', foi {r3}")
    if calls3:
        fails.append(f"master NAO deveria tocar git (chamou {calls3})")

    # 4. AMBIGUO => NO-OP (conservador).
    r4 = s.sync(lambda: {"verdict": "AMBIGUO"}, make_git("x", "y", []))
    if r4["action"] != "noop":
        fails.append(f"ambiguo deveria 'noop', foi {r4}")

    print(f"shadow-divergente=reset; shadow-sync=sem-reset; master=noop(sem git); ambiguo=noop — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (shadow auto-casa origin; master nunca reseta)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
