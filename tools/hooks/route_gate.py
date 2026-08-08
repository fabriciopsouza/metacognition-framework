#!/usr/bin/env python3
"""route_gate.py — UserPromptSubmit: roteamento deterministico (ADR-027). Port Python do
route-gate.ps1 (ADR-101), preservando comportamento; a versao PS fica como fallback.

POR QUE O PORT: o wiring GLOBAL (~/.claude/settings.json) so tinha hooks .ps1. Hook em
PowerShell e refem de politica de EDR/GPO (ADR-060) e de PS ausente (Linux/macOS) — foi
exatamente o que sobrou capado no global, deixando todo projeto nao-framework sem gates.
Python roda nos tres SOs e e o que os demais gates ja usam.

MECANISMO (identico ao PS): a cada prompt nao-trivial, injeta `additionalContext` lembrando
o agente de DECLARAR A ROTA antes de tool call de dominio. Dispara 1x por sessao (marker por
session_id). Carrega tambem o auditor de liveness (ADR-061) e o nudge de defasagem (ADR-084),
que valem TODO turno mesmo quando a rota ja foi injetada.

Fail-OPEN: qualquer erro -> emite silencio e exit 0. Um gate de ENTRADA nunca trava o usuario.

DESATIVACAO: .claude/session.lock (projeto) ou ~/.claude/session.lock (todos).
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import framework_root, project_root, read_payload  # noqa: E402

TRIVIAL_RX = re.compile(
    r"^(ok|okay|sim|n[aã]o|valeu|obrigad[oa]|certo|isso|segue|siga|continua[r]?|prossiga|"
    r"beleza|blz|pode|vai|go|yes|no|thanks?)\b.{0,12}$", re.IGNORECASE)

ROUTE_CTX = """# [route-gate ADR-027] Declare a ROTA antes de executar

Antes de QUALQUER tool call de dominio (escrever/calcular/transformar/buscar dados),
declare a rota em 1 linha e carregue a skill correspondente:

  ROTA: pontual -> metacognicao
      | multi-etapa -> squad (pmo -> discovery -> architect -> developer -> qa-critic -> docops)
      | alto-risco/regulado/irreversivel/numero-que-vai-a-decisao -> + high-stakes-gate

Classifique a tarefa (contexto x complexidade) e ATIVE a(s) skill(s) ANTES de agir —
nao comece a executar analise de dominio antes de declarar a rota.

**O pedido do dono NAO e livre de erro/questionamento.** Antes de cumprir, SURFACE
tensoes/premissas/ancoras **+ o CUSTO e a CONSEQUENCIA** (surface-and-reconcile); um
OVERRIDE de gate exige confirmacao explicita **com custo/consequencia informados**,
nunca silenciosa. Se voce nao questiona, nao funciona.

Output-style (learning/explanatory/etc.) governa o TOM/formato da entrega, **nunca
substitui** o processo (roteamento/gates). Se voce JA roteou nesta sessao, ignore esta nota.

Desativar o framework aqui: criar `.claude/session.lock` (este projeto) ou
`~/.claude/session.lock` (todos). Reativar: deletar o lock.
"""


def emit(ctx=""):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit", "additionalContext": ctx}}, ensure_ascii=False))
    sys.exit(0)


def _git(cwd, *args):
    try:
        r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=15)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def liveness_nudge(cwd, session_id):
    """ADR-061: declara gates cujo carimbo != sessao atual. Sem session_id, nao audita."""
    if not session_id:
        return ""
    # O manifesto e ASSET DO FRAMEWORK; os carimbos sao do PROJETO aberto.
    manifest = os.path.join(framework_root(), "tools", "hooks", "hooks-manifest.json")
    if not os.path.isfile(manifest):
        return ""
    try:
        with open(manifest, encoding="utf-8-sig") as f:
            audited = (json.load(f) or {}).get("audited_hooks", []) or []
    except (OSError, ValueError):
        return ""
    live = os.path.join(cwd, ".claude", ".hooklive")
    inert = []
    for h in audited:
        key = h.get("key", "")
        stamp = ""
        try:
            with open(os.path.join(live, key), encoding="utf-8") as f:
                stamp = f.read().strip()
        except (OSError, ValueError):
            stamp = ""
        if stamp != session_id:
            inert.append(f"- **{h.get('gate', key)}** (hook `{key}`) NAO rodou nesta sessao -> "
                         f"gate INERTE. Aplique manual: {h.get('manual', '(sem fallback declarado)')}")
    if not inert:
        return ""
    return ("# [liveness ADR-061] Gate(s) sem carimbo desta sessao (causa NAO verificada — "
            "declarado, NAO silencioso):\n\n" + "\n".join(inert) +
            "\n\n(Causas possiveis, em ordem: (1) timing — hook async pendente em sessao recem-aberta; "
            "(2) hook nao cabeado em settings — rode `python tools/wire_gates.py --check`; "
            "(3) veto de EDR, SO onde o detector confirmar. NAO assuma EDR: "
            "`python tools/boot_check.py` cruza a premissa com a realidade viva (ADR-093/101).)\n\n")


def stale_nudge(cwd):
    """ADR-084: repete por-turno a defasagem vs a branch de integracao ate resolver/reconhecer."""
    stale_file = os.path.join(cwd, ".claude", ".stale-vs-main")
    ack_file = os.path.join(cwd, ".claude", ".stale-vs-main.ack")
    if not os.path.isfile(stale_file):
        return ""
    base = ""
    try:
        with open(stale_file, encoding="utf-8") as f:
            for line in f:
                if line.startswith("base="):
                    base = line[len("base="):].strip()
                    break
    except (OSError, ValueError):
        return ""
    if not base:
        return ""
    cnt = _git(cwd, "rev-list", "--count", f"HEAD..{base}")
    if not cnt:  # git mudo -> nunca limpa por erro
        return ""
    if cnt == "0":
        for p in (stale_file, ack_file):
            try:
                os.remove(p)
            except OSError:
                pass
        return ""
    cur = _git(cwd, "rev-parse", "--short", base)
    ack = ""
    try:
        with open(ack_file, encoding="utf-8") as f:
            ack = re.sub(r"\s", "", f.read())
    except (OSError, ValueError):
        ack = ""
    if ack and ack == cur:
        return ""
    return (f"# [ADR-084] RETRATO CONGELADO — {cnt} commit(s) atras de `{base}`\n\n"
            "Voce NAO esta no topo do framework. NAO afirme estado/versao nem edite o nucleo "
            "antes de resolver.\n"
            f"- Resolver: `git rebase {base}` (ou merge).\n"
            f"- Reconhecer o risco: `git rev-parse --short {base} > .claude/.stale-vs-main.ack`.\n"
            "- Desativar nudges da sessao: criar `.claude/session.lock`.\n\n")


def main():
    nudge = ""
    try:
        payload = read_payload()
        session_id = str(payload.get("session_id") or "")
        prompt = str(payload.get("prompt") or "")
        cwd = project_root(payload)

        if os.path.isfile(os.path.join(cwd, ".claude", "session.lock")) or \
           os.path.isfile(os.path.join(os.path.expanduser("~"), ".claude", "session.lock")):
            emit()

        nudge = stale_nudge(cwd) + liveness_nudge(cwd, session_id)

        trimmed = re.sub(r"\s+", " ", prompt).strip()
        if len(trimmed) < 12 or TRIVIAL_RX.match(trimmed):
            emit(nudge)

        if session_id:
            state = os.path.join(os.path.expanduser("~"), ".claude", ".route-state")
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id)
            marker = os.path.join(state, safe + ".routed")
            if os.path.isfile(marker):
                emit(nudge)
            try:  # marca ANTES de injetar: falha posterior nao vira loop
                os.makedirs(state, exist_ok=True)
                with open(marker, "w", encoding="utf-8") as f:
                    f.write(cwd)
            except OSError:
                pass

        emit(nudge + ROUTE_CTX)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 — fail-open absoluto
        sys.stderr.write(f"[route-gate] warning (nao-bloqueante): {e}\n")
        emit(nudge)


if __name__ == "__main__":
    main()
