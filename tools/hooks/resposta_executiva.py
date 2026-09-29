#!/usr/bin/env python3
"""resposta_executiva.py — formato executivo da resposta ao dono (regra do dono, 27/09/2026; revista em 28/09/2026).

Regra: conciso, mas claro; objetivo, mas compreensível; nunca omisso. Número de palavras não é regra fixa (dono,
28/09/2026: "número de palavras não deve ser escrito em pedra").

POR QUE NÃO BLOQUEIA MAIS (ADR-129). O Stop com exit 2 devolvia a resposta DEPOIS que ela já estava na tela: a
reescrita saía embaixo e o dono lia tudo duas vezes. Agora são dois momentos:
  --hook      (Stop)             mede o turno que acabou e guarda os achados da sessão; nunca bloqueia. A mensagem
                                 final vem de `last_assistant_message` (o transcript pode ainda não tê-la no Stop).
  --lembrete  (UserPromptSubmit) antes da próxima resposta, injeta os achados da anterior (uma vez); sem achado,
                                 não injeta nada (o molde está na regra global, CLAUDE.md seção 4).

O que é medido na mensagem final (e no texto intermediário do turno):
  1. pedido ao dono no meio do processamento (some quando a tela sobe);
  2. bloco "★ Insight" (estilo explicativo proibido pela regra global, seção 4);
  3. tabela de decisão (cabeçalho com "Decisão") sem recomendação;
  4. duas tabelas seguidas sem título entre elas (não se vê onde começa cada assunto);
  5. prosa longa (sinal, não limite: acima de PROSA_SINAL palavras fora de tabela e código, sem pedido de detalhe
     ou de artefato) — pergunta se dá para organizar em tabela ou lista sem perder contexto.

Uso: python resposta_executiva.py --hook | --lembrete   (JSON do evento no stdin)
     python resposta_executiva.py --medir <transcript.jsonl>
"""
import datetime
import json
import os
import re
import sys

PROSA_SINAL = 300
ESTADO_DIR = os.environ.get("RESPOSTA_EXECUTIVA_DIR") or os.path.join(
    os.path.expanduser("~"), ".claude", "estado", "resposta_executiva")
HISTORICO_MAX = 500  # linhas guardadas em historico.jsonl (as mais recentes)
# O molde é estático e vive na regra global (CLAUDE.md, seção 4), que carrega uma vez por sessão; o lembrete só
# fala quando há achado (docs oficiais de hooks: instrução que nunca muda vai no CLAUDE.md, não em hook).
AVISO = "Formato executivo (regra do dono, CLAUDE.md seção 4) — na sua resposta anterior: "
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
_DECISAO = re.compile(r"(?i)decis")  # "Opções" sozinho é tabela de referência, não decisão pendente
_RECOMENDA = re.compile(r"(?i)recomend")


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
    """(último pedido do dono, [textos do assistente no turno atual, em ordem])."""
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


def _linhas_fora_de_codigo(texto):
    aberta = False
    for ln in texto.splitlines():
        if _CERCA.match(ln):
            aberta = not aberta
            continue
        if not aberta:
            yield ln


def prosa(texto):
    """Palavras fora de tabela, bloco de código e título."""
    return sum(len(re.findall(r"\w+", s)) for s in (ln.strip() for ln in _linhas_fora_de_codigo(texto))
               if s and not s.startswith("|") and not s.startswith("#"))


def _sem_codigo(texto):
    return "\n".join(ln for ln in _linhas_fora_de_codigo(texto) if not ln.strip().startswith("|"))


def tabelas(texto):
    """[(cabeçalho, linhas em branco/título entre a tabela anterior e esta)] das tabelas fora de código."""
    out, dentro, entre = [], False, None
    for ln in _linhas_fora_de_codigo(texto):
        s = ln.strip()
        if s.startswith("|"):
            if not dentro:
                out.append((s, entre))
                dentro = True
            entre = []
            continue
        dentro = False
        if entre is not None:
            entre.append(s)
    return out


def medir(pedido, textos):
    """Achados sobre o turno (vazio = resposta no formato)."""
    if not textos:
        return []
    motivos = []
    final, meio = textos[-1], textos[:-1]
    for t in meio:
        if _PEDIDO.search(_sem_codigo(t)):
            linha = next((ln.strip() for ln in _sem_codigo(t).splitlines() if _PEDIDO.search(ln)), "")[:90]
            motivos.append(f"pedido ao dono no meio do processamento (\"{linha}\"): some quando a tela sobe; "
                           f"pedido só no fim da mensagem final")
            break
    if any("★ Insight" in t for t in textos):
        motivos.append("bloco '★ Insight': proibido pela regra global (seção 4)")
    for cab, entre in tabelas(final):
        if _DECISAO.search(cab) and not _RECOMENDA.search(cab):
            motivos.append(f"tabela de decisão sem coluna de recomendação: {cab[:70]}")
        if entre is not None and not any(s for s in entre):
            motivos.append(f"tabela colada na anterior, sem título entre elas: {cab[:70]}")
    n = prosa(final)
    if n > PROSA_SINAL and not _DETALHE.search(pedido or "") and not _ARTEFATO.search(pedido or ""):
        motivos.append(f"prosa longa ({n} palavras fora de tabela e código) — sinal, não limite: dá para organizar "
                       f"em seções, tabela ou lista sem perder contexto?")
    return motivos


def _mesmo_texto(a, b):
    """Mesma mensagem apesar de CRLF e espaços (o transcript e o evento podem gravar o branco de forma diferente)."""
    return re.sub(r"\s+", " ", a).strip() == re.sub(r"\s+", " ", b).strip()


def _estado(sessao):
    return os.path.join(ESTADO_DIR, re.sub(r"[^A-Za-z0-9_.-]", "_", sessao) + ".json")


def registrar(sessao, motivos):
    """Guarda os achados para o próximo turno da MESMA sessão e acrescenta ao histórico (as últimas HISTORICO_MAX
    medições; dado do débito avaliar-resposta-executiva). Sem id de sessão não guarda: não há como devolver."""
    if not sessao:
        return
    os.makedirs(ESTADO_DIR, exist_ok=True)
    p = _estado(sessao)
    if motivos:
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"motivos": motivos}, fh, ensure_ascii=False)
    elif os.path.isfile(p):
        os.remove(p)
    h = os.path.join(ESTADO_DIR, "historico.jsonl")
    with open(h, "a", encoding="utf-8") as fh:  # acréscimo: duas sessões ao mesmo tempo não se sobrescrevem
        fh.write(json.dumps({"quando": datetime.datetime.now().isoformat(timespec="seconds"), "sessao": sessao,
                             "motivos": motivos}, ensure_ascii=False) + "\n")
    # Poda só quando passa do dobro: a reescrita (única janela de corrida, que perderia no máximo uma linha de
    # diagnóstico) fica rara. Atalho declarado: sem trava de arquivo; o estado da sessão não passa por aqui.
    linhas = open(h, encoding="utf-8").read().splitlines()
    if len(linhas) > 2 * HISTORICO_MAX:
        with open(h, "w", encoding="utf-8") as fh:
            fh.write("\n".join(linhas[-HISTORICO_MAX:]) + "\n")


def lembrete(sessao):
    """Achados da resposta anterior (consumidos: aparecem uma vez). Sem achado: texto vazio, nada é injetado."""
    if not sessao:
        return ""
    p, achados = _estado(sessao), []
    if os.path.isfile(p):
        try:
            achados = json.load(open(p, encoding="utf-8")).get("motivos") or []
        except (OSError, ValueError):
            achados = []
        os.remove(p)
    if not achados:
        return ""
    return AVISO + " | ".join(achados) + ". Corrija daqui em diante; não repita a resposta anterior."


def main(argv):
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    if len(argv) >= 3 and argv[1] == "--medir":
        pedido, textos = turno(argv[2])
        for m in medir(pedido, textos):
            print(f"ACHADO: {m}")
        return 0
    if "--hook" not in argv and "--lembrete" not in argv:
        print(__doc__)
        return 2
    try:
        dados = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        dados = {}
    sessao = str(dados.get("session_id") or "")
    try:
        if "--lembrete" in argv:
            txt = lembrete(sessao)
            if txt:
                print(txt)  # stdout do UserPromptSubmit entra como contexto do próximo turno
            return 0
        try:
            pedido, textos = turno(dados.get("transcript_path", ""))
        except (OSError, ValueError):
            pedido, textos = "", []
        final = dados.get("last_assistant_message")
        if isinstance(final, str) and final.strip():
            # docs oficiais do Stop: o transcript pode ainda não ter a mensagem final; ela vem neste campo
            if not textos or _mesmo_texto(textos[-1], final) is False:
                textos = textos + [final]
        registrar(sessao, medir(pedido, textos))
    except (OSError, ValueError):
        pass  # medir nunca trava a sessão
    return 0  # nunca bloqueia: bloquear depois de exibir duplicava a resposta na tela (ADR-129)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
