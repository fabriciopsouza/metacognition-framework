# ADR 014 — Allowlist + default-deny por EFEITO (não por nome de comando)

- Status: Aceito
- Data: 2026-05-30 · Decisores: dono (briefing v1.14.x) + squad (autônomo)
- Onda: 1 (segurança executável) · Pesquisa: **P4** · Tipo: **EMENDA** (Princípios 1, 5)
- Relaciona: ADR-015 (mecanismo/enforcement — par de maior valor), ADR-005 (modos de execução), `_shared/high-stakes-gate`.

## Contexto

O framework já tem `execution-modes` (ADR-005) com uma **denylist** de ~20 regras de comandos
destrutivos e `high-stakes-gate` para risco. Mas denylist por **nome de comando** é incompleta por
construção: exige enumerar infinitos comandos e falha de modo inseguro e silencioso quando o agente
usa uma variante não-listada (Saltzer & Schroeder: "wrong psychological base" — o default inseguro).
P4 mostra o incidente real do JARVIS: shell com input de LLM sem allowlist executou
`rm -rf tests/ patches/ plan/ ~/` com expansão de `~/` para o home inteiro.

A literatura é unânime (Saltzer & Schroeder 1975; NIST SP 800-207 Zero Trust; OWASP Proactive
Controls C3): **allowlist + default-deny** é o mínimo; denylist só como suplemento. P4 classifica
este como o item de **maior ganho/esforço** da série.

**Régua §0:** EMENDA — não cria subsistema; **eleva** o princípio que organiza a denylist existente
(de "lista de nomes proibidos" para "classe de efeitos perigosos"), tornando-a completável e
agnóstica. A denylist de comandos do ADR-005 permanece como *uma camada* (defense-in-depth), não a regra.

## Decisão (1 frase ativa)

Classificar toda ação por **EFEITO destrutivo/irreversível** (predicados E1–E6), mapeá-la a um
**tier** (T1 autonomia / T2 ask-ou-log / T3 gate humano obrigatório), com **default-deny** para o
que não é claramente T1 — princípio agnóstico de domínio em `_shared/action-safety/SKILL.md`,
aplicado por mecanismo no ADR-015.

### Predicados de efeito (E1–E6) — agnósticos, por efeito não por nome
| Cód | Efeito |
|---|---|
| E1 | Destrói/perde dados de forma irrecuperável |
| E2 | Irreversível/não-idempotente (estado anterior inalcançável) |
| E3 | Externamente visível / sai do limite de confiança (publica, envia, expõe) |
| E4 | Custa dinheiro / cria obrigação legal |
| E5 | Altera controles de segurança/permissão |
| E6 | Comportamento atípico/fora do escopo declarado |

### Tiers de decisão
- **T1** (reversível + baixo impacto): autonomia — allowlist amplo, sem prompt.
- **T2** (reversível + alto impacto **OU** irreversível + baixo impacto): ask/notify — confirmação ou log obrigatório.
- **T3** (irreversível + alto impacto; E1–E2 ∩ E3–E5): **gate humano obrigatório**, deny por padrão,
  **nunca** auto-aprovável, preferencialmente four-eyes fora do canal do agente.

### Registro auditável por gate (regulado e não-regulado)
ação proposta · predicado(s) E disparado(s) · tier · argumentos · identidade do agente · decisão
(approve/reject) · identidade do aprovador humano · timestamp · (regulado) before/after.

### Honestidade por ambiente (liga ADR-015)
- **IDE:** tiers viram regras `deny`/`ask`/`allow` + hook de backstop (ADR-015).
- **Chat:** sem runtime — rotular o risco por efeito no artefato, embutir salvaguarda reversível,
  exigir confirmação informada antes de instruir ação T3. **É higiene declarada, não gate.**

## Alternativas consideradas
1. **Manter só denylist de nomes (status quo ADR-005).** Prós: já existe. Contras: incompleta por
   construção, falha insegura e silenciosa (lição JARVIS). Rejeitada como *regra primária* — vira camada.
2. **Classificador LLM por efeito para toda ação (estilo Claude Code auto mode).** Prós: cobre o
   desconhecido. Contras: FNR medido = 17% (P4) — deixa passar ~1 em 6 ações perigosas; não substitui
   gate humano em T3; custo. Rejeitada como gate único; aceitável só como sinal auxiliar de T2.
3. **Allowlist + default-deny por efeito + denylist como camada (ESCOLHIDA).** Prós: fail-safe,
   agnóstico, completável. Contras: exige definir a taxonomia E1–E6 e o gate (pago pelo ADR-015).

## Consequências
**Positivas:** falha segura (default-deny); agnóstico (qualquer domínio classifica por efeito);
auditável; absorve a denylist existente como camada.
**Negativas:** +1 módulo `_shared/action-safety` (~1 arquivo); exige o mecanismo do ADR-015 para ter dente no IDE.
**Riscos:** (a) **fadiga de aprovação** — telemetria Anthropic mostra ~93% dos prompts aprovados no
automático ("rubber-stamping"); **mitigação:** calibrar tiers para minimizar prompts T2, reservar
fricção para T3. (b) Fronteira T2/T3 para E3 de baixo blast-radius é **[INFERIDO]** — default
conservador (trata como T3 se houver dúvida), ajustável.

## Implementação (ponteiro após aceito)
- Ponteiro: branch `feat/v1.15.0-allowlist-enforcement` · `2026-05-30` · grep `action-safety|E1.*E6|tier`
- Artefatos: `_shared/action-safety/SKILL.md` (a política); mecanismo no ADR-015.
- Lit: Saltzer&Schroeder 1975; NIST SP800-207; OWASP C3 + Agentic Top10; EU AI Act Art.14; Moldovan&Abbeel 2012.
