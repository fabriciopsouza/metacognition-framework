# Relatório Descritivo — Framework Metacognitivo Agêntico (distribuição *premium*)

> **Natureza deste documento.** Relatório puramente descritivo e expositivo. Não emite juízo de valor, não critica, não refuta, não propõe melhoria. Objetivo: registrar e explicar *o que* o framework é, *o que faz*, *como faz*, *para que serve* e *em que se baseia*, documento por documento e funcionalidade por funcionalidade — de forma que possa subsidiar estudo, artigos, aprofundamento e futuras sessões de crítica/melhoria.
>
> **Fonte primária.** Repositório `github.com/fabriciopsouza/metacognition-framework-premium` (branch `main`), lido via `raw.githubusercontent.com` em 01/06/2026. Versão declarada no `README.md`: **1.35.0**. Licença: **CC BY 4.0**. Idioma do framework: **PT-BR**. Autor declarado: Fabricio Souza.
>
> **Classificação de confiança deste relatório** (convenção do próprio framework): conteúdo marcado `[CONFIRMADO]` = lido diretamente nos arquivos do repositório; `[INFERIDO]` = derivado da leitura cruzada entre arquivos, sinalizado quando aplicável; `[DESCONHECIDO]` = arquivos referenciados que não foram lidos integralmente nesta varredura (listados na §12).

---

## 1. Visão geral — o que o framework é e o que se propõe a resolver

O framework se descreve como **"um núcleo adaptável para orquestrar agentes de IA"** — método + estrutura, não um "prompt esperto". `[CONFIRMADO]` A proposta central, conforme o `README.md`, é dar a agentes de IA (assentados sobre Claude Code) um conjunto de comportamentos governados:

- **Classificar o que sabem** e dizer "não sei" em vez de inventar (anti-alucinação).
- **Lembrar entre sessões** (digest + memória / handoff cross-sessão).
- **Recusar inchar** — toda adição passa por uma "régua de ganho líquido".
- **Passar por QA adversarial** entre cada etapa de trabalho.
- **Culminar em produto** — código, app, notebook ou pipeline, conforme o briefing.

O problema que se propõe a resolver, em síntese declarada pelos documentos: a tendência de agentes de IA a (a) **fabricar fatos/campos/parâmetros**, (b) **degradar em sessões longas** por saturação de contexto, (c) **executar ações irreversíveis** sem freio, (d) **produzir specs rasas** limitadas ao que o usuário já sabia pedir, (e) **inchar** com acúmulo de regras, e (f) **entregar fragmentos** em vez de produto utilizável. `[CONFIRMADO]`

### Princípio estruturante: agnosticismo estrito de domínio

Um princípio aparece repetido em quase todos os documentos (ADR-010 / Princípio 12): **o núcleo é estritamente agnóstico de domínio.** `[CONFIRMADO]` Linguagens, ferramentas, normas setoriais, regulamentações, padrões técnicos e regras de negócio são tratados como **aplicações/contextos** — *não* fazem parte do núcleo e *não aparecem hardcoded* em prompts, regras ou docs do framework (nem como exemplo, exceto em arquivos explicitamente rotulados como didáticos). O domínio é **declarado por projeto** pelo papel `discovery`. O que o núcleo oferece é mecanismo flexível: integridade de dados, trilha de auditoria, validação por risco, rastreabilidade e observabilidade.

### As três distribuições (fonte única)

Esta é a distribuição **premium**, parte de uma estratégia de "fonte única → três distribuições" (ADR-049, v1.35.0): `[CONFIRMADO]`

| Distribuição | Característica |
|---|---|
| **public** (baseline) | Distribuição flexível; aplicações de domínio vivem fora do núcleo. |
| **non-admin** | Variante sem hooks de PowerShell, para máquinas com restrição de scripts (GPO); gates declarados/aplicados *inline* pelo agente (ADR-047). |
| **premium** (esta) | Inclui a camada de "proposta proativa de produto" (blueprints de domínio) e canários internos; feature premium é marcada e *stripável* para gerar as baseline. |

O repositório canônico citado nos documentos é o `...-public`; o premium é um superconjunto marcado por blocos `<!-- premium:start ... premium:end -->`. `[CONFIRMADO]`

---

## 2. Arquitetura em camadas

O `README.md` descreve seis camadas: `[CONFIRMADO]`

```
ROTEADOR     AGENT-FRAMEWORK.md (v2.3)   decide o MODO (contexto × complexidade)
NÚCLEO       _shared/                    regras transversais (fonte única / SSoT)
PROCESSO     .agent/skills/              papéis flexíveis (pmo, discovery, architect,
                                         developer, qa-critic, docops, explorer, _template)
CONTRATO     docs/specs/                 requirements.md + validation.md (gate binário)
INFRA        _meta/                      isolamento de subagente, external-access, evals
APLICAÇÕES   exemplos/README.md          COMO criar aplicações (clonando _template)
```

A lógica de fluxo entre camadas: o **roteador** classifica a interação e escolhe o modo; o **núcleo** (`_shared/`) é a fonte única de toda regra transversal (ninguém recopia regra — todos referenciam); os **papéis** especializam o trabalho num pipeline; o **contrato** (`docs/specs/`) ancora os critérios de aceite binários; a **infra** provê mecanismos de isolamento e acesso externo; as **aplicações** de domínio vivem fora do núcleo, criadas por clonagem de um molde.

### Matriz de ambiente (mesma regra, mecanismo diferente)

O framework opera em dois tipos de ambiente, com paridade de regras mas mecanismos distintos: `[CONFIRMADO]`

| Recurso | Claude Code / SDK (IDE) | Chat web (Claude.ai / Gemini) |
|---|---|---|
| Ler `_shared/` via filesystem | sim | referência via contexto do Projeto |
| Isolamento real de subagente | sim | *hats* sequenciais simulados |
| Hooks OTel / auditoria | sim | checklist manual |
| Spec, roteamento por confiança, papéis | sim | sim |

No chat web não há filesystem nem subagentes reais; papéis e subagentes são **simulados** na mesma thread. Os princípios e resultados são declarados equivalentes; o que muda é o mecanismo de carga e enforcement.

---

## 3. O Roteador — `AGENT-FRAMEWORK.md` (v2.3)

**O que é / para que serve.** Ponto de entrada lógico do framework. Não redefine regras — **roteia**: classifica cada interação em dois eixos e escolhe o modo de operação. `[CONFIRMADO]`

**Como funciona — dois eixos de classificação:**

- **Eixo 1 — Contexto (tom):** casual/geral · perguntas simples/factuais · técnica criativa · **técnica (dados/dev/analytics/infra)**.
- **Eixo 2 — Complexidade:** *tarefa pontual* (1 arquivo/função/fórmula; <30 min; sem entregável) × *projeto multi-etapa* (>2 arquivos; >2 etapas com dependência; muda produção; ambiente declarado regulado).

**Regra de decisão:**
```
contexto ∈ {casual, factual, criativa}  → resposta direta (sem metacognição visível)
técnica E pontual                        → MODO METACOGNIÇÃO
técnica E projeto ≥3 sinais              → MODO SQUAD
dúvida                                   → metacognição; escalar p/ squad se exceder 2 turnos
```
Override explícito do usuário sempre vence o roteamento automático. `[CONFIRMADO]`

**Os dois modos:**
- **Modo Metacognição** (tarefas pontuais técnicas): aplica o método de 5 etapas (DECOMPOR → RESOLVER COM CONFIANÇA → CLASSIFICAR → VALIDAR → REFLETIR), cuja fonte única é `_shared/metacognition-core`.
- **Modo Squad** (projetos multi-etapa): orquestração de papéis num pipeline; roteamento por confiança (alta confiança operacional → fluxo linear orquestrador-trabalhador; baixa confiança/regulado → fluxo reflexivo multi-agente com hand-off bloqueado até revisão humana).

**Context engineering (seção 2.5 do roteador).** Trata contexto como recurso finito (*attention budget*). Fonte conceitual declarada: o artigo da Anthropic "Effective Context Engineering for AI Agents" (pesquisa A0). Quatro alavancas: `[CONFIRMADO]`
1. **Compaction por faixa medida** — disparada por ocupação medida (proxy `chars÷3` no chat; `/context` no IDE), com faixas 🟢<50% · 🟡50–69% · 🟠70–84% (digest+handoff) · 🔴≥85% (compactar). **A fonte marca explicitamente esses cortes como `[INFERIDO]` ajustáveis**, com "alarme de fumaça ±20–40%" e proxy `÷3` declarado conservador (intervalo ÷3–3,5) — não são limiares fixos.
2. **Structured note-taking** — gravar decisões/nomenclaturas/lições em arquivo persistente (`history.md`, glossário).
3. **Tool-result clearing** — limpar retornos volumosos de ferramenta já consumidos.
4. **Isolamento por subagente** — isolar subtarefas que poluem o contexto principal.

**Os 14 princípios não-negociáveis** (§6 do roteador): anti-alucinação; trabalho aprovado é permanente; validação antes de entregar; Acurácia≠Performance e Agregação≠Dimensão; single source of truth; loops de confirmação são falha; modo certo para tarefa certa; contexto é finito; override do usuário vence; **otimização líquida (ganho líquido)**; observação metacognitiva (captura de feedback); framework agnóstico (discovery declara escopo); arquitetura bicelular de QA; handoff cross-sessão obrigatório quando declarado. `[CONFIRMADO]`

---

## 4. O Núcleo SSoT — `_shared/` (fonte única das regras transversais)

O núcleo concentra as regras que todo papel referencia sem copiar. Cada skill tem `name`, `description` (com gatilhos de quando carregar/não carregar), `version`, `source` (a proveniência) e `last_review`. `[CONFIRMADO]`

### 4.1 `metacognition-core` (v1.2.0)
**Para que serve:** guarda o "COMO" do método que o roteador invoca. Contém: a **precedência de instruções** (7 níveis, do pedido explícito do usuário até output-style/persona, que nunca suplanta processo — ADR-028); a **cláusula anti-loop** ("Posso prosseguir?" 2× sobre o mesmo ponto = PARAR e avançar com premissa explícita); o **método de 5 etapas**; o protocolo de **checkpoint/transferência de chat**; e o **Pacote de handoff cross-sessão** (entregável obrigatório quando declarado — ADR-012), cujo teste binário é: "a outra sessão consegue começar sem perguntar nada de volta?". **Fonte declarada:** metacognição v2.2 + master prompt v4.1.

### 4.2 `anti-hallucination` (v1.0.0)
**Para que serve:** restrição absoluta de não fabricar dados, campos, estruturas, parâmetros ou comportamento de sistema. Procedimento quando não souber: declarar "NÃO SEI" direto; oferecer adjacente só se útil (com aviso de risco); sugerir onde validar. Anti-padrões a recusar mesmo sob insistência, incluindo **citar norma/spec sem checar vigência**. **Fonte:** master v4.1 §3.1 + SQUAD rule 02 + metacognição v2.2.

### 4.3 `confidence-classification` (v1.0.0)
**Para que serve:** única definição de classificação do ecossistema. Dois eixos: **origem** (`[CONFIRMADO]`/`[INFERIDO]`/`[DESCONHECIDO]`) e **grau** (ALTA 0,9–1,0 / MÉDIA 0,6–0,8 / BAIXA 0,0–0,5). "Gatilhos de tolerância zero" que exigem classificação sempre: nomes de tabela/campo/função/parâmetro, sintaxe exata, comportamento de versão específica, regras de negócio não confirmadas, valores monetários/prazos/métricas.

### 4.4 `output-format` (v1.0.0)
**Para que serve:** templates de saída por modo (casual; metacognição com tags `[ENTENDIMENTO]/[ABORDAGEM]/[SOLUÇÃO]/[VALIDAÇÃO]/[CONFIANÇA]`; squad com bloco YAML por papel) + o **checklist único de validação** (técnico: sintaxe, tipos, NULL, DIV/0, edge cases, agregação; lógico: magnitude, cross-check, reconciliação Total=Σpartes; visual: guia de leitura inline, cores acessíveis; test cases tabulados Normal/Zero/NULL/Negativo/Extremo). Inclui regra "anti over-formatting".

### 4.5 `traceability` (v1.0.0)
**Para que serve:** rastreabilidade + preservação. Quatro regras: **File-first** (ler antes de editar/referenciar/assumir — declarada "causa raiz #2 de retrabalho"); **Anti-rename** (não renomear nome aprovado sem ADR — "causa raiz #1"); **Preservação** de trabalho aprovado (mudança cirúrgica: O QUE SAI / O QUE FICA / ONDE ENTRA); **Cadeia de rastreabilidade** decisão→fonte→versão (parte do entregável em ambiente regulado).

### 4.6 `action-safety` (v1.0.0, ADR-014/015)
**Para que serve:** segurança de ações por **efeito**, não por intenção nem por nome de comando. **Base teórica citada:** Saltzer & Schroeder, NIST Zero Trust, OWASP C3 — princípio de *default-deny*. `[CONFIRMADO]` Argumento declarado: denylist por nome de comando é incompleta por construção (caso "JARVIS": `rm -rf ~/`); classificar pelo **efeito**, que é finito.
- **Predicados de efeito E1–E6:** E1 destrói dados irrecuperavelmente; E2 irreversível/não-idempotente; E3 externamente visível/sai do limite de confiança; E4 custa dinheiro/cria obrigação legal; E5 altera controles de segurança; E6 comportamento atípico/fora do escopo.
- **Tiers (efeito → autonomia):** T1 (reversível + baixo impacto) = autonomia; T2 (reversível + alto impacto, OU irreversível + baixo impacto) = ask/log; **T3 (irreversível + alto impacto) = gate humano obrigatório, default-deny, nunca auto-aprovável**. Dúvida T2/T3 → tratar como T3.
- **Calibração de fadiga de aprovação:** declara que ~93% dos prompts são aprovados no automático ("rubber-stamping", atribuído a telemetria Anthropic); a orientação é minimizar fricção em T2 e reservar o prompt para T3.

### 4.7 `high-stakes-gate` (v1.0.0)
**Para que serve:** validação por risco em tarefas de alto risco (decisão irreversível, ambiente regulado, número que vai a decisão executiva, mudança em produção crítica). Exige: validação por risco (critérios binários no `validation.md`), audit trail, logs imutáveis quando aplicável, e **HITL (human-in-the-loop)** com hand-off bloqueado. **A carga é DECLARADA pelo discovery do projeto** (ADR-010), nunca inferida por sinais semânticos; o núcleo nunca cita norma específica. **Fonte:** pesquisa A3 (governança/validação por risco) + A2 (HITL).

### 4.8 `execution-modes` (v1.7.0, ADR-005)
**Para que serve:** define os 3 níveis de execução do framework (regime de autonomia do shell), com **ratchet forward-only** (escalar é livre; descer só por edição manual do state file). `[CONFIRMADO]`

| Modo | `defaultMode` | Allow shell | Ask | Deny | Quando usar |
|---|---|---|---|---|---|
| **default** | prompts | só Read/Edit/Write | git push/merge/pr | destrutivo robusto (20 regras) | produção, mudança irreversível, regulado |
| **avançado** | prompts | + bare Bash/PowerShell | git push/merge/pr | destrutivo robusto | desenvolvimento ativo |
| **autosuficiente** | `bypassPermissions` | tudo | (ignorado) | mínimo (guard-rails absolutos) | iteração intensa, automação isolada |

Estado em `~/.claude/framework-mode.json`; algoritmo detalhado de merge ao `settings.json` global com backup obrigatório, validação de JSON e rollback. Inclui regra anti-downgrade *binding* (o próprio agente não pode oferecer downgrade mesmo a pedido) e lista de falhas conhecidas (corrupção de settings, state drift, crossover Bash↔PowerShell).

### 4.9 `observability` (v1.0.0, ADR-017)
**Para que serve:** rastreabilidade auditável ponta a ponta. O que capturar por execução (prompt, tools, parâmetros, retornos, modelo/versão, tokens, latência, árvore multi-agente, `spec_sha`). **Campos OTel GenAI** citados (`gen_ai.usage.input_tokens`, `gen_ai.agent.name`, `error.type`). Hook de auditoria PostToolUse logando `audit-log.jsonl`. Inclui a **telemetria mínima de processo** (ADR-017): 17-A *blame-attribution* (junção de origem de rewind; rounds de QA) e 17-B *tally + classe + poda Chesterton* (uso de regra ao longo de sessões; classes `salva-vidas`/`operacional`/`andaime`; poda só de `andaime` após N sessões sem disparo). **Fonte:** pesquisa A3 (OTel GenAI) + A2.

### 4.10 `doc-intake` (v1.0.0, ADR-029)
**Para que serve:** ingestão **determinística** de documentos (pdf/docx/xlsx/pptx/md/txt) → texto + chunks + manifesto JSON com sha256, **offline e sem embeddings**. Ferramenta: `tools/doc_intake.py`. Cada afirmação derivada de documento cita proveniência (id do chunk + sha256) — sustenta file-first e anti-alucinação. Não é OCR (PDF imagem-only → "vazio" declarado como gap). Não é RAG-vetorial (declarado fora de escopo, ADR futuro). **Fonte:** ADR-029.

---

## 5. Os Papéis de Processo — `.agent/skills/`

Os papéis são *skills* flexíveis. Cada um declara `role_order`, `consumes`, `produces`, `pass_criteria` (binário), `confidence_required` e `shared_refs` (quais skills de `_shared` carrega). No IDE são subagentes/hats; no chat web são *hats* sequenciais simulados. `[CONFIRMADO]`

### 5.1 `pmo` (orquestrador, role_order 0)
Ponto de entrada padrão. Orquestra e delega — **nunca escreve código de produção**. Sequência: ler AGENTS.md → rules → briefing → history; reformular o pedido em 1 frase; classificar afirmações; decidir (claro → delegar; ambíguo → UMA pergunta). Aplica junction-critic adversarial em J0–J3. Em **J6 (ADR-045)** é o "maestro de bloco": após o process-critic aprovar um bloco, toma **uma** decisão de re-orquestração registrada no `history.md`.

### 5.2 `discovery` (elicitação profunda universal, role_order 1)
O papel mais extenso e distintivo. **Para que serve:** combater a *spec rasa* — aquela limitada ao que o usuário lembrou de pedir. Faz elicitação profunda (lotes temáticos de perguntas, não uma) para extrair uma spec de nível sênior em **qualquer domínio**. `[CONFIRMADO]`

- **Método universal:** Natureza primeiro → decompor em 9 dimensões de spec (objetivo, stakeholders, funcional, não-funcional, dados, restrições, aceite, edge cases, fora de escopo) → perguntar em lotes → **etapa anti-raso obrigatória** ("o que um sênior deste campo levantaria que ainda não cobrimos?") → anti-alucinação (não-sabido vira `[DESCONHECIDO]` explícito).
- **Passo 6 — Escopo declarado pelo discovery (ADR-010):** dois modos. **Transcribe** (determinístico, quando o briefing declara nominalmente em ≥2 lugares, com stakeholder nomeado, sem contradição) ou **Interview** (default — 5 perguntas: (a) regulado/quais normas/vigência; (b) alto-risco; (c) regra com semântica; (d) gaps não-bloqueantes; (e) alimenta outra sessão → dispara handoff; (f) qual o `product_type`). Anti-vazamento cross-projeto.
- **Elicitação-consultiva de produto (ADR-033):** para produto recorrente, endereça dimensões universais (operador, interface, validação de entrada, escopo temporal, recortes, persistência, auditoria, ambiente, formato) recomendando um default sênior com trade-off, não pergunta em aberto. Gate mecânico: `check_spec_depth.py` deve passar antes do handoff J1.
- **Blueprint de domínio (premium, ADR-046):** quando o `product_type` casa um domínio com aplicação disponível, **propõe a forma premium do entregável de uma vez** (launcher/CLI, dicionário-contrato com auto-detecção+validação de arquivos, suíte de saída, auditoria).
- **Sub-modos (progressive disclosure, ADR-003 — carregados sob demanda via companion files):**
  - *Universal puro* (default).
  - *Revisar projeto existente* (`revisar-projeto-existente.md`).
  - *Mapeamento de processo* (v1.6.0, `mapeamento-de-processo.md`) — para processo de negócio (gatilhos/RACI/handoffs/exceções); filtro de entrada rejeita UI journey, runbook técnico, algoritmo, workflow de tool; escolhe profundidade (quick/standard/deep), notação (markdown/mermaid/swimlane) e formalidade (lean/BA sênior/BPMN 2.0); output em 3 arquivos (requirements, process-map-as-is com tags `[DECLARADO]`/`[OBSERVADO]`, gap-analysis).
  - *Pesquisa em cascata* (v1.7.0, `pesquisa-cascata.md`, ADR-007) — quando há pergunta de fundo sem fonte canônica e a resposta destrava decisão; pipeline de 9 passos (decompor → buscar via explorer → refletir → ramificar ≤2 rodadas → sintetizar → ataque anti-raso → fechar); output `research-brief.md`.
  - *Reforço sênior* (v1.8.0, `metodo-senior.md`, ADR-009) — overlay quando há fonte canônica/normativa citada; **9 passos auditáveis** (mapear fontes; verificar vigência; complementações; reconciliar cross-domain; pertinência; backlog de elicitação; classificar; pass adversarial; **coherence pass/RRC**). Output ganha 3 seções obrigatórias: Antecipações, Backlog de elicitação, Gaps não-bloqueantes.

### 5.3 `architect` (tech lead, role_order 2)
Decide e documenta — **não implementa**. Sequência: reler briefing/glossário/ADRs; listar ≥3 alternativas (uma pode ser "não fazer"); trade-offs; recomendar 1 com justificativa; gerar **ADR no formato MADR** (`docs/adr/NNN-titulo.md`). Critério de PASS: ADR com ≥3 alternativas, recomendação justificada e referência à spec.

### 5.4 `developer` (implementação, role_order 3)
Escreve/altera código, fórmula, script, query. Checklist antes de escrever: File-first, Glossário-first, ADR-first, Spec-first. Padrões: diff mínimo, tipos explícitos, NULL e DIV/0 tratados, edge cases, credenciais via env. Enforcement declarado: no IDE, hook `effect-gate` + managed-settings; no chat, auto-declarado (rotula E1–E6, exige confirmação T3). Saída sempre passa por qa-critic.

### 5.5 `qa-critic` (validação adversarial, role_order 4)
**Hipótese default = EXISTE BUG.** Valida contra o `validation.md`. **Protocolo de turno único (ADR-018):** STEELMAN → ATAQUE → VEREDITO binário. Alavanca declarada como a que "paga": **heterogeneidade de modelo** (rodar o qa-critic em família de modelo diferente do developer — atribuída a Zhang 2025). **Disparo condicional** (Self-Critique Paradox, atribuído a Snorkel 2025): forçar QA pesado onde o modelo já acerta derrubaria acurácia 15–40% — logo rotina de alta confiança usa validação técnica padrão, e ambíguo/irreversível/regulado usa QA reforçado + gate humano.
- **Duas modalidades (ADR-011):** *junction-critic* J4 (veredito `APROVADO_LIMPO`, iterações ilimitadas dentro da junção) e *process-critic* (revisa o bloco inteiro em 4 dimensões — lógica/código, spec/validation, doc-consistência, process-compliance — com poder de **rewind cascata** a qualquer junção anterior).
- **9 regras SE/ENTÃO determinísticas** derivadas de *method-audit* (≥2 ocorrências), aplicadas antes da revisão adversarial aberta — ex.: stale counts da mesma entidade; oxímoros; STATUS-field crescido; polish que vira bloco; exemplo de domínio em arquivo não-rotulado (viola Princípio 12); detecção-sem-RCA; artefato novo intra-bloco pós-J4; quantificador de escopo sem critério binário; mapeamento campo-fonte ambíguo (anti-viés-de-oráculo / anti-sicofância).

### 5.6 `docops` (documentação como código, role_order 5)
Fecha o bloco — nenhum bloco fecha sem doc proporcional. Sequência: CHANGELOG (Keep a Changelog + SemVer); dicionário de dados; glossário; README; marcar ADR "Aceito"; sincronizar spec (anti-drift). Roda o `consistency-gate` (ADR-030), gera o `execution-report` (ADR-038) e registra a decisão de re-orquestração J6.

### 5.7 `explorer` (auditoria read-only, role_order null)
Braço de leitura — varre, mapeia, audita; **nunca edita** (mesmo se a frase pedir "explorar e corrigir", só reporta). Princípio declarado (atribuído a pesquisa A1/A2): **paralelizar leitura, manter escrita single-thread**. Opera em contexto fresh isolado; devolve só o destilado classificado.

### 5.8 `_template` (molde — não ativar)
Molde para criar uma **aplicação** do framework (um domínio). Quatro passos: clonar; editar name/description (gatilhos + exclusões); listar skills de `_shared` a carregar; preencher só o domínio. As aplicações vivem fora do núcleo.

### Papéis emergentes (hats, sem skill nova)
`skill-librarian`, `evals-engineer`, `governance-lead`. Na distribuição de software (ADR-023), `ux-designer` e `evals-engineer` são ativados por `product_type`.

---

## 6. Arquitetura bicelular de QA — junções binárias e rewind (ADR-011)

Modelo central de controle de qualidade do modo squad. `[CONFIRMADO]` O fluxo (PMO → discovery → architect → developer → qa-critic → docops → release) tem **6 junções J0–J5** com artefato-gate e critério binário declarados, mais **J6** (PMO maestro, ADR-045):

- **Dentro da junção:** iterações ilimitadas até PASS binário (emendas no mesmo artefato via STATUS-field).
- **Entre junções:** forward-only após PASS (circuit-breaker contra loop eterno).
- **Process-critic adversarial** (qa-critic em subagente isolado): roda ao fim de cada bloco aprovado + on-demand + opcional em checkpoint; detém **rewind cascata** a qualquer junção anterior.
- **TODO QA é adversarial** (hipótese default = bug).
- **Política SUPLANTA × EMENDA:** mudança em §Decisão/§Alternativas de um ADR → SUPLANTA (novo ADR + "Substituído por"); mudança em §Implementação/§Consequências → EMENDA in-place via STATUS-field. Rounds dentro da junção = EMENDA (não contam como rewind).

---

## 7. Os arquivos load-bearing da raiz

### 7.1 `CLAUDE.md` e `AGENTS.md`
Pontos de entrada para o agente (Claude Code lê `CLAUDE.md` nativamente; `AGENTS.md` é o equivalente cross-tool). Mapeiam estrutura, regras invioláveis, modos de execução, modo non-admin, auto-boot global, régua de ganho líquido, e todas as ondas de evolução. Primeira ação obrigatória declarada: `/start-session` (ou "iniciar"). `[CONFIRMADO]`

### 7.2 `PROMPT-CHAT-WEB-v4.3.md`
**Para que serve:** a "encarnação" do framework para ambientes sem filesystem (Claude.ai, Gemini). Mesmos princípios, papéis e subagentes simulados. Contém protocolo de inicialização (web_fetch da URL canônica do roteador; fallback ao núcleo embutido), precedência, modos, princípios, workflow incremental, validação, formato e regra de manutenção cruzada. A §1 (identidade) e §5 (domínio) são **templates a customizar** — o prompt distribuído é agnóstico; alerta explícito contra distribuir com domínios de terceiros hardcoded (vazamento cross-projeto). `[CONFIRMADO]`

### 7.3 `LIMITS.md` ("honestidade mecanizada", ADR-044)
**Para que serve:** declarar o que o framework garante/prova e o que **não** faz. Cada capacidade tem status (✅ PROVADO / 🟡 PARCIAL / ⏳ EM DESENVOLVIMENTO) **derivado do canário** (teste) que a prova; `tools/build_limits.py --check` falha o CI se o doc divergir dos canários. Lista ~16 capacidades provadas (cada uma com seu canário e seu limite não-mecanizado). Seção "o que NÃO fazemos": não certifica conformidade; não mede tokens em tempo real (diz "NÃO MEDIDO"); não garante ausência de viés em casos novos; não promete detecção exaustiva; não substitui o gate humano. `[CONFIRMADO]`

### 7.4 `SECURITY.md`
**Para que serve:** postura de segurança honesta (mecaniza / recomenda mas não mecaniza / fora de escopo). Tese central: **não confiar no raciocínio do agente — gate por efeito, não por intenção.** Camadas mecanizadas: classificação de confiança + anti-alucinação; action-safety por efeito; `effect-gate` (hook PreToolUse que **só nega**, ativo em qualquer modo, inclusive bypassPermissions); `managed-settings` fail-closed (o agente não pode desligar os próprios guard-rails); modos de execução; high-stakes-gate; observabilidade; isolamento cross-projeto; QA adversarial heterogêneo. **Mapeamento ao OWASP Top 10 for LLM (2025):** LLM06 (Excessive Agency) marcado 🟢 forte (foco do framework); os demais 🟡/⚪ com ressalvas explícitas — declarado `[INFERIDO]` (auto-avaliação, não auditoria). Seção anti-prompt-injection separa o mecanizado (contenção por efeito) do recomendado (tratar conteúdo externo como dado) e do não-coberto (sanitização, exfiltração via tools permitidas). `[CONFIRMADO]`

### 7.5 `NOTICE` e `LICENSE`
`LICENSE`: CC BY 4.0. `NOTICE`: atribuição obrigatória ao autor e repositório canônico; autoria provada por histórico git, commits/tags assinados e a NOTICE; verificada por `tools/check_attribution.py` (guarda transparente, sem telemetria oculta — ADR-025 refuta explicitamente o "covert"). `[CONFIRMADO]`

---

## 8. Camada de mecanismo executável (hooks, gates e linters)

A "série prosa→mecanismo" deu par executável a regras críticas. Mecanismos citados nos documentos: `[CONFIRMADO]`

- **`effect-gate`** (`.ps1`/`.sh`, ADR-015) — backstop PreToolUse que nega T3 inequívoco; paridade `.ps1`↔`.sh` provada por canário (ADR-040).
- **`managed-settings`** (ADR-015) — fail-closed no caminho gerenciado do SO; `disableBypassPermissionsMode`, `allowManagedHooksOnly`.
- **`compaction-gate`** (PreCompact, ADR-021) — bloqueia compaction sem digest persistido.
- **`mission-gate`** (SessionStart, ADR-022) — declara/confirma `product_type` + escopo em `mission.md`.
- **`route-gate`** (UserPromptSubmit, ADR-027) — injeta lembrete de rota 1×/sessão (fail-open); motivado por incidente real (agente executou tarefa regulada sem rotear).
- **`ensure-global-wiring`** (ADR-027) — self-heal que reafirma a wiring global a cada abertura, derrotando "clobber".
- **`consistency-gate`** (ADR-030) — auditoria de fechamento fail-soft (version-sync, adr-status, checkpoint, unpushed).
- **`check-execution-mode.ps1`** + **`framework-sync.ps1`** (ADR-005) — disparo por hash.
- **Linters Python:** `check_core_agnostic.py` (ADR-020, varre o núcleo por termo de domínio), `check_spec_depth.py` (ADR-033), `check_completeness.py` (ADR-034), `check_field_mapping.py` (ADR-035), `check_input_contract.py` (ADR-046), `check_regulatory_coverage.py` (ADR-043), `check_reorchestration.py` (ADR-045), `build_limits.py` (ADR-044).
- **Ferramentas:** `doc_intake.py`, `execution_report.py`, `project_report.py` (ADR-026, relatório de tokens), `bootstrap.{ps1,sh,py}`.

Os canários (suíte `tools/test_*.py`) provam cada capacidade no CI; dois são internos (removidos da distribuição pública por reconstruírem fragmentos de token sensível). `[CONFIRMADO]`

---

## 9. Base de evidência e fontes/inspirações declaradas

O `guia/REFERENCIAS.md` consolida a bibliografia, com classificação `[CONFIRMADO]`/`[INFERIDO]`. `[CONFIRMADO]`

**Fontes primárias Anthropic (hub de engenharia):**
- *Building effective agents* (dez/2024) — padrões prompt chaining, routing, orchestrator-workers, evaluator-optimizer; "manter simplicidade".
- *Effective context engineering for AI agents* (set/2025) — attention budget, context rot, compaction, structured note-taking, sub-agentes → base da §2.5 do roteador.
- *How we built our multi-agent research system* (jun/2025) — multi-agente ~15× custo; paralelizar leitura.
- *Equipping agents with Agent Skills* (out/2025); *Claude Agent SDK* (set/2025); *Claude Code best practices* (abr/2025).

**Padrões abertos e convenções:** SemVer; Keep a Changelog; MADR (ADRs); EARS (sintaxe de requisitos, marcado `[INFERIDO]`); OpenTelemetry GenAI semantic conventions; formato Agent Skills `SKILL.md` (padrão aberto, agentskills.io). Para `action-safety`: Saltzer & Schroeder, NIST Zero Trust, OWASP C3, OWASP Top 10 for LLM.

**Pesquisas-base do projeto (A0–A3) — motor de evolução, declaradas no Project Knowledge:**
- **A0 — Fundamentos de Prompt e Context Engineering** → §2.5 do roteador, `metacognition-core`.
- **A1 — Arquitetura RAG Multiagente em Produção** → isolamento de subagente, explorer.
- **A2 — Desenvolvimento de Projetos com Agentes IA** + **Organização de Agentes Modulares** → spec-driven (validation.md), roles, eval-sets, SSoT por arquivo, progressive disclosure.
- **A3 — Governança de IA Não Determinística Regulada** → roteamento por confiança, high-stakes-gate, observabilidade/OTel.

**Citações acadêmicas pontuais nos skills:** Zhang 2025 (heterogeneidade de modelo no QA); Snorkel 2025 (Self-Critique Paradox); Cognition "Don't Build Multi-Agents" (jun/2025, escrita single-thread). `[CONFIRMADO]` O debate single-vs-multi-agente é registrado e resolvido na prática como "paralelizar leitura; manter escrita coerente em uma thread".

O `guia/COMO-FOI-CONSTRUIDO.md` documenta a proveniência do processo de construção. `[CONFIRMADO]`

---

## 10. Catálogo de ADRs (decisões arquiteturais registradas)

ADRs referenciados nos arquivos lidos (formato MADR). **Total: 47 ADRs distintos referenciados**, com **gaps de numeração confirmados em 008, 031 e 032** (varredura completa do repositório — esses números não aparecem em nenhum arquivo lido). Alguns ADRs estão marcados como propostos/futuros (048, 050). `[CONFIRMADO]`

| ADR | Tema (conforme citado) |
|---|---|
| 001 | Papel `discovery` + molde de subagente ocultado |
| 002 | Discovery sub-modo "mapeamento de processo" (v1.6.0) |
| 003 | Progressive disclosure via companion files |
| 004 | Auto-boot do squad via SessionStart hook |
| 005 | Modos de execução com ratchet por hash de hook |
| 006 | Auto-boot global com allowlist de owners |
| 007 | Régua §0 ganho líquido + pesquisa-cascata + aprendizado/WIP |
| 009 | Método sênior de discovery (domain-agnóstico) + auto-observação |
| 010 | Framework estritamente agnóstico + discovery declara escopo + anti-vazamento |
| 011 | QA bicelular: junções binárias forward-only + process-critic com rewind |
| 012 | Handoff cross-sessão obrigatório quando declarado |
| 013 | Contrato mínimo de skill |
| 014 | Allowlist por efeito (E1–E6 → T1/T2/T3) |
| 015 | Enforcement fail-closed (effect-gate + managed-settings) |
| 016 | Compaction por threshold medido + digest persistente |
| 017 | Telemetria mínima de processo + poda temporal |
| 018 | QA adversarial de turno único + heterogeneidade de modelo |
| 019 | Sync de repo no boot via hook |
| 020 | Linter de agnosticismo do núcleo (`check_core_agnostic`) |
| 021 | `compaction-gate` (PreCompact) |
| 022 | `mission-gate` (SessionStart) + `product_type`/`mission.md` |
| 023 | App `exemplos/dominio-software` (ux-designer + evals-engineer) |
| 024 | Comando `/start-session` |
| 025 | Atribuição transparente (refuta covert/telemetria oculta) |
| 026 | Relatório de tokens (`project_report.py`) |
| 027 | `route-gate` + `ensure-global-wiring` + disable-com-memória |
| 028 | Output-style ≠ processo (precedência nível 7) |
| 029 | `doc-intake` (parse determinístico, offline, sem embeddings) |
| 030 | `consistency-gate` (auditoria de fechamento) |
| 033 | Elicitação-consultiva de produto (banco agnóstico) |
| 034 | Completude (quantificadores do pedido) |
| 035 | Anti-viés-de-oráculo (mapeamento campo-fonte registrado) |
| 036 | Porta-do-usuário (sem TTY) + ambiente limpo |
| 037 | Overwrite-guard |
| 038 | Execution-report automático + token honesto |
| 039 | Effect-gate motor de regras por efeito (4+ famílias) |
| 040 | Paridade `.ps1`↔`.sh` provada na matriz CI |
| 041 | Anti-sicofância (erro plantado) |
| 042 | Discovery eval EXECUTADO (sai de design-time) |
| 043 | Cobertura regulada (denylist não-exaustiva + perfis clonáveis) |
| 044 | `LIMITS.md` mecanizado |
| 045 | PMO maestro — re-orquestração J6 |
| 046 | Blueprints de domínio + dicionário-contrato + ux-gate premium |
| 047 | Modo non-admin (gates anunciados, sem hooks PS) |
| 048 | (Proposto/futuro) execution-report automático só no privado |
| 049 | Três distribuições de fonte única (public · non-admin · premium) |
| 050 | (Proposto) elaboração de documentos premium (doc/pdf/pptx) |

*Observação descritiva:* os números **008, 031 e 032 são gaps de numeração** — não aparecem referenciados em nenhum arquivo do repositório (`[CONFIRMADO]` por varredura completa). Não há, nos arquivos lidos, registro de seu conteúdo ou de terem sido substituídos/abandonados.

---

## 11. Linha do tempo de versões (CHANGELOG)

O `CHANGELOG.md` (Keep a Changelog + SemVer; ~100 KB) registra cada release com a mudança → a fonte. Marcos principais: `[CONFIRMADO]`

- **v1.0.0** (23/mai/2026) — Consolidação dos Blocos 1–5 + correção "framework genérico vs aplicações".
- **v1.1.0–v1.4.0** (24/mai) — camada Claude Code, guias, prompt do chat web (v4.2), repo 100% genérico.
- **v1.5.0** (24/mai, ADR-001) — papel `discovery`.
- **v1.6.0** (25/mai, ADR-002/003) — sub-modo mapeamento de processo + progressive disclosure.
- **v1.7.0–v1.8.0** (26–27/mai, ADR-005/006) — modos de execução com ratchet; auto-boot global.
- **v1.9.0–v1.11.0** (27–28/mai, ADR-007/009/010) — régua de ganho líquido + pesquisa-cascata; método sênior; agnosticismo estrito + discovery declara escopo.
- **v1.12.0–v1.13.0** (29/mai, ADR-011/012) — QA bicelular; handoff cross-sessão.
- **v1.14.0–v1.20.0** (30/mai, ADR-013–020) — série "prosa→mecanismo" (contrato de skill; allowlist por efeito + enforcement; compaction por threshold; telemetria/poda; QA de turno único; sync de repo; linter de agnosticismo).
- **v1.21.0–v1.22.0** (30–31/mai, ADR-021–030) — hooks de runtime + entrega de produto; entrada determinística (route-gate, doc-intake, consistency-gate).
- **v1.23.0–v1.31.0** (31/mai, ADR-033–044) — "Remediação v2" (9 marcos): CI cross-platform; elicitação-consultiva; entrega vira produto; estabilidade de decisão; segurança de escrita; effect-gate motor; discovery eval executado; abrangência regulada; LIMITS mecanizado.
- **v1.32.0–v1.35.0** (01/jun, ADR-045–049) — PMO maestro J6; blueprints de domínio; modo non-admin; três distribuições de fonte única.

---

## 11-bis. Camada de contrato, processo, infra e aplicações (segunda passada)

Esta seção cobre os artefatos lidos na segunda varredura — a camada de **contrato** (`docs/specs/`), **workflows** (`.agent/workflows/`), **regras sempre ativas** (`.agent/rules/`), **infra** (`_meta/`) e **aplicações de exemplo** (`exemplos/`), completando o "cada documento" para além do núcleo e dos papéis. `[CONFIRMADO]`

### Contrato — `docs/specs/`
- **`_template/requirements.md`** + **`_template/validation.md`** — a spec atômica. O `validation.md` é declarado "o arquivo mais importante da spec": critério de aceite **binário** (cada item VERDADEIRO/FALSO), test cases obrigatórios tabulados (Normal/Zero/NULL/Negativo/Extremo), e regra de transição (tarefa = FINALIZADA só quando todos os critérios = VERDADEIRO; 3 reprovações → escalar). O qa-critic valida contra este arquivo. **Fonte:** pesquisa A2.
- **`_template/mission.md`** (ADR-022) — lar persistente do escopo declarado + `product_type` (campo inline `product_type: <ide-code | executable | gui-app | data-notebook | data-pipeline | research-code | report | spec | regulated>`), lido pelo hook `mission-gate`. Sem `product_type` declarado, o pipeline não avança a J2+ sem confirmação.
- **`_template-research/research-brief.md`** — output da pesquisa-cascata/método sênior (até 10 seções quando os dois se sobrepõem).
- **`_template-process/requirements.md`** — output do sub-modo mapeamento de processo.

### Workflows — `.agent/workflows/`
- **`/feature-plan`** — plano técnico: PMO confirma escopo+classe de confiança → cria spec atômica (sem `validation.md` não avança) → architect (3 alternativas + ADR que referencia a spec) → aprovação → `/implement` → docops.
- **`/handoff <papel>`** — transição entre papéis; encarna a **arquitetura bicelular** com a **tabela de gates J0–J6**:

| # | Junção | Artefato-gate | Critério binário | Quem aplica |
|---|---|---|---|---|
| J0 | PMO → discovery | STATUS-line PMO | natureza nomeada + dimensão + ambiguidade resolvida | PMO adversarial |
| J1 | discovery → architect | `requirements.md`/`research-brief.md` | requisitos classificados + aceite binário + (produto) `check_spec_depth` PASS | PMO adversarial |
| J2 | architect → developer | ADR `Aceito` | Aceito + ponteiro + alternativas + consequências | PMO adversarial |
| J3 | developer → qa-critic | commits + diff + testes | cobre todos REQ + sem regressão + RRC self-applied | PMO adversarial |
| J4 | qa-critic → docops | resultado adversarial | `APROVADO_LIMPO` | qa-critic subagente isolado |
| J5 | docops → release | `validation.md` do release | todos V1–Vn = PASSA | PMO + dono (HITL) |
| PC | process-critic final | revisão do bloco completo | LIMPO → merge/tag; senão rewind cascata | qa-critic subagente isolado |
| J6 | PMO re-orquestração | `RE-ORQUESTRAÇÃO:` no `history.md` | 1 decisão bounded entre blocos | PMO (maestro) |

  Invariantes: binário-com-iterações dentro da junção; forward-only entre junções; rewind cascata default. Declaração obrigatória antes de `/handoff B`: junção PASS + artefato-gate + evidência objetiva. "Não há atalho."
- **`/start-session`** (ADR-024), **`/implement`**, **`/checkpoint`** — abertura de sessão pelo PMO; implementação; save-point + RRC (não dispara process-critic automático por default).

### Regras sempre ativas — `.agent/rules/`
- **`04-confidence-routing.md`** — decide a arquitetura por classe de confiança: **alta confiança operacional** → orquestrador-trabalhador linear (validação unitária basta; otimizar com model cascading + cache semântico); **baixa confiança estratégica** (regulado/exposto/número executivo) → multi-agente reflexivo com subagente crítico obrigatório e hand-off bloqueado até revisão humana. Esclarece que o **QA-Critic sempre roda** (o que muda é a intensidade) e que **HITL é eixo separado**, governado por `execution-modes` (ADR-005), sem duplicação. **Fonte:** pesquisa A3.
- **`00-glossario.md`** — glossário de termos por projeto (preenchido pelo dono; ancora o anti-rename). `[CONFIRMADO existência]`

### Infra — `_meta/`
- **`subagent-isolation.md`** — quando um papel vira subagente com contexto isolado ("menor privilégio cognitivo"). O subagente recebe só o extrato relevante + tarefa + fragmentos afetados; começa fresh; não invoca outro subagente. Matriz de decisão isolar/não-isolar (custo ~15×). Candidatos naturais: qa-critic (evita viés de auto-aprovação) e explorer. Reafirma a heterogeneidade de modelo (Zhang et al. 2025, "Heter-MAD": heterogeneidade > número de papéis) e que o Conclave de 3 papéis foi reprovado (P6). **Fonte:** pesquisas A1/A2.
- **`external-access.md`** — padrão vendor-agnóstico de conectividade: "a skill diz COMO; o MCP conecta". Tabela Skill vs MCP vs Subagente vs Slash. Regras: credenciais nunca no prompt (via env/MCP); schema-first; validar o retorno; rastrear origem. **Fonte:** pesquisa A2.
- **`eval-template.md`** — template de eval-set de disparo por skill (8–12 should-trigger + 8–10 should-NOT) para garantir reprodutibilidade de roteamento; nota que Claude tende a sub-ativar skills (daí descrições "pushy"). **Fonte:** pesquisa A2 + skill-creator da Anthropic.

### Aplicações de exemplo — `exemplos/`
- **`dominio-software/`** (ADR-023) — única aplicação mantida no repositório, como "demonstração viva" da distribuição especializada em entrega de SW/dados. Adiciona dois papéis ativados por `product_type`: **ux-designer** (entrega `ux-spec`) e **evals-engineer** (entrega `eval-report` com gold-set). `governance-lead` e `skill-librarian` declarados **não criados** (cobertos pelo núcleo). Honra o contrato de 8 campos validado por `validate_skills.py`.
- **`dominio-regulado/`** (ADR-043) — catálogo de **perfis de conformidade clonáveis** (`compliance-profile-saude-dispositivo.json`, `-financeiro.json`, `-infosec.json`), arquétipos genéricos (ISO 13485/CLIA/21 CFR; SOX/Basel; ISO 27001/SOC 2), declarados explicitamente como **andaime de partida, não certificação**. Vivem fora do núcleo (mantêm `check_core_agnostic` verde).

---

## 12. Itens ainda não lidos integralmente `[DESCONHECIDO]`

Após as duas passadas, permanecem não lidos linha-a-linha:

- ADRs individuais em `docs/adr/NNN-*.md` (lidos por referência cruzada e via CHANGELOG, não pelo texto integral de cada um) — incluindo a verificação de **vigência/status** de cada um (ADR-048 e 050 marcados "Proposto"; os demais presumidos "Aceito" sem confirmação arquivo-a-arquivo).
- Companions do discovery `revisar-projeto-existente.md` e `mapeamento-de-processo.md`; `_shared/discovery/elicitation-dimensions.md`; `docs/specs/exemplos/` (exemplos didáticos rotulados).
- `tools/` — **código-fonte** dos hooks (`effect-gate`, `mission-gate`, `route-gate`, `consistency-gate`, `compaction-gate`), linters e canários `test_*.py`; arquivos de configuração `settings.json`, `settings.nonadmin.json`, `managed-settings.template.json`, `framework-schema.json`, `product-types.txt`.
- Guias: `INSTALAR-NO-VSCODE.md`, `SETUP.md`, `ORIENTACAO.md`, `GUIA-EQUIPE.md`, `GIT-VERSIONAMENTO.md`, `MODO-NON-ADMIN.md`, `RESILIENCIA-ACESSO.md`, `COMO-REVISAR-OUTRO-REPO.md`; site `guia/web/index.html`.
- Documentos de pesquisa A0–A3 e artefatos *compass* (vivem no Project Knowledge, fora do repositório — disponíveis no contexto deste Projeto, mas não auditados como fonte primária do framework nesta análise).
- Templates `dominio-processo/` e `dominio-projeto/` referenciados no discovery premium (ADR-046): os READMEs retornaram 404 na varredura (`[DESCONHECIDO]` se existem com outro path ou estão pendentes).

---

## 13. Síntese expositiva (mapa de uma frase por elemento)

- **Roteador (`AGENT-FRAMEWORK.md` v2.3):** classifica contexto×complexidade e escolhe metacognição ou squad.
- **`_shared/` (núcleo SSoT):** fonte única de anti-alucinação, classificação de confiança, formato/validação, rastreabilidade, segurança por efeito, gate de alto risco, modos de execução, observabilidade e ingestão de documentos.
- **Papéis (`.agent/skills/`):** pipeline PMO → discovery → architect → developer → qa-critic → docops, com explorer read-only e molde `_template`.
- **QA bicelular:** junções binárias forward-only + process-critic adversarial com rewind cascata; todo QA assume que existe bug.
- **Segurança:** gate por efeito (E1–E6 → T1/T2/T3), T3 com gate humano; effect-gate + managed-settings; OWASP LLM06 como foco.
- **Honestidade mecanizada:** `LIMITS.md` ancorado em canários que falham o CI se o doc mentir.
- **Entrega:** o framework "culmina em produto"; o que será entregue é declarado como `product_type` pelo discovery.
- **Distribuições:** uma fonte → public, non-admin, premium (esta).
- **Base:** pesquisas próprias A0–A3 + fontes primárias da Anthropic + padrões abertos (SemVer, MADR, EARS, OTel GenAI, OWASP, NIST, Saltzer & Schroeder).

---

*Relatório gerado a partir de leitura direta do repositório em 01/06/2026. Versão do framework analisada: 1.35.0. Documento descritivo, sem juízo de valor — destinado a subsidiar estudo, artigos e sessões posteriores de crítica e melhoria.*

*Rev. 2 (pós-QA adversarial): contagem de ADRs corrigida (47 referenciados; gaps 008/031/032 confirmados); faixas de compaction requalificadas como `[INFERIDO]`; adicionada §11-bis cobrindo a camada de contrato, workflows, regras, infra `_meta/` e aplicações de exemplo (segunda passada de leitura). Itens remanescentes em §12.*
