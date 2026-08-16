#!/usr/bin/env python3
"""Runner único dos canários do framework (ADR-040 — CI cross-platform).

CONTEXTO: os `tools/test_*.py` deste repo são **canários standalone** (exit 0 = PASS,
exit != 0 = FAIL) — vários executam trabalho em import-time e chamam `sys.exit()`, então
`pytest tools/` quebra na importação e foi rejeitado como entrypoint (ADR-040). Este runner
é o entrypoint canônico (local e CI): descobre cada `test_*.py`, roda como subprocesso com
o MESMO interpretador, agrega e devolve exit = nº de canários que falharam.

Um canário PODE, além disso, ser coletável por pytest (hoje: `test_squad_gate.py`, escrito
em `def test_*` com fixtures). Isso é permitido desde que ele traga um entrypoint
**stdlib-only** que execute os próprios testes — nunca delegando a `python -m pytest`, que
criaria dependência que o repo decidiu não ter e faria o ambiente reprovar o build. A 4ª
rodada de revisão do v1.79.0 pegou exatamente esse erro: a 1ª versão do entrypoint chamava
pytest e derrubou a CI nos 3 SOs com "No module named pytest".

Cross-platform por construção (ADR-040): nenhuma suposição de shell — só `sys.executable`.
Canários que dependem de pwsh/bash/jq se auto-marcam SKIP (exit 0) quando o shell falta,
então o runner nunca falha por ambiente — só por canário que efetivamente reprovou.

Uso:
    python tools/run_canaries.py            # roda todos os test_*.py de tools/
    python tools/run_canaries.py -v         # mostra stdout de cada canário
    python tools/run_canaries.py a b ...     # roda só os nomes/substrings dados

Exit 0 se todos passaram; N>0 = nº de canários que falharam.
"""
import atexit
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
SELF = os.path.basename(__file__)


def discover(filters):
    out = []
    for fn in sorted(os.listdir(TOOLS)):
        if not (fn.startswith("test_") and fn.endswith(".py")):
            continue
        if filters and not any(f in fn for f in filters):
            continue
        out.append(fn)
    return out


def _contar_testes_e_entrypoint(src):
    """(nº de funcoes `test_*`, tem bloco `if __name__ ==`?) — por AST, com fallback regex.

    Conta funcoes de topo E dentro de `if`/`try`/`with` de modulo (elas existem em globals()
    e sao coletadas pelo pytest), alem de metodos `test_*` de classes `Test*` — todas rodam
    sob pytest e portanto contam como teste que precisa de entrypoint.
    Fonte que nao parseia cai no regex antigo: nao e' motivo para o runner desistir.
    """
    import ast

    try:
        arvore = ast.parse(src)
    except SyntaxError:
        return len(re.findall(r"^def test_", src, re.M)), bool(
            re.search(r"^if __name__\s*==", src, re.M))

    def _e_teste(no):
        return (isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
                and no.name.startswith("test_"))

    def _contar(corpo, dentro_de_classe_teste=False):
        """So conta o que o pytest coletaria: funcao de modulo (inclusive dentro de
        if/try/with) e metodo de classe `Test*`. Funcao aninhada DENTRO de outra funcao
        nunca e' coletada — conta-la gerava FAIL(cego) falso (achado MENOR da 8a rodada)."""
        total = 0
        for no in corpo:
            if _e_teste(no):
                total += 1                      # nao desce: closures dentro dela nao contam
            elif isinstance(no, ast.ClassDef):
                if no.name.startswith("Test"):
                    total += _contar(no.body, True)
            elif isinstance(no, (ast.If, ast.Try, ast.With, ast.AsyncWith)):
                total += _contar(no.body, dentro_de_classe_teste)
                total += _contar(getattr(no, "orelse", []), dentro_de_classe_teste)
                total += _contar(getattr(no, "finalbody", []), dentro_de_classe_teste)
                for h in getattr(no, "handlers", []):
                    total += _contar(h.body, dentro_de_classe_teste)
        return total

    def _e_entrypoint(teste):
        # aceita `__name__ == "__main__"` E a forma invertida `"__main__" == __name__`
        if not isinstance(teste, ast.Compare):
            return False
        lados = [teste.left] + list(teste.comparators)
        return any(isinstance(x, ast.Name) and x.id == "__name__" for x in lados)

    n = _contar(arvore.body)
    entrypoint = any(isinstance(no, ast.If) and _e_entrypoint(no.test) for no in arvore.body)
    return n, entrypoint


# ---------------------------------------------------------------------------------
# BYTECODE VELHO FALSIFICA A SUITE (achado 2026-08-16, medido ao vivo nesta arvore).
# O Python decide reusar um `.pyc` comparando TAMANHO e HORARIO do fonte, e o horario
# tem resolucao de 1 SEGUNDO. Se um fonte mudar mantendo o mesmo numero de bytes e a
# gravacao cair no mesmo segundo do `.pyc`, o interpretador roda o codigo VELHO.
#
# Caso real: `test_autonomy_policy` FALHOU com `tools/autonomy_policy.py` identico ao
# commit — o `.pyc` guardava o bytecode de uma sondagem. O inverso e' pior: um canario
# pode passar VERDE sobre codigo que nao esta mais no disco.
#
# Duas travas, porque uma so seria confianca: nao escrever bytecode, e apagar o que
# porventura exista antes de comecar.
# ---------------------------------------------------------------------------------
# Nao basta `PYTHONDONTWRITEBYTECODE`: ele impede ESCREVER, nao impede LER um `.pyc` que ja
# exista — furo apontado pelo qa-critic e confirmado pelo canario deste arquivo, que reprovou
# a 1a versao desta correcao. `PYTHONPYCACHEPREFIX` apontando para um diretorio VAZIO resolve
# a leitura: com o prefixo definido, o interpretador procura cache SO' ali, e ali nao ha nada.
def ambiente_canario(prefixo_cache, sem_escrita=False):
    """Env que isola o canario de bytecode velho.

    O isolamento vem do PREFIXO NOVO por execucao da suite: com `PYTHONPYCACHEPREFIX`
    definido, o interpretador procura cache SO' ali, e ali comeca vazio — nenhum `.pyc`
    de antes pode ser lido, inclusive os que estejam ao lado do fonte.

    A escrita fica LIBERADA de proposito. Proibir tambem (`sem_escrita=True`) faz cada
    subprocesso recompilar a biblioteca padrao inteira: medido, a suite saltou de segundos
    para mais de dois minutos. Dentro de uma execucao os fontes nao mudam, entao reusar o
    cache do proprio prefixo e' seguro. `sem_escrita` existe para quem MUDA o fonte no meio
    da execucao — o caso do `audit_enforcement.py --provar`.
    """
    env = {**os.environ, "PYTHONPYCACHEPREFIX": str(prefixo_cache)}
    if sem_escrita:
        env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def purgar_bytecode(raiz):
    """Remove todo `__pycache__` sob `raiz`, menos o que estiver dentro de `.git`."""
    removidos = 0
    for atual, dirs, _ in os.walk(raiz):
        if ".git" in atual.split(os.sep):
            dirs[:] = []
            continue
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(atual, "__pycache__"), ignore_errors=True)
            dirs.remove("__pycache__")
            removidos += 1
    return removidos


def main(argv):
    verbose = "-v" in argv
    purgar_bytecode(ROOT)
    prefixo_cache = tempfile.mkdtemp(prefix="canario-pyc-")
    atexit.register(shutil.rmtree, prefixo_cache, True)
    env_canario = ambiente_canario(prefixo_cache)
    filters = [a for a in argv[1:] if not a.startswith("-")]
    canaries = discover(filters)
    if not canaries:
        print("nenhum canário test_*.py encontrado", file=sys.stderr)
        return 1

    failed, skipped, passed = [], [], []
    for fn in canaries:
        path = os.path.join(TOOLS, fn)
        # ---------------------------------------------------------------------
        # GUARD DE CANARIO CEGO (ADR-103 emenda 2 — achado da 3a rodada, 2026-08-13).
        # Este runner executa cada canario COMO SCRIPT e le o exit code. Um arquivo
        # pytest PURO (funcoes `def test_*` sem bloco `__main__`) so e' importado: as
        # funcoes sao definidas, nada e' chamado, o processo sai com 0 e o runner
        # reportava PASS — sem rodar UMA assercao. Caso real: test_squad_gate.py,
        # os testes do gate que governa o squad inteiro: verdes e nunca executados.
        # Deteccao estatica, deterministica e barata (regex no fonte); FALHA, nao avisa.
        # ---------------------------------------------------------------------
        # AST, nao regex (7a rodada do v1.79.0): `^def test_` contava linha dentro de
        # docstring como definicao, e um arquivo cujo texto de documentacao mostrasse um
        # exemplo virava FAIL(cego) falso. Texto nao e' codigo.
        try:
            src = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            src = ""
        n_testfn, tem_entrypoint = _contar_testes_e_entrypoint(src)
        if n_testfn and not tem_entrypoint:
            failed.append(fn)
            print(f"{'FAIL(cego)':9} {fn}")
            print(f"    | {n_testfn} funcao(oes) `def test_` e NENHUM bloco `if __name__ ==`.")
            print("    | Rodado como script, este arquivo nao executa assercao alguma —")
            print("    | passaria como PASS sem testar nada. Adicione um entrypoint")
            print("    | STDLIB-ONLY que execute os testes e propague o exit code.")
            print("    | NAO delegue a `python -m pytest`: o ADR-040 rejeitou pytest como")
            print("    | entrypoint e a 4a rodada do v1.79.0 mediu a CI caindo nos 3 SOs.")
            print("    | Modelo pronto: o bloco final de test_squad_gate.py.")
            continue
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
            # canario NUNCA espera stdin interativo: pipe herdado aberto = suite pendurada
            # (caso real 2026-06-11: test_repo_sync -> hook check_repo_sync.read(stdin) deadlock)
            stdin=subprocess.DEVNULL,
            env=env_canario,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        is_skip = proc.returncode == 0 and "SKIP" in out and "PASS" not in out.upper()
        if proc.returncode == 0:
            (skipped if is_skip else passed).append(fn)
            tag = "SKIP" if is_skip else "PASS"
        else:
            failed.append(fn)
            tag = f"FAIL({proc.returncode})"
        print(f"{tag:9} {fn}")
        if verbose or proc.returncode != 0:
            for line in out.strip().splitlines():
                print(f"    | {line}")

    print("-" * 50)
    print(f"RESULTADO: {len(passed)} PASS · {len(skipped)} SKIP · {len(failed)} FAIL "
          f"(de {len(canaries)} canários)")
    if failed:
        print("FALHARAM: " + ", ".join(failed))
    return len(failed)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
