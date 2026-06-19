#!/usr/bin/env python3
"""Canário de CURRENCY do prompt chat-web (PUBLIC_SRC) — ADR-089/091, débito declarado do prompt.

O prompt web (`PROMPT-CHAT-WEB-v*.md`) é mantido à MÃO (até o auto-gen do ADR-054/057) e por isso
DERIVOU silenciosamente (chegou a 29 releases atrás de main — não havia guard). Este canário fecha
o vazamento: lê o carimbo "Alinhado ao Framework Metacognitivo vX.Y.Z" do PUBLIC_SRC e compara ao
`main_version` (README). FAIL se o prompt ficar **mais de GAP_MAX minors atrás** de main.

NÃO exige == main (o prompt é uma DESTILAÇÃO curada, não espelho 1:1 — a maioria das releases é
IDE-only e não muda doutrina de chat); exige que não ULTRAPASSE GAP_MAX de defasagem → força revisão
periódica em vez de drift indefinido. Fail-closed se não conseguir parsear qualquer das versões.

Uso: python tools/test_web_prompt_currency.py   (exit 0 PASS; 1 se stale/ilegível)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import web_export  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GAP_MAX = 5  # prompt-web pode atrasar até 5 minors; além disso = revisão forçada (anti-drift-silencioso)
ALIGN_RE = re.compile(r"Alinhado ao Framework Metacognitivo v(\d+)\.(\d+)\.(\d+)")
VER_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def main():
    fails = []
    # versão de main (README)
    mv = VER_RE.match(web_export.main_version() or "")
    if not mv:
        print("RESULTADO: FAIL (main_version ilegível — fail-closed)")
        return 1
    main_major, main_minor, _ = (int(mv.group(1)), int(mv.group(2)), int(mv.group(3)))

    # versão alinhada declarada no prompt web
    src = web_export.PUBLIC_SRC
    if not os.path.isfile(src):
        print(f"RESULTADO: FAIL (PUBLIC_SRC ausente: {src})")
        return 1
    txt = open(src, encoding="utf-8").read()
    am = ALIGN_RE.search(txt)
    if not am:
        fails.append("carimbo 'Alinhado ao Framework Metacognitivo vX.Y.Z' ausente/ilegível no prompt web")
        web_major = web_minor = None
    else:
        web_major, web_minor = int(am.group(1)), int(am.group(2))
        if web_major != main_major:
            fails.append(f"major divergente: prompt web v{web_major}.x × main v{main_major}.x")
        else:
            gap = main_minor - web_minor
            if gap > GAP_MAX:
                fails.append(f"prompt web {gap} minors atrás de main (v{web_major}.{web_minor} × "
                             f"v{main_major}.{main_minor}; máx {GAP_MAX}) — sincronize a doutrina + carimbo")
            elif gap < 0:
                fails.append(f"prompt web à FRENTE de main (v{web_major}.{web_minor} × v{main_major}.{main_minor})?")

    base = os.path.basename(src)
    web_disp = f"v{web_major}.{web_minor}" if web_major is not None else "?(sem carimbo)"
    print(f"web-prompt-currency: {base} alinhado a {web_disp} × main v{main_major}.{main_minor} "
          f"(máx {GAP_MAX} minors) — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (prompt web dentro da janela de currency)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
