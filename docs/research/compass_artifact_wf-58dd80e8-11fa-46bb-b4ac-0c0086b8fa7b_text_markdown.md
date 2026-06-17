# Arquitetura de "Skills" vs. Subagentes de Contexto Isolado para Papéis Profissionais Sob Demanda — Padrão de Produção em Claude.ai Projects e Claude Code

## TL;DR
- **Adote Skills (formato Agent Skills da Anthropic) como a espinha dorsal**: SKILL.md modulares com *progressive disclosure* (metadata-first → corpo → arquivos referenciados) são o padrão correto para instanciar papéis (SAP PP, MM, ABAP, UX/Tableau, Pythonista de previsão, analista pharma) sob demanda, porque carregam ~30–50 tokens por skill em repouso e expandem só o necessário; reserve **subagentes de contexto isolado** apenas para trabalho longo, paralelo ou potencialmente "sujo" (auditoria de 50 arquivos, varredura de logs, validações GAMP em massa).
- **Use uma camada de skills compartilhadas como Single Source of Truth (SSoT)** — `anti-hallucination`, `traceability`, `validation-gamp5`, `confidence-classification`, `output-format` — referenciadas (não copiadas) por cada skill de papel; isso elimina redundância, deixa a regra viva em um único arquivo versionado e satisfaz exigências de rastreabilidade do Art. 20 da IN 134/2022 ("Os requisitos do usuário devem ser rastreáveis durante todo o ciclo de vida") e do Art. 3º §3º da RDC 982/2025 (IA admitida desde que atenda "padrões técnicos de consistência, proteção de dados, rastreabilidade e validação técnica da Anvisa").
- **Diferença Claude.ai Projects vs. API/Claude Code**: em Projects o "skill" prático é o **system prompt + Project Knowledge** com RAG automático quando o conhecimento excede o contexto; em Claude Code/API existe sistema de Skills nativo com filesystem (`~/.claude/skills/`, `.claude/skills/`), subagentes em `.claude/agents/` e Agent Teams experimentais. **Preferência operacional**: prototipar em Projects, promover para Claude Code/API quando precisar de execução real de scripts, isolamento de contexto e auditoria reproduzível.

---

## Key Findings

### 1. Agent Skills é um padrão consolidado e aberto (não experimental)
Anthropic publicou o formato Agent Skills em outubro de 2025 e o tornou padrão aberto em 18 de dezembro de 2025. Em 48 horas a Microsoft o integrou ao VS Code e GitHub, e a OpenAI adicionou suporte em ChatGPT e Codex CLI; até março de 2026, 32 ferramentas haviam adotado o formato — incluindo Google Gemini CLI, JetBrains Junie, AWS Kiro, Block Goose, Cursor, Amp e OpenCode. O contrato é mínimo: uma pasta com um arquivo `SKILL.md` contendo YAML frontmatter (`name` ≤64 chars, `description` ≤1024 chars) mais markdown de instruções, opcionalmente com subpastas `scripts/`, `references/`, `assets/`.

### 2. Progressive disclosure: três níveis, três custos de token
Anthropic descreve três estágios:
- **Discovery (startup)**: só `name` + `description` de todas as skills entram no system prompt (~30–50 tokens por skill; medição pública do repositório oficial mostrou ~1.700 tokens para 17 skills).
- **Activation**: quando o modelo julga a skill relevante, lê o `SKILL.md` inteiro via bash/Read (mediana ~2.000 tokens; recomendação: corpo ≤500 linhas / ~5.000 tokens).
- **Execution**: arquivos referenciados (`forms.md`, `reference.md`, scripts) só são lidos sob demanda; scripts executados via bash gastam tokens apenas no output.

Isso é o que torna a abordagem escalável para dezenas de papéis sem inflar contexto.

### 3. Skills ≠ Subagentes ≠ MCP ≠ Slash Commands
A documentação oficial da Anthropic ("Skills explained") distingue claramente:
- **Skill**: capacidade/conhecimento procedimental injetado no contexto *atual*, on-demand, com auto-discovery por descrição. Funciona em Claude.ai, Claude Code e API.
- **Subagente**: instância Claude *separada*, com janela de contexto própria, system prompt próprio, lista de tools restrita e modelo opcionalmente diferente; devolve só um resumo ao pai. Disponível em Claude Code e Agent SDK (não em Claude.ai web).
- **MCP**: protocolo de conectividade com sistemas externos (Drive, GitHub, BD).
- **Slash command**: atalho determinístico iniciado pelo usuário.

A heurística produzida por Anthropic e cristalizada pela comunidade: *"Use Skills to teach expertise that any agent can apply; use subagents when you need independent task execution with specific tool permissions and context isolation."*

### 4. Context rot é arquitetural, não acidental
A pesquisa "Context Rot: How Increasing Input Tokens Impacts LLM Performance" da Chroma (Hong, Troynikov & Huber, julho de 2025) testou 18 modelos (GPT-4.1, Claude 4 Opus/Sonnet, Gemini 2.5 Pro/Flash, Qwen3) e mostrou degradação não-uniforme conforme tokens crescem, mesmo em tarefas triviais. O blog de engenharia da Anthropic "Effective context engineering for AI agents" (29/09/2025) consolida o ponto: contexto é recurso finito com retornos marginais decrescentes, e a disciplina é "finding the smallest set of high-signal tokens that maximize the likelihood of your desired outcome." Daí decorrem os patterns que Anthropic recomenda: just-in-time retrieval, compaction, tool-result clearing, structured note-taking, e *subagentes para isolar trabalho ruidoso*.

### 5. Orchestrator-worker (multi-agent research) é caro mas legítimo para tarefas breadth-first
O writeup "How we built our multi-agent research system" da Anthropic afirma textualmente: *"We found that a multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval."* O custo é consumo de tokens ~15× o de um chat — não usar para tarefas determinísticas ou de baixo valor.

### 6. Spec-driven development (SDD) é o caminho para construir skills auditáveis
Frameworks como GitHub Spec Kit, Kiro (AWS), BMAD-METHOD, OpenSpec convergem em um loop de quatro fases (Specify → Plan → Tasks → Implement) com EARS-style acceptance criteria. Aplicado à autoria de skills: especifique antes de escrever, com critérios de aceitação executáveis (binários, ordenados por importância, ≤5–15 por spec).

### 7. Regulação para IA em farma já existe — e exige rastreabilidade, versionamento e human-in-command
- **GAMP 5 Second Edition (2022)** introduziu **Apêndice D11** dedicado a AI/ML; em julho de 2025 a ISPE publicou o "GAMP® Guide: Artificial Intelligence" com 290 páginas (listagem oficial: ispe.org/publications/guidance-documents/gamp-guide-artificial-intelligence).
- **EMA Draft Annex 22** — publicado em 7 de julho de 2025 (adendo de seis páginas ao EudraLex Vol. 4), primeira regulação dedicada a IA em manufatura GMP; restringe modelos adaptativos/probabilísticos em aplicações críticas; workshop EMA agendado para 30/06–01/07/2026 está reavaliando o uso de GenAI/LLMs.
- **FDA Computer Software Assurance (CSA)** — guia final 24/09/2025 e atualização 03/02/2026 ("Computer Software Assurance for Production and Quality System Software"), alinhado à QMSR e ISO 13485:2016; aplica-se explicitamente a ferramentas AI/ML usadas em produção/QMS.
- **ANVISA**:
  - **IN 134/2022** — Art. 20: *"Os requisitos do usuário devem ser rastreáveis durante todo o ciclo de vida"*; Art. 33 §§1º–3º: *"As trilhas de auditoria devem estar disponíveis e devem ser passíveis de serem apresentadas em um formato compreensível... As trilhas de auditoria devem ser revisadas regularmente."*; Art. 34 (controle de mudança) e Art. 35 (revalidação periódica).
  - **RDC 657/2022** (SaMD, em revisão pela GGTPS em maio/2026; draft propõe "software adaptável" para IA de aprendizado contínuo com Predetermined Change Control Plan — PCCP — equivalente ao do FDA, ainda não publicado).
  - **RDC 982/2025** (28/07/2025, DOU 29/07/2025), Art. 3º §3º: *"O resultado baseado em modelos de Inteligência Artificial poderá ser utilizado como critério de gestão de risco, desde que atenda a padrões técnicos de consistência, proteção de dados, rastreabilidade e validação técnica da Anvisa."*
  - **CIOMS WG XIV sobre IA em farmacovigilância** (09/12/2025) — ANVISA participou da elaboração; nota oficial gov.br cita o diretor da Quinta Diretoria, Thiago Campos: *"A incorporação da inteligência artificial à farmacovigilância demanda rigor metodológico, transparência e governança robusta. O guia do CIOMS oferece uma base comum para que reguladores, desenvolvedores e pesquisadores adotem soluções tecnológicas de maneira responsável, alinhadas à proteção da vida e à segurança dos pacientes."*

### 8. Claude.ai Projects ≠ Claude Code: o que carrega quando
Em **Claude Projects**, o "contexto sempre-on" é o system prompt + arquivos da Project Knowledge; quando o conhecimento excede o limite de contexto, RAG é ativado **automaticamente** (Claude usa uma ferramenta interna "project knowledge search" para recuperar trechos relevantes — segundo o Help Center oficial, "RAG works with all Claude features, including web search, extended thinking, and Research"). Skills em Claude.ai são ativadas em **Settings → Capabilities → Skills** (Code execution and file creation precisa estar ON) e cada skill é enviada como um arquivo `.zip` contendo a pasta com `SKILL.md`. Em **Claude Code/API**, skills vivem em `~/.claude/skills/` (pessoal) ou `.claude/skills/` (projeto) e subagentes em `.claude/agents/`; um orçamento compartilhado de **25.000 tokens** limita o quanto skills reanexadas podem ocupar simultaneamente.

---

## Details

### A. Anatomia mínima de um SKILL.md de papel (production-grade)

```yaml
---
name: sap-pp-functional-consultant
description: >
  Conduz análise funcional de SAP PP (Production Planning) — BOM, work centers,
  routings, MRP runs, demand management, capacity planning. Use sempre que o
  usuário mencionar PP, planejamento de produção, MRP, BOM, ordens de produção,
  S/4HANA manufacturing, ou pedir desenho/troubleshooting de processos
  produtivos. NÃO use para temas de Materials Management (MM), Sales (SD),
  ABAP puro, ou Finance.
version: 1.3.0
owner: <equipe-responsável>
last_review: 2026-05-15
---

# SAP PP Functional Consultant

## Quando ativar
[gatilhos positivos + exclusões explícitas]

## Antes de responder, SEMPRE
1. Carregar skill compartilhada `traceability` (referência: `../_shared/traceability/SKILL.md`)
2. Carregar `anti-hallucination` (cobre: classificação de confiança, citação SAP Notes)
3. Para perguntas regulatórias-pharma, carregar `validation-gamp5`

## Fluxo de resposta
[passos numerados; ≤500 linhas no SKILL.md, resto em references/]

## Outputs obrigatórios
- Decisão / recomendação
- Fontes consultadas (SAP Help, Notes, OSS)
- Nível de confiança: ALTA / MÉDIA / BAIXA
- Versão da skill que produziu o output
```

A descrição segue a recomendação oficial da Anthropic (skill-creator): escrita em terceira pessoa, "pushy", com gatilhos positivos *e* exclusões — porque Claude tende a *under-trigger* skills. Convenção de nome em gerúndio (gerund) é a recomendação oficial para skills genéricas; para papéis-pessoa, o padrão `role-domain-seniority` (ex. `sap-pp-functional-consultant`, `data-scientist-fuel-forecasting`) é mais legível.

### B. Arquitetura de skills compartilhadas (SSoT) e router

```
.claude/skills/
├── _shared/                          ← núcleo SSoT, referenciado por todas
│   ├── anti-hallucination/SKILL.md
│   ├── traceability/SKILL.md         ← decisão→fonte→versão (IN 134/2022)
│   ├── confidence-classification/    ← ALTA/MÉDIA/BAIXA + critérios
│   ├── output-format/                ← estrutura padrão de entrega
│   ├── validation-gamp5/             ← CSV/GAMP 5/D11 (regulado)
│   └── metacognition/                ← seu framework, normalizado
├── _router/SKILL.md                  ← dispatcher (opcional)
├── roles/
│   ├── sap-pp-functional-consultant/
│   ├── sap-mm-functional-consultant/
│   ├── abap-developer/
│   ├── ux-data-viz-designer/
│   ├── tableau-senior-analyst/
│   ├── python-fuel-forecaster/
│   └── pharma-systems-analyst/
└── domains/                          ← skills horizontais reutilizáveis
    ├── seasonality-forecasting/
    ├── rpa-uipath/
    ├── sap-hana-sql/
    └── itil4-cobit/
```

Princípios:
1. **Single source of truth**: cada regra (ex. "como citar SAP Notes", "como classificar confiança") existe em **um** arquivo. Skills de papel **referenciam** via instruções "Load `_shared/traceability/SKILL.md` before answering" — Claude lê via bash, não duplica conteúdo.
2. **Router/dispatcher é opcional, não obrigatório**: a Anthropic explicitamente afirma que Claude faz o dispatch por *LLM reasoning sobre as descriptions*; routers explícitos (como o projeto `skill-router` de hussi9, com ~80% de acurácia em prompts compostos segundo seu próprio test harness) só ganham valor quando (a) você passa de ~50 skills, (b) precisa de decisões determinísticas auditáveis, (c) quer routing de modelo (Sonnet vs. Haiku vs. Opus) por etapa. Para 7–15 papéis, descriptions bem escritas bastam.
3. **Naming**: `role-domain-seniority` para papéis; gerúndio (`reviewing-bom`, `validating-csv`) para domínios; prefixo `_` para skills compartilhadas (mantém ordenação no topo do explorador).
4. **Composição via referência, não inclusão**: o corpo do SKILL.md de papel deve ter ≤500 linhas; tudo que é compartilhado vai em `references/` ou em outro SKILL.md.

### C. Decisão Skill vs. Subagente vs. MCP vs. Slash command

| Situação | Use | Por quê |
|---|---|---|
| Injetar especialização (papel) na conversa atual; output curto; precisa do contexto do usuário | **Skill** | Carrega só o necessário; reutilizável; auditável; sem overhead |
| Trabalho longo, ruidoso, paralelizável (varrer 100 arquivos, validar 50 BOMs, rodar testes) | **Subagente** | Contexto isolado; retorna só resumo; protege contexto-pai do "rot" |
| Acesso a sistema externo (SAP HANA, Tableau Server, Drive, banco) | **MCP** | Conectividade padronizada; credenciais geridas; combina com Skill ("Skill diz como, MCP conecta") |
| Atalho determinístico do usuário (`/csv-validate`, `/pp-bom-review`) | **Slash command** | UX rápida; pode invocar Skill + Subagente em pipeline |
| Trabalho multi-papel verdadeiramente paralelo, com handoff entre especialistas | **Agent Teams** (Claude Code, experimental) | Mailbox + task list compartilhada; custo ~15× chat, só justifica em escopos amplos |

Heurística operacional (consolidada pela comunidade e validada por Anthropic docs): "Use a skill when the work is short, runs on the same model, needs the parent's context, and benefits from being injected into an ongoing conversation. Use a subagent when the work is long-running, mechanical, repeatable, would pollute the parent context, or could safely run on a cheaper model."

### D. Token-economy: números concretos

- 17 skills da Anthropic em discovery custam ~1.700 tokens (≈100 tok/skill em descriptions detalhadas); corpo médio ~2.000 tokens; reference files: zero até serem lidos.
- Subagente: cada chamada inicia janela nova; consome o prompt mais o que ele explorar; **devolve só o resumo final ao pai** (este é o ganho).
- Multi-agent research system: ~15× tokens do chat; só vale para tarefas de pesquisa breadth-first.
- Claude Code: orçamento compartilhado de 25.000 tokens para skills reanexadas após compaction; mais antigas são descartadas.
- **Regra prática**: se a soma das descriptions de discovery passar de ~3.000 tokens, divida em plugins/marketplaces separados ou implemente router MCP-style com fuzzy match (carrega só skills com keyword-hit).

### E. Spec-driven creation de skills

Para cada nova skill, escreva primeiro um `SKILL.spec.md` (não confundir com SKILL.md) contendo:
1. **Outcomes**: o que o papel produz (ex. "análise de impacto de mudança em BOM com classificação de risco GAMP")
2. **Scope boundaries**: o que NÃO faz (exclusões → vão na description)
3. **Constraints**: regras inegociáveis ("sempre citar SAP Note ID", "nunca inferir tabela ABAP sem confirmar via SE11")
4. **Acceptance criteria** (5–15, binários, executáveis): ex. "responde com seção `Confiança:` em 100% das respostas", "cita ≥1 referência primária em respostas técnicas", "rejeita perguntas fora do escopo com mensagem padrão"
5. **Eval prompts**: 8–12 should-trigger + 8–10 should-NOT-trigger (especialmente near-misses), seguindo skill-creator
6. **Versionamento**: semver — patch para clarificações, minor para adições, major para mudanças de regras existentes — com `CHANGELOG.md` linkando cada mudança a ticket/fonte

Esse spec é o artefato auditável que o regulador (ou auditor interno ITIL/COBIT) verifica.

### F. Auditabilidade e governança para o lado regulado (pharma)

GAMP 5 D11, ANVISA IN 134/2022, RDC 982/2025 e CIOMS WG XIV convergem em cinco exigências práticas:
1. **Versionamento**: skills em git com semver; `version:` no frontmatter; `CHANGELOG.md` por skill ligando mudança→fonte→aprovador→data.
2. **Trilha decisão→fonte→versão**: cada output do agente deve carregar `(skill_version, model_id, sources_consulted, timestamp, run_id)`. Em Claude Code isso é trivial via hook `SubagentStop`/`PostToolUse` que appenda em `~/.claude/audit-log.jsonl`. Em Claude Projects, exija no system prompt que cada resposta termine com um bloco `## Trilha de auditoria` estruturado.
3. **Classificação de confiança/maturidade**: skill `confidence-classification` força ALTA (fonte primária verificável), MÉDIA (inferência sobre fontes), BAIXA (extrapolação) — alinhado à exigência do Art. 3º §3º da RDC 982/2025 sobre "consistência" e "validação técnica".
4. **Human-in-command**: explícito no system prompt e no SKILL.md de domínios críticos — qualquer decisão regulatória/GMP exige confirmação humana antes da execução (ex. mudança em sistema validado).
5. **Reprodutibilidade**: temperatura baixa + seed (onde disponível) + versão exata da skill + Project Knowledge versionada = mesmo input → mesmo output (com a ressalva de que Anthropic não garante determinismo total).

A combinação skill compartilhada `traceability` + skill `validation-gamp5` + hook de log atende, em conjunto, IN 134/2022 Arts. 20/33/34/35.

### G. Diferenças Claude.ai Projects vs. API/Claude Code (operacional)

| Aspecto | Claude.ai Projects | Claude Code / API |
|---|---|---|
| "Sempre-on" | System prompt + Project Knowledge (RAG automático se exceder contexto) | `CLAUDE.md` (project), `~/.claude/CLAUDE.md` (user) |
| Skill loading | Settings → Skills (upload .zip por usuário; Team/Enterprise: org-wide via Owner) | Filesystem: `~/.claude/skills/`, `.claude/skills/`, hot-reload sem restart |
| Subagentes | Não disponível | `.claude/agents/` com isolamento de contexto; opcional `isolation: worktree`, `background: true`, `model: haiku|sonnet|opus` |
| Execução de scripts | Code execution sandboxed (sem rede; sem `pip install` runtime) | Bash real, filesystem real, MCP real |
| Auditoria | Manual via bloco `## Trilha` na resposta | Hooks (`PreToolUse`, `PostToolUse`, `SubagentStop`) + log JSONL automático |
| Sharing | Personal / Shared / Organization (Team+) | git (project) ou plugin marketplace |

**Estratégia recomendada**: prototipe e itere em **Projects** (mais rápido, sem instalação local, ótimo para colaboração não-técnica); promova skills maduras para o **filesystem Claude Code** quando precisar de (a) execução real, (b) hooks de auditoria, (c) subagentes, (d) integração CI/CD via Claude Agent SDK.

### H. Exemplo concreto: quatro papéis, mesmo padrão

**Cenário**: usuário pede "Preciso revisar uma BOM nova de combustível na refinaria X, incluindo o impacto em MRP e validar conformidade." Sem skills: Claude generaliza. Com a arquitetura proposta:

1. **Discovery (~2 KB de tokens carregados)**: descriptions de 12 skills (7 papéis + 5 compartilhadas) já estão no system prompt.
2. **Activation**: a description de `sap-pp-functional-consultant` casa em "BOM/MRP/refinaria" → Claude lê o SKILL.md (~1.500 tokens). A do `pharma-systems-analyst` não casa, fica dormente.
3. **Composição**: SKILL.md instrui carregar `_shared/traceability`, `_shared/anti-hallucination`, `_shared/output-format` (~1.500 tokens adicionais).
4. **Execução**: Claude pergunta dados específicos, consulta SAP Help (via MCP, se conectado) ou cita fontes da Project Knowledge; produz resposta com seção "Trilha".
5. **Custo total**: ~5 KB de skill-context vs. ~30 KB se tudo fosse pré-carregado no system prompt.

**Adicionar 5º papel (`tableau-senior-analyst`)** custa: 1 pasta + 1 SKILL.md (~150 linhas) + 1 description (~80 tokens permanentes). Skills compartilhadas são reusadas sem mudança. Mesmo padrão serve `python-fuel-forecaster` (importa `domains/seasonality-forecasting`) e `pharma-systems-analyst` (importa `_shared/validation-gamp5`). **Não-SAP-específico por construção**.

**Quando vira subagente**: pedido "Audite as 200 BOMs em /imports/ contra a regra X" → o agente principal **delega** a um subagente `bom-bulk-auditor` (definido em `.claude/agents/`) que carrega `sap-pp-functional-consultant` como skill, processa em loop e retorna **só** o relatório consolidado.

---

## Recommendations

### Fase 1 — Fundação (1–2 semanas)
1. **Crie a pasta `_shared/`** com 5 skills mínimas: `traceability`, `anti-hallucination`, `confidence-classification`, `output-format`, `metacognition` (porte seu Metacognition Framework atual para este formato).
2. **Migre o Squad Framework para `roles/`** — cada "membro do squad" vira um SKILL.md de ~300–500 linhas, com referências para `_shared/`.
3. **Escolha o ambiente primário**: Claude.ai Projects para prototipação compartilhada com não-técnicos; um repo git para Claude Code/API quando precisar de execução real.
4. **Especifique antes de escrever**: para cada skill, um `SKILL.spec.md` com 5–15 critérios de aceitação binários.

### Fase 2 — Validação (semanas 3–4)
5. **Escreva eval-sets**: 8–12 should-trigger + 8–10 should-NOT-trigger por skill; rode o *description improver* do skill-creator da Anthropic para otimizar a description.
6. **Implemente hook de auditoria** (Claude Code): `PostToolUse` que loga `(timestamp, skill_versions_loaded, model, tools_used, sources, output_hash)` em `audit-log.jsonl` versionado.
7. **Validation skill GAMP**: para o lado pharma, encapsule em `validation-gamp5/` a referência a IN 134/2022, RDC 657/2022, RDC 982/2025, Apêndice D11, CSA — com checklists executáveis.

### Fase 3 — Escala (semanas 5–8)
8. **Adicione skills uma a uma** medindo (a) trigger rate, (b) over-trigger em near-misses, (c) tokens consumidos por sessão típica. Threshold: se discovery > 3.000 tokens, segmente em plugins/marketplaces.
9. **Introduza subagentes** apenas quando tarefa for: (i) longa, (ii) ruidosa, (iii) paralelizável, OU (iv) modelo mais barato (Haiku) basta. Não use subagente como "skill com outra cara".
10. **Quando router faz sentido**: passe a usar router explícito (estilo `skill-router` MCP) só ao cruzar ~30–50 skills ou quando precisar de decisões determinísticas para auditoria regulatória.

### Benchmarks que mudam a decisão
- Se a soma das descriptions ultrapassar **~3.000 tokens** → segmente bibliotecas (plugins).
- Se uma skill passar de **~500 linhas / 5.000 tokens** no `SKILL.md` → quebre em referências.
- Se o trigger rate em should-trigger queries cair abaixo de **~80%** (3 runs por query) → reescreva a description com mais gatilhos e exclusões.
- Se uma sessão típica de papel passar de **~20.000 tokens** sem necessidade → revise o quanto está sendo carregado upfront vs. progressively.
- Se um subagente devolve >2.000 tokens ao pai consistentemente → faltou compaction no prompt do subagente.

---

## Caveats

1. **EMA Annex 22 ainda é draft** (publicado em 7 de julho de 2025 como adendo de seis páginas ao EudraLex Vol. 4) e está em reavaliação no workshop multistakeholder de 30/06–01/07/2026; a posição original restringia GenAI/LLMs em aplicações GMP críticas, mas EMA agora "is seeking expert input on possible control and mitigation measures such as guardrails" — não trate como regra final.
2. **RDC 657/2022 está em revisão pela GGTPS** (maio/2026): o draft introduz "software adaptável" para IA de aprendizado contínuo e adota a abordagem PCCP do FDA, mas ainda não foi publicado; planeje com a versão atual e marcos para reavaliar.
3. **Agent Teams (Claude Code) é experimental** (requer `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, Opus 4.6+); não recomendado para produção regulada hoje. Subagentes simples já são estáveis.
4. **Reprodutibilidade total não existe** em LLMs comerciais mesmo com `temperature: 0`; o que se garante é traceability (mesma skill v1.2.3 + mesma fonte → output *substancialmente* equivalente). A CIOMS reconhece isso ao falar em "reprodutibilidade, mesmo em modelos estocásticos" — você documenta variação tolerável.
5. **Skills em Claude.ai personal são privadas por usuário**; compartilhamento org-wide exige plano Team/Enterprise e que o Owner habilite "Share with organization" em Organization Settings → Skills. Considere isso ao planejar adoção em equipe.
6. **Conflito de fontes notado**: muita literatura secundária (Gemini-style, blogs genéricos) trata "skills" e "subagents" como intercambiáveis. A Anthropic é explícita que NÃO são: skill = capacidade injetada na conversa atual; subagent = instância isolada. Sempre que houver dúvida, prefira docs.claude.com e o blog de engenharia da Anthropic.
7. **Router determinístico vs. LLM-routing**: Anthropic deliberadamente prefere LLM-routing (Claude escolhe via reasoning sobre descriptions); a comunidade construiu routers explícitos com ~80–90% de acurácia em prompts compostos. Para ambientes regulados onde o auditor pergunta "por que essa skill foi escolhida?", um router explícito com log estruturado pode ser preferível mesmo que sacrifique um pouco de flexibilidade.
8. **Brazilian energy/fuel + pharma no mesmo agente** é arquiteturalmente seguro porque skills isolam contextos, mas governança humana deve manter ambientes separados (Projects diferentes em Claude.ai; repos `.claude/` distintos em Claude Code) — para que vazamentos cross-domain sejam impossíveis e auditoria seja limpa.