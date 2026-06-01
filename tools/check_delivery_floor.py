#!/usr/bin/env python3
"""check_delivery_floor.py — PISO de validação da entrega premium (ADR-050). PREMIUM-only.

Mecaniza a doutrina "runbook de validação SEMPRE" (prosa → gate; tese prosa→mecanismo do framework,
ADR-021/022/027). Varre a pasta de entrega e exige ao menos um artefato de **runbook de validação**
(nome casa `runbook` ou `valida(ç|c)`).

Default-OBRIGATÓRIO, não rígido: `--allow-skip "<motivo>"` registra uma **dispensa consciente**
(caso trivial) — nunca silenciosa (mesma flexibilidade do retrospective gate). Em domínio **regulado**
(`--regulated`, declarado pelo discovery — ADR-010/012 + high-stakes-gate) a dispensa **não vale**.

Uso:
    python tools/check_delivery_floor.py <pasta-entrega> [--allow-skip "motivo"] [--regulated]
Exit 0 = piso atendido (ou dispensa consciente registrada); 1 = runbook ausente sem dispensa válida.
"""
import argparse
import os
import re
import sys
import unicodedata

# Token EXATO (não substring): evita falso-positivo "invalidação"/"revalidação"/"avaliação" passarem
# como runbook (substring regex é armadilha — mesmo erro já pego em check_spec_depth).
RUNBOOK_TOKENS = {"runbook", "validacao", "validacoes", "validation", "validations"}
DOC_EXT = (".md", ".txt", ".pdf", ".docx", ".html")


def _tokens(name):
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii").lower()
    return {t for t in re.split(r"[^a-z0-9]+", name) if t}


def has_runbook(root):
    """Relpath de um runbook de validação na entrega (por TOKEN exato do nome), ou None."""
    for dp, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for fn in files:
            if fn.lower().endswith(DOC_EXT) and (_tokens(fn) & RUNBOOK_TOKENS):
                return os.path.relpath(os.path.join(dp, fn), root).replace(os.sep, "/")
    return None


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--allow-skip", metavar="MOTIVO", help="dispensa consciente (caso trivial; não vale em regulado)")
    ap.add_argument("--regulated", action="store_true", help="domínio regulado declarado: piso é inviolável")
    args = ap.parse_args(argv[1:])
    if not os.path.isdir(args.dir):
        print(f"pasta inexistente: {args.dir}", file=sys.stderr)
        return 2
    found = has_runbook(args.dir)
    if found:
        print(f"PASS: piso atendido — runbook de validação presente ({found}).")
        return 0
    if args.allow_skip and not args.regulated:
        print(f"PASS: runbook ausente, mas DISPENSA CONSCIENTE registrada — motivo: {args.allow_skip}")
        print("      (dispensa não-silenciosa; em domínio regulado seria bloqueada.)")
        return 0
    if args.regulated and args.allow_skip:
        print("FAIL: domínio REGULADO — a dispensa do runbook não vale. Gere o runbook de validação.")
        return 1
    print("FAIL: piso de validação não atendido — nenhum runbook de validação na entrega.")
    print("      Gere um (template docs/specs/_template-documentos/runbook-validacao.md) ou, em caso")
    print("      trivial, registre a dispensa consciente: --allow-skip \"motivo\".")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
