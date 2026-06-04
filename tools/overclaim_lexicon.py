#!/usr/bin/env python3
"""overclaim_lexicon.py — detector determinístico de OVERCLAIM (ADR-059, G2).

Honestidade da vitrine MECANIZADA. Pega afirmação ABSOLUTA de capacidade ("não alucina",
"garante", "jamais inventa", "100% preciso") **sem hedge na mesma sentença**. Consciente de
NEGAÇÃO/HEDGE: a frase honesta "os gates reduzem o risco — não o eliminam" NÃO é violação
(tem `reduz` + `não...elimina`); a headline "agentes que não alucinam" É (absoluto sem hedge).

Determinístico, offline, zero dependência externa (régua §0: funde no padrão do `anti_jarvis_gate`,
não importa Vale). Reusado por `test_marketing_claims.py` (vitrine + prompt web) e `web_export.py`.

LIMITE declarado (LIMITS.md): léxico pega absoluto EXPLÍCITO, não paráfrase ("jamais comete
deslizes"). Lexicon vivo + qa-critic adversarial são o backstop. NÃO é classificador semântico.

Uso (CLI): python tools/overclaim_lexicon.py <arquivo> [--html]   # exit 0 limpo; 1 com violação
"""
import re
import sys

# Afirmações ABSOLUTAS de capacidade (claim positivo) que exigem hedge para não serem overclaim.
# Lista expandida com paráfrases PT-BR comuns (achados MÉD-3 do qa-critic): reduz a evasão.
ABSOLUTES = [
    ("não/nunca alucina (claim positivo)", re.compile(r"(n[ãa]o|nunca|jamais)\s+alucina", re.I)),
    # inventa(m|r) no PRESENTE/infinitivo = claim de capacidade. Exclui particípio 'inventad-as'
    # ("convenções não inventadas aqui" = not-invented-here, legítimo, NÃO é overclaim).
    ("nunca/jamais/não inventa (claim absoluto)", re.compile(r"(nunca|jamais|n[ãa]o)\s+inventa(m|r)?\b", re.I)),
    ("nunca/jamais erra/mente/falha/produz incorreto",
     re.compile(r"(nunca|jamais)\s+(erra|mente|falha|produz\s+\w+\s+incorret)", re.I)),
    # 'garante' só é overclaim em contexto de QUALIDADE/RESULTADO (garante precisão, garante que não
    # erra). 'garante o gh CLI / git' = provisionar, NÃO é claim de qualidade -> não casa (anti-FP).
    ("garante qualidade/resultado", re.compile(
        r"\bgarant(e|em|ido|imos|ia)\s+(a\s+|o\s+|os\s+|as\s+|que\s+|de\s+)?"
        r"(precis|exat|conform|corret|qualidade|seguran|resultado|aus[êe]ncia|zero\b|100|cem\b|n[ãa]o\b|sem\s+erro)",
        re.I)),
    ("100%/cem por cento absoluto",
     re.compile(r"(100\s*%|100\s+por\s+cento|cem\s+por\s+cento)\s*(de\s+)?(precis|segur|confi[áa]|corret|acur|exat)", re.I)),
    ("infalível", re.compile(r"\binfal[íi]vel\b", re.I)),
    ("sempre correto/preciso/seguro", re.compile(r"\bsempre\s+(corret|cert[oa]|precis|segur|exat)", re.I)),
    # elimina + OBJETO de qualidade (anti-FP: 'elimina contagens obsoletas' não casa; 'não o eliminam' tb não).
    ("elimina erro/risco/alucinação (claim positivo)",
     re.compile(r"\belimina(m|r)?\s+(o\s+|a\s+|os\s+|as\s+)?(erro|risco|alucina|falha|bug|incerteza|deslize)", re.I)),
    ("zero erro/alucinação/falha", re.compile(r"\bzero\s+(alucina|erro|falha|deslize|incerteza)", re.I)),
    ("precisão/acurácia total/absoluta",
     re.compile(r"\b((precis[ãa]o|acur[áa]cia|confiabilidade)\s+(total|absolut)|"
                r"(total|absolut\w*)\s+(precis|acur|confiab))", re.I)),
    ("à prova de erro/falha", re.compile(r"[àa]\s+prova\s+de\s+(erro|falha|bug)", re.I)),
    ("totalmente/plenamente confiável/preciso",
     re.compile(r"\b(totalmente|plenamente|absolutamente)\s+(confi|precis|segur|corret|exat)", re.I)),
    ("livre de / sem erro", re.compile(r"\b(livre\s+de|sem)\s+(erro|falha|deslize)s?\b", re.I)),
    ("não gera/produz/comete erro/alucinação",
     re.compile(r"n[ãa]o\s+(gera|produz|comete)\s+(\w+\s+)?(alucina|erro|deslize|falha)", re.I)),
    ("acurácia/precisão de 100/cem", re.compile(r"(acur[áa]cia|precis[ãa]o)\s+de\s+(100|cem)\b", re.I)),
]

# HEDGES / negações que TORNAM a sentença honesta. ESTREITO (achado MÉD-2 do qa-critic): só negações
# que de fato refutam o ABSOLUTO da mesma frase. Palavras de transição genéricas ('pode', 'busca',
# 'visa', 'limite', 'em geral', 'tende a', 'depende') foram REMOVIDAS — resgatavam overclaim por
# coincidência intra-sentença ("Pode usar o agente, que nunca alucina"). 'não' genérico NUNCA entra
# (salvaria a headline "não alucinam").
HEDGES = re.compile(
    r"(reduz\w*|mitig\w*|atenu\w*|residual|"
    r"n[ãa]o\s+\w*\s*elimina|n[ãa]o\s+\w*\s*resolv|n[ãa]o\s+substitu|"
    r"n[ãa]o\s+\w*\s*garant|≠\s*default|n[ãa]o\s+[ée]\s+\w*\s*default|"
    r"n[ãa]o\s+\w*\s*default)",
    re.I,
)

SENT_SPLIT = re.compile(r"[.!?;\n]+")
TAG = re.compile(r"<[^>]+>")


def strip_markup(text):
    """Remove tags HTML para analisar a prosa renderizada (vitrine)."""
    return TAG.sub(" ", text)


def find_overclaims(text, strip_html=False):
    """Retorna lista de (label, trecho_casado, sentença[:90]) para absoluto-sem-hedge."""
    if strip_html:
        text = strip_markup(text)
    out = []
    for sent in SENT_SPLIT.split(text):
        s = " ".join(sent.split())
        if not s or HEDGES.search(s):
            continue
        for label, rx in ABSOLUTES:
            m = rx.search(s)
            if m:
                out.append((label, m.group(0), s[:90]))
                break
    return out


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = [a for a in argv[1:] if not a.startswith("--")]
    strip_html = "--html" in argv[1:]
    if not args:
        print("uso: python tools/overclaim_lexicon.py <arquivo> [--html]", file=sys.stderr)
        return 2
    text = open(args[0], encoding="utf-8-sig").read()
    v = find_overclaims(text, strip_html=strip_html)
    for label, hit, sent in v:
        print(f"OVERCLAIM [{label}] '{hit}' em: {sent}")
    print(f"{'FAIL' if v else 'OK'} ({len(v)} overclaim)")
    return 1 if v else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
