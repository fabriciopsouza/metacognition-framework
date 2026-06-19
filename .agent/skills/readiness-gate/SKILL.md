---
name: readiness-gate
description: "Validar que requirements, decisões arquiteturais e (quando existir) spec de UX estão alinhados e completos ANTES de avançar para o developer. Gate pré-J3 (architect→developer). Ativar quando o architect declara que a ADR está fechada ou o PMO está prestes a rotear para developer. NÃO substituir o qa-critic (que opera APÓS o developer). NÃO ativar em blocos pontuais/triviais onde não há ADR nem requirements formal."
version: 1.0.0
source: "integração externa seletiva — extraído e adaptado; proveniência na ADR-081"
last_review: 2026-06-16
role_order: null
consumes:
  - "docs/specs/<feature>/requirements.md"
  - "docs/adr/<número>-<slug>.md (a ADR relevante ao bloco)"
  - "docs/specs/<feature>/validation.md (se existir)"
produces:
  - "veredito binário: PRONTO_PARA_DEV | BLOQUEADO (com lista de gaps)"
pass_criteria: "PASS sse todos os critérios do checklist abaixo são VERDADEIRO — um único FALSO ou DESCONHECIDO que bloqueie implementação = BLOQUEADO."
confidence_required: true
shared_refs:
  - _shared/confidence-classification
rewind_target: architect
---

# Readiness Gate — Validação Pré-Developer (verificação dentro de J2, entre J2 e J3)

> "J2.5" NÃO é junção numerada do ledger (ADR-011/077) — é verificação dentro de J2 antes do forward para J3. Não citar J2.5 como entrada de ledger.

## Carregar de `_shared/`
`confidence-classification`

## Princípio

Gate **binário** (não gradual): ou todos os critérios passam e o developer avança, ou há bloqueio com lista explícita de gaps a resolver pelo architect/discovery. Nenhum "aprovar com ressalvas" — ressalva é bloqueio até resolução.

Inspiração: integração externa seletiva registrada em ADR-081. Adaptado com os artefatos e nomenclatura do metacognition.

## Posição no fluxo QA bicelular

```
discovery (requirements.md)
  ↓ J1
architect (ADR + decisões)
  ↓ J2
[readiness-gate ← ESTE GATE — posição entre J2 e J3, sem nova numeração de junção]
  ↓ J3 (só se PRONTO_PARA_DEV)
developer
  ↓ J4
qa-critic
```
> Nota: readiness-gate é verificação dentro da junção J2 (architect), não uma nova junção numerada — evitar conflito com o ledger de junções ADR-011/077.

## Checklist de prontidão

### Grupo 1 — Spec (requirements.md)

| # | Critério | Verificação |
|---|---|---|
| R1 | `requirements.md` existe em `docs/specs/<feature>/` | arquivo presente |
| R2 | Seção `## Identificação` preenchida (caso/feature + confiança da tarefa) | não tem `<placeholder>` |
| R3 | Escopo IN e Escopo OUT declarados (ou `## Fora de escopo` preenchida) | explícito |
| R4 | Pelo menos 1 critério de aceite binário declarado (`## Escopo funcional` ou `validation.md`) | verificável T/F |
| R5 | [DESCONHECIDO]s que bloqueiam implementação: zero | listar se houver |
| R6 | Se `product_type` executável: `ambiente-execucao` declarado (como roda, onde, quem opera) | declarado ou N/A |

### Grupo 2 — Arquitetura (ADR)

| # | Critério | Verificação |
|---|---|---|
| A1 | ADR relevante ao bloco existe e está com status `Aceito` ou `Proposto` com decisão clara | status declarado |
| A2 | Decisão ativa está em 1 frase ativa (não vaga) | verificável |
| A3 | Alternativas consideradas: pelo menos 1 registrada com motivo de rejeição | não está vazia |
| A4 | Consequências declaradas (positivas E negativas/limites) | ambas presentes |
| A5 | Nenhuma dependência de rename/novo módulo sem registro na ADR | verificar diff |

### Grupo 3 — Alinhamento spec × arquitetura

| # | Critério | Verificação |
|---|---|---|
| X1 | Cada requisito funcional do requirements.md tem correspondência na decisão arquitetural | rastreável |
| X2 | Não há requisito no requirements.md que a ADR contradiga | verificar contradição |
| X3 | Critérios de aceite do requirements.md são verificáveis no `validation.md` | 1:1 ou gap documentado |

### Grupo 4 — Completude operacional

| # | Critério | Verificação |
|---|---|---|
| O1 | Developer receberia este requirements.md + ADR e saberia: (a) qual arquivo/função criar ou modificar; (b) formato de input e output esperado — sem precisar perguntar | verificar explicitamente nos artefatos |
| O2 | Entradas/saídas do developer estão definidas (o que recebe, o que entrega) | declarado |

## FLOW

### Passo 1 — Coletar artefatos

- Localizar `docs/specs/<feature>/requirements.md` e a ADR relevante
- Se requirements.md não existe: BLOQUEADO imediatamente (R1 = FALSO)
- Ler os artefatos antes de avaliar (file-first)

### Passo 2 — Avaliar checklist

Para cada critério: marcar VERDADEIRO / FALSO / DESCONHECIDO com evidência:
```
R1: VERDADEIRO — arquivo presente em docs/specs/<caso>/requirements.md
A2: FALSO — decisão da ADR está em 3 frases sem ação clara
X1: DESCONHECIDO — requirements menciona "autenticação" mas ADR não trata o tema
```

### Passo 3 — Veredito

**PRONTO_PARA_DEV** se todos os critérios R1–R6, A1–A5, X1–X3, O1–O2 são VERDADEIRO.

**BLOQUEADO** se qualquer critério é FALSO ou DESCONHECIDO bloqueante. Output:
```
BLOQUEADO — <N> gap(s) encontrado(s):
- [R2] requirements.md: seção Identificação tem placeholder não preenchido
- [A2] ADR-081: decisão não está em frase ativa única
- [X1] "autenticação" no requirements não tem correspondência na ADR
→ Retornar para architect/discovery; re-executar readiness-gate após correção.
```

### Passo 4 — Forward

- PRONTO_PARA_DEV → PMO roteia para developer (J3)
- BLOQUEADO → rewind para architect (ou discovery se gap for de elicitação); readiness-gate re-executa após correção
