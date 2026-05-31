#!/usr/bin/env python3
"""Linter de agnosticismo + anti-vazamento (ADR-020 + EMENDA v1.22.x).

DOIS TIERS:

  TIER NORMA (ADR-020 original) — enforcement EXECUTÁVEL do Princípio 12 e da regra #5 do
  qa-critic. Nenhum identificador de NORMA/CONVENÇÃO REGULATÓRIA de domínio (denylist
  `agnostic-denylist.txt`) pode aparecer no NÚCLEO OPERATIVO. Escopo restrito porque
  docs/** PODE citar uma norma como exemplo pedagógico. Sentinela: `lint-agnostic:allow`.

  TIER SENSÍVEL (EMENDA v1.22.x — incidente de vazamento 2026-05-31) — nenhum identificador
  de CLIENTE / PROJETO / CASO / REPO (denylist `sensitive-denylist.txt`) pode aparecer no
  REPOSITÓRIO INTEIRO que distribui. Dado de cliente NÃO é "exemplo pedagógico" — não pode
  vazar em lugar NENHUM. Por isso o escopo é o repo todo, EXCETO `.git/`, `docs/_private/`
  (cofre do dono, fora da distribuição), os próprios denylists e arquivos binários.
  Sentinela: `lint-sensitive:allow` (meta-zero na distribuição). AUTOR ≠ CLIENTE: o nome do
  mantenedor (atribuição legal) não está na denylist sensível — só orgs/casos de cliente.

REGRA (ambos): violação = exit 1, salvo a linha portar o sentinela do tier (estilo `# noqa`,
exige justificativa visível em diff — única exceção, auditável).

Uso:
    python tools/check_core_agnostic.py                 # tier NORMA (núcleo) — gate de BOOT
    python tools/check_core_agnostic.py --sensitive     # + tier SENSÍVEL (repo inteiro) — gate de EXPORT
    python tools/check_core_agnostic.py <arquivo>...    # tier NORMA nos arquivos dados (canário)

O tier SENSÍVEL é OPT-IN porque a FONTE PRIVADA full carrega nomes de cliente por design
(é o cofre de acesso total do dono). Ele é o gate de DISTRIBUIÇÃO: roda contra a árvore LIMPA
de export, garantindo que nada de cliente seja publicado. NÃO roda no boot (evita ruído na fonte).

Exit 0 se limpo; exit 1 se houver vazamento (qualquer tier ativo). Sem dependências externas.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DENYLIST_PATH = os.path.join(ROOT, "tools", "agnostic-denylist.txt")
SENSITIVE_DENYLIST_PATH = os.path.join(ROOT, "tools", "sensitive-denylist.txt")
SENTINEL = "lint-agnostic:allow"
SENSITIVE_SENTINEL = "lint-sensitive:allow"

# Tier NORMA — núcleo operativo agnóstico (globs + arquivos-âncora). FORA: docs/, exemplos/, tools/.
CORE_GLOBS = [
    "_shared/**/*.md",
    ".agent/skills/**/*.md",
    ".agent/rules/**/*.md",
    ".agent/workflows/**/*.md",
]
CORE_FILES = ["AGENT-FRAMEWORK.md", "CLAUDE.md", "AGENTS.md", "README.md"]

# Tier SENSÍVEL — varre o repo inteiro EXCETO estes diretórios e arquivos.
SENSITIVE_PRUNE_DIRS = {".git", "node_modules", "outputs", "_private"}
SENSITIVE_PRUNE_RELPATHS = {os.path.join("docs", "_private"), os.path.join(".agent", "brain")}
ANONYMIZE_MAP_PATH = os.path.join(ROOT, "tools", "anonymize-map.txt")
# Infra de limpeza carrega os tokens reais por design → não é alvo de varredura.
SENSITIVE_EXCLUDE_FILES = {DENYLIST_PATH, SENSITIVE_DENYLIST_PATH, ANONYMIZE_MAP_PATH}
# Binários: não-texto, pula sem tentar decodificar.
BINARY_EXTS = {
    ".xlsx", ".xls", ".pdf", ".docx", ".pptx", ".png", ".jpg", ".jpeg", ".gif",
    ".ico", ".woff", ".woff2", ".ttf", ".eot", ".zip", ".gz", ".tar", ".7z",
    ".mp4", ".mov", ".webp", ".pyc", ".bak",
}


def load_patterns(path=DENYLIST_PATH):
    """Lê a denylist (uma regex por linha; # e vazias ignoradas). Retorna lista de (regex, fonte)."""
    pats = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                pats.append((re.compile(line, re.IGNORECASE), line))
            except re.error as e:
                print(f"AVISO: padrao invalido na denylist ignorado: {line!r} ({e})", file=sys.stderr)
    return pats


def core_targets():
    files = []
    for pat in CORE_GLOBS:
        files.extend(glob.glob(os.path.join(ROOT, pat), recursive=True))
    for f in CORE_FILES:
        p = os.path.join(ROOT, f)
        if os.path.isfile(p):
            files.append(p)
    return sorted(set(files))


def sensitive_targets():
    """Todos os arquivos de TEXTO do repo, exceto .git/, docs/_private/, denylists e binários."""
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # poda in-place de diretórios
        dirnames[:] = [d for d in dirnames if d not in SENSITIVE_PRUNE_DIRS]
        rel = os.path.relpath(dirpath, ROOT)
        if any(rel == p or rel.startswith(p + os.sep) for p in SENSITIVE_PRUNE_RELPATHS):
            dirnames[:] = []
            continue
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if full in SENSITIVE_EXCLUDE_FILES:
                continue
            if os.path.splitext(fn)[1].lower() in BINARY_EXTS:
                continue
            files.append(full)
    return sorted(set(files))


def scan_file(path, patterns, sentinel=SENTINEL):
    """Retorna lista de violacoes (linha_no, token, trecho). Pula binário (decode err) silenciosamente."""
    viol = []
    try:
        with open(path, encoding="utf-8-sig") as fh:
            lines = fh.readlines()
    except UnicodeDecodeError:
        return []  # binário disfarçado — não é alvo de texto
    except OSError as e:
        return [(0, "<erro-io>", str(e))]
    for n, line in enumerate(lines, 1):
        if sentinel in line:
            continue  # exceção explícita e auditável
        for rx, src in patterns:
            m = rx.search(line)
            if m:
                viol.append((n, m.group(0), line.strip()[:120]))
    return viol


def _run_tier(targets, patterns, sentinel, label, verbose):
    """Varre `targets` com `patterns`. verbose=True imprime OK por arquivo (tier norma).
    Retorna (any_leak, n_clean)."""
    any_leak = False
    n_clean = 0
    for path in targets:
        try:
            rel = os.path.relpath(path, ROOT)
        except ValueError:
            rel = path
        viol = scan_file(path, patterns, sentinel)
        if viol:
            any_leak = True
            for (n, token, snippet) in viol:
                print(f"LEAK [{label}] {rel}:{n}: '{token}' -> {snippet}")
        else:
            n_clean += 1
            if verbose:
                print(f"OK   {rel}")
    return any_leak, n_clean


def main(argv):
    sensitive_on = False
    explicit = []
    for a in argv[1:]:
        if a in ("--sensitive", "--all"):
            sensitive_on = True
        else:
            explicit.append(a)

    agnostic_patterns = load_patterns(DENYLIST_PATH)
    if not agnostic_patterns:
        print("nenhum padrao na denylist (norma) — nada a verificar", file=sys.stderr)
        return 1

    any_leak = False

    # TIER NORMA — alvos explícitos (canário) OU núcleo operativo. SEMPRE roda (gate de boot).
    targets = explicit if explicit else core_targets()
    if not targets:
        print("nenhum arquivo de nucleo encontrado", file=sys.stderr)
        return 1
    leak_n, _ = _run_tier(targets, agnostic_patterns, SENTINEL, "norma", verbose=True)
    any_leak = any_leak or leak_n

    # TIER SENSÍVEL — OPT-IN (--sensitive/--all). Varre o repo inteiro. Gate de EXPORT, não de boot:
    # a fonte privada full carrega nomes de cliente por design (cofre de acesso total do dono).
    if sensitive_on and not explicit:
        if not os.path.isfile(SENSITIVE_DENYLIST_PATH):
            print("sensitive-denylist.txt ausente (export ja limpo?) — pulando tier sensivel", file=sys.stderr)
            sens_patterns = []
        else:
            sens_patterns = load_patterns(SENSITIVE_DENYLIST_PATH)
        if not sens_patterns:
            print("nenhum padrao na denylist (sensivel) — pulando tier sensivel", file=sys.stderr)
        else:
            print("-" * 40)
            sens_files = sensitive_targets()
            leak_s, clean_s = _run_tier(sens_files, sens_patterns, SENSITIVE_SENTINEL,
                                        "sensivel", verbose=False)
            # Path-check: token sensível NÃO pode aparecer no NOME do caminho (dir/arquivo) —
            # o scan de conteúdo não vê nomes; este é o backstop do rename de path.
            for p in sens_files:
                rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
                for rx, src in sens_patterns:
                    if rx.search(rel):
                        print(f"LEAK [sensivel-path] {rel}: token '{rx.pattern}' no NOME do caminho")
                        leak_s = True
                        break
            any_leak = any_leak or leak_s
            if not leak_s:
                print(f"OK   [sensivel] {clean_s} arquivos varridos (conteúdo + nome de caminho), zero vazamento")

    print("-" * 40)
    if any_leak:
        print("RESULTADO: FAIL (vazamento — Principio 12 [norma] e/ou dado de cliente [sensivel])")
        print(f"           Corrija, ou — se legítimo — adicione '{SENTINEL}' (norma) / "
              f"'{SENSITIVE_SENTINEL}' (sensivel) na linha com justificativa.")
        return 1
    print(f"RESULTADO: PASS ({'norma + sensivel' if sensitive_on else 'norma'})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
