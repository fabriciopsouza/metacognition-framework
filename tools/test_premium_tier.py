#!/usr/bin/env python3
"""Canário do tiering premium/baseline (ADR-049).

Prova: (a) os arquivos premium declarados existem na fonte (serão stripados no baseline); (b) os
arquivos com seção premium contêm os marcadores (o strip vai agir); (c) `strip_premium_markers` remove
o bloco premium MAS preserva o CORE (discovery não morre); (d) a fonte tem o core fora dos marcadores.

É infra do pipeline de export (depende de `export-clean.py`) → removido das distribuições públicas
(STRIP_AFTER_VERIFY) e tratado como canário INTERNO no build_limits. Se export-clean ausente → SKIP.

Uso: python tools/test_premium_tier.py   (exit 0 PASS/SKIP; 1 se o tiering não marca/strip corretamente)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
try:
    from export_clean import strip_premium_markers, PREMIUM_STRIP_FILES, PREMIUM_MARKER_FILES  # type: ignore
except Exception:
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("export_clean", os.path.join(ROOT, "tools", "export-clean.py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        strip_premium_markers, PREMIUM_STRIP_FILES, PREMIUM_MARKER_FILES = (
            m.strip_premium_markers, m.PREMIUM_STRIP_FILES, m.PREMIUM_MARKER_FILES)
    except Exception as e:
        print(f"SKIP: export-clean.py indisponível (infra de pipeline não distribuída): {e}", file=sys.stderr)
        sys.exit(0)


def main():
    fails = 0

    # (a) arquivos/dirs premium existem na fonte (PREMIUM_STRIP_FILES inclui dir, ex.: _template-documentos)
    miss = [p for p in PREMIUM_STRIP_FILES if not os.path.exists(os.path.join(ROOT, *p.split("/")))]
    if miss:
        fails += 1
    print(f"{'OK  ' if not miss else 'FAIL'} arquivos premium presentes na fonte ({'todos' if not miss else miss})")

    # (b) arquivos marcadores contêm os marcadores premium
    nomark = []
    for p in PREMIUM_MARKER_FILES:
        fp = os.path.join(ROOT, *p.split("/"))
        t = open(fp, encoding="utf-8-sig").read() if os.path.isfile(fp) else ""
        if "premium:start" not in t.lower() or "premium:end" not in t.lower():
            nomark.append(p)
    if nomark:
        fails += 1
    print(f"{'OK  ' if not nomark else 'FAIL'} marcadores <!-- premium --> presentes ({'todos' if not nomark else nomark})")

    # (c) strip remove premium e preserva core (discovery)
    disc = os.path.join(ROOT, ".agent", "skills", "discovery", "SKILL.md")
    with tempfile.TemporaryDirectory() as d:
        tmp = os.path.join(d, "SKILL.md")
        open(tmp, "w", encoding="utf-8").write(open(disc, encoding="utf-8-sig").read())
        strip_premium_markers(tmp)
        out = open(tmp, encoding="utf-8").read()
    premium_gone = "Blueprint de domínio" not in out
    core_kept = ("Método universal" in out) and ("Escopo declarado pelo discovery" in out) and ("Banco de partida" in out)
    if not premium_gone:
        fails += 1
    print(f"{'OK  ' if premium_gone else 'FAIL'} strip remove a seção premium (§Blueprint) do baseline")
    if not core_kept:
        fails += 1
    print(f"{'OK  ' if core_kept else 'FAIL'} strip PRESERVA o core do discovery (método/escopo/banco) — não mata o discovery")

    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (tiering: premium marcado e stripável; core do discovery intacto no baseline)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
