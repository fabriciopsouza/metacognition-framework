# ADR 090 — BMAD project-onboarding + wayfinding: greenfield/brownfield, generate-project-context, document-project, guia do usuário (composição, não reinvenção)

- Status: **Aceito** (2026-06-19 — feedback do dono "siga"; gate: qa-critic adversarial + canário) · Decisores: dono + squad
- Tipo: **integração seletiva BMAD** (project-onboarding/wayfinding) por **composição de capacidades existentes + modos explícitos** — anti-reinvenção (ADR-072). NÃO duplica handoff/capabilities/explorer.
- Relaciona: ADR-081 (integração BMAD seletiva), ADR-002 (discovery submodo), ADR-067 (onboarding popup), ADR-072 (índice de capacidades), ADR-076 (handoff determinístico), ADR-010 (discovery declara escopo), ADR-068 (knowledge-catalog), ADR-089 (ficha de insumo)

## Contexto (pedido do dono)

O dono sente falta de capacidades estilo BMAD: análise **greenfield/brownfield**, `generate-project-context`, `document-project`, e recursos que **direcionem o usuário** ("andar da carruagem").

**Anti-reinvenção (file-first):** o framework já tem `explorer` (read-only, "revisar projeto existente" = brownfield), `discovery` (+ submodo process-mapping ADR-002), `handoff.py` + `CAPABILITIES.md` + `knowledge_catalog.py` + `project_report.py` + `framework_onboarding.py` (ADR-067) e o router. **Gaps reais:** (1) greenfield×brownfield é **implícito**, não um fork que molde a elicitação; (2) artefatos de contexto **espalhados** (sem 1-shot); (3) sem **documentador padronizado** de projeto existente; (4) wayfinding é **agent-side**, falta guia **user-facing**.

## Decisão (compor + tornar explícito; nenhum tool pesado novo)

- **(A) Discovery: fork EXPLÍCITO greenfield × brownfield** — sub-modo (padrão ADR-002). *Greenfield* = elicitação de projeto novo. *Brownfield* = `explorer` mapeia o existente PRIMEIRO, depois discovery elicita só os gaps. Declarado na rota; molda a "ficha de insumo" (ADR-089). **IMPLEMENTADO v1.70.0:** entrada no `discovery/SKILL.md` (sub-modos).
- **(B) `generate-project-context`** — workflow que **COMPÕE** (não recria): briefing + glossário + `handoff.py` + `CAPABILITIES.md` + mapa do `explorer` → **1 doc de contexto consumível por IA**. **IMPLEMENTADO:** `.agent/workflows/generate-project-context.md` (orquestra geradores existentes).
- **(C) `document-project`** (brownfield) — `explorer` (mapa) + `docops` (redação) → doc **padronizado** de arquitetura/estrutura/convenções. Saída fora do núcleo. **IMPLEMENTADO:** `.agent/workflows/document-project.md`.
- **(D) Wayfinding do usuário** — guia **user-facing** ("por onde começo? que modo p/ minha situação?") derivado de `AGENT-FRAMEWORK.md` + `CAPABILITIES.md`. **IMPLEMENTADO:** `guia/POR-ONDE-COMECAR.md` (complementa o popup ADR-067, que é 1ª-abertura).
- **Canário** `tools/test_project_onboarding.py` + capability `project-onboarding`.

## O que NÃO fazer (anti-reinvenção)
- Não recriar handoff/capabilities/explorer/knowledge-catalog — **compor** (os workflows REFERENCIAM os geradores existentes; o canário verifica que não recriam).
- Não importar `npx bmad-method` (ADR-081 já rejeitou). Régua §0: composição + modos explícitos que editam o existente, não adição pura. Nomes de produto BMAD ficam só neste ADR (proveniência), não no conteúdo operativo (ADR-091).

## Consequências
- (+) Discovery cobre greenfield/brownfield explicitamente; onboarding de projeto (novo OU existente) vira workflow nomeado; usuário ganha direção.
- (+) Tudo passa pelos gates nativos (ADR/qa-critic/history).
- (−) +1 sub-modo discovery + 2 workflows + 1 guia + 1 canário/capability; nenhum altera `_shared/`.

## Pendências
- **Aberto (backlog, não-bloqueante):** mapear 1:1 comandos BMAD adicionais que o dono queira (lista aberta — priorizar por uso). Os 4 acima são o núcleo do pedido.
