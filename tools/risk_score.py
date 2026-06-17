#!/usr/bin/env python3
"""risk_score — gating determinístico por risco (FORMA agnóstica; ADR-086, recast do TEA/BMAD).

P15 (determinismo-primeiro): o "quanto de QA/rigor gastar" deixa de ser julgamento implícito e
vira **mecanismo determinístico** — `risco = probabilidade × impacto` → gate + tier de cobertura.
Recast da matriz risk-based-testing do `bmad-method-test-architecture-enterprise` (TEA), no idioma
do framework: FORMA agnóstica (o mecanismo) vive no núcleo; o CONTEÚDO (lista de categorias, o que
conta como "impacto alto" num domínio) é INPUT/blueprint, não hardcoded (P12 / ADR-085).

MATRIZ (prob, impacto ∈ {1,2,3}; score = prob×impacto → {1,2,3,4,6,9}; 5/7/8 são IMPOSSÍVEIS):
  gate:  9 → FAIL · 6 → CONCERNS · 4 → ADVISORY · 1/2/3 → NONE
  tier:  6–9 → P0 · 4–5 → P1 · 2–3 → P2 · 1 → P3   (disjunto por prioridade-mais-alta —
         desambigua as faixas SOBREPOSTAS do TEA original, que não eram determinísticas)

Fail-closed: prob/impacto fora de 1–3, ou item sem os campos, => erro (exit 1). Sem julgamento
subjetivo: limiares fixos e auditáveis. Determinístico: mesma entrada ⇒ mesma saída.

Uso:
    python tools/risk_score.py --items risco.json      # [{id,prob,impact[,cat,nota]}] -> veredito
    python tools/risk_score.py --prob 3 --impact 3      # item único inline
    (importável: from risk_score import score_item, aggregate_gate)

Exit 0 = ok (mesmo com itens FAIL — o veredito É a saída); exit 1 = entrada inválida (fail-closed).
"""
import argparse
import json
import sys

VALID = (1, 2, 3)
# Ordem de severidade do gate (para agregação worst-case).
GATE_ORDER = {"NONE": 0, "ADVISORY": 1, "CONCERNS": 2, "FAIL": 3}


def _gate(score):
    # scores possíveis = {1,2,3,4,6,9} (5/7/8 impossíveis como produto de {1,2,3}²);
    # os `>=` cobrem faixas para robustez, mas só estes 6 valores ocorrem de fato.
    if score >= 9:
        return "FAIL"        # 9: bloqueia release sem mitigação
    if score >= 6:
        return "CONCERNS"    # 6: plano de mitigação documentado exigido
    if score >= 4:
        return "ADVISORY"    # 4: recomendado, sem gate
    return "NONE"            # 1–3: sem ação


def _tier(score):
    # disjunto por prioridade-mais-alta (desambigua faixas sobrepostas do TEA)
    if score >= 6:
        return "P0"          # cobertura máxima
    if score >= 4:
        return "P1"
    if score >= 2:
        return "P2"
    return "P3"              # smoke only


def score_item(prob, impact):
    """Núcleo determinístico. Levanta ValueError (fail-closed) se não-inteiro ou fora de 1–3."""
    # type-guard: `type is int` rejeita float (1.0 ∈ (1,2,3) é True) E bool (True==1) — fail-closed estrito.
    if type(prob) is not int or type(impact) is not int:
        raise ValueError(f"prob/impact devem ser INTEIROS; recebido prob={prob!r} ({type(prob).__name__}) "
                         f"impact={impact!r} ({type(impact).__name__})")
    if prob not in VALID or impact not in VALID:
        raise ValueError(f"prob/impact devem estar em {VALID}; recebido prob={prob!r} impact={impact!r}")
    score = prob * impact
    return {"prob": prob, "impact": impact, "score": score, "gate": _gate(score), "tier": _tier(score)}


def aggregate_gate(results):
    """Gate do conjunto = pior gate individual (worst-case). Conjunto vazio => NONE."""
    worst = "NONE"
    for r in results:
        if GATE_ORDER[r["gate"]] > GATE_ORDER[worst]:
            worst = r["gate"]
    return worst


def evaluate(items):
    """items: lista de dicts com prob/impact (+ campos livres preservados: id/cat/nota).
    Retorna (results, aggregate). Fail-closed via ValueError em item inválido."""
    results = []
    for i, it in enumerate(items):
        if "prob" not in it or "impact" not in it:
            raise ValueError(f"item #{i} sem 'prob'/'impact': {it!r}")
        sc = score_item(it["prob"], it["impact"])
        out = {k: it[k] for k in ("id", "cat", "nota") if k in it}
        out.update(sc)
        results.append(out)
    return results, aggregate_gate(results)


def main(argv):
    ap = argparse.ArgumentParser(description="Gating determinístico por risco (prob×impacto). ADR-086.")
    ap.add_argument("--items", help="JSON: lista de {id,prob,impact[,cat,nota]}")
    ap.add_argument("--prob", type=int, help="probabilidade 1-3 (item único)")
    ap.add_argument("--impact", type=int, help="impacto 1-3 (item único)")
    args = ap.parse_args(argv[1:])

    try:
        if args.items:
            with open(args.items, encoding="utf-8") as fh:
                items = json.load(fh)
            if not isinstance(items, list) or not items:
                print("ERRO (fail-closed): --items deve ser lista NÃO-vazia", file=sys.stderr)
                return 1
            results, agg = evaluate(items)
        elif args.prob is not None and args.impact is not None:
            results, agg = evaluate([{"prob": args.prob, "impact": args.impact}])
        else:
            print("ERRO: forneça --items <json> OU --prob N --impact N", file=sys.stderr)
            return 1
    except (ValueError, json.JSONDecodeError, OSError) as e:
        print(f"ERRO (fail-closed): {e}", file=sys.stderr)
        return 1

    print(json.dumps({"itens": results, "gate_agregado": agg}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
