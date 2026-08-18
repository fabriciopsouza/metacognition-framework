#!/usr/bin/env python3
"""Canario doc-sync ADR<->CHANGELOG (mecaniza falha RECORRENTE). Toda ADR com Status Aceito DEVE
estar mencionada no CHANGELOG.md ('ADR-NNN'). Falha-recorrente observada: ADR-069/070/071 (e antes,
7 sessoes em 2026-06-02) Aceito/mergeado SEM entrada de CHANGELOG (consistency-gate fail-soft nao
disparou). Aqui vira FAIL-CLOSED: o gap nao pode mais passar silencioso (cerne prosa->mecanismo).

Uso: python tools/test_adr_changelog_sync.py   (exit 0 PASS; 1 se falha)
"""
import glob
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def auditar(dir_adr, changelog):
    """(total_aceitas, faltantes). Extraida de main() para que o auto-teste exercite a MESMA
    logica contra fixtures — testar uma copia deixaria a original livre para apodrecer."""
    chg = (changelog or "").lower()
    missing, total = [], 0
    for a in sorted(glob.glob(os.path.join(dir_adr, "*.md"))):
        name = os.path.basename(a)
        if "template" in name.lower():
            continue
        m = re.match(r"(\d+)-", name)
        if not m:
            continue
        txt = open(a, encoding="utf-8").read()
        if not re.search(r"status[:* ]+.*aceito", txt, re.I):  # so ADRs Aceito
            continue
        total += 1
        n = m.group(1)
        if f"adr-{n}" not in chg:
            missing.append(n)
    return total, missing


def autoteste():
    """Fixtures que este canario e OBRIGADO a acertar.

    ADR-106: `mechanism == test` — o gate E o proprio canario, entao sabotar a deteccao o
    deixava VERDE e a capacidade nao podia ser provada. As fixtures cobrem as duas direcoes
    (pega o que deve pegar E nao acusa o que nao deve), porque um detector que acusa tudo
    tambem passaria num teste so de deteccao.
    """
    falhas = []
    with tempfile.TemporaryDirectory(prefix="adr-chg-fx-") as td:
        def adr(nome, status):
            with open(os.path.join(td, nome), "w", encoding="utf-8") as fh:
                fh.write(f"# ADR\n\n- **Status:** {status}\n")

        adr("901-aceita-e-ausente.md", "Aceito")
        adr("902-aceita-e-presente.md", "Aceito")
        adr("903-so-proposta.md", "Proposto")
        adr("000-template.md", "Aceito")

        total, missing = auditar(td, "changelog qualquer citando ADR-902 e mais nada")
        if "901" not in missing:
            falhas.append("ADR Aceito AUSENTE do changelog nao foi pega — detector cego")
        if "902" in missing:
            falhas.append("ADR Aceito PRESENTE no changelog foi acusada — falso-positivo")
        if "903" in missing:
            falhas.append("ADR apenas Proposta foi cobrada — so Aceito entra na regra")
        if total != 2:
            falhas.append(f"contagem de Aceitas = {total}, esperado 2 "
                          f"(template deve ser ignorado; Proposta nao conta)")
    return falhas


def main():
    try:
        chg = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8-sig").read()
    except Exception as e:
        print(f"RESULTADO: FAIL (CHANGELOG.md ilegivel: {e})")
        return 1

    total, missing = auditar(os.path.join(ROOT, "docs", "adr"), chg)
    falhas_canario = autoteste()

    print(f"{total} ADR(s) Aceito; mencionadas no CHANGELOG: {total - len(missing)} — "
          f"{'OK' if not missing else 'FAIL'}")
    for n in missing:
        print(f"  - ADR-{n} Aceito mas AUSENTE do CHANGELOG (doc-sync: registre a mudanca)")
    print(f"auto-teste do detector (4 fixtures) — {'OK' if not falhas_canario else 'FAIL'}")
    for f in falhas_canario:
        print("  -", f)
    print("-" * 50)
    if missing or falhas_canario:
        print(f"RESULTADO: FAIL ({len(missing)} ADR sem doc-sync, "
              f"{len(falhas_canario)} falha(s) do proprio detector)")
        return 1
    print("RESULTADO: PASS (toda ADR Aceito esta no CHANGELOG; detector provado contra fixture)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
