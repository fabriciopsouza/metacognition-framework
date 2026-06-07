#!/usr/bin/env python3
"""build_capabilities.py — gerador DERIVADO do indice de capacidades (ADR-072).

Fonte unica: `capabilities.json` (UM registro por feature). Daqui saem, sem escrita a mao:
  1. CAPABILITIES.md  — indice curto e legivel que o agente le no boot (file-first).
  2. manifest de equivalencia — alimenta `equivalence_gate.py` (paridade cross-IA claude<->gemini).
  3. --check — falha (exit 1) se CAPABILITIES.md em disco != render atual (anti-drift, como build_limits).

Por que derivado e nao escrito a mao: indice a mao DERIVA e deixa de ser confiavel; se o agente
nao confia, volta a explorar do zero (o modo de falha que o ADR-072 ataca). Aqui o canario
`test_capabilities.py` garante que cada ponteiro existe e que PROVIDES tem teste — o indice nao mente.

Uso:
    python tools/build_capabilities.py            # (re)gera CAPABILITIES.md
    python tools/build_capabilities.py --check    # exit 1 se CAPABILITIES.md fora de sync
    python tools/build_capabilities.py --manifest [out.json]   # emite manifest de equivalencia
Sem dependencias externas (stdlib).
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "capabilities.json")
INDEX_MD = os.path.join(ROOT, "CAPABILITIES.md")

STATUS_ICON = {"PROVIDES": "✅", "PARTIAL": "🟡", "ABSENT": "⏳", "JUSTIFIED_ABSENT": "🚫"}
GEN_HEADER = "<!-- GERADO por tools/build_capabilities.py a partir de capabilities.json — NAO editar a mao -->"


def load_registry(path=REGISTRY):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _link(path):
    """Link markdown relativo (clicavel) p/ um ponteiro de arquivo; '—' se ausente."""
    if not path:
        return "—"
    name = os.path.basename(path)
    return f"[{name}]({path})"


def _line(c):
    """Nivel 1: UMA linha compacta — id + title + status + marcador cross-IA. SEM mecanismo/teste/ADR
    (esses sao nivel 2, via --show). Mantem o boot barato mesmo com centenas de capacidades."""
    icon = STATUS_ICON.get(c.get("status", "?"), "?")
    x = " 🔗" if c.get("cross_ai") else ""
    return f"- {icon}{x} `{c.get('id', '?')}` — {c.get('title', '')}"


def render(reg):
    """Indice NIVEL 1 (id + title). Progressive disclosure (ADR-003/072): o agente le isto p/
    entender o que existe e achar o id; o registro completo (mecanismo/teste/ADR/doc) vem por
    `--show <id>`. Assim o indice nao trunca nem custa contexto quando cresce."""
    caps = sorted(reg.get("capabilities", []), key=lambda x: x.get("id", ""))
    cross = [c for c in caps if c.get("cross_ai")]
    local = [c for c in caps if not c.get("cross_ai")]
    n = len(caps)
    prov = sum(1 for c in caps if c.get("status") == "PROVIDES")
    part = sum(1 for c in caps if c.get("status") == "PARTIAL")

    out = []
    out.append(GEN_HEADER)
    out.append("# CAPABILITIES — indice de capacidades (nivel 1: id + title)")
    out.append("")
    out.append(f"> **{n} capacidades** — {prov} ✅ PROVIDES · {part} 🟡 PARTIAL · 🔗 = cross-IA. "
               f"Fonte: [capabilities.json](capabilities.json). Canario anti-drift: "
               f"[test_capabilities.py](tools/test_capabilities.py) (ADR-072).")
    out.append("> **Como usar (file-first, boot):** leia esta lista p/ achar o `id`; o registro "
               "completo (mecanismo · canario · ADR · doc) vem por **`python tools/build_capabilities.py "
               "--show <id>`** ou `grep -A8 '\"<id>\"' capabilities.json`. Nao reexplore o repo antes disto.")
    out.append("> **Manutencao:** feature nova -> +1 registro em `capabilities.json` + "
               "`python tools/build_capabilities.py`. Canario barra canario orfao (cobertura).")
    out.append("")
    if cross:
        out.append("## Cross-IA (claude ↔ gemini — entra no manifest de equivalencia)")
        out.append("")
        out.extend(_line(c) for c in cross)
        out.append("")
    out.append("## Nucleo (local ao repo-mae)")
    out.append("")
    out.extend(_line(c) for c in local)
    out.append("")
    return "\n".join(out) + "\n"


def show(reg, cid):
    """Nivel 2: registro COMPLETO de UMA capacidade (drill-down)."""
    for c in reg.get("capabilities", []):
        if c.get("id") == cid:
            icon = STATUS_ICON.get(c.get("status", "?"), "?")
            lines = [f"## `{c['id']}` — {c.get('title', '')}",
                     f"- status: {icon} {c.get('status')}",
                     f"- ai_owner: {c.get('ai_owner', '—')}",
                     f"- cross_ai: {bool(c.get('cross_ai'))}",
                     f"- mecanismo: {c.get('mechanism', '—')}",
                     f"- canario: {c.get('test', '—')}",
                     f"- ADR: {c.get('adr', '—')}",
                     f"- doc: {c.get('doc', '—')}",
                     f"- tags: {', '.join(c.get('tags', [])) or '—'}"]
            return "\n".join(lines)
    near = [c.get("id") for c in reg.get("capabilities", []) if cid and cid in (c.get("id") or "")]
    msg = f"capacidade '{cid}' nao encontrada."
    if near:
        msg += " Talvez: " + ", ".join(near)
    return msg


def manifest(reg, ai_default="claude"):
    """Manifest de equivalencia (subset cross_ai) no schema que equivalence_gate consome."""
    caps = []
    for c in reg.get("capabilities", []):
        if not c.get("cross_ai"):
            continue
        caps.append({
            "capability_id": c.get("id"),
            "ai": c.get("ai_owner", ai_default),
            "status": c.get("status"),
            "mechanism": c.get("mechanism"),
            "adr_ref": c.get("adr"),
        })
    return {"schema_version": "1.0", "capabilities": caps}


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        reg = load_registry()
    except Exception as e:
        print(f"capabilities.json ilegivel: {e}", file=sys.stderr)
        return 1

    if "--prune" in argv:
        # PROCESSO de publish (ADR-070/072): no shadow (export), docs/_private e outros sao stripados.
        # Poda entradas cujo ponteiro nao existe MAIS em disco (ex.: doc em docs/_private/cross-ai) e
        # WAIVA os canarios que embarcam mas ficaram sem capacidade indexada -> indice do shadow honesto
        # e canario verde, automaticamente, em TODO publish (nao remendo).
        caps = reg.get("capabilities", [])
        kept, dropped = [], []
        for c in caps:
            miss = [f for f in ("mechanism", "test", "adr", "doc")
                    if c.get(f) and not os.path.isfile(os.path.join(ROOT, c[f]))]
            (dropped if miss else kept).append(c)
        if not isinstance(dropped[0] if dropped else None, str):
            dropped = [c.get("id") for c in dropped]
        reg2 = dict(reg)
        reg2["capabilities"] = kept
        referenced = {c.get("test") for c in kept if c.get("test")}
        waivers = [w for w in reg.get("registry_waivers", []) if isinstance(w, dict)]
        waived = {w.get("file") for w in waivers}
        self_t = "tools/test_capabilities.py"
        found = set(glob.glob(os.path.join(ROOT, "tools", "test_*.py")))
        found |= set(glob.glob(os.path.join(ROOT, "tools", "**", "test_*.py"), recursive=True))
        for tp in sorted(found):
            rel = os.path.relpath(tp, ROOT).replace(os.sep, "/")
            if rel == self_t or rel in referenced or rel in waived:
                continue
            waivers.append({"file": rel, "reason": "capacidade podada no shadow (ponteiro stripado, "
                                                   "ex.: docs/_private); tooling embarca mas nao indexado"})
        reg2["registry_waivers"] = waivers
        with open(REGISTRY, "w", encoding="utf-8") as fh:
            json.dump(reg2, fh, ensure_ascii=False, indent=2)
        with open(INDEX_MD, "w", encoding="utf-8") as fh:
            fh.write(render(reg2))
        print(f"prune (shadow): {len(caps)}->{len(kept)} capacidades; podadas={dropped}; "
              f"{len(waivers)} waiver(s).")
        return 0

    if "--show" in argv:
        rest = [a for a in argv[argv.index("--show") + 1:] if not a.startswith("--")]
        if not rest:
            print("uso: --show <id>", file=sys.stderr)
            return 1
        print(show(reg, rest[0]))
        return 0

    if "--find" in argv:
        rest = [a for a in argv[argv.index("--find") + 1:] if not a.startswith("--")]
        kw = (rest[0] if rest else "").strip().lower()
        if not kw:
            print("uso: --find <keyword> (busca em id/title/tags)", file=sys.stderr)
            return 1
        hits = [c for c in reg.get("capabilities", [])
                if kw in (c.get("id", "") + " " + c.get("title", "") + " "
                          + " ".join(c.get("tags", []))).lower()]
        for c in sorted(hits, key=lambda x: x.get("id", "")):
            print(_line(c))
        if not hits:
            print(f"(nenhuma capacidade casa '{kw}')")
        return 0

    if "--manifest" in argv:
        man = manifest(reg)
        rest = [a for a in argv[2:] if not a.startswith("--")]
        if rest:
            with open(rest[0], "w", encoding="utf-8") as fh:
                json.dump(man, fh, ensure_ascii=False, indent=2)
            print(f"manifest de equivalencia escrito em {rest[0]} ({len(man['capabilities'])} caps cross-IA)")
        else:
            print(json.dumps(man, ensure_ascii=False, indent=2))
        return 0

    content = render(reg)
    if "--check" in argv:
        try:
            with open(INDEX_MD, encoding="utf-8") as fh:
                disk = fh.read()
        except FileNotFoundError:
            print("CAPABILITIES.md ausente — rode `python tools/build_capabilities.py`", file=sys.stderr)
            return 1
        if disk != content:
            print("CAPABILITIES.md FORA DE SYNC com capabilities.json — rode "
                  "`python tools/build_capabilities.py` e commite.", file=sys.stderr)
            return 1
        print("CAPABILITIES.md em sync com o registry.")
        return 0

    with open(INDEX_MD, "w", encoding="utf-8") as fh:
        fh.write(content)
    n = len(reg.get("capabilities", []))
    print(f"CAPABILITIES.md gerado ({n} capacidades).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
