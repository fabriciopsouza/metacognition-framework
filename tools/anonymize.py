#!/usr/bin/env python3
"""Anonimizador determinístico para o EXPORT público (privado → público).

Aplica as regras de `tools/anonymize-map.txt` (regex IGNORECASE, ORDENADAS) sobre todos os
arquivos de TEXTO de um diretório-alvo, in-place. Determinístico e reproduzível — é a peça
que torna o flow privado→público AUTOMÁTICO (vs. edição manual).

Backstop: NÃO é a garantia final. Depois de rodar, `check_core_agnostic.py --sensitive`
verifica que nenhum token sensível sobreviveu (se sobrar, o build falha e o dono adiciona regra).

Uso:
    python tools/anonymize.py <dir-alvo>     # reescreve os arquivos de texto sob <dir-alvo>

Sem dependências externas (stdlib).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAP_PATH = os.path.join(HERE, "anonymize-map.txt")

# Não reescrever binários nem a própria infra de limpeza.
BINARY_EXTS = {
    ".xlsx", ".xls", ".pdf", ".docx", ".pptx", ".png", ".jpg", ".jpeg", ".gif",
    ".ico", ".woff", ".woff2", ".ttf", ".eot", ".zip", ".gz", ".tar", ".7z",
    ".mp4", ".mov", ".webp", ".pyc", ".bak",
}
PRUNE_DIRS = {".git", "node_modules", "_private"}
SKIP_BASENAMES = {"anonymize-map.txt", "sensitive-denylist.txt"}


def load_rules(path=MAP_PATH):
    """Retorna lista ORDENADA de (regex_compilada, substituição)."""
    rules = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if "\t" not in line:
                print(f"AVISO: regra sem TAB ignorada: {line!r}", file=sys.stderr)
                continue
            pat, repl = line.split("\t", 1)
            try:
                rules.append((re.compile(pat, re.IGNORECASE), repl))
            except re.error as e:
                print(f"AVISO: regex invalida ignorada: {pat!r} ({e})", file=sys.stderr)
    return rules


def apply_rules(text, rules):
    for rx, repl in rules:
        text = rx.sub(repl, text)
    return text


def target_files(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]
        for fn in filenames:
            if fn in SKIP_BASENAMES:
                continue
            if os.path.splitext(fn)[1].lower() in BINARY_EXTS:
                continue
            out.append(os.path.join(dirpath, fn))
    return sorted(out)


def main(argv):
    if len(argv) < 2:
        print("uso: python tools/anonymize.py <dir-alvo>", file=sys.stderr)
        return 2
    root = argv[1]
    if not os.path.isdir(root):
        print(f"dir-alvo nao existe: {root}", file=sys.stderr)
        return 2
    rules = load_rules()
    if not rules:
        print("nenhuma regra carregada de anonymize-map.txt", file=sys.stderr)
        return 1
    changed = 0
    for path in target_files(root):
        try:
            with open(path, encoding="utf-8-sig") as fh:
                orig = fh.read()
        except (UnicodeDecodeError, OSError):
            continue  # binário disfarçado ou ilegível
        new = apply_rules(orig, rules)
        if new != orig:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
            changed += 1

    # Rename de NOMES de caminho (dir/arquivo) cujo basename casa alguma regra — fecha o
    # blind-spot: o scan de conteúdo não vê nomes de diretório (ex.: '...-aivi-method-fixes/').
    # Só renomeia se o resultado for filesystem-safe (sem espaço/separador) — regras de prosa
    # que injetariam espaço são puladas; o gate de path pega o que sobrar.
    renamed = 0
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        for name in list(filenames) + list(dirnames):
            new = apply_rules(name, rules)
            if new != name and new and " " not in new and os.sep not in new and "/" not in new:
                src, dst = os.path.join(dirpath, name), os.path.join(dirpath, new)
                if not os.path.exists(dst):
                    os.rename(src, dst)
                    renamed += 1
    print(f"anonymize: {changed} arquivo(s) reescrito(s) + {renamed} path(s) renomeado(s) "
          f"com {len(rules)} regra(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
