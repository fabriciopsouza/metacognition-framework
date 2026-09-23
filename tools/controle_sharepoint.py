#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""controle_sharepoint — a ida e a volta da List do SharePoint, para qualquer projeto.

E' OPCAO, nao padrao [decisao do dono 21/08/2026]. O padrao do pacote e' planejar, executar, lancar
acao no portal de chamados e manter cronograma. Projeto que nao usa SharePoint declara
`"adotado": {"sharepoint-list": {"usa": false, "por_que": "..."}}` e nunca ve este modulo.

O LACO QUE O DONO DESENHOU, e o defeito que ele tinha:

    eu gero backlog.csv -> automacao sobe para a List -> gestao preenche responsavel e concluido
    -> automacao escreve de volta EM backlog.csv -> eu atualizo o resto

O passo de volta destroi dado em silencio: o backlog e' GERADO. Qualquer regeneracao sobrescreve o
arquivo inteiro, e o que a gestao preencheu na List some sem erro e sem aviso.

O CONSERTO, e ele e' de desenho, nao de cuidado:

    IDA    --exportar             -> LIST-backlog.csv    (derivado, so sai)
    VOLTA  a automacao grava         LIST-retorno.csv    (insumo, so entra)
           --receber              -> escreve no estado do projeto

Arquivo que sai nunca e' o mesmo que entra.

O QUE A LIST PODE MUDAR [correcao do dono 20/08/2026]: responsavel, situacao, PRAZO e prioridade.
A primeira versao bloqueava prazo, e estava errada — reuniao de status replaneja, e bloquear obriga
a abrir o repositorio no meio da reuniao. Ninguem faz, e ai o prazo real diverge do registrado em
silencio, que e' pior que o problema que a restricao queria evitar.

O QUE ELA NAO MUDA, por outro motivo: titulo, fase, dependencia, o que fazer, onde fazer. Isso e'
ESTRUTURA do trabalho — nasce de elicitacao, nao de reuniao de status. Alteracao nesses campos e'
ignorada e RELATADA, nunca calada.

DUAS RECUSAS REAIS DO IMPORTADOR, e as duas ensinaram formato:

  1. "Esquema invalido fornecido"  -> quebra de linha dentro de celula, separador ";" e BOM.
     O importador quer virgula, UTF-8 sem BOM, e nao aceita quebra embutida.
  2. "Linhas 6 e 50 foram omitidos" -> NOME de pessoa que o catalogo nao resolveu. Contando o
     primeiro DADO como linha 1, eram as duas unicas linhas de uma mesma pessoa.
     Dai `responsavel_no_import: false` ser o padrao: o nome entra pela tela da List ou por
     automacao depois da criacao. Campo vazio nao tem como ser recusado.

Uso:
    python tools/controle_sharepoint.py --exportar
    python tools/controle_sharepoint.py --receber              # ensaio: mostra o que mudaria
    python tools/controle_sharepoint.py --receber --confirmar
    python tools/controle_sharepoint.py --projeto <caminho>    # em vez de descobrir pela pasta
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import controle_base as CB     # noqa: E402  — a FRONTEIRA, uma so para os dois modulos
import controle_projeto as CP  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                    # pragma: no cover
    pass

# Padroes de quem nao declarou nada. Existem para o projeto novo funcionar sem configurar tudo —
# nao para esconder configuracao ausente: cada um deles e' anunciado na saida.
PADRAO = {
    "saida": "docs/projeto/LIST-backlog.csv",
    "retorno": "docs/projeto/LIST-retorno.csv",
    "colunas": ["id", "titulo", "responsavel", "situacao", "prazo", "fase", "depende_de"],
    "campos_da_list": ["responsavel", "situacao", "prazo", "prioridade"],
    "situacao": {"para_fazer": "A fazer", "em_execucao": "Em execução", "concluido": "Concluído"},
    "responsavel_no_import": False,
    "limite_coluna": 250,
}


ConfiguracaoInvalida = CB.ConfiguracaoInvalida


# Que forma cada chave da declaracao TEM de ter. Existe porque `projeto.json` e' editado a mao, e
# tipo errado ali nao dava erro de configuracao: dava TypeError/AttributeError com traceback cru no
# meio da exportacao. [ACHADO ALTA DO QA RODADA 5 — e a licao e' que fronteira nao e' o `--receber`:
# e' TODO ponto onde valor de fora vira valor usado, nos DOIS modulos, nao so no que foi apontado.]
FORMA = {
    "saida": str, "retorno": str, "detalhe": str,
    "colunas": list, "campos_da_list": list,
    "situacao": dict, "mapa": dict,
    "responsavel_no_import": bool,
    "limite_coluna": "numero",
}


def _conf(projeto: dict) -> dict:
    c = dict(PADRAO)
    declarado = (projeto.get("sharepoint") or {}).get("list")
    if declarado is not None and not isinstance(declarado, dict):
        raise ConfiguracaoInvalida(
            f"`sharepoint.list` e' {type(declarado).__name__}, e tem de ser um objeto")
    c.update(declarado or {})
    # a checagem de tipo e' a MESMA da fronteira. Ter uma copia aqui foi exatamente o achado da
    # rodada 5: a validacao existia em controle_projeto e faltava neste, lendo o mesmo arquivo.
    return CB.exigir_forma(c, FORMA, "sharepoint.list")


def _detalhe(raiz: Path, conf: dict) -> dict:
    """Fonte opcional de texto por item (titulo legivel, passos, endereco).

    Existe porque o estado guarda a TAREFA e o detalhe guarda como ela foi ESCRITA para quem
    executa. Projeto que nao separa os dois simplesmente nao declara `detalhe`."""
    nome = conf.get("detalhe")
    if not nome:
        return {}
    arq = CB.dentro_da_raiz(raiz, nome, "`sharepoint.list.detalhe`")
    if not arq.is_file():
        raise ConfiguracaoInvalida(f"`sharepoint.list.detalhe` aponta {nome}, que nao existe")
    # [ACHADO ALTA DO QA RODADA 8] isto era `json.loads(read_text(encoding="utf-8"))` CRU. BOM,
    # Latin-1 e forma errada derrubavam --exportar com traceback — os tres modos de falha que a
    # fronteira existe para eliminar, no arquivo que um projeto MAIS edita a mao.
    d = CB._ler_json(arq)
    itens = d.get("itens") if isinstance(d, dict) else d
    if not isinstance(itens, list):
        raise ConfiguracaoInvalida(
            f"{nome} tem de ser uma lista de itens, ou um objeto com a chave `itens`")
    fora = [i for i in itens if not isinstance(i, dict) or "id" not in i]
    if fora:
        raise ConfiguracaoInvalida(
            f"{nome}: {len(fora)} entrada(s) sem `id` ou que nao sao objeto — a primeira e' "
            f"{fora[0]!r}")
    return {m["id"]: m for m in itens}


def _uma_origem(origem: str, item: dict, det: dict, campo: str, situacao: dict) -> str:
    if origem.startswith("detalhe."):
        return str(det.get(origem.split(".", 1)[1]) or "")
    if campo == "situacao":
        return situacao.get(item.get("coluna") or "", "")
    if campo == "depende_de":
        return ", ".join(item.get("depende_de") or [])
    v = item.get(origem)
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    return "" if v is None else str(v)


def _valor(campo: str, item: dict, det: dict, conf: dict, situacao: dict) -> str:
    """Resolve UMA coluna. `mapa` diz de onde vem cada uma, sem tocar codigo.

    [ACHADO ALTA DO QA 21/08/2026] a versao anterior aceitava UMA origem so, e por isso perdeu o
    fallback que a ferramenta do projeto tinha: `titulo or o_que[:80]`. Item ainda sem entrada no
    de-para exportava com titulo VAZIO, sem erro. `mapa` passa a aceitar CADEIA separada por "|" —
    "detalhe.titulo|o_que" — e a primeira origem com valor ganha.

    O limite de tamanho vai junto: "o_que:80" corta em 80 caracteres, que e' o que a versao antiga
    fazia e existe porque titulo de cartao nao e' paragrafo."""
    mapa = conf.get("mapa") or {}
    for origem in str(mapa.get(campo, campo)).split("|"):
        origem = origem.strip()
        limite = None
        if ":" in origem and not origem.startswith("detalhe."):
            origem, _, corte = origem.partition(":")
            limite = int(corte) if corte.isdigit() else None
        elif origem.count(":") == 1 and origem.startswith("detalhe."):
            origem, _, corte = origem.rpartition(":")
            limite = int(corte) if corte.isdigit() else None
        v = _uma_origem(origem, item, det, campo, situacao)
        if v:
            # [ACHADO MEDIA DO QA RODADA 2] era `if limite else v`, e corte 0 e' FALSY: "campo:0"
            # devolvia o valor INTEIRO em vez de string vazia. E' a MESMA classe do teto falsy que o
            # ADR-113 registra como achado do canario — nao propagada ao vizinho no mesmo commit.
            # A licao do dono e' explicita: correcao num fluxo aplica aos irmaos NA MESMA iteracao.
            return v if limite is None else v[:limite]
    return ""


def exportar(raiz: Path, projeto: dict, estado: dict) -> int:
    conf = _conf(projeto)
    det_todos = _detalhe(raiz, conf)
    situacao = conf["situacao"]
    cols = conf["colunas"]
    saida = CB.dentro_da_raiz(raiz, conf["saida"], "`sharepoint.list.saida`")

    linhas, sem_detalhe = [], []
    for i in estado.get("itens") or []:
        det = det_todos.get(i["id"]) or {}
        if det_todos and i["id"] not in det_todos:
            # o fallback do `mapa` salva a linha; nao salva a DIVIDA. Item que nunca ganhou entrada
            # no de-para vai para a List com o texto cru da tarefa, e isso tem de ser dito.
            sem_detalhe.append(i["id"])
        linha = {c: _valor(c, i, det, conf, situacao) for c in cols}
        if "responsavel" in linha and not conf["responsavel_no_import"]:
            # [DECISAO DO DONO 20/08/2026] o nome NAO vai no import. Ele entra pela tela da List ou
            # por automacao depois da criacao — que foi o que o SharePoint recusou. Campo vazio nao
            # tem como ser recusado, e a List existe justamente para RECEBER o nome.
            linha["responsavel"] = ""
        elif "responsavel" in linha and CP._sem_executor(i, projeto):
            linha["responsavel"] = ""     # marcador nao e' nome; a List existe para receber o nome
        linhas.append(linha)

    # [FALHA REAL, 1a recusa] 30 celulas tinham QUEBRA DE LINHA dentro (passos numerados), o
    # separador era ";" e havia BOM: 161 linhas fisicas para 64 logicas viram esquema quebrado.
    # Formato de saida se decide pelo CONSUMIDOR, nao pelo habito de quem gera.
    for linha in linhas:
        for k, v in list(linha.items()):
            if isinstance(v, str) and ("\n" in v or "\r" in v):
                linha[k] = " ".join(x.strip() for x in v.splitlines() if x.strip())

    # [ACHADO ALTA DO QA RODADA 11] isto era `saida.open("w", ...)` cru: CSV somente-leitura
    # derrubava --exportar com PermissionError. Monta em memoria e grava pela porta unica.
    buffer = io.StringIO()
    w = csv.DictWriter(buffer, fieldnames=cols, delimiter=",", quoting=csv.QUOTE_ALL)
    w.writeheader()
    w.writerows(linhas)
    CB.escrever_texto(saida, buffer.getvalue(), "o CSV da ida")

    # releitura do que acabamos de gravar, para conferir as linhas fisicas. Passa pela porta unica
    # tambem: falha de disco entre o write e este read subia crua. [ressalva do QA rodada 10]
    bruto = CB.ler_texto(saida, "o CSV recem-gerado")
    fisicas = bruto.count("\n")
    if fisicas != len(linhas) + 1:
        print(f"  REPROVADO: {fisicas} linhas fisicas para {len(linhas)} de dados — sobrou quebra")
        print("  embutida, e o importador vai recusar de novo.")
        return 1

    longos = sorted({k for l in linhas for k, v in l.items()
                     if isinstance(v, str) and len(v) > conf["limite_coluna"]})
    print(f"PASS — {conf['saida']}: {len(linhas)} linhas, {len(cols)} colunas")
    print(f"  formato: virgula, UTF-8 sem BOM, tudo entre aspas, sem quebra dentro de celula")
    print(f"  conferido: {fisicas} linhas fisicas = {len(linhas)} de dados + cabecalho")
    if longos:
        print(f"  passam de {conf['limite_coluna']} caracteres: {', '.join(longos)}")
        print("  -> marque essas colunas como 'Varias linhas de texto' na importacao")
    if sem_detalhe:
        print(f"  {len(sem_detalhe)} item(ns) SEM entrada no detalhe — sairam com o texto cru da")
        print(f"  tarefa, pelo fallback do `mapa`: {', '.join(sorted(sem_detalhe)[:10])}")
        print("  Escrever o cartao deles continua pendente.")
    if not conf["responsavel_no_import"]:
        print("  coluna `responsavel`: VAZIA de proposito. O nome entra pela tela da List ou por")
        print("  automacao depois da criacao — foi mandar nome no import que derrubou linha.")
    print("  Este arquivo SAI. A volta NUNCA vem por ele: vem por " + conf["retorno"])
    return 0


def _pessoas(raiz: Path, projeto: dict):
    """{nome_do_projeto: {ad, email}} e o caminho inverso. Vazio se o projeto nao declarar."""
    nome = (projeto.get("sharepoint") or {}).get("pessoas")
    if not nome:
        return {}, {}
    arq_pes = CB.dentro_da_raiz(raiz, nome, "`sharepoint.pessoas`")
    if not arq_pes.is_file():
        return {}, {}
    # [ACHADO ALTA DO QA RODADA 8] mesma leitura crua, mesmo modo de falha — e aqui `pessoas` que
    # nao fosse lista dava `AttributeError: 'str' object has no attribute 'get'` no meio do
    # --receber, depois de o comando ja ter comecado a trabalhar.
    d = CB._ler_json(arq_pes)
    if not isinstance(d, dict) or not isinstance(d.get("pessoas", []), list):
        raise ConfiguracaoInvalida(
            f"{nome} tem de ser um objeto com a chave `pessoas` contendo uma lista")
    direto, inverso = {}, {}
    for pe in d.get("pessoas", []):
        if not isinstance(pe, dict):
            raise ConfiguracaoInvalida(f"{nome}: ha entrada em `pessoas` que nao e' objeto: {pe!r}")
        n = pe.get("projeto")
        ad, mail = (pe.get("ad") or ""), (pe.get("email") or "")
        if not n:
            continue
        direto[n] = {"ad": ad if ad != "PENDENTE" else "", "email": mail if mail != "PENDENTE" else ""}
        for chave in (ad, mail, n):
            if chave and chave != "PENDENTE":
                inverso[chave.strip().lower()] = n
    return direto, inverso


def _do_ad(valor: str, inverso: dict) -> str:
    """Traduz o que a List devolveu para o nome usado no projeto.

    A coluna Pessoa nao devolve texto: devolve o objeto. Dependendo do fluxo isso chega como e-mail
    ou como claims string (`i:0#.f|membership|fulano@...`). Reconhecer as tres formas custa dez
    linhas e evita que a volta pareca vazia quando nao esta."""
    v = (valor or "").strip()
    if not v:
        return v
    if "|" in v:
        v = v.rsplit("|", 1)[-1].strip()
    return inverso.get(v.lower(), v)


def _historia(item: dict, campo: str, valor) -> None:
    """Toda mudanca vinda da List fica registrada. Prazo que muda sem rastro e' prazo que ninguem
    consegue explicar tres semanas depois."""
    item.setdefault("historico", []).append(
        {"quando": dt.date.today().isoformat(), "de_onde": "List do SharePoint",
         "campo": campo, "para": valor})


def _consequencias(estado: dict, projeto: dict) -> list[str]:
    """O que a mudanca de prazo QUEBRA. E' aqui que esta o risco de liberar prazo na List: mover
    uma data nao avisa que a dependencia ficou depois, nem que passou do prazo externo."""
    por_id = {i["id"]: i for i in estado.get("itens") or []}
    limite = estado.get("prazo_externo") or ""
    isento = (projeto.get("trilha_isenta_do_prazo_externo") or "")
    alertas = []
    limite = CP._data(limite) or ""
    for i in estado.get("itens") or []:
        # [ACHADO ALTA DO QA] aqui a data tambem era comparada como STRING crua: '2026-8-25' saia
        # maior que '2026-11-01' e virava alerta falso de "depois do limite externo".
        pz = CP._data(i.get("prazo")) or ""
        if not pz:
            continue
        for dep in (i.get("depende_de") or []):
            d = por_id.get(dep)
            dp = CP._data(d.get("prazo")) if d else None
            if dp and pz and dp > pz:
                alertas.append(f"{i['id']} vence {pz}, mas depende de {dep}, que vence "
                               f"{d['prazo']} — a ordem ficou impossivel")
        if limite and pz > limite and (i.get("trilha") or "") != isento:
            alertas.append(f"{i['id']} vence {pz}, DEPOIS do limite externo em {limite}")
    return alertas


def receber(raiz: Path, projeto: dict, estado: dict, confirmar: bool) -> int:
    conf = _conf(projeto)
    retorno = CB.dentro_da_raiz(raiz, conf["retorno"], "`sharepoint.list.retorno`")
    if not retorno.is_file():
        print(f"NAO ENCONTRADO: {conf['retorno']}")
        print("  E' o arquivo que a automacao grava com o que a List mudou.")
        print(f"  Colunas minimas: id, {', '.join(conf['campos_da_list'])}")
        return 1

    campos_ok = {c.lower() for c in conf["campos_da_list"]}
    de_volta = {v.lower(): k for k, v in conf["situacao"].items()}
    _pes, inverso = _pessoas(raiz, projeto)
    por_id = {i["id"]: i for i in estado.get("itens") or []}

    # [ACHADO ALTA DO QA RODADA 9] isto era `.read_text()` sem guarda. Um retorno em Latin-1 ou
    # binario derrubava --receber com UnicodeDecodeError cru — mesma classe que a rodada 8 corrigiu
    # para JSON, no unico CSV que o pacote LE. E o docstring deste modulo chama esse arquivo de
    # "preenchido por gente numa planilha", que e' a definicao de entrada nao-confiavel.
    bruto = CB.ler_texto(retorno, "o arquivo de volta da List")
    # o separador da volta segue o que a automacao gravar. Detectar e' mais barato que combinar por
    # prosa e descobrir na hora errada.
    cab = bruto.split("\n", 1)[0]
    sep = ";" if cab.count(";") > cab.count(",") else ","
    vindos = list(csv.DictReader(bruto.splitlines(), delimiter=sep))

    mudancas, ignorados, desconhecidos, recusados = [], [], [], []
    for r in vindos:
        ident = (r.get("id") or "").strip()
        item = por_id.get(ident)
        if not item:
            desconhecidos.append(ident or "(sem id)")
            continue
        for campo, valor in r.items():
            campo = (campo or "").strip().lower()
            valor = (valor or "").strip()
            if campo in ("id", "") or not valor:
                continue
            if campo not in campos_ok:
                # a List nao manda neste campo. Nao entra, e nao passa calado.
                atual = str(item.get(campo, ""))
                if valor != atual:
                    ignorados.append((ident, campo, atual, valor))
                continue
            if campo == "responsavel":
                valor = _do_ad(valor, inverso)
                # [achado BAIXA do QA rodada 3] so a CAIXA mudando gerava "mudanca" e churn de
                # historico. A identidade da pessoa e' a chave normalizada; a grafia nao e' evento.
                if CP._chave_executor(valor) == CP._chave_executor(item.get("responsavel") or ""):
                    continue
            if campo == "situacao":
                nova = de_volta.get(valor.lower())
                if nova is None:
                    # [ACHADO ALTA DO QA RODADA 4] isto caia direto no `continue`: nao entrava em
                    # `mudancas`, nem em `ignorados`, nem em `recusados`. Um status novo criado na
                    # List, ou so um acento diferente, sumia sem uma palavra — que e' EXATAMENTE o
                    # "passo de volta destroi dado em silencio" que este modulo existe para evitar.
                    recusados.append((ident, campo, valor))
                elif nova != item.get("coluna"):
                    mudancas.append((ident, "coluna", item.get("coluna"), nova))
                    if confirmar:
                        item["coluna"] = nova
                        _historia(item, "situacao", valor)
                continue
            # [ACHADO ALTA DO QA RODADA 3] AQUI era a fronteira que deixava dado sujo entrar.
            # `int(valor) if valor.isdigit() else valor` — e `"-1".isdigit()` e' False, `"3.5"`
            # tambem — gravava a STRING no estado, calado. O `--adiantar` seguinte crashava com
            # TypeError comparando int com str: o comando inteiro morria, para o projeto todo.
            #
            # A licao das quatro rodadas: eu vinha normalizando no ponto de COMPARACAO, e enquanto
            # o dado sujo puder ENTRAR sempre havera uma comparacao ainda nao normalizada. Converte
            # ou RECUSA na fronteira; nunca grava o que nao se sabe ler.
            atual = item.get(campo)
            novo = valor
            if campo == "prioridade":
                n = CP._num(valor)
                if n is None:
                    recusados.append((ident, campo, valor))
                    continue
                novo = int(n) if float(n).is_integer() else n
            if campo == "prazo":
                d = CP._data(valor)
                if d is None:
                    recusados.append((ident, campo, valor))
                    continue
                novo = d               # entra normalizado: "2026-8-5" vira "2026-08-05"
            if novo != (atual if atual is not None else ""):
                mudancas.append((ident, campo, atual, novo))
                if confirmar:
                    item[campo] = novo
                    _historia(item, campo, novo)

    print(f"{'RECEBENDO' if confirmar else 'ENSAIO'} — {len(vindos)} linha(s) na volta "
          f"(separador {sep!r})\n")
    for ident, campo, antes, depois in mudancas:
        print(f"  muda  {ident:5s} {campo:12s} {antes!r} -> {depois!r}")
    if not mudancas:
        print("  nada a mudar")
    if ignorados:
        print(f"\n  {len(ignorados)} alteracao(oes) IGNORADA(S) — sao ESTRUTURA do trabalho:")
        print("  o que a tarefa e', onde se faz, de quem depende. Isso nasce de elicitacao, nao de")
        print("  reuniao de status. Se a mudanca for legitima, faca no repositorio.")
        for ident, campo, antes, depois in ignorados[:6]:
            print(f"   x {ident:5s} {campo:12s} {antes!r} -> {depois!r}")
    if recusados:
        print(f"\n  {len(recusados)} valor(es) RECUSADO(S) na fronteira — nao entraram no estado")
        print("  porque nao dava para ler. Gravar o que nao se sabe ler mata o comando seguinte:")
        for ident, campo, cru in recusados[:6]:
            print(f"   x {ident:5s} {campo:12s} {cru!r}")
        print("  Corrija na List e receba de novo. Prioridade e' numero; prazo e' AAAA-MM-DD;")
        print(f"  situacao tem de ser uma de: {', '.join(sorted(conf['situacao'].values()))}.")
    if desconhecidos:
        print(f"\n  {len(desconhecidos)} linha(s) com id que nao existe aqui: "
              f"{', '.join(desconhecidos[:6])}")
        print("  Tarefa criada direto na List nao entra por aqui — ela nasce no repositorio.")

    if any(c[1] == "prazo" for c in mudancas):
        provisorio = json.loads(json.dumps(estado))
        por_id_p = {i["id"]: i for i in provisorio["itens"]}
        for ident, campo, _a, depois in mudancas:
            if campo == "prazo" and ident in por_id_p:
                por_id_p[ident]["prazo"] = depois
        alertas = _consequencias(provisorio, projeto)
        if alertas:
            print(f"\n  {len(alertas)} CONSEQUENCIA(S) da mudanca de prazo:")
            for al in alertas:
                print("   ! " + al)
            print("  Isto NAO impede a mudanca — replanejar e' direito da reuniao. Mas fica dito,")
            print("  porque prazo movido em planilha nao avisa o que arrastou junto.")

    if confirmar and mudancas:
        # [ACHADO ALTA DO QA RODADA 11] esta era a escrita de MAIOR consequencia do pacote — a
        # unica que persiste mudanca — e era a que crashava pior: estado somente-leitura derrubava
        # com PermissionError cru, depois de o comando ja ter relatado tudo o que ia mudar.
        arq = CB.dentro_da_raiz(raiz, projeto.get("estado") or "estado.json", "`estado`")
        CB.escrever_texto(arq, json.dumps(estado, ensure_ascii=False, indent=2) + "\n",
                          "o estado do projeto")
        print(f"\n  {arq.name} atualizado.")
    elif not confirmar:
        print("\n  ENSAIO — nada foi escrito. Para valer: --receber --confirmar")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--projeto", help="raiz do projeto (senao: env, senao sobe da pasta corrente)")
    ap.add_argument("--exportar", action="store_true", help="gera o CSV que sobe para a List")
    ap.add_argument("--receber", action="store_true", help="le a volta da List para o estado")
    ap.add_argument("--confirmar", action="store_true", help="com --receber, grava de verdade")
    a = ap.parse_args(argv)
    try:
        raiz, origem = CP.raiz_projeto(a.projeto)
        projeto, estado = CP.carregar(raiz)
    except CP.ProjetoInvalido as e:
        print(f"PROJETO NAO RESOLVIDO: {e}")
        return 1

    adotado = (projeto.get("adotado") or {}).get("sharepoint-list")
    if adotado is False or (isinstance(adotado, dict) and adotado.get("usa") is False):
        print("Este projeto declarou que NAO usa a List do SharePoint.")
        print(f"  Para adotar, mude `adotado.sharepoint-list` em {CP.DECLARACAO}.")
        return 1

    print(f"projeto: {raiz}  ({origem})")
    try:
        if a.exportar:
            return exportar(raiz, projeto, estado)
        if a.receber:
            return receber(raiz, projeto, estado, a.confirmar)
    # A FAMILIA INTEIRA, nao metade dela.
    #
    # `exportar()`/`receber()` chamam `CB.dentro_da_raiz()` sobre
    # `sharepoint.list.saida`/`.retorno`/`.detalhe` — caminhos que vem do
    # `projeto.json` editado A MAO e que so' passam por checagem de TIPO antes
    # daqui. Um `"../fora.csv"` colado por engano levanta `ProjetoInvalido`, que
    # NAO estava nesta captura: o processo terminava com traceback Python cru,
    # no mesmo modulo cujas treze rodadas de QA foram gastas justamente para
    # trocar stack trace por mensagem.
    #
    # E os testes nao viam porque chamavam `exportar()`/`receber()` DIRETO. A
    # funcao interna levantar a excecao e' o comportamento CERTO dela; o defeito
    # morava um nivel acima, no `main()` que deveria converter em mensagem.
    # Nenhum teste exercitava a CLI com caminho fora da raiz.
    # [achado bloqueante do QA de 18/09/2026]
    except (ConfiguracaoInvalida, CB.ProjetoInvalido) as e:
        print(f"CONFIGURACAO INVALIDA: {e}")
        return 1
    ap.error("escolha --exportar ou --receber")


if __name__ == "__main__":
    raise SystemExit(main())
