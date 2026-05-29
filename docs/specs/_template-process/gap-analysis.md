---
mode: mapeamento-de-processo
depth: standard
notation: mermaid-flow
formality: senior-ba
personas: [humano-engagement]
validation_status: PENDENTE
gap_severity_max: medio    # baixo | medio | alto | bloqueador
---

# gap-analysis.md — Diagnóstico do as-is: `<nome-do-processo>`

> Companion do `process-map-as-is.md` (mesma pasta). Diagnóstico do que está
> quebrado, ausente ou ineficiente no processo as-is. **Entrega ao `architect`**
> — ele recebe este arquivo e produz to-be design via ADR(s) de processo.
> Discovery NÃO desenha to-be; apenas diagnostica.

## Sumário executivo (3-5 linhas)

<O que o leitor precisa saber em 30 segundos. Ex.: "Processo X tem 4 gaps: 2 handoffs sem dono, 1 atividade declarada × observada divergente, 1 trilha de auditoria implícita mas não rastreada (norma específica declarada pelo discovery do projeto), owner do gateway de retrabalho indefinido. Sugestão arquitetural: ADR de processo to-be deve nomear owner único para retrabalho e formalizar trilha de auditoria.">

## Gaps detectados

### Gap G1 — `<título curto>`
- **Severidade:** baixo | medio | alto | bloqueador
- **Onde no mapa:** atividade `<A-N>` ou handoff `<de-para>`
- **Natureza:** handoff quebrado | dono ausente | regra ambígua | exceção não coberta | divergência declarativo×observacional | pain point | bottleneck
- **Evidência:** `[DECLARADO por <stakeholder>]` ou `[OBSERVADO em <log/sistema>]`
- **Impacto se não tratado:** `<consequência>`
- **Sugestão (sem desenhar to-be):** `<o que falta decidir — pergunta para architect, não resposta>`

### Gap G2 — `<título>`
...

## Pain points (C1 — apenas as-is)

| # | Pain point | Atividade onde ocorre | Quem reporta | Frequência |
|---|---|---|---|---|
| P1 | <descrição> | <A-N> | <papel> | <alta/média/baixa> |

## Bottlenecks (C1 — apenas as-is)

| # | Bottleneck | Atividade | Métrica que evidencia | Causa raiz suspeita |
|---|---|---|---|---|
| B1 | <descrição> | <A-N> | <cycle time / volume / SLA> | <causa> |

## Divergências `[DECLARADO]` × `[OBSERVADO]` (anti-padrão #1 do BPM)

| # | Atividade | Declarado por stakeholder | Observado em sistema/log | Lacuna semântica |
|---|---|---|---|---|
| D1 | <A-N> | <descrição> | <descrição> | <o que essa lacuna revela> |

## Itens para architect (seção MUST — handoff explícito)

> Esta seção é OBRIGATÓRIA. Lista as **perguntas de to-be design** que o
> `architect` precisa resolver via ADR. Discovery **não responde** essas
> perguntas — apenas as nomeia.

1. **Decisão pendente:** `<questão de arquitetura de processo>`
   - Contexto: <gap que motivou>
   - Alternativas a considerar: `<sem decidir>`
2. **Decisão pendente:** `<...>`
3. **...**

## Bloco de escalação (apenas se persona=subagente-automatizado E A4 falhou)

> Adicionar APENAS quando o pipeline rodou sem stakeholder humano disponível
> para validação A4. Caso contrário, omitir esta seção.

### [BLOQUEADOR: validação humana pendente]
- **Perguntas que precisam de resposta humana:**
  - `<pergunta 1>`
  - `<pergunta 2>`
- **Próximo passo recomendado:** agendar revisão com `<process owner>` antes de architect tocar to-be.
- **Pipeline exit-code:** não-zero (sinalização explícita ao orquestrador downstream).

## Lacunas remanescentes (anti-alucinação)

- `[DESCONHECIDO]` <item que stakeholder não soube responder + como validar>
