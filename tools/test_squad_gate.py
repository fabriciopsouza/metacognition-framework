"""Canario do squad_gate (ADR-092) — FAIL-CLOSED. Prova que o gate:
- exige qa-critic para mudanca de codigo;
- so aceita evidencia ATESTADA (agentId + modelo != autor) — auto-atestacao NAO passa (anti-teatro);
- exige architect para ADR.
Sem este teste verde, J3 do bloco do ADR-092 NAO fecha.
"""
import squad_gate as sg

MANIFEST = sg.load_manifest()


def _ev(recomendacao="aprovar", agentId="", modelo="", autor=""):
    return {"bloco": "x", "passou": True, "recomendacao": recomendacao,
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
