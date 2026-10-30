#!/usr/bin/env python3
"""Gate de UX por medida (skill ux-design, camada 3): as medidas que as ferramentas prontas nao cobrem.

Mede, numa pagina renderizada em 360 px e 1280 px: caracteres por linha de paragrafo, desalinhamento de irmaos na
mesma coluna, rolagem horizontal, palavras por elemento e acao sem controle (`div` clicavel). Contraste, alvo e
rotulos ficam com axe-core ou AccessLint; tracos de "cara de IA", com `impeccable detect` (roteiro na skill).

Uso:
  python tools/ux_gate.py --url URL [--perfil P]       extrai o retrato com Playwright (precisa estar instalado)
  python tools/ux_gate.py --retrato ARQ.json [--perfil P]  avalia um retrato salvo
  python tools/ux_gate.py --url URL --salvar ARQ.json  extrai e salva o retrato
Saida: 0 nenhum achado; 1 ha achado (uma linha por achado); 2 erro (uso, arquivo, Playwright ausente).
Excecao: elemento (ou ancestral) com o atributo `data-ux-ignore` nao e medido; declarar o motivo no DESIGN.md.
"""
import argparse
import json
import sys

LARGURAS = (360, 1280)
MAX_CARACTERES_LINHA = 80
DESVIO_ALINHAMENTO_PX = 2
# Acima disso a diferenca e intencional (recuo, outra coluna), nao quase-alinhamento. INFERIDO; calibrar no DESIGN.md.
QUASE_ALINHADO_PX = 16
LIMITE_PALAVRAS = {"controle": 3, "cabecalho": 3, "titulo": 6, "legenda": 12}  # titulo e legenda: INFERIDO
PERFIS = {"corporativo": {}, "minimalista": {"legenda": 8}, "moderno": {}, "arrojado": {}, "outro": {}}

# Executado no navegador: um registro por elemento medido. `tipo` decide a regra de palavras.
EXTRATOR = r"""
() => {
  const ign = el => el.closest('[data-ux-ignore]') !== null;
  const tipo = el => {
    const t = el.tagName.toLowerCase(), r = el.getAttribute('role');
    if (['button', 'option', 'summary'].includes(t) || ['button', 'tab', 'option', 'menuitem'].includes(r)) return 'controle';
    if (t === 'input' && ['button', 'submit', 'reset'].includes(el.type)) return 'controle';
    if (t === 'th') return 'cabecalho';
    if (['h1', 'h2', 'h3'].includes(t)) return 'titulo';
    if (['figcaption', 'caption', 'small', 'legend'].includes(t)) return 'legenda';
    if (t === 'p') return 'paragrafo';
    return 'outro';
  };
  const linhas = el => {
    const rg = document.createRange(); rg.selectNodeContents(el);
    return new Set([...rg.getClientRects()].map(r => Math.round(r.top))).size || 1;
  };
  const interativo = 'a,button,input,select,textarea,summary,[role],[tabindex]';
  const out = [], todos = [...document.querySelectorAll('body *')], indice = new Map(todos.map((e, i) => [e, i]));
  todos.forEach((el, i) => {
    if (ign(el)) return;
    const b = el.getBoundingClientRect();
    if (b.width === 0 || b.height === 0) return;
    const clicavel = (el.hasAttribute('onclick') || typeof el.onclick === 'function')
      && !el.matches(interativo) && !el.closest('a,button');
    const t = tipo(el);
    out.push({id: i, pai: indice.has(el.parentElement) ? indice.get(el.parentElement) : -1,
      tipo: t, texto: (el.innerText || el.value || '').trim(), linhas: t === 'paragrafo' ? linhas(el) : 1,
      esquerda: b.left, topo: b.top, largura: b.width, altura: b.height, clicavel_sem_controle: clicavel});
  });
  return {rolagem: document.documentElement.scrollWidth > document.documentElement.clientWidth, elementos: out};
}
"""


def limites(perfil):
    if perfil not in PERFIS:
        raise ValueError(f"perfil desconhecido: {perfil} (validos: {', '.join(PERFIS)})")
    return {**LIMITE_PALAVRAS, **PERFIS[perfil]}


def avaliar(retrato, perfil="corporativo"):
    """Achados (lista de textos) de um retrato {largura: {rolagem, elementos}}; ValueError se malformado."""
    lim = limites(perfil)
    achados = []
    for largura in LARGURAS:
        tela = retrato.get(str(largura))
        if type(tela) is not dict or type(tela.get("rolagem")) is not bool or type(tela.get("elementos")) is not list:
            raise ValueError(f"retrato sem a largura {largura} bem formada")
        if tela["rolagem"]:
            achados.append(f"{largura}px: rolagem horizontal")
        elementos = tela["elementos"]
        for el in elementos:
            texto, tipo = el["texto"], el["tipo"]
            palavras = len(texto.split())
            if tipo in lim and palavras > lim[tipo]:
                achados.append(f"{largura}px: {tipo} com {palavras} palavras (max {lim[tipo]}): {texto[:60]!r}")
            if tipo == "paragrafo":
                linhas = el["linhas"]
                if type(linhas) is not int or linhas < 1:
                    raise ValueError(f"paragrafo com linhas invalidas: {linhas!r}")
                if len(texto) / linhas > MAX_CARACTERES_LINHA:
                    achados.append(f"{largura}px: paragrafo com {len(texto) // linhas} caracteres por linha "
                                   f"(max {MAX_CARACTERES_LINHA}): {texto[:40]!r}")
            if el["clicavel_sem_controle"]:
                achados.append(f"{largura}px: acao sem controle (clicavel sem botao ou link): {texto[:40]!r}")
        achados += desalinhados(elementos, largura)
    return achados


def desalinhados(elementos, largura):
    """Irmaos empilhados (um abaixo do outro) cujas bordas esquerdas quase coincidem, mas nao coincidem."""
    por_pai = {}
    for el in elementos:
        por_pai.setdefault(el["pai"], []).append(el)
    achados = []
    for irmaos in por_pai.values():
        irmaos = sorted(irmaos, key=lambda e: e["topo"])
        for a, b in zip(irmaos, irmaos[1:]):
            empilhados = b["topo"] >= a["topo"] + a["altura"] - 1
            desvio = abs(a["esquerda"] - b["esquerda"])
            if empilhados and DESVIO_ALINHAMENTO_PX < desvio < QUASE_ALINHADO_PX:
                achados.append(f"{largura}px: irmaos desalinhados em {desvio:.1f}px "
                               f"(max {DESVIO_ALINHAMENTO_PX}): {a['texto'][:25]!r} / {b['texto'][:25]!r}")
    return achados


def extrair(url):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as erro:
        raise ValueError("Playwright ausente: pip install playwright && python -m playwright install chromium") from erro
    retrato = {}
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        for largura in LARGURAS:
            pagina = navegador.new_page(viewport={"width": largura, "height": 900})
            pagina.goto(url, wait_until="networkidle")
            retrato[str(largura)] = pagina.evaluate(EXTRATOR)
            pagina.close()
        navegador.close()
    return retrato


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    fonte = a.add_mutually_exclusive_group(required=True)
    fonte.add_argument("--url")
    fonte.add_argument("--retrato")
    a.add_argument("--perfil", default="corporativo")
    a.add_argument("--salvar")
    try:
        args = a.parse_args(argv)
    except SystemExit as saida:
        return 2 if saida.code else 0
    try:
        if args.url:
            retrato = extrair(args.url)
            if args.salvar:
                with open(args.salvar, "w", encoding="utf-8") as f:
                    json.dump(retrato, f, ensure_ascii=False)
        else:
            with open(args.retrato, encoding="utf-8") as f:
                retrato = json.load(f)
        achados = avaliar(retrato, args.perfil)
    except (OSError, ValueError, KeyError, TypeError) as erro:
        print(f"ERRO: {erro}")
        return 2
    for achado in achados:
        print(achado)
    print(f"TOTAL {len(achados)} achado(s) no perfil {args.perfil}")
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())
