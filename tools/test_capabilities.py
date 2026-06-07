#!/usr/bin/env python3
"""Canario do indice de capacidades (ADR-072). Garante que o registry NAO MENTE — e o que torna
o indice confiavel o bastante para o agente parar de reexplorar o repo. Fail-closed.

Prova:
  1. capabilities.json e JSON valido, com schema_version e lista nao-vazia.
  2. id unico, kebab-case, nao-vazio; title e ai_owner presentes; status no enum.
  3. todo ponteiro presente (mechanism/test/adr/doc) EXISTE em disco (indice nao aponta p/ morto).
  4. status PROVIDES => tem mechanism E test, ambos existem (provado = tem canario).
  5. status JUSTIFIED_ABSENT => tem adr (justificativa rastreavel).
  6. cross_ai:true => aparece no manifest de equivalencia derivado (capability_id presente).
  7. CAPABILITIES.md em disco == render atual (anti-drift; mesmo gate do build --check).
  8. COBERTURA (garantia alem de prosa, ADR-072): todo `tools/test_*.py` (canario = unidade de
     capacidade provada) esta referenciado por algum registro OU dispensado em `registry_waivers`
     (com motivo). Canario orfao => FAIL => forca registrar a capacidade nova. Sem isto, o registry
     apodrece silenciosamente quando features novas entram sem entrar no fluxo.

Uso: python tools/test_capabilities.py   (exit 0 PASS; 1 se falha)
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_capabilities as bc  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

STATUS_OK = {"PROVIDES", "PARTIAL", "ABSENT", "JUSTIFIED_ABSENT"}
# enforcement: como o processo e FORCADO (cerne do framework — nunca depender de prosa).
ENFORCE_OK = {"fail-closed", "ci-ready", "physical", "fail-soft", "advisory", "manual", "prose", "n/a"}
# abaixo de fail-closed/physical = ainda nao forca de fato -> debito de mecanizacao VISIVEL.
ENFORCE_WEAK = {"fail-soft", "advisory", "ci-ready", "manual", "prose"}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PTR_FIELDS = ("mechanism", "test", "adr", "doc")


def main():
    fails = []
    try:
        reg = bc.load_registry()
    except Exception as e:
        print(f"RESULTADO: FAIL (capabilities.json ilegivel: {e})")
        return 1

    if reg.get("schema_version") is None:
        fails.append("schema_version ausente no registry")
    caps = reg.get("capabilities")
    if not isinstance(caps, list) or not caps:
        print("RESULTADO: FAIL (capabilities deve ser lista nao-vazia)")
        return 1

    seen = set()
    for c in caps:
        cid = c.get("id", "")
        tag = cid or "<sem-id>"
        if not cid:
            fails.append("capacidade sem id")
        elif not KEBAB.match(cid):
            fails.append(f"[{tag}] id nao e kebab-case")
        if cid in seen:
            fails.append(f"[{tag}] id duplicado")
        seen.add(cid)
        if not c.get("title"):
            fails.append(f"[{tag}] sem title")
        if not c.get("ai_owner"):
            fails.append(f"[{tag}] sem ai_owner")
        st = c.get("status")
        if st not in STATUS_OK:
            fails.append(f"[{tag}] status invalido: {st!r}")

        # (3) ponteiros presentes existem em disco
        for f in PTR_FIELDS:
            p = c.get(f)
            if p and not os.path.isfile(os.path.join(ROOT, p)):
                fails.append(f"[{tag}] {f} aponta p/ arquivo inexistente: {p}")

        # (4) PROVIDES exige mechanism + test
        if st == "PROVIDES":
            if not c.get("mechanism"):
                fails.append(f"[{tag}] PROVIDES sem mechanism")
            if not c.get("test"):
                fails.append(f"[{tag}] PROVIDES sem test (provado exige canario)")

        # (5) JUSTIFIED_ABSENT exige adr
        if st == "JUSTIFIED_ABSENT" and not c.get("adr"):
            fails.append(f"[{tag}] JUSTIFIED_ABSENT sem adr (justificativa)")

        # (9) ENFORCEMENT (cerne prosa->mecanismo): valor valido se presente; OBRIGATORIO p/ cross_ai.
        enf = c.get("enforcement")
        if enf is not None and enf not in ENFORCE_OK:
            fails.append(f"[{tag}] enforcement invalido: {enf!r} (use {sorted(ENFORCE_OK)})")
        if c.get("cross_ai") and not enf:
            fails.append(f"[{tag}] cross_ai exige 'enforcement' declarado (prosa-only nao pode ser invisivel)")

    # (6) cross_ai aparece no manifest
    man_ids = {m["capability_id"] for m in bc.manifest(reg)["capabilities"]}
    for c in caps:
        if c.get("cross_ai") and c.get("id") not in man_ids:
            fails.append(f"[{c.get('id')}] cross_ai:true mas ausente do manifest de equivalencia")

    # (8) COBERTURA — garantia alem de prosa: todo canario tools/test_*.py esta referenciado
    # por algum registro (campo test) OU dispensado em registry_waivers (com motivo). Orfao => FAIL.
    referenced = {c.get("test") for c in caps if c.get("test")}
    waivers = reg.get("registry_waivers", [])
    waived = {w.get("file") for w in waivers if isinstance(w, dict)}
    for w in waivers:
        if not isinstance(w, dict) or not w.get("file") or not w.get("reason"):
            fails.append(f"registry_waivers invalido (exige file+reason): {w!r}")
    self_path = os.path.relpath(os.path.abspath(__file__), ROOT).replace(os.sep, "/")
    found = set(glob.glob(os.path.join(ROOT, "tools", "test_*.py")))
    found |= set(glob.glob(os.path.join(ROOT, "tools", "**", "test_*.py"), recursive=True))
    for tp in sorted(found):
        rel = os.path.relpath(tp, ROOT).replace(os.sep, "/")
        if rel == self_path:
            continue  # o proprio canario do indice
        if rel not in referenced and rel not in waived:
            fails.append(f"CANARIO ORFAO: {rel} nao referenciado por nenhum registro nem dispensado "
                         f"(registre a capacidade em capabilities.json ou adicione a registry_waivers com motivo)")

    # (7) CAPABILITIES.md em sync
    rendered = bc.render(reg)
    try:
        with open(bc.INDEX_MD, encoding="utf-8") as fh:
            disk = fh.read()
        if disk != rendered:
            fails.append("CAPABILITIES.md fora de sync com o registry (rode build_capabilities.py)")
    except FileNotFoundError:
        fails.append("CAPABILITIES.md ausente (rode build_capabilities.py)")

    # DEBITO DE MECANIZACAO (visibilidade — cerne do framework): lista o que ainda NAO forca de fato
    # (enforcement abaixo de fail-closed/physical). Nunca silencioso. Nao reprova (advisory pode ser
    # legitimo onde EDR veta hook), mas torna o gap prosa-vs-mecanismo AUDITAVEL.
    debt = sorted((c.get("id"), c.get("enforcement")) for c in caps
                  if c.get("enforcement") in ENFORCE_WEAK)
    if debt:
        print(f"[debito-mecanizacao] {len(debt)} capacidade(s) ainda nao fail-closed/physical "
              f"(prosa->mecanismo pendente):")
        for cid, enf in debt:
            print(f"  · {cid} — {enf}")

    print(f"{len(caps)} capacidades; ponteiros vivos; PROVIDES tem canario; cross_ai com enforcement; "
          f"indice em sync — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (registry honesto e indice em sync)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
