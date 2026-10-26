#!/usr/bin/env python3
"""Canário do varrer_irmaos (ADR-132, bloco B2) — em repositório git temporário prova que a
varredura acha o texto antigo em arquivo rastreado e em não rastreado, respeita o .gitignore,
deixa o registro histórico de fora por padrão, sai 1 quando sobra ocorrência, 0 quando não sobra
e 2 em erro (texto vazio, pasta que não é repositório).

Uso: python tools/test_varrer_irmaos.py   (exit 0 PASS; 1 se falha)
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FERRAMENTA = os.path.join(ROOT, "tools", "varrer_irmaos.py")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def rodar(raiz, *args):
    p = subprocess.run([sys.executable, FERRAMENTA, "--raiz", raiz, *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    return p.returncode, p.stdout


def main():
    fails = []
    with tempfile.TemporaryDirectory() as td:
        arquivos = {
            "a.txt": "o prazo era 30 dias\n",            # rastreado, deve aparecer
            "sub/c.md": "O PRAZO ERA 30 DIAS\n",         # só com -i
            "novo.txt": "o prazo era 30 dias\n",         # não rastreado, deve aparecer
            "ignorado.log": "o prazo era 30 dias\n",     # no .gitignore, nunca aparece
            "CHANGELOG.md": "o prazo era 30 dias\n",     # histórico, só com --incluir-historico
            "docs/adr/001-x.md": "o prazo era 30 dias\n",
            ".gitignore": "*.log\n",
        }
        for rel, txt in arquivos.items():
            os.makedirs(os.path.dirname(os.path.join(td, rel)) or td, exist_ok=True)
            with open(os.path.join(td, rel), "w", encoding="utf-8") as fh:
                fh.write(txt)
        g = ["git", "-C", td, "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(g[:3] + ["init", "-q"], check=True)
        subprocess.run(g + ["add", "--", "a.txt", "sub/c.md", "CHANGELOG.md", "docs/adr/001-x.md",
                            ".gitignore"], check=True)
        subprocess.run(g + ["commit", "-q", "-m", "x"], check=True)

        def arquivos_em(saida):
            return sorted({linha.split(":", 1)[0] for linha in saida.splitlines()})

        casos = (
            (["o prazo era 30 dias"], 1, ["a.txt", "novo.txt"], "padrão: rastreado + não rastreado"),
            (["o prazo era 30 dias", "-i"], 1, ["a.txt", "novo.txt", "sub/c.md"], "-i"),
            (["o prazo era 30 dias", "--incluir-historico"], 1,
             ["CHANGELOG.md", "a.txt", "docs/adr/001-x.md", "novo.txt"], "--incluir-historico"),
            (["o prazo era 30 dias", "--excluir", "novo.txt"], 1, ["a.txt"], "--excluir"),
            (["texto que não existe"], 0, [], "nada sobrou -> exit 0"),
            (["30 dia."], 0, [], "busca literal: '.' não é curinga"),
            ([" "], 2, [], "texto vazio -> erro"),
        )
        for args, exit_esp, esperado, porque in casos:
            rc, out = rodar(td, *args)
            if rc != exit_esp:
                fails.append(f"exit {rc} != {exit_esp} ({porque})")
            if arquivos_em(out) != esperado:
                fails.append(f"achou {arquivos_em(out)}, esperado {esperado} ({porque})")
        with tempfile.TemporaryDirectory() as fora:
            rc, _ = rodar(fora, "x")
            if rc != 2:
                fails.append(f"pasta que não é repositório saiu {rc}, esperado 2 (erro de git "
                             "não pode virar 'nada sobrou')")

    print(f"varrer_irmaos: {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (varredura de irmãos acha o que sobrou e falha fechado)"
          if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
