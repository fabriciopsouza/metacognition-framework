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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, ".claude", "hooks", "check-repo-sync.ps1")


def have(exe):
    return shutil.which(exe) is not None


def git(cwd, *args):
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)


def run_hook(pwsh, project_dir):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=project_dir)
    p = subprocess.run([pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", HOOK],
                       capture_output=True, text=True, env=env)
    ctx = ""
    out = p.stdout.strip()
    if out:
        try:
            ctx = json.loads(out).get("hookSpecificOutput", {}).get("additionalContext", "")
        except json.JSONDecodeError:
            ctx = out
    return ctx


def setup_pair(tmp):
    origin = os.path.join(tmp, "origin.git")
    work = os.path.join(tmp, "work")
    clone = os.path.join(tmp, "clone")
    # origin = repo de trabalho com um commit, depois servido como remoto
    git(tmp, "init", "-q", work) if False else None
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
    if not (have("git") and (have("pwsh") or have("powershell"))):
        print("SKIP: git ou pwsh ausente.", file=sys.stderr); return 0
    pwsh = shutil.which("pwsh") or shutil.which("powershell")
    fails = 0
    tmp = tempfile.mkdtemp(prefix="reposync_")
    try:
        work, clone = setup_pair(tmp)

        # C3 em dia
        ctx = run_hook(pwsh, clone)
        ok = (ctx == "")
        print(("OK  " if ok else "FAIL") + " C3 em-dia -> silencioso"); fails += 0 if ok else 1

        # C1 limpo e atrás -> auto-atualiza
        advance_origin(work)
        git(clone, "fetch", "-q")  # garante que o ref remoto existe; o hook refaz fetch
        ctx = run_hook(pwsh, clone)
        ok = "AUTO-ATUALIZADO" in ctx
        print(("OK  " if ok else "FAIL") + " C1 limpo+atras -> auto-atualiza  | ctx=" + repr(ctx[:60])); fails += 0 if ok else 1
        # e de fato atualizou?
        behind = git(clone, "rev-list", "--count", "HEAD..origin/main").stdout.strip()
        ok2 = (behind == "0")
        print(("OK  " if ok2 else "FAIL") + " C1 pós: clone agora em dia (behind=0)"); fails += 0 if ok2 else 1

        # C2 sujo e atrás -> avisa, não atualiza
        advance_origin(work)
        open(os.path.join(clone, "f.txt"), "a").write("dirty-local\n")  # suja o tree
        ctx = run_hook(pwsh, clone)
        ok = ("NAO auto-atualizei" in ctx) and ("SUJO" in ctx)
        print(("OK  " if ok else "FAIL") + " C2 sujo+atras -> avisa sem mexer  | ctx=" + repr(ctx[:70])); fails += 0 if ok else 1
        behind2 = git(clone, "rev-list", "--count", "HEAD..origin/main").stdout.strip()
        ok2 = (behind2 != "0")  # continua atrás (não mexeu)
        print(("OK  " if ok2 else "FAIL") + " C2 pós: clone NAO foi atualizado (behind>0)"); fails += 0 if ok2 else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("-" * 40)
    print("RESULTADO:", "PASS" if not fails else f"FAIL ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
