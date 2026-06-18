# ADR 090 — BMAD project-onboarding + wayfinding: greenfield/brownfield, generate-project-context, document-project, guia do usuário (composição, não reinvenção)

- Status: **Proposto** (2026-06-18 — feedback explícito do dono; aguarda qa-critic + ratificação)
- Tipo: **integração seletiva BMAD** (project-onboarding/wayfinding) por **composição de capacidades existentes + modos explícitos** — anti-reinvenção (ADR-072). NÃO duplica handoff/capabilities/explorer.
- Relaciona: ADR-081 (integração BMAD seletiva), ADR-002 (discovery submodo), ADR-067 (onboarding popup), ADR-072 (índice de capacidades), ADR-076 (handoff determinístico), ADR-010 (discovery declara escopo), ADR-068 (knowledge-catalog)

## Contexto (pedido do dono)
O dono sente falta de capacidades estilo BMAD: análise **greenfield/brownfield**,
`/bmad-generate-project-context`, `/bmad-document-project`, e recursos que **direcionem o
usuário** pelo framework ("andar da carruagem"). 

**Anti-reinvenção (file-first):** o framework já tem `explorer` (read-only, modo "revisar projeto
existente" = brownfield), `discovery` (+ submodo process-mapping ADR-002), `handoff.py` +
`CAPABILITIES.md` + `knowledge_catalog.py` + `project_report.py` (artefatos de contexto),
`framework_onboarding.py` (ADR-067) e o router `AGENT-FRAMEWORK.md`. **Os gaps reais são:**
(1) greenfield×brownfield é **implícito**, não um fork que molde a elicitação; (2) os artefatos de
contexto estão **espalhados** (sem 1-shot "gerar contexto do projeto"); (3) não há **documentador
padronizado** de projeto existente; (4) o wayfinding é **agent-side**, falta guia **user-facing**.

## Decisão (compor + tornar explícito; nenhum tool pesado novo)
- **(A) Discovery: fork EXPLÍCITO greenfield × brownfield** (sub-modo, padrão ADR-002).
  *Greenfield* = elicitação de projeto novo (sem código-fonte de partida). *Brownfield* = `explorer`
  mapeia o existente PRIMEIRO (estrutura/convenções/dependências), depois discovery elicita só os
  gaps. Declarado na rota (route-gate), molda quais perguntas a "ficha de insumo" (ADR-089) faz.
- **(B) `generate-project-context`** (skill/workflow que **compõe**): briefing + glossário +
  `handoff.py` + `CAPABILITIES.md` + mapa do `explorer` → **1 doc de contexto consumível por IA**
  (o equivalente adaptado do bmad-generate-project-context). Reusa geradores; não recria.
- **(C) `document-project`** (brownfield): `explorer` (mapa) + `docops` (redação) → doc
  **padronizado** de arquitetura/estrutura/convenções do projeto existente. Saída fora do núcleo.
- **(D) Wayfinding do usuário**: um **guia/comando user-facing** ("por onde começo? que modo para
  minha situação?") derivado de `AGENT-FRAMEWORK.md` + `CAPABILITIES.md` — direciona o **usuário**,
  não só o roteamento do agente. (Complementa o popup ADR-067, que é 1ª-abertura.)

## O que NÃO fazer (anti-reinvenção)
- Não recriar handoff/capabilities/explorer/knowledge-catalog — **compor**.
- Não importar `npx bmad-method` (ADR-081 já rejeitou — dois sistemas de skills).
- Régua §0: satisfeita por **composição + modos explícitos que editam o existente** (discovery,
  router), não adição pura; o ganho é "onboarding de projeto novo/existente em 1 passo + direção
  ao usuário" que hoje é manual e espalhado.

## Consequências
- (+) Discovery cobre greenfield/brownfield explicitamente; onboarding de projeto (novo OU
  existente) vira 1-comando; usuário ganha direção (reduz "andar da carruagem" travado).
- (+) Tudo passa pelos gates nativos (ADR/qa-critic/history), como ADR-081 fez.
- (−) +1 sub-modo discovery + 2 skills compostas (generate-project-context, document-project) +
  1 guia user-facing = ~4 superfícies; nenhuma altera núcleo `_shared/`.

## Pendências
- qa-critic adversarial + ratificação do dono (gate).
- Decidir forma de cada item: skill × workflow × tool (provável: B/C = skill que orquestra
  geradores; D = doc/comando; A = sub-modo no discovery/SKILL.md).
- Mapear 1:1 quais comandos BMAD adicionais o dono quer (lista aberta — priorizar por uso).
