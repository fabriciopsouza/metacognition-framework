---
mode: mapeamento-de-processo
depth: standard
notation: mermaid-swimlane
formality: senior-ba
personas: [humano-engagement]
validation_status: VALIDADO-stakeholder
as_is_source: misto
---

# process-map-as-is.md — Mapa as-is: **Liberação de Lote Farmacêutico**

> Tags por atividade: `[DECLARADO]` (stakeholder disse) ou `[OBSERVADO]`
> (fonte direta: log LIMS, query SAP, observação direta de bancada).
> Divergências entre tags vão para `gap-analysis.md` como `[DIVERGÊNCIA]`.

## Cabeçalho operacional

- **Processo:** Liberação de Lote Farmacêutico (produto sólido oral)
- **Boundaries:** começa em `recebimento de CoA do fornecedor de API`, termina em `lote liberado com etiqueta verde no SAP`.
- **Process owner:** QA Manager (fictícia).
- **Período de levantamento:** 2026-05-01 a 2026-05-20 (fictício).
- **Validação stakeholder:** `[VALIDADO — fictício para didática — 2026-05-25 por QA Manager + Coordenador QC]`

## SIPOC

| Suppliers | Inputs | Process (resumo) | Outputs | Customers |
|---|---|---|---|---|
| Fornecedor de API; Produção; QC; QA | CoA, amostras, batch record | Recebimento → análise QC → produção → análise final → revisão QA → liberação | Lote com etiqueta verde no SAP; CoA assinado pelo QA | Logística; mercado consumidor (paciente) |

## Mapa as-is — diagrama (swimlane)

```mermaid
%% Notação: mermaid-swimlane (raias por papel/sistema). Aderência aproximada — Mermaid não tem swimlane formal, mas subgraphs simulam.
flowchart TD
  subgraph S1[Fornecedor]
    F1([Trigger: CoA emitido]) --> F2[Envia CoA + amostra<br/>[OBSERVADO em LIMS-inbox]]
  end
  subgraph S2[QC]
    F2 --> Q1[Analista QC<br/>realiza análise de API<br/>[OBSERVADO em LIMS]]
    Q1 --> G1{API dentro<br/>da especificação?}
    G1 -->|sim| Q2[Coordenador QC<br/>aprova no LIMS<br/>[OBSERVADO em LIMS]]
    G1 -->|não| E1[/Exceção E1:<br/>API reprovado/]
  end
  subgraph S3[SAP/Almoxarifado]
    Q2 --> A1[Integração LIMS→SAP<br/>status muda para Liberado<br/>[OBSERVADO em SAP query MIGO]]
    A1 --> A2[Almoxarifado libera<br/>material para Produção<br/>[DECLARADO por Supervisor]]
  end
  subgraph S4[Produção]
    A2 --> P1[Operador produz lote<br/>preenche batch record<br/>[DECLARADO por Supervisor]]
    P1 --> P2[QC in-process<br/>coleta amostras intermediárias<br/>[DECLARADO por Analista QC]]
    P2 --> P3[Produção finaliza<br/>envia produto acabado para QC<br/>[OBSERVADO em MES parcial]]
  end
  subgraph S5[QC final]
    P3 --> QF1[Analista QC<br/>análise de produto acabado<br/>[OBSERVADO em LIMS]]
    QF1 --> G2{Resultado dentro<br/>da especificação?}
    G2 -->|sim| QF2[Coordenador QC<br/>aprova produto acabado]
    G2 -->|não| E2[/Exceção E2:<br/>investigação OOS/]
  end
  subgraph S6[QA]
    QF2 --> QA1[Reviewer QA<br/>revisa batch record<br/>[DECLARADO por QA Manager]]
    QA1 --> G3{Batch record OK<br/>e sem desvios?}
    G3 -->|sim| QA2[QA Manager<br/>assina liberação no LIMS<br/>[OBSERVADO em LIMS]]
    G3 -->|desvio justificável| QA3[QA Manager<br/>decide caso-a-caso<br/>[DECLARADO — sem critério escrito]]
    G3 -->|não| E3[/Reprovado:<br/>investigação ou descarte/]
    QA3 -->|aprovado| QA2
    QA3 -->|reprovado| E3
  end
  subgraph S7[SAP final]
    QA2 --> End([Lote liberado<br/>etiqueta verde no SAP<br/>[OBSERVADO em SAP query QA11]])
  end
```

## Atividades — descrição linha-por-linha

| # | Atividade | Quem (RACI A) | Inputs | Outputs | Sistemas tocados | Tag origem |
|---|---|---|---|---|---|---|
| A1 | Recebimento de CoA do fornecedor | Coordenador QC | CoA + amostra física | Registro em LIMS-inbox | LIMS | `[OBSERVADO]` |
| A2 | Análise de API no QC | Coordenador QC | Amostra de API | Resultado analítico no LIMS | LIMS | `[OBSERVADO]` |
| A3 | Aprovação de API (gateway G1) | Coordenador QC | Resultado dentro especificação | Status "Aprovado" no LIMS | LIMS | `[OBSERVADO]` |
| A4 | Integração LIMS→SAP (status Liberado) | (sistema, sem dono humano direto) | Aprovação LIMS | Status SAP atualizado | LIMS, SAP | `[OBSERVADO]` |
| A5 | Almoxarifado libera material para Produção | Supervisor de Produção | API liberado no SAP | API física na linha | SAP, físico | `[DECLARADO]` — sem rastro digital |
| A6 | Produção do lote | Supervisor de Produção | API + outros materiais | Produto acabado + batch record | MES parcial / papel | `[DECLARADO]` |
| A7 | QC in-process (amostragem intermediária) | Coordenador QC | Amostras de bancada | Resultados intermediários | LIMS | `[DECLARADO]` — log nem sempre completo |
| A8 | Análise final do produto acabado | Coordenador QC | Amostras de produto acabado | Resultado analítico | LIMS | `[OBSERVADO]` |
| A9 | Aprovação produto acabado (gateway G2) | Coordenador QC | Resultado dentro especificação | Status aprovado no LIMS | LIMS | `[OBSERVADO]` |
| A10 | Revisão de batch record | QA Manager | Batch record completo | Aprovação ou pedido de complemento | papel/MES + LIMS | `[DECLARADO]` |
| A11 | Decisão sobre desvio justificável (G3 branch) | QA Manager | Batch record com desvio | Decisão caso-a-caso | — | `[DECLARADO — sem critério escrito]` |
| A12 | Liberação final do lote | QA Manager | Batch record OK | Etiqueta verde no SAP | LIMS, SAP | `[OBSERVADO]` |

## Business rules (M4)

- **Gateway G1 (após análise API):** SE `[parâmetros do CoA] ∈ [especificação SOP-LIB-007 secção 4.2]` ENTÃO aprovar; SENÃO reprovar e notificar Suprimentos. `[OBSERVADO em SOP-LIB-007 + log LIMS]`
- **Gateway G2 (após análise final):** SE `[todos parâmetros] ∈ [especificação] E [batch record completo]` ENTÃO seguir para QA; SENÃO abrir OOS. `[OBSERVADO em SOP-LIB-007]`
- **Gateway G3 (revisão QA):** SE batch record OK e sem desvios ENTÃO liberar (caminho normal); SE desvio justificável ENTÃO QA decide caso-a-caso (sem critério escrito — `[DECLARADO]` apenas); SE desvio crítico ENTÃO reprovar. **`[DIVERGÊNCIA]`: stakeholder declara que "QA decide caso-a-caso" mas observação revela 12 lotes com desvios "justificados" nos últimos 6 meses sem critério documentado.**

## Exceções (M4 — sad paths)

- **E1 — API reprovado:** notificação Suprimentos via e-mail + abertura de RNC (Registro de Não-Conformidade) no SAP. `[OBSERVADO]`
- **E2 — OOS no produto acabado:** abre investigação formal em 24h; QA Manager + Coordenador QC convocam reunião; lote permanece em "Quarentena Amarela". `[OBSERVADO em registro de OOS dos últimos 12 meses]`
- **E3 — Desvio crítico em produção:** Supervisor aciona QA; decisão de continuar/parar é do QA Manager. `[DECLARADO]`
- **E4 — Quarentena estendida:** lote em "Quarentena Cinza" no SAP até investigação fechar. `[OBSERVADO]`

## Handoffs (M4)

| De (papel/sistema) | Para (papel/sistema) | O que é transferido | Modo | Risco |
|---|---|---|---|---|
| Fornecedor → LIMS-inbox | Analista QC | CoA + amostra física | Síncrono (físico) | Médio |
| QC (LIMS) → Integração → SAP | Almoxarifado | Status "Liberado" | Assíncrono | **ALTO** — falhas de integração causam atraso (15 ocorrências nos últimos 12 meses, `[OBSERVADO]`) |
| Produção (batch record híbrido papel+MES) → QA | QA reviewer | Batch record completo | Assíncrono | **ALTO** — erros de transcrição papel→eletrônico (`[OBSERVADO em RNCs]`) |
| QA → SAP (etiqueta verde) | Logística | Lote liberado | Assíncrono | Baixo |

## Validação (anti-raso A4)

- **Status:** `[VALIDADO — fictício para didática — 2026-05-25]`.
- **Validado por:** QA Manager fictícia (process owner) + Coordenador QC fictício (executor).
- **Mudanças solicitadas na validação:** nenhuma estrutural; um esclarecimento sobre o critério do desvio justificável (G3 branch) — registrado como gap G3 no `gap-analysis.md`.
- **Persona executor:** humano-engagement (não persona 4). Bloco `[BLOQUEADOR]` não se aplica.

## Compliance OUT (referência cruzada)

> Trilha de auditoria ALCOA+, validação ANVISA, ALCOA+ por atividade, e logging
> imutável NÃO são tratados por este mapa. Pertencem ao `high-stakes-gate`
> que se aciona em paralelo. Este mapa apenas registra que cada atividade
> tem ou não controle regulatório associado — não desenha o controle.

| Atividade | Tem controle regulatório? | Onde está documentado |
|---|---|---|
| A1-A4 (QC/SAP) | Sim — ALCOA+ aplicável a LIMS | SOP-LIB-007 + procedimentos LIMS |
| A5-A7 (Produção) | Sim — batch record é GMP obrigatório | RDC 658/2022 + SOPs de produção |
| A8-A9 (QC final) | Sim | SOP-LIB-007 |
| A10-A12 (QA) | Sim — assinatura é registro regulatório | RDC 658/2022 |
