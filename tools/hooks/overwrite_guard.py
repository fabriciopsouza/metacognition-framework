#!/usr/bin/env python3
"""overwrite_guard.py — PreToolUse/PostToolUse hook: anti-overwrite cego (ADR-037, porta 1:1 de overwrite-guard.ps1).

PreToolUse(Write|Edit): arquivo existe + tem conteudo + NAO esta no manifesto -> exit 2 (bloqueia).
PostToolUse(Read|Write|Edit|NotebookEdit): registra path no manifesto da sessao.
Fail-open em erro (exit 0). Manifesto: .agent/brain/session-files.json (override: OVERWRITE_GUARD_MANIFEST).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    raw = sys.stdin.read()
    if not raw:
        sys.exit(0)

    hook = json.loads(raw)
    evt = str(hook.get("hook_event_name") or "")
    tool = str(hook.get("tool_name") or "")
    sid = str(hook.get("session_id") or "default")

    fp = None
    ti = hook.get("tool_input") or {}
    if ti.get("file_path"):
        fp = str(ti["file_path"])
    elif ti.get("notebook_path"):
        fp = str(ti["notebook_path"])
    if not fp:
        sys.exit(0)

    manifest = os.environ.get("OVERWRITE_GUARD_MANIFEST") or ""
    if not manifest:
        cwd = str(hook.get("cwd") or ROOT)
        manifest = os.path.join(cwd, ".agent", "brain", "session-files.json")

    data: dict = {}
    if os.path.isfile(manifest):
        try:
            data = json.loads(open(manifest, encoding="utf-8").read())
        except Exception:
            data = {}

    try:
        full = os.path.realpath(fp)
    except Exception:
        full = fp

    known = list(data.get(sid) or [])
    is_known = any(str(k).lower() == full.lower() for k in known if k)

    if evt == "PreToolUse" and tool in ("Write", "Edit"):
        if not os.path.exists(full):
            sys.exit(0)          # arquivo novo
        if os.path.getsize(full) == 0:
            sys.exit(0)          # vazio
        if is_known:
            sys.exit(0)          # lido/criado nesta sessao
        print(
            f"[overwrite-guard ADR-037] BLOQUEADO: '{fp}' existe com conteudo e NAO foi lido "
            "nem criado nesta sessao. LEIA o arquivo antes de sobrescrever (anti-overwrite cego).",
            file=sys.stderr,
        )
        sys.exit(2)

    if evt == "PostToolUse":
        if not is_known:
            known.append(full)
            data[sid] = known
            try:
                os.makedirs(os.path.dirname(manifest), exist_ok=True)
                with open(manifest, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
            except Exception:
                pass

    sys.exit(0)

except Exception as e:
    print(f"[overwrite-guard] warning (nao-bloqueante): {e}", file=sys.stderr)
    sys.exit(0)
