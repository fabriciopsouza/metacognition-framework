#!/usr/bin/env python3
"""Canário do autonomy_policy (ADR-087) — prova FERRAMENTAL de que o dial retry/escalate por modo é
determinístico e fail-closed:
 (a) MODOS HITL (default/avançado) SEMPRE escalam na 1ª falha — nunca auto-retentam (HITL preservado);
 (b) MODO autônomo retenta subindo a escada (haiku<sonnet<opus<fable) até budget; escala por ÚLTIMO
     (budget esgotado OU topo da escada);
 (c) fail-closed: modo/modelo desconhecido, attempt/budget negativo ou não-inteiro => ValueError.
Sem isto, "autosuficiente auto-recupera mas HITL não" seria prosa. Fail-closed (exit 1 se diverge).

Uso: python tools/test_autonomy_policy.py   (exit 0 PASS; 1 se falha)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import autonomy_policy as ap  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# (mode, attempt, budget, model) -> (action, next_model)
EXPECT = {
    # (a) HITL escala sempre — independe de attempt/budget/model
    ("default", 0, 2, "sonnet"): ("escalate", None),
    ("default", 0, 9, "haiku"): ("escalate", None),
    ("avancado", 0, 5, "opus"): ("escalate", None),
    # (b) autônomo: retenta subindo a escada
    ("autosuficiente", 0, 2, "haiku"): ("retry", "sonnet"),
    ("autosuficiente", 0, 2, "sonnet"): ("retry", "opus"),
    ("autosuficiente", 1, 2, "opus"): ("retry", "fable"),
    # ... escala por último: budget esgotado
    ("autosuficiente", 2, 2, "opus"): ("escalate", None),
    ("autosuficiente", 0, 0, "sonnet"): ("escalate", None),
    # ... escala por último: já no topo da escada (fable), mesmo com budget restante
    ("autosuficiente", 0, 5, "fable"): ("escalate", None),
}


def main():
    fails = []

    for (mode, att, bud, model), (want_action, want_model) in EXPECT.items():
        r = ap.next_action(mode, att, bud, model)
        if (r["action"], r["next_model"]) != (want_action, want_model):
            fails.append(f"({mode},att={att},bud={bud},{model}): esperado {want_action}/{want_model}, "
                         f"veio {r['action']}/{r['next_model']}")
        if "reason" not in r or not r["reason"]:
            fails.append(f"({mode},...): sem 'reason'")

    # invariante crítico (exaustivo em budgets também): NENHUM modo HITL retorna 'retry' — jamais
    # auto-retenta, independente de attempt/budget/model.
    for mode in ("default", "avancado"):
        for model in ap.CAP_ORDER:
            for att in (0, 1, 5):
                for bud in (0, 1, 2, 9):
                    if ap.next_action(mode, att, bud, model)["action"] != "escalate":
                        fails.append(f"VIOLAÇÃO HITL: {mode} retornou retry (att={att},bud={bud},{model})")

    # invariante: autônomo NUNCA escala enquanto há budget E há degrau acima (escalação é último passo)
    for att in range(0, 2):
        for model in ("haiku", "sonnet", "opus"):
            r = ap.next_action("autosuficiente", att, 2, model)
            if r["action"] != "retry":
                fails.append(f"autônomo escalou cedo demais (att={att},{model},budget=2): {r['action']}")

    # (c) fail-closed
    bad = [("bogus", 0, 2, "sonnet"), ("autosuficiente", 0, 2, "gpt"),
           ("autosuficiente", -1, 2, "sonnet"), ("autosuficiente", 0, -1, "sonnet"),
           ("autosuficiente", 1.0, 2, "sonnet"), ("autosuficiente", 0, 2, ""),
           ("autosuficiente", True, 2, "sonnet"), ("autosuficiente", 0, False, "sonnet")]
    for args in bad:
        try:
            ap.next_action(*args)
            fails.append(f"NÃO falhou-closed para {args}")
        except ValueError:
            pass

    # determinismo
    if ap.next_action("autosuficiente", 0, 2, "sonnet") != ap.next_action("autosuficiente", 0, 2, "sonnet"):
        fails.append("next_action não-determinístico")

    print(f"autonomy_policy: HITL-sempre-escala + autônomo-retenta-subindo-até-budget + fail-closed — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (dial retry/escalate por modo determinístico e fail-closed)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
