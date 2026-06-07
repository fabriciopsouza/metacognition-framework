#!/usr/bin/env python3
"""Canario dev-dogfood DETERMINISTICO (ADR-074 emendado): um repo-MASTER (dev) que fecha bloco DEVE
ter os artefatos de dogfood — execution-report (telemetria de processo) + handoff cross-IA. NAO e
opt-in nem provocado: o opt-in e so a PUBLICACAO publica (ADR-062/063); a GERACAO dev-side e exigida.

Shadow-aware (ADR-070): so MASTER gera cross-IA. Detecta master pela presenca de `docs/_private/`
(o cofre, stripado dos shadows por export-clean) -> num shadow, este canario PASSA (nao cobra cross-IA).

FORWARD-floor honesto: exige que os artefatos EXISTAM (CI vermelho num master sem eles -> forca o
dogfood). Frescor por-release e disciplina do /checkpoint (ADR-074 camada de oferta); o EXISTIR e o
piso determinista que tira o "so gera se o dono pedir".

Uso: python tools/test_dev_dogfood.py   (exit 0 PASS; 1 se falha)
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    priv = os.path.join(ROOT, "docs", "_private")
    if not os.path.isdir(priv):
        print("docs/_private ausente -> SHADOW (so master gera cross-IA). PASS (nao cobra dogfood).")
        print("RESULTADO: PASS (shadow — sem cobranca de cross-IA)")
        return 0

    fails = []
    execs = glob.glob(os.path.join(priv, "execution-report-*.md"))
    handoffs = glob.glob(os.path.join(priv, "cross-ai", "outbox", "*.md"))
    if not execs:
        fails.append("MASTER sem execution-report (docs/_private/execution-report-*.md) — dogfood dev nao gerado")
    if not handoffs:
        fails.append("MASTER sem handoff cross-IA (docs/_private/cross-ai/outbox/*.md) — melhoria nao propagada")

    print(f"master(docs/_private)=True; execution-reports={len(execs)}; handoffs cross-IA={len(handoffs)} — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (master tem dogfood dev determinista: report + handoff cross-IA)" if not fails
          else f"FAIL ({len(fails)} — dogfood dev exigido, nao opt-in)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
