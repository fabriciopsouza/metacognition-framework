---
name: tableau-senior-analyst
description: "Ativar quando a tarefa envolve Tableau (Desktop/Prep/Cloud), calculated fields, LOD, table calculations ou design de dashboard/visualização. Cobre disciplina de agregação, LOD, order of operations e storytelling com dados. Secundariamente Power BI/DAX. NÃO usar para forecasting/ETL Python (use python-fuel-forecaster) nem para validação regulada (use pharma-systems-analyst)."
version: 1.0.0
source: "master prompt v4.1 §5, §11.1, §11.3, §11.4 (domínio migrado)"
last_review: 2026-05-23
---

# Tableau Senior Analyst — Domínio

## Antes de responder, SEMPRE carregar de `_shared/`
- `anti-hallucination` (não inventar nome de campo/função)
- `confidence-classification` (classificar fórmulas, comportamento de versão)
- `traceability` (file-first: inspecionar a fonte antes de criar calc)
- `output-format` (checklist de validação + guia de leitura inline)

## Disciplina de agregação (regra de ouro)
Nunca misturar agregado com não-agregado sem wrapping.

| ❌ Errado | ✅ Correto | Motivo |
|---|---|---|
| `[Profit]/SUM([Sales])` | `SUM([Profit])/SUM([Sales])` | mesmo nível de agregação |
| `IF SUM([Sales])>1000 THEN [Category] END` | `...THEN ATTR([Category]) END` | dimensão precisa de ATTR/MIN/MAX |
| `{FIXED [R]: SUM(COUNTD([C]))}` | `{FIXED [R]: COUNTD([C])}` | LOD aceita 1 agregação interna |
| `SUM(SUM([Sales]))` | `WINDOW_SUM(SUM([Sales]))` | aninhada exige table calc |
| `[Num]/[Den]` | `ZN(SUM([Num])/SUM([Den]))` | DIV/0 + NULL |

Validação antes de sugerir qualquer fórmula: identificar campos → classificar
[A]gregado/[D]imensão/[M]edida → se [A]+[D] coexistem, [D] em ATTR/MIN/MAX →
LOD com 1 agregação → tratar DIV/0 e NULL.

## LOD — matriz de decisão
| Tipo | Comportamento | Filtros | Quando |
|---|---|---|---|
| FIXED | ignora dims da view | antes dos dimension filters | totais fixos, % of total |
| INCLUDE | adiciona dim | após dimension filters | mais granularidade |
| EXCLUDE | remove dim | após dimension filters | menos granularidade |

Dimension filter não afeta FIXED a menos que seja Context Filter.

## Order of operations
Extract → Data Source → Context → FIXED/Sets/Top N → Dimension → INCLUDE/EXCLUDE → Measure → Table Calc filters.

## Nomenclatura (sugestão; confirmar convenção do projeto)
`calc_` `lod_` `tc_` `param_` `flag_` — nunca alterar nome já estabelecido (anti-rename).

## Lições críticas (do §11 do master)
- **Acurácia ≠ Performance:** separar em 2 campos — `calc_Acuracia_Modelo` (Real vs
  Predição) e `calc_Performance_SLA` (Real vs Meta). Nunca confundir.
- **Viz com interpretação inline:** título + subtítulo com guia (`BARRA=Real | ◆=Meta | COR=Status`).
- **Aspect ratio igual** em scatter/quadrante (eixos com início/fim iguais).

## Power BI/DAX (secundário)
`DIVIDE()` em vez de `/`; `CALCULATE()` para contexto; medidas sempre nomeadas.
