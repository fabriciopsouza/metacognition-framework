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


def avaliar(main_major, main_minor, txt):
    """Lista de problemas de currency do prompt web. Extraida de main() para que o auto-teste
    exercite a MESMA regra — e nao uma reimplementacao que pode divergir em silencio."""
    fails = []
    am = ALIGN_RE.search(txt or "")
    if not am:
        fails.append("carimbo 'Alinhado ao Framework Metacognitivo vX.Y.Z' ausente/ilegivel no prompt web")
        return fails, None, None
    web_major, web_minor = int(am.group(1)), int(am.group(2))
    if web_major != main_major:
        fails.append(f"major divergente: prompt web v{web_major}.x x main v{main_major}.x")
    else:
        gap = main_minor - web_minor
        if gap > GAP_MAX:
            fails.append(f"prompt web {gap} minors atras de main (v{web_major}.{web_minor} x "
                         f"v{main_major}.{main_minor}; max {GAP_MAX}) - sincronize a doutrina + carimbo")
        elif gap < 0:
            fails.append(f"prompt web a FRENTE de main (v{web_major}.{web_minor} x "
                         f"v{main_major}.{main_minor})?")
    return fails, web_major, web_minor


def autoteste():
    """Fixtures que este canario e OBRIGADO a acertar (ADR-106).

    Classe `mechanism == test`: sabotar a regra (ex.: afrouxar GAP_MAX) deixava o canario
    VERDE, porque o repo real estava em dia — o gate parava de existir sem nenhum sinal.
    Isso e' pior do que nao ter gate: o painel continua dizendo que a doutrina esta alinhada.
    """
    falhas = []
    carimbo = "Alinhado ao Framework Metacognitivo v{}.{}.0"

    f, _, _ = avaliar(1, 87, carimbo.format(1, 87))
    if f:
        falhas.append(f"prompt EM DIA foi acusado (falso-positivo): {f}")

    f, _, _ = avaliar(1, 87, carimbo.format(1, 87 - GAP_MAX - 1))
    if not f:
        falhas.append(f"prompt {GAP_MAX + 1} minors atras NAO foi pego - a janela de currency "
                      f"parou de valer (GAP_MAX afrouxado?)")

    f, _, _ = avaliar(2, 3, carimbo.format(1, 3))
    if not f:
        falhas.append("major divergente NAO foi pego")

    f, _, _ = avaliar(1, 3, carimbo.format(1, 9))
    if not f:
        falhas.append("prompt A FRENTE de main NAO foi pego")

    f, _, _ = avaliar(1, 87, "documento sem carimbo nenhum")
    if not f:
        falhas.append("prompt SEM carimbo NAO foi pego - fail-closed furado")

    f, _, _ = avaliar(1, 87, carimbo.format(1, 87 - GAP_MAX))
    if f:
        falhas.append(f"prompt exatamente no limite ({GAP_MAX} minors) foi acusado - "
                      f"a janela e' inclusiva por design")
    return falhas


def main():
    fails = []
    mv = VER_RE.match(web_export.main_version() or "")
    if not mv:
        print("RESULTADO: FAIL (main_version ilegivel - fail-closed)")
        return 1
    main_major, main_minor = int(mv.group(1)), int(mv.group(2))

    src = web_export.PUBLIC_SRC
    if not os.path.isfile(src):
        print(f"RESULTADO: FAIL (PUBLIC_SRC ausente: {src})")
        return 1
    txt = open(src, encoding="utf-8").read()
    fails, web_major, web_minor = avaliar(main_major, main_minor, txt)
    falhas_canario = autoteste()

    base = os.path.basename(src)
    web_disp = f"v{web_major}.{web_minor}" if web_major is not None else "?(sem carimbo)"
    print(f"web-prompt-currency: {base} alinhado a {web_disp} x main v{main_major}.{main_minor} "
          f"(max {GAP_MAX} minors) - {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print(f"auto-teste do detector (6 fixtures) - {'OK' if not falhas_canario else 'FAIL'}")
    for f in falhas_canario:
        print("  -", f)
    print("-" * 50)
    if fails or falhas_canario:
        print(f"RESULTADO: FAIL ({len(fails)} problema(s) de currency, "
              f"{len(falhas_canario)} falha(s) do proprio detector)")
        return 1
    print("RESULTADO: PASS (prompt web dentro da janela de currency; detector provado contra fixture)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
