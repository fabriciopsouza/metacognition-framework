#!/usr/bin/env python3
"""check_web_public_size.py — mede o tamanho do prompt público web vs o alvo (REQ-PUB-3 / GAP-3).

REQ-PUB-3: o tier público deve caber em ~12k tokens (campo de instruções do Claude.ai/Gemini sem estourar).
Aqui é a medida DETERMINÍSTICA local: chars, palavras, e uma ESTIMATIVA de tokens (chars/4 — heurística PT-BR).

LIMITE HONESTO (GAP-3): chars/4 é estimativa, NÃO o tokenizer real do Claude.ai/Gemini. A medida exata
depende do tokenizer da plataforma-alvo (dependência externa). Use este número como semáforo, não como verdade
final; a validação real é o eval na plataforma (ver _meta/eval-web-gemini.md).

Uso: python tools/check_web_public_size.py [arquivo]   # default: PROMPT-CHAT-WEB-v4.4.md
Exit 0 se dentro do alvo; 1 se estourar (corte profundidade de domínio antes do transversal — REQ-PUB-3).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = os.path.join(ROOT, "PROMPT-CHAT-WEB-v4.4.md")
TARGET_TOKENS = 12000          # REQ-PUB-3
CHARS_PER_TOKEN = 4            # heurística PT-BR (estimativa — não é o tokenizer real; GAP-3)


def measure(path):
    txt = open(path, encoding="utf-8").read()
    chars = len(txt)
    words = len(txt.split())
    est_tokens = round(chars / CHARS_PER_TOKEN)
    return chars, words, est_tokens


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    if not os.path.isfile(path):
        print(f"FAIL: arquivo nao encontrado: {path}")
        return 1
    chars, words, est = measure(path)
    pct = round(100 * est / TARGET_TOKENS)
    print(f"Arquivo: {os.path.relpath(path, ROOT)}")
    print(f"  chars      : {chars:,}")
    print(f"  palavras   : {words:,}")
    print(f"  ~tokens    : {est:,}  (estimativa chars/{CHARS_PER_TOKEN} — NAO e o tokenizer real; GAP-3)")
    print(f"  alvo       : {TARGET_TOKENS:,} tokens  ({pct}% do alvo)")
    if est > TARGET_TOKENS:
        print("  VERDITO    : ESTOUROU (estimado) — corte profundidade de DOMINIO antes do transversal (REQ-PUB-3).")
        return 1
    print("  VERDITO    : dentro do alvo (estimado). Validar com tokenizer real no eval da plataforma.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
