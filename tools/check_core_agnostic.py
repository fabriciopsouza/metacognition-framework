#!/usr/bin/env python3
"""Linter de agnosticismo do NÚCLEO (ADR-020, v1.20.0).

Enforcement EXECUTÁVEL do Princípio 12 (framework agnóstico de domínio) e da regra #5 do
qa-critic — que era PROSA e falhou >=2x (vazamentos de ALCOA+/ANP/... pegos pelo dono, nunca
auto-detectados; history.md ## Aprendizado 2026-05-29/30). Mesma tese da série v1.14.x ("da
prosa ao mecanismo") e mesmo padrão de ADR-013->validate_skills / ADR-015->effect-gate.

REGRA: nenhum identificador de norma/convenção regulatória de domínio (denylist) pode aparecer
no NÚCLEO OPERATIVO, EXCETO em linha portando o sentinela explícito `lint-agnostic:allow`
(estilo `# noqa` — exige justificativa visível em diff; é a única exceção, auditável).

ESCOPO (núcleo operativo agnóstico): _shared/**, .agent/skills/**, .agent/rules/**, .agent/workflows/**
(.md) + AGENT-FRAMEWORK.md, CLAUDE.md, AGENTS.md, README.md. FORA: docs/** (ADRs/specs/_intake discutem
domínio como exemplo/decisão), exemplos/** (aplicações de domínio), tools/** (infra, inclui este linter e
a denylist). CLAUDE.md lista rules/ e workflows/ como núcleo (qa-critic round 2 ADR-020): incluídos.

Uso:
    python tools/check_core_agnostic.py                 # varre o núcleo operativo
    python tools/check_core_agnostic.py <arquivo>...    # varre arquivos específicos (canário)

Exit 0 se limpo; exit 1 se houver vazamento. Sem dependências externas (só stdlib).
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DENYLIST_PATH = os.path.join(ROOT, "tools", "agnostic-denylist.txt")
SENTINEL = "lint-agnostic:allow"

# Núcleo operativo agnóstico (globs + arquivos-âncora). FORA: docs/, exemplos/, tools/.
CORE_GLOBS = [
    "_shared/**/*.md",
    ".agent/skills/**/*.md",
    ".agent/rules/**/*.md",
    ".agent/workflows/**/*.md",
]
CORE_FILES = ["AGENT-FRAMEWORK.md", "CLAUDE.md", "AGENTS.md", "README.md"]


def load_patterns():
    """Lê a denylist (uma regex por linha; # e vazias ignoradas). Retorna lista de (regex, fonte)."""
    pats = []
    with open(DENYLIST_PATH, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                pats.append((re.compile(line, re.IGNORECASE), line))
            except re.error as e:
                print(f"AVISO: padrao invalido na denylist ignorado: {line!r} ({e})", file=sys.stderr)
    return pats


def core_targets():
    files = []
    for pat in CORE_GLOBS:
        files.extend(glob.glob(os.path.join(ROOT, pat), recursive=True))
    for f in CORE_FILES:
        p = os.path.join(ROOT, f)
        if os.path.isfile(p):
            files.append(p)
    return sorted(set(files))


def scan_file(path, patterns):
    """Retorna lista de violacoes (linha_no, token, trecho)."""
    viol = []
    try:
        with open(path, encoding="utf-8-sig") as fh:
            lines = fh.readlines()
    except OSError as e:
        return [(0, "<erro-io>", str(e))]
    for n, line in enumerate(lines, 1):
        if SENTINEL in line:
            continue  # exceção explícita e auditável (ex.: a própria regra #5 que define a detecção)
        for rx, src in patterns:
            m = rx.search(line)
            if m:
                viol.append((n, m.group(0), line.strip()[:120]))
    return viol


def main(argv):
    patterns = load_patterns()
    if not patterns:
        print("nenhum padrao na denylist — nada a verificar", file=sys.stderr)
        return 1
    targets = argv[1:] if len(argv) > 1 else core_targets()
    if not targets:
        print("nenhum arquivo de nucleo encontrado", file=sys.stderr)
        return 1
    any_leak = False
    for path in targets:
        try:
            rel = os.path.relpath(path, ROOT)
        except ValueError:
            rel = path
        viol = scan_file(path, patterns)
        if viol:
            any_leak = True
            for (n, token, snippet) in viol:
                print(f"LEAK {rel}:{n}: norma de dominio '{token}' no nucleo -> {snippet}")
        else:
            print(f"OK   {rel}")
    print("-" * 40)
    if any_leak:
        print("RESULTADO: FAIL (vazamento de dominio no nucleo — Principio 12 / qa-critic regra #5)")
        print(f"           Corrija, ou — se for menção legítima — adicione o sentinela '{SENTINEL}' na linha com justificativa.")
        return 1
    print("RESULTADO: PASS (nucleo agnostico — sem normas de dominio hardcoded)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
