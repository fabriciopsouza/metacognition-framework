# validation.md — AIVI (SCAFFOLD — critérios de domínio pendentes)

## Critérios genéricos (já válidos, herdados do framework)
| # | Critério | Verificação | Status |
|---|---|---|---|
| 1 | Colunas reais inspecionadas antes da lógica (file-first) | log de schema | ☐ |
| 2 | Total = Σ regionais (tolerância a definir) | reconciliação | ☐ |
| 3 | Edge cases tratados (NULL/zero/neg/extremo) | test cases | ☐ |
| 4 | Toda afirmação numérica classificada | `_shared/confidence-classification` | ☐ |
| 5 | Número rastreável à query/arquivo de origem | trilha decisão→fonte | ☐ |
| 6 | Saída no modo certo (executivo vs analista) | revisão | ☐ |
| 7 | Gate high-stakes: revisão humana antes de entregar | HITL | ☐ |

## Critérios de DOMÍNIO — ⚠️ PENDENTES [DESCONHECIDO]
| # | Critério | Status |
|---|---|---|
| D1 | <regra de recálculo de limite correta> | ☐ bloqueado |
| D2 | <gatilho 'emergencial' corretamente identificado> | ☐ bloqueado |
| D3 | <thresholds/batentes conforme norma> | ☐ bloqueado |

## Regra de transição
FINALIZADA só quando critérios genéricos **e** de domínio = VERDADEIRO.
Hoje: bloqueada nos D1–D3 até as regras emergenciais chegarem.
