#!/usr/bin/env python3
"""Gate de COMPLETUDE pedido × entrega (ADR-034) — cruza o escopo pedido com o validado.

GAP de campo: o escopo entregue era **subconjunto** do pedido (o pedido dizia "para cada
unidade, mês a mês, com acumulado"; entregou-se um mês / uma base). **Nenhum gate cruzou
pedido × entrega.**

MECANISMO (determinístico, sem NLP pesado): o linter detecta **quantificadores de escopo** no
texto do pedido (lexicon agnóstico: "cada X", "por X", "todos", "mês a mês/mensal", "acumulado",
"ano inteiro/anual", "intervalo") e exige que CADA quantificador detectado esteja (a) declarado na
seção `## Cobertura exigida pelo pedido` do requirements.md E (b) coberto por um critério binário
no `validation.md`. Quantificador do pedido sem critério correspondente = FAIL antes do PASS (J4).

Verifica **cobertura**, não correção numérica (isso é o qa-critic adversarial). Limite → LIMITS.md:
o lexicon é não-exaustivo; quantificador fora dele não é detectado (declarado, não escondido).

Uso:
    python tools/check_completeness.py <spec_dir>              # usa requirements.md + validation.md
    python tools/check_completeness.py <requirements.md> <validation.md>
    python tools/check_completeness.py                          # docs/specs/*/ (exceto _template)

Exit 0 se toda entrega cobre o pedido; 1 se algum quantificador ficou sem critério.
"""
import glob
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s.strip().lower())


# Lexicon agnóstico de quantificadores de escopo → palavra distintiva a rastrear.
# Cada entrada: (regex sobre texto normalizado, função que extrai o token distintivo).
QUANTIFIERS = [
    (re.compile(r"\bcada\s+([a-z]{3,})"), lambda m: m.group(1)),
    (re.compile(r"\bpor\s+([a-z]{3,})"), lambda m: m.group(1)),
    (re.compile(r"\btodos?\b|\btodas?\b"), lambda m: "todos"),
    (re.compile(r"\bmes a mes\b|\bmensal\b|\bmensalmente\b"), lambda m: "mes"),
    (re.compile(r"\bacumulad[oa]\b"), lambda m: "acumulado"),
    (re.compile(r"\bano inteiro\b|\banual\b|\banualmente\b"), lambda m: "ano"),
    (re.compile(r"\bintervalo\b"), lambda m: "intervalo"),
]
# Palavras-cola que não viram exigência mesmo casando "por X"/"cada X".
STOPWORDS = {"que", "ser", "uma", "isso", "exemplo", "meio", "favor", "isso", "via"}


def extract_section(text, *needles):
    """Linhas sob a 1ª heading cujo título normalizado contém qualquer needle."""
    lines = text.splitlines()
    out, in_sec, lvl = [], False, 0
    for ln in lines:
        h = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if h:
            t = _norm(h.group(2))
            if not in_sec and any(n in t for n in needles):
                in_sec, lvl = True, len(h.group(1))
                continue
            if in_sec and len(h.group(1)) <= lvl:
                break
        if in_sec:
            out.append(ln)
    return out


def request_text(req):
    """Texto do pedido = seções de objetivo/pedido/escopo (fallback: doc inteiro)."""
    sec = extract_section(req, "objetivo", "pedido", "escopo funcional", "identificacao")
    return _norm(" ".join(sec)) if sec else _norm(req)


def detect_quantifiers(text):
    found = set()
    for rx, tok in QUANTIFIERS:
        for m in rx.finditer(text):
            t = tok(m)
            if t and t not in STOPWORDS:
                found.add(t)
    return found


def coverage_tokens(req):
    """Tokens distintivos declarados na seção de cobertura exigida."""
    sec = extract_section(req, "cobertura", "completude")
    return _norm(" ".join(sec))


def check(req_text_raw, val_text_raw):
    req_norm = request_text(req_text_raw)
    quant = detect_quantifiers(req_norm)
    cov = coverage_tokens(req_text_raw)
    val = _norm(val_text_raw)
    missing_cov, missing_val = [], []
    for q in sorted(quant):
        if q not in cov:
            missing_cov.append(q)
        if q not in val:
            missing_val.append(q)
    return quant, missing_cov, missing_val


def _resolve(targets):
    """Normaliza args em pares (requirements.md, validation.md)."""
    pairs = []
    if not targets:
        for d in glob.glob(os.path.join(ROOT, "docs", "specs", "*")):
            if os.path.isdir(d) and "_template" not in d:
                r = os.path.join(d, "requirements.md")
                v = os.path.join(d, "validation.md")
                if os.path.isfile(r) and os.path.isfile(v):
                    pairs.append((r, v))
    elif len(targets) == 1 and os.path.isdir(targets[0]):
        pairs.append((os.path.join(targets[0], "requirements.md"),
                      os.path.join(targets[0], "validation.md")))
    elif len(targets) == 2:
        pairs.append((targets[0], targets[1]))
    return pairs


def main(argv):
    pairs = _resolve(argv[1:])
    if not pairs:
        print("nenhum par requirements.md/validation.md para checar.")
        return 0
    any_fail = False
    for r, v in pairs:
        try:
            req = open(r, encoding="utf-8-sig").read()
            val = open(v, encoding="utf-8-sig").read()
        except OSError as e:
            print(f"FAIL {r}: {e}")
            any_fail = True
            continue
        quant, miss_cov, miss_val = check(req, val)
        try:  # spec em drive/mount diferente do framework (Windows) → relpath lança ValueError (§13.1)
            rel = os.path.relpath(os.path.dirname(r), ROOT) if os.path.dirname(r) else r
        except ValueError:
            rel = os.path.dirname(r) or r
        if not quant:
            print(f"PASS {rel}  (nenhum quantificador de escopo detectado no pedido)")
            continue
        if miss_cov or miss_val:
            any_fail = True
            print(f"FAIL {rel}  — pedido cobre {sorted(quant)}")
            if miss_cov:
                print(f"      sem declaração em '## Cobertura exigida pelo pedido': {miss_cov}")
            if miss_val:
                print(f"      sem critério binário no validation.md: {miss_val}")
        else:
            print(f"PASS {rel}  (quantificadores {sorted(quant)} cobertos em coverage + validation)")
    print("-" * 50)
    print("RESULTADO:", "FAIL (entrega cobre subconjunto do pedido)" if any_fail
          else "PASS (entrega cobre cada quantificador do pedido)")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
