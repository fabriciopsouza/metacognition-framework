# validation.md — Critério de Aceite Binário (o gate de "pronto")

> O arquivo mais importante da spec. Declara **objetivamente** quando a tarefa
> transita de *incompleta* para *finalizada*. Fonte: pesquisa A2.
> O QA-Critic valida contra ESTE arquivo. Sem critério binário → não fecha.

## Critérios de aceite (cada um VERDADEIRO ou FALSO — nada subjetivo)

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 1 | <ex.: campos aderem ao glossário> | comparar termo a termo | ☐ |
| 2 | <ex.: reconciliação Total = Σ partes bate (tolerância X)> | somar regionais vs total | ☐ |
| 3 | <ex.: edge cases tratados: NULL, zero, neg., extremo> | test cases tabulados | ☐ |
| 4 | <ex.: DIV/0 explícito> | inspeção da fórmula | ☐ |
| 5 | <ex.: toda afirmação numérica classificada> | ver `_shared/confidence-classification` | ☐ |
| 6 | <ex.: número rastreável à query/arquivo de origem> | trilha decisão→fonte | ☐ |

## Test cases obrigatórios (referência: `_shared/output-format`)

| Caso | Input | Esperado | Resultado | OK? |
|---|---|---|---|---|
| Normal | <típico> | <…> | | ☐ |
| Zero | denom=0 | NULL ou 0 | | ☐ |
| NULL | campo NULL | tratado | | ☐ |
| Negativo | < 0 | conforme regra | | ☐ |
| Extremo | outlier | conforme regra | | ☐ |

## Regra de transição
Tarefa = **FINALIZADA** somente quando **todos** os critérios acima = VERDADEIRO.
Qualquer FALSO → volta ao Developer (limite: 3 reprovações → escalar, reabrir spec/ADR).
