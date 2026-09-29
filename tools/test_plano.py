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

    vazio = troca("- **Requisitos aprovados pelo dono em:** 10/09/2026 · **Aceite escrito em:** 11/09/2026",
                  "- **Requisitos aprovados pelo dono em:** 10/09/2026\n- **Aceite escrito em:**\n- nota de 01/01/2020")
    ach, _ = rodar(vazio)
    check("aceite vazio não lê a data da linha seguinte", not any("aceite escrito" in a for a in ach), ach)

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

    print("(f) painel de fases gerado")
    base_painel = troca("## Painel\n", f"## Painel\n\n{plano.MARCA_INI}\n{plano.painel(BASE)}\n{plano.MARCA_FIM}\n")
    ach, _ = rodar(base_painel)
    check("painel gerado e intacto passa", ach == [], ach)
    check("painel: contagem, barra e onde estamos",
          "| B1 — primeiro bloco ◀ onde estamos | 1/2 | `██████░░░░░░` | 50% |" in base_painel
          and "| B2 — segundo bloco | 1/1 | `████████████` | 100% |" in base_painel, plano.painel(BASE))
    ach, _ = rodar(troca("| 1/2 | `██████░░░░░░` | 50% |", "| 1/2 | `██████░░░░░░` | 80% |", base_painel))
    check("% editado à mão no painel reprova", any("painel de fases diferente" in a for a in ach), ach)
    ach, _ = rodar(troca("- [ ] T2 fazer y", "- [x] T2 fazer y — prova: `x.py`", base_painel).replace("B1 50%", "B1 100%"))
    check("tarefa marcada sem regenerar o painel reprova", any("painel de fases diferente" in a for a in ach), ach)
    _, p = rodar(troca("B1 50%", "B1 100%", troca("- [ ] T2 fazer y", "- [x] T2 fazer y — prova: `x.py`")))
    plano.escrever_painel(p)
    check("--escrever insere o painel e o plano passa", plano.verificar(p) == [], plano.verificar(p))
    plano.escrever_painel(p)
    gravado = open(p, encoding="utf-8").read()
    check("--escrever de novo não duplica", gravado.count(plano.MARCA_INI) == 1)
    check("--escrever sem linha em branco a mais", f"## Painel\n\n{plano.MARCA_INI}" in gravado
          and f"{plano.MARCA_FIM}\n**Avanço:**" in gravado, gravado[:300])

    ach, _ = rodar(base_painel + f"\n{plano.MARCA_INI}\nvelho\n{plano.MARCA_FIM}\n")
    check("par de marcadores duplicado reprova", any("marcadores do painel inválidos" in a for a in ach), ach)
    ach, _ = rodar(troca("## Painel\n", f"## Painel\n{plano.MARCA_FIM}\nx\n{plano.MARCA_INI}\n"))
    check("marcadores invertidos reprovam", any("fim antes do início" in a for a in ach), ach)
    exemplo = troca("### B2 — segundo bloco\n", "### B2 — segundo bloco\n```\n- [ ] T8 exemplo de sintaxe — depende: T99\n```\n")
    check("tarefa dentro de bloco de código não conta", "T8" not in [t["id"] for t in plano.tarefas(exemplo)]
          and rodar(exemplo)[0] == [], rodar(exemplo)[0])

    print("(g) cronograma")
    crono = troca("- [ ] T2 fazer y", "- [ ] T2 fazer y — prazo: 20/10/2026 · depende: T1").replace(
        "- [x] T1 fazer x — prova: `tools/x.py`", "- [x] T1 fazer x — prova: `tools/x.py` · prazo: 10/10/2026")
    ach, _ = rodar(crono)
    check("cronograma coerente passa", ach == [], ach)
    ach, _ = rodar(crono.replace("depende: T1", "depende: T1."))
    check("ponto final depois do id não vira dependência inexistente", ach == [], ach)
    hoje = plano.datetime.date(2026, 10, 25)
    linhas = plano.cronograma(crono, hoje=hoje)
    check("ordenado por prazo, sem prazo por último",
          [x["tarefa"][:2] for x in linhas] == ["T1", "T2", "T3", "T4"], [x["tarefa"] for x in linhas])
    check("tarefa aberta com prazo vencido sai ATRASADA", linhas[1]["situacao"] == "ATRASADA", linhas[1])
    linhas2 = plano.cronograma(crono.replace("prazo: 20/10/2026", "prazo: 05/11/2026"), hoje=hoje)
    check("mudar a data da tarefa muda o cronograma (critério 9)",
          linhas2[1]["prazo"] == plano.datetime.date(2026, 11, 5) and linhas2[1]["situacao"] == "aberta", linhas2[1])
    for nome, texto, trecho in [
        ("prazo ilegível", crono.replace("prazo: 20/10/2026", "prazo: 31/02/2026"), "prazo '31/02/2026' ilegível"),
        ("dependência inexistente", crono.replace("depende: T1", "depende: T9"), "depende de T9, que não existe"),
        ("prazo antes da dependência", crono.replace("prazo: 20/10/2026", "prazo: 01/10/2026"),
         "antes de T1 de quem depende"),
    ]:
        ach, _ = rodar(texto)
        check(f"cronograma: {nome} reprova", any(trecho in a for a in ach), ach)

    print("(e) especificações reais deste repositório")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "plano.py"), "verificar"],
                       capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"))
    check("todas as specs reais passam no verificador do plano", r.returncode == 0, r.stdout[-1500:])

    print(f"\nRESULTADO: {'FAIL' if falhas else 'PASS'} ({len(falhas)} falha(s))")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
