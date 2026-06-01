---
name: action-safety
description: "Núcleo SSoT da segurança de ações por EFEITO (allowlist + default-deny). Carregar antes de executar ou instruir QUALQUER ação que mude estado fora da leitura: shell, escrita, rede, git push/merge, exclusão, operação financeira/legal, mudança de permissão. Classifica por efeito (E1–E6), mapeia a tier (T1/T2/T3) e exige gate humano para T3 (irreversível + alto impacto). NÃO carregar para leitura pura ou bate-papo."
metadata:
  type: shared
  version: 1.0.0
  adr: "014, 015"
---

# action-safety — Segurança de ações por EFEITO (allowlist + default-deny)

> SSoT da política de segurança de ações (ADR-014). O mecanismo de enforcement vive no ADR-015
> (`tools/hooks/effect-gate.ps1` + managed-settings + canary). Aqui mora o **julgamento**: a regra
> que o agente aplica em qualquer ambiente. Agnóstico de domínio — classifica por efeito, não por nome.

## Princípio (Saltzer & Schroeder; NIST Zero Trust; OWASP C3) <!-- lint-agnostic:allow NIST/OWASP = padrão aberto FUNDACIONAL (guia/REFERENCIAS.md), citado como fonte do princípio, não norma de domínio (ADR-043) -->
**Default-deny.** O que não é claramente reversível-e-baixo-impacto (T1) não é autônomo.
Denylist por nome de comando é incompleta por construção (falha insegura e silenciosa — caso JARVIS:
`rm -rf ~/`). Classifique pelo **efeito**, que é finito; nomes de comando são infinitos.

## Predicados de efeito (E1–E6)
Antes de executar/instruir, marque quais efeitos a ação tem:
- **E1** — destrói/perde dados de forma irrecuperável.
- **E2** — irreversível/não-idempotente (estado anterior inalcançável; rodar 2× ≠ rodar 1×).
- **E3** — externamente visível / sai do limite de confiança (publica, envia, expõe, faz deploy).
- **E4** — custa dinheiro / cria obrigação legal.
- **E5** — altera controles de segurança/permissão.
- **E6** — comportamento atípico/fora do escopo declarado da tarefa.

## Tiers (mapa efeito → autonomia)
| Tier | Quando | Conduta |
|---|---|---|
| **T1** | reversível **e** baixo impacto (nenhum E, ou só E6 trivial) | autonomia — executar; allowlist amplo |
| **T2** | reversível **e** alto impacto, **ou** irreversível **e** baixo impacto | **ask/log** — confirmar ou registrar antes |
| **T3** | irreversível **e** alto impacto — (E1 ∪ E2) ∩ (E3 ∪ E4 ∪ E5) | **gate humano obrigatório** — deny por padrão; nunca auto-aprovar; four-eyes fora do canal |

**Dúvida entre T2 e T3 → trate como T3** (default conservador; ADR-014 §Riscos).

## Conduta por ambiente (mesma regra, mecanismo diferente — sem paridade)
- **IDE/SDK:** T3 inequívoco é bloqueado pelo hook `effect-gate` (deny determinístico) + managed-settings.
  T2 → `ask`/log. O hook é **backstop** dos casos inequívocos, não o juiz do universo — o julgamento E1–E6 é seu.
- **Chat web (sem runtime):** **não há gate real.** Rotule o efeito no artefato ("⚠ E1/E2 — irreversível"),
  embuta salvaguarda reversível (backup, `--dry-run`, confirmação), e **exija confirmação informada**
  antes de instruir ação T3. Chamar isso de "gate" seria a desonestidade do JARVIS (`--dangerously-skip-permissions` autodeclarado seguro). É **higiene declarada**.

## Registro auditável (toda ação T2/T3)
ação · predicado(s) E · tier · args · identidade do agente · decisão · aprovador humano · timestamp ·
(regulado) estado before/after. No IDE: log do hook / atributo de span. No chat: no digest/history.

## Fadiga de aprovação (calibração)
~93% dos prompts são aprovados no automático ("rubber-stamping" — telemetria Anthropic). **Não
maximize prompts:** minimize fricção em T2 (log > prompt quando possível), reserve o prompt para T3.

## Relações
- `[[high-stakes-gate]]` — T3 é o gatilho do gate de alto risco; este módulo dá o critério por efeito.
- `[[execution-modes]]` — a denylist de comandos do ADR-005 é **uma camada** (defense-in-depth), não a regra primária.
- `[[traceability]]` — registro auditável.
- ADR-014 (política) · ADR-015 (mecanismo/enforcement).

## Quando NÃO carregar
Leitura pura (Read/grep/ls), análise, bate-papo sem ação de mudança de estado.
