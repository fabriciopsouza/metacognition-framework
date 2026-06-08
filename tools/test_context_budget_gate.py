#!/usr/bin/env python3
"""Canario do hook PreToolUse(Read) context_budget_gate (ADR-029 doc-intake): anuncia (nao bloqueia)
quando a leitura excede o orcamento; silencioso abaixo; fail-open em input invalido.

Uso: python tools/test_context_budget_gate.py
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "tools", "hooks", "context_budget_gate.py")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _run(payload):
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                       capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def main():
    fails = []
    d = tempfile.mkdtemp()

    big = os.path.join(d, "big.md")
    open(big, "w", encoding="utf-8").write("x" * 40000)  # ~10k tokens > 6000
    rc, out = _run({"tool_input": {"file_path": big}})
    if rc != 0:
        fails.append(f"exit != 0 em arquivo grande ({rc}) — hook deve ser fail-open")
    if "context-budget" not in out or "additionalContext" not in out:
        fails.append("arquivo grande deveria ANUNCIAR (additionalContext context-budget)")
    else:
        try:
            j = json.loads(out)
            if "doc_intake" not in j["hookSpecificOutput"]["additionalContext"]:
                fails.append("anuncio nao recomenda doc_intake")
        except Exception as e:
            fails.append(f"saida nao e JSON valido: {e}")

    small = os.path.join(d, "small.md")
    open(small, "w", encoding="utf-8").write("x" * 100)
    rc, out = _run({"tool_input": {"file_path": small}})
    if rc != 0 or out:
        fails.append(f"arquivo pequeno deveria ser SILENCIOSO (rc={rc}, out={out[:60]!r})")

    # input invalido -> fail-open exit 0, sem saida
    p = subprocess.run([sys.executable, HOOK], input="nao-json", capture_output=True, text=True)
    if p.returncode != 0:
        fails.append("input invalido deveria fail-open (exit 0)")

    # path inexistente -> silencioso, exit 0
    rc, out = _run({"tool_input": {"file_path": os.path.join(d, "nope.md")}})
    if rc != 0 or out:
        fails.append("path inexistente deveria ser silencioso fail-open")

    print("context_budget_gate:", "OK" if not fails else f"FAIL ({len(fails)})")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (hook anuncia grande / silencia pequeno / fail-open)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
