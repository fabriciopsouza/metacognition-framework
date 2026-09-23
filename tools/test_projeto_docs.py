#!/usr/bin/env python3
"""Canário do projeto_docs — o quadro de gestão sai do dado, não da digitação.

CONTEXTO. O dono pediu backlog transponível para Trello/Planner, cronograma, e status report
obrigatório. A armadilha conhecida é documento de gestão digitado à mão: envelhece na primeira
semana, vira ficção, e todo mundo para de olhar. Por isso o gerador **deriva** das fontes que já
são mantidas por obrigação.

Na primeira execução real ele já provou o ponto: apontou um item listado como pendente que havia
sido **entregue na release anterior** e ninguém tinha riscado.

O QUE ESTE CANÁRIO PROTEGE. Que o quadro reflita as fontes — nos dois sentidos. Item aberto que
some do backlog é pior que backlog nenhum: dá a sensação de que acabou.

Uso: python tools/test_projeto_docs.py   (exit 0 PASS; 1 se o quadro divergir das fontes)
"""
import csv
import io
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import projeto_docs as pd  # noqa: E402

resultados = []


def caso(nome, ok, detalhe=""):
    resultados.append((nome, ok))
    print(f"  [{'PASS' if ok else 'FALHA'}] {nome}")
    if detalhe and not ok:
        print(f"          {detalhe}")


def _repo(raiz, *, abertos=(), adr_proposto=False, sem_prova=0):
    raiz = Path(raiz)
    (raiz / "docs" / "adr").mkdir(parents=True)
    # A nota `> ` vem DEPOIS do primeiro item, de propósito. Na 1ª versão ela vinha antes, onde o
    # parser a descartava por OUTRO motivo (nenhum item acumulando) — então a checagem passava por
    # vácuo: sabotar o skip da nota não deixava o canário vermelho. Achado ALTO do qa-critic
    # (Fable, 2026-08-16). No `history.md` real as notas vêm depois do primeiro item, como aqui.
    linhas = [f"- **{a}** detalhe do item." for a in abertos]
    corpo = "\n".join(linhas[:1] + ["> nota de higiene que NAO e' item"] + linhas[1:])
    (raiz / "history.md").write_text(
        "# history\n\n## 2026-08-16 — release\ntexto\n\n## Em aberto\n\n"
        + corpo + "\n\n## Aprendizado\n- nota\n", encoding="utf-8")
    (raiz / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [1.9.0] — 2026-08-16 — titulo da release\ntexto\n", encoding="utf-8")
    (raiz / "docs" / "adr" / "001-decidido.md").write_text(
        "# ADR-001 - Ja decidido\n- Status: Aceito\n", encoding="utf-8")
    if adr_proposto:
        (raiz / "docs" / "adr" / "002-esperando.md").write_text(
            "# ADR-002 - Esperando o dono\n- Status: Proposto\n", encoding="utf-8")
    caps = [{"id": f"c{i}", "enforcement": "fail-closed"} for i in range(sem_prova)]
    (raiz / "capabilities.json").write_text(json.dumps({"capabilities": caps}), encoding="utf-8")
    return raiz


def linhas_csv(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8-sig")))


def main():
    print("projeto_docs: o quadro sai das fontes, e some quando a fonte some")

    with tempfile.TemporaryDirectory(prefix="pd-") as t:
        r = _repo(t, abertos=("Divida A", "Divida B"), adr_proposto=True, sem_prova=3)
        itens = pd.backlog(r)
        titulos = " | ".join(i["titulo"] for i in itens)

        caso("cada item de `## Em aberto` vira item de backlog",
             "Divida A" in titulos and "Divida B" in titulos, titulos)
        caso("nota de higiene da secao NAO vira item",
             "higiene" not in titulos.lower(), titulos)
        caso("e a nota tambem nao gruda no DETALHE do item anterior",
             all("higiene" not in i["detalhe"].lower() for i in itens),
             "a nota vem DEPOIS do 1o item; sem o skip ela seria colada nele")
        caso("ADR em Proposto entra como decisao DO DONO",
             any(i["tipo"] == "decisão do dono" for i in itens),
             f"tipos: {[i['tipo'] for i in itens]}")
        caso("ADR ja Aceito NAO entra", "Ja decidido" not in titulos)
        caso("decisao do dono vem com prioridade maior que divida",
             min(i["prioridade"] for i in itens if i["tipo"] == "decisão do dono")
             < min(i["prioridade"] for i in itens if i["tipo"] == "dívida"))
        caso("passivo entra AGREGADO, nao uma linha por capacidade",
             sum(1 for i in itens if "Passivo de prova" in i["titulo"]) == 1
             and "3 capacidades" in titulos, titulos)

        pd.gerar(r)
        b = linhas_csv(r / pd.SAIDA / "backlog.csv")
        col = set(b[0].keys()) if b else set()
        caso("backlog.csv traz as colunas do Trello E do Planner",
             {"Card name", "Description", "Task Name", "Notes"} <= col, f"colunas: {sorted(col)}")
        caso("toda linha do backlog tem titulo e descricao preenchidos",
             all(l["Card name"].strip() and l["Description"].strip() for l in b))

        crono = linhas_csv(r / pd.SAIDA / "cronograma.csv")
        caso("cronograma diz QUEM responde por cada item",
             all(l["responsavel"] in ("dono", "squad") for l in crono),
             f"responsaveis: {[l['responsavel'] for l in crono]}")
        caso("cronograma vem ordenado por prioridade",
             [l["prioridade"] for l in crono] == sorted(l["prioridade"] for l in crono))

        rep = (r / pd.SAIDA / "STATUS-REPORT.md").read_text(encoding="utf-8")
        for secao in ("Onde chegamos", "Estado agora", "O que falta", "Ação"):
            caso(f"o status report tem a secao '{secao}'", secao in rep)
        caso("o status report cita a release do CHANGELOG", "1.9.0" in rep)
        caso("o status report separa o que depende do DONO",
             "dependem de decisão do dono" in rep, "sem isso o dono nao sabe o que travou nele")

        # O sentido inverso, que e' o que faz backlog virar ficcao: fechar item e nao riscar.
        antes = len(pd.backlog(r))
        _repo_novo = Path(t) / "history.md"
        _repo_novo.write_text(_repo_novo.read_text(encoding="utf-8")
                              .replace("- **Divida A** detalhe do item.\n", ""), encoding="utf-8")
        depois = len(pd.backlog(r))
        caso("item removido da fonte SOME do backlog", depois == antes - 1,
             f"antes={antes} depois={depois} — quadro que so' cresce e' quadro que ninguem le")

        caso("--verificar acusa quando o backlog mudou e o arquivo nao",
             pd.main(["--repo", str(r), "--verificar"]) == 1)
        pd.gerar(r)
        caso("--verificar aprova depois de regerar",
             pd.main(["--repo", str(r), "--verificar"]) == 0)

    with tempfile.TemporaryDirectory(prefix="pd-vazio-") as t:
        r = _repo(t)
        caso("repo sem nada em aberto gera quadro vazio sem quebrar",
             pd.backlog(r) == [] and pd.gerar(r))
        rep = (r / pd.SAIDA / "STATUS-REPORT.md").read_text(encoding="utf-8")
        caso("e o report diz explicitamente que nada esta em aberto", "nada em aberto" in rep)

    # ── o CARIMBO de canarios: quatro modos de falha, nenhum coberto antes ──
    #
    # `estado()` deixou de RODAR a suite (subprocess com teto de 600s, que a suite
    # ja' ultrapassava) e passou a LER `_meta/canarios-ultimo.json`. O QA da 35a
    # rodada achou 2 ALTA + 1 MEDIA nesse codigo novo — e achou tambem que ele
    # tinha ZERO cobertura. Estes quatro casos sao a rede que faltava.
    with tempfile.TemporaryDirectory(prefix="pd-carimbo-") as td:
        r = _repo(td)
        alvo = r / "_meta" / "canarios-ultimo.json"
        alvo.parent.mkdir(parents=True, exist_ok=True)

        alvo.write_text("null", encoding="utf-8")
        e = pd.estado(r)
        caso("carimbo JSON-valido mas NAO-dict nao derruba o quadro",
             "ilegível" in e["canarios"] and "NoneType" in e["canarios"])

        alvo.write_text("{truncado", encoding="utf-8")
        caso("carimbo truncado (o que a escrita nao-atomica produzia) e' legivel como erro",
             "ilegível" in pd.estado(r)["canarios"])

        alvo.write_text(json.dumps({
            "resultado": "88 PASS · 1 SKIP · 0 FAIL (de 89 canários)",
            "medido_em": "2020-01-01T00:00:00-03:00", "commit": "deadbee",
        }), encoding="utf-8")
        velho = pd.estado(r)["canarios"]
        caso("numero medido em 2020 sai marcado DESATUALIZADO, nao como atual",
             "88 PASS" in velho and "DESATUALIZADO" in velho)

        # e o par que prova que a marca sabe ficar QUIETA: medicao no futuro
        # proximo cobre tudo que ha' no disco, entao nada envelheceu.
        alvo.write_text(json.dumps({
            "resultado": "88 PASS · 1 SKIP · 0 FAIL (de 89 canários)",
            "medido_em": (datetime.now().astimezone()
                          + timedelta(days=1)).isoformat(timespec="seconds"),
            "commit": "deadbee",
        }), encoding="utf-8")
        fresco = pd.estado(r)["canarios"]
        caso("medicao mais nova que todo arquivo NAO e' marcada desatualizada",
             "88 PASS" in fresco and "DESATUALIZADO" not in fresco)

        # A MARCA NAO PODE SE ACUSAR. Gerar o quadro toca STATUS-REPORT.md,
        # backlog.csv e cronograma.csv — rastreados, e portanto contados como
        # "mudaram depois da medicao". A 1a versao acendia a marca ao gerar, e a
        # contagem CRESCIA a cada geracao: marca sempre acesa por motivo alheio
        # aos canarios, que e' pior que marca nenhuma porque ensina a ignora-la.
        pd.gerar(r)
        pd.gerar(r)
        depois_de_gerar = pd.estado(r)["canarios"]
        caso("gerar o quadro (2x) NAO envelhece o proprio quadro",
             "88 PASS" in depois_de_gerar and "DESATUALIZADO" not in depois_de_gerar)

        # E O PAR: mexer em CODIGO de verdade acende, senao a exclusao dos
        # derivados virou cegueira em vez de precisao.
        #
        # A 1a versao deste caso reaproveitava o carimbo do caso anterior, cuja
        # medicao esta' no FUTURO (amanha) — nada que se escrevesse podia ser
        # mais novo que ela, e o caso reprovava por vazamento de estado entre
        # casos, nao por defeito. Aqui o carimbo e' de AGORA e o arquivo de
        # codigo recebe mtime explicitamente posterior.
        agora = datetime.now().astimezone()
        alvo.write_text(json.dumps({
            "resultado": "88 PASS · 1 SKIP · 0 FAIL (de 89 canários)",
            "medido_em": agora.isoformat(timespec="seconds"), "commit": "deadbee",
        }), encoding="utf-8")
        caso("com o carimbo de agora, nada envelheceu ainda",
             "DESATUALIZADO" not in pd.estado(r)["canarios"])

        (r / "tools").mkdir(parents=True, exist_ok=True)
        codigo_novo = r / "tools" / "algo.py"
        codigo_novo.write_text("# mudei o codigo\n", encoding="utf-8")
        futuro = agora.timestamp() + 120
        os.utime(codigo_novo, (futuro, futuro))
        caso("mas mexer em CODIGO depois da medicao acende a marca",
             "DESATUALIZADO" in pd.estado(r)["canarios"])

    print("-" * 50)
    ruins = [n for n, ok in resultados if not ok]
    if ruins:
        print(f"RESULTADO: FAIL ({len(ruins)}) — {', '.join(ruins)}")
        return 1
    print(f"RESULTADO: PASS ({len(resultados)} verificacoes: o quadro reflete as fontes nos dois "
          f"sentidos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
