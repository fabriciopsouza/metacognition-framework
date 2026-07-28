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

# (next_role, risk, author) -> familia esperada (ADR-078: politica lida de model-policy.json;
# tier max = fable [Mythos-class, acima de Opus], balanced = sonnet, economy = haiku)
MODEL_CASES = [
    ("qa-critic", "low", "opus", "sonnet"),   # heterogeneo: autor tier-alto -> sonnet
    ("qa-critic", "low", "fable", "sonnet"),  # heterogeneo: autor fable -> sonnet
    ("qa-critic", "low", "sonnet", "fable"),  # heterogeneo: autor sonnet -> tier max
    ("review", "low", "opus", "sonnet"),
    ("cross-ai", "low", "opus", "fable"),     # handoff cross-IA -> tier max
    ("handoff gemini", "low", "opus", "fable"),
    ("architect", "low", "opus", "fable"),    # tier max
    ("discovery", "low", "opus", "fable"),
    ("docops", "low", "opus", "haiku"),       # tier economy (mecanico gateado por canario)
    ("developer", "low", "opus", "opus"),     # papel autoral -> tier baseline (= opus hoje; ADR-082)
    ("developer", "high", "opus", "fable"),   # risco sobrepoe papel -> tier max
    ("docops", "regulated", "sonnet", "fable"),  # risco sobrepoe papel
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
    # pre-condicao de ambiente (achado BAIXO do process-critic v1.57.0): MODEL_CASES assume
    # nenhuma indisponibilidade declarada — limpa env herdada (canario roda em processo proprio)
    os.environ.pop("FRAMEWORK_MODELS_UNAVAILABLE", None)

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

    # (b3) schema da policy (ADR-078): fonte unica integra — tiers resolvem a model_ids,
    # roles apontam para tiers existentes, escada declarada, risk_override valido.
    pol = handoff.POLICY
    for key in ("model_ids", "tiers", "roles", "default_tier", "risk_override", "heterogeneity_ladder"):
        if key not in pol:
            fails.append(f"model-policy.json sem chave obrigatoria '{key}'")
    for tname, t in pol.get("tiers", {}).items():
        chain = t.get("chain") or []
        if not chain:
            fails.append(f"tier '{tname}' sem chain de fallback")
        for fam in chain:
            if fam not in pol.get("model_ids", {}):
                fails.append(f"tier '{tname}': familia '{fam}' na chain sem model_id")
    for rule in pol.get("roles", []):
        tr = rule.get("tier")
        if tr != "heterogeneous" and tr not in pol.get("tiers", {}):
            fails.append(f"role {rule.get('match')} aponta tier inexistente '{tr}'")
    if pol.get("default_tier") not in pol.get("tiers", {}):
        fails.append(f"default_tier '{pol.get('default_tier')}' inexistente")
    for rk, rv in pol.get("risk_override", {}).items():
        if not rk.startswith("_") and rv not in pol.get("tiers", {}):
            fails.append(f"risk_override['{rk}'] aponta tier inexistente '{rv}'")
    if len(pol.get("heterogeneity_ladder", [])) < 3:
        fails.append("heterogeneity_ladder incompleta (3 degraus: cross-IA > modelo!=, > fresh declarado)")

    # (b3.1) baseline_author (ADR-082): autor da SESSAO >= baseline; relativo/evolutivo, guardado por canario
    ba = pol.get("baseline_author")
    if not isinstance(ba, dict):
        fails.append("model-policy.json sem bloco 'baseline_author' (ADR-082)")
    else:
        bm = (ba.get("model") or "").lower()
        if bm not in pol.get("model_ids", {}):
            fails.append(f"baseline_author.model '{bm}' sem model_id correspondente")
        if "baseline" not in pol.get("tiers", {}):
            fails.append("baseline_author exige tier 'baseline' (autor roda nele)")
        elif pol["tiers"]["baseline"]["chain"][0].lower() != bm:
            fails.append(f"tier baseline.chain[0] '{pol['tiers']['baseline']['chain'][0]}' != baseline_author.model '{bm}' (devem coincidir)")
        if not ba.get("author_roles"):
            fails.append("baseline_author.author_roles vazio (quais papeis sao autorais)")
    # papel autoral developer DEVE resolver ao baseline (nao mais ao default balanced)
    fam_dev, _ = handoff.suggest_model("developer", "low", "opus")
    if fam_dev != (ba.get("model") if isinstance(ba, dict) else None):
        fails.append(f"developer (autoral) = {fam_dev}, esperado baseline {ba.get('model') if isinstance(ba, dict) else '?'}")

    # (b4) fallback de indisponibilidade (ADR-078: declarada via env, nunca sondada/silenciosa)
    saved_env = os.environ.get("FRAMEWORK_MODELS_UNAVAILABLE")
    try:
        os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = "fable"
        fam, why = handoff.suggest_model("architect", "low", "opus")
        if fam != "opus" or "fallback" not in why:
            fails.append(f"fable indisponivel: architect = {fam} ({why!r}), esperado opus com nota de fallback")
        os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = "fable,opus"
        fam, _ = handoff.suggest_model("discovery", "low", "opus")
        if fam != "sonnet":
            fails.append(f"fable+opus indisponiveis: discovery = {fam}, esperado sonnet")
        fam, _ = handoff.suggest_model("qa-critic", "low", "sonnet")
        if fam == "sonnet":
            fails.append("het com fable/opus indisponiveis devolveu o proprio autor sem esgotar haiku")
        os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = "fable,opus,haiku"
        fam, why = handoff.suggest_model("qa-critic", "low", "sonnet")
        if fam != "sonnet" or "DEGRAU 3" not in why:
            fails.append(f"het esgotado: = {fam} ({why!r}), esperado degrau 3 DECLARADO (mesmo modelo fresh)")
        os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = "fable,opus,sonnet"
        fam, why = handoff.suggest_model("developer", "low", "opus")
        if fam != "haiku" or "fallback" not in why:
            fails.append(f"balanced com sonnet/opus indisponiveis: = {fam} ({why!r}), "
                         f"esperado haiku com nota de fallback")
        os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = "haiku,sonnet"
        try:
            handoff.suggest_model("docops", "low", "opus")
            fails.append("chain economy esgotada deveria levantar erro declarado, nao escolher em silencio")
        except ValueError:
            pass
    finally:
        if saved_env is None:
            os.environ.pop("FRAMEWORK_MODELS_UNAVAILABLE", None)
        else:
            os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = saved_env

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

    # --- ADR-095: modo PROCEDENCIA (carimbo em diretorio EXTERNO ao repo) -------------------
    import tempfile
    prov = handoff.provenance("/alvo/externo", ts="2026-07-22T00:00:00Z")
    # (a) campos DETERMINISTICOS do repo tem de aparecer
    for campo in ("metacognition-framework", "Versao", "Commit", "Operador humano"):
        if campo not in prov:
            fails.append(f"procedencia: campo deterministico ausente: {campo}")
    # (b) slots de dominio tem de ficar VISIVEIS (lacuna declarada, nao silencio)
    if "<preencher>" not in prov:
        fails.append("procedencia: nenhum SLOT '<preencher>' — lacuna de dominio ficaria silenciosa")
    # (c) status por artefato e o ponto todo do carimbo (minuta != registro)
    if "MINUTA" not in prov or "APROVADO" not in prov:
        fails.append("procedencia: taxonomia de status (MINUTA/PROPOSTA/MIGRADO/APROVADO) ausente")
    # (d) determinismo
    if prov != handoff.provenance("/alvo/externo", ts="2026-07-22T00:00:00Z"):
        fails.append("procedencia: nao-deterministico com mesmo estado/ts")
    # (e) RECUSA alvo dentro do repo (la a procedencia e o proprio git)
    if handoff.emit_provenance(os.path.join(handoff.ROOT, "tools"), "ts", write=False) != 2:
        fails.append("procedencia: aceitou alvo DENTRO do repo (devia recusar com exit 2)")
    # (f) recusa diretorio inexistente
    with tempfile.TemporaryDirectory() as td:
        if handoff.emit_provenance(os.path.join(td, "nao-existe"), "ts", write=False) != 2:
            fails.append("procedencia: aceitou diretorio inexistente (devia recusar com exit 2)")
        # (g) nao sobrescreve carimbo existente — apenda (traceability Regra 3)
        alvo = os.path.join(td, "externo")
        os.makedirs(alvo)
        handoff.emit_provenance(alvo, "2026-07-22T00:00:00Z", write=True)
        marca = "MARCA-QUE-NAO-PODE-SUMIR"
        with open(os.path.join(alvo, "PROCEDENCIA.md"), "a", encoding="utf-8") as fh:
            fh.write("\n" + marca + "\n")
        handoff.emit_provenance(alvo, "2026-07-23T00:00:00Z", write=True)
        txt = open(os.path.join(alvo, "PROCEDENCIA.md"), encoding="utf-8").read()
        if marca not in txt:
            fails.append("procedencia: SOBRESCREVEU carimbo existente (viola preservacao — Regra 3)")
        if "Sessao adicional" not in txt:
            fails.append("procedencia: 2a passagem nao apendou secao de sessao")

        # (h) NAO apenda em documento alheio: arquivo existente que nao e carimbo (pasta
        #     reaproveitada, arquivo vazio/truncado) — devia recusar, nao colar rabo sem cabeca.
        alheio_dir = os.path.join(td, "alheio")
        os.makedirs(alheio_dir)
        alheio = os.path.join(alheio_dir, "PROCEDENCIA.md")
        for conteudo in ("", "# Outro documento qualquer\n\ntexto de outra demanda\n"):
            with open(alheio, "w", encoding="utf-8") as fh:
                fh.write(conteudo)
            if handoff.emit_provenance(alheio_dir, "ts", write=True) != 2:
                fails.append("procedencia: apendou/sobrescreveu arquivo que NAO e carimbo "
                             f"(conteudo={conteudo!r:.30})")
            if open(alheio, encoding="utf-8").read() != conteudo:
                fails.append("procedencia: alterou documento alheio (devia deixar intacto)")

        # (i) --write COM caminho no modo procedencia: destino e sempre <DIR>/PROCEDENCIA.md.
        #     Aceitar e descartar em silencio e armadilha de CLI.
        limpo = os.path.join(td, "limpo")
        os.makedirs(limpo)
        if handoff.main(["handoff.py", "--provenance", limpo, "--write", "algum/caminho"]) != 2:
            fails.append("procedencia: --write com caminho foi aceito e descartado em silencio")

    # (j) guarda robusta a path exotico — commonpath levanta ValueError em drive diferente/UNC,
    #     que e JUSTAMENTE o caso de uso primario (drive corporativo sincronizado / share de rede).
    for exotico in ("D:\\NaoExisteDrive\\Chamado123", "\\\\servidor\\share\\Chamado123"):
        try:
            rc = handoff.emit_provenance(exotico, "ts", write=False)
        except Exception as e:  # noqa: BLE001 — qualquer excecao aqui e o bug
            fails.append(f"procedencia: guarda estourou {type(e).__name__} em alvo exotico {exotico}")
        else:
            if rc != 2:
                fails.append(f"procedencia: alvo exotico inexistente {exotico} devia dar exit 2, deu {rc}")

    # (k) bypass por CASE: filesystem Windows e case-INSENSITIVE, commonpath compara
    #     case-SENSITIVE — sem normcase, alvo DENTRO do repo passa como 'externo'.
    if os.name == "nt":
        if not handoff._inside_repo(os.path.join(handoff.ROOT.upper(), "tools")):
            fails.append("procedencia: guarda furada por CASE — alvo dentro do repo passou como externo")

    print(f"handoff: 6 campos P14; {len(MODEL_CASES)} regras de modelo; {len(ROLE_CASES)} inferencias; "
          f"deterministico; procedencia ADR-095 (11 checks) — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (gerador roda, regra papel+risco correta, deterministico)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
