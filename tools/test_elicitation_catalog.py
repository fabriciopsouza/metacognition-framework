#!/usr/bin/env python3
"""Canario do catalogo de elicitacao (advanced-elicitation/methods.md) — ADR-085.

Prova FERRAMENTAL (nao prosa) de que o catalogo e estruturalmente integro e tem o eixo de FASE:
 (a) tabela parseavel; numeracao contigua e unica 1..N (sem buraco/duplicata/desordem);
 (b) toda linha tem as 5 colunas e output_pattern NAO-vazio (anti-linha-quebrada);
 (c) anti-JARVIS: nenhum placeholder (TODO/TBD/FIXME/XXX/[descricao]) vazou pro catalogo;
 (d) o eixo de FASE existe: secao 'Fase: divergente x convergente' + >=7 metodos categoria 'divergente'
     (a importacao CIS do ADR-085 — sem isso, "tem fase divergente" seria prosa);
 (e) a 'Selecao rapida por objetivo' expoe a rota DIVERGIR.
Fail-closed: exit 1 se qualquer invariante quebra. Auto-descoberto por run_canaries.py.

Uso: python tools/test_elicitation_catalog.py   (exit 0 PASS; 1 se falha)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, ".agent", "skills", "advanced-elicitation", "methods.md")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Placeholders proibidos, em dois grupos (ajuste pos-qa-critic ADR-085):
#  - CS (case-SENSITIVE): tokens all-caps isolados — senao "metodo" casaria "todo".
#  - CI (case-INSENSITIVE) e tolerante a espaco dentro do colchete: pega
#    'placeholder', '[descricao do metodo]', '[nome ...]', 'preencher aqui'.
JARVIS_CS = [r"\bTODO\b", r"\bTBD\b", r"\bFIXME\b", r"\bXXX\b", r"\bLOREM\b"]
JARVIS_CI = [r"\[[^\]]*descri[^\]]*\]", r"\[nome[^\]]*\]", r"placeholder", r"preencher\s+aqui"]
ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|")
MIN_DIVERGENTE = 7  # importacao CIS (#70-#76); fail-closed se o catalogo for truncado abaixo disso


def main():
    fails = []
    if not os.path.isfile(CATALOG):
        print(f"RESULTADO: FAIL (catalogo ausente: {CATALOG})")
        return 1
    txt = open(CATALOG, encoding="utf-8").read()

    # --- parse das linhas numeradas da tabela principal ---
    nums, divergente = [], 0
    for line in txt.splitlines():
        if not ROW_RE.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            fails.append(f"linha #{cells[0] if cells else '?'} tem {len(cells)} colunas (esperado 5): {line[:70]}")
            continue
        num, categoria, metodo, descricao, output = cells
        nums.append(int(num))
        if not metodo:
            fails.append(f"#{num} sem nome de metodo")
        if not descricao:
            fails.append(f"#{num} sem descricao")
        if not output:
            fails.append(f"#{num} sem output_pattern (coluna 5 vazia)")
        if categoria == "divergente":
            divergente += 1

    # (a) numeracao contigua e unica
    if not nums:
        fails.append("nenhuma linha de metodo parseada — catalogo vazio/quebrado (fail-closed)")
    else:
        if len(nums) != len(set(nums)):
            dups = sorted({n for n in nums if nums.count(n) > 1})
            fails.append(f"numeros de metodo duplicados: {dups}")
        expected = list(range(1, len(nums) + 1))
        if sorted(nums) != expected:
            missing = sorted(set(expected) - set(nums))
            extra = sorted(set(nums) - set(expected))
            fails.append(f"numeracao nao-contigua: faltam {missing}, sobram {extra}")

    # (c) anti-JARVIS no arquivo inteiro
    for rx in JARVIS_CS:
        m = re.search(rx, txt)
        if m:
            fails.append(f"anti-JARVIS: placeholder '{m.group(0)}' vazou no catalogo")
    for rx in JARVIS_CI:
        m = re.search(rx, txt, re.IGNORECASE)
        if m:
            fails.append(f"anti-JARVIS: placeholder '{m.group(0)}' vazou no catalogo")

    # (d) eixo de fase
    if "## Fase: divergente" not in txt:
        fails.append("secao '## Fase: divergente x convergente' ausente (eixo de selecao do ADR-085)")
    if divergente < MIN_DIVERGENTE:
        fails.append(f"so {divergente} metodos categoria 'divergente' (< {MIN_DIVERGENTE}) — "
                     f"importacao CIS truncada (fail-closed)")

    # (e) rota DIVERGIR exposta na selecao por objetivo
    if "(DIVERGIR)" not in txt:
        fails.append("'Selecao rapida por objetivo' sem a rota DIVERGIR")

    n = len(nums)
    print(f"elicitation-catalog: {n} metodos ({divergente} divergente / {n - divergente} convergente); "
          f"numeracao + colunas + fase + anti-JARVIS — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (catalogo integro: numeracao contigua, fase divergente presente, sem placeholder)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
