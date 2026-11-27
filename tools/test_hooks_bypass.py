#!/usr/bin/env python3
"""Canário dos hooks em modo bypass (dono, 27/11/2026: "AUTORIZO A REMOCAO destas perguntas, chats ja estao em bypass permissions").

Em `permission_mode == bypassPermissions`, o "ask" do effect_gate e do prepush_sync_guard vira aviso não-bloqueante (sem
`permissionDecision`); o "deny" do effect_gate continua em qualquer modo; fora do bypass o "ask" continua.
O prepush mede o repositório do `cd`/`git -C` do comando, não a pasta da sessão.

Uso: python tools/test_hooks_bypass.py   (exit 0 se todos corretos)
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EFFECT = os.path.join(ROOT, "tools", "hooks", "effect_gate.py")
PREPUSH = os.path.join(ROOT, "tools", "hooks", "prepush_sync_guard.py")


def rodar(hook, evento):
    r = subprocess.run([sys.executable, hook], input=json.dumps(evento), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    assert r.returncode == 0, f"hook terminou com erro {r.returncode}: {r.stderr[:200]}"  # r4: erro não vale como liberação
    saida = r.stdout.strip()
    return json.loads(saida) if saida else {}


def decisao(out):
    return (out.get("hookSpecificOutput") or {}).get("permissionDecision")


def aviso(out, marca):
    """Modo aviso de fato (r2 do PR #228): sem permissionDecision E com systemMessage e additionalContext trazendo a razão."""
    hs = out.get("hookSpecificOutput") or {}
    ok = (hs.get("permissionDecision") is None and marca in str(out.get("systemMessage") or "")
          and marca in str(hs.get("additionalContext") or ""))
    return "aviso" if ok else f"sem aviso: {out}"


def git(cwd, *a):
    subprocess.run(["git", "-C", cwd, *a], capture_output=True, check=True)


def repo_atrasado(base):
    """origem com 1 commit a mais que o clone: o clone fica 1 atrás do upstream."""
    origem, clone = os.path.join(base, "origem"), os.path.join(base, "clone")
    os.makedirs(origem)
    git(origem, "init", "-q", "-b", "main")
    git(origem, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "a")
    subprocess.run(["git", "clone", "-q", origem, clone], capture_output=True, check=True)
    git(origem, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "b")
    return clone


def main():
    falhas = []
    ask_cmd = "find / -name x -delete"
    deny_cmd = "rm -rf /"
    casos = [
        ("effect ask em bypass vira aviso", aviso(rodar(EFFECT, {"tool_name": "Bash", "permission_mode": "bypassPermissions",
                                                                  "tool_input": {"command": ask_cmd}}), "effect-gate"), "aviso"),
        ("effect ask fora do bypass continua ask", decisao(rodar(EFFECT, {"tool_name": "Bash", "permission_mode": "default",
                                                                          "tool_input": {"command": ask_cmd}})), "ask"),
        ("effect deny em bypass continua deny", decisao(rodar(EFFECT, {"tool_name": "Bash", "permission_mode": "bypassPermissions",
                                                                       "tool_input": {"command": deny_cmd}})), "deny"),
    ]
    with tempfile.TemporaryDirectory() as base:
        clone = repo_atrasado(base)
        limpo = os.path.join(base, "sessao")
        os.makedirs(limpo)
        casos += [
            ("prepush atrasado fora do bypass pergunta", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": clone,
                                                                                  "tool_input": {"command": "git push"}})), "ask"),
            ("prepush atrasado em bypass vira aviso", aviso(rodar(PREPUSH, {"permission_mode": "bypassPermissions", "cwd": clone,
                                                                             "tool_input": {"command": "git push"}}), "PRE-PUSH"), "aviso"),
            ("prepush mede o repo do cd, nao a pasta da sessao", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": limpo,
                "tool_input": {"command": f'cd "{clone}" && git push'}})), "ask"),
            ("prepush mede o repo do git -C", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": limpo,
                "tool_input": {"command": f'git -C "{clone}" push'}})), "ask"),
            # r1 do PR #228: vale o ULTIMO cd antes do push
            ("prepush cd encadeado: limpo e depois atrasado", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": limpo,
                "tool_input": {"command": f'cd "{limpo}" && cd "{clone}" && git push'}})), "ask"),
            ("prepush cd encadeado: atrasado e depois limpo", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": limpo,
                "tool_input": {"command": f'cd "{clone}" && cd "{limpo}" && git push'}})), None),
            ("prepush cd relativo", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": base,
                "tool_input": {"command": "cd clone && git push"}})), "ask"),
            ("prepush ignora cd depois do push", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": limpo,
                "tool_input": {"command": f'git push; cd "{clone}" && ls'}})), None),
            # r2 do PR #228: cd relativo acumulado, -C relativo ao cd anterior, mais de um push
            ("prepush cd relativo encadeado", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": limpo,
                "tool_input": {"command": f'cd "{base}" && cd clone && git push'}})), "ask"),
            ("prepush git -C relativo ao cd anterior", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": limpo,
                "tool_input": {"command": f'cd "{base}" && git -C clone push'}})), "ask"),
            ("prepush avalia o segundo push", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": limpo,
                "tool_input": {"command": f'git -C "{limpo}" push && git -C "{clone}" push'}})), "ask"),
            # r3 do PR #228: separadores e cd dentro de aspas não contam
            ("prepush ignora cd dentro da mensagem de commit", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": clone,
                "tool_input": {"command": f'git commit -m "fix a; cd {limpo}" && git push'}})), "ask"),
            ("prepush ignora git push citado na mensagem", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": clone,
                "tool_input": {"command": 'git commit -m "docs: explica git push"'}})), None),
            # r4 do PR #228: shlex (aspas simples, escapes, subshell)
            ("prepush aspa dupla dentro de aspas simples", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": clone,
                "tool_input": {"command": "echo '\"'; git push --force"}})), "ask"),
            ("prepush aspa escapada", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": clone,
                "tool_input": {"command": 'echo "x\\""; git push --force'}})), "ask"),
            ("prepush cd dentro de aspas simples nao conta", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": clone,
                "tool_input": {"command": f"echo 'a; cd {limpo}; b'; git push --force"}})), "ask"),
            ("prepush git push em aspas simples nao conta", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": clone,
                "tool_input": {"command": "printf '%s\n' 'git push'"}})), None),
            ("prepush subshell com cd e push", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": limpo,
                "tool_input": {"command": f'(cd "{clone}" && git push)'}})), "ask"),
            ("prepush subshell restaura a pasta", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": limpo,
                "tool_input": {"command": f'(cd "{clone}") && git push'}})), None),
            ("prepush git -C com -c antes do push", decisao(rodar(PREPUSH, {"permission_mode": "default", "cwd": limpo,
                "tool_input": {"command": f'git -C "{clone}" -c a=b push'}})), "ask"),
        ]
    for nome, obtido, esperado in casos:
        ok = obtido == esperado
        print(f"{'PASS' if ok else 'FAIL'}  {nome}: obtido={obtido} esperado={esperado}")
        if not ok:
            falhas.append(nome)
    print("RESULTADO:", "PASS" if not falhas else f"FAIL {falhas}")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
