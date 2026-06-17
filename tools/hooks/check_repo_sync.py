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


STALE_MARKER = os.path.join(".claude", ".stale-vs-main")
STALE_ACK = os.path.join(".claude", ".stale-vs-main.ack")


def resolve_baseline(cwd):
    """Branch de integracao (ADR-084) de forma AGNOSTICA (ADR-020): a default branch do remoto
    via origin/HEAD, com fallback origin/main -> origin/master. Hardcodar 'main' feriria o nucleo
    agnostico. Retorna '' se indeterminada (sem remoto) -> caller degrada silencioso."""
    ref, rc = git(cwd, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if rc == 0 and ref.startswith("refs/remotes/"):
        return ref[len("refs/remotes/"):]
    for cand in ("origin/main", "origin/master"):
        _, rc = git(cwd, "rev-parse", "--verify", "--quiet", cand)
        if rc == 0:
            return cand
    return ""


def _clear_stale(cwd):
    for f in (os.path.join(cwd, STALE_MARKER), os.path.join(cwd, STALE_ACK)):
        try:
            os.remove(f)
        except OSError:
            pass


def baseline_staleness(cwd, sid, upstream):
    """Dimensao ORTOGONAL ao @{upstream} (ADR-084). O gap do method-audit: uma feature branch pode
    estar 0 atras do PROPRIO upstream (origin/feat) e ainda assim N atras da branch de integracao
    (origin/main) = retrato congelado do framework. Mede HEAD..baseline; escreve/limpa o marker
    persistente (.stale-vs-main) que o route-gate repete por-turno ate resolver/reconhecer.
    Retorna o texto de aviso ('' se em dia/indeterminado). Roda DEPOIS do auto-pull (HEAD ja movido)."""
    marker = os.path.join(cwd, STALE_MARKER)
    base = resolve_baseline(cwd)
    if not base:
        return ""
    if base == upstream:
        # Branch de integracao E o proprio upstream (ex.: estou NA main) -> a dimensao 1 ja cobre.
        # Mudanca cirurgica: nada de marker aqui (preserva C1-C5). Limpa marker orfao de outra branch.
        _clear_stale(cwd)
        return ""
    cnt, rc = git(cwd, "rev-list", "--count", f"HEAD..{base}")
    if rc != 0:
        return ""
    behind_base = int(cnt or "0")
    if behind_base == 0:
        _clear_stale(cwd)  # resolvido (branch atualizada) -> limpa marker E ack
        return ""
    base_sha, _ = git(cwd, "rev-parse", "--short", base)
    cur, _ = git(cwd, "rev-parse", "--abbrev-ref", "HEAD")
    try:
        os.makedirs(os.path.join(cwd, ".claude"), exist_ok=True)
        with open(marker, "w", encoding="utf-8") as f:
            f.write(f"behind={behind_base}\nbase={base}\nbase_sha={base_sha}\nsession={sid or ''}\n")
    except OSError:
        pass
    return (f"⚠️ Voce esta {behind_base} commit(s) ATRAS de `{base}` (branch `{cur}`). "
            f"O framework MOVEU desde que esta branch saiu: voce le um RETRATO CONGELADO. "
            f"NAO afirme estado/versao nem edite codigo do nucleo antes de `git rebase {base}` "
            f"(ou merge). Persistido em `.claude/.stale-vs-main` -> o route-gate REPETE por-turno "
            f"ate (a) atualizar a branch ou (b) reconhecer: "
            f"`git rev-parse --short {base} > .claude/.stale-vs-main.ack`.")


def sync_upstream(cwd, upstream):
    """Dimensao 1 (ADR-019/060): sincronia vs o PROPRIO upstream da branch, com auto-pull --ff-only
    quando seguro. Retorna o corpo do aviso ('' se em dia). NAO emite/exit aqui (composicao no main)."""
    counts, rc = git(cwd, "rev-list", "--left-right", "--count", f"{upstream}...HEAD")
    if rc != 0 or not counts:
        return ""
    parts = counts.split()
    behind = int(parts[0])
    ahead = int(parts[1]) if len(parts) > 1 else 0
    if behind == 0:
        return ""

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
            return (f"✅ Repo estava {behind} commit(s) atras de `{upstream}` e foi AUTO-ATUALIZADO "
                    f"(fast-forward, sem modificacoes rastreadas). Agora em dia. Reconcilie WIP "
                    f"sobre o estado novo.")
        return (f"⚠️ Tentei auto-atualizar (estava {behind} atras de `{upstream}`) mas "
                f"`pull --ff-only` NAO concluiu (rc={pull_rc}). Rode `git pull` manual e verifique "
                f"ANTES de reconciliar WIP.")
    if not is_clean:
        motivo, acao = "working tree com modificacoes RASTREADAS", "commit ou stash, depois `git pull`"
    else:
        motivo, acao = "historico DIVERGIU (nao-fast-forward)", f"rebase/merge manual de `{upstream}`"
    return (f"⚠️ Repo esta {behind} commit(s) atras de `{upstream}` (e {ahead} a frente). "
            f"NAO auto-atualizei: {motivo}. **Antes de reconciliar WIP / afirmar estado:** {acao}. "
            f"Operar agora = ler retrato congelado.")


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

        # Dimensao 1: sincronia vs o proprio upstream (pode AUTO-PULL e mover HEAD).
        upstream_msg = sync_upstream(cwd, upstream)
        # Dimensao 2 (ORTOGONAL, ADR-084): defasagem vs a branch de integracao (origin/HEAD),
        # medida DEPOIS do auto-pull. Pega o caso feature-branch-em-dia-mas-atras-do-main.
        baseline_msg = baseline_staleness(cwd, sid, upstream)

        bodies = [m for m in (upstream_msg, baseline_msg) if m]
        if not bodies:
            emit("")  # em dia nas duas dimensoes -> silencioso
        emit("# Repo sync (ADR-019/060/084)\n" + "\n\n".join(bodies))
    except Exception as e:
        sys.stderr.write(f"[check_repo_sync] warning (nao-bloqueante): {e}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
