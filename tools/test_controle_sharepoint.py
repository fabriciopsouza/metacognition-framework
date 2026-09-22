#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canario da ida e da volta da List do SharePoint — exit 0 = PASS, exit 1 = FAIL.

POR QUE ESTE ARQUIVO EXISTE. O importador do SharePoint ja recusou este CSV duas vezes, por duas
causas diferentes, e nas duas quem descobriu foi o dono olhando a tela de erro — nao um teste.

    1a  "Esquema invalido fornecido"   -> quebra de linha dentro de celula, separador ";", BOM
    2a  "Linhas 6 e 50 foram omitidos" -> NOME de pessoa que o catalogo nao resolveu

A 2a custou uma correcao ERRADA: o autor culpou o tamanho dos campos e enxugou o arquivo, jogando
fora tres colunas uteis. A evidencia contra essa hipotese ja estava na tela — 18 linhas passavam de
255 caracteres e importaram bem. O dono achou a causa contando as linhas a partir do primeiro DADO
em vez do cabecalho: as rejeitadas eram as duas unicas linhas de uma mesma pessoa.

Cada regra e' testada por SABOTAGEM contra um projeto de mentira montado aqui — o canario nao pode
depender de nenhum projeto real existir na maquina, senao ele so roda na maquina de uma pessoa.

Rodar: python tools/test_controle_sharepoint.py
"""
from __future__ import annotations

import copy
import csv
import io
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import controle_projeto as CP    # noqa: E402
import controle_sharepoint as CS  # noqa: E402

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


PROJETO = {
    "nome": "teste", "estado": "estado.json",
    "adotado": {"sharepoint-list": True},
    "sharepoint": {
        "pessoas": "pessoas.json",
        "list": {
            "saida": "saida.csv", "retorno": "retorno.csv", "detalhe": "detalhe.json",
            "colunas": ["id", "titulo", "responsavel", "situacao", "prazo", "o_que_fazer"],
            "mapa": {"titulo": "detalhe.titulo", "o_que_fazer": "detalhe.o_que_fazer"},
            "campos_da_list": ["responsavel", "situacao", "prazo", "prioridade"],
            "situacao": {"para_fazer": "A fazer", "concluido": "Concluído"},
            "responsavel_no_import": False,
            "limite_coluna": 250,
        },
    },
}
ESTADO = {
    "prazo_externo": "2026-11-01",
    "itens": [
        {"id": "T1", "responsavel": "Amanda Damasceno", "coluna": "para_fazer",
         "prazo": "2026-08-25", "prioridade": 1},
        {"id": "T2", "responsavel": "A DEFINIR", "coluna": "para_fazer",
         "prazo": "2026-08-26", "prioridade": 2, "depende_de": ["T1"]},
    ],
}
DETALHE = {"itens": [
    # os passos numerados com QUEBRA DE LINHA dentro: foi exatamente isto que derrubou o 1o import
    {"id": "T1", "titulo": "Fazer a coisa",
     "o_que_fazer": "1- primeiro passo\n2- segundo passo\n3- terceiro"},
    {"id": "T2", "titulo": "Fazer a outra", "o_que_fazer": "1- passo unico"},
]}
PESSOAS = {"pessoas": [
    {"projeto": "Amanda Damasceno", "ad": "Amanda D Damasceno", "email": "amanda@empresa.com"}]}


def montar(tmp, projeto=None, estado=None):
    """Um projeto de mentira em disco. Le do ARQUIVO, porque o que o SharePoint recusa e' o
    arquivo — verificar a estrutura em memoria nao prova nada sobre o que sai."""
    raiz = Path(tmp)
    (raiz / CP.DECLARACAO).write_text(json.dumps(projeto or PROJETO, ensure_ascii=False),
                                      encoding="utf-8")
    (raiz / "estado.json").write_text(json.dumps(estado or ESTADO, ensure_ascii=False),
                                      encoding="utf-8")
    (raiz / "detalhe.json").write_text(json.dumps(DETALHE, ensure_ascii=False), encoding="utf-8")
    (raiz / "pessoas.json").write_text(json.dumps(PESSOAS, ensure_ascii=False), encoding="utf-8")
    return raiz


def exportado(raiz):
    p, e = CP.carregar(raiz)
    codigo = CS.exportar(raiz, p, e)
    bruto = (raiz / "saida.csv").read_bytes()
    return codigo, bruto, list(csv.DictReader(io.StringIO(bruto.decode("utf-8"))))


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        raiz = montar(tmp)
        codigo, bruto, linhas = exportado(raiz)

        print("A ida:")
        checar("exportar termina em 0", codigo == 0, f"-> {codigo}")
        checar("uma linha por item", len(linhas) == len(ESTADO["itens"]))
        checar("`mapa` traz texto do arquivo de detalhe",
               linhas[0]["titulo"] == "Fazer a coisa",
               "-> sem isto a List sai com o id no lugar do titulo")

        print("\nFormato que o importador aceita (causa da 1a recusa):")
        checar("sem BOM", not bruto.startswith(b"\xef\xbb\xbf"))
        checar("separador virgula", bruto.split(b"\n")[0].count(b",") >= 5)
        checar("uma linha fisica por linha logica", bruto.count(b"\n") == len(linhas) + 1,
               "-> passo numerado com quebra dentro da celula derruba o import inteiro")
        checar("os passos numerados sobreviveram na mesma linha",
               "1- primeiro passo 2- segundo passo" in linhas[0]["o_que_fazer"],
               "-> achatar nao pode APAGAR o conteudo, so a quebra")

        print("\nO nome NAO vai no import (causa da 2a recusa):")
        checar("responsavel vazio em todas as linhas",
               all(not l["responsavel"] for l in linhas),
               "-> nome que o catalogo nao resolve derruba a linha inteira, em silencio")

        # SABOTAGEM: a traducao de nome ja esteve neste codigo e pode voltar sem ninguem notar.
        p2 = copy.deepcopy(PROJETO)
        p2["sharepoint"]["list"]["responsavel_no_import"] = True
        raiz2 = montar(tempfile.mkdtemp(), projeto=p2)
        _c, _b, l2 = exportado(raiz2)
        checar("sabotagem: com responsavel_no_import=true o nome SAI (e a flag e' o unico jeito)",
               l2[0]["responsavel"] == "Amanda Damasceno",
               "-> a flag tem de ser a unica porta; se o nome sair sem ela, a protecao e' fingida")
        checar("mesmo com a flag ligada, MARCADOR nao vira nome",
               l2[1]["responsavel"] == "",
               "-> 'A DEFINIR' ja virou 'responsavel: A' num cartao real")

        # [ACHADO ALTA DO QA 21/08/2026] a migracao perdeu o fallback `titulo or o_que[:80]` que a
        # ferramenta antiga do projeto tinha. Item ainda sem entrada no de-para exportava com titulo
        # VAZIO, sem erro. A alegacao de "identico byte a byte" valia para UM estado — aquele em que
        # todos os ids batiam. Sobrevivencia do estado testado nao e' invariante do codigo.
        print("\n  item sem entrada no detalhe nao pode sair em branco:")
        pf = copy.deepcopy(PROJETO)
        pf["sharepoint"]["list"]["mapa"]["titulo"] = "detalhe.titulo|o_que:40"
        ef = copy.deepcopy(ESTADO)
        ef["itens"].append({"id": "T9", "responsavel": "Amanda Damasceno", "coluna": "para_fazer",
                            "prazo": "2026-08-30", "prioridade": 3,
                            "o_que": "Levantar as formulas do painel de vendas com a area"})
        raizf = montar(tempfile.mkdtemp(), projeto=pf, estado=ef)
        _c, _b, lf = exportado(raizf)
        novo = [l for l in lf if l["id"] == "T9"][0]
        checar("titulo cai para o texto da tarefa quando o detalhe nao tem o item",
               novo["titulo"].startswith("Levantar as formulas"),
               f"-> saiu {novo['titulo']!r}; linha em branco na List que ninguem entende")
        checar("o corte declarado na cadeia e' respeitado", len(novo["titulo"]) <= 40,
               f"-> {len(novo['titulo'])} caracteres; titulo de cartao nao e' paragrafo")
        checar("item COM detalhe continua usando o titulo escrito a mao",
               [l for l in lf if l["id"] == "T1"][0]["titulo"] == "Fazer a coisa",
               "-> o fallback nao pode atropelar o que foi escrito de proposito")

        # [ACHADO MEDIA DO QA RODADA 2] `v[:limite] if limite else v` — corte 0 e' FALSY e devolvia
        # o valor INTEIRO. Mesma classe do teto falsy que o ADR-113 registra como achado do canario,
        # nao propagada ao vizinho no mesmo commit. A licao do dono e' explicita: correcao num fluxo
        # aplica aos irmaos NA MESMA iteracao.
        # [ACHADO ALTA DO QA RODADA 5] `projeto.json` e' editado a mao, e tipo errado ali nao dava
        # erro de configuracao: dava TypeError/AttributeError com traceback cru no meio da
        # exportacao. Fronteira nao e' o `--receber`; e' TODO ponto onde valor de fora vira usado.
        print("\n  declaracao com tipo errado vira MENSAGEM, nao traceback:")
        for chave, valor, aceita in [
            ("limite_coluna", "250", True), ("limite_coluna", 250, True),
            ("limite_coluna", "duzentos", False),
            ("situacao", ["nao", "e", "dict"], False), ("colunas", "id", False),
            ("mapa", "x", False), ("campos_da_list", {"a": 1}, False),
            ("responsavel_no_import", "sim", False),
        ]:
            try:
                CS._conf({"sharepoint": {"list": {chave: valor}}})
                deu = True
            except CS.ConfiguracaoInvalida:
                deu = False
            except Exception as ex:
                deu = None
                checar(f"{chave}={valor!r} nao levanta excecao crua", False,
                       f"-> {type(ex).__name__}: {ex}")
            if deu is not None:
                checar(f"declaracao {chave}={valor!r} -> {'aceita' if aceita else 'recusada'}",
                       deu == aceita, "-> tipo errado tem de virar ConfiguracaoInvalida")
        try:
            CS._conf({"sharepoint": {"list": ["nao", "e", "dict"]}})
            ok_forma = False
        except CS.ConfiguracaoInvalida:
            ok_forma = True
        checar("`sharepoint.list` que nao e' objeto tambem e' recusado", ok_forma)

        print("\n  corte declarado na cadeia, inclusive zero:")
        conf = {"mapa": {"titulo": "o_que:0", "outro": "o_que:5", "livre": "o_que"}}
        item = {"o_que": "texto bem longo aqui"}
        checar("corte 0 devolve vazio, nao o valor inteiro",
               CS._valor("titulo", item, {}, conf, {}) == "",
               f"-> deu {CS._valor('titulo', item, {}, conf, {})!r}")
        checar("corte 5 corta em 5", CS._valor("outro", item, {}, conf, {}) == "texto")
        checar("sem corte devolve inteiro",
               CS._valor("livre", item, {}, conf, {}) == "texto bem longo aqui")
        checar("cadeia de 3 origens usa a primeira COM valor",
               CS._valor("x", {"b": "", "c": "achou"}, {}, {"mapa": {"x": "a|b|c"}}, {}) == "achou",
               "-> origem vazia no meio da cadeia nao pode encerrar a busca")

        print("\nA volta:")
        (raiz / "retorno.csv").write_text(
            "id,responsavel,situacao,prazo,titulo\n"
            "T1,i:0#.f|membership|amanda@empresa.com,Concluído,2026-08-25,TITULO NOVO\n"
            "T2,amanda@empresa.com,A fazer,2026-12-30,\n"
            "ZZ,alguem,A fazer,,\n", encoding="utf-8")
        p, e = CP.carregar(raiz)
        CS.receber(raiz, p, e, confirmar=True)
        depois = json.loads((raiz / "estado.json").read_text(encoding="utf-8"))
        por_id = {i["id"]: i for i in depois["itens"]}
        checar("claims string vira o nome do projeto",
               por_id["T1"]["responsavel"] == "Amanda Damasceno",
               f"-> ficou {por_id['T1']['responsavel']!r}")
        checar("e-mail tambem vira o nome do projeto",
               por_id["T2"]["responsavel"] == "Amanda Damasceno")
        checar("situacao volta para a coluna interna", por_id["T1"]["coluna"] == "concluido")
        checar("prazo pode ser mudado na List", por_id["T2"]["prazo"] == "2026-12-30",
               "-> reuniao de status replaneja; bloquear obriga a abrir o repo no meio da reuniao")
        checar("titulo NAO pode ser mudado na List", "TITULO NOVO" not in json.dumps(depois),
               "-> titulo e' ESTRUTURA: nasce de elicitacao, nao de reuniao de status")
        checar("toda mudanca deixou historico",
               all(i.get("historico") for i in depois["itens"]),
               "-> prazo que muda sem rastro e' prazo que ninguem explica tres semanas depois")

        # [ACHADO ALTA DO QA RODADA 4] situacao nao mapeada caia num `continue` seco: nao entrava
        # em `mudancas`, nem em `ignorados`, nem em `recusados`. Sumia sem uma palavra — o
        # "passo de volta destroi dado em silencio" que este modulo existe para evitar.
        print("\n  a volta nao pode DESCARTAR valor em silencio:")
        raiz_r = montar(tempfile.mkdtemp())
        (raiz_r / "retorno.csv").write_text(
            "id,situacao,prioridade,prazo\n"
            "T1,Em Revisao,2,2026-08-25\n"          # situacao fora do de-para
            "T2,Concluído,tres,2026-99-99\n",       # prioridade e prazo ilegiveis
            encoding="utf-8")
        pr, er = CP.carregar(raiz_r)
        import io as _io, contextlib as _ctx
        buf = _io.StringIO()
        with _ctx.redirect_stdout(buf):
            CS.receber(raiz_r, pr, er, confirmar=True)
        saida = buf.getvalue()
        for cru in ("Em Revisao", "tres", "2026-99-99"):
            checar(f"valor ilegivel {cru!r} e' RELATADO, nao descartado", cru in saida,
                   "-> sumir calado e' o defeito que este modulo existe para nao ter")
        depois_r = json.loads((raiz_r / "estado.json").read_text(encoding="utf-8"))
        por_id_r = {i["id"]: i for i in depois_r["itens"]}
        checar("valor ilegivel NAO entra no estado",
               por_id_r["T2"].get("prioridade") != "tres" and por_id_r["T2"].get("prazo") != "2026-99-99",
               "-> gravar o que nao se sabe ler mata o comando seguinte")
        checar("valor LEGIVEL na mesma linha continua entrando",
               por_id_r["T1"].get("prioridade") == 2,
               "-> recusar um campo nao pode descartar a linha inteira")

        # [ACHADO ALTA DO QA RODADA 8] `detalhe.json` e `pessoas.json` eram lidos CRUS, fora da
        # fronteira. BOM (padrao de editor no Windows), Latin-1 (acento salvo em ANSI) e forma
        # errada derrubavam --exportar e --receber com traceback — os TRES modos de falha que a
        # fronteira existe para eliminar, nos dois arquivos que um projeto MAIS edita a mao.
        #
        # A licao ja estava escrita em comentario neste modulo desde a rodada 5 ("fronteira e' TODO
        # ponto onde valor de fora vira valor usado"). Escrever a licao nao aplica a licao.
        print("\n  os arquivos AUXILIARES tambem sao fronteira:")
        raiz_aux = montar(tempfile.mkdtemp())
        base = (raiz_aux / "detalhe.json").read_bytes()
        for conteudo, o_que, aceita in [
            (b"\xef\xbb\xbf" + base, "detalhe com BOM (arquivo CORRETO)", True),
            ('{"itens": [{"id":"T1","titulo":"caf\u00e9"}]}'.encode("latin-1"),
             "detalhe em Latin-1", False),
            (json.dumps({"itens": "nao e lista"}).encode("utf-8"), "detalhe com forma errada", False),
            (json.dumps({"itens": [{"sem": "id"}]}).encode("utf-8"), "detalhe com item sem id", False),
            (b"{quebrado", "detalhe com typo de JSON", False),
        ]:
            (raiz_aux / "detalhe.json").write_bytes(conteudo)
            try:
                pa, ea = CP.carregar(raiz_aux)
                CS.exportar(raiz_aux, pa, ea)
                r = "aceito"
            except (CS.ConfiguracaoInvalida, CP.ProjetoInvalido):
                r = "recusado com mensagem"
            except Exception as ex:
                r = f"CRUA:{type(ex).__name__}"
            checar(f"{o_que} -> {'aceito' if aceita else 'recusado com mensagem'}",
                   r == ("aceito" if aceita else "recusado com mensagem"),
                   f"-> {r}; traceback cru e' o defeito que a fronteira existe para nao ter")

        (raiz_aux / "detalhe.json").write_bytes(base)
        (raiz_aux / "retorno.csv").write_text("id,situacao\nT1,A fazer\n", encoding="utf-8")
        for conteudo, o_que in [
            (json.dumps({"pessoas": "nao e lista"}).encode("utf-8"), "pessoas com forma errada"),
            (json.dumps({"pessoas": ["nao e objeto"]}).encode("utf-8"), "pessoas com entrada crua"),
            ('{"pessoas":[{"projeto":"caf\u00e9"}]}'.encode("latin-1"), "pessoas em Latin-1"),
            (b"[]", "pessoas sem a chave `pessoas`"),
        ]:
            (raiz_aux / "pessoas.json").write_bytes(conteudo)
            try:
                pa, ea = CP.carregar(raiz_aux)
                CS.receber(raiz_aux, pa, ea, confirmar=False)
                r = "aceito"
            except (CS.ConfiguracaoInvalida, CP.ProjetoInvalido):
                r = "recusado com mensagem"
            except Exception as ex:
                r = f"CRUA:{type(ex).__name__}"
            checar(f"{o_que} -> recusado com mensagem", r == "recusado com mensagem", f"-> {r}")

        # estrutural: nenhuma leitura de JSON do pacote pode escapar da fronteira
        print("\n  nenhuma leitura de JSON do pacote escapa da fronteira:")
        # Por AST, e nao por texto: a primeira versao usava regex sobre o fonte e acusou o
        # DOCSTRING de `_ler_json`, que CITA `json.loads(read_text(...))` para explicar o defeito.
        # Grep confunde codigo com prosa; AST olha chamada de verdade.
        import ast as _a

        def _leituras_cruas(fonte: str) -> list[int]:
            """Leitura de JSON externo fora das funcoes guardadas.

            [ACHADO MEDIA DO QA RODADA 9] a primeira versao so reconhecia a forma canonica
            `json.loads(x.read_text())`, e cinco escritas equivalentes passavam: `from json import
            loads`, `import json as j`, `getattr(json, "loads")`, `json.load(open(p))` e
            `json.loads(open(p).read())`. A ADR afirmava "NENHUMA leitura escapa" — ou a checagem
            cobre, ou a frase muda. Cobrir e' barato."""
            arvore = _a.parse(fonte)
            guardadas = {"_ler_json", "ler_texto"}
            dentro = set()
            for no in _a.walk(arvore):
                if isinstance(no, _a.FunctionDef) and no.name in guardadas:
                    dentro.update(id(x) for x in _a.walk(no))

            # nomes que se referem a json.load/loads, seja como for que tenham chegado ali
            apelidos = {"json"}
            soltos = set()
            for no in _a.walk(arvore):
                if isinstance(no, _a.Import):
                    for a in no.names:
                        if a.name == "json":
                            apelidos.add(a.asname or "json")
                elif isinstance(no, _a.ImportFrom) and no.module == "json":
                    for a in no.names:
                        if a.name in ("load", "loads"):
                            soltos.add(a.asname or a.name)

            def _e_json_load(alvo) -> bool:
                if isinstance(alvo, _a.Attribute) and alvo.attr in ("load", "loads"):
                    return isinstance(alvo.value, _a.Name) and alvo.value.id in apelidos
                if isinstance(alvo, _a.Name):                      # from json import loads
                    return alvo.id in soltos
                if isinstance(alvo, _a.Call) and isinstance(alvo.func, _a.Name) \
                        and alvo.func.id == "getattr":             # getattr(json, "loads")
                    return (len(alvo.args) >= 2 and isinstance(alvo.args[0], _a.Name)
                            and alvo.args[0].id in apelidos
                            and isinstance(alvo.args[1], _a.Constant)
                            and alvo.args[1].value in ("load", "loads"))
                return False

            achados = []
            for no in _a.walk(arvore):
                if not isinstance(no, _a.Call) or id(no) in dentro or not _e_json_load(no.func):
                    continue
                # so acusa quando o argumento LE ARQUIVO — `json.loads(json.dumps(x))` e' copia
                # profunda, nao entrada externa, e nao tem nada a ver com fronteira.
                le = False
                for d in _a.walk(no):
                    if isinstance(d, _a.Attribute) and d.attr in ("read_text", "read_bytes", "read"):
                        le = True
                    if isinstance(d, _a.Name) and d.id == "open":
                        le = True
                if le:
                    achados.append(no.lineno)
            return achados

        def _escritas_cruas(fonte: str) -> list[int]:
            """Escrita de arquivo fora de `escrever_texto`.

            [ACHADO ALTA DO QA RODADA 11] a checagem estrutural so olhava LEITURA, e os dois pontos
            de escrita do pacote crashavam com PermissionError cru — inclusive o `--receber
            --confirmar`, o unico comando que PERSISTE mudanca."""
            arvore = _a.parse(fonte)
            dentro = set()
            for no in _a.walk(arvore):
                if isinstance(no, _a.FunctionDef) and no.name == "escrever_texto":
                    dentro.update(id(x) for x in _a.walk(no))
            achados = []
            for no in _a.walk(arvore):
                if id(no) in dentro:
                    continue
                if isinstance(no, _a.Call) and isinstance(no.func, _a.Attribute) \
                        and no.func.attr in ("write_text", "write_bytes", "mkdir", "unlink"):
                    achados.append(no.lineno)
                # `x.open("w")` / `open(x, "w")`
                if isinstance(no, _a.Call):
                    modo = next((a.value for a in no.args
                                 if isinstance(a, _a.Constant) and isinstance(a.value, str)
                                 and set(a.value) <= set("rwxabt+")), None)
                    e_open = (isinstance(no.func, _a.Attribute) and no.func.attr == "open") or \
                             (isinstance(no.func, _a.Name) and no.func.id == "open")
                    if e_open and modo and any(c in modo for c in "wax"):
                        achados.append(no.lineno)
            return sorted(set(achados))

        for arquivo in ("controle_base.py", "controle_projeto.py", "controle_sharepoint.py"):
            fonte = (Path(__file__).resolve().parent / arquivo).read_text(encoding="utf-8")
            cruas = _leituras_cruas(fonte)
            checar(f"{arquivo}: nenhuma leitura de JSON escapa de _ler_json", not cruas,
                   f"-> linhas {cruas}; arquivo externo lido cru volta a crashar com traceback")
            escritas = _escritas_cruas(fonte)
            checar(f"{arquivo}: nenhuma escrita escapa de escrever_texto", not escritas,
                   f"-> linhas {escritas}; escrita crua crasha com PermissionError")
        checar("o detector de escrita pega uma escrita crua de verdade",
               _escritas_cruas("def f(p):\n    p.write_text('x')\n"),
               "-> o detector parou de enxergar e vira carimbo")
        checar("o detector de escrita pega open(modo w)",
               _escritas_cruas("def f(p):\n    with p.open('w') as h:\n        h.write('x')\n"))
        checar("e NAO acusa leitura", not _escritas_cruas("def f(p):\n    return p.read_text()\n"))
        # auto-teste do detector: ele ainda enxerga?
        # os CINCO desvios que a rodada 9 achou, cada um como caso proprio
        for fonte, rotulo in [
            ("import json\ndef f(p):\n    return json.loads(p.read_text())\n", "forma canonica"),
            ("from json import loads\ndef f(p):\n    return loads(p.read_text())\n",
             "from json import loads"),
            ("import json as j\ndef f(p):\n    return j.loads(p.read_text())\n", "alias do modulo"),
            ("import json\ndef f(p):\n    return getattr(json, 'loads')(p.read_text())\n",
             "getattr"),
            ("import json\ndef f(p):\n    return json.load(open(p))\n", "open() em vez de read_text"),
            ("import json\ndef f(p):\n    return json.loads(open(p).read())\n", "open().read()"),
        ]:
            checar(f"o detector pega: {rotulo}", _leituras_cruas(fonte),
                   "-> escrita equivalente que dribla o detector torna a alegacao falsa")
        checar("e NAO acusa copia profunda nem citacao em docstring",
               not _leituras_cruas('import json\ndef f(x):\n    """cita json.loads(read_text())"""\n'
                                   "    return json.loads(json.dumps(x))\n"),
               "-> acusar prosa treina a pessoa a ignorar o vermelho")

        print("\n  o CSV da volta tambem passa pela fronteira:")
        raiz_csv = montar(tempfile.mkdtemp())
        for conteudo, o_que, aceita in [
            ("id,situacao\nT1,A fazer\n".encode("utf-8"), "retorno em UTF-8", True),
            (b"\xef\xbb\xbfid,situacao\nT1,A fazer\n", "retorno com BOM", True),
            ("id,responsavel\nT1,Jos\u00e9\n".encode("latin-1"), "retorno em Latin-1", False),
        ]:
            (raiz_csv / "retorno.csv").write_bytes(conteudo)
            pc, ec = CP.carregar(raiz_csv)
            try:
                CS.receber(raiz_csv, pc, ec, confirmar=False)
                r = "aceito"
            except CP.ProjetoInvalido:
                r = "recusado com mensagem"
            except Exception as ex:
                r = f"CRUA:{type(ex).__name__}"
            checar(f"{o_que} -> {'aceito' if aceita else 'recusado com mensagem'}",
                   r == ("aceito" if aceita else "recusado com mensagem"),
                   f"-> {r}; o docstring chama esse arquivo de 'preenchido por gente numa planilha'")

        print("\nSeparador da volta e adesao:")
        (raiz / "retorno.csv").write_text("id;situacao\nT1;A fazer\n", encoding="utf-8")
        p, e = CP.carregar(raiz)
        CS.receber(raiz, p, e, confirmar=True)
        d3 = json.loads((raiz / "estado.json").read_text(encoding="utf-8"))
        checar("volta com ';' tambem e' lida",
               {i["id"]: i for i in d3["itens"]}["T1"]["coluna"] == "para_fazer",
               "-> o separador segue o que a automacao gravar; detectar e' mais barato que combinar")

        p4 = copy.deepcopy(PROJETO)
        p4["adotado"]["sharepoint-list"] = {"usa": False, "por_que": "projeto sem SharePoint"}
        raiz4 = montar(tempfile.mkdtemp(), projeto=p4)
        checar("projeto que dispensou a feature e' recusado, nao servido em silencio",
               CS.main(["--projeto", str(raiz4), "--exportar"]) == 1)

        # CAMINHO FORA DA RAIZ, PELA CLI — e a distincao importa.
        #
        # Os testes deste arquivo chamavam `CS.exportar(...)`/`CS.receber(...)`
        # DIRETO. A funcao interna LEVANTAR `ProjetoInvalido` e' o comportamento
        # certo dela; o defeito morava um nivel acima, no `main()`, que capturava
        # so' `ConfiguracaoInvalida` e deixava `ProjetoInvalido` sair como
        # traceback Python cru — no modulo cujas treze rodadas de QA foram
        # gastas justamente para trocar stack trace por mensagem.
        #
        # Nenhum teste exercitava a CLI com `"../"` no caminho, entao a lacuna
        # nao era do codigo: era do ANGULO de onde se olhava.
        # [achado bloqueante do QA de 18/09/2026]
        for campo in ("saida", "retorno"):
            pf = copy.deepcopy(PROJETO)
            pf["sharepoint"]["list"][campo] = "../fora-da-raiz.csv"
            raizf = montar(tempfile.mkdtemp(), projeto=pf)
            acao = "--exportar" if campo == "saida" else "--receber"
            try:
                codigo = CS.main(["--projeto", str(raizf), acao])
                estourou = False
            except Exception as erro:           # noqa: BLE001 — e' o ponto do teste
                codigo, estourou = None, type(erro).__name__
            checar(f"`{campo}` FORA da raiz e' mensagem, nao traceback (pela CLI)",
                   estourou is False and codigo == 1,
                   f"-> saiu {estourou or codigo}; `projeto.json` e' editado a mao e "
                   f"'../' colado por engano nao pode virar stack trace")

        p5 = copy.deepcopy(PROJETO)
        p5["sharepoint"]["list"]["detalhe"] = "nao-existe.json"
        raiz5 = montar(tempfile.mkdtemp(), projeto=p5)
        checar("detalhe apontando para arquivo inexistente e' erro DECLARADO",
               CS.main(["--projeto", str(raiz5), "--exportar"]) == 1,
               "-> silenciar viraria uma List de titulos vazios que ninguem entenderia")

    print()
    if falhou:
        print(f"FAIL — {len(falhou)} verificacao(oes) falharam: {falhou}")
        return 1
    print("PASS — a ida sai no formato aceito e sem nome; a volta traduz, filtra e deixa rastro.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
