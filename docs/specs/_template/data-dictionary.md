# Dicionário-contrato de entrada (ADR-046) — `<caso>`

> **Contrato verificável** dos arquivos de entrada do produto. O `discovery` produz; o produto
> **auto-detecta** esses arquivos na pasta selecionada e **valida** (via `tools/check_input_contract.py`)
> que as colunas obrigatórias existem — antes de processar. É o antídoto a "produto sem validação de
> arquivos" e a join-silencioso-a-zero. Remover esta seção se o produto não consome arquivos.
>
> Formato machine-readable (lido pelo gate): um bloco `### arquivo: <glob>` por arquivo + tabela de colunas.

## Contrato de entrada

### arquivo: <glob, ex.: fonte_*.xlsx>  | obrigatório
| coluna | tipo | obrigatória | regra/observação (ex.: prioridade de mapeamento, normalização de chave) |
|---|---|---|---|
| <nome-padronizado> | string\|int\|float\|date | sim | <ex.: normalizar `5123.0`→`5123` antes do join; nunca misturar antes/depois> |

### arquivo: <glob, ex.: dimensao_*.xlsx>  | opcional
| coluna | tipo | obrigatória | regra/observação |
|---|---|---|---|
| <nome> | string | sim | — |

> **Regra de mapeamento (quando há colunas-irmãs):** declarar a prioridade explícita (ex.: "usar a
> coluna *após* tratamento; nunca a bruta") — isto alimenta também o `## Mapeamento de campo-fonte`
> (ADR-035). **Alerta de join:** toda chave de junção deve ter regra de normalização declarada (o
> anti-pattern recorrente é inteiro lido como float → join retorna zero match silencioso).
