#!/usr/bin/env python3
"""Canario do boot_check (emenda ADR-061 / plano anti-bypass): prova que o self-check de boot RODA,
produz .claude/boot-proof.json com o schema esperado, FRESCO desta execucao, e cobre as 7 verificacoes
session-time (incl. author-tier ADR-082, env-applicability ADR-093, trabalhos-abertos ADR-100). Sem isto, "boot_check existe e funciona" seria prosa. Fail-closed (exit 1 se diverge).

Anti false-PASS (achado CRITICO do qa-critic 2026-06-10): NAO basta validar o schema de QUALQUER
boot-proof.json em disco — uma prova velha/forjada passaria. Aqui capturamos t0 ANTES de rodar e
exigimos que `ts` da prova seja >= t0 (gravada por ESTA execucao). Se boot_check falhar ao gravar e
deixar uma prova velha, o `ts` antigo reprova.

Roda boot_check.py SEM --session (nao carimba liveness -> sem efeito colateral no CI). Robusto offline:
checa SCHEMA + FRESCOR, nao os valores dos checks (um fetch que falha offline ainda produz prova valida).

Uso: python tools/test_boot_check.py   (exit 0 PASS; 1 se falha)
"""
import datetime
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

EXPECTED_CHECKS = {"repo-sync", "core-agnostic", "cross-ai-boot-scan", "version-sanity",
                   "env-applicability", "author-tier",  # env-applicability: ADR-093
                   "trabalhos-abertos"}  # ADR-100: oferece handoff pendente ate ser tratado
VALID_STATUS = {"ok", "warn", "fail", "skip"}


def main():
    fails = []

    # t0 ANTES de rodar (truncado a segundos: boot_check grava ts com timespec=seconds).
    t0 = datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(seconds=2)

    rc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "boot_check.py")],
                        cwd=ROOT, capture_output=True, text=True,
                        encoding="utf-8", errors="replace").returncode
    if rc != 0:
        fails.append(f"boot_check.py exit {rc} (deveria ser 0 fail-soft)")

    proof_path = os.path.join(ROOT, ".claude", "boot-proof.json")
    if not os.path.isfile(proof_path):
        print("RESULTADO: FAIL (boot-proof.json nao foi gravado)")
        return 1
    try:
        proof = json.load(open(proof_path, encoding="utf-8-sig"))  # BOM-tolerante
    except Exception as e:
        print(f"RESULTADO: FAIL (boot-proof.json ilegivel: {e})")
        return 1

    for k in ("session", "ts", "all_ok", "checks"):
        if k not in proof:
            fails.append(f"boot-proof sem campo '{k}'")

    # FRESCOR: a prova tem de ter sido escrita por ESTA execucao (anti prova velha/forjada).
    try:
        ts = datetime.datetime.fromisoformat(proof["ts"])
        if ts < t0:
            fails.append(f"boot-proof STALE: ts={proof['ts']} anterior a esta execucao (t0={t0.isoformat()}) "
                         f"— boot_check pode ter falhado ao gravar e deixado prova velha")
    except Exception as e:
        fails.append(f"boot-proof ts invalido/ausente: {e}")

    checks = proof.get("checks", [])
    names = {c.get("name") for c in checks}
    if names != EXPECTED_CHECKS:
        fails.append(f"checks {names} != esperado {EXPECTED_CHECKS}")
    for c in checks:
        if c.get("status") not in VALID_STATUS:
            fails.append(f"check {c.get('name')!r} status invalido: {c.get('status')!r}")
        if not c.get("detail"):
            fails.append(f"check {c.get('name')!r} sem detail")

    # contrato anti-bypass: importavel + funcoes-chave presentes (o gate de fechamento E2 depende disto)
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    try:
        import boot_check  # noqa: E402
        for fn in ("run_checks", "write_proof", "stamp_liveness"):
            if not callable(getattr(boot_check, fn, None)):
                fails.append(f"boot_check.{fn} ausente/nao-callable")
    except Exception as e:
        fails.append(f"boot_check nao importavel: {e}")

    print(f"boot-proof schema+frescor ok; {len(checks)} checks; nomes esperados; status validos — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (boot_check roda e prova e fresca e valida)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
