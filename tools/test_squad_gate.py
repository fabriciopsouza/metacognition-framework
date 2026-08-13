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

    # (d) fechamento legitimo da versao corrente -> libera
    led.write_text(json.dumps({"junction": "PC", "bloco": "v1.79.0-project-docs"}) + "\n",
                   encoding="utf-8")
    assert sg._release_junction_closed() is True


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
