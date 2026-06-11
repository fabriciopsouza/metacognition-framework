#!/usr/bin/env python3
"""Canario do handoff.py (ADR-076): prova que o gerador (a) RODA e emite os 5 campos P14 + sugestao de
modelo, (b) a regra papel+risco mapeia corretamente, (c) e DETERMINISTICO (mesmos inputs -> mesma saida).
Sem (b)/(c) a "sugestao deterministica" seria prosa. Fail-closed.

Uso: python tools/test_handoff.py   (exit 0 PASS; 1 se falha)
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import handoff  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P14_SECTIONS = [
    "[modelo sugerido]",
    "[P14] Artefato consumivel",
    "[P14] Localizacao",
    "[P14] Acesso",
    "[P14] Prompt pronto-para-colar",
    "[P14] Pendencias e premissas herdadas",
]

# (next_role, risk, author) -> familia esperada
MODEL_CASES = [
    ("qa-critic", "low", "opus", "sonnet"),   # heterogeneo: autor opus -> sonnet
    ("qa-critic", "low", "sonnet", "opus"),   # heterogeneo: autor sonnet -> opus
    ("review", "low", "opus", "sonnet"),
    ("cross-ai", "low", "opus", "opus"),      # handoff cross-IA -> mais capaz
    ("handoff gemini", "low", "opus", "opus"),
    ("architect", "low", "opus", "opus"),     # mais capaz
    ("discovery", "low", "opus", "opus"),
    ("docops", "low", "opus", "sonnet"),      # custo-eficiente
    ("developer", "low", "opus", "sonnet"),   # default
    ("developer", "high", "opus", "opus"),    # risco sobrepoe papel
    ("docops", "regulated", "sonnet", "opus"),  # risco sobrepoe papel
]

ROLE_CASES = [
    ("rodar o qa-critic adversarial no bloco", "qa-critic"),
    ("entregar handoff cross-IA para o gemini", "cross-ai"),
    ("decidir a arquitetura e abrir ADR", "architect"),
    ("implementar o script e o canario", "developer"),
    ("atualizar CHANGELOG e taggear o release", "docops"),
]


def main():
    fails = []

    # (a) roda e emite os campos
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "handoff.py")],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        fails.append(f"handoff.py exit {r.returncode} (esperado 0)")
    out = r.stdout or ""
    for s in P14_SECTIONS:
        if s not in out:
            fails.append(f"saida sem secao P14: {s!r}")
    if "claude-" not in out:
        fails.append("saida sem ID de modelo sugerido (claude-*)")

    # (b) regra papel+risco
    for role, risk, author, expect_fam in MODEL_CASES:
        fam, _why = handoff.suggest_model(role, risk, author)
        if fam != expect_fam:
            fails.append(f"suggest_model({role},{risk},autor={author}) = {fam}, esperado {expect_fam}")
        if handoff.MODEL_ID.get(fam) is None:
            fails.append(f"familia {fam} sem ID em MODEL_ID")

    # (b2) inferencia de papel
    for text, expect_role in ROLE_CASES:
        got = handoff.infer_role(text)
        if got != expect_role:
            fails.append(f"infer_role({text!r}) = {got}, esperado {expect_role}")

    # (c) determinismo RIGOROSO: congela TAMBEM o estado do repo e a rede (repo_state/pr_info
    # monkeypatch) -> prova que a CAMADA DE FORMATACAO e byte-identica dado o mesmo estado, nao so
    # ausencia de wall-clock (ressalva do qa-critic). Restaura os originais ao fim.
    orig_rs, orig_pr, orig_ea, orig_pa, orig_cf = (
        handoff.repo_state, handoff.pr_info, handoff.em_aberto,
        handoff.proposed_adrs, handoff.latest_checkpoint_field)
    try:
        FIXED = {"version": "9.9.9", "branch": "feat/x", "commit": "abc1234",
                 "origin": "git@example/repo", "unpushed": "?", "uncommitted": 0, "recent": ["a.py", "b.md"]}
        handoff.repo_state = lambda: dict(FIXED)
        handoff.pr_info = lambda branch: "(sem PR aberto para esta branch)"
        handoff.em_aberto = lambda: ["pendencia X"]
        handoff.proposed_adrs = lambda: []
        handoff.latest_checkpoint_field = lambda f: "Fazer Y (criterio: Z)"
        a = handoff.build("developer", "low", "opus", ts="2026-06-11T00:00:00Z")
        b = handoff.build("developer", "low", "opus", ts="2026-06-11T00:00:00Z")
        if a != b:
            fails.append("nao-deterministico: build() com MESMO estado deu saidas diferentes")
        # safety P14 (achado ALTO): unpushed='?' NUNCA pode render 'nada pendente'
        if "nada pendente" in a or "DESCONHECIDO" not in a:
            fails.append("unpushed='?' renderizou 'nada pendente' (falso) em vez de 'DESCONHECIDO' — P14 Acesso inseguro")
    finally:
        (handoff.repo_state, handoff.pr_info, handoff.em_aberto,
         handoff.proposed_adrs, handoff.latest_checkpoint_field) = (
            orig_rs, orig_pr, orig_ea, orig_pa, orig_cf)

    print(f"handoff: 6 campos P14; {len(MODEL_CASES)} regras de modelo; {len(ROLE_CASES)} inferencias; "
          f"deterministico — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (gerador roda, regra papel+risco correta, deterministico)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
