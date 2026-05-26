---
mode: mapeamento-de-processo
depth: standard            # quick | standard | deep
notation: mermaid-flow     # markdown-only | mermaid-flow | mermaid-swimlane | bpmn-lite | custom
formality: senior-ba       # lean | senior-ba | bpmn-2.0-strict
personas: [humano-engagement]   # humano-engagement | humano-pessoal | terceiro-repo | subagente-automatizado
validation_status: PENDENTE     # PENDENTE | VALIDADO-stakeholder | BLOQUEADOR-sem-stakeholder
---

# requirements.md — Mapeamento de Processo: `<nome-do-processo>`

> Clonado de `docs/specs/_template-process/`. Spec do método em
> `docs/specs/discovery-process-mapping/requirements.md`. ADR-002 ratifica.

## Identificação

- **Processo:** <nome único do processo de negócio>
- **Boundaries (anti-raso A2):** começa em `<1ª atividade observável>` e termina em `<última atividade observável>`.
- **Process owner (M2 — accountable único):** <nome | DESCONHECIDO>
- **Trigger (M1):** <evento | agendamento | condição que inicia>
- **Output (M1):** <entregável | decisão | registro final>
- **Voice of Customer / CTQ (anti-raso A1):** cliente externo final = `<quem>`; ele valoriza = `<o que (CTQ)>`.

## Dimensões MUST

### M2 — Process owner + RACI por atividade
<conforme profundidade: só owner em `quick`; RACI por sub-processo em `standard`; RACI por atividade em `deep`>

### M3 — Inputs/Outputs (SIPOC)
<SIPOC macro em `quick`; SIPOC por sub-processo em `standard`; linha-por-atividade em `deep`>

### M4 — Business rules + Exceptions + Handoffs
- **Rules nos gateways:** <regras de decisão>
- **Exceptions (sad-paths):** <desvios do happy path>
- **Handoffs (em `standard`/`deep`):** <transferências de responsabilidade entre papéis/sistemas>

## Dimensões MAY (apenas em `deep` ou sob pedido)

- **MAY1 — Métricas operacionais:** cycle time · lead time · volume · frequência.
- **MAY2 — Mapa tecnológico:** sistemas e dados tocados por atividade.
- **MAY3 — Variações:** caminhos por segmento/regional/valor (máx 5 classes).
- **MAY4 — Lean/maturity:** value-add classification (VA/BVA/NVA) · CMMI level.

## Condicional as-is-only

- **C1 — Pain points + bottlenecks:** <listar quando há processo rodando; OUT se greenfield>

## Anti-raso BPM (sempre presentes)

- **A1 — VoC/CTQ:** preenchido na seção Identificação.
- **A2 — Boundaries:** preenchidos na seção Identificação.
- **A3 — Declarativo × Observacional:** vide `process-map-as-is.md` (tag por atividade).
- **A4 — Validação stakeholders:** ver header YAML `validation_status`.

## Fora de escopo (deste mapa)

- Compliance/audit trail → `high-stakes-gate`.
- Desenho do to-be → `architect` (via ADR — consultar `gap-analysis.md`).
- Process simulation, RPA, change management.

## Fontes (file-first)

- Stakeholders entrevistados: `<lista>`
- Documentos consultados: `<lista>`
- Sistemas auditados pelo explorer: `<lista — se EARS-W5 ativo>`

## Lacunas abertas (anti-alucinação)

- `[DESCONHECIDO]` <item não confirmado pelo stakeholder + como validar>

## Glossário do caso

- <termos específicos do domínio deste processo>
