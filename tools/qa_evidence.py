#!/usr/bin/env python3
"""qa_evidence.py — persiste o VEREDITO do qa-critic (subagente isolado, read-only) como ARTEFATO
auditavel em `_meta/qa/<bloco>.{json,md}`. Mecaniza "o qa-critic rodou no bloco" (ADR-074 emenda 2).

Cerne prosa->mecanismo: o subagente qa-critic NAO tem Write (so valida); o orquestrador canaliza o
JSON do veredito por aqui. O artefato e a EVIDENCIA que `test_qa_evidence.py` (fail-closed no master)
exige por release — fechando o gap "qa-critic e disciplina minha, nao processo" (sessao 2026-06-07).

Schema do veredito (compativel com o Output JSON do qa-critic SKILL):
  bloco                   str   id do bloco revisado (vira slug do arquivo)
  passou                  bool  veredito binario do protocolo de turno unico
  recomendacao            str   reverter|corrigir|aprovar_com_ressalvas|aprovar  (eixo de acao)
  problemas               list  [{severidade, local, descricao, ...}]
  verificacoes_executadas list  comandos/canarios rodados -> resultado (anti-fabricacao)
  release        (opcional) str versao que este veredito FECHA (ex.: "1.51.0"). So o veredito
                                 final do bloco (process-critic aprovativo) carrega isto -> e o que
                                 o gate de release exige. SE presente, `postura` torna-se OBRIGATORIO.
  postura        (cond.)    dict EVIDENCIA DE POSTURA (ADR-074 emenda 3 / posture-gate). Preenchida
                                 pelo qa-critic ADVERSARIAL (subagente isolado, nao auto-atestada pelo
                                 gerador). Campos: discovery (str nao-vazia: path do artefato OU
                                 "inline: <justificativa>"), rrc ("PASSA"|"FALHA"|"N/A: <razao>"),
                                 metodo_senior ("aplicado: <path>"|"N/A: <razao>"). Para fechar release,
                                 rrc DEVE ser PASSA.
  steelman       (opcional) str
  data           (auto)     str ISO UTC (preenchido se ausente)

CLI:
  python tools/qa_evidence.py --from-json <f|->   le veredito (arquivo ou '-'=stdin) e grava artefato
  python tools/qa_evidence.py --list              lista artefatos existentes
"""
import argparse
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA_DIR = os.path.join(ROOT, "_meta", "qa")
REQUIRED = ["bloco", "passou", "recomendacao", "problemas", "verificacoes_executadas"]
APPROVING = {"aprovar", "aprovar_com_ressalvas"}

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _slug(s):
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", str(s).strip().lower())
    s = re.sub(r"-+", "-", s).strip("-.")
    return s or "bloco"


def _now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def render_md(v):
    L = [f"# QA-evidence — {v['bloco']}", ""]
    L.append(f"- **Data:** {v.get('data', '?')}")
    L.append(f"- **Veredito (passou):** {v['passou']}")
    L.append(f"- **Recomendacao:** {v['recomendacao']}")
    if v.get("release"):
        L.append(f"- **Fecha release:** v{v['release']}")
    if v.get("postura"):
        p = v["postura"]
        L += ["", "## Postura (posture-gate — atestada pelo qa-critic adversarial)"]
        L.append(f"- **Discovery:** {p.get('discovery', '—')}")
        L.append(f"- **RRC:** {p.get('rrc', '—')}")
        L.append(f"- **Metodo-senior:** {p.get('metodo_senior', '—')}")
    if v.get("steelman"):
        L += ["", "## Steelman", v["steelman"]]
    L += ["", "## Problemas", ""]
    probs = v.get("problemas") or []
    if not probs:
        L.append("_nenhum_")
    else:
        L += ["| Sev | Local | Descricao |", "|---|---|---|"]
        for p in probs:
            sev = p.get("severidade", "?")
            loc = str(p.get("local", "")).replace("|", "\\|")
            desc = str(p.get("descricao", "")).replace("|", "\\|").replace("\n", " ")
            L.append(f"| {sev} | {loc} | {desc} |")
    L += ["", "## Verificacoes executadas (anti-fabricacao)", ""]
    for x in (v.get("verificacoes_executadas") or []):
        L.append(f"- {x}")
    L.append("")
    return "\n".join(L)


def validate_postura(postura, for_release=False):
    """Valida o bloco de evidencia de postura. Retorna lista de problemas (vazia = OK)."""
    probs = []
    if not isinstance(postura, dict):
        return ["postura ausente ou nao-dict"]
    disc = str(postura.get("discovery", "")).strip()
    if not disc:
        probs.append("postura.discovery vazio (path do artefato OU 'inline: <justificativa>')")
    rrc = str(postura.get("rrc", "")).strip()
    if not rrc:
        probs.append("postura.rrc ausente (PASSA|FALHA|N/A: <razao>)")
    elif for_release and not rrc.upper().startswith("PASSA"):
        probs.append(f"postura.rrc='{rrc}' — release exige RRC PASSA")
    ms = str(postura.get("metodo_senior", "")).strip()
    if not ms:
        probs.append("postura.metodo_senior ausente ('aplicado: <path>' | 'N/A: <razao>')")
    # Gatilho DETERMINISTICO (ADR-009/010 mecanizado): fonte canonica/ADR nova -> metodo-senior
    # EXIGIDO, nao opcional. `fonte_canonica` e atestado pelo qa-critic adversarial (anti-JARVIS).
    if postura.get("fonte_canonica") and not ms.lower().startswith("aplicado"):
        probs.append("postura.fonte_canonica=true (norma/spec/ADR) -> metodo_senior DEVE ser "
                     "'aplicado: <path>' (gatilho deterministico, nao N/A)")
    return probs


def write_artifact(verdict, when=None):
    missing = [k for k in REQUIRED if k not in verdict]
    if missing:
        raise ValueError(f"veredito invalido — campos ausentes: {missing}")
    # ADR-074 emenda 3 (posture-gate): veredito que FECHA release exige bloco de postura valido.
    if verdict.get("release"):
        pp = validate_postura(verdict.get("postura"), for_release=True)
        if pp:
            raise ValueError(f"veredito de release sem postura valida: {pp}")
    verdict.setdefault("data", when or _now_iso())
    os.makedirs(QA_DIR, exist_ok=True)
    slug = _slug(verdict["bloco"])
    jpath = os.path.join(QA_DIR, slug + ".json")
    mpath = os.path.join(QA_DIR, slug + ".md")
    json.dump(verdict, open(jpath, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(mpath, "w", encoding="utf-8").write(render_md(verdict))
    return jpath, mpath


def main(argv=None):
    ap = argparse.ArgumentParser(description="Persiste veredito qa-critic em _meta/qa/ (ADR-074).")
    ap.add_argument("--from-json", help="arquivo JSON do veredito, ou '-' para stdin")
    ap.add_argument("--list", action="store_true", help="lista artefatos existentes")
    args = ap.parse_args(argv)

    if args.list:
        if not os.path.isdir(QA_DIR):
            print("_meta/qa/ ausente — nenhum artefato.")
            return 0
        for f in sorted(os.listdir(QA_DIR)):
            if f.endswith(".json"):
                v = json.load(open(os.path.join(QA_DIR, f), encoding="utf-8"))
                rel = f" release=v{v['release']}" if v.get("release") else ""
                print(f"{f}: passou={v.get('passou')} rec={v.get('recomendacao')}{rel} "
                      f"problemas={len(v.get('problemas') or [])}")
        return 0

    if not args.from_json:
        ap.error("informe --from-json <f|-> ou --list")
    raw = sys.stdin.read() if args.from_json == "-" else open(args.from_json, encoding="utf-8").read()
    verdict = json.loads(raw)
    jpath, mpath = write_artifact(verdict)
    print(f"[qa-evidence] gravado: {os.path.relpath(jpath, ROOT)} + {os.path.relpath(mpath, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
