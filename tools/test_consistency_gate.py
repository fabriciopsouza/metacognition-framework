#!/usr/bin/env python3
"""Canário do consistency_gate (ADR-030) — o espelho de fechamento agora tem quem o vigie.

CONTEXTO. O mecanismo existia desde o ADR-030 como `consistency-gate.ps1` e **nunca foi ligado
a evento nenhum**: sem hook, sem canário, sem chamada no fluxo. É a falha catalogada duas vezes
no `## Aprendizado` — *"gate existe mas não disparou em 7 fechamentos"*. Portado para Python e
cabeado no evento `Stop`, ele precisa de um canário, senão repete a história: mecanismo que
ninguém sabe se funciona.

MÉTODO. Monta dois repositórios de mentira — um SUJO, com um defeito plantado por dimensão, e
um LIMPO — e exige que o gate acuse os seis do sujo e nenhum do limpo. Falso-negativo e
falso-positivo, os dois lados. Sem repo de verdade: o gate é uma função pura sobre um diretório.

Uso: python tools/test_consistency_gate.py   (exit 0 PASS; 1 se o espelho mentir)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS / "hooks"))
import consistency_gate as cg  # noqa: E402

resultados = []


def caso(nome, ok, detalhe=""):
    resultados.append((nome, ok))
    print(f"  [{'PASS' if ok else 'FALHA'}] {nome}")
    if detalhe and not ok:
        print(f"          {detalhe}")


def _repo(raiz, *, versao_readme, versao_clog, adr_proposto, adr_duplicado,
          checkpoint, transiente, relatorio):
    """Monta um repo de mentira com os defeitos ligados/desligados um a um."""
    raiz = Path(raiz)
    (raiz / "docs" / "adr").mkdir(parents=True)
    (raiz / "README.md").write_text(f"> **Versão:** {versao_readme} · x\n", encoding="utf-8")
    (raiz / "CHANGELOG.md").write_text(f"## [{versao_clog}] — hoje — titulo\n", encoding="utf-8")
    (raiz / "history.md").write_text(
        f"## checkpoint {versao_clog}\n" if checkpoint else "## sem versao aqui\n",
        encoding="utf-8")
    status = "Proposto" if adr_proposto else "Aceito"
    (raiz / "docs" / "adr" / "001-um.md").write_text(f"- Status: {status}\n", encoding="utf-8")
    if adr_duplicado:
        (raiz / "docs" / "adr" / "001-outro-com-mesmo-numero.md").write_text(
            "- Status: Aceito\n", encoding="utf-8")
    if transiente:
        (raiz / "docs" / "_intake").mkdir(parents=True)
        (raiz / "docs" / "_intake" / "rascunho.md").write_text("x\n", encoding="utf-8")
    if relatorio:
        (raiz / "telemetry").mkdir(parents=True)
        (raiz / "telemetry" / "telemetry-report.md").write_text("conteudo\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(raiz)], capture_output=True)
    return raiz


def dims_acusadas(raiz):
    pend, _ = cg.auditar(raiz)
    return {i["dimensao"] for i in pend}


def main():
    print("consistency_gate: acusa o repo sujo e absolve o limpo, dimensao a dimensao")

    with tempfile.TemporaryDirectory(prefix="cg-sujo-") as tmp:
        sujo = _repo(tmp, versao_readme="1.0.0", versao_clog="2.0.0", adr_proposto=True,
                     adr_duplicado=True, checkpoint=False, transiente=True, relatorio=False)
        acusou = dims_acusadas(sujo)
        for dim, oquee in [
            ("version-sync", "README diferente do topo do CHANGELOG"),
            ("adr-status", "ADR parado em Proposto"),
            ("checkpoint", "history.md sem a versao corrente"),
            ("contagens", "dois ADR com o mesmo numero"),
            ("transients", "rascunho esquecido em docs/_intake"),
            ("execution-report", "relatorio do bloco ausente"),
        ]:
            caso(f"acusa {dim} ({oquee})", dim in acusou, f"acusadas: {sorted(acusou)}")

    with tempfile.TemporaryDirectory(prefix="cg-limpo-") as tmp:
        limpo = _repo(tmp, versao_readme="2.0.0", versao_clog="2.0.0", adr_proposto=False,
                      adr_duplicado=False, checkpoint=True, transiente=False, relatorio=True)
        acusou = dims_acusadas(limpo)
        # `unpushed` sempre acusa num repo sem remoto — e' correto e nao e' falso-positivo.
        indevidas = acusou - {"unpushed"}
        caso("absolve o repo limpo (nenhum falso-positivo)", not indevidas,
             f"acusou indevidamente: {sorted(indevidas)}")
        caso("acusa unpushed em repo sem upstream", "unpushed" in acusou)

    # Achado MEDIO do qa-critic: no `.ps1` original o filtro de `000-*` vale so para a lista de
    # "Proposto"; para DUPLICATA de numero o template conta. O port tinha perdido isso.
    with tempfile.TemporaryDirectory(prefix="cg-000-") as tmp:
        r = _repo(tmp, versao_readme="2.0.0", versao_clog="2.0.0", adr_proposto=False,
                  adr_duplicado=False, checkpoint=True, transiente=False, relatorio=True)
        (r / "docs" / "adr" / "000-template.md").write_text("- Status: Aceito" + chr(10), encoding="utf-8")
        (r / "docs" / "adr" / "000-copia-indevida.md").write_text("- Status: Aceito" + chr(10),
                                                                  encoding="utf-8")
        caso("duplicata entre arquivos 000-* e' acusada (o template conta para numero)",
             "contagens" in dims_acusadas(r), f"acusadas: {sorted(dims_acusadas(r))}")
        pend, dims = cg.auditar(r)
        caso("mas 000-* NAO entra na lista de 'Proposto'",
             dims["adr-status"]["propostos"] == [],
             f"propostos: {dims['adr-status']['propostos']}")

    # O modo hook e' fail-soft por DESENHO: pendencia nao pode derrubar a sessao do dono.
    with tempfile.TemporaryDirectory(prefix="cg-hook-") as tmp:
        sujo = _repo(tmp, versao_readme="1.0.0", versao_clog="2.0.0", adr_proposto=True,
                     adr_duplicado=True, checkpoint=False, transiente=True, relatorio=False)
        import contextlib, io as _io
        with contextlib.redirect_stdout(_io.StringIO()):
            rc = cg.main(["--repo", str(sujo), "--hook"])
        recibo = sujo / cg.RECIBO
        caso("modo --hook nao falha a sessao mesmo com pendencia", rc == 0, f"exit={rc}")
        caso("modo --hook grava recibo do que encontrou", recibo.is_file(),
             f"esperado em {recibo}")

    # Fora do modo hook o exit code E' o numero de pendencias — e' o que o /checkpoint consome.
    with tempfile.TemporaryDirectory(prefix="cg-exit-") as tmp:
        limpo = _repo(tmp, versao_readme="2.0.0", versao_clog="2.0.0", adr_proposto=False,
                      adr_duplicado=False, checkpoint=True, transiente=False, relatorio=True)
        import contextlib, io as _io
        with contextlib.redirect_stdout(_io.StringIO()):
            rc = cg.main(["--repo", str(limpo), "--json"])
        caso("exit code fora do modo hook = numero de pendencias", rc == 1, f"exit={rc}")

    print("-" * 50)
    ruins = [n for n, ok in resultados if not ok]
    if ruins:
        print(f"RESULTADO: FAIL ({len(ruins)}) — {', '.join(ruins)}")
        return 1
    print(f"RESULTADO: PASS ({len(resultados)} verificacoes: o espelho de fechamento "
          f"acusa o que deve e absolve o que deve)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
