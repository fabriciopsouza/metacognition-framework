#!/usr/bin/env python3
"""Canário do linter de profundidade de spec (ADR-033, item 1 do plano de remediação v2).

Reproduz o MODO de falha do incidente de campo com fixtures **sintéticas e agnósticas**
(zero termo de domínio — o produto é um "indicador X" genérico): uma spec que só diz
"calcular o indicador" sem endereçar operador/interface/escopo/persistência/log DEVE falhar;
uma spec que decide todas as dimensões obrigatórias DEVE passar; um placeholder não conta
como decisão.

Uso: python tools/test_spec_depth.py   (exit 0 PASS; 1 se o gate não se comporta como devia)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_spec_depth import load_bank, check_spec  # noqa: E402

DIMS = load_bank()

# Spec COMPLETA — todas as 9 dimensões decididas (vocabulário genérico, sem domínio).
SPEC_COMPLETA = """# Requirements — Indicador X (sintético)

## Objetivo
Calcular o indicador X de forma recorrente.

## Dimensões de elicitação (banco agnóstico)
- operador: analista não-técnico → interface guiada (default sênior confirmado)
- interface: app com GUI, seleção de arquivos por janela
- entrada-validacao: produto lista os arquivos necessários e valida o schema antes de processar
- escopo-temporal: ponto único, intervalo e total acumulado (realizado + acumulado)
- recortes-saida: por entidade, por grupo, por período, e "todos"
- persistencia: histórico entre execuções + reprocessar período fechado (idempotente)
- auditoria-log: registra quem rodou, quando, com quais insumos e versão da regra
- ambiente-execucao: testar instalação em máquina limpa; entry-point não-interativo
- formato-saida: relatório exportável com faixas/metas visíveis e números rastreáveis
"""

# Spec RASA — regressão do incidente: só "calcular", sem seção de dimensões.
SPEC_RASA = """# Requirements — Indicador X

## Objetivo
Calcular o indicador X para um período. Stack: linguagem genérica + biblioteca de planilha.

## Critério de aceite
- bate o valor de referência do caso validado.
"""

# Spec FALTANDO duas dimensões obrigatórias (sem operador, sem auditoria-log).
SPEC_FALTANDO = """# Requirements — Indicador X

## Dimensões de elicitação
- interface: CLI
- entrada-validacao: arquivos em pasta fixa
- escopo-temporal: mês único
- recortes-saida: por entidade
- persistencia: sobrescreve a cada execução
- ambiente-execucao: assume libs instaladas
- formato-saida: planilha
"""

# Spec com PLACEHOLDER — dimensão presente mas sem decisão registrada.
SPEC_PLACEHOLDER = SPEC_COMPLETA.replace(
    "operador: analista não-técnico → interface guiada (default sênior confirmado)",
    "operador: <preencher>",
)

# Spec com ALIASES de domínio — usa o vocabulário do projeto, não a chave canônica.
SPEC_ALIASES = """# Requirements — Indicador X

## Dimensões de elicitação
- usuario: leigo → app guiado
- gui: aplicação desktop
- input: upload validado por schema
- periodo: intervalo + acumulado
- granularidade: por grupo + todos
- memoria: histórico persistido
- log: trilha de auditoria completa
- instalacao: validar em máquina limpa
- saida: relatório exportável
"""

# Regressão do falso-PASS por substring (process-critic ADR-011): usa 'ui' e 'saida', que ANTES
# casavam por substring 'req(ui)sitos' (ambiente-execucao) e 'recortes-(saida)' — creditando dimensões
# que a spec NÃO endereçou. Faltam de fato recortes-saida e ambiente-execucao -> DEVE falhar.
SPEC_SUBSTRING_TRAP = """# Requirements — Indicador X

## Dimensões de elicitação
- operador: leigo
- ui: app com GUI
- entrada-validacao: valida schema
- escopo-temporal: intervalo + acumulado
- persistencia: histórico
- auditoria-log: trilha completa
- saida: relatório exportável
"""

CASES = [
    ("spec completa decide as 9 dimensões", SPEC_COMPLETA, True),
    ("regressão falso-PASS substring (ui/saida não cobrem ambiente/recortes)", SPEC_SUBSTRING_TRAP, False),
    ("spec rasa (só 'calcular X', sem dimensões) — regressão de campo", SPEC_RASA, False),
    ("spec faltando operador + auditoria-log", SPEC_FALTANDO, False),
    ("spec com placeholder '<preencher>' não conta como decisão", SPEC_PLACEHOLDER, False),
    ("spec usando aliases de domínio cobre as dimensões", SPEC_ALIASES, True),
]


def main():
    if not DIMS:
        print("FAIL: banco de dimensões não carregou", file=sys.stderr)
        return 1
    fails = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, (desc, content, expect_pass) in enumerate(CASES):
            p = os.path.join(tmp, f"requirements_{i}.md")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(content)
            ok, faltando, _ = check_spec(p, DIMS)
            correct = ok == expect_pass
            if not correct:
                fails += 1
            status = "OK  " if correct else "FAIL"
            exp = "PASS" if expect_pass else "FAIL"
            got = "PASS" if ok else f"FAIL({','.join(faltando)})"
            print(f"{status} [esperado {exp:4} -> obteve {got}] {desc}")
    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails} caso(s))" if fails
          else "PASS (gate barra spec rasa; aceita spec que decide as dimensões)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
