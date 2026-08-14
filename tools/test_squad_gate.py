"""Canario do squad_gate (ADR-092) — FAIL-CLOSED. Prova que o gate:
- exige qa-critic para mudanca de codigo;
- so aceita evidencia ATESTADA (agentId + modelo != autor) — auto-atestacao NAO passa (anti-teatro);
- so aceita evidencia ESCOPADA aos paths avaliados (ADR-103 emenda 1) — evidencia antiga
  NAO e' carta-branca retroativa;
- exige architect para ADR;
- fecha juncao de release por match ANCORADO na versao, nao por substring.
Sem este teste verde, J3 do bloco do ADR-092 NAO fecha.
"""
import json

import squad_gate as sg

MANIFEST = sg.load_manifest()


def _ev(recomendacao="aprovar", agentId="", modelo="", autor="", escopo=("src/", "docs/adr/")):
    """Veredito de teste. `escopo` = escopo_paths declarado (ADR-103 emenda 1): veredito sem
    escopo NAO conta como evidencia — passe escopo=() para exercitar esse caso."""
    return {"bloco": "x", "passou": True, "recomendacao": recomendacao,
            "escopo_paths": list(escopo),
            "atestacao": {"agentId": agentId, "modelo": modelo, "autor": autor}}


def test_classify_codigo_exige_qa_critic():
    assert "qa_critic" in sg.classify(["src/x.py"], MANIFEST)


def test_classify_adr_exige_architect_e_qa():
    req = sg.classify(["docs/adr/099-foo.md"], MANIFEST)
    assert "architect" in req and "qa_critic" in req


def test_codigo_sem_evidencia_BLOQUEIA():
    faltam, _ = sg.evaluate(["src/x.py"], MANIFEST, artifacts=[])
    assert "qa_critic" in faltam


def test_codigo_com_evidencia_atestada_PASSA():
    ev = _ev(agentId="a4c1ac49", modelo="claude-haiku", autor="claude-opus")
    faltam, _ = sg.evaluate(["src/x.py"], MANIFEST, artifacts=[ev])
    assert "qa_critic" not in faltam


def test_auto_atestacao_NAO_passa():
    # modelo == autor (mesmo agente) -> teatro -> rejeitado
    ev = _ev(agentId="self", modelo="claude-opus", autor="claude-opus")
    faltam, _ = sg.evaluate(["src/x.py"], MANIFEST, artifacts=[ev])
    assert "qa_critic" in faltam


def test_sem_agentId_NAO_passa():
    ev = _ev(agentId="", modelo="claude-haiku", autor="claude-opus")
    faltam, _ = sg.evaluate(["src/x.py"], MANIFEST, artifacts=[ev])
    assert "qa_critic" in faltam


def test_doc_comum_nao_exige_qa():
    assert sg.classify(["docs/guia/leia.md"], MANIFEST) == set()


def test_adr_com_qa_atestado_passa():
    ev = _ev(agentId="a4c1", modelo="claude-haiku", autor="claude-opus")
    faltam, _ = sg.evaluate(["docs/adr/099-foo.md"], MANIFEST, artifacts=[ev])
    # architect OK (path e adr) e qa_critic OK (atestado) -> nada falta
    assert faltam == []


# ---------------------------------------------------------------------------
# Matriz ampliada (ADR-103): skill de nucleo/papel e regra sempre-ativa passam a
# exigir revisao. Antes devolviam "papeis exigidos: nenhum" — medido na sessao.
# ---------------------------------------------------------------------------

def test_skill_de_nucleo_exige_qa_critic():
    assert "qa_critic" in sg.classify(["_shared/project-docs/SKILL.md"], MANIFEST)


def test_skill_de_papel_e_regra_exigem_qa_critic():
    assert "qa_critic" in sg.classify([".agent/skills/docops/SKILL.md"], MANIFEST)
    assert "qa_critic" in sg.classify([".agent/rules/00-glossario.md"], MANIFEST)


def test_a_propria_matriz_exige_qa_critic():
    """Sem isto o gate se auto-afrouxa: bastaria editar a matriz sem revisao."""
    assert "qa_critic" in sg.classify(["behaviors/manifest.json"], MANIFEST)


# ---------------------------------------------------------------------------
# ADR-103 emenda 1 — achados BLOQUEANTE 2 e GRAVE 3 da 2a rodada (2026-08-13).
# Antes destes testes as funcoes novas nao tinham cobertura NENHUMA.
# ---------------------------------------------------------------------------

def test_evidencia_SEM_escopo_declarado_NAO_libera():
    """O gate se auto-liberava para sempre: UM veredito aprovativo em qualquer lugar de
    _meta/qa/ bastava para QUALQUER mudanca futura. Sem escopo declarado, nao conta."""
    ev = _ev(agentId="a1", modelo="claude-sonnet", autor="claude-opus", escopo=())
    faltam, _ = sg.evaluate(["src/x.py"], MANIFEST, artifacts=[ev])
    assert "qa_critic" in faltam


def test_evidencia_de_OUTRO_escopo_NAO_libera():
    """Veredito que revisou src/ nao pode liberar mudanca em _shared/."""
    ev = _ev(agentId="a1", modelo="claude-sonnet", autor="claude-opus", escopo=("src/",))
    faltam, _ = sg.evaluate(["_shared/project-docs/SKILL.md"], MANIFEST, artifacts=[ev])
    assert "qa_critic" in faltam


def test_evidencia_ESCOPADA_libera_so_o_que_cobre():
    ev = _ev(agentId="a1", modelo="claude-sonnet", autor="claude-opus",
             escopo=("_shared/", "docs/adr/"))
    faltam, _ = sg.evaluate(["_shared/project-docs/SKILL.md", "docs/adr/102-x.md"],
                            MANIFEST, artifacts=[ev])
    assert faltam == []


def test_escopo_parcial_NAO_libera_o_conjunto():
    """Cobrir 1 de 2 paths nao basta — o gate avalia o conjunto."""
    ev = _ev(agentId="a1", modelo="claude-sonnet", autor="claude-opus", escopo=("_shared/",))
    faltam, _ = sg.evaluate(["_shared/a/SKILL.md", "tools/outro.py"], MANIFEST, artifacts=[ev])
    assert "qa_critic" in faltam


def test_cobre_e_prefixo_de_PATH_nao_de_string():
    assert sg._cobre(["_shared"], "_shared/a/SKILL.md") is True
    assert sg._cobre(["_shared"], "_shared_antigo/a/SKILL.md") is False


def test_juncao_release_match_ANCORADO(tmp_path, monkeypatch):
    """Substring livre casava versao errada: '1.79.0' in 'release-21.79.0-x' era True."""
    qa = tmp_path / "qa"
    (qa / "junctions").mkdir(parents=True)
    (tmp_path / "CHANGELOG.md").write_text("# c\n\n## [1.79.0] - x\n", encoding="utf-8")
    monkeypatch.setattr(sg, "QA_DIR", str(qa))
    monkeypatch.setattr(sg, "ROOT", str(tmp_path))
    led = qa / "junctions" / "l.jsonl"

    # (a) versao DIFERENTE que contem a corrente como substring -> NAO libera
    led.write_text(json.dumps({"junction": "PC", "bloco": "release-21.79.0-x"}) + "\n",
                   encoding="utf-8")
    assert sg._release_junction_closed() is False

    # (b) fechamento de OUTRA versao -> NAO libera
    led.write_text(json.dumps({"junction": "PC", "bloco": "v1.58.0-adr-079-080"}) + "\n",
                   encoding="utf-8")
    assert sg._release_junction_closed() is False

    # (c) juncao que nao e' de fechamento -> NAO libera
    led.write_text(json.dumps({"junction": "J2", "bloco": "v1.79.0-project-docs"}) + "\n",
                   encoding="utf-8")
    assert sg._release_junction_closed() is False

    # (d) fechamento da versao corrente MAS sem veredito aprovativo vigente -> NAO libera
    #     (emenda 2 do ADR-103: presenca no ledger nao basta; ver o teste dedicado abaixo)
    led.write_text(json.dumps({"junction": "PC", "bloco": "v1.79.0-project-docs"}) + "\n",
                   encoding="utf-8")
    assert sg._release_junction_closed([]) is False

    # (e) fechamento legitimo + veredito aprovativo atestado do MESMO release -> libera
    ok = _ev(agentId="a1", modelo="sonnet", autor="opus")
    ok["release"] = "1.79.0"
    assert sg._release_junction_closed([ok]) is True


def test_juncao_release_REPROVACAO_POSTERIOR_invalida_o_PC(tmp_path, monkeypatch):
    """Achado BLOQUEANTE da 3a rodada (2026-08-13), reproduzido no repo real.

    O ledger e append-only e o PC e escrito UMA vez, no inicio do bloco. Sem checagem de
    veredito vigente, esse registro seguia liberando `juncao_release` mesmo depois de o QA
    REPROVAR o release duas vezes. Caso real: o unico registro de v1.79.0 nasceu em 4faf971
    (1o commit da serie) com `evidencia` dizendo "REPROVOU a 1a rodada", vieram 10 commits e
    2 reprovacoes, e `squad_gate --paths CHANGELOG.md` respondia OK.
    """
    qa = tmp_path / "qa"
    (qa / "junctions").mkdir(parents=True)
    (tmp_path / "CHANGELOG.md").write_text("## [1.79.0] - x\n", encoding="utf-8")
    monkeypatch.setattr(sg, "QA_DIR", str(qa))
    monkeypatch.setattr(sg, "ROOT", str(tmp_path))
    (qa / "junctions" / "l.jsonl").write_text(
        json.dumps({"junction": "PC", "bloco": "v1.79.0-project-docs"}) + "\n", encoding="utf-8")

    reprovado = _ev(recomendacao="reprovar", agentId="a1", modelo="sonnet", autor="opus")
    reprovado["release"] = "1.79.0"
    assert sg._release_junction_closed([reprovado]) is False, \
        "PC no ledger nao pode liberar release cujo veredito vigente REPROVA"

    # auto-atestacao (critico no MESMO modelo do autor) tambem nao vale como fechamento
    homogeneo = _ev(agentId="a1", modelo="opus", autor="opus")
    homogeneo["release"] = "1.79.0"
    assert sg._release_junction_closed([homogeneo]) is False, \
        "veredito sem heterogeneidade de modelo nao fecha juncao de release"

    # veredito aprovativo de OUTRO release nao serve
    outro = _ev(agentId="a1", modelo="sonnet", autor="opus")
    outro["release"] = "1.58.0"
    assert sg._release_junction_closed([outro]) is False


def test_juncao_release_SEM_ledger_bloqueia(tmp_path, monkeypatch):
    (tmp_path / "CHANGELOG.md").write_text("## [9.9.9] - x\n", encoding="utf-8")
    monkeypatch.setattr(sg, "QA_DIR", str(tmp_path / "qa"))
    monkeypatch.setattr(sg, "ROOT", str(tmp_path))
    assert sg._release_junction_closed() is False


def test_juncao_release_linha_corrompida_nao_libera(tmp_path, monkeypatch):
    """Fail-closed em ledger corrompido: linha invalida nao pode virar fechamento."""
    qa = tmp_path / "qa"
    (qa / "junctions").mkdir(parents=True)
    (tmp_path / "CHANGELOG.md").write_text("## [1.79.0] - x\n", encoding="utf-8")
    monkeypatch.setattr(sg, "QA_DIR", str(qa))
    monkeypatch.setattr(sg, "ROOT", str(tmp_path))
    (qa / "junctions" / "l.jsonl").write_text("{lixo nao-json\n", encoding="utf-8")
    assert sg._release_junction_closed() is False


# ---------------------------------------------------------------------------
# ADR-103 emenda 2 (3a e 4a rodadas, 2026-08-13/14): este arquivo e' pytest PURO. Sem o
# bloco abaixo, `run_canaries.py` o executava como script, o import definia as funcoes,
# o processo saia com 0 e o runner reportava PASS -- SEM rodar uma unica assercao.
# os testes do gate que governa o squad inteiro nunca haviam rodado no runner canonico.
#
# 4a RODADA — a 1a versao deste bloco delegava a `python -m pytest` e REPROVOU: o ADR-040
# ja rejeitara "pytest como entrypoint dos canarios", `pytest` nao esta em
# `requirements-dev.txt`, e a CI quebrou nos 3 SOs com "No module named pytest".
# Isso feria o principio declarado no proprio requirements-dev.txt: **ambiente nao
# reprova build**. Agora o entrypoint e' STDLIB PURA: implementa os dois unicos fixtures
# que estes testes usam (`tmp_path`, `monkeypatch`), descobre as funcoes `test_*` por
# introspecao e as executa. O arquivo continua coletavel por pytest para quem o tiver.
# ---------------------------------------------------------------------------
class _MonkeyPatch:
    """Substituto stdlib do fixture `monkeypatch` — so o que estes testes usam."""

    def __init__(self):
        self._undo = []

    def setattr(self, alvo, nome, valor):
        self._undo.append((alvo, nome, getattr(alvo, nome)))
        setattr(alvo, nome, valor)

    def desfazer(self):
        for alvo, nome, antigo in reversed(self._undo):
            setattr(alvo, nome, antigo)
        self._undo.clear()


def _descobrir():
    """Funcoes `test_*` DEFINIDAS NESTE ARQUIVO, em ordem de linha.

    Filtra por `__module__` e `isfunction` porque um callable `test_*` importado de outro
    modulo faria `getsourcelines` levantar OSError e derrubar a descoberta inteira antes de
    qualquer teste rodar (achado GRAVE latente da 5a rodada).
    """
    import inspect

    achadas = []
    for nome, obj in globals().items():
        if not nome.startswith("test_") or not inspect.isfunction(obj):
            continue
        if obj.__module__ != __name__:
            continue
        try:
            linha = inspect.getsourcelines(obj)[1]
        except OSError:
            linha = 10 ** 9  # nao localizavel: roda por ultimo, mas RODA
        achadas.append((linha, nome, obj))
    return [(n, f) for _, n, f in sorted(achadas)]


def _contar_no_fonte():
    """Quantas funcoes `test_*` de TOPO existem no ARQUIVO, por AST.

    A 1a versao usava regex `^def (test_\\w+)` e a 6a rodada achou o falso positivo: um
    exemplo dentro de docstring cuja linha comeca com `def test_algo():` era contado como
    definicao, a barreira disparava e reprovava o release inteiro por um artefato de prosa,
    com diagnostico enganoso. AST nao confunde texto com codigo.

    Retorna `None` so se o fonte nao puder ser lido — e nesse caso a barreira reprova, em
    vez de ser pulada em silencio (a versao anterior era fail-open aqui, contradizendo o
    proprio cabecalho FAIL-CLOSED deste arquivo).
    """
    import ast

    try:
        src = open(__file__, encoding="utf-8", errors="replace").read()
        arvore = ast.parse(src)
    except (OSError, SyntaxError):
        return None
    return sum(1 for no in arvore.body
               if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
               and no.name.startswith("test_"))


def _rodar_sem_pytest():
    import pathlib
    import shutil
    import tempfile
    import traceback
    import inspect

    testes = _descobrir()

    # ------------------------------------------------------------------
    # BARREIRA DE COMPLETUDE (5a rodada, 2026-08-13). Sem ela, um `def test_*`
    # escrito DEPOIS do bloco `if __name__` — o lugar mais natural para um dev
    # acrescentar codigo — nao existe em globals() quando a descoberta roda, e o
    # canario reporta "20 PASS / 0 FAIL" ignorando o teste novo em silencio.
    # O guard estatico do run_canaries.py nao pega isso: o bloco `if __name__`
    # ESTA no arquivo. Aqui a conta e' direta: descoberto tem de bater com o que
    # existe no fonte. Divergencia REPROVA.
    # ------------------------------------------------------------------
    no_fonte = _contar_no_fonte()
    if no_fonte is None:
        # fail-closed: nao conseguir ler o proprio fonte nao pode virar "barreira pulada"
        print("FAIL barreira-de-completude: nao foi possivel ler/parsear o proprio arquivo "
              "para conferir a contagem de testes.")
        print("RESULTADO: 0 PASS / 1 FAIL (barreira de completude inoperante)")
        return 1
    if no_fonte != len(testes):
        print(f"FAIL barreira-de-completude: o arquivo define {no_fonte} funcao(oes) `test_*` "
              f"de topo, mas o entrypoint descobriu {len(testes)}.")
        print("     Causas possiveis, em ordem: (a) teste definido DEPOIS do bloco "
              "`if __name__ == \"__main__\":` — nao existe em globals() na hora da descoberta;")
        print("     (b) teste registrado dinamicamente em globals(), que nao aparece no fonte;")
        print("     (c) funcao `test_*` importada de outro modulo (o filtro por __module__ a "
              "descarta).")
        print("     Um teste que nao roda e' pior que um teste ausente: o verde mente.")
        print(f"RESULTADO: 0 PASS / {no_fonte} FAIL (de {no_fonte} testes do squad_gate)")
        return 1

    falhas = []
    for nome, fn in testes:
        params = inspect.signature(fn).parameters
        tmp = mp = None
        try:
            kwargs = {}
            if "tmp_path" in params:
                tmp = tempfile.mkdtemp(prefix="canario_sg_")
                kwargs["tmp_path"] = pathlib.Path(tmp)
            if "monkeypatch" in params:
                mp = _MonkeyPatch()
                kwargs["monkeypatch"] = mp
            desconhecidos = set(params) - set(kwargs)
            if desconhecidos:
                raise RuntimeError(
                    f"fixture nao suportado pelo entrypoint stdlib: {sorted(desconhecidos)} "
                    f"— implemente-o aqui ou o teste NAO roda no runner canonico"
                )
            fn(**kwargs)
        # BaseException, nao Exception (5a rodada): `SystemExit` herda de BaseException.
        # Um `sys.exit(0)` no meio da suite matava o processo ANTES da linha RESULTADO,
        # com stdout vazio e returncode 0 — e o run_canaries.py taggeava PASS sem que
        # uma unica assercao tivesse rodado. KeyboardInterrupt segue interrompendo.
        except KeyboardInterrupt:
            raise
        except BaseException:
            falhas.append((nome, traceback.format_exc()))
        finally:
            try:
                if mp is not None:
                    mp.desfazer()
            finally:
                if tmp:
                    shutil.rmtree(tmp, ignore_errors=True)

    for nome, tb in falhas:
        print(f"FAIL {nome}\n{tb}")
    print(f"RESULTADO: {len(testes) - len(falhas)} PASS / {len(falhas)} FAIL "
          f"(de {len(testes)} testes do squad_gate)")
    return 1 if falhas else 0


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(_rodar_sem_pytest())
