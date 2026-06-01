#!/usr/bin/env python3
"""Canário do gerador de documento executivo premium (ADR-050). PREMIUM-only (stripado do baseline).

Fixtures sintéticas e agnósticas: spec completa → valida + gera markdown com as seções; seção
obrigatória ausente → FAIL; **custo placeholder → renderizado como NÃO PREENCHIDO, nunca fabricado**
(invariante anti-fabricação). doc/pptx/pdf degradam se a lib faltar (não falham).

Uso: python tools/test_gen_exec_doc.py   (exit 0 PASS; 1 se gerar errado ou fabricar custo)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
try:
    import gen_exec_doc as g  # noqa
except Exception:
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("gen_exec_doc", os.path.join(ROOT, "tools", "gen_exec_doc.py"))
        g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
    except Exception as e:
        print(f"SKIP: gen_exec_doc.py indisponível (premium não distribuído neste pacote): {e}", file=sys.stderr)
        sys.exit(0)

SPEC_OK = """<!-- required: Proposta; Custo; Decisão / Aprovação -->
# Decisão Executiva (sintético)
## Proposta
Construir o produto X (flexível: GUI + CLI), conforme elicitado.
## Escopo
Módulos A e B; fora: integração externa.
## Custo
Esforço estimado: 3 incrementos; custo MAIOR que a baseline por incluir suíte de saída + auditoria.
## Trade-offs
Mais custo agora vs. menos retrabalho depois; premium vs. baseline.
## Alternativas
(1) baseline sem suíte de saída; (2) premium com documentos executivos.
## Decisão / Aprovação
Aprovar orçamento do incremento 1? [ ] sim [ ] não — aprovação do patrocinador pendente.
"""

# Custo como placeholder → deve virar NÃO PREENCHIDO (não inventar número)
SPEC_CUSTO_VAZIO = SPEC_OK.replace(
    "Esforço estimado: 3 incrementos; custo MAIOR que a baseline por incluir suíte de saída + auditoria.",
    "<preencher>")

SPEC_SEM_DECISAO = SPEC_OK.replace("## Decisão / Aprovação", "## Outra coisa")


def main():
    fails = 0
    with tempfile.TemporaryDirectory() as d:
        # 1. spec completa: valida + gera md com seções
        ok, _ = g.validate(SPEC_OK)
        written, _ = g.export(SPEC_OK, os.path.join(d, "ok"), ["md"])
        md = open(written[0], encoding="utf-8").read() if written else ""
        c1 = ok and ("## Custo" in md) and ("## Decisão / Aprovação" in md)
        if not c1:
            fails += 1
        print(f"{'OK  ' if c1 else 'FAIL'} spec completa valida e gera md com as seções")

        # 2. seção obrigatória ausente → validate FAIL
        ok2, _ = g.validate(SPEC_SEM_DECISAO)
        if ok2:
            fails += 1
        print(f"{'OK  ' if not ok2 else 'FAIL'} seção obrigatória ausente reprova (Decisão/Aprovação)")

        # 3. custo placeholder → NÃO PREENCHIDO, nunca fabricado
        w3, _ = g.export(SPEC_CUSTO_VAZIO, os.path.join(d, "vazio"), ["md"])
        md3 = open(w3[0], encoding="utf-8").read() if w3 else ""
        # localizar a seção Custo no md gerado
        import re
        m = re.search(r"## Custo\s*\n(.+?)(\n## |\Z)", md3, re.DOTALL)
        custo = (m.group(1).strip() if m else "")
        honesto = (g.NAO_PREENCHIDO in custo) and not re.search(r"\d", custo)
        if not honesto:
            fails += 1
        print(f"{'OK  ' if honesto else 'FAIL'} custo placeholder vira NÃO PREENCHIDO (não fabrica número) [custo='{custo[:40]}']")

    print("-" * 50)
    print("RESULTADO:", f"FAIL ({fails})" if fails
          else "PASS (gera documento executivo; seções obrigatórias; custo nunca fabricado)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
