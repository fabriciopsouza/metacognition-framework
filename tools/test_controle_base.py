#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canario da FRONTEIRA do pacote controle_* — exit 0 = PASS, exit 1 = FAIL.

POR QUE ESTE ARQUIVO EXISTE, e a razao e' medida, nao estetica.

O pacote passou por cinco rodadas de critica adversarial e as cinco reprovaram. Olhando os achados
juntos, **quase todos moram na mesma camada**: converter, validar ou resolver um valor que veio de
fora. E a camada estava espalhada entre dois modulos — o que produziu, na rodada 5, o achado que
fechou o argumento: a validacao de tipo existia num e faltava no irmao, lendo o MESMO `projeto.json`.

Diante disso o dono mandou **reabrir o desenho**. A fronteira virou `tools/controle_base.py`, e este
canario e' o dela — separado, porque a densidade de defeito aqui foi muito maior que no resto.

CADA CASO ABAIXO E' UMA CICATRIZ. Nenhum e' hipotetico: todos vieram de um defeito reproduzido, seja
por um critico, seja pela varredura de classe, seja pela CLI real do projeto.

Rodar: python tools/test_controle_base.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import controle_base as CB  # noqa: E402

falhou = []


def checar(nome, condicao, detalhe=""):
    if condicao:
        print(f"  ok   {nome}")
    else:
        print(f"  FAIL {nome} {detalhe}")
        falhou.append(nome)


def main() -> int:
    print("_num — converter ou recusar, nunca gravar o que nao se sabe ler:")
    # cicatriz 1 (rodada 3): "-1" e "3.5" viravam STRING no estado porque `.isdigit()` recusa sinal
    #                        e ponto; o comando seguinte MORRIA com TypeError.
    # cicatriz 2 (rodada 4): "nan" atravessava, gravava JSON invalido, ordenava em 1o lugar, e
    #                        escapava do relatorio porque o teste era `is None`.
    for cru, esperado in [
        ("3", 3), (" 3 ", 3), ("-1", -1), ("+2", 2), ("3.5", 3.5), ("3,5", 3.5),
        (".5", 0.5), ("3.", 3.0), ("1e3", 1000.0), (0, 0), (-7, -7), (2.5, 2.5),
        ("nan", None), ("NaN", None), ("inf", None), ("-inf", None), ("Infinity", None),
        (float("nan"), None), (float("inf"), None),
        ("0x10", None), ("--3", None), ("tres", None), ("", None), ("   ", None), (None, None),
        (True, None), (False, None), ([3], None), ({"a": 3}, None), ((1, 2), None),
    ]:
        got = CB._num(cru)
        igual = (got is None and esperado is None) or (got is not None and got == esperado)
        checar(f"_num({cru!r}) = {esperado!r}", igual, f"-> deu {got!r}")

    print("\n  o resultado de _num sempre serializa em JSON valido:")
    for cru in ("nan", "inf", float("nan"), float("inf"), "3.5", "-1", 0):
        n = CB._num(cru)
        if n is None:
            continue
        texto = json.dumps({"v": n})
        checar(f"json.dumps de _num({cru!r}) nao produz NaN/Infinity",
               "NaN" not in texto and "Infinity" not in texto,
               f"-> {texto}; NaN nao e' JSON valido pela RFC 8259")

    print("\n_data — data e' data, nao texto:")
    # cicatriz (rodada 1): '2026-8-25' — DENTRO do sprint — dava False contra '2026-09-02',
    #                      porque '8' > '0'. A tarefa sumia do portal sem erro.
    for cru, esperado in [
        ("2026-08-25", "2026-08-25"), ("2026-8-25", "2026-08-25"), ("2026/8/25", "2026-08-25"),
        ("  2026-8-5  ", "2026-08-05"), ("2028-02-29", "2028-02-29"),
        ("2026-02-30", None), ("2026-04-31", None), ("2026-13-01", None), ("2026-02-29", None),
        ("2026-08", None), ("2026-08-25-99", None), ("2026-8-25extra", None),
        ("0-0-0", None), ("1899-01-01", None), ("banana", None), ("", None), (None, None),
        (True, None), (20260825, None), ([2026, 8, 25], None),
    ]:
        got = CB._data(cru)
        checar(f"_data({cru!r}) = {esperado!r}", got == esperado, f"-> deu {got!r}")
    checar("a ordem de _data e' cronologica, nao lexicografica",
           CB._data("2026-9-3") < CB._data("2026-12-1"),
           "-> '2026-12-1' < '2026-9-3' como texto; era o bug da ordenacao do adiantamento")

    print("\n_chave_executor — a mesma pessoa e' a mesma pessoa:")
    # cicatriz (rodada 1): "Bruno"/"BRUNO"/"bruno " viravam TRES pessoas e o teto de carga
    #                      parava de proteger quem ja estava cheio.
    mesma = {CB._chave_executor(x) for x in ("Bruno", "BRUNO", "bruno ", " Bruno")}
    checar("quatro grafias -> uma identidade", len(mesma) == 1, f"-> {mesma}")
    checar("espaco duplo no meio nao cria pessoa nova",
           CB._chave_executor("Ana  Maria") == CB._chave_executor("Ana Maria"))
    checar("pessoas diferentes seguem diferentes",
           CB._chave_executor("Ana") != CB._chave_executor("Ana Maria"))
    checar("vazio e None dao a mesma chave vazia",
           CB._chave_executor("") == CB._chave_executor(None) == "")

    print("\nlista_de — declaracao do projeto nao pode ser descartada calada:")
    # cicatriz (rodada 5): string era iterada CARACTERE A CARACTERE, e um executor de nome "A"
    #                      virava ausente. E cair no padrao sem avisar perde a regra declarada.
    for cru, esperado, avisa in [
        (["a", "b"], ["a", "b"], False), ("SEM DONO", ["SEM DONO"], False),
        (("a",), ["a"], False), (None, ["p1", "p2"], False),
        (42, ["p1", "p2"], True), ({"a": 1}, ["p1", "p2"], True),
    ]:
        got, aviso = CB.lista_de(cru, ["p1", "p2"])
        checar(f"lista_de({cru!r}) = {esperado!r}{' + aviso' if avisa else ''}",
               got == esperado and bool(aviso) == avisa, f"-> {got!r}, aviso={aviso!r}")

    print("\nconfig_num — numero de configuracao e' fronteira tambem:")
    # cicatriz (rodada 4): o teto vinha por `.get()` cru e reproduzia o MESMO TypeError, por outra
    #                      porta. Fronteira nao e' o --receber: e' todo ponto de entrada.
    for cru, valor, avisa in [(3, 3, False), ("3", 3, False), (0, 0, False), ("0", 0, False),
                              ("-1", -1, False), ("tres", 9, True), ([], 9, True),
                              (None, 9, False), (float("nan"), 9, True)]:
        pj = {} if cru is None else {"cap": {"n": cru}}
        got, problema = CB.config_num(pj, {}, ("cap", "n"), None, 9)
        checar(f"config_num({cru!r}) = {valor}{' + problema' if avisa else ''}",
               got == valor and bool(problema) == avisa, f"-> {got!r}, problema={problema!r}")
    got, _p = CB.config_num({}, {"alt": 5}, ("cap", "n"), "alt", 9)
    checar("cai na alternativa do estado quando o projeto nao declara", got == 5, f"-> {got}")
    got, _p = CB.config_num({"cap": "nao e dict"}, {}, ("cap", "n"), None, 9)
    checar("caminho que atravessa nao-dict nao crasha", got == 9, f"-> {got}")

    print("\nexigir_forma — tipo errado vira MENSAGEM, nunca traceback:")
    # cicatriz (rodada 5): `situacao` como lista derrubava a exportacao com AttributeError e
    #                      `colunas` como string com TypeError, no meio do trabalho.
    FORMA = {"cols": list, "mapa": dict, "flag": bool, "lim": "numero", "nome": str}
    for conf, aceita in [
        ({"cols": ["a"], "mapa": {}, "flag": True, "lim": 250, "nome": "x"}, True),
        ({"lim": "250"}, True), ({"lim": None}, True), ({}, True),
        ({"cols": "a"}, False), ({"mapa": "x"}, False), ({"flag": "sim"}, False),
        ({"lim": "duzentos"}, False), ({"nome": 5}, False), ({"lim": float("inf")}, False),
    ]:
        try:
            saida = CB.exigir_forma(conf, FORMA, "teste")
            deu, cru = True, None
        except CB.ConfiguracaoInvalida:
            deu, cru = False, None
        except Exception as ex:
            deu, cru = None, f"{type(ex).__name__}: {ex}"
        if cru:
            checar(f"exigir_forma({conf!r}) nao levanta excecao crua", False, f"-> {cru}")
        else:
            checar(f"exigir_forma({conf!r}) -> {'aceita' if aceita else 'recusa'}", deu == aceita)
    checar("`numero` declarado como texto e' CONVERTIDO, nao so aceito",
           CB.exigir_forma({"lim": "250"}, FORMA, "t")["lim"] == 250)
    checar("chave nao declarada na forma passa intacta",
           CB.exigir_forma({"outra": [1, 2]}, FORMA, "t")["outra"] == [1, 2])

    print("\n_chave_executor com acento — NFC e NFD sao a mesma pessoa:")
    # [ACHADO ALTA DO QA DA FRONTEIRA] "José" pre-composto (NFC) e "Jose"+acento combinante (NFD)
    # sao VISUALMENTE identicos e davam duas pessoas. Copiar de PDF/macOS tende a NFD; digitar no
    # Windows tende a NFC. E' a mesma consequencia que esta funcao existe para evitar, num caso tao
    # provavel quanto o "BRUNO" maiusculo — e nenhum dos 4 casos anteriores tinha acento.
    for a, b, rotulo, mesma in [
        ("Jos\u00e9", "Jose\u0301", "José pre-composto x combinante", True),
        ("Ver\u00f4nica", "Vero\u0302nica", "Verônica NFC x NFD", True),
        ("\uff22\uff52\uff55\uff4e\uff4f", "Bruno", "largura total x normal", True),
        ("Concei\u00e7\u00e3o", "Conceic\u0327a\u0303o", "Conceição NFC x NFD", True),
        ("Ana", "Ana Maria", "pessoas diferentes", False),
        ("Jos\u00e9", "Jose", "com acento x sem acento", False),
    ]:
        igual = CB._chave_executor(a) == CB._chave_executor(b)
        checar(f"{rotulo}: mesma pessoa={mesma}", igual == mesma,
               "-> forma Unicode diferente do MESMO nome tem de dar a MESMA carga")

    print("\n  digito nao-ASCII e separador de milhar: decisao consciente, nao heranca:")
    # levantado pelo QA como "aceitacao silenciosa que ninguem decidiu". A decisao e' ACEITAR,
    # porque a saida volta em digito ASCII e o valor normalizado ordena certo — recusar seria
    # recusar uma colagem de planilha que no fundo esta certa. Fica testado para ser decisao.
    for cru, esperado in [("\uff13", 3), ("\u0661\u0662\u0663", 123), ("1_000", 1000),
                          ("\uff11\uff10", 10)]:
        # `ascii()` e nao `{!r}`: o glifo cru derrubava o proprio canario no console cp1252 do
        # Windows, e o traceback matava o runner e os 68 canarios seguintes. Mensagem de teste nao
        # pode depender do encoding do terminal de quem roda.
        checar(f"_num({ascii(cru)}) = {esperado} (decisao: aceitar)", CB._num(cru) == esperado,
               f"-> deu {CB._num(cru)!r}")

    print("\nexigir_forma — bool nao e' int, nos DOIS sentidos:")
    # [achado MEDIA do QA da fronteira] `isinstance(True, int)` e' True em Python: forma pedindo
    # `int` aceitava `True` e o mantinha como bool. A direcao oposta ja era recusada — faltava
    # a simetria, que e' a forma de erro desta rodada inteira.
    for valor, esperado, aceita in [(True, int, False), (1, int, True), (0, int, True),
                                    (True, bool, True), (1, bool, False), (0, bool, False)]:
        try:
            CB.exigir_forma({"n": valor}, {"n": esperado}, "t")
            deu = True
        except CB.ConfiguracaoInvalida:
            deu = False
        checar(f"valor={valor!r} forma={esperado.__name__} -> "
               f"{'aceita' if aceita else 'recusa'}", deu == aceita)

    print("\nconfig_num — guarda simetrica: projeto E estado:")
    # [achado MEDIA do QA da fronteira] o acesso a `projeto` era protegido e o a `estado` nao.
    for pj, est, rotulo in [(None, None, "ambos None"), ({}, None, "estado None"),
                            (None, {}, "projeto None"), ("nao e dict", "nem isso", "ambos str")]:
        try:
            got, _pr = CB.config_num(pj, est, ("cap", "n"), "alt", 9)
            crashou = False
        except Exception as ex:
            got, crashou = None, f"{type(ex).__name__}"
        checar(f"config_num com {rotulo} nao crasha", not crashou and got == 9,
               f"-> {crashou or got!r}")

    print("\nexigir_forma — forma MALFORMADA tambem merece mensagem:")
    # [achado MEDIA do QA da fronteira, rodada 2] `isinstance(x, None)` levanta TypeError cru.
    for declarada in (None, "banana", 5, [list]):
        try:
            CB.exigir_forma({"x": 5}, {"x": declarada}, "t")
            r = "aceita"
        except CB.ConfiguracaoInvalida:
            r = "recusa com mensagem"
        except Exception as ex:
            r = f"CRUA:{type(ex).__name__}"
        checar(f"forma declarada como {declarada!r} -> recusa com mensagem",
               r == "recusa com mensagem", f"-> {r}")

    print("\nlista_de — set e frozenset sao a mesma coisa aqui:")
    for cru in ({1, 2}, frozenset({1, 2})):
        got, aviso = CB.lista_de(cru, ["p"])
        checar(f"lista_de({type(cru).__name__}) aceita sem aviso",
               sorted(got) == [1, 2] and not aviso, f"-> {got!r}, aviso={aviso!r}")

    print("\n_chave_executor — o alcance REAL do NFKC, nao so o documentado:")
    for a, b, rotulo in [("Steffi", "Ste\ufb03", "ligadura ffi"),
                         ("Henrique IV", "Henrique \u2163", "numeral romano"),
                         ("m2", "m\u00b2", "superscript")]:
        checar(f"NFKC funde {rotulo} (alcance declarado)",
               CB._chave_executor(a) == CB._chave_executor(b),
               "-> o comentario do codigo tem de dizer o que o mecanismo faz de verdade")

    print("\nler_texto — a guarda vale para JSON e para CSV, uma leitura so:")
    # [ACHADO ALTA DO QA RODADA 9] o `LIST-retorno.csv` era lido com `.read_text()` cru e derrubava
    # `--receber` com UnicodeDecodeError, enquanto os JSON irmaos ja tinham guarda.
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _d:
        _p = Path(_d) / "x.csv"
        for conteudo, o_que, aceita in [
            ("id,a\nT1,ok\n".encode("utf-8"), "UTF-8 limpo", True),
            (b"\xef\xbb\xbfid,a\nT1,ok\n", "com BOM (arquivo CORRETO)", True),
            ("id,a\nT1,caf\u00e9\n".encode("latin-1"), "em Latin-1", False),
            (b"\xff\xfe\x00i\x00d", "UTF-16 sem conversao", False),
        ]:
            _p.write_bytes(conteudo)
            try:
                CB.ler_texto(_p, "o arquivo de teste")
                r3 = "aceito"
            except CB.ProjetoInvalido:
                r3 = "recusado com mensagem"
            except Exception as ex:
                r3 = f"CRUA:{type(ex).__name__}"
            checar(f"ler_texto: {o_que} -> {'aceito' if aceita else 'recusado com mensagem'}",
                   r3 == ("aceito" if aceita else "recusado com mensagem"), f"-> {r3}")
        try:
            CB.ler_texto(Path(_d) / "nao-existe.csv")
            r4 = "aceito"
        except CB.ProjetoInvalido:
            r4 = "recusado com mensagem"
        except Exception as ex:
            r4 = f"CRUA:{type(ex).__name__}"
        checar("ler_texto: arquivo ausente -> recusado com mensagem",
               r4 == "recusado com mensagem", f"-> {r4}")

    print("\nescrever_texto — a fronteira tem DOIS lados, e o da escrita faltava:")
    # [ACHADO ALTA DO QA RODADA 11] onze rodadas perseguindo guarda assimetrica, e a assimetria
    # maior estava na palavra: eu li "fronteira" como LEITURA o tempo todo. O docstring do modulo
    # sempre disse "nunca GRAVAR nem comparar o que nao se sabe ler".
    import os as _os, stat as _st, tempfile as _tf
    with _tf.TemporaryDirectory() as _d:
        alvo = Path(_d) / "sub" / "x.txt"
        try:
            CB.escrever_texto(alvo, "conteudo\n", "o arquivo de teste")
            r = "gravou"
        except Exception as ex:
            r = f"{type(ex).__name__}"
        checar("cria a pasta que falta e grava", r == "gravou" and alvo.is_file(), f"-> {r}")
        checar("o conteudo sai intacto", alvo.read_text(encoding="utf-8") == "conteudo\n")

        # A BARREIRA E' DIFERENTE EM CADA PLATAFORMA — achado da CI do macOS, 22/09/2026, na
        # primeira vez que este pacote rodou fora do Windows.
        #
        # `escrever_texto` e' ATOMICO: grava um temporario ao lado e troca com `os.replace`.
        # No POSIX, trocar um arquivo depende da permissao do DIRETORIO, nao da do arquivo —
        # entao deixar o ARQUIVO somente-leitura nao barra nada, e o teste reprovava uma
        # garantia que existe. No Windows e' o contrario: `chmod` num diretorio nao faz efeito,
        # e quem barra e' o atributo do arquivo.
        #
        # Supor uma das duas semanticas e' o mesmo erro que esta serie persegue: a verificacao
        # olhando um fato que nao discrimina o que ela afirma discriminar.
        # E COMO ROOT NAO BARRA NADA [ressalva MEDIA do qa-critic, 22/09/2026]. O kernel POSIX
        # ignora a permissao do diretorio para o UID 0: a gravacao SUCEDERIA e este caso voltaria
        # a reprovar uma garantia que existe — agora tambem no Linux, que e' pior que o defeito
        # original, porque ninguem esperaria por ele ali. Hoje nao acontece (a CI roda em runner
        # nao-root, conferido em .github/workflows/ci.yml, sem `container:`), mas trocar
        # `runs-on` por um job containerizado reabriria a classe EM SILENCIO. Entao a condicao
        # e' declarada em vez de suposta: sob root, este caso se declara nao-exercitado.
        _posix = _os.name != "nt"
        _root = _posix and hasattr(_os, "geteuid") and _os.geteuid() == 0
        _pasta = alvo.parent
        if _root:
            # NAO simula um PASS: declara que a condicao nao pode ser montada aqui. Um teste que
            # se diz verde sem ter exercitado nada e' o carimbo que este repo passa o tempo todo
            # desmontando — entao o caso se anuncia, alto, como nao-exercitado.
            print("  ---  somente-leitura -> mensagem, nao traceback: NAO EXERCITADO "
                  "(rodando como root; o UID 0 ignora a permissao do diretorio)")
        else:
            if _posix:
                _os.chmod(_pasta, 0o500)      # r-x: nao da' para criar o temporario
            else:
                _os.chmod(alvo, _st.S_IREAD)
            try:
                CB.escrever_texto(alvo, "outro", "o arquivo de teste")
                r2 = "gravou"
            except CB.ProjetoInvalido:
                r2 = "recusado com mensagem"
            except Exception as ex:
                r2 = f"CRUA:{type(ex).__name__}"
            finally:
                # `stat.S_IWRITE` e' 0o200 — write-only, SEM leitura. No POSIX isso tirava a
                # permissao de LER e o `read_text` da checagem seguinte estourava de verdade.
                if _posix:
                    _os.chmod(_pasta, 0o700)
                    _os.chmod(alvo, 0o644)
                else:
                    _os.chmod(alvo, _st.S_IWRITE)
            checar("somente-leitura -> mensagem, nao traceback", r2 == "recusado com mensagem",
                   f"-> {r2}; era PermissionError cru no comando que PERSISTE mudanca")
        checar("e o conteudo antigo nao foi destruido",
               alvo.read_text(encoding="utf-8") == "conteudo\n",
               "-> escrita que falha nao pode deixar o arquivo pela metade")

        # [ACHADO ALTA DO QA RODADA 12] o `checar` acima AFIRMAVA a garantia geral, mas so
        # exercitava o caso em que o `open` falha ANTES de truncar. `open("w")` trunca no momento
        # do open: falha NO MEIO da escrita destruia o conteudo antigo sem gravar o novo — e o
        # arquivo de maior consequencia do pacote e' justamente o estado. A alegacao do teste era
        # mais forte que o mecanismo, que e' a classe que esta serie inteira persegue.
        import tempfile as _t2
        _real = _t2.NamedTemporaryFile

        class _Falha:
            """Escreve tudo certo ate o `write`, e ai o disco enche."""
            def __init__(self, *a, **k):
                self._f = _real(*a, **k)
                self.name = self._f.name

            def __enter__(self):
                return self

            def __exit__(self, *a):
                self._f.__exit__(*a)
                return False

            def write(self, s):
                raise OSError(28, "No space left on device")

            def flush(self):
                pass

            def fileno(self):
                return self._f.fileno()

        alvo.write_text("ORIGINAL PRECIOSO\n", encoding="utf-8")
        _t2.NamedTemporaryFile = _Falha
        try:
            CB.escrever_texto(alvo, "novo", "o arquivo de teste")
            r5 = "gravou"
        except CB.ProjetoInvalido:
            r5 = "recusado com mensagem"
        except Exception as ex:
            r5 = f"CRUA:{type(ex).__name__}"
        finally:
            _t2.NamedTemporaryFile = _real
        checar("disco cheio NO MEIO da escrita -> mensagem", r5 == "recusado com mensagem", f"-> {r5}")
        checar("e o conteudo original sobrevive INTACTO",
               alvo.read_text(encoding="utf-8") == "ORIGINAL PRECIOSO\n",
               "-> a troca so pode acontecer se a escrita inteira der certo (os.replace)")
        sobrou = [x.name for x in alvo.parent.iterdir() if x.name.endswith(".parcial")]
        checar("e nao sobra arquivo parcial na pasta", not sobrou, f"-> {sobrou}")

    print("\ndentro_da_raiz — caminho da declaracao nao sai do projeto:")
    # [ACHADO ALTA DO QA RODADA 12, o mais serio da serie] `raiz / nome` DESCARTA a raiz se `nome`
    # for absoluto, e sobe com `..`. Um caminho colado por engano fazia `--receber --confirmar`
    # sobrescrever arquivo qualquer do disco, e a mensagem de sucesso nem revelava o alvo real.
    with _tf.TemporaryDirectory() as _d2:
        base = Path(_d2) / "proj"
        base.mkdir()
        (Path(_d2) / "fora").mkdir()
        for nome, aceita, rotulo in [
            ("estado.json", True, "arquivo na raiz"),
            ("sub/estado.json", True, "arquivo em subpasta"),
            ("./estado.json", True, "com ./ na frente"),
            ("../fora/alvo.json", False, "subindo com .."),
            ("../../alvo.json", False, "subindo dois niveis"),
            (str(Path(_d2) / "fora" / "alvo.json"), False, "caminho ABSOLUTO"),
            ("sub/../../fora/alvo.json", False, ".. escondido no meio"),
            ("", False, "vazio"),
            ("   ", False, "so espaco"),
            (42, False, "nem e' texto"),
        ]:
            try:
                CB.dentro_da_raiz(base, nome, "`teste`")
                r6 = "aceito"
            except CB.ProjetoInvalido:
                r6 = "recusado com mensagem"
            except Exception as ex:
                r6 = f"CRUA:{type(ex).__name__}"
            checar(f"caminho {rotulo} -> {'aceito' if aceita else 'recusado'}",
                   r6 == ("aceito" if aceita else "recusado com mensagem"),
                   f"-> {r6}; caminho fora da raiz sobrescreve arquivo de terceiro em silencio")

        # `base` e' uma PASTA que existe. (A versao anterior usava `_d`, de um bloco `with` ja
        # fechado — o diretorio nao existia mais, e o teste "passava" gravando um arquivo com aquele
        # nome. Verificacao que aponta para alvo inexistente nao verifica nada.)
        try:
            CB.escrever_texto(base, "x", "uma pasta")
            r3 = "gravou"
        except CB.ProjetoInvalido:
            r3 = "recusado com mensagem"
        except Exception as ex:
            r3 = f"CRUA:{type(ex).__name__}"
        checar("gravar por cima de uma PASTA -> mensagem", r3 == "recusado com mensagem", f"-> {r3}")

    print("\nraiz_projeto e carregar — nunca chutar, sempre dizer como achou:")
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp) / "proj"
        raiz.mkdir()
        (raiz / CB.DECLARACAO).write_text(json.dumps({"estado": "e.json"}), encoding="utf-8")
        (raiz / "e.json").write_text(json.dumps({"itens": []}), encoding="utf-8")
        achada, origem = CB.raiz_projeto(str(raiz))
        checar("resolve quando indicado", achada == raiz.resolve(), f"-> {origem}")
        checar("a origem e' declarada", bool(origem))
        pj, est = CB.carregar(raiz)
        checar("carrega declaracao e estado", pj["estado"] == "e.json" and est["itens"] == [])

        for quebra, o_que in [
            ('["nao", "e", "objeto"]', "declaracao que nao e' objeto"),
            ('{"estado": 42}', "`estado` que nao e' nome de arquivo"),
            ('{"estado": "nao-existe.json"}', "`estado` apontando para arquivo ausente"),
        ]:
            (raiz / CB.DECLARACAO).write_text(quebra, encoding="utf-8")
            try:
                CB.carregar(raiz)
                pegou = False
            except CB.ProjetoInvalido:
                pegou = True
            except Exception as ex:
                pegou = False
                checar(f"{o_que} nao levanta excecao crua", False, f"-> {type(ex).__name__}: {ex}")
            checar(f"{o_que} e' recusada com mensagem", pegou)

        (raiz / CB.DECLARACAO).write_text(json.dumps({"estado": "e.json"}), encoding="utf-8")
        (raiz / "e.json").write_text(json.dumps({"itens": "nao e lista"}), encoding="utf-8")
        try:
            CB.carregar(raiz)
            pegou = False
        except CB.ProjetoInvalido:
            pegou = True
        checar("`itens` que nao e' lista e' recusado", pegou,
               "-> forma errada aqui crasha todo consumidor la' na frente")

        try:
            CB.raiz_projeto(str(Path(tmp) / "nao-existe"))
            pegou = False
        except CB.ProjetoInvalido:
            pegou = True
        checar("pasta sem declaracao levanta erro que diz o que fazer", pegou)

        # [achado MEDIA do QA da fronteira, rodada 2] o canario so exercitava o ramo `indicado`.
        # Os outros DOIS jeitos de achar a raiz — variavel de ambiente e subida por `parents` —
        # tinham cobertura ZERO, apesar de o modulo prometer "a origem volta junto para depurar".
        (raiz / CB.DECLARACAO).write_text(json.dumps({"estado": "e.json"}), encoding="utf-8")
        (raiz / "e.json").write_text(json.dumps({"itens": []}), encoding="utf-8")

        import os as _os
        guardado = _os.environ.get(CB.ENV_PROJETO)
        try:
            _os.environ[CB.ENV_PROJETO] = str(raiz)
            achada2, origem2 = CB.raiz_projeto()
            checar("acha pela variavel de ambiente", achada2 == raiz.resolve(), f"-> {achada2}")
            checar("e DIZ que foi pela variavel de ambiente",
                   CB.ENV_PROJETO in origem2, f"-> origem={origem2!r}")
            _os.environ[CB.ENV_PROJETO] = str(Path(tmp) / "vazio")
            try:
                CB.raiz_projeto()
                pegou_env = False
            except CB.ProjetoInvalido:
                pegou_env = True
            checar("variavel de ambiente apontando para pasta sem declaracao e' recusada", pegou_env)
        finally:
            if guardado is None:
                _os.environ.pop(CB.ENV_PROJETO, None)
            else:
                _os.environ[CB.ENV_PROJETO] = guardado

        fundo = raiz / "a" / "b" / "c"
        fundo.mkdir(parents=True, exist_ok=True)
        anterior = _os.getcwd()
        try:
            _os.chdir(fundo)
            achada3, origem3 = CB.raiz_projeto()
            checar("acha subindo a arvore a partir da pasta corrente",
                   achada3 == raiz.resolve(), f"-> {achada3}")
            checar("e DIZ que subiu", "subindo" in origem3, f"-> origem={origem3!r}")
        finally:
            _os.chdir(anterior)

        # [achado BAIXA] NUL embutido levantava ValueError cru
        # [achado BAIXA do QA rodada 8] a versao anterior tinha `... or (not cru and ...)`, que para
        # a string vazia era SEMPRE verdadeiro: o checar reportava "ok" desse jeito qualquer que
        # fosse o comportamento. Verificacao que nao pode falhar nao verifica nada.
        try:
            CB.raiz_projeto("C:\\foo\x00bar")
            r = "aceito"
        except CB.ProjetoInvalido:
            r = "recusado com mensagem"
        except Exception as ex:
            r = f"CRUA:{type(ex).__name__}"
        # [ACHADO ALTA DO QA RODADA 9] esta era a UNICA prova da guarda, e ela depende do
        # interpretador: `Path("...\\0...").resolve()` levanta ValueError no 3.12 e NAO levanta nada
        # no 3.14 — e esta maquina tem os dois. Prova que muda de resultado conforme o Python que
        # roda nao e' prova; e' o irmao do PYTHONIOENCODING da rodada 7.
        #
        # Entao o gatilho que a suite EXIGE passou a ser um que vale em qualquer versao, e o NUL
        # virou verificacao condicional que se DECLARA quando o interpretador nao o produz.
        for cru, rotulo in [(123, "numero em vez de texto"), (["a"], "lista em vez de texto"),
                            ({"a": 1}, "objeto em vez de texto")]:
            try:
                CB.raiz_projeto(cru)
                r2 = "aceito"
            except CB.ProjetoInvalido:
                r2 = "recusado com mensagem"
            except Exception as ex:
                r2 = f"CRUA:{type(ex).__name__}"
            checar(f"caminho como {rotulo} -> recusado com mensagem",
                   r2 == "recusado com mensagem", f"-> {r2}")

        if r == "aceito":
            print("     (este interpretador nao levanta com NUL no caminho — a verificacao do NUL")
            print("      nao se aplica aqui, e isto fica DITO em vez de passar calado)")
        else:
            checar("caminho com NUL embutido -> recusado com mensagem",
                   r == "recusado com mensagem", f"-> {r}")
        # `--projeto ""` NAO e' "caminho vazio invalido": e' o mesmo que nao informar, e cai no
        # modo de subir a arvore. Isto e' comportamento declarado, e o teste diz qual e'.
        _guardado = os.environ.pop(CB.ENV_PROJETO, None)
        _antes = os.getcwd()
        try:
            os.chdir(raiz)
            achada_v, origem_v = CB.raiz_projeto("")
            checar("--projeto vazio e' o mesmo que nao informar (sobe a arvore)",
                   achada_v == raiz.resolve() and "subindo" in origem_v,
                   f"-> {achada_v}, origem={origem_v!r}")
        finally:
            os.chdir(_antes)
            if _guardado is not None:
                os.environ[CB.ENV_PROJETO] = _guardado

        # [ACHADO ALTA DO QA DA FRONTEIRA] forma errada em JSON VALIDO era recusada com mensagem;
        # JSON com typo, com BOM ou em Latin-1 subia excecao CRUA. O caso mais provavel de todos —
        # typo em arquivo editado a mao — era o unico sem guarda. Guarda assimetrica.
        print("\n  JSON que nao da' para ler vira MENSAGEM, nunca traceback:")
        (raiz / "e.json").write_text(json.dumps({"itens": []}), encoding="utf-8")
        for conteudo, o_que, aceita in [
            ("{not valid json", "typo de sintaxe", False),
            ('{"estado": "e.json", "a": 1,}', "virgula sobrando", False),
            ('{"estado": "e.json"', "chave nao fechada", False),
            (b"\xef\xbb\xbf" + json.dumps({"estado": "e.json"}).encode("utf-8"),
             "BOM (arquivo CORRETO)", True),
            ('{"estado": "e.json", "nota": "caf\u00e9"}'.encode("latin-1"), "Latin-1", False),
            ("", "arquivo vazio", False),
        ]:
            if isinstance(conteudo, bytes):
                (raiz / CB.DECLARACAO).write_bytes(conteudo)
            else:
                (raiz / CB.DECLARACAO).write_text(conteudo, encoding="utf-8")
            try:
                CB.carregar(raiz)
                estado_, cru = "aceito", None
            except CB.ProjetoInvalido:
                estado_, cru = "recusado com mensagem", None
            except Exception as ex:
                estado_, cru = None, f"{type(ex).__name__}"
            if cru:
                checar(f"{o_que} nao levanta excecao crua", False, f"-> {cru}")
            else:
                checar(f"{o_que} -> {'aceito' if aceita else 'recusado com mensagem'}",
                       (estado_ == "aceito") == aceita,
                       "-> BOM e' o padrao de editor no Windows e o arquivo esta CERTO")
        # o mesmo vale para o arquivo de ESTADO, nao so para a declaracao
        (raiz / CB.DECLARACAO).write_text(json.dumps({"estado": "e.json"}), encoding="utf-8")
        (raiz / "e.json").write_text("{quebrado", encoding="utf-8")
        try:
            CB.carregar(raiz)
            pegou_est = False
        except CB.ProjetoInvalido:
            pegou_est = True
        except Exception:
            pegou_est = False
        checar("JSON quebrado no arquivo de ESTADO tambem vira mensagem", pegou_est,
               "-> a guarda nao pode existir so na declaracao")

    print()
    if falhou:
        print(f"FAIL — {len(falhou)} verificacao(oes) falharam: {falhou}")
        return 1
    print("PASS — a fronteira converte o que da' para ler e recusa o resto, sempre dizendo qual.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
