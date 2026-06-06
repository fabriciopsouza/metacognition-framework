#!/usr/bin/env python3
"""equivalence-gate v2 (ADR-071) — gate de equivalência FUNCIONAL entre repos-mãe.

ENFORCEMENT CONDICIONAL (honesto — qa-critic): este gate é a LÓGICA determinística; o
enforcement REAL exige dois itens ainda PENDENTES: (a) um passo de CI que rode este gate sobre
o manifest do hub E verifique a autenticidade de cada `hitl_proof` via `git verify-commit`;
(b) o hub provisionado. Enquanto isso, o gate valida FORMA (formato do proof, catálogo, duplicata)
mas NÃO prova a assinatura humana sozinho. Não é "trava física" plena até a CR existir.

OBJETIVO: os repos-mãe (claude, gemini, futuros — agnóstico de IA) devem ser SEMPRE
funcionalmente EQUIVALENTES. Equivalência é de CAPACIDADE (resultado), NÃO de implementação:
uma IA pode PROVER a mesma capacidade por mecanismo próprio. Quando ≥1 mãe provê uma capacidade,
toda outra mãe deve PROVÊ-LA (por qualquer meio) OU declarar ausência JUSTIFICADA com ADR + prova
de HITL + motivação. Ausência não-justificada (ou IA omissa) → FLAGA (exit≠2) e exige ADR+HITL.

POR QUE v2 (correções do qa-critic adversarial sobre a v1):
  - v1 comparava ADOÇÃO por improvement_id LITERAL → forçava import do mecanismo da outra IA
    (burocracia / solução que não encaixa). v2 compara CAPACIDADE: PROVIDES por qualquer mechanism.
  - v1 aceitava `hitl: true` (booleano AUTO-DECLARADO = teatro). v2 exige `hitl_proof`: referência a
    artefato que SÓ o humano produz — commit/tag ASSINADO pelo dono (verificável por `git verify-commit`
    na CI) ou PR aprovado pelo dono. O gate exige presença; a CI verifica autenticidade (limite honesto:
    o gate sozinho, lendo o manifest, não tem como criptografar — por isso a verificação real é da CI).
  - "ambas rejeitam em silêncio" dissolve no frame de capacidade: ninguém provê = todas iguais = sem
    divergência. Qualquer NÃO-provisão deliberada vira JUSTIFIED_ABSENT (exige prova completa).
  - IA omissa total: `known_ais` é OBRIGATÓRIO (--ais ou manifest.known_ais); sem ele, FLAGA
    (não dá p/ detectar quem não publicou nada).

Cada IA registra só no PRÓPRIO repo; o gate lê o manifest UNIFICADO do hub (agregado). Nenhuma escreve
na outra. Divergência sistemática → ADR + HITL (decisão do dono, consciente; ADR-011/041).

Manifest: capabilities[] = {capability_id, ai, status, mechanism, adr_ref, hitl_proof, motivation}
  status ∈ {PROVIDES, ABSENT, JUSTIFIED_ABSENT}
Uso:
    python tools/equivalence_gate.py <manifest.json> --ais claude,gemini [--json]
Exit 0 = equivalentes/justificados; 2 = divergência flagada; 1 = erro. Stdlib only.
"""
import json
import re
import sys

VALID_STATUS = {"PROVIDES", "ABSENT", "JUSTIFIED_ABSENT"}
# hitl_proof = referencia a artefato que SO o humano produz. Formato minimo checado AQUI
# (rejeita 'fake'/'true'/'ok'); a AUTENTICIDADE (git verify-commit) e do passo de CI (declarado).
PROOF_RE = re.compile(r"^(commit:[0-9a-f]{7,40}|tag:\S+|pr:[0-9]+|approved-pr:\S+)$")


def _valid_proof(s):
    return bool(s) and bool(PROOF_RE.match(str(s).strip()))


def validate(manifest, known_ais=None):
    flags = []
    records = manifest.get("capabilities", [])
    declared = set(known_ais or manifest.get("known_ais") or [])
    if not declared:
        flags.append(
            "known_ais NAO declarado (--ais ou manifest.known_ais) -> impossivel detectar IA omissa; "
            "equivalencia so pode ser parcial. Declare o conjunto de maes.")
    ais = set(declared)
    ais_with_records = set()
    catalog = manifest.get("capability_catalog")  # opcional: enum FECHADO de capability_id

    by_cap = {}
    for r in records:
        ai = r.get("ai")
        if ai:
            ais.add(ai)
            ais_with_records.add(ai)
        cid = r.get("capability_id")
        if cid is None:
            flags.append("registro sem capability_id")
            continue
        st = r.get("status")
        if st not in VALID_STATUS:
            flags.append(f"[{cid}] '{ai}' status invalido '{st}' (use {sorted(VALID_STATUS)})")
        # catalogo canonico fecha o furo do vocabulario divergente (qa-critic ALTO):
        # sem ele, 'anti-loop' e 'loop-prevention' contam como capacidades distintas.
        if catalog is not None and cid not in catalog:
            flags.append(
                f"[{cid}] capability_id FORA do catalogo canonico -> normalize p/ um id do catalogo "
                f"(vocabulario divergente mascara nao-cobertura)")
        # duplicata conflitante (qa-critic ALTO): (capability_id, ai) deve ter status unico.
        prev = by_cap.setdefault(cid, {}).get(ai)
        if prev is not None and prev.get("status") != st:
            flags.append(
                f"[{cid}] '{ai}' registros DUPLICADOS conflitantes ('{prev.get('status')}' vs '{st}') "
                f"-> ambiguo, rejeitado")
        by_cap[cid][ai] = r

    if len(ais) < 2:
        return flags  # <2 maes: nada a reconciliar

    # OMISSA TOTAL: inscrita mas sem NENHUM registro -> 1 flag so (evita flood por-capacidade).
    omissa_total = sorted(declared - ais_with_records)
    for ai in omissa_total:
        flags.append(
            f"'{ai}' inscrita em known_ais mas NAO publicou nenhuma capability (OMISSA total) -> "
            f"publicar suas capabilities ou sair do conjunto")

    for cap, decided in by_cap.items():
        providers = [ai for ai, r in decided.items() if r.get("status") == "PROVIDES"]
        if not providers:
            continue  # ninguem prove -> todas iguais (sem capacidade) -> sem divergencia
        for ai in sorted(ais):
            if ai in omissa_total:
                continue  # ja flagada 1x; nao floodar por-capacidade
            r = decided.get(ai)
            if r is None:
                flags.append(
                    f"[{cap}] '{ai}' OMISSA nesta capacidade mas {providers} prove(em) -> PROVIDES "
                    f"ou JUSTIFIED_ABSENT (ADR + hitl_proof + motivacao)")
                continue
            st = r.get("status")
            if st == "PROVIDES":
                continue  # equivalente por qualquer mecanismo (mechanism documenta como)
            if st != "JUSTIFIED_ABSENT":
                flags.append(
                    f"[{cap}] '{ai}' status '{st}' diverge de {providers} sem justificativa -> "
                    f"JUSTIFIED_ABSENT com ADR + hitl_proof + motivacao")
                continue
            faltas = []
            if not r.get("adr_ref"):
                faltas.append("sem adr_ref")
            if not _valid_proof(r.get("hitl_proof")):
                faltas.append("hitl_proof ausente/invalido (use commit:<sha>|tag:<t>|pr:<n>|"
                              "approved-pr:<ref>; autenticidade verificada na CI via git verify-commit)")
            if not r.get("motivation"):
                faltas.append("sem motivation")
            if faltas:
                flags.append(
                    f"[{cap}] '{ai}' JUSTIFIED_ABSENT INCOMPLETO: " + "; ".join(faltas)
                    + " -> ADR + HITL obrigatorio")
    return flags


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("uso: python tools/equivalence_gate.py <manifest.json> --ais a,b [--json]", file=sys.stderr)
        return 1
    known = None
    for i, a in enumerate(argv):
        if a.startswith("--ais="):
            known = a.split("=", 1)[1].split(",")
        elif a == "--ais" and i + 1 < len(argv):
            known = argv[i + 1].split(",")
    try:
        manifest = json.load(open(args[0], encoding="utf-8"))
    except Exception as e:
        print(f"erro lendo manifest: {e}", file=sys.stderr)
        return 1

    flags = validate(manifest, known)
    if "--json" in argv:
        print(json.dumps({"equivalent": not flags, "flags": flags}, ensure_ascii=False, indent=2))
    else:
        if not flags:
            print("[equivalence-gate] PASS — maes equivalentes (ou ausencias justificadas c/ ADR+HITL-proof).")
        else:
            print(f"[equivalence-gate] FAIL — {len(flags)} divergencia(s) exigindo ADR+HITL:")
            for f in flags:
                print(f"  - {f}")
    return 0 if not flags else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
