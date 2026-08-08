#!/usr/bin/env python3
"""boot_brief.py — SessionStart: injeta O QUE JA ESTA DECIDIDO (ADR-101). Anti-repergunta.

GAP DE CAMPO (dono, 2026-08-07): *"muitas perguntas ja respondidas, elementos ja definidos, etc
sao perguntados ou ignorados em algumas sessoes; o modelo nao le a documentacao antes de iniciar
todos os trabalhos, resultando em retrabalho, presuncoes de premissas, esquecimento de regras,
quando tudo ja esta documentado e definido."*

POR QUE ACONTECIA: "leia a documentacao antes de comecar" era PROSA no CLAUDE.md — uma instrucao
que compete com o vies de progredir na tarefa e perde. E fora do repo-framework nem a prosa
chegava, porque o CLAUDE.md do framework nao esta la. O agente entao PERGUNTA o que ja estava
escrito, ou pior, PRESUME.

MECANISMO: o boot le o que existe no projeto (briefing, glossario, decisoes aceitas, regras,
trabalhos abertos) e injeta um INVENTARIO com os caminhos. Nao injeta o conteudo — injeta a
existencia e o ponteiro, para nao queimar contexto (ADR-029): "isto ja esta decidido AQUI".
Perguntar o que consta no inventario passa a ser erro visivel, nao esquecimento.

Fail-open e barato: so lista arquivos, nunca le documento grande inteiro.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_root, read_payload  # noqa: E402

# (rotulo, caminho relativo, o que este arquivo DECIDE)
SOURCES = [
    ("briefing", "docs/briefing.md", "objetivo, escopo IN/OUT, criterio de aceite"),
    ("glossario", ".agent/rules/00-glossario.md", "nomes/termos = fonte da verdade (anti-rename)"),
    ("mission", "mission.md", "product_type + escopo declarado"),
    ("mission", "docs/mission.md", "product_type + escopo declarado"),
    ("requirements", "docs/requirements.md", "spec elicitada pelo discovery"),
    ("correlacoes", ".agent/correlations.json", "artefatos que mudam juntos"),
    ("ambiente", ".agent/environment.json", "premissas de ambiente ja verificadas"),
]
DIRS = [
    ("decisoes (ADR)", "docs/adr", "decisoes ja tomadas — NAO reabrir sem ADR novo"),
    ("regras sempre-ativas", ".agent/rules", "regras do projeto"),
]
MAX_LIST = 12


def main():
    try:
        root = project_root(read_payload())
        lines = []

        for label, rel, decides in SOURCES:
            p = os.path.join(root, rel.replace("/", os.sep))
            if os.path.isfile(p):
                lines.append(f"- **{label}** — `{rel}` (decide: {decides})")

        for label, rel, decides in DIRS:
            d = os.path.join(root, rel.replace("/", os.sep))
            if not os.path.isdir(d):
                continue
            try:
                files = sorted(f for f in os.listdir(d) if f.lower().endswith(".md"))
            except OSError:
                continue
            if not files:
                continue
            shown = ", ".join(f"`{f}`" for f in files[:MAX_LIST])
            more = f" (+{len(files) - MAX_LIST})" if len(files) > MAX_LIST else ""
            lines.append(f"- **{label}** — `{rel}/`: {shown}{more} (decide: {decides})")

        if not lines:
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "SessionStart", "additionalContext": ""}}, ensure_ascii=False))
            return 0

        ctx = ("# [boot-brief ADR-101] JA DECIDIDO neste projeto — leia ANTES de perguntar\n\n"
               "Os artefatos abaixo EXISTEM. Perguntar ao dono o que esta neles, ou presumir "
               "premissa que eles ja fixam, e retrabalho — file-first (regra inviolavel 3):\n\n"
               + "\n".join(lines) +
               "\n\nLeia o que for pertinente a tarefa ANTES do primeiro tool call de dominio. "
               "Se algo estiver faltando, ai sim elicite — mas diga o que procurou.\n")
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "SessionStart", "additionalContext": ctx}}, ensure_ascii=False))
        return 0
    except Exception as e:  # noqa: BLE001 — boot nunca crasha
        sys.stderr.write(f"[boot-brief] warning (nao-bloqueante): {e}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
