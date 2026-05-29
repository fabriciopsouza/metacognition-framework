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

## Régua §0 — GANHO LÍQUIDO (v1.9.0 — ADR-007)
Princípio 10 do `AGENT-FRAMEWORK.md` §6: adição pura é rejeitada. Aceitar só se (a) funde/remove ≥ adiciona, (b) reduz tokens/latência, ou (c) destrava eval inalcançável editando existente. Sub-modo `pesquisa-cascata` do discovery (sob demanda) é a primeira aplicação.

## Método sênior de discovery — reforço transversal (v1.10.0 — ADR-009; passo 9 RRC v1.11.0 — ADR-010)
Quando há **fonte canônica/normativa citada**, o discovery carrega `metodo-senior.md` (companion sob demanda). **9 passos:** mapeamento + **vigência** + complementações + cross-domain + pertinência + elicitação + classificação + adversarial + **coherence pass (RRC)**. Domain-agnóstico. Output ganha **3 seções obrigatórias**: Antecipações + Backlog + **Gaps não-bloqueantes**. Princípio 11 reescrito em v1.11.0 (observação meta-cognitiva, não auto-observação dura) + method-audit autônomo no `/checkpoint`.

## Framework agnóstico — discovery declara escopo (v1.11.0 — ADR-010)
Núcleo NÃO carrega listas hardcoded de normas/convenções de domínio. Discovery pergunta explicitamente: (a) regulado? quais normas? (b) alto-risco? (c) regra com semântica? (d) gaps não-bloqueantes? Respostas vão para `## Escopo declarado pelo discovery` no output e disparam gates downstream (`high-stakes-gate`, reforço sênior, roteamento reflexivo). Sem declaração → defaults agnósticos. **Anti-vazamento cross-projeto**: não importar convenção/norma de outra sessão sem confirmação. **Gaps não-bloqueantes flagados, não silenciados** (abordagem sênior). HITL via `execution-modes` (ADR-005). Princípio 12 do §6.

## Handoff cross-sessão obrigatório quando declarado (v1.13.0 — ADR-012)
discovery passo 6(e) "alimenta outra sessão?" → SE SIM, Pacote de handoff (`metacognition-core` §Pacote) é entregável obrigatório via J5. Conteúdo mínimo: artefato+versão, localização, acesso, prompt pronto-para-colar, pendências. Teste binário: outra sessão começa sem perguntar nada? Princípio 14 §6. +qa-critic rules #6 (RCA gate) e #7 (cobertura temporal pós-J4).

## QA bicelular — junções binárias + process-critic com rewind (v1.12.0 — ADR-011)
6 junções no fluxo squad (J0-J5) com artefato-gate + critério binário declarados em `/handoff`. DENTRO da junção: iterações até PASS. ENTRE junções: forward-only (anti-loop). Process-critic adversarial (qa-critic subagente isolado) ao final de BLOCO APROVADO + on-demand + opcional /checkpoint; rewind cascata para qualquer J_i; downstream re-roda. **TODO QA é adversarial.** SUPLANTA (§Decisão/§Alternativas muda → novo ADR + Substituído por) × EMENDA (§Implementação/§Consequências muda → in-place STATUS-field). Within-junction rounds = EMENDA. Princípio 13 do §6.

## Aplicações
Domínios específicos (BI, regulado, etc.) NÃO ficam no núcleo — são criados clonando
.agent/skills/_template e vivem FORA do núcleo (no seu repositório).
Ver `exemplos/README.md` para o guia de criação.

## Roteador base
https://raw.githubusercontent.com/fabriciopsouza/metacognition-framework/main/AGENT-FRAMEWORK.md
