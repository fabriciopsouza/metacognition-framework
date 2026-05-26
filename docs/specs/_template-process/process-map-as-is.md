---
mode: mapeamento-de-processo
depth: standard
notation: mermaid-flow
formality: senior-ba
personas: [humano-engagement]
validation_status: PENDENTE
as_is_source: declarativo   # declarativo | observacional | misto
---

# process-map-as-is.md — Mapa as-is: `<nome-do-processo>`

> Mapa do **estado atual** do processo. Cada atividade carrega tag
> `[DECLARADO]` (stakeholder disse) ou `[OBSERVADO]` (fonte direta: log de
> sistema, observação, baseline golden). Quando ambos rodam (EARS-W5),
> divergências viram `[DIVERGÊNCIA]` no gap-analysis.md.

## Cabeçalho operacional

- **Processo:** <nome>
- **Boundaries (anti-raso A2):** começa em `<atividade-A>`, termina em `<atividade-Z>`.
- **Process owner:** <nome>
- **Voice of Customer / CTQ (anti-raso A1):** cliente externo final = `<quem>`; ele valoriza = `<o que é Critical-to-Quality>`.
- **Período de levantamento:** <YYYY-MM-DD a YYYY-MM-DD>
- **Validação stakeholder (anti-raso A4):** [PENDENTE | VALIDADO em YYYY-MM-DD por `<nome>` | BLOQUEADOR: validação humana pendente — pipeline persona-4]

## SIPOC

| Suppliers | Inputs | Process (resumo) | Outputs | Customers |
|---|---|---|---|---|
| <quem fornece> | <o que entra> | <resumo do processo em 1-3 linhas> | <o que sai> | <quem recebe> |

## Mapa as-is — diagrama

> Notação configurada: `<notation>` no cabeçalho YAML acima.

```mermaid
%% Notação: mermaid-flow (default). Trocar bloco para swimlane/sequence conforme `notation`.
flowchart TD
  Start([Trigger: <evento>]) --> A1[Atividade 1<br/>[DECLARADO]]
  A1 --> A2[Atividade 2<br/>[OBSERVADO]]
  A2 --> G1{Gateway:<br/>regra de decisão}
  G1 -->|sim| A3[Atividade 3<br/>[DECLARADO]]
  G1 -->|não| A4[Atividade 4 (exceção)<br/>[DECLARADO]]
  A3 --> End([Output: <entregável>])
  A4 --> End
```

## Atividades — descrição linha-por-linha

| # | Atividade | Quem (RACI A) | Inputs | Outputs | Sistemas tocados | Tag origem |
|---|---|---|---|---|---|---|
| A1 | <nome> | <papel R/A> | <input> | <output> | <sistema/N/A> | `[DECLARADO]` ou `[OBSERVADO]` |
| A2 | <nome> | <papel R/A> | <input> | <output> | <sistema/N/A> | `[DECLARADO]` ou `[OBSERVADO]` |
| ... | | | | | | |

## Business rules (M4)

- **Gateway G1:** `<regra de decisão exata>` — `[DECLARADO por <stakeholder>]` ou `[OBSERVADO em <log/sistema>]`.

## Exceções (M4 — sad paths)

- **Excepção E1:** `<descrição>` → tratamento: `<atividade>`.

## Handoffs (M4 — em `standard`/`deep`)

| De (papel/sistema) | Para (papel/sistema) | O que é transferido | Modo (síncrono/assíncrono) | Risco |
|---|---|---|---|---|
| <de> | <para> | <artefato> | <síncrono\|assíncrono> | <alto\|médio\|baixo> |

## Métricas operacionais (MAY1 — só em `deep` ou sob pedido)

| Atividade | Cycle time | Lead time | Volume/período | Frequência |
|---|---|---|---|---|
| A1 | <> | <> | <> | <> |

## Variações (MAY3 — quando aplicável)

- **Classe V1:** `<segmento/regional/valor>` — desvia em `<atividade>`.

## Validação (anti-raso A4)

- **Status:** vide cabeçalho YAML.
- **Validado por:** `<nome do process owner + 1 executor>` em `<YYYY-MM-DD>`.
- **Mudanças solicitadas na validação:** `<lista — pode ser vazia>`.
- **Se persona=4 e sem stakeholder:** abrir bloco `[BLOQUEADOR: validação humana pendente]` no `gap-analysis.md` e encerrar pipeline com exit-code não-zero.
