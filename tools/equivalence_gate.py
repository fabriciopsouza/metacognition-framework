#!/usr/bin/env python3
"""equivalence-gate v2 (ADR-071) — TRAVA FÍSICA de equivalência FUNCIONAL entre repos-mãe.

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
import sys

VALID_STATUS = {"PROVIDES", "ABSENT", "JUSTIFIED_ABSENT"}


def validate(manifest, known_ais=None):
    flags = []
    records = manifest.get("capabilities", [])
    declared = set(known_ais or manifest.get("known_ais") or [])
    if not declared:
        flags.append(
            "known_ais NAO declarado (--ais ou manifest.known_ais) -> impossivel detectar IA omissa; "
            "equivalencia so pode ser parcial. Declare o conjunto de maes.")
    ais = set(declared)
    for r in records:
        if r.get("ai"):
            ais.add(r["ai"])
    if len(ais) < 2:
        return flags  # <2 maes: nada a reconciliar

    by_cap = {}
    for r in records:
        cid = r.get("capability_id")
        if cid is None:
            flags.append("registro sem capability_id")
            continue
        st = r.get("status")
        if st not in VALID_STATUS:
            flags.append(f"[{cid}] '{r.get('ai')}' status invalido '{st}' (use {sorted(VALID_STATUS)})")
        by_cap.setdefault(cid, {})[r.get("ai")] = r

    for cap, decided in by_cap.items():
        providers = [ai for ai, r in decided.items() if r.get("status") == "PROVIDES"]
        if not providers:
            continue  # ninguem prove -> todas iguais (sem capacidade) -> sem divergencia
        for ai in sorted(ais):
            r = decided.get(ai)
            if r is None:
                flags.append(
                    f"[{cap}] '{ai}' OMISSA (sem registro) mas {providers} prove(em) -> exige PROVIDES "
                    f"ou JUSTIFIED_ABSENT (ADR + hitl_proof + motivacao)")
                continue
            st = r.get("status")
            if st == "PROVIDES":
                continue  # equivalente por qualquer mecanismo (mechanism documenta como)
            if st != "JUSTIFIED_ABSENT":
                flags.append(
                    f"[{cap}] '{ai}' status '{st}' diverge de {providers} sem justificativa -> "
                    f"use JUSTIFIED_ABSENT com ADR + hitl_proof + motivacao")
                continue
            faltas = []
            if not r.get("adr_ref"):
                faltas.append("sem adr_ref (replicabilidade)")
            if not r.get("hitl_proof"):
                faltas.append("sem hitl_proof (commit/tag assinado pelo dono ou PR aprovado — verificado na CI)")
            if not r.get("motivation"):
                faltas.append("sem motivation (ganho subjetivo/finalidade/motivacao do usuario)")
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
