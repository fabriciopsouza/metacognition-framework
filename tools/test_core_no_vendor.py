#!/usr/bin/env python3
"""Canário de pureza do NÚCLEO: nenhum nome de PRODUTO/VENDOR externo no conteúdo operativo do
núcleo (regression-guard do "este repo não pode ter domínios/produtos" — P12, ADR-010/020).

O linter `check_core_agnostic.py` barra NORMAS regulatórias (ANVISA/ANP/…). Este canário é
complementar: barra **nomes de produto externo** (ex.: vendor de IA integrado por recast) no que o
agente LÊ PARA AGIR (`_shared/`, `.agent/skills|rules|workflows`, e os arquivos-raiz do roteador).
A PROVENIÊNCIA (de onde a técnica veio) vive nos **ADRs** (`docs/`, fora deste escopo) — por isso
referências a *arquivos de ADR* (ex.: `docs/adr/085-...-bmad-...md`) são EXCLUÍDAS antes do check:
citar o ADR que registra a integração é legítimo; nomear o produto na prosa operativa não é.

Exceção auditável: linha com `vendor-ok:allow` (estilo `# noqa`, exige justificativa visível).

Uso: python tools/test_core_no_vendor.py   (exit 0 PASS; 1 se vazou nome de produto)
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENTINEL = "vendor-ok:allow"

# Escopo = NÚCLEO operativo (o que o agente carrega para agir). Fora: docs/ (ADRs citam proveniência),
# tools/ (infra; docstrings citam fonte como comentário de código), capabilities.json (dado/metadado).
CORE_GLOBS = ["_shared/**/*.md", ".agent/skills/**/*.md", ".agent/rules/**/*.md", ".agent/workflows/**/*.md"]
# capabilities.json incluido (metadado do repo) — a exclusao de ADR-path cobre os campos `adr`
# que apontam p/ arquivos de ADR com 'bmad' no nome; tags/titulos NAO podem nomear produto (qa-critic).
CORE_FILES = ["AGENT-FRAMEWORK.md", "CLAUDE.md", "AGENTS.md", "capabilities.json"]

# Vendores externos integrados (slugs inequívocos). NÃO usar acrônimos ambíguos (CIS/TEA) — falso-positivo.
VENDOR = re.compile(r"bmad|creative-intelligence-suite|game-dev-studio", re.IGNORECASE)
# Referências a ARQUIVO de ADR (proveniência legítima) — removidas antes do check.
ADR_PATH = re.compile(r"(docs/adr/)?\b0\d\d-[a-z0-9-]+\.md\b", re.IGNORECASE)


def targets():
    files = []
    for pat in CORE_GLOBS:
        files.extend(glob.glob(os.path.join(ROOT, pat), recursive=True))
    for f in CORE_FILES:
        p = os.path.join(ROOT, f)
        if os.path.isfile(p):
            files.append(p)
    return sorted(set(files))


def main():
    leaks = []
    files = targets()
    for path in files:
        try:
            lines = open(path, encoding="utf-8-sig").read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        rel = os.path.relpath(path, ROOT)
        for n, line in enumerate(lines, 1):
            if SENTINEL in line:
                continue
            scrub = ADR_PATH.sub("", line)  # remove refs a arquivo de ADR (proveniência ok)
            m = VENDOR.search(scrub)
            if m:
                leaks.append(f"{rel}:{n}: produto '{m.group(0)}' no conteúdo operativo -> {line.strip()[:90]}")

    print(f"core-no-vendor: {len(files)} arquivos de núcleo varridos; nome de produto externo — "
          f"{'OK (nenhum)' if not leaks else 'FAIL'}")
    for lk in leaks:
        print("  -", lk)
    print("-" * 50)
    print("RESULTADO:", "PASS (núcleo product-free; proveniência só nos ADRs)"
          if not leaks else f"FAIL ({len(leaks)} vazamento(s) de produto)")
    return 1 if leaks else 0


if __name__ == "__main__":
    sys.exit(main())
