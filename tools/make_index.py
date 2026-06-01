#!/usr/bin/env python3
"""make_index.py — índice VISÍVEL e navegável de uma pasta de entrega (baseline; ADR-050 emenda).

Varre a pasta de entrega e gera **index.html** (duplo-clique → navegador, links clicáveis) +
**LEIA-ME.txt** (universal, abre em qualquer editor), com **ORDEM DE LEITURA GUIADA** (comece-aqui →
resumo → apresentação → documentos → código → dados) para o usuário leigo NÃO se perder.

Princípios:
- **Auto-verificação:** lista só arquivos que EXISTEM (varredura real do disco) — nenhum link aponta
  pro vazio, nada na pasta fica órfão do índice. Anti-fabricação no nível da entrega.
- **Resumo de 3 linhas no topo:** lido de um arquivo de resumo/decisão se houver; senão `NÃO PREENCHIDO`
  (nunca inventado).
- **Duplo-papel handoff (ADR-012):** o índice declara artefato/localização/carimbo — serve de Pacote de
  handoff cross-sessão (outra sessão começa sem perguntar).

Uso:
    python tools/make_index.py <pasta-entrega> [--title "..."] [--resumo "..."] [--version "..."]
Sem dependências externas (stdlib). Idempotente: re-rodar regenera. Baseline (todas as distribuições).
"""
import argparse
import html as _html
import os
import re
import sys
import urllib.parse

NAO_PREENCHIDO = "NÃO PREENCHIDO"
INDEX_FILES = {"index.html", "leia-me.txt"}          # não indexa a si mesmo
SKIP_DIRS = {".git", "__pycache__"}
DATESTAMP_RX = re.compile(r"\d{4}-\d{2}-\d{2}(?:[t_]\d{2,6})?", re.IGNORECASE)

# Ordem de leitura guiada: categoria → (prioridade, rótulo amigável).
CATEGORIES = {
    "resumo": (0, "comece aqui — visão geral"),
    "apresentacao": (1, "apresentação executiva (decisão)"),
    "docs": (2, "documentos: relatórios, manuais, POPs"),
    "codigo": (3, "código e scripts (técnico)"),
    "dados": (4, "planilhas e dados"),
    "outros": (5, "outros arquivos"),
}
RESUMO_HINT = re.compile(r"resumo|sumario|sum[aá]rio|leia|decis[aã]o|summary|readme", re.IGNORECASE)


def file_desc(rel):
    ext = rel.rsplit(".", 1)[-1].lower() if "." in rel else ""
    return {"pdf": "documento para leitura/impressão", "docx": "documento editável (Word)",
            "pptx": "apresentação de slides (PowerPoint/Slides)", "md": "documento em texto",
            "txt": "texto simples", "xlsx": "planilha (Excel)", "csv": "dados em tabela",
            "py": "script (código)", "ipynb": "notebook", "json": "dados estruturados",
            "png": "imagem", "html": "abre no navegador"}.get(ext, "arquivo da entrega")


def categorize(rel):
    top = rel.split("/", 1)[0].lower() if "/" in rel else ""
    if top in CATEGORIES:
        return top
    if RESUMO_HINT.search(os.path.basename(rel)):
        return "resumo"
    return "outros"


def scan(root):
    """Relpaths (posix) de todo arquivo da entrega, exceto o próprio índice e lixo."""
    out = []
    for dp, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            rel = os.path.relpath(os.path.join(dp, fn), root).replace(os.sep, "/")
            if rel.lower() in INDEX_FILES:
                continue
            out.append(rel)
    return sorted(out, key=lambda r: (CATEGORIES[categorize(r)][0], r.lower()))


def read_resumo(root, rels):
    """3 primeiras linhas úteis de um arquivo de resumo/decisão (se houver). Senão None — não inventa."""
    cands = [r for r in rels if RESUMO_HINT.search(os.path.basename(r)) and r.endswith((".md", ".txt"))]
    for r in cands:
        try:
            lines = open(os.path.join(root, *r.split("/")), encoding="utf-8-sig").read().splitlines()
        except OSError:
            continue
        # pula frontmatter YAML (--- ... ---) — senão metadata (date:/author:) vira "resumo" falso
        if lines and lines[0].strip() == "---":
            end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
            if end is not None:
                lines = lines[end + 1:]
        useful = [l.strip() for l in lines
                  if l.strip() and not l.lstrip().startswith(("#", ">", "<!--", "---"))]
        if useful:
            return " ".join(useful[:3])[:300]
    return None


def _order_blocks(rels):
    blocks = []
    for cat, (_, label) in sorted(CATEGORIES.items(), key=lambda kv: kv[1][0]):
        members = [r for r in rels if categorize(r) == cat]
        if members:
            blocks.append((cat, label, members))
    return blocks


def generate(root, title=None, resumo=None, version=None):
    """Escreve index.html + LEIA-ME.txt na raiz da entrega. Retorna (n_arquivos, caminhos_indice)."""
    root = os.path.abspath(root)
    title = title or os.path.basename(root.rstrip(os.sep)) or "Entrega"
    rels = scan(root)
    resumo = resumo or read_resumo(root, rels) or NAO_PREENCHIDO
    m = DATESTAMP_RX.search(os.path.basename(root))
    version = version or (m.group(0) if m else NAO_PREENCHIDO)
    blocks = _order_blocks(rels)
    n = sum(1 for _ in rels)

    # --- LEIA-ME.txt ---
    T = [f"ENTREGA: {title}", "=" * 60, "",
         "RESUMO: " + resumo, "",
         "COMECE POR AQUI. Leia nesta ordem (de cima para baixo):", ""]
    step = 1
    for _, label, members in blocks:
        T.append(f"{step}. {label.upper()}")
        for r in members:
            T.append(f"     {r}   ({file_desc(r)})")
        T.append("")
        step += 1
    if not blocks:
        T += ["(nenhum arquivo nesta pasta)", ""]
    T += ["-" * 60, "PACOTE DE HANDOFF (ADR-012):",
          f"  Artefato : {title}",
          f"  Versao   : {version}",
          f"  Local    : {root}",
          f"  Arquivos : {n}", "",
          "Abra o index.html para a versao navegavel (links clicaveis).",
          "Campos vazios nos documentos = NAO PREENCHIDO (nunca inventados)."]
    with open(os.path.join(root, "LEIA-ME.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(T) + "\n")

    # --- index.html ---
    e = _html.escape
    sections = []
    step = 1
    for _, label, members in blocks:
        items = "\n".join(
            f'      <li><a href="{e(urllib.parse.quote(r))}">{e(r)}</a> '
            f'<span class="d">— {e(file_desc(r))}</span></li>'
            for r in members)
        sections.append(f'    <li><b>{step}. {e(label)}</b><ul>\n{items}\n    </ul></li>')
        step += 1
    order_html = "\n".join(sections) or "    <li>(nenhum arquivo nesta pasta)</li>"
    doc = f"""<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Entrega: {e(title)}</title>
<style>body{{font-family:system-ui,Arial,sans-serif;max-width:780px;margin:2rem auto;padding:0 1rem;line-height:1.55;color:#1a1a1a}}
h1{{font-size:1.4rem;margin-bottom:.2rem}}.resumo{{background:#f4f6fb;border-left:4px solid #0a58ca;padding:.6rem .9rem;border-radius:4px}}
h2{{font-size:1.05rem;margin-top:1.8rem}}a{{color:#0a58ca;text-decoration:none}}a:hover{{text-decoration:underline}}
ul{{padding-left:1.2rem}}li{{margin:.25rem 0}}.d{{color:#666}}.hand{{color:#444;font-size:.9rem;background:#fafafa;border:1px solid #eee;border-radius:4px;padding:.6rem .9rem}}
.note{{color:#777;font-size:.82rem;margin-top:2rem}}code{{background:#f0f0f0;padding:0 .2rem;border-radius:3px}}</style>
</head><body>
<h1>Entrega: {e(title)}</h1>
<p class="resumo"><b>Resumo:</b> {e(resumo)}</p>
<p><b>Comece por aqui.</b> Leia nesta ordem — os artefatos estão agrupados do mais geral ao mais técnico:</p>
<ol style="list-style:none;padding-left:0">
{order_html}
</ol>
<h2>Pacote de handoff (ADR-012)</h2>
<p class="hand">Artefato: <b>{e(title)}</b> · Versão: <code>{e(version)}</code> · Arquivos: {n}<br>
Local: <code>{e(root)}</code></p>
<p class="note">Gerado por <code>tools/make_index.py</code> (ADR-050). Lista só o que existe de fato na pasta
(nenhum link aponta pro vazio). Campos vazios nos documentos = <b>NÃO PREENCHIDO</b> — nunca fabricados.</p>
</body></html>
"""
    with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(doc)
    return n, [os.path.join(root, "index.html"), os.path.join(root, "LEIA-ME.txt")]


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--title")
    ap.add_argument("--resumo")
    ap.add_argument("--version")
    args = ap.parse_args(argv[1:])
    if not os.path.isdir(args.dir):
        print(f"pasta inexistente: {args.dir}", file=sys.stderr)
        return 2
    n, idx = generate(args.dir, args.title, args.resumo, args.version)
    for p in idx:
        print(f"  índice: {p}")
    print(f"RESULTADO: PASS (índice de {n} arquivo(s); ordem guiada; auto-verificado)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
