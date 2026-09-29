#!/usr/bin/env python3
"""plano.py — verificador do plano no arquivo único de especificação (B2b, ADR-125).

Reprova o que torna o plano enganoso para quem o lê (regra: o dono decide pelo painel):
  1. seção obrigatória ausente (Painel, Resumo executivo, Partes A e B, Decisões, Tarefas, Mapa de impacto,
     Replanejamento, Revisões adversariais);
  2. decisão pendente no Painel sem "Quem age";
  3. tarefa `[x]` sem prova (a palavra "prova", um PR `#nn` ou um arquivo citado entre crases);
     tarefa `[~]` sem linha no Replanejamento que a cite;
  4. percentual do "**Avanço:**" que não bate com a contagem das tarefas do bloco (tolerância de 5 pontos);
  5. Mapa de impacto sem linhas, ou item que muda ("sim") sem situação;
  6. aceite datado antes da aprovação dos requisitos (Parte B);
  7. painel de fases (entre `<!-- painel:inicio -->` e `<!-- painel:fim -->`) diferente do que as tarefas geram —
     % editado à mão ou tarefa marcada sem regenerar;
  8. cronograma: `prazo:` ilegível, `depende:` de tarefa inexistente, prazo antes do prazo da dependência.

Cronograma: na linha da tarefa, `prazo: dd/mm/aaaa` e, se houver, `depende: T1, T2`.

Uso:
    python tools/plano.py verificar [<spec.md> ...]   # sem argumento: todos os spec.md únicos de docs/specs
    python tools/plano.py verificar <spec.md> --avisar # só avisa (exit 0): uso fora deste repositório
    python tools/plano.py painel <spec.md> [--escrever] # fases com contagem, barra e % (grava entre os marcadores)
    python tools/plano.py cronograma <spec.md> [--csv <arquivo>]   # tarefas por prazo, com atraso na data de hoje
Exit 1 com achado (0 com --avisar).
"""
import datetime
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_fonte  # noqa: E402

SECOES = [("##", "Painel"), ("##", "Resumo executivo"), ("#", "Parte A"), ("#", "Parte B"), ("#", "Decisões"),
          ("#", "Tarefas"), ("#", "Mapa de impacto"), ("#", "Replanejamento"), ("#", "Revisões adversariais")]
_DATA = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
_PROVA = re.compile(r"(?i)\bprova\b|#\d{2,}|`[^`]+\.(?:py|md|json|xlsx|csv|html|docx|sql|ps1|sh|txt)`")
_TAREFA = re.compile(r"^\s*-\s*\[([ xX~])\]\s*(T[\w.-]*\d[\w.-]*)?\s*(.*)$")
_VAZIO = {"", "—", "-", "n/a"}


def _vazio(v):
    v = (v or "").strip()
    return v.lower() in _VAZIO or bool(re.fullmatch(r"<[^>]*>", v))


def _data(txt):
    for d, m, a in _DATA.findall(txt or ""):
        try:
            return datetime.date(int(a), int(m), int(d))
        except ValueError:
            pass
    return None


def _celulas(ln):
    return [c.strip() for c in re.split(r"(?<!\\)\|", ln.strip().strip("|"))]


def _blocos(texto):
    """{título de H1 ou H2 (fora de código): [linhas até o próximo H1 ou H2]}. `###` fica dentro do bloco."""
    out, atual = {}, None
    for ln, fora, _h1 in spec_fonte._linhas_classificadas(texto):
        m = re.match(r"^(#{1,2})\s+(.+?)\s*$", ln) if fora else None
        if m:
            atual = m.group(2)
            out.setdefault(atual, [])
            continue
        if atual is not None and fora:  # exemplo dentro de bloco de código não é tarefa nem linha de tabela
            out[atual].append(ln)
    return out


def _secao(blocos, prefixo):
    return next((v for k, v in blocos.items() if k.lower().startswith(prefixo.lower())), None)


MARCA_INI, MARCA_FIM = "<!-- painel:inicio -->", "<!-- painel:fim -->"
_PRAZO = re.compile(r"(?i)\bprazo:\s*(\S+)")
_DEPENDE = re.compile(r"(?i)\bdepende:\s*((?:T[\w.-]*\d[\w.-]*(?:\s*,\s*|\s+e\s+|\s*))+)")
_ID = re.compile(r"T[\w.-]*\d[\w.-]*")
BARRA = 12


def tarefas(texto):
    """Tarefas da seção Tarefas, na ordem: bloco (`### `), marca, id, texto, prazo (cru e data), dependências."""
    out, grupo = [], "(sem bloco)"
    for ln in _secao(_blocos(texto), "Tarefas") or []:
        if ln.startswith("### "):
            grupo = ln[4:].strip()
            continue
        m = _TAREFA.match(ln)
        if not m:
            continue
        mp, md = _PRAZO.search(ln), _DEPENDE.search(ln)
        out.append({"grupo": grupo, "marca": m.group(1).lower(), "id": m.group(2) or "", "texto": m.group(3).strip(),
                    "linha": ln, "prazo_cru": mp.group(1).rstrip(".,;") if mp else "",
                    "prazo": _data(mp.group(1)) if mp else None,
                    "depende": [d.rstrip(".,;-") for d in _ID.findall(md.group(1))] if md else []})
    return out


def painel(texto):
    """Tabela de fases gerada das tarefas: feitas/total, barra de 12 blocos, %, e onde estamos (1ª fase aberta)."""
    grupos = {}
    for t in tarefas(texto):
        if t["marca"] != "~":
            grupos.setdefault(t["grupo"], []).append(t["marca"] == "x")
    linhas, onde = ["| Fase | Feitas | Andamento | % |", "|---|---|---|---|"], None
    for g, feitas in grupos.items():
        n, f = len(feitas), sum(feitas)
        pct = round(100 * f / n)
        cheio = round(pct * BARRA / 100)
        marca = ""
        if onde is None and f < n:
            onde, marca = g, " ◀ onde estamos"
        linhas.append(f"| {g}{marca} | {f}/{n} | `{'█' * cheio}{'░' * (BARRA - cheio)}` | {pct}% |")
    return "\n".join(linhas)


def _painel_escrito(texto):
    """(conteúdo entre os marcadores ou None, erro de marcador ou None)."""
    ni, nf = texto.count(MARCA_INI), texto.count(MARCA_FIM)
    if ni == nf == 0:
        return None, None
    i, j = texto.find(MARCA_INI), texto.find(MARCA_FIM)
    if ni != 1 or nf != 1 or i > j:
        return None, (f"marcadores do painel inválidos ({ni} de início, {nf} de fim, "
                      f"{'fim antes do início' if i > j else 'fora de par'}) — deixe um par e rode painel --escrever")
    return texto[i + len(MARCA_INI):j].strip(), None


def escrever_painel(spec):
    texto = open(spec, encoding="utf-8-sig").read()
    bloco = f"{MARCA_INI}\n{painel(texto)}\n{MARCA_FIM}"
    escrito, erro = _painel_escrito(texto)
    if erro:
        raise ValueError(erro)
    i, j = texto.find(MARCA_INI), texto.find(MARCA_FIM)
    if escrito is not None:
        novo = texto[:i] + bloco + texto[j + len(MARCA_FIM):]
    else:
        m = re.search(r"(?m)^## Painel[ \t]*$", texto)
        if not m:
            raise ValueError("sem '## Painel' para receber o painel de fases")
        novo = texto[:m.end()] + "\n\n" + bloco + texto[m.end():]
    with open(spec, "w", encoding="utf-8") as fh:
        fh.write(novo)


def cronograma(texto, hoje=None):
    """Linhas do cronograma ordenadas por prazo (sem prazo por último)."""
    hoje = hoje or datetime.date.today()
    linhas = []
    for t in tarefas(texto):
        sit = {"x": "feita", "~": "replanejada"}.get(t["marca"], "aberta")
        if sit == "aberta" and t["prazo"] and t["prazo"] < hoje:
            sit = "ATRASADA"
        linhas.append({"prazo": t["prazo"], "tarefa": (t["id"] + " " + t["texto"][:70]).strip(), "fase": t["grupo"],
                       "situacao": sit, "depende": ", ".join(t["depende"])})
    return sorted(linhas, key=lambda x: (x["prazo"] is None, x["prazo"] or datetime.date.max))


def _achados_cronograma(texto):
    ts = tarefas(texto)
    por_id = {t["id"]: t for t in ts if t["id"]}
    ach = []
    for t in ts:
        nome = t["id"] or t["texto"][:40]
        if t["prazo_cru"] and t["prazo"] is None:
            ach.append(f"tarefa {nome}: prazo '{t['prazo_cru']}' ilegível (use dd/mm/aaaa)")
        for d in t["depende"]:
            dep = por_id.get(d)
            if dep is None:
                ach.append(f"tarefa {nome} depende de {d}, que não existe nas Tarefas")
            elif t["prazo"] and dep["prazo"] and t["prazo"] < dep["prazo"]:
                ach.append(f"tarefa {nome} tem prazo {t['prazo']:%d/%m/%Y}, antes de {d} de quem depende "
                           f"({dep['prazo']:%d/%m/%Y})")
    return ach


def verificar(spec):
    texto = open(spec, encoding="utf-8-sig").read()
    spec_fonte.validar_unico(texto)
    blocos = _blocos(texto)
    ach = []
    for _nivel, nome in SECOES:
        if _secao(blocos, nome) is None:
            ach.append(f"seção obrigatória ausente: {nome}")

    sec_painel = _secao(blocos, "Painel") or []
    cab = None
    for ln in sec_painel:
        if not ln.strip().startswith("|") or re.match(r"^\|?\s*:?-{3,}", ln.strip()):
            continue
        cel = _celulas(ln)
        if cab is None:
            cab = [c.lower() for c in cel]
            continue
        linha = dict(zip(cab, cel))
        sit = linha.get("situação", "")
        if re.search(r"(?i)pendente|⏳|aguard", sit) and _vazio(linha.get("quem age", "")):
            ach.append(f"Painel {linha.get('#', '?')}: decisão pendente sem 'Quem age'")

    tarefas = _secao(blocos, "Tarefas") or []
    replan = "\n".join(_secao(blocos, "Replanejamento") or [])
    grupos, grupo = {}, "(sem bloco)"
    for ln in tarefas:
        if ln.startswith("### "):
            grupo = ln[4:].strip()
            continue
        m = _TAREFA.match(ln)
        if not m:
            continue
        marca, tid, resto = m.group(1).lower(), m.group(2) or "", m.group(3)
        grupos.setdefault(grupo, []).append(marca)
        if marca == "x" and not _PROVA.search(ln):
            ach.append(f"tarefa {tid or resto[:40]} marcada [x] sem prova (cite 'prova:', o PR ou o arquivo)")
        if marca == "~" and tid and tid not in replan:
            ach.append(f"tarefa {tid} replanejada [~] sem linha no Replanejamento que a cite")

    avanco = next((ln for ln in sec_painel if "**Avanço:**" in ln), "")
    for nome, pct in re.findall(r"([A-Za-zÀ-ÿ0-9][\w.\-]*)\s+(\d{1,3})\s*%", avanco):
        chave = next((g for g in grupos if g.split()[0].lower().rstrip("—-") == nome.lower()), None)
        if chave is None:
            continue  # bloco sem lista de tarefas aqui: nada a comparar
        marcas = [x for x in grupos[chave] if x != "~"]
        if not marcas:
            continue
        real = round(100 * sum(1 for x in marcas if x == "x") / len(marcas))
        if abs(real - int(pct)) > 5:
            ach.append(f"Avanço de {nome}: painel diz {pct}%, as tarefas dão {real}% "
                       f"({sum(1 for x in marcas if x == 'x')} de {len(marcas)})")

    mapa = _secao(blocos, "Mapa de impacto")
    if mapa is not None:
        linhas = [_celulas(ln) for ln in mapa if ln.strip().startswith("|") and not re.match(r"^\|?\s*:?-{3,}", ln.strip())]
        dados = linhas[1:] if linhas else []
        if not dados:
            ach.append("Mapa de impacto sem linhas")
        for c in dados:
            if len(c) >= 3 and re.match(r"(?i)\s*sim", c[1]) and _vazio(c[2]):
                ach.append(f"Mapa de impacto: '{c[0]}' muda e está sem situação")

    parte_b = "\n".join(_secao(blocos, "Parte B") or [])
    m_ap = re.search(r"\*\*Requisitos aprovados pelo dono em:\*\*[ \t]*([^·\n]+)", parte_b)  # [ \t]: vazio não
    m_ac = re.search(r"\*\*Aceite escrito em:\*\*[ \t]*([^·\n]+)", parte_b)                  # lê a linha seguinte
    d_ap, d_ac = _data(m_ap.group(1) if m_ap else ""), _data(m_ac.group(1) if m_ac else "")
    if d_ap and d_ac and d_ac < d_ap:
        ach.append(f"aceite escrito em {d_ac:%d/%m/%Y}, antes da aprovação dos requisitos ({d_ap:%d/%m/%Y})")

    escrito, erro = _painel_escrito(texto)
    if erro:
        ach.append(erro)
    elif escrito is not None and escrito != painel(texto):
        ach.append("painel de fases diferente do que as tarefas geram (% editado à mão ou tarefa marcada sem "
                   "regenerar) — rode: python tools/plano.py painel <spec.md> --escrever")
    ach += _achados_cronograma(texto)
    return ach


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if len(argv) >= 3 and argv[1] in ("painel", "cronograma"):
        spec = argv[2]
        texto = open(spec, encoding="utf-8-sig").read()
        spec_fonte.validar_unico(texto)
        if argv[1] == "painel":
            if "--escrever" in argv:
                escrever_painel(spec)
                print(f"painel gravado em {spec}")
            else:
                print(painel(texto))
            return 0
        linhas = cronograma(texto)
        if "--csv" in argv:
            import csv
            destino = argv[argv.index("--csv") + 1]
            with open(destino, "w", encoding="utf-8-sig", newline="") as fh:
                w = csv.writer(fh, delimiter=";")
                w.writerow(["Prazo", "Tarefa", "Fase", "Situação", "Depende de"])
                for x in linhas:
                    w.writerow([f"{x['prazo']:%d/%m/%Y}" if x["prazo"] else "", x["tarefa"], x["fase"],
                                x["situacao"], x["depende"]])
            print(f"cronograma gravado em {destino}")
            return 0
        print("| Prazo | Tarefa | Fase | Situação | Depende de |\n|---|---|---|---|---|")
        for x in linhas:
            p = f"{x['prazo']:%d/%m/%Y}" if x["prazo"] else "—"
            print(f"| {p} | {x['tarefa']} | {x['fase']} | {x['situacao']} | {x['depende'] or '—'} |")
        return 0
    if len(argv) < 2 or argv[1] != "verificar":
        print(__doc__)
        return 2
    avisar = "--avisar" in argv
    alvos = [a for a in argv[2:] if not a.startswith("--")]
    if not alvos:
        alvos = [p for p in spec_fonte.alvos_unicos(ROOT) if "_template" not in p.replace("\\", "/")]
    total = 0
    for spec in alvos:
        try:
            ach = verificar(spec)
        except (OSError, spec_fonte.SpecInvalida) as e:
            ach = [f"ilegível: {e}"]
        rel = os.path.relpath(spec, ROOT)
        print(f"{'FAIL' if ach else 'OK  '} {rel}")
        for a in ach:
            print(f"   - {a}")
        total += len(ach)
    print("-" * 50)
    print("RESULTADO:", (f"{'AVISO' if avisar else 'FAIL'} ({total})" if total else "PASS"))
    return 1 if (total and not avisar) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
