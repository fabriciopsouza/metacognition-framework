#!/usr/bin/env python3
"""check_attribution.py — guarda TRANSPARENTE de autoria (ADR-025).

Falha (exit 1) se a atribuição obrigatória (LICENSE + NOTICE + crédito no README) for removida.
É aberto e documentado de propósito: proteção de autoria por **licença (CC BY 4.0) + integridade
visível + commits assinados** — NUNCA por mecanismo oculto, telemetria silenciosa ou "phone-home"
(ADR-025 refuta o covert explicitamente). Num fork que tire o crédito, o CI do próprio fork acusa.

Uso: python tools/check_attribution.py   (exit 0 se ok; 1 se atribuição ausente)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# arquivo obrigatório -> trecho que prova a atribuição ao autor canônico
ATTRIBUTION = {
    "LICENSE": "github.com/fabriciopsouza",
    "NOTICE": "github.com/fabriciopsouza",
    "README.md": "fabriciopsouza/metacognition-framework",
}


def main():
    fails = []
    for fname, needle in ATTRIBUTION.items():
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            fails.append(f"arquivo de atribuicao ausente: {fname}")
            continue
        with open(path, encoding="utf-8") as fh:
            if needle not in fh.read():
                fails.append(f"atribuicao ausente em {fname} (esperado conter: '{needle}')")
    for x in fails:
        print(f"FAIL {x}")
    print("-" * 48)
    if fails:
        print(f"RESULTADO: FAIL ({len(fails)}) — atribuicao ao autor removida/ausente "
              f"(viola CC BY 4.0 / ADR-025).")
        return 1
    print("RESULTADO: PASS (atribuicao ao autor presente em LICENSE + NOTICE + README).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
