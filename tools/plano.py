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
  6. aceite datado antes da aprovação dos requisitos (Parte B).

Uso:
    python tools/plano.py verificar [<spec.md> ...]   # sem argumento: todos os spec.md únicos de docs/specs
    python tools/plano.py verificar <spec.md> --avisar # só avisa (exit 0): uso fora deste repositório
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
        if atual is not None:
            out[atual].append(ln)
    return out


def _secao(blocos, prefixo):
    return next((v for k, v in blocos.items() if k.lower().startswith(prefixo.lower())), None)


def verificar(spec):
    texto = open(spec, encoding="utf-8-sig").read()
    spec_fonte.validar_unico(texto)
    blocos = _blocos(texto)
    ach = []
    for _nivel, nome in SECOES:
        if _secao(blocos, nome) is None:
            ach.append(f"seção obrigatória ausente: {nome}")

    painel = _secao(blocos, "Painel") or []
    cab = None
    for ln in painel:
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

    avanco = next((ln for ln in painel if "**Avanço:**" in ln), "")
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
    m_ap = re.search(r"\*\*Requisitos aprovados pelo dono em:\*\*\s*([^·\n]+)", parte_b)
    m_ac = re.search(r"\*\*Aceite escrito em:\*\*\s*([^·\n]+)", parte_b)
    d_ap, d_ac = _data(m_ap.group(1) if m_ap else ""), _data(m_ac.group(1) if m_ac else "")
    if d_ap and d_ac and d_ac < d_ap:
        ach.append(f"aceite escrito em {d_ac:%d/%m/%Y}, antes da aprovação dos requisitos ({d_ap:%d/%m/%Y})")
    return ach


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
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
