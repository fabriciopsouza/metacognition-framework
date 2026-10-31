#!/usr/bin/env python3
"""Gate de UX por medida (skill ux-design, camada 3): as medidas que as ferramentas prontas nao cobrem.

Mede, numa pagina renderizada em 360 px e 1280 px: caracteres por linha de paragrafo, desalinhamento de irmaos na
mesma coluna, rolagem horizontal, palavras por elemento, acao sem controle (`div` clicavel) e irmaos do mesmo tipo com
tamanhos diferentes. Contraste, alvo e
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
# Acima disso a diferenca e intencional (recuo, outra coluna), nao quase-alinhamento. Mantido pelo dono, 30/10/2026.
QUASE_ALINHADO_PX = 16
# Irmaos do mesmo tipo (dono, 30/10/2026: "nao gosto quando elementos ficam de tamanhos diferentes"). INFERIDO, a calibrar.
TOLERANCIA_TAMANHO_PX = 2
GRAFICOS = ("svg", "canvas")
# Grafico com classe e com largura >= isto no grupo; abaixo e icone, que pode ter tamanho proprio (QA r1).
GRAFICO_MIN_PX = 60
LIMITE_PALAVRAS = {"controle": 2, "cabecalho": 2, "titulo": 4, "legenda": 8}  # calibrado pelo dono, 30/10/2026
# Perfis mudam o estilo, nao os limites (calibracao do dono): so a lista de nomes validos, sem limite por perfil.
PERFIS = ("corporativo", "corporativo-2", "minimalista", "moderno", "arrojado", "outro")

# Executado no navegador: um registro por elemento medido. `tipo` decide a regra de palavras.
EXTRATOR = r"""
() => {
  const ign = el => el.closest('[data-ux-ignore]') !== null;
  const tipo = el => {
    const t = el.tagName.toLowerCase(), r = el.getAttribute('role');
    if (['button', 'option'].includes(t) || ['button', 'tab', 'option', 'menuitem'].includes(r)) return 'controle';
    if (t === 'input' && ['button', 'submit', 'reset'].includes(el.type)) return 'controle';
    if (t === 'th') return 'cabecalho';
    if (['h1', 'h2', 'h3'].includes(t)) return 'titulo';
    if (['figcaption', 'caption', 'small', 'legend'].includes(t)) return 'legenda';
    if (t === 'p') return 'paragrafo';
    return 'outro';
  };
  const px = v => parseFloat(v) || 0;
  // Caixa centralizada (flex, margin auto): mais estreita que a area de CONTEUDO do pai (sem padding e borda) e com
  // sobras iguais dos dois lados; bloco de largura total num pai com padding simetrico nao e centralizado.
  const centrado = (el, b) => {
    if (!el.parentElement) return false;
    const p = el.parentElement.getBoundingClientRect(), cs = getComputedStyle(el.parentElement);
    const esq = p.left + px(cs.borderLeftWidth) + px(cs.paddingLeft);
    const dir = p.right - px(cs.borderRightWidth) - px(cs.paddingRight);
    return b.width < dir - esq - 1 && Math.abs((b.left - esq) - (dir - b.right)) < 1;
  };
  const linhas = el => {  // altura do conteudo / line-height; sem line-height em px, tops distintos do texto
    const cs = getComputedStyle(el), lh = parseFloat(cs.lineHeight);
    const h = el.getBoundingClientRect().height - px(cs.paddingTop) - px(cs.paddingBottom)
      - px(cs.borderTopWidth) - px(cs.borderBottomWidth);
    if (lh > 0) return Math.max(1, Math.round(h / lh));
    const rg = document.createRange(); rg.selectNodeContents(el);
    return new Set([...rg.getClientRects()].map(r => Math.round(r.top))).size || 1;
  };
  // Arranjo do pai: 'grade' (grid: celulas de trilhas) ou 'flex' (largura vem do conteudo); senao vazio.
  const arranjo = el => {
    if (!el.parentElement) return '';
    const d = getComputedStyle(el.parentElement).display;
    return d.endsWith('grid') ? 'grade' : d.endsWith('flex') ? 'flex' : '';
  };
  const trilhas = el => { const cs = getComputedStyle(el); return cs.gridColumnStart + '/' + cs.gridColumnEnd; };
  const classe = el => (el.getAttribute('class') || '').trim().split(/\s+/)[0];  // a primeira classe e o tipo
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
      esquerda: b.left, topo: b.top, largura: b.width, altura: b.height, clicavel_sem_controle: clicavel,
      coluna: !getComputedStyle(el).display.startsWith('inline') && !centrado(el, b),
      tag: el.tagName.toLowerCase(), classe: classe(el), arranjo: arranjo(el),
      trilhas: trilhas(el)});
  });
  return {rolagem: document.documentElement.scrollWidth > document.documentElement.clientWidth, elementos: out};
}
"""


def limites(perfil):
    if perfil not in PERFIS:
        raise ValueError(f"perfil desconhecido: {perfil} (validos: {', '.join(PERFIS)})")
    return LIMITE_PALAVRAS


def avaliar(retrato, perfil="corporativo"):
    """Achados (lista de textos) de um retrato {largura: {rolagem, elementos}}; ValueError se malformado."""
    lim = limites(perfil)
    if type(retrato) is not dict:
        raise ValueError("retrato deve ser objeto {largura: tela}")
    achados = []
    for largura in LARGURAS:
        tela = retrato.get(str(largura))
        if type(tela) is not dict or type(tela.get("rolagem")) is not bool or type(tela.get("elementos")) is not list:
            raise ValueError(f"retrato sem a largura {largura} bem formada")
        if tela["rolagem"]:
            achados.append(f"{largura}px: rolagem horizontal")
        elementos = tela["elementos"]
        for el in elementos:
            if type(el) is not dict or type(el.get("texto")) is not str or type(el.get("tipo")) is not str:
                raise ValueError(f"elemento malformado em {largura}px: {el!r}"[:120])
            if any(type(el.get(c)) is not str for c in ("tag", "classe", "arranjo", "trilhas")):
                raise ValueError(f"elemento sem tag, classe, arranjo ou trilhas em {largura}px (extrair de novo): {el!r}"[:120])
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
        achados += tamanhos_diferentes(elementos, largura)
    return achados


def desalinhados(elementos, largura):
    """Irmaos empilhados (um abaixo do outro) cujas bordas esquerdas quase coincidem, mas nao coincidem."""
    por_pai = {}
    for el in elementos:
        if el["coluna"]:  # o extrator marca falso o inline e a caixa centralizada no pai
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


def grupos_de_tipo(elementos):
    """Agrupa por (grupo do pai, tag, classe): filhos de pais do mesmo grupo (cartoes de uma grade) caem no mesmo grupo,
    entao o grafico de cada cartao e comparado com os outros. Pai unico no grupo dele = grupo do proprio pai."""
    chave, grupos = {}, {}
    for el in elementos:  # ordem do documento: o pai vem antes do filho
        chave[el["id"]] = (chave.get(el["pai"], ("pai", el["pai"])), el["tag"], el["classe"])
        grupos.setdefault(chave[el["id"]], []).append(el)
    return list(grupos.values())


def lado_a_lado(a, b):
    return a["topo"] < b["topo"] + b["altura"] - 1 and b["topo"] < a["topo"] + a["altura"] - 1


def tamanhos_diferentes(elementos, largura):
    """Grafico (svg, canvas com classe, largura >= GRAFICO_MIN_PX), entre primos: largura e altura. Irmaos do mesmo pai:
    item de grid, largura entre os da mesma posicao de trilhas ('auto/auto' quando auto-posicionado) e altura entre os
    lado a lado; item de flex, so altura entre os lado a lado (a largura vem do conteudo: chip, link)."""
    achados = []
    for grupo in grupos_de_tipo(elementos):
        tag, classe = grupo[0]["tag"], grupo[0]["classe"]
        diferencas = {}
        if tag in GRAFICOS:
            if not classe or len(grupo) < 2 or max(e["largura"] for e in grupo) < GRAFICO_MIN_PX:
                continue
            for medida in ("largura", "altura"):
                diferencas[medida] = max(e[medida] for e in grupo) - min(e[medida] for e in grupo)
        else:
            # So irmaos do mesmo pai: a uniao entre primos vale so para grafico (QA r2: texto de cartoes diferentes).
            por_pai, por_trilha = {}, {}
            for e in grupo:
                if e["arranjo"]:
                    por_pai.setdefault(e["pai"], []).append(e)
                if e["arranjo"] == "grade":
                    por_trilha.setdefault((e["pai"], e["trilhas"]), []).append(e)
            diferencas["largura"] = max((max(e["largura"] for e in g) - min(e["largura"] for e in g)
                                         for g in por_trilha.values()), default=0)
            diferencas["altura"] = max((abs(a["altura"] - b["altura"]) for g in por_pai.values()
                                        for i, a in enumerate(g) for b in g[i + 1:] if lado_a_lado(a, b)), default=0)
        for medida, diferenca in diferencas.items():
            if diferenca > TOLERANCIA_TAMANHO_PX:
                nome = f"{tag}.{classe}" if classe else tag
                achados.append(f"{largura}px: {len(grupo)} {nome} com {medida} diferente em {diferenca:.1f}px "
                               f"(max {TOLERANCIA_TAMANHO_PX}): {grupo[0]['texto'][:25]!r}")
    return achados


def extrair(url):
    try:
        from playwright.sync_api import Error as ErroPlaywright, sync_playwright
    except ImportError as erro:
        raise ValueError("Playwright ausente: pip install playwright && python -m playwright install chromium") from erro
    retrato = {}
    try:  # navegador ausente, URL fora do ar ou tempo esgotado = gate nao executado (2), nunca "reprovou" (1)
        with sync_playwright() as p:
            navegador = p.chromium.launch()
            for largura in LARGURAS:
                pagina = navegador.new_page(viewport={"width": largura, "height": 900})
                pagina.goto(url, wait_until="networkidle")
                retrato[str(largura)] = pagina.evaluate(EXTRATOR)
                pagina.close()
            navegador.close()
    except ErroPlaywright as erro:
        raise ValueError(f"Playwright falhou (gate nao executado): {erro}") from erro
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
