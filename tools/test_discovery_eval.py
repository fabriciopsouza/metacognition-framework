#!/usr/bin/env python3
"""Eval funcional EXECUTADO do discovery (ADR-042, item 10 do plano de remediação v2).

GAP: os evals dos papéis `discovery` (G) e `mapeamento de processo` (H) estavam DESIGN-TIME
(não executados). A senioridade central era promessa não-medida. Este canário **executa** o eval
funcional ponta-a-ponta: ≥3 briefings sintéticos agnósticos → a saída esperada do discovery
(`requirements.md` com as dimensões) é medida por `check_spec_depth` (cobertura das dimensões do
item 1/ADR-033). Reproduzível em CI — não é tabela de uma vez só.

O que É medido (mecanizável): a saída de discovery cobre as dimensões obrigatórias? E discrimina —
uma saída rasa REPROVA. O que NÃO é medido (→ LIMITS.md): a *qualidade sênior* do default (julgamento).

Uso: python tools/test_discovery_eval.py   (exit 0 PASS; 1 se o eval não discrimina raso de sênior)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_spec_depth import load_bank, check_spec  # noqa: E402
import tempfile  # noqa: E402

DIMS = load_bank()

# 3 briefings sintéticos agnósticos + a saída de discovery esperada (sênior, cobre as dimensões).
SENIOR_OUTPUT = """# Requirements (saída do discovery)
## Dimensões de elicitação
- operador: {op}
- interface: {ui}
- entrada-validacao: lista + valida schema + orienta a fonte
- escopo-temporal: intervalo + acumulado
- recortes-saida: por entidade, por grupo, todos
- persistencia: histórico + reprocesso idempotente
- auditoria-log: registra quem/quando/insumos/versão
- ambiente-execucao: instalação limpa + entry-point não-interativo
- formato-saida: export rastreável à fonte
"""

BRIEFINGS = [
    ("B1: app de indicador recorrente para vários setores, mês a mês",
     SENIOR_OUTPUT.format(op="analista não-técnico -> GUI guiada", ui="app desktop com GUI")),
    ("B2: pipeline que consolida dados de várias fontes periodicamente",
     SENIOR_OUTPUT.format(op="engenheiro de dados -> CLI aceitável", ui="CLI + agendador")),
    ("B3: relatório recorrente para a gestão, exportável",
     SENIOR_OUTPUT.format(op="gestor não-técnico -> leitura", ui="relatório web/export")),
]

# Saída RASA (regressão): discovery que só repete o pedido sem endereçar produto.
SHALLOW_OUTPUT = """# Requirements (saída rasa)
## Objetivo
Construir o que o usuário pediu. Stack a definir.
"""


def run_one(content):
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "requirements.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(content)
        ok, faltando, _ = check_spec(p, DIMS)
        return ok, faltando


def main():
    if not DIMS:
        print("FAIL: banco de dimensões não carregou", file=sys.stderr)
        return 1
    fails = 0
    print("# Eval funcional do discovery (executado) — cobertura de dimensões (ADR-033)")
    for desc, out in BRIEFINGS:
        ok, faltando = run_one(out)
        if not ok:
            fails += 1
        print(f"{'OK  ' if ok else 'FAIL'} [sênior cobre dimensões] {desc}"
              + ("" if ok else f" -> faltando {faltando}"))
    # discriminação: a saída rasa DEVE reprovar
    ok_shallow, faltando = run_one(SHALLOW_OUTPUT)
    discrimina = not ok_shallow
    if not discrimina:
        fails += 1
    print(f"{'OK  ' if discrimina else 'FAIL'} [raso reprova — eval discrimina] saída rasa "
          + ("reprovou (correto)" if discrimina else "PASSOU (eval não discrimina!)"))
    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else f"PASS (discovery EXECUTADO contra {len(BRIEFINGS)} briefings; cobre dimensões e discrimina raso)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
