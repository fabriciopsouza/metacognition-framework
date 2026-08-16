#!/usr/bin/env python3
"""Canário do research_evidence (ADR-092) — "NÃO SEI" só vale depois de busca provada.

CONTEXTO. O `behaviors/manifest.json` declara dois comportamentos que dependem desta ferramenta
(`research_ou_ratificacao` e `busca_exaustiva`) e ela nunca existiu — o `squad_gate.py` marcava o
papel como faltante para sempre, sem caminho para passar. Última peça em aberto do ADR-092.

O QUE ESTE CANÁRIO PROTEGE. Duas fraudes que esvaziariam a exigência sem que ninguém notasse:
citar o **mesmo domínio** duas vezes e chamar de triangulação; e anexar fonte **sem prova do que
foi lido** (sem hash, sem data de vigência). Mais o caminho humano: `ratificado_por` dispensa as
fontes de propósito, e precisa continuar dispensando — se quebrar, a pessoa que assume o número
fica sem caminho.

Uso: python tools/test_research_evidence.py   (exit 0 PASS; 1 se a exigência puder ser burlada)
"""
import json
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import research_evidence as re_  # noqa: E402

resultados = []


def caso(nome, ok, detalhe=""):
    resultados.append((nome, ok))
    print(f"  [{'PASS' if ok else 'FALHA'}] {nome}")
    if detalhe and not ok:
        print(f"          {detalhe}")


def _fonte(url, **troca):
    f = {"url": url, "sha256": "a" * 64, "vigencia_verificada_em": "2026-08-16",
         "oficial": True, "trecho": "o que sustenta"}
    f.update(troca)
    return f


def _repo(raiz, registro=None, k=2):
    raiz = Path(raiz)
    (raiz / "behaviors").mkdir(parents=True, exist_ok=True)
    (raiz / "behaviors" / "manifest.json").write_text(
        json.dumps({"parametros": {"K_dominios_distintos": k}}), encoding="utf-8")
    (raiz / "_meta" / "research").mkdir(parents=True, exist_ok=True)
    if registro is not None:
        (raiz / "_meta" / "research" / "assunto.json").write_text(
            json.dumps(registro, ensure_ascii=False), encoding="utf-8")
    return raiz


ALVO = "data/catalog/bindings.json"


def base(**troca):
    r = {"assunto": "faixa regulada", "escopo_paths": [ALVO], "data": "2026-08-16",
         "conclusao": "o valor e' X porque as fontes dizem",
         "fontes": [_fonte("https://a.exemplo/p1"), _fonte("https://b.exemplo/p2")]}
    r.update(troca)
    return r


def main():
    print("research_evidence: exige dominios distintos com prova, ou uma pessoa que assuma")

    with tempfile.TemporaryDirectory(prefix="re-ok-") as t:
        r = _repo(t, base())
        caso("registro com 2 dominios distintos e prova completa PASSA",
             re_.main(["--repo", str(r), "--paths", ALVO]) == 0)

    with tempfile.TemporaryDirectory(prefix="re-vazio-") as t:
        r = _repo(t, None)
        caso("sem registro nenhum, BLOQUEIA (fail-closed)",
             re_.main(["--repo", str(r), "--paths", ALVO]) == 1)

    # A fraude central: duas paginas do MESMO site nao sao duas fontes.
    with tempfile.TemporaryDirectory(prefix="re-mesmo-") as t:
        r = _repo(t, base(fontes=[_fonte("https://a.exemplo/p1"),
                                  _fonte("https://a.exemplo/p2")]))
        caso("mesmo dominio duas vezes NAO conta como triangulacao",
             re_.main(["--repo", str(r), "--paths", ALVO]) == 1,
             "citar o mesmo site duas vezes esvaziaria a exigencia inteira")

    with tempfile.TemporaryDirectory(prefix="re-www-") as t:
        r = _repo(t, base(fontes=[_fonte("https://a.exemplo/p1"),
                                  _fonte("https://www.a.exemplo/p2")]))
        caso("`www.` nao cria um dominio novo",
             re_.main(["--repo", str(r), "--paths", ALVO]) == 1)

    # A outra fraude: fonte sem prova do que foi lido.
    for campo in ("sha256", "vigencia_verificada_em", "url"):
        with tempfile.TemporaryDirectory(prefix=f"re-sem-{campo}-") as t:
            incompleta = _fonte("https://b.exemplo/p2")
            incompleta[campo] = ""      # `url` tambem entra aqui: fonte sem endereco nao prova nada
            r = _repo(t, base(fontes=[_fonte("https://a.exemplo/p1"), incompleta]))
            caso(f"fonte sem `{campo}` BLOQUEIA",
                 re_.main(["--repo", str(r), "--paths", ALVO]) == 1)

    # Burlas de UM CARACTERE, achadas pelo qa-critic (Fable, 2026-08-16).
    with tempfile.TemporaryDirectory(prefix="re-ponto-") as t:
        r = _repo(t, base(fontes=[_fonte("https://a.exemplo/p1"),
                                  _fonte("https://a.exemplo./p2")]))
        caso("ponto final no host NAO cria dominio novo (a.exemplo. == a.exemplo)",
             re_.main(["--repo", str(r), "--paths", ALVO]) == 1,
             "no DNS e' o mesmo site; um caractere inflava a triangulacao")

    with tempfile.TemporaryDirectory(prefix="re-file-") as t:
        r = _repo(t, base(fontes=[_fonte("https://a.exemplo/p1"),
                                  _fonte("file://qualquer/x")]))
        caso("esquema nao-web (file://) NAO conta como fonte",
             re_.main(["--repo", str(r), "--paths", ALVO]) == 1,
             "fonte que nem e' da rede virava a segunda perna da triangulacao")

    # O caminho humano precisa continuar existindo.
    with tempfile.TemporaryDirectory(prefix="re-ratif-") as t:
        r = _repo(t, base(fontes=[], ratificado_por="Fabricio Souza"))
        caso("ratificacao humana dispensa as fontes, por desenho",
             re_.main(["--repo", str(r), "--paths", ALVO]) == 0,
             "ha' numero que nao esta em fonte nenhuma; alguem assume")

    with tempfile.TemporaryDirectory(prefix="re-ratif-bool-") as t:
        r = _repo(t, base(fontes=[], ratificado_por=True))
        caso("`ratificado_por: true` NAO e' uma pessoa assumindo",
             re_.main(["--repo", str(r), "--paths", ALVO]) == 1,
             "booleano virava ratificado por 'True' — ninguem assumia e passava")

    with tempfile.TemporaryDirectory(prefix="re-ratif-vazia-") as t:
        r = _repo(t, base(fontes=[], ratificado_por="Fabricio", conclusao=""))
        caso("ratificacao SEM conclusao BLOQUEIA (assinar o que?)",
             re_.main(["--repo", str(r), "--paths", ALVO]) == 1)

    # Escopo: registro que nao declara o path nao cobre o path.
    with tempfile.TemporaryDirectory(prefix="re-escopo-") as t:
        r = _repo(t, base(escopo_paths=["outro/arquivo.json"]))
        caso("registro de OUTRO escopo nao cobre este path",
             re_.main(["--repo", str(r), "--paths", ALVO]) == 1)

    # K vem do manifesto: mudar a exigencia e' editar dado, nao codigo.
    with tempfile.TemporaryDirectory(prefix="re-k3-") as t:
        r = _repo(t, base(), k=3)
        caso("K sai do manifesto — com K=3, dois dominios nao bastam",
             re_.main(["--repo", str(r), "--paths", ALVO]) == 1
             and re_.k_exigido(r) == 3)

    with tempfile.TemporaryDirectory(prefix="re-json-ruim-") as t:
        r = _repo(t, None)
        (r / "_meta" / "research" / "quebrado.json").write_text("{ nao e json",
                                                                encoding="utf-8")
        caso("JSON invalido nao derruba a ferramenta (e nao cobre nada)",
             re_.main(["--repo", str(r), "--paths", ALVO]) == 1)

    caso("o modelo em branco e' JSON valido e utilizavel",
         isinstance(re_.MODELO, dict) and re_.main(["--modelo"]) == 0)

    print("-" * 50)
    ruins = [n for n, ok in resultados if not ok]
    if ruins:
        print(f"RESULTADO: FAIL ({len(ruins)}) — {', '.join(ruins)}")
        return 1
    print(f"RESULTADO: PASS ({len(resultados)} verificacoes: busca provada ou pessoa que assume; "
          f"o resto nao passa)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
