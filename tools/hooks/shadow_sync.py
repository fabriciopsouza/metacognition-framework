#!/usr/bin/env python3
"""shadow_sync.py — SessionStart: AUTO-sincroniza um SHADOW com origin (o "reset --hard" mecânico).

Regra do dono mecanizada (não-prosa): shadow (premium/public/web) é ESPELHO PUBLICADO — sincronizar =
CASAR origin, nunca push, nunca merge. Se o repo é `SOMBRA-EXPORT` (ADR-070) e divergiu/atrasou de
origin, este hook faz `git fetch` + `git reset --hard origin/<branch>` AUTOMATICAMENTE no boot.

SEGURO porque um SOMBRA-EXPORT só carrega commits de auto-publish (export-clean) — não há trabalho
humano a perder; o "ahead" de um shadow é sempre um export velho que o force-push superou. Estritamente
gated em `SOMBRA-EXPORT` (alta confiança, carimbo role=shadow + origin canônico): master/dev/clone/
ambíguo => NO-OP absoluto (NUNCA reset --hard onde haveria trabalho a perder). Fail-safe: erro/dúvida => no-op.

Par do `shadow_write_guard` (que NEGA push): juntos, um shadow só recebe — nunca empurra, e sempre casa origin.
Contrato SessionStart: emite hookSpecificOutput.additionalContext. Uso: python tools/hooks/shadow_sync.py
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git(*args):
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=30)
        return r.stdout.strip(), r.returncode
    except Exception:
        return "", 1


def sync(classify, git=_git):
    """Núcleo testável. classify() -> dict do repo_identity; git(*args) -> (stdout, rc).
    Retorna dict {action: noop|synced|already, ...}."""
    info = classify() or {}
    if info.get("verdict") != "SOMBRA-EXPORT":
        return {"action": "noop", "reason": f"nao e shadow (verdict={info.get('verdict')})"}
    branch = info.get("canonical_branch") or "main"
    git("fetch", "--quiet", "origin", branch)
    ref = f"origin/{branch}"
    head, _ = git("rev-parse", "HEAD")
    target, rc = git("rev-parse", ref)
    if rc != 0 or not target:
        return {"action": "noop", "reason": f"{ref} indisponivel"}
    if head == target:
        return {"action": "already", "ref": ref}
    _, rc = git("reset", "--hard", ref)
    if rc != 0:
        return {"action": "noop", "reason": "reset --hard falhou"}
    return {"action": "synced", "ref": ref, "from": head[:8], "to": target[:8]}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ctx = ""
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import repo_identity
        r = sync(repo_identity.classify)
        if r["action"] == "synced":
            ctx = (f"[shadow-sync] ESPELHO sincronizado automaticamente: reset --hard {r['ref']} "
                   f"({r['from']}->{r['to']}). Shadow so RECEBE do main; nunca push/merge aqui.")
        elif r["action"] == "already":
            ctx = f"[shadow-sync] espelho ja em sync com {r['ref']}."
    except Exception:
        ctx = ""
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": ctx}}, ensure_ascii=True))
    sys.exit(0)


if __name__ == "__main__":
    main()
