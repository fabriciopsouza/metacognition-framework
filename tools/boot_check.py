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
import platform
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


def check_trabalhos_abertos():
    """Oferece os trabalhos com handoff em aberto (ADR-100).

    O Pacote P14 (`tools/handoff.py`) e completo, mas EFEMERO: gerado, exibido e perdido.
    Sem isto, quem abre a proxima sessao nao e lembrado de que existe trabalho aguardando
    decisao — e reconstitui o estado do zero, ou simplesmente nao retoma.

    NUNCA falha o boot: trabalho pendente e informacao, nao erro. Mas tambem nunca fica
    silencioso — "nenhum aberto" e resultado declarado, nao ausencia de checagem.
    """
    rc, out = _run(sys.executable, os.path.join("tools", "trabalhos.py"), "listar")
    text = out.strip()
    if rc != 0:
        return {"name": "trabalhos-abertos", "status": "warn",
                "detail": text.replace("\n", " ")[:300], "stamps": []}
    if "nenhum trabalho em aberto" in text:
        return {"name": "trabalhos-abertos", "status": "ok",
                "detail": "nenhum trabalho em aberto (verificado, nao presumido)",
                "stamps": []}
    nomes = [l.strip()[2:].strip() for l in text.splitlines() if l.startswith("▸")]
    return {"name": "trabalhos-abertos", "status": "ok",
            "detail": f"{len(nomes)} trabalho(s) aguardando decisao: " +
                      " · ".join(n[:60] for n in nomes[:4]),
            "stamps": []}


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


def detect_session_model(transcript_path=""):
    """Auto-detecta o modelo ATIVO da sessao SEM cooperacao do agente: le o ULTIMO turn assistant do
    transcript JSONL (campo `message.model`/`model`). Path vem do hook (transcript_path) OU e derivado
    de CLAUDE_CODE_SESSION_ID em ~/.claude/projects/*/<sid>.jsonl. Determinismo: le arquivo local,
    nunca probe de rede. '' se nao encontrar (-> gate emite 'declare', nunca falso-OK)."""
    import glob
    path = transcript_path
    if not path:
        sid = os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID") or ""
        if not sid:
            return ""
        cands = glob.glob(os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", sid + ".jsonl"))
        if not cands:
            return ""
        path = max(cands, key=os.path.getmtime)
    model = ""
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = re.search(r'"model"\s*:\s*"([^"]+)"', line)
                if m and m.group(1) not in ("<synthetic>", ""):
                    model = m.group(1)  # mantem o ULTIMO -> modelo do turn mais recente
    except Exception:
        return ""
    return model


def check_author_tier(author_model=""):
    """Gate de TIER-AUTOR da sessao (ADR-082): o modelo da sessao principal NAO e governado pelo
    model-policy.json (e do harness/`/model`) — esta era a cegueira que deixou Sonnet virar autor em
    silencio e auto-aprovar um gate vermelho (v1.59.0). Aqui o baseline de autor e LIDO do dado e
    comparado ao modelo-autor detectado; autor < baseline COM baseline disponivel -> banner LOUD.
    Determinismo: entrada = arg/env declarada, nunca probe de rede. Fail-soft (nunca trava o boot)."""
    try:
        pol = json.load(open(os.path.join(ROOT, "tools", "model-policy.json"), encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"name": "author-tier", "status": "warn",
                "detail": f"model-policy.json ilegivel ({e}) — baseline de autor nao verificado", "stamps": []}
    ba = pol.get("baseline_author", {})
    baseline = (ba.get("model") or "").lower()
    # ordem de capacidade (desc) data-driven: max -> balanced -> economy, dedup
    order = []
    for t in ("max", "balanced", "economy"):
        for fam in pol.get("tiers", {}).get(t, {}).get("chain", []):
            if fam not in order:
                order.append(fam)
    unavailable = {x.strip().lower() for x in os.environ.get("FRAMEWORK_MODELS_UNAVAILABLE", "").split(",") if x.strip()}
    baseline_avail = baseline and baseline not in unavailable
    am = (author_model or os.environ.get("CLAUDE_CODE_MODEL") or os.environ.get("ANTHROPIC_MODEL")
          or os.environ.get("CLAUDE_MODEL") or detect_session_model()).lower()
    fam = ""
    for f, mid in pol.get("model_ids", {}).items():
        if f in am or str(mid).lower() in am:
            fam = f
            break
    crit = "Sonnet/Haiku so como CRITICO/docops, nunca como autor com baseline disponivel (ADR-082)."
    if not fam:
        return {"name": "author-tier", "status": "warn",
                "detail": f"modelo-autor da sessao NAO detectado — DECLARE. Baseline de autor = {baseline or '?'}. "
                          f"Se a sessao roda < baseline com baseline disponivel, troque (/model {baseline}) "
                          f"ou declare indisponibilidade. {crit}", "stamps": []}
    if baseline_avail and fam in order and baseline in order and order.index(fam) > order.index(baseline):
        return {"name": "author-tier", "status": "warn",
                "detail": f"AUTOR rodando em '{fam}' ABAIXO do baseline '{baseline}' (disponivel). "
                          f"TROQUE: /model {baseline} — ou declare {baseline} indisponivel "
                          f"(FRAMEWORK_MODELS_UNAVAILABLE). {crit}", "stamps": []}
    return {"name": "author-tier", "status": "ok",
            "detail": f"autor='{fam}' >= baseline='{baseline}'"
                      + ("" if baseline_avail else f" (baseline {baseline} DECLARADO indisponivel -> downgrade ok)"),
            "stamps": []}


# ---------------------------------------------------------------------------
# ADR-093 — detecção de ambiente + aplicabilidade das premissas (cross-session/cross-IA)
# ---------------------------------------------------------------------------
ENV_MANIFEST = os.path.join(ROOT, ".agent", "environment.json")


def detect_environment():
    """Ambiente REAL desta máquina (determinístico — nunca probe de rede)."""
    return {"host": platform.node() or "?", "os": platform.system() or "?"}


def _path_exists(value):
    """Primitivo único cross-platform p/ kind path|drive. Drive ejetado/inacessível -> False
    (a verdade viva que o agente precisa), não falso-presente por 'letra reservada'."""
    try:
        return bool(value) and os.path.exists(os.path.expandvars(os.path.expanduser(str(value))))
    except Exception:  # noqa: BLE001 — boot nunca crasha
        return False


SUPPORTED_KINDS = ("path", "drive", "env", "host", "hook", "process")


def _process_running(value):
    """ADR-094: detecta se um processo casa `value` (regex, ex.: 'avp|kaspersky') na lista viva.
    Cross-platform, determinístico (sem rede), fail-soft. Torna a premissa EDR VERIFICÁVEL, não assumida.
    NB (qa-critic): POSIX `ps -o comm` trunca o nome a ~15 chars → use PREFIXO curto no manifesto
    (ex.: 'avp', 'klnag'). ReDoS: o regex vem do manifesto (controlado pelo dono) e é COMPILADO antes do
    subprocess (re.error cai cedo); risco baixo (boot advisory/fail-soft)."""
    if not value:
        return False
    try:
        rx = re.compile(str(value), re.IGNORECASE)  # compila ANTES (re.error imediato; qa-critic MÉD-1)
        cmd = ["tasklist"] if platform.system() == "Windows" else ["ps", "-A", "-o", "comm"]
        out = subprocess.run(cmd, capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=20).stdout
        return rx.search(out) is not None
    except Exception:  # noqa: BLE001 — boot nunca crasha
        return False


def eval_assumption(a):
    """Matriz de polaridade (ADR-093): expect_present × found -> APLICA | ESTALE | AUSENTE.
    kind não-suportado -> INDEFINIDO (NUNCA APLICA silencioso — achado M1 do qa-critic)."""
    kind = (a.get("kind") or "").lower()
    expect = bool(a.get("expect_present", True))
    value = a.get("value", "")
    if kind not in SUPPORTED_KINDS:
        return {"id": a.get("id", "?"), "kind": kind, "expect_present": expect, "found": None,
                "verdict": "INDEFINIDO",
                "note": f"kind '{kind}' não suportado ({'/'.join(SUPPORTED_KINDS)}) — premissa NÃO verificada"}
    if kind in ("path", "drive"):
        found = _path_exists(value)
    elif kind == "env":
        found = bool(os.environ.get(str(value))) if value else False
    elif kind == "host":
        found = (platform.node() or "").lower() == str(value).lower()
    elif kind == "process":  # ADR-094: EDR/processo VERIFICÁVEL (ex.: premissa "Kaspersky veta hooks")
        found = _process_running(value)
    else:  # hook — NB: .hooklive PERSISTE entre sessões (proxy de "hooks já rodaram neste repo",
        #  não "hooks ativos NESTA sessão"); limite declarado (ADR-093, achado B3 do qa-critic).
        found = os.path.isdir(os.path.join(ROOT, ".claude", ".hooklive"))
    if expect and found:
        verdict = "APLICA"
    elif expect and not found:
        verdict = "AUSENTE"
    elif not expect and not found:
        verdict = "APLICA"
    else:  # not expect and found -> o CASO-RAIZ (prosa diz ausente, mas existe)
        verdict = "ESTALE"
    return {"id": a.get("id", "?"), "kind": kind, "expect_present": expect,
            "found": found, "verdict": verdict, "note": a.get("note", "")}


def build_env_envelope(stale, env):
    """Monta o envelope de handoff EXATO que cross_ai_hub.deposit() exige (os 10 campos REQUIRED).
    Determinístico (report_id por host+dia -> idempotente). Função pura -> o canário a verifica."""
    host = env.get("host", "?")
    date = datetime.date.today().isoformat()
    return {
        "schema_version": "1.0",
        "report_id": f"env-applicability-{host}-{date}",
        "topic_fingerprint": "environment-applicability",
        "thread_id": f"env-{host}",
        "from": "claude-master",
        "to": "[all]",
        "date": date,
        "status": "open",
        "kind": "environment-alert",
        "round": 1,
    }


def emit_cross_ai_handoff(stale, env):
    """ADR-069: claude-master só ESCREVE no próprio outbox (deposit no hub = fluxo de PR, não auto).
    Escreve o envelope quando há ESTALE/AUSENTE -> outra IA/sessão não repete a premissa errada.
    Fail-soft: outbox não-gravável -> só registro local em boot-proof.json. Devolve msg de status."""
    envelope = build_env_envelope(stale, env)
    ids = ", ".join(s["id"] for s in stale)
    fm = "\n".join(f"{k}: {envelope[k]}" for k in envelope)
    body = (f"---\n{fm}\n---\n\n"
            f"# Alerta de ambiente — premissa(s) divergente(s) em {env.get('host', '?')}\n\n"
            f"Premissas ESTALE/AUSENTE no boot: {ids}.\n"
            f"Não confie na prosa do briefing/ADR sobre estes itens NESTA máquina — file-first (ADR-093).\n")
    outbox = os.path.join(ROOT, "docs", "_private", "cross-ai", "outbox")
    try:
        os.makedirs(outbox, exist_ok=True)
        dest = os.path.join(outbox, f"{envelope['report_id']}.md")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(body)
        return f"envelope cross-IA -> {os.path.relpath(dest, ROOT)} (deposite no hub via PR, ADR-069)"
    except Exception as e:  # noqa: BLE001
        return f"cross-IA fail-soft (outbox não-gravável: {e}) — registro só local em boot-proof.json"


def check_environment_applicability():
    """ADR-093: detecta ambiente real + cruza com .agent/environment.json (APLICA/ESTALE/AUSENTE).
    Sem manifesto -> skip declarado (nunca falso-OK). Fail-soft. Cross-session via bloco 'environment'
    do boot-proof.json; cross-IA via outbox quando há divergência."""
    env = detect_environment()
    if not os.path.isfile(ENV_MANIFEST):
        return {"name": "env-applicability", "status": "skip",
                "detail": f"sem .agent/environment.json (host={env['host']} os={env['os']}) — copie "
                          f".agent/environment.example.json e declare as premissas (ADR-093)",
                "stamps": [], "environment": {**env, "assumptions": []}}
    try:
        with open(ENV_MANIFEST, encoding="utf-8-sig") as _f:  # B1: context manager
            data = json.load(_f)
        assumptions = data.get("assumptions", []) or []
    except Exception as e:  # noqa: BLE001
        return {"name": "env-applicability", "status": "warn",
                "detail": f".agent/environment.json ilegível ({e}) — premissas NÃO verificadas",
                "stamps": [], "environment": {**env, "assumptions": []}}
    if not assumptions:  # B4: manifesto presente mas vazio != "tudo OK" (nunca falso-OK)
        return {"name": "env-applicability", "status": "skip",
                "detail": f"manifesto presente sem premissas (host={env['host']} os={env['os']}) — "
                          f"preencha assumptions[] (ADR-093)",
                "stamps": [], "environment": {**env, "assumptions": []}}
    evaluated = [eval_assumption(a) for a in assumptions]
    stale = [e for e in evaluated if e["verdict"] in ("ESTALE", "AUSENTE")]
    indef = [e for e in evaluated if e["verdict"] == "INDEFINIDO"]  # M1: kind não-suportado
    block = {**env, "assumptions": evaluated}
    if not stale and not indef:
        return {"name": "env-applicability", "status": "ok",
                "detail": f"host={env['host']} os={env['os']} — {len(evaluated)} premissa(s) APLICAM",
                "stamps": [], "environment": block}
    parts = []
    xai = ""
    if stale:
        xai = " " + emit_cross_ai_handoff(stale, env)
        parts.append("DIVERGÊNCIA: " + "; ".join(f"{s['id']}={s['verdict']}" for s in stale))
    if indef:
        parts.append("NÃO-VERIFICADO (kind inválido): " + "; ".join(s["id"] for s in indef))
    return {"name": "env-applicability", "status": "warn",
            "detail": f"host={env['host']} os={env['os']} — " + " | ".join(parts) +
                      ". NÃO confie na prosa documentada; file-first." + xai,
            "stamps": [], "environment": block}


CHECKS = [check_repo_sync, check_core_agnostic, check_cross_ai_boot_scan, check_version_sanity,
          check_environment_applicability, check_trabalhos_abertos]


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
    # ADR-093: bloco environment = SNAPSHOT por-boot (datado em `ts`), "última realidade observada",
    # NUNCA premissa congelada — o próximo boot re-detecta e sobrescreve.
    env_res = next((r for r in results if r.get("name") == "env-applicability"), None)
    if env_res and "environment" in env_res:
        proof["environment"] = env_res["environment"]
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

    author_model = ""
    if "--author-model" in argv:
        i = argv.index("--author-model")
        if i + 1 < len(argv):
            author_model = argv[i + 1]

    results = run_checks()
    results.append(check_author_tier(author_model))  # ADR-082: tier-autor da sessao (arg/env)
    stamp_liveness(session_id, results)
    proof = write_proof(session_id, results)

    glyph = {"ok": "✅", "warn": "⚠️ ", "fail": "❌", "skip": "·"}
    print("# boot_check (emenda ADR-061) — self-check de boot, prova em .claude/boot-proof.json")
    for r in results:
        print(f"{glyph.get(r['status'], '?')} {r['name']:18} {r['detail']}")
    print("-" * 50)
    skips = [r["name"] for r in results if r["status"] == "skip"]
    warns = [r["name"] for r in results if r["status"] == "warn"]
    if not proof["all_ok"]:
        verdict = "ATENCAO (gate de boot FALHOU — ver acima)"
    elif warns:
        # honestidade anti-overclaim (process-critic heterogeneo Sonnet 2026-06-16): warn NAO pode
        # se esconder atras de 'OK' na linha-resumo que a CI le. author-tier<baseline aparece AQUI.
        verdict = f"OK-COM-ALERTA ({len(warns)} warn: {', '.join(warns)} — ver acima; ex.: author-tier abaixo do baseline)"
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
