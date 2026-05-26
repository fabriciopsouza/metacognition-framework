---
mode: mapeamento-de-processo
depth: standard
notation: mermaid-swimlane
formality: senior-ba
personas: [humano-engagement]
validation_status: VALIDADO-stakeholder
gap_severity_max: alto
---

# gap-analysis.md — Diagnóstico do as-is: **Liberação de Lote Farmacêutico**

> Companion do `process-map-as-is.md` (mesma pasta). Diagnóstico do as-is.
> **Entrega ao `architect`** — perguntas de to-be design vão na seção
> "Itens para architect". Discovery NÃO desenha to-be.

## Sumário executivo

O as-is da liberação de lote tem **5 gaps** com severidade variando de médio a
alto. Dois gaps são estruturais (integração LIMS↔SAP frágil; batch record
híbrido papel+MES gera erros de transcrição). Um gap é semântico crítico:
gateway G3 ("desvio justificável") sem critério escrito — 12 lotes liberados
nessa categoria sem rastreabilidade auditável. Um gap é declarativo×observacional:
QA Manager diz "decisão caso-a-caso" mas observação revela padrão silencioso.
Quarto gap = ALCOA+ está delegado ao high-stakes-gate (não é gap deste mapa, mas
está flagado para coordenação). O architect deve priorizar G3 (semântico/auditoria)
e G2 (handoff de sistema) na produção de to-be ADR.

## Gaps detectados

### Gap G1 — Integração LIMS↔SAP frágil
- **Severidade:** **ALTO**
- **Onde no mapa:** handoff A3→A4 (QC LIMS → SAP); atividade A4 (integração automática)
- **Natureza:** handoff de sistema sem owner humano + 15 falhas observadas em 12 meses
- **Evidência:** `[OBSERVADO em logs de retry da integração + RNCs abertas]`
- **Impacto:** atrasa liberação até 48h por incidente; já causou backlog de produção.
- **Sugestão (sem desenhar to-be):** o architect deve decidir se a integração ganha owner humano (operador de IT/QA monitorando) ou se vira síncrona com falha visível, ou se há redundância de mecanismo.

### Gap G2 — Batch record híbrido papel+MES gera erros de transcrição
- **Severidade:** **ALTO**
- **Onde no mapa:** handoff A6→A10 (Produção → QA)
- **Natureza:** handoff de papel para eletrônico; transcrição manual
- **Evidência:** `[OBSERVADO em RNCs: 8 não-conformidades de "divergência batch record papel × MES" nos últimos 12 meses]`
- **Impacto:** retrabalho de QA; possível questionamento em inspeção ANVISA.
- **Sugestão (sem desenhar to-be):** o architect deve decidir se to-be requer MES eletrônico 100% (substituindo papel) ou se mantém híbrido com controle de transcrição reforçado. Decisão tem CAPEX implicado — fora do escopo deste mapa.

### Gap G3 — Gateway G3 "desvio justificável" sem critério escrito (anti-padrão #1)
- **Severidade:** **ALTO** (auditoria/compliance)
- **Onde no mapa:** atividade A11 (Decisão sobre desvio justificável)
- **Natureza:** divergência declarativo×observacional + ausência de critério escrito
- **Evidência:** `[DIVERGÊNCIA — DECLARADO por QA Manager: "decisão caso-a-caso" | OBSERVADO em LIMS: 12 lotes liberados com desvios "justificáveis" sem critério rastreável nos últimos 6 meses]`
- **Impacto:** risco regulatório real — em uma inspeção ANVISA, "decisão caso-a-caso sem critério" é um achado crítico (RDC 658/2022). Pode gerar 483 (FDA-equivalent).
- **Sugestão (sem desenhar to-be):** o architect deve decidir se to-be exige critério escrito formal (matriz de severidade de desvio) ou se a decisão precisa de QA Manager + RA + Coordenador QC (3 assinaturas) caso-a-caso para criar trilha de auditoria. Discovery não decide entre as duas — apenas nomeia o gap.

### Gap G4 — Atividade A7 (QC in-process) sem rastro digital completo
- **Severidade:** **MÉDIO**
- **Onde no mapa:** atividade A7 (QC in-process — amostragem intermediária)
- **Natureza:** declarativo apenas — log do LIMS é incompleto para amostragem intermediária
- **Evidência:** `[DECLARADO por Analista QC: amostragem intermediária acontece, mas log do LIMS só registra ~60% dessas amostragens]`
- **Impacto:** lacuna ALCOA+ — "Original" e "Contemporaneous" comprometidos em 40% das ocorrências.
- **Sugestão:** o architect coordena com high-stakes-gate. Pode ser que esse gap caia inteiramente no high-stakes-gate (não no to-be do processo).

### Gap G5 — Owner do retrabalho de exceção E3 (desvio crítico) ambíguo
- **Severidade:** **MÉDIO**
- **Onde no mapa:** exceção E3
- **Natureza:** dono ambíguo
- **Evidência:** `[DECLARADO por Supervisor de Produção: "aciono QA"]` — mas QA Manager diz "Supervisor decide se chama"; observação: 3 ocorrências em 12 meses, em 1 delas Supervisor decidiu sozinho sem QA.
- **Impacto:** risco de retrabalho não documentado.
- **Sugestão:** to-be ADR deve nomear accountable único para E3.

## Pain points (C1)

| # | Pain point | Atividade | Quem reporta | Frequência |
|---|---|---|---|---|
| P1 | "Espero o SAP atualizar para soltar material" | A4-A5 | Supervisor Produção | Diária |
| P2 | "Refaço o batch record digital porque o papel não casa" | A10 | Reviewer QA | Semanal |
| P3 | "Não sei se preciso chamar QA quando o desvio é só de tempo" | A11/E3 | Supervisor Produção | Mensal |

## Bottlenecks (C1)

| # | Bottleneck | Atividade | Métrica | Causa raiz suspeita |
|---|---|---|---|---|
| B1 | Revisão de batch record acumula | A10 | Cycle time P95 = 7 dias (declarado 2-5) | Reviewer QA único; batch record híbrido lento |

## Divergências `[DECLARADO]` × `[OBSERVADO]`

| # | Atividade | Declarado | Observado | Lacuna semântica |
|---|---|---|---|---|
| D1 | A11 (G3 branch) | "QA decide caso-a-caso" | 12 lotes liberados sem critério escrito em 6 meses | Decisão de fato existe como padrão silencioso — não é "caso-a-caso", é "sempre justifica" |
| D2 | A7 (QC in-process) | "Sempre registro" | LIMS só tem ~60% das amostragens | Registro retrospectivo viola ALCOA+ "Contemporaneous" |

## Itens para architect (handoff explícito)

> Discovery **não responde** estas perguntas — apenas as nomeia. Architect produz ADR(s) de to-be.

1. **Decisão pendente — Integração LIMS↔SAP (resolve G1):**
   - Contexto: handoff sistema-sistema com 15 falhas em 12 meses, sem owner humano.
   - Alternativas a considerar (sem decidir): (a) owner humano de monitoramento; (b) integração síncrona com falha visível ao operador; (c) redundância via segundo mecanismo de update.
2. **Decisão pendente — Batch record (resolve G2):**
   - Contexto: híbrido papel+MES gera erros de transcrição; 8 RNCs em 12 meses.
   - Alternativas a considerar: (a) MES eletrônico 100% (CAPEX); (b) processo de double-check formal na transcrição; (c) escâner OCR para reconciliar papel↔MES automaticamente.
3. **Decisão pendente — Critério do gateway G3 (resolve G3 e D1):**
   - Contexto: "desvio justificável" sem critério escrito é achado crítico de inspeção.
   - Alternativas a considerar: (a) matriz formal de severidade de desvio (escrita); (b) 3 assinaturas obrigatórias (QA Manager + RA + Coordenador QC) caso-a-caso; (c) eliminação da categoria "justificável" — só "aprovado" ou "reprovado".
4. **Decisão pendente — Coordenação com high-stakes-gate (resolve G4):**
   - Contexto: lacuna ALCOA+ em A7 pode ser tratada no `high-stakes-gate` (não no to-be do processo).
   - Alternativas a considerar: (a) escalar para high-stakes-gate como camada separada; (b) incluir validação ALCOA+ no to-be do processo; (c) ambos em camadas distintas.
5. **Decisão pendente — Accountable de E3 (resolve G5):**
   - Contexto: dono ambíguo de desvio crítico — 1 ocorrência sem QA em 12 meses.
   - Alternativas a considerar: (a) Supervisor de Produção tem autonomia documentada; (b) QA Manager sempre acionado; (c) árvore de decisão escrita por tipo de desvio.

## Bloco de escalação

> Não aplicável — persona = humano-engagement, validação stakeholder concluída (`[VALIDADO — fictício para didática]`).

## Lacunas remanescentes

- `[DESCONHECIDO]` Tempo real (P50/P95) do sub-processo 5 (revisão QA) — declarado 2-5 dias, observado 7 dias P95. Investigação pendente.
- `[DESCONHECIDO]` Existe alguma política de "desvio justificável" em SOP que ninguém lembrou de citar? File-first do explorer pode ter perdido — recomendar busca em wiki/SharePoint da QA.
