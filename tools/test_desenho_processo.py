#!/usr/bin/env python3
"""Canário do desenho do processo e do método único (ADR-121).

  (a) VERDE — processo simples gera HTML e docx; HTML autônomo (sem http nos recursos), com raias, decisão,
      retorno, papéis, gatilhos, pontos para aprovação e perguntas; mostra onde responder;
  (b) GERADO, NÃO EDITADO — alterar um passo na especificação e gerar de novo muda o HTML e o docx (critério 15);
  (c) SABOTAGENS — passo sem papel, destino inexistente, passo repetido, 16 passos sem macroação, mais papéis do que
      cabem na tela, parte H ausente: reprovam e nada é gerado;
  (d) MACROAÇÕES — 16 passos agrupados geram visão geral + um desenho por macroação; aceite do dono com data libera
      16 passos sem agrupar; aceite sem data não libera;
  (e) MÉTODO ÚNICO — `guia/METODO-DE-PROJETO.md` existe, tem as 8 etapas na ordem, e `CLAUDE.md` e o início de
      sessão apontam para ele (critério 14).

Uso: python tools/test_desenho_processo.py   (exit 0 PASS; 1 FAIL)
"""
import os
import re
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import desenho_processo as dp  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

CAB = "| Passo | Macroação | Descrição | Papel | Gatilho | Saída | Próximo | Regra | Controle |\n|---|---|---|---|---|---|---|---|---|\n"
BASE = ("<!-- spec-unico:v1 -->\n# Caso — Especificação\n\n# Parte H — Processo\n\n" + CAB +
        "| P-01 | — | Registrar pedido | Solicitante | necessidade | pedido | P-02 | pedido justificado | — |\n"
        "| P-02 | — | Avaliar risco | Dono | — | avaliação | P-03 | — | avaliação datada |\n"
        "| P-03 | — | Aprovado? | Qualidade | — | — | sim: P-04; não: P-01 | — | decisão registrada |\n"
        "| P-04 | — | Liberar | Sistemas | aprovação | liberado | | — | — |\n\n"
        "### Pontos para aprovação\n| # | Ponto | Por que importa |\n|---|---|---|\n| 1 | Qualidade decide | dono |\n\n"
        "### Perguntas em aberto\n| # | Pergunta | Quem decide |\n|---|---|---|\n| 1 | Emergência pula P-02? | Qualidade |\n")
falhas = []


def check(nome, cond, detalhe=""):
    print(("  PASS " if cond else "  FAIL ") + nome + ("" if cond else f" — {detalhe}"))
    if not cond:
        falhas.append(nome)


def gerar(texto, *extra):
    d = tempfile.mkdtemp()
    esp, out = os.path.join(d, "esp"), os.path.join(d, "out")
    os.makedirs(esp)
    with open(os.path.join(esp, "spec.md"), "w", encoding="utf-8") as fh:
        fh.write(texto)
    rc = dp.main(["x", os.path.join(esp, "spec.md"), "--out-dir", out, *extra])
    return rc, out, os.path.join(esp, "spec.md")


def ler(p):
    return open(p, encoding="utf-8").read() if os.path.isfile(p) else ""


def docx_texto(p):
    with zipfile.ZipFile(p) as z:
        return z.read("word/document.xml").decode("utf-8")


def passos_lineares(n, macro=""):
    linhas = []
    for i in range(1, n + 1):
        m = macro(i) if callable(macro) else "—"
        prox = f"P-{i + 1:02d}" if i < n else ""
        linhas.append(f"| P-{i:02d} | {m} | Passo {i} | Papel {1 + i % 3} | — | — | {prox} | — | — |")
    return "<!-- spec-unico:v1 -->\n# Longo — Especificação\n\n# Parte H — Processo\n\n" + CAB + "\n".join(linhas) + "\n"


def main():
    print("(a) verde")
    rc, out, spec = gerar(BASE)
    h = ler(os.path.join(out, "desenho-processo.html"))
    check("gera HTML, md e docx", rc == 0 and all(os.path.isfile(os.path.join(out, f"desenho-processo.{x}"))
                                                  for x in ("html", "md", "docx")), rc)
    check("HTML autônomo (sem recurso externo)", not re.search(r'(src|href)="https?:', h))
    check("uma raia por papel", all(p in h for p in ("Solicitante", "Dono", "Qualidade", "Sistemas")))
    check("decisão em losango e retorno tracejado no fluxo (além da legenda)",
          "<polygon" in h and h.count('class="ar ret"') >= 2, h.count('class="ar ret"'))
    check("seções de revisão", all(s in h for s in ("Quem faz o quê", "Gatilhos", "Regras", "Pontos de controle",
                                                    "O que pedimos que aprovem", "Perguntas em aberto")))
    check("diz onde responder (planilha de confirmação)", "planilha de confirmação" in h)
    check("carimbo de versão com sha da especificação", re.search(r"sha256 [0-9a-f]{12}", h))

    print("(b) gerado, não editado")
    antes_h, antes_d = h, docx_texto(os.path.join(out, "desenho-processo.docx"))
    with open(spec, "w", encoding="utf-8") as fh:
        fh.write(BASE.replace("Registrar pedido", "Registrar pedido com anexo"))
    rc = dp.main(["x", spec, "--out-dir", out])
    depois_h, depois_d = ler(os.path.join(out, "desenho-processo.html")), docx_texto(os.path.join(out, "desenho-processo.docx"))
    check("HTML muda", rc == 0 and antes_h != depois_h and "com anexo" in depois_h)
    check("docx muda (regravado, sem cópia -1)", "com anexo" in depois_d and not os.path.exists(
        os.path.join(out, "desenho-processo-1.docx")))

    print("(b2) rodada 1 do QA isolado")
    variantes = (BASE.replace("| Avaliar risco | Dono |", "| Avaliar risco | solicitante |")
                 .replace("| Liberar | Sistemas |", "| Liberar | SOLICITANTE |"))
    rc, out2, _ = gerar(variantes)
    check("mesmo papel com caixa diferente é uma raia só", rc == 0 and "· 2 papéis" in ler(
        os.path.join(out2, "desenho-processo.html")), rc)
    if os.name == "nt":  # trava de arquivo aberto é comportamento do Windows
        docx = os.path.join(out, "desenho-processo.docx")
        html_antes = ler(os.path.join(out, "desenho-processo.html"))
        with open(docx, "r+b"):
            rc = dp.main(["x", spec, "--out-dir", out])
        check("docx em uso: recusa e deixa os três gerados como estavam",
              rc == 1 and os.path.isfile(os.path.join(out, "desenho-processo.md"))
              and ler(os.path.join(out, "desenho-processo.html")) == html_antes
              and not any(f.endswith(".anterior") for f in os.listdir(out)), (rc, os.listdir(out)))

    # rodada 2 do QA isolado: falha DURANTE a escrita dos novos também volta ao estado anterior
    import gen_exec_doc
    original = gen_exec_doc.export
    antes = {x: ler(os.path.join(out, f"desenho-processo.{x}")) for x in ("html", "md")}
    antes_docx = open(os.path.join(out, "desenho-processo.docx"), "rb").read()

    def export_quebrado(*a, **k):
        raise OSError("disco cheio (simulado)")
    gen_exec_doc.export = export_quebrado
    try:
        with open(spec, "w", encoding="utf-8") as fh:
            fh.write(BASE.replace("Registrar pedido", "Texto que não pode aparecer"))
        rc = dp.main(["x", spec, "--out-dir", out])
    finally:
        gen_exec_doc.export = original
    depois = {x: ler(os.path.join(out, f"desenho-processo.{x}")) for x in ("html", "md")}
    check("falha na escrita: recusa e os três gerados anteriores ficam intactos",
          rc == 1 and depois == antes and open(os.path.join(out, "desenho-processo.docx"), "rb").read() == antes_docx
          and not any(f.endswith(".anterior") for f in os.listdir(out)), (rc, os.listdir(out)))

    print("(c) sabotagens — reprovam e não geram")
    linha_p4 = "| P-04 | — | Liberar | Sistemas | aprovação | liberado | | — | — |\n"
    casos = [
        ("passo sem papel", BASE.replace("| Avaliar risco | Dono |", "| Avaliar risco | — |"), "P-02: sem papel"),
        ("destino inexistente", BASE.replace("sim: P-04; não: P-01", "sim: P-09; não: P-01"), "próximo P-09 não existe"),
        ("passo repetido", BASE.replace(linha_p4, linha_p4 + linha_p4), "P-04 repetido"),
        ("16 passos sem macroação", passos_lineares(16), "16 passos sem macroação"),
        ("mais papéis do que cabem na tela", "<!-- spec-unico:v1 -->\n# X — Especificação\n\n# Parte H — Processo\n\n"
         + CAB + "\n".join(f"| P-{i:02d} | — | passo | Papel{i} | — | — | {'P-%02d' % (i + 1) if i < 8 else ''} | — | — |"
                           for i in range(1, 9)) + "\n", "8 papéis dá"),
        ("parte H ausente", "<!-- spec-unico:v1 -->\n# X — Especificação\n\n# Parte A — Requisitos\n- REQ-01: x\n",
         "Parte H — Processo ausente"),
    ]
    for nome, texto, esperado in casos:
        rc, out, spec = gerar(texto)
        passos, _pt, _pg, ach = dp.carregar(spec)
        ach += dp.validar(passos)
        check(nome, rc == 1 and not os.path.exists(os.path.join(out, "desenho-processo.html"))
              and any(esperado in a for a in ach), (rc, ach))

    print("(d) macroações e aceite")
    agrupado = passos_lineares(16, lambda i: "Entrada" if i <= 8 else "Execução")
    rc, out, _ = gerar(agrupado)
    h = ler(os.path.join(out, "desenho-processo.html"))
    check("16 passos em 2 macroações: visão geral + 2 detalhes", rc == 0 and "Visão geral em 2 macroações" in h
          and "Entrada — 8 passos" in h and "Execução — 8 passos" in h, rc)
    rc, _o, _ = gerar(passos_lineares(16), "--aceito-mais-de-15", "dono aceitou manter assim em 26/09/2026")
    check("aceite do dono com data libera 16 passos", rc == 0, rc)
    rc, _o, _ = gerar(passos_lineares(16), "--aceito-mais-de-15", "pode seguir")
    check("aceite sem data não libera", rc == 1, rc)
    rc, _o, _ = gerar(passos_lineares(17, lambda i: "Uma só"))
    check("macroação com mais de 15 passos reprova", rc == 1, rc)

    print("(e) método único")
    metodo = ler(os.path.join(ROOT, "guia", "METODO-DE-PROJETO.md"))
    etapas = ["Abertura", "Elicitação", "Confirmação da área", "Especificação", "Desenho do processo",
              "Testes e evidências", "Liberação", "Operação e fechamento"]
    idx = [metodo.find(f"| {n} | {e} |") for n, e in enumerate(etapas)]
    check("8 etapas na ordem", all(i > 0 for i in idx) and idx == sorted(idx), idx)
    check("CLAUDE.md aponta para o método", "guia/METODO-DE-PROJETO.md" in ler(os.path.join(ROOT, "CLAUDE.md")))
    check("início de sessão aponta para o método",
          "guia/METODO-DE-PROJETO.md" in ler(os.path.join(ROOT, ".agent", "workflows", "start-session.md")))

    print("-" * 50)
    print("RESULTADO:", f"FAIL ({len(falhas)})" if falhas else "PASS")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
