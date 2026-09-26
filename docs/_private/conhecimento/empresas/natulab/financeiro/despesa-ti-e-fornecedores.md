# financeiro · despesa-ti-e-fornecedores

Gerado em 26/09/2026 por `C:\Users\fabriciosouza\sap-mrp-natulab\gestao\_migracao-scripts\gerar_biblioteca_natulab.py`
a partir das fontes apontadas em cada entrada (SQL copiado sem edição). Consulta em uso num projeto continua no projeto.
## B19 rateio/provisao — documento sem nenhuma linha de fornecedor
- **Tipo:** consulta
- **Pergunta:** RATEIO/PROVISAO — documento SEM nenhuma linha de fornecedor
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 19 (linha 73)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT ti.RCNTR AS CENTRO_CUSTO, h.BLART AS TIPO_DOC,
       COUNT(*) AS LINHAS, COUNT(DISTINCT ti.BELNR) AS DOCUMENTOS,
       SUM(ti.HSL) AS VALOR
FROM       SAPABAP1.ACDOCA ti
LEFT JOIN  SAPABAP1.BKPF h ON h.MANDT = '400' AND h.BUKRS = ti.RBUKRS
                          AND h.BELNR = ti.BELNR AND h.GJAHR = ti.GJAHR
WHERE  ti.RCLNT = '400' AND ti.RLDNR = '0L' AND ti.GJAHR = '2026'
  AND  ti.RCNTR IN ('0000122012','0000222012')
  AND  NOT EXISTS (SELECT 1 FROM SAPABAP1.ACDOCA v
                   WHERE v.RCLNT = ti.RCLNT AND v.RLDNR = ti.RLDNR
                     AND v.RBUKRS = ti.RBUKRS AND v.BELNR = ti.BELNR
                     AND v.GJAHR = ti.GJAHR AND v.LIFNR <> '')
GROUP  BY ti.RCNTR, h.BLART
ORDER  BY 5 DESC
```

## B20 o espelho — documento com linha de fornecedor
- **Tipo:** consulta
- **Pergunta:** O ESPELHO — documento COM linha de fornecedor
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 20 (linha 94)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT ti.RCNTR AS CENTRO_CUSTO, h.BLART AS TIPO_DOC,
       COUNT(*) AS LINHAS, COUNT(DISTINCT ti.BELNR) AS DOCUMENTOS,
       SUM(ti.HSL) AS VALOR
FROM       SAPABAP1.ACDOCA ti
LEFT JOIN  SAPABAP1.BKPF h ON h.MANDT = '400' AND h.BUKRS = ti.RBUKRS
                          AND h.BELNR = ti.BELNR AND h.GJAHR = ti.GJAHR
WHERE  ti.RCLNT = '400' AND ti.RLDNR = '0L' AND ti.GJAHR = '2026'
  AND  ti.RCNTR IN ('0000122012','0000222012')
  AND  EXISTS (SELECT 1 FROM SAPABAP1.ACDOCA v
               WHERE v.RCLNT = ti.RCLNT AND v.RLDNR = ti.RLDNR
                 AND v.RBUKRS = ti.RBUKRS AND v.BELNR = ti.BELNR
                 AND v.GJAHR = ti.GJAHR AND v.LIFNR <> '')
GROUP  BY ti.RCNTR, h.BLART
ORDER  BY 5 DESC
```

## B22 o plano — ryear no lugar de gjahr (a 13 falhou por isso)
- **Tipo:** consulta
- **Pergunta:** O PLANO — RYEAR no lugar de GJAHR (a 13 falhou por isso)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 22 (linha 115)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT RLDNR AS LEDGER, RCNTR AS CENTRO_CUSTO, RACCT AS CONTA,
       POPER AS PERIODO, SUM(HSL) AS VALOR_PLANEJADO
FROM   SAPABAP1.ACDOCP
WHERE  RCLNT = '400' AND RYEAR = '2026'
  AND  RCNTR IN ('0000122012','0000222012')
GROUP  BY RLDNR, RCNTR, RACCT, POPER
ORDER  BY RCNTR, POPER, RACCT
```

## B23 se a 22 vier vazia — existe plano em algum centro de custo?
- **Tipo:** consulta
- **Pergunta:** SE A 22 VIER VAZIA — existe plano em ALGUM centro de custo?
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 23 (linha 128)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT RYEAR, RLDNR, COUNT(*) AS LINHAS, COUNT(DISTINCT RCNTR) AS CENTROS_DE_CUSTO
FROM   SAPABAP1.ACDOCP
WHERE  RCLNT = '400'
GROUP  BY RYEAR, RLDNR
ORDER  BY RYEAR DESC, RLDNR
```

## B24 *** o entregavel *** — uma linha por lancamento de ti, com tudo que o diretor pe
- **Tipo:** consulta
- **Pergunta:** *** O ENTREGAVEL *** — uma linha por lancamento de TI, com tudo que o diretor pediu
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 24 (linha 140)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT
    CASE WHEN h.BLART = 'AF' THEN 'DEPRECIACAO'
         WHEN UPPER(COALESCE(ti.SGTXT,'') || COALESCE(h.BKTXT,'')) LIKE '%DEPRECIA%' THEN 'DEPRECIACAO'
         WHEN UPPER(COALESCE(ti.SGTXT,'') || COALESCE(h.BKTXT,'')) LIKE '%IFRS%'     THEN 'DEPRECIACAO'
         WHEN NOT EXISTS (SELECT 1 FROM SAPABAP1.ACDOCA v
                          WHERE v.RCLNT = ti.RCLNT AND v.RLDNR = ti.RLDNR
                            AND v.RBUKRS = ti.RBUKRS AND v.BELNR = ti.BELNR
                            AND v.GJAHR = ti.GJAHR AND v.LIFNR <> '')
              THEN 'RATEIO/PROVISAO'
         WHEN f.AUGDT IS NOT NULL AND f.AUGDT <> '00000000' THEN 'PAGO'
         ELSE 'EM ABERTO' END                              AS SITUACAO,
    f.LIFNR                                                AS COD_FORNECEDOR,
    l.NAME1                                                AS FORNECEDOR,
    l.STCD1                                                AS CNPJ,
    l.STCD2                                                AS CPF,
    h.XBLNR                                                AS NUMERO_TITULO,
    h.BLDAT                                                AS EMISSAO,
    f.AUGDT                                                AS DATA_PAGAMENTO,
    CASE WHEN f.AUGDT IS NULL OR f.AUGDT = '00000000' THEN ''
         ELSE LEFT(f.AUGDT,4) || '/' || SUBSTRING(f.AUGDT,5,2) END AS MES_CAIXA,
    LEFT(h.BUDAT,4) || '/' || SUBSTRING(h.BUDAT,5,2)       AS MES_COMPETENCIA,
    ti.HSL                                                 AS VALOR,
    ti.RBUKRS                                              AS EMPRESA,
    ti.RCNTR                                               AS CENTRO_CUSTO,
    -- CORRIGIDO 21/09/2026: dizia 'TI filial 1000' / 'TI filial 2000'. O '2000' NAO
    -- existe. MEDIDO: RBUKRS = 1000 em 100% das 3.606 linhas, nos DOIS centros de custo.
    -- As filiais sao Medicamentos e Suplementos, e o codigo delas (1001 / 1005, declarado
    -- pelo dono) NAO e' o BUKRS — e' a FILIAL, campo que nunca foi extraido. Na ACDOCA
    -- esse campo e' BRANCH_ID (medido no bloco 31; BUPLA nao existe aqui), trazido
    -- abaixo com WERKS. Ate a 31b medir, este rotulo carrega so' o nome.
    CASE WHEN ti.RCNTR = '0000122012' THEN 'TI - Medicamentos'
         WHEN ti.RCNTR = '0000222012' THEN 'TI - Suplementos' END AS CC_DESCRICAO,
    ti.BRANCH_ID                                           AS FILIAL,
    ti.WERKS                                               AS CENTRO,
    '2200_ADM'                                             AS GRUPO_CC,
    ti.RACCT                                               AS CONTA_CONTABIL,
    ti.SGTXT                                               AS HISTORICO,
    h.BKTXT                                                AS TEXTO_CABECALHO,
    h.BLART                                                AS TIPO_DOC,
    ti.BELNR                                               AS DOCUMENTO,
    ti.DOCLN                                               AS LINHA,
    ti.GJAHR                                               AS EXERCICIO,
    f.AUGBL                                                AS DOC_COMPENSACAO
FROM       SAPABAP1.ACDOCA ti
LEFT JOIN  ( SELECT a.RBUKRS, a.BELNR, a.GJAHR,
                    MAX(a.LIFNR) AS LIFNR, MAX(a.AUGDT) AS AUGDT, MAX(a.AUGBL) AS AUGBL
             FROM   SAPABAP1.ACDOCA a
             WHERE  a.RCLNT = '400' AND a.RLDNR = '0L' AND a.GJAHR = '2026'
               AND  a.LIFNR <> ''
             GROUP  BY a.RBUKRS, a.BELNR, a.GJAHR ) f
       ON  f.RBUKRS = ti.RBUKRS AND f.BELNR = ti.BELNR AND f.GJAHR = ti.GJAHR
LEFT JOIN  SAPABAP1.BKPF h ON h.MANDT = '400' AND h.BUKRS = ti.RBUKRS
                          AND h.BELNR = ti.BELNR AND h.GJAHR = ti.GJAHR
LEFT JOIN  SAPABAP1.LFA1 l ON l.MANDT = '400' AND l.LIFNR = f.LIFNR
WHERE  ti.RCLNT = '400' AND ti.RLDNR = '0L' AND ti.GJAHR = '2026'
  AND  ti.RCNTR IN ('0000122012','0000222012')
ORDER  BY 1, f.AUGDT, l.NAME1, ti.BELNR, ti.DOCLN
```

## B25 o resumo da 24 — para conferir os totais antes de montar a planilha
- **Tipo:** consulta
- **Pergunta:** O RESUMO DA 24 — para conferir os totais antes de montar a planilha
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 25 (linha 214)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT SITUACAO, COUNT(*) AS LINHAS, SUM(VALOR) AS VALOR
FROM (
    SELECT
        CASE WHEN h.BLART = 'AF' THEN 'DEPRECIACAO'
             WHEN UPPER(COALESCE(ti.SGTXT,'') || COALESCE(h.BKTXT,'')) LIKE '%DEPRECIA%' THEN 'DEPRECIACAO'
             WHEN UPPER(COALESCE(ti.SGTXT,'') || COALESCE(h.BKTXT,'')) LIKE '%IFRS%'     THEN 'DEPRECIACAO'
             WHEN NOT EXISTS (SELECT 1 FROM SAPABAP1.ACDOCA v
                              WHERE v.RCLNT = ti.RCLNT AND v.RLDNR = ti.RLDNR
                                AND v.RBUKRS = ti.RBUKRS AND v.BELNR = ti.BELNR
                                AND v.GJAHR = ti.GJAHR AND v.LIFNR <> '')
                  THEN 'RATEIO/PROVISAO'
             WHEN f.AUGDT IS NOT NULL AND f.AUGDT <> '00000000' THEN 'PAGO'
             ELSE 'EM ABERTO' END AS SITUACAO,
        ti.HSL AS VALOR
    FROM       SAPABAP1.ACDOCA ti
    LEFT JOIN  ( SELECT a.RBUKRS, a.BELNR, a.GJAHR, MAX(a.AUGDT) AS AUGDT
                 FROM   SAPABAP1.ACDOCA a
                 WHERE  a.RCLNT = '400' AND a.RLDNR = '0L' AND a.GJAHR = '2026'
                   AND  a.LIFNR <> ''
                 GROUP  BY a.RBUKRS, a.BELNR, a.GJAHR ) f
           ON  f.RBUKRS = ti.RBUKRS AND f.BELNR = ti.BELNR AND f.GJAHR = ti.GJAHR
    LEFT JOIN  SAPABAP1.BKPF h ON h.MANDT = '400' AND h.BUKRS = ti.RBUKRS
                              AND h.BELNR = ti.BELNR AND h.GJAHR = ti.GJAHR
    WHERE  ti.RCLNT = '400' AND ti.RLDNR = '0L' AND ti.GJAHR = '2026'
      AND  ti.RCNTR IN ('0000122012','0000222012')
) x
GROUP  BY SITUACAO
ORDER  BY 3 DESC
```

## B28b medir a semantica dos prazos — em vez de acreditar em mim ou no qa
- **Tipo:** consulta
- **Pergunta:** MEDIR A SEMANTICA DOS PRAZOS — em vez de acreditar em mim OU no QA
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 28b (linha 249)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT d.FIELDNAME AS CAMPO,
       d.ROLLNAME  AS ELEMENTO_DADOS,
       d.DATATYPE  AS TIPO,
       d.LENG      AS TAMANHO
FROM   SAPABAP1.DD03L d
WHERE  d.TABNAME = 'BSEG'
  AND  d.FIELDNAME IN ('ZFBDT','ZBD1T','ZBD2T','ZBD3T','ZBD1P','ZBD2P','ZTERM')
ORDER  BY d.FIELDNAME
```

## B28 vencimento e parcela — as duas colunas do diretor que a 24 nao tem
- **Tipo:** consulta
- **Pergunta:** VENCIMENTO E PARCELA — as duas colunas do diretor que a 24 nao tem
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 28 (linha 274)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT b.BUKRS  AS EMPRESA,
       b.BELNR  AS DOCUMENTO,
       b.GJAHR  AS EXERCICIO,
       b.BUZEI  AS PARTIDA,
       b.LIFNR  AS COD_FORNECEDOR,
       b.SHKZG  AS DEB_CRED,
       b.DMBTR  AS VALOR_PARTIDA,
       b.ZFBDT  AS DATA_BASE,
       b.ZBD3T  AS DIAS_LIQUIDO,
       b.ZBD2T  AS DIAS_DESCONTO2,
       b.ZBD1T  AS DIAS_DESCONTO1,
       b.ZBD1P  AS PCT_DESCONTO1,
       b.ZLSCH  AS FORMA_PAGAMENTO,
       b.ZTERM  AS COND_PAGAMENTO,
       b.AUGDT  AS COMPENSACAO,
       b.AUGBL  AS DOC_COMPENSACAO,
       b.ZUONR  AS ATRIBUICAO,
       b.XREF3  AS REF_CHAVE3
FROM   SAPABAP1.BSEG b
WHERE  b.MANDT = '400' AND b.GJAHR = '2026' AND b.KOART = 'K'
  AND  b.BUKRS IN ('1000','2000')
  AND  b.SHKZG = 'H'
  AND  EXISTS (SELECT 1 FROM SAPABAP1.ACDOCA ti
               WHERE ti.RCLNT = '400' AND ti.RLDNR = '0L' AND ti.GJAHR = b.GJAHR
                 AND ti.RBUKRS = b.BUKRS AND ti.BELNR = b.BELNR
                 AND ti.RCNTR IN ('0000122012','0000222012'))
ORDER  BY b.BUKRS, b.BELNR, b.BUZEI
```

## B29 a validacao que faltava — o equivalente do fbl1n, pelo caminho que existe no han
- **Tipo:** consulta
- **Pergunta:** A VALIDACAO QUE FALTAVA — o equivalente do FBL1N, pelo caminho que existe no HANA
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 29 (linha 352)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT CASE WHEN b.AUGDT IS NULL OR b.AUGDT = '00000000'
            THEN 'EM ABERTO' ELSE 'COMPENSADA' END      AS STATUS_PARTIDA,
       b.BUKRS                                          AS EMPRESA,
       COUNT(*)                                         AS PARTIDAS,
       COUNT(DISTINCT b.BELNR)                          AS DOCUMENTOS,
       SUM(CASE WHEN b.SHKZG = 'H' THEN b.DMBTR ELSE -b.DMBTR END) AS VALOR
FROM   SAPABAP1.BSEG b
WHERE  b.MANDT = '400' AND b.GJAHR = '2026' AND b.KOART = 'K'
  AND  b.BUKRS IN ('1000','2000')
GROUP  BY CASE WHEN b.AUGDT IS NULL OR b.AUGDT = '00000000'
               THEN 'EM ABERTO' ELSE 'COMPENSADA' END, b.BUKRS
ORDER  BY 1, 2
```

## B29b o risco especifico: compensacao parcial
- **Tipo:** consulta
- **Pergunta:** O RISCO ESPECIFICO: COMPENSACAO PARCIAL
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 29b (linha 384)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT b.BUKRS AS EMPRESA, b.BELNR AS DOCUMENTO, b.GJAHR AS EXERCICIO,
       COUNT(*) AS PARTIDAS_NO_DOC,
       SUM(CASE WHEN b.AUGDT IS NULL OR b.AUGDT = '00000000' THEN 1 ELSE 0 END) AS ABERTAS,
       SUM(CASE WHEN b.AUGDT IS NULL OR b.AUGDT = '00000000'
                THEN CASE WHEN b.SHKZG = 'H' THEN b.DMBTR ELSE -b.DMBTR END
                ELSE 0 END)                                    AS VALOR_AINDA_ABERTO
FROM   SAPABAP1.BSEG b
WHERE  b.MANDT = '400' AND b.GJAHR = '2026' AND b.KOART = 'K'
  AND  b.BUKRS IN ('1000','2000')
  AND  EXISTS (SELECT 1 FROM SAPABAP1.ACDOCA ti
               WHERE ti.RCLNT = '400' AND ti.RLDNR = '0L' AND ti.GJAHR = b.GJAHR
                 AND ti.RBUKRS = b.BUKRS AND ti.BELNR = b.BELNR
                 AND ti.RCNTR IN ('0000122012','0000222012'))
GROUP  BY b.BUKRS, b.BELNR, b.GJAHR
HAVING SUM(CASE WHEN b.AUGDT IS NULL OR b.AUGDT = '00000000' THEN 1 ELSE 0 END) > 0
   AND SUM(CASE WHEN b.AUGDT IS NULL OR b.AUGDT = '00000000' THEN 1 ELSE 0 END) < COUNT(*)
ORDER  BY 6 DESC

-- *** REVISAO DE 24/09/2026 — O ALCANCE DA 29b E' MENOR DO QUE O ESCRITO ACIMA ***
--
-- (1) A 29b so' enxerga documento com DUAS OU MAIS partidas de fornecedor (COUNT(*) > 1
--     e' condicao para o HAVING ser verdadeiro). Fatura de linha unica — o caso comum —
--     NUNCA aparece aqui, qualquer que seja a situacao dela. O "0 linhas" prova que nao
--     ha' fatura PARCELADA meio paga; nao prova que nao ha' pagamento parcial.
-- (2) No SAP, pagamento com RESIDUO compensa a fatura INTEIRA e abre o que falta como
--     partida nova no documento de PAGAMENTO — que nao tem centro de custo de TI e por
--     isso nunca entra no universo desta consulta nem do entregavel. A fatura aparece
--     como PAGA pelo valor cheio. E' dinheiro que esta no SAP e nao no relatorio.
-- (3) O "0 linhas" de 21/09 nao tem export salvo. Nao da' para distinguir "rodou e
--     voltou vazio" de "deu erro e foi relatado como vazio".
-- A 29c mede o que a 29b nao alcanca. RODAR DE NOVO A 29b SALVANDO O EXPORT, mesmo
-- vazio: arquivo so' com cabecalho e' a prova de que a consulta rodou sem erro.
```

## B29c-sonda os campos de referencia da bseg existem?
- **Tipo:** consulta
- **Pergunta:** OS CAMPOS DE REFERENCIA DA BSEG EXISTEM?
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 29c-sonda (linha 435)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT COLUMN_NAME, DATA_TYPE_NAME, LENGTH
FROM   SYS.TABLE_COLUMNS
WHERE  SCHEMA_NAME = 'SAPABAP1' AND TABLE_NAME = 'BSEG'
  AND  COLUMN_NAME IN ('REBZG','REBZJ','REBZT','BUZEI')
ORDER  BY COLUMN_NAME
```

## B29c o dinheiro que referencia uma fatura de ti e esta em outro documento
- **Tipo:** consulta
- **Pergunta:** O DINHEIRO QUE REFERENCIA UMA FATURA DE TI E ESTA EM OUTRO DOCUMENTO
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 29c (linha 453)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT r.BUKRS  AS EMPRESA,
       r.BELNR  AS DOCUMENTO_COM_REFERENCIA,
       r.GJAHR  AS EXERCICIO,
       r.REBZG  AS FATURA_DE_TI,
       r.REBZJ  AS ANO_DA_FATURA,
       r.REBZT  AS TIPO_REFERENCIA,
       CASE WHEN r.AUGDT IS NULL OR r.AUGDT = '00000000' THEN 'EM ABERTO'
            ELSE 'COMPENSADA' END                             AS SITUACAO,
       r.AUGDT  AS DATA_COMPENSACAO,
       CASE WHEN r.SHKZG = 'H' THEN r.DMBTR ELSE -r.DMBTR END  AS VALOR,
       r.BUZEI  AS PARTIDA
FROM   SAPABAP1.BSEG r
WHERE  r.MANDT = '400' AND r.GJAHR = '2026' AND r.KOART = 'K'
  AND  r.BUKRS IN ('1000','2000')
  AND  r.REBZG <> ''
  AND  NOT (r.BELNR = r.REBZG AND r.GJAHR = r.REBZJ)
  AND  EXISTS (SELECT 1 FROM SAPABAP1.ACDOCA ti
               WHERE ti.RCLNT = '400' AND ti.RLDNR = '0L'
                 AND ti.RBUKRS = r.BUKRS AND ti.BELNR = r.REBZG AND ti.GJAHR = r.REBZJ
                 AND ti.RCNTR IN ('0000122012','0000222012'))
ORDER  BY 6, 7, 4, 2

-- *** LIMITES DA 29c, declarados na v9 (25/09/2026, QA adversarial rodadas 1 e 2) ***
--   (1) So' enxerga vinculo por REBZG. Compensacao feita a mao, sem a funcao de residuo,
--       pode nao preencher REBZG — a 29d cobre isso por outro caminho.
--   (2) So' enxerga UM salto. Residuo de residuo aponta para o 1o documento de pagamento,
--       que nao tem CC de TI; o EXISTS falha e a cadeia escapa. A 29e mede se a cadeia
--       EXISTE nos dados antes de se escrever uma busca recursiva.
--   (3) So' empresas 1000 e 2000. A 33 mediu que 2000 nao tem fornecedor; 2000 fica no
--       filtro de proposito, para que a premissa nao vire filtro silencioso.
--   Ordem obrigatoria: 29c-sonda -> 29c -> 29d-controle -> 29d -> 29e. A 29c e a 29e usam
--   REBZG/REBZJ/REBZT, que so' a sonda prova. Sonda sem os campos = NAO rodar 29c nem 29e.
```

## B29d-controle o caminho pelo documento de compensacao funciona?  (rodar antes da 29d)
- **Tipo:** consulta
- **Pergunta:** O CAMINHO PELO DOCUMENTO DE COMPENSACAO FUNCIONA?  (rodar ANTES da 29d)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 29d-controle (linha 514)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
WITH fat AS (
    SELECT DISTINCT f.BUKRS, f.BELNR, f.GJAHR, f.AUGBL, f.AUGDT AS DATA_COMP,
           SUBSTRING(f.AUGDT, 1, 4) AS ANO_COMP
    FROM   SAPABAP1.BSEG f
    WHERE  f.MANDT = '400' AND f.GJAHR = '2026' AND f.KOART = 'K'
      AND  f.BUKRS IN ('1000','2000')
      AND  f.AUGDT <> '' AND f.AUGDT <> '00000000'
      AND  EXISTS (SELECT 1 FROM SAPABAP1.ACDOCA ti
                   WHERE ti.RCLNT = '400' AND ti.RLDNR = '0L' AND ti.GJAHR = f.GJAHR
                     AND ti.RBUKRS = f.BUKRS AND ti.BELNR = f.BELNR
                     AND ti.RCNTR IN ('0000122012','0000222012'))
),
par AS (
    SELECT fat.*,
           CASE WHEN fat.AUGBL = fat.BELNR AND fat.ANO_COMP = fat.GJAHR
                THEN 'S' ELSE 'N' END AS AUTO
    FROM   fat
)
SELECT COUNT(DISTINCT par.BUKRS || par.BELNR || par.AUGBL)                     AS PARES_FATURA_COMPENSACAO,
       COUNT(DISTINCT CASE WHEN par.AUTO = 'S'
                           THEN par.BUKRS || par.BELNR || par.AUGBL END)       AS AUTOCOMPENSADAS,
       COUNT(DISTINCT CASE WHEN par.AUTO = 'N' AND c.BELNR IS NOT NULL
                           THEN par.BUKRS || par.BELNR || par.AUGBL END)       AS COM_DOC_CONFIRMADO
FROM   par
LEFT   JOIN SAPABAP1.BSEG c
       ON  c.MANDT = '400'
       AND c.BUKRS = par.BUKRS
       AND c.BELNR = par.AUGBL
       AND c.GJAHR = par.ANO_COMP
       AND c.KOART = 'K'
       AND c.AUGBL = par.AUGBL
       AND c.AUGDT = par.DATA_COMP
```

## B29d residuo pelo segundo caminho: partida aberta no documento que compensou a fatura
- **Tipo:** consulta
- **Pergunta:** RESIDUO PELO SEGUNDO CAMINHO: PARTIDA ABERTA NO DOCUMENTO QUE COMPENSOU A FATURA
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 29d (linha 577)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
WITH fat AS (
    SELECT DISTINCT f.BUKRS, f.BELNR, f.GJAHR, f.LIFNR, f.AUGBL, f.AUGDT AS DATA_COMP,
           SUBSTRING(f.AUGDT, 1, 4) AS ANO_COMP
    FROM   SAPABAP1.BSEG f
    WHERE  f.MANDT = '400' AND f.GJAHR = '2026' AND f.KOART = 'K'
      AND  f.BUKRS IN ('1000','2000')
      AND  f.AUGDT <> '' AND f.AUGDT <> '00000000'
      AND  EXISTS (SELECT 1 FROM SAPABAP1.ACDOCA ti
                   WHERE ti.RCLNT = '400' AND ti.RLDNR = '0L' AND ti.GJAHR = f.GJAHR
                     AND ti.RBUKRS = f.BUKRS AND ti.BELNR = f.BELNR
                     AND ti.RCNTR IN ('0000122012','0000222012'))
),
-- sem as autocompensadas: nelas nao ha' documento de pagamento
fat_pag AS (
    SELECT * FROM fat
    WHERE  NOT (AUGBL = BELNR AND ANO_COMP = GJAHR)
),
-- documento de compensacao CONFIRMADO: tem partida de fornecedor compensada por ele
-- mesmo, na mesma data. Um documento por linha (DISTINCT).
doc AS (
    SELECT DISTINCT fp.BUKRS, fp.AUGBL, fp.ANO_COMP
    FROM   fat_pag fp
    INNER  JOIN SAPABAP1.BSEG c
           ON  c.MANDT = '400'
           AND c.BUKRS = fp.BUKRS
           AND c.BELNR = fp.AUGBL
           AND c.GJAHR = fp.ANO_COMP
           AND c.KOART = 'K'
           AND c.AUGBL = fp.AUGBL
           AND c.AUGDT = fp.DATA_COMP
),
-- partida de fornecedor ainda aberta nesses documentos: uma linha por partida
abertas AS (
    SELECT p.BUKRS, p.BELNR, p.GJAHR, p.BUZEI, p.LIFNR,
           CASE WHEN p.SHKZG = 'H' THEN p.DMBTR ELSE -p.DMBTR END AS VALOR_ABERTO
    FROM   doc d
    INNER  JOIN SAPABAP1.BSEG p
           ON  p.MANDT = '400'
           AND p.BUKRS = d.BUKRS
           AND p.BELNR = d.AUGBL
           AND p.GJAHR = d.ANO_COMP
           AND p.KOART = 'K'
           AND (p.AUGDT = '' OR p.AUGDT = '00000000')
)
SELECT a.BUKRS                                                       AS EMPRESA,
       a.BELNR                                                       AS DOC_COMPENSACAO,
       a.GJAHR                                                       AS ANO_DOC,
       a.BUZEI                                                       AS PARTIDA_ABERTA,
       a.LIFNR                                                       AS COD_FORNECEDOR,
       a.VALOR_ABERTO,
       COUNT(DISTINCT f.BELNR)                                       AS FATURAS_TI_NO_DOC,
       MIN(f.BELNR)                                                  AS UMA_DAS_FATURAS,
       CASE WHEN MAX(CASE WHEN f.LIFNR = a.LIFNR THEN 1 ELSE 0 END) = 1
            THEN 'S' ELSE 'N' END                                    AS MESMO_FORNECEDOR_DA_FATURA
FROM   abertas a
INNER  JOIN fat_pag f
       ON  f.BUKRS = a.BUKRS AND f.AUGBL = a.BELNR AND f.ANO_COMP = a.GJAHR
GROUP  BY a.BUKRS, a.BELNR, a.GJAHR, a.BUZEI, a.LIFNR, a.VALOR_ABERTO
ORDER  BY 1, 2, 4
```

## B29e existe cadeia de residuo?  (so' depois da 29c-sonda confirmar rebzg e rebzj)
- **Tipo:** consulta
- **Pergunta:** EXISTE CADEIA DE RESIDUO?  (so' depois da 29c-sonda confirmar REBZG e REBZJ)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 29e (linha 680)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
WITH salto1 AS (
    SELECT DISTINCT r.BUKRS, r.BELNR, r.GJAHR
    FROM   SAPABAP1.BSEG r
    WHERE  r.MANDT = '400' AND r.GJAHR = '2026' AND r.KOART = 'K'
      AND  r.BUKRS IN ('1000','2000')
      AND  r.REBZG <> ''
      AND  NOT (r.BELNR = r.REBZG AND r.GJAHR = r.REBZJ)
      AND  EXISTS (SELECT 1 FROM SAPABAP1.ACDOCA ti
                   WHERE ti.RCLNT = '400' AND ti.RLDNR = '0L'
                     AND ti.RBUKRS = r.BUKRS AND ti.BELNR = r.REBZG AND ti.GJAHR = r.REBZJ
                     AND ti.RCNTR IN ('0000122012','0000222012'))
)
SELECT COUNT(DISTINCT r2.BUKRS || r2.BELNR || r2.GJAHR)                           AS DOCUMENTOS,
       COUNT(*)                                                                   AS LINHAS,
       SUM(CASE WHEN r2.SHKZG = 'H' THEN r2.DMBTR ELSE -r2.DMBTR END)             AS VALOR,
       SUM(CASE WHEN r2.AUGDT = '' OR r2.AUGDT = '00000000' THEN 1 ELSE 0 END)    AS LINHAS_AINDA_ABERTAS
FROM   SAPABAP1.BSEG r2
INNER  JOIN salto1 s
       ON  r2.BUKRS = s.BUKRS AND r2.REBZG = s.BELNR AND r2.REBZJ = s.GJAHR
WHERE  r2.MANDT = '400' AND r2.KOART = 'K'
  AND  NOT (r2.BELNR = s.BELNR AND r2.GJAHR = s.GJAHR)
```

## B30 o nome de toda conta que passa pelo centro de custo de ti
- **Tipo:** consulta
- **Pergunta:** O NOME DE TODA CONTA QUE PASSA PELO CENTRO DE CUSTO DE TI
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 30 (linha 720)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT t.KTOPL AS PLANO_DE_CONTAS, t.SAKNR AS CONTA,
       t.TXT50 AS DESCRICAO, t.SPRAS AS IDIOMA
FROM   SAPABAP1.SKAT t
WHERE  t.MANDT = '400' AND t.SPRAS = 'P'
  AND  t.SAKNR IN ( SELECT DISTINCT a.RACCT
                    FROM   SAPABAP1.ACDOCA a
                    WHERE  a.RCLNT = '400' AND a.RLDNR = '0L' AND a.GJAHR = '2026'
                      AND  a.RCNTR IN ('0000122012','0000222012') )
ORDER  BY t.SAKNR, t.KTOPL
```

## B31 a filial existe? em qual campo? — probe antes de rodar a 24 de novo
- **Tipo:** consulta
- **Pergunta:** A FILIAL EXISTE? EM QUAL CAMPO? — probe ANTES de rodar a 24 de novo
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 31 (linha 748)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT COLUMN_NAME, DATA_TYPE_NAME, LENGTH
FROM   SYS.TABLE_COLUMNS
WHERE  SCHEMA_NAME = 'SAPABAP1' AND TABLE_NAME = 'ACDOCA'
  AND  (COLUMN_NAME LIKE '%BUPLA%'  OR COLUMN_NAME LIKE '%BRANCH%'
     OR COLUMN_NAME LIKE '%WERKS%'  OR COLUMN_NAME LIKE '%BUKRS%'
     OR COLUMN_NAME LIKE '%SEGMENT%')
ORDER  BY COLUMN_NAME
```

## B31b a medicao da filial — confirma ou derruba o 1001/1005
- **Tipo:** consulta
- **Pergunta:** A MEDICAO DA FILIAL — confirma ou derruba o 1001/1005
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 31b (linha 777)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT ti.RCNTR AS CENTRO_CUSTO, ti.RBUKRS AS EMPRESA,
       ti.BRANCH_ID AS FILIAL, ti.WERKS AS CENTRO,
       COUNT(*) AS LINHAS, SUM(ti.HSL) AS VALOR
FROM   SAPABAP1.ACDOCA ti
WHERE  ti.RCLNT = '400' AND ti.RLDNR = '0L' AND ti.GJAHR = '2026'
  AND  ti.RCNTR IN ('0000122012','0000222012')
GROUP  BY ti.RCNTR, ti.RBUKRS, ti.BRANCH_ID, ti.WERKS
ORDER  BY 1, 3
```

## B32 quanto pesa a fbl1n inteira — contar antes de extrair
- **Tipo:** consulta
- **Pergunta:** QUANTO PESA A FBL1N INTEIRA — CONTAR antes de extrair
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 32 (linha 797)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT b.BUKRS AS EMPRESA,
       LEFT(b.AUGDT,6) AS MES_COMPENSACAO,
       COUNT(*) AS PARTIDAS,
       COUNT(DISTINCT b.BELNR) AS DOCUMENTOS,
       COUNT(DISTINCT b.LIFNR) AS FORNECEDORES
FROM   SAPABAP1.BSEG b
WHERE  b.MANDT = '400' AND b.GJAHR = '2026' AND b.KOART = 'K'
  AND  b.BUKRS IN ('1000','2000')
GROUP  BY b.BUKRS, LEFT(b.AUGDT,6)
ORDER  BY 1, 2
```

## B33 a fbl1n inteira — todas as partidas de fornecedor, nao so' as de ti
- **Tipo:** consulta
- **Pergunta:** A FBL1N INTEIRA — todas as partidas de fornecedor, nao so' as de TI
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 33 (linha 825)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT b.BUKRS  AS EMPRESA,
       b.BELNR  AS DOCUMENTO,
       b.GJAHR  AS EXERCICIO,
       b.BUZEI  AS PARTIDA,
       b.LIFNR  AS COD_FORNECEDOR,
       l.NAME1  AS FORNECEDOR,
       l.STCD1  AS CNPJ,
       l.STCD2  AS CPF,
       h.XBLNR  AS NUMERO_TITULO,
       h.BLART  AS TIPO_DOC,
       h.BLDAT  AS EMISSAO,
       h.BUDAT  AS LANCAMENTO,
       b.ZFBDT  AS DATA_BASE,
       -- ACHADO DO QA: a versao anterior trazia so' `b.ZBD1T AS DIAS_PRAZO`. Um nome
       -- generico escondendo o campo que JA causou vencimento adiantado neste projeto —
       -- quem usasse a coluna direto deste export reproduziria o bug corrigido no 28.
       -- Os tres prazos saem com o nome do que sao, e o vencimento se calcula pela
       -- cascata ZBD3T > ZBD2T > ZBD1T (medido: aqui ZBD3T=0 e ZBD1P=0, entao vale o 1T).
       b.ZBD3T  AS DIAS_LIQUIDO,
       b.ZBD2T  AS DIAS_DESCONTO2,
       b.ZBD1T  AS DIAS_DESCONTO1,
       b.ZBD1P  AS PCT_DESCONTO1,
       b.ZTERM  AS COND_PAGAMENTO,
       b.SHKZG  AS DEB_CRED,
       CASE WHEN b.SHKZG = 'H' THEN b.DMBTR ELSE -b.DMBTR END AS VALOR_COM_SINAL,
       b.AUGDT  AS COMPENSACAO,
       b.AUGBL  AS DOC_COMPENSACAO,
       CASE WHEN b.AUGDT IS NULL OR b.AUGDT = '00000000'
            THEN 'EM ABERTO' ELSE 'COMPENSADA' END AS STATUS_PARTIDA
FROM       SAPABAP1.BSEG b
LEFT JOIN  SAPABAP1.BKPF h ON h.MANDT = '400' AND h.BUKRS = b.BUKRS
                          AND h.BELNR = b.BELNR AND h.GJAHR = b.GJAHR
LEFT JOIN  SAPABAP1.LFA1 l ON l.MANDT = '400' AND l.LIFNR = b.LIFNR
WHERE  b.MANDT = '400' AND b.GJAHR = '2026' AND b.KOART = 'K'
  AND  b.BUKRS IN ('1000','2000')
ORDER  BY b.BUKRS, b.BELNR, b.BUZEI
```

## B34 a linha do tempo do documento — onde cada lancamento parou
- **Tipo:** consulta
- **Pergunta:** A LINHA DO TEMPO DO DOCUMENTO — onde cada lancamento parou
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 34 (linha 884)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT  d.BUKRS      AS EMPRESA,
        d.BELNR      AS DOCUMENTO,
        d.GJAHR      AS EXERCICIO,
        d.BLART      AS TIPO_DOC,
        d.XBLNR      AS NUMERO_TITULO,
        d.BLDAT      AS EMISSAO_NF,
        d.BUDAT      AS LANCAMENTO,
        p.EBELN      AS PEDIDO,
        p.PEDIDOS_NO_DOC AS PEDIDOS_NO_DOC,
        p.BEDAT      AS DATA_PEDIDO,
        h.DATA_MIGO  AS DATA_MIGO,
        h.DATA_MIRO  AS DATA_MIRO,
        f.AUGDT      AS COMPENSACAO,
        f.LIFNR      AS COD_FORNECEDOR,
        l.NAME1      AS FORNECEDOR,
        l.STCD1      AS CNPJ,
        CASE WHEN p.EBELN IS NULL
                  THEN 'SEM PEDIDO DE COMPRA (fatura direta em FI — normal, nao pendencia)'
             WHEN h.DATA_MIGO IS NULL
                  THEN 'PEDIDO SEM ENTRADA DE MERCADORIA'
             WHEN h.DATA_MIRO IS NULL
                  THEN 'RECEBIDO E NAO FATURADO'
             WHEN f.AUGDT IS NULL OR f.AUGDT = '00000000'
                  THEN 'FATURADO E NAO PAGO'
             ELSE 'CICLO COMPLETO' END AS ONDE_PAROU
FROM       SAPABAP1.BKPF d
LEFT JOIN  ( SELECT a.RBUKRS, a.BELNR, a.GJAHR,
                    MAX(a.LIFNR) AS LIFNR, MAX(a.AUGDT) AS AUGDT
             FROM   SAPABAP1.ACDOCA a
             WHERE  a.RCLNT = '400' AND a.RLDNR = '0L' AND a.GJAHR = '2026'
               AND  a.LIFNR <> ''
             GROUP  BY a.RBUKRS, a.BELNR, a.GJAHR ) f
       ON  f.RBUKRS = d.BUKRS AND f.BELNR = d.BELNR AND f.GJAHR = d.GJAHR
LEFT JOIN  SAPABAP1.LFA1 l ON l.MANDT = '400' AND l.LIFNR = f.LIFNR
-- ACHADO DO QA: `MAX(o.EBELN)` colapsa o documento que toca MAIS DE UM pedido e fica
-- so' com o maior em ordem alfabetica — a DATA_PEDIDO reportada pode nao ser a do pedido
-- que importa, e ninguem fica sabendo. A coluna PEDIDOS_NO_DOC denuncia o caso: quando
-- for > 1, a data e' a do primeiro por data e ha' outros pedidos no mesmo documento.
LEFT JOIN  ( SELECT s.MANDT, s.BELNR, s.GJAHR, s.BUKRS,
                    MIN(o.BEDAT) AS BEDAT,
                    MIN(o.EBELN) AS EBELN,
                    COUNT(DISTINCT o.EBELN) AS PEDIDOS_NO_DOC
             FROM   SAPABAP1.BSEG s
             JOIN   SAPABAP1.EKKO o ON o.MANDT = s.MANDT AND o.EBELN = s.EBELN
             WHERE  s.MANDT = '400' AND s.GJAHR = '2026' AND s.EBELN <> ''
             GROUP  BY s.MANDT, s.BELNR, s.GJAHR, s.BUKRS ) p
       ON  p.MANDT = '400' AND p.BUKRS = d.BUKRS
       AND p.BELNR = d.BELNR AND p.GJAHR = d.GJAHR
-- ACHADO DO QA: havia `AND e.GJAHR = '2026'` aqui. O EKBE.GJAHR e' o exercicio do
-- PROPRIO lancamento de MIGO/MIRO — um pedido de 2025, recebido em 2025 e faturado em
-- 2026 ficaria com DATA_MIGO nula e seria rotulado "PEDIDO SEM ENTRADA DE MERCADORIA",
-- que e' FALSO: houve entrada, so' que fora da janela que eu mesmo filtrei. O historico
-- do pedido nao se corta por exercicio; quem se restringe a 2026 e' o documento contabil.
LEFT JOIN  ( SELECT e.MANDT, e.EBELN,
                    MAX(CASE WHEN e.VGABE = '1' THEN e.BUDAT END) AS DATA_MIGO,
                    MAX(CASE WHEN e.VGABE = '2' THEN e.BUDAT END) AS DATA_MIRO
             FROM   SAPABAP1.EKBE e
             WHERE  e.MANDT = '400'
             GROUP  BY e.MANDT, e.EBELN ) h
       ON  h.MANDT = '400' AND h.EBELN = p.EBELN
WHERE   d.MANDT = '400' AND d.GJAHR = '2026'
  AND   EXISTS ( SELECT 1 FROM SAPABAP1.ACDOCA ti
                 WHERE ti.RCLNT = '400' AND ti.RLDNR = '0L' AND ti.GJAHR = d.GJAHR
                   AND ti.RBUKRS = d.BUKRS AND ti.BELNR = d.BELNR
                   AND ti.RCNTR IN ('0000122012','0000222012') )
ORDER   BY d.BUKRS, d.BELNR
```

## B34b as 13 linhas sem cabecalho — r$ 581.061,34 que o left join nao achou
- **Tipo:** consulta
- **Pergunta:** AS 13 LINHAS SEM CABECALHO — R$ 581.061,34 que o LEFT JOIN nao achou
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 34b (linha 982)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
-- *** CORRIGIDO 22/09: `ti.AWKEY` nao existe na ACDOCA (AWKEY e' campo da BKPF). ***
-- Mesmo erro do BUPLA, na mesma sessao: escrevi um campo sem provar que ele existe.
-- Agora esta consulta usa SOMENTE campos ja' provados por execucao (ver o cabecalho do
-- arquivo); os campos de origem entram depois que o bloco 34c disser quais sao.
SELECT  ti.RBUKRS AS EMPRESA, ti.BELNR AS DOCUMENTO, ti.GJAHR AS EXERCICIO,
        ti.DOCLN AS LINHA, ti.RACCT AS CONTA, ti.HSL AS VALOR,
        ti.SGTXT AS HISTORICO, ti.RLDNR AS LEDGER, ti.LIFNR AS COD_FORNECEDOR,
        ti.AUGDT AS COMPENSACAO
FROM    SAPABAP1.ACDOCA ti
WHERE   ti.RCLNT = '400' AND ti.RLDNR = '0L' AND ti.GJAHR = '2026'
  AND   ti.RCNTR IN ('0000122012','0000222012')
  AND   NOT EXISTS ( SELECT 1 FROM SAPABAP1.BKPF h
                     WHERE h.MANDT = '400' AND h.BUKRS = ti.RBUKRS
                       AND h.BELNR = ti.BELNR AND h.GJAHR = ti.GJAHR )
ORDER   BY ti.HSL DESC
```

## B34c probe: os campos de origem da acdoca, e os codigos de vgabe que existem de fato
- **Tipo:** consulta
- **Pergunta:** PROBE: os campos de ORIGEM da ACDOCA, e os codigos de VGABE que existem de fato
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 34c (linha 1011)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT COLUMN_NAME, DATA_TYPE_NAME, LENGTH
FROM   SYS.TABLE_COLUMNS
WHERE  SCHEMA_NAME = 'SAPABAP1' AND TABLE_NAME = 'ACDOCA'
  AND  (COLUMN_NAME LIKE 'AW%' OR COLUMN_NAME LIKE '%REF%'
     OR COLUMN_NAME LIKE '%BUDAT%' OR COLUMN_NAME LIKE '%BLART%')
ORDER  BY COLUMN_NAME
```

## B34d quais codigos de movimento existem no historico do pedido
- **Tipo:** consulta
- **Pergunta:** QUAIS CODIGOS DE MOVIMENTO EXISTEM NO HISTORICO DO PEDIDO
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 34d (linha 1037)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT e.VGABE AS COD_MOVIMENTO, COUNT(*) AS LINHAS,
       COUNT(DISTINCT e.EBELN) AS PEDIDOS,
       MIN(e.BUDAT) AS PRIMEIRA_DATA, MAX(e.BUDAT) AS ULTIMA_DATA
FROM   SAPABAP1.EKBE e
WHERE  e.MANDT = '400'
  AND  e.EBELN IN ( SELECT DISTINCT s.EBELN
                    FROM   SAPABAP1.BSEG s
                    WHERE  s.MANDT = '400' AND s.GJAHR = '2026' AND s.EBELN <> ''
                      AND  EXISTS ( SELECT 1 FROM SAPABAP1.ACDOCA ti
                                    WHERE ti.RCLNT = '400' AND ti.RLDNR = '0L'
                                      AND ti.GJAHR = s.GJAHR AND ti.RBUKRS = s.BUKRS
                                      AND ti.BELNR = s.BELNR
                                      AND ti.RCNTR IN ('0000122012','0000222012') ) )
GROUP  BY e.VGABE
ORDER  BY 2 DESC
```

## B50-sonda os campos que ligam nf-e, fatura, estorno e saldo em/ef  (v13, 25/09/2026)
- **Tipo:** consulta
- **Pergunta:** OS CAMPOS QUE LIGAM NF-e, FATURA, ESTORNO E SALDO EM/EF  (v13, 25/09/2026)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 50-sonda (linha 1065)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE_NAME, LENGTH
FROM   SYS.TABLE_COLUMNS
WHERE  SCHEMA_NAME = 'SAPABAP1'
  AND  ( (TABLE_NAME = 'EKBE'      AND COLUMN_NAME IN ('EBELP','GJAHR','BELNR','BUZEI','BWART',
                                                       'MENGE','DMBTR','WRBTR','WAERS','SHKZG',
                                                       'LFBNR','LFGJA','XBLNR'))
      OR (TABLE_NAME = 'BKPF'      AND COLUMN_NAME IN ('STBLG','STJAH','STGRD','AWKEY','AWTYP',
                                                       'XREVERSAL','BKTXT'))
      OR (TABLE_NAME = 'J_1BNFLIN' AND COLUMN_NAME IN ('DOCNUM','ITMNUM','REFKEY','REFTYP',
                                                       'REFITM','NETWR','MATNR','CFOP'))
      OR (TABLE_NAME = 'RBKP'      AND COLUMN_NAME IN ('BELNR','GJAHR','STBLG','STJAH','XBLNR',
                                                       'BLDAT','BUDAT','RMWWR')) )
ORDER  BY TABLE_NAME, COLUMN_NAME
```

## B50 a base de ti enriquecida — nf-e, pedido, entrada, fatura, estorno, em/ef  (v14, 
- **Tipo:** consulta
- **Pergunta:** A BASE DE TI ENRIQUECIDA — NF-e, PEDIDO, ENTRADA, FATURA, ESTORNO, EM/EF  (v14, 25/09)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 50 (linha 1106)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT  d.BUKRS        AS EMPRESA,
        d.BELNR        AS DOCUMENTO,
        d.GJAHR        AS EXERCICIO,
        d.BLART        AS TIPO_DOC,
        d.XBLNR        AS NUMERO_TITULO,
        d.BLDAT        AS EMISSAO,
        d.BUDAT        AS LANCAMENTO,
        d.BKTXT        AS TEXTO,
        d.AWTYP        AS ORIGEM,
        d.XREVERSAL    AS IND_ESTORNO,
        d.STBLG        AS DOC_ESTORNO,
        d.STJAH        AS ANO_ESTORNO,
        d.STGRD        AS MOTIVO_ESTORNO,
        p.EBELN        AS PEDIDO,
        p.PEDIDOS_NO_DOC,
        p.BEDAT        AS DATA_PEDIDO,
        h.DATA_ENTRADA_MERCADORIA,
        CASE WHEN h.DATA_ENTRADA_MERCADORIA IS NULL THEN 'N' ELSE 'S' END AS TEM_ENTRADA_MERCADORIA,
        h.DATA_FATURA_PEDIDO,
        h.VALOR_ENTRADA_MERCADORIA,
        h.VALOR_FATURADO,
        COALESCE(h.VALOR_ENTRADA_MERCADORIA, 0) - COALESCE(h.VALOR_FATURADO, 0) AS DIFERENCA_EM_EF,
        r.BELNR        AS FATURA_MIRO,
        r.BLDAT        AS EMISSAO_MIRO,
        r.BUDAT        AS LANCAMENTO_MIRO,
        r.RMWWR        AS VALOR_BRUTO_MIRO,
        r.STBLG        AS ESTORNO_MIRO,
        nf.NFENUM      AS NFE,
        nf.SERIES      AS SERIE_NFE,
        nf.DOCDAT      AS DATA_NFE,
        nf.REFTYP      AS TIPO_REF_NFE,
        nf.NFES_NO_DOC,
        f.AUGDT        AS COMPENSACAO,
        f.LIFNR        AS COD_FORNECEDOR,
        CASE WHEN d.STBLG <> '' THEN 'ESTORNADO'
             WHEN f.LIFNR IS NULL
                  THEN 'SEM FORNECEDOR (rateio, provisao, depreciacao, baixa de estoque)'
             WHEN p.EBELN IS NULL AND (f.AUGDT IS NULL OR f.AUGDT = '00000000')
                  THEN 'SEM PEDIDO - EM ABERTO'
             WHEN p.EBELN IS NULL THEN 'SEM PEDIDO - PAGO'
             WHEN f.AUGDT IS NULL OR f.AUGDT = '00000000' THEN 'COM PEDIDO - EM ABERTO'
             ELSE 'COM PEDIDO - PAGO' END AS SITUACAO
FROM       SAPABAP1.BKPF d
LEFT JOIN  ( SELECT a.RBUKRS, a.BELNR, a.GJAHR,
                    MAX(a.LIFNR) AS LIFNR, MAX(a.AUGDT) AS AUGDT
             FROM   SAPABAP1.ACDOCA a
             WHERE  a.RCLNT = '400' AND a.RLDNR = '0L' AND a.GJAHR = '2026'
               AND  a.LIFNR <> ''
             GROUP  BY a.RBUKRS, a.BELNR, a.GJAHR ) f
       ON  f.RBUKRS = d.BUKRS AND f.BELNR = d.BELNR AND f.GJAHR = d.GJAHR
LEFT JOIN  ( SELECT s.BUKRS, s.BELNR, s.GJAHR,
                    MIN(o.EBELN) AS EBELN, MIN(o.BEDAT) AS BEDAT,
                    COUNT(DISTINCT o.EBELN) AS PEDIDOS_NO_DOC
             FROM   SAPABAP1.BSEG s
             JOIN   SAPABAP1.EKKO o ON o.MANDT = s.MANDT AND o.EBELN = s.EBELN
             WHERE  s.MANDT = '400' AND s.GJAHR = '2026' AND s.EBELN <> ''
             GROUP  BY s.BUKRS, s.BELNR, s.GJAHR ) p
       ON  p.BUKRS = d.BUKRS AND p.BELNR = d.BELNR AND p.GJAHR = d.GJAHR
LEFT JOIN  ( SELECT e.EBELN,
                    MAX(CASE WHEN e.VGABE = '1' THEN e.BUDAT END) AS DATA_ENTRADA_MERCADORIA,
                    MAX(CASE WHEN e.VGABE = '2' THEN e.BUDAT END) AS DATA_FATURA_PEDIDO,
                    SUM(CASE WHEN e.VGABE = '1' THEN
                             CASE WHEN e.SHKZG = 'H' THEN -e.DMBTR ELSE e.DMBTR END END) AS VALOR_ENTRADA_MERCADORIA,
                    SUM(CASE WHEN e.VGABE = '2' THEN
                             CASE WHEN e.SHKZG = 'H' THEN -e.DMBTR ELSE e.DMBTR END END) AS VALOR_FATURADO
             FROM   SAPABAP1.EKBE e
             WHERE  e.MANDT = '400'
               AND  e.EBELN IN ( SELECT DISTINCT s2.EBELN
                                 FROM   SAPABAP1.BSEG s2
                                 WHERE  s2.MANDT = '400' AND s2.GJAHR = '2026' AND s2.EBELN <> ''
                                   AND  EXISTS ( SELECT 1 FROM SAPABAP1.ACDOCA t2
                                                 WHERE t2.RCLNT = '400' AND t2.RLDNR = '0L'
                                                   AND t2.GJAHR = s2.GJAHR AND t2.RBUKRS = s2.BUKRS
                                                   AND t2.BELNR = s2.BELNR
                                                   AND t2.RCNTR IN ('0000122012','0000222012') ) )
             GROUP  BY e.EBELN ) h
       ON  h.EBELN = p.EBELN
LEFT JOIN  ( SELECT x.BELNR, x.GJAHR,
                    MIN(x.BLDAT) AS BLDAT, MIN(x.BUDAT) AS BUDAT,
                    MAX(x.RMWWR) AS RMWWR, MAX(x.STBLG) AS STBLG
             FROM   SAPABAP1.RBKP x
             WHERE  x.MANDT = '400' AND x.GJAHR = '2026'
             GROUP  BY x.BELNR, x.GJAHR ) r
       ON  d.AWTYP = 'RMRP'
       AND r.BELNR = SUBSTRING(d.AWKEY, 1, 10) AND r.GJAHR = SUBSTRING(d.AWKEY, 11, 4)
LEFT JOIN  ( SELECT l.REFKEY,
                    MIN(n.NFENUM) AS NFENUM, MIN(n.SERIES) AS SERIES, MIN(n.DOCDAT) AS DOCDAT,
                    MIN(l.REFTYP) AS REFTYP, COUNT(DISTINCT n.DOCNUM) AS NFES_NO_DOC
             FROM   SAPABAP1.J_1BNFLIN l
             JOIN   SAPABAP1.J_1BNFDOC n ON n.MANDT = l.MANDT AND n.DOCNUM = l.DOCNUM
             WHERE  l.MANDT = '400' AND n.CANCEL <> 'X' AND n.DOCDAT >= '20250101'
             GROUP  BY l.REFKEY ) nf
       ON  nf.REFKEY = d.AWKEY
WHERE   d.MANDT = '400' AND d.GJAHR = '2026'
  AND   EXISTS ( SELECT 1 FROM SAPABAP1.ACDOCA ti
                 WHERE ti.RCLNT = '400' AND ti.RLDNR = '0L' AND ti.GJAHR = d.GJAHR
                   AND ti.RBUKRS = d.BUKRS AND ti.BELNR = d.BELNR
                   AND ti.RCNTR IN ('0000122012','0000222012') )
ORDER   BY d.BUKRS, d.BELNR
```

## B51-sonda o que existe para a linha do tempo completa do custo  (v16, 26/09/2026)
- **Tipo:** consulta
- **Pergunta:** O QUE EXISTE PARA A LINHA DO TEMPO COMPLETA DO CUSTO  (v16, 26/09/2026)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql, bloco 51-sonda (linha 1248)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql

Copiar do arquivo apontado: o bloco traz comentários `--` que o Editor SQL do DBACOCKPIT corta.

```sql
SELECT 'TABELA' AS TIPO, SCHEMA_NAME AS ESQUEMA, TABLE_NAME AS TABELA, '' AS CAMPO
FROM   SYS.TABLES
WHERE  (SCHEMA_NAME = 'SAPABAP1' AND TABLE_NAME IN ('EBAN','J_1BNFE_ACTIVE'))
   OR  TABLE_NAME LIKE '/XNFE/%'
UNION ALL
SELECT 'TABELA', SCHEMA_NAME, VIEW_NAME, ''
FROM   SYS.VIEWS
WHERE  (SCHEMA_NAME = 'SAPABAP1' AND VIEW_NAME IN ('EBAN','J_1BNFE_ACTIVE'))
   OR  VIEW_NAME LIKE '/XNFE/%'
UNION ALL
SELECT 'CAMPO', SCHEMA_NAME, TABLE_NAME, COLUMN_NAME
FROM   SYS.TABLE_COLUMNS
WHERE  SCHEMA_NAME = 'SAPABAP1'
  AND  ( (TABLE_NAME = 'EBAN'           AND COLUMN_NAME IN ('MANDT','BANFN','BNFPO','BADAT','ERDAT',
                                                            'FRGDT','AFNAM','EBELN','EBELP','LOEKZ'))
      OR (TABLE_NAME = 'EKPO'           AND COLUMN_NAME IN ('MANDT','EBELN','EBELP','BANFN','BNFPO',
                                                            'AEDAT','LOEKZ'))
      OR (TABLE_NAME = 'BKPF'           AND COLUMN_NAME IN ('CPUDT','CPUTM','USNAM','TCODE'))
      OR (TABLE_NAME = 'RBKP'           AND COLUMN_NAME IN ('MANDT','CPUDT','CPUTM','LIFNR','ZUONR'))
      OR (TABLE_NAME = 'J_1BNFDOC'      AND COLUMN_NAME IN ('BELNR','GJAHR','DOCREF','CREDAT','CRETIM',
                                                            'NFE','NFNUM','NFENUM','AUTHDATE','AUTHTIM'))
      OR (TABLE_NAME = 'J_1BNFE_ACTIVE' AND COLUMN_NAME IN ('MANDT','DOCNUM','REGIO','NFYEAR','NFMONTH',
                                                            'STCD1','MODEL','SERIE','NFNUM9','DOCNUM9',
                                                            'CDV','AUTHDATE','AUTHTIME','DOCSTA','SCSSTA')) )
ORDER  BY 1 DESC, 2, 3, 4
```

## ACDOCA usa RCLNT
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql (regras e resultados registrados no próprio arquivo)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)

A ACDOCA usa `RCLNT`, não `MANDT` (BSEG, LFA1, SETLEAF e CSKS usam `MANDT`); a ACDOCP usa `RYEAR`, não `GJAHR`.

## fornecedor não está na linha de despesa
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql (regras e resultados registrados no próprio arquivo)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)

`ACDOCA-LIFNR` vem vazio na linha de despesa; o fornecedor está na linha de fornecedor do mesmo documento (usar EXISTS no documento).

## ACDOCA sem BUPLA e AWKEY
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql (regras e resultados registrados no próprio arquivo)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)

A ACDOCA não tem BUPLA nem AWKEY (erro real em produção); a filial está em `BRANCH_ID` (há também WERKS, RBUKRS, SEGMENT).

## BSAK e BSIK não existem no HANA
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql (regras e resultados registrados no próprio arquivo)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)

BSAK e BSIK são views de compatibilidade do ABAP: SQL direto dá `invalid table name`; a partida de fornecedor por SQL está na BSEG.

## prazo de pagamento em ZBD1T
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql (regras e resultados registrados no próprio arquivo)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)

21/09/2026: `ZBD3T` = 0 e `ZBD1P` = 0 em 422 de 422 títulos; o prazo real está em `ZBD1T` (cascata ZBD3T > ZBD2T > ZBD1T sobre ZFBDT).

## códigos de VGABE
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql (regras e resultados registrados no próprio arquivo)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)

Na EKBE, `VGABE` 1 = entrada de mercadoria e 2 = entrada de fatura; `SHKZG` S soma e H subtrai.

## RBKP ligada ao BKPF pelo AWKEY
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql (regras e resultados registrados no próprio arquivo)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO

`RBKP-BELNR` = 10 primeiros caracteres do `BKPF-AWKEY`, `GJAHR` = 4 seguintes (não conferido no dicionário).

## NF-e não liga pela REFKEY
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql (regras e resultados registrados no próprio arquivo)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)

25/09/2026: a ligação NF-e × fatura por `J_1BNFLIN-REFKEY` = AWKEY achou só 1 de 426 faturas logísticas de TI (refuta a hipótese).

## TI fatura sem entrada de mercadoria
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** C:\Users\fabriciosouza\budget-opex\CONSULTAS-SAP-FINAL-v17.sql (regras e resultados registrados no próprio arquivo)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução registrada no arquivo de origem (sessão do budget TI)

Pedidos de TI: 748 movimentos de fatura contra 8 de entrada de mercadoria; faturar sem entrada é o padrão da área.
