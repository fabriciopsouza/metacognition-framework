# Engenharia de Prompt e Engenharia de Contexto para LLMs: Princípios Transferíveis

## 1. Sumário Executivo

Este documento sintetiza, em profundidade técnica e a partir de fontes primárias (2017–2026), o estado atual dos princípios que governam a interação com Large Language Models (LLMs) por meio de instrução (*prompt engineering*) e de manipulação ativa do estado contextual (*context engineering*). A pergunta central é: **como a instrução e o contexto modelam o comportamento de um LLM, e quais princípios são transferíveis entre modelos e gerações?**

A resposta empírica, hoje, tem cinco vetores:

1. **O contexto não é processado uniformemente.** O paper "Lost in the Middle" (Liu et al., TACL 2024) mostrou uma curva em U na recuperação de informação: o modelo lembra muito melhor o início e o fim do prompt do que o meio. O relatório técnico "Context Rot" da Chroma (Hong, Troynikov & Huber, julho de 2025), testando 18 modelos de fronteira (GPT-4.1, Claude 4, Gemini 2.5, Qwen3), confirmou e generalizou: **o desempenho degrada de forma não uniforme à medida que o input cresce, mesmo em tarefas triviais como replicar texto**. NoLiMa (Modarressi et al., ICML 2025) demonstrou que, sem correspondência lexical entre pergunta e "agulha", **11 dos 13 modelos avaliados** caem para menos de 50% do seu baseline já em 32K tokens — e mesmo o GPT-4o cai de 99,3% para 69,7%.

2. **Context engineering é a disciplina sucessora da prompt engineering** para sistemas agênticos. Anthropic (*Effective context engineering for AI agents*, 29/09/2025) define-a como "the set of strategies for curating and maintaining the optimal set of tokens during LLM inference, including all the other information that may land there outside of the prompts". O foco muda de "achar as palavras certas" para "configurar o estado completo que o modelo verá" — instruções de sistema, ferramentas, histórico, dados via MCP, memória externa.

3. **Técnicas de instrução consolidadas existem, mas são muito sensíveis a forma.** Few-shot prompting (Brown et al., 2020) e chain-of-thought (Wei et al., 2022) são fundamentos comprovados; porém Sclar et al. (ICLR 2024) mostraram **diferenças de até 76 pontos de acurácia** em LLaMA-2-13B apenas por mudanças cosméticas de formatação, e Lu et al. (ACL 2022) mostraram que a ordem dos exemplos few-shot pode oscilar entre "estado da arte" e "chute aleatório". Min et al. (EMNLP 2022) revelaram que o que os exemplos few-shot ensinam é o **formato e o espaço de rótulos**, não a associação correta entre entrada e saída.

4. **Memória e estado precisam de arquitetura, não de prompts maiores.** MemGPT (Packer et al., 2023; hoje Letta) propôs gerenciar memória como um SO faz com memória virtual: hierarquias de memória "principal" e "arquivo", paginadas via tool calls. Anthropic recomenda compactação, anotações estruturadas (NOTES.md) e sub-agentes para tarefas de longo horizonte — e relata que sua arquitetura multi-agente com Claude Opus 4 como lead e Sonnet 4 como sub-agentes **superou o Claude Opus 4 single-agent em 90,2%** numa avaliação interna de pesquisa, ao custo de ~15× mais tokens.

5. **Muito do "folclore" de prompts tem evidência fraca ou nula.** Personas tipo "você é um especialista" não melhoram acurácia factual em benchmarks de PhD (Wharton GAIL, 2025); ameaças e gorjetas ("vou te dar $200") não têm efeito agregado significativo em 5 modelos de fronteira (Meincke et al., arXiv:2508.00614, 2025); a célebre frase "Take a deep breath" funcionou para a combinação otimizador PaLM 2-L-IT + scorer PaLM 2-L em GSM8K mas **não é transferível** (Yang et al., 2023; Battle & Gollapudi, 2024).

**Conclusão acionável para liderança técnica:** trate o contexto como recurso escasso com retornos marginais decrescentes; estruture prompts com seções claras e instruções explícitas; valide com avaliações próprias antes de adotar "truques"; invista em pipelines de contexto (RAG, compactação, memória externa) em vez de janelas maiores. Os ganhos vêm de arquitetura, não de magia textual.

---

## 2. Glossário dos Termos Essenciais

- **Token** — unidade básica de processamento de um LLM (subpalavra). 1 token ≈ 4 caracteres em inglês; em português costuma ser pior (mais tokens por palavra).
- **Janela de contexto (context window)** — número máximo de tokens (entrada + saída) que o modelo aceita por inferência. Em 2025–2026: 200K (Claude), 1M (GPT-4.1, Gemini 2.5 Pro), **10M para Llama 4 Scout e 1M para Llama 4 Maverick** (Meta, "The Llama 4 herd", abril de 2025).
- **Atenção (attention)** — mecanismo do Transformer (Vaswani et al., 2017) que permite a cada token "olhar" para todos os outros tokens; gera n² relações pareadas para n tokens.
- **Embedding** — representação vetorial densa de um token, frase ou documento; base de busca semântica e RAG.
- **System prompt** — instrução de mais alto nível, persistente entre turns, que define papel, regras e estilo.
- **Few-shot / In-Context Learning (ICL)** — fornecer exemplos de entrada-saída no prompt para induzir o comportamento desejado, sem treinar o modelo (Brown et al., 2020).
- **Chain-of-Thought (CoT)** — pedir ao modelo que gere raciocínio intermediário antes da resposta final (Wei et al., 2022).
- **Lost in the Middle** — fenômeno observado por Liu et al. (TACL 2024): desempenho de recuperação cai quando a informação relevante está no meio do contexto.
- **Context Rot** — termo cunhado pela Chroma (Hong et al., 2025) para a degradação não-uniforme do desempenho à medida que o input cresce.
- **RAG (Retrieval-Augmented Generation)** — combinar busca em base externa com geração (Lewis et al., NeurIPS 2020).
- **Context Engineering** — disciplina de curar e manter o conjunto ótimo de tokens em cada inferência, especialmente em agentes (Anthropic, 2025).
- **Compactação (compaction)** — sumarizar histórico de conversa próximo do limite da janela e reinicializar o contexto com o resumo.
- **Just-in-time context** — estratégia em que o agente carrega dinamicamente apenas o necessário em runtime, via identificadores leves (caminhos, IDs, queries).
- **MCP (Model Context Protocol)** — protocolo aberto da Anthropic para conectar LLMs a ferramentas e fontes de dados externas.
- **Needle in a Haystack (NIAH)** — benchmark clássico de contexto longo: inserir uma "agulha" (frase com fato isolado) em um "palheiro" (texto longo) e perguntar ao modelo.

---

## 3. Como um LLM usa Contexto

### 3.1 Conceito — Mecanismo de atenção e janela de contexto

**Por quê.** Um Transformer (Vaswani et al., "Attention Is All You Need", NeurIPS 2017) processa todos os tokens do prompt em paralelo. Cada token computa pesos de atenção sobre todos os demais — formando n² relações pareadas. A "janela de contexto" é o limite duro: além dela, tokens são truncados ou ignorados. Modelos modernos usam técnicas como **position encoding interpolation** (RoPE; YaRN — Peng et al., arXiv:2309.00071) para estender essa janela, mas com algum custo de precisão posicional, conforme reconhece a Anthropic em seu post de context engineering: *"position encoding interpolation allow models to handle longer sequences by adapting them to the originally trained smaller context, though with some degradation in token position understanding"*.

**Como.** Em termos práticos, três fatos importam para quem escreve prompts:

1. **Atenção é finita.** Anthropic descreve isso como um "attention budget": cada novo token "deprecia" o orçamento disponível. [CONSOLIDADO] — a complexidade quadrática da atenção é matematicamente verificável e empiricamente medida.
2. **Posição importa.** Há viés de início (primacy) e fim (recency).
3. **Distribuição de treinamento importa.** Sequências curtas dominam dados de treino, portanto o modelo tem menos "experiência" com dependências de longo alcance.

### 3.2 "Lost in the Middle" — A curva em U

**Conceito.** Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni & Liang ("Lost in the Middle: How Language Models Use Long Contexts", TACL 12:157–173, 2024; arXiv:2307.03172) mediram QA multi-documento e key-value retrieval variando a posição da passagem relevante. Reportam: *"performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle of long contexts, even for explicitly long-context models."*

**Por quê.** Combinação de viés de atenção e da maneira como dados de pré-treino são estruturados (introduções e conclusões costumam concentrar informação).

**Como aplicar.**
- Em RAG, **ranquear** documentos recuperados de modo que os mais relevantes fiquem nas pontas.
- Em prompts com muitos blocos, **colocar a pergunta ou a instrução-chave no início E reafirmá-la no fim**.
- Em documentos longos, **pedir que o modelo cite/cole trechos relevantes antes de responder** (mitigação clássica de Anthropic).

**Trade-offs.** Repetir instruções consome tokens; ranquear adiciona latência de pipeline. [CONSOLIDADO] — múltiplas replicações independentes (incluindo Chroma 2025) confirmam o efeito.

### 3.3 Limites práticos — Janela ≠ Performance utilizável

A regra prática emergente em 2025–2026 é distinguir **janela nominal** (o que a API aceita) de **janela efetiva** (a partir da qual o modelo continua confiável). NoLiMa (Modarressi et al., ICML 2025, arXiv:2502.05167) define janela efetiva como "the longest context where a model maintains at least 85% of its base score"; nos seus testes, mesmo modelos com janela nominal de 128K–1M caem abaixo desse limite muito antes — *"At 32K, for instance, 11 models drop below 50% of their strong short-length baselines. Even GPT-4o, one of the top-performing exceptions, experiences a reduction from an almost-perfect baseline of 99.3% to 69.7%."*

---

## 4. "Context Rot" e Mitigação de Degradação em Contexto Longo

### 4.1 Conceito

**Context Rot** é o termo do relatório técnico Chroma (Hong, Troynikov, Huber — julho de 2025, research.trychroma.com/context-rot) para descrever o fato de que *"models do not use their context uniformly; instead, their performance grows increasingly unreliable as input length grows"*. Foram testados 18 LLMs (Claude Opus 4 e Sonnet 3.5/3.7/4, Haiku 3.5; GPT-4.1 e variantes, GPT-4o, GPT-4 Turbo, o3; Gemini 2.0/2.5 Flash e Pro; Qwen3 8B/32B/235B) em quatro famílias de experimentos:

1. **NIAH com pares pergunta-agulha de baixa similaridade**: quanto mais semântica (menos lexical) a busca, mais rápido degrada com o comprimento.
2. **Distractors**: adicionar 1 distrator (frase topicamente relacionada mas incorreta) já reduz acurácia em relação ao baseline; 4 distratores compõem o efeito; impacto **não é uniforme entre distratores**.
3. **Similaridade agulha-palheiro**: quando a agulha se funde semanticamente no texto, modelos têm mais dificuldade — mas o efeito é não-monotônico.
4. **Estrutura do palheiro**: contraintuitivamente, **palheiros embaralhados (sem fluxo lógico) produziram melhor desempenho que palheiros coerentes** em todos os 18 modelos. Isso aponta para vieses de atenção condicionados pela estrutura.

E o experimento "Repeated Words": pedir ao modelo para replicar uma sequência simples (e.g. "apple apple apple ... apples apple apple ...") degrada com o tamanho — modelos ora sub-geram, ora super-geram, ora se recusam a responder (Claude Opus 4 chegou a recusar 2,89% das tentativas, GPT-4.1 a 2,55%).

LongMemEval (Wu et al., arXiv:2410.10813, 2025; usado pela Chroma) reforça: dado o mesmo prompt, **prompts focados (~300 tokens, só o relevante) superam fortemente prompts cheios (~113K, com irrelevâncias)** em todas as famílias.

### 4.2 Por que acontece

Hipóteses convergentes:
- Atenção espalhada por mais tokens.
- Modelos foram treinados predominantemente em sequências curtas/médias.
- Modos de extensão de contexto (RoPE/YaRN) preservam alcance mas distorcem encoding posicional.
- Pré-treino enviesa para textos coerentes; estruturas patologicamente longas e homogêneas (e.g. repetições) saem da distribuição.

### 4.3 Estratégias de mitigação (todas com respaldo primário)

| Técnica | Origem / Fonte | Maturidade |
|---|---|---|
| **Reduzir input ao mínimo viável** (filtragem prévia, RAG bem feito) | Anthropic 2025; Chroma 2025 | [CONSOLIDADO] |
| **Compaction** (sumarizar a conversa) | Anthropic, "Effective context engineering" (2025); Claude Code | [CONSOLIDADO] |
| **Anotações estruturadas / scratchpads externos** (NOTES.md) | MemGPT (Packer et al., 2023); Anthropic 2025 | [CONSOLIDADO] |
| **Sub-agentes** com janelas limpas, retornando resumos curtos | Anthropic, "How we built our multi-agent research system" (jun. 2025) | [EMERGENTE] |
| **Just-in-time retrieval** (IDs leves; o agente busca quando precisa) | Anthropic 2025; Claude Code (glob, grep) | [EMERGENTE] |
| **Tool-result clearing** (limpar saídas de ferramentas antigas) | Anthropic 2025 (Claude Developer Platform) | [EMERGENTE] |
| **Ranquear por relevância** com a agulha nas pontas | Liu et al. 2024 (corolário) | [CONSOLIDADO] |

**Trade-offs.** Compaction perde detalhes finos cuja relevância só aparece depois; sub-agentes adicionam latência e custo (Anthropic relata ~15× mais tokens que chat single-agent); just-in-time é mais lento que pré-carregamento.

---

## 5. Engenharia de Contexto: o que é e por que virou disciplina própria

### 5.1 Conceito

Anthropic, em *"Effective context engineering for AI agents"* (Applied AI team: Rajasekaran, Dixon, Ryan, Hadfield et al., 29/09/2025): **"Context engineering refers to the set of strategies for curating and maintaining the optimal set of tokens (information) during LLM inference, including all the other information that may land there outside of the prompts."**

Andrej Karpathy, citado pela própria Anthropic (X/Twitter, jun. 2025): *"In every industrial-strength LLM app, context engineering is the delicate art and science of filling the context window."*

### 5.2 Por que se separou de prompt engineering

Três pressões empíricas:

1. **Agentes geram contexto.** Em um loop autônomo, cada chamada de ferramenta retorna tokens, acumulando rapidamente. A Anthropic, no post sobre seu sistema multi-agente (junho de 2025), observou que *"token usage by itself explains 80% of the variance"* no desempenho em BrowseComp.
2. **Janelas longas degradam (context rot).** Confirmado por Chroma 2025, NoLiMa 2025, Liu 2024 — a janela não é gratuita.
3. **Multiagentes amplificam o problema.** A Anthropic relata que sistemas multi-agentes consomem **~15× mais tokens** que chats single-agent, em troca de ganhos como *"a multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval"*.

### 5.3 Como — A anatomia de um bom contexto (Anthropic 2025)

Os componentes que precisam ser projetados em conjunto:

- **System prompt na "altitude certa"**: nem if-else rígido, nem vago demais. *"specific enough to guide behavior effectively, yet flexible enough to provide the model with strong heuristics."* Organização sugerida: seções com tags XML ou cabeçalhos Markdown (`<background_information>`, `<instructions>`, `## Tool guidance`, `## Output description`).
- **Tools**: pequenas, distintas, token-eficientes, com parâmetros descritivos. *"If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better."*
- **Exemplos**: poucos e canônicos, não enciclopédia de edge cases.
- **Histórico (message history)**: podado seletivamente.
- **Recuperação JIT**: identificadores leves + tools.

Princípio guia: **"the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."**

### 5.4 Diferença prática vs. prompt engineering

| Prompt engineering | Context engineering |
|---|---|
| Foco em instruções estáticas | Foco no estado dinâmico completo |
| One-shot, fixo | Iterativo, curado a cada turn |
| Otimiza wording | Otimiza orçamento de atenção |
| Comum em chat/QA | Necessário em agentes multi-turn |

[CONSOLIDADO como termo e como prática nas big-techs em 2025–2026]; [EMERGENTE como corpo formal de princípios — métricas e padrões ainda em consolidação].

---

## 6. Técnicas de Instrução Comprovadas

### 6.1 Clareza, especificidade, instruções literais

OpenAI documenta para o GPT-4.1 (developers.openai.com/cookbook/examples/gpt4-1_prompting_guide): *"GPT-4.1 is trained to follow instructions more closely and more literally than its predecessors... if model behavior is different from what you expect, a single sentence firmly and unequivocally clarifying your desired behavior is almost always sufficient to steer the model on course."*

Implicações:
- Diga o que **fazer**, não apenas o que evitar.
- Resolva conflitos explícitos no prompt (uma instrução por regra).
- Para agentes, OpenAI recomenda três lembretes obrigatórios: **persistência** ("siga até o problema estar resolvido"), **uso de tools** ("não chute; use as ferramentas"), **planejamento** ("planeje antes de chamar funções e reflita depois"). Segundo a própria OpenAI: *"the model adhered closely to these three simple instructions and increased our internal SWE-bench Verified score by close to 20%"*, contribuindo para que GPT-4.1 alcançasse 55% no SWE-bench Verified — *"a state-of-the-art performance for non-reasoning models"*.

[CONSOLIDADO] — toda documentação oficial converge.

### 6.2 Estruturação: XML tags, Markdown, output contracts

Anthropic treina Claude com forte uso de XML tags. Da documentação oficial Claude (docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags): *"When your prompts involve multiple components like context, instructions, and examples, XML tags can be a game-changer. They help Claude parse your prompts more accurately, leading to higher-quality outputs."*

OpenAI prefere Markdown e JSON em GPT-4/4.1, mas também aceita XML. A regra transferível: **use delimitadores explícitos que separem dados de instruções**. O AWS Bedrock prompt-engineering guide ilustra: sem delimitadores, Claude confundiu "Yo Claude" do início de um e-mail com instrução.

[CONSOLIDADO] como princípio (separar dados de instruções); **[EM DISPUTA]** quanto a *qual* sintaxe é melhor — depende do modelo e fica menos relevante conforme modelos melhoram (Anthropic 2025: *"the exact formatting of prompts is likely becoming less important as models become more capable"*).

### 6.3 Few-shot / In-Context Learning

**Origem.** Brown et al., "Language Models are Few-Shot Learners" (NeurIPS 2020, arXiv:2005.14165) — GPT-3 175B mostrou que **fornecer exemplos no prompt** rivaliza com fine-tuning para muitas tarefas.

**Nuances cruciais (frequentemente ignoradas):**

- **Min et al., "Rethinking the Role of Demonstrations" (EMNLP 2022, arXiv:2202.12837)** mostraram que **substituir os rótulos dos exemplos por rótulos aleatórios quase não derruba a performance**: *"ground truth demonstrations are in fact not required—randomly replacing labels in the demonstrations barely hurts performance on a range of classification and multi-choice tasks, consistently over 12 different models including GPT-3."* O que conta são: o espaço de rótulos, a distribuição do input e o formato da sequência. Implicação prática: invista em diversidade de formato e cobertura do espaço de classes; a "verdade" dos exemplos importa menos do que se imagina.

- **Lu et al., "Fantastically Ordered Prompts" (ACL 2022, arXiv:2104.08786)** mostraram que **a ordem dos exemplos pode levar o desempenho de "near state-of-the-art" a "random guess"**. Mitigação: testar várias permutações.

- **Sclar et al., "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design" (ICLR 2024, arXiv:2310.11324)** documentaram **"performance differences of up to 76 accuracy points when evaluated using LLaMA-2-13B"** apenas mudando separadores, quebras de linha ou espaços. Sensibilidade permanece com mais exemplos, modelos maiores e instruction tuning. Apresentam o algoritmo FormatSpread para medir esse intervalo.

**Como aplicar.**
- 3–5 exemplos diversos e canônicos; padrão da Anthropic: *"examples are the 'pictures' worth a thousand words"*, mas explicitamente *"we do not recommend stuffing a laundry list of edge cases."*
- Padronize formato.
- Em produção: reportar **intervalo** de desempenho sobre formatos plausíveis (FormatSpread de Sclar et al.), não um número único.

[CONSOLIDADO] — few-shot ajuda; **[EM DISPUTA]** — magnitude e mecanismo; **[CONSOLIDADO]** — alta sensibilidade a forma.

### 6.4 Chain-of-Thought (CoT) e decomposição

**Origem.** Wei, Wang, Schuurmans, Bosma, Ichter, Xia, Chi, Le, Zhou — "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (NeurIPS 2022, arXiv:2201.11903). Em modelos suficientemente grandes, exemplos com raciocínio intermediário melhoram drasticamente tarefas aritméticas, de senso comum e simbólicas. Variante zero-shot: Kojima et al., "Let's think step by step" (NeurIPS 2022).

**Quando ajuda — evidência atual.**
- **Sprague et al., "To CoT or Not to CoT?" (arXiv:2409.12183, 2024)**: meta-análise de 100+ papers + 20 datasets × 14 modelos. *"CoT gives strong performance benefits primarily on tasks involving math or logic, with much smaller gains on other types of tasks. On MMLU, directly generating the answer without CoT leads to almost identical accuracy as CoT unless the question or model's response contains an equals sign, indicating symbolic operations and reasoning."*
- **Meincke et al., "Prompting Science Report 2: The Decreasing Value of Chain of Thought" (arXiv:2506.07142, 2025)**: em modelos com "reasoning mode" interno (o-series, Gemini 2.5 thinking), CoT explícito traz ganhos pequenos ou nulos porque o modelo já raciocina internamente.

**Trade-offs.** CoT aumenta latência e custo (mais tokens de saída); em modelos "thinking" pode duplicar raciocínio.

[CONSOLIDADO para math/symbolic]; [EM DISPUTA para tarefas não-simbólicas e modelos thinking].

### 6.5 Decomposição e prompt chaining

Quebrar uma tarefa complexa em sub-tarefas encadeadas — output de uma vira input da próxima — melhora robustez e facilita debug. Documentado por OpenAI (cookbook), Anthropic (sub-agent architectures), e empiricamente respaldado pelas evidências de degradação em contexto longo: tarefas menores cabem em janelas menores. [CONSOLIDADO].

### 6.6 Papéis, restrições, "personas"

**Hype.** Toda documentação oficial recomenda: *"You are an expert..."* (Anthropic, OpenAI, Google Vertex AI).

**Evidência.**
- **Zheng et al., "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models" (arXiv:2311.10054, 2023)**: testaram 162 personas × 4 famílias de LLMs × 2.410 perguntas factuais e concluíram que *"adding personas in system prompts does not improve model performance across a range of questions compared to the control setting where no persona is added."*
- **Meincke, Mollick, Mollick & Shapiro, "Prompting Science Report 4: Playing Pretend: Expert Personas Don't Improve Factual Accuracy" (Wharton GAIL, arXiv:2512.05858, 2025/2026):** em GPQA Diamond e MMLU-Pro, *"persona prompts generally did not improve accuracy relative to a no-persona baseline. Expert personas showed no consistent benefit across models, with few exceptions. Domain-mismatched expert personas sometimes degraded performance. Low-knowledge personas often reduced accuracy."* Personas de domínio mismatched podem causar recusas (Gemini 2.0 Flash).
- **USC (paper "PRISM", 2026):** confirma que personas ajudam em **alinhamento** (tom, estilo, segurança) mas **prejudicam tarefas factuais** (math, code, knowledge); em MMLU: 68,0% com persona vs. 71,6% sem.

**Como usar bem.** Use personas para **estilo e tom**, não para "ativar expertise". Para tarefas factuais, prompt neutro + verificação. [CONSOLIDADO que persona não melhora factualmente; ainda assim, [EMERGENTE] como prática para estilo/alinhamento].

---

## 7. Estado e Memória Entre Interações

### 7.1 Conceito

LLMs são **stateless** por padrão: cada chamada vê apenas o que está na janela. Construir continuidade exige arquitetura externa.

### 7.2 Abordagens

**A. Janela como memória pura.** Concatenar todo o histórico no prompt. Simples; falha em volume (context rot) e custo.

**B. Compaction / sumarização.** Anthropic (2025): *"Compaction is the practice of taking a conversation nearing the context window limit, summarizing its contents, and reinitiating a new context window with the summary."* Em Claude Code: preserva decisões arquiteturais, bugs não resolvidos, detalhes de implementação; descarta tool calls/outputs redundantes; agente continua com resumo + 5 arquivos mais recentes.

**C. MemGPT / Letta.** Packer, Wooders, Lin, Fang, Patil, Stoica & Gonzalez ("MemGPT: Towards LLMs as Operating Systems", arXiv:2310.08560, 2023; hoje framework Letta). Inspirado em paginação de SO: memória "main" (in-context: persona, working memory) vs. "external" (archival, recall) acessada via function calls. O LLM **edita sua própria memória**. Validado em document analysis (documentos maiores que a janela) e multi-session chat.

**D. Notas estruturadas (agentic memory).** Agente escreve em arquivo externo (NOTES.md, TODO list). Anthropic cita o caso de "Claude Plays Pokémon" como demonstração: o agente mantém contagens precisas ("for the last 1,234 steps I've been training my Pokémon in Route 1, Pikachu has gained 8 levels toward the target of 10"), mapas, estratégias. Lançado em beta como **memory tool** na Claude Developer Platform com o Claude Sonnet 4.5 (set/2025).

**E. RAG (Retrieval-Augmented Generation).** Lewis, Perez, Piktus, Petroni, Karpukhin, Goyal, Küttler, Lewis, Yih, Rocktäschel, Riedel, Kiela — "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (NeurIPS 2020, arXiv:2005.11401). Recuperar trechos relevantes de um índice (denso ou esparso) e injetá-los no prompt. Combina memória **paramétrica** (pesos) e **não-paramétrica** (índice). Base para grande parte da arquitetura de agentes com conhecimento empresarial.

**F. Sub-agentes.** Cada sub-tarefa em janela limpa; agente principal coordena (Anthropic, "How we built our multi-agent research system", jun. 2025).

### 7.3 Trade-offs

| Estratégia | Custo | Fidelidade | Complexidade |
|---|---|---|---|
| Histórico cru | Alto | Alta até context rot | Baixa |
| Compaction | Médio | Média (perda fina) | Baixa-média |
| MemGPT/Letta | Médio | Alta (mas depende de function calling certo) | Alta |
| Notas em arquivo | Baixo | Alta (escrita explícita) | Média |
| RAG | Baixo-médio | Alta para fatos; depende de retrieval | Alta |
| Sub-agentes | Alto (~15× tokens) | Alta isolamento | Muito alta |

[CONSOLIDADO] que arquiteturas externas superam "janela maior" para horizontes longos.

---

## 8. Hype vs. Evidência

### 8.1 Quadro-resumo

| Prática | Status empírico | Fonte primária |
|---|---|---|
| Few-shot ajuda | [CONSOLIDADO] | Brown et al. 2020 |
| Mas é muito sensível a forma/ordem | [CONSOLIDADO] | Sclar 2024; Lu 2022 |
| CoT ajuda em math/symbolic | [CONSOLIDADO] | Wei 2022; Sprague 2024 |
| CoT ajuda em tudo | [EM DISPUTA] | Sprague 2024 (contra) |
| XML tags ajudam (Claude) | [CONSOLIDADO] | Anthropic docs |
| Persona "expert" melhora acurácia factual | [EM DISPUTA] (evidência contra) | Zheng 2023; Wharton 2025/2026 |
| "Take a deep breath" como prompt universal | [EM DISPUTA] (não generaliza) | Yang 2023; Battle & Gollapudi 2024 |
| Gorjetas/ameaças melhoram performance | [EM DISPUTA] (evidência contra) | Meincke et al. 2025 |
| Polidez sempre ajuda | [EM DISPUTA] | Yin et al. 2024 |
| Context rot existe | [CONSOLIDADO] | Chroma 2025; NoLiMa 2025; Liu 2024 |
| Compaction funciona | [CONSOLIDADO] | Anthropic 2025; uso em Claude Code |
| Memória externa (MemGPT/RAG) | [CONSOLIDADO] | Packer 2023; Lewis 2020 |
| Just-in-time context para agentes | [EMERGENTE] | Anthropic 2025 |

### 8.2 Detalhamento de claims hypeados

**"Take a deep breath and work on this problem step-by-step"** — Yang, Wang, Lu, Liu, Le, Zhou & Chen, "Large Language Models as Optimizers" (Google DeepMind, arXiv:2309.03409, ICLR 2024). A frase atingiu **80,2 de acurácia em GSM8K especificamente com otimizador PaLM 2-L-IT + scorer PaLM 2-L** (Tabela 1 do paper; compare com 71,8 de "Let's think step by step" e 78,5 de "Let's work this out in a step by step way..."). A própria Tabela 1 mostra que prompts diferentes vencem para combinações diferentes (PaLM 2-L como otimizador favoreceu "Break this down." a 79,9; gpt-3.5-turbo como otimizador produziu "Let's combine our numerical command and a clear thinking process..."). Battle & Gollapudi (arXiv:2402.10949, 2024) testaram "positive thinking prompts" em Mistral-7B, Llama2-13B e Llama2-70B: *"Our findings reveal that results do not universally generalize across models. ... Notably, however, Llama2-70B exhibited an exception when not utilizing Chain of Thought, as the optimal system message was found to be none at all. ... the highest-scoring, automatically-optimized prompt exhibits a degree of peculiarity far beyond expectations"* — inclusive prompts no estilo Star Trek. **Lição:** prompts são otimizados localmente; trate qualquer "frase mágica" como hipótese a testar no seu modelo, não como receita.

**Gorjetas e ameaças.** Bsharat, Myrzakhan & Shen (arXiv:2312.16171, 2023) popularizaram "Add 'I'm going to tip $xxx for a better solution!'" como Princípio 6. Meincke, Mollick, Mollick & Shapiro, "Prompting Science Report 3: I'll Pay You or I'll Kill You — But Will You Care?" (Wharton GAIL, arXiv:2508.00614, agosto de 2025) replicaram rigorosamente em GPQA Diamond (N=4.950 por condição) e MMLU-Pro engineering (2.500 por condição) com 5 modelos (Gemini 1.5/2.0 Flash, GPT-4o, GPT-4o-mini, o4-mini). Conclusão: *"Threatening or tipping a model generally has no significant effect on benchmark performance."* Efeitos esporádicos em questões individuais (até ±36 pp), mas imprevisíveis. O prompt "Email shutdown threat" **piorou** Gemini 2.0 Flash em 27,5 pp porque o modelo engajou com o contexto de e-mail em vez de responder.

**Polidez.** Yin, Wang, Horio, Kawahara & Sekine, "Should We Respect LLMs? A Cross-Lingual Study on the Influence of Prompt Politeness on LLM Performance" (SICon 2024 @ EMNLP, arXiv:2402.14531) testaram inglês, chinês e japonês em tarefas de sumarização, language understanding e bias detection: *"impolite prompts often result in poor performance, but overly polite language does not guarantee better outcomes. The best politeness level is different according to the language."* Implicação: extremos de impolidez prejudicam; cortesia exagerada não compensa custo de tokens. [EM DISPUTA, com gradação por idioma].

**"Você é um expert..."** — ver §6.6.

### 8.3 Pontos onde a evidência ainda é fraca

- Magnitude exata da degradação de contexto por modelo: cada release muda a curva.
- Quando exatamente CoT explícito ajuda em modelos thinking — depende de domínio e de orçamento de tokens internos.
- Transferência de boas práticas de um modelo para outro: Sclar 2024 mostra que correlação entre formatos é fraca entre modelos.

---

## 9. Analogias Didáticas para Treinamento de Equipe

1. **Janela de contexto = mesa de trabalho.** Um LLM trabalha como um analista numa mesa pequena. Quanto mais papéis você empilha, mais difícil encontrar o que importa. Tirar papel da mesa **não apaga o conhecimento dele** (o treino fica nos pesos), mas remove o que ele está "olhando agora".

2. **Atenção = orçamento de foco.** Pense em 100 unidades de foco. Cada token gasta. Tokens irrelevantes não são neutros: roubam foco. (Anthropic chama de "attention budget".)

3. **Lost in the Middle = pilha de relatórios.** Se a chefia entrega 30 relatórios para ler, o analista lembra do primeiro e do último; o do meio "some". Por isso ranqueamos.

4. **Few-shot examples = manual de estilo, não verdades.** Quando você mostra exemplos, está ensinando **formato e espaço de respostas**, não fatos. Trocar rótulos por aleatórios quase não muda o resultado (Min et al. 2022) — o modelo está aprendendo "como responder", não "o que responder".

5. **CoT = "mostre o trabalho".** Funciona como em prova de matemática: pedir passos intermediários ajuda **se a tarefa tem cálculo ou lógica simbólica**. Em pergunta de opinião, "mostrar o trabalho" pouco adiciona.

6. **Context engineering = direção de cena.** Prompt engineering é escrever a fala do ator. Context engineering é montar o palco: que objetos estão à mão, que personagem ele lembra, que cenas anteriores ele viu, quando trocamos de cena (compaction).

7. **Memória externa = caderno do detetive.** O detetive (agente) carrega um caderno (NOTES.md, MemGPT archival memory) onde anota o essencial. Quando o caso fica longo, ele relê o caderno, não toda a conversa.

8. **RAG = biblioteca + bibliotecário.** O modelo é o leitor; o índice vetorial é a biblioteca; o retriever é o bibliotecário que traz só os livros relevantes. Sem isso, leitor tenta lembrar tudo da cabeça (pesos) e alucina.

9. **"Take a deep breath" não é mágica, é overfit.** Foi prompt ótimo para uma combinação específica de modelos, como uma chave que abre uma fechadura específica. Não traga para a sua porta sem testar.

---

## 10. Bibliografia Anotada

**Fundamentos arquiteturais e capacidades**

- Vaswani et al., "Attention Is All You Need" (NeurIPS 2017, arXiv:1706.03762). Paper original do Transformer; explica por que cada token atende a todos os outros e por que o custo é n². Citável para qualquer discussão sobre limites de atenção.
- Brown et al., "Language Models are Few-Shot Learners" (NeurIPS 2020, arXiv:2005.14165). GPT-3 (175B); mostrou pela primeira vez que ICL escala com tamanho. Base da prática moderna de few-shot.
- Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (NeurIPS 2020, arXiv:2005.11401). Paper fundador do RAG. Define memória paramétrica + não-paramétrica.

**Comportamento em contexto longo**

- Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni & Liang, "Lost in the Middle: How Language Models Use Long Contexts" (TACL 12:157–173, 2024; DOI:10.1162/tacl_a_00638; arXiv:2307.03172). A curva em U. Stanford/Berkeley/Samaya AI. Citado universalmente.
- Hong, Troynikov & Huber, "Context Rot: How Increasing Input Tokens Impacts LLM Performance" (Chroma Technical Report, julho de 2025, research.trychroma.com/context-rot). 18 modelos, 4 famílias de experimentos; o relatório mais completo de 2025.
- Modarressi et al., "NoLiMa: Long-Context Evaluation Beyond Literal Matching" (ICML 2025, arXiv:2502.05167). NIAH sem pistas lexicais; define "janela efetiva" como 85% do baseline.
- Peng et al., "YaRN: Efficient Context Window Extension of Large Language Models" (arXiv:2309.00071, 2023). Técnica usada pelos modelos Qwen na avaliação Chroma.

**Engenharia de contexto e agentes**

- Anthropic Applied AI Team (Rajasekaran, Dixon, Ryan, Hadfield et al.), "Effective context engineering for AI agents" (Anthropic Engineering Blog, 29/09/2025, anthropic.com/engineering/effective-context-engineering-for-ai-agents). A definição operacional canônica de context engineering. Inclui compaction, structured note-taking, sub-agents.
- Anthropic, "Prompt engineering overview" e "Use XML tags" (docs.anthropic.com/en/docs/build-with-claude/prompt-engineering). Documentação oficial.
- Anthropic, "How we built our multi-agent research system" (engineering blog, junho de 2025). Sub-agentes especializados; multi-agent supera single-agent em 90,2% na avaliação interna; consome ~15× tokens.
- OpenAI, "GPT-4.1 Prompting Guide" (developers.openai.com/cookbook/examples/gpt4-1_prompting_guide, abril de 2025). Persistência, tool use, planning; uplift de ~20% em SWE-bench Verified com 3 instruções padrão.

**Estado e memória**

- Packer, Wooders, Lin, Fang, Patil, Stoica & Gonzalez, "MemGPT: Towards LLMs as Operating Systems" (arXiv:2310.08560, 2023). UC Berkeley. Fundamenta agentes com memória; base do framework Letta.

**Raciocínio e CoT**

- Wei, Wang, Schuurmans, Bosma, Ichter, Xia, Chi, Le, Zhou, "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (NeurIPS 2022, arXiv:2201.11903). Google. Paper original do CoT.
- Kojima et al., "Large Language Models are Zero-Shot Reasoners" (NeurIPS 2022). Origem do "Let's think step by step".
- Sprague, Yin, Rodriguez et al., "To CoT or Not to CoT? Chain-of-Thought Helps Mainly on Math and Symbolic Reasoning" (arXiv:2409.12183, 2024). UT Austin/JHU/Princeton. Meta-análise de 100+ papers + 20 datasets × 14 modelos. Limita o escopo do CoT.
- Meincke et al., "Prompting Science Report 2: The Decreasing Value of Chain of Thought" (Wharton GAIL, arXiv:2506.07142, 2025).

**Sensibilidade e fragilidade de prompts**

- Sclar, Choi, Tsvetkov & Suhr, "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design" (ICLR 2024, arXiv:2310.11324). Diferenças de até 76 pontos de acurácia em LLaMA-2-13B. Apresenta FormatSpread.
- Lu, Bartolo, Moore, Riedel & Stenetorp, "Fantastically Ordered Prompts and Where to Find Them" (ACL 2022, arXiv:2104.08786). UCL/Cohere. Sensibilidade a ordem.
- Min, Lyu, Holtzman, Artetxe, Lewis, Hajishirzi & Zettlemoyer, "Rethinking the Role of Demonstrations" (EMNLP 2022, arXiv:2202.12837). UW/Meta. Rótulos aleatórios em ICL.

**Hype vs. evidência**

- Yang, Wang, Lu, Liu, Le, Zhou & Chen, "Large Language Models as Optimizers" (Google DeepMind, ICLR 2024, arXiv:2309.03409). Fonte original de "Take a deep breath..."; Tabela 1 mostra natureza modelo-específica.
- Battle & Gollapudi (VMware NLP Lab), "The Unreasonable Effectiveness of Eccentric Automatic Prompts" (arXiv:2402.10949, 2024). Mostra que prompts "positivos" não generalizam.
- Bsharat, Myrzakhan & Shen, "Principled Instructions Are All You Need for Questioning LLaMA-1/2, GPT-3.5/4" (arXiv:2312.16171, 2023). Fonte do meme de "tip $200"; metodologicamente fraca.
- Meincke, Mollick, Mollick & Shapiro, "Prompting Science Report 3: I'll Pay You or I'll Kill You — But Will You Care?" (Wharton GAIL, arXiv:2508.00614, agosto de 2025). Refutação rigorosa de tips/threats em 5 modelos modernos.
- Meincke et al., "Prompting Science Report 4: Playing Pretend: Expert Personas Don't Improve Factual Accuracy" (Wharton GAIL, arXiv:2512.05858, 2025/2026). Persona expert não ajuda factualmente.
- Zheng et al., "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of LLMs" (arXiv:2311.10054, 2023). 162 personas × 4 LLMs × 2.410 perguntas.
- Yin, Wang, Horio, Kawahara & Sekine, "Should We Respect LLMs? A Cross-Lingual Study on the Influence of Prompt Politeness on LLM Performance" (SICon 2024 @ EMNLP, arXiv:2402.14531). Polidez em EN/ZH/JA.
- Li et al., "EmotionPrompt: Large Language Models Understand and Can be Enhanced by Emotional Stimuli" (CAS/Microsoft/W&M, arXiv:2307.11760, 2023). Reivindica ganhos com prompts emocionais; contestado por trabalhos posteriores.

---

## 11. Lacunas de Conhecimento e Perguntas em Aberto

1. **Mecanismo causal do context rot.** Chroma 2025 reconhece explicitamente que não explica *por que* desempenho cai não-uniformemente, nem por que palheiros "embaralhados" às vezes ajudam. Aguarda trabalho em interpretabilidade mecanicista.

2. **Transferibilidade de prompts entre modelos.** Sclar et al. 2024: correlação de formatos entre modelos é baixa. Falta um padrão para reportar "intervalo de desempenho sobre formatos plausíveis" em benchmarks.

3. **Quando CoT explícito ajuda em modelos thinking?** Meincke 2025 sugere que o ganho diminui; falta um mapa preciso por domínio.

4. **Memória de longo prazo em produção.** MemGPT/Letta e Anthropic memory tool são promissores, mas há poucos estudos comparativos públicos em workloads enterprise reais (multi-mês, milhares de sessões).

5. **Métricas de "boa curadoria de contexto".** Não há equivalente formal a "perplexity" para qualidade de context engineering. Falta padronização.

6. **Polidez e cultura.** Yin et al. 2024 sugere variação por idioma; quase nada está publicado em português.

7. **Avaliação adversarial de agentes.** Como medir robustez a prompt injection em pipelines com MCP, RAG e ferramentas externas? Área quente, padrões ainda em formação.

8. **Custo-benefício de janelas ultralongas.** 1M–10M tokens existem nominais (Llama 4 Scout: 10M; Llama 4 Maverick: 1M, conforme Meta abril de 2025); estudos custo-versus-acurácia em tarefas reais são raros e geralmente apontam contra a janela máxima.

9. **Replicabilidade de "frases mágicas".** Falta um repositório padronizado, versionado por modelo, que permita reproduzir claims tipo "take a deep breath" ou "tip $200" — o campo depende de pré-prints individuais.

---

## 12. Recomendações Acionáveis para a Equipe

**Para o profissional individual:**
1. Estruture todo prompt em blocos delimitados (XML para Claude; Markdown/JSON para GPT).
2. Coloque instrução-chave e pergunta no início **e** repita no fim em prompts longos.
3. Use 3–5 exemplos diversos no formato exato esperado da saída.
4. Use CoT explícito quando a tarefa tiver matemática ou lógica simbólica; caso contrário, peça resposta direta com justificativa curta.
5. Persona apenas para tom/estilo; nunca espere que ela melhore acurácia factual.
6. Ignore gorjetas, ameaças e frases motivacionais como técnica geral.
7. Sempre que possível, recupere apenas o necessário em vez de empilhar contexto.

**Para a liderança técnica:**
1. Adote context engineering como disciplina formal: revisões de design para agentes incluem orçamento de tokens, política de compaction, estratégia de memória.
2. Construa avaliações próprias antes de adotar qualquer "best practice" — Sclar 2024 e Battle 2024 mostram que técnicas não transferem.
3. Padronize templates de prompt versionados (prompt-as-code).
4. Para RAG: ranqueie sempre (efeito Lost in the Middle).
5. Para agentes longos: combine just-in-time + compaction + notas estruturadas; teste sub-agentes para tarefas com decomposição clara (lembre-se: ~15× tokens, justifique pelo ganho de qualidade observado em benchmark próprio).
6. Monitore custo de tokens por sessão e degradação de qualidade ao crescer o contexto (defina janela efetiva por modelo via benchmarks NoLiMa-style internos).

---

## 13. Caveats

- O campo evolui mensalmente; práticas "[EMERGENTE]" em 2025 podem ser [CONSOLIDADO] ou abandonadas em 2026.
- Quase toda evidência empírica é em inglês; transferência para português não é garantida (ver §11.6).
- Documentação de fornecedores (Anthropic, OpenAI, Google) reflete também interesses comerciais — confronte com papers independentes.
- Benchmarks (GSM8K, MMLU, GPQA, NIAH) são proxies; nem sempre refletem casos de uso reais (Chroma 2025 enfatiza isso explicitamente: NIAH "is fundamentally a simple retrieval task... which may not be representative of flexible, semantically oriented tasks").
- "Tamanho efetivo de janela" depende do modelo e da tarefa; reporte sempre o experimento, não o número nominal.
- Algumas afirmações que circulam em blogs (por exemplo, que "tool results podem consumir 50.000 tokens antes do agente ler a request", atribuída à Cognition) não puderam ser verificadas em fonte primária no momento desta redação — trate como ilustração qualitativa, não como número auditado.