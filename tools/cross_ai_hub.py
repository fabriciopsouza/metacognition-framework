#!/usr/bin/env python3
"""cross_ai_hub.py — tooling do HUB privado cross-IA (ADR-069). Mecaniza o que hoje e doutrina:
scan (descoberta no boot), manifest (deriva p/ o cross_ai_gate), deposit (publica handoff validado).

ISOLAMENTO POR IA (ADR-069, ordem do dono "vc nao mexe em nada gemini"): eu (claude-master) so
escrevo no MEU outbox (docs/_private/cross-ai/outbox/) e DEPOSITO no hub via PR no MEU branch.
NUNCA escrevo/comito no repo da outra IA. Este tool nunca toca o repo gemini — so o hub (neutro,
compartilhado) e o meu outbox. A outra IA le o hub, critica e implementa NO REPO DELA.

Subcomandos:
  scan <hubdir> --me <id> [--seen <f>]   handoffs abertos p/ mim, nao-vistos (file-first do boot).
                                         ZERO-DEP (so campos planos: to/status/report_id).
  manifest <hubdir> [out.json]           glob inbox/** -> manifest.json p/ o cross_ai_gate (usa PyYAML).
  gate <hubdir>                          roda cross_ai_gate sobre o manifest derivado (anti-loop).
  deposit <msg.md> <hubdir>              valida + roda gate + copia p/ inbox/AAAA/MM/DD (routing por date).

Saida (exit): 0 ok; 2 violacao (gate); 1 erro de uso/IO.
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
REQUIRED = ("schema_version", "report_id", "topic_fingerprint", "thread_id",
            "from", "to", "date", "status", "kind", "round")


def _split_frontmatter(text):
    """Devolve o bloco YAML entre o 1o par de '---'. None se ausente."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    return m.group(1) if m else None


def parse_flat(text):
    """Parser ZERO-DEP dos campos PLANOS do frontmatter (escalares + listas inline [a,b]).
    Suficiente p/ scan/routing (to/status/report_id/date/from/kind). Ignora blocos aninhados
    (claims/verdict_per_claim) — esses sao p/ o manifest, que usa PyYAML."""
    block = _split_frontmatter(text)
    if block is None:
        return {}
    out = {}
    for line in block.split("\n"):
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)  # so topo (sem indentacao)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "":
            continue  # bloco aninhado: fora do escopo plano
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            out[key] = [x.strip().strip('"').strip("'") for x in inner.split(",")] if inner else []
        else:
            out[key] = val.strip().strip('"').strip("'")
    return out


def _iter_inbox(hubdir):
    inbox = os.path.join(hubdir, "inbox")
    for dp, _dn, fns in os.walk(inbox):
        for fn in sorted(fns):
            if fn.endswith(".md"):
                yield os.path.join(dp, fn)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def scan(hubdir, me, seen_path):
    """Lista handoffs abertos p/ `me` (ou 'all'), status open, report_id nao em .cross-ai-seen.json.
    Leitura e automatica; AGIR exige passar pelo qa-critic (ADR-011) — este tool so DESCOBRE."""
    seen = set()
    if seen_path and os.path.isfile(seen_path):
        try:
            seen = set(json.loads(_read(seen_path)).get("seen", []))
        except Exception:
            seen = set()
    novos = []
    for path in _iter_inbox(hubdir):
        fm = parse_flat(_read(path))
        to = fm.get("to") or []
        if isinstance(to, str):
            to = [to]
        if fm.get("status") != "open":
            continue
        if not (me in to or "all" in to):
            continue
        rid = fm.get("report_id")
        if rid in seen:
            continue
        novos.append({"report_id": rid, "from": fm.get("from"), "kind": fm.get("kind"),
                      "thread_id": fm.get("thread_id"), "path": path})
    return novos, seen


def build_manifest(hubdir):
    """manifest.json p/ o cross_ai_gate: cada msg do inbox vira um item com o frontmatter COMPLETO
    (inclui claims/verdict_per_claim aninhados). Usa PyYAML (dep operacional do hub, nao do nucleo)."""
    try:
        import yaml
    except Exception:
        print("manifest/gate exigem PyYAML (dep operacional do hub). `pip install pyyaml`.", file=sys.stderr)
        raise
    messages = []
    for path in _iter_inbox(hubdir):
        block = _split_frontmatter(_read(path))
        if block is None:
            continue
        fm = yaml.safe_load(block) or {}
        messages.append(fm)
    return {"schema_version": "1.0", "messages": messages}


def _validate_required(fm):
    missing = [k for k in REQUIRED if k not in fm or fm.get(k) in (None, "")]
    return missing


def deposit(msgpath, hubdir):
    """Valida frontmatter requerido + roda o cross_ai_gate (anti-loop) sobre o inbox + esta msg,
    e SE passar copia p/ inbox/AAAA/MM/DD (date-shard, ADR-069). Routing pela `date` do frontmatter."""
    import cross_ai_gate
    text = _read(msgpath)
    flat = parse_flat(text)
    missing = _validate_required(flat)
    if missing:
        print(f"frontmatter incompleto: faltam {missing}", file=sys.stderr)
        return 1
    date = str(flat.get("date", ""))
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", date)
    if not m:
        print(f"date invalida no frontmatter: {date!r} (esperado AAAA-MM-DD)", file=sys.stderr)
        return 1
    # anti-loop: monta manifest do inbox + esta msg e roda o gate ANTES de publicar.
    man = build_manifest(hubdir)
    try:
        import yaml
        man["messages"].append(yaml.safe_load(_split_frontmatter(text)) or {})
    except Exception:
        return 1
    violations = cross_ai_gate.validate(man)
    if violations:
        print(f"[cross-ai-gate] deposit BARRADO — {len(violations)} violacao(oes):", file=sys.stderr)
        for v in violations:
            print("  -", v, file=sys.stderr)
        return 2
    dest_dir = os.path.join(hubdir, "inbox", m.group(1), m.group(2), m.group(3))
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(msgpath))
    shutil.copyfile(msgpath, dest)
    print(f"depositado: {dest} (gate verde). Publique via PR no SEU branch (nunca no repo da outra IA).")
    return 0


def _resolve_hub_path():
    """Resolve o path do hub clonado por config (ordem: env -> ~/.claude -> repo .agent).
    Retorna o dir existente ou None. Permite boot-scan sem hardcode (agnostico de maquina)."""
    cand = []
    env = os.environ.get("CROSS_AI_HUB")
    if env:
        cand.append(env)
    for cfg in (os.path.expanduser("~/.claude/cross-ai-hub-path.txt"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             ".agent", "cross-ai-hub-path.txt")):
        try:
            if os.path.isfile(cfg):
                line = open(cfg, encoding="utf-8-sig").read().strip()
                if line and not line.startswith("#"):
                    cand.append(os.path.expanduser(line))
        except Exception:
            pass
    for c in cand:
        if c and os.path.isdir(c):
            return c
    return None


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd = argv[1]
    rest = [a for a in argv[2:] if not a.startswith("--")]

    def opt(name, default=None):
        return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default

    if cmd == "scan":
        if not rest:
            print("uso: scan <hubdir> --me <id> [--seen <f>]", file=sys.stderr)
            return 1
        me = opt("--me", "claude-master")
        seen_path = opt("--seen")
        novos, _ = scan(rest[0], me, seen_path)
        if not novos:
            print(f"📭 nenhum handoff aberto novo p/ {me}.")
        else:
            print(f"📥 {len(novos)} handoff(s) aberto(s) p/ {me} (ler != aceitar — passe pelo qa-critic):")
            for n in novos:
                print(f"  - {n['report_id']} de {n['from']} ({n['kind']}) :: {n['path']}")
        return 0

    if cmd == "boot-scan":
        # Descoberta AUTOMATICA de handoffs no boot (file-first, ADR-069). Resolve o path do hub
        # clonado por config -> nunca silencioso: anuncia handoffs OU anuncia que o hub nao esta
        # configurado (com como configurar). Criterio do item 4: "boot anuncia handoffs".
        me = opt("--me", "claude-master")
        hubdir = _resolve_hub_path()
        if not hubdir:
            print("📭 [cross-ai boot-scan] hub nao configurado. Para ativar a descoberta de handoffs:")
            print("   - clone o hub privado (metacognition-hub) e aponte o path em UMA destas fontes:")
            print("     env CROSS_AI_HUB=<dir>  |  ~/.claude/cross-ai-hub-path.txt  |  .agent/cross-ai-hub-path.txt")
            return 0
        if not os.path.isdir(os.path.join(hubdir, "inbox")):
            print(f"📭 [cross-ai boot-scan] hub configurado ({hubdir}) mas sem inbox/ — clone/sync pendente.")
            return 0
        seen_path = opt("--seen") or os.path.join(hubdir, ".cross-ai-seen.json")
        novos, _ = scan(hubdir, me, seen_path)
        if not novos:
            print(f"📭 [cross-ai boot-scan] {hubdir}: nenhum handoff aberto novo p/ {me}.")
        else:
            print(f"📥 [cross-ai boot-scan] {len(novos)} handoff(s) aberto(s) p/ {me} "
                  f"(ler != aceitar — passe pelo qa-critic, ADR-011):")
            for n in novos:
                print(f"  - {n['report_id']} de {n['from']} ({n['kind']}) :: {n['path']}")
        return 0

    if cmd == "manifest":
        if not rest:
            print("uso: manifest <hubdir> [out.json]", file=sys.stderr)
            return 1
        man = build_manifest(rest[0])
        if len(rest) > 1:
            with open(rest[1], "w", encoding="utf-8") as fh:
                json.dump(man, fh, ensure_ascii=False, indent=2)
            print(f"manifest com {len(man['messages'])} msg(s) -> {rest[1]}")
        else:
            print(json.dumps(man, ensure_ascii=False, indent=2))
        return 0

    if cmd == "gate":
        if not rest:
            print("uso: gate <hubdir>", file=sys.stderr)
            return 1
        import cross_ai_gate
        violations = cross_ai_gate.validate(build_manifest(rest[0]))
        if not violations:
            print("[cross-ai-gate] PASS — terminacao garantida.")
            return 0
        print(f"[cross-ai-gate] FAIL — {len(violations)} violacao(oes):")
        for v in violations:
            print("  -", v)
        return 2

    if cmd == "deposit":
        if len(rest) < 2:
            print("uso: deposit <msg.md> <hubdir>", file=sys.stderr)
            return 1
        return deposit(rest[0], rest[1])

    print(f"subcomando desconhecido: {cmd}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
