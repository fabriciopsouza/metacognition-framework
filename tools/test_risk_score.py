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
import json
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
# 4ª coluna = hitl (ADR-096): score >= 6. Note (1,3) e (3,1) = 3 -> hitl False:
# raro × catastrófico NÃO trava o hand-off. Lacuna ACEITA pelo dono, travada aqui
# para que só mude com ADR — não por deriva silenciosa.
EXPECT = {
    (1, 1): (1, "NONE", "P3", False),
    (1, 2): (2, "NONE", "P2", False), (2, 1): (2, "NONE", "P2", False),
    (1, 3): (3, "NONE", "P2", False), (3, 1): (3, "NONE", "P2", False),
    (2, 2): (4, "ADVISORY", "P1", False),
    (2, 3): (6, "CONCERNS", "P0", True), (3, 2): (6, "CONCERNS", "P0", True),
    (3, 3): (9, "FAIL", "P0", True),
}


def main():
    fails = []

    # (a) os 9 combos exatos
    for (p, i), (sc, gate, tier, hitl) in EXPECT.items():
        r = rs.score_item(p, i)
        if (r["score"], r["gate"], r["tier"], r["hitl"]) != (sc, gate, tier, hitl):
            fails.append(f"({p},{i}): esperado score={sc}/{gate}/{tier}/hitl={hitl}, veio "
                         f"{r['score']}/{r['gate']}/{r['tier']}/hitl={r['hitl']}")

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

    # (d2) agregação do HITL (ADR-096): worst-case — UM item >= 6 basta.
    res_h, _ = rs.evaluate([{"prob": 1, "impact": 1}, {"prob": 3, "impact": 2}])
    if not rs.hitl_required(res_h):
        fails.append("hitl_required esperado True (tem um 6), veio False")
    res_n, _ = rs.evaluate([{"prob": 2, "impact": 2}, {"prob": 1, "impact": 3}])
    if rs.hitl_required(res_n):
        fails.append("hitl_required esperado False (max=4; 1x3=3 NÃO gateia), veio True")
    if rs.hitl_required([]):
        fails.append("hitl_required de conjunto VAZIO esperado False, veio True")
    if rs.HITL_MIN_SCORE != 6:
        fails.append(f"HITL_MIN_SCORE mudou para {rs.HITL_MIN_SCORE} sem ADR (corte do dono = 6)")

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

    # (f) exit codes do --gate-exit (ADR-096). O contrato é o que um hook consegue ler:
    #     0 = liberado · 1 = entrada inválida · 2 = HITL requerido.
    #     O último caso é o crítico: entrada inválida COM --gate-exit deve dar 1, não 2 —
    #     fail-closed precede o gate, senão JSON torto viraria "risco aceito com humano".
    for argv, esperado, porque in (
        (["--prob", "3", "--impact", "2", "--gate-exit"], 2, "score 6 com flag -> bloqueia"),
        (["--prob", "3", "--impact", "3", "--gate-exit"], 2, "score 9 com flag -> bloqueia"),
        (["--prob", "3", "--impact", "2"], 0, "score 6 SEM flag -> compat. ADR-086 (exit 0)"),
        (["--prob", "2", "--impact", "2", "--gate-exit"], 0, "score 4 -> abaixo do corte"),
        (["--prob", "1", "--impact", "3", "--gate-exit"], 0, "score 3 (raro x catastrofico) -> lacuna aceita"),
        (["--prob", "5", "--impact", "1", "--gate-exit"], 1, "invalido + flag -> fail-closed PRECEDE o gate"),
    ):
        proc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "risk_score.py"), *argv],
                              capture_output=True, text=True, cwd=ROOT, stdin=subprocess.DEVNULL)
        if proc.returncode != esperado:
            fails.append(f"exit {proc.returncode} != {esperado} para {argv} ({porque})")

    # (c3) guarda de TIPO no item (A5 do qa-critic). Sem ela, `["prob impact"]`
    #      atravessava porque `in` casa substring em str, e `[1,2]` estourava
    #      TypeError cru — exit 1 vinha do interpretador, por acidente.
    for ruim in ([1, 2], ["prob impact"], [None], [[1, 2]], [{"prob": 1, "impact": 1}, 7]):
        try:
            rs.evaluate(ruim)
            fails.append(f"evaluate NÃO falhou-closed para item não-dict: {ruim!r}")
        except ValueError:
            pass
        except Exception as e:
            fails.append(f"evaluate levantou {type(e).__name__} (esperado ValueError) "
                         f"para {ruim!r} — fail-closed por acidente, não por desenho")

    # (g) ERRO DE USO DO ARGPARSE => 1, nunca 2 (achado CRÍTICO do qa-critic).
    #     argparse sai 2 por padrão, que é o código do HITL. Um hook leria
    #     "aguardando humano" para item que nunca foi avaliado.
    for argv, porque in (
        (["--prob", "abc", "--impact", "3", "--gate-exit"], "tipo inválido no valor"),
        (["--prob", "3", "--impact", "--gate-exit"], "valor faltando"),
        (["--flag-que-nao-existe"], "flag inexistente"),
    ):
        proc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "risk_score.py"), *argv],
                              capture_output=True, text=True, cwd=ROOT, stdin=subprocess.DEVNULL)
        if proc.returncode != 1:
            fails.append(f"erro de uso saiu {proc.returncode} != 1 para {argv} ({porque}) "
                         "— exit 2 colide com HITL requerido")

    # (h) FORMA DO STDOUT. O canário aferia só o returncode: uma mutação que
    #     apagasse 'hitl_requerido' do JSON passava, e o SKILL manda o consumidor
    #     ler exatamente esse campo. Prova por mutação do qa-critic adversarial.
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "risk_score.py"),
                           "--prob", "3", "--impact", "3"],
                          capture_output=True, text=True, cwd=ROOT, stdin=subprocess.DEVNULL)
    try:
        saida = json.loads(proc.stdout)
    except Exception as e:
        saida = None
        fails.append(f"stdout não é JSON válido: {e}")
    if saida is not None:
        for campo in ("itens", "gate_agregado", "hitl_requerido", "hitl_min_score"):
            if campo not in saida:
                fails.append(f"campo '{campo}' ausente do JSON — consumidor documentado quebra")
        if saida.get("hitl_min_score") != rs.HITL_MIN_SCORE:
            fails.append("hitl_min_score do JSON diverge da constante")
        if saida.get("hitl_requerido") is not True:
            fails.append("hitl_requerido deveria ser True para score 9")
        if saida.get("itens") and "hitl" not in saida["itens"][0]:
            fails.append("campo 'hitl' ausente do item — agregação não é auditável")

    print(f"risk_score: tabela-verdade 9 combos (+hitl) + scores {{1,2,3,4,6,9}} + fail-closed + "
          f"agregação + HITL>=6 + exit-codes + determinismo — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (gating por risco determinístico e fail-closed)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
