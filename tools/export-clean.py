#!/usr/bin/env python3
"""Pipeline de EXPORT privado → público (determinístico, auto-verificável).

Produz uma árvore LIMPA publicável a partir da fonte privada full:
  1. copia a árvore (sem .git);
  2. remove o cofre `docs/_private/` (não vai ao público);
  3. anonimiza via `tools/anonymize.py` (regras determinísticas);
  4. GATE: `check_core_agnostic.py --sensitive` — se QUALQUER token de cliente sobreviver,
     ABORTA (exit 1). É o que garante que o "automático" nunca publica vazamento;
  5. remove a infra de limpeza (denylist/map/scripts contêm os tokens reais).

Uso:
    python tools/export-clean.py <out-dir>

Exit 0 + árvore limpa em <out-dir>; exit 1 se o gate falhar (adicione regra em anonymize-map.txt).
Sem dependências externas (stdlib).
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.path.dirname(HERE)

STRIP_BEFORE = ["docs/_private", ".git"]            # cofre + história não vão ao público
STRIP_AFTER_VERIFY = [                               # infra de limpeza: carrega tokens reais
    "tools/sensitive-denylist.txt",
    "tools/anonymize-map.txt",
    "tools/anonymize.py",
    "tools/export-clean.py",
    "tools/test_core_agnostic.py",                   # canário interno: tokens split + dep da denylist
    ".github/workflows/publish-clean.yml",
]


def strip_pycache(root):
    """Remove todo __pycache__ (bytecode cacheado vaza caminhos internos; nunca distribuir)."""
    for dirpath, dirnames, _ in os.walk(root):
        for d in list(dirnames):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(dirpath, d))
                dirnames.remove(d)


def _rm(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def run(cmd, cwd=None):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd).returncode


def main(argv):
    if len(argv) < 2:
        print("uso: python tools/export-clean.py <out-dir>", file=sys.stderr)
        return 2
    out = os.path.abspath(argv[1])
    if os.path.abspath(out) == os.path.abspath(SRC_ROOT):
        print("out-dir nao pode ser a propria fonte", file=sys.stderr)
        return 2
    if os.path.exists(out):
        shutil.rmtree(out)

    # 1. copia
    shutil.copytree(SRC_ROOT, out, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    strip_pycache(out)
    # 2. strip cofre/história
    for rel in STRIP_BEFORE:
        _rm(os.path.join(out, *rel.split("/")))
    # 3. anonimiza
    py = sys.executable
    if run([py, os.path.join(out, "tools", "anonymize.py"), out]) != 0:
        print("anonymize falhou", file=sys.stderr)
        return 1
    # 4. GATE determinístico — denylist ainda presente em out/tools/
    if run([py, "tools/check_core_agnostic.py", "--sensitive"], cwd=out) != 0:
        print("\nGATE FALHOU: token de cliente sobreviveu ao anonymize.", file=sys.stderr)
        print("Adicione a regra correspondente em tools/anonymize-map.txt e rode de novo.", file=sys.stderr)
        return 1
    # 5. strip infra de limpeza (contém tokens reais)
    for rel in STRIP_AFTER_VERIFY:
        _rm(os.path.join(out, *rel.split("/")))

    print(f"\nEXPORT OK: arvore limpa publicavel em {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
