#!/usr/bin/env python3
"""shadow_write_guard.py — Hook PreToolUse(Bash): WRITE-ISOLATION dos repos (ADR-069/070).

Regra do dono (inviolável, "nem por injeção de prompt"): cada repo só escreve em SI mesmo.
READ é livre (um main PODE ler o repo do outro p/ análise); WRITE é travado. Duas negações:

  (1) SHADOW nunca empurra: se o repo é `SOMBRA-EXPORT` (espelho publicado, carimbo role=shadow),
      QUALQUER `git push` => deny. Shadow só RECEBE do main via CI; sync = `git reset --hard origin`.
  (2) MASTER só empurra pro PRÓPRIO repo: se o alvo do `git push` resolve p/ um remote != o
      `canonical_remote` do marker => deny (não escreve no repo de outra IA/setor). Isto é o gate que
      torna a LEITURA cross-repo segura: ler o repo do outro é ok porque escrever nele é impossível.

deny de hook NÃO é bypassável pelo agente/prompt. Embarca em todo repo via export-clean (tools/).
Python (escapa da regra Kaspersky AAC). Fail-OPEN em dúvida (só nega quando tem CERTEZA do alvo/identidade).
Contrato PreToolUse: lê JSON no stdin (tool_input.command, cwd). Uso: python tools/hooks/shadow_write_guard.py
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../tools


def allow():
    sys.exit(0)


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                              "permissionDecision": "deny",
                                              "permissionDecisionReason": reason}}, ensure_ascii=True))
    sys.exit(0)


def _git(cwd, *args):
    try:
        r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=15)
        return r.stdout.strip(), r.returncode
    except Exception:
        return "", 1


def _target_url(cmd, cwd):
    """Resolve a URL-alvo de um `git push`. Token explícito (URL ou nome de remote) ou, sem token, o
    remote 'origin'. Retorna None se não der p/ resolver com certeza (=> fail-open no chamador)."""
    m = re.search(r"\bgit\s+push\b(.*)$", cmd)
    if not m:
        return None
    args = [a for a in m.group(1).split() if not a.startswith("-")]
    tok = args[0] if args else "origin"
    if re.match(r"^(git@|https?://|ssh://)", tok):
        return tok
    if re.match(r"^[\w./-]+$", tok):  # nome de remote
        url, rc = _git(cwd, "remote", "get-url", tok)
        return url if rc == 0 and url else None
    return None


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        cmd = str(((payload.get("tool_input") or {}).get("command")) or "")
        cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

        if not re.search(r"\bgit\s+push\b", cmd):
            allow()

        sys.path.insert(0, ROOT)
        try:
            import repo_identity
        except Exception:
            allow()  # sem o classificador, não afirmamos nada => fail-open

        cur = os.getcwd()
        try:
            os.chdir(cwd)
            info = repo_identity.classify()
        finally:
            os.chdir(cur)

        # (1) shadow nunca empurra.
        if info.get("verdict") == "SOMBRA-EXPORT":
            deny("SHADOW-WRITE-GUARD (ADR-070): este repo e ESPELHO PUBLICADO (role=shadow). Shadows "
                 "(premium/public/web) NUNCA empurram pro proprio online — so RECEBEM do main via CI. "
                 "Sync = `git reset --hard origin/main`, nunca push. Push NEGADO (regra inviolavel).")

        # (2) master so empurra pro proprio canonical_remote.
        marker = {}
        f = os.path.join(cwd, ".repo-identity.json")
        try:
            with open(f, encoding="utf-8") as fh:
                marker = json.load(fh)
        except Exception:
            marker = {}
        canon = marker.get("canonical_remote")
        target = _target_url(cmd, cwd)
        if canon and target:
            if repo_identity._norm_remote(target) != repo_identity._norm_remote(canon):
                deny(f"WRITE-ISOLATION (ADR-069): push mira `{target}`, que NAO e o canonical_remote "
                     f"deste repo (`{canon}`). Cada repo escreve so em SI — ler o repo de outra IA/setor "
                     f"e ok, ESCREVER nele NAO. Push NEGADO (nem por injecao de prompt).")
        allow()
    except Exception:
        sys.exit(0)  # fail-open


if __name__ == "__main__":
    main()
