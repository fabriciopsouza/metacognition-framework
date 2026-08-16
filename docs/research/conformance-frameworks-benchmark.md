# Benchmark — Frameworks de referência para conformance de processo agêntico

> **Objetivo (pedido do dono):** "analisar um framework e entender como o processo flui e
> respeita o fluxo desenhado para skills, papéis, controles, pausas, templates, ferramentas" —
> usando frameworks **comprovados** como régua. Critério de "comprovado" = adoção/maturidade +
> evidência empírica + **conformance explícito** (mecanismo que garante o fluxo).
>
> **Data:** 2026-06-23 · **Tipo:** pesquisa (não-decisão; alimenta ADR-097) · **Autor:** squad (discovery+pesquisa, opus) ·
> verificação adversarial: qa-critic heterogêneo (sobre o ADR-097, não sobre esta pesquisa).
> **Convenção de confiança:** CONFIRMADO (fonte citada) · INFERIDO (deduzido) · DESCONHECIDO.

---

## 0. File-first — o que já existia no repo (anti-reinvenção, ADR-072)

- `docs/research/BMAD-ecossistema-analise-com-fontes.md` — BMAD força etapas **por convenção**
  (template/workflow + persona instruída a parar); o nosso framework move a confiança do modelo
  para **hooks determinísticos no harness**. Cobertura forte de elicitação analítica; fraca de
  ideação criativa (CIS não importado). Débito declarado.
- `docs/research/OpenMetadata-analise-contribuicoes-processo-com-fontes.md` — **nada a importar**;
  addendum 2026-06-22 reabriu **um** gap: falta **proveniência por-turno** (gates são de
  marco/junção, não de turno). Este benchmark ataca exatamente esse gap.

**Implicação:** o eixo onde nos diferenciamos (conformance HARD via mecanismo executável) é o
eixo (C) abaixo — e é onde quase todo o mercado é ADVISORY.

---

## 1. Distinção que muda a leitura

A pergunta "o fluxo é respeitado?" tem DUAS respostas de famílias distintas:

1. **Frameworks de orquestração** (régua do *desenho* de papéis/gates/pausas) — Família 1.
2. **Conformance checking / process mining** (a disciplina que de fato *mede* "executado × desenhado") — Família 2.

Eixo decisivo da Família 1: **HARD** (o runtime impõe) vs **ADVISORY** (convenção/prompt).
Stars medem popularidade, **não eficácia**.

---

## 2. Família 1 — Orquestração de agentes-LLM

| Framework | Adoção (★, ~2026-06) | Conformance do fluxo | Nota |
|---|---|---|---|
| **LangGraph** | ~35.6k [CONFIRMADO]; produção citada (Klarna/Uber/JPMorgan) [INFERIDO] | **HARD** — grafo de estados + checkpoint durável + `interrupt()` (pausa/retoma no ponto exato) | Referência de ouro p/ pausa imposta pelo runtime |
| **MS Agent Framework** (SK+AutoGen fundidos; GA 1.0 2026-04-03) | ~11.6k [CONFIRMADO] (repo novo) | **HARD** — workflow graph + checkpoint + HITL + *time-travel* | Governança/audit "enterprise" |
| **OpenAI Agents SDK** | ~27.4k [CONFIRMADO] | **HÍBRIDO** — guardrails fail-fast (HARD) + handoff decidido pelo modelo (ADVISORY) | Modelo de "validação em paralelo" |
| **CrewAI** | ~54.2k [CONFIRMADO]; claims enterprise = vendor [DESCONHECIDO] | **PARCIAL** — `Process.sequential/hierarchical` impõe ordem; papéis são prompt | Impõe topologia, não disciplina |
| **AutoGen** (microsoft) | ~59.2k [CONFIRMADO] mas **maintenance mode** | **ADVISORY** — group chat por prompt | README manda migrar p/ Agent Framework |
| **AG2** (fork comunitário) | ~4.7k [CONFIRMADO] | **ADVISORY** | Cuidado: comparativos citam o nº do AutoGen original |
| **BMAD-METHOD** | ~49.6k [CONFIRMADO], releases mensais | **ADVISORY puro** — papéis/templates por convenção | Parente mais próximo em *forma* |

Fontes: [LangGraph](https://github.com/langchain-ai/langgraph) ·
[CrewAI hierarchical](https://docs.crewai.com/en/learn/hierarchical-process) ·
[AutoGen](https://github.com/microsoft/autogen) · [AG2](https://github.com/ag2ai/ag2) ·
[OpenAI Agents — guardrails](https://openai.github.io/openai-agents-python/guardrails/) /
[handoffs](https://openai.github.io/openai-agents-python/handoffs/) ·
[MS Agent Framework](https://github.com/microsoft/agent-framework) ·
[BMAD](https://github.com/bmad-code-org/BMAD-METHOD)

---

## 3. Família 2 — A disciplina que MEDE conformance (a resposta mais sólida ao "comprovado")

| Camada | Ferramenta comprovada | Papel |
|---|---|---|
| Desenho | **BPMN 2.0** — OMG, **ISO/IEC 19510** (Camunda, jBPM) | lanes = papéis; gateways = decisões/pausas |
| Medição | **Process mining / conformance checking** (van der Aalst; **PM4Py** open-source) | event log × modelo → **fitness, precision** + desvios |
| Pausas | **Stage-Gate** (Cooper, 1988) | ancestral direto das junções J0–J6 (aprovar/refazer/descontinuar) |

- Conformance checking = comparar **event log** (o que aconteceu) com **modelo** desenhado;
  mecanismo "replaying history"; 4 dimensões: **fitness, precision, generalization, simplicity**.
  Campo acadêmico maduro (livro van der Aalst, Springer 2016, ISBN 978-3-662-49850-7; IEEE Task
  Force on Process Mining). [CONFIRMADO]
- **PM4Py** (Python, origem Fraunhofer, publicado em SoftwareX) implementa token-based replay
  (rápido), alignments (preciso, diz *onde* divergiu) e footprints. [CONFIRMADO]

Fontes: [IBM BPMN](https://www.ibm.com/think/topics/bpmn) ·
[Camunda BPMN ref](https://camunda.com/bpmn/reference/) ·
[van der Aalst — Process Mining (Springer 2016)](https://link.springer.com/book/10.1007/978-3-662-49851-4) ·
[PM4Py (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S2665963823000933) ·
[PM4Py conformance](https://deepwiki.com/process-intelligence-solutions/pm4py/2.3-conformance-checking) ·
[Stage-Gate (Cooper/Asana)](https://asana.com/resources/stage-gate-process)

### Aplicado a agentes-LLM (2024–2026) — área INCIPIENTE
- Fournier, Limonad & David, **"Agentic AI Process Observability"** (arXiv:2505.20127) — process
  discovery sobre trajetórias de agentes; faz o caminho inverso (descobre, não confere). [CONFIRMADO]
- Redis et al., **"Skill Learning Using Process Mining…"** (arXiv:2410.12870) — usa conformance
  checking sobre traces de ação de agente (prova que funciona). [CONFIRMADO]
- Avaliação de trajetória (T-Eval, AgentBoard "Progress Rate", FlowBench) usa métricas próprias,
  não o aparato formal fitness/precision. [CONFIRMADO]
- **DESCONHECIDO:** paper que aplique conformance checking a um pipeline multi-papel
  (pmo→architect→developer→qa) com gates humanos. Seríamos *early adopters* de técnica madura
  em domínio novo — não inventores.

---

## 4. Evidência empírica do MÉTODO (honestidade — eixo B)

**Nenhum** dos seis frameworks tem prova controlada de que seu *método* melhora o resultado.
A literatura controlada 2025–2026 corre **contra** a moda multi-agente:
- arXiv:2604.02460 — single-agent **iguala/supera** multi-agente sob orçamento de tokens igual.
- arXiv:2503.13657 — "Why Do Multi-Agent LLM Systems Fail?" — ganhos mínimos; 14 modos de falha.

O sub-padrão com mais sinal positivo é **crítica/reflexão adversarial** — o que o nosso
`qa-critic` faz. Conclusão: a parte do nosso framework com mais respaldo empírico é o QA
adversarial, não a multiplicidade de papéis em si.

Fontes: [arXiv 2604.02460](https://arxiv.org/abs/2604.02460) ·
[arXiv 2503.13657](https://arxiv.org/html/2503.13657v1)

---

## 5. Diagnóstico do nosso framework contra a régua

Conformance HARD existe — mas **desigual** (mapa file-first, explorer 2026-06-23):

- **HARD real (hook Python / canário CI, à prova de EDR):** compaction-gate, effect-gate T3,
  overwrite-guard, consistency-gate, qa-evidence/posture-gate.
- **ADVISORY / só-prosa (risco de pulo silencioso):** `readiness-gate` (J2→J3),
  `high-stakes-gate`, junções **J0–J3** (PMO adversarial em prosa). Único rastro mecânico = ledger
  `qa_evidence.py --junction`; CI só reprova se o process-critic auditar **no fim do bloco**.

Diferencial vs mercado: LangGraph/MS impõem **topologia de execução** (grafo); nós tentamos impor
**disciplina metacognitiva** (classificar confiança, file-first, QA adversarial) — de forma
agnóstica de domínio, que nenhum dos seis faz. Mas "tentar por prosa" é o que o process mining
tornaria **mensurável**: o ledger de junções já é um event log incipiente.

---

## 6. Recomendação

**Referência primária: LangGraph** (Python = nosso `tools/`; `interrupt()`/checkpoint = tradução
mais limpa das pausas e do grafo J0–J6). **Referência secundária condicional: MS Agent Framework**
(time-travel + governança) **só para trabalho alto-risco/regulado** (high-stakes-gate). Os outros
quatro = contraexemplo (advisory), não referência de implementação.

> Distinção crítica: estes são **referências de PADRÃO**, não runtimes drop-in — o nosso motor é o
> harness do Claude Code (hooks + canários). Copiamos o padrão `interrupt`/state-graph e o
> reimplementamos via ledger+hook+canário.

**Medição objetiva (alinha à régua §0 — reusa o que existe):**
1. Normalizar o ledger (`qa_evidence.py --junction`, ADR-077) em event log XES/CSV
   `(case_id=bloco, activity=J_n.PASS, timestamp, resource=modelo)`.
2. Formalizar o fluxo do squad como modelo BPMN/Petri (hoje em prosa).
3. Rodar PM4Py (token-replay p/ dashboard + alignments p/ diagnóstico).
4. Gate de conformidade fail-closed (análogo ao posture-gate, ADR-074): bloco fecha só se
   fitness ≥ limiar. → vira ADR-097 (advisory→HARD), acionando o `squad_gate` que ADR-094 deixou
   reservado como escalada.

**Limite honesto:** "HARD via hook" não é universal (EDR veta hooks; ADR-047/060) — a camada
EDR-proof é o **canário CI fail-closed**. E conformance clássico assume traces bem-estruturados;
trajetórias de agente são ruidosas → limiares de fitness precisarão de **calibração empírica**,
não chute.
