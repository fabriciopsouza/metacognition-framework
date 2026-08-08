#!/usr/bin/env python3
"""wire_gates.py — o wiring de gates vira FUNCAO DO MANIFESTO, local e global (ADR-101).

A FALHA QUE ISTO CORRIGE (auditoria do dono, 2026-08-07). O wiring era escrito a mao em dois
lugares e divergiu de forma grosseira:
    .claude/settings.json  (repo-framework) ....... 17 gates
    ~/.claude/settings.json (global) ..............  2 gates, ambos .ps1
Como o global e o que vale ao abrir QUALQUER outro projeto, o framework rodava capado fora
de casa: sem mission-gate, sem effect-gate, sem overwrite-guard, sem context-budget, sem
author-tier, sem compaction-gate. Sobrava a prosa do CLAUDE.md — e prosa e exatamente o que
"so acontece se provocado" (relato do dono, verbatim). Isto explica de uma vez os itens
"ritos nao sao seguidos", "troca de modelos nao acontece", "ferramentas so se provocadas" e
"mais comum ao abrir repos que nao este".

Segunda falha, cozida no instalador: `bootstrap.py` instalava o **perfil non-admin** (settings
SEM hooks) como default, por medo de EDR. O medo virou politica permanente e desarmou o
framework em maquinas onde nao havia veto nenhum (ver ADR-093/094: a premissa e VERIFICAVEL).

MECANISMO: `tools/gates-manifest.json` e a SSoT. Este script GERA os dois settings a partir
dela, com `scope` decidindo quem vai pra onde ('framework' = so o repo-mae; 'both' = qualquer
projeto). No global os comandos recebem o path ABSOLUTO do framework, resolvido no ato — por
isso e re-executado a cada boot do repo-framework (ponto de Arquimedes herdado do
ensure-global-wiring.ps1, que este script SUBSTITUI).

PRESERVACAO (traceability Regra 3): nunca dropa chave que nao seja `hooks`; faz backup
`.wire.bak` antes de escrever; so escreve se houve mudanca (idempotente).

Uso:
    python tools/wire_gates.py --check              # diagnostico (exit 1 se divergente)
    python tools/wire_gates.py --install            # escreve .claude/settings.json do framework
    python tools/wire_gates.py --install-global     # escreve ~/.claude/settings.json (+ skills)
    python tools/wire_gates.py --print [--scope both]
"""
import argparse
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "tools", "gates-manifest.json")
EVENT_ORDER = ["SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "PreCompact", "Stop"]


def load_gates():
    with open(MANIFEST, encoding="utf-8-sig") as f:
        data = json.load(f)
    gates = data.get("gates") or []
    if not gates:
        raise SystemExit("[wire_gates] manifesto sem gates[] — nada a wirar")
    return gates


def _cmd(gate, base):
    """Comando do hook. base='' -> relativo (repo-framework); base=<abs> -> global portatil."""
    script = gate["script"]
    parts = script.split(" ", 1)
    path, extra = parts[0], (" " + parts[1] if len(parts) > 1 else "")
    if base:
        return f'python "{os.path.join(base, path.replace("/", os.sep))}"{extra}'
    return f"python {path}{extra}"


def build_hooks(gates, scope, base=""):
    """scope='framework' inclui tudo; scope='both' inclui so os portateis."""
    out = {}
    for g in gates:
        if scope == "both" and g.get("scope") != "both":
            continue
        entry = {"type": "command", "command": _cmd(g, base),
                 "timeout": g.get("timeout", 30), "statusMessage": g.get("status", g["key"])}
        block = {"hooks": [entry]}
        if g.get("matcher"):
            block["matcher"] = g["matcher"]
        out.setdefault(g["event"], []).append(block)
    return {ev: out[ev] for ev in EVENT_ORDER if ev in out}


def read_json(path):
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f) or {}
    except (OSError, ValueError):
        return {}


def write_settings(path, hooks, quiet=False):
    """Escreve preservando toda chave que nao seja `hooks`. Retorna True se mudou."""
    cur = read_json(path)
    if cur.get("hooks") == hooks:
        if not quiet:
            print(f"[wire_gates] ja wirado: {path}")
        return False
    if os.path.isfile(path):
        try:
            shutil.copy2(path, path + ".wire.bak")
        except OSError:
            pass
    new = dict(cur)
    new["hooks"] = hooks
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(new, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)
    if not quiet:
        n = sum(len(v) for v in hooks.values())
        print(f"[wire_gates] wiring aplicada: {path} ({n} gate(s))")
    return True


def mirror_assets(quiet=False):
    """Espelha skills/agents/workflows p/ ~/.claude (o que o sync-global.ps1 fazia, em Python)."""
    home = os.path.join(os.path.expanduser("~"), ".claude")
    pairs = [(os.path.join(ROOT, "_shared"), os.path.join(home, "skills")),
             (os.path.join(ROOT, ".agent", "skills"), os.path.join(home, "skills")),
             (os.path.join(ROOT, ".claude", "agents"), os.path.join(home, "agents")),
             (os.path.join(ROOT, ".agent", "workflows"), os.path.join(home, "workflows"))]
    n = 0
    for src, dst in pairs:
        if not os.path.isdir(src):
            continue
        os.makedirs(dst, exist_ok=True)
        for name in os.listdir(src):
            s = os.path.join(src, name)
            try:
                if os.path.isdir(s):
                    if not os.path.isfile(os.path.join(s, "SKILL.md")):
                        continue
                    shutil.copytree(s, os.path.join(dst, name), dirs_exist_ok=True)
                    n += 1
                elif name.endswith(".md"):
                    shutil.copy2(s, os.path.join(dst, name))
                    n += 1
            except (OSError, shutil.Error):
                continue
    if not quiet:
        print(f"[wire_gates] assets espelhados p/ ~/.claude ({n} item(s))")
    return n


def diagnose(gates):
    """Compara disco x manifesto nos dois escopos. Retorna (ok, linhas)."""
    home = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
    local = os.path.join(ROOT, ".claude", "settings.json")
    want_local = build_hooks(gates, "framework")
    want_global = build_hooks(gates, "both", base=ROOT)
    lines, ok = [], True
    for label, path, want in (("projeto (framework)", local, want_local),
                              ("global (~/.claude)", home, want_global)):
        have = read_json(path).get("hooks") or {}
        n_have = sum(len(v) for v in have.values())
        n_want = sum(len(v) for v in want.values())
        if have == want:
            lines.append(f"  OK   {label}: {n_have} gate(s) — em sincronia com o manifesto")
        else:
            ok = False
            lines.append(f"  DIVERGE {label}: disco={n_have} gate(s) x manifesto={n_want} "
                         f"-> rode `python tools/wire_gates.py "
                         f"{'--install' if 'projeto' in label else '--install-global'}`")
    return ok, lines


def main():
    ap = argparse.ArgumentParser(description="Wiring de gates a partir do manifesto (ADR-101)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--install-global", action="store_true")
    ap.add_argument("--print", dest="show", action="store_true")
    ap.add_argument("--scope", default="framework", choices=["framework", "both"])
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    gates = load_gates()

    if args.show:
        base = ROOT if args.scope == "both" else ""
        print(json.dumps(build_hooks(gates, args.scope, base), ensure_ascii=False, indent=2))
        return 0

    if args.check:
        ok, lines = diagnose(gates)
        print("[wire_gates] diagnostico do wiring (ADR-101):")
        for ln in lines:
            print(ln)
        return 0 if ok else 1

    rc = 0
    if args.install:
        write_settings(os.path.join(ROOT, ".claude", "settings.json"),
                       build_hooks(gates, "framework"), args.quiet)
    if args.install_global:
        mirror_assets(args.quiet)
        changed = write_settings(os.path.join(os.path.expanduser("~"), ".claude", "settings.json"),
                                 build_hooks(gates, "both", base=ROOT), args.quiet)
        if changed and not args.quiet:
            print("[wire_gates] gates globais re-afirmados — todo projeto herda os portateis.")
    if not (args.install or args.install_global):
        ap.print_help()
        rc = 2
    return rc


if __name__ == "__main__":
    sys.exit(main())
