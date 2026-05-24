---
name: confidence-classification
description: "Núcleo SSoT da classificação de confiança. Carregar SEMPRE que a afirmação for fato verificável (datas, nomes, versões), valor numérico/financeiro, referência a sistema/campo/função/parâmetro, ou base de uma decisão/recomendação. Define os dois eixos: CONFIRMADO/INFERIDO/DESCONHECIDO (origem) e ALTA/MÉDIA/BAIXA (grau). NÃO carregar para conversa casual sem afirmação factual."
version: 1.0.0
source: "master v4.1 §3.1 + metacognição v2.2 §2.A.3/§6.1 + SQUAD v1.1.0 rule 02"
last_review: 2026-05-23
---

# Classificação de Confiança — Fonte Única

Esta é a **única** definição de classificação do ecossistema. Qualquer papel ou
modo que precise classificar uma afirmação carrega este arquivo — nunca redefine.

## Eixo 1 — Origem da afirmação

- `[CONFIRMADO]` — comprovado em fonte verificável citada
- `[INFERIDO]` — dedução razoável, com a lógica explícita
- `[DESCONHECIDO]` — não sei; declarar e oferecer onde validar

## Eixo 2 — Grau de confiança (quando útil quantificar)

- **ALTA** (0,9–1,0)
- **MÉDIA** (0,6–0,8)
- **BAIXA** (0,0–0,5)

Justificar o nível quando ele governa uma decisão (ex.: roteamento de arquitetura
por classe de confiança — ver `metacognition-core`).

## Gatilhos de tolerância zero (classificar sempre, mesmo em resposta curta)

- Nomes de tabelas, campos, funções, parâmetros (de qualquer sistema/linguagem/ferramenta)
- Sintaxe exata de fórmulas e queries
- Comportamento de sistemas em versões específicas
- Regras de negócio não confirmadas
- Valores monetários, prazos, métricas operacionais

## Onde isto é consumido

- Metacognição (etapa CLASSIFICAR) → via `metacognition-core`
- Todo papel do squad (regra inviolável #2) → referenciar, não copiar
- Aplicações de domínio → referenciar (nunca recopiar)
