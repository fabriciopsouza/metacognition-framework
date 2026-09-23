#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""controle_base — a FRONTEIRA do pacote controle_*: onde valor de fora vira valor usado.

POR QUE ESTE MODULO EXISTE, e ele nasceu de uma decisao do dono, nao de gosto.

O pacote `controle_*` passou por CINCO rodadas de critica adversarial e as cinco reprovaram. Olhando
os vinte e tantos achados juntos, quase todos moram no mesmo lugar: **converter, validar ou resolver
um valor que veio de fora**. E a camada que faz isso estava espalhada entre os dois modulos — o que
produziu, na rodada 5, o achado que fecha o argumento: a validacao de tipo existia em
`controle_projeto` e NAO existia no irmao `controle_sharepoint`, que le o MESMO `projeto.json`.

Diante disso o dono mandou **reabrir o desenho** em vez de seguir iterando. Esta e' a costura: a
fronteira vira um bloco proprio, com canario proprio e critica propria, e os dois modulos de cima
passam a depender dela em vez de cada um ter a sua.

O QUE E' FRONTEIRA, na pratica: `projeto.json` e `estado.json` sao editados a mao; o `LIST-retorno`
e' preenchido por gente numa planilha. Nada disso e' confiavel por construcao. A regra e' uma so —
**converter ou recusar**, nunca gravar nem comparar o que nao se sabe ler.

A CICATRIZ DE CADA FUNCAO, porque cada uma nasceu de um defeito medido:

    _chave_executor  "Bruno" / "BRUNO" / "bruno " viravam TRES pessoas, e o teto de carga
                     parava de proteger quem ja estava cheio.
    _data            '2026-8-25' — dentro do sprint — dava False contra '2026-09-02', porque
                     '8' > '0' como texto. A tarefa sumia do portal sem erro.
    _num             "-1" e "3.5" eram gravados como STRING (`.isdigit()` recusa sinal e ponto),
                     e o comando seguinte MORRIA com TypeError. Depois: "nan" atravessava,
                     corrompia o estado com JSON invalido e escapava do relatorio.
    config_num       o teto vinha de `projeto.json` por `.get()` cru e reproduzia o mesmo crash
                     por outra porta.
    exigir_forma     `situacao` como lista e `colunas` como string derrubavam a exportacao com
                     traceback cru, em vez de mensagem.
    raiz_projeto     caminho fixo quebra em outra maquina, e quebra em SILENCIO.

Uso:
    from controle_base import raiz_projeto, carregar, _num, _data, config_num, exigir_forma
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import tempfile
import unicodedata
from pathlib import Path

DECLARACAO = "projeto.json"
ENV_PROJETO = "CONTROLE_PROJETO_RAIZ"


class ProjetoInvalido(RuntimeError):
    """A declaracao do projeto nao serve. Diz o que falta, nunca completa por conta."""


class ConfiguracaoInvalida(RuntimeError):
    """A declaracao existe mas tem forma errada. Mensagem, nunca traceback."""


# ----------------------------------------------------------------- resolucao


def _caminho(cru: str, de_onde: str) -> Path:
    """Texto vira Path, ou ProjetoInvalido dizendo de onde veio o texto ruim.

    [achado BAIXA do QA da fronteira, rodada 2] `Path(x).resolve()` levanta ValueError cru com NUL
    embutido, e OSError com caractere ilegal no Windows. O caminho vem de fora — do argumento ou de
    uma variavel de ambiente que pode ter sido montada por script — entao esta dentro do contrato.

    [ACHADO ALTA DO QA RODADA 9] TypeError entrou na guarda por um motivo de METODO, nao de defeito:
    o NUL — unico gatilho que o teste usava — levanta ValueError no Python 3.12 e NAO levanta nada
    no 3.14, e esta maquina tem os dois. A prova da guarda ficava dependendo de qual interpretador
    rodava, que e' o irmao exato do `PYTHONIOENCODING` da rodada 7. Com TypeError a guarda tem um
    gatilho que vale em QUALQUER versao, e o teste deixa de depender do ambiente."""
    try:
        return Path(cru).resolve()
    except (ValueError, OSError, TypeError) as e:
        raise ProjetoInvalido(f"{de_onde} nao e' um caminho valido ({e})") from None


def raiz_projeto(indicado: str | None = None) -> tuple[Path, str]:
    """Acha a raiz do projeto e DECLARA como achou.

    Caminho fixo quebra em outra maquina, em outro usuario, e quando a pasta sincronizada muda de
    nome. E quebra em SILENCIO: o script nao acha o arquivo e segue como se nao houvesse nada la.
    A origem volta junto para quem for depurar."""
    if indicado:
        p = _caminho(indicado, "o caminho indicado no comando")
        if not (p / DECLARACAO).is_file():
            raise ProjetoInvalido(f"{p} nao tem {DECLARACAO}")
        return p, "indicado no comando"

    if os.environ.get(ENV_PROJETO):
        p = _caminho(os.environ[ENV_PROJETO], f"a variavel de ambiente {ENV_PROJETO}")
        if not (p / DECLARACAO).is_file():
            raise ProjetoInvalido(f"{ENV_PROJETO}={p} nao tem {DECLARACAO}")
        return p, f"variavel de ambiente {ENV_PROJETO}"

    atual = Path.cwd().resolve()
    for cand in [atual, *atual.parents]:
        if (cand / DECLARACAO).is_file():
            return cand, f"achado subindo de {atual}"

    raise ProjetoInvalido(
        f"nenhum {DECLARACAO} em {atual} nem acima dela.\n"
        f"  Aponte com --projeto <caminho>, ou defina {ENV_PROJETO}.\n"
        f"  Para criar a declaracao: python tools/controle_projeto.py --iniciar <caminho>")


def ler_texto(caminho: Path, o_que: str = "") -> str:
    """Le um arquivo de texto, ou levanta ProjetoInvalido dizendo o que houve.

    Vale para JSON e para CSV: [ACHADO ALTA DO QA RODADA 9] o `LIST-retorno.csv` era lido com
    `.read_text()` cru e derrubava `--receber` com UnicodeDecodeError, enquanto os JSON irmaos ja
    tinham guarda. Guarda assimetrica de novo — a mesma forma de erro que esta serie inteira
    persegue. Uma leitura so, para nao haver um terceiro caminho amanha.

    `utf-8-sig` de proposito: BOM e' o padrao de varios editores no Windows e o arquivo esta CERTO."""
    rotulo = o_que or caminho.name
    try:
        return caminho.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as e:
        raise ProjetoInvalido(
            f"{rotulo} ({caminho.name}) nao esta em UTF-8 (byte {e.start}). Salve como UTF-8 — "
            f"acento salvo em ANSI/Latin-1 quebra a leitura.") from None
    except OSError as e:
        raise ProjetoInvalido(f"nao consegui ler {caminho}: {e}") from None


def escrever_texto(caminho: Path, conteudo: str, o_que: str = "") -> None:
    """Grava um arquivo de texto, ou levanta ProjetoInvalido dizendo o que houve.

    [ACHADO ALTA DO QA RODADA 11] a fronteira so olhava a ENTRADA. `receber` gravava o estado e
    `exportar` abria o CSV sem guarda: arquivo somente-leitura derrubava os dois com
    `PermissionError` e traceback completo — e o `--receber --confirmar` e' o unico comando do
    pacote que PERSISTE mudanca, ou seja, o de maior consequencia.

    Onze rodadas perseguindo guarda assimetrica, e a assimetria maior estava na palavra: o docstring
    deste modulo sempre disse "nunca GRAVAR nem comparar o que nao se sabe ler" — e so o "ler" tinha
    sido tratado.

    Grava com `newline=""` para o CSV nao ganhar \r\n duplicado no Windows; para Markdown e JSON isso
    e' indiferente."""
    rotulo = o_que or caminho.name
    # [ACHADO MEDIA DO QA RODADA 12] `mkdir(parents=True)` criava a arvore inteira em silencio
    # quando o caminho tinha typo — "dcos/projeto/" em vez de "docs/projeto/" — e respondia PASS.
    # Criar continua permitido (projeto novo precisa), mas passa a ser DITO.
    criadas = []
    faltando = caminho.parent
    while not faltando.exists() and faltando != faltando.parent:
        criadas.append(faltando)
        faltando = faltando.parent

    # [ACHADO ALTA DO QA RODADA 12] `open("w")` TRUNCA no momento do open, antes de escrever um
    # byte: falha no meio da escrita destruia o conteudo antigo sem gravar o novo — e o arquivo de
    # maior consequencia do pacote e' justamente o estado. Grava num temporario ao lado e troca com
    # `os.replace`, que e' atomico no NTFS e no POSIX: ou o velho inteiro, ou o novo inteiro.
    tmp = None
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False,
                                         dir=str(caminho.parent),
                                         prefix=f".{caminho.name}.", suffix=".parcial") as f:
            tmp = Path(f.name)
            f.write(conteudo)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, caminho)
        tmp = None
    except OSError as e:
        raise ProjetoInvalido(
            f"nao consegui gravar {rotulo} ({caminho}): {e}.\n"
            f"  Arquivo aberto noutro programa, somente-leitura, pasta sem permissao, ou disco\n"
            f"  cheio. O conteudo anterior NAO foi tocado — a troca so acontece se a escrita "
            f"inteira der certo.") from None
    finally:
        if tmp is not None and tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
    for nova in reversed(criadas):
        print(f"  (criei a pasta {nova})")


def dentro_da_raiz(raiz: Path, nome: str, o_que: str) -> Path:
    """Resolve `nome` DENTRO de `raiz`, ou recusa.

    [ACHADO ALTA DO QA RODADA 12 — o mais serio da serie] `raiz / nome` do pathlib DESCARTA a raiz
    se `nome` for absoluto, e sobe livremente com `..`:

        Path("C:/projetos/meu") / "C:/Windows/win.ini"  ->  WindowsPath('C:/Windows/win.ini')

    Um `"estado": "../fora/alvo.json"` — ou um caminho absoluto colado por engano ao editar
    `projeto.json` a mao, que e' o cenario que esta fronteira inteira existe para tratar — fazia
    `--receber --confirmar` LER, MESCLAR e SOBRESCREVER um arquivo qualquer do disco, e a mensagem
    de sucesso nem revelava que o alvo nao era o do projeto.

    Os outros defeitos desta serie produziam crash ou numero errado. Este destroi arquivo de
    terceiro em silencio, e por isso a regra e' dura: o caminho tem de ficar debaixo da raiz."""
    if not isinstance(nome, str) or not nome.strip():
        raise ProjetoInvalido(f"{o_que} tem de ser o nome de um arquivo dentro do projeto")
    alvo = _caminho(str(raiz / nome), o_que)
    base = _caminho(str(raiz), "a raiz do projeto")
    try:
        dentro = alvo == base or alvo.is_relative_to(base)
    except AttributeError:                       # pragma: no cover - Python < 3.9
        dentro = str(alvo).startswith(str(base) + os.sep)
    if not dentro:
        raise ProjetoInvalido(
            f"{o_que} aponta para FORA do projeto: {nome!r} resolve em {alvo}.\n"
            f"  Caminho absoluto ou `..` na declaracao sai da pasta do projeto — e a escrita\n"
            f"  sobrescreveria arquivo de terceiro sem avisar. Use caminho relativo a {base}.")
    return alvo


def _ler_json(caminho: Path) -> object:
    """Le um JSON e devolve o conteudo, ou levanta ProjetoInvalido dizendo o que houve.

    [ACHADO ALTA DO QA DA FRONTEIRA] `json.loads(read_text(...))` nao tinha guarda de PARSE nem de
    ENCODING. Forma errada em JSON valido era recusada com mensagem; virgula sobrando, aspas nao
    fechadas, BOM ou arquivo em Latin-1 subiam excecao crua. O caso MAIS provavel — typo em arquivo
    editado a mao — era o unico sem guarda. Guarda assimetrica.

    `utf-8-sig` no lugar de `utf-8` nao e' so mensagem melhor: BOM e' o padrao de varios editores no
    Windows, e o arquivo com BOM esta CORRETO. Recusa-lo seria recusar dado bom."""
    bruto = ler_texto(caminho)
    try:
        return json.loads(bruto)
    except json.JSONDecodeError as e:
        raise ProjetoInvalido(
            f"{caminho.name} nao e' JSON valido: {e.msg}, linha {e.lineno} coluna {e.colno}.\n"
            f"  Erro comum: virgula sobrando antes de }} ou ], ou aspas nao fechadas.") from None


def carregar(raiz: Path) -> tuple[dict, dict]:
    """Le a declaracao do projeto e o estado que ela aponta. Recusa forma errada nos dois."""
    declarado = _ler_json(raiz / DECLARACAO)
    if not isinstance(declarado, dict):
        raise ProjetoInvalido(f"{DECLARACAO} tem de ser um objeto, e e' {type(declarado).__name__}")
    nome_estado = declarado.get("estado") or "estado.json"
    if not isinstance(nome_estado, str):
        raise ProjetoInvalido(f"`estado` em {DECLARACAO} tem de ser o nome de um arquivo")
    arq = dentro_da_raiz(raiz, nome_estado, "`estado` na declaracao")
    if not arq.is_file():
        raise ProjetoInvalido(f"{DECLARACAO} aponta `estado`={nome_estado}, que nao existe em {raiz}")
    estado = _ler_json(arq)
    if not isinstance(estado, dict):
        raise ProjetoInvalido(f"{nome_estado} tem de ser um objeto, e e' {type(estado).__name__}")
    if estado.get("itens") is not None and not isinstance(estado["itens"], list):
        raise ProjetoInvalido(f"`itens` em {nome_estado} tem de ser uma lista")
    return declarado, estado


# ----------------------------------------------------------------- normalizadores


def _chave_executor(nome: str) -> str:
    """A identidade da pessoa para efeito de CARGA. Nao e' o nome de exibicao.

    "Bruno", "BRUNO" e "bruno " viravam tres pessoas: a carga real de 3 aparecia como 1+1+1 e o teto
    parava de proteger quem ja estava cheio. Grafia inconsistente e' o normal em preenchimento
    manual — nao e' caso exotico.

    LIMITE CONHECIDO, e fica dito: dois HOMONIMOS reais somam carga como se fossem uma pessoa.
    Aceito de proposito — o campo guarda um nome, nao uma matricula, e inventar desambiguacao que o
    dado nao tem seria fingir precisao. Havendo homonimo na equipe, o projeto declara nome distinto."""
    # [ACHADO ALTA DO QA DA FRONTEIRA] faltava normalizar UNICODE. "José" pre-composto (NFC) e
    # "Jose"+acento combinante (NFD) sao VISUALMENTE identicos e davam duas pessoas — a mesma
    # consequencia que esta funcao existe para evitar, num caso tao provavel quanto o "BRUNO"
    # maiusculo: copiar de PDF ou de macOS tende a produzir NFD, digitar no Windows tende a NFC.
    #
    # NFKC e nao NFC, e o alcance dele e' MAIOR do que a primeira redacao deste comentario dizia
    # [achado BAIXA do QA da fronteira, rodada 2]: alem de acento e largura ("Ｂｒｕｎｏ" = "Bruno"),
    # ele dobra ligadura ("Steﬃ" = "Steffi"), numeral romano ("Ⅳ" = "IV") e superscript ("m²" =
    # "m2"). Testado: em todos os casos a fusao e' "mesma pessoa, grafia diferente" — nao achamos
    # par de pessoas distintas que colida. A decisao e' MANTER o NFKC e dizer o alcance, em vez de
    # descrever menos do que o mecanismo faz.
    return unicodedata.normalize("NFKC", " ".join((nome or "").split())).casefold()


def _data(valor) -> str | None:
    """Normaliza para AAAA-MM-DD, ou None se nao for data reconhecivel.

    Prazo era comparado como STRING lexicografica: '2026-8-25' — 25 de agosto, DENTRO do sprint —
    dava False contra '2026-09-02', porque '8' > '0'. A tarefa ficava retida como "fora do sprint" e
    sumia do portal sem erro.

    Devolver None em vez de chutar e' de proposito: quem chama tem de DIZER que nao entendeu a data,
    nunca tratar como se estivesse fora da janela."""
    v = str(valor or "").strip()
    if not v:
        return None
    try:
        a, m, d = (int(x) for x in v.replace("/", "-").split("-"))
    except (ValueError, TypeError):
        return None
    try:
        dt.date(a, m, d)          # dia do mes de VERDADE: "2026-02-30" nao existe
    except ValueError:
        return None
    if not 1900 <= a <= 2999:
        return None
    return f"{a:04d}-{m:02d}-{d:02d}"


def _num(valor):
    """Numero finito, ou None. Aceita int, float e texto com sinal, ponto ou virgula decimal.

    Duas cicatrizes, das rodadas 3 e 4:
      · `int(v) if v.isdigit() else v` gravava a STRING "-1" no estado, porque `.isdigit()` recusa
        sinal e ponto. O comando seguinte morria com TypeError comparando int com str.
      · `float()` reconhece "nan", "inf", "-inf" e "Infinity". "nan" atravessava a fronteira,
        gravava NaN no estado.json — que NAO e' JSON valido pela RFC 8259 — ordenava em PRIMEIRO
        lugar no adiantamento, e ESCAPAVA do relatorio de ilegibilidade, porque o teste era
        `is None` e nan nao e' None. Corrompia sem deixar rastro."""
    # DECISAO CONSCIENTE, levantada pelo QA da fronteira como aceitacao silenciosa nao decidida:
    # digito nao-ASCII ("１２３", "١٢٣") e separador "1_000" sao aceitos, porque `int()`/`float()` os
    # aceitam e a SAIDA volta sempre em digito ASCII — o valor normalizado e' correto e ordena
    # certo. Recusar seria recusar uma colagem de planilha que esta, no fundo, certa. Fica DITO e
    # testado, em vez de ser comportamento herdado que ninguem escolheu.
    if isinstance(valor, bool):
        return None                        # True nao e' 1 aqui; e' erro de preenchimento
    if isinstance(valor, (int, float)):
        return valor if math.isfinite(valor) else None
    v = str(valor or "").strip().replace(",", ".")
    try:
        return int(v)
    except (ValueError, TypeError):
        pass
    try:
        f = float(v)
    except (ValueError, TypeError):
        return None
    return f if math.isfinite(f) else None


def lista_de(valor, padrao):
    """Uma lista, custe o que custar — mas sem descartar a declaracao do projeto em silencio.

    String vira lista de UM elemento: `"marcadores_de_ausencia": "SEM DONO"` e' erro de edicao
    provavel, e iterar a string caractere a caractere fazia um executor chamado "A" virar ausente.
    Tipo sem conserto cai no padrao — e quem chama diz isso, nao cala."""
    if valor is None:
        return list(padrao), None
    if isinstance(valor, str):
        return [valor], None
    if isinstance(valor, (list, tuple, set, frozenset)):
        return list(valor), None
    return list(padrao), f"{type(valor).__name__} onde se esperava lista — usando o padrao"


# ----------------------------------------------------------------- acessores


def config_num(projeto: dict, estado: dict, caminho: tuple[str, ...], alternativa: str | None,
               padrao):
    """Le um numero de configuracao. Devolve (valor, problema).

    O teto de capacidade vinha de `projeto.json` por `.get()` cru e ia direto para uma comparacao.
    Teto escrito como "3" — erro de edicao tao plausivel quanto o "-1" da List — reproduzia o mesmo
    TypeError, por outra porta.

    A licao que faltava, e que motivou este modulo: fronteira nao e' o `--receber`. E' TODO ponto
    onde valor de fora vira valor usado, nos DOIS modulos, nao so no que foi apontado."""
    cru = projeto
    for chave in caminho:
        cru = (cru or {}).get(chave) if isinstance(cru, dict) else None
    if cru is None and alternativa:
        # [achado MEDIA do QA da fronteira] o acesso a `projeto` era protegido e o a `estado` nao.
        # Guarda assimetrica de novo — a mesma forma de erro dos tres ALTA desta rodada.
        cru = estado.get(alternativa) if isinstance(estado, dict) else None
    if cru is None:
        return padrao, None
    n = _num(cru)
    if n is None:
        return padrao, f"{'.'.join(caminho)}={cru!r} nao e' numero — usando {padrao}"
    return n, None


def exigir_forma(conf: dict, forma: dict, onde: str) -> dict:
    """Confere o TIPO de cada chave declarada, converte o que der, e levanta com mensagem.

    `situacao` como lista derrubava a exportacao com `AttributeError`; `colunas` como string, com
    `TypeError`. Traceback cru nao ajuda quem editou o JSON — mensagem dizendo qual chave e qual
    tipo, sim.

    `forma` mapeia chave -> tipo Python, ou a string "numero" para o que deve passar por `_num`.
    Chave ausente ou None e' ignorada: o padrao de quem chama continua valendo."""
    c, problemas = dict(conf), []
    for chave, esperado in forma.items():
        if chave not in c or c[chave] is None:
            continue
        if not (esperado == "numero" or isinstance(esperado, type)):
            # [achado MEDIA do QA da fronteira, rodada 2] `isinstance(x, None)` levanta TypeError
            # cru. A forma e' escrita a mao pelo autor do modulo consumidor, e `{"campo": None}`
            # pensando "sem checagem" e' confusao plausivel — o docstring ja usa None com OUTRO
            # sentido (valor ausente em `conf`). Erro de quem escreve a forma tambem merece
            # mensagem: e' o mesmo contrato.
            problemas.append(f"a forma declarada para `{chave}` e' {esperado!r}, que nao e' um tipo "
                             f"nem a palavra \"numero\"")
        elif esperado == "numero":
            n = _num(c[chave])
            if n is None:
                problemas.append(f"`{chave}`={c[chave]!r} nao e' numero")
            else:
                c[chave] = n
        elif esperado is not bool and isinstance(c[chave], bool):
            # [achado MEDIA do QA da fronteira] `isinstance(True, int)` e' True em Python, entao uma
            # forma pedindo `int` aceitava `True` — e o mantinha como bool, nao como 1. A direcao
            # oposta (bool pedido, 1 recebido) ja era recusada; faltava a simetria.
            problemas.append(f"`{chave}` e' bool, e tem de ser {esperado.__name__}")
        elif not isinstance(c[chave], esperado):
            problemas.append(f"`{chave}` e' {type(c[chave]).__name__}, e tem de ser "
                             f"{esperado.__name__}")
    if problemas:
        raise ConfiguracaoInvalida(
            f"{onde}: " + "; ".join(problemas)
            + f".\n  Corrija em {DECLARACAO} — tipo errado aqui derruba o comando no meio.")
    return c
