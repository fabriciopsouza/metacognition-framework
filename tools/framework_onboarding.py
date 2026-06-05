#!/usr/bin/env python3
"""framework_onboarding.py — detecção de 1ª abertura do REPO-FRAMEWORK (instalador) — ADR-067.

O repo-framework é o INSTALADOR, não um workspace. Na 1ª abertura na IDE, o agente deve apresentar
um popup (AskUserQuestion) orientando: USAR (instala global + feche e abra seu projeto — auto-boot
ADR-006) ou DESENVOLVER (fica). Este módulo é a parte MECANIZÁVEL (o popup é ato do agente — gate
anunciado ADR-047): detecta o repo-framework + marca 1x (não re-pergunta).

CLI:
  python tools/framework_onboarding.py --check        # diz se precisa onboarding (+ link)
  python tools/framework_onboarding.py --mark use|dev  # grava o marker (não re-pergunta)
"""
import argparse
import json
import os
import sys

SETUP_LINK = "guia/SETUP.md"


def repo_root(start=None):
    cur = os.path.abspath(start or os.getcwd())
    while True:
        if os.path.isdir(os.path.join(cur, ".git")) or os.path.isfile(os.path.join(cur, "AGENT-FRAMEWORK.md")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return os.path.abspath(start or os.getcwd())
        cur = parent


def is_framework_repo(root=None):
    """É o repo-FONTE do framework (instalador), não um projeto que o USA. Assinatura: AGENT-FRAMEWORK.md
    + _shared/ + tools/web_export.py na raiz (o gerador das distros — só existe na fonte)."""
    root = root or repo_root()
    return (os.path.isfile(os.path.join(root, "AGENT-FRAMEWORK.md"))
            and os.path.isdir(os.path.join(root, "_shared"))
            and os.path.isfile(os.path.join(root, "tools", "web_export.py")))


def _marker(home=None):
    return os.path.join(home or os.path.expanduser("~"), ".claude", ".framework-onboarded")


def onboarding_done(home=None):
    return os.path.isfile(_marker(home))


def needs_onboarding(root=None, home=None):
    """Popup de onboarding só na 1ª abertura DO REPO-FRAMEWORK + se ainda não onboardado."""
    return is_framework_repo(root) and not onboarding_done(home)


def mark_onboarded(mode, home=None):
    """mode = 'use' (vai usar nos projetos) | 'dev' (vai desenvolver o framework). Idempotente."""
    if mode not in ("use", "dev"):
        return False
    mk = _marker(home)
    os.makedirs(os.path.dirname(mk), exist_ok=True)
    with open(mk, "w", encoding="utf-8") as fh:
        json.dump({"onboarded": True, "mode": mode, "adr": "067"}, fh, ensure_ascii=True)
    return True


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--mark", choices=["use", "dev"])
    a = ap.parse_args(argv[1:])
    root = repo_root()
    if a.mark:
        mark_onboarded(a.mark)
        print(f"onboarding marcado: mode={a.mark} (ADR-067). Nao re-pergunta.")
        return 0
    need = needs_onboarding(root)
    print(f"framework_repo={is_framework_repo(root)} · onboarded={onboarding_done()} · "
          f"precisa_popup={'SIM' if need else 'nao'}" + (f" · instrucoes={SETUP_LINK}" if need else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
