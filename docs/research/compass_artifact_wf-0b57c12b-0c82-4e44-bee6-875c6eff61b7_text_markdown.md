# Documentação de Referência — Sistemas RAG Multi-Agente em Produção
## Arquitetura, Operação e Governança, com Controle de Custo por Token, Resiliência e Compliance GxP

---

## 1. Sumário Executivo

**O que é.** Um sistema RAG (Retrieval-Augmented Generation) multi-agente em produção é uma arquitetura composta por seis camadas independentes e versionáveis: (i) pipeline de ingestão → parsing → chunking → embedding → indexação; (ii) retrieval híbrido (denso + esparso) com re-ranking; (iii) orquestrador de agentes especializados (roteador, supervisor, workers, críticos, ferramentas); (iv) gateway de LLM (roteamento, fallback, cache, quotas, telemetria); (v) observabilidade e avaliação contínua (faithfulness, relevância, groundedness, drift); (vi) segurança e governança (PII, prompt injection, RBAC, audit trail, change control).

**Por que importa em seus dois contextos.**
- **Distribuição de combustíveis (alto volume operacional; dados em SAP HANA/BW e SharePoint):** o custo por token, a latência e a robustez a picos de tráfego dominam o ROI. O retorno vem de cascading de modelos, cache semântico, hybrid search e isolamento por unidade de negócio.
- **Farma regulado (GAMP 5, ANVISA RDC 658/2022, ITIL 4, COBIT):** o gargalo é a governabilidade do ciclo de vida do modelo — validação, controle de mudanças, rastreabilidade ALCOA+. O ISPE GAMP Guide: Artificial Intelligence (julho de 2025) e o draft EU GMP Annex 22 (publicado para consulta pelo DG SANTE da Comissão Europeia em 7 de julho de 2025) introduzem requisitos formais que, no caso do Annex 22, **proíbem explicitamente o uso de Generative AI e LLMs em aplicações GMP críticas**.

**Decisões-chave (Bottom Line Up Front).**
1. **Arquitetura única, dois perfis de execução.** A mesma stack lógica (gateway + orquestrador + retrieval + observabilidade) atende ambos, com perfis de risco distintos. O perfil "operacional" pode usar LLMs como geradores; o perfil "GxP crítico" reduz o LLM a tarefas não-críticas com **human-in-the-loop obrigatório** ou prefere RAG extrativo (chunk verbatim) sobre geração livre.
2. **Gateway como ponto único de controle.** LiteLLM (auto-hospedado, MIT) é o default open-source; **Portkey, que foi totalmente disponibilizado em código aberto em 24 de março de 2026 (per release na GlobeNewswire: "Everything that previously required a separate SaaS subscription — governance, observability, authentication, cost controls — is now open source"; processa hoje 1 trilhão+ de tokens e 120M+ requisições/dia em 24.000+ organizações)**, é a escolha para perfis com PII e auditoria pesada. Cloudflare AI Gateway é alternativa managed-edge.
3. **Orquestração: LangGraph (v1.0 fim de 2025) como padrão de produção crítica; CrewAI para iteração rápida.** **Em outubro de 2025 a Microsoft anunciou (per VentureBeat) que "AutoGen and Semantic Kernel will remain in maintenance mode, which means they will not receive new feature investments but will continue to receive bug fixes, security patches and stability updates"; o Microsoft Agent Framework entrou em public preview em 1 de outubro de 2025 e o guia de migração foi publicado em fevereiro de 2026 (Microsoft Learn).** Planeje migração se o stack atual depende de AutoGen.
4. **Vetor + reranker: pgvector ou Qdrant + Cohere Rerank ou BGE-reranker-v2-m3.** Para farma regulado, prefira self-hosted (Qdrant ou pgvector) por residência de dados e auditabilidade; para o operacional de combustíveis, pgvector reaproveita expertise SQL/RBAC.
5. **Avaliação multi-camada obrigatória.** Ragas para iteração de desenvolvimento, DeepEval como CI gate, Langfuse ou Arize Phoenix para tracing/monitoramento online. Em GxP, a evidência de avaliação é artefato de validação (CSV).
6. **Compliance é restrição de design, não verniz.** O não-determinismo de LLMs colide com o requisito GMP de outputs determinísticos (Annex 22 draft, §1). Trate como restrição: ou (a) decisões críticas continuam humanas com IA como suporte (HITL), ou (b) use modelos determinísticos não-generativos (classificadores, embeddings) para a decisão e LLMs apenas para apresentação textual.

---

## 2. Glossário Essencial

- **Agente:** entidade autônoma com ciclo perceber-decidir-agir, ferramentas (function calling) e memória.
- **ALCOA+:** integridade de dados regulada: Attributable, Legible, Contemporaneous, Original, Accurate + Complete, Consistent, Enduring, Available.
- **Chunking:** segmentação de documentos em unidades indexáveis (fixed-size, recursive, semantic, late chunking, agentic).
- **Circuit breaker:** padrão de resiliência que isola dependência falhante após N falhas (Fowler / Nygard, "Release It!").
- **Context of Use (COU):** termo do FDA — papel e escopo específico do modelo na decisão regulatória.
- **CSV (Computer System Validation):** demonstração documentada de que um sistema computadorizado atende ao uso pretendido (RDC 658/2022, GAMP 5).
- **Embedding:** vetor numérico denso representando semântica.
- **Faithfulness (= groundedness em TruLens):** mede se cada afirmação da resposta é suportada pelo contexto recuperado.
- **GAMP 5 (Second Edition, julho de 2022):** Good Automated Manufacturing Practice da ISPE; risk-based CSV; inclui Appendix D11 sobre AI/ML.
- **GraphRAG:** padrão que constrói grafo de entidades/relações sobre o corpus para responder consultas globais.
- **HITL (Human-in-the-Loop):** revisão humana obrigatória antes que output gere efeito regulado.
- **Hybrid search:** combinação de busca densa + esparsa (BM25/SPLADE) com fusão (RRF).
- **MTEB:** Massive Text Embedding Benchmark — referência pública para embedding models.
- **PCCP (Predetermined Change Control Plan):** plano pré-aprovado de mudanças em modelo adaptativo (medical devices; FDA).
- **Re-ranking:** reordenação dos top-k com cross-encoder.
- **RBAC:** Role-Based Access Control.
- **Tenant isolation:** isolamento lógico/físico de dados entre clientes/unidades.
- **Token:** unidade de cobrança de LLM (≈4 caracteres em inglês; ≈3 em PT-BR).

---

## 3. Tópico 1 — Fundamentos de RAG em Produção

### 3.1 Arquitetura e maturidade
Pipelines RAG ingênuos (embed → retrieve → prompt) têm taxas de sucesso de 10–40% em ambientes corporativos (Applied AI, 2025; kapa.ai). Produção real exige hybrid search + reranking + query transformation.

### 3.2 Estratégias de chunking

| Estratégia | Quando usar | Custo | Maturidade |
|---|---|---|---|
| Fixed-size + overlap (400–512 tokens, 10–20% overlap) | Default barato | $ | [CONSOLIDADO] |
| Recursive character | Texto sem estrutura clara | $ | [CONSOLIDADO] |
| Document- / page-based | PDFs paginados, POPs, normas (vencedor do benchmark NVIDIA 2024 com 0.648 de acurácia) | $ | [CONSOLIDADO] |
| Semantic chunking | Narrativas longas; ganho até 9% recall vs simples | $$ | [EMERGENTE] |
| Late chunking (Jina, arXiv:2409.04701, 2024) | Documentos com coreferências longas | $$ | [EMERGENTE] |
| Agentic chunking (LLM-based) | Documentos heterogêneos de alto valor | $$$ | [EM DISPUTA] (ganho marginal vs custo) |

**Recomendação:** combustíveis → recursive 400–512 tokens + page-based; farma → page-based com metadata explícita (SOP ID, versão, data efetiva).

### 3.3 Embedding models — comparativo

| Modelo | Tipo | Dim | MTEB (aprox.) | Preço | Observação |
|---|---|---|---|---|---|
| OpenAI text-embedding-3-large | API | 3072 (Matryoshka) | ~64.6 | $0.13/1M tok | Default seguro |
| OpenAI text-embedding-3-small | API | 1536 | ~62.3 | $0.02/1M tok | Sweet spot custo/qualidade |
| Cohere embed-v3 / v4 | API | 1024 | ~65.2 | $$ | Líder multilíngue (PT-BR); par natural com Cohere Rerank |
| Voyage voyage-3-large | API | 1024 | Top retrieval | $$$ | Domínios específicos (legal, médico, código) |
| BGE-M3 (BAAI) | Open-source | 1024 | ~63 | Self-host | Dense+sparse+multi-vector; 100+ idiomas; Apache 2.0 |
| Nomic Embed v2 | Open-source | 768 | Competitivo | Self-host | Multilíngue, leve |
| NV-Embed-v2 | Open-source | 4096 | Topo MTEB | Self-host (GPU) | Pesado, líder em benchmarks |

**Regra de break-even self-host vs API:** abaixo de 10–15M embeddings/mês a API é mais barata; acima, BGE-M3 / Nomic em GPU própria.

### 3.4 Vector databases — comparativo

| Banco | Modelo | Hybrid nativo | Self-host | Notas |
|---|---|---|---|---|
| **Pinecone** | Managed | Sparse-dense proprietário | Não | Mais simples; SLA enterprise; sem on-prem |
| **Weaviate** | OSS + Cloud | BM25F (BlockMax WAND GA 2025) | Sim | Melhor hybrid; >100M vetores requer planejamento |
| **Qdrant** | OSS + Cloud | Sim (sparse + dense, v1.9+; IDF server-side v1.15.2+) | Sim | Rust, eficiente, free 1GB; ACORN filtered HNSW |
| **Milvus / Zilliz** | OSS + Cloud | Sparse-BM25 nativo (v2.5+) | Sim | Escala bilhões; complexidade operacional (Kafka, MinIO, etcd) |
| **pgvector** | Extensão Postgres | Combinação com tsvector | Sim | Reutiliza RBAC/backup do Postgres; bom até ~50M vetores |
| **OpenSearch / Elasticsearch** | OSS + Cloud | Sim (kNN + BM25; OpenSearch 3.0 ~9.5x mais rápido) | Sim | Reaproveita stack de busca corporativa |
| **Chroma** | OSS | Limitado | Sim | Prototipagem, não produção crítica |

**Recomendação:** combustíveis → pgvector (se já houver Postgres) ou Qdrant self-hosted; farma → Qdrant on-prem ou pgvector on-prem (open-source auditável, versionamento determinístico de índice, residência de dados).

### 3.5 Re-ranking — comparativo

| Reranker | Tipo | Latência | Qualidade | Custo |
|---|---|---|---|---|
| Cohere Rerank 3.5 / v4 Pro | API | ~600 ms p50 | ELO ~1629 | API pago |
| BGE-reranker-v2-m3 | OSS (Apache 2.0) | 50–100 ms GPU; 350 ms CPU | Próximo ao topo | Self-host |
| Jina Reranker v2 multilingual | OSS/API | ~110 ms | Bom multilíngue | Misto |
| Voyage Rerank 2.5 | API | ~595 ms | Top | API pago |
| Zerank 2 (ZeroEntropy) | API | — | ELO ~1638 (líder) | ~40x mais barato que Cohere |
| MiniLM-L-6 msmarco | OSS | ~55 ms | Baseline | Trivial |

**Recomendação:** combustíveis → BGE-reranker-v2-m3 em GPU ou Cohere Rerank Nimble se latência é crítica; farma → BGE-reranker-v2-m3 self-hosted (determinismo de output alinhado ao Annex 22).

### 3.6 Padrões avançados
- **Hybrid Search (denso + esparso + RRF):** [CONSOLIDADO]. Obrigatório em domínios com jargão/códigos.
- **Query rewriting / HyDE / multi-query:** [CONSOLIDADO]. Reduz mismatch query-documento.
- **GraphRAG (Microsoft, jun/2024) e LazyGraphRAG (nov/2024):** [EMERGENTE]. **Per BenchmarkQED da Microsoft Research (blog de 17 de junho de 2025): "LazyGraphRAG outperformed every comparison condition using the same generative model (GPT-4o), winning all 96 comparisons, with all but one reaching statistical significance"** — superando GraphRAG Local/Global/Drift, Vector RAG 8k e 120k, LightRAG, RAPTOR e TREX, com custo de indexação de 0.1% do GraphRAG completo. Indicado para queries globais ("temas principais"); vector RAG continua melhor para queries locais.
- **Agentic RAG:** [EMERGENTE]. Padrão de retry/refine; risco de loops e custo descontrolado.

---

## 4. Tópico 2 — Orquestração Multi-Agente

### 4.1 Padrões fundamentais

| Padrão | Quando usar | Trade-off |
|---|---|---|
| **Router** | Pedidos heterogêneos com handler claro | Não combina especialistas; misclassificação |
| **Supervisor / Orchestrator-Worker** | Tarefa decomponível, controle central | Supervisor é SPOF; latência soma; plano alucinado |
| **Pipeline / Sequential** | ETL-like, etapas determinísticas | Pouca flexibilidade |
| **Hierárquico** | >50 agentes, múltiplos domínios | Única opção viável em escala enterprise (IBM, Atlan 2026); debug complexo |
| **Group Chat / Conversational** | Brainstorm, debate, revisão | Tokens explodem; difícil terminar |
| **Critic-Refiner (Maker-Checker)** | Tarefas com critério verificável | Aumenta custo; exige stopping criteria |

### 4.2 Frameworks — comparativo concreto

| Framework | Modelo mental | Pontos fortes | Pontos fracos | Maturidade |
|---|---|---|---|---|
| **LangGraph (LangChain)** | Grafo direcionado tipado; v1.0 fim de 2025 | Durable execution; checkpoint/replay; HITL nativo; LangSmith tracing; Python+JS; ~47M downloads/mês | Curva; verboso | [CONSOLIDADO] |
| **CrewAI** | Crews (papéis) + Flows (event-driven, 2025) | ~35 LOC para MVP; intuitivo; YAML | Logging fraco; debug difícil em loops; ~5.2M downloads | [CONSOLIDADO] para protótipo; [EMERGENTE] em produção |
| **AutoGen → Microsoft Agent Framework** | Conversação entre agentes | Padrões de diálogo; .NET; AutoGen Studio | **Em maintenance mode desde outubro de 2025** (Microsoft, per VentureBeat, anunciou que AutoGen e Semantic Kernel "will not receive new feature investments but will continue to receive bug fixes, security patches and stability updates"). **Microsoft Agent Framework lançou public preview em 1 de outubro de 2025; migration guide publicado em fevereiro de 2026 (Microsoft Learn).** | [EM DISPUTA] |
| **OpenAI Agents SDK** | Agents + Handoffs + Guardrails | Simples; tracing nativo; integração OpenAI | Lock-in OpenAI | [EMERGENTE] |
| **Semantic Kernel (Microsoft)** | Skills + Planners | .NET first-class | Maintenance mode (out/2025) | [EM DISPUTA] |
| **Google ADK / Vertex Agent Builder** | Managed agentic | Integração GCP/Gemini | Ecossistema novo | [EMERGENTE] |
| **LlamaIndex Workflows** | Eventos + agentes | Forte em retrieval | Misturado com RAG | [CONSOLIDADO em RAG] |
| **OpenAgents** | Mesh com MCP + A2A | Interop entre frameworks | Comunidade pequena | [EMERGENTE] |

**Recomendação:**
- **Combustíveis:** LangGraph + LangSmith para produção; CrewAI para PoCs.
- **Farma regulado:** LangGraph com checkpointer Postgres (estado serializado é evidência de audit trail); evite frameworks em manutenção ou com lock-in proprietário.

### 4.3 Estado, memória, ferramentas
- **Short-term:** typed dict (LangGraph) ou histórico de chat (AutoGen).
- **Long-term:** Postgres/Redis para sessões; vector store para "experiences".
- **Interop:** Model Context Protocol (MCP, Anthropic, 2024) para tools; Agent2Agent (A2A, Linux Foundation, 2025) para comunicação cross-framework.

---

## 5. Tópico 3 — Controle de Custo por Token

### 5.1 Medição e atribuição
- Tagging em cada chamada: usuário, tenant, agente, prompt-template, modelo, versão.
- OpenTelemetry com `gen_ai.usage.input_tokens` / `output_tokens` (convenções semânticas em incubação 2024–25).
- Dashboards por intent, tenant, agente; alerta em desvio (>2σ).

### 5.2 Model cascading / routing (FrugalGPT)
**FrugalGPT (Chen, Zaharia, Zou — Stanford, arXiv:2305.05176):** três técnicas — prompt adaptation, LLM approximation, LLM cascade. Autores reportam **redução de até 98% de custo mantendo a acurácia de GPT-4** em datasets selecionados.

**Em 2025–26**, gateways gerenciam (LiteLLM `Router`, Portkey `Config`, OpenRouter `auto`); pesquisa em routers: **RouteLLM (LMSYS / UC Berkeley, 2024), per tianpan.co citando o paper: o "matrix factorization router achieved 95% of GPT-4 performance using only 26% GPT-4 calls" — encaminhando ~74% das queries para modelos mais baratos enquanto mantém 95% da qualidade do modelo de fronteira.** Outras opções: Martian, NotDiamond, openrouter/auto.

### 5.3 Caching
| Tipo | Hit típico | Quando | Cuidados |
|---|---|---|---|
| Embedding cache | Alto | Re-embeddings de docs imutáveis | Invalidação por hash |
| Exact prompt cache | Médio | FAQs internos | Trivial |
| Semantic cache (GPTCache, Redis Vector, Azure APIM) | Alto em chatbots | Queries semelhantes | Risco de hit falso; threshold 0.85–0.95 |
| Prompt caching nativo (Anthropic 2024, OpenAI 2024) | Alto | Prompts com prefixo estável | Configuração por provedor |

**Evidência:** GPT Semantic Cache (Regmi & Pun, arXiv:2411.05276) reporta **redução de ~68.8% de chamadas API com positive hit rate >97%**. GPTCache (Bang, ACL NLP-OSS 2023) é a referência open-source. SAFE-CACHE (2025) mostra que semantic cache é vulnerável a exploração adversarial (taxa de ataque cai de 52.77% para 14.27% com defesas).

### 5.4 Compressão de contexto
- **LLMLingua / LLMLingua-2 (Microsoft, 2023–24):** compressão preservando informação relevante.
- Sumarização hierárquica de longos históricos.

### 5.5 Gateways de LLM — comparativo concreto

| Gateway | Modelo | Fallback | Cache | Guardrails | Auditoria | Recomendado para |
|---|---|---|---|---|---|---|
| **LiteLLM** | OSS (MIT), self-host; ~33k stars; ~10–20ms overhead | Sim | Via Redis | Básico | Logs (instrumentar) | Default OSS auto-hospedado |
| **Portkey** | **Totalmente OSS desde 24 de março de 2026** (GlobeNewswire) | Latency/cost-based | Exact + semantic | PII redaction, jailbreak detection | RBAC, audit trails, workspaces, data residency, SSO/SCIM | Produção enterprise; GxP |
| **Cloudflare AI Gateway** | Managed (edge) | Sim | Sim | Básico | Analytics | Apps já em Cloudflare |
| **Helicone** | OSS + SaaS | Sim | Sim | Limitado | Logs detalhados | Observability-first |
| **OpenRouter** | SaaS marketplace, 290+ modelos, markup 5–15% | Sim (auto) | Sim | Não | Limitado | Acesso multi-modelo zero-setup |
| **Vercel AI Gateway** | Managed | Sim | Sim | Limitado | Limitado | Apps Vercel/Next.js |
| **Bifrost (Maxim)** | OSS, Rust, ~11µs overhead a 5k RPS | Sim | Sim | Médio | OpenTelemetry, VPC | Alta performance |
| **TrueFoundry AI Gateway** | Plataforma MLOps | Sim | Sim | RBAC | Sim | MLOps + gateway |
| **Kong AI Gateway** | Plugins sobre Kong | Básico | Básico | Genérico | Sim | Já usa Kong |
| **AWS Bedrock + AgentCore / Azure APIM / Google Apigee** | Managed cloud | Sim | Variável (Azure APIM tem semantic cache via Redis) | Variável | Sim | Stack mono-cloud |

**Recomendação:**
- **Combustíveis:** LiteLLM self-hosted + Redis (controle total, custo zero de licença) ou Portkey self-hosted se PII/guardrails forem prioridade.
- **Farma regulado:** **Portkey self-hosted em VPC privada** (totalmente OSS desde mar/2026) ou Bifrost. Justificativa: PII redaction, jailbreak detection, audit trails, RBAC e data residency são essenciais para CSV e Annex 11. Não use OpenRouter ou Cloudflare AI Gateway managed para dados de pacientes (LGPD/GDPR).

### 5.6 Quotas e orçamento
- Hard limits por chave/usuário/tenant no gateway.
- Soft budget com alerta em 70%/90%.
- Kill switch automático em runaway loops (limite de iterações, deadlock detector).

---

## 6. Tópico 4 — Resiliência e Fallback

### 6.1 Detecção de falha
- HTTP 429 (rate limit), 5xx, timeout configurável (latência p95+25%).
- Falha semântica: refusal, output vazio, hallucination (Patronus Lynx, Vectara HHEM).
- Health checks ativos por provedor.

### 6.2 Retry/backoff
- Exponential backoff com jitter (AWS Architecture).
- Idempotency keys (padrão Stripe) para evitar duplicatas com side effects.
- Limite máximo de retries (3 típico).

### 6.3 Circuit breaker
- Padrão Fowler/Nygard ("Release It!"): closed → open (após N falhas) → half-open (probe).
- Implementações: `pybreaker`, `resilience4j`, embutido em LiteLLM/Portkey/Bifrost.

### 6.4 Cadeias multi-provedor
- **Padrão:** OpenAI → Azure OpenAI (mesmo modelo, região distinta) → Anthropic → modelo local (Llama, Mistral via vLLM/Ollama).
- Gateways gerenciam: LiteLLM `fallback_models`, Portkey `fallback config`, OpenRouter `auto`.
- **Em farma:** rotação automática para provedor não-aprovado é violação. DPA/BAA + lista branca obrigatórios.

### 6.5 Graceful degradation
- Resposta extrativa (top chunk verbatim) em vez de gerada quando geração falha.
- Cached stale response.
- Mensagem honesta "informação indisponível, ticket gerado" — **obrigatória em GxP**.

### 6.6 Idempotência e filas
- Filas: RabbitMQ, Kafka, SQS para ingestão e tarefas longas.
- Workflows duráveis: Temporal, AWS Step Functions, LangGraph com checkpointer Postgres.
- Dead-letter queue para reprocessamento manual.

---

## 7. Tópico 5 — Avaliação e Observabilidade

### 7.1 Métricas RAG (RAG Triad — TruLens; Ragas; DeepEval)
- **Context Relevance / Context Precision:** quão relevantes são os chunks.
- **Context Recall:** quantos documentos relevantes foram recuperados.
- **Faithfulness (= groundedness em TruLens):** cada claim suportado pelo contexto.
- **Answer Relevance:** resposta endereça a pergunta.
- **Answer Correctness:** com ground truth labeled.

Es et al. (2023), arXiv:2309.15217: "Faithfulness refers to the idea that the answer should be grounded in the given context."

### 7.2 Frameworks — comparativo

| Framework | Foco | Pontos fortes | Limitações |
|---|---|---|---|
| **Ragas** | RAG-específico | 4 métricas reference-free; rápido; OSS | Limitado a RAG |
| **DeepEval (Confident AI)** | Geral (50+ metrics) | Pytest-style; CI/CD; red-teaming via DeepTeam. **Fundada por Jeffrey Ip (ex-Google, escalou infraestrutura do YouTube creator studio; ex-Microsoft Office 365) e Kritin Vongthongsri (Princeton ORFE'24 + CS, pesquisador AI publicado em CHI), per página da Y Combinator: "Confident AI is founded by Jeffrey Ip, a SWE formally at Google scaling YouTube's creators studio infrastructure... and Kritin Vongthongsri... who researched self-driving cars/HCI during his time at Princeton."** | Alto consumo de tokens (LLM-as-judge) |
| **TruLens (Snowflake)** | Trace + eval inline; Snowflake adquiriu TruEra em maio de 2024; 3.000+ GitHub stars | Feedback functions em produção; sampling em traffic real | Setup pesado; acoplado a runtime |
| **Arize Phoenix** | Observability OSS | Tracing OTel-native | Eval embutida limitada |
| **Langfuse** | LLMOps end-to-end | Tracing + prompt mgmt + datasets; self-host fácil | Eval superficial |
| **LangSmith** | LangChain native | Trace + experimentos | Pago; lock-in LangChain |
| **Helicone** | Observability + gateway | Logs + caching | Eval básica |
| **MLflow LLM Evaluate** | MLOps unificado | Integra MLflow tracking | Menos profundo em RAG |
| **W&B Weave** | Experiment tracking | Forte em ranking benchmark adversarial | R&D focus |
| **Patronus / Vectara HHEM** | Hallucination | Especializados | Não substitui suite |
| **Giskard / RAGChecker** | Robustez/red-teaming | Fairness, adversarial | Curva |

**Benchmark independente (AIMultiple, 2025, GPT-4o como juiz, 1460 questões, 14600 contextos):** W&B, TruLens e Ragas empatam estatisticamente no top-1 (94–98%). **Nenhuma ferramenta distingue de forma confiável contexto factualmente errado mas topicamente relevante (hard negative) de contexto correto.** Limitação fundamental do LLM-as-judge sobre relevância versus correção factual.

**Receita prática:**
- Ragas para iteração rápida em dev.
- DeepEval como CI gate (bloqueia merge em regressão).
- TruLens ou Langfuse para sampling online em produção.

### 7.3 Avaliação offline vs online
- **Offline:** golden dataset (50–200 Q&A curados); CI; refresh trimestral.
- **Online:** sampling 1–5% via LLM-as-judge; user feedback; regressão por changepoint detection (PELT, BOCPD).
- **Drift:** monitorar distribuição de queries (embedding space), distribuição de scores de relevance, taxa de refusals.

### 7.4 Tracing
- OpenTelemetry com semantic conventions para GenAI (em incubação 2024–25).
- Span por etapa: query → embed → search → rerank → prompt → LLM → parse.
- Correlation ID end-to-end.

### 7.5 Cuidados com LLM-as-judge
- **Bias do mesmo provedor:** juiz GPT-4 sobre output GPT-4 é leniente. Use modelo diferente como juiz (cross-provider judging).
- **Sensibilidade a prompt:** alta variância; use dual-judge (Ragas) ou rubric calibrado.
- **Golden set drift:** revisar trimestralmente.

---

## 8. Tópico 6 — Segurança e Privacidade

### 8.1 PII e LGPD/GDPR
- **Detecção:** Microsoft Presidio, AWS Comprehend PII, GCP DLP, Portkey PII Redaction.
- **Estratégias:** mascaramento pré-prompt, tokenização reversível, pseudonimização com mapping em vault.
- **LGPD (Lei 13.709/2018):** base legal (consentimento, legítimo interesse); minimização; retenção; DPO informado.
- **Locais de processamento:** documentar fluxo; DPA/BAA com provedores; preferir regiões com adequação.

### 8.2 Prompt injection via conteúdo recuperado (OWASP LLM01:2025)
**Categoria #1 do OWASP Top 10 for LLM Applications.** RAG é particularmente vulnerável porque o retrieval, por design, insere conteúdo externo no contexto. Pesquisa (Ramakrishnan & Balaji, arXiv:2511.15759, 2025): apenas **5 documentos cuidadosamente construídos manipulam respostas em 90% dos casos** via RAG poisoning; sua framework combinada reduz successful attack rate de 73.2% para 8.7% mantendo 94.3% do baseline performance.

**Defesa em camadas:**
1. **Sanitização de fontes:** classificadores de "promptlike" (Llama Guard, NeMo Guardrails, Azure Prompt Shield, Lakera).
2. **Delimitadores + instruction hierarchy:** OpenAI (2024) "Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions" — reduz, não elimina.
3. **Privilege separation:** o agente que lê documento não-confiável **não pode** chamar tools com efeito (Simon Willison's "dual LLM").
4. **Human-in-the-loop** para qualquer ação irreversível.
5. **Sandboxing de tool calls:** whitelist; validação de parâmetros.
6. **Output filtering:** classificador antes de devolver ao usuário.

**Aviso franco:** prompt injection **não tem solução fechada** em 2026; é vulnerabilidade arquitetural; aceite e mitigue (defense in depth), não pretenda eliminar.

### 8.3 Controle de acesso a documentos
- **Tenant isolation físico:** namespaces por tenant; coleções separadas; coleção única com filtros é anti-padrão em regulado.
- **Document-level ACL:** metadata `acl_groups: [...]`; filtro obrigatório no retrieval; PostgreSQL Row-Level Security (RLS) com pgvector é o padrão mais auditável.
- **Embedding leakage:** Morris et al. (2023) — ataques de inversão; evite armazenar PII como `text` do chunk.
- **Vector poisoning:** valide ingestão; assine fonte; quarentene fontes externas.

### 8.4 Multi-tenant isolation
- **Físico:** infra separada (caro, mais seguro).
- **Lógico:** namespace + tags + RLS; chave de criptografia por tenant (BYOK).
- **Auditoria por tenant:** logs separados; access reviews trimestrais.

---

## 9. Tópico 7 — Governança e Compliance (Foco em Farma Regulado)

### 9.1 Cenário regulatório atualizado (fontes primárias)

#### ISPE GAMP 5 (Second Edition, julho de 2022)
Inclui **Appendix D11 dedicado a AI/ML**; abordagem risk-based para CSV.

#### ISPE GAMP Guide: Artificial Intelligence — julho de 2025
- ~290 páginas (ispe.org/publications/guidance-documents/gamp-guide-artificial-intelligence).
- Co-leads: **Brandi M. Stockton** (Triality Group), **Eric Staib** (Syneos Health), **Martin Heitmann** (Triality Group); sponsored by ISPE GAMP CoP Software Automation & AI SIG + ISPE AI CoP.
- Cobre rule-based ML → traditional ML → generative AI sob framework risk-based de ciclo de vida.
- Não proíbe generative AI; trata via mitigação e monitoramento.
- Alinha-se a **ISO/IEC 42001:2023** (AI Management System).
- Aborda: knowledge management, AI literacy, trustworthy AI, explainable AI, dynamic systems (estendendo Appendix D11 de GAMP 5 SE).
- Status: [CONSOLIDADO] como referência industrial; **não vinculante** mas é a interpretação que inspectorias esperam.

#### EU GMP Annex 22 — Artificial Intelligence (DRAFT)
- Publicado para consulta pela **European Commission DG SANTE em 7 de julho de 2025**; consulta encerrou em **7 de outubro de 2025** (health.ec.europa.eu/consultations/stakeholders-consultation-eudralex-volume-4-good-manufacturing-practice-guidelines-chapter-4-annex_en).
- Elaborado pelo **EMA GMDP-Inspectors Working Group em cooperação com PIC/S**.
- **Escopo (verbatim):** "This annex applies to all types of computerised systems used in the manufacturing of medicinal products and active substances, where Artificial Intelligence models are used in **critical applications with direct impact on patient safety, product quality or data integrity**, e.g. to predict or classify data."
- **Modelos estáticos vs dinâmicos (verbatim):** "The document applies to **static models, i.e. models that do not adapt their performance during use** by incorporating new data. The use of **dynamic models which continuously and automatically learn and adapt performance during use, is not covered by this document, and should not be used in critical GMP applications**."
- **Determinismo (verbatim):** "The document applies to models with a **deterministic output** […]. **Models with a probabilistic output** which, when given identical inputs, might not provide identical outputs are not covered by this document and **should not be used in critical GMP applications**."
- **Generative AI / LLM (verbatim):** "Following the above, **the document does not apply to Generative AI and Large Language Models (LLM), and such models should not be used in critical GMP applications**. If used in non-critical GMP applications, which do not have direct impact on patient safety, product quality or data integrity, personnel with adequate qualification and training should always be responsible for ensuring that the outputs from such models are suitable for the intended use, i.e. a **human-in-the-loop (HITL)**."
- Estrutura: 10 seções (Scope; Principles; Intended Use; Acceptance Criteria; Test Data; Test Data Independency; Test Execution; Explainability; Confidence; Operation; Glossary).
- **Status maio/2026:** ainda draft; timeline final não confirmado pela EC (comentários industriais sugerem final em 2026, enforcement 2027–28 — **não confirmado em fonte primária**).
- Status conceptual: [EMERGENTE]; impacto direto se finalizado conforme escrito.

#### FDA Draft Guidance — "Considerations for the Use of AI to Support Regulatory Decision-Making for Drug and Biological Products"
- **Disponibilizada em 6 de janeiro de 2025**; Federal Register Notice de Availability em **7 de janeiro de 2025** (Docket FDA-2024-D-4689). Período de comentários encerrou **7 de abril de 2025**.
- **Status maio/2026: ainda DRAFT**; versão final não publicada.
- **Framework de credibilidade em 7 passos** (verbatim das fontes regulatórias):
  1. **Define the question of interest** to be addressed by the AI model.
  2. **Define the context of use (COU)** for the AI model.
  3. **Assess the AI model risk** (model influence × decision consequence).
  4. **Develop a plan to establish the credibility** of the AI model output within the COU.
  5. **Execute the plan.**
  6. **Document the results** of the credibility assessment plan and discuss deviations.
  7. **Determine the adequacy** of the AI model for the COU.
- Escopo: nonclinical, clinical, post-marketing, manufacturing-quality; exclui drug discovery e eficiências operacionais sem impacto regulatório.
- Status: [EMERGENTE].

#### Princípios Conjuntos FDA-EMA — "Guiding Principles of Good AI Practice in Drug Development" (14 de janeiro de 2026)
- Publicado conjuntamente pela EMA e FDA em **14 de janeiro de 2026** (ema.europa.eu/en/news/ema-fda-set-common-principles-ai-medicine-development-0; fda.gov/media/189581/download).
- EMA verbatim: "EMA and the U.S. Food and Drug Administration (FDA) have jointly identified **ten principles for good artificial intelligence (AI) practice in the medicines lifecycle**. The principles give broad guidance on AI use in evidence generation and monitoring across all phases of a medicine, from early research and clinical trials to manufacturing and safety monitoring."
- **Não-vinculante** (McGuireWoods, jan/2026: "While not formal industry guidance, the document provides important insights into FDA and EMA thinking […] and signals future regulatory guidance from both regulators").
- Construído sobre EMA Reflection Paper (set/2024) e bilateral FDA-EU (abril 2024).
- Status: [EMERGENTE].

#### GMLP Trilateral FDA + Health Canada + UK MHRA
- **10 Guiding Principles for GMLP** — outubro de 2021.
- **PCCP Guiding Principles** — outubro de 2023; **PCCP final guidance** para medical devices em dezembro de 2024.
- **Transparency for Machine Learning-Enabled Medical Devices: Guiding Principles** — 13 de junho de 2024.
- **IMDRF final adoption** dos 10 GMLP principles — janeiro de 2025.

#### ANVISA — Brasil
- **RDC 658/2022:** publicada em **30 de março de 2022**; vigor em **2 de maio de 2022**; revoga RDC 301/2019; alinha BPF brasileiro ao PIC/S.
- **IN 134/2022** (30 de março de 2022): adota PIC/S para sistemas computadorizados (substitui IN 43/2019). Verbatim Art. 1: "esta Instrução Normativa possui o objetivo de adotar as diretrizes de Boas Práticas de Fabricação relacionadas aos sistemas computadorizados do Esquema de Cooperação em Inspeção Farmacêutica (PIC/S), como requisitos complementares a serem seguidos na fabricação de medicamentos em adição às Diretrizes Gerais de Boas Práticas de Fabricação".
- Indústria brasileira usa **GAMP 5 como metodologia de fato** para satisfazer IN 134.
- **Não há, até maio de 2026, regulação específica da ANVISA sobre AI/ML/GenAI/LLM em GxP de manufatura ou desenvolvimento.** RDC 657/2022 (SaMD) cobre software estático; está em revisão para incorporar ML adaptativo.
- Status: [CONSOLIDADO] para CSV "tradicional"; **vazio regulatório explícito para AI/ML** — expectativa industrial é convergência com EU Annex 22 e ISPE GAMP AI.

#### EU AI Act (Regulation 2024/1689)
Vigor 1 ago 2024. Aplicação faseada: proibições e AI literacy de 2/2/2025; GPAI de 2/8/2025; high-risk (incluindo muitos casos pharma/med-device) de 2/8/2026; aplicação plena para AI embutida em produtos regulados em ago 2027.

### 9.2 Validação de sistemas não-determinísticos sob GAMP 5 / CSV

**O problema fundamental.** GAMP 5 / CSV pressupõem reprodutibilidade — mesmo input gera mesmo output. LLMs violam isso por design (sampling estocástico; atualizações silenciosas do provedor). EU Annex 22 reconhece isso e proíbe LLMs em GMP crítico.

| Estratégia | Determinismo | Defensável em GMP crítico? |
|---|---|---|
| LLM com `temperature=0` + seed + snapshot | Aproximado | **Não** (providers não garantem determinismo bit-exato; Annex 22 §1 proíbe) |
| LLM apenas para apresentação de classificador determinístico | Output determinístico | **Sim**, com HITL |
| RAG extrativo (chunk verbatim, sem geração) | Sim | **Sim**, com validação do retrieval |
| RAG generativo apenas em aplicações não-críticas com HITL | Não | **Permitido** sob Annex 22 |
| Modelos estáticos, determinísticos, não-generativos | Sim | **Sim** |
| Modelo dinâmico/adaptativo em produção | Não | **Não** (Annex 22) |

### 9.3 Rastreabilidade, versionamento e audit trail
**Obrigatórios em CSV de RAG/LLM:**
- Snapshot exato do modelo (ex.: `gpt-4o-2024-08-06`) com hash; prompt template em SCM (Git); embedding model com versão + hash; índice com hash do conjunto.
- Pipeline de ingestão versionado.
- Audit trail por execução: request ID, timestamp, user, tenant, modelo, prompt version, chunks recuperados (IDs), output, latência, tokens, custo — ALCOA+ aplica.
- Change control: PM com avaliação de impacto, retest do golden set, aprovação.
- Re-validação periódica trimestral; drift dispara re-validação.

### 9.4 Risk management
- ICH Q9(R1) — Quality Risk Management; FMEA por agente, por tool, por modelo.
- O framework 7-step da FDA Jan/2025 funciona como template:
  1. Pergunta de interesse → caso de uso.
  2. COU → escopo do agente.
  3. Risco = influência × consequência → categoria GAMP.
  4. Plano de credibilidade → protocolo (IQ/OQ/PQ + métricas RAG).
  5. Execução → testes em golden set + adversarial.
  6. Documentação → relatório de validação.
  7. Adequação → certificação de uso.

### 9.5 O que é incerto ou em disputa
- [EM DISPUTA] **Validação estatística de não-determinismo:** tamanho de amostra (n) e tolerância de variância para output de LLM sem consenso.
- [EM DISPUTA] **Re-qualificação por atualização silenciosa do provedor.** Sem prescrição numérica.
- [EM DISPUTA] **Aceitabilidade de cloud nos EUA sob LGPD** para dados de pacientes brasileiros — practice varia.
- [EM DISPUTA] **Se LangSmith/Langfuse/Phoenix substituem ferramentas tradicionais de validação** — interpretação industrial divergente.
- [EMERGENTE] **Annex 22 final pode flexibilizar ou endurecer** — desfecho incerto.

---

## 10. Frameworks de Decisão ("Se X então Y")

### 10.1 Seleção de modelo
| Se… | Então… |
|---|---|
| Classificação simples (intent, sentimento) | Mistral 7B / Llama 3 8B local ou GPT-4o-mini |
| Raciocínio multi-step com tools | Claude Sonnet 3.7 / GPT-4o / Gemini 2.5 Pro |
| Code generation | Claude Sonnet ou GPT-4o; Voyage embed para código |
| Determinismo (suporte GxP) | Modelo extrativo + LLM somente para parafraseio, ou desligar geração |
| Latência crítica (<500ms) | Haiku / GPT-4o-mini / Gemini Flash + cache agressivo |
| Custo dominante | Cascade Haiku → Sonnet com gate de confiança |
| Dado altamente sensível (PII farma) | Llama 3.3 70B / Mistral Large on-prem via vLLM |

### 10.2 Estratégia de chunking
| Se… | Então… |
|---|---|
| Documentos curtos auto-contidos (FAQ, tickets) | Sem chunking ou document-level |
| PDFs paginados (manuais, POPs) | Page-based + metadata |
| Texto contínuo longo (contrato, narrativa) | Recursive 400–512 tokens + 50 overlap |
| Coreferência longa importa | Late chunking + long-context embedding |
| Domínio com jargão e códigos | Hybrid (dense + BM25) > chunking exótico |
| Documentos heterogêneos alto valor | Agentic chunking (cuidado com custo) |

### 10.3 Política de fallback
| Se… | Então… |
|---|---|
| Provedor primário retorna 429 | Exponential backoff + jitter; após 3 tentativas, secundário |
| Provedor primário retorna 5xx | Imediatamente secundário; circuit breaker open após 5 falhas em 60s |
| Resposta é refusal ou vazia | Reescrever query (HyDE) ou escalar para modelo maior |
| Confidence score < threshold | Cascade upgrade |
| Tudo falha | Extrativa do top-chunk + handoff humano |
| GxP crítico | Sem fallback automático para provedor não-aprovado; falhar com mensagem auditável |

### 10.4 Estratégia de cache
| Se… | Então… |
|---|---|
| Prompts repetidos exatos (FAQ interno) | Exact match cache no gateway |
| Variações semânticas frequentes | Semantic cache threshold 0.85–0.95; monitorar falsos hits |
| Prompt longo com prefixo fixo | Prompt caching nativo (Anthropic, OpenAI) |
| Conteúdo regulado/legal | Desabilitar semantic cache; apenas exact com TTL curto |
| Output muda no tempo (dados operacionais) | TTL curto (minutos) ou desabilitar |

---

## 11. Apêndice A — Aplicação Prática: Distribuição de Combustíveis (Energia/Operacional)

### A.1 Casos de uso prioritários
1. Consulta de normas, padrões operacionais e POPs (regulamentação ANP, manuais de segurança).
2. Suporte à decisão operacional (anomalia volumétrica; conferência SAP HANA × SharePoint).
3. Geração de relatórios e dashboards conversacionais sobre vendas/distribuição.
4. Assistente ITSM (enriquecimento de tickets, sugestão de causa-raiz).

### A.2 Arquitetura recomendada
- **Ingestão:** Airflow ou Azure Data Factory → Unstructured.io ou Azure Document Intelligence (PDFs) → chunking page-based com metadata `{doc_id, version, effective_date, área}`.
- **Embedding:** OpenAI text-embedding-3-small (se já houver contrato Azure OpenAI) ou Cohere embed-v3 multilingual.
- **Vector DB:** pgvector em Azure Database for PostgreSQL Flexible Server.
- **Retrieval:** hybrid (pgvector + tsvector + RRF) → BGE-reranker-v2-m3 em GPU.
- **Orquestração:** LangGraph com checkpointer Postgres; agentes: roteador, retrieval, SAP HANA query agent (read-only via view materializada), report generator.
- **LLM:** cascade GPT-4o-mini → GPT-4o via Azure OpenAI; fallback Anthropic via AWS Bedrock.
- **Gateway:** LiteLLM self-hosted + Redis (cache exact + semantic).
- **Observability:** Langfuse self-hosted; OpenTelemetry → Azure Monitor.

### A.3 Restrições e governança
- LGPD: anonimização de motoristas/clientes; minimização nos prompts.
- SAP: agente nunca executa SQL livre — apenas views aprovadas com parâmetros validados.
- SharePoint: ACL replicada como metadata; filtro no retrieval.
- ITIL 4 / COBIT: pipeline de mudança (request → CAB → deploy) aplicado a prompts, modelos, índices.

### A.4 KPI esperados
- Custo por consulta: <$0.01 com cache + cascade.
- Latência p95: <3s.
- Faithfulness em golden set operacional: >0.85.
- Taxa de fallback humano: <10%.

---

## 12. Apêndice B — Aplicação Prática: Farmacêutico Regulado (GxP)

### B.1 Casos de uso permitidos × proibidos

| Caso | Permitido? | Justificativa |
|---|---|---|
| Assistente de busca em POPs internos (não-crítico) | **Sim**, com HITL | Annex 22 §1; não impacta decisão GMP crítica |
| Suporte à elaboração de Change Control / CAPA (draft) | **Sim**, HITL + aprovador humano | Output é minuta; aprovação humana é o ato regulado |
| Triagem de relatos de farmacovigilância para priorização (sem auto-decisão) | **Sim**, HITL | CIOMS WG XIV reconhece IA como suporte |
| Geração de release de batch (decisão crítica) | **Não** | Annex 22 proíbe LLM em decisões críticas |
| Inspeção visual de frascos com modelo determinístico de visão | **Sim** | Modelo estático determinístico; exemplo do FDA Jan/2025 |
| Chatbot regulatório para colaboradores treinados | **Sim**, com disclaimer e logs | Não-crítico; humano valida antes de agir |
| OOS automatizado por LLM | **Não** | Crítico GMP; proibido pelo Annex 22 |
| Geração de validation documentation a partir de specs | **Sim**, com revisão humana | Acelera; revisão humana mantém ALCOA+ |

### B.2 Arquitetura recomendada (perfil GxP)
- **Tudo on-prem ou em VPC dedicada** — preferencialmente em região brasileira com DPA (Azure Brazil South, AWS São Paulo).
- **Embedding:** BGE-M3 self-hosted em GPU (Apache 2.0; versionável; reprodutível).
- **Vector DB:** Qdrant on-prem ou pgvector on-prem; tenant por unidade fabril; ACL via Postgres RLS ou Qdrant payload filters.
- **Reranker:** BGE-reranker-v2-m3 (determinístico, self-hosted).
- **LLM:** primário Llama 3.3 70B / Mistral Large via vLLM em GPU on-prem; secundário Azure OpenAI Brazil (DPA).
- **Orquestração:** LangGraph com checkpointer Postgres; cada nó persiste estado para audit trail.
- **Gateway:** Portkey self-hosted (open-source desde 24 de março de 2026) ou Bifrost; PII redaction, guardrails, audit logs, RBAC.
- **Observability/Eval:** Langfuse self-hosted + Ragas em CI; DeepEval como CI gate; revisão humana amostral 5–10%.
- **Document storage:** SharePoint (já existente) com ACL; replicação a Postgres com sincronização incremental e versionamento.

### B.3 Documentação CSV — artefatos esperados
1. URS (User Requirement Specification): caso de uso, COU, criticidade GMP.
2. FS + DS: arquitetura, modelos, versões.
3. Risk Assessment (FMEA + framework 7-step FDA): influence × consequence.
4. Validation Plan: estratégia, golden set, métricas, critérios.
5. IQ/OQ/PQ:
   - IQ: instalação dos componentes versionados.
   - OQ: testes funcionais (golden set, adversarial, prompt injection).
   - PQ: performance em produção controlada (sampling, métricas RAG).
6. Traceability Matrix.
7. Audit trail design (ALCOA+).
8. Change Control SOP.
9. Periodic Review trimestral.
10. Decommissioning Plan (retenção ≥5 anos — RDC 658/2022 art. 128).

### B.4 Mapeamento normativo
| Requisito | Origem | Como atender |
|---|---|---|
| Sistemas computadorizados validados | RDC 658/2022 + IN 134/2022 | CSV conforme GAMP 5 + ISPE GAMP AI |
| Audit trail | Annex 11 EU; IN 134 | Logs imutáveis (gateway + LangGraph state) |
| Determinismo em crítico | Annex 22 draft | Não usar LLM em crítico; usar classificadores |
| HITL em uso de LLM | Annex 22 draft | Workflow obriga aprovação humana antes de side-effect |
| Risk-based credibility | FDA Jan/2025 + GAMP 5 | 7-step + GAMP categories |
| ALCOA+ | EU Annex 11; RDC 658 | Tagging completo de cada execução |
| Change control | GAMP 5; ITIL 4 | PM com avaliação de impacto e retest |
| Explainability | Annex 22 §8 | Citação de chunks; trace completo |
| Confidence | Annex 22 §9 | Reranker score + threshold; abstain em low confidence |

---

## 13. Production Readiness Checklist

### 13.1 Segurança
- [ ] PII detection + redaction (Presidio, Portkey).
- [ ] RBAC por tenant/usuário (gateway + vector DB + storage).
- [ ] Filtros ACL em **todo** retrieval.
- [ ] Defesa em camadas vs prompt injection (Llama Guard / Azure Prompt Shield, instruction hierarchy, privilege separation, HITL).
- [ ] Pen test e red-teaming (DeepTeam, Lakera Red).
- [ ] Secrets em vault (HashiCorp / AWS Secrets / Azure Key Vault); rotação.
- [ ] Criptografia em repouso e trânsito; BYOK por tenant.

### 13.2 Custo
- [ ] Tagging de tokens por user/tenant/agent/prompt template.
- [ ] Hard limits no gateway.
- [ ] Alertas em 70%/90% do budget.
- [ ] Cascade configurado.
- [ ] Cache exact + semantic com TTL.
- [ ] Prompt caching nativo onde aplicável.
- [ ] Revisão mensal por intent.

### 13.3 Observabilidade
- [ ] OpenTelemetry com GenAI semantic conventions.
- [ ] Trace end-to-end com correlation ID.
- [ ] Métricas: latência p50/p95/p99, error rate, tokens, custo, faithfulness, refusal rate.
- [ ] LLM-as-judge online sampling 1–5%.
- [ ] Drift detection em distribuição de queries.
- [ ] Dashboards por tenant.
- [ ] Alertas para regressão (>2σ).
- [ ] Incident response runbook.

### 13.4 Compliance (GxP)
- [ ] URS / FS / DS / VP / IQ / OQ / PQ / Traceability.
- [ ] Risk assessment com framework 7-step FDA + ICH Q9.
- [ ] Versionamento bit-exato de modelo, prompt, índice.
- [ ] Audit trail ALCOA+ retido ≥5 anos.
- [ ] Change control via QMS (TrackWise, MasterControl, Qualio).
- [ ] Periodic review trimestral.
- [ ] Annual review com management.
- [ ] Treinamento documentado (AI literacy — ISPE GAMP AI).
- [ ] DPA/BAA com cada provedor cloud.
- [ ] Plano de contingência para descontinuidade do provedor.

---

## 14. Bibliografia Anotada

### Fundamentos
- **Lewis et al. (2020), Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks, NeurIPS.** Paper seminal de RAG.
- **Es et al. (2023), Ragas: Automated Evaluation of RAG, arXiv:2309.15217.** Define faithfulness e demais métricas reference-free.
- **Chen, Zaharia, Zou (2023), FrugalGPT, arXiv:2305.05176.** Cascade, prompt adaptation, approximation; até 98% redução de custo.
- **Regmi & Pun (2024), GPT Semantic Cache, arXiv:2411.05276.** 68.8% redução de chamadas; positive hit rate >97%.
- **Bang (2023), GPTCache, ACL NLP-OSS.** Implementação OSS de semantic cache.
- **Jin et al. (2024), Late Chunking, arXiv:2409.04701 (Jina).** Embedding com contexto antes do chunking.
- **Microsoft Research (jun/2024), GraphRAG; (nov/2024), LazyGraphRAG; (jun/2025), BenchmarkQED.** Comparação 96/96 contra vector RAG e variantes.
- **Ong et al. (2024), RouteLLM (LMSYS / UC Berkeley).** Routing matrix factorization atinge 95% da performance do GPT-4 com 26% das chamadas.

### Orquestração e frameworks
- **LangGraph docs (LangChain Inc.), v1.0 final de 2025.** Grafo tipado; durable execution; HITL.
- **CrewAI docs.** Crews + Flows event-driven (2025).
- **Microsoft (out/2025), Agent Framework public preview;** transição AutoGen/Semantic Kernel para maintenance mode.
- **OpenAI Agents SDK (2025).** Agents + Handoffs + Guardrails.
- **Anthropic Model Context Protocol (MCP), 2024.** Padrão de interop.
- **Linux Foundation Agent2Agent (A2A) Protocol, 2025.** Comunicação cross-framework.

### Segurança
- **OWASP Top 10 for LLM Applications 2025; LLM Prompt Injection Prevention Cheat Sheet.**
- **Ramakrishnan & Balaji (2025), Securing AI Agents Against Prompt Injection, arXiv:2511.15759.** Benchmark de 847 casos; PALADIN.
- **OpenAI (2024), Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions.**
- **Morris et al. (2023), Text Embeddings Reveal (Almost) As Much As Text.** Inversão de embeddings.

### Compliance (fontes primárias)
- **ISPE GAMP 5 Second Edition (julho de 2022)** — ispe.org. Inclui Appendix D11.
- **ISPE GAMP Guide: Artificial Intelligence (julho de 2025)** — ispe.org/publications/guidance-documents/gamp-guide-artificial-intelligence. ~290 pp; co-leads Stockton, Staib, Heitmann.
- **European Commission DG SANTE (7 de julho de 2025), Draft EU GMP Annex 22 — Artificial Intelligence** — health.ec.europa.eu/consultations/stakeholders-consultation-eudralex-volume-4-good-manufacturing-practice-guidelines-chapter-4-annex_en. Consulta encerrou 7 de outubro de 2025.
- **FDA (6 jan 2025; Fed. Register 7 jan 2025), Considerations for the Use of AI to Support Regulatory Decision-Making for Drug and Biological Products (DRAFT).** Docket FDA-2024-D-4689. Comment period encerrou 7 de abril de 2025.
- **EMA & FDA (14 de janeiro de 2026), Guiding Principles of Good AI Practice in Drug Development** — ema.europa.eu; fda.gov/media/189581/download. 10 princípios, não-vinculantes.
- **EMA (set/2024), Reflection Paper on the use of AI in the medicinal product lifecycle.**
- **FDA + Health Canada + UK MHRA (out 2021), 10 Guiding Principles for GMLP; (out 2023) PCCP Guiding Principles; (13 jun 2024) Transparency Guiding Principles; IMDRF final (jan 2025).**
- **FDA (dez 2024), Predetermined Change Control Plans for ML-Enabled Medical Devices — Final Guidance.**
- **ANVISA, RDC 658/2022 (30 mar 2022; vigor 2 mai 2022)** — anvisalegis.datalegis.net. BPF alinhado ao PIC/S.
- **ANVISA, IN 134/2022 (30 mar 2022).** Adota PIC/S para sistemas computadorizados.
- **ICH Q9(R1).** Quality Risk Management.
- **EU AI Act (Regulation 2024/1689, vigor 1 ago 2024).** Aplicação faseada 2025–2027.
- **ISO/IEC 42001:2023.** AI Management System.

### Benchmarks
- **MTEB Leaderboard (Hugging Face).** Embedding benchmark contínuo.
- **VectorDBBench.** Vector DBs.
- **Microsoft BenchmarkQED (17 jun 2025).** LazyGraphRAG vence 96/96 (statisticamente significativo em 95/96).
- **Agentset Rerankers Leaderboard.** ELO de rerankers.
- **AIMultiple (2025), RAG Evaluation Tools.** Comparativo W&B/Ragas/DeepEval/TruLens com 1460 questões e hard negatives.

### Gateways
- **Portkey (24 de março de 2026; GlobeNewswire).** Open source completo; processa 1T+ tokens/dia em 24.000+ orgs.
- **LiteLLM docs (BerriAI).** OSS MIT.
- **Bifrost (Maxim).** Rust, ~11µs overhead a 5k RPS.
- **Cloudflare AI Gateway docs.**

---

## 15. Lacunas de Conhecimento e Questões Abertas

1. **Validação estatística de não-determinismo de geração:** ausência de consenso sobre tamanho de amostra (n execuções) e tolerância de variância aceitável para CSV.
2. **Re-qualificação por atualização silenciosa do provedor:** sem prazo prescrito; OpenAI/Anthropic atualizam modelos sem aviso regulatório.
3. **Annex 22 final:** texto pode flexibilizar ou endurecer; impacto em RAG generativo em farma depende do desfecho.
4. **ANVISA AI específica:** vazio regulatório; expectativa industrial de convergência com EU/PIC/S, timing incerto.
5. **Métricas faithfulness em PT-BR:** maior parte da literatura é em inglês; juízes LLM em PT-BR ainda pouco estudados — validação local recomendada.
6. **Custo de evals:** LLM-as-judge pode custar mais que o sistema avaliado; balance sampling × cobertura é caso-a-caso.
7. **Prompt injection sem solução fechada:** defesas reduzem mas não eliminam; arquitetura (privilege separation) é mais eficaz que filtros.
8. **GraphRAG vs hybrid vs LazyGraphRAG:** vitória de LazyGraphRAG em BenchmarkQED carece de reprodutibilidade independente em domínios fora dos avaliados.
9. **AutoGen → Agent Framework migration path:** documentação ainda em transição (2025–26); equipes em produção devem planejar substituição.
10. **Aceitabilidade de modelos hospedados nos EUA sob LGPD** para dados sensíveis brasileiros: jurisprudência ANPD ainda incipiente.

---

## 16. Caveats

- **Velocidade de mudança:** ferramentas e modelos mudam mensalmente. Revalide trimestralmente. Toda recomendação tem validade ~6–12 meses.
- **Benchmarks são direcionais.** MTEB, ELO de rerankers, comparativos de gateways refletem cenários sintéticos; mantenha golden set proprietário para decisão final.
- **Vendor neutrality:** comparações são técnicas; nenhuma ferramenta é endossada absolutamente. Há viés de cobertura — ferramentas mais documentadas aparecem mais.
- **Annex 22 é DRAFT.** Citações verbatim são do texto em consulta pública (7 de julho de 2025); versão final pode divergir.
- **FDA Jan/2025 é DRAFT.** Status maio/2026: comentários processados, final não publicado.
- **ANVISA não tem regulação AI específica.** A leitura aqui apresentada (aplicar GAMP 5 + ISPE GAMP AI + Annex 22 como referência por analogia) é interpretação industrial razoável, **não** exigência expressa da ANVISA.
- **Prompt injection:** pesquisa ativa; defesas atuais reduzem risco, não eliminam.
- **LLM-as-judge tem limites empíricos demonstrados.** Benchmarks 2025 mostram que **nenhuma ferramenta de eval** distingue de forma confiável hard negatives factualmente errados de contextos corretos. Use múltiplas ferramentas e revisão humana amostral.
- **Esta é documentação de referência, não substitui consultoria jurídica/regulatória.** Para submissões à FDA/ANVISA, valide com regulatório e jurídico.