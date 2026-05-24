---
name: high-stakes-gate
description: "Carregar quando a tarefa é de alto risco: ambiente regulado, decisão irreversível, número que vai a decisão executiva, ou operação que afeta produção crítica. Define validação por risco, audit trail, logs imutáveis e gate humano (HITL). Regras de domínio específicas (ex.: normas setoriais) são CONFIG de aplicação, não deste núcleo. NÃO carregar para tarefa pontual de baixo risco."
version: 1.0.0
source: "pesquisa A3 (governança/validação por risco) + A2 (HITL); generalização de validação regulada"
last_review: 2026-05-23
---

# High-Stakes Gate — Validação por Risco (genérico)

> Capability **agnóstica de domínio**. O *o quê* validar vem da aplicação; o *como*
> garantir rigor vem daqui. Trabalha com `traceability`, `observability` e
> `confidence-classification`.

## Quando este gate é obrigatório
- Decisão **irreversível** ou de alto custo.
- **Ambiente regulado** (qualquer norma — a norma específica é config da aplicação).
- Número/saída que **embasa decisão executiva**.
- Mudança que **afeta produção crítica**.

## O que o gate exige
1. **Validação por risco** (não por volume de documento) — foco em mitigar o que
   pode dar errado, com critérios binários no `validation.md`.
2. **Audit trail** — quem, o quê, quando, com base em qual fonte/versão (`traceability`).
3. **Logs imutáveis** quando o contexto exigir (`observability`).
4. **Human-in-the-loop (HITL)** — hand-off **bloqueado** até revisão humana sobre
   diffs/saídas estruturadas. Liga a `rules/04-confidence-routing` (baixa confiança
   estratégica → arquitetura reflexiva).

## Como uma aplicação especializa este gate
A aplicação fornece, via sua própria skill (clone de `_template`), a **config**:
- quais normas/critérios setoriais aplicar (ex.: GAMP 5 / ANVISA / SOX / LGPD / ITIL —
  a norma específica vive na aplicação, não aqui);
- quais campos de audit são obrigatórios;
- o que conta como "revisão humana suficiente".

O núcleo nunca cita uma norma específica — ele garante o **mecanismo** de rigor.
