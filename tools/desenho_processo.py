#!/usr/bin/env python3
"""desenho_processo.py — desenho do processo gerado da especificação (B3d, ADR-121).

Lê a Parte H — Processo do arquivo único e gera, na pasta de saída:
  - desenho-processo.html  revisão pelas áreas: HTML autônomo (sem CDN), SVG com uma raia VERTICAL por papel,
                           passos de cima para baixo, decisão em losango, retorno tracejado; papéis, gatilhos,
                           regras, controles, pontos para aprovação e perguntas em aberto;
  - desenho-processo.md / .docx  documento controlado, pelo `gen_exec_doc.export` existente.
Os gerados nunca são editados à mão: altere a Parte H e gere de novo.

Regras (reprovam, exit 1):
  - passo sem Descrição ou Papel; Próximo apontando para passo inexistente; passo repetido;
  - mais de 15 passos sem Macroação em todos → agrupe (o desenho sai em dois níveis: macroações e o detalhe de
    cada uma) ou registre `--aceito-mais-de-15 "<frase do dono, dd/mm/aaaa>"`; macroação com mais de 15 passos;
  - desenho mais largo que a tela (1536 px): a largura sai do número de papéis (uma raia cada); agrupe papéis ou
    divida o processo.

Uso:
    python tools/desenho_processo.py <spec.md> --out-dir <pasta> [--aceito-mais-de-15 "<frase, dd/mm/aaaa>"]
    python tools/desenho_processo.py <spec.md> --verificar      # só valida, não gera
"""
import datetime
import hashlib
import html
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_fonte  # noqa: E402

COLS = ["passo", "macroação", "descrição", "papel", "gatilho", "saída", "próximo", "regra", "controle"]
LIMITE_PASSOS = 15
LARGURA_TELA = 1536  # full HD a 125%: o SVG não pode passar disto
RAIA, LINHA, CX_L, CX_A, MARGEM, TOPO = 190, 96, 150, 58, 30, 70
CORES = ["#1f5f8b", "#2e6b4f", "#8a5a12", "#6b3f8b", "#9b2c2c", "#2f6f73", "#5b5b5b"]
_VAZIO = {"", "—", "-", "n/a"}
_DATA = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")


def _vazio(v):
    v = (v or "").strip()
    return v.lower() in _VAZIO or bool(re.fullmatch(r"<[^>]*>", v))


def _data_valida(txt):
    for d, m, a in _DATA.findall(txt or ""):
        try:
            datetime.date(int(a), int(m), int(d))
            return True
        except ValueError:
            pass
    return False


def _celulas(linha):
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", linha.strip().strip("|"))]


def _secoes(texto):
    """{'': linhas antes do 1º ###, 'pontos para aprovação': [...], ...}"""
    out, atual = {"": []}, ""
    for ln in (texto or "").splitlines():
        if ln.startswith("### "):
            atual = ln[4:].strip().lower()
            out[atual] = []
            continue
        out[atual].append(ln)
    return out


def _tabela_numerada(linhas):
    rows = []
    for ln in linhas:
        if ln.strip().startswith("|"):
            c = _celulas(ln)
            if c and re.fullmatch(r"\d+", c[0]):
                rows.append(c)
    return rows


def carregar(spec):
    """(passos, pontos, perguntas, achados). Passos em ordem, como dicts pelas colunas COLS."""
    texto = spec_fonte.ler_parte(spec, "processo")
    if texto is None:
        return [], [], [], ["Parte H — Processo ausente"]
    sec = _secoes(texto)
    passos, ach, vistos = [], [], set()
    for ln in sec[""]:
        if not ln.strip().startswith("|"):
            continue
        c = _celulas(ln)
        if not re.fullmatch(r"P-\d+", c[0]):
            continue
        if len(c) != len(COLS):
            ach.append(f"{c[0]}: {len(c)} colunas, o modelo tem {len(COLS)}")
            continue
        p = dict(zip(COLS, c))
        if p["passo"] in vistos:
            ach.append(f"{p['passo']} repetido")
        vistos.add(p["passo"])
        for k in ("descrição", "papel"):
            if _vazio(p[k]):
                ach.append(f"{p['passo']}: sem {k}")
        passos.append(p)
    if not passos:
        ach.append("Parte H sem passos (linhas `| P-nn | ...`)")
    # Mesmo papel com caixa ou acento diferente ("Comprador"/"comprador") é UMA raia; vale a primeira grafia.
    canon = {}
    for p in passos:
        chave = "".join(ch for ch in unicodedata.normalize("NFKD", p["papel"].strip()) if not unicodedata.combining(ch)).casefold()
        p["papel"] = canon.setdefault(chave, p["papel"].strip())
    pontos = _tabela_numerada(sec.get("pontos para aprovação", []))
    perguntas = _tabela_numerada(sec.get("perguntas em aberto", []))
    return passos, pontos, perguntas, ach


def destinos(p):
    """[(rótulo, 'P-nn')] do campo Próximo: 'P-02' ou 'sim: P-03; não: P-05'."""
    out = []
    for parte in re.split(r"\s*;\s*", p["próximo"] or ""):
        parte = parte.strip()
        if not parte or _vazio(parte):
            continue
        rot, _, alvo = parte.rpartition(":")
        for a in re.findall(r"P-\d+", alvo or parte):
            out.append((rot.strip(), a))
    return out


def validar(passos, aceite=""):
    ach, ids = [], {p["passo"] for p in passos}
    for p in passos:
        for _rot, alvo in destinos(p):
            if alvo not in ids:
                ach.append(f"{p['passo']}: próximo {alvo} não existe")
    agrupado = passos and all(not _vazio(p["macroação"]) for p in passos)
    if len(passos) > LIMITE_PASSOS and not agrupado:
        if not (aceite and _data_valida(aceite) and len(aceite.split()) >= 3):
            ach.append(f"{len(passos)} passos sem macroação em todos (limite {LIMITE_PASSOS}): agrupe em macroações "
                       f"ou registre --aceito-mais-de-15 \"<frase do dono, dd/mm/aaaa>\"")
    if agrupado:
        for m, grupo in macroacoes(passos):
            if len(grupo) > LIMITE_PASSOS:
                ach.append(f"macroação '{m}' com {len(grupo)} passos (limite {LIMITE_PASSOS}): divida")
    for nome, grupo in ([("processo", passos)] if not agrupado else macroacoes(passos)):
        papeis = _papeis(grupo)
        largura = _largura(len(papeis))
        if largura > LARGURA_TELA:  # medido: a largura do desenho sai do número de papéis (raias)
            ach.append(f"'{nome}' com {len(papeis)} papéis dá {largura} px, mais que a tela ({LARGURA_TELA} px): "
                       f"agrupe papéis ou divida")
    return ach


def _largura(n_papeis):
    return MARGEM * 2 + RAIA * n_papeis + 60  # 60 = corredor à direita para os retornos


def macroacoes(passos):
    ordem, grupos = [], {}
    for p in passos:
        m = p["macroação"].strip()
        if m not in grupos:
            ordem.append(m)
            grupos[m] = []
        grupos[m].append(p)
    return [(m, grupos[m]) for m in ordem]


def _papeis(passos):
    out = []
    for p in passos:
        if p["papel"] not in out:
            out.append(p["papel"])
    return out


def _quebra(texto, largura=22, linhas=3):
    palavras, out, atual = (texto or "").split(), [], ""
    for w in palavras:
        if len(atual) + len(w) + 1 > largura and atual:
            out.append(atual)
            atual = w
        else:
            atual = f"{atual} {w}".strip()
    if atual:
        out.append(atual)
    if len(out) > linhas:
        out = out[:linhas]
        out[-1] = out[-1][: largura - 1] + "…"
    return out


def svg(passos, titulo="", fora=None):
    """SVG com raias verticais (uma por papel). `fora`: {passo: macroação} dos destinos fora deste desenho.
    Devolve (texto_svg, largura)."""
    fora = fora or {}
    papeis = _papeis(passos)
    cor = {pa: CORES[i % len(CORES)] for i, pa in enumerate(papeis)}
    largura = _largura(len(papeis))
    altura = TOPO + LINHA * len(passos) + 70
    pos = {}
    for k, p in enumerate(passos):
        i = papeis.index(p["papel"])
        pos[p["passo"]] = (MARGEM + i * RAIA + RAIA // 2, TOPO + k * LINHA + LINHA // 2, k)
    e = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" width="{largura}" '
         f'role="img" aria-label="{html.escape(titulo)}">',
         '<defs><marker id="seta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#44505c"/></marker></defs>']
    for i, pa in enumerate(papeis):
        x = MARGEM + i * RAIA
        e.append(f'<rect x="{x}" y="10" width="{RAIA - 6}" height="{altura - 20}" rx="6" fill="{cor[pa]}" '
                 f'fill-opacity="0.06" stroke="{cor[pa]}" stroke-opacity="0.35"/>')
        for j, ln in enumerate(_quebra(pa, 24, 2)):
            e.append(f'<text class="raia" x="{x + (RAIA - 6) // 2}" y="{32 + j * 15}" text-anchor="middle" '
                     f'fill="{cor[pa]}">{html.escape(ln)}</text>')
    xret = largura - 40
    for p in passos:
        cx, cy, k = pos[p["passo"]]
        for rot, alvo in destinos(p):
            if alvo not in pos:  # destino em outra macroação: seta curta e indicação de onde segue
                y1 = cy + CX_A // 2
                e.append(f'<path class="ar" d="M{cx},{y1} V{y1 + 22}" marker-end="url(#seta)"/>'
                         f'<text class="lbl" x="{cx + 6}" y="{y1 + 34}">{html.escape((rot + ": ") if rot else "")}'
                         f'segue em {html.escape(alvo)} ({html.escape(fora.get(alvo, "outra macroação"))})</text>')
                continue
            tx, ty, tk = pos[alvo]
            if tk > k:  # para a frente: desce e cruza a raia
                y1, y2 = cy + CX_A // 2, ty - CX_A // 2
                ym = y1 + 18
                d = f"M{cx},{y1} V{ym} H{tx} V{y2}" if tx != cx else f"M{cx},{y1} V{y2}"
                e.append(f'<path class="ar" d="{d}" marker-end="url(#seta)"/>')
                lx, ly_ = cx + 6, y1 + 13  # rótulo no início da seta que desce
            else:  # retorno: pelo corredor da direita, tracejado
                d = f"M{cx + CX_L // 2},{cy} H{xret} V{ty} H{tx + CX_L // 2}"
                e.append(f'<path class="ar ret" d="{d}" marker-end="url(#seta)"/>')
                lx, ly_ = cx + CX_L // 2 + 10, cy - 6  # rótulo no início da seta que sai pela direita
            if rot:
                e.append(f'<text class="lbl" x="{lx}" y="{ly_}">{html.escape(rot)}</text>')
    for p in passos:
        cx, cy, _k = pos[p["passo"]]
        c = cor[p["papel"]]
        if len(destinos(p)) > 1:
            pts = f"{cx},{cy - CX_A // 2 - 4} {cx + CX_L // 2 + 6},{cy} {cx},{cy + CX_A // 2 + 4} {cx - CX_L // 2 - 6},{cy}"
            e.append(f'<polygon points="{pts}" fill="#ffffff" stroke="{c}" stroke-width="2"/>')
        else:
            fim = not destinos(p)
            e.append(f'<rect x="{cx - CX_L // 2}" y="{cy - CX_A // 2}" width="{CX_L}" height="{CX_A}" rx="8" '
                     f'fill="#ffffff" stroke="{c}" stroke-width="{3 if fim else 2}"/>')
        e.append(f'<text class="id" x="{cx}" y="{cy - CX_A // 2 + 13}" text-anchor="middle" fill="{c}">'
                 f'{html.escape(p["passo"])}</text>')
        decisao = len(destinos(p)) > 1
        for j, ln in enumerate(_quebra(p["descrição"], 16 if decisao else 22, 2 if decisao else 3)):
            e.append(f'<text class="t" x="{cx}" y="{cy - 4 + j * 14}" text-anchor="middle">{html.escape(ln)}</text>')
    ly = altura - 30
    e.append(f'<rect x="{MARGEM}" y="{ly - 11}" width="18" height="12" rx="3" fill="#fff" stroke="#44505c"/>'
             f'<text class="lbl" x="{MARGEM + 24}" y="{ly}">passo</text>'
             f'<polygon points="{MARGEM + 90},{ly - 12} {MARGEM + 100},{ly - 5} {MARGEM + 90},{ly + 2} {MARGEM + 80},{ly - 5}" '
             f'fill="#fff" stroke="#44505c"/><text class="lbl" x="{MARGEM + 106}" y="{ly}">decisão</text>'
             f'<path class="ar ret" d="M{MARGEM + 170},{ly - 5} h30"/><text class="lbl" x="{MARGEM + 206}" y="{ly}">retorno</text>'
             f'<rect x="{MARGEM + 270}" y="{ly - 11}" width="18" height="12" rx="3" fill="#fff" stroke="#44505c" '
             f'stroke-width="3"/><text class="lbl" x="{MARGEM + 294}" y="{ly}">fim</text>')
    e.append("</svg>")
    return "\n".join(e), largura


def svg_macro(grupos):
    """Visão geral: uma caixa por macroação, em sequência vertical."""
    largura, altura = 520, TOPO + LINHA * len(grupos) + 20
    e = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" width="{largura}" role="img" '
         'aria-label="macroações"><defs><marker id="seta2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
         'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#44505c"/></marker></defs>']
    for k, (m, grupo) in enumerate(grupos):
        y = TOPO + k * LINHA
        e.append(f'<rect x="60" y="{y}" width="400" height="{CX_A}" rx="8" fill="#fff" stroke="{CORES[0]}" stroke-width="2"/>'
                 f'<text class="t" x="260" y="{y + 25}" text-anchor="middle">{html.escape(m)}</text>'
                 f'<text class="lbl" x="260" y="{y + 44}" text-anchor="middle">{len(grupo)} passos · '
                 f'{html.escape(", ".join(_papeis(grupo)))[:60]}</text>')
        if k:
            e.append(f'<path class="ar" d="M260,{y - LINHA + CX_A} V{y}" marker-end="url(#seta2)"/>')
    e.append("</svg>")
    return "\n".join(e), largura


CSS = """:root{--gq:#1f5f8b;--gq-soft:#e8f0f6;--warn:#9b2c2c;--bg:#f7f6f2;--card:#fff;--line:#c9ced6;--ink:#1d2129;--muted:#5b6470}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 "Segoe UI",system-ui,-apple-system,Roboto,Arial,sans-serif}
main{max-width:1200px;margin:0 auto;padding:24px 16px 48px}h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;border-top:1px solid var(--line);padding-top:18px;margin-top:28px}
.muted{color:var(--muted)}.stamp{border-left:4px solid var(--gq);background:var(--gq-soft);padding:10px 14px;margin:14px 0;border-radius:4px}
.flow{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto}
.flow svg{max-width:100%;height:auto}svg text{font-family:"Segoe UI",system-ui,Arial,sans-serif}
svg .t{font-size:12px;fill:#1d2129}svg .id{font-size:11px;font-weight:700}svg .raia{font-size:13px;font-weight:700}svg .lbl{font-size:11px;fill:#5b6470}
svg .ar{fill:none;stroke:#44505c;stroke-width:1.6}svg .ret{stroke-dasharray:6 4}
.roles{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}.role{background:var(--card);border:1px solid var(--line);border-top:4px solid var(--gq);border-radius:8px;padding:10px 12px}
table{border-collapse:collapse;width:100%;background:var(--card)}th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}th{background:#eef1f4}
.note{border-left:4px solid var(--warn);padding:8px 12px;background:#fbeeee;border-radius:4px}footer{margin-top:32px;font-size:13px;color:var(--muted)}
@media print{.flow{overflow:visible}body{background:#fff}}"""


def _tabela_html(cab, linhas):
    if not linhas:
        return "<p class=\"muted\">Nenhum.</p>"
    th = "".join(f"<th>{html.escape(c)}</th>" for c in cab)
    tr = "".join("<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in l) + "</tr>" for l in linhas)
    return f"<table><tr>{th}</tr>{tr}</table>"


def gerar_html(spec, passos, pontos, perguntas):
    txt = open(spec, encoding="utf-8-sig").read()
    m = re.search(r"(?m)^#\s+(?!Parte\b)(.+)$", txt)
    titulo = re.sub(r"\s+—\s+Especificação\s*$", "", m.group(1).strip()) if m else os.path.basename(spec)
    sha = hashlib.sha256(txt.encode("utf-8")).hexdigest()[:12]
    agrupado = all(not _vazio(p["macroação"]) for p in passos) and len(macroacoes(passos)) > 1
    partes = []
    if agrupado:
        s, _w = svg_macro(macroacoes(passos))
        partes.append(f"<h2>Visão geral em {len(macroacoes(passos))} macroações</h2><div class=\"flow\">{s}</div>")
        de_macro = {p["passo"]: p["macroação"].strip() for p in passos}
        for mac, grupo in macroacoes(passos):
            s, _w = svg(grupo, mac, de_macro)
            partes.append(f"<h2>{html.escape(mac)} — {len(grupo)} passos</h2><div class=\"flow\">{s}</div>")
    else:
        s, _w = svg(passos, titulo)
        partes.append(f"<h2>O desenho em {len(passos)} passos</h2><div class=\"flow\">{s}</div>")
    papeis = _papeis(passos)
    cards = "".join(
        f'<div class="role" style="border-top-color:{CORES[i % len(CORES)]}"><b>{html.escape(pa)}</b><ul>'
        + "".join(f"<li>{html.escape(p['passo'])} · {html.escape(p['descrição'])}</li>" for p in passos if p["papel"] == pa)
        + "</ul></div>" for i, pa in enumerate(papeis))
    gat = [(p["passo"], p["gatilho"], p["saída"]) for p in passos if not _vazio(p["gatilho"])]
    regras = [(p["passo"], p["regra"]) for p in passos if not _vazio(p["regra"])]
    ctrl = [(p["passo"], p["controle"], p["papel"]) for p in passos if not _vazio(p["controle"])]
    corpo = f"""<main>
<h1>{html.escape(titulo)}</h1>
<p class="muted">Desenho do processo para revisão das áreas · {len(passos)} passos · {len(papeis)} papéis</p>
<div class="stamp"><b>Versão:</b> gerado de <code>{html.escape(os.path.basename(os.path.dirname(os.path.abspath(spec))))}/spec.md</code>
(sha256 {sha}) em {datetime.date.today():%d/%m/%Y}. Não edite este arquivo: altere a Parte H da especificação e gere de novo.</div>
{''.join(partes)}
<h2>Quem faz o quê</h2><div class="roles">{cards}</div>
<h2>Gatilhos</h2>{_tabela_html(["Passo", "O que dispara", "O que sai"], gat)}
<h2>Regras</h2>{_tabela_html(["Passo", "Regra"], regras)}
<h2>Pontos de controle</h2>{_tabela_html(["Passo", "Controle", "Quem"], ctrl)}
<h2>O que pedimos que aprovem</h2>
<p class="note">Responda na <b>planilha de confirmação</b> (colunas "Área confirma?", "Correção da área", "Nome e data"). Este HTML é só para leitura.</p>
{_tabela_html(["#", "Ponto", "Por que importa"], pontos)}
<h2>Perguntas em aberto</h2>{_tabela_html(["#", "Pergunta", "Quem decide"], perguntas)}
<footer>Gerado por <code>tools/desenho_processo.py</code> (ADR-121) a partir da Parte H — Processo.</footer>
</main>"""
    doc = (f"<!doctype html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\"><title>{html.escape(titulo)}</title>"
           f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><style>{CSS}</style></head>"
           f"<body>{corpo}</body></html>")
    return doc, titulo


def gerar_md(titulo, passos, pontos, perguntas):
    """Fonte do docx controlado (seções `##` lidas pelo gen_exec_doc)."""
    ln = [f"# {titulo} — Desenho do processo", "", "## Passos", ""]
    for p in passos:
        prox = p["próximo"] if not _vazio(p["próximo"]) else "fim"
        mac = "" if _vazio(p["macroação"]) else f"[{p['macroação']}] "
        ln.append(f"- {p['passo']} {mac}{p['descrição']} — {p['papel']}; próximo: {prox}")
    ln += ["", "## Papéis", ""] + [f"- {pa}" for pa in _papeis(passos)]
    ln += ["", "## Regras", ""] + [f"- {p['passo']}: {p['regra']}" for p in passos if not _vazio(p["regra"])]
    ln += ["", "## Pontos de controle", ""] + [f"- {p['passo']}: {p['controle']}" for p in passos
                                                if not _vazio(p["controle"])]
    ln += ["", "## Pontos para aprovação", ""] + [f"- {c[0]}. {' — '.join(c[1:])}" for c in pontos]
    ln += ["", "## Perguntas em aberto", ""] + [f"- {c[0]}. {' — '.join(c[1:])}" for c in perguntas]
    return "\n".join(ln) + "\n"


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    args = list(argv[1:])
    opts = {}
    for flag in ("--out-dir", "--aceito-mais-de-15"):
        if flag in args:
            i = args.index(flag)
            if i + 1 >= len(args):
                print(__doc__)
                return 2
            opts[flag] = args[i + 1]
            del args[i:i + 2]
    so_verificar = "--verificar" in args
    args = [a for a in args if a != "--verificar"]
    if len(args) != 1 or (not so_verificar and "--out-dir" not in opts):
        print(__doc__)
        return 2
    spec = args[0]
    if not spec_fonte.eh_unico(spec):
        print(f"RECUSADO: {spec} não é arquivo único de especificação (marca {spec_fonte.MARCA})")
        return 2
    try:
        passos, pontos, perguntas, ach = carregar(spec)
    except OSError as e:
        print(f"FAIL {spec}: {e}")
        return 1
    ach += validar(passos, opts.get("--aceito-mais-de-15", ""))
    if not ach and not so_verificar:
        doc, titulo = gerar_html(spec, passos, pontos, perguntas)
        out = opts["--out-dir"]
        os.makedirs(out, exist_ok=True)
        # Tudo ou nada: os gerados antigos são afastados ANTES de escrever. Arquivo em uso (ex.: docx aberto no
        # Word) faz a renomeação falhar; aí tudo volta como estava e nada novo é escrito.
        afastados, bloqueado = [], None
        for ext in ("html", "md", "docx"):
            p = os.path.join(out, f"desenho-processo.{ext}")
            if os.path.exists(p):
                try:
                    os.replace(p, p + ".anterior")
                    afastados.append(p)
                except OSError as ex:
                    bloqueado = f"{p} está em uso ({ex.strerror}): feche e gere de novo"
                    break
        if bloqueado:
            for p in afastados:
                os.replace(p + ".anterior", p)
            ach.append(bloqueado)
        else:
            novos = [os.path.join(out, f"desenho-processo.{x}") for x in ("html", "md", "docx")]
            try:
                with open(novos[0], "w", encoding="utf-8") as fh:
                    fh.write(doc)
                import gen_exec_doc  # noqa: E402
                escritos, pulados = gen_exec_doc.export(gerar_md(titulo, passos, pontos, perguntas), out,
                                                        ["md", "docx"], basename="desenho-processo")
                faltam = [os.path.basename(p) for p in novos if not os.path.isfile(p)]
                if faltam:
                    raise OSError(f"não gerado: {', '.join(faltam)} ({'; '.join(pulados) or 'sem motivo informado'})")
            except Exception as ex:  # qualquer falha na escrita: os três voltam como estavam (tudo ou nada)
                for p in novos:
                    if os.path.exists(p):
                        try:
                            os.remove(p)
                        except OSError:
                            pass
                for p in afastados:
                    os.replace(p + ".anterior", p)
                ach.append(f"falha ao gravar os gerados ({ex}); os anteriores foram mantidos")
            else:
                for p in afastados:
                    os.remove(p + ".anterior")
                print("gerado:", *novos)
    for a in ach:
        print(f"  - {a}")
    print("-" * 50)
    print("RESULTADO:", f"FAIL ({len(ach)})" if ach else "PASS")
    return 1 if ach else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
