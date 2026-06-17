#!/usr/bin/env python3
"""Canary do check-repo-sync (ADR-019): prova que o hook auto-atualiza quando seguro e AVISA quando não.

Critério (espelha P1/ADR-015): existe teste que exercita os caminhos reais e confirma o comportamento.
Monta um origin + clone temporários, avança o origin, e roda o hook com CLAUDE_PROJECT_DIR=clone:
  C1 clone LIMPO e atrás (ff)        -> deve AUTO-ATUALIZAR (additionalContext contém "AUTO-ATUALIZADO")
  C2 clone SUJO e atrás              -> deve AVISAR, sem atualizar (contém "NAO auto-atualizei" + "SUJO")
  C3 clone EM DIA                    -> silencioso (additionalContext == "")

Uso: python tools/test_repo_sync.py   (exit 0 se todos OK; 1 caso contrário; SKIP se sem pwsh/git).
"""
import json, os, shutil, subprocess, sys, tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_PY = os.path.join(ROOT, "tools", "hooks", "check_repo_sync.py")
HOOK_PS = os.path.join(ROOT, ".claude", "hooks", "check-repo-sync.ps1")


def have(exe):
    return shutil.which(exe) is not None


def git(cwd, *args):
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)


def find_runner():
    """Python-first (ADR-060 pattern): check_repo_sync.py ja existe como porta definitiva."""
    if os.path.isfile(HOOK_PY):
        return (sys.executable, HOOK_PY, False)
    for exe in ("pwsh", "powershell"):
        if shutil.which(exe):
            return (exe, HOOK_PS, True)
    return None


def run_hook(runner, project_dir):
    exe, hook, is_ps = runner
    env = dict(os.environ, CLAUDE_PROJECT_DIR=project_dir)
    if is_ps:
        cmd = [exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", hook]
    else:
        cmd = [exe, hook]
    # stdin=DEVNULL: o hook le stdin quando nao-tty (SessionStart JSON); pipe herdado aberto = deadlock
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
                       stdin=subprocess.DEVNULL)
    ctx = ""
    out = (p.stdout or "").strip()
    if out:
        try:
            ctx = json.loads(out).get("hookSpecificOutput", {}).get("additionalContext", "")
        except json.JSONDecodeError:
            ctx = out
    return ctx


def setup_pair(tmp):
    os.makedirs(tmp, exist_ok=True)
    work = os.path.join(tmp, "work")
    clone = os.path.join(tmp, "clone")
    # work = repo de trabalho com um commit, servido como "origin" para o clone
    subprocess.run(["git", "init", "-q", work], capture_output=True)
    for k, v in (("user.email", "t@t"), ("user.name", "t")):
        git(work, "config", k, v)
    open(os.path.join(work, "f.txt"), "w").write("v1\n")
    git(work, "add", "."); git(work, "commit", "-q", "-m", "c1")
    git(work, "branch", "-M", "main")
    subprocess.run(["git", "clone", "-q", work, clone], capture_output=True)
    for k, v in (("user.email", "t@t"), ("user.name", "t")):
        git(clone, "config", k, v)
    return work, clone


def advance_origin(work):
    open(os.path.join(work, "f.txt"), "a").write("v2\n")
    git(work, "add", "."); git(work, "commit", "-q", "-m", "c2")


def main():
    runner = find_runner()
    if not runner or not have("git"):
        print("SKIP: git ou runner (python/pwsh) ausente.", file=sys.stderr); return 0
    fails = 0
    tmp = tempfile.mkdtemp(prefix="reposync_")
    try:
        work, clone = setup_pair(tmp)

        # C3 em dia
        ctx = run_hook(runner, clone)
        ok = (ctx == "")
        print(("OK  " if ok else "FAIL") + " C3 em-dia -> silencioso"); fails += 0 if ok else 1

        # C1 limpo e atrás -> auto-atualiza
        advance_origin(work)
        git(clone, "fetch", "-q")  # garante que o ref remoto existe; o hook refaz fetch
        ctx = run_hook(runner, clone)
        ok = "AUTO-ATUALIZADO" in ctx
        print(("OK  " if ok else "FAIL") + " C1 limpo+atras -> auto-atualiza  | ctx=" + repr(ctx[:60])); fails += 0 if ok else 1
        # e de fato atualizou?
        behind = git(clone, "rev-list", "--count", "HEAD..origin/main").stdout.strip()
        ok2 = (behind == "0")
        print(("OK  " if ok2 else "FAIL") + " C1 pós: clone agora em dia (behind=0)"); fails += 0 if ok2 else 1

        # C2 sujo e atrás -> avisa, não atualiza
        advance_origin(work)
        open(os.path.join(clone, "f.txt"), "a").write("dirty-local\n")  # suja o tree
        ctx = run_hook(runner, clone)
        ok = ("NAO auto-atualizei" in ctx) and ("RASTREADAS" in ctx)
        print(("OK  " if ok else "FAIL") + " C2 modif-rastreada+atras -> avisa sem mexer  | ctx=" + repr(ctx[:70])); fails += 0 if ok else 1
        behind2 = git(clone, "rev-list", "--count", "HEAD..origin/main").stdout.strip()
        ok2 = (behind2 != "0")  # continua atrás (não mexeu)
        print(("OK  " if ok2 else "FAIL") + " C2 pós: clone NAO foi atualizado (behind>0)"); fails += 0 if ok2 else 1

        # C4 DIVERGIU (não-ff): clone com commit local próprio + origin avança → deve AVISAR "DIVERGIU"
        w4, c4 = setup_pair(os.path.join(tmp, "d4"))
        open(os.path.join(c4, "local.txt"), "w").write("commit local\n")
        git(c4, "add", "."); git(c4, "commit", "-q", "-m", "local-only")  # diverge
        advance_origin(w4)  # origin tb avança → históricos divergem
        ctx = run_hook(runner, c4)
        ok = ("DIVERGIU" in ctx) and ("NAO auto-atualizei" in ctx)
        print(("OK  " if ok else "FAIL") + " C4 divergiu(nao-ff) -> avisa DIVERGIU, sem pull  | ctx=" + repr(ctx[:70])); fails += 0 if ok else 1
        behind4 = git(c4, "rev-list", "--count", "HEAD..origin/main").stdout.strip()
        ok2 = (behind4 != "0")
        print(("OK  " if ok2 else "FAIL") + " C4 pós: clone NAO foi tocado (behind>0)"); fails += 0 if ok2 else 1

        # C5 só UNTRACKED (sem modificação rastreada) + atrás → deve AUTO-ATUALIZAR (fix do qa-critic)
        w5, c5 = setup_pair(os.path.join(tmp, "u5"))
        advance_origin(w5)
        open(os.path.join(c5, "minha-nota.txt"), "w").write("nota local untracked\n")  # untracked apenas
        ctx = run_hook(runner, c5)
        ok = "AUTO-ATUALIZADO" in ctx
        print(("OK  " if ok else "FAIL") + " C5 untracked-only+atras -> AUTO-ATUALIZA  | ctx=" + repr(ctx[:60])); fails += 0 if ok else 1
        behind5 = git(c5, "rev-list", "--count", "HEAD..origin/main").stdout.strip()
        ok2 = (behind5 == "0")
        print(("OK  " if ok2 else "FAIL") + " C5 pós: atualizou (behind=0) e preservou untracked"); fails += 0 if ok2 else 1
        ok3 = os.path.exists(os.path.join(c5, "minha-nota.txt"))
        print(("OK  " if ok3 else "FAIL") + " C5 pós: untracked local preservado"); fails += 0 if ok3 else 1

        # C6 FEATURE BRANCH em dia com o PRÓPRIO upstream (origin/feat) mas ATRÁS de origin/main.
        # É EXATAMENTE a topologia que o @{upstream} sozinho reportava "em dia" (regressão 2026-06-16,
        # sessão operou 6 commits atrás de main numa branch de teste). ADR-084: dimensão ortogonal.
        w6, c6 = setup_pair(os.path.join(tmp, "fb6"))
        git(w6, "branch", "feat")                                          # feat no origin (work fica na main)
        git(c6, "fetch", "-q")
        git(c6, "checkout", "-q", "-b", "feat", "--track", "origin/feat")  # clone na feat, em dia c/ origin/feat
        advance_origin(w6)                                                  # origin/main avança; feat NÃO
        ctx = run_hook(runner, c6)
        ok = ("ATRAS de" in ctx) and ("origin/main" in ctx)
        print(("OK  " if ok else "FAIL") + " C6 feat-em-dia-mas-atras-de-main -> AVISA baseline (NÃO silencioso)  | ctx=" + repr(ctx[:80])); fails += 0 if ok else 1
        marker6 = os.path.join(c6, ".claude", ".stale-vs-main")
        ok2 = os.path.exists(marker6)
        print(("OK  " if ok2 else "FAIL") + " C6 pós: marker .stale-vs-main escrito (route-gate repete por-turno)"); fails += 0 if ok2 else 1
        ok3 = ("origin/feat" not in ctx)  # dimensão 1 (upstream) deve ficar calada: feat em dia c/ seu remote
        print(("OK  " if ok3 else "FAIL") + " C6 pós: dimensão upstream silenciosa (sem ruído sobre origin/feat)"); fails += 0 if ok3 else 1

        # C7 a feature branch é atualizada (incorpora origin/main) -> em dia vs baseline -> LIMPA marker, silencioso.
        git(c6, "merge", "-q", "--no-edit", "origin/main")
        ctx = run_hook(runner, c6)
        ok = (ctx == "")
        print(("OK  " if ok else "FAIL") + " C7 feat-atualizada -> silencioso (baseline em dia)  | ctx=" + repr(ctx[:60])); fails += 0 if ok else 1
        ok2 = not os.path.exists(marker6)
        print(("OK  " if ok2 else "FAIL") + " C7 pós: marker .stale-vs-main REMOVIDO (resolvido)"); fails += 0 if ok2 else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("-" * 40)
    print("RESULTADO:", "PASS" if not fails else f"FAIL ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
