# qualidade · lotes-e-validade

Gerado em 26/09/2026 por `C:\Users\fabriciosouza\sap-mrp-natulab\gestao\_migracao-scripts\gerar_biblioteca_natulab.py`
a partir das fontes apontadas em cada entrada (SQL copiado sem edição). Consulta em uso num projeto continua no projeto.
## SP02-59 2. **schema** — a consulta não acha a tabela sem isso
- **Tipo:** consulta
- **Pergunta:** 2. **SCHEMA** — a consulta não acha a tabela sem isso
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linha 59
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SET SCHEMA SAPHANADB;     -- <- CONFIRMAR o nome no seu ambiente; depois disso, nome curto funciona
```

## SP02-68 o padrão corrigido — use q-b como molde para todas as outras
- **Tipo:** consulta
- **Pergunta:** O padrão corrigido — use Q-B como molde para todas as outras
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linha 68
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SET SCHEMA SAPHANADB;          -- confirmar

SELECT  b.WERKS AS planta, b.MATNR AS material, a.MTART AS tipo_material,
        b.CHARG AS lote,
        COALESCE(c.VFDAT, c1.VFDAT) AS validade,
        DAYS_BETWEEN(CURRENT_DATE, COALESCE(c.VFDAT, c1.VFDAT)) AS dias_para_vencer,
        b.CLABS AS utilizacao_livre, b.CINSM AS em_controle_qualidade,
        b.CEINM AS utilizacao_restrita, b.CSPEM AS bloqueado,
        b.CUMLM AS em_transferencia, b.CRETM AS devolucao,
        CASE
          WHEN COALESCE(c.VFDAT, c1.VFDAT) IS NULL        THEN 'SEM VALIDADE'
          WHEN COALESCE(c.VFDAT, c1.VFDAT) < CURRENT_DATE THEN 'VENCIDO'
          WHEN DAYS_BETWEEN(CURRENT_DATE, COALESCE(c.VFDAT, c1.VFDAT)) <= 10 THEN 'VENCE EM 10'
          WHEN DAYS_BETWEEN(CURRENT_DATE, COALESCE(c.VFDAT, c1.VFDAT)) <= 30 THEN 'VENCE EM 30'
          WHEN DAYS_BETWEEN(CURRENT_DATE, COALESCE(c.VFDAT, c1.VFDAT)) <= 60 THEN 'VENCE EM 60'
          ELSE 'OK'
        END AS situacao
FROM    MCHB b
LEFT JOIN MCHA c  ON c.MANDT  = b.MANDT AND c.MATNR  = b.MATNR
                 AND c.WERKS  = b.WERKS AND c.CHARG  = b.CHARG
LEFT JOIN MCH1 c1 ON c1.MANDT = b.MANDT AND c1.MATNR = b.MATNR
                 AND c1.CHARG = b.CHARG
JOIN    MARA a ON a.MANDT = b.MANDT AND a.MATNR = b.MATNR
WHERE   b.MANDT = '400'                -- <- CONFIRMAR o mandante
  AND   a.MTART IN ('ROH','VERP')
  AND   b.WERKS IN ('1001','1005')
  AND   (b.CLABS + b.CINSM + b.CEINM + b.CSPEM + b.CUMLM + b.CRETM) > 0
ORDER BY situacao, validade;
```

## SP02-120 pré-voo 1 — o sinal da função de data (armadilha a1)
- **Tipo:** consulta
- **Pergunta:** Pré-voo 1 — o sinal da função de data (armadilha A1)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linha 120
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT DAYS_BETWEEN(CURRENT_DATE, ADD_DAYS(CURRENT_DATE,  30)) AS deve_dar_MAIS_30,
       DAYS_BETWEEN(CURRENT_DATE, ADD_DAYS(CURRENT_DATE, -30)) AS deve_dar_MENOS_30
FROM DUMMY;
```

## SP02-137 pré-voo 2 — onde mora a validade do lote (armadilha a2)
- **Tipo:** consulta
- **Pergunta:** Pré-voo 2 — onde mora a validade do lote (armadilha A2)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linha 137
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT 'MCHA' AS tabela, COUNT(*) AS lotes_com_validade
FROM   MCHA WHERE MANDT = '400' AND VFDAT IS NOT NULL
UNION ALL
SELECT 'MCH1' AS tabela, COUNT(*) AS lotes_com_validade
FROM   MCH1 WHERE MANDT = '400' AND VFDAT IS NOT NULL;
```

## SP02-230 q-b — validade dos lotes de roh e verp: o tamanho do problema **e o al
- **Tipo:** consulta
- **Pergunta:** Q-B — Validade dos lotes de ROH e VERP: o tamanho do problema **e o alerta pronto**
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linha 230
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT  b.WERKS AS planta, b.MATNR AS material, a.MTART AS tipo_material,
        b.CHARG AS lote,
        COALESCE(c.VFDAT, c1.VFDAT) AS validade,
        DAYS_BETWEEN(CURRENT_DATE, COALESCE(c.VFDAT, c1.VFDAT)) AS dias_para_vencer,
        b.CLABS AS utilizacao_livre,      -- e' o que o MRP conta
        b.CINSM AS em_controle_qualidade,
        b.CEINM AS utilizacao_restrita,
        b.CSPEM AS bloqueado,
        b.CUMLM AS em_transferencia,
        b.CRETM AS devolucao,
        CASE
          WHEN COALESCE(c.VFDAT, c1.VFDAT) IS NULL   THEN 'SEM VALIDADE'
          WHEN COALESCE(c.VFDAT, c1.VFDAT) < CURRENT_DATE THEN 'VENCIDO'
          WHEN DAYS_BETWEEN(CURRENT_DATE, COALESCE(c.VFDAT, c1.VFDAT)) <= 10 THEN 'VENCE EM 10'
          WHEN DAYS_BETWEEN(CURRENT_DATE, COALESCE(c.VFDAT, c1.VFDAT)) <= 30 THEN 'VENCE EM 30'
          WHEN DAYS_BETWEEN(CURRENT_DATE, COALESCE(c.VFDAT, c1.VFDAT)) <= 60 THEN 'VENCE EM 60'
          ELSE 'OK'
        END AS situacao
FROM    MCHB b
LEFT JOIN MCHA  c  ON c.MATNR  = b.MATNR AND c.WERKS = b.WERKS AND c.CHARG = b.CHARG
LEFT JOIN MCH1  c1 ON c1.MATNR = b.MATNR AND c1.CHARG = b.CHARG     -- ver armadilha A2
JOIN    MARA a ON a.MATNR = b.MATNR
WHERE   a.MTART IN ('ROH','VERP')
  AND   b.WERKS IN ('1001','1005')
  AND   (b.CLABS + b.CINSM + b.CEINM + b.CSPEM + b.CUMLM + b.CRETM) > 0
ORDER BY situacao, validade;
```

## SP02-281 q-c ⭐ — o **alerta b**: estoque que estará vencido na data da necessid
- **Tipo:** consulta
- **Pergunta:** Q-C ⭐ — O **alerta B**: estoque que estará vencido na data da necessidade
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linha 281
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT  r.WERKS AS planta, r.MATNR AS material,
        r.BDTER AS data_da_necessidade,
        SUM(r.BDMNG - r.ENMNG) AS qtd_necessaria,
        (SELECT SUM(b2.CLABS) FROM MCHB b2
          WHERE b2.MATNR = r.MATNR AND b2.WERKS = r.WERKS) AS estoque_livre_total,
        (SELECT SUM(b3.CLABS) FROM MCHB b3
          LEFT JOIN MCHA c3 ON c3.MATNR = b3.MATNR AND c3.WERKS = b3.WERKS
                           AND c3.CHARG = b3.CHARG
          LEFT JOIN MCH1 c4 ON c4.MATNR = b3.MATNR AND c4.CHARG = b3.CHARG
          WHERE b3.MATNR = r.MATNR AND b3.WERKS = r.WERKS
            AND COALESCE(c3.VFDAT, c4.VFDAT) >= r.BDTER) AS estoque_valido_na_data
FROM    RESB r
WHERE   r.XLOEK = ''
  AND   r.WERKS IN ('1001','1005')
  AND   r.BDTER > CURRENT_DATE
  AND   (r.BDMNG - r.ENMNG) > 0
GROUP BY r.WERKS, r.MATNR, r.BDTER
ORDER BY r.BDTER;
```
