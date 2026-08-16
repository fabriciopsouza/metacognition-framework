#!/usr/bin/env python3
"""conformance — o fluxo executado bate com o desenhado? (ADR-097)

O QUE RESOLVE. "O processo foi seguido?" era julgamento: alguém lia o histórico e opinava. Este
verificador compara o **executado** (o ledger de junções, `_meta/qa/junctions/*.jsonl`) contra o
**desenhado** (`_meta/conformance/modelo-juncoes.json`) e devolve número, não opinião: onde
divergiu, em qual junção, por qual regra.

É *token-replay* mínimo, escrito à mão. O ADR-097 rejeitou adotar PM4Py por default — dependência
externa não paga a régua §0 para o que aqui é um percurso linear de oito atividades.

O QUE ELE MEDE
  · **fitness** = passos do trace que o modelo aceita ÷ total de passos. 1.0 = trace conforme.
  · **violações**, cada uma com a regra que ela quebra: junção pulada, regressão sem rewind
    declarado, rewind mal declarado, status fora do conjunto fechado, registro sem ponteiro
    de prova, registro sem `resource`.

  A regra `prova-verificavel` confere que o ponteiro **resolve**, não que ele seja
  relevante: qualquer arquivo do repositório serve para qualquer junção, e um digest
  inventado passa. Está declarado assim no validador — o nome da regra promete mais do
  que ela entrega, e o texto é o lugar de dizer isso.

O TETO, declarado no próprio ADR e repetido aqui porque importa: **o agente escreve o ledger que
este verificador lê.** Isso é auditabilidade, não constrangimento externo. Um terceiro pode
re-rodar e chegar ao mesmo número — o que é estritamente melhor que prosa —, mas ninguém de fora
impede o agente de registrar o que quiser. Hard de verdade exigiria árbitro neutro escrevendo o
log, e isso está fora do escopo.

O RATCHET. As duas regras de nível `ratchet` (prova verificável, resource declarado) apenas
**avisam** nos primeiros 5 blocos medidos e passam a reprovar depois. Motivo, do ADR: traces de
agente são ruidosos e o limiar precisa de calibração empírica — gate calibrado no chute é gate
desligado na primeira semana. O estado vive em `_meta/conformance/ratchet.json`.

Uso:
    python tools/conformance.py                     # relatório de todos os blocos
    python tools/conformance.py --bloco <id>        # um bloco
    python tools/conformance.py --gate --bloco <id> # modo release: exit != 0 se violar
    python tools/conformance.py --json

Códigos de saída: 0 conforme (ou só avisos) · 1 violação bloqueante · 2 modelo/ledger ausente.
"""
import argparse
import json
import os
import sys
from pathlib import Path

RAIZ_PADRAO = Path(__file__).resolve().parent.parent
MODELO = "_meta/conformance/modelo-juncoes.json"
LEDGER = "_meta/qa/junctions"
RATCHET = "_meta/conformance/ratchet.json"
# Conjunto FECHADO. Status fora daqui e' violacao, nao "outro tipo de sucesso".
STATUS_VALIDOS = {"PASS", "REPROVADO_REWIND"}

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass


def carregar_modelo(raiz):
    p = Path(raiz) / MODELO
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def ordem_de(modelo):
    return {a["id"]: a["ordem"] for a in modelo.get("atividades", [])}


def ler_trace(caminho):
    """(passos, erro). Uma linha ilegível NÃO é ignorada: ledger corrompido invalida o trace."""
    passos = []
    try:
        for n, linha in enumerate(Path(caminho).read_text(encoding="utf-8").splitlines(), 1):
            linha = linha.strip()
            if not linha:
                continue
            try:
                passos.append(json.loads(linha))
            except json.JSONDecodeError:
                return [], f"linha {n} nao e' JSON — ledger corrompido, nao interpretavel"
    except OSError as e:
        return [], f"nao consegui ler: {e}"
    return passos, None


def avaliar_trace(passos, modelo, ratchet_ativo):
    """(fitness, violacoes, avisos) de UM bloco. Puro: e' o que o canário exercita."""
    ordem = ordem_de(modelo)
    violacoes, avisos = [], []
    aceitos, total = 0, 0
    vistos_pass = set()
    ultima_ordem = -1

    for i, p in enumerate(passos):
        total += 1
        j = str(p.get("junction", "")).upper().strip()
        status = str(p.get("status", "")).upper().strip() or "PASS"
        rotulo = f"passo {i + 1} ({j or '?'})"

        if j not in ordem:
            violacoes.append((rotulo, "modelo", f"junção '{j}' não existe no modelo"))
            continue
        o = ordem[j]

        # `status` fechado. A 1a versao so' comparava com PASS e REPROVADO_REWIND: qualquer outra
        # string escapava das duas comparacoes e o passo era contado como aceito, sem violacao.
        # Um `status: "TALVEZ"` passava por conforme. Achado MEDIO do qa-critic (Sonnet, 2026-08-16).
        if status not in STATUS_VALIDOS:
            violacoes.append((rotulo, "status-invalido",
                              f"status '{status}' não existe — válidos: {', '.join(sorted(STATUS_VALIDOS))}"))

        # REWIND SO' VALE DECLARADO E REGREDINDO. Achado CRITICO do mesmo critico: a 1a versao
        # aceitava a flag booleana `rewind: true` sozinha e, com ela, desligava AS DUAS checagens
        # em QUALQUER direcao. Um bloco com um unico registro — a juncao final, com a flag
        # pendurada — devolvia fitness 1.0 e zero violacoes, isto e', "processo completo e
        # conforme" sem ter passado por nenhuma etapa. Esvaziava o ADR inteiro.
        rewind_declarado = status == "REPROVADO_REWIND"
        regressao = o < ultima_ordem

        if bool(p.get("rewind")) and not rewind_declarado:
            violacoes.append((rotulo, "rewind-mal-declarado",
                              "flag `rewind` sem `status: REPROVADO_REWIND` — a flag sozinha não "
                              "autoriza nada"))
        if rewind_declarado and not regressao:
            violacoes.append((rotulo, "rewind-mal-declarado",
                              f"declarado rewind mas a ordem NÃO regride ({ultima_ordem} -> {o}): "
                              f"salto para frente mascarado de rewind"))
        elif regressao and not rewind_declarado:
            violacoes.append((rotulo, "forward-only",
                              f"regressão de ordem {ultima_ordem} para {o} sem rewind declarado"))
        else:
            faltando = ([] if regressao else
                        [k for k, v in ordem.items() if v < o and k not in vistos_pass])
            if faltando:
                violacoes.append((rotulo, "sem-salto",
                                  f"registrada sem PASS anterior de: {', '.join(sorted(faltando, key=lambda x: ordem[x]))}"))
            else:
                aceitos += 1
        rewind = rewind_declarado and regressao

        if not str(p.get("prova") or "").strip():
            (violacoes if ratchet_ativo else avisos).append(
                (rotulo, "prova-verificavel", "sem `prova` — registro afirma e não comprova"))
        if str(p.get("resource") or "").strip() in ("", "nao-declarado"):
            (violacoes if ratchet_ativo else avisos).append(
                (rotulo, "resource-declarado", "sem `resource` — não diz quem produziu o PASS"))

        if status == "PASS":
            vistos_pass.add(j)
        ultima_ordem = max(ultima_ordem, o) if not rewind else o

    if total == 0:
        # Vacuo lido como conformidade era o achado BAIXO do qa-critic: um bloco cujo ledger
        # existe e nunca recebeu registro nenhum voltava fitness 1.0, indistinguivel de um fluxo
        # inteiro bem executado. Ausencia de prova nao e' prova de conformidade.
        return 0.0, [("trace", "vacuo", "ledger existe e nao tem registro nenhum — "
                                        "ausencia de dado nao e' conformidade")], avisos
    return round(aceitos / total, 4), violacoes, avisos


def blocos(raiz):
    d = Path(raiz) / LEDGER
    return sorted(d.glob("*.jsonl")) if d.is_dir() else []


def estado_ratchet(raiz):
    p = Path(raiz) / RATCHET
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"blocos_medidos": []}


def registrar_medicao(raiz, bloco):
    """Conta o bloco na janela de calibração. Idempotente: o mesmo bloco não conta duas vezes."""
    p = Path(raiz) / RATCHET
    est = estado_ratchet(raiz)
    medidos = list(est.get("blocos_medidos", []))
    if bloco not in medidos:
        medidos.append(bloco)
    est["blocos_medidos"] = medidos
    est["_doc"] = ("ADR-097: janela de calibracao. As regras de nivel `ratchet` avisam ate a janela "
                   "fechar e reprovam depois. Apagar este arquivo REABRE a janela — e' registro, "
                   "nao configuracao.")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(est, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(medidos)


def ratchet_fechado(raiz, modelo):
    janela = int((modelo.get("ratchet") or {}).get("janela_warn", 5))
    return len(estado_ratchet(raiz).get("blocos_medidos", [])) >= janela


def main(argv=None):
    ap = argparse.ArgumentParser(description="Executado x desenhado no fluxo de juncoes (ADR-097).")
    ap.add_argument("--repo", default=str(RAIZ_PADRAO))
    ap.add_argument("--bloco", help="avalia so este bloco (nome do arquivo sem .jsonl)")
    ap.add_argument("--gate", action="store_true", help="modo release: exit != 0 se violar")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    raiz = Path(a.repo)

    modelo = carregar_modelo(raiz)
    if modelo is None:
        print(f"[conformance] modelo ausente ou invalido em {MODELO} — sem 'desenhado', "
              f"nao ha' o que comparar.")
        return 2

    arquivos = blocos(raiz)
    if a.bloco:
        arquivos = [f for f in arquivos if f.stem == a.bloco]
        if not arquivos:
            print(f"[conformance] bloco '{a.bloco}' sem ledger de juncoes.")
            return 2 if a.gate else 0

    fechado = ratchet_fechado(raiz, modelo)
    relatorio, bloqueia = [], False

    for arq in arquivos:
        passos, erro = ler_trace(arq)
        if erro:
            relatorio.append({"bloco": arq.stem, "fitness": 0.0,
                              "violacoes": [["ledger", "integridade", erro]], "avisos": []})
            bloqueia = True
            continue
        fit, viol, avi = avaliar_trace(passos, modelo, fechado)
        relatorio.append({"bloco": arq.stem, "passos": len(passos), "fitness": fit,
                          "violacoes": [list(v) for v in viol], "avisos": [list(x) for x in avi]})
        if viol:
            bloqueia = True
        if a.gate:
            registrar_medicao(raiz, arq.stem)

    if a.json:
        print(json.dumps({"ratchet_fechado": fechado, "blocos": relatorio},
                         ensure_ascii=False, indent=2))
    else:
        janela = int((modelo.get("ratchet") or {}).get("janela_warn", 5))
        medidos = len(estado_ratchet(raiz).get("blocos_medidos", []))
        print(f"[conformance] modelo v{modelo.get('versao')} · {len(relatorio)} bloco(s) · "
              f"ratchet {'FECHADO (regras de calibracao reprovam)' if fechado else f'aberto ({medidos}/{janela} blocos medidos — regras de calibracao so avisam)'}")
        for r in relatorio:
            print(f"\n  {r['bloco']} — fitness {r['fitness']}")
            for rotulo, regra, msg in r["violacoes"]:
                print(f"    VIOLA  [{regra}] {rotulo}: {msg}")
            for rotulo, regra, msg in r["avisos"]:
                print(f"    avisa  [{regra}] {rotulo}: {msg}")
            if not r["violacoes"] and not r["avisos"]:
                print("    conforme")
        if not relatorio:
            print("  (nenhum bloco com ledger de juncoes)")

    return 1 if (a.gate and bloqueia) else 0


if __name__ == "__main__":
    sys.exit(main())
