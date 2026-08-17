#!/usr/bin/env python3
"""projeto_docs — documentação de gestão DERIVADA do estado real (ADR-102).

O QUE RESOLVE. Backlog digitado à mão envelhece na primeira semana: alguém fecha um item e esquece
de riscar, alguém abre outro e esquece de anotar. Aí o quadro vira ficção e todo mundo para de
olhar. Este gerador não pede digitação — ele **deriva** o backlog, o cronograma e o status report
das fontes que já são mantidas por obrigação:

  · `history.md` seção `## Em aberto`  -> dívidas e pendências declaradas
  · `docs/adr/*.md` com Status Proposto -> decisões esperando o dono
  · `capabilities.json`                 -> capacidades sem prova (o passivo medido)
  · `CHANGELOG.md`                      -> o que foi entregue, por release
  · git + suíte de canários             -> onde o trabalho está agora

Se o dado muda, o documento muda na próxima execução. Nada aqui é opinião.

O QUE PRODUZ (em `docs/projeto/`):
  · `backlog.csv`        colunas de importação direta em Trello e Planner
  · `cronograma.csv`     mesma base, ordenada por prioridade, abre no Excel
  · `STATUS-REPORT.md`   de onde partimos, onde chegamos, o que faltou, quem faz o quê

FORMATO CSV, não xlsx, por decisão do dono: o núcleo não instala biblioteca nenhuma — é o que o faz
rodar em máquina corporativa travada. CSV o Excel abre direto e os quadros importam nativamente.

Uso:
    python tools/projeto_docs.py                # gera tudo em docs/projeto/
    python tools/projeto_docs.py --status       # só o status report, no terminal
    python tools/projeto_docs.py --verificar    # os arquivos estão em dia com as fontes?

Códigos de saída: 0 ok · 1 desatualizado (com --verificar).
"""
import argparse
import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ_PADRAO = Path(__file__).resolve().parent.parent
SAIDA = "docs/projeto"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass


def _ler(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _git(raiz, *args):
    try:
        r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=30)
        return (r.stdout or "").strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _titulo(texto, limite=110):
    """Primeira frase util de um item, sem marcação, para caber numa célula de quadro."""
    t = re.sub(r"\*\*|`|\[\[|\]\]", "", str(texto)).strip()
    t = re.sub(r"\s+", " ", t)
    corte = re.split(r"(?<=[.:;])\s", t, maxsplit=1)[0]
    return (corte[:limite] + "…") if len(corte) > limite else corte


def itens_em_aberto(raiz):
    """Cada marcador de 1o nivel da secao `## Em aberto` vira um item de backlog."""
    m = re.search(r"(?ms)^## Em aberto\s*\n(.*?)(?=^## |\Z)", _ler(Path(raiz) / "history.md"))
    if not m:
        return []
    itens, atual, pai = [], [], None
    for linha in m.group(1).splitlines():
        if linha.startswith("> "):          # notas de higiene da seção, não são itens
            continue
        if linha.strip() == "---":          # fim da seção; sem isto o traço entrava no detalhe
            break
        # Sub-item INDENTADO vira card proprio, com o pai como contexto. A 1a versao tratava
        # indentacao como continuacao, e os 9 sub-itens de "Backlog ativo" viravam UM card so'.
        # Pior que perder granularidade: acrescentar sub-item mudava o detalhe e nao o titulo, e o
        # `--verificar` (que compara titulos) seguia dizendo "em dia" com o CSV velho. Trabalho
        # novo nunca virava card e nada apitava. Achado ALTO do qa-critic (Fable, 2026-08-16).
        sub = re.match(r"^\s{2,}[-*]\s+(.*)$", linha)
        topo = re.match(r"^[-*]\s+(.*)$", linha)
        if topo:
            if atual:
                itens.append((pai, " ".join(atual)))
            pai, atual = None, [topo.group(1).strip()]
        elif sub:
            if atual:
                itens.append((pai, " ".join(atual)))
                pai = _titulo(" ".join(atual), 60) if pai is None else pai
            atual = [sub.group(1).strip()]
        elif atual and linha.strip():
            atual.append(linha.strip())
    if atual:
        itens.append((pai, " ".join(atual)))
    saida = []
    for p_, t in itens:
        if not t.strip():
            continue
        titulo = _titulo(t)
        saida.append({"origem": "history.md · Em aberto" + (f" › {p_}" if p_ else ""),
                      "titulo": (f"{p_} · {titulo}" if p_ else titulo)[:140],
                      "detalhe": t.strip(), "tipo": "dívida", "prioridade": 2})
    return saida


def adrs_propostos(raiz):
    d = Path(raiz) / "docs" / "adr"
    fora = []
    if not d.is_dir():
        return fora
    for f in sorted(d.glob("*.md")):
        if f.name.startswith("000"):
            continue
        txt = _ler(f)
        if re.search(r"(?im)^\s*-?\s*\**Status:\**\s*\**Proposto", txt):
            cab = next((l.lstrip("# ").strip() for l in txt.splitlines() if l.startswith("# ")),
                       f.name)
            fora.append({"origem": f"docs/adr/{f.name}", "titulo": _titulo(cab),
                         "detalhe": f"Decisão registrada e não ratificada. Bloqueia implementar em "
                                    f"cima dela. Arquivo: docs/adr/{f.name}",
                         "tipo": "decisão do dono", "prioridade": 1})
    return fora


def passivo_capacidades(raiz):
    """Um item AGREGADO, não 53 linhas: o quadro precisa caber na cabeça de quem o lê."""
    try:
        d = json.loads(_ler(Path(raiz) / "capabilities.json") or "{}")
        caps = d.get("capabilities", d) if isinstance(d, dict) else d
    except json.JSONDecodeError:
        return []
    sem_prova = [c for c in caps
                 if c.get("enforcement") == "fail-closed" and not c.get("mutacao")]
    sem_campo = [c for c in caps if not c.get("enforcement")]
    total = len(sem_prova) + len(sem_campo)
    if not total:
        return []
    return [{"origem": "capabilities.json", "tipo": "dívida",
             "titulo": f"Passivo de prova: {total} capacidades sem gate provado",
             "detalhe": (f"{len(sem_prova)} declaram bloquear falha e nunca foram sabotadas para "
                         f"conferir que o teste apita; {len(sem_campo)} não declaram como se "
                         f"protegem e são invisíveis à auditoria. Migram uma a uma, cada uma só "
                         f"entra no registro depois da prova passar. Comando: "
                         f"python tools/audit_enforcement.py --passivo"),
             "prioridade": 2}]


def backlog(raiz):
    itens = adrs_propostos(raiz) + itens_em_aberto(raiz) + passivo_capacidades(raiz)
    for i, it in enumerate(itens, 1):
        it["id"] = f"B{i:03d}"
    return itens


def releases(raiz, n=5):
    saida = []
    for m in re.finditer(r"(?m)^##\s*\[(\d+\.\d+\.\d+)\]\s*—\s*(\S+)\s*—\s*(.+)$",
                         _ler(Path(raiz) / "CHANGELOG.md")):
        saida.append({"versao": m.group(1), "data": m.group(2), "titulo": _titulo(m.group(3), 95)})
        if len(saida) >= n:
            break
    return saida


def estado(raiz):
    canarios = "não executada nesta geração"
    alvo = Path(raiz) / "tools" / "run_canaries.py"
    if alvo.is_file():
        try:
            # `-X utf8` no filho: sem isso ele emite na codificacao do console e o
            # relatorio sai com acento quebrado — documento com mojibake e' descartado
            # na primeira olhada, entao isto nao e' cosmetico.
            r = subprocess.run([sys.executable, "-X", "utf8", str(alvo)],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", cwd=str(raiz), timeout=600,
                               stdin=subprocess.DEVNULL)
            linha = [l for l in (r.stdout or "").splitlines() if l.startswith("RESULTADO:")]
            canarios = linha[-1].replace("RESULTADO:", "").strip() if linha else "sem resultado"
        except (OSError, subprocess.SubprocessError):
            canarios = "não consegui executar"
    return {
        "branch": _git(raiz, "rev-parse", "--abbrev-ref", "HEAD") or "?",
        "commit": _git(raiz, "log", "-1", "--format=%h %s") or "?",
        # So tags de release v1.x: `--sort=-v:refname` sozinho trazia v2.3.0, que e' a tag
        # do roteador e nao da release — numero maior, significado diferente.
        "tag": (_git(raiz, "tag", "--list", "v1.*", "--sort=-v:refname")
                or "").splitlines()[:1],
        "nao_pushados": _git(raiz, "rev-list", "--count", "@{upstream}..HEAD") or "?",
        "sujo": bool(_git(raiz, "status", "--porcelain")),
        "canarios": canarios,
    }


def _tabelas(itens):
    """(nome, linhas, colunas) de cada CSV. UMA fonte para gerar e para verificar — se as duas
    montassem a tabela cada uma do seu jeito, o verificador compararia contra outra coisa."""
    backlog_linhas = [{
        "Card name": i["titulo"], "Task Name": i["titulo"],
        "Description": i["detalhe"], "Notes": i["detalhe"],
        "Labels": i["tipo"], "Bucket Name": i["tipo"],
        "Priority": {1: "Urgent", 2: "Important", 3: "Medium"}.get(i["prioridade"], "Medium"),
        "id": i["id"], "origem": i["origem"]} for i in itens]
    crono_linhas = sorted(({"id": i["id"], "item": i["titulo"], "tipo": i["tipo"],
                            "prioridade": i["prioridade"], "origem": i["origem"],
                            "responsavel": "dono" if i["tipo"] == "decisão do dono" else "squad",
                            "estado": "aberto"} for i in itens),
                          key=lambda x: (x["prioridade"], x["id"]))
    return [("backlog.csv", backlog_linhas,
             ["id", "Card name", "Task Name", "Description", "Notes", "Labels", "Bucket Name",
              "Priority", "origem"]),
            ("cronograma.csv", crono_linhas,
             ["id", "item", "tipo", "prioridade", "responsavel", "estado", "origem"])]


def _csv_texto(linhas, colunas):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=colunas, extrasaction="ignore",
                       lineterminator=chr(10))
    w.writeheader()
    for l in linhas:
        w.writerow(l)
    return buf.getvalue()


def escrever_csv(destino, linhas, colunas):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=colunas, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for l in linhas:
        w.writerow(l)
    # utf-8-sig: sem o BOM o Excel em português abre acento quebrado, e aí o quadro é descartado
    # na primeira olhada. Trello e Planner ignoram o BOM.
    Path(destino).write_text(buf.getvalue(), encoding="utf-8-sig")


def gerar(raiz):
    raiz = Path(raiz)
    out = raiz / SAIDA
    out.mkdir(parents=True, exist_ok=True)
    itens = backlog(raiz)

    # Trello importa "Card name"/"Description"; Planner importa "Task Name"/"Notes".
    # As duas grafias na mesma planilha para nao obrigar ninguem a renomear coluna.
    for nome, linhas, cols in _tabelas(itens):
        escrever_csv(out / nome, linhas, cols)

    (out / "STATUS-REPORT.md").write_text(status_report(raiz, itens), encoding="utf-8")
    return [out / "backlog.csv", out / "cronograma.csv", out / "STATUS-REPORT.md"]


def status_report(raiz, itens=None, com_estado=True):
    itens = backlog(raiz) if itens is None else itens
    # `com_estado=False` no --verificar: montar 'Estado agora' roda a suite inteira
    # (98s medidos pelo qa-critic) e o resultado e' DESCARTADO pela comparacao. Pior:
    # o gate de fechamento chamava com timeout de 120s e `except: pass`, entao um dia
    # lento deixava quadro desatualizado passar em silencio — fail-open por timeout.
    e = estado(raiz) if com_estado else {'branch': '-', 'commit': '-', 'tag': [],
                                         'nao_pushados': '-', 'sujo': False,
                                         'canarios': '-'}
    rels = releases(raiz)
    do_dono = [i for i in itens if i["tipo"] == "decisão do dono"]
    L = ["# Status report", "",
         "> Gerado por `python tools/projeto_docs.py` a partir do estado real do repositório.",
         "> Não é digitado: se o dado mudar, este arquivo muda na próxima execução.", "",
         "## Onde chegamos", ""]
    if rels:
        L += ["| release | data | o quê |", "|---|---|---|"]
        L += [f"| {r['versao']} | {r['data']} | {r['titulo']} |" for r in rels]
    else:
        L.append("_sem releases registradas no CHANGELOG._")
    L += ["", "## Estado agora", "",
          f"- Branch **{e['branch']}**, commit `{e['commit']}`",
          f"- Última tag: **{e['tag'][0] if e['tag'] else 'nenhuma'}**",
          f"- Commits não enviados: **{e['nao_pushados']}**",
          f"- Árvore de trabalho: **{'com alterações não commitadas' if e['sujo'] else 'limpa'}**",
          f"- Canários: **{e['canarios']}**", "",
          "## O que falta", ""]
    if itens:
        L += ["| id | item | tipo | quem |", "|---|---|---|---|"]
        for i in sorted(itens, key=lambda x: (x["prioridade"], x["id"])):
            quem = "**dono**" if i["tipo"] == "decisão do dono" else "squad"
            L.append(f"| {i['id']} | {i['titulo']} | {i['tipo']} | {quem} |")
    else:
        L.append("_nada em aberto._")
    L += ["", "## Ação", ""]
    if do_dono:
        L.append(f"**{len(do_dono)} item(ns) dependem de decisão do dono** — nada avança neles "
                 f"sem isso:")
        L += [f"- {i['id']} — {i['titulo']}" for i in do_dono]
    else:
        L.append("Nenhum item bloqueado por decisão do dono. O squad segue pelo backlog acima.")
    L += ["", "## Detalhe dos itens", ""]
    for i in sorted(itens, key=lambda x: (x["prioridade"], x["id"])):
        L += [f"### {i['id']} — {i['titulo']}", "", f"_{i['origem']}_", "", i["detalhe"], ""]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Documentacao de gestao derivada do estado real.")
    ap.add_argument("--repo", default=str(RAIZ_PADRAO))
    ap.add_argument("--status", action="store_true", help="so imprime o status report")
    ap.add_argument("--verificar", action="store_true",
                    help="os arquivos gerados estao em dia com as fontes?")
    a = ap.parse_args(argv)
    raiz = Path(a.repo)

    if a.status:
        print(status_report(raiz))
        return 0

    if a.verificar:
        atual = status_report(raiz, com_estado=False)
        gravado = _ler(raiz / SAIDA / "STATUS-REPORT.md")
        # Comparar tambem os CSV, byte a byte contra o que seria gerado agora. A 1a versao so'
        # olhava o relatorio, entao apagar ou editar a mao um CSV passava verde — e o relatorio
        # compara apenas TITULOS, entao mudanca em sub-item tambem escapava. Achado ALTO do
        # qa-critic (Fable, 2026-08-16).
        itens_agora = backlog(raiz)
        for nome, linhas, cols in _tabelas(itens_agora):
            alvo = raiz / SAIDA / nome
            try:                                  # utf-8-sig na LEITURA tambem: o arquivo e'
                gravado_csv = alvo.read_text(     # gravado com a marca para o Excel, e compara-lo
                    encoding="utf-8-sig")         # sem descontar a marca nunca daria igual
            except OSError:
                gravado_csv = ""
            if _csv_texto(linhas, cols) != gravado_csv:
                print(f"[projeto-docs] DESATUALIZADO: {nome} diverge das fontes.")
                print("  Rode: python tools/projeto_docs.py")
                return 1
        # A seção "Estado agora" muda a cada commit e a cada execução da suíte — comparar o
        # arquivo inteiro daria "desatualizado" sempre, e um verificador que sempre reclama e' um
        # verificador que ninguem le. Compara o que so' muda quando o TRABALHO muda.
        def so_backlog(t):
            m = re.search(r"(?ms)^## O que falta\s*\n(.*?)(?=^## Ação)", t)
            return (m.group(1).strip() if m else t)
        if not gravado:
            print(f"[projeto-docs] {SAIDA}/STATUS-REPORT.md nao existe — rode sem --verificar.")
            return 1
        if so_backlog(atual) != so_backlog(gravado):
            print("[projeto-docs] DESATUALIZADO: o backlog mudou desde a ultima geracao.")
            print("  Rode: python tools/projeto_docs.py")
            return 1
        print("[projeto-docs] em dia com as fontes.")
        return 0

    gerados = gerar(raiz)
    print(f"[projeto-docs] gerados em {SAIDA}/:")
    for g in gerados:
        print(f"  {g.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
