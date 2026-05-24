# REFERÊNCIAS — Bibliografia, Pesquisas e Base de Evolução

> Tudo que fundamenta este framework. Fontes primárias da Anthropic, padrões
> abertos, e os documentos de pesquisa do próprio projeto (A0–A3).
> Classificação: [CONFIRMADO] = URL verificada nesta build; [INFERIDO] = derivável.

## 1. Fontes primárias Anthropic — agentes e contexto
Hub de engenharia: https://www.anthropic.com/engineering  [CONFIRMADO]
- **Building effective agents** (19/dez/2024) — padrões: prompt chaining, routing,
  orchestrator-workers, evaluator-optimizer; "manter simplicidade". [CONFIRMADO via hub]
- **Effective context engineering for AI agents** (29/set/2025) — attention budget,
  context rot, compaction, structured note-taking, sub-agentes. [CONFIRMADO via hub]
- **How we built our multi-agent research system** (13/jun/2025) — multi-agente
  ~15× custo; paralelizar leitura. [CONFIRMADO via hub]
- **Equipping agents for the real world with Agent Skills** (16/out/2025). [CONFIRMADO via hub]
- **Building agents with the Claude Agent SDK** (29/set/2025). [CONFIRMADO via hub]
- **Claude Code: Best practices for agentic coding** (18/abr/2025). [CONFIRMADO via hub]

## 2. Documentação técnica Claude Code / SDK
- Skills (Claude Code): https://code.claude.com/docs/en/skills  [CONFIRMADO]
  — `.claude/skills/<nome>/SKILL.md`; comandos fundidos em skills; auto-load de
  `.claude/skills/` em `--add-dir`.
- Subagentes (Claude Code): https://docs.anthropic.com/en/docs/claude-code/subagents  [CONFIRMADO]
  — `.claude/agents/<nome>.md`; contexto isolado; tools restritas; não herda skills.
- Agent Skills no SDK: https://platform.claude.com/docs/en/agent-sdk/skills  [CONFIRMADO]
- Skills explained (comparativo): https://claude.com/blog/skills-explained  [CONFIRMADO]

## 3. Padrão aberto Agent Skills
- Agent Skills (formato SKILL.md, padrão aberto): https://agentskills.io  [CONFIRMADO via pesquisa]
  Adotado por VS Code, Cursor, Gemini CLI, Kiro, entre outros (2025–2026).

## 4. Padrões e convenções usados no framework
- Semantic Versioning: https://semver.org  [CONFIRMADO]
- Keep a Changelog: https://keepachangelog.com  [CONFIRMADO]
- MADR (Architecture Decision Records): https://adr.github.io  [CONFIRMADO]
- EARS (Easy Approach to Requirements Syntax) — sintaxe de requisitos. [INFERIDO: buscar fonte canônica]
- OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/  [INFERIDO]

## 5. Pesquisas-base do projeto (A0–A3) — fonte de evolução
Documentos do próprio projeto que orientaram cada decisão (no Project Knowledge):
- **A0 — Fundamentos de Prompt e Context Engineering** → §2.5 do roteador, `_shared/metacognition-core`.
- **A1 — Arquitetura RAG Multiagente em Produção** → isolamento de subagente, explorer.
- **A2 — Desenvolvimento de Projetos com Agentes IA** → spec-driven (validation.md),
  roles, eval-sets, "manter simplicidade".
- **A2 — Organização de Agentes Modulares Otimizados** → SSoT por arquivo, progressive disclosure.
- **A3 — Governança de IA Não Determinística Regulada** → roteamento por confiança,
  high-stakes-gate, observabilidade/OTel.
- Artefatos de síntese (compass): `compass_artifact_wf-*` no Project Knowledge.

## 6. Debate single vs multi-agente (registrado para contexto)
- Cognition, "Don't Build Multi-Agents" (jun/2025) — escrita single-thread. [INFERIDO]
- Anthropic, multi-agente p/ pesquisa breadth-first (jun/2025). [CONFIRMADO via §1]
- Resolução prática: paralelizar leitura; manter escrita coerente em uma thread.

## 7. Como esta base evolui
Cada release registra no `CHANGELOG.md` a mudança → a fonte (item desta lista).
Ao incorporar uma fonte nova: adicione aqui, cite no changelog, e versione (SemVer).

> Nota: URLs marcadas [INFERIDO] devem ser confirmadas antes de citar formalmente.
> Não tratar [INFERIDO] como verificado.
