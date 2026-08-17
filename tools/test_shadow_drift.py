#!/usr/bin/env python3
"""Canário do shadow_drift — o silêncio das distribuições vira número.

CONTEXTO. As cinco distribuições são geradas do canônico por um workflow no GitHub Actions.
Quando o Actions ficou desligado por billing, elas **congelaram por vinte releases sem nenhum
alarme** — a deriva só apareceu quando alguém foi olhar à mão, meses depois. O workflow voltou a
funcionar, mas o ponto único de falha é o mesmo: se cair de novo, o silêncio volta.

O QUE ESTE CANÁRIO PROTEGE. Que o verificador **acuse a deriva** e, principalmente, que ele **não
confunda ausência de medição com aprovação**. Sem rede ele declara SKIP; se algum dia esse SKIP
virar "em dia", o alarme morre exatamente como morreu da primeira vez, e ninguém percebe.

git é real (repositório de mentira criado na hora); a consulta ao GitHub é substituída, porque
canário que depende de rede não é determinístico.

Uso: python tools/test_shadow_drift.py   (exit 0 PASS; 1 se a deriva puder passar despercebida)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import shadow_drift as sd  # noqa: E402

resultados = []


def caso(nome, ok, detalhe=""):
    resultados.append((nome, ok))
    print(f"  [{'PASS' if ok else 'FALHA'}] {nome}")
    if detalhe and not ok:
        print(f"          {detalhe}")


def _repo(raiz, n_commits=4):
    """Repositório real com N commits, e o workflow que declara duas distribuições."""
    raiz = Path(raiz)
    (raiz / ".github" / "workflows").mkdir(parents=True)
    (raiz / ".github" / "workflows" / "publish-clean.yml").write_text(
        'env:\n  PUBLIC_REPO: "dono/proj-public"\n  PREMIUM_REPO: "dono/proj-premium"\n',
        encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(raiz)], capture_output=True)
    shas = []
    for i in range(n_commits):
        (raiz / f"f{i}.txt").write_text(str(i), encoding="utf-8")
        subprocess.run(["git", "-C", str(raiz), "add", "-A"], capture_output=True)
        subprocess.run(["git", "-C", str(raiz), "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", f"c{i}"], capture_output=True)
        shas.append(subprocess.run(["git", "-C", str(raiz), "rev-parse", "--short", "HEAD"],
                                   capture_output=True, text=True).stdout.strip())
    return raiz, shas


def main():
    print("shadow_drift: acusa deriva, e nao confunde ausencia de medicao com aprovacao")

    with tempfile.TemporaryDirectory(prefix="sd-") as t:
        r, shas = _repo(t)
        alvos = sd.sombras(r)
        caso("le a lista de distribuicoes do proprio workflow",
             alvos == ["dono/proj-premium", "dono/proj-public"], f"leu: {alvos}")

        caso("extrai o commit de origem da mensagem de publicacao",
             sd.sha_publicado("publish: export limpo da fonte privada @ abc1234") == "abc1234")
        caso("mensagem sem o commit de origem NAO vira zero",
             sd.sha_publicado("publish: export limpo") is None,
             "sem saber de onde veio, a distancia e' desconhecida, nao zero")

        caso("distancia zero quando a sombra esta no HEAD",
             sd.distancia(r, shas[-1])[0] == 0)
        caso("distancia conta os commits de atraso",
             sd.distancia(r, shas[0])[0] == len(shas) - 1,
             f"esperado {len(shas)-1}, veio {sd.distancia(r, shas[0])[0]}")
        caso("commit inexistente e' DUVIDA, nao zero",
             sd.distancia(r, "deadbee")[0] is None)
        caso("commit fora da linha do HEAD e' DUVIDA, nao zero",
             sd.distancia(r, None)[0] is None)

        # A consulta ao GitHub e' substituida: o canario mede a LOGICA, nao a rede.
        original = sd._rodar

        def fingir(respostas):
            def _fake(args, timeout=45):
                if args[:2] == ["gh", "auth"]:
                    return "ok"
                if args[:2] == ["gh", "api"]:
                    for chave, valor in respostas.items():
                        if chave in args[2]:
                            return valor
                    return None
                return original(args, timeout)
            return _fake

        try:
            sd._rodar = fingir({"proj-public": f"publish @ {shas[-1]}",
                                "proj-premium": f"publish @ {shas[0]}"})
            res, skip = sd.medir(r)
            atras = {x["repo"].split("/")[-1]: x["atras"] for x in res}
            caso("mede cada distribuicao separadamente",
                 skip is None and atras == {"proj-public": 0, "proj-premium": len(shas) - 1},
                 f"skip={skip} atras={atras}")
            caso("exit 1 quando alguma passa da tolerancia",
                 sd.main(["--repo", str(r), "--json", "--limite", "1"]) == 1)
            caso("exit 0 quando todas cabem na tolerancia",
                 sd.main(["--repo", str(r), "--json", "--limite", "99"]) == 0)

            # O caso que fez a deriva passar despercebida da 1a vez.
            sd._rodar = lambda args, timeout=45: None
            res, skip = sd.medir(r)
            caso("sem `gh` autenticado, declara SKIP em vez de dizer 'em dia'",
                 skip is not None and res == [],
                 f"skip={skip} — ausencia de medicao NAO e' aprovacao")
            caso("e o SKIP nao vira exit 1 (nao reprova por falta de rede)",
                 sd.main(["--repo", str(r), "--json"]) == 0,
                 "verificador que reprova offline e' desligado na primeira viagem")

            # Consulta que falha para UMA sombra nao pode zerar aquela sombra.
            sd._rodar = fingir({"proj-public": f"publish @ {shas[-1]}"})
            res, _ = sd.medir(r)
            premium = next(x for x in res if "premium" in x["repo"])
            caso("sombra que nao respondeu fica em DUVIDA, nao em dia",
                 premium["atras"] is None and "nao consegui consultar" in premium["situacao"],
                 f"premium={premium}")

            # ACHADO ALTO do qa-critic: duvida nao pode sair zero.
            sd._rodar = fingir({})   # gh autentica, mas nenhuma consulta responde
            caso("todas em DUVIDA sai com codigo 2, nao 0",
                 sd.main(["--repo", str(r), "--json"]) == 2,
                 "verde perpetuo com '?' que ninguem le e' o defeito original de volta")

            sd._rodar = fingir({"proj-public": "publish sem o commit de origem",
                                "proj-premium": f"publish @ {shas[-1]}"})
            caso("UMA em duvida ja' sai diferente de zero",
                 sd.main(["--repo", str(r), "--json"]) == 2)
        finally:
            sd._rodar = original

    # ACHADO ALTO do qa-critic: o canario so' testava contra workflow FAKE. Se o formato do
    # workflow REAL mudar (rename, aspas simples, matrix), a lista zera e o alarme emudece —
    # pela porta que este teste diz guardar. Agora ele exige a lista real.
    reais = sd.sombras(TOOLS.parent)
    caso("le as distribuicoes do workflow REAL deste repositorio",
         len(reais) >= 5 and all("/" in x for x in reais),
         f"leu {len(reais)}: {reais} — se o formato do workflow mudar, isto fica vermelho")

    with tempfile.TemporaryDirectory(prefix="sd-aspas-") as t:
        r = Path(t)
        (r / ".github" / "workflows").mkdir(parents=True)
        # aspas SIMPLES: o formato que o regex nao entende — e que um refactor inocente produz
        (r / ".github" / "workflows" / "publish-clean.yml").write_text(
            "env:\n  PUBLIC_REPO: 'dono/proj-public'\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(r)], capture_output=True)
        res, skip = sd.medir(r)
        caso("workflow que existe mas nao foi entendido NAO vira SKIP silencioso",
             skip is None and res and res[0]["atras"] is None,
             f"skip={skip} res={res} — arquivo local ilegivel e' defeito, nao ausencia de dado")
        caso("e sai com codigo 2", sd.main(["--repo", str(r), "--json"]) == 2)

    with tempfile.TemporaryDirectory(prefix="sd-sem-wf-") as t:
        r = Path(t)
        subprocess.run(["git", "init", "-q", str(r)], capture_output=True)
        _, skip = sd.medir(r)
        caso("sem o workflow, declara SKIP em vez de aprovar",
             skip is not None, f"skip={skip}")

    print("-" * 50)
    ruins = [n for n, ok in resultados if not ok]
    if ruins:
        print(f"RESULTADO: FAIL ({len(ruins)}) — {', '.join(ruins)}")
        return 1
    print(f"RESULTADO: PASS ({len(resultados)} verificacoes: deriva vira numero, e falta de "
          f"medicao nao vira aprovacao)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
