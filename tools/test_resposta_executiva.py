#!/usr/bin/env python3
"""Canário do hook de formato executivo (`tools/hooks/resposta_executiva.py`, regra do dono de 27/09/2026).

Transcripts sintéticos no formato do Claude Code (JSONL). Prova:
  (a) resposta executiva curta (tabela + ações) passa; tabela e código não contam como prosa;
  (b) prosa longa na mensagem final é devolvida; com pedido de detalhe, passa;
  (c) pedido ao dono no meio do turno é devolvido; o mesmo pedido no fim passa;
  (d) bloco "★ Insight" é devolvido;
  (e) `stop_hook_active` não devolve de novo (sem laço); transcript ausente não trava;
  (f) resultado de ferramenta e subagente não contam como pedido do dono nem como resposta;
  (g) a regra global (seção 4) e a wiring global citam o hook.

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


def rodar(entradas, ativo=False, caminho=None):
    if caminho is None:
        fd, caminho = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            for e in entradas:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    r = subprocess.run([sys.executable, HOOK, "--hook"], input=json.dumps(
        {"transcript_path": caminho, "stop_hook_active": ativo}), capture_output=True, text=True, encoding="utf-8",
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"))
    # Contrato do Stop: exit 2 + motivo no stderr = devolve; exit 0 = passa. Normalizado para o dict dos casos.
    if r.returncode == 2:
        return r.returncode, {"decision": "block", "reason": r.stderr.strip()}
    return r.returncode, ({} if r.returncode == 0 else {"erro": r.returncode, "stderr": r.stderr})


EXEC = ("| Bloco | Situação |\n|---|---|\n| B1 | ✅ |\n| B2 | ⏳ |\n\n**Próximo passo:** revisar B2.\n\n"
        "**Você precisa:** responder D1.")
LONGA = " ".join(["Esta frase explica em detalhe o contexto histórico da decisão e suas implicações."] * 20)
TABELA_GRANDE = "| a | b |\n|---|---|\n" + "\n".join(f"| linha {i} com muitas palavras de conteúdo | x |" for i in range(80))
CODIGO = "```\n" + "\n".join("palavra " * 20 for _ in range(30)) + "\n```\nPronto."


def main():
    print("(a) resposta executiva")
    rc, out = rodar([user("status"), tool_use(), tool_result(), asst(EXEC)])
    check("tabela + ações + pedido no fim passa", rc == 0 and out == {}, out)
    rc, out = rodar([user("status"), asst(TABELA_GRANDE)])
    check("tabela grande não conta como prosa", out == {}, out)
    rc, out = rodar([user("gere"), asst(CODIGO)])
    check("bloco de código não conta como prosa", out == {}, out)

    print("(b) prosa longa")
    rc, out = rodar([user("status"), asst(LONGA)])
    check("prosa longa na final é devolvida", out.get("decision") == "block" and "palavras de prosa" in out.get("reason", ""), out)
    rc, out = rodar([user("explique em detalhe por que mudou"), asst(LONGA)])
    check("com pedido de detalhe, prosa longa passa", out == {}, out)

    print("(c) pedido no meio do turno")
    rc, out = rodar([user("faça X"), asst("Quer que eu siga pela opção A?"), tool_use(), tool_result(), asst(EXEC)])
    check("pergunta ao dono no meio do turno é devolvida", out.get("decision") == "block"
          and "meio do processamento" in out.get("reason", ""), out)
    rc, out = rodar([user("faça X"), asst("Decida entre A e B."), tool_use(), tool_result(), asst("Feito.")])
    check("ordem de decidir no meio do turno é devolvida", out.get("decision") == "block", out)
    rc, out = rodar([user("faça X"), asst("Rodando os testes."), tool_use(), tool_result(),
                     asst(EXEC + "\n\nSigo pela opção A?")])
    check("o mesmo pedido no fim da mensagem final passa", out == {}, out)
    rc, out = rodar([user("faça X"), asst("```\nif x?\n```\nRodando."), tool_use(), tool_result(), asst("Feito.")])
    check("'?' dentro de bloco de código no meio não conta", out == {}, out)

    print("(d) estilo explicativo")
    rc, out = rodar([user("faça"), asst("`★ Insight ─────`\nexplicação\n`─────`\n" + EXEC)])
    check("bloco ★ Insight é devolvido", out.get("decision") == "block" and "Insight" in out.get("reason", ""), out)

    print("(e) sem laço e sem travar")
    rc, out = rodar([user("status"), asst(LONGA)], ativo=True)
    check("stop_hook_active não devolve de novo", out == {} and rc == 0, out)
    rc, out = rodar([], caminho=os.path.join(tempfile.gettempdir(), "nao-existe-123.jsonl"))
    check("transcript ausente não trava (exit 0, sem bloqueio)", rc == 0 and out == {}, out)

    print("(f) ferramenta e subagente")
    rc, out = rodar([user("status"), tool_use(), tool_result(), asst(EXEC)])
    check("'?' em resultado de ferramenta não é pedido ao dono", out == {}, out)
    rc, out = rodar([user("status"), asst("Posso seguir?", lado=True), asst(EXEC)])
    check("texto de subagente não conta", out == {}, out)
    rc, out = rodar([user("explique em detalhe"), tool_use(), tool_result(), asst(LONGA)])
    check("resultado de ferramenta não abre turno novo (o pedido de detalhe continua valendo)", out == {}, out)

    print("(h) achados da revisão (27/09)")
    notif = user("<task-notification>\n<task-id>x</task-id>\n<status>completed</status>\n</task-notification>")
    rc, out = rodar([user("explique em detalhe o motivo"), asst("Rodando."), notif, asst(LONGA)])
    check("notificação do sistema não vira pedido do dono (a isenção de detalhe continua)", out == {}, out)
    rc, out = rodar([user("status"), asst("Posso seguir com A?"), notif, asst(EXEC)])
    check("turno anterior à notificação não é medido de novo", out == {}, out)
    rc, out = rodar([user("status"), notif, asst("Quer que eu siga?"), tool_use(), tool_result(), asst(EXEC)])
    check("pedido no meio do turno aberto por notificação é devolvido", out.get("decision") == "block", out)
    rc, out = rodar([user("escreva o ADR do formato executivo"), asst(LONGA)])
    check("artefato pedido (escreva o ADR) não é devolvido por ser longo", out == {}, out)
    rc, out = rodar([user("gere o relatório da semana"), asst(LONGA)])
    check("artefato pedido (gere o relatório) não é devolvido", out == {}, out)
    cross = user("Another Claude session sent a message: <cross-session-message from=\"x\">explique em detalhe</cross-session-message>")
    rc, out = rodar([user("status"), asst("ok"), cross, asst(LONGA)])
    check("mensagem de outra sessão não vira pedido do dono (sem isenção indevida)", out.get("decision") == "block", out)
    rc, out = rodar([user("status"), user("<qualquer-tag>explique em detalhe</qualquer-tag>"), asst(LONGA)])
    check("mensagem que começa com tag é envelope de sistema", out.get("decision") == "block", out)
    rc, out = rodar([user("<nova-tag x=1>explique em detalhe</nova-tag>"), asst(LONGA)])
    check("outra tag com hífen também é envelope", out.get("decision") == "block", out)
    rc, out = rodar([user("<br> no texto? explique em detalhe"), asst(LONGA)])
    check("HTML colado pelo dono (<br>) continua sendo pedido dele", out == {}, out)
    for frase in ("quero revisar o documento com você", "quero discutir o parecer com calma",
                  "preciso entender o relatório que você mandou", "faça uma leitura do relatório e me diga"):
        rc, out = rodar([user(frase), asst(LONGA)])
        check(f"conversa sobre artefato não isenta: '{frase}'", out.get("decision") == "block", out)
    rc, out = rodar([user("preciso de um prompt para retomar a sessão"), asst(LONGA)])
    check("artefato pedido sem verbo de criação (preciso de um prompt) não é devolvido", out == {}, out)
    rc, out = rodar([user("me mande o texto do e-mail"), asst(LONGA)])
    check("artefato pedido (me mande o texto) não é devolvido", out == {}, out)
    rc, out = rodar([user("qual o status do relatório?"), asst(LONGA)])
    check("citar 'relatório' sem pedir artefato não isenta", out.get("decision") == "block", out)

    print("(g) regra e wiring")
    glob = open(os.path.join(ROOT, ".claude", "global", "CLAUDE-global.md"), encoding="utf-8").read()
    check("regra global cita o hook", "resposta_executiva" in glob)
    wiring = open(os.path.join(ROOT, "tools", "hooks", "ensure-global-wiring.ps1"), encoding="utf-8").read()
    check("wiring global instala o hook no Stop, sem travar a sessão", "resposta_executiva" in wiring
          and "'Stop'" in wiring and "--hook || true" not in wiring)
    check("wiring isolada (-RepoDir) copia o hook", "tools\\hooks\\resposta_executiva.py" in wiring)
    sync = open(os.path.join(ROOT, ".claude", "hooks", "sync-global.ps1"), encoding="utf-8").read()
    check("sync-global espelha o hook para ~/.claude/hooks", "resposta_executiva.py" in sync)

    print(f"\nRESULTADO: {'FAIL' if falhas else 'PASS'} ({len(falhas)} falha(s))")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
