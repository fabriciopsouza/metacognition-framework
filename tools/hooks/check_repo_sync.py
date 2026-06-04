#!/usr/bin/env python3
"""check_repo_sync.py - Hook SessionStart (porte Python do check-repo-sync.ps1) - ADR-019 + ADR-060.

PORQUE PYTHON: na maquina 9TRP7H4 o Kaspersky AAC bloqueia o .ps1 (regra "O PowerShell executa
codigo ofuscado") porque powershell.exe pare git+rede. Este porte roda como python.exe (process tree
sem powershell.exe) -> escapa daquela regra (ADR-060). Determinístico (roda na engine, nao depende do
agente). Cadeia de fallback: o launcher chama ESTE; se python falhar (ausente/bloqueado), cai no .ps1.

Logica IDENTICA ao .ps1 (paridade): fetch sempre (read-only); AUTO-PULL so se tree LIMPO (rastreado;
untracked nao bloqueia) E fast-forward -> pull --ff-only; senao AVISA sem mexer. Falha SOFT (exit 0).

Saida: JSON do protocolo SessionStart {hookSpecificOutput:{hookEventName,additionalContext}}.
Uso: python tools/hooks/check_repo_sync.py   (sempre exit 0)
"""
import json
import os
import subprocess
import sys


def emit(ctx):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                              "additionalContext": ctx}}, ensure_ascii=True))
    sys.exit(0)


def git(cwd, *args):
    """git -C <cwd> ...; retorna stdout.strip() ou '' (erros engolidos - fail-soft)."""
    try:
        r = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        return r.stdout.strip(), r.returncode
    except Exception:
        return "", 1


def session_id_from_stdin():
    """SessionStart passa {session_id,...} no stdin. tty-guard: nao bloqueia em run manual."""
    try:
        if sys.stdin and not sys.stdin.isatty():
            raw = sys.stdin.read()
            if raw and raw.strip():
                return str(json.loads(raw).get("session_id") or "")
    except Exception:
        pass
    return ""


def stamp_liveness(cwd, key, session_id):
    """Prova de liveness (ADR-060/061): grava .claude/.hooklive/<key>=<session_id> (ou epoch se
    sem session_id). O route-gate (nao-bloqueavel) compara com a sessao atual e DECLARA se ausente
    -> sem falha silenciosa. Local, NAO versionado."""
    try:
        import time
        d = os.path.join(cwd, ".claude", ".hooklive")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, key), "w", encoding="utf-8") as f:
            f.write(session_id or f"epoch:{int(time.time())}")
    except Exception:
        pass


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sid = session_id_from_stdin()
    try:
        pd = os.environ.get("CLAUDE_PROJECT_DIR")
        cwd = pd if (pd and os.path.isdir(pd)) else os.getcwd()
        stamp_liveness(cwd, "check-repo-sync", sid)  # ADR-061: carimba ANTES de qualquer saida
                                                     # antecipada (carimbo = "o hook executou").

        inside, _ = git(cwd, "rev-parse", "--is-inside-work-tree")
        if inside != "true":
            emit("")

        upstream, rc = git(cwd, "rev-parse", "--abbrev-ref", "@{upstream}")
        if rc != 0 or not upstream:
            upstream = "origin/main"

        git(cwd, "fetch", "--quiet")  # sempre (read-only, seguro)

        counts, rc = git(cwd, "rev-list", "--left-right", "--count", f"{upstream}...HEAD")
        if rc != 0 or not counts:
            emit("")
        parts = counts.split()
        behind = int(parts[0])
        ahead = int(parts[1]) if len(parts) > 1 else 0

        if behind == 0:
            emit("")  # em dia -> silencioso

        # Esta atras. Seguro auto-atualizar? SEM modificacoes RASTREADAS (untracked nao bloqueia -
        # --ff-only e a trava final) E fast-forward (HEAD ancestral do upstream).
        dirty, _ = git(cwd, "status", "--porcelain", "--untracked-files=no")
        is_clean = (dirty == "")
        ff_possible = False
        if is_clean:
            _, anc_rc = git(cwd, "merge-base", "--is-ancestor", "HEAD", upstream)
            ff_possible = (anc_rc == 0)

        if is_clean and ff_possible:
            _, pull_rc = git(cwd, "pull", "--ff-only", "--quiet")
            new_behind, _ = git(cwd, "rev-list", "--count", f"HEAD..{upstream}")
            if pull_rc == 0 and new_behind == "0":
                emit(f"# Repo sync (ADR-019/060)\n✅ Repo estava {behind} commit(s) atras de "
                     f"`{upstream}` e foi AUTO-ATUALIZADO (fast-forward, sem modificacoes rastreadas). "
                     f"Agora em dia. Reconcilie WIP sobre o estado novo.")
            else:
                emit(f"# Repo sync (ADR-019/060)\n⚠️ Tentei auto-atualizar (estava {behind} "
                     f"atras de `{upstream}`) mas `pull --ff-only` NAO concluiu (rc={pull_rc}). "
                     f"Rode `git pull` manual e verifique ANTES de reconciliar WIP.")
        else:
            if not is_clean:
                motivo, acao = "working tree com modificacoes RASTREADAS", "commit ou stash, depois `git pull`"
            else:
                motivo, acao = "historico DIVERGIU (nao-fast-forward)", f"rebase/merge manual de `{upstream}`"
            emit(f"# Repo sync (ADR-019/060)\n⚠️ Repo esta {behind} commit(s) atras de "
                 f"`{upstream}` (e {ahead} a frente). NAO auto-atualizei: {motivo}. **Antes de "
                 f"reconciliar WIP / afirmar estado:** {acao}. Operar agora = ler retrato congelado.")
    except Exception as e:
        sys.stderr.write(f"[check_repo_sync] warning (nao-bloqueante): {e}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
