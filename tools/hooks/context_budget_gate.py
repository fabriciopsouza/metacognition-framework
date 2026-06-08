#!/usr/bin/env python3
"""context_budget_gate.py — Hook PreToolUse(Read): MECANIZA "fracionar contexto maior" (pedido do
dono 2026-06-08). Quando o agente vai LER um arquivo grande inteiro, o hook ANUNCIA (additionalContext,
nao-bloqueante — "gates anunciados") que a fonte excede o orcamento e deveria ser fracionada via
doc-intake. Faz a regra deixar de ser prosa/disciplina: aparece em TODA leitura grande.

Por que NAO bloquear: as vezes ler inteiro e legitimo (arquivo que vou editar). Bloquear Read seria
hostil. O mecanismo correto e tornar o desperdicio VISIVEL a cada ocorrencia (auto-correcao), nao
impedir. Onde a maquina permite hook, isto roda; onde um EDR/AAC veta hook (ex. a 9TRP7H4 com
Kaspersky — NEM TODA maquina tem), fica a doutrina + o tool chamavel `context_budget.py` (limite
declarado, nao mascarado; nao assumir veto sem verificar a maquina).

Contrato PreToolUse: le JSON no stdin (tool_input.file_path). Emite hookSpecificOutput.additionalContext
se acima do orcamento; senao silencioso. SEMPRE exit 0 (fail-open — nunca quebra a leitura).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def _emit(ctx):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "additionalContext": ctx}}, ensure_ascii=True))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # sem input valido -> fail-open
    ti = payload.get("tool_input") or {}
    path = ti.get("file_path") or ti.get("path")
    if not path or not os.path.isfile(path):
        return 0
    try:
        import context_budget as cb
        r = cb.assess(path)
    except Exception:
        return 0  # fail-open
    if r.get("over_budget"):
        _emit(f"[context-budget] '{os.path.basename(path)}' ~{r['est_tokens']} tokens > orcamento "
              f"{r['budget_tokens']}. Considere FRACIONAR: `python tools/doc_intake.py \"{path}\" "
              f"--out manifest.json` e citar por chunk+sha, OU ler cirurgicamente (grep + offset/limit) "
              f"em vez do arquivo inteiro. (anti-queima de tokens; nao-bloqueante)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
