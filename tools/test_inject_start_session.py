#!/usr/bin/env python3
"""Canario do auto-boot do squad em Python (ADR-006/101).

POR QUE ESTE ARQUIVO EXISTE: `inject_start_session.py` e o hook que faz o framework ACORDAR em
projetos que nao o repo-mae. O ADR-101 o portou de PowerShell para Python e nao deixou canario —
divida cobrada pelo gate `gate-precisa-de-canario` depois que o QA heterogeneo (2026-08-08)
consertou seus falsos-negativos.

O RISCO ESPECIFICO deste hook: ele erra nas DUAS direcoes e as duas sao silenciosas. Nao acordar
onde devia = o dono abre o projeto e o squad simplesmente nao existe (a queixa original do
ADR-006). Acordar onde NAO devia = injetar o protocolo do squad no repo de terceiro. Por isso os
asserts abaixo cobrem allowlist, marker, os dois locks e o parse de owner em HTTPS e SSH.

Isolamento: HOME/USERPROFILE apontam p/ temporario (allowlist e workflows vivem em ~/.claude).
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "tools", "hooks", "inject_start_session.py")

FAILS = []


def check(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def run(payload, home):
    env = dict(os.environ)
    env["HOME"] = home
    env["USERPROFILE"] = home
    env.pop("CLAUDE_PROJECT_DIR", None)
    r = subprocess.run([sys.executable, HOOK], input=json.dumps(payload), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=60, env=env)
    try:
        out = json.loads((r.stdout or "").strip() or "{}")
    except ValueError:
        out = {}
    return out.get("hookSpecificOutput", {}).get("additionalContext", ""), r


def prep_home(home, owners="fabriciopsouza\n"):
    """~/.claude com allowlist de owners + o workflow que o hook injeta."""
    c = os.path.join(home, ".claude")
    os.makedirs(os.path.join(c, "workflows"), exist_ok=True)
    with open(os.path.join(c, "squad-owners.txt"), "w", encoding="utf-8") as f:
        f.write(owners)
    with open(os.path.join(c, "workflows", "start-session.md"), "w", encoding="utf-8") as f:
        f.write("# /start-session\nPROTOCOLO-CANONICO-DE-ABERTURA\n")
    return c


def git(d, *a):
    subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, timeout=30)


def repo_com_origin(d, url):
    git(d, "init", "-q")
    git(d, "remote", "add", "origin", url)


def main():
    print("# test_inject_start_session (ADR-006/101)")

    # --- 1. Owner na allowlist -> ACORDA e injeta o protocolo (a razao de existir do ADR-006).
    for rotulo, url in (("SSH", "git@github.com:fabriciopsouza/algum-projeto.git"),
                        ("HTTPS", "https://github.com/fabriciopsouza/algum-projeto.git")):
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as d:
            prep_home(home)
            repo_com_origin(d, url)
            ctx, r = run({"cwd": d, "session_id": "s1"}, home)
            check(r.returncode == 0, f"{rotulo}: exit 0 (auto-boot nunca trava a sessao)")
            check("PROTOCOLO-CANONICO-DE-ABERTURA" in ctx,
                  f"{rotulo}: owner na allowlist -> injeta o start-session")

    # --- 2. Owner FORA da allowlist e sem marker -> NAO acorda (nao invade repo de terceiro).
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as d:
        prep_home(home)
        repo_com_origin(d, "git@github.com:outra-pessoa/projeto-alheio.git")
        ctx, _ = run({"cwd": d, "session_id": "s2"}, home)
        check("PROTOCOLO-CANONICO-DE-ABERTURA" not in ctx,
              "owner fora da allowlist e sem marker -> NAO injeta (nao invade repo alheio)")

    # --- 3. Marker do framework no projeto (.agent/ ou AGENTS.md) acorda mesmo sem allowlist.
    for marker in ("AGENTS.md", os.path.join(".agent", "rules", "00-glossario.md")):
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as d:
            prep_home(home, owners="ninguem-com-esse-nome\n")
            repo_com_origin(d, "git@github.com:outra-pessoa/projeto-alheio.git")
            p = os.path.join(d, marker)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write("# marker do framework\n")
            ctx, _ = run({"cwd": d, "session_id": "s3"}, home)
            check("PROTOCOLO-CANONICO-DE-ABERTURA" in ctx,
                  f"marker `{marker}` no projeto acorda o squad sem allowlist")

    # --- 4. Soberania: ~/.claude/session.lock -> SKIP SILENCIOSO (opt-out amplo do dono).
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as d:
        c = prep_home(home)
        with open(os.path.join(c, "session.lock"), "w", encoding="utf-8") as f:
            f.write("off\n")
        repo_com_origin(d, "git@github.com:fabriciopsouza/algum-projeto.git")
        ctx, r = run({"cwd": d, "session_id": "s4"}, home)
        check(r.returncode == 0 and "PROTOCOLO-CANONICO-DE-ABERTURA" not in ctx,
              "session.lock GLOBAL -> skip silencioso (opt-out amplo)")

    # --- 5. <cwd>/.claude/session.lock -> SKIP, mas COM MEMORIA: tem que dizer como religar,
    #        senao o dono desliga e meses depois nao lembra por que o squad sumiu.
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as d:
        prep_home(home)
        repo_com_origin(d, "git@github.com:fabriciopsouza/algum-projeto.git")
        os.makedirs(os.path.join(d, ".claude"), exist_ok=True)
        with open(os.path.join(d, ".claude", "session.lock"), "w", encoding="utf-8") as f:
            f.write("desligado porque X\n")
        ctx, r = run({"cwd": d, "session_id": "s5"}, home)
        check("PROTOCOLO-CANONICO-DE-ABERTURA" not in ctx,
              "session.lock do PROJETO -> nao injeta o protocolo")
        check("session.lock" in ctx.lower(),
              "session.lock do PROJETO -> skip COM MEMORIA (diz como religar)")

    # --- 6. Diretorio sem git e sem marker -> skip declarado, sem crash.
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as d:
        prep_home(home)
        ctx, r = run({"cwd": d, "session_id": "s6"}, home)
        check(r.returncode == 0 and "PROTOCOLO-CANONICO-DE-ABERTURA" not in ctx,
              "pasta sem git nem marker -> skip declarado (exit 0)")

    # --- 7. Fail-soft: payload lixo nunca derruba o SessionStart.
    r = subprocess.run([sys.executable, HOOK], input="{{{lixo", capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=60)
    check(r.returncode == 0, "payload invalido -> exit 0 (falha soft, nunca bloqueia)")

    print("-" * 50)
    print(f"RESULTADO: {'PASS' if not FAILS else 'FAIL (' + str(len(FAILS)) + ')'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
