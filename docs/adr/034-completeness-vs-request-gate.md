# ADR 034 — Gate de completude pedido × entrega

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: remediação v2 (marco v1.25.0) · Tipo: **novo** (1 linter + 1 canário) — net-gain por destravar verificação inalcançável (régua §0 c): nenhum gate cruza pedido × entrega hoje.
- Origem no plano: item 2 ⭐ (`[campo]`: calculou 1 mês quando o pedido dizia "mês a mês" e "cada unidade"). Relaciona: ADR-033 (profundidade de spec, J1), qa-critic (J4), ADR-040 (CI).

## Contexto

O escopo entregue (um ponto único / uma base) era **subconjunto** do pedido ("mês a mês", "cada
unidade", acumulado implícito). **Nenhum gate cruzou pedido × entrega** — a aritmética bateu, mas o
produto cobria menos do que foi pedido, e isso só apareceu quando o dono rodou. É um gap de
**completude**, distinto da profundidade de elicitação (ADR-033): a dimensão até foi nomeada, mas a
entrega validou um recorte menor.

## Decisão (1 frase ativa)

Criar **`tools/check_completeness.py`** (detecta quantificadores de escopo no texto do pedido via
lexicon agnóstico — "cada X", "por X", "todos", "mês a mês/mensal", "acumulado", "ano inteiro/anual",
"intervalo" — e exige que CADA um esteja declarado em `## Cobertura exigida pelo pedido` E coberto por
critério binário no `validation.md`) + canário `tools/test_completeness.py`, wirado no qa-critic como
**rule #8** (gate antes do PASS J4): quantificador do pedido sem critério = REPROVADO.

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** O subconjunto silencioso reaparece. **Rejeitada — é o gap.**
2. **NLP/LLM extrai "tudo que o pedido implica" e compara semanticamente.** Não-determinístico, não-auditável, alucina escopo. **Rejeitada** — gate tem de ser binário e reproduzível.
3. **Exigir só a seção de cobertura (sem scan do pedido).** O autor poderia declarar o subconjunto e passar. **Rejeitada** — o scan de quantificadores força a declaração a partir do texto do pedido.
4. **Scan agnóstico de quantificadores + cobertura declarada + cruzamento com validation (ESCOLHIDA).** Prós: determinístico, agnóstico, barra o subconjunto antes do PASS. Contras: o lexicon é não-exaustivo (quantificador fora dele não é detectado) — limite **declarado** em `LIMITS.md`.

## Consequências

**Positivas:** "1 mês ≠ mês a mês" vira FAIL mecânico antes do PASS; o pedido e a entrega ficam
amarrados por critério binário. **Negativas:** exige a seção `## Cobertura exigida pelo pedido` no
requirements (pequena adição ao template, régua §0 ok). **Riscos/limite:** lexicon não-exaustivo;
falso-negativo de quantificador exótico → `LIMITS.md` ("mecanizado: quantificadores do lexicon").

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.23-v1.31-remediacao` · `2026-05-31` · grep `check_completeness`
- Artefatos: `tools/check_completeness.py`, `tools/test_completeness.py` (4 casos sintéticos agnósticos),
  qa-critic rule #8, referência no `evals-engineer` (gate de entrega de software).
- DONE quando: gate no CI, wirado a J4 (qa-critic). [CONFIRMADO — canário verde]
