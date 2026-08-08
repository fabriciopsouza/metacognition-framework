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
import re
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


RULES = ("all", "pairwise")


def _norm(p):
    return str(p).replace("\\", "/").lstrip("./")


def matches(pattern, path):
    """fnmatch com semantica de prefixo p/ '**': 'a/**' casa 'a/b/c.txt' e 'a/b'.

    QA ADR-101: usava `fnmatch.fnmatch`, que aplica `os.path.normcase` — case-INsensitive no
    Windows e case-sensitive no POSIX. O mesmo manifesto dava veredito diferente no CI Linux e
    na maquina do dono, contradizendo o "determinismo total" do docstring. `fnmatchcase` fixa.
    """
    pat, p = _norm(pattern), _norm(path)
    if fnmatch.fnmatchcase(p, pat):
        return True
    if pat.endswith("/**") and (p == pat[:-3] or p.startswith(pat[:-2])):
        return True
    return False


def _stem(pattern, path, strip_prefixes=(), strip_suffixes=()):
    """Radical capturado pelos curingas do glob. 'tools/test_*.py' x 'tools/test_a.py' -> 'a'.

    Base do rule='pairwise': exige que o PAR CORRESPONDENTE mude, nao um membro qualquer do
    conjunto. A normalizacao (`strip_prefixes`/`strip_suffixes`) e DADO declarado no manifesto,
    nao convencao adivinhada em codigo: neste repo `check_author_tier.py` pareia com
    `test_author_tier.py`, e sem declarar o afixo o pareamento acusaria falso-positivo.
    """
    pat, p = _norm(pattern), _norm(path)
    rx = "^" + "(.*)".join(re.escape(part) for part in pat.replace("**", "*").split("*")) + "$"
    m = re.match(rx, p)
    if not m:
        return None
    s = "|".join(m.groups()) if m.groups() else p
    for pre in strip_prefixes:
        if s.startswith(pre):
            s = s[len(pre):]
    for suf in strip_suffixes:
        if s.endswith(suf):
            s = s[:-len(suf)]
    return s


def _check_all(members, touched):
    """Semantica de CONJUNTO: >=1 membro tocado obriga TODOS os membros tocados."""
    hit = [m for m in members if any(matches(m, t) for t in touched)]
    miss = [m for m in members if m not in hit]
    return (hit, miss, "") if (hit and miss) else (None, None, "")


def _check_pairwise(members, touched, cfg=None):
    """Semantica de PAR: o radical tocado num membro obriga o MESMO radical nos outros.

    QA ADR-101 (BLOQUEANTE): com rule='all', o grupo `gate-precisa-de-canario`
    (tools/hooks/*.py + tools/test_*.py) era silenciado por QUALQUER test_*.py tocado — bastava
    mexer num teste nao relacionado para o gate parar de exigir canario do hook novo. Medido:
    `--files tools/hooks/new_gate.py tools/test_totalmente_nao_relacionado.py` dava OK.
    """
    cfg = cfg or {}
    pre = tuple(cfg.get("strip_prefixes") or ())
    suf = tuple(cfg.get("strip_suffixes") or ())
    isento = tuple(cfg.get("exempt") or ())
    # direction='forward': so os radicais vindos do PRIMEIRO membro obrigam os demais.
    # Sem isto o pareamento e simetrico e inventa exigencia impossivel: `tools/test_*.py` casa
    # TODO canario do repo, entao `test_wire_gates.py` passaria a exigir um
    # `tools/hooks/wire_gates.py` que nunca existiu (wire_gates.py mora em tools/). A relacao
    # real e direcional — gate exige canario, canario nao exige gate.
    forward = (cfg.get("direction") or "both").lower() == "forward"
    tocados = [t for t in touched if not any(matches(x, t) for x in isento)]
    por_membro = {m: {s for s in (_stem(m, t, pre, suf) for t in tocados) if s is not None}
                  for m in members}
    origem = [members[0]] if forward else members
    todos = set().union(*(por_membro[m] for m in origem)) if por_membro else set()
    hit, miss = [], []
    for stem in sorted(todos):
        if all(stem in por_membro[m] for m in members):
            continue
        for m in members:
            alvo = hit if stem in por_membro[m] else miss
            alvo.append(m.replace("*", stem, 1) if "*" in m else m)
    if not miss:
        return None, None, ""
    return sorted(set(hit)), sorted(set(miss)), "par correspondente"


def check(groups, touched, repo_files=None):
    """Retorna lista de violacoes. `repo_files` (opcional) diagnostica membro inatingivel."""
    touched = [_norm(t) for t in touched if t]
    violations = []
    for g in groups:
        members = g.get("members") or []
        if len(members) < 2:
            continue
        rule = (g.get("rule") or "all").lower()
        if rule not in RULES:
            # QA ADR-101: `rule` era campo MORTO (nunca lido) — quem declarasse outro valor
            # nao tinha efeito nem aviso. Agora vale, e valor invalido reprova DECLARADO.
            violations.append({"id": g.get("id", "?"), "note": g.get("note", ""),
                               "touched": [], "missing": [],
                               "erro": f"rule '{rule}' desconhecida (use: {', '.join(RULES)})"})
            continue
        if rule == "pairwise":
            hit, miss, modo = _check_pairwise(members, touched, g)
        else:
            hit, miss, modo = _check_all(members, touched)
        if not miss:
            continue
        inatingivel = []
        if repo_files is not None:
            for m in miss:
                alvo = m if "*" not in m else None
                existe = (any(matches(m, f) for f in repo_files) if alvo is None
                          else alvo in repo_files)
                if not existe:
                    inatingivel.append(m)
        violations.append({"id": g.get("id", "?"), "note": g.get("note", ""),
                           "rule": rule, "modo": modo,
                           "touched": hit, "missing": miss, "inatingivel": inatingivel})
    return violations


def _git(root, *args, timeout=30):
    try:
        r = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _worktree_touched(root):
    """Mudanca ainda nao commitada: working tree + staged + untracked."""
    out = []
    for line in _git(root, "status", "--porcelain", "-uall").splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip().strip('"')
        if " -> " in path:
            # QA ADR-101: contava so o destino; a origem sumia do escopo e um rename podia
            # tirar o arquivo de um glob de grupo sem que a correlacao percebesse.
            src, dst = path.split(" -> ", 1)
            out += [src.strip().strip('"'), dst.strip().strip('"')]
        else:
            out.append(path)
    return out


def _resolve_base(root, preferido="origin/main"):
    """Resolve a ref base do bloco. Ref inexistente = checagem que some em silencio."""
    for cand in (preferido, "origin/main", "origin/master", "main", "master"):
        if cand and _git(root, "rev-parse", "--verify", "--quiet", cand).strip():
            return cand
    return ""


def _branch_touched(root, base_ref="origin/main"):
    """Arquivos mudados pelos COMMITS do bloco (merge-base..HEAD)."""
    ref = _resolve_base(root, base_ref)
    if not ref:
        return []
    mb = _git(root, "merge-base", ref, "HEAD").strip()
    if not mb:
        return []
    return [ln.strip() for ln in _git(root, "diff", "--name-only", mb, "HEAD").splitlines()
            if ln.strip()]


def git_touched(root, scope="branch", base_ref="origin/main"):
    """Conjunto tocado pelo BLOCO de trabalho.

    QA ADR-101 (BLOQUEANTE): media so `git status --porcelain` no INSTANTE da chamada. Assim que
    o par quebrado era commitado, ele sumia do porcelain e o `--check` passava trivialmente com
    a arvore limpa ("OK: 5 grupo(s) coerente(s)" com zero arquivos tocados). Como o closing_gate
    roda no Stop — depois do commit — o gate media exatamente o momento em que nao ha mais nada
    para ver. Agora o default une working tree + commits do bloco; `--scope worktree` volta ao
    comportamento antigo quando so interessa o nao-commitado.
    """
    wt = _worktree_touched(root)
    if scope == "worktree":
        return wt
    return sorted(set(wt) | set(_branch_touched(root, base_ref)))


def repo_files(root):
    """Arquivos versionados — usados p/ distinguir 'membro esquecido' de 'glob com typo'."""
    return [ln.strip() for ln in _git(root, "ls-files").splitlines() if ln.strip()]


def main():
    ap = argparse.ArgumentParser(description="Gate de atualizacao correlacionada (ADR-101)")
    ap.add_argument("--root", default=os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    ap.add_argument("--files", nargs="*", help="conjunto explicito (default: git status do projeto)")
    ap.add_argument("--check", action="store_true",
                    help="checa o conjunto tocado (default; explicito p/ legibilidade em script)")
    ap.add_argument("--init", action="store_true", help="cria .agent/correlations.json de exemplo")
    ap.add_argument("--scope", default="branch", choices=["branch", "worktree"],
                    help="branch (default): working tree + commits do bloco; worktree: so o nao-commitado")
    ap.add_argument("--base", default="origin/main", help="ref base p/ --scope branch")
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
    if args.files is not None:
        touched, escopo = args.files, "explicito"
    else:
        touched = git_touched(root, args.scope, args.base)
        escopo = args.scope
    if groups is None:
        result = {"status": "SKIP", "detail": skip, "violations": [], "escopo": escopo}
    else:
        viols = check(groups, touched, repo_files(root))
        result = {"status": "FAIL" if viols else "OK",
                  "detail": (f"{len(viols)} grupo(s) violado(s)" if viols
                             else f"{len(groups)} grupo(s) coerente(s)"),
                  "escopo": escopo, "arquivos_tocados": len(touched), "violations": viols}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        n = result.get("arquivos_tocados", len(touched))
        print(f"[correlated] {result['status']}: {result['detail']} "
              f"(escopo={escopo}, {n} arquivo(s) tocado(s))")
        for v in result["violations"]:
            if v.get("erro"):
                print(f"  - grupo `{v['id']}`: MANIFESTO INVALIDO — {v['erro']}")
                continue
            print(f"  - grupo `{v['id']}` [rule={v.get('rule', 'all')}]: "
                  f"tocou {v['touched']} mas NAO tocou {v['missing']}")
            if v.get("inatingivel"):
                # Sem isto, um typo no glob viraria violacao PERMANENTE sem causa visivel —
                # e, via closing_gate, travaria o encerramento de sessao indefinidamente.
                print(f"    ATENCAO: {v['inatingivel']} nao casa NENHUM arquivo do repo "
                      f"— provavel TYPO no correlations.json, nao par esquecido.")
            if v["note"]:
                print(f"    ({v['note']})")
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
