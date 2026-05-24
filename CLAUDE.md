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
- Aplicações de domínio (exemplos): `exemplos/` — NÃO é núcleo.

## Primeira ação obrigatória em toda sessão
/start-session   (abre a sessão pelo PMO; lê rules + briefing + history)

## Regras invioláveis (de _shared/, não redefinir)
1. Classificar afirmação relevante: CONFIRMADO | INFERIDO | DESCONHECIDO.
2. Anti-rename: não renomear nome aprovado sem ADR.
3. File-first: ler/inspecionar antes de assumir.
4. NÃO SEI direto — nunca inventar.

## Como ler skills
As skills de processo vivem em `.agent/skills/<nome>/SKILL.md` e o núcleo em
`_shared/<nome>/SKILL.md`. Carregue o SKILL.md relevante antes de agir. Para
auto-descoberta nativa do Claude Code, espelhe-as em `.claude/skills/` (ver guia/SETUP.md).

## Roteador base
https://raw.githubusercontent.com/fabriciopsouza/metacognition-framework/main/AGENT-FRAMEWORK.md
