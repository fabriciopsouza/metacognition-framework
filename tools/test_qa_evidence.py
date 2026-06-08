#!/usr/bin/env python3
"""Canario qa-evidence (ADR-074 emenda 2, parte FAIL-CLOSED no master): o release ATUAL (versao do
topo do CHANGELOG) DEVE ter um artefato de veredito qa-critic APROVATIVO em `_meta/qa/*.json` com
`release == <versao>`. Mecaniza "o qa-critic rodou no bloco" — antes era disciplina/prosa minha
(maior debito de processo admitido em 2026-06-07).

Shadow-aware (espelha test_dev_dogfood, ADR-070): docs/_private ausente + repo_identity != master
-> PASS (so master desenvolve e fecha bloco com qa-critic). Master degradado (sem _private mas
git=master) NAO e isento.

FORWARD-ONLY (regua §0): so gateia o release atual — nao exige artefato qa p/ as versoes historicas
(que nunca tiveram artefato; fabricar seria desonesto, mesma doutrina do test_release_checkpoint).

APROVATIVO = recomendacao em {aprovar, aprovar_com_ressalvas}. Um veredito "corrigir"/"reverter"
NAO fecha release (forca o fix + re-review antes do release) — exatamente o fluxo correto.

Uso: python tools/test_qa_evidence.py   (exit 0 PASS; 1 se falha)
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA_DIR = os.path.join(ROOT, "_meta", "qa")
APPROVING = {"aprovar", "aprovar_com_ressalvas"}

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _is_genuine_shadow():
    """Este gate cobre artefato COMMITADO (_meta/qa, versionado) — DIFERENTE do test_dev_dogfood
    (que cobre docs/_private, cofre LOCAL gitignored). Logo NAO pode usar 'docs/_private ausente'
    como sinal de shadow: na CI do PROPRIO master docs/_private esta ausente (gitignored) mas
    _meta/qa esta presente -> o gate DEVE disparar. Pula SO em shadow POSITIVO (repo_identity=
    SOMBRA-EXPORT, carimbado por export-clean). Default = ENFORCE. (Falha de design pega na
    auto-revisao 2026-06-08: o sinal docs/_private faria o gate nunca disparar na CI do master.)"""
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import repo_identity
        if repo_identity.is_export_shadow():
            return True, "repo_identity.is_export_shadow (carimbo shadow + commit de export) — shadow legitimo"
    except Exception:
        pass
    return False, "nao-shadow (enforce — so export-shadow genuino pula; anti-forja)"


def main():
    shadow, why = _is_genuine_shadow()
    if shadow:
        print(f"{why}. PASS (shadow — nao cobra artefato qa-critic).")
        print("RESULTADO: PASS (shadow — sem cobranca de qa-evidence)")
        return 0

    try:
        chg = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8-sig").read()
    except Exception as e:
        print(f"RESULTADO: FAIL (CHANGELOG ilegivel: {e})")
        return 1
    vers = re.findall(r"(?m)^## \[(\d+\.\d+\.\d+)\]", chg)
    if not vers:
        print("RESULTADO: FAIL (nenhuma versao no CHANGELOG)")
        return 1
    latest = vers[0]

    if not os.path.isdir(QA_DIR):
        print(f"_meta/qa/ ausente — release v{latest} sem evidencia qa-critic")
        print("RESULTADO: FAIL (release sem artefato qa-critic — rode qa_evidence.py com o veredito)")
        return 1

    approving = []
    for jf in glob.glob(os.path.join(QA_DIR, "*.json")):
        try:
            v = json.load(open(jf, encoding="utf-8"))
        except Exception:
            continue
        if str(v.get("release", "")) == latest and v.get("recomendacao") in APPROVING:
            approving.append(os.path.basename(jf))

    ok = bool(approving)
    if ok:
        print(f"release atual v{latest}: veredito qa-critic aprovativo presente — {approving} — OK")
    else:
        print(f"release atual v{latest}: SEM artefato qa-critic aprovativo (release==v{latest} + "
              f"recomendacao em {sorted(APPROVING)}) em _meta/qa/")
    print("-" * 50)
    print("RESULTADO:", f"PASS (release v{latest} tem evidencia qa-critic)" if ok
          else f"FAIL (release v{latest} sem veredito qa-critic aprovativo — qa-critic e processo, nao opt-in)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
