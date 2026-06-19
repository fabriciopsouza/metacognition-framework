#!/usr/bin/env python3
"""Canário do elicitation-gate VINCULANTE (ADR-089) — prova FERRAMENTAL (não prosa) de que a
"ficha de insumo" obrigatória está presente e completa no discovery, com natureza BINDING:
 (a) a seção do gate existe no `discovery/SKILL.md` (referência a ADR-089 + "elicitation-gate");
 (b) os 6 campos obrigatórios da ficha estão TODOS presentes (fontes, método/fórmula+exclusões,
     limites/natureza, granularidade/janela/unidade, exemplo verificado, memória de cálculo);
 (c) a natureza VINCULANTE está declarada (não-skippável / "mesmo em autosuficiente").
Sem isto, "elicitar antes de implementar sobre indicador regulado" seria prosa que o autosuficiente
bypassa (foi a falha da sessão 2026-06-18). Fail-closed (exit 1 se faltar qualquer parte).

Uso: python tools/test_elicitation_gate.py   (exit 0 PASS; 1 se falha)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, ".agent", "skills", "discovery", "SKILL.md")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# (b) os 6 campos da ficha — ANCORADOS no RÓTULO EM NEGRITO do campo (qa-critic ADR-089: padrões
# genéricos como "font"/"unidade"/"referência" casavam em OUTRAS seções -> teatro. O rótulo `**X**`
# é específico do passo 4.1). +2 sub-checks (EXCLUSÕES no campo 2; decimal no campo 4).
SEIS_CAMPOS = [
    (r"\*\*Fontes\*\*", "1-Fontes (rótulo)"),
    (r"\*\*M[ée]todo/f[óo]rmula", "2-Método/fórmula (rótulo)"),
    (r"inclus[õo]es e EXCLUS|EXCLUS[ÕO]ES", "2-EXCLUSÕES explícitas"),
    (r"\*\*Limites/toler[âa]ncias", "3-Limites/tolerância+natureza (rótulo)"),
    (r"\*\*Granularidade", "4-Granularidade/janela/UNIDADE (rótulo)"),
    (r"decimal", "4-unidade %/decimal"),
    (r"\*\*Exemplo verificado\*\*", "5-Exemplo verificado (rótulo)"),
    (r"\*\*Mem[óo]ria de c[áa]lculo\*\*", "6-Memória de cálculo (rótulo)"),
]
# (c) natureza vinculante
BINDING = [r"VINCULANTE|n[ãa]o-?skipp[áa]vel|não-skippável", r"mesmo em autosufici|autosufici"]


def main():
    fails = []
    if not os.path.isfile(SKILL):
        print(f"RESULTADO: FAIL (discovery/SKILL.md ausente: {SKILL})")
        return 1
    txt = open(SKILL, encoding="utf-8").read()

    # (a) seção do gate existe (ancorada no passo 4.1 — anti-drift, qa-critic)
    if not (("ADR-089" in txt) and re.search(r"ficha de insumo", txt, re.I) and re.search(r"\b4\.1\b", txt)):
        fails.append("seção do elicitation-gate (passo 4.1 / 'ficha de insumo' / ADR-089) ausente no discovery/SKILL.md")

    # (b) 6 campos
    for rx, label in SEIS_CAMPOS:
        if not re.search(rx, txt, re.I):
            fails.append(f"campo da ficha ausente: {label}")

    # (c) natureza vinculante
    for rx in BINDING:
        if not re.search(rx, txt, re.I):
            fails.append(f"natureza vinculante não declarada (padrão ausente: {rx})")

    print(f"elicitation-gate: ficha de insumo (6 campos) + natureza vinculante no discovery — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (elicitation-gate VINCULANTE presente e completo)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
