#!/usr/bin/env python3
"""Canario do route-gate em Python (ADR-027/101).

POR QUE ESTE ARQUIVO EXISTE: o ADR-101 portou o route-gate de PowerShell para Python — o hook
que faz o agente DECLARAR A ROTA antes de agir — e nao deixou canario. Quem cobrou foi o gate
`gate-precisa-de-canario`, depois que o QA heterogeneo (2026-08-08) o consertou. O port trocou a
implementacao de um gate que roda a CADA prompt: sem canario, uma regressao aqui degradaria o
framework inteiro em silencio (a rota deixaria de ser exigida e ninguem veria).

Isolamento: HOME/USERPROFILE apontam p/ um diretorio temporario, porque o marker 1x-por-sessao
do route-gate vive em ~/.claude/.route-state — canario nao suja a maquina do dono.
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "tools", "hooks", "route_gate.py")

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


PROMPT = "preciso consolidar as regras de calculo e transformar a planilha em tabela final"


def main():
    print("# test_route_gate (ADR-027/101)")

    # --- 1. Prompt de dominio -> EXIGE declaracao de rota (a razao de existir do gate).
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as d:
        ctx, r = run({"cwd": d, "session_id": "r1", "prompt": PROMPT}, home)
        check(r.returncode == 0, "exit 0 (gate de ENTRADA nunca trava o usuario)")
        check("Declare a ROTA" in ctx, "prompt de dominio -> injeta a exigencia de rota")
        check("metacognicao" in ctx and "squad" in ctx, "oferece as rotas (pontual x multi-etapa)")
        check("high-stakes-gate" in ctx, "declara a rota de alto risco/regulado/irreversivel")
        check("surface-and-reconcile" in ctx,
              "lembra que o pedido do dono NAO e imune a questionamento (ADR-051)")

    # --- 2. Prompt trivial ('ok', 'segue') -> silencio. Gate que fala sempre vira ruido ignorado.
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as d:
        for triv in ("ok", "sim", "beleza", "continua", "valeu"):
            ctx, _ = run({"cwd": d, "session_id": f"t-{triv}", "prompt": triv}, home)
            check("Declare a ROTA" not in ctx, f"prompt trivial '{triv}' nao injeta rota")

    # --- 3. Uma vez por sessao: reinjetar a cada turno queimaria contexto e viraria ruido.
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as d:
        c1, _ = run({"cwd": d, "session_id": "mesma", "prompt": PROMPT}, home)
        c2, _ = run({"cwd": d, "session_id": "mesma", "prompt": PROMPT}, home)
        check("Declare a ROTA" in c1, "1o prompt da sessao injeta a rota")
        check("Declare a ROTA" not in c2, "2o prompt da MESMA sessao nao repete (1x por sessao)")
        c3, _ = run({"cwd": d, "session_id": "outra", "prompt": PROMPT}, home)
        check("Declare a ROTA" in c3, "sessao NOVA volta a injetar (marker e por session_id)")

    # --- 4. Soberania do dono: session.lock silencia (projeto e global).
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, ".claude"), exist_ok=True)
        with open(os.path.join(d, ".claude", "session.lock"), "w", encoding="utf-8") as f:
            f.write("off\n")
        ctx, _ = run({"cwd": d, "session_id": "lock1", "prompt": PROMPT}, home)
        check("Declare a ROTA" not in ctx, "session.lock do PROJETO silencia o gate")
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(home, ".claude"), exist_ok=True)
        with open(os.path.join(home, ".claude", "session.lock"), "w", encoding="utf-8") as f:
            f.write("off\n")
        ctx, _ = run({"cwd": d, "session_id": "lock2", "prompt": PROMPT}, home)
        check("Declare a ROTA" not in ctx, "session.lock GLOBAL silencia o gate")

    # --- 5. Fail-open absoluto: payload lixo -> exit 0 e JSON valido (nunca trava o prompt).
    r = subprocess.run([sys.executable, HOOK], input="{{{lixo", capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=60)
    check(r.returncode == 0, "payload invalido -> exit 0 (fail-open)")
    try:
        json.loads((r.stdout or "").strip() or "{}")
        check(True, "payload invalido -> stdout continua sendo JSON valido")
    except ValueError:
        check(False, "payload invalido -> stdout continua sendo JSON valido")

    # --- 6. Sem session_id (payload minimo) o gate ainda injeta — nao pode virar no-op.
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as d:
        ctx, _ = run({"cwd": d, "prompt": PROMPT}, home)
        check("Declare a ROTA" in ctx, "sem session_id o gate ainda exige a rota")

    print("-" * 50)
    print(f"RESULTADO: {'PASS' if not FAILS else 'FAIL (' + str(len(FAILS)) + ')'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
