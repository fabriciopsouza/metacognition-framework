#!/usr/bin/env python3
"""Canário do conformance (ADR-097) — o executado bate com o desenhado?

CONTEXTO. O ADR-097 estava em `Proposto` desde 23/06, nascido de uma frase do dono: *"onde sou
advisory dá pra ficar hard?"*. Ele lista três pendências, e a terceira é explícita sobre o que
separa intenção de mecanismo: *"implementar tools/conformance.py + tools/test_conformance.py e
rodar verde na suíte local — **sem isso há intenção de HARD, não HARD**"*.

O QUE ESTE CANÁRIO PROTEGE. Que o verificador **reprove topologia violada**. Um verificador que
aprova qualquer trace é pior que nenhum: produz um número de conformidade que ninguém pode
contestar e todo mundo acredita.

O TETO, que este canário NÃO resolve e não finge resolver: o agente escreve o ledger que o
verificador lê. Isso é auditabilidade — terceiro re-roda e chega ao mesmo número —, não
constrangimento externo. Está declarado no ADR e repetido aqui de propósito.

Uso: python tools/test_conformance.py   (exit 0 PASS; 1 se o verificador aprovar o que viola)
"""
import json
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import conformance as cf  # noqa: E402

resultados = []


def caso(nome, ok, detalhe=""):
    resultados.append((nome, ok))
    print(f"  [{'PASS' if ok else 'FALHA'}] {nome}")
    if detalhe and not ok:
        print(f"          {detalhe}")


MODELO_REAL = json.loads((TOOLS.parent / "_meta" / "conformance"
                          / "modelo-juncoes.json").read_text(encoding="utf-8"))


def passo(j, **troca):
    # Prova DISTINTA por juncao de proposito: a 1a versao usava "CLAUDE.md" para as oito, e o
    # qa-critic apontou que o proprio canario demonstrava o buraco (qualquer arquivo serve para
    # qualquer juncao). O verificador nao confere relevancia — mas o canario nao vai ilustrar isso.
    p = {"junction": j, "bloco": "b", "status": "PASS", "resource": "claude-opus-5",
         "prova": f"sha256:{ord(j[-1]):02x}" + "0" * 62,
         "evidencia": "criterio", "data": "2026-08-16T00:00:00Z"}
    p.update(troca)
    return p


def regras(viol):
    return {r for _, r, _ in viol}


def main():
    print("conformance: reprova topologia violada e aceita o fluxo inteiro")

    completo = [passo(j) for j in ("J0", "J1", "J2", "J3", "J4", "J5", "PC", "J6")]

    fit, viol, avi = cf.avaliar_trace(completo, MODELO_REAL, True)
    caso("fluxo completo e' conforme, fitness 1.0", fit == 1.0 and not viol,
         f"fitness={fit} violacoes={viol}")

    # ACHADO CRITICO do qa-critic: a flag `rewind` sozinha desligava tudo, em qualquer direcao.
    fit, viol, _ = cf.avaliar_trace([passo("J6", rewind=True)], MODELO_REAL, True)
    caso("so' a juncao FINAL com flag `rewind` NAO passa por processo completo",
         viol and fit < 1.0,
         f"fitness={fit} violacoes={viol} — devolvia 1.0 e zero violacoes, o pior defeito possivel")
    caso("flag `rewind` sem status REPROVADO_REWIND e' VIOLACAO",
         "rewind-mal-declarado" in regras(viol))

    fit, viol, _ = cf.avaliar_trace([passo("J0"), passo("J6", status="REPROVADO_REWIND")],
                                    MODELO_REAL, True)
    caso("rewind que NAO regride e' salto mascarado, e VIOLA",
         "rewind-mal-declarado" in regras(viol), f"violacoes={viol}")

    _, viol, _ = cf.avaliar_trace([passo("J0"), passo("J1", status="TALVEZ")], MODELO_REAL, True)
    caso("status fora do conjunto fechado e' VIOLACAO",
         "status-invalido" in regras(viol), f"violacoes={viol}")

    fit, viol, _ = cf.avaliar_trace([], MODELO_REAL, True)
    caso("trace VAZIO nao e' conformidade (vacuo != conforme)",
         fit == 0.0 and "vacuo" in regras(viol), f"fitness={fit} violacoes={viol}")

    # A violacao central: junção posterior sem a anterior.
    fit, viol, _ = cf.avaliar_trace([passo("J0"), passo("J4")], MODELO_REAL, True)
    caso("junção pulada e' VIOLACAO (sem-salto)", "sem-salto" in regras(viol),
         f"violacoes={viol}")
    caso("e o fitness cai abaixo de 1.0 quando ha' salto", fit < 1.0, f"fitness={fit}")

    # Regressao: voltar sem declarar rewind apaga o fato de que algo foi refeito.
    fit, viol, _ = cf.avaliar_trace([passo("J0"), passo("J1"), passo("J2"), passo("J1")],
                                    MODELO_REAL, True)
    caso("regressao SEM rewind e' VIOLACAO (forward-only)",
         "forward-only" in regras(viol), f"violacoes={viol}")

    # ...e com rewind declarado e' legitimo: e' o mecanismo do process-critic.
    fit, viol, _ = cf.avaliar_trace(
        [passo("J0"), passo("J1"), passo("J2"),
         passo("J1", status="REPROVADO_REWIND", rewind=True), passo("J2")], MODELO_REAL, True)
    caso("regressao COM rewind declarado e' legitima", "forward-only" not in regras(viol),
         f"violacoes={viol} — rewind do process-critic e' parte do desenho, nao desvio")

    # Junção que não existe no modelo.
    _, viol, _ = cf.avaliar_trace([passo("J9")], MODELO_REAL, True)
    caso("junção fora do modelo e' VIOLACAO", "modelo" in regras(viol))

    # O RATCHET: as duas regras de calibracao avisam antes, reprovam depois.
    sem_prova = [passo(j, prova="", resource="") for j in ("J0", "J1")]
    _, viol_aberto, avi_aberto = cf.avaliar_trace(sem_prova, MODELO_REAL, False)
    _, viol_fechado, _ = cf.avaliar_trace(sem_prova, MODELO_REAL, True)
    caso("com ratchet ABERTO, falta de prova/resource so' AVISA",
         not viol_aberto and len(avi_aberto) == 4, f"viol={viol_aberto} avisos={len(avi_aberto)}")
    caso("com ratchet FECHADO, a mesma falta VIOLA",
         {"prova-verificavel", "resource-declarado"} <= regras(viol_fechado),
         f"violacoes={viol_fechado}")

    # Integracao: ledger corrompido nao e' ignorado.
    with tempfile.TemporaryDirectory(prefix="cf-") as t:
        r = Path(t)
        (r / "_meta" / "conformance").mkdir(parents=True)
        (r / "_meta" / "qa" / "junctions").mkdir(parents=True)
        (r / "_meta" / "conformance" / "modelo-juncoes.json").write_text(
            json.dumps(MODELO_REAL, ensure_ascii=False), encoding="utf-8")
        led = r / "_meta" / "qa" / "junctions" / "bloco.jsonl"

        led.write_text("\n".join(json.dumps(p, ensure_ascii=False) for p in completo) + "\n",
                       encoding="utf-8")
        caso("--gate aprova bloco conforme", cf.main(["--repo", str(r), "--json",
                                                      "--gate", "--bloco", "bloco"]) == 0)

        led.write_text(json.dumps(passo("PC"), ensure_ascii=False) + "\n", encoding="utf-8")
        caso("--gate REPROVA bloco que pula tudo e vai direto ao fim",
             cf.main(["--repo", str(r), "--json", "--gate", "--bloco", "bloco"]) == 1)

        led.write_text("{ isto nao e json\n", encoding="utf-8")
        caso("ledger corrompido NAO e' ignorado — reprova",
             cf.main(["--repo", str(r), "--json", "--gate", "--bloco", "bloco"]) == 1,
             "pular linha ilegivel zeraria a topologia em silencio")

        (r / "_meta" / "conformance" / "modelo-juncoes.json").unlink()
        caso("sem modelo, recusa medir (exit 2) em vez de aprovar",
             cf.main(["--repo", str(r), "--json"]) == 2,
             "sem 'desenhado' nao existe conformidade — aprovar seria inventar")

    # O ratchet conta blocos e nao conta o mesmo duas vezes.
    with tempfile.TemporaryDirectory(prefix="cf-ratchet-") as t:
        r = Path(t)
        (r / "_meta" / "conformance").mkdir(parents=True)
        caso("ratchet conta bloco novo", cf.registrar_medicao(r, "a") == 1)
        caso("ratchet nao conta o mesmo bloco duas vezes", cf.registrar_medicao(r, "a") == 1)
        caso("ratchet conta o segundo bloco", cf.registrar_medicao(r, "b") == 2)

    print("-" * 50)
    ruins = [n for n, ok in resultados if not ok]
    if ruins:
        print(f"RESULTADO: FAIL ({len(ruins)}) — {', '.join(ruins)}")
        return 1
    print(f"RESULTADO: PASS ({len(resultados)} verificacoes: topologia violada nao passa por "
          f"conforme)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
