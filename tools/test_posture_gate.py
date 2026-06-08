#!/usr/bin/env python3
"""Canario posture-gate (ADR-074 emenda 3, FAIL-CLOSED no master): um BLOCO SUBSTANTIVO nao pode
fechar sem EVIDENCIA DE POSTURA (pipeline deep-research/squad rodou) — discovery + RRC + (quando ha
fonte canonica/ADR) metodo-senior. Mecaniza a falha admitida em 2026-06-07: "pulei a postura
deep-research/squad; operei fast-mode". Antes era prosa; agora release sem postura = CI vermelho.

Bloco substantivo = release ATUAL (versao no topo do CHANGELOG). A evidencia vive no artefato qa-critic
APROVATIVO do release (`_meta/qa/*.json` com release==versao) no campo `postura`, PREENCHIDO PELO
qa-critic ADVERSARIAL (subagente isolado) — nao auto-atestado pelo gerador (anti-JARVIS).

Exige: postura.discovery nao-vazio + postura.rrc == PASSA + postura.metodo_senior presente.

Shadow-aware (espelha test_dev_dogfood/test_qa_evidence): docs/_private ausente + repo_identity !=
master -> PASS. FORWARD-ONLY: so o release atual.

Uso: python tools/test_posture_gate.py   (exit 0 PASS; 1 se falha)
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

# reusa o validador de postura do qa_evidence (fonte unica)
sys.path.insert(0, os.path.join(ROOT, "tools"))
try:
    from qa_evidence import validate_postura
except Exception:
    def validate_postura(postura, for_release=False):  # fallback minimo
        if not isinstance(postura, dict):
            return ["postura ausente"]
        out = []
        if not str(postura.get("discovery", "")).strip():
            out.append("postura.discovery vazio")
        rrc = str(postura.get("rrc", "")).strip()
        if for_release and not rrc.upper().startswith("PASSA"):
            out.append("rrc != PASSA")
        if not str(postura.get("metodo_senior", "")).strip():
            out.append("metodo_senior ausente")
        return out


def _is_genuine_shadow():
    """Gateia artefato COMMITADO (_meta/qa) — pula SO em SOMBRA-EXPORT positivo; default ENFORCE
    (na CI do master docs/_private esta ausente mas _meta/qa presente -> gate deve disparar).
    Mesma correcao de design do test_qa_evidence (auto-revisao 2026-06-08)."""
    try:
        import repo_identity
        if repo_identity.is_export_shadow():
            return True, "repo_identity.is_export_shadow — shadow legitimo"
    except Exception:
        pass
    return False, "nao-shadow (enforce — so export-shadow genuino pula; anti-forja)"


def main():
    shadow, why = _is_genuine_shadow()
    if shadow:
        print(f"{why}. PASS (shadow — nao cobra postura).")
        print("RESULTADO: PASS (shadow — sem cobranca de posture-gate)")
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
        print(f"_meta/qa/ ausente — release v{latest} sem evidencia de postura")
        print("RESULTADO: FAIL (release sem artefato de postura)")
        return 1

    # artefato aprovativo do release
    rel_art = None
    for jf in glob.glob(os.path.join(QA_DIR, "*.json")):
        try:
            v = json.load(open(jf, encoding="utf-8"))
        except Exception:
            continue
        if str(v.get("release", "")) == latest and v.get("recomendacao") in APPROVING:
            rel_art = (os.path.basename(jf), v)
            break

    if not rel_art:
        print(f"release v{latest}: SEM artefato qa-critic aprovativo (pre-requisito da postura)")
        print("RESULTADO: FAIL (sem veredito qa-critic aprovativo do release)")
        return 1

    name, v = rel_art
    probs = validate_postura(v.get("postura"), for_release=True)
    if not probs:
        p = v["postura"]
        print(f"release v{latest} ({name}): postura OK — discovery='{p.get('discovery')[:40]}...' "
              f"rrc={p.get('rrc')} metodo_senior={str(p.get('metodo_senior'))[:30]}")
    else:
        print(f"release v{latest} ({name}): postura INCOMPLETA -> {probs}")
    print("-" * 50)
    print("RESULTADO:", f"PASS (release v{latest} tem evidencia de postura deep-research/squad)" if not probs
          else f"FAIL (release v{latest} sem postura — pipeline nao evidenciado; CI vermelho)")
    return 0 if not probs else 1


if __name__ == "__main__":
    sys.exit(main())
