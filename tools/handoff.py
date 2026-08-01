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
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Politica de modelo = DADO, nao codigo (ADR-078): tools/model-policy.json e a fonte unica
# (papel+risco -> tier -> model-id). MODEL_ID mantido como alias derivado (compat ADR-076).
POLICY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model-policy.json")
with open(POLICY_PATH, encoding="utf-8") as _f:
    POLICY = json.load(_f)
MODEL_ID = dict(POLICY["model_ids"])


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


def _unavailable():
    """Indisponibilidade SITUACIONAL declarada (nunca sondada — determinismo): env
    FRAMEWORK_MODELS_UNAVAILABLE=fam1,fam2. Permanente = remover de model_ids no policy."""
    raw = os.environ.get("FRAMEWORK_MODELS_UNAVAILABLE", "")
    return {x.strip().lower() for x in raw.split(",") if x.strip()}


def _available(fam):
    return fam in MODEL_ID and fam not in _unavailable()


def _tier_model(tier):
    """Resolve tier -> (familia, nota-de-fallback) caminhando a chain e pulando indisponiveis.
    Chain esgotada -> ValueError declarado (nunca escolha silenciosa)."""
    chain = POLICY["tiers"][tier]["chain"]
    for i, fam in enumerate(chain):
        if _available(fam):
            note = "" if i == 0 else f" [fallback: {'/'.join(chain[:i])} indisponivel -> {fam}]"
            return fam, note
    raise ValueError(f"tier '{tier}' esgotado: chain {chain} toda indisponivel "
                     f"(FRAMEWORK_MODELS_UNAVAILABLE={','.join(sorted(_unavailable())) or '-'})")


def _heterogeneous(author):
    """Degrau 2 da escada (ADR-078/018): modelo DIFERENTE do autor, ordem de preferencia vinda da
    policy (autor tier-alto -> balanced primeiro; senao -> max primeiro). Pula indisponiveis;
    esgotado -> degrau 3 (mesmo modelo, fresh, DECLARADO)."""
    pref = POLICY["heterogeneous_preference"]
    tiers = pref["order_if_high"] if author in pref["high_authors"] else pref["order_otherwise"]
    seen = []
    for tier in tiers:
        for fam in POLICY["tiers"][tier]["chain"]:
            if fam not in seen:
                seen.append(fam)
    for fam in seen:
        if fam != author and _available(fam):
            return fam, ""
    return author, (" [DEGRAU 3 da escada: nenhum modelo distinto disponivel -> mesmo modelo em "
                    "contexto fresh — DECLARAR no veredito, nunca fingir heterogeneidade]")


def suggest_model(next_role, risk, author):
    """Regra DETERMINISTICA papel+risco -> modelo, lida de model-policy.json (ADR-078; era
    hardcoded no ADR-076 — politica em 3 fontes divergentes foi o gap P5 da avaliacao 2026-06-11)."""
    role = (next_role or "").lower()
    # robusto a metadados no JSON: so e override se o VALOR resolve a um tier existente
    risk_tier = POLICY["risk_override"].get(risk or "")
    if risk_tier in POLICY["tiers"]:
        fam, fb = _tier_model(risk_tier)
        return fam, f"alto-risco/regulado/irreversivel -> tier max ({fam}) + gate humano (HITL){fb}"
    for rule in POLICY["roles"]:
        if any(k in role for k in rule["match"]):
            if rule["tier"] == "heterogeneous":
                het, fb = _heterogeneous(author)
                return het, (f"qa/review -> HETEROGENEO (autor={author}; ADR-018 anti-vies; "
                             f"escada completa em model-policy.json){fb}")
            fam, fb = _tier_model(rule["tier"])
            return fam, f"{rule['match'][0]} -> tier {rule['tier']} ({fam}): {rule['why']}{fb}"
    fam, fb = _tier_model(POLICY["default_tier"])
    return fam, f"default -> tier {POLICY['default_tier']} ({fam}){fb}"


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


# --- Regra 8 / ADR-098: referencia a arquivo resolve no cwd do DESTINATARIO ------------------
# Conservador POR DESENHO: so acusa o que e deterministicamente quebrado no destino. Falso
# positivo aqui custa a confianca no gate inteiro — e um gate em que ninguem acredita e pior
# que nenhum gate.
_TEMP_MARCAS = (
    "appdata\\local\\temp", "appdata/local/temp", "/tmp/", "\\temp\\",
    "%temp%", "$env:temp", "scratchpad",
)
# link markdown cujo alvo nao e URL, nao e ancora e nao e path absoluto -> so resolve
# a partir do diretorio do arquivo que o contem
_LINK_REL = re.compile(r"\]\((?!https?://|#|mailto:|/|[A-Za-z]:[\\/])([^)\s]+)\)")


def audit_paths(texto):
    """Avisos sobre referencias que NAO resolvem no cwd do destinatario (ADR-098, Regra 8).

    Retorna lista de avisos. Nao levanta excecao e nao altera o texto: o handoff continua
    sendo emitido — o aviso e VISIVEL, nao bloqueante (conformance advisory do ADR-097).
    """
    avisos = []
    baixo = texto.lower()
    achadas = sorted({m for m in _TEMP_MARCAS if m in baixo})
    if achadas:
        avisos.append(
            "path em diretorio TEMPORARIO (" + ", ".join(achadas) + ") — some em limpeza de "
            "disco. Copie o artefato para caminho PERMANENTE e informe esse."
        )
    rel = sorted({m.group(1) for m in _LINK_REL.finditer(texto)})
    if rel:
        amostra = ", ".join(rel[:3]) + (" ..." if len(rel) > 3 else "")
        avisos.append(
            f"link markdown RELATIVO ({amostra}) — morto para quem le fora deste diretorio. "
            "Use path absoluto ou URL completa."
        )
    return avisos


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
    # ADR-098 (Regra 8): sem a raiz ABSOLUTA, todo path relativo citado abaixo (arquivos
    # recentes, pendencias) so resolve no cwd de quem gerou — a proxima sessao pode estar
    # em outra maquina, outro clone ou outro repo aberto.
    L.append(f"- raiz absoluta desta copia: `{ROOT}` (paths relativos abaixo ancoram AQUI)")
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
    pacote = "\n".join(L) + "\n"
    # ADR-098: audita o proprio pacote antes de entregar. Aviso VISIVEL no artefato — nao
    # basta o agente "lembrar" da Regra 8, senao volta a ser prosa.
    avisos = audit_paths(pacote)
    if avisos:
        pacote += "\n## [ADR-098] Avisos de referencia\n"
        pacote += "".join(f"- ⚠️ {a}\n" for a in avisos)
    return pacote


def provenance(target, ts="<timestamp>"):
    """Carimbo de PROCEDENCIA para trabalho executado FORA do repositorio (ADR-095).

    AGNOSTICO POR DESENHO: o gatilho e a FORMA da situacao — diretorio de trabalho externo ao
    repo (drive corporativo sincronizado, pasta de cliente, share de rede) — nunca o nome de um
    produto/cliente/vendor (canario core-no-vendor). O que o REPO sabe (framework, versao, commit,
    branch, origin, operador) e DETERMINISTICO e sai daqui; o que so o dominio sabe (chamado,
    sistema, pasta de origem, modelos por papel) sai como SLOT explicito para quem executa
    preencher. Slot vazio e lacuna VISIVEL, nao silencio.

    Porque existe (regua §0 — mecaniza prosa que ja era regra): rastreabilidade decisao->fonte->versao
    (traceability Regra 4) so vale se o artefato ENTREGUE souber dizer de onde veio. Trabalho que sai
    do repo para uma pasta externa perdia esse elo — quem abre a pasta meses depois nao sabe qual
    framework/versao/sessao produziu, nem o que e minuta e o que e registro.
    """
    st = repo_state()
    op = _git("config", "user.name") or "(nao configurado)"
    L = [
        "# PROCEDENCIA — quem produziu o conteudo desta pasta",
        "",
        "> Leia antes de usar qualquer arquivo desta pasta como registro.",
        "> Material produzido com assistencia de IA sob framework de processo.",
        "> Nada aqui e registro validado enquanto nao passar pelas aprovacoes do processo do dono.",
        "",
        "## 1. Demanda            (SLOT — preencher)",
        "",
        "| Campo | Valor |",
        "|---|---|",
        "| Identificador da demanda | `<preencher>` |",
        "| Identificador externo | `<preencher ou n/a>` |",
        "| Titulo | `<preencher>` |",
        "| Sistema / objeto | `<preencher>` |",
        "| Solicitante | `<preencher>` |",
        "",
        "## 2. Pasta de trabalho  (SLOT — preencher)",
        "",
        "| Campo | Valor |",
        "|---|---|",
        f"| Pasta desta procedencia | `{target}` |",
        "| Origem do material migrado | `<preencher ou n/a>` |",
        "",
        "## 3. Framework e sessao (DETERMINISTICO — lido do repo)",
        "",
        "| Campo | Valor |",
        "|---|---|",
        "| Framework | metacognition-framework |",
        f"| Versao | v{st['version']} |",
        f"| Commit | `{st['commit']}` (branch `{st['branch']}`) |",
        f"| Repositorio | {st['origin']} |",
        f"| Estado do repo no carimbo | {st['uncommitted']} arquivo(s) nao-commitado(s) · {st['unpushed']} commit(s) nao-pushado(s) |",
        f"| Data (commit HEAD) | {ts} |",
        f"| Operador humano | {op} |",
        "| Sessao (ID) | `<preencher>` |",
        "| Modo de execucao / rota | `<preencher>` |",
        "",
        "> **Isolamento de escrita (ADR-070):** o repositorio do framework NAO foi alterado por este",
        "> trabalho, e este material NAO foi copiado para la. Esta pasta e o unico destino de escrita.",
        "",
        "## 4. Modelos e papeis   (SLOT — preencher)",
        "",
        "| Papel | Modelo | O que produziu |",
        "|---|---|---|",
        "| `<papel>` | `<modelo>` | `<entregavel>` |",
        "",
        "Politica de modelo por papel/risco: `tools/model-policy.json` (ADR-078/082).",
        "Revisor sempre em modelo distinto do autor (anti-vies de auto-aprovacao, ADR-018).",
        "",
        "## 5. Origem e status de cada artefato (SLOT — preencher)",
        "",
        "| Arquivo | Origem | Status (MINUTA / PROPOSTA / MIGRADO / APROVADO) |",
        "|---|---|---|",
        "| `<arquivo>` | `<sessao ou origem>` | `<status>` |",
        "",
        "## 6. O que este material NAO e (SLOT — preencher/confirmar)",
        "",
        "- Nao e registro validado enquanto nao houver aprovacao formal no processo do dono.",
        "- Nao e codigo liberado enquanto nao houver compilacao/teste no ambiente real.",
        "",
        "## 7. Estado no encerramento (SLOT — preencher)",
        "",
        "- Bloqueio atual: `<preencher>`",
        "- Decisoes pendentes do dono: `<preencher>`",
        "",
        "---",
        "",
        f"*Carimbo gerado por `tools/handoff.py --provenance` em {ts}. Atualizar a cada sessao que alterar esta pasta.*",
    ]
    return "\n".join(L) + "\n"


PROV_HEADER = "# PROCEDENCIA"
WRITE_DEFAULT_DIR = "docs/_private/handoffs"


def _inside_repo(target):
    """True se `target` cai DENTRO da arvore do repo. Endurecido por qa-critic (ADR-095):

    - `realpath`: resolve symlink/junction/reparse-point. Sync clients criam junction e um alvo
      textualmente 'fora' pode apontar fisicamente para dentro do repo — `abspath` NAO resolve isso.
    - `normcase`: filesystem Windows e case-INSENSITIVE, mas `commonpath` compara string
      case-SENSITIVE. Sem isto, 'C:\\Users\\Fulano\\repo' nao casa 'C:\\Users\\fulano\\repo' e a
      guarda deixa escrever DENTRO do repo (bypass reproduzido na revisao).
    - `ValueError`: `commonpath` levanta quando os paths estao em drives diferentes ou um e UNC
      (`\\\\servidor\\share`) — que e JUSTAMENTE o caso de uso primario (drive corporativo/share).
      Drive diferente => certamente fora; retorna False em vez de estourar stack trace.
    """
    try:
        t = os.path.normcase(os.path.realpath(target))
        r = os.path.normcase(os.path.realpath(ROOT))
        return os.path.commonpath([t, r]) == r
    except (ValueError, OSError):
        return False


def emit_provenance(target, ts, write):
    """Imprime o carimbo; com --write grava <target>/PROCEDENCIA.md.

    NAO sobrescreve carimbo existente (traceability Regra 3 — preservacao): se o arquivo ja
    existe E E UM CARIMBO VALIDO, APENDA uma secao de sessao. Recusa alvo DENTRO do repo:
    la a procedencia e o proprio git, e o carimbo seria ruido.
    """
    target = os.path.abspath(os.path.expanduser(target))
    if _inside_repo(target):
        print(f"[handoff] ERRO: '{target}' esta DENTRO do repo — procedencia aqui e o proprio git."
              " Este carimbo e para diretorio de trabalho EXTERNO.", file=sys.stderr)
        return 2
    if not os.path.isdir(target):
        print(f"[handoff] ERRO: diretorio inexistente: {target}", file=sys.stderr)
        return 2
    pkg = provenance(target, ts=ts)
    if not write:
        print(pkg)
        return 0

    out = os.path.join(target, "PROCEDENCIA.md")
    if os.path.exists(out):
        # Existir NAO basta: pasta reaproveitada de outra demanda, arquivo vazio ou truncado
        # fariam o append colar um rabo de sessao num documento sem cabeca (achado da revisao).
        try:
            head = open(out, encoding="utf-8-sig").read(4096)
        except OSError as e:
            print(f"[handoff] ERRO: {out} existe mas nao pode ser lido ({e}).", file=sys.stderr)
            return 2
        if PROV_HEADER not in head:
            print(f"[handoff] ERRO: '{out}' existe mas NAO e um carimbo de procedencia"
                  f" (falta o cabecalho '{PROV_HEADER}'). Nao vou apendar em documento alheio nem"
                  " sobrescrever. Renomeie/remova o arquivo, ou gere o carimbo em outra pasta.",
                  file=sys.stderr)
            return 2
        st = repo_state()
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"\n\n---\n\n## Sessao adicional — {ts}\n\n"
                    f"- Framework v{st['version']} · commit `{st['commit']}` · branch `{st['branch']}`\n"
                    f"- Operador: {_git('config', 'user.name') or '(nao configurado)'}\n"
                    f"- Sessao (ID): `<preencher>`\n"
                    f"- O que esta sessao alterou nesta pasta: `<preencher>`\n")
        print(f"[handoff] carimbo JA EXISTIA — apendada secao de sessao em: {out}")
        return 0

    with open(out, "w", encoding="utf-8") as f:
        f.write(pkg)
    print(f"[handoff] carimbo de procedencia gravado: {out}")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="Gerador deterministico do Pacote de handoff P14 (ADR-076).")
    ap.add_argument("--next-role", default="", help="papel da proxima sessao (default: inferido do checkpoint)")
    ap.add_argument("--risk", default="low", choices=["low", "high", "regulated", "irreversible"])
    ap.add_argument("--author", default="opus", choices=list(MODEL_ID), help="familia do modelo autor do bloco")
    ap.add_argument("--write", nargs="?", const=WRITE_DEFAULT_DIR, default=None,
                    help=f"grava o pacote (default dir {WRITE_DEFAULT_DIR}/) em vez de so imprimir")
    ap.add_argument("--provenance", metavar="DIR", default=None,
                    help="emite CARIMBO DE PROCEDENCIA para um diretorio de trabalho EXTERNO ao repo "
                         "(ADR-095); com --write (SEM valor) grava/atualiza <DIR>/PROCEDENCIA.md")
    a = ap.parse_args(argv[1:])

    # timestamp DETERMINISTICO do estado do repo: data do commit HEAD (nao Date.now).
    ts = _git("show", "-s", "--format=%cI", "HEAD") or "<sem-data>"

    if a.provenance is not None:
        # --write tem semantica DIFERENTE nos dois modos: no handoff aceita caminho; aqui o
        # destino e sempre <DIR>/PROCEDENCIA.md. Aceitar um caminho e descarta-lo em silencio
        # e armadilha de CLI (achado da revisao adversarial) — falhar alto e o correto.
        # normpath nos dois lados: 'docs\\_private\\handoffs' e 'docs/_private/handoffs' sao a
        # MESMA pasta; comparar string crua rejeitava a forma nativa do Windows (falso-positivo).
        if a.write is not None and os.path.normpath(a.write) != os.path.normpath(WRITE_DEFAULT_DIR):
            print(f"[handoff] ERRO: '--write {a.write}' nao se aplica a --provenance: o carimbo"
                  " grava SEMPRE em <DIR>/PROCEDENCIA.md. Use '--write' sem valor.", file=sys.stderr)
            return 2
        return emit_provenance(a.provenance, ts, write=a.write is not None)
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
