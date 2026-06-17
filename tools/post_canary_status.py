#!/usr/bin/env python3
"""post_canary_status — BYO-CI: a segurança do GHA SEM GHA (ADR-088).

O gate de qualidade do repo é `tools/run_canaries.py` (suíte fail-closed). O GHA era só um
GATILHO morto desse gate (vermelho na main, bloqueava todo merge — ver memória/ADR-088). Este
tool reconecta a suíte VIVA à trava do GitHub: roda os canários e **só** posta um commit-status
`success` se 0 FAIL; senão posta `failure`. A branch protection exige o context `canarios-local`,
então um sha sem run verde **não pode** ser mergeado — mesmo modelo do GHA (required status check),
driver local em vez do runner morto.

Trade-off declarado vs GHA (ADR-088): 1 OS (não a matriz 3-OS — coberto em parte por
test_rules_parity) + auto-atestação na máquina do mantenedor (não infra neutra). Aceitável para
repo de dono único onde "não usamos github actions"; bloqueia merge ACIDENTAL de código vermelho.

O status é atrelado ao SHA exato + resultado real (não é carimbo): um novo commit invalida o
status anterior (strict mode), exigindo novo run verde.

Uso:
    python tools/post_canary_status.py            # roda canários + posta status no HEAD
    python tools/post_canary_status.py --dry-run  # mostra o payload, NÃO posta (sem rede)

Sempre posta no HEAD (= o que foi de fato testado). NÃO há `--sha` arbitrário (evita certificar
um sha diferente do que rodou — dissociação apontada pelo qa-critic, ADR-088).

Exit 0 se canários PASS (status success postado/simulado); 1 se FAIL (status failure) ou erro.
Requer `gh` autenticado (exceto --dry-run).
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTEXT = "canarios-local"


def parse_repo(remote_url):
    """github.com/owner/repo(.git)? -> 'owner/repo'. Fail-closed (ValueError) se não casar.
    ANCORADO no início (re.match + esquema/host) — 'github.com' no PATH (ex.: notgithub.com/github.com/o/r)
    NÃO conta como GitHub (qa-critic ADR-088: re.search aceitava host falso)."""
    m = re.match(r"(?:https?://github\.com/|git@github\.com:)([^/]+/[^/]+?)(?:\.git)?/?$", remote_url.strip())
    if not m:
        raise ValueError(f"remote não-GitHub ou ilegível: {remote_url!r}")
    return m.group(1)


def decide_state(canary_exit):
    """Mapeia exit-code do run_canaries em state de commit-status. Fonte única da regra."""
    return "success" if canary_exit == 0 else "failure"


def _git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT).stdout.strip()


def run_canaries():
    """Roda a suíte; retorna (exit_code, ultima_linha_resumo)."""
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "run_canaries.py")],
                          capture_output=True, text=True, cwd=ROOT, stdin=subprocess.DEVNULL)
    out = (proc.stdout or "").strip().splitlines()
    summary = next((l for l in reversed(out) if "RESULTADO" in l), out[-1] if out else "sem saída")
    return proc.returncode, summary


def main(argv):
    ap = argparse.ArgumentParser(description="Posta commit-status a partir do run de canários local (ADR-088).")
    ap.add_argument("--dry-run", action="store_true", help="mostra o payload, não posta (sem rede)")
    args = ap.parse_args(argv[1:])

    try:
        repo = parse_repo(_git("remote", "get-url", "origin"))
    except ValueError as e:
        print(f"ERRO (fail-closed): {e}", file=sys.stderr)
        return 1
    sha = _git("rev-parse", "HEAD")
    if not sha:
        print("ERRO (fail-closed): não consegui resolver o SHA", file=sys.stderr)
        return 1

    code, summary = run_canaries()
    state = decide_state(code)
    desc = summary[:140]

    if args.dry_run:
        print(f"[dry-run] repo={repo} sha={sha[:12]} context={CONTEXT} state={state}")
        print(f"[dry-run] description={desc!r}")
        return 0 if state == "success" else 1

    post = subprocess.run(
        ["gh", "api", "-X", "POST", f"repos/{repo}/statuses/{sha}",
         "-f", f"state={state}", "-f", f"context={CONTEXT}", "-f", f"description={desc}"],
        capture_output=True, text=True, cwd=ROOT)
    if post.returncode != 0:
        print(f"ERRO ao postar status (gh): {post.stderr.strip()[:200]}", file=sys.stderr)
        return 1
    print(f"status '{state}' postado em {repo}@{sha[:12]} (context={CONTEXT}) — {desc}")
    return 0 if state == "success" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
