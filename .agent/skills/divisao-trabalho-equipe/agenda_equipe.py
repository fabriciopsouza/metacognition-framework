#!/usr/bin/env python3
"""agenda_equipe.py — distribui as tarefas do estado.json entre os executantes, pela capacidade de cada um.

Pedido do dono (22/10/2026): usar a mão de obra de 3 aprendizes (2 de manhã, 1 à tarde; 4 h por dia, 4 dias por
semana) e "dividir trabalho paralelo, ou sequencial entre pessoas diferentes, de forma clara, objetiva, direta".

Regras do cálculo:
- Tarefa com `horas` e `executante` igual a um papel de `equipe` é agendada: começa quando todas as dependências
  terminaram e o executante está livre; ocupa as horas do turno dele, dia útil a dia útil, nos dias de trabalho dele.
- Executante "Aprendiz (qualquer)" vai para o aprendiz que termina primeiro.
- Tarefa de quem não está em `equipe` (ex.: dono, outras áreas) não é agendada: vale o `prazo` informado.
- Tarefa concluída mantém a data de conclusão.
- Feriados em `equipe_feriados` não contam.
Saída: dicionário id -> {"inicio", "fim", "executante", "blocos": [(data, horas)], "agendada"}. Não grava nada sozinho:
o projeto usa o resultado para gerar planilhas, agenda e painéis (skill divisao-trabalho-equipe).
"""
from __future__ import annotations

import datetime as dt

QUALQUER = "Aprendiz (qualquer)"


def _dias_de_trabalho(pessoa: dict, de: dt.date, feriados: set[dt.date]):
    d = de
    while True:
        if d.weekday() in pessoa["dias_semana"] and d not in feriados:
            yield d
        d += dt.timedelta(days=1)


def _encaixar(pessoa: dict, livre: dict, inicio_min: dt.date, horas: float, feriados: set[dt.date]):
    """Ocupa `horas` a partir de inicio_min; `livre` guarda horas já usadas por dia. Devolve blocos."""
    blocos, resta = [], horas
    for d in _dias_de_trabalho(pessoa, inicio_min, feriados):
        usado = livre.get(d, 0.0)
        cabe = pessoa["horas_dia"] - usado
        if cabe <= 0:
            continue
        h = min(cabe, resta)
        livre[d] = usado + h
        blocos.append((d, h))
        resta -= h
        if resta <= 1e-9:
            return blocos


def _conferir(est: dict) -> None:
    """Recusa entrada que travaria ou quebraria o cálculo (a validação completa fica no projeto)."""
    for p in est.get("equipe", []):
        if not p.get("dias_semana") or not p.get("horas_dia") or p["horas_dia"] <= 0:
            raise ValueError(f"{p.get('papel')}: dias_semana vazio ou horas_dia inválido")
    for i in est["itens"]:
        h = i.get("horas")
        if h is not None and (isinstance(h, bool) or not isinstance(h, (int, float)) or h <= 0):
            raise ValueError(f"{i['id']}: horas deve ser número positivo")
        if (i.get("executante") == QUALQUER and h
                and not any(p["papel"].startswith("Aprendiz") for p in est.get("equipe", []))):
            raise ValueError(f"{i['id']}: '{QUALQUER}' exige papéis começando por 'Aprendiz'")


def planejar(est: dict, inicio_projeto: dt.date) -> dict:
    _conferir(est)
    equipe = {p["papel"]: p for p in est.get("equipe", [])}
    feriados = {dt.date.fromisoformat(f) for f in est.get("equipe_feriados", [])}
    itens = {i["id"]: i for i in est["itens"]}
    ocupacao = {papel: {} for papel in equipe}
    fim_livre = {papel: inicio_projeto for papel in equipe}
    resultado: dict[str, dict] = {}

    def resolver(iid: str, pilha=()):
        if iid in resultado:
            return resultado[iid]
        if iid in pilha:
            raise ValueError(f"dependência circular em {iid}")
        i = itens[iid]
        deps = [resolver(d, pilha + (iid,)) for d in i.get("depende_de") or []]
        pronto = max([inicio_projeto] + [r["fim"] + dt.timedelta(days=1) for r in deps])
        quem = i.get("executante") or i.get("responsavel")
        if i["coluna"] == "concluido":
            fim = dt.date.fromisoformat(i["prazo"])
            r = {"inicio": fim, "fim": fim, "executante": quem, "blocos": [], "agendada": False}
        elif i.get("apos_dependencias") and deps:
            fim = pronto
            while fim.weekday() >= 5 or fim in feriados:
                fim += dt.timedelta(days=1)
            r = {"inicio": fim, "fim": fim, "executante": quem, "blocos": [], "agendada": True}
        elif not i.get("horas") or (quem not in equipe and quem != QUALQUER):
            fim = dt.date.fromisoformat(i["prazo"])
            r = {"inicio": fim, "fim": fim, "executante": quem, "blocos": [], "agendada": False}
        else:
            candidatos = [p for p in equipe if p.startswith("Aprendiz")] if quem == QUALQUER else [quem]
            melhor = None
            for papel in candidatos:
                copia = dict(ocupacao[papel])
                horas = float(i["horas"]) * (1 + float(est.get("equipe_folga", 0)))
                blocos = _encaixar(equipe[papel], copia, pronto, horas, feriados)
                if melhor is None or blocos[-1][0] < melhor[1][-1][0]:
                    melhor = (papel, blocos, copia)
            papel, blocos, copia = melhor
            ocupacao[papel] = copia
            fim_livre[papel] = max(fim_livre[papel], blocos[-1][0])
            r = {"inicio": blocos[0][0], "fim": blocos[-1][0], "executante": papel, "blocos": blocos, "agendada": True}
        resultado[iid] = r
        return r

    for iid in sorted(itens, key=lambda k: (itens[k]["fase"], k)):
        resolver(iid)
    return resultado


def capacidade_semana(est: dict) -> float:
    return sum(p["horas_dia"] * len(p["dias_semana"]) for p in est.get("equipe", []))
