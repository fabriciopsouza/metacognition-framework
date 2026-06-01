#!/usr/bin/env python3
"""check_regulatory_coverage.py — meta-linter de cobertura da denylist regulada (ADR-043).

A `agnostic-denylist.txt` é NÃO-EXAUSTIVA por design. Este meta-linter (advisory, fail-soft) mapeia
FAMÍLIAS reguladas comuns e avisa quais ainda NÃO têm representante na denylist — ajuda o mantenedor a
manter a lista ampla SEM jamais prometer exaustividade (o aviso "não-exaustiva" permanece).

NÃO é gate de bloqueio: por default exit 0 (advisory). Com `--strict`, exit = nº de famílias sem
representante (uso programático/CI opcional). NÃO viola agnosticismo: opera sobre a denylist (tools/,
a NEGATIVA), não sobre o núcleo.

Uso:
    python tools/check_regulatory_coverage.py            # relatório advisory (exit 0)
    python tools/check_regulatory_coverage.py --strict   # exit = nº de famílias descobertas
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DENYLIST = os.path.join(ROOT, "tools", "agnostic-denylist.txt")

# Família regulada -> tokens representativos (substring case-insensitive procurada nas linhas da denylist).
# Cobertura = >=1 token da família presente. Lista de FAMÍLIAS é editável (e também não-exaustiva).
FAMILIES = {
    "privacidade/dados-pessoais": ["LGPD", "GDPR", "HIPAA"],
    "farma/GxP/qualidade-regulada": ["GAMP", "GxP", "ANVISA", "FDA", "CFR", "ALCOA"],
    "saúde/dispositivos/laboratório": ["13485", "CLIA"],
    "financeiro/contábil": ["SOX", "Sarbanes", "BACEN", "Basel"],
    "segurança-da-informação": ["27001", "SOC", "NIST"],
    "governança-de-TI/serviço": ["COBIT", "ITIL"],
    "qualidade-geral": ["9001"],
    "pagamentos": ["PCI"],
    "setorial-energia-etc": ["ANP"],
}

DISCLAIMER = ("AVISO: esta verificação é advisory e a denylist é NÃO-EXAUSTIVA por design — "
              "surgem normas novas; o linter REDUZ, não ELIMINA o vazamento (qa-critic semântico é o backstop).")


def load_denylist_text(path=DENYLIST):
    out = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if line and not line.startswith("#"):
                out.append(line)
    return "\n".join(out)


def coverage(deny_text=None):
    """Retorna (cobertas, descobertas) — listas de nomes de família."""
    text = (deny_text if deny_text is not None else load_denylist_text()).upper()
    cobertas, descobertas = [], []
    for fam, tokens in FAMILIES.items():
        if any(t.upper() in text for t in tokens):
            cobertas.append(fam)
        else:
            descobertas.append(fam)
    return cobertas, descobertas


def main(argv):
    strict = "--strict" in argv
    cobertas, descobertas = coverage()
    print("# Cobertura regulada da denylist (advisory — ADR-043)")
    for fam in cobertas:
        print(f"  OK     {fam}")
    for fam in descobertas:
        print(f"  FALTA  {fam}  (sem representante na denylist; considere adicionar)")
    print("-" * 50)
    print(f"{len(cobertas)}/{len(FAMILIES)} famílias com representante.")
    print(DISCLAIMER)
    if strict:
        return len(descobertas)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
