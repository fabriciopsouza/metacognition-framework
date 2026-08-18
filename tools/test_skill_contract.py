#!/usr/bin/env python3
"""Canario do CONTRATO DE SKILL (ADR-013) — liga um validador que estava dormente.

GAP fechado: `tools/validate_skills.py` existia, passava, e **nada o executava** — nem o
`ci.yml`, nem o `run_canaries.py`. Um validador de contrato que ninguem invoca e' documentacao
com sintaxe colorida: nao impede nada. Medido em 2026-08-18, ao migrar o passivo do ADR-106
(a capacidade `skill-contract` nao declarava `enforcement` porque nao havia canario nenhum).

Prova as duas direcoes, que e' o que torna a capacidade PROVAVEL (ADR-106):
  (a) o conjunto REAL de skills do repo passa;
  (b) frontmatter quebrado e' PEGO — fixtures sinteticas para cada classe de violacao.
Sem (b), este canario seria indistinguivel de um canario cego: varreria, nao acharia nada e
ficaria verde, exatamente como os 8 casos `mechanism == test` migrados no v1.88.0.

Uso: python tools/test_skill_contract.py   (exit 0 PASS; 1 se falha)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import validate_skills as vs  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _erros(frontmatter, schema):
    """Roda o MESMO caminho do validador real: parse do frontmatter + schema."""
    data, err = vs.extract_frontmatter(frontmatter)
    if err:
        return [err]
    return vs.validate_against_schema(data, schema)


def autoteste(schema):
    """Fixtures que este canario e OBRIGADO a acertar."""
    falhas = []
    # Fixture VALIDA: precisa carregar o contrato INTEIRO (8 campos obrigatorios). Escrever
    # so `name`+`description` fazia o caso (a) reprovar por incompletude e mascarar o que ele
    # existe para medir — falso-positivo do proprio canario, pego na 1a execucao.
    bom = ("---\n"
           "name: skill-de-teste\n"
           "description: Skill sintetica usada so pelo canario do contrato.\n"
           "role_order: null\n"
           "consumes: []\n"
           "produces: [artefato-de-teste]\n"
           "pass_criteria: o canario roda e devolve verde\n"
           "confidence_required: false\n"
           "shared_refs: []\n"
           "---\n\n# Corpo\n")

    if _erros(bom, schema):
        falhas.append(f"skill VALIDA foi reprovada (falso-positivo): {_erros(bom, schema)}")

    sem_fm = "# Sem frontmatter nenhum\n\ntexto\n"
    if not _erros(sem_fm, schema):
        falhas.append("arquivo SEM frontmatter passou — o contrato deixou de existir")

    fm_aberto = "---\nname: x\ndescription: y\n\n# esqueceu de fechar\n"
    if not _erros(fm_aberto, schema):
        falhas.append("frontmatter NAO FECHADO passou — parse aceita documento truncado")

    sem_name = ("---\n"
                "description: Skill sem o campo name, que e obrigatorio.\n"
                "---\n\n# Corpo\n")
    if not _erros(sem_name, schema):
        falhas.append("skill sem `name` passou — campo obrigatorio deixou de ser exigido")

    sem_desc = "---\nname: skill-sem-descricao\n---\n\n# Corpo\n"
    if not _erros(sem_desc, schema):
        falhas.append("skill sem `description` passou — e' o campo que decide o auto-trigger")
    return falhas


def main():
    schema = vs.load_schema()
    falhas_canario = autoteste(schema)

    # (a) o conjunto REAL do repo — o validador rodando pela primeira vez dentro da suite
    reais, ruins = 0, []
    for path in vs.glob_default():
        reais += 1
        try:
            texto = open(path, encoding="utf-8-sig").read()
        except OSError as e:
            ruins.append(f"{os.path.relpath(path, ROOT)}: ilegivel ({e})")
            continue
        for e in _erros(texto, schema):
            ruins.append(f"{os.path.relpath(path, ROOT)}: {e}")

    print(f"skill-contract: {reais} skill(s) do repo validadas — "
          f"{'OK' if not ruins else 'FAIL'}")
    for r in ruins:
        print("  -", r)
    print(f"auto-teste do validador (5 fixtures) — {'OK' if not falhas_canario else 'FAIL'}")
    for f in falhas_canario:
        print("  -", f)
    print("-" * 50)
    if ruins or falhas_canario:
        print(f"RESULTADO: FAIL ({len(ruins)} skill(s) fora do contrato, "
              f"{len(falhas_canario)} falha(s) do proprio validador)")
        return 1
    print("RESULTADO: PASS (contrato de skill vigente; validador provado contra fixture)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
