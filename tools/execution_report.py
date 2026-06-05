#!/usr/bin/env python3
"""execution_report.py — relatório de execução de DOIS TIERS no encerramento de bloco.

ADR-038 criou o tier OWNER (placar gate × achado, retrabalho, tokens). ADR-052 torna o tool
dois-tiers e mecaniza o ADR-048:

  TIER OWNER  (repo-fonte do mantenedor; detectado por `docs/_private/` existir — o export-clean
              o remove de TODA distribuição): relatório FULL, sem filtro, sem anonimização. Vai
              para `docs/_private/_intake/` (stripped do export). É o insumo cru do dono.

  TIER EXTERNAL (qualquer distribuição: public/non-admin/premium — sem `docs/_private/`):
              telemetria SÓ de sinais de PROCESSO codificados (gates disparados, pontos de
              falha mecanismo×junção, eventos de correção, retrabalho, rota, modo). SEM texto
              livre, SEM conteúdo de domínio. Garantia de "zero vazamento" = WHITELIST de schema
              (não confiança): cada linha tem de casar `<chave>: <enum|int|versão|hash|NÃO MEDIDO>`,
              senão FAIL. + heurística anti-PII + backstop de anonimização quando disponível.
              Vai para `telemetry/`, respeita opt-out, e o usuário PODE abrir PR para o master
              (o PR é o consentimento — ADR-052). Não-pessoal → fora da LGPD (Art. 12).

INVARIANTE ANTI-FABRICAÇÃO (herdada, vale nos dois tiers): tokens é "NÃO MEDIDO" OU número COM
fonte declarada — NUNCA inventado.

Uso:
    python tools/execution_report.py [--tier owner|external|auto] [--from-transcripts] [--out FILE]
    python tools/execution_report.py --validate <report.md>     # tier inferido do conteúdo

Exit 0 ok; 1 falha de validação/geração; 3 = tier external desligado por opt-out (geração pulada).
"""
import argparse
import os
import re
import sys
import unicodedata

# --- OWNER: seções obrigatórias (ADR-038 + ADR-062 aprendizado estilo-AIVI) ---
REQUIRED = {
    "tokens": ["token"],
    "tempo": ["tempo", "wall-clock", "wall clock", "duracao"],
    "turnos": ["turno"],
    "arquivos": ["arquivo"],
    "testes": ["teste"],
    "retrabalho": ["retrabalho", "rework"],
    "placar": ["placar", "gate x achado", "gate × achado", "quem pegou"],
    # ADR-062: seções de APRENDIZADO (heading obrigatório; conteúdo vazio="— (nenhum)" é válido,
    # NÃO é fabricação — só tokens tem invariante de número-com-fonte).
    "deteccao": ["framework x humano", "framework × humano", "deteccao framework"],
    "gaps": ["gap"],
    "melhorias": ["melhoria"],
    "boas_praticas": ["boa pratica", "boas praticas", "boa prática", "boas práticas"],
    "licoes": ["licao por skill", "licoes por skill", "lição por skill", "lições por skill"],
}
NENHUM = "— (nenhum neste bloco)"
SOURCE_KEYS = ("fonte:", "transcript", "telemetria", "usage", "adr-026")
NAO_MEDIDO = "NÃO MEDIDO"

# --- EXTERNAL: vocabulário CONTROLADO (a whitelist). Tunar aqui é a única superfície de design. ---
# Escalares de topo: chave -> validador(valor)->bool
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")          # id de mecanismo do framework; não cabe frase
JUNCTION = {"j0", "j1", "j2", "j3", "j4", "j5", "na"}
EXT_SCALARS = {
    "tier": lambda v: v == "external",
    "session_id": lambda v: re.fullmatch(r"[a-f0-9]{6,64}", v) is not None,
    "framework_version": lambda v: re.fullmatch(r"v?\d+\.\d+(\.\d+)?[a-z0-9.-]*", v) is not None,
    "execution_mode": lambda v: v in {"default", "avancado", "autosuficiente", "nao medido"},
    "route": lambda v: v in {"pontual", "squad", "squad+high-stakes", "nao medido"},
    "turnos": lambda v: v.isdigit() or v == "nao medido",
    "retrabalho_rodadas": lambda v: v.isdigit() or v == "nao medido",
}
# Seções de lista: nome -> {chave: validador}
EXT_LIST_SECTIONS = {
    "gates_fired": {
        "gate": lambda v: SLUG.match(v) is not None,
        "outcome": lambda v: v in {"pass", "fail", "override", "skip"},
    },
    "failure_points": {
        "mechanism": lambda v: v in {"hook", "gate", "tool", "prose"},
        "id": lambda v: SLUG.match(v) is not None,
        "failure": lambda v: v in {"missed", "misfired", "absent", "bypassed", "false-positive"},
        "junction": lambda v: v in JUNCTION,
    },
    "correction_events": {
        "type": lambda v: v in {"rewind", "override", "redirect", "reject", "clarify"},
        "junction": lambda v: v in JUNCTION,
        "turn": lambda v: v.isdigit(),
    },
}
# Heurística anti-PII (rede extra; o whitelist já barra prosa). Roda sobre o texto inteiro.
PII_PATTERNS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "e-mail"),
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "CPF"),
    (re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"), "CNPJ"),
    (re.compile(r"(?:\+?55[\s-]?)?\(?\d{2}\)?[\s-]?9?\d{4}[\s-]?\d{4}"), "telefone"),
    (re.compile(r'"[^"]{15,}"'), "string longa entre aspas (texto livre?)"),
]


def _norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s.lower()


# ---------------------------------------------------------------- detecção de tier / opt-out

def repo_root(start=None):
    """Sobe de `start` (ou cwd) até achar a raiz do repo (tem `docs/` ou `.git`)."""
    cur = os.path.abspath(start or os.getcwd())
    while True:
        if os.path.isdir(os.path.join(cur, "docs")) or os.path.isdir(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return os.path.abspath(start or os.getcwd())
        cur = parent


def detect_tier(root=None):
    """OWNER sse `docs/_private/` existe (= repo-fonte; export-clean o remove de TODA distribuição)."""
    root = root or repo_root()
    return "owner" if os.path.isdir(os.path.join(root, "docs", "_private")) else "external"


def telemetry_enabled(root=None):
    """Switch de opt-out do tier EXTERNAL (geração). Owner ignora isto."""
    if os.environ.get("FRAMEWORK_NO_TELEMETRY"):
        return False
    root = root or repo_root()
    home = os.path.expanduser("~")
    for lock in (os.path.join(root, ".claude", "no-telemetry.lock"),
                 os.path.join(home, ".claude", "no-telemetry.lock")):
        if os.path.exists(lock):
            return False
    return True


def default_out_path(tier, root=None):
    root = root or repo_root()
    if tier == "owner":
        return os.path.join(root, "docs", "_private", "_intake", "execution-report.md")
    return os.path.join(root, "telemetry", "telemetry-report.md")


# ---------------------------------------------------------------- OWNER (ADR-038, inalterado)

def token_value_ok(text):
    """Linha de tokens diz 'NÃO MEDIDO' OU tem número COM fonte. Número sem fonte = fabricado."""
    n = _norm(text)
    token_lines = [ln for ln in n.splitlines() if "token" in ln]
    if not token_lines:
        return False, "sem campo de tokens"
    for ln in token_lines:
        if "nao medido" in ln:
            return True, "NÃO MEDIDO (honesto)"
        if re.search(r"\d{2,}", ln):
            if any(k in ln for k in SOURCE_KEYS):
                return True, "número com fonte declarada"
            return False, "número de token sem fonte declarada (fabricado)"
    return False, "campo de tokens sem 'NÃO MEDIDO' nem número+fonte"


def validate_owner_report(text):
    problems = []
    if not text or not text.strip():
        return False, ["report ausente/vazio (encerramento sem execution-report)"]
    n = _norm(text)
    for sec, needles in REQUIRED.items():
        if not any(_norm(x) in n for x in needles):
            problems.append(f"seção ausente: {sec}")
    ok_tok, why = token_value_ok(text)
    if not ok_tok:
        problems.append(f"tokens: {why}")
    return (len(problems) == 0), problems


def build_owner_report(tokens_line=None, wall_clock="NÃO MEDIDO", turnos="NÃO MEDIDO",
                       arquivos=None, testes="NÃO MEDIDO", retrabalho="NÃO MEDIDO", placar=None,
                       deteccao=None, gaps=None, melhorias=None, boas_praticas=None, licoes=None):
    if tokens_line is None:
        tokens_line = f"{NAO_MEDIDO} — sem telemetria de token exposta ao agente (dependência do host; ver LIMITS.md)"
    arquivos = arquivos or "NÃO MEDIDO"
    placar = placar or [("(preencher por bloco)", "quem pegou", "gate que deveria")]
    L = ["# Execution-report — encerramento de bloco (ADR-038/052 · tier OWNER · privado, não distribuído)", ""]
    L.append(f"- **Tokens:** {tokens_line}")
    L.append(f"- **Tempo (wall-clock):** {wall_clock}")
    L.append(f"- **Turnos:** {turnos}")
    L.append(f"- **Arquivos tocados:** {arquivos}")
    L.append(f"- **Testes:** {testes}")
    L.append(f"- **Rodadas de retrabalho:** {retrabalho}")
    L += ["", "## Placar gate × achado (quem pegou o quê)",
          "| Achado | Quem pegou | Gate que deveria ter pego |", "|---|---|---|"]
    for achado, quem, gate in placar:
        L.append(f"| {achado} | {quem} | {gate} |")

    # ADR-062: seções de APRENDIZADO (estilo-AIVI). Default = NENHUM (válido, não fabricado).
    def _block(title, body):
        return ["", f"## {title}", (body or NENHUM)]
    L += _block("Detecção: framework × humano (quem pegou o quê — mecanismo vs. revisão humana)", deteccao)
    L += _block("Gaps (não-bloqueantes detectados — flagados, não silenciados)", gaps)
    L += _block("Melhorias (do framework/processo — adição passa pela régua §0)", melhorias)
    L += _block("Boas práticas (o que funcionou — reutilizável)", boas_praticas)
    L += _block("Lições por skill (agnóstico de domínio — o que daqui serve a OUTRO projeto)",
                licoes or "- dev: " + NENHUM + "\n- discovery: " + NENHUM + "\n- architect: " + NENHUM +
                "\n- qa-critic: " + NENHUM + "\n- docops: " + NENHUM + "\n- research/spec/ux: " + NENHUM)
    return "\n".join(L)


# ---------------------------------------------------------------- EXTERNAL (ADR-052, whitelist)

def _split_pairs(item_body):
    """'k: v; k2: v2' -> [(k, v_normalizado), ...]; None se alguma parte não casa 'k: v'."""
    pairs = []
    for part in item_body.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            return None
        k, v = part.split(":", 1)
        pairs.append((k.strip().lower(), _norm(v.strip())))
    return pairs


def validate_external_report(text):
    """WHITELIST: cada linha relevante tem de casar o schema codificado. Texto livre = FAIL."""
    problems = []
    if not text or not text.strip():
        return False, ["telemetria ausente/vazia"]

    # 1) heurística anti-PII sobre o texto inteiro (rede extra)
    for rx, label in PII_PATTERNS:
        if rx.search(text):
            problems.append(f"possível PII/texto livre detectado ({label}) — payload externo só aceita sinais codificados")

    section = None
    saw_tier = False
    for raw in text.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if not s or s.startswith("# ") or s == "#" or s.startswith("#!"):
            continue
        if s.startswith("##"):
            # nome da seção = texto após '##' até um comentário inline '#'; normalizado
            name = _norm(s.lstrip("#").split("#", 1)[0].strip()).replace(" ", "_")
            section = name if name in EXT_LIST_SECTIONS else None
            if name not in EXT_LIST_SECTIONS:
                problems.append(f"seção desconhecida: {name}")
            continue
        if s.startswith("- "):
            if section is None:
                problems.append(f"item de lista fora de seção conhecida: {s[:40]!r}")
                continue
            pairs = _split_pairs(s[2:])
            if pairs is None:
                problems.append(f"item não-codificado em {section}: {s[:40]!r}")
                continue
            allowed = EXT_LIST_SECTIONS[section]
            for k, v in pairs:
                if k not in allowed:
                    problems.append(f"chave fora do schema em {section}: {k!r}")
                elif not allowed[k](v):
                    problems.append(f"valor fora do enum em {section}.{k}: {v!r}")
            continue
        # escalar 'chave: valor'
        m = re.match(r"^[-*]?\s*([a-z_]+):\s*(.+)$", s, re.IGNORECASE)
        if not m:
            problems.append(f"linha não-codificada (texto livre?): {s[:50]!r}")
            continue
        key, val = m.group(1).lower(), m.group(2).strip()
        if key == "tokens":
            ok_tok, why = token_value_ok(s)
            if not ok_tok:
                problems.append(f"tokens: {why}")
            continue
        if key not in EXT_SCALARS:
            problems.append(f"chave escalar fora do schema: {key!r}")
            continue
        if key == "tier":
            saw_tier = True
        if not EXT_SCALARS[key](_norm(val)):
            problems.append(f"valor escalar fora do enum em {key}: {val!r}")

    if not saw_tier:
        problems.append("falta 'tier: external'")
    return (len(problems) == 0), problems


def build_external_report(framework_version="NÃO MEDIDO", execution_mode="NÃO MEDIDO",
                          route="NÃO MEDIDO", turnos="NÃO MEDIDO", retrabalho="NÃO MEDIDO",
                          session_id=None, gates_fired=None, failure_points=None,
                          correction_events=None, tokens_line=None):
    if tokens_line is None:
        tokens_line = f"{NAO_MEDIDO} — sem telemetria de token exposta ao agente (ver LIMITS.md)"
    sid = session_id or "000000"  # hash opaco; sem relógio (Date.now indisponível) — preenchido pelo caller
    L = ["# Telemetria de PROCESSO — anonimizada, estruturada (ADR-052 · tier EXTERNAL)",
         "# Só sinais de processo codificados. SEM texto livre, SEM conteúdo de domínio.",
         "# Não-pessoal (LGPD Art. 12). Revise e, se quiser contribuir, abra PR para o master",
         "# (github.com/fabriciopsouza/metacognition-framework). O PR é o consentimento.",
         "# Desligar a geração: .claude/no-telemetry.lock ou FRAMEWORK_NO_TELEMETRY=1. Ver TELEMETRY.md.",
         "",
         "tier: external",
         f"session_id: {sid}",
         f"framework_version: {framework_version if framework_version != NAO_MEDIDO else '0.0.0'}",
         f"execution_mode: {execution_mode}",
         f"route: {route}",
         f"turnos: {turnos}",
         f"retrabalho_rodadas: {retrabalho}",
         f"tokens: {tokens_line}",
         "",
         "## gates_fired"]
    for g in (gates_fired or [("route-gate", "pass")]):
        L.append(f"- gate: {g[0]}; outcome: {g[1]}")
    L += ["", "## failure_points  # onde o processo falhou (o foco do retroalimento)"]
    for f in (failure_points or [("gate", "exemplo-gate", "missed", "na")]):
        L.append(f"- mechanism: {f[0]}; id: {f[1]}; failure: {f[2]}; junction: {f[3]}")
    L += ["", "## correction_events  # onde o usuário corrigiu (codificado, sem verbatim)"]
    for c in (correction_events or [("redirect", "na", "1")]):
        L.append(f"- type: {c[0]}; junction: {c[1]}; turn: {c[2]}")
    return "\n".join(L)


# ---------------------------------------------------------------- dispatch (compat ADR-038)

def validate_report(text, tier=None):
    """Compat: default OWNER. tier=None infere do conteúdo (external se tiver marca de schema externo)."""
    if tier is None:
        n = _norm(text or "")
        tier = "external" if ("tier: external" in n or "## failure_points" in n
                              or "## correction_events" in n) else "owner"
    return validate_external_report(text) if tier == "external" else validate_owner_report(text)


def build_report(*args, tier="owner", **kwargs):
    """Compat: build_report() -> owner. tier='external' -> telemetria estruturada."""
    return build_external_report(**kwargs) if tier == "external" else build_owner_report(*args, **kwargs)


def tokens_from_transcripts():
    """Lê tokens dos transcripts (project_report, ADR-026). None se indisponível."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import project_report as pr  # noqa
        import glob
        directory = pr.find_dir(None)
        if not directory or not os.path.isdir(directory):
            return None
        files = sorted(glob.glob(os.path.join(directory, "*.jsonl")))
        if not files:
            return None
        g = {"input": 0, "output": 0}
        for f in files:
            s = pr.parse_session(f)
            g["input"] += s["tokens"]["input"]
            g["output"] += s["tokens"]["output"]
        if g["input"] + g["output"] == 0:
            return None
        return (f"input {g['input']:,} + output {g['output']:,} = {g['input'] + g['output']:,} "
                f"(fonte: transcripts do Claude Code, ADR-026)")
    except Exception:
        return None


def has_publish_consent(home=None):
    """ADR-062: opt-in p/ publicar o corpus público, registrado em ~/.claude/exec-report-consent.json
    (`{"consent": true, ...}`). Sem o arquivo / consent != true -> não publica. Ver REPORTS-CONTRIBUTION.md."""
    import json
    home = home or os.path.expanduser("~")
    try:
        with open(os.path.join(home, ".claude", "exec-report-consent.json"), encoding="utf-8") as fh:
            return json.load(fh).get("consent") is True
    except Exception:
        return False


def publish_pseudonym(home=None):
    """ADR-063: pseudônimo ALEATÓRIO e estável do contribuidor (gerado 1x no opt-in, guardado no
    consent.json). NÃO derivado de e-mail/username (anti-rainbow). None se sem consent/pseudônimo."""
    import json
    home = home or os.path.expanduser("~")
    try:
        with open(os.path.join(home, ".claude", "exec-report-consent.json"), encoding="utf-8") as fh:
            p = str(json.load(fh).get("pseudonym") or "")
            return p if re.fullmatch(r"[a-f0-9]{8,32}", p) else None
    except Exception:
        return None


def init_consent(home=None):
    """ADR-062/063: registra o opt-in (o ato de rodar É o consentimento informado — ver
    REPORTS-CONTRIBUTION.md) com um pseudônimo ALEATÓRIO. Idempotente: não sobrescreve consent existente."""
    import json
    import secrets
    home = home or os.path.expanduser("~")
    path = os.path.join(home, ".claude", "exec-report-consent.json")
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as fh:
                cur = json.load(fh)
            if cur.get("consent") is True and re.fullmatch(r"[a-f0-9]{8,32}", str(cur.get("pseudonym") or "")):
                return path, cur["pseudonym"], False  # já existe — preserva
        except Exception:
            pass
    # Preserva campos existentes (ex.: central_repo gravado pelo setup) — não sobrescrever (bug evitado).
    data = {}
    if os.path.isfile(path):
        try:
            data = json.load(open(path, encoding="utf-8"))
        except Exception:
            data = {}
    pseudo = secrets.token_hex(6)
    data.update({"consent": True, "pseudonym": pseudo, "adr": "062/063",
                 "scope": "learnings-public-anonimizado"})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=True, indent=2)
    return path, pseudo, True


def central_report_path(pseudonym, timestamp, exec_id):
    """ADR-063: reports/<pseudonimo>/<ISO-timestamp>__<exec-id>.md. Sanitiza componentes (anti-traversal)."""
    def safe(s, default):
        # só alfanumérico/_/- : filesystem-safe (Windows não aceita ':') E anti-traversal (sem '.').
        s = re.sub(r"[^A-Za-z0-9_-]", "-", str(s or "")).strip("-")[:64]  # trunca (MAX_PATH Windows)
        return s or default
    return "reports/{}/{}__{}.md".format(
        safe(pseudonym, "anon"), safe(timestamp, "0000"), safe(exec_id, "exec"))


def learnings_public(owner_text, root=None, require_consent=True):
    """ADR-062: versão PÚBLICA ANONIMIZADA do report OWNER (corpus de aprendizado agnóstico).
    Reusa anonymize.py (determinístico) + GATE sensitive-denylist (mesmo trust-model do export-clean,
    ADR-020). FAIL-CLOSED: denylist ausente OU token sensível sobrevivente -> RECUSA (problems != []).
    Retorna (texto_publico, problems). problems não-vazio = NÃO publicar."""
    root = root or repo_root()
    problems = []
    text = owner_text or ""
    # 0) CONSENT (ADR-062/063) — gate na própria função, não só no CLI (anti-bypass de API caller).
    if require_consent and not has_publish_consent():
        return "", ["sem opt-in registrado (~/.claude/exec-report-consent.json) — recuso publicar (ADR-063)"]
    # 1) anonimização determinística — FAIL-CLOSED: map ausente = sem anonimização = recuso.
    map_path = os.path.join(root, "tools", "anonymize-map.txt")
    if not os.path.isfile(map_path):
        problems.append("anonymize-map.txt ausente — sem anonimização; recuso publicar (fail-closed)")
    else:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import anonymize as an  # noqa
            text = an.apply_rules(text, an.load_rules(map_path))
        except Exception as e:
            problems.append(f"anonimização indisponível ({e}) — recuso publicar (fail-closed)")
    # 2) backstop denylist — FAIL-CLOSED: ausente, token sobrevivente, OU regex inválida = recuso.
    deny_path = os.path.join(root, "tools", "sensitive-denylist.txt")
    if not os.path.isfile(deny_path):
        problems.append("sensitive-denylist.txt ausente — sem backstop; recuso publicar (fail-closed)")
    else:
        for raw in open(deny_path, encoding="utf-8"):
            pat = raw.strip()
            if not pat or pat.startswith("#"):
                continue
            try:
                if re.search(pat, text, re.IGNORECASE):
                    problems.append(f"token sensível sobreviveu: /{pat}/ — NÃO publicar")
            except re.error:
                problems.append(f"padrão de denylist inválido (/{pat}/) — backstop comprometido; recuso (fail-closed)")
    # NUNCA devolver texto (possivelmente contaminado) quando recusado (anti-footgun p/ callers).
    if problems:
        return "", problems
    header = ("# Learnings report — PÚBLICO ANONIMIZADO (ADR-062 · corpus de melhoria do framework)\n"
              "# anonymize.py + gate sensitive-denylist. SEM cliente/PII. Opt-in: ver docs/REPORTS-CONTRIBUTION.md.\n\n")
    return header + text, problems


def _valid_slug(s):
    """owner/repo do GitHub: owner alfanum/-, repo alfanum/._- ; REJEITA '..' (anti-traversal de path/URL)."""
    s = str(s or "")
    return bool(re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9._-]+", s)) and ".." not in s


def central_repo_slug(home=None):
    """ADR-064: slug <owner>/repo do repo central. Do consent.json (`central_repo`) ou env
    FRAMEWORK_REPORTS_REPO. None se não configurado/ inválido (→ stage local, sem publicar)."""
    import json
    env = os.environ.get("FRAMEWORK_REPORTS_REPO")
    if env:  # env DEFINIDO decide (não cai p/ consent): inválido -> None (sem surpresa silenciosa)
        return env if _valid_slug(env) else None
    home = home or os.path.expanduser("~")
    try:
        with open(os.path.join(home, ".claude", "exec-report-consent.json"), encoding="utf-8") as fh:
            s = str(json.load(fh).get("central_repo") or "")
            return s if _valid_slug(s) else None
    except Exception:
        return None


def solution_id(root=None):
    """ADR-065: identidade da SOLUÇÃO (p/ ofertar o relatório 1x). De mission.md (1ª linha/título),
    senão basename do repo. Slug seguro."""
    root = root or repo_root()
    name = ""
    mp = os.path.join(root, "mission.md")
    if os.path.isfile(mp):
        try:
            for ln in open(mp, encoding="utf-8-sig"):
                ln = ln.strip().lstrip("#").strip()
                if ln:
                    name = ln
                    break
        except Exception:
            pass
    if not name:
        name = os.path.basename(os.path.abspath(root)) or "solucao"
    return re.sub(r"[^A-Za-z0-9_-]", "-", name).strip("-").lower()[:48] or "solucao"


_OFFER_STATES = {"deferred", "declined", "done"}  # ausente = "pending"


def _offer_marker(sid, root=None):
    root = root or repo_root()
    return os.path.join(root, ".claude", ".report-offers", re.sub(r"[^A-Za-z0-9_-]", "-", str(sid))[:48] or "x")


def get_offer_state(sid, root=None):
    try:
        s = open(_offer_marker(sid, root), encoding="utf-8").read().strip()
        return s if s in _OFFER_STATES else "pending"
    except Exception:
        return "pending"


def set_offer_state(sid, state, root=None):
    if state not in _OFFER_STATES:
        return False
    mk = _offer_marker(sid, root)
    os.makedirs(os.path.dirname(mk), exist_ok=True)
    with open(mk, "w", encoding="utf-8") as fh:
        fh.write(state)
    return True


def should_offer(sid, root=None):
    """ADR-065: ofertar se a solução está 'pending' ou 'deferred' (ainda não). 'done'/'declined' = não."""
    return get_offer_state(sid, root) in ("pending", "deferred")


def publish_learnings(owner_path, root=None, run_gh=True, home=None, now_iso=None):
    """ADR-064: AUTO-PUBLISH (fail-soft). consent→learnings_public(fail-closed)→stage em
    telemetry/learnings-public/<pseudo>/<ts>__<exec>.md→PR p/ o central (best-effort, gh).
    SEM gh/consent/slug → gera local e NÃO publica (nunca trava). Retorna (staging_path, problems, published)."""
    import hashlib
    root = root or repo_root()
    if not has_publish_consent(home):
        return None, ["sem opt-in (rode --init-consent) — não publico"], False
    try:
        owner_text = open(owner_path, encoding="utf-8-sig").read()
    except OSError as e:
        return None, [f"report OWNER ausente ({e})"], False
    # consent JÁ gateado acima (com home); o anonimizador re-valida só denylist/map (require_consent=False).
    pub, problems = learnings_public(owner_text, root, require_consent=False)
    if problems:
        return None, problems, False  # fail-closed: não publica conteúdo possivelmente sujo
    pseudo = publish_pseudonym(home) or "anon"
    ts = (now_iso or "0000").replace(":", "-")  # caller passa ISO; sem relógio aqui (determinístico/testável)
    exec_id = hashlib.sha256(pub.encode("utf-8")).hexdigest()[:8]
    rel = central_report_path(pseudo, ts, exec_id)  # reports/<pseudo>/<ts>__<exec>.md
    staging = os.path.join(root, "telemetry", "learnings-public", os.path.relpath(rel, "reports"))
    os.makedirs(os.path.dirname(staging), exist_ok=True)
    with open(staging, "w", encoding="utf-8") as fh:
        fh.write(pub + "\n")
    published = False
    if run_gh:
        published = _gh_publish_best_effort(staging, rel, central_repo_slug(home))
    return staging, [], published


def _gh_publish_best_effort(staging_file, central_rel_path, slug):
    """PR best-effort p/ o repo central via gh (fork→branch→PR). FAIL-SOFT: qualquer erro → False
    (já está staged local). Não testado no sandbox (sem gh/repo) — verificação do dono."""
    import shutil
    import subprocess
    if not slug or not shutil.which("gh"):
        return False
    def gh(*args, t=40):
        return subprocess.run(["gh", *args], capture_output=True, text=True, timeout=t)
    try:
        import base64
        with open(staging_file, encoding="utf-8") as fh:
            content_b64 = base64.b64encode(fh.read().encode("utf-8")).decode("ascii")
        branch = "report-" + central_rel_path.rsplit("/", 1)[-1].replace(".md", "")
        # 1. branch precisa EXISTIR antes do PUT (a contents API NÃO cria branch). Cria do default.
        default = (gh("api", f"repos/{slug}", "--jq", ".default_branch").stdout.strip() or "main")
        sha = gh("api", f"repos/{slug}/git/ref/heads/{default}", "--jq", ".object.sha").stdout.strip()
        if not sha:
            return False
        gh("api", "--method", "POST", f"repos/{slug}/git/refs",
           "-f", f"ref=refs/heads/{branch}", "-f", f"sha={sha}")  # ignora se já existe
        # 2. cria o arquivo nesse branch.
        r = gh("api", "--method", "PUT", f"repos/{slug}/contents/{central_rel_path}",
               "-f", f"message=report {central_rel_path}", "-f", f"content={content_b64}",
               "-f", f"branch={branch}", t=60)
        if r.returncode != 0:
            return False
        # 3. abre o PR contra o default; tenta ligar auto-merge (fail-soft se não configurado).
        pr = gh("pr", "create", "--repo", slug, "--base", default, "--head", branch,
                "--title", f"report {central_rel_path}", "--body", "auto (ADR-064/065)", t=60)
        if pr.returncode != 0:
            return False
        gh("pr", "merge", branch, "--repo", slug, "--auto", "--merge")  # auto-merge se CI verde (best-effort)
        return True
    except Exception:
        return False


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", choices=["owner", "external", "auto"], default="auto",
                    help="auto = detecta por docs/_private/ (ADR-052)")
    ap.add_argument("--from-transcripts", action="store_true", help="tokens via project_report (ADR-026)")
    ap.add_argument("--out", help="arquivo de saída (default: por tier; '-' = stdout)")
    ap.add_argument("--validate", help="validar um report existente (tier inferido do conteúdo)")
    ap.add_argument("--learnings-public", dest="learnings_public",
                    help="ADR-062: gera versão PÚBLICA ANONIMIZADA de um report OWNER (anonymize+denylist)")
    ap.add_argument("--init-consent", action="store_true",
                    help="ADR-063: registra opt-in (consent + pseudônimo aleatório) — ver REPORTS-CONTRIBUTION.md")
    ap.add_argument("--publish", nargs="?", const="auto", default=None,
                    help="ADR-064: auto-publish (fim de sessão) do report OWNER anonimizado p/ o repo central (fail-soft)")
    ap.add_argument("--offer-state", action="store_true",
                    help="ADR-065: mostra o estado da oferta de relatório da solução atual (e se deve ofertar)")
    ap.add_argument("--set-offer", choices=sorted(_OFFER_STATES),
                    help="ADR-065: seta o estado da oferta da solução atual (deferred|declined|done)")
    args = ap.parse_args()

    if args.offer_state or args.set_offer:
        root = repo_root()
        sid = solution_id(root)
        if args.set_offer:
            set_offer_state(sid, args.set_offer, root)
        print(f"solução={sid} · estado={get_offer_state(sid, root)} · "
              f"ofertar={'SIM' if should_offer(sid, root) else 'não'} (ADR-065)")
        return 0

    if args.init_consent:
        path, pseudo, created = init_consent()
        print(f"opt-in {'registrado' if created else 'já existia'}: {path} · pseudônimo={pseudo} "
              f"(aleatório, não-identificável; ADR-063). Corpus público via PR ativado — ver docs/REPORTS-CONTRIBUTION.md.")
        return 0

    if args.publish:  # ADR-064: auto-publish (fim de sessão; fail-soft)
        root = repo_root()
        owner = args.publish if isinstance(args.publish, str) and args.publish not in ("", "auto") \
            else default_out_path("owner", root)
        try:
            import datetime
            now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        except Exception:
            now_iso = "0000"
        staging, problems, published = publish_learnings(owner, root, now_iso=now_iso)
        if problems:
            print("publish: não publicado — " + "; ".join(problems) + " (fail-soft, não trava).")
            return 0
        msg = "publicado (PR aberto no repo central)" if published else \
              "gerado LOCAL (gh ausente/sem slug ou PR falhou — publique depois; fail-soft)"
        print(f"learnings-public {msg}: {staging}")
        return 0

    if args.learnings_public:
        if not has_publish_consent():
            print("RECUSADO: sem opt-in registrado (~/.claude/exec-report-consent.json com "
                  '{"consent": true}). Ver docs/REPORTS-CONTRIBUTION.md. (Geração pública é opt-in — ADR-062.)')
            return 1
        try:
            owner_text = open(args.learnings_public, encoding="utf-8-sig").read()
        except OSError as e:
            print(f"FAIL: {e}")
            return 1
        pub, problems = learnings_public(owner_text, repo_root())
        if problems:
            print("RECUSADO publicar learnings-public (fail-closed, ADR-062/020):")
            for p in problems:
                print("  - " + p)
            return 1
        out = args.out or os.path.join(repo_root(), "telemetry", "learnings-public.md")
        if out == "-":
            print(pub)
            return 0
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(pub + "\n")
        print(f"learnings-public ANONIMIZADO escrito em {out} (revise antes do push ao repo público)")
        return 0

    if args.validate:
        try:
            text = open(args.validate, encoding="utf-8-sig").read()
        except OSError as e:
            print(f"FAIL: {e}")
            return 1
        ok, problems = validate_report(text)
        print("PASS: execution-report válido" if ok else "FAIL: " + "; ".join(problems))
        return 0 if ok else 1

    root = repo_root()
    tier = detect_tier(root) if args.tier == "auto" else args.tier

    if tier == "external" and not telemetry_enabled(root):
        print("execution-report: tier EXTERNAL com telemetria DESLIGADA (opt-out) — geração pulada.")
        return 3

    tokens_line = tokens_from_transcripts() if args.from_transcripts else None
    if tier == "external":
        report = build_external_report(tokens_line=tokens_line)
    else:
        report = build_owner_report(tokens_line=tokens_line)

    out = args.out
    if out == "-":
        print(report)
        return 0
    if not out:
        out = default_out_path(tier, root)
    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(report + "\n")
    print(f"execution-report (tier {tier}) escrito em {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
