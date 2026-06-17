# ADR 087 — Modo autônomo (`autosuficiente`): retry-budget com fallback antes de escalar (recast H do ADR-085)

- Status: **Aceito** (2026-06-17 — ratificado pelo dono "prossiga"; gate: qa-critic heterogêneo + canário do resolvedor) · Decisores: dono ("estudar automator p/ melhorar modo autônomo"; "prossiga") + squad
- Tipo: **adição que mecaniza um dial de processo** (P15). Régua §0 (ADR-007): satisfaz (c) — *destrava* a decisão retry/escalate que era implícita, tornando-a determinística; reusa a escada de modelo (ADR-078/082) e o ledger qa-evidence existentes. +1 capability `autonomy-retry-policy`.
- Relaciona: **ADR-085** (recast H), **ADR-005** (execution-modes), **ADR-011/045** (QA bicelular), **ADR-078/082** (escada de modelo), **ADR-074/077** (qa-evidence), P15 (HITL por modo). Proposta original: PR #94 (superseded por esta versão consolidada — ratificada + implementada).

## Contexto — estudo do `bmad-automator` (fontes citadas)

Estudo do orquestrador autônomo do `bmad-automator` (`docs/how-it-works.md` + `docs/agents-and-monitoring.md`, CONFIRMADO): **retry-budget com fallback, escalação por último** (*"escalation is intentionally the last step, not the first response"*) · verificação por **artefato** (não "CLI exited") · máquina de estado de liveness (`stuck/crashed`) · sem gate humano no fluxo normal.

**Relevância (correção do dono, P15):** HITL é por **modo** (ADR-005). `autosuficiente` É autônomo; deve ganhar auto-recuperação SEM remover HITL de `default`/`avançado`. Nosso QA bicelular itera DENTRO da junção mas **não formaliza retry-budget + fallback de modelo antes de escalar**.

## Decisão

**(H1) — CONSTRUÍDO:** `tools/autonomy_policy.py` (`next_action(mode, attempt, budget, current_model)`): resolvedor **determinístico** do dial por modo. HITL (default/avançado) → `escalate` na 1ª falha (nunca auto-retenta). `autosuficiente` → `retry` subindo a escada de capacidade (`haiku<sonnet<opus<fable`) até o budget; `escalate` por ÚLTIMO (budget esgotado OU topo). Fail-closed (modo/modelo/budget inválido → ValueError). Canário `tools/test_autonomy_policy.py` (tabela-verdade + invariantes "HITL nunca retenta" / "autônomo não escala cedo" + fail-closed).

**(H2) — JÁ EXISTE:** verificação por artefato = o **qa-evidence ledger** (ADR-077) é o "PASS" que dispara avanço (não "o subagente terminou"). Sem novo mecanismo.

**(H3) — DEFERIDO (declarado):** detector de "stuck" (liveness) precisa de um sinal de progresso que o harness não expõe de forma limpa (mesma classe do harness_limit do ADR-078). Fica como follow-up; sem ele, o budget finito + a escalação-por-último já evitam loop eterno.

**(H4) — NÃO ADOTADO:** orquestração tmux/child-sessions e "zero gate humano" do automator — conflitam com junções declaradas + HITL configurável. Adotamos a **doutrina** (retry-budget, escalação-última, verificação-por-artefato), não a implementação.

**Limite declarado (ADR-078/082 harness_limit):** o fallback de modelo aplica-se ao **dispatch de SUBAGENTE** (developer/qa-critic via `Agent(model=...)`), onde o framework controla o modelo — NÃO ao modelo INTERATIVO da sessão (controle do harness/`/model`). O resolvedor diz QUAL modelo usar no retry; o orquestrador EXECUTA o retry (parte prosa-pela-porta do P15).

## Alternativas consideradas

1. **Adotar o orquestrador inteiro do automator.** Importa autonomia desatendida + tmux; conflita com junções/HITL. **Rejeitada** (recast da doutrina, não do código — P15).
2. **Status quo: autosuficiente escala igual aos outros na 1ª falha.** Nega o propósito do modo autônomo. **Rejeitada — é o gap.**
3. **Retry infinito.** Loop/custo; viola forward-only (ADR-011). **Rejeitada** — budget finito + escalação-por-último.

## Consequências

**Positivas:** `autosuficiente` ganha auto-recuperação determinística (retry-budget + fallback de modelo) com escalação-por-último, **mantendo HITL intacto** nos outros modos (P15, provado por canário: "HITL nunca retenta"); decisão auditável (não "o agente achou que devia tentar de novo"). **Negativas/limite (declarado):** +1 capability `autonomy-retry-policy`; o fallback só vale no dispatch de subagente (modelo interativo = limite do harness); (H3 stuck) deferido; a *execução* do retry pelo orquestrador é prosa-pela-porta (o resolvedor é a parte determinística).
