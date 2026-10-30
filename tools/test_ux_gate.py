#!/usr/bin/env python3
"""Canário do gate de UX por medida (`tools/ux_gate.py`, skill ux-design).

  (a) retrato limpo passa nas duas larguras;
  (b) cada medida, quebrada isoladamente, gera o achado dela: rolagem, palavras por tipo, caracteres por linha,
      acao sem controle e irmaos quase alinhados;
  (c) bordas iguais ou bem distintas (recuo intencional) e irmaos lado a lado nao sao desalinhamento;
  (d) o perfil minimalista aperta a legenda para 8 palavras; perfil desconhecido e retrato malformado sao erro;
  (e) a linha de comando sai 0, 1 e 2 conforme o caso, inclusive com falha do Playwright;
  (f) a funcao `centrado` do EXTRATOR, executada no Node, separa caixa centralizada de bloco de largura total em pai
      com padding (sem Node: SKIP declarado na saida).

Uso: python tools/test_ux_gate.py   (exit 0 PASS; 1 FAIL)
"""
import contextlib
import copy
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import ux_gate  # noqa: E402

FALHAS = []


def el(i, tipo, texto, topo, esquerda=16, linhas=1, pai=0, altura=20, clicavel=False):
    return {"id": i, "pai": pai, "tipo": tipo, "texto": texto, "linhas": linhas, "esquerda": esquerda,
            "topo": topo, "largura": 300, "altura": altura, "clicavel_sem_controle": clicavel, "coluna": True}


def limpo():
    tela = {"rolagem": False, "elementos": [
        el(1, "titulo", "Vendas do mes", 0),
        el(2, "paragrafo", "Texto curto de leitura.", 30),
        el(3, "controle", "Salvar alteracoes", 60),
        el(4, "legenda", "Fonte: sistema interno, atualizado hoje", 90),
    ]}
    return {"360": tela, "1280": copy.deepcopy(tela)}


def checar(nome, cond):
    if not cond:
        FALHAS.append(nome)


def achados(retrato, perfil="corporativo"):
    return ux_gate.avaliar(retrato, perfil)


def test_limpo_passa():
    checar("(a) limpo", achados(limpo()) == [])


def test_cada_medida_acusa():
    casos = {
        "rolagem horizontal": lambda t: t.update(rolagem=True),
        "controle com 4 palavras": lambda t: t["elementos"][2].update(texto="Salvar todas as alteracoes"),
        "titulo com 7 palavras": lambda t: t["elementos"][0].update(texto="Um dois tres quatro cinco seis sete"),
        "legenda com 13 palavras": lambda t: t["elementos"][3].update(texto=" ".join(["p"] * 13)),
        "caracteres por linha": lambda t: t["elementos"][1].update(texto="x" * 162, linhas=2),
        "acao sem controle": lambda t: t["elementos"][1].update(clicavel_sem_controle=True),
        "irmaos desalinhados": lambda t: t["elementos"][2].update(esquerda=21),
    }
    trecho = {"rolagem horizontal": "rolagem", "controle com 4 palavras": "controle com 4",
              "titulo com 7 palavras": "titulo com 7", "legenda com 13 palavras": "legenda com 13",
              "caracteres por linha": "81 caracteres", "acao sem controle": "acao sem controle",
              "irmaos desalinhados": "desalinhados em 5.0px"}
    for nome, quebra in casos.items():
        r = limpo()
        quebra(r["1280"])
        a = achados(r)
        n = 2 if nome == "irmaos desalinhados" else 1  # o do meio fica desalinhado com os dois vizinhos
        checar(f"(b) {nome}: {a}", len(a) == n and all(trecho[nome] in x and x.startswith("1280px") for x in a))
    r = limpo()
    r["1280"]["elementos"][1].update(texto="x" * 160, linhas=2)
    checar("(b) exatamente 80 por linha passa", achados(r) == [])
    r = limpo()
    r["1280"]["elementos"][2]["texto"] = "Salvar todas alteracoes"
    checar("(b) exatamente 3 palavras no controle passa", achados(r) == [])


def test_alinhamento_sem_falso_positivo():
    for nome, esquerda in (("borda igual", 16), ("desvio de 2px", 18), ("recuo de 16px", 32), ("recuo intencional", 40)):
        r = limpo()
        r["360"]["elementos"][2]["esquerda"] = esquerda
        checar(f"(c) {nome}", achados(r) == [])
    r = limpo()
    r["360"]["elementos"][2].update(esquerda=21, topo=30)  # lado a lado com o paragrafo: nao e coluna
    r["360"]["elementos"][3]["esquerda"] = 21  # a legenda abaixo segue a coluna do botao
    checar("(c) lado a lado", achados(r) == [])
    r = limpo()
    r["360"]["elementos"][2].update(esquerda=21, pai=9)  # outro pai: nao e irmao
    checar("(c) outro pai", achados(r) == [])
    r = limpo()
    r["360"]["elementos"][2].update(esquerda=21, coluna=False)  # centralizado ou inline: nao e coluna esquerda
    checar("(c) centralizado ou inline", achados(r) == [])


def test_perfis_e_malformado():
    r = limpo()
    r["360"]["elementos"][3]["texto"] = " ".join(["p"] * 9)
    checar("(d) corporativo aceita 9", achados(r) == [])
    checar("(d) minimalista recusa 9", len(achados(r, "minimalista")) == 1)
    for nome, retrato, perfil in (("perfil desconhecido", limpo(), "neon"),
                                  ("sem 1280", {"360": limpo()["360"]}, "corporativo"),
                                  ("rolagem nao booleana", {**limpo(), "360": {"rolagem": 1, "elementos": []}},
                                   "corporativo")):
        try:
            achados(retrato, perfil)
            checar(f"(d) {nome} devia ser erro", False)
        except ValueError:
            pass
    for nome, retrato in (("retrato lista", []), ("elemento nao objeto", {**limpo(), "360": {"rolagem": False,
                          "elementos": [5]}}), ("texto numero", {**limpo(), "360": {"rolagem": False,
                          "elementos": [{**el(1, "titulo", "x", 0), "texto": 5}]}})):
        try:
            achados(retrato)
            checar(f"(d) {nome} devia ser erro", False)
        except ValueError:
            pass
    r = limpo()
    r["360"]["elementos"][1]["linhas"] = 0
    try:
        achados(r)
        checar("(d) linhas 0 devia ser erro", False)
    except ValueError:
        pass


def test_linha_de_comando():
    with tempfile.TemporaryDirectory() as pasta:
        bom, ruim = os.path.join(pasta, "bom.json"), os.path.join(pasta, "ruim.json")
        with open(bom, "w", encoding="utf-8") as f:
            json.dump(limpo(), f)
        r = limpo()
        r["360"]["rolagem"] = True
        with open(ruim, "w", encoding="utf-8") as f:
            json.dump(r, f)
        for nome, argv, esperado in (("limpo", ["--retrato", bom], 0), ("com achado", ["--retrato", ruim], 1),
                                     ("arquivo ausente", ["--retrato", os.path.join(pasta, "x.json")], 2),
                                     ("sem fonte", [], 2), ("perfil ruim", ["--retrato", bom, "--perfil", "neon"], 2)):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                codigo = ux_gate.main(argv)
            checar(f"(e) {nome}: {codigo}", codigo == esperado)
        salvo = os.path.join(pasta, "salvo.json")
        original = ux_gate.extrair
        ux_gate.extrair = lambda url: limpo()  # sem navegador: o caminho --url usa o extrator substituido
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                codigo = ux_gate.main(["--url", "http://exemplo.invalid", "--salvar", salvo])
        finally:
            ux_gate.extrair = original
        checar(f"(e) --url com --salvar: {codigo}", codigo == 0 and os.path.exists(salvo))
        if os.path.exists(salvo):
            with open(salvo, encoding="utf-8") as f:
                checar("(e) retrato salvo", json.load(f) == limpo())
    # Falha do Playwright (navegador ausente, URL fora do ar) = gate nao executado (2), nunca achado (1).
    falso = types.ModuleType("playwright.sync_api")

    class Erro(Exception):
        pass

    def sync_playwright():
        raise Erro("navegador ausente")

    falso.Error, falso.sync_playwright = Erro, sync_playwright
    antes = {k: sys.modules.get(k) for k in ("playwright", "playwright.sync_api")}
    sys.modules["playwright"], sys.modules["playwright.sync_api"] = types.ModuleType("playwright"), falso
    try:
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            codigo = ux_gate.main(["--url", "http://exemplo.invalid"])
    finally:
        for k, v in antes.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    checar(f"(e) falha do Playwright sai 2: {codigo}", codigo == 2
           and saida.getvalue().startswith("ERRO: Playwright falhou"))


CENTRADO_JS = r"""
const src = require('fs').readFileSync(process.argv[2], 'utf8');
const corpo = src.match(/const centrado = (\(el, b\) => \{[\s\S]*?\n  \});/)[1];
const px = v => parseFloat(v) || 0;
let estilo = {};
global.getComputedStyle = () => estilo;
const centrado = eval(corpo);
const pai = (l, r) => ({parentElement: {getBoundingClientRect: () => ({left: l, right: r})}});
const p16 = {paddingLeft: '16px', paddingRight: '16px'};
const casos = [
  ['largura total em pai com padding', p16, pai(0, 400), {left: 16, right: 384, width: 368}, false],
  ['caixa centralizada', p16, pai(0, 400), {left: 50, right: 350, width: 300}, true],
  ['caixa estreita a esquerda', p16, pai(0, 400), {left: 16, right: 316, width: 300}, false],
  ['centralizada com borda', {borderLeftWidth: '2px', borderRightWidth: '2px'}, pai(0, 404),
   {left: 52, right: 352, width: 300}, true],
];
for (const [nome, est, el, b, esperado] of casos) {
  estilo = est;
  if (centrado(el, b) !== esperado) console.log('FALHOU ' + nome);
}
"""


def test_centrado_js():
    node = shutil.which("node")
    if not node:
        print("SKIP (f) centrado no Node: node ausente")
        return
    with tempfile.TemporaryDirectory() as pasta:
        script = os.path.join(pasta, "centrado.js")
        with open(script, "w", encoding="utf-8") as f:
            f.write(CENTRADO_JS)
        r = subprocess.run([node, script, os.path.join(ROOT, "tools", "ux_gate.py")], capture_output=True, text=True,
                           timeout=60)
    checar(f"(f) centrado no Node: rc {r.returncode} {r.stdout}{r.stderr}", r.returncode == 0 and not r.stdout)


if __name__ == "__main__":
    for nome, funcao in list(globals().items()):
        if nome.startswith("test_") and callable(funcao):
            funcao()
    for falha in FALHAS:
        print("FAIL", falha)
    print("PASS" if not FALHAS else f"FAIL ({len(FALHAS)})")
    sys.exit(1 if FALHAS else 0)
