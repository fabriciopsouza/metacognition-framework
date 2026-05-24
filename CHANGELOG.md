# Changelog — Refatoração do Framework Metacognitivo Agêntico

Formato: Keep a Changelog + SemVer. Cada mudança vincula-se à pesquisa que a sustenta.
Maturidade: [CONSOLIDADO] / [EMERGENTE]. Confiança: [CONFIRMADO] / [INFERIDO].

## Política

- **SemVer + Conventional Commits**: feature nova compatível → MINOR; correção sem
  feature → PATCH; quebra → MAJOR. Tag, número no `README.md` e nome do .zip sobem
  juntos a cada release. Detalhe em `guia/GIT-VERSIONAMENTO.md`.
- **Núcleo × aplicação**: o framework é genérico. Domínio (BI, regulado, contexto X)
  vive FORA do núcleo, criado clonando `.agent/skills/_template`. Ver `exemplos/README.md`.
- **Sincronia PROMPT-CHAT-WEB**: o `PROMPT-CHAT-WEB-v4.x.md` na raiz é a encarnação do
  framework para ambientes sem filesystem (Claude.ai, Gemini). Parte dos mesmos
  princípios e busca os mesmos resultados do núcleo. A cada release, revisar — e se
  necessário, bumpar a versão do prompt (v4.2→v4.3…) e registrar aqui.

## [1.0.0] — 2026-05-23 — Consolidação dos Blocos 1–5

### Bloco 1 — Núcleo `_shared/` (fonte única)
- **Added** 6 skills de núcleo desduplicadas dos 3 documentos existentes.
  Fonte: A2 (SSoT por arquivo) + princípio já declarado em v2.2 §6.6 / SQUAD Seção 1.
  [CONSOLIDADO] / [CONFIRMADO].
- **Changed** regras transversais: de triplicadas → referência única.
- **Preservado** conteúdo idêntico às fontes (rótulos, prefixos, categorias).

### Bloco 2 — Roteador Metacognição v2.2 → v2.3
- **Added** §2.5 Context Engineering nomeada (attention budget, compaction,
  structured note-taking, tool-result clearing, isolamento). Fonte: A0. [CONSOLIDADO].
- **Changed** precedência/anti-loop/5 etapas/checkpoint → referência a `_shared/`.
- **Changed** versão 2.2→2.3; nota de carregamento IDE vs chat web.

### Bloco 3 — Squad v1.1 → v1.2
- **Added** spec atômica (`docs/specs/_template/requirements.md` + `validation.md`,
  gate binário). Fonte: A2. [CONSOLIDADO].
- **Added** `_meta/subagent-isolation.md` (contexto fresh, menor privilégio).
  Fonte: A1/A2. [CONSOLIDADO].
- **Added** `.agent/rules/04-confidence-routing.md` (linear vs reflexivo por risco).
  Fonte: A3. [CONSOLIDADO].
- **Changed** `rules/01·02·03` → ponteiros para `_shared/` (dedup).
- **Changed** workflows `feature-plan` e `implement` → v1.2 com gate de spec +
  roteamento por confiança + validação contra `validation.md`.

### Bloco 4 — Master v4.1 → `roles/`
- **Added** `roles/tableau-senior-analyst`, `roles/python-fuel-forecaster`,
  `roles/pharma-systems-analyst`, `roles/_template`. Fonte: A2. [CONSOLIDADO].
- **Changed** master v4.1 superado: transversais→`_shared/`, domínio→`roles/`.
- **Fixed** conflito de domínio BI fragmentado (bi-sap vs §5) → casa única em roles.
- **Note** decisão de granularidade: 3 roles (premissa anunciada; reversível).

### Bloco 5 — Observabilidade + eval-sets
- **Added** `_shared/observability/SKILL.md` (OTel GenAI, audit hook, logs imutáveis).
  Fonte: A3. [EMERGENTE] / [CONFIRMADO].
- **Added** `_meta/eval-template.md` (should-trigger / should-NOT por skill).
  Fonte: A2. [EMERGENTE].

### Ressalvas de ambiente (transversais) [CONFIRMADO]
- Isolamento real de subagente, hooks e leitura de filesystem: só em Claude Code/SDK.
- Chat web: regras idênticas, mecanismos degradam para referência/manual.

### Pendências conhecidas
- `roles/aivi-indicator-analyst`: aplicação específica — aguarda as regras de
  "AIVI emergencial" (repo indisponível na sessão). [DESCONHECIDO].
- Versão do master prompt citava "v2.1" — corrigida no roteador para 2.3.

## [1.0.0-generico] — 2026-05-23 — Correção: framework genérico vs aplicações

### Changed (separação núcleo × aplicação)
- **Movido** `roles/tableau-senior-analyst`, `python-fuel-forecaster`,
  `pharma-systems-analyst` → `exemplos/` (são APLICAÇÕES, não núcleo). Fonte: A2
  (skill de papel ≠ domínio; manter simplicidade do núcleo). [CONFIRMADO].
- **Generalizado** `_shared/validation-gamp5` → `_shared/high-stakes-gate`
  (validação por risco + audit trail + HITL, agnóstico). Normas setoriais viram
  config de aplicação (`exemplos/regulated-pharma`). Fonte: A3. [CONSOLIDADO].
- **Papéis de processo** (pmo/architect/developer/qa-critic/docops) reescritos
  enxutos, referenciando `_shared/` — preservados em nome (anti-rename).

### Added (gaps da pesquisa, GENÉRICOS)
- `.agent/skills/explorer` — subagente read-only de exploração/auditoria. Fonte: A1/A2.
- `_meta/external-access.md` — padrão de conectividade MCP, vendor-agnóstico. Fonte: A2.
- `.agent/skills/_template` — molde para criar QUALQUER aplicação (escala por clonagem).
- `exemplos/README.md` — separa explicitamente aplicação de núcleo.

### Princípio reforçado
Núcleo agnóstico de domínio; específico nasce por clonagem. Sem roles especulativas
(antipadrão "tudo agente" / skill sprawl — pesquisa). [CONFIRMADO].

## [1.1.0] — 2026-05-24 — Camada Claude Code + guias de uso

> Correção de versionamento: as entregas anteriores foram indevidamente mantidas
> como 1.0.0. Conforme SemVer, features novas = MINOR bump. Consolidado aqui.

### Added (features novas desde 1.0.0)
- Camada nativa Claude Code: `CLAUDE.md` (raiz) + `.claude/agents/` + `.claude/skills/`.
- Subagentes isolados: `explorer` (read-only) e `qa-critic` + `_template`.
  Fonte: doc oficial Claude Code (skills em .claude/skills, subagentes em .claude/agents).
- `SETUP.md` (entrada, 3 modos: greenfield / revisar / migrar).
- `INSTALAR-NO-VSCODE.md` (instalação + remoção do antigo, passo a passo).
- `COMO-REVISAR-OUTRO-REPO.md` (multi-root + explorer).
- `aivi-indicator-analyst` (scaffold) + spec — exemplo de aplicação por clonagem.
- Eval-set executado dos papéis (`_meta/eval-results-papeis.md`, 33/33).

### Changed
- Versão do sistema: 1.0.0 → 1.1.0.

### Política de versionamento (registrada para não repetir o erro)
- Feature nova compatível → MINOR (1.x.0). Correção → PATCH (1.0.x). Quebra → MAJOR.
- O número da versão e o nome do arquivo .zip devem subir juntos a cada release.

## [1.2.0] — 2026-05-24 — Reorganização, referências, git e versão web

### Added
- `guia/` consolida toda a documentação humana (raiz fica enxuta).
- `guia/ORIENTACAO.md` — mapa de leitura humano × IA.
- `guia/GIT-VERSIONAMENTO.md` — git + SemVer + Conventional Commits + tags.
- `guia/REFERENCIAS.md` — bibliografia completa com links (fontes Anthropic
  verificadas, padrão Agent Skills, SemVer/Keep a Changelog/MADR, pesquisas A0–A3).
- `guia/web/index.html` — versão web single-file, offline, navegável.

### Changed
- Estrutura: guias humanos movidos para `guia/`. Mantidos na raiz só os arquivos
  load-bearing (CLAUDE.md, AGENTS.md, AGENT-FRAMEWORK.md, README.md, CHANGELOG.md, .gitignore).
- Referências cruzadas (README/SETUP/CLAUDE) atualizadas para os novos caminhos.
- Versão do sistema: 1.1.0 → 1.2.0 (features novas = MINOR, conforme política registrada).

## [1.3.0] — 2026-05-24 — Prompt do chat web (v4.2, híbrido)

### Added
- `guia/PROMPT-CHAT-WEB-v4.2.md` — instruções para o campo "Instruções para o Claude"
  (Claude.ai), alinhadas ao framework v2.3. Núcleo transversal inline; domínio
  RESUMIDO inline + detalhe no Project Knowledge (escolha: híbrido).
- §10 do prompt: REGRA DE MANUTENÇÃO CRUZADA — ao revisar regra de domínio, atualizar
  o resumo no prompt + o detalhe no Project + a aplicação em exemplos/. Evita divergência.

### Changed
- Corrigida a compatibilidade do prompt de chat: v2.1 (antigo v4.1) → v2.3 (v4.2).
- Versão do sistema: 1.2.0 → 1.3.0 (feature nova = MINOR).

### Nota de design
- v4.2 é uma APLICAÇÃO do framework para o ambiente de chat (sem filesystem; papéis
  simulados). O núcleo genérico no zip permanece a fonte única; o prompt o encarna inline.

## [1.4.0] — 2026-05-24 — Repo 100% genérico + drift fix + PROMPT-CHAT-WEB consolidado

> Distribuição do framework deixa de carregar aplicações específicas. Aplicações
> de domínio vivem **FORA do núcleo** a partir desta versão (criadas clonando
> `.agent/skills/_template` no repositório de cada equipe). Fonte: A2 (núcleo
> agnóstico de domínio; antipadrão "skill sprawl" evitado). [CONSOLIDADO] / [CONFIRMADO].

### Removed (BLOCO A — repo genérico)
- `exemplos/aivi-indicator-analyst/`, `exemplos/python-fuel-forecaster/`,
  `exemplos/regulated-pharma/`, `exemplos/tableau-senior-analyst/` — aplicações
  de domínio específicas que não pertencem ao núcleo distribuído.
- `exemplos/workflows/{bi-deliverable.md, sap-change.md}` — workflows de domínio
  (BI/SAP), também aplicação-específicos.
- `docs/specs/aivi-recalculo-limites/` — spec específica que estava bloqueada por
  domínio (pendência registrada na entrada [1.0.0] "Pendências conhecidas"). Sai
  junto com a aplicação correspondente.
- `guia/PROMPT-CHAT-WEB-v4.2.md` — duplicata. A cópia canônica é a da RAIZ.

### Added (BLOCO A — guia de criação substitui exemplos prontos)
- `exemplos/README.md` reescrito como **guia de como criar aplicações** (clonando
  `_template` no SEU repositório). Deixa de listar aplicações pré-prontas.

### Added (BLOCO D — sincronia formal do PROMPT-CHAT-WEB)
- `guia/GIT-VERSIONAMENTO.md` checklist de release ganha item: revisar e, se
  necessário, bumpar `PROMPT-CHAT-WEB-v4.x.md` da raiz a cada release. Liga o
  ciclo de vida do prompt web ao do núcleo.
- `CHANGELOG.md` ganha seção `## Política` no topo (SemVer + núcleo×aplicação +
  sincronia PROMPT-CHAT-WEB). Consolida políticas vivas dispersas. [CONFIRMADO].

### Changed (BLOCO B — PROMPT-CHAT-WEB consolidado na RAIZ)
- A cópia canônica do prompt é `PROMPT-CHAT-WEB-v4.2.md` na RAIZ (par de
  `CLAUDE.md`/`AGENTS.md`/`AGENT-FRAMEWORK.md` — load-bearing).
- `README.md` e `guia/ORIENTACAO.md` atualizados: descrevem o arquivo como
  "encarnação do framework para ambientes sem filesystem (Claude.ai, Gemini) —
  mesmos princípios, mesmos resultados, papéis/subagentes simulados".

### Fixed (BLOCO C — drift detectado pela auditoria do `explorer` em 2026-05-24)
- `guia/INSTALAR-NO-VSCODE.md`: contagem 56→54 arquivos; lista de raiz corrigida
  (`SETUP.md` vive em `guia/`, não na raiz desde v1.2.0); referência ao zip
  `v1.0.0` → `v1.4.0`. Causa-raiz: o guia não acompanhou a reorganização da v1.2.0.
- `guia/GUIA-EQUIPE.md`: linha 38 referência órfã `roles/` → atualizada para
  "aplicação criada clonando `_template`, fora do núcleo". Linha 33 (comandos):
  removidos `/sap-change` e `/bi-deliverable` (eram aplicação-específicos);
  adicionada nota de que comandos de domínio vivem na aplicação.
- `guia/GIT-VERSIONAMENTO.md`: exemplos atualizados de v1.2.0 → v1.4.0.
- `guia/web/index.html`: versão visível e camada APLICAÇÕES atualizadas.
- Back-references órfãs varridas e corrigidas em: `AGENTS.md`, `CLAUDE.md`,
  `AGENT-FRAMEWORK.md`, `_meta/eval-template.md`, `.agent/workflows/handoff.md`,
  `.agent/skills/_template/SKILL.md`, `_shared/high-stakes-gate/SKILL.md`,
  `PROMPT-CHAT-WEB-v4.2.md` (§10).

### Changed (system version)
- Versão do sistema: 1.3.0 → 1.4.0 (feature/refactor compatível = MINOR).

### Não tocado nesta entrega (registro deliberado — BLOCO E adiado)
- Renome `_template-application` (no frontmatter) ↔ pasta `_template/`:
  inconsistência menor detectada pelo `explorer`. **Exige ADR pela regra
  anti-rename** (`.agent/rules/01-anti-rename.md` → `_shared/traceability`).
  Fica para entrega separada, com ADR próprio.

### Pipeline auditável desta entrega
- PMO orquestra → `explorer` (subagente read-only) auditou o repo → developer
  executou A–D na branch `chore/repo-generico-drift-e-prompt-web` → `qa-critic`
  (subagente adversarial) validou contra critérios binários C1–C6 (todos
  V; recomendação `aprovar_com_ressalvas` — ressalva 1 incorporada neste
  commit: bump do `index.html` para v1.4.0) → docops (esta entrada).
- Merge **bloqueado**: gate humano. Branch espera revisão antes de cair em `main`.
