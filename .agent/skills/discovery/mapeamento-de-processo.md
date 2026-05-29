# Sub-modo "mapeamento de processo" — discovery v1.6.0

> **Companion da `.agent/skills/discovery/SKILL.md`.** Carregar SOB DEMANDA
> quando o filtro de entrada deste sub-modo ativar. Não é skill autônoma —
> é uma extensão modular do papel `discovery` para BPM-sênior. Padrão:
> progressive disclosure (ADR-003).
>
> Spec completa: `docs/specs/discovery-process-mapping/requirements.md`.
> Decisão arquitetural: `docs/adr/002-discovery-process-mapping-v160.md`.

## Quando ativar este sub-modo
Trabalho é **processo de negócio** (fluxo cross-funcional com gatilhos, donos, RACI, regras, handoffs, exceções).

### Filtro de entrada
1ª pergunta após detectar natureza = processo: **"isto é processo de negócio ou um dos 4 redirecionáveis?"**
- **ATIVA quando:** processo de negócio (cross-funcional, com gatilhos/donos/regras/handoffs).
- **NÃO ATIVA (REDIRECIONAR) quando:**
  - **Jornada UI** (fluxo de telas em app/site) → discovery trilha web/produto.
  - **Runbook / passo-a-passo técnico** (deploy, rollback, restart) → developer/docops.
  - **Algoritmo / fluxo de código** (função interna, pipeline ETL) → developer/dev.
  - **Workflow de aprovação de ferramenta** (PR no GitHub, ticket no Jira) → configuração da ferramenta (fora de discovery).

### Profundidade
Operador escolhe explicitamente no início (após filtro de entrada):
- **`quick`** — SIPOC + macro (5-9 etapas no mapa). Alinhamento inicial.
- **`standard`** *(default)* — macro + sub-processo (15-40 atividades). Padrão de engagement BPM sério.
- **`deep`** — atividade granular com I/O por atividade. Projeto de melhoria.

### Notação plugável (operador escolhe por caso)
- markdown-só (zero dependência de render)
- +Mermaid flow/sequence (GitHub/Claude.ai renderizam nativo)
- +Mermaid swimlane / BPMN-lite (raias por papel/sistema — padrão BA sênior)
- plug livre (Mermaid completo, PlantUML, etc.)

### Formalidade configurável (operador escolhe por caso)
- pragmático/lean — vocabulário acessível, sem jargão BPMN puro
- sênior BA prático — SIPOC, RACI, swimlane, gateway, gatilho (padrão de mercado)
- BPMN 2.0 estrito — aderência à norma (para BPMS/auditoria)
- per case — discovery pergunta no início

### Matriz de dimensões (13 nominais — modulada por profundidade)

#### MUST (4 blocos — sempre presentes)

| # | Dimensão | `quick` | `standard` (default) | `deep` |
|---|---|---|---|---|
| M1 | **Trigger + Output** | 1 trigger + 1 output | + 1 condição alternativa | tipo (evento/temporal/condicional) + outputs por variação |
| M2 | **Process owner + RACI** | **apenas owner** (1 campo) | + RACI agregada por sub-processo | RACI completa por atividade |
| M3 | **Inputs/Outputs por atividade** (SIPOC) | **SIPOC macro** (1 linha p/ processo inteiro) | linha por sub-processo | linha por atividade |
| M4 | **Business rules + Exceptions + Handoffs** | **rules + exceptions principais** | + handoffs em tabela | + diagrama visual de handoffs |

#### MAY (4 blocos — ativados em `deep` ou sob pedido)

- **MAY1 — Métricas operacionais:** cycle/lead time, volume, frequência.
- **MAY2 — Mapa tecnológico:** sistemas e dados tocados por atividade.
- **MAY3 — Variações:** caminhos por segmento/regional/valor (máx 5 classes).
- **MAY4 — Lean/maturity:** value-add classification (VA/BVA/NVA) + CMMI level.

#### Condicional as-is-only

- **C1 — Pain points + bottlenecks:** MUST quando há processo rodando hoje; OUT em greenfield.

#### Anti-raso BPM (4 itens — sempre presentes)

- **A1 — Voice of Customer / CTQ:** cliente externo final + Critical-to-Quality. MUST.
- **A2 — Boundaries explícitos:** onde COMEÇA e onde TERMINA o processo. MUST.
- **A3 — Declarativo × Observacional** *(anti-padrão #1 do BPM)*: tag por atividade `[DECLARADO]` ou `[OBSERVADO]`. Comparar é o ponto quando ambos rodam.
- **A4 — Validação com stakeholders antes de fechar:** ver seção dedicada abaixo.

#### Fora de escopo deste sub-modo

- Compliance/audit trail → `high-stakes-gate` quando declarado pelo discovery (ADR-010).
- Desenho do to-be → `architect` via ADR de processo.
- Process simulation, RPA recommendation, change management, process mining industrial, KPI/OKR design.

### Output em 3 arquivos
Em `docs/specs/<caso>/` (clonar `docs/specs/_template-process/`):
- `requirements.md` — dimensões MUST/MAY + boundaries + VoC/CTQ + validação.
- `process-map-as-is.md` — mapa com diagrama na notação configurada + tags `[DECLARADO]`/`[OBSERVADO]`.
- `gap-analysis.md` — diagnóstico com seção MUST `## Itens para architect`.

**Cabeçalho YAML obrigatório** em CADA artefato quando persona=subagente-automatizado (`mode`, `depth`, `notation`, `formality`, `personas`, `validation_status`). Garante parseabilidade independente da notação.

### Integração com explorer (EARS-W5)
Quando o processo está em código/sistema (BPMS, n8n, Airflow, workflow de SaaS):
- **Single-thread (default — Claude Code sem subagentes reais):** discovery faz etnografia humana; depois explorer audita o código (sequência rápida no mesmo turno). Discovery consolida ambos em `gap-analysis.md`.
- **Persona 4 (pipeline automatizado com infraestrutura):** discovery e explorer rodam como subagentes reais em paralelo. Orquestrador faz cruzamento.

Em ambos os modos, o **cruzamento** é feito pelo discovery — detecta o gap entre **as-is-declarado** (stakeholder), **as-is-codificado** (sistema) e **as-is-real** (observação). Anti-padrão #1 do BPM tratado built-in.

### Validação com stakeholders (anti-raso A4)
Passo **MUST de encerramento** do sub-modo — o mapa não fecha sem revisão explícita por process owner + 1 executor.
- **Persona humana (engagement / pessoal / terceiro):** sem revisão → marcar `[VALIDAÇÃO PENDENTE]` no cabeçalho do `process-map-as-is.md` (EARS-I4). Mapa não pode ser tratado como verdade.
- **Persona 4 (subagente automatizado):** sem stakeholder → abrir bloco `## [BLOQUEADOR: validação humana pendente]` no `gap-analysis.md` listando perguntas que precisam de resposta humana E encerrar pipeline com **exit-code não-zero** (EARS-I5).

## Handoff para architect
Discovery NÃO desenha to-be. Entrega `gap-analysis.md` com seção MUST `## Itens para architect` listando as perguntas de design — architect produz to-be via ADR(s) de processo. Compliance fica com `high-stakes-gate`.
