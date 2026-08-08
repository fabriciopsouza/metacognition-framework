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


def qa_regressoes():
    """Regressoes do QA heterogeneo (sonnet, 2026-08-08) — cada uma REPRODUZIDA antes do fix."""
    print("# regressoes do QA heterogeneo (ADR-101)")

    # --- QA-1 [GRAVE] Poluicao de raiz sobrevivia ao proprio conselho do gate.
    # `root_pollution` olhava so untracked (`??`). O agente seguia a instrucao "Commit + push"
    # e o arquivo mal-posicionado sumia do porcelain: invisivel para sempre.
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        git(d, "checkout", "-qb", "bloco")
        with open(os.path.join(d, "handoff-2026-relatorio.md"), "w", encoding="utf-8") as f:
            f.write("handoff no lugar errado\n")
        res = run_gate({"cwd": d, "session_id": "qa1a"})
        check(res is not None and "raiz" in (res or {}).get("reason", "").lower(),
              "QA-1: handoff solto na raiz bloqueia enquanto untracked")
        git(d, "add", "-A")
        git(d, "commit", "-qm", "commit do handoff na raiz")
        res = run_gate({"cwd": d, "session_id": "qa1b"})
        raz = (res or {}).get("reason", "").lower()
        check(res is not None and "raiz" in raz,
              "QA-1: poluicao de raiz CONTINUA detectada depois do commit (era invisivel)")

    # --- QA-2 [GRAVE] `.closing.ack` nunca expirava: 1 `echo ok` desligava o gate para sempre.
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        with open(os.path.join(d, "README.md"), "a", encoding="utf-8") as f:
            f.write("mudanca\n")
        os.makedirs(os.path.join(d, ".claude"), exist_ok=True)
        ack = os.path.join(d, ".claude", ".closing.ack")
        with open(ack, "w", encoding="utf-8") as f:
            f.write("ok\n")
        res = run_gate({"cwd": d, "session_id": "qa2a"})
        check(res is None, "QA-2: ack cru (`echo ok`) libera na primeira vez")
        with open(ack, encoding="utf-8") as f:
            check("closing-ack-fp:" in f.read(),
                  "QA-2: ack e CARIMBADO com o estado que reconheceu")
        res = run_gate({"cwd": d, "session_id": "qa2b"})
        check(res is None, "QA-2: mesmo estado + ack carimbado -> continua liberando")
        with open(os.path.join(d, "NOVIDADE-nao-relacionada.md"), "w", encoding="utf-8") as f:
            f.write("estado mudou depois do ack\n")
        res = run_gate({"cwd": d, "session_id": "qa2c"})
        check(res is not None,
              "QA-2: estado MUDOU depois do ack -> gate volta a valer (ack nao e interruptor)")

    # --- QA-3 [GRAVE] Sem `session_id` o marcador virava "" e o anti-loop sumia: 3 chamadas,
    #     3 bloqueios. A garantia "no maximo 1x por sessao" tem que valer sem session_id.
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        with open(os.path.join(d, "README.md"), "a", encoding="utf-8") as f:
            f.write("sujo\n")
        r1 = run_gate({"cwd": d})
        r2 = run_gate({"cwd": d})
        r3 = run_gate({"cwd": d})
        check(r1 is not None, "QA-3: sem session_id, o 1o Stop ainda bloqueia")
        check(r2 is None and r3 is None,
              "QA-3: sem session_id, 2a/3a chamadas LIBERAM (anti-loop vale sem session_id)")

    # --- QA-4 [GRAVE] `git` fora do PATH era engolido: gate virava no-op indistinguivel de
    #     "nao e repo git". Fail-open continua (correto), mas tem que ser DECLARADO em stderr.
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        with open(os.path.join(d, "README.md"), "a", encoding="utf-8") as f:
            f.write("sujo\n")
        env = dict(os.environ)
        env["PATH"] = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32") \
            if os.name == "nt" else "/nonexistent"
        r = subprocess.run([sys.executable, GATE], input=json.dumps({"cwd": d}),
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=90, env=env)
        check(r.returncode == 0 and not (r.stdout or "").strip(),
              "QA-4: git ausente -> fail-open (nao sequestra a sessao)")
        check("INERTE" in (r.stderr or ""),
              "QA-4: git ausente -> DECLARA em stderr (fail-open silencioso e falso-OK)")

    # --- QA-6 [BLOQUEANTE] correlated media so o working tree: par quebrado JA COMMITADO
    #     passava trivialmente. Como o closing_gate roda no Stop (DEPOIS do commit), o gate
    #     media exatamente o instante em que nao ha mais nada para ver.
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        os.makedirs(os.path.join(d, ".agent"), exist_ok=True)
        with open(os.path.join(d, ".agent", "correlations.json"), "w", encoding="utf-8") as f:
            json.dump({"schema_version": 1, "groups": [
                {"id": "par", "rule": "all", "members": ["a.md", "b.md"]}]}, f)
        git(d, "add", "-A")
        git(d, "commit", "-qm", "manifesto")
        git(d, "checkout", "-qb", "bloco")
        with open(os.path.join(d, "a.md"), "w", encoding="utf-8") as f:
            f.write("so metade do par\n")
        git(d, "add", "-A")
        git(d, "commit", "-qm", "quebra o par e COMMITA")
        viol_wt = correlated.check(
            [{"id": "par", "rule": "all", "members": ["a.md", "b.md"]}],
            correlated.git_touched(d, scope="worktree"))
        viol_br = correlated.check(
            [{"id": "par", "rule": "all", "members": ["a.md", "b.md"]}],
            correlated.git_touched(d, scope="branch"))
        check(not viol_wt, "QA-6: escopo worktree nao ve o par quebrado apos o commit (o bug)")
        check(len(viol_br) == 1,
              "QA-6: escopo branch (default) PEGA o par quebrado ja commitado")

    # --- QA-7 [BLOQUEANTE] rule='all' era silenciada por QUALQUER membro do outro glob.
    #     Tocar um teste nao relacionado calava a exigencia de canario do gate novo.
    grupo_all = {"id": "g", "rule": "all",
                 "members": ["tools/hooks/*.py", "tools/test_*.py"]}
    grupo_par = {"id": "g", "rule": "pairwise", "direction": "forward",
                 "strip_prefixes": ["check_"], "exempt": ["tools/hooks/_*.py"],
                 "members": ["tools/hooks/*.py", "tools/test_*.py"]}
    nao_relacionado = ["tools/hooks/novo_gate.py", "tools/test_outra_coisa.py"]
    par_correto = ["tools/hooks/novo_gate.py", "tools/test_novo_gate.py"]
    check(not correlated.check([grupo_all], nao_relacionado),
          "QA-7: rule='all' NAO pega o teste nao relacionado (o bug reproduzido)")
    check(len(correlated.check([grupo_par], nao_relacionado)) == 1,
          "QA-7: rule='pairwise' PEGA — exige o canario correspondente")
    check(not correlated.check([grupo_par], par_correto),
          "QA-7: rule='pairwise' aprova o par correspondente (sem falso-positivo)")
    check(not correlated.check([grupo_par], ["tools/hooks/_project.py"]),
          "QA-7: `exempt` isenta helper que nao e gate (tools/hooks/_*.py)")
    check(correlated._stem("tools/test_*.py", "tools/test_author_tier.py") == "author_tier"
          and correlated._stem("tools/hooks/*.py", "tools/hooks/check_author_tier.py",
                               ("check_",)) == "author_tier",
          "QA-7: strip_prefixes pareia check_author_tier.py <-> test_author_tier.py")
    check(not correlated.check([grupo_par], ["tools/test_wire_gates.py"]),
          "QA-7: direction=forward — canario nao exige gate inverso (wire_gates mora em tools/)")

    # --- QA-8 [GRAVE] `rule` era campo MORTO: valor invalido nao tinha efeito nem aviso.
    inval = correlated.check([{"id": "x", "rule": "maioria", "members": ["a", "b"]}], ["a"])
    check(len(inval) == 1 and "desconhecida" in (inval[0].get("erro") or ""),
          "QA-8: rule invalida REPROVA declarado (campo deixou de ser decorativo)")

    # --- QA-9 [GRAVE] fnmatch case-insensitive no Windows: mesmo manifesto, veredito diferente
    #     entre CI Linux e a maquina do dono. Determinismo exige fnmatchcase.
    check(not correlated.matches("tools/hooks/*.py", "tools/HOOKS/Foo.PY"),
          "QA-9: casamento e case-SENSITIVE (mesmo veredito em Linux e Windows)")

    # --- QA-5 [MENOR] session_id patologico ('..') resolvia o marcador p/ o proprio .claude/.
    with tempfile.TemporaryDirectory() as d:
        make_repo(d)
        with open(os.path.join(d, "README.md"), "a", encoding="utf-8") as f:
            f.write("sujo\n")
        r1 = run_gate({"cwd": d, "session_id": ".."})
        r2 = run_gate({"cwd": d, "session_id": ".."})
        check(r1 is not None and r2 is None,
              "QA-5: session_id '..' nao quebra o marcador (bloqueia 1x, depois libera)")


def main():
    print("# test_closing_gate (ADR-101)")
    qa_regressoes()

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
