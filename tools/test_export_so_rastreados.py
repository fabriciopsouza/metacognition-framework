#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canário: o export leva SÓ o que o git rastreia.
================================================================================

POR QUE EXISTE. O QA adversarial de 14/09/2026 provou, com token de controle,
que `.agent/brain/session-files.json` — 54 KB, **gitignored** — entrava no
pacote público. Dentro dele: 23× um identificador de projeto de cliente, 19× de
outro, 9× de um terceiro. E `check_core_agnostic.py` **poda** `.agent/brain`:
o verificador anti-vazamento estava configurado para não olhar exatamente onde
o vazamento estava.

A causa era `shutil.copytree` sobre a árvore de trabalho com `ignore_patterns` —
uma lista que alguém precisa lembrar de manter. Ela tinha `.git`, `__pycache__`,
`.venv` e `.pytest_cache`, e deixava passar todo o resto do `.gitignore`:
`.claude/settings.local.json`, `boot-proof.json`, `closing-proof.json`,
`cross-ai-repos.json`.

Agravante de rota: o publish por GitHub Actions está morto, então o caminho vivo
é este script rodado localmente — a partir da árvore de trabalho, onde os
gitignored existem.

A REGRA, e ela não tem exceção a esquecer: **o que não está versionado não
pertence a uma distribuição do repositório.**

Este canário prova as três coisas que importam:
  1. arquivo rastreado É copiado;
  2. arquivo gitignored NÃO é copiado — com token de controle;
  3. sem `git ls-files`, a função PARA em vez de cair para copiar tudo.
"""

import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "export_clean", os.path.join(ROOT, "tools", "export-clean.py"))
export_clean = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export_clean)

TOKEN = "ZZTOKENDECONTROLEQUENAOPODEVIAJAR"
falhas = []


def gate(ok: bool, nome: str) -> None:
    print(("PASS " if ok else "FAIL ") + nome)
    if not ok:
        falhas.append(nome)


def _git(cwd, *args):
    subprocess.run(["git", "-C", cwd, *args], check=True,
                   capture_output=True)


def repo_de_teste(base: str) -> str:
    """Um repositório de verdade: rastreado, gitignored e o token de controle."""
    src = os.path.join(base, "src")
    os.makedirs(os.path.join(src, ".agent", "brain"))
    _git(base, "init", "src")
    _git(src, "config", "user.email", "canario@example.com")
    _git(src, "config", "user.name", "canario")

    with open(os.path.join(src, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(".agent/brain/\nsegredo.local\n")
    with open(os.path.join(src, "rastreado.md"), "w", encoding="utf-8") as f:
        f.write("conteudo publico\n")
    # os dois gitignored, cada um com o token
    with open(os.path.join(src, ".agent", "brain", "sessao.json"),
              "w", encoding="utf-8") as f:
        f.write('{"projeto": "' + TOKEN + '"}\n')
    with open(os.path.join(src, "segredo.local"), "w", encoding="utf-8") as f:
        f.write(TOKEN + "\n")

    _git(src, "add", ".gitignore", "rastreado.md")
    _git(src, "commit", "-m", "canario")
    return src


def contem_token(raiz: str) -> list:
    achados = []
    for pasta, _dirs, arquivos in os.walk(raiz):
        for nome in arquivos:
            caminho = os.path.join(pasta, nome)
            try:
                with open(caminho, encoding="utf-8", errors="ignore") as f:
                    if TOKEN in f.read():
                        achados.append(os.path.relpath(caminho, raiz))
            except OSError:
                pass
    return achados


def main() -> int:
    with tempfile.TemporaryDirectory() as base:
        src = repo_de_teste(base)
        out = os.path.join(base, "out")

        ok = export_clean.copiar_rastreados(src, out)
        gate(ok, "copiar_rastreados devolve True num repositorio valido")

        gate(os.path.isfile(os.path.join(out, "rastreado.md")),
             "arquivo RASTREADO e' copiado")

        vazando = contem_token(out)
        gate(not vazando,
             f"token de controle NAO viaja (achado em: {vazando})")

        gate(not os.path.exists(os.path.join(out, ".agent", "brain")),
             "diretorio gitignored nao existe no export")
        gate(not os.path.exists(os.path.join(out, "segredo.local")),
             "arquivo gitignored solto nao existe no export")

        # 3. fail-closed: sem git, PARA — nao cai para copiar tudo
        sem_git = os.path.join(base, "sem-git")
        os.makedirs(sem_git)
        with open(os.path.join(sem_git, "x.txt"), "w", encoding="utf-8") as f:
            f.write(TOKEN)
        out2 = os.path.join(base, "out2")
        gate(export_clean.copiar_rastreados(sem_git, out2) is False,
             "sem repositorio git, PARA em vez de copiar a arvore inteira")
        gate(not contem_token(out2) if os.path.isdir(out2) else True,
             "e nao deixa nada copiado ao parar")

    print("-" * 60)
    if falhas:
        print(f"{len(falhas)} FALHA(S): {falhas}")
        return 1
    print("export leva so' o que o git rastreia.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
