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

def _canon(path):
    """Path canonico e ESTAVEL entre processos.

    QA ADR-101 (critico heterogeneo, 2026-08-08): `os.path.abspath` devolve a letra do drive
    com o case do processo chamador — terminal interativo dava `C:\\...`, o runner de hooks do
    Claude Code dava `c:\\...`. Paths funcionalmente identicos, textualmente distintos: o
    `--check` acusava DIVERGE com contagens IGUAIS dos dois lados (13 x 13) e mandava rodar
    `--install-global` para "corrigir" o que ja estava correto — e cada reescrita queimava o
    unico backup. Canonicalizar na origem mata o churn; `_cmp_key` abaixo e o cinto reserva.
    """
    p = os.path.normpath(os.path.abspath(path))
    drive, rest = os.path.splitdrive(p)
    return drive.upper() + rest


ROOT = _canon(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST = os.path.join(ROOT, "tools", "gates-manifest.json")
EVENT_ORDER = ["SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "PreCompact", "Stop"]
BACKUP_DEPTH = 3


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


class CorruptSettings(Exception):
    """settings.json existe mas nao e JSON valido — NUNCA sobrescrever por cima disto."""


def read_json(path, strict=False):
    """strict=True: arquivo ilegivel levanta CorruptSettings em vez de virar {}.

    QA ADR-101: engolir ValueError e devolver {} fazia com que um settings.json corrompido
    (truncado por crash, editado a mao com virgula sobrando) fosse SUBSTITUIDO por um arquivo
    contendo so `hooks` — perdendo permissions/model/env/statusLine do dono. Escrita usa strict.
    """
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f) or {}
    except ValueError as e:
        if strict:
            raise CorruptSettings(f"{path}: JSON invalido ({e})")
        return {}
    except OSError as e:
        if strict:
            raise CorruptSettings(f"{path}: ilegivel ({e})")
        return {}


def framework_scripts(gates):
    """Basenames dos scripts do manifesto — usados p/ reconhecer hook NOSSO x hook DO DONO."""
    return {os.path.basename(g["script"].split(" ", 1)[0]).lower() for g in gates}


def _block_is_ours(block, scripts):
    """True se TODO entry do bloco aponta p/ script do framework.

    Reconhece tambem o wiring LEGADO (`.claude/hooks/*.ps1` do ensure-global-wiring.ps1, que
    este script substitui) e qualquer comando ancorado na raiz do framework — senao a migracao
    2 .ps1 -> 13 Python nunca limparia os antigos. Na duvida o bloco e do DONO: preservar.
    """
    entries = block.get("hooks") or []
    if not entries:
        return False
    root_key = os.path.normcase(ROOT)
    for e in entries:
        cmd = os.path.normcase(e.get("command") or "")
        if not cmd:
            return False
        ours = (any(s in cmd for s in scripts)
                or root_key in cmd
                or os.path.normcase(os.path.join(".claude", "hooks")) in cmd)
        if not ours:
            return False
    return True


def merge_hooks(cur_hooks, new_hooks, scripts):
    """Substitui os blocos do FRAMEWORK e PRESERVA os do dono. Retorna (merged, n_preservados).

    QA ADR-101 (BLOQUEANTE): `new["hooks"] = hooks` era overwrite total da chave. Como o gate
    `sync-global` roda `--install-global` a CADA boot do repo-framework, qualquer hook proprio
    do dono (ou de outro plugin/MCP) num evento/matcher que o manifesto nao gera sumia
    silenciosamente — sem prompt, sem log do que foi removido.
    """
    merged, kept = {}, 0
    events = [e for e in EVENT_ORDER if e in new_hooks or e in cur_hooks]
    events += [e for e in cur_hooks if e not in events]
    for ev in events:
        ours = list(new_hooks.get(ev) or [])
        theirs = [b for b in (cur_hooks.get(ev) or []) if not _block_is_ours(b, scripts)]
        kept += len(theirs)
        if ours or theirs:
            merged[ev] = ours + theirs
    return merged, kept


def _cmp_key(hooks):
    """Chave de comparacao estavel: no Windows normaliza case de path dentro do `command`."""
    if os.name != "nt":
        return json.dumps(hooks, sort_keys=True, ensure_ascii=False)
    norm = {}
    for ev, blocks in (hooks or {}).items():
        norm[ev] = [dict(b, hooks=[dict(e, command=os.path.normcase(e.get("command") or ""))
                                   for e in (b.get("hooks") or [])]) for b in blocks]
    return json.dumps(norm, sort_keys=True, ensure_ascii=False)


def _rotate_backup(path):
    """Backup em profundidade (ADR-101 QA): .wire.bak, .wire.bak.1, .wire.bak.2.

    Backup de 1 geracao so protege contra o ULTIMO erro; um segundo boot ja apagava a prova.
    """
    if not os.path.isfile(path):
        return
    try:
        for i in range(BACKUP_DEPTH - 1, 0, -1):
            src = f"{path}.wire.bak" + (f".{i}" if i > 1 else "")
            if os.path.isfile(src):
                os.replace(src, f"{path}.wire.bak.{i + 1}")
        shutil.copy2(path, path + ".wire.bak")
    except OSError:
        pass


def write_settings(path, hooks, gates, quiet=False):
    """Escreve preservando toda chave != `hooks` E todo hook que nao seja do framework.

    Retorna True se mudou. Levanta CorruptSettings se o destino existe e nao e JSON valido.
    """
    cur = read_json(path, strict=True)
    scripts = framework_scripts(gates)
    merged, kept = merge_hooks(cur.get("hooks") or {}, hooks, scripts)
    if _cmp_key(cur.get("hooks") or {}) == _cmp_key(merged):
        if not quiet:
            print(f"[wire_gates] ja wirado: {path}")
        return False
    _rotate_backup(path)
    new = dict(cur)
    new["hooks"] = merged
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(new, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)
    if not quiet:
        n = sum(len(v) for v in hooks.values())
        extra = f" · {kept} hook(s) do dono PRESERVADO(s)" if kept else ""
        print(f"[wire_gates] wiring aplicada: {path} ({n} gate(s){extra})")
    return True


def mirror_assets(quiet=False):
    """Espelha skills/agents/workflows p/ ~/.claude (o que o sync-global.ps1 fazia, em Python)."""
    home = os.path.join(os.path.expanduser("~"), ".claude")
    pairs = [(os.path.join(ROOT, "_shared"), os.path.join(home, "skills")),
             (os.path.join(ROOT, ".agent", "skills"), os.path.join(home, "skills")),
             (os.path.join(ROOT, ".claude", "agents"), os.path.join(home, "agents")),
             (os.path.join(ROOT, ".agent", "workflows"), os.path.join(home, "workflows"))]
    n, seen, colisoes = 0, {}, []
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
                    # QA ADR-101: `_shared/` e `.agent/skills/` caem no MESMO destino; sem isto
                    # o segundo copytree sobrescreve o primeiro em silencio.
                    key = os.path.normcase(os.path.join(dst, name))
                    if key in seen and seen[key] != src:
                        colisoes.append(f"{name} ({seen[key]} x {src})")
                    seen[key] = src
                    shutil.copytree(s, os.path.join(dst, name), dirs_exist_ok=True)
                    n += 1
                elif name.endswith(".md"):
                    shutil.copy2(s, os.path.join(dst, name))
                    n += 1
            except (OSError, shutil.Error):
                continue
    if colisoes and not quiet:
        print(f"[wire_gates] AVISO colisao de nome no espelho ({len(colisoes)}): "
              f"{'; '.join(colisoes[:3])} — o ultimo venceu. Renomeie para desambiguar.")
    if not quiet:
        print(f"[wire_gates] assets espelhados p/ ~/.claude ({n} item(s))")
    return n


def _diff_detail(have, want, scripts):
    """DIZ o que diverge — chave por chave. Diagnostico que so conta gates e enganoso."""
    faltando, sobrando = [], []
    for ev, blocks in want.items():
        keys = {_cmp_key({ev: [b]}) for b in (have.get(ev) or [])}
        for b in blocks:
            if _cmp_key({ev: [b]}) not in keys:
                st = (b.get("hooks") or [{}])[0].get("statusMessage") or ev
                faltando.append(f"{ev}/{st}")
    for ev, blocks in have.items():
        keys = {_cmp_key({ev: [b]}) for b in (want.get(ev) or [])}
        for b in blocks:
            if _block_is_ours(b, scripts) and _cmp_key({ev: [b]}) not in keys:
                st = (b.get("hooks") or [{}])[0].get("statusMessage") or ev
                sobrando.append(f"{ev}/{st}")
    return faltando, sobrando


def diagnose(gates):
    """Compara disco x manifesto nos dois escopos. Retorna (ok, linhas).

    QA ADR-101: comparava `have == want` cru, o que (a) acusava divergencia por case do drive e
    (b) acusava divergencia sempre que o dono tivesse hook proprio — porque hook do dono nao
    esta no manifesto. Agora compara o que SERIA escrito (merge) e NOMEIA a diferenca.
    """
    home = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
    local = os.path.join(ROOT, ".claude", "settings.json")
    scripts = framework_scripts(gates)
    want_local = build_hooks(gates, "framework")
    want_global = build_hooks(gates, "both", base=ROOT)
    lines, ok = [], True
    for label, path, want in (("projeto (framework)", local, want_local),
                              ("global (~/.claude)", home, want_global)):
        try:
            have = read_json(path, strict=True).get("hooks") or {}
        except CorruptSettings as e:
            ok = False
            lines.append(f"  CORROMPIDO {label}: {e} -> conserte o JSON A MAO "
                         f"(nao sobrescrevo: perderia suas outras chaves)")
            continue
        merged, kept = merge_hooks(have, want, scripts)
        n_have = sum(len(v) for v in have.values())
        n_want = sum(len(v) for v in want.values())
        nota = f" · {kept} hook(s) seu(s) preservado(s)" if kept else ""
        if _cmp_key(have) == _cmp_key(merged):
            lines.append(f"  OK   {label}: {n_have} gate(s) — em sincronia com o manifesto{nota}")
        else:
            ok = False
            faltando, sobrando = _diff_detail(have, want, scripts)
            causa = []
            if faltando:
                causa.append(f"faltam {len(faltando)}: {', '.join(faltando[:4])}")
            if sobrando:
                causa.append(f"obsoletos {len(sobrando)}: {', '.join(sobrando[:4])}")
            lines.append(f"  DIVERGE {label}: disco={n_have} x manifesto={n_want} "
                         f"({'; '.join(causa) or 'conteudo do comando difere'}){nota}")
            lines.append(f"           -> `python tools/wire_gates.py "
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
    try:
        if args.install:
            write_settings(os.path.join(ROOT, ".claude", "settings.json"),
                           build_hooks(gates, "framework"), gates, args.quiet)
        if args.install_global:
            mirror_assets(args.quiet)
            changed = write_settings(
                os.path.join(os.path.expanduser("~"), ".claude", "settings.json"),
                build_hooks(gates, "both", base=ROOT), gates, args.quiet)
            if changed and not args.quiet:
                print("[wire_gates] gates globais re-afirmados — todo projeto herda os portateis.")
    except CorruptSettings as e:
        # Fail-closed DECLARADO: sobrescrever um settings.json corrompido apagaria as chaves
        # do dono (permissions/model/env). Ele conserta o JSON; nos nao adivinhamos.
        print(f"[wire_gates] ABORTADO — {e}\n"
              f"             conserte o JSON a mao e rode de novo (nao sobrescrevo por cima).",
              file=sys.stderr)
        return 1
    if not (args.install or args.install_global):
        ap.print_help()
        rc = 2
    return rc


if __name__ == "__main__":
    sys.exit(main())
