#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""controle_projeto — a POLITICA DE LANCAMENTO de um projeto, uma vez, para qualquer projeto.

O QUE RESOLVE. Um projeto tem sessenta tarefas e a equipe tem quatro pessoas. Lancar as sessenta no
portal de chamados nao acelera nada: enterra o que importa, e o quadro deixa de ser lido. Mas
segurar tarefa pronta tambem custa — trabalho automatizavel fica parado esperando alguem lembrar.

Este modulo decide O QUE PODE SER LANCADO e QUANDO, por regra escrita, nao por memoria do operador.

AS QUATRO REGRAS [decisao do dono 21/08/2026], na ordem em que ele as declarou:

  1. So o SPRINT corrente vai para o portal. O resto vive no backlog e no espelho.
  2. So tarefa COM EXECUTOR definido e' lancada. Tarefa sem dono aparece para o time inteiro e
     polui o backlog geral — regra dele, de 20/08/2026.
  3. Se o sprint acabou, PERGUNTAR ao dono "adiantar tarefas?" e adiantar um numero que nao
     sobrecarregue. Perguntar, nunca decidir sozinho (ADR-111).
  4. Tarefa AUTOMATIZAVEL sem impedimento e' monitorada e executada o quanto antes.

A regra 2 nao e' um degrau da ordem: e' um FILTRO que vale para todas. A politica efetiva de
lancamento e' `dentro do sprint` E `com executor`. As regras 3 e 4 e' que sao mecanismo novo.

[PROCEDENCIA, porque o QA cobrou e estava certo em cobrar] esta leitura NAO e' inferencia do autor:
foi levada ao dono como decisao-em-aberto, com as tres alternativas escritas, e ele escolheu
"quem quer que esteja designado — a regra 2 vira: so lanca tarefa que tem executor definido"
(21/08/2026), confirmando depois com "agente = executor = responsavel". O que faltava era a MARCA
da confirmacao aqui no codigo: sem ela, quem le nao distingue decisao do dono de escolha do autor.

AGENTE = EXECUTOR = RESPONSAVEL [correcao do dono 21/08/2026]. Um campo so. O portal de chamados
nao tem usuario "agente", entao quem resolve isso e' o ADAPTADOR, na hora de lancar o cartao:
`agente_responde_por` diz qual conta humana recebe. O dado do projeto continua com um campo.

O LIMITE DA REGRA 4, e ele vem de outra regra do dono: "tudo que envolver decisao, numero, valor,
critico, deve ser revisado por humano". Entao auto-execucao so alcanca classe declarada como
inocua — ler, coletar, publicar derivado. Tarefa que decide, calcula ou altera sistema de terceiro
para na fila COM o resultado pronto, e o humano aprova. E este modulo nao executa nada: ele
IDENTIFICA e mede impedimento. Quem executa e' o agente, e deixa prova.

ONDE MORA O QUE NAO ESTA AQUI [decisao do dono 21/08/2026, "reabrir o desenho"]: converter, validar
e resolver valor vindo de fora e' `tools/controle_base.py`. Cinco rodadas de critica acharam quase
todos os defeitos naquela camada, e ela estava espalhada entre este modulo e o da List — o que fez a
validacao existir num e faltar no irmao, lendo o MESMO projeto.json. Agora ha uma so.

COMO CHEGA EM QUALQUER PROJETO: por RESOLVEDOR, nunca por copia. O
projeto guarda `projeto.json` (declaracao) e o seu proprio estado (dado). As ferramentas vivem uma
vez, aqui. Copia foi descartada por motivo medido: os repos-sombra deste framework congelaram vinte
releases atras porque ninguem viu a copia envelhecer.

Uso:
    python tools/controle_projeto.py --situacao          # o que pode ir, o que esta retido e por que
    python tools/controle_projeto.py --adiantar 3        # so com autorizacao ativa do dono
    python tools/controle_projeto.py --auto              # automatizavel sem impedimento, agora
    python tools/controle_projeto.py --revisar-adocao    # o projeto adotou as features do pacote?
    python tools/controle_projeto.py --projeto <caminho> # em vez de descobrir pela pasta corrente

Codigos de saida: 0 ok · 1 reprovado · 2 pergunta pendente ao dono.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                    # pragma: no cover - so em stdout exotico
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from controle_base import (           # noqa: E402  — a FRONTEIRA vive uma vez, ver controle_base
    DECLARACAO, ENV_PROJETO, ProjetoInvalido, _caminho, _chave_executor, _data, _num, carregar,
    config_num as _config_num, escrever_texto, lista_de, raiz_projeto,
)

RAIZ_NUCLEO = Path(__file__).resolve().parent.parent

# AS FEATURES DO PACOTE, com a versao em que entraram. [pedido do dono 21/08/2026] "pacote deve ser
# atualizado/revisado nos projetos sempre que houver feature nova adotada".
#
# Com resolvedor o CODIGO ja chega atualizado sozinho — nao ha copia para envelhecer. O que
# envelhece e' a DECLARACAO do projeto: feature nova nasce sem ninguem ter dito se aquele projeto a
# usa. Sem esta lista, feature entra no nucleo e fica orfa, existindo e nao sendo usada por
# ninguem. Feature nova aqui obriga cada projeto a se pronunciar: adotou, ou dispensou e por que.
FEATURES = {
    "sprint":           ("1.0", "so o sprint corrente vai para o portal"),
    "executor":         ("1.0", "so tarefa com executor definido e' lancada"),
    "adiantamento":     ("1.0", "sprint concluido pergunta ao dono antes de puxar tarefa"),
    "auto":             ("1.0", "tarefa automatizavel sem impedimento e' monitorada e executada"),
    "revisao-adocao":   ("1.0", "o projeto declara o que adotou de cada versao do pacote"),
    "sharepoint-list":  ("1.0", "laco da List do SharePoint — OPCAO, nao padrao"),
}
VERSAO_PACOTE = "1.0"

CLASSES_AUTO_PADRAO = ["leitura", "coleta", "publicacao"]


# ----------------------------------------------------------------------------- resolucao


# ----------------------------------------------------------------------------- as regras


def _sprint(estado: dict, projeto: dict) -> dict:
    """A janela declarada, se ela tiver a forma de uma janela.

    [ACHADO ALTA DO QA RODADA 3] isto devolvia o que estivesse la, sem checar. `sprint: ["a","b"]`
    fazia o comando DEFAULT crashar com AttributeError e traceback cru — enquanto prazo malformado
    de ITEM ja era relatado com elegancia. Mesma assimetria de antes, uma camada acima: o VALOR era
    validado, a FORMA nao. Forma errada agora vira {} aqui e denuncia em `sprint_ilegivel`."""
    for fonte in (estado.get("sprint"), projeto.get("sprint")):
        if isinstance(fonte, dict) and fonte:
            return fonte
    return {}


def sprint_ilegivel(estado: dict, projeto: dict) -> list[str]:
    """A janela do sprint esta escrita como data, e tem a forma de uma janela?

    [ACHADO ALTA DO QA RODADA 2] janela invalida faz `_no_sprint` devolver True para tudo — o que
    esta certo, porque reter trabalho por causa de um typo do dono seria pior. O ERRADO era o
    silencio: prazo ilegivel de ITEM ja era relatado, e o do SPRINT nao.

    [ACHADO ALTA DO QA RODADA 3] e a FORMA tambem nao era checada: `sprint: ["a","b"]` crashava o
    comando default com AttributeError e traceback cru."""
    sp, ruins = _sprint(estado, projeto), []
    for onde, cru in (("estado", estado.get("sprint")), ("projeto", projeto.get("sprint"))):
        if cru is not None and not isinstance(cru, dict):
            ruins.append(f"{onde}.sprint e' {type(cru).__name__}, nao um objeto com inicio/fim")
    for campo in ("inicio", "fim"):
        cru = sp.get(campo)
        if cru and _data(cru) is None:
            ruins.append(f"sprint.{campo}={cru!r}")
    ini, fim = _data(sp.get("inicio")), _data(sp.get("fim"))
    if ini and fim and ini > fim:
        ruins.append(f"sprint comeca em {ini} e termina em {fim} — a janela esta invertida")
    return ruins


def prazos_ilegiveis(estado: dict) -> list[tuple[str, str]]:
    """Itens cujo prazo existe mas nao e' data. Existem para serem DITOS, nao silenciados."""
    return [(i["id"], i.get("prazo")) for i in (estado.get("itens") or [])
            if (i.get("prazo") or "").strip() and _data(i.get("prazo")) is None]


def _sem_executor(item: dict, projeto: dict) -> bool:
    """Regra 2. Marcador nao e' executor: 'A DEFINIR' e 'PENDENTE' contam como vazio.

    Isto ja mordeu antes — um gerador partiu 'A DEFINIR na abertura' no primeiro espaco e escreveu
    'responsavel: A' no cartao. Marcador tem de ser reconhecido como ausencia, nao como nome."""
    r = (item.get("responsavel") or "").strip()
    if not r:
        return True
    marcadores, _ruim = lista_de(projeto.get("marcadores_de_ausencia"),
                                 ["A DEFINIR", "PENDENTE", "TBD", "N/A", "-"])
    alvo = r.upper()
    for m in marcadores:
        mu = m.strip().upper()
        if not mu:
            continue
        if alvo == mu:
            return True
        # marcador SEGUIDO DE FRONTEIRA: "A DEFINIR na abertura", "PENDENTE - aguardando GQ".
        #
        # [DEFEITO ACHADO 21/08/2026] a primeira versao usava `m in r` — SUBSTRING — e isso tratava
        # "Ana-Maria", "Jean-Pierre" e "TBDaniel" como SEM EXECUTOR, porque "-" cabe em qualquer
        # nome hifenizado e "TBD" cabe em "TBDaniel". As tarefas dessas pessoas sumiriam do portal
        # sem erro e sem aviso, que e' a pior forma de errar aqui.
        #
        # O canario nao pegou porque so testava os marcadores PUROS, nunca um nome que os CONTEM.
        # Caso bom e caso ruim obvio nao cobrem a fronteira entre os dois.
        if alvo.startswith(mu) and (len(alvo) == len(mu) or not alvo[len(mu)].isalnum()):
            return True
    return False


def _no_sprint(item: dict, sprint: dict, projeto: dict | None = None) -> bool:
    """Regra 1. Sem sprint declarado, tudo passa — o projeto ainda nao adotou a feature, e
    silenciar tarefa por causa disso seria pior que nao filtrar.

    [DEFEITO ACHADO AO RECONCILIAR COM O PROJETO REAL, 21/08/2026] a primeira versao olhava so o
    prazo, e por isso teria TIRADO 3 tarefas do quadro do projeto SAC: as que ja estavam em
    execucao ou concluidas com prazo fora da janela. Tarefa que a equipe ja comecou nao pode sumir
    do quadro porque o sprint virou — o quadro e' tambem o historico, e retroceder o historico
    apaga o trabalho feito aos olhos de quem o fez.

    Reconciliar contra o comportamento vivo achou isto. Testar so contra o meu proprio modelo
    mental nao teria achado."""
    projeto = projeto or {}
    if not sprint.get("inicio") or not sprint.get("fim"):
        return True
    if (item.get("coluna") or "") in _colunas_visiveis(projeto):
        return True
    prazo, ini, fim = _data(item.get("prazo")), _data(sprint["inicio"]), _data(sprint["fim"])
    if prazo is None:
        # prazo vazio OU ilegivel. Nenhum dos dois entra no sprint por acidente; quem chama
        # relata os ilegiveis por `prazos_ilegiveis`, para nao sumirem calados.
        return False
    if ini is None or fim is None:
        return True                      # janela invalida nao pode reter trabalho: melhor nao filtrar
    return ini <= prazo <= fim


def _colunas_visiveis(projeto: dict) -> set[str]:
    """Colunas cujo item fica no quadro independentemente do sprint: o que ja andou."""
    return {projeto.get("coluna_em_execucao") or "em_execucao",
            projeto.get("coluna_concluido") or "concluido"}


def _concluido(item: dict, projeto: dict) -> bool:
    fim = projeto.get("coluna_concluido") or "concluido"
    return (item.get("coluna") or "") == fim


def politica(estado: dict, projeto: dict) -> dict:
    """Aplica as regras 1 e 2 e devolve o que pode ir, o que ficou e POR QUE ficou.

    O `por_que` nao e' cortesia: retencao silenciosa e' como tarefa some sem ninguem notar."""
    sprint = _sprint(estado, projeto)
    lancaveis, retidos = [], []
    for i in estado.get("itens") or []:
        if not _no_sprint(i, sprint, projeto):
            retidos.append((i["id"], "fora do sprint corrente"))
        elif _sem_executor(i, projeto):
            retidos.append((i["id"], "sem executor definido"))
        else:
            lancaveis.append(i)
    return {"sprint": sprint, "lancaveis": lancaveis, "retidos": retidos}


def sprint_concluido(estado: dict, projeto: dict) -> tuple[bool, int, int]:
    """Regra 3, primeira metade. Sprint vazio NAO conta como concluido: 'nao ha nada' e 'acabou
    tudo' sao estados diferentes, e tratar um como o outro faria a ferramenta pedir adiantamento
    para um projeto que sequer comecou."""
    p = politica(estado, projeto)
    dentro = [i for i in (estado.get("itens") or []) if _no_sprint(i, p["sprint"], projeto)]
    feitos = [i for i in dentro if _concluido(i, projeto)]
    return (bool(dentro) and len(feitos) == len(dentro)), len(feitos), len(dentro)


def carga_atual(estado: dict, projeto: dict) -> dict[str, int]:
    """Quantas tarefas cada executor ja tem em andamento. Base do 'sem sobrecarregar'."""
    em_curso = projeto.get("coluna_em_execucao") or "em_execucao"
    carga: dict[str, int] = {}
    for i in estado.get("itens") or []:
        if (i.get("coluna") or "") == em_curso and not _sem_executor(i, projeto):
            # chave NORMALIZADA: "Bruno", "BRUNO" e "bruno " sao a mesma pessoa e a mesma carga
            carga[_chave_executor(i["responsavel"])] = \
                carga.get(_chave_executor(i["responsavel"]), 0) + 1
    return carga


def candidatos_adiantamento(estado: dict, projeto: dict, quantos: int) -> dict:
    """Regra 3, segunda metade. Puxa as proximas por prioridade SEM estourar a capacidade.

    O teto vem de `capacidade.em_execucao_por_pessoa`. Tarefa sem executor NAO pode ser puxada:
    sem dono nao ha como saber a carga de ninguem, e puxar assim mesmo transformaria 'sem
    sobrecarregar' em enfeite. Elas voltam como `sem_executor`, contadas e ditas."""
    # [DEFEITO ACHADO PELO CANARIO 21/08/2026] isto era uma cadeia de `or`, e teto 0 e' FALSY:
    # `0 or 3` da' 3. O comando que deveria congelar a equipe inteira liberava tres por pessoa, em
    # silencio. Teto 0 e' valor VALIDO e significa "ninguem pega mais nada" — cadeia de `or` nao
    # sabe distinguir "nao declarado" de "declarado zero".
    teto, problema_teto = _config_num(projeto, estado,
                                      ("capacidade", "em_execucao_por_pessoa"),
                                      "limite_em_execucao", 3)
    sprint = _sprint(estado, projeto)
    carga = carga_atual(estado, projeto)

    fora = [i for i in (estado.get("itens") or [])
            if not _no_sprint(i, sprint, projeto) and not _concluido(i, projeto)]
    # [ACHADOS DA VARREDURA DE CLASSE 21/08/2026] esta linha tinha DOIS defeitos da mesma familia:
    #
    #   `i.get("prazo") or "9999"` — ordem por STRING crua. '2026-12-1' < '2026-9-3' porque '1'<'9',
    #   entao a tarefa de DEZEMBRO era adiantada antes da de SETEMBRO. Achado pelo QA rodada 2.
    #
    #   `i.get("prioridade") or 999` — prioridade 0 significa a MAIS ALTA, e' falsy, e virava 999,
    #   a mais baixa: a tarefa mais urgente do projeto seria a ULTIMA a ser adiantada. Nao foi
    #   achado por nenhum critico — apareceu na varredura da familia "zero valido cai como falsy",
    #   que so foi feita porque o critico disse que a classe estava sobrevivendo ao processo.
    def _ordem(i):
        # `_num` em vez do valor cru: estado escrito a mao nao passa por fronteira nenhuma, e
        # comparar int com str nao ordena errado — MATA o comando com TypeError. [QA rodada 3]
        pr = _num(i.get("prioridade"))
        return (999 if pr is None else pr,      # 0 e' prioridade valida, e e' a mais alta
                _data(i.get("prazo")) or "9999-12-31",
                str(i["id"]))

    fora.sort(key=_ordem)

    escolhidos, sem_executor, estourariam = [], [], []
    for i in fora:
        if len(escolhidos) >= quantos:
            break
        if _sem_executor(i, projeto):
            sem_executor.append(i["id"])
            continue
        r, k = i["responsavel"].strip(), _chave_executor(i["responsavel"])
        if carga.get(k, 0) + 1 > teto:
            estourariam.append((i["id"], r, carga.get(k, 0), teto))
            continue
        carga[k] = carga.get(k, 0) + 1
        escolhidos.append(i)
    return {"teto": teto, "escolhidos": escolhidos, "sem_executor": sem_executor,
            "estourariam": estourariam, "disponiveis": len(fora), "problema": problema_teto}


def impedimentos(item: dict, estado: dict, projeto: dict) -> list[str]:
    """Regra 4. O que impede ESTA tarefa de ser executada agora."""
    por_id = {i["id"]: i for i in (estado.get("itens") or [])}
    presos = []
    if item.get("travado"):
        presos.append(f"travado por {item.get('travado_em') or 'motivo nao declarado'}")
    for dep in (item.get("depende_de") or []):
        d = por_id.get(dep)
        if d is None:
            presos.append(f"depende de {dep}, que nao existe no estado")
        elif not _concluido(d, projeto):
            presos.append(f"depende de {dep}, ainda nao concluida")
    for req in (item.get("requer") or []):
        # credencial/acesso que o projeto declara ter ou nao ter. Nao adivinhamos.
        if req not in (projeto.get("disponivel") or []):
            presos.append(f"requer `{req}`, que o projeto nao declara disponivel")
    return presos


def automatizaveis(estado: dict, projeto: dict) -> dict:
    """Regra 4. Separa o que da' para executar agora do que esta bloqueado — e do que NAO pode ser
    automatizado, que e' a parte que protege a regra do dono sobre revisao humana."""
    permitidas = ((projeto.get("auto") or {}).get("classes_permitidas") or CLASSES_AUTO_PADRAO)
    agora, bloqueadas, fora_de_classe = [], [], []
    for i in estado.get("itens") or []:
        classe = (i.get("auto") or "").strip()
        if not classe or _concluido(i, projeto):
            continue
        if classe not in permitidas:
            fora_de_classe.append((i["id"], classe))
            continue
        presos = impedimentos(i, estado, projeto)
        (bloqueadas if presos else agora).append((i, presos))
    return {"permitidas": permitidas, "agora": agora, "bloqueadas": bloqueadas,
            "fora_de_classe": fora_de_classe}


def revisar_adocao(projeto: dict) -> dict:
    """O projeto se pronunciou sobre cada feature do pacote?

    [pedido do dono 21/08/2026] Com resolvedor o codigo chega atualizado sozinho; o que envelhece e'
    a DECLARACAO. Feature nova nasce sem ninguem ter dito se aquele projeto a usa — e feature que
    nenhum projeto adota e' feature orfa, que e' exatamente o que o canario de capacidades deste
    framework existe para barrar."""
    adotado = projeto.get("adotado") or {}
    novas, dispensadas, ativas = [], [], []
    for nome, (versao, o_que) in sorted(FEATURES.items()):
        decl = adotado.get(nome)
        if decl is None:
            novas.append((nome, versao, o_que))
        elif decl is False or (isinstance(decl, dict) and decl.get("usa") is False):
            dispensadas.append((nome, (decl or {}).get("por_que") if isinstance(decl, dict) else ""))
        else:
            ativas.append(nome)
    return {"versao_pacote": VERSAO_PACOTE,
            "versao_no_projeto": (projeto.get("pacote") or {}).get("versao_adotada"),
            "novas": novas, "dispensadas": dispensadas, "ativas": ativas}


# ----------------------------------------------------------------------------- apresentacao


def _cab(t):
    print("\n" + "=" * 74 + f"\n {t}\n" + "=" * 74)


def mostrar_situacao(estado, projeto) -> int:
    p = politica(estado, projeto)
    sp = p["sprint"]
    _cab(f"{projeto.get('nome') or 'projeto'} — o que pode ser lancado")
    if sp.get("inicio"):
        print(f" sprint {sp.get('numero', '?')}: {sp['inicio']} a {sp['fim']}")
    else:
        print(" sem sprint declarado — a regra 1 nao esta filtrando nada.")
    print(f" PODE IR: {len(p['lancaveis'])} · RETIDO: {len(p['retidos'])}")

    motivos: dict[str, list[str]] = {}
    for ident, por_que in p["retidos"]:
        motivos.setdefault(por_que, []).append(ident)
    for por_que, ids in sorted(motivos.items()):
        print(f"\n  {len(ids)} retido(s): {por_que}")
        print(f"    {', '.join(sorted(ids)[:14])}{' ...' if len(ids) > 14 else ''}")

    ruins = prazos_ilegiveis(estado)
    pri_ruins = [(i["id"], i.get("prioridade")) for i in (estado.get("itens") or [])
                 if i.get("prioridade") is not None and _num(i.get("prioridade")) is None]
    if pri_ruins:
        print(f"\n  {len(pri_ruins)} item(ns) com PRIORIDADE que nao e' numero:")
        for ident, cru in pri_ruins[:8]:
            print(f"    x {ident:5s} prioridade={cru!r}")

    janela = sprint_ilegivel(estado, projeto)
    if janela:
        # [ACHADO DO QA RODADA 5] a versao anterior afirmava "TODAS as tarefas aparecem como
        # lancaveis" mesmo quando nao era verdade — item com prazo ILEGIVEL e' retido antes de a
        # janela ser olhada, entao dava para ver "PODE IR: 0" e "TODAS lancaveis" na mesma tela.
        # Mensagem que se contradiz destroi a confianca justamente quando o dado esta sujo, que e'
        # quando ela mais precisa ser exata.
        print(f"\n  A JANELA DO SPRINT NAO E' DATA: {'; '.join(janela)}")
        print("  Com a janela invalida a regra 1 esta DESLIGADA: ela deixa de reter por prazo.")
        if ruins:
            print(f"  ({len(ruins)} item(ns) seguem retidos por terem prazo ilegivel — isso e' outra")
            print("  coisa, e continua valendo.)")
        print("  Isto nao e' o sprint ter crescido; e' o filtro estar desligado.")

    if ruins:
        print(f"\n  {len(ruins)} item(ns) com PRAZO ILEGIVEL — nao entram em sprint nenhum ate")
        print("  serem corrigidos, e sem este aviso sumiriam calados:")
        for ident, cru in ruins[:8]:
            print(f"    x {ident:5s} prazo={cru!r} — use AAAA-MM-DD")

    if janela or ruins or pri_ruins:
        # [ACHADO DO QA RODADA 5] isto saia 0. Um script de CI que olha o codigo de saida leria
        # "tudo bem" com o filtro desligado por configuracao corrompida. Dado sujo tem de sair 1.
        print("\n  REPROVADO: ha dado que este comando nao consegue interpretar (acima). Enquanto")
        print("  nao for corrigido, o que esta na tela vale menos do que parece.")
        return 1

    feito, n_feitos, n_dentro = sprint_concluido(estado, projeto)
    print(f"\n sprint: {n_feitos}/{n_dentro} concluida(s)")
    if feito:
        print("\n  O SPRINT ACABOU. Regra 3: adiantar tarefas?")
        print("  Nao vou puxar nada sozinho — autorizacao e' ativa (ADR-111).")
        print("  Autorizando: python tools/controle_projeto.py --adiantar <N>")
        return 2
    return 0


def mostrar_adiantamento(estado, projeto, quantos) -> int:
    if quantos <= 0:
        # [ACHADO BAIXA DO QA] devolver lista vazia calado destoa do resto do modulo, que nunca cala
        print(f"  --adiantar {quantos}: nada a fazer. Informe quantas tarefas puxar (ex.: 3).")
        return 1
    r = candidatos_adiantamento(estado, projeto, quantos)
    _cab(f"adiantar {quantos} — teto de {r['teto']} em execucao por pessoa")
    if r.get("problema"):
        print(f"  ATENCAO: {r['problema']}")
    if not r["escolhidos"]:
        print(" nenhuma tarefa pode ser adiantada agora.")
    for i in r["escolhidos"]:
        print(f"  + {i['id']:5s} {i['responsavel']:20s} {(i.get('o_que') or '')[:44]}")
    if r["estourariam"]:
        print(f"\n  {len(r['estourariam'])} fora por estourar o teto:")
        for ident, quem, tem, teto in r["estourariam"][:8]:
            print(f"    x {ident:5s} {quem} ja tem {tem}, teto {teto}")
    if r["sem_executor"]:
        print(f"\n  {len(r['sem_executor'])} fora por nao terem executor — sem dono nao ha carga")
        print(f"  que calcular, e puxar assim seria fingir que a capacidade foi respeitada:")
        print(f"    {', '.join(sorted(r['sem_executor'])[:14])}")
    print(f"\n  {r['disponiveis']} tarefa(s) fora do sprint ao todo.")
    print("  ENSAIO — isto so LISTA. Quem move para o sprint e' voce, no estado do projeto.")
    return 0


def mostrar_auto(estado, projeto) -> int:
    r = automatizaveis(estado, projeto)
    _cab("regra 4 — automatizavel sem impedimento")
    print(f" classes permitidas: {', '.join(r['permitidas'])}")
    print(f" EXECUTAVEL AGORA: {len(r['agora'])} · bloqueada: {len(r['bloqueadas'])}")
    for i, _ in r["agora"]:
        print(f"  > {i['id']:5s} [{i.get('auto')}] {(i.get('o_que') or '')[:50]}")
    for i, presos in r["bloqueadas"]:
        print(f"  . {i['id']:5s} bloqueada: {presos[0]}")
    if r["fora_de_classe"]:
        print(f"\n  {len(r['fora_de_classe'])} declarada(s) fora das classes permitidas — decisao,")
        print("  numero, valor ou alteracao de sistema de terceiro exigem revisao humana:")
        for ident, classe in r["fora_de_classe"][:8]:
            print(f"    x {ident:5s} classe `{classe}`")
    print("\n  Este comando NAO executa. Ele identifica e mede impedimento; quem executa e' o")
    print("  agente, e deixa prova.")
    return 0


def mostrar_adocao(projeto) -> int:
    r = revisar_adocao(projeto)
    _cab(f"revisao de adocao — pacote {r['versao_pacote']}")
    print(f" o projeto declara ter adotado: {r['versao_no_projeto'] or 'NADA'}")
    print(f" ativas: {len(r['ativas'])} · dispensadas: {len(r['dispensadas'])}")
    for nome, por_que in r["dispensadas"]:
        print(f"    - {nome}: dispensada ({por_que or 'sem motivo declarado'})")
    if r["novas"]:
        print(f"\n  {len(r['novas'])} feature(s) do pacote sobre as quais este projeto NAO se")
        print("  pronunciou. Feature que nenhum projeto adota e' feature orfa:")
        for nome, versao, o_que in r["novas"]:
            print(f"    ? {nome} (v{versao}) — {o_que}")
        print(f"\n  Declare em {DECLARACAO}, chave `adotado`:")
        print('    "adotado": {"' + r["novas"][0][0] + '": true}          # usa')
        print('    "adotado": {"' + r["novas"][0][0] + '": {"usa": false, "por_que": "..."}}')
        return 1
    print("\n  PASS — o projeto se pronunciou sobre todas as features do pacote.")
    return 0


def iniciar(caminho: str) -> int:
    """Cria a declaracao minima. Nao inventa dado: so o esqueleto e o que perguntar."""
    # [ACHADO ALTA DO QA RODADA 10] isto era `Path(caminho).resolve()` cru, e o `mkdir` abaixo
    # tambem. Caminho com caractere ilegal derrubava o comando de ENTRADA de um projeto novo com
    # `OSError: [WinError 123]` — o primeiro contato de qualquer projeto com o pacote, fora da
    # fronteira que o resto do pacote existe para impor. Terceiro ponto a escapar da mesma promessa.
    raiz = _caminho(caminho, "o caminho passado em --iniciar")
    alvo = raiz / DECLARACAO
    if alvo.exists():
        print(f"ja existe: {alvo}")
        return 1
    modelo = {
        "_leia": "Declaracao do projeto para o pacote controle_projeto do metacognition-framework. "
                 "O CODIGO vive no nucleo e e' achado por resolvedor; aqui fica so o que e' DESTE "
                 "projeto.",
        "nome": raiz.name,
        "pacote": {"versao_adotada": VERSAO_PACOTE, "revisado_em": dt.date.today().isoformat()},
        "estado": "estado.json",
        "adotado": {nome: True for nome in FEATURES},
        "agentes": [],
        "agente_responde_por": {},
        "capacidade": {"em_execucao_por_pessoa": 3},
        "auto": {"classes_permitidas": CLASSES_AUTO_PADRAO},
        "disponivel": [],
        "adaptadores": {},
    }
    escrever_texto(alvo, json.dumps(modelo, ensure_ascii=False, indent=2) + "\n",
                   "a declaracao do projeto novo")
    print(f"criado: {alvo}")
    print("  Preencha `estado`, `agentes` e `capacidade` antes de usar.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--projeto", help="raiz do projeto (senao: env, senao sobe da pasta corrente)")
    ap.add_argument("--situacao", action="store_true", help="o que pode ir e o que esta retido")
    ap.add_argument("--adiantar", type=int, metavar="N", help="regra 3 — exige autorizacao ativa")
    ap.add_argument("--auto", action="store_true", help="regra 4 — automatizavel sem impedimento")
    ap.add_argument("--revisar-adocao", action="store_true", help="o projeto adotou as features?")
    ap.add_argument("--iniciar", metavar="CAMINHO", help="cria a declaracao minima do projeto")
    a = ap.parse_args(argv)

    try:
        if a.iniciar:
            return iniciar(a.iniciar)
    except ProjetoInvalido as e:
        # [ACHADO ALTA DO QA RODADA 10] a chamada ficava FORA do try, entao nem se `iniciar`
        # levantasse ProjetoInvalido o usuario veria mensagem.
        print(f"NAO CONSEGUI INICIAR: {e}")
        return 1
    try:
        raiz, origem = raiz_projeto(a.projeto)
        projeto, estado = carregar(raiz)
    except ProjetoInvalido as e:
        print(f"PROJETO NAO RESOLVIDO: {e}")
        return 1
    print(f"projeto: {raiz}  ({origem})")

    if a.revisar_adocao:
        return mostrar_adocao(projeto)
    if a.adiantar is not None:
        return mostrar_adiantamento(estado, projeto, a.adiantar)
    if a.auto:
        return mostrar_auto(estado, projeto)
    return mostrar_situacao(estado, projeto)


if __name__ == "__main__":
    raise SystemExit(main())
