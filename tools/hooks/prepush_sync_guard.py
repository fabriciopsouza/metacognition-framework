#!/usr/bin/env python3
"""prepush_sync_guard.py - Hook PreToolUse (Bash): barra push sobre base ATRASADA (ADR-060).

Camada HARD do anti-defasagem no momento de maior dano (empurrar sobre base velha -> divergência/
clobber). Determinístico, NAO-PowerShell (python.exe -> escapa da regra Kaspersky AAC). Só age quando
o comando e `git push`; caso contrario, allow silencioso (overhead mínimo).

Decisoes adversariais:
 - Compara atraso vs `@{upstream}` (a tracking da PROPRIA branch), NAO origin/main — senao bloquearia
   feature-branch normal (que e intencionalmente atras de main). Sem upstream (branch nova) -> allow.
 - Usa permissionDecision **ask** (gate humano), NAO deny dura — rebase-force-push legítimo nao deve
   travar; o humano confirma com a informação na mão.
 - Fail-OPEN: qualquer erro -> allow (um guard nunca trava o usuário pelo seu próprio defeito).

Contrato PreToolUse: le JSON no stdin (tool_input.command, cwd). Emite hookSpecificOutput com
permissionDecision (ask|allow). Uso: python tools/hooks/prepush_sync_guard.py
"""
import json
import os
import re
import subprocess
import sys


def allow():
    sys.exit(0)  # exit 0 sem output = allow


MODO = {"permissao": ""}  # preenchido em main() com o permission_mode do evento


def ask(reason):
    # Dono, 27/11/2026: "AUTORIZO A REMOCAO destas perguntas, chats ja estao em bypass permissions". Em bypass, o ask vira
    # aviso nao-bloqueante (a sessao segue e o agente le o aviso); fora do bypass, o gate humano continua.
    if MODO["permissao"] == "bypassPermissions":
        print(json.dumps({"systemMessage": "[aviso, sem bloquear] " + reason,
                          "hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": reason}},
                         ensure_ascii=True))
        sys.exit(0)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                              "permissionDecision": "ask",
                                              "permissionDecisionReason": reason}}, ensure_ascii=True))
    sys.exit(0)


def git(cwd, *args):
    try:
        r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        return r.stdout.strip(), r.returncode
    except Exception:
        return "", 1


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        MODO["permissao"] = str(payload.get("permission_mode") or "")
        cmd = str(((payload.get("tool_input") or {}).get("command")) or "")
        cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

        # So age em `git push`. Regex evita casar "git pushd" ou substrings em comentário trivial.
        m_push = re.search(r"\bgit\s+(?:-C\s+(\"[^\"]+\"|\S+)\s+)?push\b", cmd)
        if not m_push:
            allow()

        # O comando pode trocar de pasta antes do push (`cd <worktree> && ... git push`, ou `git -C <pasta> push`): mede o
        # repositorio do push, nao a pasta da sessao (falso alarme medido em 27/11/2026 com worktrees). Vale o `git -C` do
        # proprio push ou o ULTIMO `cd` antes dele (cd encadeado; r1 do PR #228).
        # Atalho declarado: aspas simples, subshell `(cd ...)`, `||`, quebra de linha, `Set-Location` e `git -C x -c a=b push`
        # nao sao reconhecidos e caem na pasta da sessao (o comportamento anterior). Ampliar se aparecer caso real.
        anteriores = re.findall(r"(?:^|&&|;)\s*cd\s+(\"[^\"]+\"|[^&;|]+?)\s*(?:&&|;)", cmd[:m_push.start()])
        alvo_txt = m_push.group(1) or (anteriores[-1] if anteriores else None)
        if alvo_txt:
            pasta = alvo_txt.strip().strip('"')
            pasta = os.path.expanduser(pasta)
            m_drive = re.match(r"^/([a-zA-Z])/(.*)$", pasta)
            if m_drive:
                pasta = f"{m_drive.group(1).upper()}:/{m_drive.group(2)}"
            if not os.path.isabs(pasta):
                pasta = os.path.join(cwd, pasta)
            if os.path.isdir(pasta):
                cwd = pasta
        inside, _ = git(cwd, "rev-parse", "--is-inside-work-tree")
        if inside != "true":
            allow()

        upstream, rc = git(cwd, "rev-parse", "--abbrev-ref", "@{upstream}")
        if rc != 0 or not upstream:
            allow()  # branch nova / sem tracking -> nada a estar atras

        git(cwd, "fetch", "--quiet")  # checagem honesta do estado remoto antes de empurrar
        behind, rc = git(cwd, "rev-list", "--count", f"HEAD..{upstream}")
        if rc == 0 and behind not in ("", "0") and int(behind) > 0:
            ask(f"PRE-PUSH (ADR-060): local esta {behind} commit(s) ATRAS de `{upstream}`. "
                f"Empurrar agora arrisca push sobre base velha / divergencia. "
                f"Recomendado: `git pull --ff-only` (ou rebase) ANTES. Confirmar o push mesmo assim?")
        allow()
    except Exception:
        # Fail-open: guard nunca trava o usuario pelo proprio defeito.
        sys.exit(0)


if __name__ == "__main__":
    main()
