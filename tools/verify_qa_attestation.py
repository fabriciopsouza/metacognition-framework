#!/usr/bin/env python3
"""verify_qa_attestation.py — PROCEDENCIA do veredito de qa-critic (nao so a forma dele).

O QUE RESOLVE
O `squad_gate` conferia forma, escopo e recencia do veredito — nunca a PROCEDENCIA. O
`atestacao.agentId` e o `atestacao.modelo` eram strings que o proprio orquestrador digitava,
e o texto do veredito era transcrito a mao do relatorio do subagente. Consequencia: a
revisao era independente (modelo diferente, contexto isolado), mas o REGISTRO da revisao era
escrito pelo avaliado. Um agente com pressa poderia gravar um veredito plausivel sem nunca
ter rodado critico nenhum, e o gate liberaria — porque nada ligava aquele JSON a uma
execucao real.

O QUE ESTE VERIFICADOR USA — e por que serve
Os transcripts do harness (`~/.claude/projects/<slug>/*.jsonl`) sao escritos pelo HARNESS,
nao pelo agente, e no momento em que cada coisa acontece. Deles saem quatro fatos que o
orquestrador nao produz:
  1. que houve chamada `Agent` com `subagent_type` de qa-critic, e com que modelo foi PEDIDA;
  2. o TEXTO EXATO que o subagente devolveu (`tool_result`);
  3. o `agentId` daquela execucao;
  4. o modelo do AUTOR, gravado turno a turno (`message.model`).

A prova: o veredito declara `atestacao.prova_transcript = "sha256:<hex>"`, o hash do relatorio
que o critico devolveu. Este verificador procura, nos transcripts, um `tool_result` cujo hash
bata. Sem relatorio real com aquele texto, nao existe hash que bata — e achado nao pode ser
inventado nem amaciado sem quebrar a prova.

E a invariante que mais importa, alem do hash: **relatorio que REPROVA nao pode virar veredito
aprovativo**. Essa e' a fraude de maior valor, e ela e' checavel diretamente no texto.

LIMITES DECLARADOS (nao sao propriedades que este verificador finge ter)
  - **Qual modelo REALMENTE respondeu nao e' verificavel.** O harness nao grava os turnos do
    subagente (`isSidechain` ausente nos transcripts). Da para provar o modelo PEDIDO e o
    modelo do AUTOR, nao o modelo que executou.
  - **Amaciamento fino escapa.** O hash prova que o relatorio existe e que o veredito global
    concorda com ele; nao prova que cada achado foi transcrito com a mesma severidade.
  - **O transcript e' um arquivo local, gravavel pelo agente em principio.** O modelo de ameaca
    aqui e' "agente com pressa corta caminho", nao "agente forja deliberadamente o log do
    harness". Falsificar transcript e' ato de outra natureza — e fica declarado, nao coberto.
  - **Local, nao CI.** Transcripts nao sao versionados. Verificacao roda na maquina do autor,
    mesma postura do `post_canary_status.py` (driver local, checagem real).

Uso:
    python tools/verify_qa_attestation.py                    # todos os vereditos de _meta/qa
    python tools/verify_qa_attestation.py --veredito <path>  # um so
    python tools/verify_qa_attestation.py --transcripts <dir> --qa-dir <dir>   # para o canario
Codigos de saida: 0 = tudo verificado · 1 = veredito CONTRADIZ o relatorio ou hash nao bate ·
3 = ha ressalva/sem-leitura (procedencia ok, concordancia NAO verificada — leia a saida).
Veredito legado (sem `prova_transcript`) e' LISTADO, nao reprovado — mesmo desenho do passivo
do ADR-106: quem nasce depois da norma nasce sob ela.
NAO usa IA.
"""
import argparse
import glob
import hashlib
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA_DIR = os.path.join(RAIZ, "_meta", "qa")

APROVATIVOS = {"aprovar", "aprovar_com_ressalvas"}

TOKENS = r"(REPROVAR|APROVAR[_ ]COM[_ ]RESSALVAS|APROVAR)"

# O veredito DECLARADO: token colado a um marcador "Veredito". E' a unica forma de ler a
# conclusao sem confundi-la com o texto que a explica.
#
# A 1a versao desta funcao varria os ultimos 4000 caracteres procurando `\bREPROVAR\b` e
# acusou FRAUDE num veredito legitimo: o relatorio do lote 2 dizia "## Veredito:
# APROVAR_COM_RESSALVAS" no topo e, no fim, "### Por que nao e REPROVAR nem APROVAR limpo".
# O detector leu a explicacao como se fosse a conclusao. Detector que grita fraude em veredito
# correto e desligado na primeira semana — o falso-positivo aqui custa mais que o
# falso-negativo, porque destroi a confianca no mecanismo inteiro.
RX_TOKEN = re.compile(r"\b" + TOKENS + r"\b")

# NEGACAO IMEDIATA: "nao e X" / "nem X". Precisa ser IMEDIATA — sem virgula, ponto ou quebra
# entre a negacao e o token — senao "nao e APROVAR, e REPROVAR" marcaria REPROVAR como negado
# e desarmaria a invariante central.
#
# A 2a versao (esta) existe porque a 1a so aplicava negacao no fallback, e o caminho principal
# ("veredito" na mesma linha do token) passava sem guarda. O qa-critic reproduziu os DOIS
# sentidos do defeito:
#   "O veredito nao e REPROVAR, mas sim APROVAR_COM_RESSALVAS" -> lia 'reprovar' (acusa o honesto)
#   "O veredito nao e um simples APROVAR. (...) **REPROVAR**"  -> lia 'aprovar'  (desarma a trava)
# O segundo e' o grave: deixa passar como VERIFICADO um relatorio que REPROVA.
# So conta DECLARACAO FORMAL: uma linha cujo conteudo inteiro E' o token (com decoracao
# markdown e rotulo opcionais). Mencao em prosa NUNCA conta.
#
# A regra anterior — 'ultima ocorrencia nao-negada no texto inteiro' — foi REPROVADA pelo
# qa-critic na rodada 2, com reproducao ponta a ponta: um relatorio com bug bloqueante e
# `**REPROVAR**` explicito, seguido de um P.S. comparando com rodadas passadas ('nas rodadas
# anteriores o padrao era APROVAR_COM_RESSALVAS'), era lido como APROVATIVO. Nao exige ma-fe:
# e' o formato natural de um relatorio de QA que compara rodadas — coisa que este repo faz o
# tempo todo. A causa-raiz era o detector nao ter nocao de ONDE TERMINA a conclusao; confiar
# na ordem fisica do texto e' fragil demais para a invariante central deste ADR.
#
# Ambiguidade agora devolve None (o hash segue provando procedencia) em vez de um palpite —
# e' a unica postura que nao acusa o inocente nem absolve o culpado.
RX_LINHA_FORMAL = re.compile(
    r"^\s*[#*_\-\s]*(?:(?:veredito|recomenda[cç][aã]o|resultado|conclus[aã]o)\s*[:\-]?\s*)?"
    r"\**\s*" + TOKENS + r"\s*\**\s*[.!]?\s*$", re.I | re.M)


def slug_do_projeto(raiz=RAIZ):
    """Nome da pasta de transcripts que o harness usa para este repo."""
    return raiz.replace(":", "").replace("\\", "-").replace("/", "-").lower()


def dir_transcripts_default():
    base = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    alvo = os.path.join(base, slug_do_projeto())
    if os.path.isdir(alvo):
        return alvo
    # Fallback tolerante: o slug do harness pode diferir em maiusculas/prefixo de drive.
    cauda = os.path.basename(RAIZ).lower()
    if os.path.isdir(base):
        for nome in sorted(os.listdir(base)):
            if nome.lower().endswith(cauda):
                return os.path.join(base, nome)
    return alvo


def sha256_texto(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


# O harness anexa SEMPRE, no fim do resultado de um Agent, o trailer
# "agentId: <id> (use SendMessage ...". Ancorar nele evita o defeito que o qa-critic
# reproduziu: `re.search` pegava a PRIMEIRA ocorrencia, e um relatorio que MENCIONA o agentId
# de outra rodada (meta-QA, coisa que este proprio repo faz o tempo todo) era indexado sob a
# chave errada — veredito honesto virava "execucao nao encontrada".
RX_TRAILER = re.compile(r"agentId:\s*([0-9a-z]{8,})\s*\(use\s+SendMessage", re.I)
RX_AGENT_ID = re.compile(r"agentId:\s*([0-9a-z]{8,})", re.I)


def _agent_id_do_trailer(txt: str):
    """O agentId do TRAILER do harness. Preferir o trailer; se ausente, a ULTIMA ocorrencia."""
    m = list(RX_TRAILER.finditer(txt))
    if m:
        return m[-1].group(1)
    m = list(RX_AGENT_ID.finditer(txt))
    return m[-1].group(1) if m else None


def _texto_do_tool_result(bloco) -> str:
    """Normaliza o conteudo de um tool_result para uma string estavel."""
    c = bloco.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "".join(b.get("text", "") for b in c if isinstance(b, dict))
    return ""


def coletar_execucoes(dir_transcripts):
    """{agentId: {"relatorio": str, "sha256": str, "modelo_pedido": str|None,
                  "subagent_type": str|None, "modelo_autor": str|None}}

    Um `tool_result` de Agent termina com "agentId: <id>", e e' por ele que amarramos o
    relatorio a chamada. O modelo PEDIDO vem do `tool_use` correspondente (mesmo id).
    """
    if not os.path.isdir(dir_transcripts):
        return {}, None
    # `autor_do_arquivo`: modelo do autor POR SESSAO. O global (max lexicografico do
    # diretorio inteiro) reprovava veredito honesto assim que aparecesse um modelo novo —
    # e 'claude-opus-10' < 'claude-opus-5' como string. Achado ALTO do qa-critic, reproduzido.
    resultados, chamadas, autor_do_arquivo = {}, {}, {}
    for arq in sorted(glob.glob(os.path.join(dir_transcripts, "*.jsonl"))):
        for linha in io.open(arq, encoding="utf-8", errors="replace"):
            linha = linha.strip()
            if not linha:
                continue
            try:
                r = json.loads(linha)
            except ValueError:
                continue                      # linha corrompida nao invalida o resto
            msg = r.get("message") or {}
            if r.get("type") == "assistant" and msg.get("model"):
                m0 = msg["model"]
                if not m0.startswith("<"):
                    autor_do_arquivo.setdefault(arq, m0)
            cont = msg.get("content")
            if not isinstance(cont, list):
                continue
            for b in cont:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use" and b.get("name") == "Agent":
                    inp = b.get("input") or {}
                    chamadas[b.get("id")] = {"modelo_pedido": inp.get("model"),
                                             "subagent_type": inp.get("subagent_type")}
                elif b.get("type") == "tool_result":
                    txt = _texto_do_tool_result(b)
                    aid = _agent_id_do_trailer(txt)
                    if aid:
                        resultados[aid] = {"relatorio": txt,
                                           "sha256": sha256_texto(txt),
                                           "tool_use_id": b.get("tool_use_id"),
                                           # modelo do autor da SESSAO deste resultado, nao o
                                           # global do diretorio (achado ALTO do qa-critic)
                                           "modelo_autor": autor_do_arquivo.get(arq)}
    for aid, dados in resultados.items():
        c = chamadas.get(dados.get("tool_use_id")) or {}
        dados["modelo_pedido"] = c.get("modelo_pedido")
        dados["subagent_type"] = c.get("subagent_type")
    # O 2o valor de retorno segue existindo por compatibilidade (visao geral do diretorio),
    # mas a CHECAGEM usa `dados['modelo_autor']`, que e' o autor daquela SESSAO.
    vistos = sorted(set(autor_do_arquivo.values()))
    return resultados, (vistos[-1] if len(vistos) == 1 else None)


# CONTRATO DE CONCLUSAO — sentinela unico, nao heuristica.
#
# Quatro rodadas adversariais fecharam quatro vetores de leitura errada (negacao, linha
# formal, exemplo em cerca, citacao em blockquote, P.S., subveredito por achado) e NUNCA
# fecharam a classe. O critico nomeou o motivo: heuristica de POSICAO sobre prosa livre nao
# distingue 'a conclusao' de 'qualquer outra linha formatada como token'. E os motivos
# legitimos para escrever uma segunda linha dessas sao ilimitados — inclusive um que este
# framework INCENTIVA: o critico narrar que mudou de ideia depois de medir.
#
# Entao o mecanismo deixa de adivinhar. A conclusao e' o sentinela, e nada mais. O prompt
# do qa-critic passa a exigi-lo como ULTIMA coisa escrita, com instrucao de nunca reusar a
# sequencia em exemplo ou citacao. Sem sentinela -> `sem_leitura`, que e' a verdade: a
# procedencia esta provada, a concordancia nao foi verificada.
SENTINELA = "<<<VEREDITO_FINAL:"
RX_SENTINELA = re.compile(r"<<<VEREDITO_FINAL:\s*" + TOKENS + r"\s*>>>", re.I)

# Cercas: crase OU til, fechadas OU abertas-ate-o-fim. A nao-fechada e' a mais provavel de
# aparecer sem intencao nenhuma — relatorio truncado no meio produz exatamente isso.
RX_CERCA = re.compile(r"(```|~~~).*?(\1|\Z)", re.S)


def _janela_de_conclusao(txt: str) -> str:
    """O trecho onde a conclusao pode estar: ANTES do trailer do harness, sem cercas de codigo.

    Tres rodadas de reprovacao chegaram a mesma causa-raiz por caminhos diferentes: o detector
    ficou mais estrito sobre O QUE conta como declaracao (prosa -> ultima ocorrencia -> linha
    formal), mas nunca sobre ONDE procurar. Por isso o vetor sobreviveu as tres: P.S. depois da
    conclusao, exemplo dentro de cerca de codigo, e citacao da rodada anterior em blockquote —
    todos leem como conclusao algo que nao e'.

    A ancora existe e e' fisica: o harness anexa `agentId: ... (use SendMessage` DEPOIS de tudo
    que o subagente escreveu. Nada legitimo vem depois dele. E cerca de codigo e' exemplo por
    definicao — nunca conclusao.
    """
    m = list(RX_TRAILER.finditer(txt))
    corte = txt[:m[-1].start()] if m else txt
    return RX_CERCA.sub("", corte)

def _norm_token(t: str) -> str:
    return t.strip().lower().replace(" ", "_")


def veredito_do_relatorio(txt: str):
    """O veredito que o RELATORIO DECLARA, ou None se nao houver declaracao inequivoca.

    None e' resposta legitima e frequente: relatorios variam de formato, e este verificador
    prefere admitir 'nao sei ler a conclusao' a inventar uma. Quando devolve None, o hash
    continua provando a procedencia — so a checagem de concordancia fica de fora.
    """
    janela = _janela_de_conclusao(txt)
    # SO' o sentinela. `**TOKEN**` solto e' ignorado de proposito — foi a fonte das quatro
    # leituras erradas, e nenhuma regex sobre prosa alheia fecha essa classe.
    #
    # E EXATAMENTE UM. 'Ultima ocorrencia vence' ainda resolvia ambiguidade por POSICAO, e a
    # 5a rodada adversarial mostrou o vetor que restava: um critico citando o sentinela da
    # rodada anterior DEPOIS do proprio — pratica que a Regra 4 de rastreabilidade deste
    # framework (decisao -> fonte -> versao) literalmente incentiva. A rule #13 proibe o
    # reuso, mas proibicao de CONTRATO nao fecha invariante: e' a mesma folga que este ADR
    # nasceu para nao aceitar do orquestrador, e nao vale diferente para o texto do critico.
    #
    # Contagem e' a propriedade certa: reuso SEMPRE a quebra, em qualquer ordem.
    ms = list(RX_SENTINELA.finditer(janela))
    if len(ms) != 1:
        return None          # zero (sem declaracao) ou >1 (ambiguo) -> nao sei, e digo
    sobreviventes = [_norm_token(ms[0].group(1))]
    # A conclusao e' a ULTIMA DECLARACAO FORMAL: o relatorio explica em prosa e declara no fim.
    # e o harness anexa o trailer no fim. Ancorar no fim e' mais estavel que procurar um
    # marcador "Veredito", que nem todo critico escreve — e nao tem o furo de ler a explicacao.
    return sobreviventes[-1] if sobreviventes else None


def verificar(veredito, execucoes, modelo_autor_real):
    """(status, motivo). status: 'verificado' | 'legado' | 'divergente'."""
    at = veredito.get("atestacao") or {}
    # Veredito de RELEASE costuma ser rollup de N rodadas. Se so a ultima carrega prova, o
    # [VERIFICADO] sugere que a narrativa inteira de QA esta provada — e nao esta. Achado ALTO
    # do qa-critic. `provas` (lista de {agentId, prova_transcript}) cobre as demais rodadas;
    # o par solto continua valendo, e o que NAO tem prova aparece na contagem.
    pares = [(str(p.get("agentId", "") or "").strip(),
              str(p.get("prova_transcript", "") or "").strip())
             for p in (at.get("provas") or []) if isinstance(p, dict)]
    if at.get("prova_transcript") or not pares:
        pares.insert(0, (str(at.get("agentId", "") or "").strip(),
                         str(at.get("prova_transcript", "") or "").strip()))

    # DEDUP obrigatorio antes de contar. Sem ele: (a) o par do topo, quando repetido dentro de
    # `provas`, inflava a contagem em +1 — ja acontecia nos dois rollups reais, medido pelo
    # qa-critic; e (b) listar a MESMA execucao 5 vezes rendia '6 de 6 rodada(s) com prova' a
    # partir de UMA execucao. Contagem de rodadas que aceita repeticao nao mede nada — e' o
    # numero-que-soa-como-evidencia de novo, agora no relatorio do proprio verificador.
    vistos, unicos = set(), []
    for par in pares:
        if par not in vistos:
            vistos.add(par)
            unicos.append(par)
    pares = unicos

    resultados = [_verificar_par(a, pr, execucoes, at, veredito, modelo_autor_real)
                  for a, pr in pares]
    ruins = [(s, m) for s, m in resultados if s == "divergente"]
    if ruins:
        return ruins[0]
    ilegiveis = [(s, m) for s, m in resultados if s == "sem_leitura"]
    ressalvas = [(s, m) for s, m in resultados if s == "ressalva"]
    aprovadas = [(s, m) for s, m in resultados if s == "verificado"]
    # Rodada ILEGIVEL nunca e' absorvida por uma rodada aprovada: a conclusao dela poderia
    # ter sido REPROVAR, e dizer 'reprovaram antes e foram remediadas' afirmaria um fato
    # que ninguem sabe. Achado ALTO do qa-critic (rodada 4): o sinal sumia justamente
    # quando havia companhia boa no mesmo rollup.
    # Concatena as categorias nao-limpas: devolver so a primeira escondia o fato MAIS
    # acionavel do rollup (uma rodada que reprova sem re-revisao ficava invisivel atras de
    # uma ilegivel). Achado ALTO do qa-critic, rodada 5.
    if ilegiveis:
        partes = [m for _, m in ilegiveis] + [m for _, m in ressalvas]
        return "sem_leitura", " | TAMBEM: ".join(partes)
    if ressalvas and not aprovadas:
        return "ressalva", " | TAMBEM: ".join(m for _, m in ressalvas)
    if ressalvas and aprovadas:
        return "verificado", (aprovadas[0][1] +
                              f" · {len(ressalvas)} rodada(s) reprovaram antes e foram "
                              f"remediadas com re-revisao")
    legados = [(s, m) for s, m in resultados if s == "legado"]
    if legados and len(legados) == len(resultados):
        return legados[0]
    ok = len(resultados) - len(legados)
    extra = f" ({ok} de {len(resultados)} rodada(s) com prova)" if len(resultados) > 1 else ""
    return "verificado", [m for s, m in resultados if s == "verificado"][0] + extra


def _verificar_par(aid, prova, execucoes, at, veredito, modelo_autor_real):
    """Verifica UM par (agentId, hash). Extraida para que o rollup possa checar N rodadas."""

    if not prova:
        return "legado", "sem `atestacao.prova_transcript` — procedencia nao verificavel"

    if not prova.startswith("sha256:") or len(prova) != len("sha256:") + 64:
        return "divergente", f"`prova_transcript` malformada ({prova[:20]}...): esperado sha256:<64 hex>"

    if not aid:
        return "divergente", "declara `prova_transcript` sem `agentId` — nada para amarrar"

    exec_ = execucoes.get(aid)
    if exec_ is None:
        if not execucoes:
            return "legado", "transcripts indisponiveis nesta maquina — nao verificado (declarado)"
        return "divergente", (f"nenhuma execucao de subagente com agentId {aid} nos transcripts "
                              f"— o veredito afirma uma revisao que nao aparece no log do harness")

    if prova.split(":", 1)[1].lower() != exec_["sha256"]:
        return "divergente", ("hash do relatorio NAO bate com o que o subagente devolveu — o "
                              "veredito foi escrito sobre outro texto (ou o texto foi editado)")

    st = str(exec_.get("subagent_type") or "")
    if not st:
        # O `tool_use` daquela chamada nao esta nos logs disponiveis (sessao antiga, transcript
        # rotacionado). Papel NAO verificavel != papel errado — tratar ausencia de dado como
        # acusacao e a mesma falha de acusar o inocente que ja custou uma rodada aqui.
        return "ressalva", (f"hash confere para {aid}, mas o `tool_use` da chamada nao esta nos "
                            f"logs disponiveis: o PAPEL do subagente nao pode ser verificado")
    if "qa" not in st.lower() and "critic" not in st.lower():
        return "divergente", (f"o relatorio veio de subagent_type={st!r}, que nao e' um critico "
                              f"— evidencia de QA exige o papel de QA")

    declarado = str(veredito.get("recomendacao", "") or "").strip().lower()
    do_relatorio = veredito_do_relatorio(exec_["relatorio"])
    if do_relatorio == "reprovar" and declarado in APROVATIVOS:
        # REPROVACAO REMEDIADA nao e' fraude — e' o fluxo normal deste repo: o critico reprova,
        # o autor corrige, e o veredito registra o estado FINAL citando a rodada que reprovou.
        # Medido em `release-1.82.0` (rodada 2, resumo dizendo 'R1 REPROVOU'), que a 1a versao
        # desta regra acusou de fraude. Acusar o inocente aqui e' pior que nao acusar: mata a
        # confianca no verificador inteiro.
        #
        # Mas tambem NAO da para chamar de verificado sem mais nada — sem uma re-revisao, o que
        # existe e' a palavra do autor de que corrigiu. A distincao e' EMPIRICA: se houver, nas
        # `provas`, outra execucao cujo relatorio NAO reprova, a remediacao foi revisada.
        # Senao, o fato fica VISIVEL como ressalva — nem absolvido, nem acusado.
        return "ressalva", (f"o relatorio de {aid} REPROVA e o veredito e' {declarado!r}: "
                            f"reprovacao remediada e legitima, mas nao ha nas `provas` uma "
                            f"re-revisao que aprove o estado corrigido")

    # Autor da SESSAO onde este agentId executou — nao o global do diretorio.
    if do_relatorio is None and declarado in APROVATIVOS:
        # Quanto mais estrita a regra de leitura, mais relatorio cai em None — e None nao pode
        # virar silencio. Um relatorio que reprova EM SUBSTANCIA sem escrever a linha formal
        # ('Recomendo fortemente NAO seguir') saia como verificado puro, sem nenhum sinal.
        # Achado do qa-critic, rodada 3. Agora fica visivel: procedencia OK, concordancia NAO
        # verificada — que sao coisas diferentes e devem aparecer separadas.
        return "sem_leitura", (f"hash confere para {aid}, mas a conclusao do relatorio nao esta "
                               f"em forma declarada: a CONCORDANCIA nao foi verificada")

    autor_declarado = str(at.get("modelo_autor", "") or at.get("autor", "") or "").strip()
    autor_da_sessao = exec_.get("modelo_autor") or modelo_autor_real
    if autor_declarado and autor_da_sessao and autor_declarado != autor_da_sessao:
        return "divergente", (f"modelo do autor declarado ({autor_declarado}) != o que o harness "
                              f"gravou nos turnos daquela sessao ({autor_da_sessao})")

    pedido = exec_.get("modelo_pedido")
    detalhe = f"agentId {aid}, subagent={st}, modelo pedido={pedido}"
    return "verificado", detalhe


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--veredito", help="um veredito especifico (default: todos de _meta/qa)")
    ap.add_argument("--qa-dir", default=QA_DIR)
    ap.add_argument("--transcripts", default=None,
                    help="pasta de transcripts .jsonl (default: a do harness para este repo)")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    padrao = dir_transcripts_default()
    dir_t = a.transcripts or padrao
    if os.path.abspath(dir_t) != os.path.abspath(padrao):
        # Fronteira de confianca atravessada: o verificador passa a ler um log que nao e o do
        # harness deste repo. E' legitimo (o canario usa), mas nao pode ser silencioso — senao
        # o [VERIFICADO] some de contexto. Achado MEDIO do qa-critic.
        print(f"[AVISO] lendo transcripts FORA do padrao do harness: {dir_t}")
        print(f"        (padrao seria {padrao}) — VERIFICADO aqui vale para ESTE log, nao para o do repo")
    execucoes, modelo_autor = coletar_execucoes(dir_t)

    alvos = [a.veredito] if a.veredito else sorted(glob.glob(os.path.join(a.qa_dir, "*.json")))
    if not alvos:
        print(f"RESULTADO: SKIP (nenhum veredito em {a.qa_dir})")
        return 0

    verificados, legados, divergentes, ressalvas, sem_leitura = [], [], [], [], []
    for p in alvos:
        nome = os.path.basename(p)
        try:
            v = json.loads(io.open(p, encoding="utf-8").read())
        except ValueError as e:
            divergentes.append((nome, f"JSON invalido: {str(e)[:60]}"))
            continue
        status, motivo = verificar(v, execucoes, modelo_autor)
        {"verificado": verificados, "legado": legados, "ressalva": ressalvas,
         "sem_leitura": sem_leitura}.get(status, divergentes).append((nome, motivo))

    print(f"procedencia de veredito qa-critic: {len(alvos)} veredito(s) · "
          f"{len(execucoes)} execucao(oes) de subagente no log do harness "
          f"({os.path.basename(dir_t)})")
    for nome, det in verificados:
        print(f"  [VERIFICADO] {nome} — {det}")
    if legados:
        print(f"  [legado] {len(legados)} sem prova de procedencia (nao reprova; a norma vale "
              f"para veredito novo):")
        for nome, motivo in legados:
            print(f"      - {nome}: {motivo}")
    if ressalvas:
        print(f"  [RESSALVA] {len(ressalvas)} veredito(s) aprovam sobre relatorio que REPROVA, sem re-revisao nas provas:")
        for nome, motivo in ressalvas:
            print(f"      - {nome}: {motivo}")
    for nome, motivo in divergentes:
        print(f"  [DIVERGENTE] {nome} — {motivo}")

    print("-" * 50)
    if divergentes:
        print(f"RESULTADO: FAIL ({len(divergentes)} veredito(s) sem procedencia valida)")
        return 1
    if sem_leitura:
        print(f"  [SEM LEITURA] {len(sem_leitura)} veredito(s) com procedencia OK mas conclusao "
              f"do relatorio nao-declarada (concordancia NAO verificada):")
        for nome, motivo in sem_leitura:
            print(f"      - {nome}: {motivo}")
    # Codigo de saida DISTINTO para ressalva: 'PASS' liso e exit 0 sao indistinguiveis de
    # aprovacao limpa para qualquer consumidor automatico. Achado ALTO do qa-critic: no dia em
    # que isto virar gate (pendencia do ADR-108), ressalva viraria aprovacao silenciosa.
    # PROCEDENCIA e CONCORDANCIA sao provas DIFERENTES e devem aparecer separadas: a
    # primeira e' 'este relatorio existiu mesmo'; a segunda, 'o veredito gravado concorda
    # com ele'. Reportar so a segunda faria parecer que nada foi provado.
    com_procedencia = len(verificados) + len(ressalvas) + len(sem_leitura)
    if ressalvas or sem_leitura:
        print(f"RESULTADO: PASS COM RESSALVA — {com_procedencia} veredito(s) com "
              f"PROCEDENCIA provada, dos quais {len(verificados)} tambem com CONCORDANCIA "
              f"verificada ({len(sem_leitura)} sem leitura da conclusao, {len(ressalvas)} "
              f"com ressalva) · {len(legados)} legado(s) sem prova de procedencia. "
              f"Leia as linhas acima: o codigo de saida nao basta.")
        return 3
    print(f"RESULTADO: PASS — {len(verificados)} veredito(s) com procedencia E concordancia "
          f"verificadas · {len(legados)} legado(s) sem prova de procedencia")
    return 0


if __name__ == "__main__":
    sys.exit(main())
