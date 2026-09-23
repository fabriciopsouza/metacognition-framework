#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canario do pacote controle_projeto — exit 0 = PASS, exit 1 = FAIL.

POR QUE ESTE ARQUIVO EXISTE. As quatro regras do dono sao POLITICA: elas decidem o que a equipe ve
no portal e o que fica escondido. Politica errada nao da erro — ela simplesmente esconde a tarefa
certa, e ninguem descobre ate a reuniao em que faltou.

Cada regra e' testada por SABOTAGEM: parte-se de um projeto valido, quebra-se uma coisa por vez, e
exige-se que a regra reprove. Teste que so confirma o estado bom nao prova que a regra prende — foi
assim que dois gates deste framework passaram meses sendo decoracao.

Rodar: python tools/test_controle_projeto.py
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import controle_projeto as CP  # noqa: E402

try:
    # O console default do Windows e' cp1252, e um glifo fora dele derruba o `print` com
    # UnicodeEncodeError — matando o canario no meio, sem veredito, e levando o runner junto.
    # [ACHADO ALTA DO QA DA FRONTEIRA, rodada 2] aconteceu de verdade: 68 canarios deixaram de
    # rodar. As ferramentas ja se blindavam; os canarios, nao.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                    # pragma: no cover
    pass

falhou = []


def checar(nome, condicao, detalhe=""):
    if condicao:
        print(f"  ok   {nome}")
    else:
        print(f"  FAIL {nome} {detalhe}")
        falhou.append(nome)


# Um projeto minimo e VALIDO, com as situacoes que importam representadas de proposito:
#   S1 dentro do sprint, com executor      -> deve ir
#   S2 dentro do sprint, SEM executor      -> retido pela regra 2
#   S3 dentro do sprint, marcador de dono  -> retido: marcador nao e' executor
#   F1 fora do sprint, com executor        -> retido pela regra 1
#   F2 fora do sprint, executor sobrecarregado
#   A1 automatizavel, sem impedimento      -> regra 4, executavel
#   A2 automatizavel, dependencia aberta   -> regra 4, bloqueada
#   A3 classe nao permitida                -> regra 4 NAO alcanca (revisao humana)
PROJETO = {
    "nome": "teste",
    "estado": "estado.json",
    "pacote": {"versao_adotada": CP.VERSAO_PACOTE},
    "adotado": {n: True for n in CP.FEATURES},
    "agentes": ["agente"],
    "agente_responde_por": {"agente": "Humano Responsavel"},
    "capacidade": {"em_execucao_por_pessoa": 2},
    "auto": {"classes_permitidas": ["leitura", "coleta"]},
    "disponivel": ["token-portal"],
}
ESTADO = {
    "sprint": {"numero": 1, "inicio": "2026-08-20", "fim": "2026-09-02"},
    "itens": [
        {"id": "S1", "o_que": "dentro, com dono", "prazo": "2026-08-25",
         "responsavel": "Ana", "coluna": "para_fazer", "prioridade": 1},
        {"id": "S2", "o_que": "dentro, sem dono", "prazo": "2026-08-26",
         "responsavel": "", "coluna": "para_fazer", "prioridade": 2},
        {"id": "S3", "o_que": "dentro, marcador", "prazo": "2026-08-27",
         "responsavel": "A DEFINIR na abertura", "coluna": "para_fazer", "prioridade": 3},
        {"id": "F1", "o_que": "fora, com dono", "prazo": "2026-10-01",
         "responsavel": "Ana", "coluna": "para_fazer", "prioridade": 4},
        {"id": "F2", "o_que": "fora, dono cheio", "prazo": "2026-10-02",
         "responsavel": "Bruno", "coluna": "para_fazer", "prioridade": 5},
        {"id": "W1", "o_que": "em execucao", "prazo": "2026-08-28",
         "responsavel": "Bruno", "coluna": "em_execucao", "prioridade": 6},
        {"id": "W2", "o_que": "em execucao", "prazo": "2026-08-29",
         "responsavel": "Bruno", "coluna": "em_execucao", "prioridade": 7},
        {"id": "A1", "o_que": "coletar dado", "prazo": "2026-08-25", "auto": "coleta",
         "responsavel": "agente", "coluna": "para_fazer", "prioridade": 8,
         "requer": ["token-portal"]},
        {"id": "A2", "o_que": "ler resultado", "prazo": "2026-08-25", "auto": "leitura",
         "responsavel": "agente", "coluna": "para_fazer", "prioridade": 9,
         "depende_de": ["S1"]},
        {"id": "A3", "o_que": "aprovar valor", "prazo": "2026-08-25", "auto": "decisao",
         "responsavel": "agente", "coluna": "para_fazer", "prioridade": 10},
    ],
}


def ids(itens):
    return sorted(i["id"] for i in itens)


def sabotar(nome, mutacao, condicao, detalhe=""):
    """Quebra uma coisa e exige que a regra reprove."""
    e, p = copy.deepcopy(ESTADO), copy.deepcopy(PROJETO)
    mutacao(e, p)
    checar(f"sabotagem detectada: {nome}", condicao(e, p), detalhe)


def main() -> int:
    print("Regra 1 — so o sprint corrente vai para o portal:")
    r = CP.politica(ESTADO, PROJETO)
    checar("F1 e F2 ficam fora por estarem fora do sprint",
           {"F1", "F2"} <= {i for i, m in r["retidos"] if m == "fora do sprint corrente"})
    checar("S1 passa", "S1" in ids(r["lancaveis"]))
    # [REGRESSAO REAL 21/08/2026] a 1a versao olhava so o prazo e teria TIRADO 3 tarefas do quadro
    # do projeto SAC — as que ja estavam em execucao/concluidas com prazo fora da janela. Tarefa que
    # a equipe ja comecou nao pode sumir porque o sprint virou: o quadro e' tambem o historico.
    e_hist = copy.deepcopy(ESTADO)
    e_hist["itens"].append({"id": "H1", "o_que": "comecada, prazo fora", "prazo": "2026-10-20",
                            "responsavel": "Ana", "coluna": "em_execucao", "prioridade": 11})
    e_hist["itens"].append({"id": "H2", "o_que": "feita, prazo fora", "prazo": "2026-10-21",
                            "responsavel": "Ana", "coluna": "concluido", "prioridade": 12})
    vis = ids(CP.politica(e_hist, PROJETO)["lancaveis"])
    checar("tarefa EM EXECUCAO com prazo fora do sprint continua no quadro", "H1" in vis,
           "-> ela sumiria do quadro no dia em que o sprint virasse")
    checar("tarefa CONCLUIDA com prazo fora do sprint continua no quadro", "H2" in vis,
           "-> apagar o historico apaga o trabalho feito aos olhos de quem o fez")
    checar("mas ela NAO conta como pendencia do sprint",
           CP.sprint_concluido(e_hist, PROJETO)[2] == CP.sprint_concluido(ESTADO, PROJETO)[2] + 2,
           "-> entra no denominador porque esta visivel; o teste e' so que o numero seja coerente")

    sabotar("sprint apagado deixa de filtrar (e nao pode filtrar em silencio)",
            lambda e, p: e.pop("sprint"),
            lambda e, p: not any(m == "fora do sprint corrente" for _i, m in
                                 CP.politica(e, p)["retidos"]),
            "-> sem sprint declarado a regra tem de se declarar inativa, nao reter tudo")

    print("\nRegra 2 — so tarefa com executor e' lancada:")
    checar("S2 (vazio) retido", ("S2", "sem executor definido") in r["retidos"])
    checar("S3 (marcador 'A DEFINIR') retido tambem", ("S3", "sem executor definido") in r["retidos"],
           "-> marcador ja foi confundido com nome: 'A DEFINIR na abertura' virou 'responsavel: A'")
    for marcador in ("PENDENTE", "TBD", "N/A", "-", "a definir"):
        sabotar(f"marcador {marcador!r} nao passa por executor",
                lambda e, p, m=marcador: e["itens"][0].update(responsavel=m),
                lambda e, p: ("S1", "sem executor definido") in CP.politica(e, p)["retidos"])

    # [DEFEITO REAL 21/08/2026] a 1a versao casava marcador por SUBSTRING (`m in r`), e por isso
    # tratava "Ana-Maria", "Jean-Pierre" e "TBDaniel" como SEM EXECUTOR: "-" cabe em qualquer nome
    # hifenizado e "TBD" cabe em "TBDaniel". As tarefas dessas pessoas sumiriam do portal sem erro e
    # sem aviso — a pior forma de errar aqui, porque ninguem procura o que nao sabe que faltou.
    #
    # O canario anterior nao pegou porque so testava os marcadores PUROS. Caso bom e caso ruim
    # obvio nao cobrem a FRONTEIRA entre os dois, que e' exatamente onde este defeito morava.
    print("\n  a fronteira entre marcador e nome que o contem:")
    for nome, esperado in [
        ("Ana-Maria", False), ("Jean-Pierre", False), ("Maria-Clara Souza", False),
        ("TBDaniel", False), ("Ana Maria", False), ("José N/A Silva", False),
        ("ana definir", False), ("Andre", False), ("Pendencia Silva", False),
        ("-", True), ("N/A", True), ("TBD", True), ("A DEFINIR", True),
        ("A DEFINIR na abertura", True), ("PENDENTE - aguardando GQ", True),
        ("pendente", True), ("  A DEFINIR  ", True), ("", True), ("   ", True),
    ]:
        got = CP._sem_executor({"responsavel": nome}, {})
        checar(f"{nome!r} -> sem executor={esperado}", got == esperado,
               (f"-> deu {got}; nome tratado como marcador some do portal em silencio"
                if esperado is False else
                f"-> deu {got}; marcador tratado como nome cria cobranca sobre ninguem"))

    print("\nRegra 3 — sprint concluido pergunta antes de puxar:")
    feito, n, total = CP.sprint_concluido(ESTADO, PROJETO)
    checar("sprint em aberto nao pede adiantamento", not feito, f"-> {n}/{total}")
    e2 = copy.deepcopy(ESTADO)
    for i in e2["itens"]:
        if CP._no_sprint(i, e2["sprint"]):
            i["coluna"] = "concluido"
    checar("sprint todo concluido dispara a pergunta", CP.sprint_concluido(e2, PROJETO)[0])
    e3 = copy.deepcopy(ESTADO)
    e3["itens"] = [i for i in e3["itens"] if not CP._no_sprint(i, e3["sprint"])]
    checar("sprint VAZIO nao conta como concluido", not CP.sprint_concluido(e3, PROJETO)[0],
           "-> 'nao ha nada' e 'acabou tudo' sao estados diferentes")

    ad = CP.candidatos_adiantamento(ESTADO, PROJETO, 5)
    checar("adiantamento respeita o teto por pessoa",
           "F2" in [x[0] for x in ad["estourariam"]],
           "-> Bruno ja tem 2 em execucao e o teto e' 2; F2 nao pode entrar")
    checar("adiantamento nao puxa tarefa sem executor",
           all(not CP._sem_executor(i, PROJETO) for i in ad["escolhidos"]),
           "-> sem dono nao ha carga que calcular; puxar assim seria fingir capacidade")
    # [ACHADO ALTA-1 DO QA RODADA 2] a ordem de adiantamento saia de `i.get("prazo") or "9999"` —
    # STRING crua. '2026-12-1' < '2026-9-3' porque '1'<'9', entao DEZEMBRO era adiantado antes de
    # SETEMBRO. Nenhuma fixture tinha dois itens com prazos diferentes e a MESMA prioridade, entao
    # nada visitava esta linha.
    print("\n  a ordem do adiantamento e' por data e por prioridade, nao por texto:")
    e_ord = {"sprint": {"inicio": "2026-08-20", "fim": "2026-09-02"}, "itens": [
        {"id": "DEZ", "prioridade": 5, "prazo": "2026-12-1", "responsavel": "Ana",
         "coluna": "para_fazer"},
        {"id": "SET", "prioridade": 5, "prazo": "2026-9-3", "responsavel": "Ana",
         "coluna": "para_fazer"}]}
    checar("mesma prioridade: vence primeiro vem primeiro, mesmo sem zero a esquerda",
           [i["id"] for i in CP.candidatos_adiantamento(e_ord, {}, 5)["escolhidos"]] == ["SET", "DEZ"],
           "-> '2026-12-1' < '2026-9-3' como texto; dezembro era adiantado antes de setembro")

    # [ACHADO DA VARREDURA, nao de critico] `i.get("prioridade") or 999` — prioridade 0 significa a
    # MAIS ALTA, e' falsy, e virava 999: a tarefa mais urgente do projeto seria a ULTIMA a entrar.
    e_p0 = {"sprint": {"inicio": "2026-08-20", "fim": "2026-09-02"}, "itens": [
        {"id": "URGENTE", "prioridade": 0, "prazo": "2026-12-05", "responsavel": "Ana",
         "coluna": "para_fazer"},
        {"id": "NORMAL", "prioridade": 1, "prazo": "2026-12-01", "responsavel": "Ana",
         "coluna": "para_fazer"}]}
    checar("prioridade 0 e' a MAIS alta, nao a ausencia de prioridade",
           [i["id"] for i in CP.candidatos_adiantamento(e_p0, {}, 5)["escolhidos"]][0] == "URGENTE",
           "-> `or 999` fazia a tarefa mais urgente virar a menos urgente")
    checar("item SEM prioridade vai para o fim, nao para o comeco",
           [i["id"] for i in CP.candidatos_adiantamento(
               {"sprint": {"inicio": "2026-08-20", "fim": "2026-09-02"}, "itens": [
                   {"id": "SEMPRI", "prazo": "2026-10-01", "responsavel": "Ana",
                    "coluna": "para_fazer"},
                   {"id": "COMPRI", "prioridade": 3, "prazo": "2026-11-01", "responsavel": "Ana",
                    "coluna": "para_fazer"}]}, {}, 5)["escolhidos"]][0] == "COMPRI",
           "-> ausencia de prioridade nao pode virar prioridade maxima")

    # [ACHADO ALTA-3 DO QA RODADA 2] janela de sprint ilegivel desliga a regra 1 e libera TUDO.
    # Nao filtrar esta certo — reter por causa de um typo do dono seria pior. O errado era o
    # SILENCIO: prazo ilegivel de item ja era relatado; o do sprint, nao.
    print("\n  janela de sprint quebrada desliga o filtro, e isso tem de ser DITO:")
    checar("mes invalido no inicio e' detectado",
           CP.sprint_ilegivel({"sprint": {"inicio": "2026-13-40", "fim": "2026-08-31"}}, {}),
           "-> sem aviso, as sessenta tarefas viram lancaveis e parece so o sprint ter crescido")
    checar("janela invertida e' detectada",
           any("invertida" in x for x in
               CP.sprint_ilegivel({"sprint": {"inicio": "2026-09-30", "fim": "2026-08-31"}}, {})),
           "-> comeco depois do fim nao retem nada e nao avisa")
    checar("janela boa nao gera alarme falso",
           not CP.sprint_ilegivel({"sprint": {"inicio": "2026-08-20", "fim": "2026-09-02"}}, {}))
    # [ACHADO ALTA DO QA RODADA 3] `_sprint` devolvia o que estivesse la sem checar a FORMA:
    # `sprint: ["a","b"]` crashava o comando DEFAULT com AttributeError e traceback cru — enquanto
    # prazo malformado de item ja era relatado com elegancia. Valor validado, forma nao.
    for forma in (["a", "b"], "2026-08", 42, {}):
        est_f = {"sprint": forma, "itens": [{"id": "X", "prazo": "2026-01-01",
                                             "coluna": "para_fazer", "responsavel": "Ana"}]}
        try:
            CP.politica(est_f, {})
            crashou = False
        except Exception:
            crashou = True
        checar(f"sprint com forma {type(forma).__name__} nao crasha o comando", not crashou,
               "-> o usuario recebia traceback Python cru em vez de mensagem")
        if forma != {}:
            checar(f"sprint com forma {type(forma).__name__} e' DENUNCIADO",
                   bool(CP.sprint_ilegivel(est_f, {})),
                   "-> nao filtrar esta certo; calar nao")

    checar("projeto SEM sprint declarado nao e' 'janela quebrada'",
           not CP.sprint_ilegivel({"itens": []}, {}),
           "-> 'nao usa sprint' e 'sprint escrito errado' sao coisas diferentes")

    # [ACHADO ALTA DO QA RODADA 4] `float()` reconhece "nan"/"inf". O valor atravessava a fronteira,
    # gravava NaN no estado.json (JSON invalido pela RFC 8259), ordenava em PRIMEIRO lugar no
    # adiantamento, e ESCAPAVA do relatorio de ilegibilidade porque o teste era `is None` e nan nao
    # e' None. Corrompia sem deixar rastro — a pior combinacao possivel aqui.
    # [ACHADO DO REPARO 21/08/2026] `ast.parse` passa num arquivo a que faltam funcoes — ausencia e'
    # erro de EXECUCAO, nao de sintaxe. Eu confiava nele como prova de que a edicao ficou sa, e uma
    # remocao de codigo morto recortou seis funcoes junto sem que nada acusasse. Fumaca e' barata e
    # pega a classe inteira "edicao apagou mais do que devia".
    print("\n  fumaca: todo nome que o modulo usa existe de verdade?")
    import ast as _ast
    for arquivo in ("controle_projeto.py", "controle_sharepoint.py"):
        fonte = (Path(__file__).resolve().parent / arquivo).read_text(encoding="utf-8")
        arvore = _ast.parse(fonte)
        definidos = {n.name for n in _ast.walk(arvore)
                     if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef))}
        globais = {n.targets[0].id for n in arvore.body
                   if isinstance(n, _ast.Assign) and isinstance(n.targets[0], _ast.Name)}
        importados = {(a.asname or a.name).split(".")[0] for n in _ast.walk(arvore)
                      if isinstance(n, (_ast.Import, _ast.ImportFrom)) for a in n.names}
        chamados = {n.func.id for n in _ast.walk(arvore)
                    if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)}
        import builtins as _b
        faltando = sorted(c for c in chamados
                          if c not in definidos | globais | importados | set(dir(_b)))
        checar(f"{arquivo}: nenhuma funcao usada esta ausente", not faltando,
               f"-> chamadas sem definicao: {faltando}")

    print("\n  o canario de numeros tem UM caminho so para a moldura?")
    # [ACHADO ALTA DO QA RODADA 5] o laco de `main()` tinha uma COPIA da logica de moldura, e quando
    # `_e_historico` foi corrigida a copia ficou com a versao antiga: o auto-teste provava que a
    # funcao enxerga, enquanto o canario aprovava documento pelo outro caminho, com o defeito vivo.
    fonte_num = (Path(__file__).resolve().parent / "test_numeros_controle.py").read_text(
        encoding="utf-8")
    checar("uma leitura so de MOLDURA_HISTORICA (mais a definicao)",
           fonte_num.count("MOLDURA_HISTORICA") <= 2,
           f"-> {fonte_num.count('MOLDURA_HISTORICA')} usos; copia diverge")
    checar("nenhuma janela de caracteres sobrou fora de `_e_historico`",
           fonte_num.count("m.start() - 130") == 0,
           "-> a janela de 130 caracteres era exatamente o defeito corrigido")

    print("  numero: converte o que da' para ler, recusa o resto:")
    for cru, esperado in [
        ("3", 3), (" 3 ", 3), ("-1", -1), ("3.5", 3.5), ("3,5", 3.5), (".5", 0.5), ("3.", 3.0),
        (0, 0), (7, 7), (2.5, 2.5),
        ("nan", None), ("NaN", None), ("inf", None), ("-inf", None), ("Infinity", None),
        ("0x10", None), ("--3", None), ("tres", None), ("", None), (None, None),
        (True, None), (False, None), ([3], None), ({"a": 3}, None),
    ]:
        got = CP._num(cru)
        checar(f"_num({cru!r}) = {esperado!r}", got == esperado or (got is None and esperado is None),
               f"-> deu {got!r}")
    checar("nan nao escapa do relatorio de ilegibilidade",
           CP._num("nan") is None,
           "-> `is None` era o teste; nan nao e' None, entao o valor corrompido nao aparecia")

    # [ACHADO ALTA DO QA RODADA 4] o teto vinha de projeto.json por `.get()` cru e ia direto para
    # uma comparacao: teto "3" (string) reproduzia o MESMO TypeError, por outra porta, na mesma
    # funcao. Fronteira nao e' o `--receber`; e' TODO ponto onde valor de fora vira valor usado.
    print("\n  numero de CONFIGURACAO tambem passa pela fronteira:")
    e_teto = {"sprint": {"inicio": "2026-08-20", "fim": "2026-09-02"}, "itens": [
        {"id": "A", "prioridade": 1, "prazo": "2026-12-01", "responsavel": "Ana",
         "coluna": "para_fazer"}]}
    for cru, teto_esperado, tem_problema in [
        (3, 3, False), ("3", 3, False), (0, 0, False), ("0", 0, False),
        ("tres", 3, True), (None, 3, False), ([], 3, True),
    ]:
        pj = {"capacidade": {"em_execucao_por_pessoa": cru}} if cru is not None else {}
        r = CP.candidatos_adiantamento(e_teto, pj, 5)
        checar(f"teto {cru!r} -> {teto_esperado}{' e avisa' if tem_problema else ''}",
               r["teto"] == teto_esperado and bool(r.get("problema")) == tem_problema,
               f"-> teto={r['teto']!r} problema={r.get('problema')!r}")

    # [ACHADO DO QA RODADA 5] a mensagem afirmava "TODAS as tarefas aparecem como lancaveis" mesmo
    # quando nao era verdade, e o comando saia 0 com a configuracao corrompida. CI que olha exit
    # code leria "tudo bem" com o filtro desligado.
    print("\n  dado sujo: a tela nao pode se contradizer, e o exit nao pode dizer 'tudo bem':")
    import io as _io, contextlib as _ctx
    e_sujo = {"sprint": {"inicio": "2026-13-40", "fim": "2026-09-02"},
              "itens": [{"id": "T1", "prazo": "not-a-date", "coluna": "para_fazer",
                         "responsavel": "Ana"}]}
    _buf = _io.StringIO()
    with _ctx.redirect_stdout(_buf):
        codigo = CP.mostrar_situacao(e_sujo, {})
    tela = _buf.getvalue()
    checar("configuracao corrompida sai com codigo 1", codigo == 1, f"-> saiu {codigo}")
    checar("a tela nao afirma 'TODAS as tarefas' quando ha item retido",
           "TODAS as tarefas" not in tela,
           "-> 'PODE IR: 0' e 'TODAS lancaveis' apareciam juntos, sobre o mesmo item")
    checar("a janela quebrada e' dita", "DESLIGADA" in tela)
    checar("o prazo ilegivel tambem e' dito", "PRAZO ILEGIVEL" in tela)
    _buf2 = _io.StringIO()
    with _ctx.redirect_stdout(_buf2):
        limpo = CP.mostrar_situacao(ESTADO, PROJETO)
    checar("dado limpo continua saindo 0", limpo == 0, f"-> saiu {limpo}")

    print("\n  marcador de ausencia com tipo errado nao pode virar armadilha:")
    for m, esperado in [("A DEFINIR", False), (["A DEFINIR"], False), (42, False), (None, False)]:
        got = CP._sem_executor({"responsavel": "A"}, {"marcadores_de_ausencia": m})
        checar(f"executor 'A' com marcadores={m!r} -> sem executor={esperado}", got == esperado,
               "-> string era iterada caractere a caractere, e 'A' virava ausente")
    # o marcador CUSTOMIZADO escrito como string tem de continuar VALENDO. Cair no default
    # silenciosamente faria o projeto perder a regra que ele declarou.
    checar("marcador customizado escrito como string continua valendo",
           CP._sem_executor({"responsavel": "SEM DONO"}, {"marcadores_de_ausencia": "SEM DONO"}),
           "-> descartar a declaracao do projeto e cair no default e' perder a regra em silencio")

    print("\n  dia do mes que nao existe nao e' data:")
    for cru, vale in [("2026-02-30", False), ("2026-04-31", False), ("2026-13-01", False),
                      ("2026-02-28", True), ("2028-02-29", True), ("2026-2-9", True),
                      ("2026/8/25", True), ("  2026-8-25  ", True), ("2026-8-25extra", False),
                      ("", False), (None, False), (20260825, False)]:
        got = CP._data(cru)
        checar(f"_data({cru!r}) {'reconhece' if vale else 'recusa'}", bool(got) == vale,
               f"-> devolveu {got!r}")

    sabotar("teto de 0 impede qualquer adiantamento",
            lambda e, p: p["capacidade"].update(em_execucao_por_pessoa=0),
            lambda e, p: not CP.candidatos_adiantamento(e, p, 5)["escolhidos"])

    # [ACHADO ALTA DO QA 21/08/2026] carga era contada por string CRUA: "Bruno", "BRUNO" e "bruno "
    # viravam tres pessoas, a carga real de 3 aparecia como 1+1+1, e o teto de 2 deixava de proteger
    # quem ja estava cheio. Grafia inconsistente e' o normal em preenchimento manual.
    print("\n  identidade do executor nao pode depender de caixa nem de espaco:")
    e_caixa = {"sprint": {"inicio": "2026-08-20", "fim": "2026-09-02"}, "itens": [
        {"id": "K1", "responsavel": "Bruno", "coluna": "em_execucao", "prazo": "2026-08-21"},
        {"id": "K2", "responsavel": "BRUNO", "coluna": "em_execucao", "prazo": "2026-08-22"},
        {"id": "K3", "responsavel": "bruno ", "coluna": "em_execucao", "prazo": "2026-08-23"},
        {"id": "K4", "responsavel": " Bruno  Silva", "coluna": "em_execucao", "prazo": "2026-08-24"},
        {"id": "K5", "responsavel": "Bruno Silva", "coluna": "em_execucao", "prazo": "2026-08-25"},
        {"id": "K9", "responsavel": "Bruno", "coluna": "para_fazer", "prazo": "2026-12-01",
         "prioridade": 1}]}
    p_caixa = {"capacidade": {"em_execucao_por_pessoa": 2}}
    carga = CP.carga_atual(e_caixa, p_caixa)
    checar("tres grafias do mesmo nome contam como UMA pessoa", carga.get("bruno") == 3,
           f"-> carga saiu {carga}; grafia inconsistente fura o teto sem ninguem ver")
    checar("espaco duplo no meio do nome nao cria pessoa nova", carga.get("bruno silva") == 2,
           f"-> carga saiu {carga}")
    checar("adiantamento NAO puxa para quem ja estourou o teto por grafia diferente",
           not CP.candidatos_adiantamento(e_caixa, p_caixa, 5)["escolhidos"],
           "-> a regra 3 do dono ('sem sobrecarregar') fura em silencio")

    # [ACHADO ALTA DO QA 21/08/2026] prazo era comparado como STRING lexicografica: '2026-8-25' —
    # 25 de agosto, DENTRO do sprint — dava False contra '2026-09-02' porque '8' > '0'. A tarefa
    # ficava retida como "fora do sprint" e sumia do portal sem erro.
    print("\n  data comparada como DATA, nao como texto:")
    sp = {"inicio": "2026-08-20", "fim": "2026-09-02"}
    for prazo, dentro, por_que in [
        ("2026-08-25", True,  "ISO estrito, no meio da janela"),
        ("2026-8-25",  True,  "sem zero a esquerda — era o bug"),
        ("2026/8/25",  True,  "barra em vez de hifen"),
        ("2026-08-20", True,  "primeiro dia, fronteira inclusiva"),
        ("2026-09-02", True,  "ultimo dia, fronteira inclusiva"),
        ("2026-09-03", False, "um dia depois do fim"),
        ("2026-08-19", False, "um dia antes do inicio"),
        ("2026-9-3",   False, "sem zero a esquerda, FORA — nao pode virar dentro"),
    ]:
        got = CP._no_sprint({"prazo": prazo, "coluna": "para_fazer"}, sp, {})
        checar(f"prazo {prazo!r} -> dentro={dentro} ({por_que})", got == dentro,
               f"-> deu {got}")

    print("\n  prazo que nao e' data e' DITO, nunca tratado como fora:")
    ruins = CP.prazos_ilegiveis({"itens": [
        {"id": "Z1", "prazo": "banana"}, {"id": "Z2", "prazo": "2026-13-45"},
        {"id": "Z3", "prazo": "em breve"}, {"id": "Z4", "prazo": "2026-8-1"},
        {"id": "Z5", "prazo": ""}, {"id": "Z6"}]})
    checar("os 3 ilegiveis sao relatados", sorted(i for i, _c in ruins) == ["Z1", "Z2", "Z3"],
           f"-> relatou {ruins}")
    checar("data valida mal formatada NAO e' ilegivel", "Z4" not in [i for i, _c in ruins],
           "-> '2026-8-1' e' legivel; so precisa ser normalizada")
    checar("prazo vazio ou ausente nao entra na lista de ilegivel",
           not {"Z5", "Z6"} & {i for i, _c in ruins},
           "-> 'ainda nao tem prazo' e 'tem prazo quebrado' sao coisas diferentes")

    print("\nRegra 4 — automatizavel sem impedimento:")
    au = CP.automatizaveis(ESTADO, PROJETO)
    checar("A1 executavel agora", "A1" in [i["id"] for i, _ in au["agora"]])
    checar("A2 bloqueada por dependencia aberta", "A2" in [i["id"] for i, _ in au["bloqueadas"]])
    checar("A3 fora das classes permitidas", ("A3", "decisao") in au["fora_de_classe"],
           "-> 'tudo que envolver decisao, numero, valor, critico' e' revisado por humano")
    sabotar("credencial ausente bloqueia a auto-execucao",
            lambda e, p: p.__setitem__("disponivel", []),
            lambda e, p: "A1" in [i["id"] for i, _ in CP.automatizaveis(e, p)["bloqueadas"]],
            "-> requer `token-portal` e o projeto deixou de declarar que o tem")
    sabotar("item travado bloqueia a auto-execucao",
            lambda e, p: e["itens"][7].update(travado=True, travado_em="aprovacao da GQ"),
            lambda e, p: "A1" in [i["id"] for i, _ in CP.automatizaveis(e, p)["bloqueadas"]])
    sabotar("dependencia que nem existe bloqueia",
            lambda e, p: e["itens"][7].update(depende_de=["NAO-EXISTE"]),
            lambda e, p: "A1" in [i["id"] for i, _ in CP.automatizaveis(e, p)["bloqueadas"]],
            "-> id quebrado nao pode virar 'sem impedimento'")
    sabotar("classe permitida a mais NAO abre decisao por acidente",
            lambda e, p: p["auto"].update(classes_permitidas=["leitura"]),
            lambda e, p: "A3" in [i for i, _c in CP.automatizaveis(e, p)["fora_de_classe"]])

    print("\nRevisao de adocao — feature nova obriga o projeto a se pronunciar:")
    checar("projeto em dia passa", not CP.revisar_adocao(PROJETO)["novas"])
    p2 = copy.deepcopy(PROJETO)
    p2["adotado"].pop(sorted(CP.FEATURES)[0])
    checar("feature nao declarada aparece como pendente",
           sorted(CP.FEATURES)[0] in [n for n, _v, _o in CP.revisar_adocao(p2)["novas"]],
           "-> feature que nenhum projeto adota e' feature orfa")
    p3 = copy.deepcopy(PROJETO)
    p3["adotado"][sorted(CP.FEATURES)[0]] = {"usa": False, "por_que": "projeto sem portal"}
    checar("dispensa DECLARADA nao vira pendencia",
           not CP.revisar_adocao(p3)["novas"] and CP.revisar_adocao(p3)["dispensadas"],
           "-> dispensar com motivo e' resposta valida; o que nao vale e' o silencio")

    print("\nResolucao de caminho — nunca chutar:")
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp) / "proj"
        CP.iniciar(str(raiz))
        checar("--iniciar cria a declaracao", (raiz / CP.DECLARACAO).is_file())
        # [ACHADO ALTA DO QA RODADA 10] `--iniciar` e' o comando de ENTRADA de um projeto novo e
        # nao passava pela fronteira: caminho ilegal derrubava com OSError cru, e a chamada em
        # main() ficava FORA do try que captura ProjetoInvalido.
        for ruim, rotulo in [(123, "numero em vez de texto"), (["a"], "lista em vez de texto")]:
            try:
                CP.iniciar(ruim)
                r = "aceito"
            except CP.ProjetoInvalido:
                r = "recusado com mensagem"
            except Exception as ex:
                r = f"CRUA:{type(ex).__name__}"
            checar(f"--iniciar com {rotulo} -> recusado com mensagem",
                   r == "recusado com mensagem", f"-> {r}")
        checar("main() devolve 1 e nao traceback quando --iniciar recebe caminho ruim",
               CP.main(["--iniciar", str(raiz / "ja-existe-nao")]) in (0, 1),
               "-> a chamada estava fora do try; nem a mensagem chegava")
        achada, origem = CP.raiz_projeto(str(raiz))
        checar("resolve quando indicado", achada == raiz.resolve(), f"-> {origem}")
        try:
            CP.raiz_projeto(str(Path(tmp) / "nao-existe"))
            checar("pasta sem declaracao levanta erro", False, "-> aceitou caminho invalido")
        except CP.ProjetoInvalido:
            checar("pasta sem declaracao levanta erro", True)
        modelo = json.loads((raiz / CP.DECLARACAO).read_text(encoding="utf-8"))
        checar("o modelo nasce com todas as features declaradas",
               set(modelo["adotado"]) == set(CP.FEATURES),
               "-> senao o projeto novo ja nasce devendo revisao")

    print()
    if falhou:
        print(f"FAIL — {len(falhou)} verificacao(oes) falharam: {falhou}")
        return 1
    print("PASS — as 4 regras prendem, a revisao de adocao prende, e o resolvedor nao chuta.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
