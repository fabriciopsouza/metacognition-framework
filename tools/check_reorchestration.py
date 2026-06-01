#!/usr/bin/env python3
"""check_reorchestration.py — verifica a decisão de RE-ORQUESTRAÇÃO do PMO na fronteira de bloco (ADR-045).

CONTEXTO (emenda ao ADR-011): voltar ao PMO a CADA gate não compensa (custo+loop+gargalo). A opção
adotada é o PMO como **maestro de re-orquestração na fronteira de BLOCO**: após o process-critic emitir
APROVADO_LIMPO, o controle volta ao PMO para UMA decisão explícita registrada no history.md —
`RE-ORQUESTRAÇÃO: <prosseguir | re-priorizar X | rewind J_i | injetar escopo Y | reativar estágio Z>`.
O intra-bloco segue forward-only (circuit-breaker do ADR-011 preservado).

Este linter mecaniza o que É verificável: **o bloco mais recente fechado registrou a decisão?** A
QUALIDADE da decisão (julgamento de re-orquestração) NÃO é mecanizável → declarada em LIMITS.md.
Audita só o ÚLTIMO bloco fechado (não retroage convenção a blocos antigos).

Uso:
    python tools/check_reorchestration.py [history.md]   # default: ./history.md
Exit 0 se o último bloco fechado tem decisão (ou não há bloco a auditar); 1 se fechou sem decisão.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Marcador de BLOCO FECHADO: o veredito binário do process-critic (ADR-011). Token específico
# (evita falso-positivo em prosa negativa tipo "bloco não fechado").
CLOSE = re.compile(r"\baprovado_limpo\b", re.IGNORECASE)
# Marcador da DECISÃO do PMO: campo DECLARADO com dois-pontos (não menção em prosa).
DECISION = re.compile(r"re-?orquestra[çc][ãa]o\s*:", re.IGNORECASE)


def check_text(text):
    """Retorna (ok, motivo). ok=True se não há bloco a auditar ou o último bloco tem decisão."""
    lines = text.splitlines()
    closes = [i for i, l in enumerate(lines) if CLOSE.search(l)]
    if not closes:
        return True, "nenhum bloco fechado marcado — nada a auditar (advisory)"
    last = closes[-1]
    window = lines[last:]
    if any(DECISION.search(l) for l in window):
        return True, "último bloco fechado tem RE-ORQUESTRAÇÃO do PMO registrada"
    return False, ("bloco fechado SEM decisão de RE-ORQUESTRAÇÃO do PMO (ADR-045): registre "
                   "'RE-ORQUESTRAÇÃO: prosseguir|re-priorizar|rewind J_i|injetar escopo|reativar estágio'")


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    path = argv[1] if len(argv) > 1 else os.path.join(ROOT, "history.md")
    if not os.path.isfile(path):
        print(f"history.md não encontrado em {path} — nada a auditar.")
        return 0
    text = open(path, encoding="utf-8-sig").read()
    ok, motivo = check_text(text)
    print(("PASS: " if ok else "FAIL: ") + motivo)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
