#!/usr/bin/env python3
"""Canário do formato executivo (`tools/hooks/resposta_executiva.py`, regra do dono de 27/09 e 28/09/2026; ADR-129).

Transcripts sintéticos no formato do Claude Code (JSONL). Prova:
  (a) resposta no formato não gera achado; tabela e código não contam como prosa;
  (b) prosa longa é SINAL, não limite: 200 palavras passam; muito longa vira achado; pedido de detalhe isenta;
  (c) pedido ao dono no meio do turno vira achado; o mesmo pedido no fim passa;
  (d) bloco "★ Insight" vira achado;
  (e) tabela de decisão sem recomendação e tabelas coladas sem título viram achado;
  (f) o hook de Stop NUNCA bloqueia (exit 0 sempre) — bloquear depois de exibir duplicava a resposta;
  (g) o lembrete injeta o molde sempre e os achados da resposta anterior UMA vez, por sessão;
  (h) resultado de ferramenta, subagente e notificação do sistema não contam como pedido do dono;
  (i) regra global e wiring citam o hook nos dois eventos.

Uso: python tools/test_resposta_executiva.py   (exit 0 PASS; 1 FAIL)
"""
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "tools", "hooks", "resposta_executiva.py")
ESTADO = tempfile.mkdtemp()

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

falhas = []


def check(nome, cond, detalhe=""):
    print(("  PASS " if cond else "  FAIL ") + nome + ("" if cond else f" — {detalhe}"))
    if not cond:
        falhas.append(nome)


def user(texto):
    return {"type": "user", "isSidechain": False, "message": {"role": "user", "content": texto}}


def tool_result():
    return {"type": "user", "isSidechain": False,
            "message": {"role": "user", "content": [{"type": "tool_result", "content": "Qual é a sua cor? ok"}]}}


def asst(texto, lado=False):
    return {"type": "assistant", "isSidechain": lado, "message": {"role": "assistant",
                                                                 "content": [{"type": "text", "text": texto}]}}


def tool_use():
    return {"type": "assistant", "isSidechain": False, "message": {"role": "assistant",
                                                                  "content": [{"type": "tool_use", "name": "Bash"}]}}


def _executar(modo, dados):
    return subprocess.run([sys.executable, HOOK, modo], input=json.dumps(dados), capture_output=True, text=True,
                          encoding="utf-8", env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
                                                     RESPOSTA_EXECUTIVA_DIR=ESTADO))


def rodar(entradas, sessao="s1", caminho=None, final=None):
    """(exit do Stop, achados guardados para a sessão). `final` = last_assistant_message do evento."""
    if caminho is None:
        fd, caminho = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            for e in entradas:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    dados = {"transcript_path": caminho, "session_id": sessao}
    if final is not None:
        dados["last_assistant_message"] = final
    r = _executar("--hook", dados)
    p = os.path.join(ESTADO, f"{sessao}.json")
    achados = json.load(open(p, encoding="utf-8"))["motivos"] if os.path.isfile(p) else []
    return r.returncode, achados


def lembrete(sessao="s1"):
    return _executar("--lembrete", {"session_id": sessao}).stdout


def tem(achados, trecho):
    return any(trecho in a for a in achados)


EXEC = ("## Resultado\n\n| Bloco | O que é | Situação |\n|---|---|---|\n| B1 | kit | ✅ |\n\n"
        "## Sua ação\n\nresponder D1.")
PROSA = lambda n: " ".join(["palavra"] * n)  # noqa: E731
TABELA_GRANDE = "| a | b |\n|---|---|\n" + "\n".join(f"| linha {i} com muitas palavras de conteúdo | x |" for i in range(80))
CODIGO = "```\n" + "\n".join("palavra " * 20 for _ in range(30)) + "\n```\nPronto."
DECISAO_SEM = "## Decisões\n\n| # | Decisão | Opções |\n|---|---|---|\n| 1 | x | a · b |"
DECISAO_COM = "## Decisões\n\n| # | Decisão | Opções | Recomendo |\n|---|---|---|---|\n| 1 | x | a · b | a |"
COLADAS = "| A | B |\n|---|---|\n| 1 | 2 |\n\n| C | D |\n|---|---|\n| 3 | 4 |"
SEPARADAS = "## Um\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n## Dois\n\n| C | D |\n|---|---|\n| 3 | 4 |"


def main():
    print("(a) resposta no formato")
    rc, a = rodar([user("status"), tool_use(), tool_result(), asst(EXEC)])
    check("seções + tabela + ação no fim: sem achado", a == [], a)
    rc, a = rodar([user("status"), asst(TABELA_GRANDE)])
    check("tabela grande não conta como prosa", a == [], a)
    rc, a = rodar([user("gere"), asst(CODIGO)])
    check("bloco de código não conta como prosa", a == [], a)

    print("(b) prosa: sinal, não limite")
    rc, a = rodar([user("status"), asst(PROSA(200))])
    check("200 palavras passam (número não é regra fixa)", a == [], a)
    rc, a = rodar([user("status"), asst(PROSA(400))])
    check("prosa muito longa vira achado de sinal", tem(a, "sinal, não limite"), a)
    rc, a = rodar([user("explique em detalhe por que mudou"), asst(PROSA(400))])
    check("com pedido de detalhe, prosa longa passa", a == [], a)
    rc, a = rodar([user("escreva o ADR do formato executivo"), asst(PROSA(400))])
    check("artefato pedido (escreva o ADR) passa", a == [], a)
    for frase in ("quero revisar o documento com você", "qual o status do relatório?"):
        rc, a = rodar([user(frase), asst(PROSA(400))])
        check(f"conversa sobre artefato não isenta: '{frase}'", tem(a, "prosa longa"), a)

    print("(c) pedido no meio do turno")
    rc, a = rodar([user("faça X"), asst("Quer que eu siga pela opção A?"), tool_use(), tool_result(), asst(EXEC)])
    check("pergunta ao dono no meio do turno vira achado", tem(a, "meio do processamento"), a)
    rc, a = rodar([user("faça X"), asst("Rodando os testes."), tool_use(), tool_result(), asst(EXEC + "\n\nSigo pela A?")])
    check("o mesmo pedido no fim da mensagem final passa", a == [], a)
    rc, a = rodar([user("faça X"), asst("```\nif x?\n```\nRodando."), tool_use(), tool_result(), asst("Feito.")])
    check("'?' dentro de bloco de código no meio não conta", a == [], a)

    print("(d) estilo explicativo")
    rc, a = rodar([user("faça"), asst("`★ Insight ─────`\nexplicação\n`─────`\n" + EXEC)])
    check("bloco ★ Insight vira achado", tem(a, "Insight"), a)

    print("(e) estrutura")
    rc, a = rodar([user("faça"), asst(DECISAO_SEM)])
    check("tabela de decisão sem recomendação vira achado", tem(a, "sem coluna de recomendação"), a)
    rc, a = rodar([user("faça"), asst(DECISAO_COM)])
    check("tabela de decisão com recomendação passa", a == [], a)
    rc, a = rodar([user("faça"), asst(COLADAS)])
    check("tabelas coladas sem título viram achado", tem(a, "sem título entre elas"), a)
    rc, a = rodar([user("faça"), asst(SEPARADAS)])
    check("tabelas com título entre elas passam", a == [], a)
    rc, a = rodar([user("faça"), asst("```\n| A |\n|---|\n\n| B |\n|---|\n```\nFeito.")])
    check("tabelas dentro de bloco de código não contam", a == [], a)
    rc, a = rodar([user("faça"), asst("## Parâmetros\n\n| Parâmetro | Opções | Padrão |\n|---|---|---|\n| x | a · b | a |")])
    check("tabela de referência com 'Opções' não é tabela de decisão", a == [], a)

    print("(f) nunca bloqueia")
    rc, a = rodar([user("faça X"), asst("Decida entre A e B."), tool_use(), tool_result(), asst(DECISAO_SEM + "\n\n" + PROSA(500))])
    check("com vários achados, o Stop sai com 0 (não duplica a resposta na tela)", rc == 0 and len(a) >= 3, (rc, a))
    rc, a = rodar([], caminho=os.path.join(tempfile.gettempdir(), "nao-existe-123.jsonl"))
    check("transcript ausente não trava (exit 0)", rc == 0, rc)

    print("(f2) mensagem final vem do evento (last_assistant_message)")
    rc, a = rodar([user("faça X"), asst("Rodando os testes.")], final=DECISAO_SEM)
    check("transcript sem a final: mede a do evento", tem(a, "sem coluna de recomendação"), a)
    rc, a = rodar([user("faça X"), asst(DECISAO_SEM)], final=DECISAO_SEM)
    check("final já no transcript não é contada duas vezes", len([x for x in a if "sem coluna" in x]) == 1, a)
    rc, a = rodar([user("faça X"), asst("Quer que eu siga?")], final=EXEC)
    check("texto do transcript vira intermediário quando a final vem do evento", tem(a, "meio do processamento"), a)
    for branco in ("\r\n", "  "):
        rc, a = rodar([user("faça X"), asst(f"Resumo feito.{branco}\n\nSigo com o deploy?")],
                      final="Resumo feito.\n\nSigo com o deploy?")
        check(f"final igual à do transcript salvo branco ({branco!r}) não vira pedido no meio", a == [], a)
    antes = sorted(os.listdir(ESTADO))
    rc, a = rodar([user("faça"), asst(DECISAO_SEM)], sessao="")
    check("sem id de sessão nada é gravado", sorted(os.listdir(ESTADO)) == antes, os.listdir(ESTADO))

    print("(g) lembrete")
    rodar([user("faça"), asst(DECISAO_SEM)], sessao="s2")
    l1, l2 = lembrete("s2"), lembrete("s2")
    check("lembrete traz o achado da resposta anterior e aponta a regra", "sem coluna de recomendação" in l1
          and "CLAUDE.md" in l1, l1)
    check("o achado aparece uma vez; sem achado, nada é injetado", l2.strip() == "", l2)
    sys.path.insert(0, os.path.dirname(HOOK))
    import resposta_executiva as rex  # noqa: E402
    rex.ESTADO_DIR = ESTADO
    h = os.path.join(ESTADO, "historico.jsonl")
    base = len(open(h, encoding="utf-8").read().splitlines())
    rex.registrar("h", [])
    check("histórico cresce por acréscimo", len(open(h, encoding="utf-8").read().splitlines()) == base + 1)
    with open(h, "w", encoding="utf-8") as fh:  # recomeça do zero para contar a poda com exatidão
        fh.write("")
    for _ in range(rex.HISTORICO_MAX + 10):
        rex.registrar("h", [])
    check("abaixo do dobro não poda (a reescrita do arquivo é rara)",
          len(open(h, encoding="utf-8").read().splitlines()) == rex.HISTORICO_MAX + 10)
    for _ in range(rex.HISTORICO_MAX):
        rex.registrar("h", [])
    n = len(open(h, encoding="utf-8").read().splitlines())
    check("passando do dobro, o histórico é podado às últimas 500 medições", rex.HISTORICO_MAX <= n <= 2 * rex.HISTORICO_MAX
          and n < base + 1 + 2 * rex.HISTORICO_MAX, n)
    rodar([user("faça"), asst(DECISAO_SEM)], sessao="s3")
    check("achado de outra sessão não vaza", "sem coluna" not in lembrete("s4"), lembrete("s4"))
    rodar([user("faça"), asst(EXEC)], sessao="s3")
    check("resposta corrigida limpa o achado pendente", "sem coluna" not in lembrete("s3"))
    check("histórico das medições é gravado", os.path.isfile(os.path.join(ESTADO, "historico.jsonl")))

    print("(h) ferramenta, subagente e sistema")
    rc, a = rodar([user("status"), tool_use(), tool_result(), asst(EXEC)])
    check("'?' em resultado de ferramenta não é pedido ao dono", a == [], a)
    rc, a = rodar([user("status"), asst("Posso seguir?", lado=True), asst(EXEC)])
    check("texto de subagente não conta", a == [], a)
    notif = user("<task-notification>\n<task-id>x</task-id>\n<status>completed</status>\n</task-notification>")
    rc, a = rodar([user("explique em detalhe o motivo"), asst("Rodando."), notif, asst(PROSA(400))])
    check("notificação do sistema não vira pedido do dono (a isenção de detalhe continua)", a == [], a)
    rc, a = rodar([user("status"), asst("Posso seguir com A?"), notif, asst(EXEC)])
    check("turno anterior à notificação não é medido de novo", a == [], a)
    rc, a = rodar([user("status"), user("<qualquer-tag>explique em detalhe</qualquer-tag>"), asst(PROSA(400))])
    check("mensagem que começa com tag com hífen é envelope de sistema", tem(a, "prosa longa"), a)
    rc, a = rodar([user("<br> no texto? explique em detalhe"), asst(PROSA(400))])
    check("HTML colado pelo dono (<br>) continua sendo pedido dele", a == [], a)

    print("(i) regra e wiring")
    glob = open(os.path.join(ROOT, ".claude", "global", "CLAUDE-global.md"), encoding="utf-8").read()
    check("regra global cita o hook e o critério sem número fixo",
          "resposta_executiva" in glob and "nunca omisso" in glob and "150" not in glob)
    wiring = open(os.path.join(ROOT, "tools", "hooks", "ensure-global-wiring.ps1"), encoding="utf-8").read()
    check("wiring instala o Stop (--hook) e o UserPromptSubmit (--lembrete)",
          "'Stop'" in wiring and "--hook" in wiring and "--lembrete" in wiring and "|| true" not in wiring)
    check("wiring isolada (-RepoDir) copia o hook", "tools\\hooks\\resposta_executiva.py" in wiring)
    sync = open(os.path.join(ROOT, ".claude", "hooks", "sync-global.ps1"), encoding="utf-8").read()
    check("sync-global espelha o hook para ~/.claude/hooks", "resposta_executiva.py" in sync)

    print(f"\nRESULTADO: {'FAIL' if falhas else 'PASS'} ({len(falhas)} falha(s))")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
