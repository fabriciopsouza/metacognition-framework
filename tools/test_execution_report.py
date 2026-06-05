#!/usr/bin/env python3
"""Canário do execution-report dois-tiers (ADR-038 + ADR-052).

Prova as invariantes:
  OWNER (ADR-038): encerramento sem report = FAIL; sem placar = FAIL; token fabricado = FAIL; honesto = PASS.
  EXTERNAL (ADR-052): whitelist barra texto livre/PII; só passa schema codificado; opt-out e detector funcionam.
Hipótese adversarial (qa-critic): o whitelist VAZA até prova em contrário. Zero domínio.

Uso: python tools/test_execution_report.py   (exit 0 PASS; 1 se qualquer caso falha)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from execution_report import (  # noqa: E402
    validate_report, build_report, build_external_report, validate_external_report,
    detect_tier, telemetry_enabled, learnings_public,
    central_report_path, init_consent, publish_pseudonym, publish_learnings, central_repo_slug, _valid_slug,
    solution_id, get_offer_state, set_offer_state, should_offer,
)

# ----------------------------------------------------------------- OWNER (compat ADR-038)
REPORT_HONESTO = build_report()  # default tier=owner; tokens = NÃO MEDIDO

REPORT_FABRICADO = """# Execution-report
- Tokens: 152300
- Tempo (wall-clock): 45 min
- Turnos: 11
- Arquivos tocados: 13
- Testes: 6/6
- Rodadas de retrabalho: 3
## Placar gate × achado
| Achado | Quem pegou | Gate |
|---|---|---|
| bug | agente | qa |
"""
REPORT_TOKEN_COM_FONTE = build_report(  # ADR-062: via build_owner_report -> inclui seções de aprendizado
    tokens_line="input 100000 + output 52300 (fonte: transcripts ADR-026)")
# ADR-062: report completo MENOS as seções de aprendizado -> deve FALHAR (obrigação nova).
REPORT_SEM_APRENDIZADO = REPORT_FABRICADO.replace("- Tokens: 152300", "- Tokens: NÃO MEDIDO")
REPORT_SEM_PLACAR = """# Execution-report
- Tokens: NÃO MEDIDO (sem telemetria exposta)
- Tempo (wall-clock): NÃO MEDIDO
- Turnos: 11
- Arquivos tocados: 13
- Testes: 6/6
- Rodadas de retrabalho: 3
"""

# ----------------------------------------------------------------- EXTERNAL (ADR-052)
EXT_HONESTO = build_external_report(framework_version="1.39.0", execution_mode="default",
                                    route="squad", turnos="11", retrabalho="2", session_id="a1b2c3",
                                    gates_fired=[("route-gate", "pass"), ("mission-gate", "override")],
                                    failure_points=[("hook", "compaction-gate", "missed", "j4")],
                                    correction_events=[("rewind", "j3", "7")])

# Ataques que o whitelist DEVE reprovar:
# token de cliente FICTÍCIO de propósito (não usar nome real — seria o próprio vazamento que testamos)
EXT_TEXTO_LIVRE = EXT_HONESTO + "\n## notas\n- O cliente ACME-FICTICIO pediu uma mudanca no calculo.\n"
EXT_EMAIL = EXT_HONESTO.replace("session_id: a1b2c3", "session_id: joao@cliente.com")
EXT_CPF = EXT_HONESTO + "\n- id: 123.456.789-00; mechanism: gate; failure: missed; junction: na\n"
EXT_PROSA_COMO_VALOR = EXT_HONESTO.replace(
    "- type: rewind; junction: j3; turn: 7",
    "- type: rewind; junction: j3; turn: porque o usuario reclamou bastante do resultado")
EXT_ENUM_INVALIDO = EXT_HONESTO.replace("failure: missed", "failure: explodiu")
EXT_SEM_TIER = EXT_HONESTO.replace("tier: external\n", "")
EXT_SECAO_FORJADA = EXT_HONESTO + '\n## payload_secreto\n- dado: "informacao sensivel do cliente aqui"\n'

CASES = [
    # (desc, validador, texto, espera_ok)
    ("OWNER ausente", validate_report, "", False),
    ("OWNER honesto (NÃO MEDIDO)", validate_report, REPORT_HONESTO, True),
    ("OWNER token fabricado", validate_report, REPORT_FABRICADO, False),
    ("OWNER token + fonte", validate_report, REPORT_TOKEN_COM_FONTE, True),
    ("OWNER sem placar", validate_report, REPORT_SEM_PLACAR, False),
    ("OWNER sem seção de aprendizado (ADR-062)", validate_report, REPORT_SEM_APRENDIZADO, False),
    ("EXTERNAL honesto (schema)", validate_external_report, EXT_HONESTO, True),
    ("EXTERNAL com texto livre (cliente)", validate_external_report, EXT_TEXTO_LIVRE, False),
    ("EXTERNAL com e-mail em campo", validate_external_report, EXT_EMAIL, False),
    ("EXTERNAL com CPF", validate_external_report, EXT_CPF, False),
    ("EXTERNAL prosa como valor", validate_external_report, EXT_PROSA_COMO_VALOR, False),
    ("EXTERNAL enum inválido", validate_external_report, EXT_ENUM_INVALIDO, False),
    ("EXTERNAL sem tier", validate_external_report, EXT_SEM_TIER, False),
    ("EXTERNAL seção forjada c/ texto", validate_external_report, EXT_SECAO_FORJADA, False),
    # validate_report deve INFERIR external e barrar (não tratar como owner)
    ("dispatch infere external e barra texto livre", validate_report, EXT_TEXTO_LIVRE, False),
    ("dispatch infere external honesto", validate_report, EXT_HONESTO, True),
]


def main():
    fails = 0
    for desc, fn, text, expect_ok in CASES:
        ok, problems = fn(text)
        correct = ok == expect_ok
        fails += 0 if correct else 1
        status = "OK  " if correct else "FAIL"
        exp = "PASS" if expect_ok else "FAIL"
        detail = "" if ok else f" -> {problems[:2]}"
        print(f"{status} [esperado {exp:4}] {desc}{detail}")

    # detector de tier: este repo TEM docs/_private/ -> owner
    tier = detect_tier(ROOT)
    det_ok = tier == "owner"
    fails += 0 if det_ok else 1
    print(f"{'OK  ' if det_ok else 'FAIL'} detect_tier(repo do dono) == owner (got {tier!r})")

    # ADR-062: learnings_public no report OWNER limpo -> publicavel (sem problems) + header presente.
    pub, problems = learnings_public(REPORT_HONESTO, ROOT, require_consent=False)
    lp_ok = (not problems) and "PÚBLICO ANONIMIZADO" in pub
    fails += 0 if lp_ok else 1
    print(f"{'OK  ' if lp_ok else 'FAIL'} learnings_public (report limpo -> publicavel) "
          f"{'' if lp_ok else problems[:2]}")

    # ADR-063: central_report_path determinístico + anti-traversal.
    p_ok = central_report_path("ab12cd34", "2026-06-04T10:00:00", "blk-1") == "reports/ab12cd34/2026-06-04T10-00-00__blk-1.md"
    p_safe = ".." not in central_report_path("../../etc", "../..", "../../../x")  # traversal sanitizado
    # ADR-064 (qa-critic): slug rejeita '..' e formato invalido; aceita owner/repo legitimo.
    slug_ok = (_valid_slug("fabriciopsouza/metacognition-exec-reports") and not _valid_slug("../etc")
               and not _valid_slug("owner/..foo") and not _valid_slug("noslash"))
    fails += 0 if slug_ok else 1
    print(f"{'OK  ' if slug_ok else 'FAIL'} _valid_slug (rejeita '..'/invalido, aceita owner/repo)")

    # ADR-065: oferta por-solução — solution_id de mission.md + transições de estado (deferred re-oferta; done/declined nao).
    import tempfile
    tr = tempfile.mkdtemp(prefix="sol_")
    open(os.path.join(tr, "mission.md"), "w", encoding="utf-8").write("# Solucao Exemplo BI\n")
    sid = solution_id(tr)
    s0 = should_offer(sid, tr)                                   # pending -> oferta
    set_offer_state(sid, "deferred", tr); s1 = should_offer(sid, tr)   # deferred -> re-oferta
    set_offer_state(sid, "done", tr); s2 = should_offer(sid, tr)       # done -> nao
    set_offer_state(sid, "declined", tr); s3 = should_offer(sid, tr)   # declined -> nao
    inv = set_offer_state(sid, "lixo", tr)                       # estado invalido recusado
    off_ok = (sid == "solucao-exemplo-bi" and s0 and s1 and not s2 and not s3 and not inv)
    fails += 0 if off_ok else 1
    print(f"{'OK  ' if off_ok else 'FAIL'} oferta por-solução (solution_id + pending/deferred ofertam; done/declined nao)")
    fails += 0 if (p_ok and p_safe) else 1
    print(f"{'OK  ' if (p_ok and p_safe) else 'FAIL'} central_report_path (deterministico + anti-traversal)")

    # ADR-063: init_consent em home temporario (idempotente, pseudonimo aleatorio valido).
    import tempfile, re as _re
    th = tempfile.mkdtemp(prefix="consent_")
    path1, pseudo1, created1 = init_consent(home=th)
    path2, pseudo2, created2 = init_consent(home=th)  # 2a vez: preserva
    ic_ok = (created1 and not created2 and pseudo1 == pseudo2
             and _re.fullmatch(r"[a-f0-9]{8,32}", pseudo1) and publish_pseudonym(home=th) == pseudo1)
    fails += 0 if ic_ok else 1
    print(f"{'OK  ' if ic_ok else 'FAIL'} init_consent (idempotente + pseudonimo aleatorio + publish_pseudonym le)")

    # ADR-064: publish_learnings — consent-gated, gera staging anonimizado, fail-soft sem gh.
    ow = os.path.join(th, "owner.md"); open(ow, "w", encoding="utf-8").write(REPORT_HONESTO)
    th2 = tempfile.mkdtemp(prefix="noconsent_")  # home SEM consent
    _, prob_nc, _ = publish_learnings(ow, ROOT, run_gh=False, home=th2)
    staging, prob_ok, published = publish_learnings(ow, ROOT, run_gh=False, home=th, now_iso="2026-06-05T10-00-00")
    pl_ok = (prob_nc and "opt-in" in prob_nc[0]                       # sem consent -> recusa
             and not prob_ok and staging and os.path.isfile(staging)  # com consent -> staging gravado
             and "PÚBLICO ANONIMIZADO" in open(staging, encoding="utf-8").read()
             and published is False)                                  # run_gh=False -> nao publica (fail-soft)
    fails += 0 if pl_ok else 1
    print(f"{'OK  ' if pl_ok else 'FAIL'} publish_learnings (consent-gated + staging anonimizado + fail-soft sem gh)")

    # opt-out: env desliga o tier external
    os.environ["FRAMEWORK_NO_TELEMETRY"] = "1"
    off = telemetry_enabled(ROOT) is False
    del os.environ["FRAMEWORK_NO_TELEMETRY"]
    fails += 0 if off else 1
    print(f"{'OK  ' if off else 'FAIL'} opt-out via FRAMEWORK_NO_TELEMETRY desliga geração")

    print("-" * 60)
    print("RESULTADO:", f"FAIL ({fails} caso(s))" if fails else
          "PASS (owner ADR-038 + whitelist external ADR-052 + detector + opt-out)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
