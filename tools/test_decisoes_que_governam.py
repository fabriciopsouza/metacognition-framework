#!/usr/bin/env python3
"""Canário do decisoes_que_governam — o framework não pode ser passivo (ADR-051/094).

CONTEXTO. A norma "o pedido do dono não é imune a questionamento" era prosa: dependia de alguém
lembrar de consultar o registro de decisões. Em 2026-08-16 o dono pediu algo que colidia com uma
dívida que ele mesmo abrira três dias antes, e a colisão só apareceu porque um crítico
independente foi varrer os registros — uma rodada de agente para uma consulta determinística.

MÉTODO. Repo de mentira com uma capacidade, o ADR que a decidiu e uma dívida aberta que cita esse
ADR. Exige que a ferramenta ligue os três, e que o código de saída distinga os três estados:
nada governa (0), governado sem dívida (1), governado COM dívida aberta (2). O 2 é o que dispara
o surface-and-reconcile — se ele não sair, a ferramenta é decorativa.

Uso: python tools/test_decisoes_que_governam.py   (exit 0 PASS; 1 se a consulta mentir)
"""
import json
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import decisoes_que_governam as dg  # noqa: E402

resultados = []


def caso(nome, ok, detalhe=""):
    resultados.append((nome, ok))
    print(f"  [{'PASS' if ok else 'FALHA'}] {nome}")
    if detalhe and not ok:
        print(f"          {detalhe}")


def _repo(raiz, *, com_divida, status_adr="Aceito"):
    raiz = Path(raiz)
    (raiz / "docs" / "adr").mkdir(parents=True)
    (raiz / "docs" / "adr" / "102-padrao-x.md").write_text(
        f"# ADR-102 - Padrao X\n- Status: {status_adr}\n", encoding="utf-8")
    (raiz / "docs" / "adr" / "050-outra-coisa.md").write_text(
        "# ADR-050 - Outra coisa\n- Status: Aceito\n", encoding="utf-8")
    (raiz / "capabilities.json").write_text(json.dumps({"capabilities": [
        {"id": "padrao-x", "title": "Padrao documental X", "mechanism": "tools/x.py",
         "test": "tools/test_x.py", "adr": "docs/adr/102-padrao-x.md", "enforcement": "prose"},
        {"id": "sem-divida", "title": "Coisa tranquila", "mechanism": "tools/z.py",
         "test": "tools/test_z.py", "adr": "docs/adr/050-outra-coisa.md",
         "enforcement": "fail-closed"},
    ]}, ensure_ascii=False), encoding="utf-8")
    divida = ("- **Quitacao do override do ADR-102** (aberto em 13/08): so promove ao framework "
              "depois de um SEGUNDO projeto usar o padrao.\n") if com_divida else ""
    (raiz / "history.md").write_text(
        f"# history\n\n## 2026-08-16 - checkpoint\ntexto\n\n## Em aberto\n\n{divida}"
        "- Pendencia sem relacao nenhuma com o que se consulta aqui.\n", encoding="utf-8")
    return raiz


def main():
    print("decisoes_que_governam: liga caminho -> decisao -> divida aberta, e grita quando ha")

    with tempfile.TemporaryDirectory(prefix="dg-com-") as tmp:
        r = _repo(tmp, com_divida=True)

        a = dg.governam(r, caminhos=["tools/x.py"])
        caso("acha a decisao que governa um CAMINHO",
             len(a) == 1 and a[0]["capacidade"] == "padrao-x", f"achou: {a}")
        caso("liga a divida aberta que cita o ADR daquela decisao",
             bool(a) and len(a[0]["dividas_abertas"]) == 1,
             f"dividas: {a[0]['dividas_abertas'] if a else None}")
        caso("NAO arrasta a pendencia sem relacao",
             bool(a) and all("sem relacao" not in d for d in a[0]["dividas_abertas"]))

        t = dg.governam(r, termos=["documental"])
        caso("acha a mesma decisao por TERMO, nao so por caminho",
             len(t) == 1 and t[0]["capacidade"] == "padrao-x", f"achou: {t}")

        caso("exit 2 quando ha divida aberta (dispara o surface-and-reconcile)",
             dg.main(["--repo", str(r), "--json", "tools/x.py"]) == 2)
        caso("exit 1 quando governado SEM divida aberta",
             dg.main(["--repo", str(r), "--json", "tools/z.py"]) == 1)
        caso("exit 0 quando nada no registro governa",
             dg.main(["--repo", str(r), "--json", "tools/inexistente.py"]) == 0)

    with tempfile.TemporaryDirectory(prefix="dg-sem-") as tmp:
        r = _repo(tmp, com_divida=False)
        caso("sem divida no history, nao inventa divida",
             dg.main(["--repo", str(r), "--json", "tools/x.py"]) == 1)

    with tempfile.TemporaryDirectory(prefix="dg-prop-") as tmp:
        r = _repo(tmp, com_divida=False, status_adr="Proposto")
        a = dg.governam(r, caminhos=["tools/x.py"])
        caso("reporta que o ADR ainda esta PROPOSTO (decisao nao fechada)",
             bool(a) and a[0]["adr_status"] == "Proposto",
             f"status lido: {a[0]['adr_status'] if a else None}")

    print("-" * 50)
    ruins = [n for n, ok in resultados if not ok]
    if ruins:
        print(f"RESULTADO: FAIL ({len(ruins)}) — {', '.join(ruins)}")
        return 1
    print(f"RESULTADO: PASS ({len(resultados)} verificacoes: a colisao com decisao registrada "
          f"vira consulta deterministica, nao memoria de agente)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
