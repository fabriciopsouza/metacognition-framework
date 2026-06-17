# ADR 087 — Modo autônomo (`autosuficiente`): retry-budget com fallback antes de escalar (recast H do ADR-085)

- Status: **Proposto** (2026-06-17 — estudo + proposta; aguarda ratificação do dono + qa-critic se construído. NÃO construído aqui) · Decisores: dono ("estudar automator p/ melhorar modo autônomo") + squad
- Tipo: **proposta de política (doutrina), build deferido**. Régua §0 (ADR-007): este ADR **não adiciona código** — propõe política que, se ratificada, será recast no idioma do framework (P15 — mecanismo) reusando QA bicelular + escada de modelo + ledger existentes. +0 capability até build.
- Relaciona: **ADR-085** (recast H), **ADR-005** (execution-modes), **ADR-011/045** (QA bicelular J0–J6 + rewind), **ADR-078** (escada de modelo), **ADR-074/077** (qa-evidence), P15 (HITL por modo)

## Contexto — estudo do `bmad-automator` (fontes citadas)

Estudo do orquestrador autônomo do `bmad-automator` (org `bmad-code-org`), que **funciona** (autonomia desatendida de implementação de stories). Fontes lidas: `docs/how-it-works.md` + `docs/agents-and-monitoring.md`. Modelo de autonomia (CONFIRMADO das fontes):

1. **Retry-budget com fallback, escalação por último.** Sessão-filha completa → se "not healthy/verified" → se há budget, **retry com agente igual ou fallback**; budget esgotado → **escala ao humano**. Doutrina explícita: *"escalation is intentionally the last step, not the first response."*
2. **Verificação por ARTEFATO, não por saída de processo.** Completion = "verification passed" (não "CLI exited") — guarda contra false-PASS ("review session exits but story never marked done").
3. **Máquina de estado de liveness.** Monitor poda o estado em `{just_started, in_progress, completed, stuck, crashed, not_found}`; "stuck" = sem sinal de progresso válido na janela.
4. **Sem gate humano no fluxo normal** — roda desatendido até falhar, então surface ao humano. (Não documenta pause/resume/inject — só escalação.)

**Por que é relevante a NÓS (correção do dono, P15):** HITL é por **modo** (ADR-005). O `autosuficiente` É um modo autônomo; o automator é "autonomia-que-funciona" e deve melhorá-lo — **sem** remover HITL de `default`/`avançado`. Nosso QA bicelular (ADR-011) itera DENTRO da junção até PASS, mas **não formaliza retry-budget + fallback de modelo antes de escalar**, nem detector de "stuck".

## Decisão proposta (recast no nosso idioma — NÃO construído aqui)

**(H1) Política de auto-recuperação do `autosuficiente`:** em FAIL de junção (ex.: qa-critic), o modo `autosuficiente` **auto-retenta** o autor antes de escalar ao humano, com **budget** (ex.: N=2) e **fallback de modelo subindo a escada ADR-078** (autor sonnet→opus→fable). **Escalação ao humano = último passo**, ao esgotar o budget — não a primeira resposta. `default`/`avançado` permanecem HITL (escalam na primeira fricção). Mesmo mecanismo, **dial por modo** (P15).

**(H2) Verificação por artefato (já temos — formalizar):** o "PASS" de junção que dispara avanço é o registro no **qa-evidence ledger** (ADR-077), não "o subagente terminou". Guarda contra false-PASS. Alinhado ao automator; sem novo mecanismo.

**(H3) Detector de "stuck" (net-new):** em runs autônomos longos, um sinal de liveness (sem progresso em janela X → `stuck` → escala) evita hang silencioso. Recast da máquina de estado do monitor; candidato a +1 capability `autonomous-liveness` se construído.

**(H4) NÃO adotar:** orquestração tmux/child-sessions e "zero gate humano" do automator — conflitam com a topologia do framework (junções declaradas, HITL configurável). Adotamos a **doutrina** (retry-budget, escalação-última, verificação-por-artefato, liveness), não a implementação.

## Alternativas consideradas

1. **Adotar o orquestrador do automator inteiro.** Importa modelo de autonomia desatendida + tmux; conflita com junções/HITL configuráveis. **Rejeitada** (recast da doutrina, não do código — ADR-085 P15).
2. **Status quo: qa-critic FAIL no autosuficiente escala igual aos outros modos.** Desperdiça o ganho de auto-recuperação que o autônomo permite; "escalar na primeira fricção" nega o propósito do modo. **Rejeitada — é o gap.**
3. **Retry infinito (sem budget).** Risco de loop/custo; viola circuit-breaker (ADR-011 forward-only). **Rejeitada** — budget finito + escalação.

## Consequências

**Positivas:** `autosuficiente` ganha auto-recuperação real (retry-budget + fallback de modelo) com escalação-por-último, mantendo HITL intacto nos outros modos (P15); verificação-por-artefato e liveness reduzem false-PASS e hang. **Negativas/limite (declarado):** se construído, +1 capability (`autonomous-liveness`) + política no `_shared/execution-modes`; **build deferido** — este ADR é estudo+proposta (Proposto). Risco: retry com fallback de modelo aumenta custo/tempo no autônomo (mitigado pelo budget finito + telemetria ADR-026/052). **Pré-requisito de build:** ratificação do dono (toca semântica de HITL/escalação por modo — load-bearing).
