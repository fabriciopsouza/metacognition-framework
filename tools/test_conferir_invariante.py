#!/usr/bin/env python3
"""Canário da conferência por invariante (ADR-134, B2 do plano da análise acompanhada).

Para cada invariante da seção 3 da skill `.agent/skills/analise-dados/SKILL.md`: um caso legítimo que PASSA e ao
menos um defeito que REPROVA, inclusive troca de valores entre linhas que preserva contagem e soma. Também prova o
limite declarado (soma por grupo não vê troca dentro do mesmo grupo; a chave vê) e o caminho da linha de comando
(exit 0, 1 e 2). Dados neutros, sem número de projeto.

Uso: python tools/test_conferir_invariante.py   (exit 0 PASS; 1 se falha)
"""
import csv
import json
import os
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import conferir_invariante as ci  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def t(cab, *linhas):
    return list(cab), [dict(zip(cab, ln)) for ln in linhas]


def passa(v):
    return all(x["ok"] for x in v)


CAB = ("id", "grupo", "valor")
BASE = t(CAB, ("1", "A", "10"), ("2", "A", "20"), ("3", "B", "30"), ("4", "B", "40"))
# troca de valores entre linhas de grupos diferentes: contagem 4 e soma 100 preservadas
TROCA = t(CAB, ("1", "A", "30"), ("2", "A", "20"), ("3", "B", "10"), ("4", "B", "40"))
# troca dentro do mesmo grupo: soma por grupo preservada
TROCA_MESMO_GRUPO = t(CAB, ("1", "A", "20"), ("2", "A", "10"), ("3", "B", "30"), ("4", "B", "40"))

casos = []


def caso(nome, esperado_passa, verificacoes):
    casos.append((nome, esperado_passa, passa(verificacoes), verificacoes))


# ---- filtro ou exclusão
FICOU = t(CAB, ("1", "A", "10"), ("2", "A", "20"), ("4", "B", "40"))
SAIU = t(CAB + ("motivo",), ("3", "B", "30", "fora do escopo"))
caso("filtro legítimo", True, ci.conferir_filtro(BASE, FICOU, SAIU, motivo="motivo", saiu=1))
caso("filtro: linha some sem motivo (funil não fecha)", False,
     ci.conferir_filtro(BASE, t(CAB, ("1", "A", "10"), ("2", "A", "20")), SAIU, saiu=1))
caso("filtro: valor alterado na linha que ficou (contagem fecha)", False,
     ci.conferir_filtro(BASE, t(CAB, ("1", "A", "10"), ("2", "A", "20"), ("4", "B", "41")), SAIU))
caso("filtro: excluídas diferente do esperado", False,
     ci.conferir_filtro(BASE, FICOU, SAIU, motivo="motivo", saiu=2))
caso("filtro: coluna perdida nas linhas que ficaram e saíram", False,
     ci.conferir_filtro(BASE, t(("id", "grupo"), ("1", "A"), ("2", "A"), ("4", "B")),
                        t(("id", "grupo"), ("3", "B")), saiu=1))
caso("filtro: coluna a mais nas linhas que ficaram", False,
     ci.conferir_filtro(BASE, t(CAB + ("extra",), ("1", "A", "10", "x"), ("2", "A", "20", "x"), ("4", "B", "40", "x")),
                        SAIU, motivo="motivo"))
caso("filtro: excluída sem motivo", False,
     ci.conferir_filtro(BASE, FICOU, t(CAB + ("motivo",), ("3", "B", "30", "")), motivo="motivo"))

# ---- junção
ESQ = t(("id", "grupo"), ("1", "A"), ("2", "A"), ("3", "B"))
DIR = t(("grupo", "nome"), ("A", "alfa"), ("B", "beta"), ("C", "gama"))
RES = t(("id", "grupo", "nome"), ("1", "A", "alfa"), ("2", "A", "alfa"), ("3", "B", "beta"))
caso("junção N:1 legítima", True, ci.conferir_juncao(ESQ, DIR, RES, ["grupo"], "N:1"))
DIR_DUP = t(("grupo", "nome"), ("A", "alfa"), ("A", "alfa2"), ("B", "beta"))
RES_DUP = t(("id", "grupo", "nome"), ("1", "A", "alfa"), ("1", "A", "alfa2"), ("2", "A", "alfa"),
            ("2", "A", "alfa2"), ("3", "B", "beta"))
caso("junção: chave repetida no lado 1 (linhas multiplicadas)", False,
     ci.conferir_juncao(ESQ, DIR_DUP, RES_DUP, ["grupo"], "N:1"))
caso("junção: resultado perdeu linha", False, ci.conferir_juncao(ESQ, DIR, t(RES[0], *[
    tuple(r.values()) for r in RES[1][:2]]), ["grupo"], "N:1"))
ESQ_ORF = t(("id", "grupo"), ("1", "A"), ("9", "Z"))
caso("junção à esquerda legítima com órfã", True,
     ci.conferir_juncao(ESQ_ORF, DIR, t(("id", "grupo", "nome"), ("1", "A", "alfa"), ("9", "Z", "")),
                        ["grupo"], "N:1", "esquerda"))
caso("junção interna: órfã da esquerda vazou para o resultado", False,
     ci.conferir_juncao(ESQ_ORF, DIR, t(("id", "grupo", "nome"), ("1", "A", "alfa"), ("9", "Z", "")),
                        ["grupo"], "N:1", "interna"))

caso("junção: resultado com chaves e valores inventados (contagem fecha)", False,
     ci.conferir_juncao(ESQ, DIR, t(RES[0], ("9", "Z", "x"), ("9", "Z", "x"), ("9", "Z", "x")), ["grupo"], "N:1"))
caso("junção: troca de valores entre linhas do resultado", False,
     ci.conferir_juncao(ESQ, DIR, t(RES[0], ("1", "A", "beta"), ("2", "A", "alfa"), ("3", "B", "alfa")),
                        ["grupo"], "N:1"))
caso("junção 1:N legítima", True,
     ci.conferir_juncao(t(("grupo", "nome"), ("A", "alfa"), ("B", "beta")), ESQ,
                        t(("grupo", "nome", "id"), ("A", "alfa", "1"), ("A", "alfa", "2"), ("B", "beta", "3")),
                        ["grupo"], "1:N"))
caso("junção: coluna da direita perdida no resultado", False,
     ci.conferir_juncao(ESQ, DIR, t(("id", "grupo"), ("1", "A"), ("2", "A"), ("3", "B")), ["grupo"], "N:1"))

caso("junção 1:1: chave repetida na esquerda", False,
     ci.conferir_juncao(t(("grupo", "id"), ("A", "1"), ("A", "2")), t(("grupo", "nome"), ("A", "alfa")),
                        t(("grupo", "id", "nome"), ("A", "1", "alfa"), ("A", "2", "alfa")), ["grupo"], "1:1"))
orf = [x["detalhe"] for x in ci.conferir_juncao(ESQ_ORF, DIR, t(("id", "grupo", "nome"), ("1", "A", "alfa"),
                                                                ("9", "Z", "")), ["grupo"], "N:1", "esquerda")
       if x["nome"].startswith("órfãs")]
caso("junção: órfãs contadas dos dois lados (esquerda 1, direita 2)", True,
     [ci.item("contagem de órfãs", orf == [{"esquerda": 1, "direita": 2}], orf)])

REORD_ANTES = t(("valor", "grupo", "id"), ("20", "A", "2"), ("10", "A", "1"), ("40", "B", "4"), ("30", "B", "3"))

# ---- agregação
AGG = t(("grupo", "valor"), ("A", "30"), ("B", "70"))
caso("agregação legítima", True, ci.conferir_agregacao(BASE, AGG, ["grupo"], "valor"))
caso("agregação: total perdido", False,
     ci.conferir_agregacao(BASE, t(("grupo", "valor"), ("A", "30"), ("B", "60")), ["grupo"], "valor"))
caso("agregação: grupo repetido no agregado (soma fecha)", False,
     ci.conferir_agregacao(BASE, t(("grupo", "valor"), ("A", "10"), ("A", "20"), ("B", "70")), ["grupo"], "valor"))
caso("agregação: grupo só com vazios sumiu do agregado", False,
     ci.conferir_agregacao(t(("grupo", "valor"), ("A", "10"), ("A", ""), ("C", "")),
                           t(("grupo", "valor"), ("A", "10")), ["grupo"], "valor"))
caso("agregação: ruído de ponto flutuante dentro da tolerância", True,
     ci.conferir_agregacao(t(("grupo", "valor"), ("A", "0.1"), ("A", "0.2")),
                           t(("grupo", "valor"), ("A", "0.30000000000000004")), ["grupo"], "valor",
                           tolerancia=ci.Decimal("0.000001")))
caso("agregação: diferença acima da tolerância", False,
     ci.conferir_agregacao(t(("grupo", "valor"), ("A", "0.1"), ("A", "0.2")),
                           t(("grupo", "valor"), ("A", "0.31")), ["grupo"], "valor",
                           tolerancia=ci.Decimal("0.000001")))
caso("agregação: diferença de 1 em 29 dígitos (contexto padrão arredondaria)", False,
     ci.conferir_agregacao(t(("grupo", "valor"), ("A", "10000000000000000000000000001")),
                           t(("grupo", "valor"), ("A", "10000000000000000000000000000")), ["grupo"], "valor"))
caso("agregação: soma legítima com cancelamento em 29 dígitos", True,
     ci.conferir_agregacao(t(("grupo", "valor"), ("A", "10000000000000000000000000000"), ("A", "1"),
                             ("A", "-10000000000000000000000000000")),
                           t(("grupo", "valor"), ("A", "1")), ["grupo"], "valor"))
caso("agregação: expoente no limite sem estouro", True,
     ci.conferir_agregacao(t(("grupo", "valor"), ("A", "1e10000"), ("A", "1e-10000")),
                           t(("grupo", "valor"), ("A", "1e10000")), ["grupo"], "valor",
                           tolerancia=ci.Decimal("1e-9000")))
caso("agregação: grupo novo de soma zero no agregado", False,
     ci.conferir_agregacao(BASE, t(("grupo", "valor"), ("A", "30"), ("B", "70"), ("Z", "0")), ["grupo"], "valor"))
caso("identidade legítima com --grupo e várias linhas no mesmo grupo", True,
     ci.conferir_identidade(BASE, REORD_ANTES, ["id"], ["grupo"], "valor"))
caso("agregação: troca entre grupos preserva o total", False,
     ci.conferir_agregacao(BASE, t(("grupo", "valor"), ("A", "50"), ("B", "50")), ["grupo"], "valor"))

# ---- deduplicação
DUP = t(CAB, ("1", "A", "10"), ("1", "A", "10"), ("2", "A", "20"), ("3", "B", "30"))
caso("dedup legítima", True, ci.conferir_dedup(DUP, t(CAB, ("1", "A", "10"), ("2", "A", "20"), ("3", "B", "30")),
                                               ["id"]))
caso("dedup: chave repetida depois", False, ci.conferir_dedup(DUP, DUP, ["id"]))
caso("dedup: removeu linha não duplicada", False,
     ci.conferir_dedup(DUP, t(CAB, ("1", "A", "10"), ("2", "A", "20")), ["id"]))
caso("dedup: coluna perdida", False,
     ci.conferir_dedup(DUP, t(("id", "grupo"), ("1", "A"), ("2", "A"), ("3", "B")), ["id"]))
caso("dedup: coluna a mais depois", False,
     ci.conferir_dedup(DUP, t(CAB + ("extra",), ("1", "A", "10", "x"), ("2", "A", "20", "x"), ("3", "B", "30", "x")),
                       ["id"]))
caso("dedup: linha alterada na remoção", False,
     ci.conferir_dedup(DUP, t(CAB, ("1", "A", "10"), ("2", "A", "20"), ("3", "B", "31")), ["id"]))

# ---- identidade (renomear, reordenar)
REORD = t(("valor", "grupo", "id"), ("40", "B", "4"), ("10", "A", "1"), ("30", "B", "3"), ("20", "A", "2"))
caso("identidade legítima (colunas e linhas reordenadas)", True, ci.conferir_identidade(BASE, REORD, ["id"]))
caso("identidade legítima com renomeação", True,
     ci.conferir_identidade(BASE, t(("id", "classe", "valor"), *[tuple(r.values()) for r in BASE[1]]),
                            renomear={"grupo": "classe"}))
caso("identidade: troca de valores preserva contagem e soma, chave reprova", False,
     ci.conferir_identidade(BASE, TROCA, ["id"]))
caso("identidade: troca de valores, multiconjunto reprova sem chave", False, ci.conferir_identidade(BASE, TROCA))
caso("identidade: troca de valores, soma por grupo reprova (item isolado)", False,
     [x for x in ci.conferir_identidade(BASE, TROCA, grupo=["grupo"], medida="valor")
      if x["nome"] == "soma por grupo preservada"])
caso("identidade: coluna a mais depois", False,
     [x for x in ci.conferir_identidade(BASE, t(CAB + ("extra",), *[tuple(r.values()) + ("x",) for r in BASE[1]]),
                                        ["id"]) if x["nome"] == "mesmas colunas"])
caso("identidade: linha perdida", False, ci.conferir_identidade(BASE, t(CAB, *[tuple(r.values())
                                                                               for r in BASE[1][:3]])))

# ---- limite declarado: soma por grupo não vê troca no mesmo grupo; a chave vê
so_soma = [x for x in ci.conferir_identidade(BASE, TROCA_MESMO_GRUPO, grupo=["grupo"], medida="valor")
           if x["nome"].startswith("soma")]
caso("limite: soma por grupo NÃO vê troca no mesmo grupo", True, so_soma)
caso("limite: chave vê troca no mesmo grupo", False, ci.conferir_identidade(BASE, TROCA_MESMO_GRUPO, ["id"]))

# ---- contagem e soma sozinhas não bastam (prova da premissa)
cs = [x for x in ci.conferir_identidade(BASE, TROCA, medida="valor") if x["nome"] in
      ("contagem igual", "soma total preservada")]
caso("premissa: contagem e soma passam na troca de valores", True, cs)


# ---- linha de comando: 0 PASSA, 1 REPROVA, 2 erro de uso
def cli(*args):
    try:
        p = subprocess.run([sys.executable, os.path.join(AQUI, "conferir_invariante.py"), *args],
                           capture_output=True, text=True, encoding="utf-8", timeout=30)
    except subprocess.TimeoutExpired:
        return "travou (30 s)", "{}"
    return p.returncode, p.stdout


falhas_cli = []
with tempfile.TemporaryDirectory() as d:
    def grava(nome, tab):
        caminho = os.path.join(d, nome)
        with open(caminho, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(tab[0])
            w.writerows([[r[c] for c in tab[0]] for r in tab[1]])
        return caminho
    a, b, c = grava("a.csv", BASE), grava("b.csv", REORD), grava("c.csv", TROCA)
    for args, esperado in ((("identidade", "--antes", a, "--depois", b, "--chave", "id", "--sep", ";"), 0),
                           (("identidade", "--antes", a, "--depois", c, "--chave", "id", "--sep", ";"), 1),
                           (("identidade", "--antes", a, "--depois", c, "--chave", "inexistente", "--sep", ";"), 2),
                           (("dedup", "--antes", a, "--sep", ";"), 2)):
        rc, out = cli(*args)
        try:
            json.loads(out)
        except ValueError:
            falhas_cli.append(f"saída não é JSON: {args[0]} rc={rc}")
        if rc != esperado:
            falhas_cli.append(f"{args[0]} {args[-3:]}: exit {rc}, esperado {esperado}")
    ruins = {"cab_rep.csv": "id,valor,valor\n1,10,20\n", "campos.csv": "id,valor\n1,10,99\n",
             "sem_nome.csv": "id,\n1,10\n"}
    for nome, texto in ruins.items():
        with open(os.path.join(d, nome), "w", encoding="utf-8") as f:
            f.write(texto)
        rc, out = cli("identidade", "--antes", os.path.join(d, nome), "--depois", os.path.join(d, nome))
        if rc != 2:
            falhas_cli.append(f"CSV malformado {nome}: exit {rc}, esperado 2")
    for args in (("agregacao", "--antes", a, "--depois", a, "--grupo", ",", "--medida", "valor", "--sep", ";"),
                 ("agregacao", "--antes", grava("inf.csv", t(("g", "v"), ("A", "Infinity"))),
                  "--depois", grava("inf2.csv", t(("g", "v"), ("A", "Infinity"))), "--grupo", "g", "--medida", "v",
                  "--sep", ";"),
                 ("agregacao", "--antes", grava("exp.csv", t(("g", "v"), ("A", "1e999999999"), ("A", "1"))),
                  "--depois", grava("exp2.csv", t(("g", "v"), ("A", "1e999999999"))), "--grupo", "g",
                  "--medida", "v", "--sep", ";"),
                 ("identidade", "--antes", grava("dupk.csv", t(CAB, ("1", "A", "10"), ("1", "A", "11"))),
                  "--depois", grava("dupk2.csv", t(CAB, ("1", "A", "10"), ("1", "A", "12"))), "--chave", "id",
                  "--sep", ";"),
                 ("juncao", "--esquerda", grava("col1.csv", t(("k", "n"), ("1", "a"))),
                  "--direita", grava("col2.csv", t(("k", "n"), ("1", "b"))),
                  "--resultado", grava("col3.csv", t(("k", "n"), ("1", "a"))), "--chave", "k",
                  "--cardinalidade", "1:1", "--sep", ";"),
                 ("agregacao", "--antes", grava("nan.csv", t(("g", "v"), ("A", "NaN"))),
                  "--depois", grava("nan2.csv", t(("g", "v"), ("A", "NaN"))), "--grupo", "g", "--medida", "v",
                  "--sep", ";"),
                 ("agregacao", "--antes", a, "--depois", a, "--grupo", "grupo", "--medida", "valor",
                  "--tolerancia", "-1", "--sep", ";"),
                 ("identidade", "--antes", a, "--depois", a, "--grupo", "inexistente", "--sep", ";"),
                 ("filtro", "--antes", a, "--depois", a, "--excluidas", a, "--chave", "id", "--sep", ";"),
                 ("identidade", "--antes", a, "--depois", a, "--chave", " , ", "--sep", ";")):
        rc, out = cli(*args)
        if rc != 2:
            falhas_cli.append(f"opção inválida {args[0]} {args[-4:-2]}: exit {rc}, esperado 2")
    rc, out = cli("agregacao", "--antes", grava("v.csv", t(("g", "v"), ("A", "1.234,50"), ("A", "0,50"))),
                  "--depois", grava("w.csv", t(("g", "v"), ("A", "1.235,00"))), "--grupo", "g", "--medida", "v",
                  "--sep", ";", "--decimal", "virgula")
    if rc != 0:
        falhas_cli.append(f"decimal com vírgula: exit {rc}, esperado 0")
    fl = (grava("fl.csv", t(("g", "v"), ("A", "0.1"), ("A", "0.2"))),
          grava("fl2.csv", t(("g", "v"), ("A", "0.30000000000000004"))))
    for op, tol_, esperado in (("agregacao", "0.000001", 0), ("agregacao", None, 1)):
        args = [op, "--antes", fl[0], "--depois", fl[1], "--grupo", "g", "--medida", "v", "--sep", ";"]
        rc, out = cli(*(args + (["--tolerancia", tol_] if tol_ else [])))
        if rc != esperado:
            falhas_cli.append(f"--tolerancia {tol_}: exit {rc}, esperado {esperado}")
    rc, out = cli("agregacao", "--antes", fl[0], "--depois", fl[1], "--grupo", "g", "--medida", "v", "--sep", ";",
                  "--tolerancia", "abc")
    if rc != 2 or "--tolerancia" not in out:
        falhas_cli.append(f"--tolerancia abc: exit {rc}, esperado 2 com mensagem da tolerância")

erros = [f"{n}: esperado {'PASSA' if e else 'REPROVA'}, obtido {'PASSA' if o else 'REPROVA'} {v}"
         for n, e, o, v in casos if e != o] + falhas_cli
print(f"casos: {len(casos)} + CLI 21 · falhas: {len(erros)}")
for e in erros:
    print("FAIL", e)
print("RESULTADO:", "PASS" if not erros else "FAIL")
sys.exit(0 if not erros else 1)
