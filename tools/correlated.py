#!/usr/bin/env python3
"""correlated.py — atualizacao CORRELACIONADA obrigatoria (ADR-101). "Tem que ser tudo."

GAP DE CAMPO (dono, 2026-08-07): *"se estou atualizando as regras para um agente vertexai/reasoning,
o par text-2-sql so e atualizado se eu provocar. DEVERIA ser automaticamente, pois um esta associado
ao outro."* O mesmo vale p/ ADR x CHANGELOG x capabilities, gate x canario, skill x doc.

POR QUE NENHUM GATE PEGAVA: `completeness-gate` compara ESCOPO PEDIDO x ENTREGA — mede o que foi
dito. Acoplamento e o que NAO foi dito: o par nao aparece no pedido justamente porque o dono
assume que o agente sabe que os dois andam juntos. Nenhum mecanismo do repo modelava relacao
ENTRE artefatos, entao "atualizou metade do par" era literalmente inavaliavel (regua §0, porta (c):
destrava um eval impossivel hoje).

MECANISMO: `<projeto>/.agent/correlations.json` declara GRUPOS de globs que mudam juntos. Dado o
conjunto de arquivos tocados, um grupo esta VIOLADO se >=1 membro foi tocado e >=1 membro nao foi.
Determinismo total: globs + conjuntos, sem heuristica e sem modelo.

SEM MANIFESTO -> skip DECLARADO (nunca falso-OK): o silencio diria "nada acoplado aqui", que e a
afirmacao mais perigosa possivel.

Uso:
    python tools/correlated.py --check                 # usa o git diff do projeto (working tree)
    python tools/correlated.py --files a.py b.md       # conjunto explicito
    python tools/correlated.py --init                  # cria .agent/correlations.json de exemplo

Exit 0 = OK ou skip declarado; 1 = grupo violado.
"""
import argparse
import fnmatch
import json
import os
import subprocess
import sys

MANIFEST_REL = os.path.join(".agent", "correlations.json")

TEMPLATE = {
    "_doc": "ADR-101 — grupos de artefatos que MUDAM JUNTOS. Tocar um membro obriga tocar todos "
            "(rule='all'). Globs sao relativos a raiz do projeto, estilo fnmatch (use **/ para "
            "recursivo). Declare aqui os pares que voce hoje precisa lembrar de pedir.",
    "schema_version": 1,
    "groups": [
        {
            "id": "exemplo-par-de-agentes",
            "note": "EXEMPLO — troque pelos seus. Regra do agente e seu par andam juntos.",
            "rule": "all",
            "members": ["config/agente-a/**", "config/agente-b/**"],
        }
    ],
}


def load_manifest(root):
    path = os.path.join(root, MANIFEST_REL)
    if not os.path.isfile(path):
        return None, f"sem {MANIFEST_REL} — acoplamento NAO declarado (skip declarado, nao 'OK')"
    try:
        with open(path, encoding="utf-8-sig") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        return None, f"{MANIFEST_REL} ilegivel ({e}) — acoplamento NAO verificado"
    groups = (data or {}).get("groups") or []
    if not groups:
        return None, f"{MANIFEST_REL} sem groups[] — acoplamento NAO verificado"
    return groups, ""


def _norm(p):
    return str(p).replace("\\", "/").lstrip("./")


def matches(pattern, path):
    """fnmatch com semantica de prefixo p/ '**': 'a/**' casa 'a/b/c.txt' e 'a/b'."""
    pat, p = _norm(pattern), _norm(path)
    if fnmatch.fnmatch(p, pat):
        return True
    if pat.endswith("/**") and (p == pat[:-3] or p.startswith(pat[:-2])):
        return True
    return False


def check(groups, touched):
    """Retorna lista de violacoes: grupos com membro tocado E membro intocado."""
    touched = [_norm(t) for t in touched if t]
    violations = []
    for g in groups:
        members = g.get("members") or []
        if len(members) < 2:
            continue
        hit, miss = [], []
        for m in members:
            if any(matches(m, t) for t in touched):
                hit.append(m)
            else:
                miss.append(m)
        if hit and miss:
            violations.append({"id": g.get("id", "?"), "note": g.get("note", ""),
                               "touched": hit, "missing": miss})
    return violations


def git_touched(root):
    """Arquivos com mudanca no working tree + staged (o que a sessao efetivamente mexeu)."""
    try:
        r = subprocess.run(["git", "-C", root, "status", "--porcelain", "-uall"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30)
        if r.returncode != 0:
            return []
    except (OSError, subprocess.SubprocessError):
        return []
    out = []
    for line in r.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip().strip('"')
        if " -> " in path:  # rename: conta o destino
            path = path.split(" -> ", 1)[1]
        out.append(path)
    return out


def main():
    ap = argparse.ArgumentParser(description="Gate de atualizacao correlacionada (ADR-101)")
    ap.add_argument("--root", default=os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    ap.add_argument("--files", nargs="*", help="conjunto explicito (default: git status do projeto)")
    ap.add_argument("--check", action="store_true",
                    help="checa o conjunto tocado (default; explicito p/ legibilidade em script)")
    ap.add_argument("--init", action="store_true", help="cria .agent/correlations.json de exemplo")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.init:
        path = os.path.join(root, MANIFEST_REL)
        if os.path.isfile(path):
            print(f"[correlated] ja existe: {path} (nao sobrescrevo — traceability Regra 3)")
            return 0
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(TEMPLATE, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"[correlated] criado: {path} — declare seus grupos.")
        return 0

    groups, skip = load_manifest(root)
    touched = args.files if args.files is not None else git_touched(root)
    if groups is None:
        result = {"status": "SKIP", "detail": skip, "violations": []}
    else:
        viols = check(groups, touched)
        result = {"status": "FAIL" if viols else "OK",
                  "detail": (f"{len(viols)} grupo(s) violado(s)" if viols
                             else f"{len(groups)} grupo(s) coerente(s)"),
                  "violations": viols}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"[correlated] {result['status']}: {result['detail']}")
        for v in result["violations"]:
            print(f"  - grupo `{v['id']}`: tocou {v['touched']} mas NAO tocou {v['missing']}")
            if v["note"]:
                print(f"    ({v['note']})")
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
