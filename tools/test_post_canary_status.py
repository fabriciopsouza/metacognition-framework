#!/usr/bin/env python3
"""Canário do post_canary_status (ADR-088, BYO-CI) — prova FERRAMENTAL de que a lógica do gate é
determinística e fail-closed, SEM tocar a rede:
 (a) parse_repo extrai owner/repo de formas https/ssh/.git e FALHA-closed em remote não-GitHub;
 (b) decide_state: exit 0 -> success; QUALQUER !=0 -> failure (nunca success por engano);
 (c) --dry-run não chama gh (sem rede) e seu exit reflete o state (success=0 / failure=1).
Sem isto, "o status só fica verde se os canários passam" seria prosa. Fail-closed (exit 1 se diverge).

Uso: python tools/test_post_canary_status.py   (exit 0 PASS; 1 se falha)
"""
import io
import os
import sys
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import post_canary_status as pcs  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    fails = []

    # (a) parse_repo — formas válidas
    cases = {
        "https://github.com/fabriciopsouza/metacognition-framework": "fabriciopsouza/metacognition-framework",
        "https://github.com/fabriciopsouza/metacognition-framework.git": "fabriciopsouza/metacognition-framework",
        "git@github.com:fabriciopsouza/metacognition-framework.git": "fabriciopsouza/metacognition-framework",
        "https://github.com/owner/repo/": "owner/repo",
    }
    for url, expected in cases.items():
        try:
            got = pcs.parse_repo(url)
            if got != expected:
                fails.append(f"parse_repo({url!r}) = {got!r}, esperado {expected!r}")
        except ValueError as e:
            fails.append(f"parse_repo({url!r}) levantou erro inesperado: {e}")
    # fail-closed: remote não-GitHub — inclui host FALSO com 'github.com' no PATH (qa-critic ADR-088:
    # re.search não-ancorado aceitava isso; deve levantar ValueError com a regex ancorada).
    for bad in ["https://gitlab.com/o/r", "not a url", "",
                "https://notgithub.com/github.com/owner/repo",
                "https://evil.com/?github.com/owner/repo",
                "github.com.attacker.net/owner/repo"]:
        try:
            got = pcs.parse_repo(bad)
            fails.append(f"parse_repo NÃO falhou-closed para remote não-GitHub: {bad!r} -> {got!r}")
        except ValueError:
            pass

    # (b) decide_state — 0 success; tudo !=0 failure (nunca success por engano)
    if pcs.decide_state(0) != "success":
        fails.append("decide_state(0) != success")
    for code in (1, 2, 3, 255, -1):
        if pcs.decide_state(code) != "failure":
            fails.append(f"decide_state({code}) != failure (RISCO: verde com canário vermelho)")

    # (c) --dry-run não chama rede e exit/payload refletem o state — testado IN-PROCESS com
    # run_canaries MONKEYPATCHED. CRÍTICO: NÃO rodar a suíte real aqui — este canário é descoberto
    # por run_canaries, então invocar a suíte recursaria (run_canaries -> este teste -> run_canaries...).
    orig = pcs.run_canaries
    try:
        for fake_code, want_state, want_exit in [(0, "success", 0), (1, "failure", 1), (3, "failure", 1)]:
            pcs.run_canaries = lambda c=fake_code: (c, f"RESULTADO: stub exit={c}")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = pcs.main(["post_canary_status.py", "--dry-run"])
            out = buf.getvalue()
            if "[dry-run]" not in out:
                fails.append(f"--dry-run (code={fake_code}) não emitiu [dry-run] (pode ter tentado postar)")
            if f"state={want_state}" not in out:
                fails.append(f"--dry-run (code={fake_code}) payload sem state={want_state}")
            if rc != want_exit:
                fails.append(f"--dry-run (code={fake_code}) exit={rc}, esperado {want_exit} (fail-closed)")
    finally:
        pcs.run_canaries = orig

    # (d) O NOME DO STATUS. E' o unico elo entre este script e a protecao da branch: a `main`
    # exige um check chamado exatamente `canarios-local`, e e' este script que o publica. Trocar a
    # constante nao quebrava nada aqui — e todo PR passaria a travar para sempre, sem que nenhum
    # canario apitasse. Medido em 2026-08-16 ao sabotar `CONTEXT` e ver o verde persistir: a
    # capacidade `byo-ci-gate` estava declarada como protegida sem que este canario a cobrisse.
    CHECK_EXIGIDO = "canarios-local"
    if pcs.CONTEXT != CHECK_EXIGIDO:
        fails.append(f"CONTEXT={pcs.CONTEXT!r}, mas a protecao da main exige {CHECK_EXIGIDO!r} — "
                     f"trocar isto trava TODO PR sem aviso")
    orig2 = pcs.run_canaries
    try:
        pcs.run_canaries = lambda: (0, "RESULTADO: stub")
        buf = io.StringIO()
        with redirect_stdout(buf):
            pcs.main(["post_canary_status.py", "--dry-run"])
        if f"context={CHECK_EXIGIDO}" not in buf.getvalue():
            fails.append(f"o payload publicado nao carrega context={CHECK_EXIGIDO} — o check "
                         f"exigido nunca seria satisfeito")
    finally:
        pcs.run_canaries = orig2

    print(f"post_canary_status: parse_repo + decide_state (0=success/!=0=failure) + dry-run sem-rede "
          f"+ nome do check exigido — "
          f"{'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (gate BYO-CI determinístico e fail-closed)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
