---
name: _template-application
description: "NÃO ATIVAR — molde para criar uma APLICAÇÃO do framework (um domínio/contexto específico). Clonar, renomear, preencher description (gatilhos + exclusões), as skills de _shared a carregar, e o domínio. É assim que o framework flexível vira aplicável a qualquer contexto."
version: 1.0.0
source: "padrão de aplicação derivado de A2"
last_review: 2026-05-23
role_order: null
consumes: []
produces:
  - "<o que esta skill entrega — preencher ao clonar>"
pass_criteria: "<critério BINÁRIO de PASS — preencher ao clonar>"
confidence_required: false
shared_refs: []
---

# <nome-da-aplicação> — Molde

> O framework é flexível. Uma **aplicação** é onde ele encontra um domínio/contexto
> (BI, regulado, análise de indicador, etc.). Aplicações vivem **FORA do núcleo** —
> no SEU repositório. Criar em 4 passos:
> 1. `cp -r .agent/skills/_template <seu-repo>/<minha-aplicacao>`.
> 2. Editar `name` + `description` (3ª pessoa, "pushy", gatilhos POSITIVOS **e** exclusões).
> 3. Listar as skills de `_shared/` a carregar (referência, nunca cópia).
> 4. Preencher só o **domínio**. Todo o transversal vem de `_shared/` e dos papéis.

## Carregar de `_shared/`
`anti-hallucination` · `confidence-classification` · `traceability` · `output-format`
(+ `high-stakes-gate` se o contexto for de alto risco/regulado).

## Gatilhos
- Positivos: <quando esta aplicação age>
- Exclusões: <quando NÃO — apontar a aplicação/papel correto>

## Domínio (único conteúdo próprio)
- <regras, tabelas, métodos do contexto específico>
- <qual MCP server usar, se acessa sistema externo — ver `_meta/external-access`>

## Spec e roteamento
Caso concreto → `docs/specs/<caso>/` (requirements + validation).
Classe de confiança → `rules/04-confidence-routing` escolhe a arquitetura.

> Ver `exemplos/README.md` para o guia de como aplicações de domínio se conectam
> ao núcleo. O núcleo não distribui aplicações prontas — cada equipe mantém as suas.
