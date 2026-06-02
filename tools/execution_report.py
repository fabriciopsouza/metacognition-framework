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

# --- OWNER: seções obrigatórias (ADR-038) ---
REQUIRED = {
    "tokens": ["token"],
    "tempo": ["tempo", "wall-clock", "wall clock", "duracao"],
    "turnos": ["turno"],
    "arquivos": ["arquivo"],
    "testes": ["teste"],
    "retrabalho": ["retrabalho", "rework"],
    "placar": ["placar", "gate x achado", "gate × achado", "quem pegou"],
}
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
    (re.compile(r"\b\(?\d{2}\)?\s?9?\d{4}-?\d{4}\b"), "telefone"),
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
                       arquivos=None, testes="NÃO MEDIDO", retrabalho="NÃO MEDIDO", placar=None):
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
    args = ap.parse_args()

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
