---
mode: mapeamento-de-processo
depth: standard
notation: mermaid-swimlane
formality: senior-ba
personas: [humano-engagement]
validation_status: VALIDADO-stakeholder
context-brief: nao-aplicavel — exemplo didatico, entidade ficticia, sem pesquisa de entidade real (gate ADR-051)
---

# requirements.md — Mapeamento de Processo: **Liberação de Lote (Farmacêutica)**

> Exemplo trabalhado H1 — cenário regulado. Exercita RACI multi-funcional
> (QC/QA/Produção), gatilhos por evento (CoA, OOS), handoffs entre sistemas
> (LIMS↔SAP), regras de retrabalho/reprovação, e tratamento `compliance OUT`
> delegado ao `high-stakes-gate`. Anti-padrão declarativo×observacional
> exercitado em 6 atividades. Stakeholder validação: FICTÍCIA para didática.

## Identificação

- **Processo:** Liberação de lote farmacêutico (produto sólido oral) para distribuição.
- **Boundaries (anti-raso A2):** começa em `recebimento do CoA do fornecedor de API` e termina em `lote liberado para distribuição com etiqueta verde no SAP`.
- **Process owner (M2 — accountable único):** Gerente de Garantia da Qualidade (QA Manager).
- **Trigger (M1):** chegada do Certificado de Análise (CoA) do fornecedor de princípio ativo (API), recebido via LIMS.
- **Output (M1):** lote com status "Liberado" no SAP, etiqueta verde aplicada, registro de liberação assinado no LIMS.
- **Voice of Customer / CTQ (anti-raso A1):** cliente externo final = paciente; ele valoriza = **eficácia e segurança do medicamento** (pureza ≥ 99,5%, ausência de contaminantes, dose correta). CTQ regulatório auxiliar = ANVISA (aderência à RDC 658/2022).

## Dimensões MUST

### M2 — Process owner + RACI por sub-processo (modo `standard`)

| Sub-processo | Responsible (R) | Accountable (A) | Consulted (C) | Informed (I) |
|---|---|---|---|---|
| 1. Recebimento e análise de API | Analista QC | Coordenador QC | Suprimentos | QA, Produção |
| 2. Liberação de API para produção | Coordenador QC | QA Manager | Produção | Almoxarifado |
| 3. Produção do lote | Operador de Produção | Supervisor de Produção | QC (in-process) | QA |
| 4. Análise final do produto acabado | Analista QC | Coordenador QC | — | QA, Produção |
| 5. Revisão de batch record e liberação | Reviewer QA | QA Manager | QC, Produção | Logística, RA (Regulatory Affairs) |

### M3 — SIPOC por sub-processo

| Sub-processo | Supplier | Input | Output | Customer |
|---|---|---|---|---|
| 1 | Fornecedor de API | CoA + amostra de API | Resultado de análise no LIMS | Coordenador QC |
| 2 | QC | API aprovado | Ordem de liberação no SAP | Almoxarifado/Produção |
| 3 | Produção + QC | Materiais aprovados | Batch record preenchido + amostras | QC |
| 4 | Produção | Amostras de produto acabado | Resultado de análise final | QA |
| 5 | QA | Batch record completo | Lote liberado (etiqueta verde, SAP) | Logística |

### M4 — Business rules + Exceptions + Handoffs

#### Rules nos gateways
- **G1 (após análise API):** SE resultado dentro da especificação ENTÃO API aprovada; SENÃO API reprovada → notificar Suprimentos.
- **G2 (após análise de produto acabado):** SE todos os parâmetros dentro da especificação E batch record completo ENTÃO seguir para revisão QA; SENÃO abrir investigação OOS (Out-of-Specification).
- **G3 (revisão QA):** SE batch record completo E sem desvios não-justificados ENTÃO liberar; SE desvio passível de justificativa documentada ENTÃO QA decide caso-a-caso; SENÃO reprovar lote.

#### Exceptions (sad paths)
- **E1 — API reprovado:** lote nem inicia produção; notificação ao fornecedor; ressarcimento.
- **E2 — OOS no produto acabado:** abre investigação formal (Out-of-Specification investigation); produção para; QA Manager + Coordenador QC reunem em 24h.
- **E3 — Desvio crítico durante produção:** Supervisor de Produção aciona QA; decisão de continuar/parar é do QA Manager (ele é o accountable do owner).
- **E4 — Quarentena estendida por contaminação suspeita:** lote permanece em "Quarentena Cinza" no SAP até investigação fechar.

#### Handoffs (modo `standard`)

| De (papel/sistema) | Para (papel/sistema) | O que é transferido | Modo | Risco |
|---|---|---|---|---|
| Fornecedor → LIMS | LIMS → Analista QC | CoA + amostra | Síncrono (recebimento físico) | Médio (atraso pode parar produção) |
| QC (LIMS) → SAP | SAP → Almoxarifado | Status "Liberado" da matéria-prima | Assíncrono (integração LIMS↔SAP) | **ALTO** — handoff sistema-sistema, dependente de integração funcional |
| Produção (batch record papel/eletrônico) → QA | QA reviewer | Batch record completo + amostras | Síncrono ou assíncrono dependendo do MES | Alto (erro de transcrição comum quando híbrido) |
| QA → Logística (SAP) | Logística | Lote com etiqueta verde | Assíncrono | Baixo |

## Dimensões MAY (não ativadas neste exemplo — modo `standard` default; ativaria em `deep`)

- **MAY1 — Métricas operacionais:** lead time típico = 18-24 dias (recebimento de API → liberação). Cycle time da revisão QA = 2-5 dias úteis. `[DECLARADO por QA Manager — métrica não confirmada por log do LIMS]`
- **MAY2 — Mapa tecnológico:** LIMS (LabWare), SAP S/4HANA, MES eletrônico parcial (algumas linhas ainda usam batch record papel).
- **MAY3 — Variações:** lotes destinados a exportação Mercosul têm trilha de auditoria adicional + assinatura adicional do RA. `[OBSERVADO em SOP-LIB-007]`

## Condicional as-is-only

- **C1 — Pain points (vide `gap-analysis.md`):** registrados — há processo rodando hoje.

## Anti-raso BPM

- **A1 — VoC/CTQ:** ✅ preenchido na Identificação (paciente + ANVISA).
- **A2 — Boundaries:** ✅ preenchidos na Identificação.
- **A3 — Declarativo × Observacional:** vide `process-map-as-is.md` — 6 atividades com tag explícita; 1 divergência detectada (vide `gap-analysis.md` D1).
- **A4 — Validação stakeholders:** ✅ `[VALIDADO — fictício para didática — 2026-05-25 por QA Manager fictícia e Coordenador QC fictício]`.

## Fora de escopo (deste mapa)

- **Compliance/ALCOA+/audit trail ANVISA**: delegado ao `high-stakes-gate`. Este mapa apenas registra atividades; controles formais e trilha de auditoria são tratados pela camada de compliance — não pelo discovery.
- **Desenho do to-be:** `architect` produzirá ADR(s) a partir do `gap-analysis.md`. Discovery não desenha o processo redesenhado.
- **Validação de método analítico, qualificação de equipamento, calibração:** processos distintos com seus próprios mapas.

## Fontes (file-first)

- Stakeholders entrevistados (fictícios): QA Manager, Coordenador QC, Supervisor de Produção.
- Documentos consultados: SOP-LIB-007 (Procedimento Operacional Padrão de Liberação de Lote, fictício).
- Sistemas auditados pelo explorer: LIMS (LabWare) — workflow de aprovação de matéria-prima e produto acabado; SAP S/4HANA — transações MIGO, QA32, QA11.

## Lacunas abertas (anti-alucinação)

- `[DESCONHECIDO]` Tempo médio real (P50/P95) do sub-processo 5 (revisão QA). Métrica declarada por QA Manager (2-5 dias) mas log do LIMS sugere variância maior — investigar.
- `[DESCONHECIDO]` Há tratamento formal para lotes com desvio menor "justificável"? SOP-LIB-007 diz "QA decide caso-a-caso" — falta critério escrito.

## Glossário do caso

- **API** — Active Pharmaceutical Ingredient (princípio ativo).
- **CoA** — Certificate of Analysis (Certificado de Análise do fornecedor).
- **OOS** — Out-of-Specification (resultado fora da especificação).
- **Batch record** — registro completo da produção de um lote.
- **Etiqueta verde** — indicação visual de lote liberado para distribuição (vs etiqueta amarela = quarentena, vermelha = reprovado).
- **ALCOA+** — princípios de integridade de dados: Attributable, Legible, Contemporaneous, Original, Accurate, + Complete, Consistent, Enduring, Available.
- **RDC 658/2022** — Resolução ANVISA sobre Boas Práticas de Fabricação.
