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
/start-session  **(ou diga "iniciar")** — abre a sessão pelo PMO (lê rules + briefing + history). Comando registrado em `.claude/commands/start-session.md` (ADR-024). **Não é rígido:** o agente também elicita por prosa/perguntas/inspeção de pastas. Por projeto você preenche só 2 arquivos: `docs/briefing.md` + `.agent/rules/00-glossario.md`.

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
O núcleo NÃO carrega listas hardcoded de normas/convenções/regras de domínio. Quando há sinal de contexto especializado, o **discovery pergunta explicitamente ao dono** (lote temático obrigatório, passo 6 do `discovery/SKILL.md`): *(a) regulado? quais normas? (b) decisão de alto impacto? (c) regra de negócio com peso semântico? (d) gaps não-bloqueantes? (e) alimenta outra sessão/agente? (ADR-012 v1.13.0)* A resposta vai para o `requirements.md`/`research-brief.md` em `## Escopo declarado pelo discovery` e dispara os gates downstream (`high-stakes-gate`, reforço sênior, roteamento reflexivo). **Sem declaração afirmativa → defaults agnósticos.** Anti-vazamento cross-projeto: o agente NÃO importa convenção/norma de outra sessão/projeto sem confirmação. **Gaps não-bloqueantes são flagados, não silenciados** (abordagem sênior). HITL fica desacoplado, no eixo `execution-modes` (ADR-005), sem duplicação. Princípio 12 do `AGENT-FRAMEWORK.md` §6.

## Handoff cross-sessão obrigatório quando declarado (v1.13.0 — ADR-012)
Quando `discovery` passo 6(e) declara que entrega **alimenta outra sessão/agente** (relatório downstream, pipeline, transferência de contexto), o **Pacote de handoff cross-sessão** (`_shared/metacognition-core` §Pacote) é entregável OBRIGATÓRIO via J5 (docops → release). Conteúdo mínimo: artefato consumível com versão; localização (repo/URL/path + branch/commit/PR); acesso (visibilidade + permissões); prompt pronto-para-colar; pendências herdadas. **Teste binário:** outra sessão começa **sem perguntar nada de volta**? Sem declaração afirmativa → defaults agnósticos. Princípio 14 do `AGENT-FRAMEWORK.md` §6. **+rules #6 (RCA gate) e #7 (cobertura temporal pós-J4) em qa-critic SKILL.**

## Arquitetura bicelular de QA — junções binárias + process-critic com rewind (v1.12.0 — ADR-011)
O fluxo do squad (PMO → discovery → architect → developer → qa-critic → docops → release) tem **6 junções (J0-J5)** com artefato-gate + critério binário declarados em `/handoff` workflow. **DENTRO da junção**: iterações ilimitadas até PASS binário (emendas no mesmo artefato via STATUS-field). **ENTRE junções**: forward-only após PASS (circuit-breaker contra loop eterno). **Process-critic adversarial** (qa-critic em subagente isolado) roda ao final de cada **BLOCO APROVADO** + on-demand + opcional em `/checkpoint` substantivo; detém poder de **rewind cascata** a qualquer junção anterior. **TODO QA é adversarial** (hipótese default = bug). **Política SUPLANTA × EMENDA**: §Decisão/§Alternativas muda → SUPLANTA novo ADR + `Substituído por:`; §Implementação/§Consequências muda → EMENDA in-place via STATUS-field. Within-junction rounds = EMENDA (não conta como rewind). Princípio 13 do `AGENT-FRAMEWORK.md` §6.

## Runtime hooks + entrega de produto (v1.21.0 — ADR-021/022/023)
Mecanismos de runtime (prosa→mecanismo) e a camada de entrega de produto, **sem refatorar o núcleo agnóstico**:
- **`compaction-gate`** (PreCompact, ADR-021): bloqueia compaction sem digest persistido (`history.md` sem checkpoint); fail-open; mecaniza o ADR-016.
- **`mission-gate`** (SessionStart, ADR-022): declara/confirma `product_type` + escopo (funde com discovery passo 6(f)), confirmação proporcional ao **modo de execução** (ADR-005: autosuficiente confirma 1× no briefing). Taxonomia de tipos é da **aplicação** (agnóstico). `mission.md` é o lar do escopo declarado.
- **App `exemplos/dominio-software/`** (ADR-023): distribuição especializada (demonstração viva) com `ux-designer` + `evals-engineer` — o framework **culmina em produto** de software/dados. `governance-lead`/`skill-librarian` NÃO criados (cobertos por `high-stakes-gate`/`action-safety` e pelo campo `classe`). Núcleo `_shared/` inalterado.

## Como ler skills
As skills de processo vivem em `.agent/skills/<nome>/SKILL.md` e o núcleo em
`_shared/<nome>/SKILL.md`. Carregue o SKILL.md relevante antes de agir. Para
auto-descoberta nativa do Claude Code, espelhe-as em `.claude/skills/` (ver guia/SETUP.md).

## Roteador base
https://raw.githubusercontent.com/fabriciopsouza/metacognition-framework/main/AGENT-FRAMEWORK.md
