#!/usr/bin/env python3
"""Canário do risk_score (ADR-086) — prova FERRAMENTAL (não prosa) de que o gating por risco é
determinístico e fail-closed:
 (a) tabela-verdade EXAUSTIVA: os 9 combos (prob,impacto)∈{1,2,3}² → {score,gate,tier} exatos;
 (b) scores possíveis == {1,2,3,4,6,9} (5/7/8 impossíveis como produto — guarda contra matriz torta);
 (c) fail-closed: prob/impacto fora de 1–3, ou item sem campos, ou --items vazio → erro/exit 1;
 (d) agregação worst-case correta; (e) determinismo (2 chamadas idênticas).
Sem isto, "o gate de risco é determinístico" seria prosa. Fail-closed (exit 1 se diverge).

Uso: python tools/test_risk_score.py   (exit 0 PASS; 1 se falha)
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import risk_score as rs  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# (a) tabela-verdade canônica (recast TEA, desambiguada). score = prob*impact.
EXPECT = {
    (1, 1): (1, "NONE", "P3"),
    (1, 2): (2, "NONE", "P2"), (2, 1): (2, "NONE", "P2"),
    (1, 3): (3, "NONE", "P2"), (3, 1): (3, "NONE", "P2"),
    (2, 2): (4, "ADVISORY", "P1"),
    (2, 3): (6, "CONCERNS", "P0"), (3, 2): (6, "CONCERNS", "P0"),
    (3, 3): (9, "FAIL", "P0"),
}


def main():
    fails = []

    # (a) os 9 combos exatos
    for (p, i), (sc, gate, tier) in EXPECT.items():
        r = rs.score_item(p, i)
        if (r["score"], r["gate"], r["tier"]) != (sc, gate, tier):
            fails.append(f"({p},{i}): esperado score={sc}/{gate}/{tier}, veio "
                         f"{r['score']}/{r['gate']}/{r['tier']}")

    # (b) conjunto de scores possíveis == {1,2,3,4,6,9}
    achieved = sorted({rs.score_item(p, i)["score"] for p in (1, 2, 3) for i in (1, 2, 3)})
    if achieved != [1, 2, 3, 4, 6, 9]:
        fails.append(f"scores possíveis {achieved} != [1,2,3,4,6,9] (matriz torta)")

    # (c) fail-closed: prob/impacto inválidos levantam ValueError — inclui não-inteiros
    # (1.0 ∈ (1,2,3) é True em Python; True==1) — type-guard estrito deve rejeitar.
    for p, i in [(0, 1), (4, 1), (1, 0), (1, 4), (-1, 2), (2, 99), (1.0, 2), (2, 3.0), (True, 1), (1, False)]:
        try:
            rs.score_item(p, i)
            fails.append(f"NÃO falhou-closed para prob={p!r},impact={i!r}")
        except ValueError:
            pass
    # item sem campos
    try:
        rs.evaluate([{"id": "x"}])
        fails.append("evaluate NÃO falhou-closed para item sem prob/impact")
    except ValueError:
        pass

    # (d) agregação worst-case
    res, agg = rs.evaluate([{"prob": 1, "impact": 1}, {"prob": 3, "impact": 3}, {"prob": 2, "impact": 2}])
    if agg != "FAIL":
        fails.append(f"agregado esperado FAIL (tem um 9), veio {agg}")
    res2, agg2 = rs.evaluate([{"prob": 1, "impact": 2}, {"prob": 2, "impact": 1}])
    if agg2 != "NONE":
        fails.append(f"agregado esperado NONE (só scores 2), veio {agg2}")
    if rs.aggregate_gate([]) != "NONE":
        fails.append(f"agregado de conjunto VAZIO esperado NONE, veio {rs.aggregate_gate([])}")
    # mix com ADVISORY+CONCERNS (sem FAIL) -> worst=CONCERNS
    _, agg3 = rs.evaluate([{"prob": 2, "impact": 2}, {"prob": 2, "impact": 3}, {"prob": 1, "impact": 1}])
    if agg3 != "CONCERNS":
        fails.append(f"agregado esperado CONCERNS (max=6, sem 9), veio {agg3}")

    # (e) determinismo
    if rs.evaluate([{"prob": 2, "impact": 3}])[0] != rs.evaluate([{"prob": 2, "impact": 3}])[0]:
        fails.append("evaluate não-determinístico")

    # (c2) CLI fail-closed: --items vazio e prob fora de range => exit 1
    for argv in (["--items", os.devnull], ["--prob", "5", "--impact", "1"]):
        # devnull não é JSON-lista; prob=5 é fora de range — ambos devem exit 1
        proc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "risk_score.py"), *argv],
                              capture_output=True, text=True, cwd=ROOT, stdin=subprocess.DEVNULL)
        if proc.returncode == 0:
            fails.append(f"CLI NÃO falhou-closed para args {argv} (exit 0)")

    print(f"risk_score: tabela-verdade 9 combos + scores {{1,2,3,4,6,9}} + fail-closed + "
          f"agregação + determinismo — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (gating por risco determinístico e fail-closed)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
