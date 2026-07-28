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
  hitl:  score ≥ 6 → revisão humana OBRIGATÓRIA antes do hand-off (ADR-096; corte do dono)

HITL é eixo ORTOGONAL ao gate, não um rebatismo dele (ADR-096): o gate classifica SEVERIDADE
(FAIL/CONCERNS/ADVISORY/NONE — taxonomia do recast TEA, preservada); `hitl` responde a pergunta
operacional "posso passar adiante sem humano?". Colapsar 6 em FAIL destruiria a faixa CONCERNS.

Fail-closed: prob/impacto fora de 1–3, ou item sem os campos, => erro (exit 1). Sem julgamento
subjetivo: limiares fixos e auditáveis. Determinístico: mesma entrada ⇒ mesma saída.

Uso:
    python tools/risk_score.py --items risco.json      # [{id,prob,impact[,cat,nota]}] -> veredito
    python tools/risk_score.py --prob 3 --impact 3      # item único inline
    python tools/risk_score.py --items r.json --gate-exit   # BLOQUEIA (exit 2) se hitl_requerido
    (importável: from risk_score import score_item, aggregate_gate, hitl_required)

Exit 0 = liberado; exit 1 = entrada inválida (fail-closed); exit 2 = HITL requerido, SÓ com
`--gate-exit` (sem a flag o veredito é a saída e o exit é 0 mesmo com FAIL — compat. ADR-086).
Códigos 1 e 2 são DISTINTOS de propósito: "conserte a entrada" ≠ "busque aprovação humana";
um hook que confundisse os dois trataria JSON malformado como risco aceito-com-humano.
"""
import argparse
import json
import sys

VALID = (1, 2, 3)
# Ordem de severidade do gate (para agregação worst-case).
GATE_ORDER = {"NONE": 0, "ADVISORY": 1, "CONCERNS": 2, "FAIL": 3}
# Corte do HITL (ADR-096): score ≥ 6 trava o hand-off até revisão humana.
# Alcança 2×3, 3×2 e 3×3. NÃO alcança 1×3 (raro × catastrófico = 3) — lacuna ACEITA
# explicitamente pelo dono ao escolher o corte multiplicativo; ver ADR-096 §Consequências.
HITL_MIN_SCORE = 6


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


def _hitl(score):
    """Revisão humana obrigatória? Corte do dono (ADR-096), ortogonal ao gate."""
    return score >= HITL_MIN_SCORE


def score_item(prob, impact):
    """Núcleo determinístico. Levanta ValueError (fail-closed) se não-inteiro ou fora de 1–3."""
    # type-guard: `type is int` rejeita float (1.0 ∈ (1,2,3) é True) E bool (True==1) — fail-closed estrito.
    if type(prob) is not int or type(impact) is not int:
        raise ValueError(f"prob/impact devem ser INTEIROS; recebido prob={prob!r} ({type(prob).__name__}) "
                         f"impact={impact!r} ({type(impact).__name__})")
    if prob not in VALID or impact not in VALID:
        raise ValueError(f"prob/impact devem estar em {VALID}; recebido prob={prob!r} impact={impact!r}")
    score = prob * impact
    return {"prob": prob, "impact": impact, "score": score, "gate": _gate(score),
            "tier": _tier(score), "hitl": _hitl(score)}


def aggregate_gate(results):
    """Gate do conjunto = pior gate individual (worst-case). Conjunto vazio => NONE."""
    worst = "NONE"
    for r in results:
        if GATE_ORDER[r["gate"]] > GATE_ORDER[worst]:
            worst = r["gate"]
    return worst


def hitl_required(results):
    """Conjunto exige revisão humana? UM item ≥ HITL_MIN_SCORE basta (worst-case, como o gate).
    Lê o score, não o campo `hitl`: item vindo de dict externo pode não trazê-lo."""
    return any(r["score"] >= HITL_MIN_SCORE for r in results)


def evaluate(items):
    """items: lista de dicts com prob/impact (+ campos livres preservados: id/cat/nota).
    Retorna (results, aggregate). Fail-closed via ValueError em item inválido."""
    results = []
    for i, it in enumerate(items):
        # Guarda de tipo ANTES do 'in': `["prob impact"]` passava porque o
        # operador `in` casa substring em str, e `[1,2]` estourava TypeError
        # cru — o exit 1 vinha do interpretador, por acidente, não por desenho.
        if not isinstance(it, dict):
            raise ValueError(f"item #{i} não é objeto JSON: {it!r}")
        if "prob" not in it or "impact" not in it:
            raise ValueError(f"item #{i} sem 'prob'/'impact': {it!r}")
        sc = score_item(it["prob"], it["impact"])
        out = {k: it[k] for k in ("id", "cat", "nota") if k in it}
        out.update(sc)
        results.append(out)
    return results, aggregate_gate(results)


class _ParserFailClosed(argparse.ArgumentParser):
    """argparse sai 2 em erro de uso — e 2 é o código do HITL neste contrato.

    Achado CRÍTICO do qa-critic adversarial: `--prob abc`, valor faltando ou
    typo de flag saíam com 2, indistinguíveis de "HITL requerido". Um hook
    registraria "aguardando humano" como evidência de item que nunca foi
    avaliado — exatamente a confusão que o ADR-096 declara ter rejeitado na
    Alternativa 2. Erro de uso é entrada inválida: sai 1, fail-closed.
    """

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"ERRO (fail-closed): {message}", file=sys.stderr)
        raise SystemExit(1)


def main(argv):
    ap = _ParserFailClosed(description="Gating determinístico por risco (prob×impacto). ADR-086.")
    ap.add_argument("--items", help="JSON: lista de {id,prob,impact[,cat,nota]}")
    ap.add_argument("--prob", type=int, help="probabilidade 1-3 (item único)")
    ap.add_argument("--impact", type=int, help="impacto 1-3 (item único)")
    ap.add_argument("--gate-exit", action="store_true",
                    help=f"exit 2 se algum item tem score >= {HITL_MIN_SCORE} (HITL obrigatório). "
                         "Sem a flag, o exit é 0 e o veredito é a saída (compat. ADR-086).")
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

    hitl = hitl_required(results)
    print(json.dumps({"itens": results, "gate_agregado": agg, "hitl_requerido": hitl,
                      "hitl_min_score": HITL_MIN_SCORE}, ensure_ascii=False, indent=1))
    if hitl and args.gate_exit:
        print(f"BLOQUEADO: item com score >= {HITL_MIN_SCORE} exige revisão humana antes do "
              "hand-off (ADR-096).", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
