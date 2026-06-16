#!/usr/bin/env python3
"""Canario dos coaches cross-IA (ADR-083) — prova FERRAMENTAL (nao prosa): (a) o builder e
DETERMINISTICO (2 builds identicos), (b) sem DRIFT entre coaches.json e os .md committed (fail-closed),
(c) cada coach tem as secoes obrigatorias, (d) o gate anti-JARVIS passa, (e) manifesto integro.
Sem isto, "os coaches existem e batem com a fonte" seria prosa. Fail-closed (exit 1 se diverge).

Uso: python tools/test_web_bundles.py   (exit 0 PASS; 1 se falha)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_web_bundles as bwb  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REQUIRED_SECTIONS = ["## Nucleo do metodo", "## Papel", "## Elicitar", "## Metodo", "## Saida", "## Handoff"]


def main():
    fails = []

    # (e) manifesto integro
    try:
        data = json.load(open(bwb.SRC, encoding="utf-8"))
        coaches = data["coaches"]
    except Exception as e:  # noqa: BLE001
        print(f"RESULTADO: FAIL (coaches.json ilegivel: {e})")
        return 1
    ids = [c["id"] for c in coaches]
    if len(coaches) < 1:
        fails.append("coaches.json VAZIO (manifesto sem coach) — false-PASS de manifesto truncado (fail-closed)")
    if len(ids) != len(set(ids)):
        fails.append("ids de coach duplicados no coaches.json")
    for c in coaches:
        for k in ("id", "title", "artifact", "objective", "elicit", "method", "output_sections"):
            if not c.get(k):
                fails.append(f"coach {c.get('id','?')} sem campo '{k}'")

    # (a) determinismo: dois renders identicos
    rules, forbidden = bwb.web_export.load_map()
    version = bwb.web_export.main_version()
    for c in coaches:
        try:
            a = bwb.render(c, version, rules)
            b = bwb.render(c, version, rules)
        except Exception as e:  # noqa: BLE001 — diagnostico limpo em vez de traceback (campo ausente)
            fails.append(f"render falhou para {c.get('id','?')}: {e}")
            continue
        if a != b:
            fails.append(f"render nao-deterministico: {c['id']}")

    # (b) sem drift vs committed + (d) anti-JARVIS, via build(check=True)
    _v, built_ids, violations, drift = bwb.build(check=True)
    for v in violations:
        fails.append(f"anti-JARVIS: {v}")
    for d in drift:
        fails.append(f"drift: web-bundles/{d}.md != coaches.json (regenere e commite)")
    # ghost-file (drift INVERSO): .md em web-bundles/ que NAO esta no manifesto = orfao nao-detectado
    # pelo check==rebuild (que so itera coaches presentes). Pega coach removido do JSON com .md remanescente.
    disk = {f[:-3] for f in os.listdir(os.path.join(ROOT, "web-bundles"))
            if f.endswith(".md") and f != "README.md"}
    orphans = disk - set(ids)
    if orphans:
        fails.append(f"orfaos em web-bundles/ sem coach no manifesto: {sorted(orphans)} "
                     f"(remova o .md ou re-adicione ao coaches.json)")
    if set(built_ids) != disk:
        fails.append(f"ids gerados {sorted(built_ids)} != .md em disco {sorted(disk)}")

    # README web-bundles (escrito a mao) tambem passa pelo gate anti-JARVIS — escopo antes nao coberto
    rp = os.path.join(ROOT, "web-bundles", "README.md")
    if os.path.isfile(rp):
        rtxt = open(rp, encoding="utf-8").read()
        for rx in forbidden:
            m = rx.search(rtxt)
            if m:
                fails.append(f"README.md anti-JARVIS: '{m.group(0)[:50]}'")

    # (c) secoes obrigatorias em cada .md committed
    for cid in ids:
        p = os.path.join(ROOT, "web-bundles", cid + ".md")
        if not os.path.isfile(p):
            fails.append(f"web-bundles/{cid}.md ausente (rode build_web_bundles.py)")
            continue
        txt = open(p, encoding="utf-8").read()
        for sec in REQUIRED_SECTIONS:
            if sec not in txt:
                fails.append(f"{cid}.md sem secao obrigatoria '{sec}'")

    print(f"web-bundles: {len(ids)} coaches; determinismo + sem-drift + secoes + anti-JARVIS — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (coaches ferramentais: gerados do dado, sem drift, deterministicos)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
