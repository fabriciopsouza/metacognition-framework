#!/usr/bin/env python3
"""compaction_gate.py — PreCompact hook: backstop de digest (ADR-021, porta 1:1 de compaction-gate.ps1).

Bloqueia SÓ o caso catastrófico: history.md ausente OU sem checkpoint (## YYYY-MM-DD).
Fail-open em erro interno (exit 0). Contrato PreCompact: {"decision":"block",...} em stdout.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def allow():
    sys.exit(0)


try:
    raw = sys.stdin.read()
    cwd = ROOT
    if raw:
        try:
            h = json.loads(raw)
            if h.get("cwd"):
                cwd = str(h["cwd"])
        except Exception:
            pass

    candidates = [
        os.path.join(cwd, "history.md"),
        os.path.join(cwd, "HISTORY.md"),
        os.path.join(cwd, ".claude", "memory", "HISTORY.md"),
    ]
    hist = next((c for c in candidates if os.path.isfile(c)), None)

    if not hist:
        block(
            f'history.md nao encontrado em "{cwd}": nada foi persistido nesta sessao. '
            "Rode /checkpoint (grava history.md / digest) ANTES de compactar — ADR-016/021. "
            "Compactar agora perderia o WIP nao salvo."
        )

    with open(hist, encoding="utf-8-sig", errors="replace") as f:
        content = f.read()

    if not re.search(r"(?m)^##\s+\d{4}-\d{2}-\d{2}", content):
        block(
            "history.md existe mas nao tem nenhum checkpoint (## YYYY-MM-DD): "
            "rode /checkpoint antes de compactar (ADR-016/021)."
        )

    print(
        "[compaction-gate] compaction prestes a ocorrer — confirme que o "
        "digest/checkpoint reflete o WIP atual (ADR-016). Nao-bloqueante.",
        file=sys.stderr,
    )
    allow()

except Exception as e:
    print(f"[compaction-gate] warning (nao-bloqueante): {e}", file=sys.stderr)
    sys.exit(0)
