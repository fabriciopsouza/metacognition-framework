# ADR 081 — Integração seletiva de padrões BMAD-METHOD: elicitação avançada, edge-case-hunter, party-mode e readiness gate

- Status: **Aceito** (2026-06-16 — gate: qa-critic adversarial no bloco) · Data: 2026-06-16 · Decisores: dono (pedido explícito de integração determinística) + squad
- Onda: exploração comparativa BMAD-METHOD (49k stars) × metacognition-framework · Tipo: **adição autorizada pelo dono** (pedido explícito de integração). **Régua §0 (ADR-007):** adição pura — nenhuma das 3 cláusulas mecânicas de §0 (funde/remove, reduz tokens, destrava-eval-editando) se aplica diretamente. O que satisfaz §0 aqui é a **autorização explícita do dono + a disciplina de rejeição documentada** (5 padrões BMAD recusados por baixo ganho/sobreposição — ver seção "O que NÃO foi integrado"), não uma das cláusulas (a)/(b)/(c). Override de §0 declarado, não silencioso (rule #10 / ADR-051).
- Relaciona: ADR-003 (companions), ADR-007 (régua §0), ADR-010 (agnosticismo), ADR-011 (qa-bicelular), ADR-080 (dieta)

## Contexto

Análise comparativa do BMAD-METHOD (v6.8.0, 49k stars) revelou 4 padrões com ganho líquido positivo que o metacognition-framework não cobre:

1. **`bmad-advanced-elicitation`** — biblioteca de 69 métodos de pensamento estruturado (Tree of Thoughts, Pre-mortem, Source Triangulation, Assumption Audit, Debate Club, etc.) com menu interativo e integração com party-mode. O discovery do metacognition tem método sênior de 9 passos mas sem este arsenal de técnicas ortogonais.

2. **`bmad-review-edge-case-hunter`** — enumeração *exaustiva* e *mecânica* de caminhos não tratados (não por intuição, mas por percurso de branches), com output JSON estruturado `{location, trigger_condition, guard_snippet, potential_consequence}`. O qa-critic do metacognition tem postura adversarial mas não percurso mecânico de paths.

3. **`bmad-party-mode`** — múltiplas personas em conversa real com conflito deliberado, spawn paralelo/sequencial, contrarian injection automático quando todos concordam. O metacognition não tem mecanismo de exploração multi-perspectiva numa sessão.

4. **`bmad-check-implementation-readiness`** — gate que valida alinhamento PRD + UX + Arch + Epics *antes* de implementar. O metacognition tem QA bicelular mas não este gate pré-J3 explícito.

Convergência filosófica detectada: `bmad-investigate` usa `Confirmed/Deduced/Hypothesized` — mesma semântica do `CONFIRMADO/INFERIDO/DESCONHECIDO` do metacognition. Validação independente que classificação epistêmica é necessidade real.

## Decisão (1 frase ativa por item)

**(A1)** Criar skill `.agent/skills/advanced-elicitation/SKILL.md` com companion `methods.md` (69 métodos em tabela estruturada, padrão ADR-003); ativada pelo discovery ou diretamente pelo dono para aprofundar qualquer artefato — retorna versão enriquecida ao chamador.

**(A2)** Criar skill `.agent/skills/edge-case-hunter/SKILL.md`; integra ao qa-critic como segunda passagem obrigatória em blocos de código com lógica de branching; output é JSON canonicamente verificável.

**(B1)** Criar skill `.agent/skills/party-mode/SKILL.md`; ativada pelo PMO ou dono para decisões arquiteturais, retrospectives e exploração com perspectivas conflitantes; heterogeneidade de modelo quando ambiente permite.

**(B2)** Criar skill `.agent/skills/readiness-gate/SKILL.md`; gate pré-developer (verificação dentro de J2, entre J2 e J3 — NÃO é junção numerada do ledger) que valida alinhamento entre requirements.md, UX spec e decisões do architect antes de avançar para implementação.

**(B3)** Adicionar `spec_kernel` (5 campos: Why / Capabilities / Constraints / Non-goals / Success signal) ao template `docs/specs/_template/requirements.md` como seção HEAD opcional — comprime intent para skills downstream sem substituir o requirements.md sênior.

## O que NÃO foi integrado e por quê

- `bmad-correct-course`, `bmad-sprint-*`, `bmad-retrospective`: scope produto de software específico; BAIXO ganho líquido genérico. Rejeitado.
- `bmad-shard-doc`: sobreposição com `doc-intake` + `context-budget`. Rejeitado.
- `bmad-investigate`: sobreposição ALTA com `explorer` + classificação epistêmica nativa. Rejeitado.
- Web bundles: padrão cross-AI já coberto por ADR-069; os artefatos BMAD são referência, não código para importar. Rejeitado.
- Agentes de produto (PM, UX, Arch) como papéis separados: o squad do metacognition já tem cobertura equivalente com mais rigor. Rejeitado.

## Alternativas consideradas

1. **Instalar `npx bmad-method` dentro do metacognition.** Cria conflito de dois sistemas de skills, duas convenções de `.claude/`. **Rejeitada.**
2. **Novo repo de integração.** Dois upstreams para manter; deriva garantida. **Rejeitada.**
3. **Extração seletiva de padrões como skills nativas (ESCOLHIDA).** Cada skill passa pelos gates do metacognition nativamente — ADRs, qa-critic, history.md. Custo: implementação manual dos padrões extraídos.

## Consequências

**Positivas:** discovery ganha arsenal de 69 métodos sem mudar o fluxo; qa-critic ganha cobertura mecânica de paths (complementar, não substituto); PMO ganha modo de exploração multi-persona; gate pré-developer reduz retrabalho de implementação. **Negativas/limite (declarado):** 4 novos SKILL.md + 1 companion = +5 arquivos no repo; nenhum altera núcleo (_shared/); régua §0 satisfeita por **autorização do dono + rejeição documentada** (não por cláusula mecânica). **Wiring (resolvido nesta release):** `edge-case-hunter` → `qa-critic/SKILL.md`; `advanced-elicitation` → `discovery/SKILL.md` (passo 4 anti-raso) + `architect/SKILL.md` (passo 2); `readiness-gate` → `architect/SKILL.md` (passo 6, J2→J3) + `pmo/SKILL.md`; `party-mode` → `architect` + `pmo`. Nenhum dos quatro é mais soft-orphan — cada um tem handoff explícito de um role-skill, além do auto-trigger por description.

## Implementação (ponteiro)

- BLOCO A (ALTA): `.agent/skills/advanced-elicitation/` + `.agent/skills/edge-case-hunter/` — commit + PR separado
- BLOCO B (MÉDIA): `.agent/skills/party-mode/` + `.agent/skills/readiness-gate/` + `docs/specs/_template/requirements.md` — commit + PR separado
- `capabilities.json`: +4 entradas (uma por skill nova) após BLOCO B
- `CHANGELOG.md`: entrada `[1.59.0]` após BLOCO B completo + qa-critic PASS
