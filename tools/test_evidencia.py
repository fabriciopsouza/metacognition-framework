#!/usr/bin/env python3
"""Canário do manifesto de evidência de desenvolvimento (ADR-121, REQ-15 do plano B3, critério 16).

  (a) registrar e verificar: caminho absoluto, sha256, data, origem, requisito ou teste;
  (b) sabotagens: arquivo alterado sem nome novo, arquivo apagado, arquivo sensível rastreado pelo git, caminho
      relativo e entrada sem origem no manifesto reprovam; registrar de novo o mesmo caminho com conteúdo diferente é
      recusado; registro sem origem, sem ligação ou com data impossível é recusado;
  (c) o uso antigo do doc_intake (ingestão com manifesto de chunks) continua igual.

Uso: python tools/test_evidencia.py   (exit 0 PASS; 1 FAIL)
"""
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import doc_intake as di  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

falhas = []


def check(nome, cond, detalhe=""):
    print(("  PASS " if cond else "  FAIL ") + nome + ("" if cond else f" — {detalhe}"))
    if not cond:
        falhas.append(nome)


def arquivo(pasta, nome, conteudo):
    p = os.path.join(pasta, nome)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(conteudo)
    return p


def main():
    d = tempfile.mkdtemp()
    m = os.path.join(d, "evidencia.json")
    c1 = arquivo(d, "consulta-01.sql", "SELECT 1;\n")
    x1 = arquivo(d, "resultado-01.csv", "a;b\n1;2\n")

    print("(a) registrar e verificar")
    ok, msg = di.evidencia_registrar(c1, m, "consulta de conferência", "REQ-01", "26/09/2026", False)
    ok2, _ = di.evidencia_registrar(x1, m, "saída da consulta-01.sql", "TESTE-01", "26/09/2026", False)
    ent = json.load(open(m, encoding="utf-8"))["entradas"]
    check("registra com caminho absoluto, sha, data, origem e ligação", ok and ok2 and len(ent) == 2 and all(
        os.path.isabs(e["caminho"]) and len(e["sha256"]) == 64 and e["data"] and e["origem"] and e["liga"] for e in ent),
        (msg, ent))
    check("verificar passa com tudo íntegro", di.evidencia_verificar(m) == [], di.evidencia_verificar(m))
    ok, msg = di.evidencia_registrar(c1, m, "consulta de conferência", "REQ-01", "26/09/2026", False)
    check("registrar de novo sem mudança é aceito sem duplicar", ok and len(json.load(open(m, encoding="utf-8"))["entradas"]) == 2, msg)

    print("(b) sabotagens")
    arquivo(d, "consulta-01.sql", "SELECT 2;\n")
    ach = di.evidencia_verificar(m)
    check("arquivo alterado sem nome novo reprova", any("conteúdo mudou sem nome novo" in a for a in ach), ach)
    ok, msg = di.evidencia_registrar(c1, m, "consulta de conferência", "REQ-01", "26/09/2026", False)
    check("registrar conteúdo novo com o mesmo nome é recusado", not ok and "_obsoleto" in msg, msg)
    os.remove(x1)
    check("arquivo apagado reprova", any("não existe mais" in a for a in di.evidencia_verificar(m)))
    for nome, args in [("sem origem", ("", "REQ-01", "26/09/2026")), ("sem ligação", ("origem", "", "26/09/2026")),
                       ("data impossível", ("origem", "REQ-01", "31/02/2026"))]:
        novo = arquivo(d, f"n-{nome[:3]}.txt", nome)
        ok, msg = di.evidencia_registrar(novo, os.path.join(d, "outro.json"), *args, False)
        check(f"registro {nome} é recusado", not ok, msg)
    mm = os.path.join(d, "manual.json")
    json.dump({"manifest_version": "evidencia-1", "entradas": [
        {"caminho": "relativo.txt", "sha256": "0" * 64, "data": "26/09/2026", "origem": "x", "liga": "REQ-01"},
        {"caminho": c1, "sha256": "0" * 64, "data": "26/09/2026", "origem": "", "liga": "REQ-01"}]},
        open(mm, "w", encoding="utf-8"))
    ach = di.evidencia_verificar(mm)
    check("caminho relativo no manifesto reprova", any("não é absoluto" in a for a in ach), ach)
    check("entrada sem origem no manifesto reprova", any("falta origem" in a for a in ach), ach)
    g = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", g], check=True)
    s = arquivo(g, "extracao-sensivel.csv", "cpf;valor\n")
    subprocess.run(["git", "-C", g, "add", "extracao-sensivel.csv"], check=True)
    ms = os.path.join(d, "sens.json")
    di.evidencia_registrar(s, ms, "extração", "TESTE-02", "26/09/2026", True)
    check("sensível rastreado pelo git reprova",
          any("sensível e está rastreado pelo git" in a for a in di.evidencia_verificar(ms)), di.evidencia_verificar(ms))
    nao = arquivo(g, "fora-do-git.csv", "x\n")
    mn = os.path.join(d, "nao.json")
    di.evidencia_registrar(nao, mn, "extração", "TESTE-03", "26/09/2026", True)
    check("sensível fora do git passa", di.evidencia_verificar(mn) == [], di.evidencia_verificar(mn))

    mc = arquivo(d, "corrompido.json", "{ isto não é json")
    ok, msg = di.evidencia_registrar(c1, mc, "origem", "REQ-01", "26/09/2026", False)
    check("manifesto corrompido: registrar recusa sem estourar", not ok and "manifesto ilegível" in msg, msg)

    print("(c) uso antigo intacto")
    md = arquivo(d, "doc.md", "# t\n\nparágrafo um.\n\nparágrafo dois.\n")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "doc_intake.py"), md], capture_output=True,
                       text=True, encoding="utf-8", env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    man = json.loads(r.stdout) if r.returncode == 0 else {}
    check("ingestão continua gerando manifesto de chunks", man.get("summary", {}).get("n_files") == 1, r.stderr)

    print("-" * 50)
    print("RESULTADO:", f"FAIL ({len(falhas)})" if falhas else "PASS")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
