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


# [QA rodada 2] fixtures da guarda de ponteiro morto. As crases sao montadas em runtime porque
# payload com crase nao sobrevive a um shell — licao ja registrada neste repo.
_CRASE = chr(96)
_FENCE = _CRASE * 3
EXEMPLO_EM_BLOCO = (
    "\n" + _FENCE + "\nexemplo: " + _CRASE + ".agent/rules/98-so-ilustracao.md" + _CRASE
    + "\n" + _FENCE + "\n")
PONTEIRO_FORA_DO_BLOCO = (
    "\nDetalhe real: " + _CRASE + ".agent/rules/97-fora-do-bloco.md" + _CRASE + ".\n")


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
        # [ADR-111] a guarda de ponteiro morto: fixture cita uma regra que nao existe -> tem de
        # reprovar. Sem esta prova, a guarda seria mais uma promessa nao verificada — que e'
        # exatamente a classe que este repo mede.
        write_fixture(d)
        os.makedirs(os.path.join(d, ".agent", "rules"), exist_ok=True)
        with open(os.path.join(d, "CLAUDE.md"), "a", encoding="utf-8") as f:
            f.write("\nDetalhe: `.agent/rules/99-regra-que-nao-existe.md`.\n")
        if not any("ponteiro morto" in i for i in crp.audit(d)):
            fails.append("NAO pegou: ponteiro para `.agent/rules/` inexistente (guarda ADR-111)")
        # e com o arquivo no lugar, para de reclamar
        with open(os.path.join(d, ".agent", "rules", "99-regra-que-nao-existe.md"), "w",
                  encoding="utf-8") as f:
            f.write("# regra de fixture\n")
        if any("ponteiro morto" in i for i in crp.audit(d)):
            fails.append("falso positivo: ponteiro com arquivo existente foi acusado de morto")
        # [QA rodada 2, 19/08/2026] a supressao de blocos de codigo na guarda de ponteiro morto
        # so era verdade porque alguem testou a mao — e o proprio critico apontou que reverter o
        # re.sub amanha nao reprovaria nada. Ponteiro citado DENTRO de bloco de codigo e'
        # ilustracao e nao pode reprovar; FORA do bloco, continua sendo promessa e reprova.
        write_fixture(d)
        with open(os.path.join(d, 'CLAUDE.md'), 'a', encoding='utf-8') as f:
            f.write(EXEMPLO_EM_BLOCO)
        if any('ponteiro morto' in i for i in crp.audit(d)):
            fails.append('falso positivo: ponteiro dentro de bloco de codigo tratado como promessa')
        with open(os.path.join(d, 'CLAUDE.md'), 'a', encoding='utf-8') as f:
            f.write(PONTEIRO_FORA_DO_BLOCO)
        if not any('ponteiro morto' in i for i in crp.audit(d)):
            fails.append('NAO pegou: ponteiro morto FORA do bloco, logo apos um bloco de codigo')
        write_fixture(d)  # restaura
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
