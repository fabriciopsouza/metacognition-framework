#!/usr/bin/env python3
"""Canario da Regra 8 / ADR-098 — referencia a arquivo resolve no cwd do DESTINATARIO.

Prova tres invariantes:
  (1) audit_paths ACUSA diretorio temporario (scratchpad/%TEMP%//tmp/) e link markdown relativo;
  (2) audit_paths NAO acusa o que e legitimo (URL, ancora, path absoluto Win/POSIX) — falso
      positivo derruba a confianca no gate, e gate em que ninguem acredita e pior que nenhum;
  (3) o pacote P14 emitido por handoff.build() declara a RAIZ ABSOLUTA — sem ela, todo path
      relativo listado no pacote so resolve no cwd de quem gerou.

Uso: python tools/test_path_absoluto.py   (exit 0 PASS; 1 se falha)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import handoff  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# (texto, deve_acusar, rotulo)
CASOS = [
    # --- DEVE acusar: quebra no destino
    (r"artefato em C:\Users\x\AppData\Local\Temp\claude\scratchpad\nota.md", True,
     "diretorio temporario Windows"),
    ("gerado em /tmp/relatorio.md", True, "diretorio temporario POSIX"),
    ("salvo em %TEMP%\\saida.json", True, "variavel %TEMP%"),
    ("ver [o relatorio](docs/relatorio.md)", True, "link markdown relativo"),
    ("ver [a consulta](../sql/H1.sql)", True, "link relativo com subida de nivel"),
    # --- NAO deve acusar: resolve no destino
    ("ver [o PR](https://github.com/org/repo/pull/1)", False, "URL completa"),
    ("ver [a secao](#regra-8)", False, "ancora interna"),
    (r"ver [o arquivo](C:\repo\docs\a.md)", False, "path absoluto Windows"),
    ("ver [o arquivo](/srv/repo/docs/a.md)", False, "path absoluto POSIX"),
    ("o repo esta em C:\\metacognition-framework e tudo ancora ali", False,
     "path absoluto sem link"),
]


def main():
    fails = []

    for texto, deve, rotulo in CASOS:
        acusou = bool(handoff.audit_paths(texto))
        if acusou != deve:
            verbo = "NAO acusou" if deve else "acusou INDEVIDAMENTE"
            fails.append(f"{rotulo}: {verbo} — {texto[:60]!r}")

    # (3) o pacote real declara a raiz absoluta
    try:
        pacote = handoff.build(next_role="docops", risk="low", author="opus", ts="<t>")
    except Exception as e:  # gerador quebrado e falha do canario, nao "skip"
        fails.append(f"handoff.build() levantou {type(e).__name__}: {e}")
        pacote = ""
    if pacote and "raiz absoluta desta copia" not in pacote:
        fails.append("pacote P14 NAO declara a raiz absoluta (paths relativos ficam sem ancora)")
    if pacote and ROOT not in pacote:
        fails.append(f"pacote P14 nao contem a raiz real {ROOT!r}")

    print(f"{len(CASOS)} casos de audit_paths + raiz absoluta no pacote P14 — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (Regra 8: referencia resolve no cwd do destinatario)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
