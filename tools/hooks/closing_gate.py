#!/usr/bin/env python3
"""closing_gate.py — hook `Stop`: ENCERRAMENTO DETERMINISTICO (ADR-101).

O BURACO QUE ISTO FECHA (auditoria do dono, 2026-08-07). O framework tinha 17 gates e TODOS
disparavam no comeco ou no meio: SessionStart, UserPromptSubmit, PreToolUse, PostToolUse,
PreCompact. **Nenhum no fim.** Consequencia relatada, item por item:
  - "encerramentos parciais, sem commit pr e merge, mesmo ja solicitados explicitamente"
  - "a memoria e melhoria (relatorio final sessao) tb nao tem sido deterministico"
  - "relatorios cross ia nao sao registrados ha muito tempo"
  - "documentacao continua ... so ocorre se provocado"
Os mecanismos p/ tudo isso JA EXISTIAM (consistency-gate, dev-dogfood-gate, trabalhos.py,
qa_evidence.py, correlated.py). O que faltava era **alguem que os chamasse na hora certa** —
e a hora certa e o fim. Regua §0, porta (c): destrava eval de gates que existem e nunca rodam.

MECANISMO: no Stop, mede o estado REAL do projeto (git + arquivos), monta a lista de pendencias
e BLOQUEIA a parada uma unica vez, devolvendo a lista pro agente terminar o servico. Nao infere
intencao do usuario (fragil); le estado (deterministico).

ANTI-LOOP (obrigatorio): honra `stop_hook_active` — se o proprio bloqueio ja reentrou, LIBERA.
Alem disso marca por session_id: bloqueia no maximo 1x por sessao. Nunca trava o dono num ciclo.

SOBERANIA: `.claude/session.lock` (projeto) ou `~/.claude/session.lock` (global) silenciam.
`.claude/.closing.ack` reconhece as pendencias e libera ate a proxima mudanca.

FAIL-OPEN: qualquer erro inesperado -> permite parar. Um gate de saida com bug nao pode
sequestrar a sessao do dono.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _project import project_root, read_payload  # noqa: E402

# Arquivos que podem viver na raiz. Qualquer outro .md novo la e poluicao (relato do dono:
# "handoffs no root, alem de muita documentacao ali, poluindo e sujando o repo").
ROOT_ALLOW = {
    "AGENT-FRAMEWORK.md", "AGENTS.md", "CAPABILITIES.md", "CHANGELOG.md", "CLAUDE.md",
    "LICENSE", "LIMITS.md", "NOTICE", "README.md", "REPO.md", "SECURITY.md", "TELEMETRY.md",
    "history.md", "capabilities.json", "bootstrap.py", "bootstrap.ps1", "bootstrap.sh",
    ".gitignore", ".mailmap", ".env", ".repo-identity.json",
}
ROOT_DOC_EXT = (".md", ".txt")
HANDOFF_HINT = ("handoff", "relatorio", "report", "checkpoint", "digest", "resumo")


def allow():
    sys.exit(0)


def block(reason):
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(0)


def git(root, *args, timeout=12):
    # [auto-revisao 2026-08-08] Era 30s POR CHAMADA, mas o gate faz ate 5 chamadas git (is_git,
    # porcelain, upstream, rev-list, git_touched do correlated) e o manifesto da 60s ao hook: no pior
    # caso o orcamento estourava e o harness matava o hook. Morrer por timeout falha ABERTO — o
    # sintoma seria o gate sumir em SILENCIO em repo grande/lento, que e falso-OK, pior que bloquear.
    # 12s x 5 = 60s no limite; na pratica cada chamada e local e responde em ms.
    try:
        r = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def is_git(root):
    return git(root, "rev-parse", "--is-inside-work-tree") == "true"


def git_raw(root, *args, timeout=12):
    """Como git(), mas SEM strip(). Obrigatorio p/ --porcelain: a coluna 1 e significativa
    (' M path' = modificado nao-staged) e um strip() global comeria o espaco da PRIMEIRA
    linha, deslocando o parse em 1 char. Bug pego pelo proprio teste do gate (2026-08-07)."""
    try:
        r = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def porcelain(root):
    out = git_raw(root, "status", "--porcelain", "-uall")
    tracked, untracked = [], []
    for line in out.splitlines():
        if len(line) < 4:
            continue
        code, path = line[:2], line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        (untracked if code == "??" else tracked).append(path)
    return tracked, untracked


def unpushed(root):
    up = git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    if not up:
        return 0, ""
    cnt = git(root, "rev-list", "--count", f"{up}..HEAD")
    try:
        return int(cnt or "0"), up
    except ValueError:
        return 0, up


def root_pollution(root, untracked):
    """Doc novo solto na raiz — especialmente handoff/relatorio, que tem lar proprio."""
    bad = []
    for p in untracked:
        norm = p.replace("\\", "/")
        if "/" in norm:
            continue
        base = os.path.basename(norm)
        if base in ROOT_ALLOW:
            continue
        if base.lower().endswith(ROOT_DOC_EXT):
            hint = " (handoff/relatorio -> docs/_private/handoffs/)" \
                if any(h in base.lower() for h in HANDOFF_HINT) else ""
            bad.append(base + hint)
    return bad


def correlated_violations(root):
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))))
        import correlated  # noqa: PLC0415
        groups, _skip = correlated.load_manifest(root)
        if not groups:
            return []
        return correlated.check(groups, correlated.git_touched(root))
    except Exception:  # noqa: BLE001 — nunca derruba o gate de saida
        return []


def checkpoint_today(root):
    """history.md tem checkpoint com a data de hoje? (documentacao continua, ADR-016/021)"""
    import datetime
    hist = os.path.join(root, "history.md")
    if not os.path.isfile(hist):
        return None  # projeto sem history -> nao cobra
    today = datetime.date.today().isoformat()
    try:
        with open(hist, encoding="utf-8", errors="replace") as f:
            head = f.read(60000)
    except OSError:
        return None
    return today in head


def build_pendings(root):
    pend = []
    tracked, untracked = porcelain(root)
    if tracked:
        sample = ", ".join(tracked[:6]) + (" ..." if len(tracked) > 6 else "")
        pend.append(f"**{len(tracked)} arquivo(s) rastreado(s) modificados e NAO commitados** "
                    f"({sample}). Commit + push + PR — encerramento parcial e o modo de falha "
                    f"que o dono relatou.")
    ahead, up = unpushed(root)
    if ahead:
        pend.append(f"**{ahead} commit(s) locais nao enviados** (a frente de `{up}`). "
                    f"Push e abra/atualize o PR.")
    viols = correlated_violations(root)
    for v in viols:
        pend.append(f"**Correlato nao atualizado** (grupo `{v['id']}`): tocou "
                    f"{v['touched']} mas NAO tocou {v['missing']}. "
                    f"{v['note'] or 'Estes artefatos mudam juntos — tem que ser tudo.'}")
    bad = root_pollution(root, untracked)
    if bad:
        pend.append(f"**Raiz poluida** — arquivo(s) novo(s) solto(s) na raiz: {', '.join(bad[:8])}. "
                    f"Mova p/ o diretorio proprio antes de fechar.")
    if (tracked or ahead) and checkpoint_today(root) is False:
        pend.append("**Sem checkpoint de hoje no `history.md`** — a sessao mudou o repo e nao "
                    "deixou rastro. Rode `/checkpoint` (ADR-016/021).")
    if tracked or ahead:
        pend.append("**Registre o que fica pendente**: `python tools/trabalhos.py registrar "
                    "--slug <s> --nome ... --objetivo ... --pendente ... --proximo ...` "
                    "(ADR-100 — e o que faz o handoff sobreviver a sessao).")
    return pend


def main():
    try:
        payload = read_payload()
        if payload.get("stop_hook_active"):  # ANTI-LOOP: ja reentrou -> libera
            allow()
        root = project_root(payload)
        session_id = str(payload.get("session_id") or "")

        home = os.path.expanduser("~")
        if os.path.isfile(os.path.join(root, ".claude", "session.lock")) or \
           os.path.isfile(os.path.join(home, ".claude", "session.lock")) or \
           os.path.isfile(os.path.join(root, ".claude", ".closing.ack")):
            allow()

        if not is_git(root):
            allow()

        state = os.path.join(root, ".claude", ".closing-state")
        marker = os.path.join(state, "".join(
            c if c.isalnum() or c in "_.-" else "_" for c in session_id)) if session_id else ""
        if marker and os.path.isfile(marker):  # no maximo 1 bloqueio por sessao
            allow()

        pend = build_pendings(root)
        if not pend:
            allow()

        if marker:
            try:
                os.makedirs(state, exist_ok=True)
                with open(marker, "w", encoding="utf-8") as f:
                    f.write("blocked")
            except OSError:
                pass

        items = "\n".join(f"{i}. {p}" for i, p in enumerate(pend, 1))
        block(
            "# [closing-gate ADR-101] Encerramento INCOMPLETO — nao pare aqui\n\n"
            "O estado do repo diz que este bloco nao fechou. Pendencias medidas (nao inferidas):\n\n"
            f"{items}\n\n"
            "Se o dono pediu o trabalho explicitamente, **termine agora** — confirmar entendimento "
            "e seguir e o contrato; parar no fim, quando ele ja saiu, nao e.\n"
            "Se alguma pendencia nao se aplica, diga POR QUE e siga: "
            "`echo ok > .claude/.closing.ack` libera este projeto. "
            "Este gate bloqueia no maximo 1x por sessao."
        )
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 — fail-open: bug no gate nao sequestra a sessao
        sys.stderr.write(f"[closing-gate] warning (nao-bloqueante): {e}\n")
        allow()


if __name__ == "__main__":
    main()
