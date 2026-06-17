# Pesquisa em cascata: Desenvolvimento Agêntico Spec-Driven + Descoberta Autônoma para o desenho de um fluxo unificado

## TL;DR
- O padrão demonstrado no reel da **Cod3r Cursos** (Leonardo Moura Leitão, Fortaleza, fundador desde 2017, +380 mil alunos) — `.specs/` numeradas + `.claude/skills/` por camada + `EXECUTAR-TODAS.md` orquestrando "um sub-agente isolado por spec" — é uma **convenção didática** que combina três padrões já **[CONSOLIDADOS]** na engenharia agêntica: (a) **Spec-Driven Development (SDD)** ao estilo Kiro/GitHub Spec Kit (`requirements.md` → `design.md` → `tasks.md` + `constitution`), (b) **Agent Skills** da Anthropic (open standard com SKILL.md + progressive disclosure), e (c) **orquestração orchestrator-worker com contexto isolado por subagente** (Anthropic). Não localizei o reel específico em fontes indexadas (o conteúdo provavelmente está em material pago Udemy/Formação.DEV), mas a Cod3r mantém o curso "Claude Code com Subagentes" na Udemy, alinhado com a metodologia descrita.
- Para unificar o "Squad Framework" + "Framework de Metacognição" sem inflar com mega-prompts, o desenho mais defensável é um **pipeline de 5 fases com gates explícitos e modo de override**: (a) Descoberta/Enriquecimento (deep-research em cascata com query decomposition e reflexão), (b) Especificação (specs numeradas em EARS, constitution/steering imutáveis, skills como padrões reutilizáveis), (c) Orquestração (subagente isolado por spec **sequencialmente** quando há dependência, paralelo só para breadth-first independente), (d) Crítica QA-critic (verificador separado do implementador, gates de coerência cross-artefato), (e) Validação 1:1 + Rastreabilidade (memória estruturada Zettelkasten-like, audit trail ALCOA+ para ambiente regulado).
- A divergência **Anthropic (pró-multiagente) vs Cognition/Devin (anti-multiagente)** se resolve por critério de tarefa: **paralelo só para pesquisa breadth-first com baixa interdependência**; **sequencial single-thread para codificação com alta interdependência semântica entre passos**. O padrão do reel — "sub-agente isolado **por spec, sequencialmente**" — é, na prática, **mais próximo do Cognition do que parece**: cada sub-agente é single-thread; o multiagente está apenas no nível de orquestração entre specs, não dentro de uma spec.

## Key Findings

### 1. Fonte de inspiração — Cod3r Cursos (parcialmente confirmado)
- **Empresa**: COD3R Cursos Online (Fortaleza/CE, fundada em 2017). Fundador: **Leonardo Moura Leitão** (Mestre em Informática Aplicada pela UNIFOR, ex-Engenharia Elétrica/UFC), instrutor com +12 anos de docência e +380 mil alunos cumulativos segundo o próprio site cod3r.com.br.
- **Curso correlato confirmado**: "Claude Code com Subagentes: Monte uma Equipe de IA para Criar Aplicações" (Udemy). A descrição enumera papéis "Analista de Negócios, Arquiteto de Software, Desenvolvedor, Testador e Documentador Técnico" — o que é compatível com um fluxo SDD ainda que não probe a estrutura exata de pastas `.specs/`.
- **Não localizado em fontes públicas**: o reel/vídeo específico com a estrutura `.specs/` (subpastas `archive/changes/memory/shared/templates`), specs numeradas tipo `001-criar-projeto` e `EXECUTAR-TODAS.md`. Busca direta em Instagram/YouTube/Google retornou zero resultados verbatim para `"EXECUTAR-TODAS"` ou `"cod3rcursos" ".specs"`. **A convenção apresentada no reel é provavelmente original/proprietária da Cod3r e baseada nos padrões públicos abaixo.**
- **Veredito**: a inspiração é legítima e útil como referência de **forma**, mas todos os componentes técnicos têm equivalentes públicos mais maduros (Kiro, Spec Kit, Anthropic Agent Skills, subagentes Claude Code). Tratar o reel como referência didática, não como autoridade técnica.

### 2. Spec-Driven Development (SDD) — estado da arte

**[CONSOLIDADO] Padrões de artefatos numerados e fásicos.** Três tradições convergiram:
- **AWS Kiro** (kiro.dev/docs/specs/): trio `requirements.md` → `design.md` → `tasks.md` por feature, com EARS notation obrigatória nos requisitos, steering files em `.kiro/steering/`. Suporta modo "Quick Plan" que gera os três artefatos sem gates de aprovação para features bem-entendidas.
- **GitHub Spec Kit** (github.com/github/spec-kit): comandos `/speckit.constitution` → `/speckit.specify` → `/speckit.clarify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.analyze` → `/speckit.implement`. A pasta `.specify/memory/constitution.md` contém princípios imutáveis. Suporta presets (compliance, regulatory traceability, V-Model) e workflows YAML resumíveis com gates humanos.
- **Tessl/spec-as-source**: extremo onde o spec É o código-fonte (Martin Fowler classifica o espectro como spec-first → spec-anchored → spec-as-source).

**[CONSOLIDADO] Constitution / steering files como contexto imutável.** Kiro usa product.md/structure.md/tech.md; Spec Kit usa `constitution.md`. Ambos respondem ao problema de "agentes esquecem princípios entre sessões". O CLAUDE.md do Claude Code é a primitiva análoga (recarregado a cada sessão e após compaction).

**[CONSOLIDADO] EARS notation** (Easy Approach to Requirements Syntax) — desenvolvido por **Alistair Mavin, Philip Wilkinson, Adrian Harwood e Mark Novak (Rolls-Royce PLC, Derby UK)**, no paper *"Easy approach to requirements syntax (EARS)"* apresentado na 17ª IEEE International Requirements Engineering Conference (RE'09), 2009. Formato base: *"While [pre-condition], when [trigger], the [system name] shall [response]"*. Padrão usado por Airbus, Bosch, Honeywell, NASA, Rolls-Royce, Siemens. Vantagens documentadas para agentes: (1) elimina ambiguidade que LLMs preencheriam por conta própria, (2) gera critérios testáveis 1:1, (3) facilita decomposição automática para `tasks.md`. Kiro adota EARS por padrão no `requirements.md`.

**[EMERGENTE/EM DISPUTA] Generalidade do SDD.** Birgitta Böckeler (Distinguished Engineer, Thoughtworks), em *Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl* (martinfowler.com, 15/out/2025), observa criticamente após aplicar Kiro a um bug pequeno: *"it quickly became clear that the workflow was like using a sledgehammer to crack a nut. The requirements document turned this small bug into 4 'user stories' with a total of 16 acceptance criteria"*. ThoughtWorks Technology Radar (Vol. 33) coloca SDD em "Assess" com aviso explícito de *"bias toward heavy up-front specification and big-bang releases"*. **Implicação direta para o desenho do fluxo: o modo override/rápido NÃO é opcional — é estruturalmente necessário.**

**[CONSOLIDADO] Pasta `.specs` numerada sequencialmente** (001-…, 002-…) é apenas uma convenção de organização — Spec Kit faz isso em `.specify/features/001-feature-name/`. A numeração serve para (a) dependência explícita, (b) ordem de execução em scripts orquestradores tipo `EXECUTAR-TODAS.md`.

### 3. Orquestração multiagente e isolamento de contexto

**Anthropic (pró-multiagente para pesquisa breadth-first)** — *How we built our multi-agent research system* (anthropic.com/engineering/multi-agent-research-system, publicado em **13 de junho de 2025**): orquestrador (Opus) delega a subagentes (Sonnet) com janelas de contexto independentes. Resultado verbatim: *"We found that a multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval."* O custo declarado é **15× o de uma conversa chat normal**. Funciona porque cada subagente é um "filtro inteligente" que retorna síntese condensada.

**Cognition/Devin (anti-multiagente para codificação)** — *Don't Build Multi-Agents*, por **Walden Yan (Cognition), publicado em 12 de junho de 2025** (um dia antes da resposta da Anthropic): ações implícitas de cada subagente podem conflitar; subagentes paralelos não compartilham contexto, gerando "Mario+passarinho" desalinhados; preferir single-thread linear com compaction.

**Síntese técnica** (Phil Schmid, ZenML, fountaincity, ainews): os títulos são opostos mas as conclusões convergem — **multiagente para breadth-first com baixa interdependência (research), single-thread para depth-first com alta interdependência (coding)**. O padrão do reel ("um subagente isolado por spec, sequencialmente") respeita as duas escolas: cada spec é depth-first/single-thread; a orquestração entre specs é sequencial, não paralela.

**[CONSOLIDADO] Subagentes Claude Code (`.claude/agents/*.md`)**: cada subagente é uma instância Claude isolada com system prompt próprio, lista de tools própria, e janela de contexto fresca. *"Intermediate tool calls and results stay inside the subagent; only its final message returns to the parent"* (code.claude.com/docs/en/agent-sdk/subagents). O parent recebe **uma única string final**. Subagentes não podem spawnar outros subagentes. `isolation: worktree` cria um worktree git separado para isolar edits em paralelo.

**[CONSOLIDADO] Context engineering vs context rot** (Anthropic, *Effective context engineering for AI agents*): context é **recurso finito com retornos marginais decrescentes**; "attention budget" se esgota; *"lost in the middle"* (Liu et al. 2023); estratégias: **compaction, structured note-taking, sub-agent delegation, just-in-time retrieval**. Chroma Research (jul/2025) e Databricks confirmaram degradação começando ~32K tokens em modelos menores. Manus sugere "pre-rot threshold" de 128K–200K em modelos de 1M.

**[CONSOLIDADO] Padrão "orchestrator-worker"**: lead agent planeja e delega; workers executam em paralelo (breadth-first) ou sequencial (depth-first). Anthropic Research e Claude Code Agent Teams (experimental, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) implementam variantes.

**[EMERGENTE] Fork mode** (Claude Code, `CLAUDE_CODE_FORK_SUBAGENT=1`): primeiro request reusa o cache do parent → mais barato que spawn fresco quando o subagente precisa do mesmo contexto.

### 4. Skills / padrões reutilizáveis

**[CONSOLIDADO] Agent Skills (Anthropic, open standard desde dez/2025)**: pasta com `SKILL.md` (frontmatter YAML obrigatório: `name`, `description`; opcional: `allowed-tools`, `context: fork`) + `scripts/`, `references/`, `assets/`. **Progressive disclosure em 3 níveis**:
1. **Discovery** (startup): só `name`+`description` carregados (~30–50 tokens cada).
2. **Activation**: quando match com a tarefa, o body do SKILL.md é lido.
3. **Execution**: arquivos auxiliares (references/scripts/assets) carregados sob demanda.

Anthropic recomenda manter SKILL.md ≤ 500 linhas / ≤ 5K tokens. **Custo agregado típico (Anthropic skills oficiais)**: 17 skills ≈ 1.700 tokens no system prompt, ou seja, **dezenas de skills sem penalidade de contexto significativa**.

**Adoção cross-vendor**: OpenAI Codex CLI, Gemini CLI, GitHub Copilot, Cursor, Windsurf, Antigravity — todos suportam o formato.

**Quando usar skills vs subagents vs MCP vs slash commands** (síntese de Duet/varunbhanot/alexop):
- **Skill** = **HOW (procedural knowledge)**, auto-invocada por descrição, "como fazer X repetidamente".
- **Subagent** = **delegação com contexto isolado**, "quero que outro Claude faça isto sem poluir meu contexto".
- **MCP** = **conexão a sistema externo**, "preciso ler o GitHub/DB/API".
- **Slash command** = **trigger explícito do usuário**, "vou digitar `/x` para invocar".
- **Hook** = **automação em lifecycle event** (PreToolUse, SubagentStart, etc.).

Os "skills por camada" do reel (`backend-nest-controller`, `backend-prisma-repository`, `frontend-…`, `module-use-case`) são **padrões de código reutilizáveis no formato SKILL.md** — exatamente o caso de uso para o qual a Anthropic projetou skills (ver `addyosmani/agent-skills` e `obra/superpowers` no GitHub para exemplos de bibliotecas de skills SDD).

### 5. Descoberta / Deep Research autônomo

**[CONSOLIDADO] Padrão iterativo de 4 etapas atômicas** (Step-DeepResearch, ScholarGym, OpenAI Deep Research):
1. **Planning & Task Decomposition**: decompor query em sub-perguntas; conforme **Shen, Yang, Gu & Han, *ScholarGym* (arXiv 2601.21654, 18/fev/2026)**, *"iterative query decomposition yields 2.9–3.3× F1 gains over single-query retrieval"*.
2. **Deep Information Seeking**: search → read → reflect; multi-hop com backtracking.
3. **Reflection & Verification**: "is the answer definitive? if not, loop".
4. **Synthesis**: relatório estruturado com citações.

**[CONSOLIDADO] Clarification ANTES de spec**: padrão validado por Spec Kit (`/speckit.clarify`), Kiro (perguntas obrigatórias antes do `requirements.md`), Plan Mode do Claude Code (Shift+Tab = read-only exploration + clarifying questions). O spec-kit também usa marcadores `[NEEDS CLARIFICATION: specific question]` para forçar o agente a marcar ambiguidades em vez de inventar.

**[CONSOLIDADO] Research → Spec**: GitHub Spec Kit's `spec-driven.md` afirma *"Throughout this specification process, research agents gather critical context"*. Padrão: deep research alimenta `requirements.md`/`design.md` com evidências e referências.

### 6. Ciclo de qualidade / assertividade

**[CONSOLIDADO] Generator-critic separados**. Augment Code's *What Is Spec-Driven Development?* afirma textualmente: *"The most underused pattern in spec-driven development is assigning a separate agent to check the work rather than trusting the implementing agent to self-verify"*. Verificador separado tem sinal mais limpo; força spec a conter critérios de verificação explícitos; viabiliza paralelismo seguro (múltiplos implementadores + um verificador).

**[CONSOLIDADO] LLM-as-judge para evals**: OpenAI CriticGPT (catch LLM bugs in code), Shepherd, DEBATE (Scorer + Critic + Commander). Coeficiente de Pearson de até 0,85 com humanos em QA extractivo (Ho et al., abr/2025) vs 0,17 (exact match) / 0,36 (F1).

**[EM DISPUTA] Robustez de LLM-as-judge**: vulnerável a position bias, length bias, self-preference, prompt-injection (Combined Attack, PAIR — ASR alto). Mitigação: usar **judge de família diferente** do generator, prompts decompostos, expected-answer few-shot, e meta-eval periódico.

**[EMERGENTE] Self-Play Critic (SPC)** — fine-tune adversarial generator vs critic com RL; ProcessBench accuracy de 70,8 → 77,7%.

**[CONSOLIDADO] Spec Kit `/speckit.analyze`**: gate de coerência cross-artefato (spec ↔ plan ↔ tasks ↔ constitution) ANTES de implementar — pega duplicações, ambiguidades, contradições, e violações de princípios da constitution.

**[CONSOLIDADO] TDD/acceptance-criteria-driven**: Kiro inclui testes em `tasks.md` por padrão; Spec Kit gera tarefas de teste ANTES de tarefas de implementação. Addy Osmani (O'Reilly) recomenda **conformance suites** YAML-based como contrato executável da spec.

### 7. Memória e estado estruturados

**[CONSOLIDADO] Memória externa em arquivos** (Anthropic context engineering): `NOTES.md`, `memory/` folder, scratchpad. Claude Code 4.5 ganhou file-based memory tool em beta (out/2025). Padrão Claude Playing Pokémon: agente mantém maps, combat notes, training progress em arquivos lidos APÓS context resets.

**[EMERGENTE] A-MEM (Agentic Memory, NeurIPS 2025, Xu et al.)**: aplica princípios Zettelkasten — notas atômicas + links bidirecionais + evolução de memórias antigas quando novas chegam. Supera baselines em LoCoMo. **Risco crítico documentado**: propagação de erros — se LLM erra um link, atualizações futuras propagam o erro.

**[CONSOLIDADO] Estrutura "memory bank"** (Spec Kit `.specify/memory/`, Kiro `.kiro/steering/`, reel `.specs/memory/` + `.specs/shared/`): separa o que é **imutável** (constitution, princípios) do que é **dinâmico** (notas de sessão, decisões), e do que é **reutilizável cross-spec** (shared templates).

### 8. Modos de operação / override

**[CONSOLIDADO] Roteamento por complexidade**:
- Kiro tem **"Quick Plan"** explícito que gera requirements+design+tasks sem gates.
- Spec Kit suporta `quick: true` em workflows YAML e gates `type: switch`/`type: if` baseados em `inputs.scope`.
- Claude **Adaptive Thinking** (Sonnet 4.6/Opus 4.6) — modelo decide automaticamente quanto pensar; *"Claude evaluates the complexity of each request and determines whether and how much to use extended thinking"*.

**[EMERGENTE] DAAO / EvoFlow / A²Flow** (papers fev–nov/2025): geração dinâmica de workflows heterogêneos por difficulty-prediction. **Aplicabilidade imediata baixa** (acadêmico), mas o princípio é importante: *"workflows simples para queries simples, complexos para complexas"*.

**[CONSOLIDADO] Override do usuário**: o melhor padrão é (a) **default ao fluxo completo**, (b) flag explícita `--quick` / `--scope=fast` que pula gates não-críticos mas mantém spec + crítica mínima, (c) NUNCA pular o ciclo de crítica em produção regulada. Augment Code: *"if I'd be annoyed to have the agent interpret requirements differently than I meant, I write the spec"* — heurística simples para decidir.

### 9. Ambiente regulado (farmacêutico)

**[CONSOLIDADO] GAMP 5 2ª edição + Appendix D11** (ISPE, 2022, com GAMP AI Guide 2025) — estende validação a AI/ML; **dados de treino, prompts e outputs são todos GxP records** sob ALCOA+ (Attributable, Legible, Contemporaneous, Original, Accurate, Complete, Consistent, Enduring, Available).

**[CONSOLIDADO] FDA CSA final guidance (set/2025)** — endossa risk-based validation, substitui GPSV, aplica explicitamente a AI tools em manufacturing/quality.

**[EMERGENTE com peso regulatório] EU GMP Annex 22 (AI)** — primeiro regulamento GMP-específico para AI/ML; restringe aplicações GMP críticas a "static, deterministic AI models" (importante para arquitetar gates de governança — modelo travado em produção crítica vs. modelo livre em discovery).

**[CONSOLIDADO] EU GMP Annex 11 revisão (jul/2025)** — expande lifecycle, ALCOA+, cybersecurity, periodic review.

**Implicações diretas para o fluxo**:
- Cada spec, decisão de design, output do agente, resultado de crítica e validação **deve ser persistido com atribuição (user/agent ID), timestamp, hash de versão** → audit trail nativo.
- Span-level observability (OpenTelemetry / Langfuse / Arize) para rastrear cada tool call do subagente.
- Para aplicações regulated-critical, **congelar versão do modelo + prompts + skills** (model card + skill card + constitution version) para reprodutibilidade.

## Details — Mapeamento direto para o fluxo de 5 fases

### (a) DESCOBERTA / ENRIQUECIMENTO da demanda
**Objetivo**: transformar uma demanda vaga em compreensão de domínio antes da spec.
- **Subagente "Researcher"** em contexto isolado, com tool web_search/web_fetch + read-only no repositório.
- **Padrão cascata** (Step-DeepResearch / OpenAI Deep Research): decompõe → search → reflect → loop até answer definitivo.
- **Query decomposition** (2,9–3,3× ganho em F1 medido em ScholarGym, fev/2026).
- **Output**: `discovery/<id>-brief.md` com (1) intent, (2) sub-perguntas respondidas com citações, (3) lista `[NEEDS CLARIFICATION]` para humano.
- **Skill recomendada**: `discovery-cascading-research` (SKILL.md ≤ 200 linhas + references/) que orienta o padrão.
- **Gate**: humano aprova ou ajusta brief.

### (b) ESPECIFICAÇÃO
- Trio **requirements.md (EARS) → design.md → tasks.md** por spec, numeradas (001-, 002-, …) em `.specs/changes/`.
- **constitution.md** em `.specs/shared/` (princípios imutáveis: stack, padrões de código, regras GxP, política de testes).
- **Templates** em `.specs/templates/` (spec template, design template, task template, EARS scaffold).
- **Skills reutilizáveis** em `.claude/skills/` por camada/responsabilidade (`backend-controller`, `backend-repository`, `frontend-component`, `module-use-case`) — cada uma é um padrão de código, NÃO um subagente.
- **Critérios de aceite executáveis**: cada user story em EARS gera 1–N testes (conformance suite YAML quando aplicável).
- **Gate `analyze`**: rodar verificação cross-artefato (spec ↔ design ↔ tasks ↔ constitution) — análogo a `/speckit.analyze`.

### (c) ORQUESTRAÇÃO
- **Orquestrador (lead agent)** lê `EXECUTAR-TODAS.md` (ou equivalente) que lista specs em ordem topológica.
- Para cada spec, spawna **um subagente isolado** (`.claude/agents/spec-implementer.md` com `isolation: worktree` se houver risco de conflito de arquivos) com:
  - O conteúdo da spec (requirements/design/tasks).
  - As skills relevantes (auto-detectadas por progressive disclosure).
  - **Não** o histórico das specs anteriores — apenas resumos de outputs persistidos em `.specs/memory/`.
- **Sequencial** entre specs com dependência (regra geral em coding, conforme Walden Yan / Cognition).
- **Paralelo** apenas para specs comprovadamente independentes (regra Anthropic para breadth-first).
- **TodoWrite / TaskCreate** (Claude Code v2.1.142+) para tracking visível.
- Parent recebe **string final** por subagente (Anthropic SDK: *"Only its final message returns to the parent"*) → processamento intermediário fica naturalmente "escondido".

### (d) CRÍTICA / REVISÃO
- **Subagente "QA-critic"** SEPARADO do implementer (princípio Augment Code), idealmente em modelo de família diferente para reduzir self-preference bias.
- Avalia output da spec contra: (1) critérios de aceite EARS, (2) constitution, (3) conformance suite, (4) padrões de skill aplicáveis.
- **Output estruturado**: JSON com severidade (blocker/high/medium/low) — o critic **não corrige**, só sinaliza.
- **Gate**: orquestrador decide entre re-rodar a spec com feedback do critic, escalar ao humano, ou aceitar.
- **Para queries de eval em produção regulada**: meta-eval periódico do critic com human ground truth (combate context manipulation).

### (e) VALIDAÇÃO 1:1 + RASTREABILIDADE
- **Mapeamento 1:1** entre requirement EARS ↔ teste ↔ código ↔ commit.
- **Audit trail ALCOA+**: cada artefato persistido com `created_by` (agent ID + model version + skill version + constitution hash), `created_at`, `parent_artifact_id`.
- **Span-level observability** (OpenTelemetry para tool calls).
- **Memória estruturada** `.specs/memory/` no estilo Zettelkasten — notas atômicas por decisão, com links bidirecionais (mas **sem evolução automática** em ambiente regulado, para evitar a propagação de erros sinalizada pelo paper A-MEM).

### Onde entra o OVERRIDE
- Flag explícita do usuário (e.g., `/quick <demanda>`):
  - Pula a fase de Descoberta cascata (faz só clarification curta de 1–3 perguntas).
  - Gera os 3 artefatos em "Quick Plan" mode (sem gates de aprovação por artefato).
  - Mantém crítica mínima (apenas blockers).
  - Mantém audit trail.
- **Restrição obrigatória**: em ambiente regulated-critical, override desativa publicação em produção (entrega apenas a sandbox).

## Recommendations (acionáveis, em ordem de implementação)

1. **Adotar EARS em `requirements.md`** como linguagem-padrão dos critérios de aceite. Custo: 1 página de cheatsheet + 1 skill `requirements-ears-writer`. Benefício: critérios machine-testable e baixa ambiguidade.
2. **Codificar a "constitution"** do framework em arquivo único versionado (princípios do Squad Framework + regras do Framework de Metacognição imutáveis). Carregar como steering/CLAUDE.md.
3. **Mapear as skills do "Squad Framework" no formato Agent Skills da Anthropic** (SKILL.md + progressive disclosure). Targetar SKILL.md ≤ 500 linhas; mover detalhe para `references/`. Validar: pacote total ≤ 5K tokens no startup.
4. **Padronizar `.specs/<id>-<slug>/{requirements,design,tasks}.md`** com numeração sequencial e dependências declaradas no frontmatter de cada spec.
5. **Implementar o orquestrador `EXECUTAR-TODAS`** como slash command + script Python/Bash que (a) lê DAG de specs, (b) chama subagente por spec via Claude Code Agent SDK, (c) consome resultado final, (d) persiste em `.specs/memory/`.
6. **Separar Implementer de Critic em subagentes distintos** com system prompts opostos (Critic não tem permissão de Edit/Write). Definir thresholds: bloqueio em qualquer "blocker"; re-spec em ≥2 "high".
7. **Adicionar `/analyze` gate** entre specification e orquestração — verifica coerência spec↔design↔tasks↔constitution.
8. **Introduzir Discovery-phase opcional** (skill `cascading-research` + subagente isolated) **antes** de specs para demandas com domínio novo. Skip explícito em demandas operacionais conhecidas.
9. **Implementar modo override `--quick`** com defaults agressivos mas audit trail intacto — atende casos farmacêuticos operacionais de alto volume e baixa criticidade.
10. **Observability span-level** desde o dia 1 (Langfuse/OpenTelemetry/Arize) — é o que torna o fluxo auditável GAMP 5 / Annex 22 sem retrabalho.

**Benchmarks que mudariam as recomendações**:
- Se contagem de tokens por spec > 70% de 200K → reduzir verbosidade do `design.md`, mover para references.
- Se taxa de re-spec após critic > 30% → revisar constitution (provavelmente vaga demais ou contraditória).
- Se tempo médio por spec > 3× o equivalente humano → considerar single-thread (Cognition) em vez de subagente isolado.
- Se rate de "lost in the middle" detectado em outputs → reduzir CLAUDE.md (Anthropic: 150–200 instructions é o teto prático antes de degradação).

## Caveats

- **Fonte primária do reel não localizada publicamente**. A convenção exata (`.specs/archive|changes|memory|shared|templates`, `EXECUTAR-TODAS.md`) parece ser proprietária da Cod3r/Leonardo Leitão e não está em material indexado. Use as imagens do reel como referência visual, mas atribua os componentes técnicos às fontes públicas (Kiro, Spec Kit, Anthropic).
- **Hype vs comprovação**: o número "90,2%" da Anthropic vem de **avaliação interna não-pública** e é declaradamente acompanhado de **15× o custo em tokens**; tratar como upper bound, não como benchmark replicável. ThoughtWorks já sinaliza SDD em "Assess" — não está consolidado como prática default.
- **LLM-as-judge é vulnerável** a manipulação adversarial (PAIR, Combined Attack — Li et al., jun/2025); em produção regulada, exigir human-in-the-loop em decisões de aceite finais.
- **A-MEM/Zettelkasten para agentes** tem risco de propagação de erros documentado (Xu et al., NeurIPS 2025; análise crítica em alphasmanifesto.com, abr/2026); usar apenas para memória de pesquisa, NÃO para audit trail GxP.
- **TodoWrite mudou para TaskCreate/TaskUpdate** no Claude Code v2.1.142+ (jan/2026). O conceito é o mesmo, a API mudou.
- **EU Annex 22 ainda em draft** (status no fechamento desta pesquisa, mai/2026). Acompanhar para aplicações regulated-critical.
- **Subagentes não podem spawnar outros subagentes** no Claude Code — restrição arquitetural que limita profundidade da orquestração a 2 níveis (orquestrador → workers). Para hierarquias profundas, usar Agent Teams (experimental, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`).

**Pesquisas adicionais prioritárias** (em ordem) que ainda valem a pena para fechar o desenho:
  1. Caso de uso real de SDD em farma regulado (procurar publicações ISPE/AWS Life Sciences pós-2025; o post AWS *From spec to production: a three-week drug discovery agent using Kiro* é o melhor ponto de partida).
  2. Métricas comparativas single-thread vs multiagente para coding em SWE-bench/TerminalBench (LangChain reportou ganho de 25+ posições só mudando o harness — investigar para harness próprio).
  3. Padrão de "skill versioning" — Anthropic ainda não tem semver oficial; conferir spec atual em agentskills.io e proposta de SDD-skill no `gotalab/cc-sdd`.
  4. Integração de hooks Claude Code (`SubagentStart`/`SubagentStop`) com Langfuse/OpenTelemetry para audit trail automático ALCOA+.
  5. EU AI Act + Annex 22 — mapeamento exato de obrigações de "high-risk" para sistemas agênticos não-determinísticos em manufacturing farmacêutico.
  6. Validar empiricamente, dentro do projeto-piloto, se o curso "Claude Code com Subagentes" da Cod3r (Udemy) traz convenções adicionais úteis para confirmar/refinar a hipótese sobre a estrutura `.specs/` do reel.