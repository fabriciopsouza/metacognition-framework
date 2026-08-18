#!/usr/bin/env python3
"""Canario da PROCEDENCIA do veredito de qa-critic (ADR-108).

Prova as duas direcoes contra transcripts sinteticos, nunca contra o log real: veredito
honesto e VERIFICADO, e cada forma de forja e' PEGA. Sem a segunda metade este canario seria
cego — varreria, nao acharia nada e ficaria verde, que e' a classe que o v1.89.0 zerou.

Um dos casos existe porque o autor cometeu o defeito: a 1a versao do detector varria os
ultimos 4000 caracteres procurando `REPROVAR` e acusou FRAUDE num veredito legitimo, porque o
relatorio dizia "por que nao e REPROVAR nem APROVAR limpo" ao explicar a conclusao. O caso
(f) prende isso — falso-positivo aqui custa mais que falso-negativo, porque um detector que
acusa o inocente e' desligado e ai nao resta nem o falso-negativo.

Uso: python tools/test_verify_qa_attestation.py   (exit 0 PASS; 1 se falha)
"""
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import verify_qa_attestation as vqa  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

AGENT_ID = "abc123def4567890a"
TOOL_ID = "toolu_teste_0001"


def relatorio(veredito="APROVAR_COM_RESSALVAS", com_explicacao=True):
    """Relatorio no formato que os criticos de fato produzem."""
    corpo = ["## Achados", "", "### MEDIO — alguma coisa", "descricao do achado.", ""]
    if com_explicacao:
        # A armadilha real: a EXPLICACAO cita os outros vereditos.
        corpo += ["### Por que nao e REPROVAR nem APROVAR limpo", "porque tal e tal.", ""]
    # O relatorio real passa a fechar com o SENTINELA — e o `**{veredito}**` continua no
    # texto de proposito: ele NAO pode mais influenciar a leitura, e o canario prova isso.
    corpo += [f"**{veredito}**",
              f"<<<VEREDITO_FINAL: {veredito}>>>",
              f"agentId: {AGENT_ID} (use SendMessage with to: 'x')",
              "<usage>subagent_tokens: 1</usage>"]
    return "\n".join(corpo)


def escrever_transcript(dirpath, texto, subagent_type="qa-critic", modelo="sonnet",
                        modelo_autor="claude-opus-5"):
    """Transcript sintetico no formato do harness (tool_use do Agent + tool_result)."""
    linhas = [
        {"type": "assistant", "message": {"model": modelo_autor, "content": [
            {"type": "tool_use", "id": TOOL_ID, "name": "Agent",
             "input": {"subagent_type": subagent_type, "model": modelo}}]}},
        {"type": "user", "message": {"content": [
            {"type": "tool_result", "tool_use_id": TOOL_ID, "content": texto}]}},
    ]
    p = os.path.join(dirpath, "sessao.jsonl")
    with io.open(p, "w", encoding="utf-8") as fh:
        for r in linhas:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    return p


def veredito_json(sha=None, recomendacao="aprovar_com_ressalvas", agent=AGENT_ID,
                  autor="claude-opus-5"):
    at = {"agentId": agent, "modelo": "claude-sonnet-5", "modelo_autor": autor}
    if sha is not None:
        at["prova_transcript"] = sha
    return {"bloco": "t", "passou": True, "recomendacao": recomendacao,
            "problemas": [], "verificacoes_executadas": ["x"], "atestacao": at}


def main():
    falhas = []

    def caso(nome, esperado, obtido, detalhe=""):
        ok = obtido == esperado
        print(f"{'OK  ' if ok else 'FAIL'} {nome}: esperado {esperado!r}, veio {obtido!r}"
              + (f" — {detalhe}" if detalhe and not ok else ""))
        if not ok:
            falhas.append(nome)

    with tempfile.TemporaryDirectory(prefix="qa-proc-fx-") as td:
        rel = relatorio()
        escrever_transcript(td, rel)
        execs, autor_real = vqa.coletar_execucoes(td)
        sha_certo = "sha256:" + vqa.sha256_texto(rel)

        # (a) o log e lido: uma execucao, com o subagent_type e o modelo pedido
        caso("colhe a execucao do log do harness", 1, len(execs))
        caso("le o modelo do AUTOR gravado pelo harness", "claude-opus-5", autor_real)

        # (b) veredito honesto -> VERIFICADO
        st, mot = vqa.verificar(veredito_json(sha_certo), execs, autor_real)
        caso("veredito honesto e VERIFICADO", "verificado", st, mot)

        # (c) FORJA 1: veredito sem execucao correspondente no log
        st, mot = vqa.verificar(veredito_json(sha_certo, agent="0000naoexiste0000"),
                                execs, autor_real)
        caso("agentId inexistente no log e PEGO", "divergente", st, mot)

        # (d) FORJA 2: hash que nao corresponde ao relatorio (veredito escrito sobre outro texto)
        st, mot = vqa.verificar(veredito_json("sha256:" + "f" * 64), execs, autor_real)
        caso("hash que nao bate e PEGO", "divergente", st, mot)

        # (e) legado: sem prova declarada -> LISTADO, nao reprovado
        st, mot = vqa.verificar(veredito_json(None), execs, autor_real)
        caso("veredito legado e listado, nao reprovado", "legado", st, mot)

        # (f) ANTI-FALSO-POSITIVO: o relatorio EXPLICA por que nao reprovou. A conclusao dele
        #     e APROVAR_COM_RESSALVAS, e o veredito aprovativo tem de ser aceito.
        caso("explicacao que cita REPROVAR nao vira veredito de reprovacao",
             "aprovar_com_ressalvas", vqa.veredito_do_relatorio(rel))
        st, mot = vqa.verificar(veredito_json(sha_certo), execs, autor_real)
        caso("veredito aprovativo com explicacao no relatorio NAO e acusado", "verificado", st, mot)

        # (g) modelo do autor declarado != o que o harness gravou
        st, mot = vqa.verificar(veredito_json(sha_certo, autor="claude-haiku-4-5"),
                                execs, autor_real)
        caso("modelo do autor divergente do log e PEGO", "divergente", st, mot)

    with tempfile.TemporaryDirectory(prefix="qa-proc-fx2-") as td:
        # (h) FORJA 3, a de maior valor: o relatorio REPROVA e o veredito diz aprovar.
        rel = relatorio(veredito="REPROVAR")
        escrever_transcript(td, rel)
        execs, autor_real = vqa.coletar_execucoes(td)
        sha = "sha256:" + vqa.sha256_texto(rel)
        caso("relatorio que reprova e lido como reprovar", "reprovar",
             vqa.veredito_do_relatorio(rel))
        # RESSALVA, nao 'divergente': reprovacao REMEDIADA e' o fluxo normal (critico reprova,
        # autor corrige, veredito registra o estado final citando a rodada que reprovou). Medido
        # em release-1.82.0, que a 1a regra acusou de fraude. O verificador nao consegue separar
        # fraude de remediacao sem a prova da re-revisao — entao TORNA O FATO VISIVEL em vez de
        # escolher um dos dois e errar metade das vezes.
        st, mot = vqa.verificar(veredito_json(sha), execs, autor_real)
        caso("relatorio REPROVA + veredito aprovativo vira RESSALVA visivel", "ressalva", st, mot)
        # e o veredito honesto sobre o mesmo relatorio passa
        st, mot = vqa.verificar(veredito_json(sha, recomendacao="reprovar"), execs, autor_real)
        caso("veredito de reprovacao sobre relatorio que reprova e VERIFICADO",
             "verificado", st, mot)

    with tempfile.TemporaryDirectory(prefix="qa-proc-fx3-") as td:
        # (i) FORJA 4: relatorio veio de subagente que NAO e critico
        rel = relatorio()
        escrever_transcript(td, rel, subagent_type="general-purpose")
        execs, autor_real = vqa.coletar_execucoes(td)
        st, mot = vqa.verificar(veredito_json("sha256:" + vqa.sha256_texto(rel)),
                                execs, autor_real)
        caso("relatorio de subagente NAO-critico e PEGO", "divergente", st, mot)

    with tempfile.TemporaryDirectory(prefix="qa-proc-fx4-") as td:
        # (j) sem transcripts: nao verificavel, e isso NAO pode virar aprovacao nem reprovacao
        execs, autor_real = vqa.coletar_execucoes(os.path.join(td, "nao-existe"))
        st, mot = vqa.verificar(veredito_json("sha256:" + "a" * 64), execs, autor_real)
        caso("sem transcripts o veredito fica LEGADO (nem aprovado nem reprovado)",
             "legado", st, mot)


    # ---- (l) BLOQUEANTE 2: agentId citado em prosa nao pode virar a chave ------------------
    # Meta-QA cita agentId de outras rodadas o tempo todo (este repo faz isso). `re.search`
    # pegava a PRIMEIRA ocorrencia e indexava o relatorio sob a chave errada.
    with tempfile.TemporaryDirectory(prefix="qa-proc-fx5-") as td:
        rel = ("Revisei a rodada cujo agentId: deadbeef00112233 aparece no anterior."
               "\n<<<VEREDITO_FINAL: APROVAR>>>\n"
               f"agentId: {AGENT_ID} (use SendMessage with to: 'x')\n"
               "<usage>subagent_tokens: 1</usage>")
        escrever_transcript(td, rel)
        execs, autor_real = vqa.coletar_execucoes(td)
        caso("indexa pelo TRAILER do harness, nao por agentId citado em prosa",
             True, AGENT_ID in execs, f"chaves={sorted(execs)}")
        caso("o agentId citado em prosa NAO vira chave", False, "deadbeef00112233" in execs)
        if AGENT_ID in execs:
            st, mot = vqa.verificar(
                veredito_json("sha256:" + vqa.sha256_texto(rel), recomendacao="aprovar"),
                execs, autor_real)
            caso("veredito honesto que cita outro agentId e VERIFICADO", "verificado", st, mot)

    # ---- (m) ALTO: modelo do autor e por SESSAO, nao o maximo do diretorio -----------------
    # 'claude-opus-10' < 'claude-opus-5' como string. O global reprovava veredito honesto assim
    # que um modelo novo aparecesse no diretorio — evento rotineiro (ADR-078).
    with tempfile.TemporaryDirectory(prefix="qa-proc-fx6-") as td:
        rel_novo = relatorio()
        escrever_transcript(td, rel_novo, modelo_autor="claude-opus-10")
        os.rename(os.path.join(td, "sessao.jsonl"), os.path.join(td, "sessao-nova.jsonl"))
        # sessao ANTIGA, de outro autor e outro agentId, no mesmo diretorio. agentId distinto
        # de proposito: dois resultados com o mesmo id colidiriam na chave, e o teste mediria
        # a colisao em vez do que ele quer medir (a escolha do autor por sessao).
        antigo = relatorio(com_explicacao=False).replace(AGENT_ID, "0ld0ld0ld0ld0ld0a")
        escrever_transcript(td, antigo, modelo_autor="claude-opus-5")
        execs, autor_real = vqa.coletar_execucoes(td)
        st, mot = vqa.verificar(
            veredito_json("sha256:" + vqa.sha256_texto(rel_novo), autor="claude-opus-10"),
            execs, autor_real)
        caso("autor declarado bate com o da SESSAO (nao com o max do diretorio)",
             "verificado", st, mot)


    # ---- (n) ALTO: rollup de release cita N rodadas — TODAS tem de ser verificadas ---------
    # Antes, so o par solto (agentId + prova_transcript) era checado, e o [VERIFICADO] sugeria
    # que a narrativa inteira de QA da release estava provada. Estava so a ultima rodada.
    with tempfile.TemporaryDirectory(prefix='qa-proc-fx7-') as td:
        rel = relatorio()
        escrever_transcript(td, rel)
        execs, autor_real = vqa.coletar_execucoes(td)
        sha = 'sha256:' + vqa.sha256_texto(rel)
        v = veredito_json(sha)
        # 2a rodada declarada com hash QUE NAO EXISTE -> o rollup inteiro tem de cair
        v['atestacao']['provas'] = [{'agentId': AGENT_ID, 'prova_transcript': sha},
                                    {'agentId': AGENT_ID, 'prova_transcript': 'sha256:' + 'e'*64}]
        st, mot = vqa.verificar(v, execs, autor_real)
        caso('rodada do rollup com hash invalido derruba o veredito', 'divergente', st, mot)
        v['atestacao']['provas'] = [{'agentId': AGENT_ID, 'prova_transcript': sha}]
        st, mot = vqa.verificar(v, execs, autor_real)
        caso('rollup com todas as rodadas provadas e VERIFICADO', 'verificado', st, mot)

    # ---- (o) remediacao REVISADA: reprovou numa rodada, aprovou noutra -> VERIFICADO --------
    # E a diferenca entre 'o autor diz que corrigiu' e 'alguem conferiu que corrigiu'. So a
    # segunda vira verificado; a primeira fica em ressalva (caso h).
    with tempfile.TemporaryDirectory(prefix='qa-proc-fx8-') as td:
        r1 = relatorio(veredito='REPROVAR')
        escrever_transcript(td, r1)
        os.rename(os.path.join(td, 'sessao.jsonl'), os.path.join(td, 's1.jsonl'))
        r2 = relatorio().replace(AGENT_ID, 'b2b2b2b2b2b2b2b2b')
        escrever_transcript(td, r2)
        execs, autor_real = vqa.coletar_execucoes(td)
        v = veredito_json(None)
        v['atestacao']['provas'] = [
            {'agentId': AGENT_ID, 'prova_transcript': 'sha256:' + vqa.sha256_texto(r1)},
            {'agentId': 'b2b2b2b2b2b2b2b2b', 'prova_transcript': 'sha256:' + vqa.sha256_texto(r2)}]
        st, mot = vqa.verificar(v, execs, autor_real)
        caso('reprovacao com re-revisao aprovativa nas provas e VERIFICADO', 'verificado', st, mot)

    # ---- (p) diluicao: a MESMA execucao repetida nao infla a contagem de rodadas ------------
    with tempfile.TemporaryDirectory(prefix='qa-proc-fx9-') as td:
        rel = relatorio()
        escrever_transcript(td, rel)
        execs, autor_real = vqa.coletar_execucoes(td)
        sha = 'sha256:' + vqa.sha256_texto(rel)
        v = veredito_json(sha)
        v['atestacao']['provas'] = [{'agentId': AGENT_ID, 'prova_transcript': sha}] * 5
        st, mot = vqa.verificar(v, execs, autor_real)
        caso('5 copias da mesma prova nao viram 6 rodadas', True,
             'rodada' not in mot, mot)


    # ---- (k) CONTRATO DE CONCLUSAO: so o sentinela conta ---------------------------------
    # Quatro rodadas adversariais fecharam quatro vetores de leitura por heuristica e nunca
    # a CLASSE. O critico nomeou o motivo: posicao nao distingue 'a conclusao' de 'qualquer
    # outra linha formatada como token', e os motivos legitimos para escrever uma segunda
    # sao ilimitados — inclusive um que este framework INCENTIVA (o critico narrar que mudou
    # de ideia depois de medir). Entao o mecanismo parou de adivinhar.
    TR = ("\nagentId: " + AGENT_ID + " (use SendMessage with to: 'x')"
          "\n<usage>subagent_tokens: 1</usage>")
    vetores = [
        ("bare **TOKEN** nao conta mais (era a fonte das 4 leituras erradas)",
         "analise\n\n**APROVAR**\n<<<VEREDITO_FINAL: REPROVAR>>>" + TR, "reprovar"),
        ("critico narra que MUDOU DE IDEIA (vetor A da rodada 4)",
         "**REPROVAR**\n\nAntes de medir eu diria\n\n**APROVAR_COM_RESSALVAS**\n\n"
         "mas os testes mudaram.\n<<<VEREDITO_FINAL: REPROVAR>>>" + TR, "reprovar"),
        ("subveredito por achado depois do consolidado (vetor B da rodada 4)",
         "### Geral\n<<<VEREDITO_FINAL: REPROVAR>>>\n### So o achado A: **APROVAR**\n"
         + TR, "reprovar"),
        ("sentinela dentro de cerca ~~~ nao conta",
         "<<<VEREDITO_FINAL: REPROVAR>>>\n~~~\n<<<VEREDITO_FINAL: APROVAR>>>\n~~~\n"
         + TR, "reprovar"),
        ("cerca ABERTA (relatorio truncado) nao vaza",
         "<<<VEREDITO_FINAL: REPROVAR>>>\n```\n<<<VEREDITO_FINAL: APROVAR>>>\n" + TR,
         "reprovar"),
        ("sentinela DEPOIS do trailer nao conta",
         "<<<VEREDITO_FINAL: REPROVAR>>>" + TR + "\n<<<VEREDITO_FINAL: APROVAR>>>\n",
         "reprovar"),
        ("sem sentinela e ILEGIVEL — nao chuta",
         "analise\n\n**APROVAR**\n" + TR, None),
    ]
    for nome, texto, esperado in vetores:
        caso(nome, esperado, vqa.veredito_do_relatorio(texto))

    # ---- (r) conclusao ILEGIVEL deixa RASTRO, nunca silencio ------------------------------
    with tempfile.TemporaryDirectory(prefix="qa-proc-fx10-") as td:
        rel = "Recomendo fortemente NAO seguir: ha bug grave." + TR
        escrever_transcript(td, rel)
        execs, autor_real = vqa.coletar_execucoes(td)
        st, mot = vqa.verificar(veredito_json("sha256:" + vqa.sha256_texto(rel),
                                              recomendacao="aprovar"), execs, autor_real)
        caso("aprovacao sobre relatorio ilegivel deixa RASTRO", "sem_leitura", st, mot)

    # ---- (s) rollup: rodada ILEGIVEL nao e absorvida por uma rodada aprovada --------------
    # Dizer '1 rodada reprovou antes e foi remediada' sobre uma rodada cuja conclusao
    # NINGUEM sabe afirma um fato inexistente — e some com o unico sinal que havia.
    with tempfile.TemporaryDirectory(prefix="qa-proc-fx11-") as td:
        ileg = "prosa sem sentinela nenhum." + TR
        escrever_transcript(td, ileg)
        os.rename(os.path.join(td, "sessao.jsonl"), os.path.join(td, "s1.jsonl"))
        bom = relatorio().replace(AGENT_ID, "c3c3c3c3c3c3c3c3c")
        escrever_transcript(td, bom)
        execs, autor_real = vqa.coletar_execucoes(td)
        v = veredito_json(None)
        v["atestacao"]["provas"] = [
            {"agentId": AGENT_ID, "prova_transcript": "sha256:" + vqa.sha256_texto(ileg)},
            {"agentId": "c3c3c3c3c3c3c3c3c",
             "prova_transcript": "sha256:" + vqa.sha256_texto(bom)}]
        st, mot = vqa.verificar(v, execs, autor_real)
        caso("rodada ilegivel no rollup NAO vira verificado", "sem_leitura", st, mot)

    # ---- (t) SENTINELA UNICO: contagem, nao posicao ---------------------------------------
    # 'Ultima ocorrencia vence' ainda resolvia ambiguidade por POSICAO. A 5a rodada mostrou
    # o vetor restante: o critico CITA o sentinela da rodada anterior depois do proprio —
    # pratica que a Regra 4 de rastreabilidade (decisao -> fonte -> versao) incentiva. A
    # rule #13 proibe o reuso, mas proibicao de CONTRATO nao fecha invariante; contagem sim,
    # porque reuso a quebra em qualquer ordem.
    ambiguos = [
        ("citacao de auditoria do sentinela anterior",
         "bug bloqueante.\n\n<<<VEREDITO_FINAL: REPROVAR>>>\n\n(nota: a rodada anterior "
         "concluiu <<<VEREDITO_FINAL: APROVAR>>>, registrado para rastreabilidade)\n" + TR),
        ("meta-QA citando o relatorio anterior depois do proprio",
         "<<<VEREDITO_FINAL: REPROVAR>>>\n\nPara constar, o anterior dizia:\n\n"
         "<<<VEREDITO_FINAL: APROVAR>>>\n" + TR),
    ]
    for nome, texto in ambiguos:
        caso(f"{nome} vira AMBIGUO (nao leitura errada)", None,
             vqa.veredito_do_relatorio(texto))

    # o sentinela dentro de cerca nao entra na contagem — sobra UM, e a leitura vale
    caso("cerca com sentinela extra nao torna ambiguo", "reprovar",
         vqa.veredito_do_relatorio("<<<VEREDITO_FINAL: REPROVAR>>>\n```\n"
                                   "<<<VEREDITO_FINAL: APROVAR>>>\n```\n" + TR))
    print("-" * 50)
    if falhas:
        print(f"RESULTADO: FAIL ({len(falhas)}): {', '.join(falhas)}")
        return 1
    print("RESULTADO: PASS (procedencia: forja pega em 4 formas; honesto verificado; "
          "legado listado; explicacao nao confundida com conclusao)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
