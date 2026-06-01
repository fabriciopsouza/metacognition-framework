#!/usr/bin/env python3
"""Linter de PROFUNDIDADE de spec — barra J1 se a elicitação não cobrir as dimensões (ADR-033).

GAP de campo (causa-raiz nº1): o agente fez perguntas de "coletor de requisitos" (escopo,
entrada, stack, oráculo) e NÃO endereçou produto — quem opera, interface, escopo acumulado,
persistência, log. Mesmo com a instrução de discovery em prosa, ela foi ignorada. A correção
é mecânica: um gate que **falha (exit 1)** se o `requirements.md` não registra uma DECISÃO para
cada dimensão obrigatória do banco agnóstico (`_shared/discovery/elicitation-dimensions.md`).

Verifica **cobertura de dimensão** (a dimensão foi endereçada), NÃO a qualidade da decisão
(isso é domínio/julgamento adversarial — declarado em LIMITS.md). É o equivalente do
`validate_skills.py` para completude de elicitação, wirado como gate antes de J1 (discovery→architect).

Uso:
    python tools/check_spec_depth.py <requirements.md> [...]   # checa specs dadas (uso do gate)
    python tools/check_spec_depth.py                            # checa docs/specs/**/requirements.md

Exit 0 se toda spec cobre as dimensões obrigatórias; 1 se alguma deixou dimensão sem decisão.
Sem dependências externas.
"""
import glob
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK_PATH = os.path.join(ROOT, "_shared", "discovery", "elicitation-dimensions.md")

# Decisões que NÃO contam como "endereçada" (placeholder/lacuna não-decidida).
PLACEHOLDERS = {"", "todo", "tbd", "...", "?", "-", "—", "(preencher)", "preencher",
                "a preencher", "xxx", "n/d", "tba"}


def _norm(s):
    """Lower + sem acento + colapsa espaço — para casar chave/alias de forma tolerante."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s.strip().lower())


def load_bank(path=BANK_PATH):
    """Lê a tabela machine-readable do banco. Retorna lista de dicts {key, aliases:set, obr:bool}."""
    dims = []
    with open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            if not line.lstrip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            key = _norm(cells[0])
            # pula header e separador
            if key in ("chave", "") or set(cells[0].strip()) <= {"-", ":", " "}:
                continue
            aliases = {_norm(a) for a in cells[1].split(",") if a.strip()}
            obr = _norm(cells[2]) in ("sim", "s", "yes", "true", "obrigatoria", "obrigatória")
            dims.append({"key": key, "aliases": aliases | {key}, "obr": obr})
    return dims


def extract_dim_section(text):
    """Retorna as linhas da seção de dimensões de elicitação (heading com 'elicit' ou 'dimens').
    Vazio se a seção não existe."""
    lines = text.splitlines()
    out = []
    in_sec = False
    sec_level = 0
    for ln in lines:
        h = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if h:
            title = _norm(h.group(2))
            if not in_sec and ("elicit" in title or "dimens" in title):
                in_sec = True
                sec_level = len(h.group(1))
                continue
            if in_sec and len(h.group(1)) <= sec_level:
                break  # próxima heading de nível igual/superior fecha a seção
        if in_sec:
            out.append(ln)
    return out


def parse_rows(section_lines):
    """Extrai pares (label_norm, decisao) de linhas de lista/tabela/plain da seção."""
    rows = []
    for ln in section_lines:
        s = ln.strip()
        if not s:
            continue
        # tabela: | label | decisão | ...
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) >= 2 and set(cells[0]) - {"-", ":", " "}:
                if _norm(cells[0]) not in ("chave", "dimensao", "dimensão"):
                    rows.append((_norm(cells[0]), " ".join(cells[1:]).strip()))
            continue
        # lista/plain: -/* **label**: decisão   ou   label: decisão
        m = re.match(r"^[-*\s]*\*{0,2}([\wçãõáéíóúâêô/ -]+?)\*{0,2}\s*[:=→]\s*(.*)$", s, re.IGNORECASE)
        if m:
            rows.append((_norm(m.group(1)), m.group(2).strip()))
    return rows


def is_addressed(decision):
    d = _norm(decision)
    if d in PLACEHOLDERS:
        return False
    # convenção deste repo: `<...>` é placeholder de template (ex.: `product_type: <tipo>`,
    # `<feature>`). Qualquer valor angle-bracketed = dimensão NÃO decidida.
    if d.startswith("<") and d.endswith(">"):
        return False
    # `(preencher)` e variantes parentéticas de lacuna
    if re.fullmatch(r"\(.*\)", d) and re.search(r"preench|todo|tbd|a definir", d):
        return False
    return bool(re.search(r"[a-z0-9]", d))


def check_spec(path, dims):
    """Retorna (ok, faltando_obr, avisos_rec)."""
    try:
        with open(path, encoding="utf-8-sig") as fh:
            text = fh.read()
    except OSError as e:
        return False, [f"<erro io: {e}>"], []
    section = extract_dim_section(text)
    rows = parse_rows(section)
    covered = set()
    for label, decision in rows:
        if not is_addressed(decision):
            continue
        for d in dims:
            # casamento EXATO label↔alias (substring causava falso-PASS: 'ui'⊂'req(ui)sitos',
            # 'saida'⊂'recortes-saida' creditavam dimensões erradas — process-critic ADR-011)
            if label in d["aliases"]:
                covered.add(d["key"])
    faltando_obr = [d["key"] for d in dims if d["obr"] and d["key"] not in covered]
    avisos_rec = [d["key"] for d in dims if not d["obr"] and d["key"] not in covered]
    if not section:
        # nenhuma seção de dimensões → nada coberto (regressão: spec "calcular X" sem elicitação)
        faltando_obr = [d["key"] for d in dims if d["obr"]]
    return (len(faltando_obr) == 0), faltando_obr, avisos_rec


def main(argv):
    dims = load_bank()
    if not dims:
        print("banco de dimensões vazio/ilegível — nada a verificar", file=sys.stderr)
        return 1
    targets = argv[1:]
    if not targets:
        targets = glob.glob(os.path.join(ROOT, "docs", "specs", "**", "requirements.md"), recursive=True)
        targets = [t for t in targets if "_template" not in t]
    if not targets:
        print("nenhum requirements.md para checar (gate só dispara quando há spec).")
        return 0
    obr_total = sum(1 for d in dims if d["obr"])
    any_fail = False
    for path in targets:
        try:
            rel = os.path.relpath(path, ROOT)
        except ValueError:
            rel = path
        ok, faltando, avisos = check_spec(path, dims)
        if ok:
            print(f"PASS {rel}  ({obr_total}/{obr_total} dimensões obrigatórias decididas)"
                  + (f" · recomendadas pendentes: {', '.join(avisos)}" if avisos else ""))
        else:
            any_fail = True
            print(f"FAIL {rel}  — dimensões obrigatórias SEM decisão registrada: {', '.join(faltando)}")
            print("      (registre cada uma na seção '## Dimensões de elicitação' do requirements.md)")
    print("-" * 50)
    print("RESULTADO:", "FAIL (gate barra J1: spec rasa)" if any_fail
          else "PASS (toda spec cobre as dimensões obrigatórias)")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
