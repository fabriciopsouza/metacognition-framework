# CLAUDE.md — Entrada do Framework no Claude Code

> Claude Code lê este arquivo nativamente. É o ponto de entrada.
> Conteúdo equivale ao AGENTS.md (cross-tool); aqui é a versão Claude Code.

## Estrutura
- Roteador: `AGENT-FRAMEWORK.md` (v2.3) — decide o modo (contexto × complexidade).
- Núcleo SSoT: `_shared/` — regras transversais (fonte única; nunca duplicar).
- Papéis de processo (skills): `.agent/skills/` — pmo, architect, developer,
  qa-critic, docops, explorer, _template.
- Subagentes (isolamento real): `.claude/agents/` — explorer, qa-critic.
- Regras sempre ativas: `.agent/rules/`.
- Workflows: `.agent/workflows/`.
- Aplicações de domínio: vivem FORA do núcleo (clonar `.agent/skills/_template`); ver `exemplos/README.md`.

## Primeira ação obrigatória em toda sessão
/start-session   (abre a sessão pelo PMO; lê rules + briefing + history)

## Regras invioláveis (de _shared/, não redefinir)
1. Classificar afirmação relevante: CONFIRMADO | INFERIDO | DESCONHECIDO.
2. Anti-rename: não renomear nome aprovado sem ADR.
3. File-first: ler/inspecionar antes de assumir.
4. NÃO SEI direto — nunca inventar.

## Modos de execução (v1.7.0 — ADR-005)
O framework opera sob 1 de 3 níveis registrados em `~/.claude/framework-mode.json`:
- **default** — conservador, prompts para a maioria das ações shell.
- **avançado** — confia no shell em geral, pede só em git push/merge/pr.
- **autosuficiente** — `bypassPermissions`, só guard-rails absolutos no deny.

Ratchet forward-only: escalação livre (default→avançado→autosuficiente), downgrade só por edição manual do state file. Reativação dispara só quando `~/.claude/hooks/framework-sync.ps1` muda (hash trigger). Detalhe: `_shared/execution-modes/SKILL.md`.

## Auto-boot global (v1.8.0 — ADR-006)
Após `bootstrap.ps1`, o squad acorda automaticamente em qualquer IDE/projeto
cujo owner do remote `origin` bata com `~/.claude/squad-owners.txt` (substring
match case-insensitive). Fallback: marker explícito (`AGENTS.md` ou `.agent/`).
Pular sessão: `New-Item .claude/session.lock` (projeto) ou `~/.claude/session.lock` (global).
Adicionar owner: editar `~/.claude/squad-owners.txt`.

## Como ler skills
As skills de processo vivem em `.agent/skills/<nome>/SKILL.md` e o núcleo em
`_shared/<nome>/SKILL.md`. Carregue o SKILL.md relevante antes de agir. Para
auto-descoberta nativa do Claude Code, espelhe-as em `.claude/skills/` (ver guia/SETUP.md).

## Roteador base
https://raw.githubusercontent.com/fabriciopsouza/metacognition-framework/main/AGENT-FRAMEWORK.md
