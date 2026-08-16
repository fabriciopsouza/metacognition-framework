#!/usr/bin/env python3
"""trabalhos.py — registro PERSISTENTE de trabalhos com handoff em aberto (ADR-100).

PORQUE (gap real, declarado pelo dono em 2026-08-03): o Pacote P14 (`tools/handoff.py`,
ADR-076) e deterministico e completo, mas e EFEMERO — gerado, exibido no chat e perdido.
Quem abre a proxima sessao nao e lembrado de que existe trabalho aguardando decisao. O
handoff so cumpre a funcao se sobreviver ao fim da sessao E for OFERECIDO ate ser tratado.

O QUE ESTE MODULO ACRESCENTA ao que ja existe:
  - PERSISTENCIA fora do repo (`~/.claude/trabalhos/`), porque um trabalho pode envolver
    varios repositorios e nao pode depender de qual pasta foi aberta;
  - CICLO DE VIDA explicito: `aberto` -> `tratado`. Enquanto aberto, o boot oferece;
  - ORGANIZACAO POR TRABALHO, nao por repo nem por sessao: qual e o trabalho, para que
    serve, o que foi feito, o que falta e o que decide o proximo passo.

O QUE NAO DUPLICA: o conteudo tecnico do pacote continua vindo de `tools/handoff.py`
(versao, branch, pendencias, proximo passo). Este modulo guarda e OFERECE; nao regera.

REGUA §0 (ADR-007): passa pela porta (c) — destrava o uso do handoff que ja existe. Sem
persistencia, o P14 e produzido e descartado; o custo de reconstituir estado a cada
sessao e o que este registro elimina.

Uso:
    python tools/trabalhos.py listar                 # abertos (o que o boot mostra)
    python tools/trabalhos.py listar --todos
    python tools/trabalhos.py registrar --slug <s> --nome "..." --objetivo "..." \
        [--repo <path>] [--feito "..."] [--pendente "..."] [--proximo "..."]
    python tools/trabalhos.py tratar --slug <s> [--nota "..."]
    python tools/trabalhos.py reabrir --slug <s>
    python tools/trabalhos.py mostrar --slug <s>

Codigo de saida de `listar`: 0 sempre (informativo; nao bloqueia boot).
"""
import argparse
import datetime
import os
import re
import sys

RAIZ = os.environ.get("TRABALHOS_DIR") or os.path.join(
    os.path.expanduser("~"), ".claude", "trabalhos")

CAMPOS = ("trabalho", "objetivo", "repo", "status", "criado", "atualizado")
SECOES = [
    ("feito", "O que foi feito"),
    ("pendente", "O que esta pendente"),
    ("proximo", "Proximo passo — e o que ele decide"),
]


def _hoje():
    return datetime.date.today().isoformat()


def _slug(s):
    s = re.sub(r"[^\w\s-]", "", s.lower()).strip()
    return re.sub(r"[\s_]+", "-", s)[:60] or "trabalho"


def _caminho(slug):
    return os.path.join(RAIZ, f"{_slug(slug)}.md")


def _ler(caminho):
    """Frontmatter simples + secoes. ZERO-DEP: sem PyYAML, so campos planos."""
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as f:
        txt = f.read()
    fm, corpo = {}, txt
    if txt.startswith("---"):
        fim = txt.find("\n---", 3)
        if fim > 0:
            for linha in txt[3:fim].splitlines():
                if ":" in linha:
                    k, v = linha.split(":", 1)
                    fm[k.strip()] = v.strip()
            corpo = txt[fim + 4:]
    # So os titulos CANONICOS abrem secao. Qualquer outra linha "## ..." e TEXTO do corpo.
    #
    # PORQUE (achado BLOQUEANTE do qa-critic 2026-08-03): particionar por qualquer `## `
    # e so reserializar as tres secoes conhecidas APAGA, na proxima escrita, todo conteudo
    # sob um titulo nao-canonico — e o Pacote P14, que este registro existe para guardar,
    # e cheio de `## `. O mecanismo cujo proposito e "o handoff nao se perde" perdia o
    # handoff. Ancorar no conjunto conhecido preserva o texto do usuario intacto.
    titulos = {t for _, t in SECOES}
    secoes, atual = {}, None
    for linha in corpo.splitlines():
        m = re.match(r"^##\s+(.*?)\s*$", linha)
        if m and m.group(1) in titulos:
            atual = m.group(1)
            secoes[atual] = []
        elif atual is not None:
            secoes[atual].append(linha)
    return {"fm": fm, "secoes": {k: "\n".join(v).strip() for k, v in secoes.items()},
            "caminho": caminho}


def _escrever(slug, fm, secoes):
    os.makedirs(RAIZ, exist_ok=True)
    linhas = ["---"]
    for k in CAMPOS:
        if fm.get(k):
            linhas.append(f"{k}: {fm[k]}")
    linhas.append("---")
    linhas.append("")
    for chave, titulo in SECOES:
        linhas.append(f"## {titulo}")
        linhas.append("")
        linhas.append(secoes.get(chave, "_(a preencher)_"))
        linhas.append("")
    caminho = _caminho(slug)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(linhas))
    return caminho


def _todos():
    if not os.path.isdir(RAIZ):
        return []
    saida = []
    for nome in sorted(os.listdir(RAIZ)):
        if nome.endswith(".md") and nome != "README.md":
            d = _ler(os.path.join(RAIZ, nome))
            if d:
                d["slug"] = nome[:-3]
                saida.append(d)
    return saida


def cmd_listar(a):
    itens = _todos()
    abertos = [d for d in itens if d["fm"].get("status", "aberto") == "aberto"]
    alvo = itens if a.todos else abertos
    if not alvo:
        print("nenhum trabalho em aberto." if not a.todos else "nenhum trabalho registrado.")
        return 0
    titulo = "TRABALHOS REGISTRADOS" if a.todos else "TRABALHOS EM ABERTO — aguardando sua decisao"
    print(f"\n{'='*72}\n{titulo}\n{'='*72}")
    for d in alvo:
        fm = d["fm"]
        st = fm.get("status", "aberto")
        marca = "" if st == "aberto" else f"  [{st}]"
        print(f"\n▸ {fm.get('trabalho', d['slug'])}{marca}")
        print(f"  objetivo   : {fm.get('objetivo', '(nao declarado)')}")
        if fm.get("repo"):
            print(f"  onde       : {fm['repo']}")
        prox = d["secoes"].get("Proximo passo — e o que ele decide", "").strip()
        pend = d["secoes"].get("O que esta pendente", "").strip()
        if prox:
            print(f"  proximo    : {prox.splitlines()[0][:100]}")
        if pend:
            n = len([l for l in pend.splitlines() if l.strip().startswith(("-", "*", "1"))])
            print(f"  pendencias : {n if n else 'ver detalhe'}")
        print(f"  detalhe    : python tools/trabalhos.py mostrar --slug {d['slug']}")
    if not a.todos:
        print(f"\n{'-'*72}")
        print("Ao concluir: python tools/trabalhos.py tratar --slug <slug>")
        print("Enquanto estiver aberto, este aviso reaparece a cada sessao.")
    return 0


def cmd_registrar(a):
    caminho = _caminho(a.slug)
    antigo = _ler(caminho)
    # slug ja usado por OUTRO trabalho: sem isto, os campos do antigo que nao forem
    # repassados sobrevivem e se misturam ao novo — dois trabalhos num registro so.
    # `_slug` trunca em 60 chars, o que torna a colisao mais provavel do que parece.
    if antigo and a.nome and antigo["fm"].get("trabalho") not in (None, "", a.nome):
        if not a.force:
            print(f"ERRO: o slug '{a.slug}' ja e de outro trabalho:\n"
                  f"  existente: {antigo['fm'].get('trabalho')}\n"
                  f"  informado: {a.nome}\n"
                  f"Use outro --slug, ou --force para sobrescrever deliberadamente.",
                  file=sys.stderr)
            return 1
        print(f"AVISO: sobrescrevendo '{antigo['fm'].get('trabalho')}' (--force)")
    if not antigo and not a.objetivo:
        # trabalho sem objetivo nao cumpre a funcao: o boot mostraria "(nao declarado)"
        # e quem retomasse nao saberia para que serve
        print("ERRO: --objetivo e obrigatorio ao criar um trabalho "
              "(sem ele o registro nao informa para que serve).", file=sys.stderr)
        return 1
    fm = antigo["fm"] if antigo else {}
    fm.update({
        "trabalho": a.nome or fm.get("trabalho", a.slug),
        "objetivo": a.objetivo or fm.get("objetivo", ""),
        "repo": a.repo or fm.get("repo", ""),
        "status": "aberto",
        "criado": fm.get("criado", _hoje()),
        "atualizado": _hoje(),
    })
    secoes = {}
    if antigo:
        for chave, titulo in SECOES:
            secoes[chave] = antigo["secoes"].get(titulo, "")
    for chave, valor in (("feito", a.feito), ("pendente", a.pendente),
                         ("proximo", a.proximo)):
        if valor:
            secoes[chave] = valor
    p = _escrever(a.slug, fm, secoes)
    print(f"registrado: {p}")
    print("sera oferecido no inicio de cada sessao ate ser tratado.")
    return 0


def cmd_tratar(a):
    d = _ler(_caminho(a.slug))
    if not d:
        print(f"nao encontrado: {a.slug}", file=sys.stderr)
        return 1
    d["fm"]["status"] = "tratado"
    d["fm"]["atualizado"] = _hoje()
    secoes = {c: d["secoes"].get(t, "") for c, t in SECOES}
    if a.nota:
        secoes["proximo"] = (secoes.get("proximo", "") +
                             f"\n\n**Tratado em {_hoje()}:** {a.nota}").strip()
    _escrever(a.slug, d["fm"], secoes)
    print(f"'{d['fm'].get('trabalho', a.slug)}' marcado como tratado — sai do aviso de boot.")
    return 0


def cmd_reabrir(a):
    d = _ler(_caminho(a.slug))
    if not d:
        print(f"nao encontrado: {a.slug}", file=sys.stderr)
        return 1
    d["fm"]["status"] = "aberto"
    d["fm"]["atualizado"] = _hoje()
    _escrever(a.slug, d["fm"], {c: d["secoes"].get(t, "") for c, t in SECOES})
    print(f"'{a.slug}' reaberto — volta a ser oferecido no boot.")
    return 0


def cmd_mostrar(a):
    d = _ler(_caminho(a.slug))
    if not d:
        print(f"nao encontrado: {a.slug}", file=sys.stderr)
        return 1
    with open(d["caminho"], encoding="utf-8") as f:
        print(f.read())
    return 0


def main(argv=None):
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("listar", help="trabalhos em aberto (usado pelo boot)")
    p.add_argument("--todos", action="store_true")
    p.set_defaults(func=cmd_listar)

    p = sub.add_parser("registrar", help="cria ou atualiza um trabalho")
    p.add_argument("--slug", required=True)
    p.add_argument("--nome")
    p.add_argument("--objetivo")
    p.add_argument("--repo")
    p.add_argument("--feito")
    p.add_argument("--pendente")
    p.add_argument("--proximo")
    p.add_argument("--force", action="store_true",
                   help="sobrescrever um slug ja usado por outro trabalho")
    p.set_defaults(func=cmd_registrar)

    p = sub.add_parser("tratar", help="marca como tratado; sai do aviso de boot")
    p.add_argument("--slug", required=True)
    p.add_argument("--nota")
    p.set_defaults(func=cmd_tratar)

    p = sub.add_parser("reabrir")
    p.add_argument("--slug", required=True)
    p.set_defaults(func=cmd_reabrir)

    p = sub.add_parser("mostrar")
    p.add_argument("--slug", required=True)
    p.set_defaults(func=cmd_mostrar)

    a = ap.parse_args(argv)
    if not getattr(a, "func", None):
        a = ap.parse_args(["listar"])
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
