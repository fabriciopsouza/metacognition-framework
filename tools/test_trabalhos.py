#!/usr/bin/env python3
"""Canario do registro de trabalhos (ADR-100).

O que precisa ser verdade para o mecanismo cumprir a funcao — e que uma mudanca futura
poderia quebrar em silencio:

  1. registrar cria o arquivo e o trabalho aparece em `listar`
  2. `tratar` tira do `listar` (e SO ele tira — nao some sozinho)
  3. `reabrir` traz de volta
  4. `listar` sem nada declara "nenhum" em vez de nao imprimir (silencio != vazio)
  5. re-registrar o mesmo slug ATUALIZA e PRESERVA o que nao foi passado
  6. o boot_check nunca FALHA por causa de trabalho aberto (informacao != erro)

Roda isolado em diretorio temporario: nao toca o registro real do dono.
"""
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(RAIZ, "tools", "trabalhos.py")


def run(env_dir, *args):
    env = dict(os.environ, TRABALHOS_DIR=env_dir, PYTHONIOENCODING="utf-8")
    p = subprocess.run([sys.executable, TOOL, *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, cwd=RAIZ)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    falhas = []

    def check(cond, msg):
        print(("  OK   " if cond else "  FALHA ") + msg)
        if not cond:
            falhas.append(msg)

    with tempfile.TemporaryDirectory() as d:
        print("1) listar vazio DECLARA, nao silencia")
        rc, out = run(d, "listar")
        check(rc == 0 and "nenhum trabalho em aberto" in out,
              "listar vazio diz 'nenhum trabalho em aberto'")

        print("\n2) registrar cria e aparece em listar")
        rc, _ = run(d, "registrar", "--slug", "alfa", "--nome", "Trabalho Alfa",
                    "--objetivo", "provar o ciclo", "--pendente", "- item um\n- item dois",
                    "--proximo", "decidir X")
        check(rc == 0, "registrar retorna 0")
        rc, out = run(d, "listar")
        check("Trabalho Alfa" in out, "trabalho aparece em listar")
        check("provar o ciclo" in out, "objetivo aparece em listar")
        check("decidir X" in out, "proximo passo aparece em listar")

        print("\n3) re-registrar ATUALIZA e PRESERVA o nao informado")
        rc, _ = run(d, "registrar", "--slug", "alfa", "--proximo", "decidir Y")
        rc, out = run(d, "mostrar", "--slug", "alfa")
        check("decidir Y" in out, "campo informado foi atualizado")
        check("item um" in out, "campo NAO informado foi preservado")
        check("Trabalho Alfa" in out, "nome preservado ao re-registrar")

        print("\n4) so `tratar` tira do listar")
        rc, out = run(d, "listar")
        check("Trabalho Alfa" in out, "continua aberto ate alguem tratar")
        rc, _ = run(d, "tratar", "--slug", "alfa", "--nota", "resolvido")
        check(rc == 0, "tratar retorna 0")
        rc, out = run(d, "listar")
        check("nenhum trabalho em aberto" in out, "tratado sai do listar")
        rc, out = run(d, "listar", "--todos")
        check("Trabalho Alfa" in out, "tratado continua visivel em --todos")
        rc, out = run(d, "mostrar", "--slug", "alfa")
        check("resolvido" in out, "nota do tratamento fica registrada")

        print("\n5) reabrir traz de volta")
        rc, _ = run(d, "reabrir", "--slug", "alfa")
        rc, out = run(d, "listar")
        check("Trabalho Alfa" in out, "reaberto volta ao listar")

        print("\n6) slug inexistente falha explicitamente")
        rc, out = run(d, "tratar", "--slug", "nao-existe")
        check(rc == 1, "tratar de slug inexistente retorna 1")

        print("\n7) NAO PERDE conteudo com '## ' ou '---' no texto  [achado BLOQUEANTE]")
        # o Pacote P14, que este registro existe para guardar, e cheio de '## '.
        # Particionar por qualquer '## ' e reserializar so as secoes canonicas apagava
        # esse conteudo na proxima escrita — o mecanismo perdia justamente o handoff.
        texto = "linha um\n\n## Secao do usuario\ndetalhe importante\n\n---\napos tres tracos"
        run(d, "registrar", "--slug", "beta", "--nome", "Beta", "--objetivo", "guardar P14",
            "--feito", texto)
        rc, out = run(d, "mostrar", "--slug", "beta")
        check("## Secao do usuario" in out, "titulo nao-canonico sobrevive ao 1o ciclo")
        run(d, "registrar", "--slug", "beta", "--proximo", "outro campo")  # re-escreve
        rc, out = run(d, "mostrar", "--slug", "beta")
        check("## Secao do usuario" in out, "titulo nao-canonico sobrevive a RE-ESCRITA")
        check("detalhe importante" in out, "texto sob titulo nao-canonico preservado")
        check("apos tres tracos" in out, "texto apos '---' preservado")
        run(d, "tratar", "--slug", "beta")
        rc, out = run(d, "mostrar", "--slug", "beta")
        check("detalhe importante" in out, "conteudo sobrevive tambem ao `tratar`")

        print("\n8) slug ja usado por OUTRO trabalho e recusado")
        rc, out = run(d, "registrar", "--slug", "beta", "--nome", "Trabalho Diferente",
                      "--objetivo", "outro")
        check(rc == 1 and "ja e de outro trabalho" in out, "recusa colisao de slug")
        rc, _ = run(d, "registrar", "--slug", "beta", "--nome", "Trabalho Diferente",
                    "--objetivo", "outro", "--force")
        check(rc == 0, "--force permite sobrescrever deliberadamente")

        print("\n9) objetivo e obrigatorio ao CRIAR")
        rc, out = run(d, "registrar", "--slug", "gama", "--nome", "Sem objetivo")
        check(rc == 1 and "obrigatorio" in out, "recusa criar sem --objetivo")

        print("\n10) o boot OFERECE de fato — nome e objetivo atravessam o gate")
        # sem isto, mudar o glifo '▸' ou a string 'nenhum trabalho em aberto' quebraria
        # o 'oferecer' em silencio, com o canario verde (achado GRAVE do qa-critic)
        run(d, "registrar", "--slug", "delta", "--nome", "Trabalho Delta Unico",
            "--objetivo", "ser oferecido no boot")
        env = dict(os.environ, TRABALHOS_DIR=d, PYTHONIOENCODING="utf-8")
        p = subprocess.run([sys.executable, os.path.join(RAIZ, "tools", "boot_check.py")],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=env, cwd=RAIZ)
        saida = (p.stdout or "") + (p.stderr or "")
        check("trabalhos-abertos" in saida, "boot_check executa o gate trabalhos-abertos")
        check("Trabalho Delta Unico" in saida,
              "o NOME do trabalho aberto chega ao boot (nao so o gate roda)")
        check("❌" not in saida.split("trabalhos-abertos")[-1][:60],
              "gate nao marca falha por haver trabalho aberto")
        check(p.returncode == 0, "boot_check continua exit 0 com trabalho aberto")

    print("\n" + "=" * 56)
    if falhas:
        print(f"RESULTADO: FALHA — {len(falhas)} verificacao(oes)")
        for f in falhas:
            print(f"  - {f}")
        return 1
    print("RESULTADO: PASS — ciclo aberto->tratado->reaberto integro")
    return 0


if __name__ == "__main__":
    sys.exit(main())
