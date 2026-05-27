# AGENTS.md — Framework Metacognitivo Agêntico

Roteador: AGENT-FRAMEWORK.md (v2.3) · Núcleo SSoT: _shared/ ·
Papéis de processo: .agent/skills/ · Regras: .agent/rules/ · Workflows: .agent/workflows/

## Papéis de processo (genéricos)
pmo · architect · developer · qa-critic · docops · explorer (read-only) · _template (molde).

## Regras sempre ativas
Ver .agent/rules/ (todas referenciam _shared/).

## Primeira ação obrigatória
/start-session

## Modos de execução (v1.7.0 — ADR-005)
3 níveis registrados em `~/.claude/framework-mode.json` com ratchet forward-only:
**default** (prompts conservadores) · **avançado** (blanket shell + ask em push/merge) · **autosuficiente** (`bypassPermissions` + deny mínimo). Reativação só quando `~/.claude/hooks/framework-sync.ps1` muda. Detalhe: `_shared/execution-modes/SKILL.md`.

## Auto-boot global (v1.8.0 — ADR-006)
Após `bootstrap.ps1`, o squad acorda automaticamente em qualquer IDE/projeto cujo owner do remote `origin` bata com `~/.claude/squad-owners.txt` (substring match). Fallback: `AGENTS.md` ou `.agent/` no projeto. Pular: `.claude/session.lock` ou `~/.claude/session.lock`.

## Aplicações
Domínios específicos (BI, regulado, etc.) NÃO ficam no núcleo — são criados clonando
.agent/skills/_template e vivem FORA do núcleo (no seu repositório).
Ver `exemplos/README.md` para o guia de criação.

## Roteador base
https://raw.githubusercontent.com/fabriciopsouza/metacognition-framework/main/AGENT-FRAMEWORK.md
