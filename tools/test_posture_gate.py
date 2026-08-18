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
import tempfile

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


def achar_artefato(qa_dir, versao):
    """(nome, veredito) do artefato APROVATIVO daquele release, ou None.

    Extraida de main() para o auto-teste exercitar a MESMA selecao. E' aqui que mora o
    defeito historico mais caro do ledger: aceitar como evidencia um veredito que NAO
    aprova, ou o veredito de OUTRO release.
    """
    for jf in sorted(glob.glob(os.path.join(qa_dir, "*.json"))):
        try:
            v = json.load(open(jf, encoding="utf-8"))
        except Exception:
            continue
        if str(v.get("release", "")) == versao and v.get("recomendacao") in APPROVING:
            return (os.path.basename(jf), v)
    return None


def autoteste():
    """Fixtures que este canario e OBRIGADO a acertar (ADR-106).

    Classe `mechanism == test`: com o repo real em ordem, afrouxar a selecao (ex.: aceitar
    `reprovar` como aprovativo) deixava o canario VERDE. O gate que existe para impedir
    "release fechado sem postura" passaria a liberar release REPROVADO, em silencio.
    """
    falhas = []
    postura_boa = {"discovery": "elicitacao feita", "rrc": "PASSA - coerente",
                   "metodo_senior": "9 passos"}
    with tempfile.TemporaryDirectory(prefix="posture-fx-") as td:
        def art(nome, release, rec, postura=None):
            with open(os.path.join(td, nome), "w", encoding="utf-8") as fh:
                json.dump({"release": release, "recomendacao": rec,
                           "postura": postura if postura is not None else postura_boa}, fh)

        art("aprovado.json", "9.9.9", "aprovar_com_ressalvas")
        art("reprovado.json", "9.9.8", "reprovar")
        art("outro-release.json", "1.2.3", "aprovar")

        if achar_artefato(td, "9.9.9") is None:
            falhas.append("artefato APROVATIVO do release nao foi encontrado — detector cego")
        if achar_artefato(td, "9.9.8") is not None:
            falhas.append("veredito REPROVADO foi aceito como evidencia aprovativa — e' o "
                          "defeito historico do ledger (release reprovado liberando fechamento)")
        if achar_artefato(td, "7.7.7") is not None:
            falhas.append("artefato de OUTRO release foi aceito — evidencia tem de ser do release")

    # a regra de postura em si (fonte unica: qa_evidence.validate_postura)
    if validate_postura(postura_boa, for_release=True):
        falhas.append("postura COMPLETA foi acusada (falso-positivo)")
    if not validate_postura({**postura_boa, "rrc": "NAO PASSA"}, for_release=True):
        falhas.append("rrc != PASSA nao foi pego num release")
    if not validate_postura({**postura_boa, "discovery": ""}, for_release=True):
        falhas.append("discovery vazio nao foi pego")
    if not validate_postura(None, for_release=True):
        falhas.append("postura AUSENTE nao foi pega — fail-closed furado")
    return falhas


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
    rel_art = achar_artefato(QA_DIR, latest)
    falhas_canario = autoteste()
    if falhas_canario:
        print(f"auto-teste do detector (7 fixtures) - FAIL")
        for f in falhas_canario:
            print("  -", f)
        print("RESULTADO: FAIL (o proprio detector do posture-gate esta furado)")
        return 1
    print("auto-teste do detector (7 fixtures) - OK")

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
