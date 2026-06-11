#!/usr/bin/env python3
"""handoff.py — gerador DETERMINISTICO do Pacote de handoff cross-sessao (P14 / ADR-012) a partir do
ESTADO DO REPO, com sugestao de modelo para a proxima sessao (ADR-076).

PORQUE (gap real, file-first 2026-06-11): o Pacote P14 existe como TEMPLATE
(`docs/specs/_template-digest/digest.md`) mas era PREENCHIDO A MAO pelo agente (prosa) e so quando o
discovery declarava "alimenta outra sessao" (ADR-012 passo 6e) — ou seja, NAO emitido por padrao em
auto-execucao/automacao, e sem sugestao de modelo. Este gerador torna o handoff **deterministico e
universal**: mesmo comando em auto-exec, automacao (cron) e passagem cross-model. Mecaniza o
"Gap 8 — handoff improviso" que o proprio ADR-012 admite (regua §0: prosa->mecanismo do template que ja existe).

O QUE E DETERMINISTICO (lido do repo): versao (CHANGELOG), branch/commit/PR (git/gh), nao-pushado +
nao-commitado (git), pendencias (history.md ## Em aberto + ADRs Proposto), proximo passo (ultimo
checkpoint), 5 arquivos recentes (git log), e a SUGESTAO DE MODELO (regra papel+risco). O unico slot
de julgamento (o que exatamente a proxima sessao produz) e DERIVADO do "Proximo passo: <tarefa+criterio>"
do checkpoint — esqueleto pronto, nao prosa do zero.

Uso:
  python tools/handoff.py [--next-role <papel>] [--risk low|high|regulated|irreversible]
                          [--author opus|sonnet|haiku|fable] [--write [path]]
  (sem args: infere o papel do 'Proximo passo' do checkpoint; imprime o pacote pronto-para-colar)
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# IDs reais (ambiente 2026-06): Opus 4.8, Sonnet 4.6, Haiku 4.5, Fable 5.
MODEL_ID = {
    "opus": "claude-opus-4-8",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5-20251001",
    "fable": "claude-fable-5",
}


def _git(*args):
    try:
        r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def _read(rel):
    try:
        return open(os.path.join(ROOT, rel), encoding="utf-8-sig").read()
    except Exception:
        return ""


def repo_state():
    chg = _read("CHANGELOG.md")
    m = re.search(r"(?m)^##\s*\[(\d+\.\d+\.\d+)\]", chg)
    version = m.group(1) if m else "?"
    branch = _git("rev-parse", "--abbrev-ref", "HEAD") or "?"
    commit = _git("rev-parse", "--short", "HEAD") or "?"
    origin = _git("remote", "get-url", "origin") or "(sem origin)"
    unpushed = _git("rev-list", "--count", "@{upstream}..HEAD")
    unpushed = unpushed if unpushed.isdigit() else "?"
    uncommitted = len([l for l in _git("status", "--porcelain").splitlines() if l.strip()])
    recent = [l for l in _git("log", "-5", "--name-only", "--pretty=format:").splitlines() if l.strip()]
    recent = list(dict.fromkeys(recent))[:5]  # unicos, ordem preservada
    return {"version": version, "branch": branch, "commit": commit, "origin": origin,
            "unpushed": unpushed, "uncommitted": uncommitted, "recent": recent}


def latest_checkpoint_field(field):
    """Extrai um campo (ex. 'Próximo passo') do checkpoint datado mais recente do history.md."""
    hist = _read("history.md")
    m = re.search(r"(?m)^##\s+\d{4}-\d{2}-\d{2}.*$", hist)
    if not m:
        return ""
    nxt = re.search(r"(?m)^##\s+\d{4}-\d{2}-\d{2}", hist[m.end():])
    block = hist[m.end(): m.end() + nxt.start()] if nxt else hist[m.end():]
    fm = re.search(rf"(?im)^\s*{re.escape(field)}\s*:?\s*(.+)$", block)
    return fm.group(1).strip() if fm else ""


def em_aberto():
    hist = _read("history.md")
    m = re.search(r"(?im)^##\s+Em aberto\b", hist)
    if not m:
        return []
    tail = hist[m.end():]
    nxt = re.search(r"(?m)^##\s+(?!Em aberto)", tail)
    section = tail[:nxt.start()] if nxt else tail
    items = re.findall(r"(?m)^\s*[-*]\s+(.+)$", section)
    return [re.sub(r"\s+", " ", i).strip()[:160] for i in items[:6]]


def proposed_adrs():
    out = []
    adir = os.path.join(ROOT, "docs", "adr")
    if os.path.isdir(adir):
        for fn in sorted(os.listdir(adir)):
            if fn.endswith(".md") and not fn.startswith("000"):
                txt = _read(os.path.join("docs", "adr", fn))
                if re.search(r"(?im)^\s*-?\s*Status:\s*(?:\*\*)?\s*proposto", txt):
                    out.append(fn)
    return out


def infer_role(proximo):
    p = (proximo or "").lower()
    table = [
        (("qa", "critic", "review", "revis", "verif", "adversar"), "qa-critic"),
        (("handoff", "cross-ia", "cross-ai", "gemini"), "cross-ai"),  # sinal forte, antes de architect
        (("architect", "arquitet", "design", "decis"), "architect"),
        (("discovery", "pesquis", "research", "spec", "elicit"), "discovery"),
        (("docops", "changelog", "release", "tag"), "docops"),
        (("developer", "implement", "codigo", "código", "script", "canario", "canário"), "developer"),
    ]
    for keys, role in table:
        if any(k in p for k in keys):
            return role
    return "developer"


def suggest_model(next_role, risk, author):
    """Regra DETERMINISTICA papel+risco -> modelo (ADR-076; heterogeneidade ADR-018)."""
    role = (next_role or "").lower()
    if risk in ("high", "regulated", "irreversible"):
        return "opus", "alto-risco/regulado/irreversivel -> mais capaz (Opus) + gate humano (HITL)"
    if any(k in role for k in ("qa", "critic", "review", "revis", "verif")):
        het = "sonnet" if author == "opus" else "opus"
        return het, f"qa/review -> HETEROGENEO (autor={author}; ADR-018 anti-vies de auto-aprovacao)"
    if any(k in role for k in ("cross-ai", "cross-ia", "handoff", "gemini")):
        return "opus", "cross-IA/handoff de coordenacao -> mais capaz (Opus)"
    if any(k in role for k in ("architect", "arquitet", "discovery", "design", "spec", "plan")):
        return "opus", "architect/discovery/spec -> mais capaz (Opus)"
    if any(k in role for k in ("docops", "document", "mechan", "bulk", "format", "lint", "rename", "migrate")):
        return "sonnet", "mecanico/docops/bulk -> custo-eficiente (Sonnet)"
    return "sonnet", "default -> Sonnet (equilibrio capacidade/custo)"


def pr_info(branch):
    try:
        r = subprocess.run(["gh", "pr", "view", branch, "--json", "number,url,state"],
                           cwd=ROOT, capture_output=True, text=True, timeout=15)
        if r.returncode == 0 and r.stdout.strip():
            import json
            d = json.loads(r.stdout)
            return f"PR #{d.get('number')} ({d.get('state')}) {d.get('url')}"
    except Exception:
        pass
    return "(sem PR aberto para esta branch)"


def build(next_role, risk, author, ts="<timestamp>"):
    st = repo_state()
    proximo = latest_checkpoint_field("Próximo passo") or latest_checkpoint_field("Proximo passo")
    role = next_role or infer_role(proximo)
    fam, why = suggest_model(role, risk, author)
    model_id = MODEL_ID[fam]
    aberto = em_aberto()
    props = proposed_adrs()
    pr = pr_info(st["branch"])

    L = []
    L.append(f"# Handoff — v{st['version']} · {ts} · papel-alvo: {role}")
    L.append("")
    L.append("> Pacote P14 (ADR-012) gerado DETERMINISTICAMENTE do estado do repo por `tools/handoff.py` (ADR-076).")
    L.append("> Teste binario (P14): a proxima sessao comeca SEM perguntar nada de volta?")
    L.append("")
    L.append("## [modelo sugerido] (regra papel+risco — ADR-076)")
    L.append(f"- **Proxima sessao: `{model_id}`** ({fam}). Motivo: {why}.")
    L.append("")
    L.append("## [P14] Artefato consumivel — com versao")
    L.append(f"- Repo na versao **v{st['version']}** (topo do CHANGELOG). Branch `{st['branch']}` @ `{st['commit']}`.")
    L.append("")
    L.append("## [P14] Localizacao")
    L.append(f"- origin: {st['origin']}")
    L.append(f"- branch/commit: `{st['branch']}` @ `{st['commit']}` · {pr}")
    L.append("")
    L.append("## [P14] Acesso")
    naoprot = []
    if st["unpushed"] == "?":
        # achado ALTO do qa-critic: '?' = sem upstream -> NAO afirmar 'nada pendente' (P14 Acesso e
        # safety-critical; pode haver commits locais nao protegidos).
        naoprot.append("estado de push DESCONHECIDO (branch sem upstream — pode haver commits locais nao protegidos)")
    elif st["unpushed"] != "0":
        naoprot.append(f"{st['unpushed']} commit(s) NAO-pushado(s)")
    if st["uncommitted"]:
        naoprot.append(f"{st['uncommitted']} arquivo(s) nao-commitado(s)")
    L.append(f"- Nao-protegido (recovery = conta GitHub): {', '.join(naoprot) if naoprot else 'nada pendente (tudo pushado/commitado)'}")
    L.append("")
    L.append("## [P14] Prompt pronto-para-colar")
    L.append(f"- **Papel:** {role} · **Modelo:** `{model_id}`")
    L.append(f"- **Objetivo (do 'Proximo passo'):** {proximo or '<definir: nao havia Proximo passo no checkpoint>'}")
    L.append("- **Produz/decide:** execute o objetivo acima ate o criterio de aceite citado; rode `tools/run_canaries.py` antes de fechar.")
    L.append("")
    L.append("## [P14] Pendencias e premissas herdadas")
    for it in aberto:
        L.append(f"- (em aberto) {it}")
    for p in props:
        L.append(f"- (ADR Proposto pendente) {p}")
    if not aberto and not props:
        L.append("- nenhuma pendencia explicita em history.md `## Em aberto` nem ADR Proposto.")
    L.append("")
    L.append("## Extensoes (ADR-016 — evita re-derivar)")
    L.append("- **5 arquivos mais recentes:**")
    for i, f in enumerate(st["recent"], 1):
        L.append(f"  {i}. {f}")
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser(description="Gerador deterministico do Pacote de handoff P14 (ADR-076).")
    ap.add_argument("--next-role", default="", help="papel da proxima sessao (default: inferido do checkpoint)")
    ap.add_argument("--risk", default="low", choices=["low", "high", "regulated", "irreversible"])
    ap.add_argument("--author", default="opus", choices=list(MODEL_ID), help="familia do modelo autor do bloco")
    ap.add_argument("--write", nargs="?", const="docs/_private/handoffs", default=None,
                    help="grava o pacote (default dir docs/_private/handoffs/) em vez de so imprimir")
    a = ap.parse_args(argv[1:])

    # timestamp DETERMINISTICO do estado do repo: data do commit HEAD (nao Date.now).
    ts = _git("show", "-s", "--format=%cI", "HEAD") or "<sem-data>"
    pkg = build(a.next_role, a.risk, a.author, ts=ts)
    try:
        if a.write is not None:
            d = os.path.join(ROOT, a.write)
            os.makedirs(d, exist_ok=True)
            out = os.path.join(d, "handoff-latest.md")
            with open(out, "w", encoding="utf-8") as f:
                f.write(pkg)
            print(f"[handoff] gravado: {os.path.relpath(out, ROOT)}")
        print(pkg)
    except BrokenPipeError:  # saida truncada por pipe (head/Select-Object) — nao e erro
        try:
            sys.stdout.close()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
