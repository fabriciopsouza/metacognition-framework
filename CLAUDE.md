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

## Régua §0 — GANHO LÍQUIDO (v1.9.0 — ADR-007)
Princípio 10 do `AGENT-FRAMEWORK.md` §6: adição pura é rejeitada por padrão. Mudança só passa se (a) funde/remove ≥ adiciona, (b) reduz tokens/latência, ou (c) destrava eval inalcançável editando existente. Antes de criar arquivo/skill/regra: "o que dá para remover, fundir, simplificar?"

## Discovery sub-modo pesquisa-cascata (v1.9.0 — ADR-007)
Quando o trabalho exige pesquisa antes da spec (pergunta de fundo sem fonte canônica, e a resposta destrava decisão), o discovery carrega `pesquisa-cascata.md` (companion sob demanda). Pipeline 9 passos: decompor → buscar via explorer → refletir → ramificar (≤2 rodadas) → sintetizar → **ataque anti-raso obrigatório** → refinar → handoff. Output: `research-brief.md`.

## Método sênior de discovery — reforço transversal (v1.10.0 — ADR-009; passo 9 RRC v1.11.0 — ADR-010)
Quando há **fonte canônica/normativa citada** (norma regulatória, spec oficial, padrão técnico, regra de negócio com peso semântico declarado), o discovery carrega `metodo-senior.md` (companion sob demanda) em adição ao sub-modo ativo. **9 passos auditáveis:** mapeamento + **vigência** + complementações + cross-domain + pertinência + elicitação + classificação + adversarial + **coherence pass (RRC)**. Domain-agnóstico. Output ganha **3 seções obrigatórias**: Antecipações + Backlog de elicitação + **Gaps não-bloqueantes** (§7-8 + sub-§ do `research-brief.md`). Princípio 11 do `AGENT-FRAMEWORK.md` §6 (reescrito em v1.11.0: "Observação meta-cognitiva — captura estruturada de feedback") + method-audit autônomo no `/checkpoint`.

## Framework agnóstico de domínio — discovery declara o escopo (v1.11.0 — ADR-010)
O núcleo NÃO carrega listas hardcoded de normas/convenções/regras de domínio. Quando há sinal de contexto especializado, o **discovery pergunta explicitamente ao dono** (lote temático obrigatório, passo 6 do `discovery/SKILL.md`): *(a) regulado? quais normas? (b) decisão de alto impacto? (c) regra de negócio com peso semântico? (d) gaps não-bloqueantes?* A resposta vai para o `requirements.md`/`research-brief.md` em `## Escopo declarado pelo discovery` e dispara os gates downstream (`high-stakes-gate`, reforço sênior, roteamento reflexivo). **Sem declaração afirmativa → defaults agnósticos.** Anti-vazamento cross-projeto: o agente NÃO importa convenção/norma de outra sessão/projeto sem confirmação. **Gaps não-bloqueantes são flagados, não silenciados** (abordagem sênior). HITL fica desacoplado, no eixo `execution-modes` (ADR-005), sem duplicação. Princípio 12 do `AGENT-FRAMEWORK.md` §6.

## Como ler skills
As skills de processo vivem em `.agent/skills/<nome>/SKILL.md` e o núcleo em
`_shared/<nome>/SKILL.md`. Carregue o SKILL.md relevante antes de agir. Para
auto-descoberta nativa do Claude Code, espelhe-as em `.claude/skills/` (ver guia/SETUP.md).

## Roteador base
https://raw.githubusercontent.com/fabriciopsouza/metacognition-framework/main/AGENT-FRAMEWORK.md
