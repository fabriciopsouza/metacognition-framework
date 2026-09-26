# producao · pesagem-e-reservas

Gerado em 26/09/2026 por `C:\Users\fabriciosouza\sap-mrp-natulab\gestao\_migracao-scripts\gerar_biblioteca_natulab.py`
a partir das fontes apontadas em cada entrada (SQL copiado sem edição). Consulta em uso num projeto continua no projeto.
## P06-90 consulta, exatamente como executada
- **Tipo:** consulta
- **Pergunta:** Consulta, exatamente como executada
- **Sistema:** SAP Datasphere
- **Versão:** SaaS
- **Fonte:** C:\Users\fabriciosouza\sistema-pesagem\provas\06-distribuicao-de-quantidades.md, linha 90
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no Datasphere, espaço PRODUCAO (sessão da pesagem, 24/09/2026)
- **Aponta para:** C:\Users\fabriciosouza\sistema-pesagem\provas\06-distribuicao-de-quantidades.md

```bash
cd "C:/Users/fabriciosouza/Datasphere"
PYTHONIOENCODING=utf-8 python tools/dsp.py --space PRODUCAO --limit 400 --sql "SELECT CASE WHEN \"RESB-ERFME\" = 'G' THEN 'G->kg' ELSE 'KG' END AS FONTE_UM, \"RESB-XLOEK\" AS ELIM, CASE WHEN Q < 0.1 THEN '1 <0,1' WHEN Q < 0.5 THEN '2 0,1-0,5' WHEN Q < 1 THEN '3 0,5-1' WHEN Q < 2 THEN '4 1-2' WHEN Q < 5 THEN '5 2-5' WHEN Q < 10 THEN '6 5-10' WHEN Q < 25 THEN '7 10-25' WHEN Q < 100 THEN '8 25-100' ELSE '9 >=100' END AS FAIXA_KG, COUNT(*) AS ITENS FROM (SELECT \"RESB-ERFME\", \"RESB-XLOEK\", CASE WHEN \"RESB-ERFME\" = 'G' THEN \"RESB-BDMNG\"/1000 ELSE \"RESB-BDMNG\" END AS Q FROM \"PRODUCAO\".\"VW_FD_PP_RESERVAS\" WHERE \"RESB-BWART\" = '261' AND \"RESB-BDMNG\" > 0 AND \"RESB-ERFME\" IN ('KG','G')) GROUP BY CASE WHEN \"RESB-ERFME\" = 'G' THEN 'G->kg' ELSE 'KG' END, \"RESB-XLOEK\", CASE WHEN Q < 0.1 THEN '1 <0,1' WHEN Q < 0.5 THEN '2 0,1-0,5' WHEN Q < 1 THEN '3 0,5-1' WHEN Q < 2 THEN '4 1-2' WHEN Q < 5 THEN '5 2-5' WHEN Q < 10 THEN '6 5-10' WHEN Q < 25 THEN '7 10-25' WHEN Q < 100 THEN '8 25-100' ELSE '9 >=100' END ORDER BY FONTE_UM, ELIM, FAIXA_KG LIMIT 100"
```

## P06-97 consulta, exatamente como executada
- **Tipo:** consulta
- **Pergunta:** Consulta, exatamente como executada
- **Sistema:** SAP Datasphere
- **Versão:** SaaS
- **Fonte:** C:\Users\fabriciosouza\sistema-pesagem\provas\06-distribuicao-de-quantidades.md, linha 97
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no Datasphere, espaço PRODUCAO (sessão da pesagem, 24/09/2026)
- **Aponta para:** C:\Users\fabriciosouza\sistema-pesagem\provas\06-distribuicao-de-quantidades.md

```bash
PYTHONIOENCODING=utf-8 python tools/dsp.py --space PRODUCAO --limit 40 --sql "SELECT \"RESB-ERFME\" AS UM, \"RESB-XLOEK\" AS ELIM, COUNT(*) AS ITENS, ROUND(MIN(\"RESB-BDMNG\"),3) AS Q_MIN, ROUND(MEDIAN(\"RESB-BDMNG\"),3) AS Q_MEDIANA, ROUND(MAX(\"RESB-BDMNG\"),3) AS Q_MAX, MIN(\"RESB-BDTER\") AS DT_MIN, MAX(\"RESB-BDTER\") AS DT_MAX FROM \"PRODUCAO\".\"VW_FD_PP_RESERVAS\" WHERE \"RESB-BWART\" = '261' AND \"RESB-BDMNG\" > 0 GROUP BY \"RESB-ERFME\", \"RESB-XLOEK\" ORDER BY ITENS DESC LIMIT 20"
```

## P06-182 como conferir
- **Tipo:** consulta
- **Pergunta:** Como conferir
- **Sistema:** SAP Datasphere
- **Versão:** SaaS
- **Fonte:** C:\Users\fabriciosouza\sistema-pesagem\provas\06-distribuicao-de-quantidades.md, linha 182
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no Datasphere, espaço PRODUCAO (sessão da pesagem, 24/09/2026)
- **Aponta para:** C:\Users\fabriciosouza\sistema-pesagem\provas\06-distribuicao-de-quantidades.md

```bash
PYTHONIOENCODING=utf-8 python tools/dsp.py --space PRODUCAO --limit 20 --sql "SELECT 'KG <0,1 elim=X' AS CHECAGEM, COUNT(*) AS ITENS FROM \"PRODUCAO\".\"VW_FD_PP_RESERVAS\" WHERE \"RESB-BWART\"='261' AND \"RESB-ERFME\"='KG' AND \"RESB-XLOEK\"='X' AND \"RESB-BDMNG\">0 AND \"RESB-BDMNG\"<0.1 UNION ALL SELECT 'KG 2-5 elim=X', COUNT(*) FROM \"PRODUCAO\".\"VW_FD_PP_RESERVAS\" WHERE \"RESB-BWART\"='261' AND \"RESB-ERFME\"='KG' AND \"RESB-XLOEK\"='X' AND \"RESB-BDMNG\">=2 AND \"RESB-BDMNG\"<5 UNION ALL SELECT 'G todos', COUNT(*) FROM \"PRODUCAO\".\"VW_FD_PP_RESERVAS\" WHERE \"RESB-BWART\"='261' AND \"RESB-ERFME\"='G' AND \"RESB-BDMNG\">0 LIMIT 10"
```

## RBP-38 passo 1 — o que é o movimento `z61`
- **Tipo:** consulta
- **Pergunta:** Passo 1 — O que é o movimento `Z61`
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sistema-pesagem\RUNBOOK-SAP-MOVIMENTOS-E-UNIDADES.md, linha 38
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sistema-pesagem\RUNBOOK-SAP-MOVIMENTOS-E-UNIDADES.md

```sql
SELECT BWART, SPRAS, BTEXT FROM T156T WHERE BWART IN ('261','Z61','201','202','543')
ORDER BY BWART, SPRAS;
```

## RBP-56 passo 2 — o que é a unidade `kga`
- **Tipo:** consulta
- **Pergunta:** Passo 2 — O que é a unidade `KGA`
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sistema-pesagem\RUNBOOK-SAP-MOVIMENTOS-E-UNIDADES.md, linha 56
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sistema-pesagem\RUNBOOK-SAP-MOVIMENTOS-E-UNIDADES.md

```sql
SELECT MSEHI, MSEH3, MSEHT, DIMID, ZAEHL, NENNR, EXP10, DECAN
  FROM T006 WHERE MSEHI IN ('KGA','KG','G','L','UN');
```

## RBP-72 passo 2 — o que é a unidade `kga`
- **Tipo:** consulta
- **Pergunta:** Passo 2 — O que é a unidade `KGA`
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sistema-pesagem\RUNBOOK-SAP-MOVIMENTOS-E-UNIDADES.md, linha 72
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sistema-pesagem\RUNBOOK-SAP-MOVIMENTOS-E-UNIDADES.md

```sql
SELECT MSEHI, SPRAS, MSEHL, MSEHT FROM T006A WHERE MSEHI IN ('KGA','KG','G');
```

## RBP-85 passo 3 — de quebra, fechar a premissa r4 da prova 06
- **Tipo:** consulta
- **Pergunta:** Passo 3 — De quebra, fechar a premissa R4 da prova 06
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sistema-pesagem\RUNBOOK-SAP-MOVIMENTOS-E-UNIDADES.md, linha 85
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sistema-pesagem\RUNBOOK-SAP-MOVIMENTOS-E-UNIDADES.md

```sql
SELECT ERFME, MEINS, COUNT(*) AS ITENS FROM RESB
 WHERE BWART = '261' AND BDMNG > 0 AND ERFME IN ('KG','G')
 GROUP BY ERFME, MEINS ORDER BY ITENS DESC;
```

## unidade da RESB-BDMNG
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sistema-pesagem\provas\06-distribuicao-de-quantidades.md, linhas 45-53
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no Datasphere (sessão da pesagem, 24/09/2026)

`RESB-BDMNG` está na unidade básica do material (MARA-MEINS); `ERFME` é a unidade de `ERFMG`. Medido no recorte KG/G.

## RESB-XLOEK sem significado resolvido
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** C:\Users\fabriciosouza\sistema-pesagem\provas\06-distribuicao-de-quantidades.md, linhas 133-142
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO

24/09/2026: 'X' em 99,5% dos itens do movimento 261, que têm necessidades futuras; o significado do campo aqui não foi resolvido.

## RESB muda durante a conferência
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** C:\Users\fabriciosouza\sistema-pesagem\provas\06-distribuicao-de-quantidades.md, linhas 70-71 e 121-123
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no Datasphere (sessão da pesagem, 24/09/2026)

24/09/2026: a mesma contagem mudou de 1.195 para 1.203 durante a conferência; a RESB é tabela viva.
