#!/usr/bin/env python3
"""autonomy_policy — retry/escalate determinístico por MODO (ADR-087, recast H sob P15).

Mecaniza o "dial por modo" do P15: o que acontece quando uma junção FALHA (ex.: qa-critic FAIL)?
 - MODOS HITL (default/avançado): escala ao humano na PRIMEIRA falha (HITL preservado).
 - MODO AUTÔNOMO (autosuficiente): AUTO-RECUPERA — retenta subindo a escada de modelo (ADR-078/082)
   até o BUDGET, e **escala só como ÚLTIMO passo** (doutrina do bmad-automator: "escalation is the
   last step, not the first response"). Sobe a escada de CAPACIDADE: haiku < sonnet < opus < fable.

ESCOPO/limite declarado (ADR-078/082 harness_limit): o fallback de modelo aplica-se ao DISPATCH DE
SUBAGENTE (developer/qa-critic via Agent(model=...)), onde o framework controla o modelo — NÃO ao
modelo INTERATIVO da sessão (controle do harness/`/model`). O resolvedor diz QUAL modelo usar no
retry; o orquestrador EXECUTA o retry (parte prosa-pela-porta do P15).

Fail-closed: modo/modelo desconhecido, budget/attempt negativo => ValueError. Determinístico.

Uso:
    python tools/autonomy_policy.py --mode autosuficiente --attempt 0 --budget 2 --model sonnet
    (importável: from autonomy_policy import next_action)

Exit 0 sempre que a entrada é válida (a saída É o veredito retry/escalate); 1 = entrada inválida.
"""
import argparse
import json
import sys

# Escada de CAPACIDADE ascendente (retry sobe). Fonte conceitual: tiers do model-policy.json (ADR-078).
CAP_ORDER = ["haiku", "sonnet", "opus", "fable"]
HITL_MODES = {"default", "avancado"}
AUTONOMOUS_MODES = {"autosuficiente"}


def next_action(mode, attempt, budget, current_model):
    """Resolve a próxima ação numa junção FALHA. Fail-closed (ValueError) em entrada inválida.
    Retorna {action: 'retry'|'escalate', next_model: <str|None>, reason: <str>}."""
    if mode not in (HITL_MODES | AUTONOMOUS_MODES):
        raise ValueError(f"modo desconhecido: {mode!r} (use {sorted(HITL_MODES | AUTONOMOUS_MODES)})")
    if current_model not in CAP_ORDER:
        raise ValueError(f"modelo desconhecido: {current_model!r} (use {CAP_ORDER})")
    # `type is int` rejeita bool (True==1 / isinstance(True,int)==True) e float — fail-closed estrito.
    if type(attempt) is not int or type(budget) is not int or attempt < 0 or budget < 0:
        raise ValueError(f"attempt/budget devem ser INTEIROS >= 0; recebido attempt={attempt!r} budget={budget!r}")

    # MODOS HITL: escala na primeira falha — NUNCA auto-retenta (preserva HITL).
    if mode in HITL_MODES:
        return {"action": "escalate", "next_model": None,
                "reason": f"modo {mode} é HITL: escala ao humano na primeira falha"}

    # MODO AUTÔNOMO: auto-recupera dentro do budget, subindo a escada; escala por ÚLTIMO.
    idx = CAP_ORDER.index(current_model)
    if attempt < budget and idx < len(CAP_ORDER) - 1:
        return {"action": "retry", "next_model": CAP_ORDER[idx + 1],
                "reason": f"auto-recuperação {attempt + 1}/{budget}: sobe {current_model}->{CAP_ORDER[idx + 1]}"}
    # escala por último — pode haver MAIS de um motivo simultâneo (budget esgotado E topo da escada);
    # lista todos os aplicáveis (auditabilidade completa — ressalva qa-critic ADR-087).
    causes = []
    if attempt >= budget:
        causes.append("budget esgotado")
    if idx >= len(CAP_ORDER) - 1:
        causes.append(f"topo da escada ({current_model})")
    return {"action": "escalate", "next_model": None,
            "reason": f"escalar ao humano ({' + '.join(causes)}) — último passo, não o primeiro"}


def main(argv):
    ap = argparse.ArgumentParser(description="Política retry/escalate por modo (ADR-087).")
    ap.add_argument("--mode", required=True)
    ap.add_argument("--attempt", type=int, required=True, help="retries já feitos (0 = primeira falha)")
    ap.add_argument("--budget", type=int, required=True, help="máx. de retries no modo autônomo")
    ap.add_argument("--model", required=True, help="modelo atual do autor")
    args = ap.parse_args(argv[1:])
    try:
        out = next_action(args.mode, args.attempt, args.budget, args.model)
    except ValueError as e:
        print(f"ERRO (fail-closed): {e}", file=sys.stderr)
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
