#!/usr/bin/env python3
"""repo_mode.py — modo de operação DETERMINÍSTICO por identidade de repo (ADR-070/072).

Decide, por MECANISMO (não prosa), se a sessão é:
  - "dev"  : MASTER-CANÔNICO -> desenvolve o framework (ADRs, skills, WIP, history dev).
  - "user" : SOMBRA-EXPORT (premium/public/web) -> APLICA o framework a um domínio. NÃO desenvolve o
             framework, NÃO trata ADR/WIP, NÃO reconcilia history dev. Sync é automático (shadow_sync).
             ÚNICA ação de framework-dev permitida: relatório opt-in. Write-back bloqueado (shadow_write_guard).
  - default seguro: "user" (na dúvida NÃO desenvolve — conservador; clone ambíguo não é master).

Agnóstico de IA e de repo: chaveia no VERDITO (role), não em nome de repo — vale p/ premium/public de
QUALQUER IA (claude, gemini, futura). Embarca em todo shadow via export-clean (tools/).

SessionStart: injeta o modo + as guardas no contexto (o agente no shadow já sabe que é user-mode).
Uso:
  python tools/repo_mode.py            # SessionStart: injeta additionalContext
  python tools/repo_mode.py --mode     # imprime so 'user' | 'dev'
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_CONTEXT = (
    "[repo-mode] USER MODE (distribuição/shadow — premium/public/web). Esta sessão APLICA o framework "
    "a um DOMÍNIO; NÃO desenvolve o framework: não trata ADR, não reconcilia WIP/history de dev, não "
    "edita skills/núcleo. Sync com o origin é AUTOMÁTICO (shadow_sync — não pergunte como resolver). "
    "Write-back está bloqueado (shadow_write_guard). Única ação de framework-dev aqui: relatório opt-in. "
    "Para DESENVOLVER o framework, abra o repo MASTER. Comporte-se como modo-usuário desde o 1º turno."
)


def mode(classify=None):
    """Retorna 'dev' | 'user'. classify() injetável p/ teste."""
    try:
        if classify is None:
            sys.path.insert(0, os.path.join(ROOT, "tools"))
            import repo_identity
            classify = repo_identity.classify
        verdict = (classify() or {}).get("verdict")
    except Exception:
        return "user"  # fail-safe conservador: na dúvida não desenvolve
    if verdict == "MASTER-CANONICO":
        return "dev"
    return "user"  # SOMBRA-EXPORT, CLONE, FOREIGN, AMBIGUO -> não desenvolve


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    m = mode()
    if "--mode" in argv:
        print(m)
        return 0
    ctx = USER_CONTEXT if m == "user" else ""
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": ctx}}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
