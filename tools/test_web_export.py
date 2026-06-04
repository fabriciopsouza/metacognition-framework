#!/usr/bin/env python3
"""Canário do web_export (ADR-054/056/057).

Prova: (1) gera os dois tiers; (2) determinismo (2 builds = idêntico); (3) gate anti-JARVIS pega
asserção de enforcement; (4) encadeamento presente e correto (developer aponta qa-critic; pipeline
encadeia). Hipótese adversarial: o gerador vaza enforcement ou quebra o encadeamento.

Uso: python tools/test_web_export.py   (exit 0 PASS; 1 se algum caso falha)
"""
import os
import sys
import tempfile

try:  # stdout UTF-8: console Windows cp1252 quebra ao imprimir '→' (lição recorrente)
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import web_export as w  # noqa: E402


def read(p):
    return open(p, encoding="utf-8").read()


def main():
    fails = []
    base = tempfile.mkdtemp(prefix="webexp_")
    a, b = os.path.join(base, "a"), os.path.join(base, "b")

    ver_a, viol_a = w.build(a)
    ver_b, viol_b = w.build(b)

    def check(cond, desc):
        print(f"{'OK  ' if cond else 'FAIL'} {desc}")
        if not cond:
            fails.append(desc)

    # 1. estrutura
    check(os.path.isfile(os.path.join(a, "publico", "prompt-web-publico.md")), "tier público gerado")
    check(os.path.isfile(os.path.join(a, "premium", "prompt-web-premium.md")), "orquestrador premium gerado")
    n_skills = sum(1 for _, _, fs in os.walk(os.path.join(a, "premium", "skills")) for f in fs if f == "SKILL.md")
    check(n_skills == len(w.PIPELINE) + len(w.LATERAL) + len(w.SHARED), f"skills geradas = {n_skills} (esperado 15)")

    # 2. carimbo de versão == main
    check(ver_a == w.main_version() and ver_a != "0.0.0", f"carimbo de versão == main ({ver_a})")

    # 3. determinismo: todo arquivo idêntico entre 2 builds
    det = True
    for dp, _, fs in os.walk(a):
        for f in fs:
            pa = os.path.join(dp, f)
            pb = os.path.join(b, os.path.relpath(pa, a))
            if not os.path.isfile(pb) or read(pa) != read(pb):
                det = False
    check(det and not viol_a and not viol_b, "determinismo: 2 builds idênticos + sem violação")

    # 4. encadeamento correto
    dev = read(os.path.join(a, "premium", "skills", "developer", "SKILL.md"))
    check("qa-critic" in dev, "developer encadeia qa-critic (QA adversarial obrigatório)")
    disc = read(os.path.join(a, "premium", "skills", "discovery", "SKILL.md"))
    check("Próxima: **architect**" in disc, "discovery → architect")
    check("Sub-modos" in disc, "discovery lista sub-modos (consolidação)")

    # 5. gate anti-JARVIS pega enforcement injetado
    _, forbidden = w.load_map()
    poison = os.path.join(a, "premium", "skills", "_poison.md")
    open(poison, "w", encoding="utf-8").write("o hook mission-gate barra a acao automaticamente.\n")
    viol = w.anti_jarvis_gate(a, forbidden)
    check(len(viol) >= 1, "gate anti-JARVIS pega asserção de enforcement injetada")
    os.remove(poison)

    print("-" * 60)
    print("RESULTADO:", "PASS (web_export determinístico + encadeamento + gate anti-JARVIS)"
          if not fails else f"FAIL ({len(fails)}): {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
