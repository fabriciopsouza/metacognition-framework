#!/usr/bin/env python3
"""boot_check.py — self-check de boot UNICO, em Python (imune ao veto de EDR), que executa as
verificacoes session-time que de outro modo sao hook-inerte (Kaspersky) ou skippaveis pelo agente,
e grava PROVA checavel em .claude/boot-proof.json.

PORQUE (emenda ADR-061 / plano anti-bypass 2026-06-10): os gates de boot EXISTEM mas sao
BYPASSAVEIS nesta maquina — hooks PS vetados pelo EDR + passos manuais do start-session pulados
(falha real 2026-06-08: boot-scan assumido vazio, sem executar). Este script FUNDE esses passos
espalhados num comando unico (regua §0(c): forma executavel UNICA de passos antes manuais-e-skippaveis
— destrava garantia inalcancavel por prosa; NAO e adicao pura) e deixa PROVA que um gate pode checar. Nao e hook: o agente RODA no start-session (o banner de liveness
aponta para ele). Fail-soft (exit 0): relata, nao trava o boot. A garantia forte (agnosticismo)
ja roda fail-closed no CI em paralelo — aqui ela e re-executada como reporte de sessao.

ANTI-BYPASS: CARIMBA os liveness keys dos gates que executou (.claude/.hooklive/<key>=<id>) -> o
banner de liveness do route-gate se cala, porque boot_check FEZ o trabalho que o hook faria. O id da
sessao vem do env CLAUDE_CODE_SESSION_ID (auto) ou de --session; sem id, roda os checks mas NAO
carimba (declarado na saida). Rodar boot_check = trabalho dos gates provadamente feito nesta sessao.

Uso:
  python tools/boot_check.py [--session <id>]   (sempre exit 0; escreve .claude/boot-proof.json)
  # bare: usa $env:CLAUDE_CODE_SESSION_ID automaticamente para carimbar o liveness
"""
import datetime
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _run(*args, stdin_text=""):
    """Roda um subprocesso com o MESMO interpretador/cwd; devolve (rc, stdout+stderr). Fail-soft."""
    try:
        p = subprocess.run(list(args), cwd=ROOT, input=stdin_text, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=120)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # noqa: BLE001 — boot-check nunca pode crashar o boot
        return 1, f"[boot_check] excecao ao rodar {args!r}: {e}"


def check_repo_sync():
    """Reusa o hook Python existente (sem refatora-lo): captura o additionalContext do JSON."""
    rc, out = _run(sys.executable, os.path.join("tools", "hooks", "check_repo_sync.py"))
    detail = "sync ok / em dia"
    status = "ok"
    executed = True  # so carimba o liveness key se o gate COMPROVADAMENTE rodou (envelope parseado)
    try:
        ctx = json.loads(out.strip().splitlines()[-1]).get(
            "hookSpecificOutput", {}).get("additionalContext", "")
        if ctx.strip():
            detail = ctx.strip().replace("\n", " ")[:300]
            status = "warn" if ("⚠️" in ctx or "NAO" in ctx) else "ok"
    except Exception:
        # saida inesperada (nao-JSON) -> NAO confirmamos que o gate rodou -> NAO carimba
        # (anti false-liveness; achado ALTO do qa-critic 2026-06-10).
        executed = False
        status = "warn"
        detail = "check_repo_sync: saida inesperada (nao-JSON) — gate NAO confirmado, nao carimbado"
    return {"name": "repo-sync", "status": status, "detail": detail,
            "stamps": ["check-repo-sync"] if executed else []}


def check_core_agnostic():
    rc, out = _run(sys.executable, os.path.join("tools", "check_core_agnostic.py"))
    last = (out.strip().splitlines() or ["<sem saida>"])[-1]
    ok = rc == 0
    # rc!=0 = violacao de agnosticismo OU crash: gate NAO passou -> NAO carimba (o nag persiste
    # ate o agente corrigir; boot_check imprime ❌). Stamp = "rodou e passou", nao so "rodou".
    return {"name": "core-agnostic", "status": "ok" if ok else "fail",
            "detail": last[:300], "stamps": ["check-core-agnostic"] if ok else []}


def check_cross_ai_boot_scan():
    rc, out = _run(sys.executable, os.path.join("tools", "cross_ai_hub.py"), "boot-scan")
    text = out.strip()
    # hub nao configurado e estado LEGITIMO (declarado), nao falha — mas nunca "assumir vazio".
    if "nao configurado" in text or "não configurado" in text:
        status, detail = "skip", "hub cross-IA nao configurado (declarado; ADR-069 — clonar metacognition-hub p/ ativar)"
    elif rc == 0:
        status, detail = "ok", (text.replace("\n", " ")[:300] or "boot-scan executado")
    else:
        status, detail = "warn", text.replace("\n", " ")[:300]
    return {"name": "cross-ai-boot-scan", "status": status, "detail": detail, "stamps": []}


def check_version_sanity():
    """Ancora a versao canonica (anti 'versao fantasma' — erro real do boot Gemini que declarou v3.1
    inexistente). Le o topo do CHANGELOG (release) e a versao do roteador no AGENT-FRAMEWORK.md."""
    rel = router = "?"
    try:
        chg = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8-sig").read()
        m = re.search(r"(?m)^##\s*\[(\d+\.\d+\.\d+)\]", chg)
        rel = m.group(1) if m else "?"
    except Exception:
        pass
    try:
        af = open(os.path.join(ROOT, "AGENT-FRAMEWORK.md"), encoding="utf-8-sig").read()
        m = re.search(r"v(\d+\.\d+)", af)
        router = m.group(1) if m else "?"
    except Exception:
        pass
    return {"name": "version-sanity", "status": "ok",
            "detail": f"versao canonica: release v{rel} · roteador v{router} "
                      f"(DECLARE estas, nao invente)", "stamps": []}


CHECKS = [check_repo_sync, check_core_agnostic, check_cross_ai_boot_scan, check_version_sanity]


def run_checks():
    results = []
    for fn in CHECKS:
        try:
            results.append(fn())
        except Exception as e:  # noqa: BLE001
            results.append({"name": getattr(fn, "__name__", "?"), "status": "fail",
                            "detail": f"excecao: {e}", "stamps": []})
    return results


def stamp_liveness(session_id, results):
    """Carimba .claude/.hooklive/<key>=<session_id> para cada gate que ESTE boot_check executou
    sem falha -> o auditor de liveness (route-gate) se cala. So com session_id real."""
    if not session_id:
        return
    live = os.path.join(ROOT, ".claude", ".hooklive")
    try:
        os.makedirs(live, exist_ok=True)
        # o proprio boot_check rodou nesta sessao -> cala o nag de liveness de "boot-check"
        with open(os.path.join(live, "boot-check"), "w", encoding="utf-8") as f:
            f.write(session_id)
        # cada check ja decidiu seus stamps (lista vazia se NAO confirmou execucao/passou) -> sem
        # filtro de status aqui; carimba so o que o check atestou como executado-e-ok.
        for r in results:
            for key in r.get("stamps", []):
                with open(os.path.join(live, key), "w", encoding="utf-8") as f:
                    f.write(session_id)
    except Exception:
        pass


def write_proof(session_id, results):
    proof = {
        "session": session_id,
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "all_ok": all(r["status"] != "fail" for r in results),
        "checks": [{k: r[k] for k in ("name", "status", "detail")} for r in results],
    }
    out = os.path.join(ROOT, ".claude", "boot-proof.json")
    try:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(proof, f, ensure_ascii=False, indent=2)
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"[boot_check] nao gravou boot-proof.json: {e}\n")
    return proof


def main(argv):
    session_id = ""
    if "--session" in argv:
        i = argv.index("--session")
        if i + 1 < len(argv):
            session_id = argv[i + 1]
    # auto-deteccao do session_id do runtime: o nome REAL e CLAUDE_CODE_SESSION_ID (achado CRITICO
    # do qa-critic 2026-06-10 — CLAUDE_SESSION_ID nao existe). Assim o agente roda o comando BARE
    # (`python tools/boot_check.py`) e o liveness se carimba sozinho, sem precisar saber o id.
    session_id = (session_id or os.environ.get("CLAUDE_CODE_SESSION_ID")
                  or os.environ.get("CLAUDE_SESSION_ID") or "")

    results = run_checks()
    stamp_liveness(session_id, results)
    proof = write_proof(session_id, results)

    glyph = {"ok": "✅", "warn": "⚠️ ", "fail": "❌", "skip": "·"}
    print("# boot_check (emenda ADR-061) — self-check de boot, prova em .claude/boot-proof.json")
    for r in results:
        print(f"{glyph.get(r['status'], '?')} {r['name']:18} {r['detail']}")
    print("-" * 50)
    skips = [r["name"] for r in results if r["status"] == "skip"]
    if not proof["all_ok"]:
        verdict = "ATENCAO (gate de boot FALHOU — ver acima)"
    elif skips:
        # honestidade anti-overclaim (achado do process-critic 2026-06-10): skip != executado
        verdict = f"OK (gates executados; {len(skips)} skip declarado: {', '.join(skips)})"
    else:
        verdict = "OK (todos os gates de boot executados)"
    print(f"RESULTADO: {verdict}"
          f"{'' if session_id else '  [sem --session: liveness nao carimbado]'}")
    return 0  # fail-soft: reporta, nao trava o boot


if __name__ == "__main__":
    sys.exit(main(sys.argv))
