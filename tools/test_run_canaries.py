#!/usr/bin/env python3
"""Canário do EXECUTOR da suíte (`run_canaries.py`) — quem governa os 67 não era testado.

Lacuna medida em 2026-08-16: o runner que decide PASS/FAIL de toda a suíte não tinha canário
próprio. O gatilho foi um defeito real: **bytecode velho falsifica o resultado**. O Python
reusa um `.pyc` comparando TAMANHO e HORÁRIO do fonte, com resolução de 1 segundo — fonte que
muda mantendo o mesmo número de bytes, gravado no mesmo segundo, roda o código antigo.

Observado ao vivo nesta árvore: `test_autonomy_policy` FALHOU com o fonte idêntico ao commit,
porque o `.pyc` guardava o bytecode de uma sondagem. O inverso é pior — canário VERDE sobre
código que não está mais no disco.

O caso central aqui é COMPORTAMENTAL e determinístico: monta a corrida de propósito (mesmo
tamanho, mtime congelado) e confere que o ambiente do runner detecta a mudança que o ambiente
padrão deixaria passar. Não depende de sorte de relógio.

Uso: python tools/test_run_canaries.py   (exit 0 PASS; 1 se o runner puder ser enganado)
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import run_canaries as rc  # noqa: E402

resultados = []


def caso(nome, ok, detalhe=""):
    resultados.append((nome, ok, detalhe))
    print(f"  [{'PASS' if ok else 'FALHA'}] {nome}")
    if detalhe:
        print(f"          {detalhe}")


def _fixture(raiz, valor):
    """Módulo + verificador que o importa. A mutação preserva o tamanho por construção."""
    (raiz / "mod.py").write_text(f"VALOR = {valor}\n", encoding="utf-8")
    (raiz / "chk.py").write_text(
        "import sys, pathlib\n"
        "sys.path.insert(0, str(pathlib.Path(__file__).parent))\n"
        "import mod\n"
        "sys.exit(0 if mod.VALOR == 42 else 1)\n", encoding="utf-8")


def _env_padrao():
    """Ambiente REALMENTE padrao, custe quem for o chamador.

    Este canario roda tambem POR DENTRO do `run_canaries.py`, que ja exporta
    `PYTHONPYCACHEPREFIX`. Herdar esse ambiente fazia o caso "o padrao e' enganado" testar
    o ambiente ja corrigido e reprovar — o teste media o chamador, nao o codigo. Medido em
    2026-08-16: verde sozinho, vermelho dentro da suite.
    """
    return {k: v for k, v in os.environ.items()
            if k not in ("PYTHONPYCACHEPREFIX", "PYTHONDONTWRITEBYTECODE")}


def main():
    print("run_canaries: bytecode velho nao falsifica o resultado + travas presentes")

    # (1) COMPORTAMENTAL: a corrida montada de proposito.
    with tempfile.TemporaryDirectory(prefix="runner-canario-") as tmp:
        raiz = Path(tmp)
        _fixture(raiz, 42)
        mod, chk = raiz / "mod.py", raiz / "chk.py"

        # roda uma vez com o ambiente PADRAO: compila e grava o .pyc
        subprocess.run([sys.executable, str(chk)], cwd=str(raiz),
                       capture_output=True, env=_env_padrao())
        gravou = any((raiz / "__pycache__").glob("mod*.pyc")) if (raiz / "__pycache__").is_dir() else False

        # muda o valor MANTENDO o tamanho, e congela o mtime no do arquivo original
        st = mod.stat()
        mod.write_text("VALOR = 41\n", encoding="utf-8")   # mesmo numero de bytes
        os.utime(mod, (st.st_atime, st.st_mtime))          # mesma "idade" -> cache valido

        padrao = subprocess.run([sys.executable, str(chk)], cwd=str(raiz),
                                capture_output=True, env=_env_padrao())
        caso("a corrida do bytecode existe de fato (ambiente padrao e' enganado)",
             gravou and padrao.returncode == 0,
             f".pyc gravado={gravou}; verificador devolveu {padrao.returncode} "
             f"(0 = nao viu a mudanca). Se este caso falhar, o defeito deixou de existir "
             f"nesta versao do Python e o resto do canario perde o sentido.")

        # mesma situacao, agora com o ambiente que o runner usa. O `.pyc` envenenado
        # CONTINUA no disco de proposito: e' isso que distingue impedir escrita (insuficiente,
        # reprovou a 1a versao) de isolar a leitura num prefixo vazio (o conserto de verdade).
        with tempfile.TemporaryDirectory(prefix="prefixo-vazio-") as prefixo:
            do_runner = subprocess.run([sys.executable, str(chk)], cwd=str(raiz),
                                       capture_output=True,
                                       env=rc.ambiente_canario(prefixo))
        caso("o ambiente do runner NAO e' enganado pela mesma corrida",
             do_runner.returncode == 1,
             f"verificador devolveu {do_runner.returncode} (1 = detectou a mudanca), "
             f"com o .pyc envenenado ainda presente no disco")

    # (2) a purga varre a arvore e poupa `.git`.
    with tempfile.TemporaryDirectory(prefix="purga-") as tmp:
        raiz = Path(tmp)
        (raiz / "sub" / "__pycache__").mkdir(parents=True)
        (raiz / "sub" / "__pycache__" / "x.pyc").write_bytes(b"\x00")
        (raiz / ".git" / "__pycache__").mkdir(parents=True)
        (raiz / ".git" / "__pycache__" / "y.pyc").write_bytes(b"\x00")
        n = rc.purgar_bytecode(str(raiz))
        caso("purga remove __pycache__ da arvore e NAO entra em .git",
             n == 1 and not (raiz / "sub" / "__pycache__").exists()
             and (raiz / ".git" / "__pycache__").exists(),
             f"removidos={n}; sob .git preservado="
             f"{(raiz / '.git' / '__pycache__').exists()}")

    # (3) as travas estao onde o runner as usa — pega quem remove o env do subprocess.
    fonte = (TOOLS / "run_canaries.py").read_text(encoding="utf-8")
    amb = rc.ambiente_canario("/prefixo/de/teste")
    caso("o runner passa env=env_canario ao executar cada canario",
         "env=env_canario" in fonte
         and amb.get("PYTHONPYCACHEPREFIX") == "/prefixo/de/teste"
         and rc.ambiente_canario("/p", sem_escrita=True).get(
             "PYTHONDONTWRITEBYTECODE") == "1")
    caso("o runner purga bytecode antes de comecar",
         "purgar_bytecode(ROOT)" in fonte)

    print("-" * 50)
    ruins = [n for n, ok, _ in resultados if not ok]
    if ruins:
        print(f"RESULTADO: FAIL ({len(ruins)}) — {', '.join(ruins)}")
        return 1
    print(f"RESULTADO: PASS ({len(resultados)} verificacoes: o executor da suite nao pode "
          f"ser enganado por bytecode velho)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
