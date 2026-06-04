#!/usr/bin/env python3
"""Canário do detector de overclaim (ADR-059 G2). Hipótese adversarial: o detector deixa passar
um overclaim OU grita lobo numa frase honesta (falso-positivo, que mataria a confiança no gate).

Prova: (1) pega cada VENENO (absoluto-sem-hedge); (2) POUPA cada frase honesta (hedge/negação/
provisionamento/diretiva-particípio); (3) a vitrine real passa limpa.

Uso: python tools/test_overclaim_lexicon.py   (exit 0 PASS; 1 se algum caso falha)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from overclaim_lexicon import find_overclaims  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# DEVE pegar (overclaim real): absoluto de capacidade sem hedge.
POISON = [
    "O agente nunca alucina.",
    "Garante 100% de precisão nos números.",
    "O framework jamais inventa nomes de campo.",
    "A ferramenta é infalível e sempre correta.",
    "Elimina o risco de erro humano.",
    "Os agentes não inventam fatos.",
    "Garante conformidade com a norma.",
    # Paráfrases que ANTES escapavam (achados MÉD-3 do qa-critic) — regressão:
    "Assegura precisão total nos resultados.",
    "Zero alucinação nos resultados.",
    "Solução à prova de erro por design.",
    "Totalmente confiável em qualquer cenário.",
    "Precisão absoluta garantida.",
    "Acurácia de 100 por cento.",
    "Não gera alucinações.",
    "Funciona sem falhas.",
    "Nunca mente sobre os dados.",
    "Garantia de precisão em todo cálculo.",
    # Hedge-rescue que ANTES escapava (achado MÉD-2) — transição genérica não resgata mais:
    "Pode usar o agente, que nunca alucina.",
    "Sem limite de usuários, o framework jamais inventa.",
    "O produto visa eficiência e nunca erra.",
]

# NÃO pode pegar (honesto): hedge/negação/provisionamento/particípio/diretiva.
HONEST = [
    "Os gates reduzem o risco — não o eliminam.",
    "Alucinação residual permanece; o gate não elimina o sutilmente errado.",
    "Garantia ≠ default (a dura exige managed-settings).",
    "O bootstrap configura git e garante o gh CLI autenticado.",  # provisionar, não qualidade
    "Convenções consolidadas (não inventadas aqui) para versão e registro.",  # not-invented-here
    "Classifica o que sabe e admite o que não sabe.",
    "Em vez de inventar, sinaliza onde falta fonte.",
    "Pode reduzir alucinação, mas não a elimina.",
    "A regra elimina contagens obsoletas no checkpoint.",  # elimina + objeto não-qualidade (anti-FP)
    "O método reduz, mas não elimina, o erro residual.",
]


def main():
    fails = []

    for s in POISON:
        if not find_overclaims(s):
            fails.append(f"FALSO-NEGATIVO (deixou passar veneno): {s!r}")
    for s in HONEST:
        hit = find_overclaims(s)
        if hit:
            fails.append(f"FALSO-POSITIVO (gritou lobo em frase honesta): {s!r} -> {hit}")

    # vitrine real limpa
    vit = os.path.join(ROOT, "guia", "web", "index.html")
    if os.path.isfile(vit):
        vio = find_overclaims(open(vit, encoding="utf-8-sig").read(), strip_html=True)
        if vio:
            fails.append(f"vitrine real com overclaim: {[(l, h) for l, h, _ in vio]}")

    print(f"veneno pego: {len(POISON)}/{len(POISON)} | frases honestas poupadas: "
          f"{len(HONEST) - sum(1 for f in fails if 'FALSO-POSITIVO' in f)}/{len(HONEST)}")
    for f in fails:
        print("  -", f)
    print("-" * 60)
    print("RESULTADO:", "PASS (detector pega veneno, poupa honesto, vitrine limpa)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
