#!/usr/bin/env python3
"""Resolvedor UNICO da raiz do PROJETO em que o agente esta trabalhando (ADR-101).

PROBLEMA (achado 2026-08-07, sessao de auditoria do dono): os gates Python derivavam a raiz de
`__file__` -> isso aponta para o **repo do framework**, nao para o repo que o usuario abriu.
Enquanto os hooks rodavam so no proprio repo-framework, os dois coincidiam e o bug era invisivel.
Ao wirar os gates GLOBALMENTE (ADR-101), passam a divergir: o gate auditaria o framework enquanto
o dono trabalha em outro projeto — falso-OK silencioso, que e pior que gate ausente.

Tres hooks ja resolviam isso, cada um de um jeito diferente (`check_repo_sync`, `prepush_sync_guard`,
`shadow_write_guard`). Este modulo FUNDE as tres formas numa so (regua §0, porta (a)).

PRECEDENCIA (a mais especifica vence):
  1. payload["cwd"]              — o Claude Code informa o cwd real no JSON do hook
  2. $CLAUDE_PROJECT_DIR         — variavel oficial do harness
  3. os.getcwd()                 — fallback do processo
  4. raiz do framework           — ultimo recurso (uso como ferramenta local, sem harness)

`framework_root()` continua apontando para o repo do framework — usado para ler ASSETS do proprio
framework (manifestos, catalogos), nunca para julgar o estado do projeto do usuario.
"""
import json
import os
import sys

# .../tools/hooks/_project.py -> sobe 3 = raiz do repo-framework
_FRAMEWORK_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def framework_root():
    """Raiz do repo-FRAMEWORK (onde vivem os assets do framework). Nunca o projeto do usuario."""
    return _FRAMEWORK_ROOT


def _valid_dir(p):
    try:
        return bool(p) and os.path.isdir(p)
    except (OSError, ValueError, TypeError):
        return False


def project_root(payload=None):
    """Raiz do PROJETO em que o agente trabalha AGORA. Ver precedencia no docstring do modulo."""
    if isinstance(payload, dict):
        cwd = payload.get("cwd")
        if _valid_dir(cwd):
            return os.path.abspath(cwd)
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if _valid_dir(env):
        return os.path.abspath(env)
    try:
        cwd = os.getcwd()
    except OSError:  # cwd apagado sob o processo
        cwd = None
    if _valid_dir(cwd):
        return os.path.abspath(cwd)
    return _FRAMEWORK_ROOT


def read_payload():
    """Le o JSON do hook no stdin. Fail-soft: {} se vazio/invalido/nao-tty (gate nunca crasha)."""
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return {}
        raw = sys.stdin.read()
    except (OSError, ValueError):
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def is_framework_repo(root):
    """True se `root` e o proprio repo-framework (tem o roteador na raiz). Alguns gates
    (agnosticismo do nucleo, repo_mode) so fazem sentido la — noutro projeto seriam ruido."""
    return os.path.isfile(os.path.join(root, "AGENT-FRAMEWORK.md"))
