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
import shlex
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


SEPARADORES = {";", "&&", "||", "|", "&"}


def comandos(cmd):
    """Lista de (comando em tokens, profundidade de subshell) pelo shlex da biblioteca padrão (aspas simples, duplas e
    escapes como no Bash; r4 do PR #228). Levanta ValueError em aspas desbalanceadas."""
    # quebra de linha separa comandos como ";" (dentro de aspas so afeta a tokenizacao, nao o que se mede)
    lex = shlex.shlex(cmd.replace(chr(13) + chr(10), chr(10)).replace(chr(10), " ; "), posix=True, punctuation_chars=";&|()<>")
    lex.whitespace_split = True
    saida, atual, prof = [], [], 0
    for tok in lex:
        if tok in SEPARADORES or tok in ("(", ")"):
            if atual:
                saida.append((atual, prof))
                atual = []
            if tok == "(":
                prof += 1
                saida.append((["("], prof))
            elif tok == ")":
                saida.append(([")"], prof))
                prof -= 1
            continue
        atual.append(tok)
    if atual:
        saida.append((atual, prof))
    return saida


def alvo_do_push(tokens):
    """Se o comando é `git [-C pasta] [-c k=v ...] push ...`, devolve (True, pasta ou None); senão (False, None)."""
    # o `git` pode vir depois de prefixo (`VAR=1`, `env`, `time`, `sudo`, `command`, `if`, caminho completo, `git.exe`)
    ig = next((i for i, t in enumerate(tokens) if os.path.basename(t) in ("git", "git.exe")), None)
    if ig is None:
        return False, None
    pasta, k = None, ig + 1
    while k < len(tokens) and tokens[k].startswith("-"):
        if tokens[k] in ("-C", "-c") and k + 1 < len(tokens):
            if tokens[k] == "-C":
                pasta = tokens[k + 1]
            k += 2
        else:
            k += 1
    return (k < len(tokens) and tokens[k] == "push"), pasta


def resolver(base, alvo):
    """Pasta de um `cd`/`git -C` relativa à pasta corrente; aceita ~ e /c/ do Git Bash. Inexistente -> None."""
    pasta = os.path.expanduser(alvo.strip().strip('"'))
    m_drive = re.match(r"^/([a-zA-Z])/(.*)$", pasta)
    if m_drive:
        pasta = f"{m_drive.group(1).upper()}:/{m_drive.group(2)}"
    if not os.path.isabs(pasta):
        pasta = os.path.join(base, pasta)
    return pasta if os.path.isdir(pasta) else None


def checar_push(pasta):
    """Avisa ou pergunta (ask) se o repositório da pasta está atrás da própria upstream; senão volta sem efeito."""
    inside, _ = git(pasta, "rev-parse", "--is-inside-work-tree")
    if inside != "true":
        return
    upstream, rc = git(pasta, "rev-parse", "--abbrev-ref", "@{upstream}")
    if rc != 0 or not upstream:
        return  # branch nova / sem tracking -> nada a estar atras
    git(pasta, "fetch", "--quiet")  # checagem honesta do estado remoto antes de empurrar
    behind, rc = git(pasta, "rev-list", "--count", f"HEAD..{upstream}")
    if rc == 0 and behind not in ("", "0") and int(behind) > 0:
        ask(f"PRE-PUSH (ADR-060): local esta {behind} commit(s) ATRAS de `{upstream}` em {pasta}. "
            f"Empurrar agora arrisca push sobre base velha / divergencia. "
            f"Recomendado: `git pull --ff-only` (ou rebase) ANTES."
            + ("" if MODO["permissao"] == "bypassPermissions" else " Confirmar o push mesmo assim?"))


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        MODO["permissao"] = str(payload.get("permission_mode") or "")
        cmd = str(((payload.get("tool_input") or {}).get("command")) or "")
        cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

        # So age em `git push`. Regex evita casar "git pushd" ou substrings em comentário trivial.
        if "git" not in cmd or "push" not in cmd:  # filtro barato; o shlex abaixo decide se ha push de fato
            allow()

        # O comando pode trocar de pasta antes do push (`cd A && cd B && git push`, `git -C <pasta> push`, `(cd x && git
        # push)`): tokeniza com shlex, acumula os `cd` (relativos à pasta corrente; subshell restaura ao fechar) e avalia
        # CADA push na pasta em que ele roda (falso alarme medido em 27/11/2026 com worktrees; r1 a r4 do PR #228).
        # Atalho declarado: heredoc (`<<`), `Set-Location`/PowerShell e aspas desbalanceadas caem no modo conservador:
        # se houver `git push` no texto, checa a pasta da sessão. Em bypass o aviso é um só (o primeiro push atrasado
        # encerra a checagem); fora do bypass, uma pergunta cobre o comando inteiro.
        # Piso (r5 do PR #228): nunca menos que o guard antigo. Se o texto tem `git ... push` e o tokenizador não mediu
        # nenhum push (heredoc, `bash -c '...'`, `eval`, aspas desbalanceadas, caminho Windows com barra invertida), checa a
        # pasta da sessão, como o guard antigo fazia sempre.
        texto_tem_push = re.search(r"\bgit(?:\.exe)?\b[^;&|\n]*?\bpush\b", cmd) is not None
        cmd_unido = re.sub(r"\\\r?\n", " ", cmd)  # continuação de linha não separa comandos
        try:
            lista = None if "<<" in cmd else comandos(cmd_unido)
        except ValueError:
            lista = None
        if lista is None:
            checar_push(cwd)
            allow()
        atual, pilha, medidos = cwd, [], 0
        for tokens, _prof in lista:
            if tokens == ["("]:
                pilha.append(atual)
                continue
            if tokens == [")"]:
                atual = pilha.pop() if pilha else atual
                continue
            if tokens[0] == "cd" and len(tokens) >= 2:
                atual = resolver(atual, tokens[1]) or atual
                continue
            e_push, pasta_c = alvo_do_push(tokens)
            if e_push:
                medidos += 1
                pasta = resolver(atual, pasta_c) if pasta_c else atual
                checar_push(pasta or atual)
        if medidos == 0 and texto_tem_push:
            checar_push(cwd)
        allow()
    except Exception:
        # Fail-open: guard nunca trava o usuario pelo proprio defeito.
        sys.exit(0)


if __name__ == "__main__":
    main()
