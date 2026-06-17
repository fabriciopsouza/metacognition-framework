# Base de Conhecimento — Desenvolvimento de Projetos com Agentes de IA: Spec-Driven, Orquestração de Subagentes, Skills e Memória

> Material em PT-BR para (1) consulta de referência, (2) estudo conceitual e (3) treinamento de equipe. Foco em método transferível, não em uma stack específica. Vigência das fontes: 2023–2026; campo em rápida evolução.

---

## 1. Sumário Executivo

Desenvolvimento de software com agentes de IA está convergindo, em 2024–2026, para uma disciplina com três pilares: **(a) spec-driven development (SDD)** — a especificação como fonte da verdade que gera o código; **(b) context engineering** — curadoria deliberada dos tokens que entram na janela de contexto do LLM; e **(c) orquestração agêntica** — decomposição do trabalho em agentes especializados (orchestrator–worker, pipelines sequenciais, paralelização etc.), com **skills reutilizáveis** e **memória persistente** como mecanismos de capitalização do conhecimento. O fio condutor que une os três é uma observação empírica robusta: **a qualidade do contexto presente no momento da inferência determina mais a qualidade do agente do que a inteligência bruta do modelo**.

Por que isso funciona? Três fenômenos bem documentados sustentam o método:

1. **Context rot** (Chroma, jul/2025): em 18 modelos de fronteira testados, a acurácia degrada **conforme o número de tokens de entrada cresce**, mesmo bem antes do limite duro da janela — o que torna "contextos enxutos" uma alavanca de qualidade e custo, não um luxo.
2. **Lost-in-the-middle** (Liu et al., TACL 2024): LLMs recuperam melhor informação posicionada no início ou no fim do contexto e degradam significativamente no meio — o que justifica decomposição e isolamento.
3. **Propagação composta de erro**: erros pequenos em cada turno se compõem multiplicativamente em tarefas longas; isolar contexto por subtarefa quebra essa cadeia.

A consequência prática: **escrever uma boa spec antes de gerar código**, **isolar contexto em subagentes** com janelas próprias e **persistir conhecimento em skills e memória estruturada** rende ganhos mensuráveis em qualidade. A Anthropic, em *How we built our multi-agent research system* (jun/2025), reporta: *"We found that a multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval"* — medido sobre BrowseComp, com uso de tokens explicando ~80% da variância de performance. Porém, no mesmo texto a Anthropic é explícita sobre o custo: o sistema multi-agente consome cerca de **15× mais tokens** que um chat equivalente. Multi-agente não é gratuito.

A literatura também não é unânime. Cognition AI (criadores de Devin) publicou em junho/2025 "Don't Build Multi-Agents", argumentando que paralelismo ingênuo cria "decisões implícitas conflitantes" e fragilidade — posição que eles próprios refinaram em "Multi-Agents: What's Actually Working" (mai/2026): multi-agente funciona quando **escritas ficam single-threaded** e múltiplas inteligências contribuem apenas como leitura. A síntese honesta é: **multi-agente para breadth-first (pesquisa, exploração paralela); single-thread para deep-and-narrow (coding, raciocínio coerente longo)**.

Sobre produtividade real, **separe evidência de marketing**. O RCT do METR (Becker, Rush, Barnes, Rein; arXiv 2507.09089, jul/2025) com **16 desenvolvedores open-source com média de 5 anos de experiência nos próprios projetos, completando 246 tarefas entre fev e jun/2025 usando principalmente Cursor Pro e Claude 3.5/3.7 Sonnet** mostrou que ferramentas de IA do início de 2025 **aumentaram em 19% o tempo de tarefa**. Os participantes haviam estimado, *antes* do estudo, uma aceleração de **24%**; *após* completarem o estudo, ainda estimaram **20%** de aceleração — gap de 39 a 43 pontos entre percepção e realidade. Já o **DORA Report 2025** (Google Cloud, n≈5.000) reverteu o sinal de 2024 e encontrou **relação positiva entre adoção de IA e throughput de entrega e desempenho de produto**, mas **persistente relação negativa com estabilidade** — IA acelera, mas acelera contra gargalos a jusante (review, testes, deploy). Tanto METR quanto DORA convergem para a mesma conclusão metodológica: **o sistema técnico e cultural ao redor da IA determina o sinal do ROI**.

Recomendação central: trate a adoção como **transformação organizacional**, não como ferramenta. Adote SDD para greenfield e legacy modernization; isole contexto em subagentes para tarefas decomponíveis; padronize skills como código revisável e versionado; meça com avaliações end-to-end e LLM-as-judge; e integre tudo ao seu framework próprio de decomposição, classificação de confiança e rastreabilidade — porque governança e auditabilidade são exatamente onde o método agêntico precisa ser mais forte.

---

## 2. Glossário de Termos Essenciais

- **Agente (agentic system)**: sistema em que um LLM dirige dinamicamente o próprio processo e o uso de ferramentas (Anthropic, *Building Effective Agents*, dez/2024). Contraste: **workflow**, em que LLM e ferramentas seguem caminhos de código predefinidos.
- **Spec-Driven Development (SDD)**: metodologia que coloca a especificação no centro; código deixa de ser fonte da verdade e passa a ser saída regenerável da spec (GitHub Spec Kit; Amazon Kiro).
- **Context Engineering**: "conjunto de estratégias para curar e manter o conjunto ótimo de tokens (informação) durante a inferência do LLM" (Anthropic, *Effective Context Engineering for AI Agents*, set/2025).
- **Context Window**: o limite finito de tokens que o modelo "vê" em uma chamada.
- **Context Rot**: degradação medida da qualidade do output conforme o input cresce, mesmo abaixo do limite da janela (Chroma, jul/2025).
- **Lost-in-the-Middle**: viés posicional pelo qual modelos recuperam melhor info no início/fim que no meio do contexto (Liu et al., TACL 2024).
- **Orchestrator-Worker (Lead-Subagent)**: padrão em que um agente "líder" planeja, decompõe e delega para subagentes especializados que rodam em contextos isolados (Anthropic Multi-Agent Research System).
- **Subagente**: instância de agente separada, com contexto novo (fresh), prompt próprio e ferramentas restritas, invocada pelo agente principal (Claude Agent SDK).
- **Skill (Agent Skill)**: pasta com `SKILL.md` (metadados + instruções) e recursos opcionais, carregada dinamicamente pelo agente via *progressive disclosure* (Anthropic, *Equipping Agents for the Real World with Agent Skills*, 2025).
- **Memória persistente**: estado externalizado ao contexto (arquivos, KV-store, notes) que sobrevive entre turnos e sessões.
- **MCP (Model Context Protocol)**: padrão aberto introduzido pela Anthropic (nov/2024) para conectar agentes a ferramentas e fontes de dados via cliente-servidor; adotado por OpenAI, Google e Microsoft.
- **EARS (Easy Approach to Requirements Syntax)**: notação de Mavin et al. (Rolls-Royce, 2009) com cinco padrões (Ubiquitous, State-driven WHILE, Event-driven WHEN, Optional WHERE, Unwanted IF/THEN) usada por Kiro para acceptance criteria.
- **Compaction**: técnica de resumir conversa próxima do limite do contexto para reiniciar com sumário de alta fidelidade (Anthropic).
- **LLM-as-Judge**: padrão de avaliação em que um modelo pontua saídas de outro contra critérios em linguagem natural.
- **KV-Cache hit rate**: métrica de eficiência apontada pela Manus como "North Star" para agentes em produção (mantém prefixo de contexto estável).
- **Vibe coding**: termo coloquial para gerar código a partir de prompts soltos, sem spec; contrasta com SDD.

---

## 3. Definições e Origem dos Termos-Chave

### 3.1 Spec-Driven Development (SDD)

O conceito reivindica que **"specifications don't serve code—code serves specifications"** (`spec-kit/spec-driven.md`, GitHub). Tem três raízes: (i) PRDs e design docs tradicionais; (ii) TDD/BDD (especificação executável via testes/cenários); (iii) a constatação prática de que LLMs são "pair programmers literais" e precisam de instruções não ambíguas (GitHub Blog, set/2025). Implementações canônicas em 2025–2026:

- **GitHub Spec Kit** (`github/spec-kit`, set/2025): toolkit open-source com fluxo `/specify → /plan → /tasks → /implement`, *constitution* (princípios não negociáveis), *presets* para regulação/traceabilidade, suporte a 30+ agentes (Copilot, Claude Code, Gemini CLI, Cursor, Kiro etc.). **[CONSOLIDADO]** em 2026 como referência metodológica; ferramenta ainda em evolução rápida.
- **Amazon Kiro** (jul/2025, AWS): IDE fork de VS Code com workflow Requirements → Design → Tasks; gera três arquivos canônicos (kiro.dev/docs/specs/): *"requirements.md … Captures user stories, acceptance criteria, or bug analysis in structured notation; design.md … Documents technical architecture, sequence diagrams, and implementation considerations; tasks.md … Provides a detailed implementation plan with discrete, trackable tasks"*. Também usa `steering/` (contexto persistente) e `hooks/` (gatilhos). Substitui o Amazon Q Developer IDE plugin. **[EMERGENTE]**; trade-off relatado: "spec tax" — overhead alto em tarefas pequenas.
- **BMAD Method**, **Autospec**, e presets de SDD para Claude Code e Cursor — ecossistema em formação.

### 3.2 Agentic Development

A definição operacional vem da Anthropic (*Building Effective Agents*, dez/2024): **agentes** são sistemas em que LLMs "dirigem dinamicamente seus próprios processos e uso de ferramentas". O ensaio formaliza cinco padrões composicionais consolidados: **prompt chaining, routing, parallelization (sectioning + voting), orchestrator-workers, evaluator-optimizer**. **[CONSOLIDADO]** — é a referência mais citada da indústria.

### 3.3 Context Engineering

Cunhado e formalizado pela Anthropic em set/2025 (*Effective Context Engineering for AI Agents*): "progressão natural do prompt engineering" focada em **gerir o estado completo do contexto** (system prompts, ferramentas, MCP, histórico, memória). A Manus AI (Yichao "Peak" Ji, jul/2025) chegou independentemente à mesma conclusão: *"rebuilt our agent framework four times… If model progress is the rising tide, we want Manus to be the boat, not the pillar stuck to the seabed."* **[CONSOLIDADO]** como termo; práticas específicas ainda **[EMERGENTE]**.

---

## 4. POR QUE FUNCIONA — O Núcleo Teórico (com Analogias Didáticas)

Esta é a seção mais importante para entender o método como transferível. São quatro fenômenos que, juntos, justificam *toda* a arquitetura proposta.

### 4.1 Contexto é um Recurso Finito com Retornos Decrescentes

**Analogia: memória de trabalho humana.** Você consegue manter ~7 itens na cabeça simultaneamente. Acima disso, esquece, confunde, ou raciocina mais devagar. LLMs têm o mesmo problema, agravado por uma característica arquitetural: na atenção do transformer, **cada token atende a todos os outros**, criando relações O(n²). A 10 mil tokens são 100 milhões de relações; a 100 mil, 10 bilhões. A Anthropic chama isso de **"attention budget"**: "o problema de engenharia é otimizar a utilidade desses tokens contra as restrições inerentes dos LLMs" (set/2025).

### 4.2 Context Rot — A Evidência Empírica

O estudo da **Chroma Research** (Hong, Troynikov, Huber, jul/2025) testou **18 modelos de fronteira** (incluindo GPT-4.1, Claude 4, Gemini 2.5, Qwen3) em variantes de needle-in-a-haystack e LongMemEval, mostrando que:

- **Todos** degradam conforme o input cresce — não alguns, **todos**.
- A degradação começa **bem antes** do limite da janela; um modelo com janela de 200K pode degradar significativamente já em 50K.
- Similaridade semântica needle-haystack, estrutura do haystack e até o "fluxo lógico" do contexto influenciam o resultado.
- Em LongMemEval, modelos performaram **pior** com histórico completo do que com excertos relevantes.

**Implicação:** "capacidade da janela" é a métrica errada; o que importa é **signal-to-noise ratio**. Esta é a base empírica que dispensa "jogar tudo no prompt".

### 4.3 Lost-in-the-Middle — O Viés Posicional

O paper de **Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni, Liang** (arXiv 2307.03172; publicado em TACL 2024) mostrou que em multi-document QA e key-value retrieval, "performance é frequentemente mais alta quando a informação relevante está no início ou no final do contexto, e degrada significativamente quando o modelo precisa acessá-la no meio". Confirmado por trabalhos posteriores (Found in the Middle, arXiv 2406.16008). **Implicação:** ordem importa; "empilhar contexto" sem estrutura coloca informação crítica exatamente no ponto mais fraco do modelo.

### 4.4 Propagação Composta de Erro

Em uma tarefa de N turnos, se cada turno tem 95% de acurácia, a probabilidade de tudo dar certo é 0.95^N. Em 20 turnos cai para 36%. Por isso a Anthropic enfatiza tarefas com "ciclos de feedback claros" e a Cognition argumenta que **passar todo o histórico** entre agentes é preferível a fragmentar contexto — quando o trabalho é deep-and-narrow.

### 4.5 A Síntese: Por Que Decomposição e Isolamento Ajudam

Combinando os quatro fenômenos: **se o contexto é finito e degradante, e se erros se compõem, então quebrar a tarefa em subtarefas com contextos curtos, frescos e focados é uma estratégia ótima** — desde que a decomposição seja válida (subtarefas independentes ou pouco acopladas). É exatamente esta a hipótese que o sistema multi-agente da Anthropic confirma com 90,2% de melhoria sobre single-agent em pesquisa breadth-first (BrowseComp eval interno). **Analogia: equipe de pesquisadores.** Em vez de um pesquisador tentando manter 50 papers na cabeça (e esquecendo metade), você tem um líder que distribui 5 papers para cada um de 10 assistentes, cada um devolve um briefing curto, e o líder sintetiza. Cada assistente trabalhou com contexto enxuto; o líder nunca viu os 50 papers — viu 10 resumos.

**Mas há um custo:** o sistema multi-agente da Anthropic consome **~15× mais tokens** que um chat; agentes single em geral consomem ~4× mais que chat. Por isso multi-agente só compensa quando **valor da tarefa > custo do token**.

---

## 5. COMO FUNCIONA — Mecânica Operacional

### 5.1 Especificações Atômicas (Spec-Driven)

**Estrutura canônica (síntese de GitHub Spec Kit + Kiro):**

1. **Constitution / Steering** — princípios não negociáveis do projeto (segurança, stack permitida, padrões de código, restrições regulatórias). Persistente entre features.
2. **Requirements** — *o quê* e *para quê*, sem decisões de implementação. Em Kiro, usa-se **EARS notation** (Mavin et al., 2009). Conforme a referência canônica (alistairmavin.com/ears/), uma requirement EARS *"must have: Zero or many preconditions; Zero or one trigger; One system name; One or many system responses."* Os cinco padrões com exemplos verbatim:
   - **Ubiquitous** (sem keyword, sempre ativo): *"The mobile phone shall have a mass of less than XX grams."*
   - **State-driven (WHILE)**: *"While there is no card in the ATM, the ATM shall display 'insert card to begin'."*
   - **Event-driven (WHEN)**: *"When 'mute' is selected, the laptop shall suppress all audio output."*
   - **Optional feature (WHERE)**: *"Where the car has a sunroof, the car shall have a sunroof control panel on the driver door."*
   - **Unwanted behaviour (IF/THEN)**: *"If an invalid credit card number is entered, then the website shall display 'please re-enter credit card details'."*
   - **Complex** (combinações): *"While the aircraft is on ground, when reverse thrust is commanded, the engine control system shall enable reverse thrust."*
3. **Design / Plan** — arquitetura, sequence diagrams, modelo de dados, decisões técnicas.
4. **Tasks** — lista discreta, ordenada, rastreável de tarefas implementáveis.

**Critérios de uma boa spec:**

- **Testável** (cada requirement deveria gerar pelo menos um teste).
- **Não-ambígua** (EARS força isso).
- **Granularidade certa** — nem detalhe excessivo (engessa), nem genérico (gera código genérico). A Anthropic chama isso de "the right altitude" (set/2025): "specific enough to guide behavior effectively, yet flexible enough to provide the model with strong heuristics".

**Antipatterns frequentes:**

- *Implementation in disguise*: spec que já dita classes, métodos, libs — anula o ganho de regenerabilidade.
- *Wall of text*: dezenas de páginas sem hierarquia — context rot in disguise.
- *Stale spec*: código evolui, spec não. Em SDD verdadeiro, "manter o software significa evoluir a spec" (Spec Kit).
- *Spec tax* (Kiro): em tarefas pequenas, o overhead da spec custa mais do que vibe coding entregaria. Relatos no Hacker News mostram devs abandonando SDD para utilitários triviais.

### 5.2 Orquestração de Subagentes

**Padrões consolidados (síntese Anthropic + Microsoft Agent Framework):**

| Padrão | Quando usar | Quando NÃO usar |
|---|---|---|
| **Prompt Chaining** (sequencial) | Pipeline determinístico, output de um é input do próximo | Latência crítica; etapas paralelizáveis |
| **Routing** | Inputs heterogêneos com handlers especializados | Output requer múltiplos especialistas simultâneos |
| **Parallelization (Sectioning)** | Subtarefas verdadeiramente independentes | Alta interdependência entre etapas |
| **Parallelization (Voting)** | Alta-confiança em decisões críticas (revisão de segurança, classificação) | Custo por token é restrição dura |
| **Orchestrator-Workers** | Tarefa breadth-first, decomposição não conhecida a priori | Tarefas deep-and-narrow (coding sequencial) |
| **Evaluator-Optimizer** | Qualidade melhora com iteração e critérios são claros | Sem critérios mensuráveis; risco de loop infinito sem cap |
| **Handoff** (Microsoft) | Controle passa entre especialistas com base em contexto | Decisões precisam de visão global |
| **Group Chat** (Microsoft) | Brainstorm, consenso entre roles | Tarefas com ordem rígida |
| **Magentic (Magentic-One)** | Plano dinâmico criado por agente-gerente | Custo imprevisível; cap difícil |

**Mecânica do isolamento de contexto (Claude Agent SDK):**

- Subagente é definido com `description`, `prompt`, `tools` restritas, opcionalmente `model` próprio.
- Contexto do subagente começa **fresh** — pai e filho só se comunicam pela string do tool `Agent` e pelo retorno final.
- Subagentes **não** podem invocar subagentes (no SDK Claude, por design — evita explosão).
- Trade-off chave: o que isolar reduz context rot mas elimina visão lateral; deve-se passar no prompt do subagente **todos** os file paths, mensagens de erro e decisões que ele precisa.

**Hand-off e progress tracking:**

- Em produção, persistir estado em filesystem/memória externa (a Manus trata o filesystem como "memória estruturada" do agente).
- Para tarefas longas, **compaction** (resumir conversa) e **structured note-taking** (`/memories`) — Anthropic Cookbook documenta as três técnicas: compaction, tool-result clearing e memory.

**O debate single vs multi (jun/2025):**

- **Cognition** ("Don't Build Multi-Agents", Walden Yan, jun/2025): paralelizar escritas leva a "decisões implícitas em conflito" e fragilidade; prefira agente single-threaded passando histórico completo.
- **Anthropic** (mesma semana): multi-agente entrega 90,2% melhor para pesquisa breadth-first.
- **Resolução** (Cognition, mai/2026, "Multi-Agents: What's Actually Working"): multi-agente funciona se **escritas permanecem single-threaded** e múltiplos agentes contribuem inteligência apenas como leitura/análise paralela.
- **Conclusão prática**: paralelize **leitura/exploração**; mantenha **escrita coerente** em uma thread só.

### 5.3 Skills / Padrões Reutilizáveis

**O que são:** pastas com `SKILL.md` (frontmatter YAML com `name` e `description`) e recursos opcionais (scripts, references, templates). Anthropic abriu o padrão como `agentskills.io`; Claude Code, Claude.ai e API consomem o mesmo formato.

**Progressive disclosure (chave conceitual):**

1. **Metadata** (`name` + `description`) — pré-carregado no system prompt; alguns bytes.
2. **Corpo do SKILL.md** — carregado apenas quando o modelo decide ativar a skill (custo médio).
3. **Arquivos referenciados / scripts** — carregados sob demanda (custo só quando necessário).

Isso resolve o trade-off entre "ter muita capability disponível" e "não inchar o contexto". É a operacionalização do princípio de signal-to-noise.

**Versionamento e manutenção:**

- Trate skills como código: versionadas em git, com PRs revisados, testes (evals) e changelog.
- O repositório `anthropics/skills` publica 17 skills oficiais como exemplo (document creation, code review, MCP server creation etc.).
- Evite "skill sprawl": muitas skills com descrições parecidas confundem o modelo na seleção. Auditoria periódica é necessária.

**Quando criar uma skill (heurística):**

- Você se pegou repetindo o **mesmo** prompt 3+ vezes em projetos diferentes.
- Há um *workflow* domínio-específico que envolve **passos determinísticos** (sortear, validar, formatar).
- Há padrão da empresa (branding, compliance, modelos financeiros) que precisa ser aplicado consistentemente.

### 5.4 Memória Persistente e Templates

**Tipos de memória em agentes (síntese):**

- **De curto prazo**: a própria janela de contexto (volátil).
- **Working memory externalizada**: arquivos no filesystem (`/memories`, notes), CLAUDE.md, AGENTS.md, steering files do Kiro. A Manus articula o filesystem como "memória estruturada restorável".
- **De longo prazo / cross-session**: vector stores, KV-stores, bancos de dados, skills.
- **De equipe / organizacional**: presets do Spec Kit, skills compartilhadas, constitution, design system.

**O que persistir (heurística):**

- Decisões arquiteturais e seus *whys* (irreversíveis ou de alto custo).
- Padrões de código e convenções (linting passa por aqui também).
- Glossário de domínio (termos do negócio, siglas).
- Lições aprendidas — incluindo erros (a Manus enfatiza: "deixe stack traces no contexto; modelo aprende vendo o que falhou").
- Modelos/templates de spec, de PR, de design doc.

**O que NÃO persistir:**

- Dados sensíveis sem controle de acesso.
- Saídas intermediárias verbosas (compactar antes).
- Contexto específico de uma única tarefa.

---

## 6. Padrões de Arquitetura e Trade-offs

| Arquitetura | Vantagem | Custo | Falha típica |
|---|---|---|---|
| **Single agent loop** | Coerência máxima, debug simples | Context rot em tarefas longas | Trava em problemas decomponíveis |
| **Pipeline (chain)** | Determinístico, auditável | Sem adaptação dinâmica | Cada etapa é gargalo serial |
| **Orchestrator-Worker hierárquico** | Paralelismo + visão global | ~15× tokens; coordenação não trivial | Sub-agentes spawnados em excesso para queries simples |
| **Hierarchical (orchestrator de orchestrators)** | Tarefas grandes/recursivas | Combinatorial; observabilidade difícil | Loops; custo descontrolado |
| **Group chat / debate** | Diversidade de visões, consenso | Tokens altos; pouco determinístico | Discussão circular sem cap |
| **Handoff (especialistas)** | Especialização clara | Perda de visão global | "Telefone sem fio" se contexto não é passado |
| **Magentic** | Planejamento dinâmico | Custo imprevisível | Plano muda demais; difícil cap-ar |

**Princípio-guia (Anthropic):** "Maintain simplicity. Start with the simplest architecture that could plausibly work; add complexity only when it demonstrably improves outcomes."

---

## 7. Otimização: Produtividade, Custo e Qualidade

### 7.1 O Que Otimizar

1. **Custo por tarefa concluída** (não custo por token).
2. **Latência percebida pelo usuário** (paralelização ajuda).
3. **Taxa de retrabalho** (qualidade real do output).
4. **Estabilidade** (rollback rate, change failure rate).

### 7.2 Alavancas Concretas

- **KV-cache hit rate** (Manus): mantenha prefixos estáveis; não mude prompts de sistema entre turnos; isso reduz drasticamente custo e latência.
- **Modelo certo para cada tarefa**: orchestrator pode ser o modelo mais caro (Opus / equivalente); workers podem ser modelos médios (Sonnet); extração/formatação cabe em modelos pequenos. Análises de custo de terceiros (CloudZero/Amazon Bedrock, 2026) indicam que *"even a basic routing layer based on prompt length and task type drops blended cost per request by 40–60%"* — número que vale tratar como ordem-de-grandeza, não como garantia.
- **Compaction inteligente**: substituir tail do contexto por sumários quando se aproxima do limite.
- **Tool-result clearing**: descartar resultados de ferramentas após uso, preservando apenas o que foi extraído.
- **Just-in-time retrieval**: em vez de RAG up-front pesado, recuperar quando o agente decide precisar.
- **Code execution with MCP** (Anthropic, 2026): em vez de empilhar definições de centenas de tools no prompt, o agente lista o diretório de servidores MCP e lê apenas as definições necessárias — redução de 150K para 2K tokens (~98,7%) no exemplo da Anthropic.

### 7.3 Como MEDIR Ganhos Reais — Honestamente

**Evidência atual, com caveats:**

- **METR (jul/2025)** — RCT com 16 desenvolvedores open-source de média de 5 anos de experiência nos próprios projetos, completando 246 tarefas com Cursor Pro + Claude 3.5/3.7 Sonnet: ferramentas de IA do início de 2025 **aumentaram tempo de tarefa em 19%**. Os devs previam 24% de aceleração antes do estudo e ainda estimaram 20% de aceleração após — gap consistente entre percepção e realidade. **Caveats**: amostra pequena (16); projetos próprios maduros são caso pior para IA; modelos eram do início de 2025; em fev/2026 o METR reportou que estavam mudando o desenho experimental porque devs recusavam participar sem IA, sinalizando viés.
- **DORA 2024** (n>39k): IA associada a aumento de produtividade individual percebida, mas com efeito negativo em estabilidade e throughput.
- **DORA 2025** (n≈5k): reversão parcial. No anúncio oficial (cloud.google.com): *"Unlike last year, we observe a positive relationship between AI adoption on both software delivery throughput and product performance. … However, AI adoption does continue to have a negative relationship with software delivery stability. This confirms our central theory — AI accelerates software development, but that acceleration can expose weaknesses downstream."* 90% dos respondentes usam IA no trabalho; mediana de uso é 2h/dia.
- **DORA AI Capabilities Model** (Storer & DeBellis, Google Cloud, set/2025): sete capacidades organizacionais que **amplificam** o impacto positivo da IA — citadas verbatim:
  1. **Clear and communicated AI stance** — *"Your organization's position on AI-assisted tools must be clear and well-communicated."*
  2. **Healthy data ecosystems** — *"high-quality, easily accessible, and unified internal data, substantially amplifies the positive influence of AI adoption."*
  3. **AI-accessible internal data** — *"Connecting AI tools to internal data sources boosts their impact on individual effectiveness and code quality."*
  4. **Strong version control practices** — *"frequent commits amplify AI's positive influence on individual effectiveness, while the frequent use of rollback features boosts the performance of AI-assisted teams."*
  5. **Working in small batches** — *"amplifies the positive influence of AI on product performance and reduces friction."*
  6. **User-centric focus** — *"in the absence of a user-centric focus, AI adoption can have a negative impact on team performance."*
  7. **Quality internal platforms** — *"In organizations with quality internal platforms, AI's positive influence on organizational performance is amplified."*
  
  Sem elas, ganhos de produtividade individual não se convertem em performance organizacional — e podem virar instabilidade.

**Métricas que valem a pena coletar no seu projeto:**

- *Pré*: tempo de baseline em tarefa típica sem IA.
- *Durante*: tempo gasto em prompt, tempo gasto em review, tokens consumidos por tarefa, taxa de iteração necessária.
- *Pós*: defect rate em produção, MTTR, % de PRs merged sem revisão (proxy de risco).
- *Avaliação automática*: LLM-as-judge para qualidade de output (faithfulness, relevance, completeness); evals end-state para agentes (chegou ao objetivo? quantos passos? quantas tool calls erradas?).

### 7.4 Marketing vs. Evidência

Distinguindo:

- **Claims promocionais frequentes**: "10× produtividade", "agentes autônomos resolvem tudo", "vibe coding entrega produção".
- **Claims com evidência primária**: 90,2% no eval interno da Anthropic (uma avaliação, um domínio, contexto bem definido); 15× tokens (mesmo paper, número honesto); 80% da variância de performance explicada por uso de tokens (BrowseComp, mesma fonte).
- **Conflitos reais**: METR (-19%) vs. DORA 2025 (+) — provavelmente refletem populações diferentes (devs experientes em codebases maduros vs. amostra ampla) e gerações de modelos diferentes.

---

## 8. Riscos, Limites e Quando NÃO Usar

### 8.1 Onde o Método Falha

- **Tarefas com alta interdependência** (Anthropic é explícita): "domains that require all agents to share the same context or involve many dependencies between agents are not a good fit for multi-agent systems today. Most coding tasks involve [such dependencies]."
- **Decisões irreversíveis sem checkpoint humano**: enviar e-mail, alterar produção, mover dinheiro. Anthropic: "prefer reversible actions over irreversible ones".
- **Domínios mal especificados**: se você não consegue escrever a spec, o agente também não.
- **Tarefas pequenas**: spec tax > ganho. Vibe coding pode ser superior para utilitários efêmeros.

### 8.2 Débito Técnico Específico de Agentes

- **Skill sprawl** sem governança vira "prompt sprawl 2.0".
- **PRs gigantes e gargalo de review**: a telemetria do Faros AI Engineering Report 2026 (22.000 desenvolvedores) reporta — diretamente da Faros, não do DORA — *"Pull request size is up 51.3% … Median time in PR review is up 441% … and 31% more PRs are merging with no review at all"*. O DORA 2025 confirma a direção (instabilidade ↑) mas não publica esses percentuais específicos.
- **Drift de spec**: spec deixa de refletir código se não há disciplina de regenerar.
- **Custo escondido**: agentes consomem ordens-de-grandeza mais tokens que chats simples (Anthropic: ~4× para agentes single, ~15× para multi-agente vs. chat; análises de 2026 como Gartner citam multiplicadores de 5–30× para workloads agênticos vs. chatbots). O paper "AI Tool Use and Productivity" do Stanford Digital Economy Lab (Brynjolfsson et al., maio/2026) caracteriza tarefas agênticas como *"uniquely expensive, consuming 1000× more tokens than code reasoning and code chat"* — concentradas em re-leitura acumulativa de contexto a cada ação. *(Caveat: cifras específicas como "62% do gasto em re-envio de contexto" circulam em derivados secundários e não foram confirmadas em fonte primária; trate como hipótese, não como fato.)* A métrica certa é custo por tarefa concluída, não custo por chamada.

### 8.3 Governança, Auditoria e Setor Regulado

- **Logs por agente e por subagente**: trace completo (input, tools chamadas, outputs, model versions) — essencial para auditoria e RCA.
- **Human-in-the-loop em pontos de irreversibilidade**: Kiro adicionou confirmações em operações que tocam infraestrutura viva após incidente reportado.
- **Permissões e sandboxing**: subagentes com `allowedTools` mínimo necessário (princípio de menor privilégio).
- **MCP authorization**: OAuth 2.1 / PRM para tools com side-effects.
- **Data residency e ZDR**: Anthropic explicita que Agent Skills não estão sob ZDR — implicações de compliance precisam ser checadas.
- **Versionamento de spec, skills, prompts, modelos**: tudo em git, com SBOM-equivalente para componentes de IA.
- **Avaliações pré-deploy**: evals automatizados com critérios da regulação (LGPD, BCB, etc. conforme o setor).
- **Reprodutibilidade limitada**: comportamento não-determinístico entre runs é um fato; Anthropic recomenda "full observability" como compensação.

### 8.4 Quando NÃO Usar SDD/Multi-Agente

- Bug fix triviais (1 arquivo, < 30 min).
- Exploração rápida de hipótese (vibe coding é mais barato).
- Tarefas em que o custo de spec não amortiza (cap pequeno de uso).
- Codebases legadas sem testes — automação amplifica risco; reforce testes antes.

---

## 9. Adoção e Treinamento de Equipe

### 9.1 Níveis de Maturidade (síntese Gartner + DORA)

Baseado no modelo Gartner (Awareness → Active → Operational → Systemic → Transformational) adaptado para agentic development:

| Nível | Estado | Sinais | Próximo passo |
|---|---|---|---|
| **0. Awareness** | Pessoas experimentam ChatGPT/Copilot individualmente | Sem política, sem padrões, sem métricas | Definir posicionamento e ferramentas permitidas |
| **1. Active** | Pilotos isolados; vibe coding | Algumas pessoas produtivas; outras céticas | Padronizar prompts e introduzir spec leves |
| **2. Operational** | SDD adotado em features novas; skills compartilhadas começam | CLAUDE.md/AGENTS.md ou equivalente em uso; métricas básicas | Introduzir subagentes; evals automatizados |
| **3. Systemic** | Orquestração agêntica em pipelines de produção; skills como código | DORA AI capabilities maduras; ROI mensurado | Otimizar custo/latência; tooling interno |
| **4. Transformational** | IA reorganiza o sistema de trabalho; humanos fazem review, design, governance | Métricas de outcome (produto, cliente) ligadas a IA | Inovação contínua; contribuir para ecosistema |

Gartner reporta (jun/2025, n=432): organizações de alta maturidade pontuam 4.2–4.5; baixa, 1.6–2.2. Em alta maturidade, 57% das business units confiam em soluções de IA; em baixa, 14%.

### 9.2 Plano Faseado de Capacitação (12–16 semanas)

**Fase 1 (sem 1–4) — Fundação conceitual:**
- Workshop: por que funciona (context rot, lost-in-the-middle, propagação de erro).
- Leitura guiada: Anthropic *Building Effective Agents* + *Effective Context Engineering*; Cognition vs. Anthropic debate.
- Hands-on: cada dev escreve **uma spec EARS** para uma feature real e gera via Copilot/Claude Code/Cursor.

**Fase 2 (sem 5–8) — Workflow básico:**
- Adoção de spec-driven (Spec Kit ou Kiro) em features novas.
- Criação de constitution/steering compartilhada da equipe.
- Definição de 3–5 skills da equipe (templates, padrões de PR, design system).
- Métricas baseline: tempo, defect rate, tokens/PR.

**Fase 3 (sem 9–12) — Subagentes e orquestração:**
- Primeiro subagente para code-review automatizado (read-only).
- Segundo subagente para test-generation.
- Introdução de LLM-as-judge em CI.
- Revisão de métricas; matar o que não funciona.

**Fase 4 (sem 13–16) — Governance e escala:**
- Catálogo interno de skills versionadas.
- Integração com observabilidade (logs, traces).
- Auditoria de permissões e MCP servers.
- Plano de evolução contínua e treinamento de novos.

### 9.3 Papéis Emergentes

- **Spec author / context engineer**: traduz intenção em spec não-ambígua, mantém constitution.
- **Skill librarian**: cura, versiona e revisa skills da organização.
- **Agent orchestration architect**: decide quando dividir em subagentes, define pipelines.
- **AI evaluations engineer**: dono dos evals automatizados.
- **AI governance lead**: políticas, compliance, auditoria, treinamento.

Estes papéis não exigem necessariamente headcount novo — em equipes pequenas, são *hats* que membros existentes vestem.

### 9.4 Mudança Cultural

- **Code review muda**: revisor humano agora valida intent + spec + diff, não só diff.
- **Specs viram artefato de primeira classe** — entram em PRs, têm donos, têm versões.
- **"Vibe coding" não é vilão**, mas tem lugar restrito: prototipagem e exploração. Produção exige spec.
- **Resistência típica**: devs seniores resistem porque (a) METR é real — eles podem mesmo ser desacelerados no curto prazo; (b) sentem que "spec é overhead"; (c) percebem ameaça à expertise. Tratar com transparência sobre dados (METR vs. DORA) e foco em onde a IA realmente ajuda (boilerplate, testes, exploração de código novo).

### 9.5 Antipadrões na Adoção

- Comprar ferramenta sem método.
- Métricas vaidosas (linhas de código geradas, % de aceitação de sugestões) sem ligação com outcome.
- "Tudo agente": forçar arquitetura agêntica em problemas que são workflow simples.
- Ignorar instabilidade: AI amplifica throughput e amplifica fragilidade; testes e rollback precisam evoluir junto.
- "AI shadow IT": dev usa ferramenta não autorizada com dados sensíveis.

---

## 10. Frameworks de Decisão (Se X, Então Y)

### 10.1 Quando usar SDD vs. Vibe Coding

| Se… | Então… |
|---|---|
| Feature crítica, multi-arquivo, codebase grande | SDD completo |
| Modernização de legado sem docs | SDD para reconstruir intent |
| Time multi-stakeholder com regulação | SDD + constitution + audit trail |
| Protótipo descartável, exploração | Vibe coding |
| Bug fix < 30 min, < 3 arquivos | Vibe coding (com testes) |
| Há padrão recorrente | Skill, não spec ad-hoc |

### 10.2 Quando Isolar em Subagente

| Se… | Então isolar em subagente |
|---|---|
| Subtarefa precisa de tools diferentes do agente principal | Sim |
| Subtarefa polui contexto principal com info irrelevante (search, exploração) | Sim |
| Subtarefa pode rodar em paralelo com outras | Sim, se compensar 15× custo |
| Subtarefa depende fortemente do raciocínio anterior | **Não** — mantenha single-thread |
| Decisão irreversível | **Não** — manter no agente principal com confirmação humana |

### 10.3 Quando Paralelizar

| Se… | Então paralelizar |
|---|---|
| Subtarefas verdadeiramente independentes (busca em fontes diferentes) | Sim (sectioning) |
| Output crítico precisa de checagem cruzada | Sim (voting) |
| Latência é restrição | Sim (se custo permitir) |
| Saídas precisarão ser conciliadas no meio | Não (sequencial ou orchestrator) |
| Tokens são restrição dura | Não |

### 10.4 Quando Criar uma Skill

| Se… | Então skill |
|---|---|
| Mesmo prompt repetido em 3+ contextos | Sim |
| Workflow domínio-específico com passos determinísticos | Sim (com scripts) |
| Padrão organizacional (branding, compliance) | Sim |
| Uma única feature pontual | Não — coloque na spec |
| Conhecimento muda rapidamente | Considere MCP server vivo, não skill estática |

---

## 11. Camada Didática — Analogias e Exemplo End-to-End

### 11.1 Analogias-Chave

- **Contexto = mesa de trabalho.** Cabe pouco; o que está no centro chama atenção; o que está empilhado no canto é esquecido.
- **Agente principal = gerente sênior; subagentes = especialistas.** O gerente decompõe, delega, integra. Cada especialista vê só seu briefing.
- **Skill = SOP (Standard Operating Procedure).** Documento do "como se faz aqui" que qualquer novo membro consegue executar.
- **Spec = contrato.** Define o que entregar; não dita como.
- **Memória externa = pasta de projeto compartilhada.** Onde fica o que sobrevive à reunião.
- **MCP = USB-C para IA.** Padrão universal de conexão a ferramentas.

### 11.2 Exemplo End-to-End (Transferível)

Cenário: equipe precisa adicionar **autenticação multi-fator** a um sistema interno. Aplicação do método:

1. **Constitution** (já existente): "Toda autenticação deve passar por revisão de segurança; logs imutáveis; LGPD: minimização de dados."
2. **Spec (requirements.md):**
   - Ubiquitous: "The system shall support TOTP-based MFA for all admin users."
   - WHEN: "When a user enables MFA, the system shall generate and display a QR code containing the secret per RFC 6238."
   - IF/THEN: "If the user provides an invalid TOTP code 3 times within 5 minutes, then the system shall lock the account for 15 minutes and log the event."
   - WHERE: "Where the user has hardware key registered, the system shall offer WebAuthn as preferred."
3. **Design (design.md):** sequence diagram do enroll e do login, escolha de lib, modelo de dados (tabela `user_mfa`), pontos de log.
4. **Tasks (tasks.md):** 12 tarefas ordenadas, cada uma com critério de aceite e arquivos afetados.
5. **Execução agêntica:**
   - Agente principal lê constitution + spec + design.
   - Subagente "explore" mapeia código existente de auth (read-only).
   - Subagente "implement" gera código tarefa por tarefa (single-thread, escritas coerentes).
   - Subagente "test" gera testes unitários e de integração baseados nos critérios EARS (1 requirement → ≥1 teste).
   - Subagente "security-review" (read-only, com skill `security-checklist`) revisa o diff contra OWASP e a constitution.
   - Humano revê o PR; agente atualiza spec se decisões mudaram.
6. **Memória persistente atualizada:** novo padrão de MFA vira parte da `auth-patterns.skill` para futuras features.

Esse fluxo é **stack-agnóstico**: serve para Python/Django, Java/Spring, Node, Go, Rust — só muda a sintaxe das tasks.

### 11.3 FAQ

**P: Spec não é só waterfall com nome novo?**
R: Não. Em SDD, a spec é **viva, regenerável e iterativa**; ela é editada conforme aprende-se. Spec Kit é explícito: "It's not about waterfall planning."

**P: Se LLMs melhoram, isso tudo não fica obsoleto?**
R: A Anthropic argumenta o oposto: "smarter models require less prescriptive engineering, but treating context as a precious, finite resource will remain central." A arquitetura subjacente do transformer (atenção n²) não muda; context rot continuará existindo.

**P: Preciso de multi-agente para tudo?**
R: Não. A Anthropic explicita: "you should consider adding complexity only when it demonstrably improves outcomes". Comece simples.

**P: Como evitar custo descontrolado?**
R: Token budgets por sessão; routing por modelo (caro só para orchestrator); compaction; tool-result clearing; monitoring por tarefa concluída, não por chamada.

**P: SDD funciona para data/analytics, não só software?**
R: Sim — o método é transferível. Spec descreve transformação de dados, critérios de qualidade, regras de negócio, evals. Já há presets de Spec Kit para data engineering em desenvolvimento na comunidade.

**P: Como integro com minha governança atual?**
R: Veja Seção 12.

**P: O que faço em ambiente air-gapped / sem internet?**
R: MCP servers locais; modelos on-prem (Bedrock, Vertex, Azure OpenAI gov, Anthropic via AWS/Microsoft Foundry); skills em git interno; logs em SIEM local.

**P: Posso adotar isso sem comprar Kiro/Spec Kit/Claude Code?**
R: Sim. O **método** é independente da ferramenta. Você pode implementar com qualquer LLM de fronteira, repositório git, e um padrão de pastas/arquivos. O valor está nas práticas, não no vendor.

---

## 12. Checklist de Integração com Framework Próprio de Governança / Metacognição

Para o profissional que já opera com (a) decomposição de tarefas, (b) classificação de confiança das afirmações, (c) logging/rastreabilidade, (d) workflow incremental:

**Decomposição de tarefas** ↔ **Orchestrator-Worker:**
- [ ] Mapear sua taxonomia de decomposição para padrões Anthropic (chaining, parallelization, orchestrator-worker).
- [ ] Definir threshold: tarefas com X subtarefas independentes ⇒ orchestrator; abaixo ⇒ single-thread.

**Classificação de confiança** ↔ **Evals + LLM-as-judge:**
- [ ] Para cada output do agente, exigir nível de confiança auto-reportado (já está no seu framework).
- [ ] Cross-check com LLM-as-judge independente (modelo diferente) para outputs críticos.
- [ ] Outputs com confiança baixa OU divergência judge↔agente ⇒ human-in-the-loop obrigatório.

**Logging/rastreabilidade** ↔ **Observabilidade agêntica:**
- [ ] Capturar: prompt completo, ferramentas chamadas, parâmetros, retornos, modelo/versão, tokens, latência.
- [ ] Em multi-agente: capturar tree completa (parent → child) com identificadores correlacionados.
- [ ] Persistir specs e suas versões junto com a execução (vincular run a spec_sha).
- [ ] Logs imutáveis para domínio regulado.

**Workflow incremental** ↔ **Spec-driven + iteração:**
- [ ] Cada incremento começa com revisão/edição de spec.
- [ ] Tasks atômicas com critérios EARS-testáveis.
- [ ] Após implementação, atualizar spec se decisões mudaram (anti-drift).
- [ ] Lições aprendidas → skills/constitution.

**Adições recomendadas ao seu framework:**
- [ ] Constitution / steering como artefato versionado.
- [ ] Catálogo de skills da equipe com SLA de manutenção.
- [ ] Política de quando usar subagente vs. single-thread.
- [ ] Métricas de outcome (não só de output).
- [ ] DORA AI Capabilities como checklist organizacional (7 capacidades — Seção 7.3).

---

## 13. Bibliografia Anotada

**Anthropic — fontes primárias (alta credibilidade):**
- *Building Effective Agents* (Erik Schluntz, Barry Zhang, dez/2024) — referência canônica dos 5 padrões agênticos. **[CONSOLIDADO]**
- *How We Built Our Multi-Agent Research System* (jun/2025) — orchestrator-worker, +90,2% sobre single em BrowseComp, 15× tokens. **[CONSOLIDADO como case]**
- *Effective Context Engineering for AI Agents* (set/2025) — define o termo, attention budget, compaction, structured note-taking, sub-agent architectures. **[CONSOLIDADO]**
- *Equipping Agents for the Real World with Agent Skills* (2025) — formato SKILL.md, progressive disclosure. **[EMERGENTE com adoção rápida]**
- *Building Agents with the Claude Agent SDK* — runtime e mecânica de subagentes. **[EMERGENTE]**
- *Code Execution with MCP* (2026) — alternativa de tool-loading que reduz contexto em 98,7% no exemplo. **[EMERGENTE]**

**GitHub:**
- *Spec-driven development with AI* (GitHub Blog, set/2025) — anúncio e justificativa do Spec Kit; intent-as-source-of-truth. **[CONSOLIDADO como metodologia]**
- *spec-kit/spec-driven.md* — manifesto técnico do SDD.

**Amazon / AWS:**
- Kiro docs (kiro.dev) — workflow Requirements/Design/Tasks, EARS, steering, hooks. **[EMERGENTE]**, IDE em early access em 2025–2026.

**Microsoft:**
- *AI Agent Orchestration Patterns* (Azure Architecture Center) — sequencial, concurrent, group chat, handoff, magentic. **[CONSOLIDADO em docs]**
- Microsoft Agent Framework v1.0 (sucessor de Semantic Kernel + AutoGen).

**Cognition AI:**
- *Don't Build Multi-Agents* (Walden Yan, jun/2025) — contra-argumento ao multi-agente. **[EM DISPUTA — refinado depois]**
- *Multi-Agents: What's Actually Working* (mai/2026) — síntese: paralelizar leitura, single-thread para escrita.

**Manus AI:**
- *Context Engineering for AI Agents: Lessons from Building Manus* (Yichao Ji, jul/2025) — KV-cache, mask logits, filesystem como memória, "stochastic graduate descent". **[EMERGENTE]**; insights de produção valiosos.

**Pesquisa acadêmica:**
- Liu et al., *Lost in the Middle* (arXiv 2307.03172; TACL 2024) — viés posicional. **[CONSOLIDADO]**
- Hong, Troynikov, Huber (Chroma), *Context Rot* (jul/2025) — degradação em 18 modelos. **[CONSOLIDADO empiricamente]**
- Mavin et al., *Easy Approach to Requirements Syntax (EARS)* (Rolls-Royce, RE'09, 2009) — origem da notação; cinco padrões com keywords WHILE/WHEN/WHERE/IF-THEN. **[CONSOLIDADO em engenharia de requisitos]**
- Becker, Rush, Barnes, Rein (METR), *Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity* (arXiv 2507.09089, jul/2025) — RCT com 16 devs, 246 tarefas, -19% em devs experientes; previsão pré-estudo de 24%, estimativa pós-estudo de 20%. **[CONSOLIDADO mas contestado em generalização]**
- *When AIs Judge AIs* (arXiv 2508.02994, ago/2025) — survey de LLM-as-judge.

**DORA / Google Cloud:**
- *2024 Accelerate State of DevOps Report* (DORA) — n>39k; ganho individual, perda de estabilidade. **[CONSOLIDADO]**
- *2025 DORA State of AI-assisted Software Development Report* — reversão para positivo em throughput, instabilidade ainda negativa, 7 capacidades. **[CONSOLIDADO]**
- *DORA AI Capabilities Model* (Storer & DeBellis, Google Cloud, set/2025) — sete capacidades verbatim listadas na Seção 7.3.

**Indústria / análises secundárias:**
- *Faros AI Engineering Report 2026* — telemetria de 22.000 devs; PR size +51,3%, review time +441%, PRs sem review +31%. *(Atenção: são dados Faros, não DORA.)*
- *CloudZero* e análises de Amazon Bedrock — multiplicadores de custo agêntico e routing por modelo.
- *Stanford Digital Economy Lab* — Brynjolfsson et al., mai/2026 — tarefas agênticas como "1000× mais caras" em tokens vs. chat.

**Modelos de maturidade:**
- *Gartner AI Maturity Model* — 5 níveis (Awareness → Transformational), 7 pilares. **[CONSOLIDADO]**

**Padrões / protocolos:**
- *Model Context Protocol Specification* (modelcontextprotocol.io) — protocolo oficial. **[CONSOLIDADO, adoção por OpenAI, Google, Microsoft]**

---

## 14. Lacunas de Conhecimento e Questões em Aberto

1. **Benchmark agêntico padronizado e independente** que sirva para comparar arquiteturas (não apenas modelos) está ainda em formação; SWE-bench, BrowseComp e Tau-Bench cobrem fatias, não o todo.
2. **Como medir ROI de IA em domínios não-coding** (data, analytics, ops) com rigor comparável ao DORA — ainda imaturo.
3. **Generalização do achado METR**: o resultado vale para outras populações (devs juniores, codebases novos, modelos de fim de 2025/2026)? METR mudou o desenho do experimento em fev/2026 por viés de não-participação; resultados novos ainda não consolidados.
4. **Convergência ou divergência futura entre SDD e agentic frameworks**: Kiro, Spec Kit, BMAD ainda competem por convenções; padrão único pode emergir ou não.
5. **Custo real em escala**: dados públicos sobre custo total de operação de agentes em produção são escassos; estimativas (Stanford Digital Economy Lab, multiplicadores Gartner) são ordens-de-grandeza, não números definitivos. Cifras intermediárias amplamente citadas em derivados (ex.: "62% do gasto em re-envio de contexto") não foram confirmadas em fonte primária.
6. **Eficácia de Agent Skills vs. MCP servers vs. fine-tuning**: trade-offs ainda em exploração; *code execution with MCP* (Anthropic, 2026) sugere uma nova síntese.
7. **Single vs. multi-agente em coding**: a Anthropic explicita que coding é menos paralelizável; mas Cognition e Claude Code (Agent Teams experimental) exploram híbridos. Não há consenso.
8. **Implicações de segurança de skills**: skills podem ser maliciosas; isolamento e revisão são imaturos.
9. **Governança de spec-as-source-of-truth em ambiente regulado**: como mapear specs para evidência de compliance (BCB, LGPD, EU AI Act) — práticas em formação.
10. **Sustentabilidade energética**: nenhuma fonte consultada quantifica seriamente o impacto ambiental de multi-agente vs. single; tópico ausente do debate técnico dominante.

---

> Este documento foi compilado em maio/2026 com fontes 2023–2026. Como o campo evolui rapidamente, recomenda-se revisão trimestral, em especial das seções 4 (porquês — base teórica é estável), 5 (mecânica — mais volátil) e 7.3 (métricas — em rápida evolução).