#!/usr/bin/env python3
"""Canario do check_rules_parity (E3 do plano anti-bypass): prova que o detector de DRIFT das 4 regras
invioláveis (a) PASSA no repo real e (b) PEGA cada classe de drift em fixtures sinteticas. Sem (b), o
linter poderia estar quebrado e ninguem saberia (false-PASS). Fail-closed.

Uso: python tools/test_rules_parity.py   (exit 0 PASS; 1 se falha)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_rules_parity as crp  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GOOD_CLAUDE = """# CLAUDE.md

## Regras invioláveis (de _shared/, não redefinir)
1. Classificar afirmação: CONFIRMADO | INFERIDO | DESCONHECIDO.
2. Anti-rename: não renomear nome aprovado sem ADR.
3. File-first: ler/inspecionar antes de assumir.
4. NÃO SEI direto — nunca inventar.

## Outro
"""

GOOD_AF = """# AGENT-FRAMEWORK

## 6. Princípios
só as 4 regras invioláveis seguem ativas — todas referenciando
`_shared/` (classificação, anti-rename, file-first, NÃO SEI/nunca-inventar).

## Outro
"""

GOOD_AGENTS = """# AGENTS

## Regras sempre ativas
Ver .agent/rules/ (todas referenciam _shared/).

## Outro
"""


def write_fixture(d, claude=GOOD_CLAUDE, af=GOOD_AF, agents=GOOD_AGENTS):
    for name, content in (("CLAUDE.md", claude), ("AGENT-FRAMEWORK.md", af), ("AGENTS.md", agents)):
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write(content)


def main():
    fails = []

    # (a) repo REAL passa (o digesto/referencia/delegacao estao em sync)
    real = crp.audit(ROOT)
    if real:
        fails.append(f"repo real deveria PASSAR mas reportou drift: {real}")

    with tempfile.TemporaryDirectory() as d:
        # (b0) fixture boa = 0 issues (sanidade do fixture)
        write_fixture(d)
        if crp.audit(d):
            fails.append(f"fixture BOA reportou drift indevidamente: {crp.audit(d)}")

        # (b1) CLAUDE.md perde a 4a regra (anti-alucinacao) -> drift (contagem + conceito)
        claude3 = GOOD_CLAUDE.replace("4. NÃO SEI direto — nunca inventar.\n", "")
        write_fixture(d, claude=claude3)
        if not crp.audit(d):
            fails.append("NAO pegou: CLAUDE.md com 3 regras (anti-alucinacao removida)")
        write_fixture(d)  # restaura

        # (b2) AGENT-FRAMEWORK cita contagem divergente (3 != 4 do CLAUDE)
        af_bad = GOOD_AF.replace("4 regras invioláveis", "3 regras invioláveis")
        write_fixture(d, af=af_bad)
        if not crp.audit(d):
            fails.append("NAO pegou: AGENT-FRAMEWORK com contagem divergente (3 vs 4)")
        write_fixture(d)

        # (b3) AGENTS redefine sem referenciar a SSoT -> risco dual-authority
        agents_bad = "# AGENTS\n\n## Regras sempre ativas\n1. classificar tudo inline aqui.\n\n## Outro\n"
        write_fixture(d, agents=agents_bad)
        if not crp.audit(d):
            fails.append("NAO pegou: AGENTS.md sem referencia a SSoT (dual-authority)")
        write_fixture(d)

    print(f"repo real PASS; 3 classes de drift pegas em fixture — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (linter pega drift e nao da falso-positivo no repo real)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
