#!/usr/bin/env python3
"""Canário de marketing ancorado em evidência (ADR-044, item 13 do plano de remediação v2).

Prova: (a) LIMITS.md está em sync com os canários (`build_limits --check`); (b) todo claim do
LIMITS.md aponta para um canário que EXISTE (zero ✅ órfão); (c) nenhum doc de marketing
(README/PITCH) carrega um claim "✅ PROVADO" sem referência a canário (anti-overclaim);
(d) o README linka o LIMITS.md.

Uso: python tools/test_marketing_claims.py   (exit 0 PASS; 1 se houver claim órfão ou doc fora de sync)
"""
import os
import re
import sys

try:  # stdout UTF-8: Windows usa cp1252 e quebra no emoji ✅ (lição recorrente do incidente)
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from build_limits import CLAIMS, build, INTERNAL_ONLY  # noqa: E402

MARKETING_DOCS = ["README.md", "PROMPT-CHAT-WEB-v4.3.md"]


def main():
    fails = 0

    # (a) LIMITS.md em sync com os canários
    target = os.path.join(ROOT, "LIMITS.md")
    in_sync = os.path.isfile(target) and open(target, encoding="utf-8-sig").read().strip() == build().strip()
    if not in_sync:
        fails += 1
    print(f"{'OK  ' if in_sync else 'FAIL'} LIMITS.md em sync com os canários (build_limits)")

    # (b) todo claim PROVADO aponta para canário existente (zero órfão).
    # Canários INTERNOS (removidos da distribuição por design — ADR-044) NÃO contam como órfãos:
    # rodam na fonte/CI. Sem esta exceção, o gate falha no export limpo (o próprio incidente desta correção).
    orphan = [c for c, canary, *_ in CLAIMS
              if canary not in INTERNAL_ONLY and not os.path.isfile(os.path.join(ROOT, "tools", canary))]
    if orphan:
        fails += 1
    print(f"{'OK  ' if not orphan else 'FAIL'} todo claim do LIMITS aponta p/ canário existente "
          f"({'zero órfão' if not orphan else orphan})")

    # (c) nenhum '✅ PROVADO' em doc de marketing sem referência a canário 'tools/test_'
    overclaim = []
    for doc in MARKETING_DOCS:
        p = os.path.join(ROOT, doc)
        if not os.path.isfile(p):
            continue
        for i, line in enumerate(open(p, encoding="utf-8-sig").read().splitlines(), 1):
            if "✅" in line and re.search(r"provado", line, re.IGNORECASE):
                if "tools/test_" not in line and "LIMITS.md" not in line:
                    overclaim.append(f"{doc}:{i}")
    if overclaim:
        fails += 1
    print(f"{'OK  ' if not overclaim else 'FAIL'} sem claim PROVADO orfao (marca de selo) em marketing "
          f"({'nenhum' if not overclaim else overclaim})")

    # (d) README linka o LIMITS.md
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8-sig").read()
    links = "LIMITS.md" in readme
    if not links:
        fails += 1
    print(f"{'OK  ' if links else 'FAIL'} README linka o LIMITS.md")

    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (marketing ancorado: LIMITS em sync, zero claim órfão, README linkado)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
