#!/usr/bin/env python3
"""context_budget.py — gate de ORCAMENTO DE CONTEXTO (prosa->mecanismo, pedido do dono 2026-06-08:
"usar doc-intake senao tokens vao embora; obrigatorio para todo contexto maior").

PROBLEMA mecanizado: ler uma fonte grande INTEIRA no contexto principal queima tokens — exatamente o
que `doc-intake` (ADR-029: parse deterministico -> chunks + sha256, proveniencia por trecho) evita.
A auto-deteccao do agente falha (admitido pelo claude-master E pelo premium em 2026-06-08): so usou
quando provocado (Principio 11 honesto). Este tool e o mecanismo: dada uma fonte, decide LER-INTEIRO
vs FRACIONAR-VIA-DOC-INTAKE por um limiar de tokens estimados.

LIMITE HONESTO (GAP-3, ADR-044): sem tokenizer real exposto ao agente, estima `chars/4`. E proxy
(±20-40%), nao contagem exata — declarado, nao mascarado.

ENFORCEMENT: onde a maquina permite hook, o `tools/hooks/context_budget_gate.py` (PreToolUse Read,
wirado no `.claude/settings.json`) ANUNCIA na hora da leitura grande (nao-bloqueante — "gates
anunciados"). Onde o hook nao roda (algumas maquinas com EDR/AAC que vetam — ex. a 9TRP7H4 com
Kaspersky; NEM TODA maquina tem), fica a doutrina no start-session + este tool chamavel sob demanda
(e pela discovery). NAO assumir veto de hook sem verificar a maquina.

CLI:
  python tools/context_budget.py <path> [--budget N]   exit 0 = cabe; exit 3 = FRACIONE (use doc_intake)
  python tools/context_budget.py <path> --json
"""
import argparse
import json
import os
import sys

DEFAULT_BUDGET_TOKENS = 6000   # ~24k chars: acima disso, fracionar compensa
CHARS_PER_TOKEN = 4

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def estimate_tokens(n_chars):
    return (n_chars + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN


def assess(path, budget_tokens=DEFAULT_BUDGET_TOKENS):
    """Retorna dict de decisao. Pasta = soma dos arquivos de texto."""
    paths = []
    if os.path.isdir(path):
        for r, _, fs in os.walk(path):
            for f in fs:
                paths.append(os.path.join(r, f))
    elif os.path.isfile(path):
        paths = [path]
    else:
        return {"path": path, "exists": False, "decision": "ERRO", "reason": "path inexistente"}

    total_chars = 0
    for p in paths:
        try:
            total_chars += len(open(p, encoding="utf-8-sig", errors="replace").read())
        except Exception:
            try:
                total_chars += os.path.getsize(p)
            except Exception:
                pass
    tokens = estimate_tokens(total_chars)
    over = tokens > budget_tokens
    return {
        "path": path,
        "exists": True,
        "n_files": len(paths),
        "chars": total_chars,
        "est_tokens": tokens,
        "budget_tokens": budget_tokens,
        "over_budget": over,
        "decision": "FRACIONAR" if over else "LER-INTEIRO",
        "reason": (f"~{tokens} tokens > orcamento {budget_tokens}: fracione via "
                   f"`python tools/doc_intake.py {path} --out manifest.json` e cite por chunk+sha"
                   if over else f"~{tokens} tokens <= orcamento {budget_tokens}: ler inteiro e OK"),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gate de orcamento de contexto (doc-intake p/ fontes grandes).")
    ap.add_argument("path")
    ap.add_argument("--budget", type=int, default=DEFAULT_BUDGET_TOKENS)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    r = assess(args.path, args.budget)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"[context-budget] {r['decision']} — {r.get('reason', r.get('reason'))}")
    if not r.get("exists"):
        return 1
    return 3 if r["over_budget"] else 0


if __name__ == "__main__":
    sys.exit(main())
