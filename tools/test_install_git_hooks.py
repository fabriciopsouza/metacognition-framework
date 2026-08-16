#!/usr/bin/env python3
"""Canário do install_git_hooks (ADR-092) — o gancho que faz o gate rodar sozinho.

CONTEXTO. O ADR-092 previu quatro peças; três existiam e a quarta — o instalador do gancho —
nunca foi escrita. Sem ela, o gate do squad só roda se alguém lembrar de rodar, que é exatamente
a "prosa disfarçada de ferramenta" que o ADR combate. Medido em 2026-08-16: `.git/hooks/pre-commit`
não existia neste repo.

O QUE ESTE CANÁRIO PROTEGE. Três propriedades que, se quebrarem, transformam o gancho em
armadilha: não sobrescrever gancho alheio, ser removível, e respeitar `core.hooksPath` (que muda
onde o git procura os ganchos — instalar no lugar errado dá a falsa sensação de estar protegido).

Uso: python tools/test_install_git_hooks.py   (exit 0 PASS; 1 se o instalador for inseguro)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import install_git_hooks as igh  # noqa: E402

resultados = []


def caso(nome, ok, detalhe=""):
    resultados.append((nome, ok))
    print(f"  [{'PASS' if ok else 'FALHA'}] {nome}")
    if detalhe and not ok:
        print(f"          {detalhe}")


def _repo(raiz):
    subprocess.run(["git", "init", "-q", str(raiz)], capture_output=True)
    return Path(raiz)


def main():
    print("install_git_hooks: instala, recusa sobrescrever alheio, desinstala, respeita hooksPath")

    with tempfile.TemporaryDirectory(prefix="hooks-ok-") as tmp:
        r = _repo(tmp)
        caso("antes de instalar, reporta ausente", igh.estado(r)[0] == "ausente")

        rc = igh.instalar(r)
        situacao, alvo = igh.estado(r)
        caso("instala e passa a reportar como nosso", rc == 0 and situacao == "nosso",
             f"rc={rc} situacao={situacao}")

        corpo = alvo.read_text(encoding="utf-8")
        caso("o gancho chama o squad_gate", "squad_gate.py" in corpo)
        caso("o gancho declara a escapatoria no texto do bloqueio",
             "--no-verify" in corpo,
             "gate sem saida de emergencia e' gate desinstalado no primeiro aperto")
        caso("o gancho NAO bloqueia quando falta python",
             "command -v python" in corpo and "exit 0" in corpo)
        # Achado ALTO do qa-critic: o squad_gate sai com 1 tanto ao bloquear de proposito
        # quanto ao QUEBRAR (excecao nao tratada termina o Python com 1). Conferir so' o
        # codigo faria um manifesto corrompido barrar todo commit mentindo o motivo.
        caso("o gancho exige a MENSAGEM do gate, nao so' o codigo de saida",
             '[squad-gate] BLOQUEADO' in corpo and "case " in corpo,
             "codigo 1 sem a mensagem = gate quebrado, e gate quebrado nao barra ninguem")
        caso("e libera explicitamente quando o gate quebra",
             "nao consegui avaliar" in corpo and "exit 0" in corpo)

        # instalar duas vezes e' seguro: reconhece o proprio e sobrescreve sem reclamar
        caso("instalar de novo e' idempotente", igh.instalar(r) == 0 and igh.estado(r)[0] == "nosso")

        caso("desinstala o que instalou", igh.desinstalar(r) == 0
             and igh.estado(r)[0] == "ausente")
        caso("desinstalar de novo nao quebra", igh.desinstalar(r) == 0)

    with tempfile.TemporaryDirectory(prefix="hooks-alheio-") as tmp:
        r = _repo(tmp)
        alheio = r / ".git" / "hooks" / "pre-commit"
        alheio.parent.mkdir(parents=True, exist_ok=True)
        alheio.write_text("#!/bin/sh\necho gancho de outra pessoa\n", encoding="utf-8")
        caso("reconhece gancho alheio", igh.estado(r)[0] == "alheio")
        caso("RECUSA sobrescrever gancho alheio", igh.instalar(r) == 1)
        caso("e nao mexeu no arquivo alheio",
             "outra pessoa" in alheio.read_text(encoding="utf-8"))
        caso("RECUSA desinstalar gancho alheio", igh.desinstalar(r) == 1)

    with tempfile.TemporaryDirectory(prefix="hooks-path-") as tmp:
        r = _repo(tmp)
        # `core.hooksPath` redireciona onde o git procura. Instalar em .git/hooks nesse caso
        # daria falsa sensacao de protecao: o git nunca leria o arquivo.
        outro = r / "ganchos-personalizados"
        subprocess.run(["git", "-C", str(r), "config", "core.hooksPath", "ganchos-personalizados"],
                       capture_output=True)
        igh.instalar(r)
        caso("respeita core.hooksPath e instala onde o git de fato le",
             (outro / "pre-commit").is_file() and not (r / ".git" / "hooks" / "pre-commit").is_file(),
             f"esperado em {outro / 'pre-commit'}")

    with tempfile.TemporaryDirectory(prefix="hooks-nao-repo-") as tmp:
        caso("recusa diretorio que nao e' repositorio git",
             igh.main(["--repo", tmp]) == 1)

    print("-" * 50)
    ruins = [n for n, ok in resultados if not ok]
    if ruins:
        print(f"RESULTADO: FAIL ({len(ruins)}) — {', '.join(ruins)}")
        return 1
    print(f"RESULTADO: PASS ({len(resultados)} verificacoes: o gancho instala onde o git le, "
          f"nao atropela ninguem e sai quando mandam)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
