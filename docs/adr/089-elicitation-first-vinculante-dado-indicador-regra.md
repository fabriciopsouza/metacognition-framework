# ADR 089 — Elicitation-first VINCULANTE antes de implementar sobre dado/indicador/regra de domínio (enforcement, não nova capacidade)

- Status: **Aceito** (2026-06-19 — feedback explícito do dono "1-2, siga"; gate: qa-critic adversarial + canário do gate) · Decisores: dono + squad
- Tipo: **enforcement de capacidade existente** (anti-reinvenção, ADR-072). NÃO cria skill nova.
- Relaciona: ADR-081 (advanced-elicitation/readiness-gate), ADR-055 (avançado×discovery anti-silêncio), ADR-009/010 (método-sênior discovery), ADR-051 (discovery infere contexto), ADR-086 (risk-score gating), ADR-087 (autosuficiente), ADR-072 (anti-reinvenção)

## Contexto (falha observada — sessão 2026-06-18, aplicação vibra-kb-rag / indicador AIVI)
O agente em **autosuficiente** implementou sobre um indicador regulado (AIVI) **inferindo** em vez
de elicitar, corrigindo **reativamente** ao longo de 5+ rodadas de retrabalho:
1. Fabricou base de exemplo ("CABET") — não existia.
2. Usou `Variação Interna + Manual`; o indicador é **só Interna** (o "I" é de INTERNA).
3. Tratou uma **linha bruta** como o indicador (que é **acumulado** SUM/SUM).
4. Tratou o batente ANP884 como **mandatório**; é **referência** (ANP884=varejo; Vibra=atacado).
5. Ambiguidade de **unidade** (0,0057 = 0,0057% ou 0,57%?) e ausência de **memória de cálculo**.

**Diagnóstico crítico (file-first):** a capacidade de elicitação **JÁ EXISTE** — `advanced-elicitation`
(ADR-081), `discovery` método-sênior (ADR-009/010), `readiness-gate`, anti-silêncio de stake
(ADR-055). A falha **não é capacidade — é ENFORCEMENT**: autosuficiente **bypassou** o gate. O design
do dono era que o agente, **sem provocação**, perguntasse fontes/premissas/limites/método/exemplos.
"Assertividade relativa" (perto, mas errado) em indicador regulado **é falha**.

## Decisão
Antes de **J2 / escrever código que computa ou depende de um indicador, métrica ou regra de
domínio** (gatilho: regulado · número que vai a decisão · combustível/saúde/financeiro — risco
alto por ADR-086), o agente **DEVE elicitar proativamente e confirmar** uma **ficha de insumo**
mínima — mesmo em autosuficiente:
1. **Fontes** — qual arquivo/sistema é a verdade (e qual prevalece se divergirem).
2. **Método/fórmula EXATA** — com **inclusões e EXCLUSÕES** explícitas (ex.: Interna ≠ Manual).
3. **Limites/tolerâncias + NATUREZA** — mandatório × referência; teto/fallback/piso.
4. **Granularidade / janela / UNIDADE** — linha × acumulado; 12m × YTD; % × decimal.
5. **Exemplo verificado** — ≥1 caso com resultado esperado (oráculo).
6. **Memória de cálculo** nas respostas — parcelas (numerador/denominador), fórmula, unidade, fonte.

**Autosuficiente = elicitar completo + executar; NÃO = pular a elicitação.** Postura crítica
(default-assume-gap) é **standing**, não opcional.

## Mecanismo (emenda a gates existentes — sem skill/tool de capacidade novo; satisfaz régua §0 por editar existente + destravar "acertar de primeira")
- **discovery/SKILL.md (IMPLEMENTADO v1.68.0):** a "ficha de insumo" virou o **passo 4.1** — checklist OBRIGATÓRIO, VINCULANTE (não-skippável, mesmo em autosuficiente), logo após a etapa anti-raso.
- **execution-modes (IMPLEMENTADO v1.68.0):** autosuficiente reafirma "não pula elicitação; elicitar completo + executar".
- **route-gate / risk-score (ADR-086/027):** risco alto + alvo = dado/indicador/regra → o passo 4.1 é o gate (falha-fechada como mission-gate). *(O nudge runtime do route-gate aponta o passo 4.1; sob EDR o agente aplica inline.)*
- **Canário `tools/test_elicitation_gate.py` (IMPLEMENTADO v1.68.0):** fail-closed — verifica que a ficha (6 campos) + a natureza vinculante estão presentes no discovery. +1 capability `elicitation-gate`.
- **Aplicação (ex.: vibra-kb-rag):** a "ficha de indicador" (ex.: `docs/indicadores/AIVI.md`) é o artefato consumível dessa elicitação — fora do núcleo (ADR-070).

## Consequências
- (+) Acerto de primeira em domínio regulado; elimina o ciclo build→corrige (custo real observado).
- (+) Anti-reinvenção: usa o que existe (ADR-081/055/009); não incha o núcleo (0 skill nova).
- (−) Custo de 1 rodada de elicitação up-front antes de codar (deliberado — barato vs retrabalho).
- **Régua §0:** não é adição pura — **enforcement que edita gates existentes** + destrava "acertar de primeira" (cláusula c: destrava eval editando existente). O canário é o único arquivo novo (test, não capacidade).

## Pendências (resolvidas / abertas)
- ~~Canário determinístico do gate~~ → **feito** (`test_elicitation_gate.py`).
- **Aberto (decisão por caso):** o gate exige confirmação humana da ficha (HITL) quando há **divergência de fonte**; **auto-preenche file-first** quando há **1 fonte autoritativa inequívoca**. Default registrado no passo 4.1.
