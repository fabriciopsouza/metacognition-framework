#!/usr/bin/env python3
"""Canario process-evidence (ADR-074, parte FAIL-CLOSED determinista): a versao MAIS RECENTE do
CHANGELOG DEVE ter um checkpoint no history.md. Mecaniza o gap RECORRENTE "release sem fechamento
documentado" (ADR-069/070/071 fecharam sem checkpoint; 7 sessoes em 2026-06-02).

FORWARD-ONLY (regua §0): so gateia o release ATUAL — nao exige checkpoint retroativo das 22 versoes
historicas antigas (1.0-1.7 etc. nunca tiveram checkpoint individual; fabricar seria desonesto).

A parte NAO-determinista do process-evidence (qa-critic rodou; relatorios opt-in execution/cross-IA)
e DISCIPLINA + OFERTA no fechamento (ADR-074), nao fail-closed — relatorio opt-in nao pode ser exigido.

Uso: python tools/test_release_checkpoint.py   (exit 0 PASS; 1 se falha)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def tem_checkpoint(hist, versao):
    """A versao aparece DENTRO de um heading de checkpoint datado do history.md?

    Extraida de main() para o auto-teste exercitar a MESMA regra. As duas sutilezas que ela
    protege (e que ja falharam de verdade) estao nas fixtures de `autoteste()`:
      - mencao fora de heading nao conta (false-PASS de "Proximo passo: lancar vX");
      - fronteira numerica: 1.5.0 nao casa 1.50.0/11.5.0, e 1.51.0 nao casa 1.51.0-beta.
    """
    pat = re.compile(
        rf"(?m)^##\s+\d{{4}}-\d{{2}}-\d{{2}}.*?(?<![\d.])v?{re.escape(versao)}(?![\d.\-A-Za-z])")
    return bool(pat.search(hist))


def versao_atual(chg):
    """Topo do CHANGELOG = release atual (Keep a Changelog: mais novo no topo)."""
    vers = re.findall(r"(?m)^## \[(\d+\.\d+\.\d+)\]", chg)
    return vers[0] if vers else None


def autoteste():
    """Fixtures que este canario e OBRIGADO a acertar (ADR-106).

    Antes disto o canario era da classe `mechanism == test`: sabotar a regra o deixava VERDE
    (nao acha nada de errado no repo real e passa), entao a capacidade declarava `fail-closed`
    sem poder ser provada. Cada fixture aqui e um false-PASS que ja aconteceu ou que a regra
    foi escrita para impedir.
    """
    falhas = []
    bom = "## 2026-08-17 - Release v1.87.0 (MINOR): titulo qualquer\n\ntexto\n"
    if not tem_checkpoint(bom, "1.87.0"):
        falhas.append("checkpoint datado LEGITIMO nao foi reconhecido — detector cego")

    fora = "## Em aberto\n\n- Proximo passo: lancar v1.87.0 quando der\n"
    if tem_checkpoint(fora, "1.87.0"):
        falhas.append("mencao FORA de heading datado foi aceita — e o false-PASS que a regra "
                      "existe para impedir (padrao real no history: 'Proximo passo: lancar vX')")

    vizinha = "## 2026-08-17 - Release v1.50.0 (MINOR): outra\n"
    if tem_checkpoint(vizinha, "1.5.0"):
        falhas.append("fronteira numerica furada: 1.5.0 casou com 1.50.0")

    pre = "## 2026-08-17 - Release v1.51.0-beta (MINOR): outra\n"
    if tem_checkpoint(pre, "1.51.0"):
        falhas.append("fronteira furada: 1.51.0 casou com 1.51.0-beta")

    if versao_atual("## [2.0.0] - x\n## [1.0.0] - y\n") != "2.0.0":
        falhas.append("versao atual nao e a do TOPO do CHANGELOG")
    return falhas


def main():
    try:
        chg = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8-sig").read()
        hist = open(os.path.join(ROOT, "history.md"), encoding="utf-8-sig").read()
    except Exception as e:
        print(f"RESULTADO: FAIL (CHANGELOG/history ilegivel: {e})")
        return 1

    latest = versao_atual(chg)
    if not latest:
        print("RESULTADO: FAIL (nenhuma versao no CHANGELOG)")
        return 1

    ok = tem_checkpoint(hist, latest)
    falhas_canario = autoteste()

    if ok:
        print(f"release atual v{latest}: checkpoint presente no history.md (heading datado) — OK")
    else:
        print(f"release atual v{latest}: SEM checkpoint datado no history.md "
              f"(mencao fora de heading nao conta — anti false-PASS)")
    print(f"auto-teste do detector (5 fixtures) — {'OK' if not falhas_canario else 'FAIL'}")
    for f in falhas_canario:
        print("  -", f)
    print("-" * 50)
    if not ok or falhas_canario:
        print(f"RESULTADO: FAIL (release v{latest}: "
              f"{'sem checkpoint' if not ok else 'checkpoint ok'}, "
              f"{len(falhas_canario)} falha(s) do proprio detector)")
        return 1
    print(f"RESULTADO: PASS (release v{latest} tem fechamento documentado; "
          f"detector provado contra fixture)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
