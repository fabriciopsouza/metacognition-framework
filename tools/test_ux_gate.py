#!/usr/bin/env python3
"""Canário do gate de UX por medida (`tools/ux_gate.py`, skill ux-design).

  (a) retrato limpo passa nas duas larguras;
  (b) cada medida, quebrada isoladamente, gera o achado dela: rolagem, palavras por tipo, caracteres por linha,
      acao sem controle e irmaos quase alinhados;
  (c) bordas iguais ou bem distintas (recuo intencional) e irmaos lado a lado nao sao desalinhamento;
  (d) limites calibrados pelo dono valem em todos os perfis (legenda 8, cabecalho 2); perfil desconhecido e retrato
      malformado sao erro;
  (e) a linha de comando sai 0, 1 e 2 conforme o caso, inclusive com falha do Playwright;
  (f) a funcao `centrado` do EXTRATOR, executada no Node, separa caixa centralizada de bloco de largura total em pai
      com padding (sem Node: SKIP declarado na saida);
  (g) tamanho igual entre irmaos do mesmo tipo: item de grid (largura na mesma posicao de trilhas, altura so lado a
      lado), item de flex (so altura) e grafico de cada cartao (largura e altura), nas bordas de 2 px (passa) e 3 px
      (acusa); chip de flex com largura do conteudo, item que ocupa outras trilhas, icone, grafico sem classe, fora de
      arranjo, outra classe, primo sem pai repetido e texto de cartoes diferentes nao sao comparados; elemento sem os campos novos e erro;
  (h) as funcoes `arranjo`, `trilhas` e `classe` do EXTRATOR, executadas no Node (sem Node: SKIP declarado).

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


def el(i, tipo, texto, topo, esquerda=16, linhas=1, pai=0, altura=20, clicavel=False, tag="div", classe="",
       arranjo="", largura=300, trilhas="auto/auto"):
    return {"id": i, "pai": pai, "tipo": tipo, "texto": texto, "linhas": linhas, "esquerda": esquerda,
            "topo": topo, "largura": largura, "altura": altura, "clicavel_sem_controle": clicavel, "coluna": True,
            "tag": tag, "classe": classe, "arranjo": arranjo,
            "trilhas": trilhas}


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
        "controle com 3 palavras": lambda t: t["elementos"][2].update(texto="Salvar todas alteracoes"),
        "titulo com 5 palavras": lambda t: t["elementos"][0].update(texto="Um dois tres quatro cinco"),
        "legenda com 9 palavras": lambda t: t["elementos"][3].update(texto=" ".join(["p"] * 9)),
        "caracteres por linha": lambda t: t["elementos"][1].update(texto="x" * 162, linhas=2),
        "acao sem controle": lambda t: t["elementos"][1].update(clicavel_sem_controle=True),
        "irmaos desalinhados": lambda t: t["elementos"][2].update(esquerda=21),
    }
    trecho = {"rolagem horizontal": "rolagem", "controle com 3 palavras": "controle com 3",
              "titulo com 5 palavras": "titulo com 5", "legenda com 9 palavras": "legenda com 9",
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
    r["1280"]["elementos"][0]["texto"] = "Um dois tres quatro"
    r["1280"]["elementos"][3]["texto"] = " ".join(["p"] * 8)
    r["1280"]["elementos"].append(el(5, "cabecalho", "Valor total", 120))
    checar("(b) exatamente 2, 4 e 8 palavras (controle e cabecalho, titulo, legenda) passam", achados(r) == [])


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
    # Cada perfil da lista do dono existe e aplica os 4 limites: um acima do limite em cada tipo = 4 achados.
    r = limpo()
    acima = r["360"]["elementos"]
    acima[0]["texto"] = "Um dois tres quatro cinco"
    acima[2]["texto"] = "Salvar todas alteracoes"
    acima[3]["texto"] = " ".join(["p"] * 9)
    acima.append(el(5, "cabecalho", "Valor total liquido", 120))
    borda = limpo()  # exatamente no limite em cada tipo: nenhum achado
    borda["360"]["elementos"][0]["texto"] = "Um dois tres quatro"
    borda["360"]["elementos"][3]["texto"] = " ".join(["p"] * 8)
    borda["360"]["elementos"].append(el(5, "cabecalho", "Valor total", 120))
    dono = ("corporativo", "corporativo-2", "minimalista", "moderno", "arrojado", "outro")
    checar(f"(d) perfis iguais a lista do dono: {ux_gate.PERFIS}", tuple(ux_gate.PERFIS) == dono)
    for perfil in dono:
        try:
            tipos = sorted(a.split(": ")[1].split(" com ")[0] for a in achados(r, perfil))
            checar(f"(d) {perfil} aplica os 4 limites: {tipos}", tipos == ["cabecalho", "controle", "legenda", "titulo"])
            checar(f"(d) {perfil} aceita o limite exato", achados(borda, perfil) == [])
        except ValueError as erro:
            checar(f"(d) {perfil} aceito: {erro}", False)
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


def painel(larguras=(300, 300, 300), alturas=(200, 200, 200), topos=(0, 0, 0), graficos=((280, 120),) * 3):
    """Grade (id 10) com cartoes lado a lado; cada cartao tem uma area (div.area) com o grafico (svg.spark)."""
    elementos = [el(10, "outro", "", 0, pai=0, largura=960, altura=400, classe="grade")]
    for n, (lg, al, tp, (gl, ga)) in enumerate(zip(larguras, alturas, topos, graficos)):
        c, a, g = 100 + n * 10, 101 + n * 10, 102 + n * 10
        elementos += [el(c, "outro", f"Cartao {n}", tp, pai=10, largura=lg, altura=al, classe="cartao", arranjo="grade",
                         esquerda=16 + n * 320),
                      el(a, "outro", "", tp + 60, pai=c, largura=gl, altura=ga, classe="area"),
                      el(g, "outro", "", tp + 60, pai=a, largura=gl, altura=ga, tag="svg", classe="spark")]
    tela = {"rolagem": False, "elementos": elementos}
    return {"360": copy.deepcopy(tela), "1280": tela}


def test_tamanho_igual():
    checar(f"(g) painel limpo: {achados(painel())}", achados(painel()) == [])
    for nome, kw, trecho in (
            ("cartao 3px mais largo", {"larguras": (300, 303, 300)}, "div.cartao com largura diferente em 3.0px"),
            ("cartao lado a lado 3px mais alto", {"alturas": (200, 203, 200)}, "div.cartao com altura diferente em 3.0px"),
            ("grafico 3px mais largo", {"graficos": ((280, 120), (283, 120), (280, 120))},
             "svg.spark com largura diferente em 3.0px"),
            ("grafico em outra linha 3px mais alto", {"topos": (0, 0, 220), "graficos": ((280, 120),) * 2 + ((280, 123),)},
             "svg.spark com altura diferente em 3.0px")):
        a = [x for x in achados(painel(**kw)) if x.startswith("1280px")]
        alvo = [x for x in a if trecho in x]
        checar(f"(g) {nome}: {a}", len(alvo) == 1)
    for nome, kw in (("2px de largura passa", {"larguras": (300, 302, 300)}),
                     ("2px de altura passa", {"alturas": (200, 202, 200)}),
                     ("grafico com 2px passa", {"graficos": ((280, 120), (282, 122), (280, 120))}),
                     ("cartao empilhado mais alto passa", {"topos": (0, 0, 220), "alturas": (200, 200, 260)})):
        checar(f"(g) {nome}: {achados(painel(**kw))}", achados(painel(**kw)) == [])
    r = painel(larguras=(300, 340, 300))
    for e in r["360"]["elementos"] + r["1280"]["elementos"]:
        e["arranjo"] = ""  # lista comum (pai sem grid nem flex): nao comparados
    checar(f"(g) fora de arranjo: {achados(r)}", [x for x in achados(r) if "cartao" in x] == [])
    r = painel(larguras=(300, 340, 300))
    for e in r["360"]["elementos"] + r["1280"]["elementos"]:
        if e["arranjo"]:
            e["arranjo"] = "flex"  # chip ou link em flex: largura do conteudo, nao comparada
    checar(f"(g) flex compara so altura (largura): {achados(r)}", [x for x in achados(r) if "cartao" in x] == [])
    r = painel(alturas=(200, 203, 200))
    for e in r["1280"]["elementos"]:
        if e["arranjo"]:
            e["arranjo"] = "flex"
    a = [x for x in achados(r) if x.startswith("1280px")]
    checar(f"(g) flex compara altura lado a lado: {a}", len(a) == 1 and "altura diferente em 3.0px" in a[0])
    r = painel(larguras=(300, 620, 300))
    r["1280"]["elementos"][4]["trilhas"] = "auto/span 2"  # cartao que ocupa duas trilhas: outro grupo de largura
    checar(f"(g) outra posicao de trilhas: {achados(r)}", [x for x in achados(r) if x.startswith("1280px")] == [])
    for nome, mudar in (("icone abaixo de 60px", {"graficos": ((16, 16), (24, 24), (20, 20))}),):
        checar(f"(g) {nome}: {achados(painel(**mudar))}", achados(painel(**mudar)) == [])
    r = painel()
    for tela in r.values():  # cada cartao e flex em coluna com um p.txt de altura propria: primos, nao irmaos
        tela["elementos"] += [el(103 + n * 10, "paragrafo", "Nota", 30, pai=100 + n * 10, classe="txt", arranjo="flex",
                                 altura=20 * (n + 1)) for n in range(3)]
    checar(f"(g) texto de cartoes diferentes nao e comparado: {achados(r)}", achados(r) == [])
    r = painel(larguras=(300, 303, 300))
    for e in r["1280"]["elementos"]:
        if e["arranjo"]:
            e["pai"] = 10 + e["id"]  # cartoes em pais diferentes: nao sao irmaos
    checar(f"(g) item de grade de outro pai: {achados(r)}", [x for x in achados(r) if x.startswith("1280px")] == [])
    r = painel(alturas=(200, 260, 200))
    for tela in r.values():
        for e in tela["elementos"]:
            e["arranjo"] = ""  # lado a lado sem grid nem flex (float, inline-block): altura nao comparada
    checar(f"(g) lado a lado fora de arranjo: {achados(r)}", achados(r) == [])
    r = painel()
    for tela in r.values():  # segunda grade irma da primeira: os cartoes dela sao primos, nao irmaos
        tela["elementos"] += [el(20, "outro", "", 420, pai=0, largura=960, altura=200, classe="grade"),
                              el(200, "outro", "Cartao 9", 420, pai=20, largura=340, altura=260, classe="cartao",
                                 arranjo="grade")]
    checar(f"(g) cartao de outra grade: {achados(r)}", achados(r) == [])
    r = painel(graficos=((59, 40), (40, 40), (50, 40)))
    checar(f"(g) grafico de 59px e icone: {achados(r)}", achados(r) == [])
    r = painel(graficos=((60, 40), (57, 40), (60, 40)))
    checar(f"(g) grafico de 60px e medido: {achados(r)}", len([x for x in achados(r) if x.startswith("1280px")]) == 1)
    r = painel(graficos=((280, 120), (300, 140), (280, 120)))
    for e in r["360"]["elementos"] + r["1280"]["elementos"]:
        if e["tag"] == "svg":
            e["classe"] = ""  # svg sem classe: icone, nao comparado
    checar(f"(g) svg sem classe: {achados(r)}", achados(r) == [])
    r = painel(graficos=((280, 120), (300, 140), (280, 120)))
    r["1280"]["elementos"][6]["classe"] = "barra"  # o grafico do 2o cartao e de outro tipo
    checar(f"(g) outra classe: {achados(r)}", [x for x in achados(r) if x.startswith("1280px")] == [])
    r = painel(graficos=((280, 120), (300, 140), (280, 120)))
    r["1280"]["elementos"][6]["tag"] = "canvas"  # mesma classe, outra tag: outro tipo
    checar(f"(g) outra tag: {achados(r)}", [x for x in achados(r) if x.startswith("1280px")] == [])
    r = painel(larguras=(300, 303), alturas=(200, 200), topos=(0, 0))  # dois cartoes bastam para comparar
    checar(f"(g) dois cartoes: {achados(r)}", len([x for x in achados(r) if x.startswith("1280px")]) == 1)
    tela = {"rolagem": False, "elementos": [  # dois graficos em pais unicos e diferentes: nao sao primos
        el(1, "outro", "", 0, classe="topo"), el(2, "outro", "", 0, pai=1, tag="svg", classe="spark", largura=100),
        el(3, "outro", "", 300, classe="rodape"), el(4, "outro", "", 300, pai=3, tag="svg", classe="spark", largura=200)]}
    checar("(g) primo sem pai repetido", achados({"360": tela, "1280": copy.deepcopy(tela)}) == [])
    for campo in ("tag", "classe", "arranjo", "trilhas"):
        r = painel()
        del r["360"]["elementos"][0][campo]
        try:
            achados(r)
            checar(f"(g) sem {campo} devia ser erro", False)
        except ValueError:
            pass


GRADE_JS = r"""
const src = require('fs').readFileSync(process.argv[2], 'utf8');
const arranjo = eval(src.match(/const arranjo = (el => \{[\s\S]*?\n  \});/)[1]);
const trilhas = eval(src.match(/const trilhas = (el => \{.*?\});/)[1]);
const classe = eval(src.match(/const classe = (el => .*?);  \/\//)[1]);
let estilo = {};
global.getComputedStyle = () => estilo;
const filho = {parentElement: {}};
const casos = [['grid', 'grid', 'grade'], ['inline-grid', 'inline-grid', 'grade'], ['flex', 'flex', 'flex'],
  ['inline-flex', 'inline-flex', 'flex'], ['bloco', 'block', '']];
for (const [nome, d, esperado] of casos) { estilo = {display: d}; if (arranjo(filho) !== esperado) console.log('FALHOU arranjo ' + nome); }
if (arranjo({parentElement: null}) !== '') console.log('FALHOU arranjo sem pai');
estilo = {gridColumnStart: 'auto', gridColumnEnd: 'span 2'};
if (trilhas({}) !== 'auto/span 2') console.log('FALHOU trilhas');
const comClasse = c => ({getAttribute: () => c});
for (const [c, esperado] of [['  spark bom ', 'spark'], ['spark ruim', 'spark'], ['', ''], [null, '']])
  if (classe(comClasse(c)) !== esperado) console.log('FALHOU classe ' + JSON.stringify(c));
"""


def test_grade_classe_js():
    node = shutil.which("node")
    if not node:
        print("SKIP (h) arranjo, trilhas e classe no Node: node ausente")
        return
    with tempfile.TemporaryDirectory() as pasta:
        script = os.path.join(pasta, "grade.js")
        with open(script, "w", encoding="utf-8") as f:
            f.write(GRADE_JS)
        r = subprocess.run([node, script, os.path.join(ROOT, "tools", "ux_gate.py")], capture_output=True, text=True,
                           timeout=60)
    checar(f"(h) arranjo, trilhas e classe no Node: rc {r.returncode} {r.stdout}{r.stderr}", r.returncode == 0 and not r.stdout)


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
  ['centralizada com padding assimetrico', {paddingLeft: '40px', paddingRight: '0px'}, pai(0, 400),
   {left: 70, right: 370, width: 300}, true],
  ['filho mais largo que o conteudo', p16, pai(0, 400), {left: 0, right: 400, width: 400}, false],
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
