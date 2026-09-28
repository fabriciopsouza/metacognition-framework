#!/usr/bin/env python3
"""Canário do verificador do plano (B2b, ADR-125) — `tools/plano.py`.

  (a) plano coerente passa;
  (b) cada regra, quebrada isoladamente, reprova com o achado dela;
  (c) exceções legítimas não reprovam (bloco sem tarefas no avanço; [~] citado no Replanejamento);
  (d) `--avisar` informa e não bloqueia;
  (e) TODAS as especificações reais em docs/specs passam — é isto que barra o plano enganoso neste repositório.

Uso: python tools/test_plano.py   (exit 0 PASS; 1 FAIL)
"""
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import plano  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

BASE = """<!-- spec-unico:v1 -->
# caso — Especificação

## Painel
**Avanço:** B1 50% · B2 100%

| # | Assunto | Situação | Quem age | Resultado / próximo |
|---|---|---|---|---|
| D1 | escolher opção | ⏳ pendente | **dono** | recomendo a |
| D2 | formato | ✅ decidido | — | ok |

## Resumo executivo
**Onde estamos.** metade.

# Parte A — Requisitos
- REQ-01: algo

# Parte B — Aceite
- **Requisitos aprovados pelo dono em:** 10/09/2026 · **Aceite escrito em:** 11/09/2026

# Decisões
| # | Decisão | Alternativas | Recomendação | Resposta do dono |
|---|---|---|---|---|

# Tarefas
### B1 — primeiro bloco
- [x] T1 fazer x — prova: `tools/x.py`
- [ ] T2 fazer y
### B2 — segundo bloco
- [x] T3 fazer z (PR #123)
- [~] T4 adiado

# Mapa de impacto
| Item | Muda? | Situação |
|---|---|---|
| canários | sim | ✅ test_x |
| site | não | |

# Replanejamento
| Data | Item | O que mudou | Por quê | Quem aprovou |
|---|---|---|---|---|
| 12/09/2026 | T4 | adiado | sem prioridade | dono |

# Revisões adversariais
| Rodada | Revisor | Veredito | Achados | O que mudou |
|---|---|---|---|---|
"""

falhas = []


def check(nome, cond, detalhe=""):
    print(("  PASS " if cond else "  FAIL ") + nome + ("" if cond else f" — {detalhe}"))
    if not cond:
        falhas.append(nome)


def troca(velho, novo, texto=BASE):
    assert texto.count(velho) == 1, f"âncora não é única: {velho!r}"
    return texto.replace(velho, novo)


def rodar(texto):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "spec.md")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(texto)
    return plano.verificar(p), p


def main():
    print("(a) plano coerente")
    ach, _ = rodar(BASE)
    check("plano coerente passa", ach == [], ach)

    print("(b) cada regra reprova")
    casos = [
        ("seção obrigatória ausente", troca("# Mapa de impacto\n", "# Outra coisa\n"), "seção obrigatória ausente: Mapa de impacto"),
        ("decisão pendente sem quem age", troca("| ⏳ pendente | **dono** |", "| ⏳ pendente | — |"), "D1: decisão pendente sem 'Quem age'"),
        ("tarefa feita sem prova", troca("- [x] T1 fazer x — prova: `tools/x.py`", "- [x] T1 fazer x"), "T1 marcada [x] sem prova"),
        ("replanejada sem registro", troca("| 12/09/2026 | T4 |", "| 12/09/2026 | T9 |"), "T4 replanejada [~] sem linha"),
        ("avanço que não bate", troca("B1 50%", "B1 90%"), "Avanço de B1: painel diz 90%, as tarefas dão 50%"),
        ("mapa sem situação", troca("| canários | sim | ✅ test_x |", "| canários | sim | |"), "'canários' muda e está sem situação"),
        ("mapa sem linhas", troca("| canários | sim | ✅ test_x |\n| site | não | |\n", ""), "Mapa de impacto sem linhas"),
        ("aceite antes da aprovação", troca("**Aceite escrito em:** 11/09/2026", "**Aceite escrito em:** 09/09/2026"),
         "antes da aprovação dos requisitos"),
    ]
    for nome, texto, trecho in casos:
        ach, _ = rodar(texto)
        check(nome, any(trecho in a for a in ach), ach)

    print("(c) exceções legítimas")
    ach, _ = rodar(troca("B1 50% · B2 100%", "B1 50% · B9 30%"))
    check("bloco do avanço sem lista de tarefas não reprova", ach == [], ach)
    ach, _ = rodar(troca("- [x] T3 fazer z (PR #123)", "- [x] T3 fazer z — ver `docs/adr/001-x.md`"))
    check("arquivo citado entre crases vale como prova", ach == [], ach)

    print("(d) --avisar")
    _, p = rodar(troca("| ⏳ pendente | **dono** |", "| ⏳ pendente | — |"))
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "plano.py"), "verificar", p, "--avisar"],
                       capture_output=True, text=True, encoding="utf-8",
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"))
    check("--avisar informa o achado e sai com 0", r.returncode == 0 and "AVISO" in r.stdout, r.stdout)

    print("(e) especificações reais deste repositório")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "plano.py"), "verificar"],
                       capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"))
    check("todas as specs reais passam no verificador do plano", r.returncode == 0, r.stdout[-1500:])

    print(f"\nRESULTADO: {'FAIL' if falhas else 'PASS'} ({len(falhas)} falha(s))")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
