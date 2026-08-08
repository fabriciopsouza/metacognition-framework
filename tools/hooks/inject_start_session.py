#!/usr/bin/env python3
"""inject_start_session.py — SessionStart GLOBAL: auto-boot do squad (ADR-006). Port Python
do inject-start-session-global.ps1 (ADR-101); a versao PS fica como fallback.

POR QUE O PORT: este e o hook que faz o framework ACORDAR em projetos que nao o repo-mae —
e era .ps1, portanto refem de EDR/GPO (ADR-060) e inexistente fora do Windows. Junto com o
route-gate, era um dos dois unicos sobreviventes do wiring global; porta-lo fecha o ultimo
ponto em que o auto-boot dependia de PowerShell.

ALGORITMO (identico ao PS, ADR-006):
  1. cwd = payload.cwd / $CLAUDE_PROJECT_DIR / getcwd
  2. ~/.claude/session.lock          -> SKIP silencioso (opt-out amplo)
  3. <cwd>/.claude/session.lock      -> SKIP com MEMORIA (diz desde quando/por que + como religar)
  4. owner do remote origin (HTTPS + SSH) x ~/.claude/squad-owners.txt (substring, case-insens.)
  5. sem match -> marker AGENTS.md ou .agent/ no projeto
  6. sem match nem marker            -> SKIP declarado
  7. injeta ~/.claude/workflows/start-session.md (+ session-insights.md se houver, ADR-068)
Falha soft: warning no stderr + exit 0. Nunca bloqueia a sessao.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_root, read_payload  # noqa: E402

HOME = os.path.expanduser("~")
OWNER_RX = re.compile(r"[:/]([^:/\s]+)/[^/\s]+?(?:\.git)?\s*$")


def emit(ctx="", status=""):
    out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}}
    if status:
        out["systemMessage"] = f"auto-boot: {status}"
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)


def _read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def owner_of(cwd):
    try:
        r = subprocess.run(["git", "-C", cwd, "remote", "get-url", "origin"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=15)
        url = r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return None
    if not url:
        return None
    m = OWNER_RX.search(url)
    return m.group(1) if m else None


def owner_match(owner):
    if not owner:
        return None
    raw = _read(os.path.join(HOME, ".claude", "squad-owners.txt"))
    low = owner.lower()
    for line in raw.splitlines():
        tk = line.strip().lower()
        if tk and not tk.startswith("#") and tk in low:
            return tk
    return None


def project_lock_offer(lock):
    since = "data desconhecida"
    try:
        since = datetime.fromtimestamp(os.path.getctime(lock)).strftime("%Y-%m-%d %H:%M")
    except OSError:
        pass
    reason = ""
    for line in _read(lock).splitlines():
        if re.match(r"^\s*reason\s*:", line):
            reason = re.sub(r"^\s*reason\s*:\s*", "", line).strip()
            break
    motivo = f" (motivo: {reason})" if reason else ""
    return (f"# Squad desativado NESTE projeto (session.lock) — ADR-027\n\n"
            f"O auto-boot do squad esta silenciado aqui desde {since}{motivo}.\n"
            f"Para REATIVAR em sessoes futuras: delete `.claude/session.lock`.\n"
            f"Esta sessao segue sem boot automatico (voce assume o controle).\n"), since


def main():
    try:
        cwd = project_root(read_payload())

        if os.path.isfile(os.path.join(HOME, ".claude", "session.lock")):
            emit("", "skipped (global-lock)")
        plock = os.path.join(cwd, ".claude", "session.lock")
        if os.path.isfile(plock):
            offer, since = project_lock_offer(plock)
            emit(offer, f"skipped (project-lock; desde {since}) — reativacao oferecida")

        owner = owner_of(cwd)
        token = owner_match(owner)
        marker = None
        if not token:
            if os.path.isfile(os.path.join(cwd, "AGENTS.md")):
                marker = "AGENTS.md"
            elif os.path.isdir(os.path.join(cwd, ".agent")):
                marker = ".agent"
        if not token and not marker:
            emit("", f"skipped (owner={owner}, sem match)" if owner
                 else "skipped (no-match-no-marker)")

        start_doc = os.path.join(HOME, ".claude", "workflows", "start-session.md")
        if not os.path.isfile(start_doc):
            emit("", "skipped (start-session.md ausente; abra o repo-framework 1x p/ espelhar)")
        content = _read(start_doc)

        insights = _read(os.path.join(cwd, "docs", "_private", "_catalog",
                                      "session-insights.md")).strip()
        block = f"\n\n---\n\n{insights}" if insights else ""
        status = f"owner={owner} match={token}" if token else f"marker={marker}"

        emit(f"# Boot automatico do squad — global (ADR-006)\n\n{content}{block}", status)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 — nunca bloqueia sessao
        sys.stderr.write(f"[inject-start-session] warning (nao-bloqueante): {e}\n")
        emit("", "skipped (erro nao-bloqueante)")


if __name__ == "__main__":
    main()
