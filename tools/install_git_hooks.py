#!/usr/bin/env python3
"""install_git_hooks — instala o `pre-commit` que roda o squad-gate antes de deixar commitar.

O QUE FECHA. O ADR-092 previu quatro peças e três existem: a matriz declarativa
(`behaviors/manifest.json`), o gate (`tools/squad_gate.py`) e o canário dele. Faltava a que dá
sentido às outras: **o gancho que faz o gate rodar sozinho**. Sem ele, o gate só roda se alguém
lembrar de rodar — que é a definição de prosa disfarçada de ferramenta.

Medido em 2026-08-16: `.git/hooks/pre-commit` não existia, e na CI o gate roda com
`|| echo "::warning::"` — ou seja, avisa e deixa passar. O mecanismo estava construído e desligado.

DECISÕES DE DESENHO, todas para o gancho não virar aquele que alguém desinstala:

- **Não bloqueia por ausência de Python nem por erro do próprio gate.** Só bloqueia quando o gate
  diz, com todas as letras, que falta evidência — e isso é conferido na MENSAGEM, não no código de
  saída. O `squad_gate.py` sai com 1 nos dois casos: quando bloqueia de propósito e quando quebra
  (exceção não tratada também termina o Python com 1). A primeira versão deste gancho confiava só
  no código, e o qa-critic mostrou que um manifesto corrompido barraria todo commit mentindo o
  motivo. Ferramenta quebrada não pode impedir alguém de commitar.
- **Escapatória declarada e visível:** `git commit --no-verify` continua funcionando. Um gate sem
  saída de emergência é desinstalado no primeiro aperto — e aí não protege mais nada. A saída fica
  registrada no próprio texto do bloqueio.
- **Não sobrescreve gancho alheio em silêncio.** Se já existe um `pre-commit` que não é nosso, o
  instalador recusa e diz o que fazer.
- **Desinstalável:** `--desinstalar` remove só o que este script escreveu.

Uso:
    python tools/install_git_hooks.py                 # instala
    python tools/install_git_hooks.py --verificar     # diz o estado, nao mexe em nada
    python tools/install_git_hooks.py --desinstalar   # remove
    python tools/install_git_hooks.py --repo DIR      # outra raiz (o canario usa isto)

Códigos de saída: 0 sucesso · 1 recusa consciente (gancho alheio, repo inválido).
"""
import argparse
import os
import stat
import subprocess
import sys
from pathlib import Path

RAIZ_PADRAO = Path(__file__).resolve().parent.parent
MARCA = "# gerado-por: tools/install_git_hooks.py (ADR-092)"

CORPO = f"""#!/bin/sh
{MARCA}
#
# Roda o squad-gate sobre os arquivos em stage. Bloqueia SO' quando o gate diz que
# falta evidencia de QA para o tipo de mudanca. Ferramenta ausente ou quebrada NAO
# impede commit — gate que trava por acidente e' gate que alguem desinstala.

if ! command -v python >/dev/null 2>&1; then
    exit 0
fi

raiz=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -f "$raiz/tools/squad_gate.py" ] || exit 0

saida=$(python "$raiz/tools/squad_gate.py" 2>&1)
codigo=$?

if [ $codigo -eq 0 ]; then
    exit 0
fi

# FALHA PELO MOTIVO CERTO, nao por codigo de saida. O `squad_gate.py` sai com 1 tanto
# quando bloqueia de proposito quanto quando QUEBRA — excecao nao tratada termina o
# Python com 1 tambem. Confiar so' no codigo faria um manifesto corrompido barrar todo
# commit dizendo "falta evidencia de QA", mentindo sobre o motivo. Achado ALTO do
# qa-critic (Sonnet, 2026-08-16), que apontou a contradicao com o desenho declarado
# neste mesmo arquivo. E' a mesma regra do campo `espera` do ADR-106.
case "$saida" in
    *"[squad-gate] BLOQUEADO"*) ;;   # o gate falou; segue para o bloqueio
    *)
        echo "[squad-gate] nao consegui avaliar (codigo $codigo) — commit liberado."
        echo "$saida" | head -5
        exit 0
        ;;
esac

echo "$saida"
echo ""
echo "[squad-gate] commit BLOQUEADO: falta evidencia de QA para o que esta em stage."
echo "  Registre o veredito:  python tools/qa_evidence.py --from-json <arquivo>"
echo "  Ou siga sem o gate:   git commit --no-verify"
exit 1
"""


def _caminho_hooks(raiz):
    """Respeita `core.hooksPath`, que muda onde o git procura os ganchos."""
    try:
        r = subprocess.run(["git", "-C", str(raiz), "config", "--get", "core.hooksPath"],
                           capture_output=True, text=True, timeout=15)
        personalizado = (r.stdout or "").strip()
    except Exception:
        personalizado = ""
    if personalizado:
        p = Path(personalizado)
        return p if p.is_absolute() else Path(raiz) / p
    return Path(raiz) / ".git" / "hooks"


def estado(raiz):
    """('ausente'|'nosso'|'alheio', caminho) — sem efeito colateral; e' o que o canario usa."""
    alvo = _caminho_hooks(raiz) / "pre-commit"
    if not alvo.is_file():
        return "ausente", alvo
    try:
        texto = alvo.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "alheio", alvo
    return ("nosso" if MARCA in texto else "alheio"), alvo


def instalar(raiz):
    situacao, alvo = estado(raiz)
    if situacao == "alheio":
        print(f"[install-hooks] RECUSADO: ja existe um pre-commit que nao e' nosso em {alvo}")
        print("  Nao sobrescrevo gancho alheio. Junte os dois a mao, ou remova o existente.")
        return 1
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(CORPO, encoding="utf-8", newline="\n")
    try:  # no Windows o bit de execucao e' inocuo; no resto e' obrigatorio
        alvo.chmod(alvo.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        pass
    print(f"[install-hooks] pre-commit instalado em {alvo}")
    print("  Bloqueia so' por falta de evidencia de QA. Escapatoria: git commit --no-verify")
    return 0


def desinstalar(raiz):
    situacao, alvo = estado(raiz)
    if situacao == "ausente":
        print("[install-hooks] nada a remover.")
        return 0
    if situacao == "alheio":
        print(f"[install-hooks] RECUSADO: o pre-commit em {alvo} nao foi escrito por este script.")
        return 1
    os.remove(alvo)
    print(f"[install-hooks] removido {alvo}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Instala o pre-commit do squad-gate (ADR-092).")
    ap.add_argument("--repo", default=str(RAIZ_PADRAO))
    ap.add_argument("--verificar", action="store_true", help="so reporta o estado")
    ap.add_argument("--desinstalar", action="store_true")
    a = ap.parse_args(argv)

    raiz = Path(a.repo)
    if not (raiz / ".git").exists():
        print(f"[install-hooks] {raiz} nao e' um repositorio git.")
        return 1

    if a.verificar:
        situacao, alvo = estado(raiz)
        legenda = {"ausente": "NAO instalado", "nosso": "instalado por este script",
                   "alheio": "existe um pre-commit de outra origem"}[situacao]
        print(f"[install-hooks] {legenda} — {alvo}")
        return 0
    return desinstalar(raiz) if a.desinstalar else instalar(raiz)


if __name__ == "__main__":
    sys.exit(main())
