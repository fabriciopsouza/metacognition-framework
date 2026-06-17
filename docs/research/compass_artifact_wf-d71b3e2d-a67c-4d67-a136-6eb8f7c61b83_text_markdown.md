# Base de Conhecimento Técnico — Avaliação e Governança de Sistemas de IA Não-Determinísticos em Ambientes Regulados (Farma/Life Sciences)

## 1. Sumário Executivo

Sistemas de IA não-determinísticos (LLMs, RAG, agentes) podem ser governados em ambiente farmacêutico regulado, **mas apenas se forem tratados como sub-sistemas dentro de um sistema computadorizado GxP**, não como software convencional. O eixo central permanece o de qualidade/CSV — GAMP 5 (2ª edição, 2022), seu Apêndice D11 e o novo **ISPE GAMP® Guide: Artificial Intelligence (julho de 2025, 290 páginas)** — com os frameworks específicos de IA (NIST AI RMF 1.0 + GenAI Profile, ISO/IEC 42001:2023, ISO/IEC 23894:2023, EU AI Act) atuando como **camada complementar** sobre essa espinha. Esse posicionamento é hoje **CONSOLIDADO** em fontes normativas primárias (ISPE 2025; EMA 2024; FDA 2025; MHRA 2024).

O que está **CONSOLIDADO**:
- Abordagem baseada em risco (ICH Q9, GAMP 5, FDA CSA final 24/set/2025, EU AI Act art. 9) para definir o esforço de validação proporcional ao risco do paciente/produto/dado.
- Princípios ALCOA+ aplicam-se integralmente a artefatos de IA (datasets de treino, prompts, outputs, model cards, versões de modelo).
- Necessidade de governança de mudança (change control) sobre modelos, prompts e datasets; logging completo de interações; supervisão humana proporcional ao risco.
- Princípios de Good Machine Learning Practice (GMLP, FDA/Health Canada/MHRA, 27/out/2021) e os papers de transparência (jun/2024) e PCCP (out/2023).

O que está **EMERGENTE**:
- Métricas de avaliação para LLM/RAG (faithfulness, groundedness, relevância, hallucination rate) — operacionalmente úteis, mas sem ainda valores de corte regulatórios consolidados.
- Predetermined Change Control Plan (PCCP) para dispositivos AI-enabled (FDA, final 3/dez/2024) — framework regulatório novo, com adoção ainda baixa: estudo do npj Digital Medicine (jul/2025), cobrindo 1.016 dispositivos AI/ML autorizados pela FDA até dez/2024, encontrou apenas 15 (1,5%) com PCCP reportado; já em 2025 a Innolitics Year-in-Review (295 autorizações) apontou que 10% das autorizações AI/ML incluíram PCCPs, indicando rápida ascensão.
- LLM-as-judge em pipelines de avaliação — adoção crescente, mas com vieses documentados (posição, comprimento, autoridade, self-preference).
- Categorização específica de modelos de IA na nova ISPE GAMP AI Guide (Apêndice M11 §22.4 "Model Categories"), separada da categorização tradicional Cat 1/3/4/5.

O que está **EM DISPUTA**:
- Encaixe de IA generativa nas categorias GAMP 5 originais (a indústria diverge se LLMs são "Cat 5 custom" ou demandam axis paralelo).
- Escopo da classificação "high-risk" do EU AI Act para IA usada em P&D farmacêutico (EFPIA argumenta exclusão; reguladores não convergiram).
- Aceitabilidade de modelos "black-box" em decisão regulatória (EMA admite em certos casos, FDA pede "credibilidade para o COU", ANVISA ainda sem posição formal sobre IA generativa).
- Reprodutibilidade de outputs estocásticos como critério de validação (vs. reprodutibilidade estatística de distribuições de saída).
- Validação de prompts: artefato controlado de configuração (paralelo a Cat 4) ou parte do código fonte (Cat 5)?

**Recomendação imediata**: trate cada caso de uso de IA generativa como um sub-sistema GxP com classificação de risco própria (modelo de influência × consequência da decisão, conforme o draft FDA jan/2025), defina uma Intended Use Statement formal, monte um Validation Master Plan ancorado em GAMP 5 + GAMP AI Guide, registre dataset/model/prompt versioning sob ALCOA+, e mantenha supervisão humana proporcional ao risco. Para uso em decisão regulatória, alinhar ao framework de 7 passos de credibilidade do FDA (jan/2025) e ao reflection paper da EMA (set/2024).

---

## 2. Glossário Essencial

- **ALCOA+**: Princípios de integridade de dados — Attributable, Legible, Contemporaneous, Original, Accurate, + Complete, Consistent, Enduring, Available (referenciado em FDA, EMA Annex 11, ICH Q10).
- **CSV (Computerized System Validation)**: validação tradicional de sistemas computadorizados em ambiente GxP, baseada em URS/FS/DS/IQ/OQ/PQ.
- **CSA (Computer Software Assurance)**: abordagem da FDA (draft set/2022; final 24/set/2025) que substitui Seção 6 do General Principles of Software Validation, focada em risco e "critical thinking" em vez de documentação exaustiva.
- **COU (Context of Use)**: papel e escopo específicos do modelo de IA dentro da questão de interesse — "the COU defines the specific role and scope of the AI model used to address a question of interest" (FDA Draft Guidance, jan/2025).
- **Model risk** (FDA draft jan/2025): combinação de (a) **model influence** = "the contribution of the evidence derived from the AI model relative to other contributing evidence used to inform the question of interest" e (b) **decision consequence** = "the significance of an adverse outcome resulting from an incorrect decision concerning the question of interest". Avaliados independentemente; combinados em matriz.
- **PCCP (Predetermined Change Control Plan)**: plano pré-aprovado pela FDA que descreve modificações futuras autorizadas em dispositivos AI-enabled sem nova submissão (FDA Final Guidance, 3/dez/2024) — três componentes: Description of Modifications, Modification Protocol, Impact Assessment.
- **GMLP (Good Machine Learning Practice)**: 10 princípios conjuntos FDA/Health Canada/MHRA, 27/out/2021.
- **Faithfulness / Groundedness**: métrica de fidelidade da resposta gerada ao contexto recuperado (RAG); cada afirmação do output deve ser rastreável às fontes fornecidas.
- **Hallucination / Confabulation**: geração de conteúdo plausível mas não fundamentado (NIST AI 600-1 usa "confabulation").
- **Drift**: data drift (mudança na distribuição dos inputs), concept drift (mudança na relação input→output desejado), model drift (degradação de desempenho do modelo).
- **Prompt injection**: manipulação do comportamento do LLM via inputs maliciosos (OWASP LLM01:2025).
- **AIMS**: AI Management System (ISO/IEC 42001:2023) — sistema de gestão organizacional para IA, certificável.
- **AI RMF**: AI Risk Management Framework (NIST AI 100-1, jan/2023) com funções GOVERN, MAP, MEASURE, MANAGE.
- **GenAI Profile**: NIST AI 600-1 (26/jul/2024), perfil setorial cruzado do AI RMF aplicado a IA generativa, com 12 categorias de risco e mais de 200 ações sugeridas mapeadas às quatro funções do AI RMF.
- **Dynamic vs. static ML subsystem** (ISPE GAMP 5 Apêndice D11): modelos "locked" (não mudam em produção) vs. modelos adaptativos/contínuos.
- **LLM-as-judge**: uso de outro LLM como avaliador automatizado de saídas de LLM.

---

## 3. Tópicos do Escopo

### 3.1 Como avaliar a qualidade de sistemas de IA não-determinísticos

**Conceito.** Avaliação de sistemas não-determinísticos divide-se em: (i) avaliação offline (golden datasets, regression tests sobre conjuntos representativos), (ii) avaliação online (telemetria em produção, dashboards, amostragem de tráfego para LLM-as-judge), (iii) red-teaming e adversarial testing. Para RAG, opera-se com a "RAG Triad": **context relevance** (recuperação), **groundedness/faithfulness** (geração ancorada no contexto), **answer relevance** (resposta atende à pergunta) — assim definidas em frameworks como Ragas, DeepEval, Braintrust, Evidently AI.

**Por que importa.** Em ambiente GxP, o output do sistema influencia decisões com consequência (paciente, produto, dado). Saídas estocásticas exigem critérios estatísticos de desempenho em vez de teste binário pass/fail. Sem métricas operacionais, a validação fica subjetiva e auditorias caem.

**Como aplicar.**
- Definir métricas mínimas por caso de uso (RECOMENDADO):
  - Para RAG: faithfulness ≥ X, answer relevance ≥ Y, context precision/recall ≥ Z, hallucination rate ≤ W (valores definidos via baselining; não há cortes regulatórios universais).
  - Para LLMs sem retrieval: factual correctness via golden set, toxicity, refusal-appropriateness, format adherence.
  - Para agentes: tool-call accuracy, agent goal accuracy, taxa de loops/refusals.
- Montar um **golden dataset versionado** representativo do domínio, com curadoria por SMEs, revisado periodicamente para evitar "rot" de avaliação (drift do próprio dataset).
- **Regression testing**: rodar o golden set automaticamente em cada release de prompt/modelo/RAG-index; gate de promoção definido por VMP.
- **LLM-as-judge** com cautelas (CONSOLIDADO em literatura recente, EMERGENTE como prática regulatória):
  - Calibrar contra anotação humana de SMEs em amostra inicial.
  - Mitigar vieses conhecidos:
    - **Position bias** — Shi et al., "Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge" (arXiv:2406.07791, jun/2024), com 15 LLM judges, 22 tarefas e >150.000 instâncias.
    - **Verbosity/length bias** — Saito et al., "Verbosity bias in preference labeling by large language models" (arXiv:2310.10076, 2023).
    - **Self-preference bias** — Panickssery et al., "LLM evaluators recognize and favor their own generations" (NeurIPS 2024, arXiv:2404.13076).
    - **Authority bias** — fabricated citations disrupt judgment accuracy (referenciado em arXiv:2410.02736).
  - Multi-evidence calibration; usar reference answer "full-marked" quando possível.
- **Online evaluation**: sampling assíncrono (5–10%) de tráfego de produção para um juiz LLM rodando contra rubrica offline; dashboards de drift de embeddings de prompts.

**Pontos em aberto.**
- Não existem ainda **thresholds regulatórios** de hallucination rate ou faithfulness para uso GxP — cada companhia precisa justificar seus cortes (EM DISPUTA).
- Validade de LLM-as-judge como evidência regulatória primária — aceito como triagem, **não substitui revisão humana** em pontos críticos (EMERGENTE).
- Custo de manutenção do golden dataset versus shelf-life dos modelos (em refresh contínuo) (EM DISPUTA).

**Classificação geral**: métricas core (faithfulness/relevance/groundedness) — **[CONSOLIDADO]** como prática técnica; **[EMERGENTE]** como evidência de validação regulatória.

---

### 3.2 CSV / GAMP 5 aplicado a comportamento não-determinístico

**Conceito.** GAMP 5 (2ª edição, julho de 2022) preserva a abordagem baseada em risco (alinhada a ICH Q9) e introduz o **Apêndice D11 — Artificial Intelligence and Machine Learning (AI/ML)**, que separa sub-sistemas ML em **estáticos** (locked, não evoluem em operação) e **dinâmicos** (capazes de aprender pós-deploy). O ciclo de vida ML cobre fases Concept → Project → Operation, com ênfase em dados, métricas de desempenho e monitoramento contínuo. O **ISPE GAMP® Guide: Artificial Intelligence (julho de 2025)** estende esses conceitos em 290 páginas, com Apêndice M11 §22.4 "Model Categories" introduzindo um eixo de categorização específico para modelos de IA, paralelo às categorias tradicionais de software (Cat 1/3/4/5).

**Por que importa.** Sistemas determinísticos são validados com IQ/OQ/PQ baseados em testes reproduzíveis; sistemas estocásticos exigem evidência estatística e revalidação contínua. A questão "qual categoria GAMP é um LLM" não tem resposta única consensual.

**Como aplicar.**
- **Classificação GAMP 5** (CONSOLIDADO para componentes determinísticos):
  - Cat 1: Infrastructure software (SO, DB engines, virtualização).
  - Cat 3: Non-configured products — "Systems that cannot be configured to conform to business processes and systems that are configurable but for which only the default configuration is used".
  - Cat 4: Configured products — LIMS, ERP, MES, EDMS, QMS, CDS, DCS, SCADA configurados ao processo.
  - Cat 5: Custom applications — "developed to meet the specific needs of the regulated company; this software is custom designed and coded to suit the business".
  - GAMP 5 (2ª ed.) explicita: "computerized systems are generally made up of a combination of components from different categories; the categories should be viewed as a continuum."
- **Onde encaixar IA generativa** (EM DISPUTA):
  - Modelo fundacional comercial (ex.: GPT-4o, Claude, Gemini via API): comportamento aproxima Cat 3 ou 4 dependendo de configuração (system prompt, RAG, fine-tuning).
  - Fine-tuning interno ou modelo proprietário: Cat 5.
  - **Solução prática recomendada (ISPE GAMP AI Guide 2025)**: categorizar o software hospedeiro pela escala 1/3/4/5 e o **modelo separadamente** pelo eixo "Model Categories" (§22.4 da AI Guide).
- **Princípios de validação para sub-sistemas ML** (GAMP D11):
  - Intended Use Statement formal antes de qualquer atividade técnica.
  - Data Acquisition Plan (origem, curadoria, classificação, cleansing, augmentation).
  - Splits train/validation/test com independência documentada (GMLP princípio 4).
  - Performance metrics com critérios de aceitação registrados.
  - Sustained verification: monitoramento de drift, performance e retraining triggers.
- **Computer Software Assurance (CSA)** — FDA emitiu guia final em 24/set/2025 (atualizado em 03/fev/2026), substituindo a Seção 6 do General Principles of Software Validation (1997). CSA define-se como "a risk-based approach for establishing and maintaining confidence that software is fit for its intended use" e estrutura-se em quatro passos: identificar uso pretendido; determinar risco; determinar atividades de assurance; estabelecer registro adequado. **Aplicável a IA**: a lógica risk-based encaixa-se naturalmente na validação de IA — atividades de assurance proporcionais ao risco; documentar a *razão* das escolhas em vez de scripts massivos.

**Pontos em aberto.**
- A FDA CSA aplica-se formalmente a "production and quality system software" para dispositivos (21 CFR 820.70(i)); sua extensão por analogia para IA em manufatura de medicamentos é aceita pela indústria mas **não foi formalmente endossada** para sistemas GMP de medicamentos pela FDA (EM DISPUTA).
- A categorização de **prompts** (artefatos texto que mudam comportamento) é controversa: para alguns são "configuração" (paralelo Cat 4); para outros, "código" (Cat 5). A ISPE GAMP AI Guide (jul/2025) introduziu o conceito de "prompt como artefato controlado" mas o texto detalhado está atrás do paywall (EMERGENTE).
- "Dynamic systems" (modelos que aprendem em produção) ainda têm tratamento incipiente — o PCCP da FDA (final dez/2024) preenche para devices, mas não há equivalente para sistemas GMP de medicamentos (EM DISPUTA).

---

### 3.3 Rastreabilidade e auditoria

**Conceito.** Trilha auditável para um sistema de IA generativa cobre cinco eixos: (i) versionamento de modelo (model card, hash, weights/fingerprint), (ii) versionamento de dados (datasets de treino, golden sets, RAG corpus), (iii) versionamento de prompts (system prompt, templates, RAG retrieval prompts), (iv) decision logging (input, contexto recuperado, output, scores, intervenção humana, timestamp, identidade do usuário), (v) data lineage end-to-end.

**Por que importa.** Sob ALCOA+, cada registro precisa ser Attributable, Legible, Contemporaneous, Original, Accurate, Complete, Consistent, Enduring e Available — o que para um output estocástico significa que **a entrada, o contexto, a versão do modelo e o output precisam estar amarrados por chaves persistentes**. Sem isso, não há reprodutibilidade nem possibilidade de re-análise em audit.

**Como aplicar.**
- **Model cards** (Mitchell et al., FAT* 2019) e **datasheets for datasets** (Gebru et al., CACM 2021) — **[CONSOLIDADO]** em literatura, **[EMERGENTE]** como artefato regulatório obrigatório (FDA Transparency Guiding Principles, jun/2024, reforça); ISO/IEC 42001:2023 exige documentação equivalente.
- **Logging mínimo recomendado** por interação GxP:
  - `request_id` UUID
  - `timestamp` ISO-8601 com timezone
  - `user_id` autenticado (ALCOA: Attributable)
  - `session_id`
  - `system_prompt_version` (hash + tag semver)
  - `model_id` + `model_version` + provider
  - `input` (ou hash + referência se PII)
  - `retrieved_chunks` (IDs e versões do corpus) — para RAG
  - `output` + `output_tokens` + `seed/temperature/top_p`
  - `judge_scores` (se LLM-as-judge ou guardrail)
  - `human_review_decision` (accept/reject/edit, identidade do revisor)
- **Versionamento triplo**: model + data + prompt — cada release deve ter um manifesto único que combine as três versões e os critérios de aceitação que passou (regression suite). Armazenar em repositório de configuração sob change control.
- **Reproducibility caveats**: outputs são estocásticos por design. Reprodutibilidade aceitável passa a ser:
  - Determinismo opcional via `temperature=0` + `seed` fixo (não totalmente determinístico em LLMs hospedados — providers podem alterar).
  - Reprodutibilidade estatística: re-rodar o golden set deve produzir métricas dentro de uma janela de tolerância pré-definida.
- **Change management** seguindo ITIL 4 / COBIT: cada mudança em modelo, prompt, índice RAG ou dataset é uma RFC; classificação (standard/normal/emergency) com impact assessment de risco específico para IA (drift, regressão de faithfulness, novos failure modes).

**Pontos em aberto.**
- Retenção de logs de outputs estocásticos pode crescer rapidamente — políticas de amostragem versus retenção total são debatidas (EMERGENTE).
- Para modelos fundacionais via API, o provider raramente expõe o "model version exato" auditável — risco de vendor lock-in e dependência (CONSOLIDADO como risco; EM DISPUTA quanto à mitigação aceitável).
- Determinismo verdadeiro em LLMs hospedados não é garantido pelos provedores (CONSOLIDADO como limitação técnica).

---

### 3.4 Gestão de risco específica de IA generativa

**Conceito.** A IA generativa introduz vetores de risco que não existem em software determinístico, mapeados em fontes primárias: NIST AI 600-1 (12 categorias para GenAI, mais de 200 ações sugeridas), OWASP Top 10 for LLM Applications 2025, ISO/IEC 23894:2023 (AI risk management guidance). Os principais são:
- **Hallucination/confabulation** — geração de afirmações plausíveis mas falsas (NIST 600-1).
- **Drift** — data drift, concept drift, model drift (vendor pode atualizar o modelo silenciosamente).
- **Prompt injection** (OWASP LLM01:2025) — direta ou indireta (via documentos em RAG).
- **Sensitive information disclosure** (LLM02:2025).
- **Supply chain vulnerabilities** (LLM03:2025) — modelos de terceiros, pesos baixados, datasets envenenados.
- **Data and model poisoning** (LLM04:2025).
- **Improper output handling** (LLM05:2025) — output executado sem sanitização.
- **Excessive agency** (LLM06:2025) — agente com permissões além do necessário.
- **System prompt leakage** (LLM07:2025).
- **Vector and embedding weaknesses** (LLM08:2025) — específico para RAG.
- **Misinformation** (LLM09:2025) — inclui hallucination + overreliance.
- **Unbounded consumption** (LLM10:2025).
- **Vendor dependency / lock-in** — risco de descontinuação ou alteração de modelo.

**Por que importa.** Compliance farmacêutico exige rastreabilidade do erro até a causa-raiz; cada vetor acima pode comprometer dado GxP, paciente ou IP.

**Como aplicar (controles compensatórios).**
- **Hallucination**: RAG com forçamento de citação ("answer only from provided context"); LLM-as-judge para faithfulness pós-geração; revisão humana mandatória para outputs em decisão GxP.
- **Prompt injection**: separar instrução de dado (delimitadores, structured prompts); content filters; allowlist de comandos para agentes; testes adversariais regulares (red team). OWASP (2024/2025) reconhece a limitação: "given the stochastic influence at the heart of the way models work, it is unclear if there are fool-proof methods of prevention for prompt injection".
- **Data leakage**: classificação de dados antes de envio à API; uso de tenants dedicados ou modelos on-prem para CCI; DPIA quando há dado pessoal (LGPD/GDPR); BAA/DPA com provedor.
- **Drift**: monitoramento de embeddings de input + métricas de output; alertas estatísticos; retraining/refresh triggers; testes regressivos contra golden set em cadência fixa.
- **Vendor lock-in**: abstração via gateway/orchestrator; testes A/B com modelos alternativos; cláusulas contratuais de notificação prévia para mudança de modelo; cópia/snapshot de pesos quando possível (open-weights).
- **Excessive agency / agents**: princípio do menor privilégio aplicado ao toolset; aprovação humana obrigatória para ações irreversíveis; limites duros (rate, escopo).

**Pontos em aberto.**
- Prompt injection não tem solução fool-proof — limitação fundamental admitida pelo próprio OWASP (CONSOLIDADO como limitação).
- Definição de "serious incident" para IA sob EU AI Act ainda em refinamento (EMERGENTE).

---

### 3.5 Human-in-the-loop, supervisão e níveis de autonomia

**Conceito.** A FDA GMLP Princípio 7 (out/2021) é explícito: "Focus is placed on the performance of the Human-AI Team" — "where the model has a 'human in the loop,' human factors considerations and the human interpretability of the model outputs are addressed with emphasis on the performance of the Human-AI team, rather than just the performance of the model in isolation." O EU AI Act art. 14 exige medidas de supervisão humana proporcionais ao risco para sistemas high-risk. A NIST AI RMF inclui "Human-AI Configuration" como dimensão de governança. ISO/IEC 42001:2023 exige documentação de oversight no AIMS.

**Por que importa.** O nível de autonomia que o sistema tem define o residual de risco que cai sobre o operador humano. Quanto maior a autonomia, maior a exigência de evidência de credibilidade do modelo (FDA jan/2025: model influence).

**Como aplicar — modelo de níveis de autonomia (síntese de literatura; **[EMERGENTE]** como taxonomia consensual):**

| Nível | Descrição | Papel humano | Risco residual |
|---|---|---|---|
| L0 | IA não usada | n/a | n/a |
| L1 | Assistente passivo (informa) | Decide sozinho | Baixo |
| L2 | Sugestão estruturada | Revisa cada item, decide com base | Baixo-médio |
| L3 | Pré-aprovação humana obrigatória | Aprova cada output antes de uso | Médio |
| L4 | Aprovação por exceção (sample-based) | Aprova amostra; sistema age sozinho fora dela | Médio-alto |
| L5 | Autônomo com auditoria post-hoc | Audita pós-fato | Alto |
| L6 | Totalmente autônomo | Nenhum | Não aceitável em GxP crítico |

- **Regra prática**: para decisões com `model influence = high` E `decision consequence = high` (matriz FDA jan/2025), exigir mínimo L3.
- **Design de controles**:
  - UI deve mostrar fontes/contexto recuperado para permitir verificação humana eficiente.
  - Apresentar incerteza/confidence sempre que possível.
  - "Friction" proporcional: botão de aprovação claro, log persistente do aceite.
  - Treinamento de operadores em modos de falha do modelo (não basta "saber usar"; precisa "saber desconfiar").
- **Anti-padrões a evitar**:
  - "Rubber stamp" — humano que aprova tudo sem ler (degrada a oversight para zero).
  - Automação parcial onde humano só age em alarme — vigilância humana é comprovadamente baixa em modos de exceção.

**Pontos em aberto.**
- Não há taxonomia regulatória oficial de níveis de autonomia (EMERGENTE).
- Métricas de qualidade do "Human-AI team" como conjunto (vs. modelo isolado) ainda são área de pesquisa ativa (EM DISPUTA).

---

### 3.6 Frameworks de referência e seus relacionamentos

**Eixo principal — Qualidade / CSV:**
- **ISPE GAMP® 5: A Risk-Based Approach to Compliant GxP Computerized Systems, Second Edition** (ISPE, julho/2022) — referência principal para CSV/GAMP no setor. Apêndice D11 introduz AI/ML; outras apêndices novas cobrem agile, blockchain, cloud. **[CONSOLIDADO]**.
- **ISPE GAMP® Guide: Artificial Intelligence** (ISPE, julho/2025; 290 páginas) — primeiro guia abrangente do setor para IA em GxP; explicitamente desenhado para coexistir com ISO/IEC 42001, EMA Reflection Paper, FDA AI guidances. Cobre ciclo de vida, QRM específica para IA, governança de dados/modelo, papel do fornecedor, IA como/em dispositivo médico, sistemas dinâmicos, cibersegurança (incl. ataques adversariais). **[EMERGENTE]** (publicado há menos de 12 meses).
- **ISPE GAMP RDI Good Practice Guide: Data Integrity by Design** (out/2020) com Apêndice S1 sobre ML (foco em data integrity). **[CONSOLIDADO]**.
- **FDA Computer Software Assurance for Production and Quality System Software** — final em 24/set/2025 (atualizado 03/fev/2026); substitui Seção 6 do General Principles of Software Validation (1997/2002). Pivot de CSV para CSA: risk-based, critical thinking, scripted+unscripted testing. **[CONSOLIDADO]** como direção regulatória.
- **ALCOA+** — princípios de integridade de dados aplicáveis a todo registro GxP, incluindo artefatos de IA (datasets, prompts, outputs). **[CONSOLIDADO]**.
- **PIC/S Annex 11** (revisão 2022) — endossa risk-management e reliance em evidência do fornecedor; relevante para validação de cloud/SaaS hospedando IA. **[CONSOLIDADO]**.
- **EU GMP Annex 11** e **Annex 22** (draft 2024 sobre AI/ML, EudraLex) — em desenvolvimento. **[EMERGENTE]**.

**Eixo regulatório de IA em saúde:**
- **FDA Draft Guidance: Considerations for the Use of AI to Support Regulatory Decision-Making for Drug and Biological Products** (Docket FDA-2024-D-4689; 6/jan/2025) — primeiro draft FDA para uso de IA em decisão regulatória de medicamentos/biológicos. Framework de credibilidade em 7 passos (verbatim, Seção IV.A):
  1. Define the question of interest that will be addressed by the AI model.
  2. Define the COU for the AI model.
  3. Assess the AI model risk.
  4. Develop a plan to establish the credibility of AI model output within the COU.
  5. Execute the plan.
  6. Document the results of the credibility assessment plan and discuss deviations from the plan.
  7. Determine the adequacy of the AI model for the COU.
  - **Model risk** = combinação de **model influence** + **decision consequence**, avaliados independentemente.
  - Baseado conceitualmente no **ASME V&V40-2018** (Assessing Credibility of Computational Modeling — Application to Medical Device). **[EMERGENTE]** (draft, prazo de comentário fechou em 7/abr/2025).
- **FDA Final Guidance: Marketing Submission Recommendations for a Predetermined Change Control Plan for AI-Enabled Device Software Functions** (3/dez/2024) — Description of Modifications + Modification Protocol + Impact Assessment. Aplicável a 510(k), De Novo, PMA. **[EMERGENTE]**.
- **FDA Draft Guidance: Artificial Intelligence-Enabled Device Software Functions — Lifecycle Management and Marketing Submission Recommendations** (jan/2025). **[EMERGENTE]**.
- **FDA AI/ML SaMD Action Plan** (jan/2021) — plano original; **Good Machine Learning Practice for Medical Device Development — Guiding Principles** (FDA/Health Canada/MHRA, 10 princípios, 27/out/2021); **Transparency for ML-Enabled Medical Devices — Guiding Principles** (jun/2024); **PCCP for ML-Enabled Medical Devices — Guiding Principles** (out/2023). **[CONSOLIDADO]** como base de princípios.

> **Os 10 princípios GMLP (FDA/HC/MHRA, 27/out/2021)**:
> 1. Multi-Disciplinary Expertise Is Leveraged Throughout the Total Product Life Cycle.
> 2. Good Software Engineering and Security Practices Are Implemented.
> 3. Clinical Study Participants and Data Sets Are Representative of the Intended Patient Population.
> 4. Training Data Sets Are Independent of Test Sets.
> 5. Selected Reference Datasets Are Based Upon Best Available Methods.
> 6. Model Design Is Tailored to the Available Data and Reflects the Intended Use of the Device.
> 7. Focus Is Placed on the Performance of the Human-AI Team.
> 8. Testing Demonstrates Device Performance During Clinically Relevant Conditions.
> 9. Users Are Provided Clear, Essential Information.
> 10. Deployed Models Are Monitored for Performance and Re-training Risks Are Managed.

- **EMA Reflection Paper on the use of AI in the medicinal product lifecycle** (EMA/CHMP/CVMP/83833/2023; final em 9/set/2024) — cobre discovery, nonclinical, clinical, manufacturing, post-authorisation; menciona ALTAI (Assessment List for Trustworthy AI) para self-assessment. Admite "black box" em casos específicos. **[EMERGENTE]**.
- **MHRA Software and AI as a Medical Device Change Programme Roadmap** (out/2022; atualizado jun/2024 e dez/2024) — visão estratégica, guidance em desenvolvimento sequencial. **[EMERGENTE]**.
- **WHO Ethics and governance of AI for health: Guidance on large multi-modal models** (18/jan/2024) — 40+ recomendações para LMMs; sucessor da guidance original WHO 2021. **[EMERGENTE]**.
- **ICH E6(R3) Good Clinical Practice** (jan/2025) — não menciona "AI" verbatim, mas é "media-neutral" e exige validação fit-for-purpose para qualquer tecnologia em ensaio clínico. **[CONSOLIDADO]**.
- **IMDRF GMLP N88 e N81** (jan/2025, final) — convergência internacional sobre princípios GMLP e characterization de software médico. **[EMERGENTE]**.

**Eixo de governança e gestão de risco de IA (camada complementar):**
- **NIST AI 100-1 (AI RMF 1.0)** (jan/2023) — funções GOVERN, MAP, MEASURE, MANAGE. Voluntário. **[CONSOLIDADO]** como vocabulário de fato.
- **NIST AI 600-1 (Generative AI Profile)** (26/jul/2024) — perfil cruzado para GenAI; 12 categorias de risco e mais de 200 ações sugeridas mapeadas às quatro funções do AI RMF. **[EMERGENTE]**.
- **ISO/IEC 42001:2023 — Information technology — Artificial intelligence — Management System** (dez/2023) — primeiro standard certificável de AIMS; cláusulas 6.1 (risk), 8.2 (operational controls), 9 e 10 (monitoring/improvement). Já com adoção entre hyperscalers em escopos específicos: AWS foi o primeiro provedor de cloud a anunciar certificação acreditada cobrindo Amazon Bedrock, Amazon Q Business, Amazon Textract e Amazon Transcribe (2024); Google Cloud Platform, Google Workspace e Gemini (App) estão certificados; Microsoft mantém auditorias independentes regulares. **[EMERGENTE]** (adoção crescente).
- **ISO/IEC 23894:2023 — Artificial intelligence — Guidance on risk management** (2023) — guidance, não certificável; complementa 42001 e ISO 31000. **[EMERGENTE]**.
- **ISO/IEC 22989:2022 — Artificial intelligence — Concepts and terminology** — vocabulário base. **[CONSOLIDADO]**.
- **ISO/IEC TR 24027:2021 — Bias in AI systems and AI aided decision making**. **[CONSOLIDADO]**.
- **EU AI Act** (Regulamento (UE) 2024/1689, em vigor 1/ago/2024; aplicação faseada: proibições e literacy 2/fev/2025; GPAI e governança 2/ago/2025; geral 2/ago/2026; high-risk embutido em produtos regulados 2/ago/2027) — IA usada como safety component em MDR/IVDR é high-risk; obrigações de risk management, data governance, technical documentation, automatic logging, human oversight, robustez. **[CONSOLIDADO]** como lei aplicável; **[EM DISPUTA]** a classificação de IA em P&D farmacêutico (EFPIA argumenta exclusão fora de MDR/IVDR).
- **OWASP Top 10 for LLM Applications 2025** — taxonomia de risco técnico para LLMs. **[CONSOLIDADO]** como referência técnica de segurança.

**Eixo Brasil / ANVISA:**
- **ANVISA — uso interno de IA**: em 8/nov/2024, a ANVISA anunciou ferramenta interna de IA para otimizar análise de qualificação de impurezas (RDC 53/2015; IN 258/2023). Foco operacional, não regulatório. **[CONSOLIDADO]** como fato; **[EM DISPUTA]** como sinal de política regulatória futura.
- **RDC 657/2022** (SaMD/SaaMD no Brasil) e demais resoluções sobre dispositivos médicos — IA pode cair sob regulação de dispositivo conforme intended use.
- **PL 2338/2023 (Marco Legal da IA no Brasil)** — em tramitação no Congresso (status pode ter mudado); estabelece classificação de risco análoga ao EU AI Act. **[EMERGENTE]**.
- **LGPD (Lei 13.709/2018)** — base legal para uso de dados pessoais em treinamento e inferência; DPIA quando aplicável. **[CONSOLIDADO]**.
- **ANVISA / GMP**: RDC 658/2022 (Boas Práticas de Fabricação de Medicamentos) — base de CSV nacional, aceita GAMP 5 como guidance de fato.

**Mapeamento integrado** (resumo):

| Camada | Documentos | Status |
|---|---|---|
| Espinha CSV/qualidade GxP | GAMP 5 2ª Ed. + Apêndice D11 + ISPE GAMP AI Guide 2025 + CSA FDA 2025 + ALCOA+ + Annex 11 | Consolidada |
| Decisão regulatória de medicamento | FDA AI Draft jan/2025 + EMA Reflection 2024 + ICH E6(R3) | Emergente |
| Dispositivo médico AI | FDA PCCP 2024 + GMLP 2021 + IMDRF + MHRA roadmap + EU AI Act + MDR/IVDR | Emergente-consolidado |
| Gestão de risco de IA (org.) | NIST AI RMF + NIST 600-1 + ISO/IEC 42001 + ISO/IEC 23894 + ISO/IEC 22989 | Emergente |
| Segurança técnica | OWASP LLM Top 10 2025 + ISO/IEC TR 24027 | Consolidada (técnica) |
| Brasil | LGPD + RDC 657/2022 + RDC 658/2022 + IA ANVISA (uso interno) + PL 2338/2023 | Mista |

---

## 4. Checklist de Governança e Auditoria

### 4.1 Antes de iniciar (Concept phase)
- [ ] Intended Use Statement aprovado e versionado.
- [ ] Classificação GxP do caso de uso (impacto em paciente, produto, dado).
- [ ] Avaliação de risco inicial: model influence + decision consequence (matriz FDA jan/2025).
- [ ] Decisão sobre nível de autonomia (L1–L5).
- [ ] Decisão sobre arquitetura (modelo proprietário on-prem vs. API; com/sem RAG; com/sem fine-tuning).
- [ ] DPIA/LIA conforme LGPD/GDPR.
- [ ] Avaliação EU AI Act / ANVISA RDC 657: cai como dispositivo? High-risk?
- [ ] Análise de fornecedor (questionário + auditoria + contrato com BAA/DPA + cláusulas de change notification e auditability).

### 4.2 Durante o desenvolvimento (Project phase)
- [ ] URS com critérios de aceitação quantitativos (métricas mínimas).
- [ ] Plano de validação (VMP) referenciando GAMP 5 2ª Ed. + GAMP AI Guide.
- [ ] Plano de integridade de dados (ALCOA+ aplicado a datasets, prompts, outputs).
- [ ] Golden dataset curado por SMEs, versionado, com governança de atualização.
- [ ] Datasets de treino/validação/teste com independência documentada (GMLP 4).
- [ ] Documentação de cada artefato controlado:
  - [ ] Model Card (autor, intended use, dados de treino, métricas, limites, vieses conhecidos, modos de falha).
  - [ ] Datasheet for Datasets.
  - [ ] System Prompt versionado com tag semver.
  - [ ] Configuração do retrieval (RAG): chunking, embedding model, index version.
- [ ] Testes:
  - [ ] Funcionais (golden set).
  - [ ] Estatísticos de desempenho contra critérios (faithfulness, relevance, groundedness, hallucination rate).
  - [ ] Adversariais (prompt injection, jailbreak, data exfiltration).
  - [ ] Robustez (typos, paraphrasing, idioma).
  - [ ] Fairness/bias (sub-grupos relevantes).
  - [ ] Performance/latência/carga.
- [ ] Design da supervisão humana documentado (que ponto de decisão, qual UI, quais sinais).
- [ ] Plano de monitoramento contínuo + thresholds de alerta + planos de resposta.

### 4.3 Em produção (Operation phase)
- [ ] Logging completo conforme ALCOA+ (ver §3.3).
- [ ] Dashboard de métricas online: latência, throughput, drift de embeddings, faithfulness amostrado, taxa de refusal, intervenções humanas, incidentes.
- [ ] LLM-as-judge amostral assíncrono com calibração SME.
- [ ] Cadência de regression contra golden set (no mínimo a cada release; recomendado diário para sistemas críticos).
- [ ] Change control formal para qualquer mudança em modelo, prompt, índice RAG ou dataset.
- [ ] Notificação pelo provedor de mudanças de modelo (cláusula contratual; mitigação se ausente).
- [ ] Plano de retraining/refresh com triggers definidos (drift, performance, dataset growth, regulatório).
- [ ] Periodic Review (anual ou semestral) cobrindo: incidentes, drift, mudanças no contexto regulatório, performance, satisfação de usuário.
- [ ] Inspeção-prontidão: pacote de evidência pronto (VMP, Model Cards, logs de change, training records, results de regression).

### 4.4 Auditoria / Inspeção
- [ ] Rastreabilidade end-to-end de qualquer output GxP produzido pelo sistema (timestamp → request → model version → prompt version → RAG context → output → human decision).
- [ ] Evidência de que a supervisão humana foi efetiva (não rubber-stamp): amostragens, métricas de override, training records dos revisores.
- [ ] Evidência de gestão de mudança (RFCs, CAB approvals).
- [ ] Treinamento documentado da equipe (AI literacy — exigência explícita do EU AI Act art. 4, aplicável desde 2/fev/2025).

---

## 5. Frameworks de Decisão (If-X-Then-Y)

### 5.1 Determinação de nível de validação por risco

| Model Influence | Decision Consequence | Risco do Modelo | Validação mínima |
|---|---|---|---|
| Baixa | Baixa | Baixo | CSA simplificada; testes unscripted; documentação por exceção |
| Baixa | Alta | Médio | CSA com testes scripted em pontos críticos; revisão SME |
| Alta | Baixa | Médio | Validação formal por exceção; monitoramento contínuo |
| Alta | Alta | Alto | Validação plena (URS/FS/IQ/OQ/PQ); HITL L3+; PCCP se device; revisão regulatória |

### 5.2 Nível de supervisão humana por uso

| Caso de uso | Influência | Consequência | Nível recomendado | Observações |
|---|---|---|---|---|
| Sumarização de literatura interna | Baixa | Baixa | L4–L5 | Aceitável; spot-check |
| Auxílio à redação de SOP draft | Média | Média | L3 | Revisão obrigatória antes de aprovação |
| Triagem inicial de farmacovigilância | Alta | Alta | L3 | Toda saída revisada por especialista |
| Decisão de release de lote | Alta | Crítica | L1–L2 ou Não usar | Não recomendado como decisor primário |
| Análise de impurezas (caso ANVISA) | Média | Alta | L3 | Conforme prática ANVISA: IA agrupa/sugere, humano decide |
| Chatbot para pacientes sobre medicamento | Alta | Alta | L3 ou L4 com guardrails fortes | Risco regulatório alto; revisar EU AI Act high-risk |
| Code generation interno (não-GxP) | Baixa | Baixa | L4 | Code review humano padrão |

### 5.3 Encaixe em frameworks regulatórios

| Característica do sistema | Aplicar |
|---|---|
| Roda em GxP, gera dado em registro regulatório | GAMP 5 + ALCOA+ + 21 CFR Part 11 ou Annex 11 |
| Suporta decisão de safety/efficacy/quality em submissão FDA | FDA Draft jan/2025 (framework de 7 passos) |
| É componente de dispositivo médico (SaMD/AIaMD) na UE | EU AI Act high-risk + MDR/IVDR + ISO 14971 |
| Modelo evolui pós-deploy em device aprovado pelo FDA | PCCP (final 3/dez/2024) |
| Organização busca certificação de governança | ISO/IEC 42001:2023 |
| Risk management estruturado de IA | ISO/IEC 23894:2023 + NIST AI RMF + NIST 600-1 |
| Foco em segurança técnica do LLM | OWASP LLM Top 10 2025 |
| Ambiente Brasil, dado pessoal | LGPD + RDC 657 (se SaMD) + RDC 658 (GMP) |
| Ensaio clínico com componente IA | ICH E6(R3) + EMA Reflection Paper |
| Manufatura de medicamentos | EU GMP Annex 11 (+ futuro Annex 22) + PIC/S |

### 5.4 Decisão de retraining / refresh

| Trigger | Ação |
|---|---|
| Drift estatístico de embeddings de input > limiar | Investigar; ampliar revisão humana; planejar refresh |
| Faithfulness no golden set cai > 5pp | Pausar release; root-cause; possível rollback |
| Provedor anuncia atualização de modelo | Re-validar com regression suite antes de aceitar |
| Novo guidance regulatório aplicável | Gap-analysis; possível revalidação |
| Acúmulo de N novos exemplos rotulados | Avaliar incorporação ao golden set, não necessariamente retrain |
| Incidente de segurança / prompt injection bem-sucedido | Patch imediato (system prompt + guardrails); root-cause; lessons learned |

---

## 6. Bibliografia Anotada (uma linha por fonte)

**Fontes primárias — Qualidade / CSV**
- ISPE GAMP® 5: A Risk-Based Approach to Compliant GxP Computerized Systems, Second Edition (ISPE, julho/2022) — referência mundial de CSV; Apêndice D11 introduz AI/ML.
- ISPE GAMP® Guide: Artificial Intelligence (ISPE, julho/2025, 290 pp.) — primeiro guia abrangente do setor para validação de IA em GxP.
- ISPE GAMP RDI Good Practice Guide: Data Integrity by Design, 1st Ed., outubro/2020 — Apêndice S1 sobre ML em data integrity.
- FDA, Computer Software Assurance for Production and Quality System Software, Final Guidance, 24/set/2025 (atualizado 03/fev/2026) — pivot CSV → CSA.
- FDA, General Principles of Software Validation (1997/2002) — base histórica; Seção 6 substituída pela CSA.
- EMA/CHMP/CVMP/83833/2023, Reflection paper on the use of Artificial Intelligence in the medicinal product lifecycle, final 9/set/2024 — visão EMA cobrindo todo o ciclo do medicamento.
- EU GMP Annex 11 (atual) + draft Annex 22 (em desenvolvimento) — sistemas computadorizados em GMP UE.
- PIC/S Annex 11 (revisão 2022) — risk-based em sistemas computadorizados; mundialmente referenciado por inspetorias.

**Fontes primárias — IA em saúde**
- FDA Draft Guidance: Considerations for the Use of Artificial Intelligence to Support Regulatory Decision-Making for Drug and Biological Products, Docket FDA-2024-D-4689, 6/jan/2025 — framework de 7 passos para credibilidade (baseado em ASME V&V40).
- FDA Final Guidance: Marketing Submission Recommendations for a Predetermined Change Control Plan for Artificial Intelligence-Enabled Device Software Functions, 3/dez/2024 — PCCP final para dispositivos AI.
- FDA Draft Guidance: AI-Enabled Device Software Functions — Lifecycle Management and Marketing Submission Recommendations, janeiro/2025.
- FDA, AI/ML SaMD Action Plan, janeiro/2021 — plano histórico.
- FDA/Health Canada/MHRA, Good Machine Learning Practice for Medical Device Development — Guiding Principles, 27/out/2021 — os 10 princípios fundadores.
- FDA/Health Canada/MHRA, Transparency for ML-Enabled Medical Devices — Guiding Principles, junho/2024.
- FDA/Health Canada/MHRA, Predetermined Change Control Plans for ML-Enabled Medical Devices — Guiding Principles, outubro/2023.
- IMDRF/AIMD WG/N88 e N81, janeiro/2025 — GMLP internacional e characterization de software médico.
- MHRA, Software and AI as a Medical Device Change Programme Roadmap (out/2022; revisões jun/2024 e dez/2024).
- WHO, Ethics and governance of artificial intelligence for health: Guidance on large multi-modal models, 18/jan/2024 — 40+ recomendações para LMMs em saúde.
- WHO, Ethics and governance of AI for health (2021) — guidance original com 6 princípios.
- ICH E6(R3), Good Clinical Practice, janeiro/2025 — GCP revisado, media-neutral.
- ASME V&V40-2018 — Assessing Credibility of Computational Modeling through Verification and Validation: Application to Medical Device — base conceitual do framework de credibilidade da FDA.

**Fontes primárias — Governança e risco de IA**
- NIST AI 100-1, Artificial Intelligence Risk Management Framework (AI RMF 1.0), janeiro/2023 — funções Govern/Map/Measure/Manage.
- NIST AI 600-1, Generative AI Profile, 26/jul/2024 — 12 categorias de risco GenAI; mais de 200 ações sugeridas.
- ISO/IEC 42001:2023 — AI Management System (AIMS), certificável (dez/2023).
- ISO/IEC 23894:2023 — AI risk management guidance.
- ISO/IEC 22989:2022 — AI concepts and terminology.
- ISO/IEC TR 24027:2021 — Bias in AI systems.
- Regulamento (UE) 2024/1689 — EU AI Act, em vigor 1/ago/2024.
- OWASP Top 10 for LLM Applications 2025 (OWASP GenAI Security Project, 2024) — taxonomia de risco técnico para LLMs.

**Fontes Brasil**
- ANVISA, Comunicado de 8/nov/2024 (uso interno de IA para análise de qualificação de impurezas).
- ANVISA RDC 53/2015; IN 258/2023 — impurezas em medicamentos.
- ANVISA RDC 657/2022 — software como dispositivo médico (SaMD).
- ANVISA RDC 658/2022 — Boas Práticas de Fabricação de Medicamentos.
- Lei 13.709/2018 (LGPD).
- PL 2338/2023 — Marco Legal da IA no Brasil (em tramitação).

**Fontes técnicas / acadêmicas**
- Mitchell et al., "Model Cards for Model Reporting" (FAT* 2019) — framework de documentação de modelo.
- Gebru et al., "Datasheets for Datasets" (CACM 2021) — framework de documentação de dataset.
- Es et al., Ragas: Automated Evaluation of Retrieval Augmented Generation (2023+) — métricas de RAG.
- Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS 2023) — base de LLM-as-judge.
- Shi et al., "Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge" (arXiv:2406.07791, jun/2024).
- Saito et al., "Verbosity bias in preference labeling by large language models" (arXiv:2310.10076, 2023).
- Panickssery et al., "LLM evaluators recognize and favor their own generations" (NeurIPS 2024, arXiv:2404.13076) — self-preference bias.

---

## 7. Lacunas de Conhecimento e Pontos em Disputa

### 7.1 Lacunas regulatórias (o que ainda falta)
- **Thresholds quantitativos**: nenhuma autoridade publicou cortes obrigatórios para hallucination rate, faithfulness, ou drift em uso GxP. Cada companhia define sua tolerância e justifica.
- **Validação de prompts**: nem GAMP 5 2ª Ed., nem o GAMP AI Guide 2025, nem FDA/EMA estabeleceram doutrina clara sobre o status regulatório dos prompts (configuração? código? procedimento operacional?).
- **Validação de RAG corpus**: documentos indexados em RAG são "dados de produção" ou "configuração"? Mudança de corpus é mudança controlada? Prática varia.
- **Sistemas multi-agente e agentes autônomos**: NIST 600-1 e EU AI Act foram concebidos para LLMs em uso conversacional. Agentes que invocam ferramentas e executam ações ainda não têm framework consolidado (existe um draft "Agentic Profile" da Cloud Security Alliance / NIST community, mas não oficial).
- **Brasil**: nenhuma RDC ou guia específico ANVISA para IA em manufatura/QC farmacêutico. PL 2338/2023 ainda em tramitação. Empresas brasileiras dependem de framework internacional (GAMP, FDA, EMA) e LGPD.

### 7.2 Divergências entre fontes
- **Encaixe GAMP 5 de IA generativa**: ISPE 2025 sugere categorização axial separada (Model Categories §22.4); parte da indústria continua usando Cat 5 por padrão. Sem consenso.
- **EU AI Act e P&D farmacêutico**: EFPIA argumenta que a maior parte do uso de IA em P&D não é high-risk; reguladores europeus ainda não emitiram posição definitiva. Aplicação faseada vai esclarecer.
- **Black-box vs. explainability**: EMA aceita black-box "em certos casos"; FDA insiste em credibilidade para o COU (não necessariamente explainability); WHO 2024 enfatiza transparência. Diferentes pesos.
- **CSA aplicabilidade**: formalmente FDA CSA cobre 21 CFR 820.70(i) (dispositivos). Indústria de medicamentos aplica por analogia. Não endossado explicitamente para GMP de medicamentos.
- **LLM-as-judge como evidência regulatória primária**: literatura técnica diverge; nenhum regulador endossou ou proibiu formalmente. Status prático: triagem aceitável, decisão crítica precisa humano.

### 7.3 Áreas onde a pesquisa avança rapidamente
- Confidence calibration em LLMs (uncertainty quantification).
- Robustness contra prompt injection em arquiteturas estruturadas (system/user/data com isolamento criptográfico).
- Métricas de qualidade do "Human-AI team" como conjunto.
- Federated learning e privacy-preserving ML em farma.
- IA generativa em manufatura PAT (Process Analytical Technology) e in-line release.
- Frameworks específicos para sistemas agentic.

### 7.4 Riscos sistêmicos a monitorar
- **Vendor concentration**: dependência de poucos provedores de modelo fundacional cria risco sistêmico semelhante ao de cloud hyperscalers em compliance.
- **Silent model updates**: providers podem atualizar modelos sem aviso adequado, invalidando a validação efetuada — questão contratual e técnica não resolvida na indústria.
- **AI-on-AI auditing**: tendência de delegar a auditoria de IA para outra IA — multiplica modos de falha e cria dependências circulares; ainda sem regulamentação.
- **Workforce literacy gap**: o EU AI Act art. 4 já exige AI literacy desde 2/fev/2025; muitas organizações não têm program formal — gap de conformidade real.

---

**Status do documento**: válido em 22/maio/2026. Recomenda-se revisão semestral pela natureza emergente do tema. Diferenças entre fontes foram preservadas em vez de uniformizadas — pontos marcados [EM DISPUTA] devem ser revisitados a cada release de guidance regulatório.