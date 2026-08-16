#!/usr/bin/env python3
"""Canário do `bootstrap.py --check` — a verificação que diz se a instalação funciona.

CONTEXTO. O `--check` antigo respondia duas perguntas (PowerShell roda? hooks ligados?) e chamava
aquilo de diagnóstico. Quem clonava em outra máquina descobria o que faltava **errando, um erro
por vez** — e o pedido do dono foi um runbook que permita instalar em qualquer PC *sem erros*.
Um runbook em prosa não garante isso; o que garante é a verificação recusar instalação quebrada.

O QUE ESTE CANÁRIO PROTEGE. Que a verificação de fato **reprove** o que está quebrado. Uma
verificação que aprova tudo é pior que nenhuma: dá confiança sem base — a classe de defeito que
este repositório persegue desde o ADR-106.

Uso: python tools/test_bootstrap_check.py   (exit 0 PASS; 1 se a verificação aprovar o quebrado)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import bootstrap  # noqa: E402

resultados = []


def caso(nome, ok, detalhe=""):
    resultados.append((nome, ok))
    print(f"  [{'PASS' if ok else 'FALHA'}] {nome}")
    if detalhe and not ok:
        print(f"          {detalhe}")


def _instalacao(raiz, *, com_git=True, faltando=()):
    """Monta uma instalação de mentira, opcionalmente quebrada de um jeito específico."""
    raiz = Path(raiz)
    (raiz / "tools").mkdir(parents=True, exist_ok=True)
    (raiz / "behaviors").mkdir(parents=True, exist_ok=True)
    (raiz / ".claude").mkdir(parents=True, exist_ok=True)
    arquivos = {
        "tools/run_canaries.py": "import sys; sys.exit(0)\n",
        "capabilities.json": '{"capabilities": []}\n',
        "behaviors/manifest.json": '{"matriz": []}\n',
        "CLAUDE.md": "# entrada\n",
    }
    for rel, conteudo in arquivos.items():
        if rel in faltando:
            continue
        (raiz / rel).write_text(conteudo, encoding="utf-8")
    (raiz / ".claude" / "settings.json").write_text('{"hooks": {}}', encoding="utf-8")
    if com_git:
        subprocess.run(["git", "init", "-q", str(raiz)], capture_output=True)
        subprocess.run(["git", "-C", str(raiz), "add", "-A"], capture_output=True)
        subprocess.run(["git", "-C", str(raiz), "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "inicial"], capture_output=True)
    return raiz


def bloqueios(raiz):
    return [item for nivel, item, _ in bootstrap.verificar(raiz) if nivel.strip() == "BLOQUEIA"]


def main():
    print("bootstrap --check: reprova a instalacao quebrada, aprova a inteira")

    with tempfile.TemporaryDirectory(prefix="bs-ok-") as t:
        r = _instalacao(t)
        caso("instalacao completa nao tem bloqueio", not bloqueios(r),
             f"bloqueou: {bloqueios(r)}")

    with tempfile.TemporaryDirectory(prefix="bs-zip-") as t:
        r = _instalacao(t, com_git=False)
        b = bloqueios(r)
        caso("baixar o .zip em vez de clonar e' BLOQUEIO",
             any("repositorio git" in x for x in b),
             f"bloqueios: {b} — varios gates leem historico; sem .git eles mentem")

    for rel, apelido in (("tools/run_canaries.py", "o portao do repo"),
                         ("capabilities.json", "o registro de capacidades"),
                         ("behaviors/manifest.json", "a matriz de papeis"),
                         ("CLAUDE.md", "a entrada do framework")):
        with tempfile.TemporaryDirectory(prefix="bs-falta-") as t:
            r = _instalacao(t, faltando=(rel,))
            caso(f"clone sem {rel} ({apelido}) e' BLOQUEIO",
                 any(rel in x for x in bloqueios(r)))

    with tempfile.TemporaryDirectory(prefix="bs-json-ruim-") as t:
        r = _instalacao(t)
        (r / ".claude" / "settings.json").write_text("{ isto nao e json", encoding="utf-8")
        caso("settings.json invalido e' BLOQUEIO",
             any("settings.json invalido" in x for x in bloqueios(r)),
             "arquivo de configuracao corrompido faz o agente iniciar sem gate nenhum")

    with tempfile.TemporaryDirectory(prefix="bs-avisa-") as t:
        r = _instalacao(t)
        (r / ".claude" / "settings.json").unlink()
        pend = bootstrap.verificar(r)
        niveis = {n.strip() for n, _, _ in pend}
        caso("sem settings.json e' AVISO, nao bloqueio",
             "AVISA" in niveis and "BLOQUEIA" not in niveis,
             f"niveis: {niveis} — da' para instalar depois; nao impede o clone de existir")

    with tempfile.TemporaryDirectory(prefix="bs-como-") as t:
        r = _instalacao(t, com_git=False)
        caso("toda pendencia diz COMO resolver",
             all(str(como).strip() for _, _, como in bootstrap.verificar(r)),
             "pendencia sem saida e' reclamacao, nao diagnostico")

    print("-" * 50)
    ruins = [n for n, ok in resultados if not ok]
    if ruins:
        print(f"RESULTADO: FAIL ({len(ruins)}) — {', '.join(ruins)}")
        return 1
    print(f"RESULTADO: PASS ({len(resultados)} verificacoes: instalacao quebrada nao passa por boa)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
