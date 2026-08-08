#!/usr/bin/env python3
"""Canario do encerramento deterministico + correlacao obrigatoria (ADR-101).

Trava dois relatos do dono (2026-08-07):
  - "encerramentos parciais, sem commit pr e merge, mesmo ja solicitados explicitamente"
  - "se estou atualizando as regras do agente X, o par Y so e atualizado se eu provocar. TEM QUE SER TUDO"
E o requisito nao-negociavel de um hook Stop: NUNCA entrar em loop.
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(ROOT, "tools", "hooks", "closing_gate.py")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import correlated  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def run_gate(payload):
    r = subprocess.run([sys.executable, GATE], input=json.dumps(payload), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=90)
    out = (r.stdout or "").strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except ValueError:
        return None


def git(d, *a):
    subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, timeout=30)


def make_repo(d):
    git(d, "init", "-q")
    git(d, "config", "user.email", "canary@test")
    git(d, "config", "user.name", "canary")
    with open(os.path.join(d, "README.md"), "w", encoding="utf-8") as f:
        f.write("base\n")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "base")


def main():
    print("# test_closing_gate (ADR-101)")

    # --- 1. ANTI-LOOP: stop_hook_active=True SEMPRE libera (requisito duro do hook Stop).
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        with open(os.path.join(d, "sujo.py"), "w", encoding="utf-8") as f:
            f.write("x=1\n")
        git(d, "add", "-A")
        res = run_gate({"cwd": d, "session_id": "s1", "stop_hook_active": True})
        check(res is None, "anti-loop: stop_hook_active=True libera mesmo com repo sujo")

    # --- 2. Repo limpo -> nao bloqueia (gate nao pode ser ruido).
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        res = run_gate({"cwd": d, "session_id": "s2"})
        check(res is None, "repo limpo nao bloqueia")

    # --- 3. Mudanca rastreada nao-commitada -> BLOQUEIA (o relato do dono).
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        with open(os.path.join(d, "README.md"), "a", encoding="utf-8") as f:
            f.write("mudanca nao commitada\n")
        res = run_gate({"cwd": d, "session_id": "s3"})
        check(res is not None and res.get("decision") == "block",
              "mudanca rastreada nao-commitada BLOQUEIA o encerramento")
        check(res is not None and "commit" in res.get("reason", "").lower(),
              "a razao do bloqueio cita commit")

        # --- 3b. 1x por sessao: segunda parada na MESMA sessao libera.
        res2 = run_gate({"cwd": d, "session_id": "s3"})
        check(res2 is None, "bloqueia no maximo 1x por sessao (nao sequestra a sessao)")

    # --- 4. Soberania: .closing.ack libera.
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        with open(os.path.join(d, "README.md"), "a", encoding="utf-8") as f:
            f.write("suja\n")
        os.makedirs(os.path.join(d, ".claude"), exist_ok=True)
        with open(os.path.join(d, ".claude", ".closing.ack"), "w", encoding="utf-8") as f:
            f.write("ok\n")
        check(run_gate({"cwd": d, "session_id": "s4"}) is None, ".closing.ack libera o projeto")

    # --- 5. Soberania: session.lock libera.
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        with open(os.path.join(d, "README.md"), "a", encoding="utf-8") as f:
            f.write("suja\n")
        os.makedirs(os.path.join(d, ".claude"), exist_ok=True)
        open(os.path.join(d, ".claude", "session.lock"), "w").close()
        check(run_gate({"cwd": d, "session_id": "s5"}) is None, "session.lock silencia o gate")

    # --- 6. Nao-git -> libera (gate so fala do que sabe medir).
    with tempfile.TemporaryDirectory() as d:
        check(run_gate({"cwd": d, "session_id": "s6"}) is None, "diretorio nao-git nao bloqueia")

    # --- 7. Higiene da raiz: handoff solto na raiz e apontado.
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        with open(os.path.join(d, "handoff-2026.md"), "w", encoding="utf-8") as f:
            f.write("# handoff\n")
        res = run_gate({"cwd": d, "session_id": "s7"})
        check(res is not None and "raiz" in res.get("reason", "").lower(),
              "handoff solto na raiz e detectado como poluicao")
        check(res is not None and "docs/_private/handoffs" in res.get("reason", ""),
              "a razao aponta o lar correto do handoff")

    # --- 8. Doc legitimo na raiz (README/CHANGELOG) NAO e poluicao (anti-falso-positivo).
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        for name in ("CHANGELOG.md", "SECURITY.md"):
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write("x\n")
        res = run_gate({"cwd": d, "session_id": "s8"})
        reason = (res or {}).get("reason", "")
        check("raiz" not in reason.lower(), "CHANGELOG/SECURITY na raiz nao sao falso-positivo")

    # --- 9. correlated: par incompleto reprova; par completo passa; sem manifesto = SKIP declarado.
    groups = [{"id": "par", "rule": "all", "members": ["a/**", "b/**"]}]
    check(len(correlated.check(groups, ["a/x.txt"])) == 1, "correlato: metade do par -> violacao")
    check(correlated.check(groups, ["a/x.txt", "b/y.txt"]) == [], "correlato: par completo -> OK")
    check(correlated.check(groups, ["c/z.txt"]) == [], "correlato: fora do grupo -> sem ruido")
    with tempfile.TemporaryDirectory() as d:
        g, skip = correlated.load_manifest(d)
        check(g is None and "skip declarado" in skip,
              "sem correlations.json -> SKIP DECLARADO (nunca falso-OK)")

    # --- 10. glob '**' casa recursivo e o proprio prefixo.
    check(correlated.matches("a/**", "a/b/c.txt"), "glob a/** casa a/b/c.txt")
    check(correlated.matches("docs/adr/*.md", "docs/adr/101-x.md"), "glob simples casa")
    check(not correlated.matches("a/**", "ab/c.txt"), "glob a/** NAO casa ab/c.txt")

    # --- 11. O manifesto deste repo e valido e cobre os pares que ja falharam na pratica.
    g, _ = correlated.load_manifest(ROOT)
    check(g is not None, ".agent/correlations.json deste repo carrega")
    ids = {x.get("id") for x in (g or [])}
    for want in ("adr-changelog", "capacidade-indice", "gate-precisa-de-canario"):
        check(want in ids, f"grupo declarado: `{want}`")

    print("-" * 50)
    print(f"RESULTADO: {'PASS' if not FAILS else 'FAIL (' + str(len(FAILS)) + ')'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
