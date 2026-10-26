#!/usr/bin/env python3
"""varrer_irmaos.py — antes de chamar o revisor, acha o texto antigo que sobrou (ADR-132, bloco B2).

Medição do ADR-132: metade dos vereditos da série de 39 rodadas do ADR-115 citava "irmão" ou
"mesmo defeito" — o autor trocava uma frase, um número ou um nome num arquivo e a cópia em outro
ficava para o revisor achar. Esta ferramenta faz essa busca antes, por script.

Busca literal (`git grep -F`) em arquivos rastreados e não rastreados, respeitando o .gitignore.
Registro histórico, onde o texto antigo deve continuar, fica de fora por padrão: CHANGELOG.md,
docs/adr/, _meta/qa/ (vereditos). `--incluir-historico` busca neles também.

Uso:
    python tools/varrer_irmaos.py "texto antigo" ["outro texto" ...] [-i] [--excluir <glob>]
Exit 0 = nada sobrou; 1 = há ocorrência (listada como arquivo:linha:texto); 2 = erro de uso ou git.
"""
import argparse
import subprocess
import sys

HISTORICO = ("CHANGELOG.md", "docs/adr/**", "_meta/qa/**")

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def varrer(textos, raiz=".", ignorar_caixa=False, excluir=(), incluir_historico=False):
    """Lista 'arquivo:linha:conteúdo' de cada ocorrência. Levanta RuntimeError se o git falhar."""
    cmd = ["git", "-C", raiz, "grep", "-n", "-I", "-F", "--untracked"]
    if ignorar_caixa:
        cmd.append("-i")
    for t in textos:
        cmd += ["-e", t]
    fora = list(excluir) + ([] if incluir_historico else list(HISTORICO))
    cmd += ["--", "."] + [f":(exclude,glob){g}" for g in fora]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode not in (0, 1):  # git grep: 0 achou, 1 não achou, >1 erro
        raise RuntimeError(proc.stderr.strip() or f"git grep saiu {proc.returncode}")
    return proc.stdout.splitlines()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lista ocorrências remanescentes de texto antigo.")
    ap.add_argument("texto", nargs="+", help="texto antigo (frase, número, nome); literal")
    ap.add_argument("-i", action="store_true", help="ignora maiúsculas/minúsculas")
    ap.add_argument("--excluir", action="append", default=[], help="glob a ignorar (repetível)")
    ap.add_argument("--incluir-historico", action="store_true",
                    help="busca também em " + ", ".join(HISTORICO))
    ap.add_argument("--raiz", default=".", help="repositório (padrão: diretório atual)")
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return 0 if e.code == 0 else 2
    if any(not t.strip() for t in args.texto):
        print("ERRO: texto vazio casaria todas as linhas", file=sys.stderr)
        return 2
    try:
        achados = varrer(args.texto, args.raiz, args.i, args.excluir, args.incluir_historico)
    except (RuntimeError, OSError) as e:
        print(f"ERRO (git): {e}", file=sys.stderr)
        return 2
    for linha in achados:
        print(linha)
    print(f"{len(achados)} ocorrência(s) remanescente(s)", file=sys.stderr)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())
