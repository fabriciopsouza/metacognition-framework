#!/usr/bin/env python3
"""Canario do executor de trabalhador externo (ADR-131) — prova que o portao MORDE.

Sem rede: as vias sao falsas e contam as chamadas. Roda: python tools/test_trabalhador_externo.py
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trabalhador_externo as tx  # noqa: E402

SEGREDO = "CONTEUDO-QUE-NAO-PODE-IR-AO-REGISTRO-7731"


class ViaFalsa:
    def __init__(self, resposta=None, explode=None):
        self.chamadas = []
        self.resposta = resposta or {"status_via": "SUCCESS", "texto": "ok", "estruturado": {"ok": True},
                                     "negado": [], "tokens_entrada": 10, "tokens_saida": 2}
        self.explode = explode

    def __call__(self, trab, mensagem, esquema_path, timeout):
        self.chamadas.append(mensagem)
        if self.explode:
            raise self.explode
        return self.resposta


def _repo(base, classe=None, bruto=None):
    os.makedirs(os.path.join(base, ".agent"), exist_ok=True)
    if bruto is not None:
        with open(os.path.join(base, ".agent", "classe-de-dado.json"), "w", encoding="utf-8") as f:
            f.write(bruto)
    elif classe is not None:
        with open(os.path.join(base, ".agent", "classe-de-dado.json"), "w", encoding="utf-8") as f:
            json.dump({"classe": classe, "origem": "teste"}, f)
    with open(os.path.join(base, "a.txt"), "w", encoding="utf-8") as f:
        f.write(SEGREDO)
    with open(os.path.join(base, "outro.txt"), "w", encoding="utf-8") as f:
        f.write("NAO-PEDIDO-9")
    return base


def _cli(args):
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        return tx.main(args)


def run():
    fails = []
    te = tx.carregar_politica()
    tmp = tempfile.mkdtemp(prefix="test-trab-")
    os.environ["TRABALHADOR_REGISTRO"] = os.path.join(tmp, "registro.jsonl")
    os.environ["TRABALHADOR_PEDIDOS"] = os.path.join(tmp, "pedidos")  # [QA r3 A5] nao herda de fora
    os.environ.pop("TRABALHADOR_PAINEL", None)  # o teste grava e apaga o painel: nunca o painel real do dono

    def vias(f):
        return {"agy": f, "ollama": f, "codex": f}

    # Portao por dados_aceitos (dono, 06/11/2026: sem veto por classe empresa). Copia da politica em que nenhum
    # trabalhador externo aceita empresa: prova o portao sem depender do que a politica real libera.
    te_restrita = json.loads(json.dumps(te))
    for t in te_restrita["trabalhadores"].values():
        if t.get("sai_da_maquina") is not False:
            t["dados_aceitos"] = [c for c in t["dados_aceitos"] if c != "empresa"]

    # (1) sem declaracao -> classe mais restrita -> trabalhador que nao a aceita RECUSADO, sem chamada
    r1 = _repo(os.path.join(tmp, "r1"))
    f = ViaFalsa()
    rc, out = tx.rodar("gemini-pro", r1, "revise", ["a.txt"], te=te_restrita, vias=vias(f))
    if rc != tx.RC_RECUSADO or f.chamadas:
        fails.append("sem declaracao, trabalhador que nao aceita a classe tem de ser RECUSADO antes de chamar "
                     f"(rc={rc}, chamadas={len(f.chamadas)})")

    # (2) classe desconhecida -> tratada como a mais restrita
    r2 = _repo(os.path.join(tmp, "r2"), classe="liberado-geral")
    f = ViaFalsa()
    rc, out = tx.rodar("gemini-flash", r2, "revise", te=te_restrita, vias=vias(f))
    if rc != tx.RC_RECUSADO or f.chamadas or out.get("classe") != te["sem_declaracao"]:
        fails.append(f"classe desconhecida tem de valer '{te['sem_declaracao']}' e recusar (rc={rc}, out={out})")

    # (3) declaracao corrompida -> mesma coisa
    r3 = _repo(os.path.join(tmp, "r3"), bruto="{nao e json")
    f = ViaFalsa()
    rc, _ = tx.rodar("sonnet-agy", r3, "revise", te=te_restrita, vias=vias(f))
    if rc != tx.RC_RECUSADO or f.chamadas:
        fails.append("declaracao corrompida tem de recusar trabalhador que nao aceita a classe")

    # (4) classe empresa -> local aceito, chamado uma vez
    r4 = _repo(os.path.join(tmp, "r4"), classe="empresa")
    f = ViaFalsa()
    rc, out = tx.rodar("local-qwen", r4, "revise", ["a.txt"], te=te, vias=vias(f))
    if rc != tx.RC_OK or len(f.chamadas) != 1:
        fails.append(f"classe empresa com trabalhador local tem de rodar (rc={rc}, chamadas={len(f.chamadas)})")

    # (5) classe sintetico -> externo aceito; a mensagem leva SO o arquivo pedido
    r5 = _repo(os.path.join(tmp, "r5"), classe="sintetico")
    f = ViaFalsa()
    rc, out = tx.rodar("gemini-pro", r5, "revise", ["a.txt"], te=te, vias=vias(f))
    if rc != tx.RC_OK or len(f.chamadas) != 1:
        fails.append(f"classe sintetico com trabalhador externo tem de rodar (rc={rc})")
    elif SEGREDO not in f.chamadas[0] or "NAO-PEDIDO-9" in f.chamadas[0]:
        fails.append("a mensagem tem de levar o arquivo pedido e NENHUM outro do repositorio")

    # (6) arquivo fora do repositorio (via ..) -> RECUSADO, sem chamada
    fora = os.path.join(tmp, "fora.txt")
    with open(fora, "w", encoding="utf-8") as fh:
        fh.write("x")
    f = ViaFalsa()
    rc, _ = tx.rodar("gemini-pro", r5, "revise", ["../fora.txt"], te=te, vias=vias(f))
    if rc != tx.RC_RECUSADO or f.chamadas:
        fails.append("arquivo fora do repositorio (..) tem de ser recusado antes de chamar")
    f = ViaFalsa()
    rc, _ = tx.rodar("gemini-pro", r5, "revise", [fora], te=te, vias=vias(f))
    if rc != tx.RC_RECUSADO or f.chamadas:
        fails.append("arquivo fora do repositorio (caminho absoluto) tem de ser recusado")

    # (7) esquema: resposta fora dele e' INVALIDA, nunca OK
    esq = os.path.join(tmp, "esq.json")
    with open(esq, "w", encoding="utf-8") as fh:
        json.dump({"type": "object", "required": ["achados"],
                   "properties": {"achados": {"type": "array", "items": {"type": "object",
                                  "required": ["gravidade"], "properties": {"gravidade": {
                                      "type": "string", "enum": ["alta", "media", "baixa"]}}}}}}, fh)
    ruins = [{"ok": True}, {"achados": [{"gravidade": "gravissima"}]}, {"achados": "nada"}, None]
    for ruim in ruins:
        f = ViaFalsa({"status_via": "SUCCESS", "texto": "", "estruturado": ruim, "negado": []})
        rc, out = tx.rodar("gemini-pro", r5, "revise", esquema_path=esq, te=te, vias=vias(f))
        if rc != tx.RC_INVALIDO:
            fails.append(f"resposta {ruim!r} fora do esquema tem de ser INVALIDA (rc={rc})")
    f = ViaFalsa({"status_via": "SUCCESS", "texto": "", "estruturado": {"achados": [{"gravidade": "alta"}]},
                  "negado": []})
    rc, _ = tx.rodar("gemini-pro", r5, "revise", esquema_path=esq, te=te, vias=vias(f))
    if rc != tx.RC_OK:
        fails.append(f"resposta dentro do esquema tem de passar (rc={rc})")

    # (8) erro da via e status nao-SUCCESS viram ERRO declarado
    f = ViaFalsa(explode=RuntimeError("via caiu"))
    rc, out = tx.rodar("gemini-pro", r5, "revise", te=te, vias=vias(f))
    if rc != tx.RC_ERRO or out.get("status") != "ERRO":
        fails.append("excecao da via tem de virar ERRO declarado (rc 2)")
    f = ViaFalsa({"status_via": "ERROR", "texto": "", "estruturado": None, "negado": [], "erro_via": "x"})
    rc, _ = tx.rodar("gemini-pro", r5, "revise", te=te, vias=vias(f))
    if rc != tx.RC_ERRO:
        fails.append("status da via diferente de SUCCESS tem de virar ERRO")

    # (9) registro: uma linha por chamada, sem conteudo, com sha256
    with open(os.environ["TRABALHADOR_REGISTRO"], encoding="utf-8") as fh:
        linhas = fh.read()
    if SEGREDO in linhas or "NAO-PEDIDO-9" in linhas:
        fails.append("o registro nao pode guardar conteudo enviado")
    if '"sha256_mensagem"' not in linhas or '"RECUSADO"' not in linhas:
        fails.append("o registro tem de guardar sha256 das chamadas e as recusas")

    # (10) toda saida carrega o aviso de que e' consultiva
    if tx.AVISO not in json.dumps(out, ensure_ascii=False) or "qa-critic" not in tx.AVISO:
        fails.append("a saida tem de dizer que e' consultiva e nao substitui o qa-critic")

    # (11) invariantes da politica (dado): nada que sai da maquina aceita a classe mais restrita
    ordem = te["classes_de_dado"]["ordem"]
    if te.get("sem_declaracao") != ordem[-1]:
        fails.append("sem_declaracao tem de ser a classe mais restrita da ordem")
    for tid, t in te["trabalhadores"].items():
        if t.get("via") not in tx.VIAS:
            fails.append(f"trabalhador {tid}: via '{t.get('via')}' sem executor")
        if not set(t.get("dados_aceitos") or []) <= set(ordem):
            fails.append(f"trabalhador {tid}: dados_aceitos fora das classes declaradas")
        if not t.get("modelo") or not t.get("familia"):
            fails.append(f"trabalhador {tid} sem modelo ou familia")

    # (codex) revisor formal: so ele leva o aviso formal; familia diferente do autor Claude
    for tid, t in te["trabalhadores"].items():
        if t.get("revisor_formal") and t.get("familia") == "claude":
            fails.append(f"trabalhador {tid}: revisor_formal exige familia diferente de claude")
    if te["trabalhadores"].get("codex", {}).get("revisor_formal") is not True or "revisao_alternada" not in te:
        fails.append("politica: codex tem de ser revisor_formal e revisao_alternada tem de existir")
    qfd = tx.json.load(open(tx.POLICY_PATH, encoding="utf-8"))["qa_final_duplo"]
    if not all("codex" in str(qfd.get(k, {}).get("alterna_com", "")) for k in ("passo_1", "juncoes")):
        fails.append("politica: passo_1 e juncoes tem de declarar alterna_com codex")
    f = ViaFalsa()
    rc, out = tx.rodar("codex", r5, "revise", ["a.txt"], te=te, vias=vias(f))
    if rc != tx.RC_OK or out.get("aviso") != tx.AVISO_FORMAL:
        fails.append(f"codex em repo sintetico tem de rodar com o aviso formal (rc={rc})")
    # Dono, 06/11/2026: "nao tem veto em empresa". Positivo: os quatro aceitam e sao chamados, o Codex com o aviso formal.
    for tid in ("codex", "gemini-pro", "gemini-flash", "sonnet-agy"):
        f = ViaFalsa()
        rc, out = tx.rodar(tid, r4, "revise", ["a.txt"], te=te, vias=vias(f))
        if rc != tx.RC_OK or len(f.chamadas) != 1:
            fails.append(f"{tid} em repo empresa tem de rodar (rc={rc}, chamadas={len(f.chamadas)})")
        if (tid == "codex") != (out.get("aviso") == tx.AVISO_FORMAL):
            fails.append(f"{tid} em repo empresa: aviso formal errado ({out.get('aviso')})")
    # Negativo: trabalhador sem empresa em dados_aceitos segue recusado, rc 3, sem chamada.
    f = ViaFalsa()
    rc, _ = tx.rodar("codex", r4, "revise", ["a.txt"], te=te_restrita, vias=vias(f))
    if rc != tx.RC_RECUSADO or rc != 3 or f.chamadas:
        fails.append("codex sem empresa em dados_aceitos tem de ser RECUSADO (rc 3) antes de chamar")

    # (codex) linha de comando: so leitura, pasta vazia, sem config do usuario; resposta vazia e' ERRO
    class PopenFalso:
        cmds = []

        rc = 0

        def __init__(self, cmd, **kw):
            PopenFalso.cmds.append((cmd, kw.get("cwd")))
            self.cmd, self.returncode = cmd, PopenFalso.rc

        def communicate(self, entrada=None, timeout=None):
            PopenFalso.entrada = entrada
            arq = self.cmd[self.cmd.index("-o") + 1]
            if PopenFalso.resposta is not None:
                with open(arq, "w", encoding="utf-8") as fh:
                    fh.write(PopenFalso.resposta)
            return ('{"type":"thread.started"}\nlixo\n'
                    '{"type":"turn.completed","usage":{"input_tokens":30,"output_tokens":4}}\n'), ""
    popen_orig, bin_orig = tx.subprocess.Popen, os.environ.get("CODEX_BIN")
    tx.subprocess.Popen, os.environ["CODEX_BIN"] = PopenFalso, "codex-falso"
    try:
        PopenFalso.resposta = "achados: nenhum"
        r = tx.via_codex({"modelo": "gpt-x"}, "msg-unica", None, 10)
        cmd, cwd = PopenFalso.cmds[-1]
        if r["status_via"] != "SUCCESS" or r["texto"] != "achados: nenhum" or PopenFalso.entrada != "msg-unica":
            fails.append(f"via_codex: mensagem pela entrada e resposta lida do -o ({r})")
        if (r["tokens_entrada"], r["tokens_saida"]) != (30, 4):
            fails.append("via_codex tem de ler os tokens do evento turn.completed")
        for exigido in ("read-only", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json"):
            if exigido not in cmd:
                fails.append(f"via_codex sem {exigido}")
        if cmd[cmd.index("-m") + 1] != "gpt-x" or cmd[-1] != "-":
            fails.append("via_codex tem de fixar o modelo com -m e ler o pedido da entrada")
        if cmd[cmd.index("-C") + 1] != cwd or os.path.exists(cwd):  # pasta propria, apagada ao fim
            fails.append("via_codex tem de rodar na pasta vazia e descartavel")
        PopenFalso.rc = 1
        if tx.via_codex({"modelo": "gpt-x"}, "msg", None, 10)["status_via"] == "SUCCESS":
            fails.append("via_codex com rc diferente de 0 nao pode ser SUCCESS")
        PopenFalso.rc, PopenFalso.resposta = 0, None
        if tx.via_codex({"modelo": "gpt-x"}, "msg", None, 10)["status_via"] == "SUCCESS":
            fails.append("via_codex com resposta vazia nao pode ser SUCCESS")
    finally:
        tx.subprocess.Popen = popen_orig
        if bin_orig is None:
            os.environ.pop("CODEX_BIN", None)
        else:
            os.environ["CODEX_BIN"] = bin_orig

    # (12) validador: bool nao e' numero; inteiro com fracao reprova
    if not tx.validar(True, {"type": "integer"}) or not tx.validar(1.5, {"type": "integer"}):
        fails.append("validador aceitou bool ou fracao como inteiro")
    if tx.validar(3, {"type": "integer"}) or tx.validar(2.5, {"type": "number"}):
        fails.append("validador reprovou numero valido")

    # (13) monitor: texto de modelo nunca vira codigo na pagina
    import monitor_trabalhadores as mon
    mal = "<script>alert('x')</script><img src=x onerror=alert(1)>"
    mon.evento("trab-teste", "etapa <b>perigosa</b>", "qa-critic Opus 5.5", "FALHOU", resumo=mal,
               spec="docs/spec.md", repo="r5")
    pagina = open(mon.gerar(), encoding="utf-8").read()
    if "<script>alert" in pagina or "<img src=x" in pagina or "<b>perigosa</b>" in pagina:
        fails.append("o monitor injetou texto de modelo sem escapar (XSS)")
    if "etapa &lt;b&gt;perigosa&lt;/b&gt;" not in pagina or "qa-critic Opus 5.5" not in pagina:
        fails.append("a etapa registrada pelo Claude Code tem de aparecer na trilha")
    try:
        mon.evento("t", "e", "q", "TALVEZ")
        fails.append("evento com status fora da lista tem de ser recusado")
    except ValueError:
        pass

    # (14) monitor: linha corrompida e' contada e avisada, nunca some em silencio
    with open(os.environ["TRABALHADOR_REGISTRO"], "a", encoding="utf-8") as fh:
        fh.write("{isto nao e json\n")
    _, ruins_lidas = mon.ler()
    pagina = open(mon.gerar(), encoding="utf-8").read()
    if ruins_lidas != 1 or "corrompida" not in pagina:
        fails.append(f"linha corrompida tem de ser contada e avisada na pagina (contadas={ruins_lidas})")

    # (14b) painel do plano: escapado, na ordem pedida pelo dono, e arquivo ilegivel nao derruba a pagina
    pp = mon.painel_path()
    with open(pp, "w", encoding="utf-8") as fh:
        json.dump({"titulo": "Plano <i>x</i>", "meta": "<u>m</u>", "entregas": [["Entregas feitas", "3", "de 6"]],
                   "blocos": [["E0-3", "<script>alert(2)</script>", "wip", 75, "branch", "QA"],
                              ["x", "y", ["ok"], float("inf"), "z", "w"]],
                   "grupos": [["<s>g</s>", "<s>s</s>"]], "onde": "<em>o</em>", "falta": "<em>f</em>",
                   "comDono": ["decidir <b>algo</b>"], "fontes": ["<q>fonte</q>"]}, fh)
    pagina = open(mon.gerar(), encoding="utf-8").read()
    if any(t in pagina for t in ("<script>alert(2)", "<b>algo</b>", "<i>x</i>", "<u>m</u>", "<s>g</s>", "<s>s</s>",
                                 "<em>o</em>", "<em>f</em>", "<q>fonte</q>")):
        fails.append("o painel do plano injetou texto sem escapar (XSS)")
    if "Blocos do plano" not in pagina:
        fails.append("situacao fora do formato ou pct infinito derrubou o plano")
    ordem = [pagina.find(s) for s in ("Entregas feitas", "Etapas</small>", "Blocos do plano", "Etapas por trabalho",
                                      "Consumo por trabalhador")]
    if -1 in ordem or ordem != sorted(ordem):
        fails.append(f"ordem do painel errada (posicoes {ordem}): entregas, trilha, plano, etapas, consumo")
    with open(pp, "w", encoding="utf-8") as fh:
        fh.write("{quebrado")
    pagina = open(mon.gerar(), encoding="utf-8").read()
    if "ilegível" not in pagina or "Consumo por trabalhador" not in pagina:
        fails.append("painel ilegivel tem de ser avisado sem derrubar a trilha")
    os.remove(pp)

    # (14c) tokens poupados do Claude: so etapa externa sem falha conta; Codex sem tokens vira "sem medicao"
    poup = [{"trabalho": "p", "etapa": "a", "via": "agy", "trabalhador": "gemini-pro", "status": "OK",
             "tokens_entrada": 100, "tokens_saida": 20},
            {"trabalho": "p", "etapa": "b", "via": "agy", "trabalhador": "gemini-pro", "status": "FALHOU",
             "tokens_entrada": 999, "tokens_saida": 999},
            {"trabalho": "p", "etapa": "c", "via": "claude-code", "quem": "autor Opus", "status": "OK",
             "tokens_entrada": 5000, "tokens_saida": 5000},
            {"trabalho": "p", "etapa": "d", "via": "claude-code", "quem": "codex gpt (exec)", "status": "EM-CURSO"},
            {"trabalho": "p", "etapa": "d", "via": "claude-code", "quem": "codex gpt (exec)", "status": "OK"},
            {"trabalho": "p", "etapa": "e", "via": "ollama", "trabalhador": "so-falhas", "status": "FALHOU",
             "tokens_entrada": 5}]
    tp, pt, _ = mon.agregar(poup)
    if (tp["poupado"], tp["fora"], tp["fora_sem_medida"]) != (120, 2, 1):
        fails.append(f"tokens poupados errados: {tp['poupado']}, fora {tp['fora']}, sem medida {tp['fora_sem_medida']}"
                     "; esperado 120, 2, 1 (abertura EM-CURSO e fecho OK da mesma etapa contam uma vez)")
    if not pt["so-falhas"]["fora"]:
        fails.append("trabalhador externo so com falhas aparece como Claude Code")
    if pt["so-falhas"]["poupado"] != 0 or pt["gemini-pro"]["poupado"] != 120:
        fails.append("linha do trabalhador soma tokens de chamada que falhou (diverge do card)")
    pag_poup = mon.html_pagina(poup)
    if "Tokens processados fora do Claude" not in pag_poup:
        fails.append("card de tokens processados fora do Claude ausente da pagina")
    if "0 processados fora do Claude (etapas OK)" not in pag_poup:
        fails.append("linha na tela do trabalhador so com falhas nao mostra 0 processados (usa tokens de falha)")
    # eventos "status ..." antigos nao contam como etapa
    antes = len(mon.ler()[0])
    with open(os.environ["TRABALHADOR_REGISTRO"], "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"quando": "2026-10-25T20:20:00-03:00", "trabalho": "p", "etapa": "status E0-4",
                             "quem": "PMO (status)", "status": "EM-CURSO"}) + "\n")
        fh.write(json.dumps({"quando": "2026-11-02T10:00:00-03:00", "trabalho": "p", "etapa": "status real",
                             "quem": "PMO (status)", "status": "OK"}) + "\n")
    antes += 1  # evento com outra data e etapa real: conta
    # painel salvo com BOM (padrao do PowerShell 5) e lido
    with open(mon.painel_path(), "w", encoding="utf-8-sig") as fh:
        json.dump({"blocos": [["b", "o", "ok", 100, "w", "f"]]}, fh)
    if "Blocos do plano" not in open(mon.gerar(), encoding="utf-8").read():
        fails.append("painel com BOM virou ilegivel")
    os.remove(mon.painel_path())
    obtido = len(mon.ler()[0])
    if obtido != antes:
        fails.append(f"descarte de eventos de status errou a contagem (esperado {antes}, obtido {obtido})")

    # (15) monitor quebrado nunca derruba a chamada
    original = mon.gerar
    mon.gerar = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("monitor caiu"))
    try:
        f = ViaFalsa()
        rc, _ = tx.rodar("gemini-pro", r5, "revise", te=te, vias=vias(f), trabalho="t", etapa="e")
        if rc != tx.RC_OK:
            fails.append(f"falha do monitor derrubou a chamada (rc={rc})")
    finally:
        mon.gerar = original

    # (16) a integra fica em arquivo proprio e a trilha guarda so o resumo
    f = ViaFalsa({"status_via": "SUCCESS", "texto": "R" * 5000, "estruturado": None, "negado": []})
    rc, out = tx.rodar("gemini-pro", r5, "revise", te=te, vias=vias(f), trabalho="t", etapa="longa")
    ultima = json.loads(open(os.environ["TRABALHADOR_REGISTRO"], encoding="utf-8").read().splitlines()[-1])
    if len(ultima.get("resumo", "")) > tx.RESUMO_MAX or not os.path.exists(ultima.get("saida", "")):
        fails.append("a trilha tem de guardar so o resumo e apontar para a integra em arquivo")
    elif "R" * 5000 not in open(ultima["saida"], encoding="utf-8").read():
        fails.append("o arquivo da integra tem de conter a resposta completa")

    # ---------------- correcoes da QA r1 (Opus, 25/10/2026) ----------------
    # (Q1) pedido fora do repositorio e da pasta temporaria: recusado sem chamada; pedido gigante tambem
    fora_tmp = os.path.join(os.path.expanduser("~"), "pedido-fora-qualquer.md")
    f = ViaFalsa()
    rc, _ = tx.rodar("gemini-pro", r5, "revise", te=te, vias=vias(f), pedido_path=fora_tmp)
    if rc != tx.RC_RECUSADO or f.chamadas:
        fails.append("Q1: pedido de fora do repositorio e da pasta temporaria tem de ser recusado sem chamada")
    f = ViaFalsa()
    rc, _ = tx.rodar("gemini-pro", r5, "x" * (tx.LIMITE_PEDIDO + 1), te=te, vias=vias(f))
    if rc != tx.RC_RECUSADO or f.chamadas:
        fails.append("Q1: pedido acima do teto tem de ser recusado (material vai por --arquivo)")

    # (Q2) trabalhador local apontado para outra maquina: recusado sem chamada
    antes = os.environ.get("OLLAMA_URL")
    os.environ["OLLAMA_URL"] = "http://servidor-remoto:11434"
    try:
        f = ViaFalsa()
        rc, _ = tx.rodar("local-qwen", r4, "revise", ["a.txt"], te=te, vias=vias(f))
        if rc != tx.RC_RECUSADO or f.chamadas:
            fails.append("Q2: trabalhador local com OLLAMA_URL remoto tem de ser recusado sem chamada")
    finally:
        if antes is None:
            os.environ.pop("OLLAMA_URL", None)
        else:
            os.environ["OLLAMA_URL"] = antes

    # (Q3/Q4) esquema: palavra-chave nao suportada recusa ANTES; suportadas sao aplicadas
    def esq_arq(nome, conteudo):
        caminho = os.path.join(tmp, nome)
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(conteudo, fh)
        return caminho
    f = ViaFalsa()
    rc, _ = tx.rodar("gemini-pro", r5, "x", esquema_path=esq_arq("e1.json", {"type": "object", "pattern": "x"}),
                     te=te, vias=vias(f))
    if rc != tx.RC_RECUSADO or f.chamadas:
        fails.append("Q3: esquema com palavra-chave nao suportada tem de ser recusado antes da chamada")
    casos = [({"type": "object", "additionalProperties": False, "properties": {}}, {"x": 1}),
             ({"type": "null"}, 5), ({"type": "array", "minItems": 1}, []),
             ({"type": ["string", "null"]}, 5)]
    for i, (esq, resp) in enumerate(casos):
        f = ViaFalsa({"status_via": "SUCCESS", "texto": "", "estruturado": resp, "negado": []})
        rc, _ = tx.rodar("gemini-pro", r5, "x", esquema_path=esq_arq(f"e{i + 2}.json", esq), te=te, vias=vias(f))
        if rc != tx.RC_INVALIDO:
            fails.append(f"Q3/Q4: resposta {resp!r} fora de {esq} tem de ser INVALIDA (rc={rc})")
    f = ViaFalsa({"status_via": "SUCCESS", "texto": "", "estruturado": None, "negado": []})
    rc, _ = tx.rodar("gemini-pro", r5, "x", esquema_path=esq_arq("e9.json", {"type": ["object", "null"]}),
                     te=te, vias=vias(f))
    if rc not in (tx.RC_OK, tx.RC_INVALIDO):
        fails.append(f"Q4: type em lista nao pode quebrar a chamada (rc={rc})")

    # (Q9) arquivo inexistente: recusa declarada e registrada, nunca traceback
    f = ViaFalsa()
    n_antes = len(open(os.environ["TRABALHADOR_REGISTRO"], encoding="utf-8").read().splitlines())
    rc, _ = tx.rodar("gemini-pro", r5, "x", ["nao-existe.txt"], te=te, vias=vias(f))
    n_depois = len(open(os.environ["TRABALHADOR_REGISTRO"], encoding="utf-8").read().splitlines())
    if rc != tx.RC_RECUSADO or f.chamadas or n_depois != n_antes + 1:
        fails.append("Q9: arquivo inexistente tem de virar RECUSADO registrado, sem chamada")

    # (Q6) a mensagem enviada nao pode estar em NENHUM arquivo da trilha, inclusive nas integras
    pasta_trilha = os.path.dirname(os.environ["TRABALHADOR_REGISTRO"])
    for raiz, _d, nomes in os.walk(pasta_trilha):
        for nome in nomes:
            if nome.endswith((".json", ".jsonl")) and SEGREDO in open(os.path.join(raiz, nome), encoding="utf-8").read():
                fails.append(f"Q6: conteudo enviado gravado em {nome}")

    # (Q5) JSON valido fora do formato nao derruba o monitor; e' contado como ruim
    with open(os.environ["TRABALHADOR_REGISTRO"], "a", encoding="utf-8") as fh:
        fh.write('[1,2]\n{"status":null,"trabalho":"t"}\n{"resumo":5,"trabalho":"t","status":"OK"}\n')
    try:
        _, ruins_lidas = mon.ler()
        pagina = open(mon.gerar(), encoding="utf-8").read()
        if ruins_lidas != 2:  # a corrompida de (14) + o [1,2]
            fails.append(f"Q5: linhas fora do formato tem de ser contadas como ruins (contadas={ruins_lidas})")
    except Exception as e:
        fails.append(f"Q5: linha fora do formato derrubou o monitor ({type(e).__name__}: {e})")

    # (Q7/Q8/Q10) links e escape em todo campo
    mon.evento("trab-link", "e", "<i>quem-mal</i>", "OK", spec="javascript:alert(1)")
    estranho = os.path.join(tmp, "pasta #1", "spec com espaço.md")
    os.makedirs(os.path.dirname(estranho), exist_ok=True)
    open(estranho, "w", encoding="utf-8").write("x")
    mon.evento("trab-link", "e2", "q", "OK", spec=estranho)
    pagina = open(mon.gerar(), encoding="utf-8").read()
    if "href='javascript:" in pagina or "alert(1)'" in pagina:
        fails.append("Q7: spec inexistente virou link clicavel (javascript:)")
    if "<i>quem-mal</i>" in pagina:
        fails.append("Q10: campo 'quem' sem escape no monitor")
    if "%23" not in pagina or "%20" not in pagina:
        fails.append("Q8: link de arquivo com # ou espaco sem codificacao")

    # ---------------- correcoes da QA r2 (Opus, 25/10/2026) ----------------
    vias_orig = tx.VIAS
    f_cli = ViaFalsa()
    tx.VIAS = {"agy": f_cli, "ollama": f_cli}  # a linha de comando nunca chama rede no teste
    cwd_orig = os.getcwd()
    try:
        # (N1) pedido relativo e' resolvido contra a pasta corrente e conferido: arquivo do repo
        # empresa na pasta corrente nao pode ir para o trabalhador de um repo sintetico
        with open(os.path.join(r4, "notas.md"), "w", encoding="utf-8") as fh:
            fh.write("SEGREDO-EMPRESA-CWD")
        os.chdir(r4)
        n0 = len(open(os.environ["TRABALHADOR_REGISTRO"], encoding="utf-8").read().splitlines())
        rc = _cli(["rodar", "--trabalhador", "gemini-pro", "--repo", r5, "--pedido", "notas.md"])
        n1 = len(open(os.environ["TRABALHADOR_REGISTRO"], encoding="utf-8").read().splitlines())
        if rc != tx.RC_RECUSADO or f_cli.chamadas:
            fails.append("N1: pedido relativo da pasta corrente (repo empresa) saiu para o repo sintetico")
        # (N4) a recusa da linha de comando fica na trilha
        if n1 != n0 + 1:
            fails.append("N4: recusa do pedido pela linha de comando nao ficou na trilha")
        # (N7) pedido na pasta temporaria geral (fora da pasta de pedidos) e' recusado
        os.chdir(cwd_orig)
        solto = os.path.join(tempfile.gettempdir(), "pedido-solto-teste.md")
        open(solto, "w", encoding="utf-8").write("x")
        rc = _cli(["rodar", "--trabalhador", "gemini-pro", "--repo", r5, "--pedido", solto])
        if rc != tx.RC_RECUSADO or f_cli.chamadas:
            fails.append("N7: pedido no %TEMP% geral tem de ser recusado; so a pasta de pedidos vale")
        os.remove(solto)
        os.makedirs(tx.pasta_pedidos(), exist_ok=True)
        bom = os.path.join(tx.pasta_pedidos(), "pedido-ok-teste.md")
        open(bom, "w", encoding="utf-8").write("revise")
        rc = _cli(["rodar", "--trabalhador", "gemini-pro", "--repo", r5, "--pedido", bom])
        os.remove(bom)
        if rc != tx.RC_OK or len(f_cli.chamadas) != 1:
            fails.append(f"N7: pedido na pasta de pedidos tem de rodar (rc={rc})")
    finally:
        os.chdir(cwd_orig)
        tx.VIAS = vias_orig

    # (N2) o trabalhador local ignora HTTP_PROXY: o proxy falso nao pode receber nada
    import socket
    import threading
    proxy = socket.socket()
    proxy.bind(("127.0.0.1", 0))
    proxy.listen(1)
    proxy.settimeout(3)
    recebido = []

    def ouvir():
        try:
            c, _ = proxy.accept()
            recebido.append(c.recv(200))
            c.close()
        except OSError:
            pass
    th = threading.Thread(target=ouvir, daemon=True)
    th.start()
    fechado = socket.socket()
    fechado.bind(("127.0.0.1", 0))
    porta_fechada = fechado.getsockname()[1]
    fechado.close()
    env_antes = {k: os.environ.get(k) for k in ("HTTP_PROXY", "http_proxy", "OLLAMA_URL", "NO_PROXY", "no_proxy")}
    os.environ["HTTP_PROXY"] = os.environ["http_proxy"] = f"http://127.0.0.1:{proxy.getsockname()[1]}"
    os.environ.pop("NO_PROXY", None)
    os.environ.pop("no_proxy", None)
    os.environ["OLLAMA_URL"] = f"http://127.0.0.1:{porta_fechada}"
    try:
        tx.via_ollama(te["trabalhadores"]["local-qwen"], "MENSAGEM-EMPRESA", None, 3)
    except Exception:
        pass  # a porta esta fechada: o esperado e' falhar SEM passar pelo proxy
    th.join(4)
    proxy.close()
    for k, v in env_antes.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    if recebido:
        fails.append("N2: a via local mandou a mensagem ao HTTP_PROXY do sistema")

    # (N3) esquema malformado: recusa registrada, sem chamada e sem traceback
    for i, ruim in enumerate([{"type": {"a": 1}}, {"type": [["x"]]}, {"properties": [1]},
                              {"type": "string", "minLength": "3"}, {"required": "x"}]):
        f = ViaFalsa()
        try:
            rc, _ = tx.rodar("gemini-pro", r5, "x", esquema_path=esq_arq(f"m{i}.json", ruim), te=te, vias=vias(f))
        except Exception as e:
            fails.append(f"N3: esquema {ruim} derrubou o executor ({type(e).__name__})")
            continue
        if rc != tx.RC_RECUSADO or f.chamadas:
            fails.append(f"N3: esquema malformado {ruim} tem de ser recusado sem chamada (rc={rc})")

    # (N6) excecao na validacao DEPOIS da chamada vira INVALIDO registrado
    validar_orig = tx.validar
    tx.validar = lambda *a, **k: (_ for _ in ()).throw(TypeError("validador quebrou"))
    try:
        f = ViaFalsa({"status_via": "SUCCESS", "texto": "", "estruturado": {"x": 1}, "negado": []})
        n0 = len(open(os.environ["TRABALHADOR_REGISTRO"], encoding="utf-8").read().splitlines())
        rc, _ = tx.rodar("gemini-pro", r5, "x", esquema_path=esq_arq("v.json", {"type": "object"}), te=te, vias=vias(f))
        n1 = len(open(os.environ["TRABALHADOR_REGISTRO"], encoding="utf-8").read().splitlines())
        if rc != tx.RC_INVALIDO or n1 != n0 + 1:
            fails.append(f"N6: excecao na validacao depois da chamada tem de virar INVALIDO registrado (rc={rc})")
    except Exception as e:
        fails.append(f"N6: excecao na validacao vazou ({type(e).__name__})")
    finally:
        tx.validar = validar_orig
    # (N6) spec comum inexistente nao vira link
    mon.evento("trab-link2", "e", "q", "OK", spec="docs/nao-existe.md")
    if "nao-existe.md'" in open(mon.gerar(), encoding="utf-8").read().replace("spec docs/nao-existe.md", ""):
        fails.append("N6: spec inexistente virou link")

    # (N5) texto do monitor aguenta campo nulo
    with open(os.environ["TRABALHADOR_REGISTRO"], "a", encoding="utf-8") as fh:
        fh.write('{"trabalho":null,"status":null,"etapa":null}\n')
    try:
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            mon.texto(5)
    except Exception as e:
        fails.append(f"N5: monitor texto quebrou com campo nulo ({type(e).__name__})")

    # ---------------- ressalvas da QA r3 ----------------
    # (A3) relativo e' resolvido contra a pasta corrente: pai do repo + caminho relativo roda
    f_cli = ViaFalsa()
    tx.VIAS, vias_orig = {"agy": f_cli, "ollama": f_cli}, tx.VIAS
    cwd_orig = os.getcwd()
    try:
        open(os.path.join(r5, "pedido-rel.md"), "w", encoding="utf-8").write("revise")
        os.chdir(os.path.dirname(r5))
        rc = _cli(["rodar", "--trabalhador", "gemini-pro", "--repo", r5, "--pedido",
                   os.path.join(os.path.basename(r5), "pedido-rel.md")])
        if rc != tx.RC_OK or len(f_cli.chamadas) != 1:
            fails.append(f"A3: pedido relativo a pasta corrente, dentro do repo, tem de rodar (rc={rc})")
    finally:
        os.chdir(cwd_orig)
        tx.VIAS = vias_orig
    # (A4) juncao/link dentro do repo apontando para fora: recusado (realpath)
    alvo_fora = os.path.join(tmp, "fora-juncao")
    os.makedirs(alvo_fora, exist_ok=True)
    open(os.path.join(alvo_fora, "seg.md"), "w", encoding="utf-8").write(SEGREDO)
    juncao = os.path.join(r5, "junc")
    criou = False
    if os.name == "nt":
        import subprocess
        criou = subprocess.run(["cmd", "/c", "mklink", "/J", juncao, alvo_fora], capture_output=True).returncode == 0
    else:
        try:
            os.symlink(alvo_fora, juncao)
            criou = True
        except OSError:
            pass
    if criou:
        f = ViaFalsa()
        rc, _ = tx.rodar("gemini-pro", r5, "x", [os.path.join("junc", "seg.md")], te=te, vias=vias(f))
        if rc != tx.RC_RECUSADO or f.chamadas:
            fails.append("A4: arquivo alcancado por juncao dentro do repo saiu do portao")
    else:
        print("aviso: juncao nao pode ser criada aqui; caso A4 nao rodou")
    # (A6) hardlink: o mesmo arquivo com dois nomes e' recusado
    origem_hl = os.path.join(tmp, "hl-origem.md")
    open(origem_hl, "w", encoding="utf-8").write(SEGREDO)
    try:
        os.link(origem_hl, os.path.join(r5, "hl.md"))
        f = ViaFalsa()
        rc, _ = tx.rodar("gemini-pro", r5, "x", ["hl.md"], te=te, vias=vias(f))
        if rc != tx.RC_RECUSADO or f.chamadas:
            fails.append("A6: hardlink dentro do repo para arquivo de fora saiu do portao")
    except OSError:
        print("aviso: hardlink nao suportado aqui; caso A6 nao rodou")

    # (monitor) EM-CURSO substituido por registro posterior da mesma etapa nao conta como em curso
    tot, _, _ = mon.agregar([{"trabalho": "t", "etapa": "QA", "status": "EM-CURSO"},
                             {"trabalho": "t", "etapa": "QA", "status": "OK"},
                             {"trabalho": "t", "etapa": "outra", "status": "EM-CURSO"}])
    if tot["em_curso"] != 1:
        fails.append(f"monitor contou {tot['em_curso']} em curso; esperado 1 (a etapa fechada saiu)")

    if fails:
        print("FAIL:")
        for x in fails:
            print("  -", x)
        return 1
    print("PASS: trabalhador_externo — portao fail-closed, so o pedido sai, esquema, erro declarado, "
          "registro sem conteudo, politica coerente")
    return 0


if __name__ == "__main__":
    sys.exit(run())
