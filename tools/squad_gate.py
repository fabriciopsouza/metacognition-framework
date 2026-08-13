#!/usr/bin/env python3
"""squad_gate.py — GATE deterministico do squad (ADR-092). Dada a mudanca STAGED, exige a evidencia
ATESTADA dos papeis obrigatorios (matriz em behaviors/manifest.json). Fail-closed.

Corrige o "teatro" (qa-critic C2): evidencia de qa-critic so conta com ATESTACAO DE ISOLAMENTO —
`atestacao.agentId` nao-vazio (subagente isolado) E `atestacao.modelo` != autor do bloco (ADR-074).
String solta / auto-atestacao nao passa.

Trava real (qa-critic C1): este check alimenta o commit-status no SHA (post_canary_status.py / ADR-088),
que e server-side e o agente nao falsifica. O git-hook local e so conveniencia (provar por probe, nao assumir).

CLI:
  python tools/squad_gate.py            # avalia o que esta staged (git diff --cached) -> exit!=0 se faltar
  python tools/squad_gate.py --paths a.py docs/adr/x.md   # avalia paths dados (teste/CI)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "behaviors", "manifest.json")
QA_DIR = os.path.join(ROOT, "_meta", "qa")
APPROVING = {"aprovar", "aprovar_com_ressalvas"}

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def load_manifest(path: str = MANIFEST) -> dict:
    return json.load(open(path, encoding="utf-8"))


def classify(paths, manifest) -> set:
    """Path(s) staged -> conjunto de papeis OBRIGATORIOS (deterministico por match de path)."""
    req: set = set()
    for p in paths:
        p = p.replace("\\", "/").strip()
        for item in manifest.get("matriz", []):
            m = item.get("match", {})
            hit = (("suffix" in m and p.endswith(m["suffix"]))
                   or ("prefix" in m and p.startswith(m["prefix"]))
                   or ("exact" in m and p == m["exact"]))
            if hit:
                req.update(item.get("exige", []))
    return req


def load_evidence(qa_dir: str = QA_DIR) -> list:
    out = []
    if os.path.isdir(qa_dir):
        for f in os.listdir(qa_dir):
            if f.endswith(".json"):
                try:
                    out.append(json.load(open(os.path.join(qa_dir, f), encoding="utf-8")))
                except Exception:
                    pass
    return out


def _qa_critic_attested(artifacts) -> bool:
    """Existe veredito qa-critic APROVATIVO com ATESTACAO de isolamento valida? (anti-teatro)"""
    for v in artifacts:
        if v.get("recomendacao") not in APPROVING:
            continue
        at = v.get("atestacao") or {}
        agent = str(at.get("agentId", "")).strip()
        modelo = str(at.get("modelo", "")).strip()
        autor = str(at.get("autor", "")).strip()
        if agent and modelo and (not autor or modelo != autor):
            return True
    return False


def _release_junction_closed() -> bool:
    """Existe junção de FECHAMENTO (PC ou J6) no ledger para o release do topo do CHANGELOG?

    ADR-103: enquanto o gate era advisory, `juncao_release` ficava sempre False ("delegado").
    Ao ATIVAR o gate isso vira bloqueio permanente de todo release — defeito que só a ativação
    revela. Aqui o papel passa a ser VERIFICÁVEL: lê o ledger de junções (ADR-077) e exige o
    fechamento declarado para a versão que o CHANGELOG está publicando.
    """
    ch = os.path.join(ROOT, "CHANGELOG.md")
    if not os.path.isfile(ch):
        return False
    m = re.search(r"^##\s*\[(\d+\.\d+\.\d+)\]", open(ch, encoding="utf-8").read(), re.M)
    if not m:
        return False
    versao = m.group(1)
    led_dir = os.path.join(QA_DIR, "junctions")
    if not os.path.isdir(led_dir):
        return False
    for fn in os.listdir(led_dir):
        if not fn.endswith(".jsonl"):
            continue
        for line in open(os.path.join(led_dir, fn), encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue  # fail-closed em linha corrompida: não conta como fechamento
            if rec.get("junction") in ("PC", "J6") and versao in str(rec.get("bloco", "")):
                return True
    return False


def evaluate(paths, manifest, artifacts):
    """Retorna (faltam, detalhe). faltam=[] => gate PASSA."""
    required = classify(paths, manifest)
    faltam, detalhe = [], {}
    for role in sorted(required):
        if role == "qa_critic":
            ok = _qa_critic_attested(artifacts)
        elif role == "architect":
            ok = any(str(p).replace("\\", "/").startswith("docs/adr/") for p in paths)
        elif role == "juncao_release":
            ok = _release_junction_closed()
        else:
            # research_ou_ratificacao: delegado (research_evidence.py).
            # Marca como EXIGIDO-nao-verificavel-localmente -> falta (fail-closed) ate o check proprio rodar.
            ok = False
        detalhe[role] = ok
        if not ok:
            faltam.append(role)
    return faltam, detalhe


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", nargs="*", help="paths a avaliar (default: git diff --cached)")
    a = ap.parse_args(argv)
    paths = a.paths
    if paths is None:
        r = subprocess.run(["git", "diff", "--cached", "--name-only"],
                           capture_output=True, text=True, cwd=ROOT)
        paths = [x for x in r.stdout.splitlines() if x.strip()]
    manifest = load_manifest()
    faltam, detalhe = evaluate(paths, manifest, load_evidence())
    req = classify(paths, manifest)
    print(f"[squad-gate] {len(paths)} path(s) staged -> papeis exigidos: {sorted(req) or 'nenhum'}")
    for role, ok in detalhe.items():
        print(f"   {'OK ' if ok else 'FALTA'} {role}")
    if faltam:
        print(f"[squad-gate] BLOQUEADO (fail-closed): faltam evidencias atestadas: {faltam}")
        print("   -> rode o papel (ex.: qa-critic isolado) e registre via tools/qa_evidence.py com atestacao.")
        return 1
    print("[squad-gate] OK — evidencia atestada presente para os papeis exigidos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
