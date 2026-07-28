---
name: high-stakes-gate
description: "Carregar quando a tarefa é de alto risco: ambiente regulado, decisão irreversível, número que vai a decisão executiva, ou operação que afeta produção crítica. Define validação por risco, audit trail, logs imutáveis e gate humano (HITL). Regras de domínio específicas (ex.: normas setoriais) são CONFIG de aplicação, não deste núcleo. NÃO carregar para tarefa pontual de baixo risco."
version: 1.1.0
source: "pesquisa A3 (governança/validação por risco) + A2 (HITL); generalização de validação regulada"
last_review: 2026-07-26
---

# High-Stakes Gate — Validação por Risco (genérico)

> Capability **agnóstica de domínio**. O *o quê* validar vem da aplicação; o *como*
> garantir rigor vem daqui. Trabalha com `traceability`, `observability` e
> `confidence-classification`.
>
> **Carga é DECLARADA pelo discovery do projeto** (ADR-010), não inferida por sinais semânticos do framework. Sem declaração no `requirements.md`/`research-brief.md`, este gate NÃO carrega.

## Quando este gate é obrigatório
Quando o `## Escopo declarado pelo discovery` do projeto afirma **qualquer** dos seguintes:
- Decisão **irreversível** ou de alto custo.
- **Ambiente regulado** (qualquer norma — a norma específica é declarada pelo discovery; o framework não pré-lista).
- Número/saída que **embasa decisão executiva**.
- Mudança que **afeta produção crítica**.

## O que o gate exige
1. **Validação por risco** (não por volume de documento) — foco em mitigar o que
   pode dar errado, com critérios binários no `validation.md`. **Mecanismo determinístico (P15):**
   priorizar a profundidade de validação por `python tools/risk_score.py --items <json>`
   (`risco = prob × impacto` → `gate` FAIL/CONCERNS/ADVISORY + `tier` P0–P3; ADR-086). O score é
   FORMA agnóstica; as *categorias* e o que conta como impacto alto são CONTEÚDO do domínio
   (input/blueprint, não hardcoded — P12). `gate_agregado=FAIL` ⇒ mitigação obrigatória antes do hand-off.
2. **Audit trail** — quem, o quê, quando, com base em qual fonte/versão (`traceability`).
3. **Logs imutáveis** quando o contexto exigir (`observability`).
4. **Human-in-the-loop (HITL)** — hand-off **bloqueado** até revisão humana sobre
   diffs/saídas estruturadas. Liga a `rules/04-confidence-routing` (baixa confiança
   estratégica → arquitetura reflexiva). **Mecanismo, não prosa (ADR-096):** o disparo é
   `score ≥ 6` (`hitl_requerido` no JSON do `risk_score`) — rodar
   `python tools/risk_score.py --items <json> --gate-exit` no ponto de hand-off; **exit 2 = travado**
   (0 = liberado, 1 = entrada inválida). Corte escolhido pelo dono: alcança 2×3, 3×2 e 3×3.
   **Lacuna declarada:** 1×3 (raro × catastrófico = 3) **não** trava — se o item for irreversível,
   o bloqueio vem do `action-safety` (T3), não daqui — e a cobertura dele é ESTREITA: o hook só
   inspeciona Bash/PowerShell, é fail-open em erro e com regras ausentes, e o
   julgamento T3 pleno é prosa do agente. Para item `1×3` cujo dano não vira
   comando de shell casando com padrão, NENHUM dos dois pega; é achado de
   process-compliance, e assumir que o outro mecanismo cobre é o erro a evitar.

## Como uma aplicação especializa este gate
A aplicação fornece, via sua própria skill (clone de `_template`) E via declaração do discovery do projeto, a **config**:
- quais normas/critérios setoriais aplicar (a norma específica vive na declaração do projeto, não em listas pré-fixadas aqui — ADR-010);
- quais campos de audit são obrigatórios;
- o que conta como "revisão humana suficiente" (HITL adicional governado por ADR-005 / execution-modes).

O núcleo nunca cita uma norma específica nem mantém lista de exemplos — ele garante o **mecanismo** de rigor. Anti-vazamento cross-projeto (ADR-010): exemplos de outros projetos NÃO entram aqui mesmo como ilustração.
