#!/usr/bin/env python3
"""mission_gate.py — SessionStart hook: gate de product_type/escopo (ADR-022, porta 1:1 de mission-gate.ps1).

3 modos: BRIEFING (sem mission.md) | ADVANCE (sem product_type) | STANDARD (product_type ok).
Fail-soft: nunca bloqueia. Contrato SessionStart: additionalContext em stdout JSON.
AGNOSTICO (P12): taxonomia de product_type e mapa tipo->papel sao da aplicacao ativa.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def emit(ctx):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": ctx,
        }
    }))
    sys.exit(0)


try:
    raw = sys.stdin.read()
    cwd = ROOT
    if raw:
        try:
            h = json.loads(raw)
            if h.get("cwd"):
                cwd = str(h["cwd"])
        except Exception:
            pass

    # Modo de execucao (ADR-005)
    mode = "default"
    home = (os.environ.get("USERPROFILE") or os.environ.get("HOME") or os.path.expanduser("~"))
    mode_file = os.path.join(home, ".claude", "framework-mode.json")
    if os.path.isfile(mode_file):
        try:
            m = json.loads(open(mode_file, encoding="utf-8-sig").read())
            if m.get("mode"):
                mode = str(m["mode"])
        except Exception:
            pass

    conf_during = (
        "autonomia (product_type ja confirmado no briefing)."
        if mode == "autosuficiente"
        else "confirme product_type com o dono antes de avancar a juncao (J2+)."
    )

    candidates = [
        os.path.join(cwd, "mission.md"),
        os.path.join(cwd, "docs", "mission.md"),
        os.path.join(cwd, "docs", "specs", "mission.md"),
    ]
    mission = next((c for c in candidates if os.path.isfile(c)), None)

    if not mission:
        emit(
            "[mission-gate ADR-022] BRIEFING: sem mission.md. Antes de avancar para implementacao (J2+), "
            "o PMO deve declarar em mission.md: product_type + escopo (regulado? alto-risco? semantica? "
            f"gaps? handoff?). Modo={mode} -> {conf_during}"
        )

    content = open(mission, encoding="utf-8-sig", errors="replace").read()

    pt = None
    # Formato canonico inline: product_type: <valor>
    m = re.search(r"(?m)^\s*product_type:\s*(.+?)\s*$", content)
    if m:
        pt = m.group(1).strip()
    # Fallback tolerante: heading markdown seguido do valor
    if not pt or re.match(r"^<.*>$", pt or ""):
        m2 = re.search(r"(?ims)^\s*#{1,6}\s*product_type\s*\n+\s*([^\s<#].*?)\s*$", content)
        if m2:
            pt = m2.group(1).strip()

    if not pt or re.match(r"^<.*>$", pt):
        emit(
            "[mission-gate ADR-022] ADVANCE: mission.md presente mas sem product_type valido. "
            f"Declare 'product_type: <tipo>' antes de J2+. Modo={mode} -> {conf_during}"
        )

    # Mapa tipo->papel da aplicacao (agnostico: product-types.txt em exemplos/*/)
    roles = ""
    exemplos = os.path.join(cwd, "exemplos")
    if os.path.isdir(exemplos):
        for dp, _dn, fns in os.walk(exemplos):
            if "product-types.txt" in fns:
                try:
                    for line in open(os.path.join(dp, "product-types.txt"), encoding="utf-8-sig"):
                        if re.match(r"^\s*" + re.escape(pt) + r"\s*[:=]", line, re.IGNORECASE):
                            roles = " Papeis ativados (app): " + re.sub(r"^[^:=]*[:=]\s*", "", line).strip() + "."
                            break
                except Exception:
                    pass
                break

    emit(f"[mission-gate ADR-022] STANDARD: product_type='{pt}' declarado. Modo={mode} -> {conf_during}{roles}")

except Exception as e:
    print(f"[mission-gate] warning (nao-bloqueante): {e}", file=sys.stderr)
    sys.exit(0)
