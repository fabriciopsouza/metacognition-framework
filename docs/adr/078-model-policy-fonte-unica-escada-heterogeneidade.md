# ADR 078 — Política de modelo como dado: `model-policy.json` fonte única (papel×risco→tier), escada de heterogeneidade declarada e fallback de indisponibilidade

- Status: **Aceito** (2026-06-11 — gate: **qa-critic adversarial** (Sonnet isolado, 3 rounds J4): R1 `corrigir` (1 ALTO espúrios + 1 MÉDIO ADR-076 stale + 3 BAIXO) → fixes → R2 confirmou substantivos → R3 `aprovar`/0 problemas; **suíte local verde**; CI billing-blocked → validação local) · Data: 2026-06-11 · Decisores: dono + squad
- Onda: F2 do plano de melhoria (`docs/_private/reports/avaliacao-processo-framework-2026-06-11.md`, P5–P7) · Tipo: **fusão** justificada pela régua §0(a) — a política de modelo vivia em **3 fontes divergentes** (regras hardcoded em `suggest_model`, `model: sonnet` fixo no frontmatter dos subagentes, prosa no ADR-018) e **funde em 1 arquivo de dados**; remove as regras hardcoded do código.
- Relaciona: ADR-076 (sugestão de modelo no handoff — as regras saem do código para o dado), ADR-018 (heterogeneidade gerador↔crítico — ganha escada de degradação explícita), ADR-069 (hub cross-IA — degrau 1 da escada). Pergunta do dono incorporada em sessão: *"fallback para situações de modelos indisponíveis?"* → mecanismo de indisponibilidade declarada.

## Contexto

O `suggest_model` (ADR-076) hardcodava opus/sonnet e **não conhecia o tier acima de Opus** (Fable/Mythos) — "architect → mais capaz (Opus)" ficou stale por construção, pois amarrava a regra a um *nome* de modelo, não a um *tier*. Os subagentes `.claude/agents/{qa-critic,explorer}.md` fixam `model: sonnet` mesmo quando o autor da sessão JÁ é sonnet (heterogeneidade zero por inércia). "Família diferente" (ADR-018) é inalcançável dentro do Claude Code puro (opus/sonnet/haiku/fable = mesma família) e a degradação não era explicitada. Haiku não era usado em papel nenhum. E não havia resposta para **modelo indisponível** (deprecado, plano sem acesso, API fora).

## Decisão (1 frase ativa)

Criar **`tools/model-policy.json`** como fonte única — papel×risco→**tier** (`max`/`balanced`/`economy`/`heterogeneous`), cada tier com **chain de fallback** (`max: fable→opus→sonnet`; `balanced: sonnet→opus→haiku`; `economy: haiku→sonnet`), mapa tier→model-id vigente, **escada de heterogeneidade** em 3 degraus (família≠ via hub cross-IA > modelo≠ mesma família com preferência data-driven [autor tier-alto→sonnet; autor sonnet/haiku→tier max] > mesmo modelo fresh **declarado**) e **indisponibilidade situacional declarada** via env `FRAMEWORK_MODELS_UNAVAILABLE=fam1,fam2` (permanente = editar `model_ids`) — a resolução caminha a chain pulando indisponíveis, **anota o fallback usado no output**, e chain esgotada → **erro declarado** (nunca escolha silenciosa); `handoff.py` consome a policy (regras hardcoded REMOVIDAS), o orquestrador sobrepõe o `model:` do subagente na chamada `Agent(...)` conforme a policy, e papéis mecânicos (docops/bulk) descem ao tier economy (julgamento nunca desce de balanced).

## Alternativas consideradas

1. **Status quo (3 fontes, hardcode).** Diverge a cada modelo novo; cego ao tier máximo; heterogeneidade por inércia de frontmatter. **Rejeitada** (é o gap P5).
2. **Sondar disponibilidade na API em runtime.** Quebra o determinismo (mesmo estado → saídas diferentes conforme rede), exige credencial no tooling offline e é exatamente a classe de não-determinismo que o ADR-076 baniu. **Rejeitada** — indisponibilidade é **declarada** (env/arquivo), não sondada.
3. **Policy por projeto (briefing) em vez de global.** Domínio pode sobrepor no futuro (config de aplicação), mas o default racional papel×risco é transversal — núcleo agnóstico carrega o mecanismo, não o domínio. **Deferida** (não exclui a escolhida).
4. **`model-policy.json` global + chains + env de indisponibilidade (ESCOLHIDA).** Atualizar modelo novo = editar dado; determinismo preservado (entrada = arquivo + env explícita); fallback auditável no próprio output; canário valida schema + 12 regras + 5 cenários de indisponibilidade.

## Consequências

**Positivas:** 3 fontes → 1; tier max passa a apontar para o modelo mais capaz **disponível** (hoje Fable, fallback Opus) sem editar código; haiku entra nos papéis mecânicos (token/latência ↓ sem tocar garantia — a saída mecânica é gateada por canários Python, não pelo modelo); heterogeneidade deixa de falhar silenciosamente quando o autor é sonnet; indisponibilidade tem caminho declarado em vez de improviso. **Negativas/limite (declarado):** o frontmatter dos subagentes é estático — o `model: sonnet` permanece como default sano e a sobreposição depende de o orquestrador passar `model:` na chamada (prosa instruída no próprio frontmatter; trava física exigiria recurso do harness); a env de indisponibilidade é por sessão (esquecível — mas o erro de chain esgotada é loud); a regra continua **heurística por papel** (recomendação auditável, não prova de otimalidade — herda a ressalva do ADR-076).

## Implementação (ponteiro)

- `tools/model-policy.json` (fonte única; schema validado por canário) · `tools/handoff.py` (`POLICY`/`_tier_model`/`_heterogeneous`/`_unavailable`; `MODEL_ID` vira alias derivado — compat ADR-076) · `tools/test_handoff.py` (12 regras + schema + 5 cenários de indisponibilidade incl. degrau 3 declarado e chain esgotada → erro).
- `_meta/subagent-isolation.md` §Heterogeneidade (escada de 3 degraus) · `.claude/agents/qa-critic.md` (instrução de sobreposição) · `.agent/workflows/checkpoint.md` (regra citada por ponteiro, não por cópia).
- `capabilities.json`: `model-policy` (+1; enforcement=fail-closed via `test_handoff.py`).
