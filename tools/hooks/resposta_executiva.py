#!/usr/bin/env python3
"""resposta_executiva.py — hook de Stop: a resposta ao dono sai no formato executivo (regra do dono, 27/09/2026).

Regra: "CONCISÃO, CLAREZA, informação simples e direta, overview, checklist, ações e ideias encadeadas. NÃO uma
redação verborrágica. A explicação detalhada SE SOLICITADA." e "Reportou e a tarefa precisa de algo, tem que parar e
esperar. Ou terminar o que está fazendo e pedir ao final."

Mede o turno que acabou (o texto que o dono lê) e devolve para reescrita UMA vez (exit 2, motivo no stderr) quando:
  1. a mensagem final tem mais de PROSA_MAX palavras de prosa (fora de tabela, bloco de código e títulos) — não vale
     quando o dono pediu detalhe no último pedido;
  2. há pedido ao dono (pergunta ou ordem de decidir/responder) em texto intermediário do turno, antes da mensagem
     final: o pedido some quando a tela sobe;
  3. há bloco "★ Insight" (estilo explicativo proibido pela regra global, seção 4).
Com `stop_hook_active` (já devolvido uma vez) não bloqueia de novo: evita laço. Transcript ilegível: não bloqueia.

Uso (hook): python resposta_executiva.py --hook   (lê o JSON do Stop no stdin)
      teste: python resposta_executiva.py --medir <transcript.jsonl>
"""
import json
import re
import sys

PROSA_MAX = 150
_CERCA = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_PEDIDO = re.compile(r"(?im)(\?\s*$|^\W*(responda|decida|confirme|aprove|escolha|diga|preciso que (você|voce)|"
                     r"você precisa|voce precisa|me diga|qual (você|voce) prefere)\b)")
_DETALHE = re.compile(r"(?i)\b(detalh\w*|expliq\w*|explic\w*|por que|porqu[eê]|como funciona|passo a passo|"
                      r"relat[oó]rio completo|documento completo|na [ií]ntegra)\b")
# Pedido de um ARTEFATO (o texto longo é a entrega, não conversa): escreva/gere/crie + tipo de documento.
# Verbo forte de criação vale para todo tipo de documento; "quero"/"preciso" só para os curtos (prompt, texto, e-mail,
# mensagem): "quero discutir o relatório" é conversa, não pedido de artefato (revisão de 27/09, rodada 3).
_ARTEFATO = re.compile(r"(?i)\b(escrev\w*|ger[ea]\w*|cri[ea]\w*|redij\w*|redig\w*|mont[ea]\w*|elabor\w*|reda[çc]\w*|"
                       r"mand[ea]\w*|envi[ea]\w*|prepar\w*)\b.{0,60}\b(adr|spec\w*|especifica\w*|"
                       r"relat[oó]rio|documento|doc|readme|pop|runbook|e-?mail|mensagem|texto|ata|proposta|prompt|"
                       r"post|artigo|carta|parecer)\b|\b(quero|precis\w*)\b.{0,30}\b(prompt|texto|e-?mail|mensagem)\b")


def _texto(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(x.get("text", "") for x in content if isinstance(x, dict) and x.get("type") == "text")
    return ""


_SISTEMA = ("<task-notification", "<system-reminder", "<local-command", "<command-name", "<cross-session-message",
            "Another Claude session sent a message")
# Mensagem que COMEÇA com tag COM HÍFEN (<task-notification>, <system-reminder>, <cross-session-message>) é envelope
# do sistema. Tag sem hífen (<br>, <div>, <b>) é HTML que o dono colou: continua sendo pedido dele.
_TAG_INICIAL = re.compile(r"^\s*<[a-z][a-z0-9]*-[a-z0-9-]+[\s>]")


def _inicio_de_turno(d):
    """Entrada que abre um turno: pedido do dono ou aviso do sistema (não resultado de ferramenta nem subagente)."""
    if d.get("type") != "user" or d.get("isSidechain"):
        return False
    c = (d.get("message") or {}).get("content")
    if isinstance(c, str):
        return bool(c.strip())
    return isinstance(c, list) and any(isinstance(x, dict) and x.get("type") == "text" for x in c) \
        and not any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c)


def _prompt_real(d):
    """Pedido escrito pelo dono: abre turno e não é aviso do sistema (notificação de tarefa em segundo plano)."""
    if not _inicio_de_turno(d):
        return False
    t = _texto((d.get("message") or {}).get("content")).lstrip()
    return not (t.startswith(_SISTEMA) or _TAG_INICIAL.match(t))


def turno(caminho):
    """(último pedido do dono, [textos do assistente no turno atual, em ordem]). O turno começa no último pedido do
    dono OU aviso do sistema (o turno anterior já foi medido no Stop dele); a isenção de detalhe vem do último
    pedido escrito pelo dono."""
    entradas = []
    with open(caminho, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            try:
                entradas.append(json.loads(ln))
            except ValueError:
                continue
    ini = max((i for i, d in enumerate(entradas) if _inicio_de_turno(d)), default=-1)
    ult = max((i for i, d in enumerate(entradas) if _prompt_real(d)), default=-1)
    pedido = _texto((entradas[ult].get("message") or {}).get("content")) if ult >= 0 else ""
    textos = [_texto((d.get("message") or {}).get("content")) for d in entradas[ini + 1:]
              if d.get("type") == "assistant" and not d.get("isSidechain")]
    return pedido, [t for t in textos if t.strip()]


def prosa(texto):
    """Palavras fora de tabela, bloco de código e título."""
    n, aberta = 0, False
    for ln in texto.splitlines():
        if _CERCA.match(ln):
            aberta = not aberta
            continue
        s = ln.strip()
        if aberta or not s or s.startswith("|") or s.startswith("#"):
            continue
        n += len(re.findall(r"\w+", s))
    return n


def _sem_codigo(texto):
    out, aberta = [], False
    for ln in texto.splitlines():
        if _CERCA.match(ln):
            aberta = not aberta
            continue
        if not aberta and not ln.strip().startswith("|"):
            out.append(ln)
    return "\n".join(out)


def medir(pedido, textos):
    """Motivos para devolver a resposta (vazio = passa)."""
    if not textos:
        return []
    motivos = []
    final, meio = textos[-1], textos[:-1]
    n = prosa(final)
    if n > PROSA_MAX and not _DETALHE.search(pedido or "") and not _ARTEFATO.search(pedido or ""):
        motivos.append(f"a mensagem final tem {n} palavras de prosa (limite {PROSA_MAX} fora de tabela e código): "
                       f"reescreva no formato executivo — overview, tabela ou checklist, ações encadeadas, o que o dono "
                       f"precisa fazer; detalhe só se pedido")
    for t in meio:
        m = _PEDIDO.search(_sem_codigo(t))
        if m:
            linha = next((ln.strip() for ln in _sem_codigo(t).splitlines() if _PEDIDO.search(ln)), "")[:90]
            motivos.append(f"há pedido ao dono no meio do processamento (\"{linha}\"): ele se perde quando a tela "
                           f"sobe; repita-o no fim da mensagem final, ou pare e espere")
            break
    if any("★ Insight" in t for t in textos):
        motivos.append("há bloco '★ Insight': proibido pela regra global (seção 4); retire a explicação didática")
    return motivos


def main(argv):
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    if len(argv) >= 3 and argv[1] == "--medir":
        pedido, textos = turno(argv[2])
        for m in medir(pedido, textos):
            print(f"MOTIVO: {m}")
        return 0
    if "--hook" not in argv:
        print(__doc__)
        return 2
    try:
        dados = json.loads(sys.stdin.read() or "{}")
        if dados.get("stop_hook_active"):
            return 0
        pedido, textos = turno(dados.get("transcript_path", ""))
    except (OSError, ValueError):
        return 0  # sem transcript legível não há o que medir; nunca trava a sessão
    motivos = medir(pedido, textos)
    if motivos:
        # Contrato do Stop (docs oficiais, hooks.md, conferido em 27/09/2026): exit 2 impede a parada e o stderr
        # volta ao modelo. Qualquer outro código não bloqueia.
        print("Formato executivo (regra do dono): " + " | ".join(motivos), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
