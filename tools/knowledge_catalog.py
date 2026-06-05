#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""knowledge_catalog.py — catálogo de insights + RAG léxico sobre corpus de relatórios.

ADR-068: retroalimentação do corpus de execution-reports (ADR-062..065).
Parse offline → catalog.json + session-insights.md + patterns.md.
BM25 stdlib puro (sem dep externa — ADR-029 decisão #4).

Uso:
  python tools/knowledge_catalog.py --build [--intake-dir PATH] [--out-dir PATH]
  python tools/knowledge_catalog.py --recall --context "keywords"
  python tools/knowledge_catalog.py --recall --from-briefing docs/briefing.md
  python tools/knowledge_catalog.py --patterns [--out-dir PATH]

Exit 0 ok; 1 erro; 2 catálogo vazio.

INVARIANTE ANTI-FABRICAÇÃO: nenhum campo é inventado; conteúdo ausente = lista/dict
vazio, nunca valor sintético. Relatório sem nenhuma seção de aprendizado = ignorado.
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

# ── Constantes ────────────────────────────────────────────────────────────────

DEFAULT_INTAKE = os.path.join("docs", "_private", "_intake")
DEFAULT_OUT    = os.path.join("docs", "_private", "_catalog")
TOP_N_SESSION  = 5    # entradas no session-insights.md (hook lê)
TOP_N_RECALL   = 5    # entradas no --recall
MAX_SNIPPET    = 130  # chars por bullet no output

# Fragmentos que identificam cada seção (normalizado, sem acento)
SECTION_KEYS: Dict[str, List[str]] = {
    "detecao":       ["framework x humano", "framework × humano", "detecao framework", "deteccao framework"],
    "gaps":          ["gap"],
    "melhorias":     ["melhoria"],
    "boas_praticas": ["boa pratica", "boas praticas"],
    "licoes":        ["licao por skill", "licoes por skill", "licoes novas"],
    "placar":        ["placar gate", "gate x achado", "gate × achado"],
}

KNOWN_SKILLS = ["dev", "discovery", "architect", "qa-critic", "docops", "pmo",
                "ux", "research", "spec", "docops", "evals"]


# ── Utilidades ────────────────────────────────────────────────────────────────

def _read_text(path: str) -> str:
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with open(path, "r", encoding=enc, errors="replace") as fh:
                return fh.read()
        except OSError:
            continue
    return ""


def _normalize(text: str) -> str:
    """Lowercase + remove acentos via NFKD para match de heading robusto."""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _sha8(path: str) -> str:
    return hashlib.sha256(os.path.abspath(path).encode()).hexdigest()[:8]


def _snippet(text: str, max_chars: int = MAX_SNIPPET) -> str:
    t = text.strip()
    return t if len(t) <= max_chars else t[:max_chars - 1] + "…"


def _tokenize(text: str) -> List[str]:
    """Tokenização simples: normaliza (remove acentos) + extrai alfanumérico."""
    return re.findall(r"[a-z0-9]+", _normalize(text))


# ── Parser de relatório ───────────────────────────────────────────────────────

def _split_h2_sections(text: str) -> List[Tuple[str, str]]:
    """Divide markdown em (heading, body) por '## heading'. Inclui '__header__'."""
    result: List[Tuple[str, str]] = []
    current_heading = "__header__"
    current_lines: List[str] = []
    for line in text.splitlines():
        if re.match(r"^##\s+", line):
            result.append((current_heading, "\n".join(current_lines)))
            current_heading = re.sub(r"^##\s+", "", line).strip()
            current_lines = []
        else:
            current_lines.append(line)
    result.append((current_heading, "\n".join(current_lines)))
    return result


def _section_matches(heading: str, key: str) -> bool:
    norm = _normalize(heading)
    return any(_normalize(frag) in norm for frag in SECTION_KEYS[key])


def _parse_bullets(text: str) -> List[str]:
    """Extrai texto de bullets markdown (- item / * item), remove markdown inline."""
    bullets: List[str] = []
    for line in text.splitlines():
        m = re.match(r"^\s*[-*]\s+(.+)$", line)
        if not m:
            continue
        raw = re.sub(r"\*\*(.+?)\*\*", r"\1", m.group(1))  # remove **bold**
        raw = re.sub(r"`(.+?)`", r"\1", raw)                # remove `code`
        raw = raw.strip()
        if raw and raw not in ("-", "—", ""):
            bullets.append(raw)
    return bullets


def _parse_table_col1(text: str) -> List[str]:
    """Extrai 1ª coluna de tabela markdown (ignora header + separador)."""
    rows: List[str] = []
    for line in text.splitlines():
        if not re.match(r"^\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        first = cells[0]
        # Ignora cabeçalho ("Achado", "Gate") e separador (----)
        if re.match(r"^[-: ]+$", first):
            continue
        if _normalize(first) in ("achado", "gate", "quem pegou", "gate que deveria ter pego"):
            continue
        if first:
            rows.append(first)
    return rows


def _extract_date(text: str, filename: str) -> str:
    m = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if m:
        return m.group(1)
    m = re.search(r"(20\d{2}-\d{2}-\d{2})", filename)
    if m:
        return m.group(1)
    return "desconhecido"


def _extract_skills_mentioned(text: str) -> List[str]:
    norm = _normalize(text)
    found: List[str] = []
    for s in KNOWN_SKILLS:
        if _normalize(s) in norm and s not in found:
            found.append(s)
    return found


def _extract_route(text: str) -> str:
    norm = _normalize(text)
    if "squad" in norm:
        return "squad"
    if "pontual" in norm:
        return "pontual"
    return "desconhecido"


def _parse_licoes_per_skill(text: str) -> Dict[str, List[str]]:
    """Extrai lições agrupadas por skill da forma '- **dev:** texto'."""
    result: Dict[str, List[str]] = defaultdict(list)
    for line in text.splitlines():
        m = re.match(r"^\s*[-*]\s+\*\*([^*:]+)[*:]+\*?\*?\s*(.+)$", line)
        if m:
            skill = m.group(1).strip().lower().rstrip(":")
            lesson = m.group(2).strip()
            if lesson:
                result[skill].append(lesson)
    return dict(result)


def parse_report(path: str) -> Optional[dict]:
    """Parse um execution-report .md → entrada do catálogo. None se sem conteúdo."""
    text = _read_text(path)
    if not text:
        return None

    sections = _split_h2_sections(text)

    entry: dict = {
        "report_id": _sha8(path),
        "date":       _extract_date(text, os.path.basename(path)),
        "source":     path,
        "skills":     _extract_skills_mentioned(text),
        "route":      _extract_route(text),
        "gaps":          [],
        "melhorias":     [],
        "boas_praticas": [],
        "licoes":        {},
        "detecao":       [],
        "placar":        [],
    }

    for heading, body in sections:
        for key in SECTION_KEYS:
            if not _section_matches(heading, key):
                continue
            if key == "licoes":
                grouped = _parse_licoes_per_skill(body)
                if grouped:
                    # Merge: acumula se houver várias seções de lições (ex.: continuação)
                    for sk, lics in grouped.items():
                        entry["licoes"].setdefault(sk, []).extend(lics)
                else:
                    # Fallback para bullets sem agrupamento
                    for b in _parse_bullets(body):
                        entry["licoes"].setdefault("geral", []).append(b)
            elif key == "placar":
                entry["placar"].extend(_parse_table_col1(body))
            else:
                entry[key].extend(_parse_bullets(body))

    # Texto completo para BM25 (nunca persistido em catalog.json — reconstruído no load)
    all_parts: List[str] = (
        entry["gaps"] + entry["melhorias"] + entry["boas_praticas"] + entry["detecao"] +
        [l for lls in entry["licoes"].values() for l in lls]
    )
    entry["_tokens_full"] = " ".join(all_parts)

    # Só inclui relatórios com pelo menos algum conteúdo de aprendizado
    has_content = any([
        entry["gaps"], entry["melhorias"], entry["boas_praticas"],
        entry["licoes"], entry["detecao"],
    ])
    return entry if has_content else None


def build_catalog(intake_dir: str) -> List[dict]:
    """Parse todos os .md em intake_dir → lista de entradas do catálogo."""
    if not os.path.isdir(intake_dir):
        return []
    entries: List[dict] = []
    for fname in sorted(os.listdir(intake_dir)):
        if not fname.lower().endswith(".md"):
            continue
        path = os.path.join(intake_dir, fname)
        entry = parse_report(path)
        if entry:
            entries.append(entry)
    return entries


# ── BM25 (stdlib puro — k1=1.5, b=0.75) ─────────────────────────────────────

def _build_bm25_index(entries: List[dict]) -> dict:
    tokenized = [_tokenize(e.get("_tokens_full", "")) for e in entries]
    N = len(tokenized)
    if N == 0:
        return {"N": 0, "avgdl": 1.0, "df": {}, "tokenized": []}
    avgdl = max(1.0, sum(len(d) for d in tokenized) / N)
    df: Counter = Counter()
    for doc in tokenized:
        for term in set(doc):
            df[term] += 1
    return {"N": N, "avgdl": avgdl, "df": dict(df), "tokenized": tokenized}


def _bm25_score(q_tokens: List[str], doc_tokens: List[str], idx: dict,
                k1: float = 1.5, b: float = 0.75) -> float:
    N, avgdl, df = idx["N"], idx["avgdl"], idx["df"]
    if N == 0:
        return 0.0
    tf_map = Counter(doc_tokens)
    dl = max(1, len(doc_tokens))
    score = 0.0
    for term in q_tokens:
        if term not in df:
            continue
        idf = math.log((N - df[term] + 0.5) / (df[term] + 0.5) + 1)
        tf = tf_map.get(term, 0)
        score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avgdl))
    return score


def recall(entries: List[dict], query: str, top_n: int = TOP_N_RECALL) -> List[dict]:
    """BM25 recall: retorna top-N entradas mais relevantes para query."""
    if not entries:
        return []
    idx = _build_bm25_index(entries)
    q_tokens = _tokenize(query)
    if not q_tokens:
        return entries[:top_n]
    scored = [
        (_bm25_score(q_tokens, idx["tokenized"][i], idx), i, entry)
        for i, entry in enumerate(entries)
    ]
    scored.sort(key=lambda x: -x[0])
    return [e for _, _, e in scored[:top_n]]


# ── Renderização ──────────────────────────────────────────────────────────────

def render_insights_md(entries: List[dict], header: str = "## Insights do Corpus de Aprendizado") -> str:
    """Renderiza top insights de entradas como markdown (injetado no boot)."""
    if not entries:
        return ""

    lines = [header, ""]
    lines.append("> ADR-068 · Catálogo agnóstico de processo · Rebuild: `python tools/knowledge_catalog.py --build`")
    lines.append("")

    for entry in entries:
        date = entry.get("date", "?")
        src  = os.path.basename(entry.get("source", "?"))
        skills_str = ", ".join(entry.get("skills", [])) or "?"
        lines.append(f"### [{entry['report_id']}] {date} · {src}")
        lines.append(f"> Rota: `{entry.get('route', '?')}` · Skills: {skills_str}")
        lines.append("")

        if entry.get("melhorias"):
            lines.append("**Melhorias:**")
            for m in entry["melhorias"][:3]:
                lines.append(f"- {_snippet(m)}")
            lines.append("")

        if entry.get("boas_praticas"):
            lines.append("**Boas práticas:**")
            for bp in entry["boas_praticas"][:3]:
                lines.append(f"- {_snippet(bp)}")
            lines.append("")

        if entry.get("licoes"):
            lines.append("**Lições por skill:**")
            for skill, lics in list(entry["licoes"].items())[:5]:
                for lesson in lics[:1]:
                    lines.append(f"- **{skill}:** {_snippet(lesson)}")
            lines.append("")

        if entry.get("gaps"):
            lines.append("**Gaps declarados:**")
            for g in entry["gaps"][:2]:
                lines.append(f"- {_snippet(g)}")
            lines.append("")

    return "\n".join(lines)


def extract_patterns(entries: List[dict]) -> str:
    """Agrega padrões recorrentes cross-relatório → markdown de patterns."""
    if not entries:
        return "# Padrões do Corpus\n\n> Corpus vazio — nenhum relatório indexado.\n"

    cat_counters: Dict[str, Counter] = {
        "melhorias":     Counter(),
        "boas_praticas": Counter(),
        "gaps":          Counter(),
        "detecao":       Counter(),
    }
    licoes_agg: Dict[str, List[str]] = defaultdict(list)

    for entry in entries:
        for cat in cat_counters:
            for item in entry.get(cat, []):
                cat_counters[cat][item] += 1
        for skill, lics in entry.get("licoes", {}).items():
            licoes_agg[skill].extend(lics)

    lines = [
        "# Padrões do Corpus de Aprendizado (ADR-068)",
        "",
        f"> Gerado de **{len(entries)} relatório(s)**. Agnóstico de domínio — reutilizável em qualquer projeto.",
        f"> Rebuild: `python tools/knowledge_catalog.py --build`",
        "",
    ]

    def _add_section(title: str, counter: Counter, limit: int = 12) -> None:
        top = counter.most_common(limit)
        if not top:
            return
        lines.append(f"## {title}")
        lines.append("")
        for item, count in top:
            star = " ★" if count > 1 else ""
            lines.append(f"- {_snippet(item)}{star}  *(×{count})*")
        lines.append("")

    _add_section("Melhorias recorrentes", cat_counters["melhorias"])
    _add_section("Boas práticas recorrentes", cat_counters["boas_praticas"])
    _add_section("Gaps recorrentes declarados", cat_counters["gaps"])
    _add_section("Detecções framework × humano", cat_counters["detecao"])

    if licoes_agg:
        lines.append("## Lições por skill (cross-relatório)")
        lines.append("")
        for skill in sorted(licoes_agg):
            lics = licoes_agg[skill]
            lines.append(f"### {skill}")
            for l in lics[:5]:
                lines.append(f"- {_snippet(l)}")
            lines.append("")

    lines += ["---", ""]
    return "\n".join(lines)


# ── Persistência do catálogo ──────────────────────────────────────────────────

def _catalog_save(entries: List[dict], out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    # Remove _tokens_full do JSON (verboso; reconstruído no load)
    saveable = [{k: v for k, v in e.items() if k != "_tokens_full"} for e in entries]
    with open(os.path.join(out_dir, "catalog.json"), "w", encoding="utf-8") as fh:
        json.dump(saveable, fh, ensure_ascii=False, indent=2)


def _catalog_load(out_dir: str) -> List[dict]:
    path = os.path.join(out_dir, "catalog.json")
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            entries = json.load(fh)
        for entry in entries:
            all_parts: List[str] = (
                entry.get("gaps", []) + entry.get("melhorias", []) +
                entry.get("boas_praticas", []) + entry.get("detecao", []) +
                [l for lls in entry.get("licoes", {}).values() for l in lls]
            )
            entry["_tokens_full"] = " ".join(all_parts)
        return entries
    except (json.JSONDecodeError, OSError, ValueError):
        return []


# ── Comandos CLI ──────────────────────────────────────────────────────────────

def cmd_build(intake_dir: str, out_dir: str) -> int:
    entries = build_catalog(intake_dir)
    if not entries:
        print(f"[knowledge-catalog] aviso: nenhum relatório em '{intake_dir}'.", file=sys.stderr)
        return 2

    _catalog_save(entries, out_dir)

    # session-insights.md — hook lê este arquivo, sem spawn Python
    si_path = os.path.join(out_dir, "session-insights.md")
    with open(si_path, "w", encoding="utf-8") as fh:
        fh.write(render_insights_md(entries[:TOP_N_SESSION]))

    # patterns.md
    pat_path = os.path.join(out_dir, "patterns.md")
    with open(pat_path, "w", encoding="utf-8") as fh:
        fh.write(extract_patterns(entries))

    print(f"[knowledge-catalog] {len(entries)} relatório(s) indexados.")
    print(f"  catalog: {os.path.join(out_dir, 'catalog.json')}")
    print(f"  session-insights: {si_path}")
    print(f"  patterns: {pat_path}")
    return 0


def cmd_recall(context: str, out_dir: str, top_n: int) -> int:
    entries = _catalog_load(out_dir)
    if not entries:
        print("[knowledge-catalog] catálogo vazio — rode '--build' primeiro.", file=sys.stderr)
        return 2
    top = recall(entries, context, top_n=top_n)
    label = context[:60].replace("\n", " ")
    print(render_insights_md(top, header=f"## Insights Relevantes (query: `{label}`)"))
    return 0


def cmd_patterns(out_dir: str) -> int:
    entries = _catalog_load(out_dir)
    if not entries:
        print("[knowledge-catalog] catálogo vazio — rode '--build' primeiro.", file=sys.stderr)
        return 2
    os.makedirs(out_dir, exist_ok=True)
    pat_path = os.path.join(out_dir, "patterns.md")
    with open(pat_path, "w", encoding="utf-8") as fh:
        fh.write(extract_patterns(entries))
    print(f"[knowledge-catalog] patterns.md atualizado: {pat_path}")
    return 0


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Catálogo de insights + RAG léxico offline sobre corpus de relatórios (ADR-068)."
    )
    ap.add_argument("--build",   action="store_true",
                    help="Parse relatórios → catalog.json + session-insights.md + patterns.md")
    ap.add_argument("--recall",  action="store_true",
                    help="BM25 query → top-N insights (stdout markdown)")
    ap.add_argument("--patterns", action="store_true",
                    help="Agregar padrões cross-relatório → patterns.md")
    ap.add_argument("--context", default="",
                    help="Query para --recall (string de keywords)")
    ap.add_argument("--from-briefing", default="", metavar="PATH",
                    help="Usar texto de briefing.md como contexto para --recall")
    ap.add_argument("--intake-dir", default=DEFAULT_INTAKE,
                    help=f"Dir com relatórios .md (default: {DEFAULT_INTAKE})")
    ap.add_argument("--out-dir", default=DEFAULT_OUT,
                    help=f"Dir de saída do catálogo (default: {DEFAULT_OUT})")
    ap.add_argument("--top-n", type=int, default=TOP_N_RECALL,
                    help=f"Insights retornados por --recall (default: {TOP_N_RECALL})")

    args = ap.parse_args()

    if args.build:
        sys.exit(cmd_build(args.intake_dir, args.out_dir))

    if args.recall:
        ctx = args.context
        if args.from_briefing:
            ctx = _read_text(args.from_briefing)
        if not ctx.strip():
            print("[knowledge-catalog] --recall requer --context ou --from-briefing com conteúdo.",
                  file=sys.stderr)
            sys.exit(1)
        sys.exit(cmd_recall(ctx, args.out_dir, args.top_n))

    if args.patterns:
        sys.exit(cmd_patterns(args.out_dir))

    ap.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
