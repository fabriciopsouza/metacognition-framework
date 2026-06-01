#!/usr/bin/env python3
"""Canário: make_index gera índice navegável, ordem guiada, auto-verificado (baseline). Exit 0 PASS."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_index  # noqa: E402


def _mk(root, rel, content=""):
    p = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(content)


def run():
    fails = []
    with tempfile.TemporaryDirectory() as d:
        root = os.path.join(d, "2026-06-01T120000-analise-x")
        _mk(root, "docs/RESUMO.md", "# Resumo\nLinha util um.\nLinha util dois.\n")
        _mk(root, "docs/relatorio.pdf", "x")
        _mk(root, "apresentacao/deck.pptx", "x")
        _mk(root, "codigo/run.py", "print(1)")
        _mk(root, "dados/base.csv", "a,b")
        n, idx = make_index.generate(root)

        html_p = os.path.join(root, "index.html")
        txt_p = os.path.join(root, "LEIA-ME.txt")
        if not os.path.isfile(html_p):
            fails.append("index.html não gerado")
        if not os.path.isfile(txt_p):
            fails.append("LEIA-ME.txt não gerado")
        if n != 5:
            fails.append(f"contagem errada: {n} (esperado 5)")

        html = open(html_p, encoding="utf-8").read() if os.path.isfile(html_p) else ""
        # auto-verificação: todo arquivo varrido aparece linkado; o índice não se autolista
        for rel in ("docs/relatorio.pdf", "apresentacao/deck.pptx", "codigo/run.py", "dados/base.csv"):
            if f'href="{rel}"' not in html:
                fails.append(f"arquivo ausente do índice: {rel}")
        if "index.html" in [l for l in html.split('href="') if l.startswith("index.html")]:
            fails.append("índice se autolistou")
        # resumo lido do RESUMO.md (não NÃO PREENCHIDO)
        if "Linha util um" not in html:
            fails.append("resumo de 3 linhas não extraído do arquivo de resumo")
        # ordem guiada: 'comece aqui' antes de 'planilhas e dados'
        if "comece aqui" in html and "planilhas e dados" in html:
            if html.index("comece aqui") > html.index("planilhas e dados"):
                fails.append("ordem de leitura guiada fora de ordem")
        # handoff: versão derivada do datestamp da pasta
        if "2026-06-01T120000" not in html:
            fails.append("handoff: carimbo/versão não derivado do nome da pasta")

        # entrega sem resumo → NÃO PREENCHIDO (não inventa)
        root2 = os.path.join(d, "entrega-sem-resumo")
        _mk(root2, "codigo/x.py", "1")
        make_index.generate(root2)
        h2 = open(os.path.join(root2, "index.html"), encoding="utf-8").read()
        if "NÃO PREENCHIDO" not in h2:
            fails.append("sem arquivo de resumo deveria render NÃO PREENCHIDO (não inventar)")

    if fails:
        print("FAIL:\n  - " + "\n  - ".join(fails))
        return 1
    print("PASS: índice html+txt, ordem guiada, auto-verificado, resumo anti-fabricação, handoff.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
