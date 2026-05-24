---
name: python-fuel-forecaster
description: "Ativar quando a tarefa envolve Python para dados (pandas/numpy), ETL, validação de schema (Pandera), forecasting de combustíveis (ARIMA/SARIMA/Prophet/XGBoost), sazonalidade Brasil, ou KPIs de distribuição de combustíveis. NÃO usar para construção de dashboard Tableau (use tableau-senior-analyst) nem para change SAP regulado (use pharma-systems-analyst)."
version: 1.0.0
source: "master prompt v4.1 §6, §7, §8, §11.2, §11.5, §12 (domínio migrado)"
last_review: 2026-05-23
---

# Python Fuel Forecaster — Domínio

## Antes de responder, SEMPRE carregar de `_shared/`
- `anti-hallucination` · `confidence-classification` · `traceability` · `output-format`

## Regra-zero (file-first aplicado a dados)
`print(df.columns.tolist())` antes de referenciar qualquer coluna. Nunca assumir
nome de campo (causa raiz #2 de retrabalho — `_shared/traceability`).

## Stack core
pandas/numpy · matplotlib/seaborn/plotly · statsmodels/scipy ·
scikit-learn/xgboost/prophet · ETL: prefect|airflow · validação: pandera|great_expectations
· SAP: hdbcli/pyrfc.

## Forecasting — escolha de método (Brasil)
| Método | Quando |
|---|---|
| ARIMA | estável, sem sazonalidade forte |
| SARIMA | sazonal claro (etanol safra, gasolina verão) |
| Prophet | múltiplas sazonalidades + feriados BR |
| LSTM | não-linear complexo (≥2 anos diários) |
| XGBoost | multi-feature com externos (clima, GDP, preços) |

Sazonalidades: **etanol** pico Out–Dez; **gasolina** pico Mai–Set; **diesel** ciclos agrícolas regionais.

## Produtos (nomenclatura padronizada)
`GASOLINA_C` · `DIESEL_B` · `ETANOL_HIDRATADO` · `QUEROSENE_AVIACAO` (+ GNV, lubrificantes).

## KPIs distribuição
Operacionais: Tank Turnover (~10/ano), Capacity Util. (85–95%), Days of Supply (15–30d),
Truck Turnaround (30–45min). Comerciais: volume/base/produto (m³), margem/m³, market share.
Logísticos: eficiência de rota, empty miles, produtividade frota.

## ETL — pipeline padrão (5 fases, não simplificar)
EXTRACT (conexão validada, credenciais via env) → VALIDATE (Pandera/asserts) →
TRANSFORM (snake_case, datas BR DD.MM.YYYY, NULL explícito) → ENRICH (calendário,
holiday_flag, joins) → LOAD (schema documentado, índices, metadata).

## Pandera (validação antes de exportar)
```python
import pandera as pa
schema = pa.DataFrameSchema({
    "data": pa.Column(pa.DateTime),
    "produto": pa.Column(str, pa.Check.isin(['GASOLINA_C','DIESEL_B','ETANOL_HIDRATADO'])),
    "volume_m3": pa.Column(float, pa.Check.greater_than(0)),
}, strict=True)
```

## Conversão de tipos é o primeiro passo
```python
def classificar_seguro(v):
    try: x = float(v) if pd.notna(v) else 0
    except (ValueError, TypeError): return 'NAO_IDENTIFICADO'
    # lógica numérica
```

## Flags > remoção (§12)
Nunca remover registro prematuramente. Criar `flag_Outlier_<campo>`,
`flag_Dados_Incompletos`, `flag_Inconsistencia_Logica`, `flag_Suspeito` (OR) — e
transferir a decisão ao analista. Reconciliação Total = Σ partes sempre (`_shared/output-format`).
