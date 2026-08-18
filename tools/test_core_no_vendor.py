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
import tempfile
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


def varrer(files, raiz):
    """Devolve a lista de vazamentos nos arquivos dados.

    Extraida de main() para que o AUTO-TESTE abaixo exercite a MESMA logica de deteccao
    contra fixtures sinteticas — se ele testasse uma copia, sabotar a original passaria.
    """
    leaks = []
    for path in files:
        try:
            lines = open(path, encoding="utf-8-sig").read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        rel = os.path.relpath(path, raiz)
        for n, line in enumerate(lines, 1):
            if SENTINEL in line:
                continue
            scrub = ADR_PATH.sub("", line)  # remove refs a arquivo de ADR (proveniencia ok)
            m = VENDOR.search(scrub)
            if m:
                leaks.append(f"{rel}:{n}: produto {m.group(0)!r} no conteudo operativo "
                             f"-> {line.strip()[:90]}")
    return leaks


def autoteste():
    """Fixtures que este canario e OBRIGADO a acertar — a prova de que ele nao esta cego.

    ADR-106: capacidade `fail-closed` declara a mutacao que a derruba. Este canario nao
    podia ser derrubado, porque `mechanism == test`: sabotar a deteccao o deixava VERDE
    (medido em 17/08/2026, `--provar --id core-no-vendor` recusou a prova com "continuou
    VERDE"). Com o auto-teste, esvaziar o VENDOR reprova aqui.

    Devolve a lista de falhas do proprio detector (vazia = detector integro).
    """
    falhas = []
    # 'bmad' abaixo e' DADO DE TESTE, nao conteudo operativo. tools/ esta fora do escopo
    # varrido (ver CORE_GLOBS), e as linhas levam o SENTINEL como cinto de seguranca caso
    # o escopo mude um dia.
    produto = "bmad"
    with tempfile.TemporaryDirectory(prefix="core-no-vendor-fx-") as td:
        def escrever(nome, conteudo):
            p = os.path.join(td, nome)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(conteudo)
            return p

        # (1) vazamento OBVIO -> TEM de ser pego. E' este caso que morre se o detector cegar.
        sujo = escrever("sujo.md", "# Skill qualquer" + chr(10) + "Use o metodo do " + produto + " aqui." + chr(10))
        if not varrer([sujo], td):
            falhas.append("fixture COM nome de produto nao foi pega — detector cego "
                          "(VENDOR vazio/quebrado?)")

        # (2) fixture LIMPA nao pode acusar: detector que acusa tudo nao serve para nada.
        limpo = escrever("limpo.md", "# Skill qualquer" + chr(10) + "Metodo agnostico, sem produto." + chr(10))
        if varrer([limpo], td):
            falhas.append("fixture LIMPA foi acusada — falso-positivo do detector")

        # (3) a excecao auditavel continua valendo (senao vira ruido e alguem a desliga).
        isento = escrever("isento.md", "Cita " + produto + " com justificativa. " + SENTINEL + chr(10))
        if varrer([isento], td):
            falhas.append("linha com " + SENTINEL + " foi acusada — excecao auditavel parou de valer")

        # (4) referencia a ARQUIVO de ADR e proveniencia legitima -> nao pode acusar.
        adr = escrever("adr.md", "Ver docs/adr/085-integracao-" + produto + "-por-recast.md" + chr(10))
        if varrer([adr], td):
            falhas.append("referencia a arquivo de ADR foi acusada — proveniencia legitima barrada")
    return falhas


def main():
    files = targets()
    leaks = varrer(files, ROOT)
    falhas_canario = autoteste()

    print(f"core-no-vendor: {len(files)} arquivos de nucleo varridos; nome de produto externo — "
          f"{'OK (nenhum)' if not leaks else 'FAIL'}")
    for lk in leaks:
        print("  -", lk)
    print(f"auto-teste do detector (4 fixtures: suja/limpa/isenta/ADR) — "
          f"{'OK' if not falhas_canario else 'FAIL'}")
    for f in falhas_canario:
        print("  -", f)
    print("-" * 50)
    if leaks or falhas_canario:
        print(f"RESULTADO: FAIL ({len(leaks)} vazamento(s) de produto, "
              f"{len(falhas_canario)} falha(s) do proprio detector)")
        return 1
    print("RESULTADO: PASS (nucleo product-free; proveniencia so nos ADRs; "
          "detector provado contra fixture)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
