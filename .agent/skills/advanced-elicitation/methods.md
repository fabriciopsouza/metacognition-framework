# methods.md — Catálogo de Métodos de Elicitação Avançada

> Companion do `advanced-elicitation/SKILL.md` (ADR-003 / ADR-081).
> Carregar sob demanda — não em toda ativação da skill.
> Fonte (#1–#69, fase convergente): integração externa seletiva — proveniência completa em **ADR-081**.
> Fonte (#70–#76, fase divergente): proveniência em **ADR-085** (forma agnóstica → núcleo). **Confiança:** descrições/output_pattern são [INFERIDO] do resumo da fonte (primária não lida integralmente); a fonte lista 28 de 36 técnicas — as 8 restantes são [DESCONHECIDO] e não foram importadas.
> Fonte (#77, calibração de parâmetros): proveniência em **ADR-085 (C)** (veículo dados/análise → forma agnóstica no núcleo). [INFERIDO] do método generalizável da fonte.
> **Nota de nomenclatura:** nomes dos métodos mantidos em inglês (nomes próprios de técnicas com uso estabelecido na literatura). Restante do framework segue português conforme glossário.

## Como usar este catálogo

1. Analisar o tipo de conteúdo e o objetivo do enriquecimento
2. Filtrar por `categoria` relevante
3. Ler `output_pattern` para saber o que o método produz
4. Selecionar 5 que mais se encaixam no contexto (não repetir categoria na mesma seleção)

---

## Tabela de métodos

| # | Categoria | Método | Descrição (quando/por que usar) | output_pattern |
|---|---|---|---|---|
| 1 | advanced | Tree of Thoughts | Explora múltiplos caminhos de raciocínio em paralelo, avalia e seleciona o melhor — ideal para problemas complexos com múltiplas abordagens válidas | paths → evaluation → selection |
| 2 | advanced | Graph of Thoughts | Modela o raciocínio como rede interconectada de ideias para revelar relações ocultas — ideal para pensamento sistêmico e padrões emergentes | nodes → connections → patterns |
| 3 | advanced | Thread of Thought | Mantém raciocínio coerente em contextos longos — essencial para RAG e consistência em análises extensas | context → thread → synthesis |
| 4 | advanced | Self-Consistency Validation | Gera múltiplas abordagens independentes e compara consistência — crucial para decisões de alto risco onde verificação importa | approaches → comparison → consensus |
| 5 | advanced | Meta-Prompting Analysis | Recua para analisar a estrutura e metodologia da própria abordagem — valioso para otimizar o processo de resolução | current → analysis → optimization |
| 6 | advanced | Reasoning via Planning | Constrói árvore de raciocínio guiada por modelo de mundo e estados-alvo — excelente para planejamento estratégico e decisões sequenciais | model → planning → strategy |
| 7 | advanced | Chain-of-Thought Scaffolding | Força passos intermediários explícitos antes de qualquer conclusão — previne saltos intuitivos que pulam lógica falha | premise → step → step → conclusion |
| 8 | advanced | Few-Shot Exemplar Priming | Fornece 2–3 exemplos trabalhados do padrão de raciocínio desejado antes da tarefa real — alinha formato e profundidade por demonstração | examples → pattern recognition → application |
| 9 | collaboration | Stakeholder Round Table | Reúne múltiplas personas para contribuições diversas — essencial para coleta de requisitos e soluções balanceadas entre interesses conflitantes | perspectives → synthesis → alignment |
| 10 | collaboration | Expert Panel Review | Monta especialistas de domínio para análise profunda — ideal quando profundidade técnica e revisão por pares são necessárias | expert views → consensus → recommendations |
| 11 | collaboration | Debate Club Showdown | Duas personas argumentam posições opostas enquanto moderador pontua — ótimo para explorar decisões controversas e encontrar meio-termo | thesis → antithesis → synthesis |
| 12 | collaboration | User Persona Focus Group | Reúne personas de usuário do produto para reagir a propostas e compartilhar frustrações — essencial para validar features e descobrir necessidades não atendidas | reactions → concerns → priorities |
| 13 | collaboration | Time Traveler Council | Você-passado e você-futuro aconselham você-presente — poderoso para ganhar perspectiva sobre consequências de longo prazo vs pressões de curto prazo | past wisdom → present choice → future impact |
| 14 | collaboration | Cross-Functional War Room | PM + engenheiro + designer atacam um problema juntos — revela trade-offs entre viabilidade, desejabilidade e viabilidade de negócio | constraints → trade-offs → balanced solution |
| 15 | collaboration | Mentor and Apprentice | Especialista sênior ensina junior enquanto junior faz perguntas ingênuas — aflorar pressupostos ocultos através do ensino | explanation → questions → deeper understanding |
| 16 | collaboration | Good Cop Bad Cop | Persona de suporte e persona crítica se alternam — encontra pontos fortes para construir e fraquezas para endereçar | encouragement → criticism → balanced view |
| 17 | collaboration | Improv Yes-And | Múltiplas personas constroem sobre ideias umas das outras sem bloquear — gera direções criativas inesperadas através de construção colaborativa | idea → build → build → surprising result |
| 18 | collaboration | Customer Support Theater | Cliente irritado e representante de suporte simulam para encontrar pontos de dor — revela frustrações reais do usuário e lacunas de serviço | complaint → investigation → resolution → prevention |
| 19 | collaboration | Six Thinking Hats | Rotacionar por seis modos (fatos, sentimentos, cautela, otimismo, criatividade, processo) para garantir que todos os ângulos sejam cobertos sem crosstalk | white → red → black → yellow → green → blue |
| 20 | collaboration | Delphi Method | Especialistas dão estimativas independentes, veem resultados anonimizados e revisam — converge para julgamento de grupo calibrado evitando viés de ancoragem | independent estimates → reveal → revise → converge |
| 21 | competitive | Red Team vs Blue Team | Análise adversarial ataque-defesa para encontrar vulnerabilidades — crítico para testes de segurança e construção de soluções robustas | defense → attack → hardening |
| 22 | competitive | Shark Tank Pitch | Empreendedor faz pitch para investidores céticos que questionam — testa viabilidade de negócio e força clareza sobre proposta de valor | pitch → challenges → refinement |
| 23 | competitive | Code Review Gauntlet | Desenvolvedores sêniors com filosofias diferentes revisam o mesmo código — aflorar debates de estilo e encontrar consenso sobre melhores práticas | reviews → debates → standards |
| 24 | core | First Principles Analysis | Remover pressupostos para reconstruir a partir de verdades fundamentais — técnica de ruptura para inovação e resolução de problemas impossíveis | assumptions → truths → new approach |
| 25 | core | 5 Whys Deep Dive | Perguntar "por quê?" repetidamente para chegar às causas raiz — simples mas poderoso para entender falhas | why chain → root cause → solution |
| 26 | core | Socratic Questioning | Usar perguntas direcionadas para revelar pressupostos ocultos e guiar descoberta — excelente para ensino e auto-descoberta | questions → revelations → understanding |
| 27 | core | Critique and Refine | Revisão sistemática para identificar pontos fortes e fracos, depois melhorar — verificação padrão de qualidade para rascunhos | strengths/weaknesses → improvements → refined |
| 28 | core | Explain Reasoning | Percorrer raciocínio passo a passo para mostrar como conclusões foram alcançadas — crucial para transparência | steps → logic → conclusion |
| 29 | core | Expand or Contract for Audience | Ajustar dinamicamente nível de detalhe e profundidade técnica para o público-alvo — adequar conteúdo às capacidades do leitor | audience → adjustments → refined content |
| 30 | core | Second-Order Thinking | Pensar além das consequências imediatas para antecipar efeitos cascata e implicações de longo prazo — essencial para decisões estratégicas | action → consequences → second-order effects → informed choice |
| 31 | core | Inversion Analysis | Inverter o problema perguntando o que garantiria o fracasso em vez de como ter sucesso — revela obstáculos ocultos e pontos cegos | goal → invert → failure paths → avoidance → solution |
| 32 | core | Problem Decomposition | Quebrar problema complexo em subproblemas independentes, resolver cada um, depois remontar — essencial quando a tarefa é grande ou emaranhada | whole → parts → solutions → reassembly |
| 33 | core | Analogy Mapping | Encontrar domínio paralelo bem compreendido e transferir sua estrutura ao problema atual — desbloqueia insight emprestando modelos mentais provados | source domain → mapping → target insight |
| 34 | core | Steelmanning | Construir a versão mais forte possível do argumento oposto antes de responder — constrói credibilidade e captura pontos cegos que o strawmanning perde | opposing view → strongest form → honest rebuttal |
| 35 | creative | SCAMPER Method | Aplicar sete lentes de criatividade (Substituir/Combinar/Adaptar/Modificar/Usar/Eliminar/Reverter) — ideação sistemática para inovação de produto | S→C→A→M→P→E→R |
| 36 | creative | Reverse Engineering | Trabalhar de trás para frente a partir do resultado desejado para encontrar o caminho de implementação — poderoso para alcance de metas | end state → steps backward → path forward |
| 37 | creative | What If Scenarios | Explorar realidades alternativas para entender possibilidades e implicações — valioso para planejamento de contingências e exploração | scenarios → implications → insights |
| 38 | creative | Random Input Stimulus | Injetar conceitos não relacionados para provocar conexões inesperadas — quebra bloqueios criativos através de pensamento lateral forçado | random word → associations → novel ideas |
| 39 | creative | Exquisite Corpse Brainstorm | Cada persona adiciona à ideia vendo apenas a contribuição anterior — gera combinações surpreendentes através de colaboração com restrição | contribution → handoff → contribution → surprise |
| 40 | creative | Genre Mashup | Combinar dois domínios não relacionados para encontrar abordagens novas — inovação através de polinização cruzada inesperada | domain A + domain B → hybrid insights |
| 41 | creative | Constraint Injection | Adicionar deliberadamente uma limitação artificial (orçamento, tempo, tecnologia) para forçar soluções novas — criatividade prospera sob pressão | add constraint → forced creativity → remove constraint → evaluate |
| 42 | creative | Morphological Analysis | Listar parâmetros independentes do problema, enumerar opções para cada um e combinar sistematicamente — garante não perder configurações não óbvias | parameters → options grid → combinations → evaluation |
| 43 | framing | Abstraction Laddering | Mover para cima ("por quê?") para clareza estratégica ou para baixo ("como?") para detalhe tático — garante que você está resolvendo na altitude certa | concrete ↔ abstract → right level |
| 44 | framing | Reframe the Question | Questionar se o problema declarado é o problema real — muitas vezes a pergunta em si está errada e um melhor enquadramento desbloqueia uma resposta fácil | stated problem → reframe → true problem → solution |
| 45 | framing | Stakeholder Lens Rotation | Adotar seriamente a visão de mundo de cada stakeholder para ver a mesma situação de forma diferente — revela cujas necessidades estão sendo ignoradas | perspective A → B → C → gaps found |
| 46 | learning | Feynman Technique | Explicar conceitos complexos de forma simples como se ensinando uma criança — o teste definitivo de verdadeiro entendimento | complex → simple → gaps → mastery |
| 47 | learning | Active Recall Testing | Testar entendimento sem referências para verificar conhecimento real — essencial para identificar lacunas | test → gaps → reinforcement |
| 48 | learning | Deliberate Practice Loop | Identificar sub-habilidade específica, treinar com feedback imediato, ajustar, repetir — melhoria direcionada supera repetição geral | isolate → drill → feedback → adjust → repeat |
| 49 | philosophical | Occam's Razor Application | Encontrar a explicação mais simples suficiente eliminando complexidade desnecessária — essencial para debugging | options → simplification → selection |
| 50 | philosophical | Trolley Problem Variations | Explorar trade-offs éticos através de dilemas morais — valioso para entender valores e decisões difíceis | dilemma → analysis → decision |
| 51 | research | Literature Review Personas | Pesquisador otimista + pesquisador cético + sintetizador revisam fontes — avaliação equilibrada da qualidade de evidências | sources → critiques → synthesis |
| 52 | research | Thesis Defense Simulation | Estudante defende hipótese contra comitê com diferentes preocupações — testa metodologia de pesquisa e conclusões sob pressão | thesis → challenges → defense → refinements |
| 53 | research | Comparative Analysis Matrix | Múltiplos analistas avaliam opções contra critérios ponderados — tomada de decisão estruturada com pontuação explícita | options → criteria → scores → recommendation |
| 54 | research | Source Triangulation | Exigir pelo menos três tipos de fontes independentes (quantitativo, qualitativo, especialista) antes de aceitar um claim — guarda contra viés de fonte única. **Alinha-se com CONFIRMADO/INFERIDO/DESCONHECIDO do metacognition.** | claim → source A → source B → source C → confidence rating |
| 55 | retrospective | Hindsight Reflection | Imaginar olhar para trás a partir do futuro para ganhar perspectiva — poderoso para revisões de projeto | future view → insights → application |
| 56 | retrospective | Lessons Learned Extraction | Identificar sistematicamente lições-chave e melhorias acionáveis — essencial para melhoria contínua | experience → lessons → actions |
| 57 | risk | Pre-mortem Analysis | Imaginar o fracasso futuro e trabalhar de trás para frente para preveni-lo — poderoso para mitigação de risco antes de lançamentos | failure scenario → causes → prevention |
| 58 | risk | Failure Mode Analysis | Explorar sistematicamente como cada componente pode falhar — crítico para engenharia de confiabilidade e sistemas safety-critical | components → failures → prevention |
| 59 | risk | Challenge from Critical Perspective | Fazer papel de advogado do diabo para testar ideias e encontrar fraquezas — essencial para superar pensamento de grupo | assumptions → challenges → strengthening |
| 60 | risk | Identify Potential Risks | Brainstorm de tudo que pode dar errado em todas as categorias — fundamental para planejamento de projeto e preparação de deploy | categories → risks → mitigations |
| 61 | risk | Chaos Monkey Scenarios | Quebrar deliberadamente as coisas para testar resiliência e recuperação — garante que sistemas lidem com falhas graciosamente | break → observe → harden |
| 62 | risk | Assumption Audit | Listar explicitamente TODOS os pressupostos subjacentes a um plano, classificar por confiança e impacto, stress-testar os mais fracos — previne construir sobre fundações frágeis | list → rate → stress-test → shore up |
| 63 | risk | Cascading Failure Simulation | Rastrear como a falha de um componente se propaga por dependências — revela acoplamento oculto e pontos únicos de falha | trigger failure → trace propagation → find amplifiers → decouple |
| 64 | technical | Architecture Decision Records | Múltiplas personas de arquiteto propõem e debatem escolhas arquiteturais com trade-offs explícitos — garante que decisões sejam bem fundamentadas e documentadas. **No metacognition: output vai para ADR formal.** | options → trade-offs → decision → rationale |
| 65 | technical | Rubber Duck Debugging Evolved | Explicar seu código para ducks progressivamente mais técnicos até encontrar o bug — força clareza em múltiplos níveis de abstração | simple → detailed → technical → aha |
| 66 | technical | Algorithm Olympics | Múltiplas abordagens competem no mesmo problema com benchmarks — encontra a solução ótima por comparação direta | implementations → benchmarks → winner |
| 67 | technical | Security Audit Personas | Hacker + defensor + auditor examinam sistema a partir de diferentes modelos de ameaça — revisão de segurança abrangente de múltiplos ângulos | vulnerabilities → defenses → compliance |
| 68 | technical | Performance Profiler Panel | Especialista em banco + especialista em frontend + engenheiro DevOps diagnosticam lentidão — encontra gargalos em toda a pilha | symptoms → analysis → optimizations |
| 69 | technical | Boundary & Edge Case Sweep | Testar sistematicamente extremos, zeros, nulls, máximos e incompatibilidades de tipo — captura as falhas que o pensamento happy-path sempre perde. **Complementa o edge-case-hunter do metacognition.** | inputs → boundaries → edge cases → failures found |
| 70 | divergente | Worst Possible Idea | Gerar deliberadamente as PIORES ideias possíveis e então inverter cada uma — destrava grupo travado removendo o medo de errar; a inversão de uma péssima ideia revela uma viável. Distinto do #31 (Inversion analítica): aqui a geração é o produto | problema → piores ideias → inverter → ideias viáveis |
| 71 | divergente | 100 Ideas | Forçar QUANTIDADE sob tempo (ex.: 100 ideias em 20 min) — a pressão de volume esgota o óbvio e empurra ao território não-óbvio; quantidade antes de qualidade, triagem depois | meta de volume → geração rápida → triagem posterior |
| 72 | divergente | Exaggeration | Ampliar um aspecto a proporções absurdas (10×, 1000×, infinito) — distorção de escala revela suposições e abre soluções que a escala "normal" esconde | aspecto → ampliar ao absurdo → insight → reduzir ao viável |
| 73 | divergente | Incubation | Afastar-se deliberadamente do problema após carregamento intenso — delega ao processamento não-consciente; retomar depois com captura imediata do que emergiu. Técnica de processo (temporal), não de conteúdo | imersão → afastamento → retomada → captura |
| 74 | divergente | Stream of Consciousness | Gerar sem parar e sem editar por período fixo — suspende o crítico interno que poda ideias cedo demais; separa geração de avaliação | tempo fixo → escrita contínua sem filtro → mineração posterior |
| 75 | divergente | Future Press Release | Escrever o anúncio do sucesso futuro como se já tivesse acontecido (data, manchete, resultado) — força concretude sobre o estado-alvo e revela o que precisa ser verdade. Distinto do #55 (Hindsight retrospectivo) e do #37 (What If hipotético): aqui o alvo é gerar a visão de sucesso concreta | data futura → manchete de sucesso → detalhes → requisitos implicados |
| 76 | divergente | Brainwriting | Ideação silenciosa e paralela antes de qualquer discussão, depois construir sobre as contribuições — evita ancoragem e dominância do primeiro/mais-alto. Distinto do #9 (Stakeholder Round Table, debate verbal): aqui a geração é silenciosa e precede a discussão. Combina com party-mode | rodada silenciosa → trocar → construir → convergir |
| 77 | core | Parameter Tuning Loop | Calibrar parâmetros de um sistema contra alvos quantificados: modelar matematicamente (planilha/simulação) → testar isolado → junto → em escala → medir vs alvo com **red-flags numéricos** (limiar de intervenção) → ajustar e iterar. Veículo dados/análise — agnóstico (economia, manufatura, software, processo). Recast registrado em ADR-085 (C) | intent → model → isolate→integrate→scale → measure vs target → red-flag → iterate |

---

## Fase: divergente × convergente (eixo de seleção)

O catálogo cobre duas fases ortogonais do pensamento — selecionar pela **fase certa** importa tanto quanto pelo método:

- **DIVERGENTE (gerar):** produzir muitas opções do zero, suspendendo o julgamento. Usar quando o artefato está **vazio ou raso** (poucas alternativas, pouca matéria-prima). Métodos: **#70–#76** (novos — ADR-085) + os criativos já existentes **#24, #35, #37, #38, #39, #40, #41**.
- **CONVERGENTE (refinar/validar):** estressar, criticar e selecionar sobre material **que já existe**. Usar quando há artefato a aprofundar. Métodos: **todo o restante** (#1–#23, #25–#34, #36, #42–#69).

**Regra de seleção por objetivo (determinística):** se o objetivo é **GERAR** (artefato vazio/poucas opções) → priorizar fase divergente. Se é **REFINAR/VALIDAR** (artefato existe) → priorizar fase convergente. Em dúvida ou trabalho longo: **divergir primeiro, convergir depois** (não misturar geração e crítica na mesma rodada — é o ponto de #74 Stream of Consciousness).

> **Não integrados (rejeição documentada, régua §0 — ADR-085):** *Dream Capture* e *Guided Imagery* — baixo rigor, não-mecanizáveis, output não-auditável; ficam de fora até haver caso que prove ganho. *Anti-Problems* foi absorvido por #70 (Worst Possible Idea); *Forced Connections* por #38/#40; *Round Robin/Brainwalking* (logística de grupo) por party-mode.

## Seleção rápida por objetivo

| Objetivo | Métodos recomendados |
|---|---|
| **Gerar ideias do zero (DIVERGIR)** | #71 (100 Ideas) · #70 (Worst Possible Idea) · #72 (Exaggeration) · #38 (Random Input) · #74 (Stream of Consciousness) |
| Validar premissas de um plano | #62 (Assumption Audit) · #57 (Pre-mortem) · #63 (Cascading Failure) · #30 (Second-Order) · #34 (Steelmanning) |
| Explorar decisão difícil/controversa | #11 (Debate Club) · #21 (Red Team/Blue Team) · #1 (Tree of Thoughts) · #4 (Self-Consistency) · #44 (Reframe) |
| Aprofundar spec/requirements | #54 (Source Triangulation) · #52 (Thesis Defense) · #7 (Chain-of-Thought) · #26 (Socratic) · #43 (Abstraction Laddering) |
| Inovar / explorar alternativas | #24 (First Principles) · #35 (SCAMPER) · #31 (Inversion) · #40 (Genre Mashup) · #41 (Constraint Injection) |
| Ganhar múltiplas perspectivas | #9 (Stakeholder Round Table) · #45 (Stakeholder Lens) · #12 (User Persona) · #10 (Expert Panel) · #14 (Cross-Functional War Room) |
| Analisar risco | #57 (Pre-mortem) · #58 (Failure Mode) · #63 (Cascading Failure) · #60 (Identify Risks) · #61 (Chaos Monkey) |
| Retrospectiva / lição aprendida | #55 (Hindsight) · #56 (Lessons Learned) · #25 (5 Whys) · #5 (Meta-Prompting) · #46 (Feynman) |
| Decisão arquitetural (técnico) | #64 (ADR multi-persona) · #66 (Algorithm Olympics) · #1 (Tree of Thoughts) · #4 (Self-Consistency) · #21 (Red Team) |
