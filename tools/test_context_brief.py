#!/usr/bin/env python3
"""Canário do gate de pesquisa de contexto (ADR-051). Agnóstico, sintético, reproduzível.

Casos:
  1. spec com sinal de stake + context-brief completo  -> PASS
  2. spec com sinal de stake + context-brief AUSENTE     -> FAIL (gate dispara)
  3. spec com sinal de stake + context-brief SEM âncora   -> FAIL (estrutura incompleta)
  4. spec SEM sinal de stake                              -> PASS (gate não dispara)
Controle: o caso 2/3 DEVE reprovar — o canário discrimina (não é always-green).

Roda standalone (python tools/test_context_brief.py) e sob pytest.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_context_brief as ccb

SIGNALS = ["regulado", "decisao executiva", "perda financeira", "auditavel", "saude"]

SPEC_STAKE = """# requirements.md
## Dimensões de elicitação
- operador: analista
- interface: GUI
Este indicador é **regulado** e a saída é **auditável**, alimenta **decisao executiva**.
"""

SPEC_NO_STAKE = """# requirements.md
## Dimensões de elicitação
- operador: dev
- interface: CLI
Ferramenta interna de conveniência, sem impacto material.
"""

BRIEF_FULL = """---
artefato: context-brief
---
# Context-Brief
## Verificação de âncora
| norma | vigência | pertinência ao tipo de entidade |
|---|---|---|
| Norma X | em vigor 2024 | NÃO se aplica a este tipo — referencial |
## Perfil
Setor, porte, posição. [CONFIRMADO]
## Fontes
ÓRGÃO. Norma X. https://exemplo. Acesso em: 1 jun. 2026.
"""

BRIEF_NO_ANCHOR = """# Context-Brief
## Perfil
Setor e porte. [INFERIDO]
## Fontes
http://exemplo 2026
"""


def _mk(tmp, spec_text, brief_text=None):
    d = tempfile.mkdtemp(dir=tmp)
    spec = os.path.join(d, "requirements.md")
    with open(spec, "w", encoding="utf-8") as fh:
        fh.write(spec_text)
    if brief_text is not None:
        with open(os.path.join(d, "context-brief.md"), "w", encoding="utf-8") as fh:
            fh.write(brief_text)
    return spec


def test_stake_with_full_brief_passes():
    with tempfile.TemporaryDirectory() as tmp:
        spec = _mk(tmp, SPEC_STAKE, BRIEF_FULL)
        ok, motivo, _ = ccb.check_spec(spec, SIGNALS)
        assert ok, f"esperado PASS, veio FAIL: {motivo}"


def test_stake_without_brief_fails():
    with tempfile.TemporaryDirectory() as tmp:
        spec = _mk(tmp, SPEC_STAKE, None)
        ok, motivo, _ = ccb.check_spec(spec, SIGNALS)
        assert not ok, "esperado FAIL (brief ausente), veio PASS"


def test_stake_with_brief_missing_anchor_fails():
    with tempfile.TemporaryDirectory() as tmp:
        spec = _mk(tmp, SPEC_STAKE, BRIEF_NO_ANCHOR)
        ok, motivo, faltas = ccb.check_spec(spec, SIGNALS)
        assert not ok, "esperado FAIL (sem tabela de âncora), veio PASS"
        assert any("ancora" in f for f in faltas), faltas


def test_no_stake_passes():
    with tempfile.TemporaryDirectory() as tmp:
        spec = _mk(tmp, SPEC_NO_STAKE, None)
        ok, motivo, _ = ccb.check_spec(spec, SIGNALS)
        assert ok, f"esperado PASS (sem stake), veio FAIL: {motivo}"


def test_word_boundary_no_false_positive():
    # 'normalizar'/'informacao'/'normal' NÃO podem disparar via substring de 'norma'
    real = ccb.load_signals()
    txt = "Pipeline para normalizar a informacao e gerar relatorio normal de rotina."
    assert ccb.spec_has_stake(txt, real) == [], \
        f"word-boundary falhou: {ccb.spec_has_stake(txt, real)}"
    assert "regulado" in ccb.spec_has_stake("Indicador regulado e auditavel.", real)


def test_real_seed_signals_load():
    sigs = ccb.load_signals()
    assert len(sigs) >= 10, "registro de sinais-semente deveria ter >=10 termos"
    assert "regulado" in sigs


def test_conscious_exemption_passes():
    with tempfile.TemporaryDirectory() as tmp:
        spec = _mk(tmp, SPEC_STAKE + "\n> context-brief: nao-aplicavel — spec interna\n", None)
        ok, motivo, _ = ccb.check_spec(spec, SIGNALS)
        assert ok, f"exceção consciente deveria passar: {motivo}"


def test_learn_signal_self_feeds_without_hitl():
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
        fh.write("regulado\nsaude\n")
        path = fh.name
    try:
        assert ccb.learn_signal("Risco Ambiental", path) is True
        assert "risco ambiental" in ccb.load_signals(path)
        assert ccb.learn_signal("regulado", path) is False  # idempotente
    finally:
        os.unlink(path)


def _run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fails = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            fails += 1
            print(f"FAIL {t.__name__}: {e}")
    print("-" * 50)
    print("CANÁRIO:", "PASS" if not fails else f"FAIL ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_run())
