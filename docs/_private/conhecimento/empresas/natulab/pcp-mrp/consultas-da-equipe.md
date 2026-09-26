# pcp-mrp · consultas-da-equipe

Gerado em 26/09/2026 por `C:\Users\fabriciosouza\sap-mrp-natulab\gestao\_migracao-scripts\gerar_biblioteca_natulab.py`
a partir das fontes apontadas em cada entrada (SQL copiado sem edição). Consulta em uso num projeto continua no projeto.
## Q1 Params MRP VALIDADA
- **Tipo:** consulta
- **Pergunta:** Q1 - PARAMETROS MRP (MARC+MARA+MAKT) - VERSAO FINAL VALIDADA
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q1 Params MRP VALIDADA" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução da equipe no NSQ (Guia Rapido Queries, 25/03/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
-- VALIDADA: todos os campos confirmados via SE16N neste ambiente NSQ
-- Aliases: A=MARC (NSDM_V_MARC) B=MAKT C=MARA
-- Correcoes v2: B.MTART -> C.MTART | A.IPRKZ -> C.IPRKZ | FXHOR removido | BESKZ adicionado
SELECT DISTINCT
    A.WERKS                  AS Centro,
    LTRIM(A.MATNR, '0')      AS Cod_Material,
    B.MAKTX                  AS Descricao_Material,
    C.MTART                  AS Tipo_Material,
    C.MSTAE                  AS Status_Material,
    A.MMSTA                  AS Status_Centro,
    A.MMSTD                  AS Valido_Ate_Status,
    A.DISMM                  AS Tipo_MRP,
    A.DISPR                  AS Perfil_MRP,
    A.DISPO                  AS Responsavel_MRP,
    A.BESKZ                  AS Tipo_Suprimento,
    A.SOBSL                  AS Suprimento_Especial,
    A.DISLS                  AS Tamanho_Lote,
    A.BSTMI                  AS Lote_Minimo,
    A.BSTMA                  AS Lote_Maximo,
    A.BSTFE                  AS Lote_Fixo,
    A.DISGR                  AS Grupo_MRP,
    A.EISBE                  AS Estoque_Seguranca,
    A.MINBE                  AS Ponto_Reposicao,
    A.MABST                  AS Estoque_Maximo,
    A.PLIFZ                  AS Lead_Time_Planejado,
    A.WEBAZ                  AS Prazo_Entrada_Mercadoria,
    A.WZEIT                  AS Prazo_Saida_Mercadoria,
    A.STRGR                  AS Estrategia_Planejamento,
    A.VRMOD                  AS Modo_Consumo_Previsao,
    A.VINT1                  AS Consumo_Para_Tras,
    A.VINT2                  AS Consumo_Para_Frente,
    A.MTVFP                  AS Verificacao_Disponib,
    A.LGPRO                  AS Deposito_Producao,
    A.LGFSB                  AS Deposito_Forn_Especial,
    A.EKGRP                  AS Grupo_Compradores,
    C.IPRKZ                  AS Indicador_Periodo,
    C.MHDRZ                  AS Shelf_Life_Total,
    C.MHDLP                  AS Shelf_Life_Min_Restante
FROM MARC AS A
INNER JOIN MAKT AS B  ON A.MATNR = B.MATNR AND B.SPRAS = 'P'
INNER JOIN MARA AS C  ON A.MATNR = C.MATNR
WHERE  A.WERKS IN ('1001', '1005')
  AND  C.MTART IN ('FERT', 'HAWA', 'HALB', 'ROH', 'VERP')
  AND  C.MSTAE NOT IN ('O1', 'Z4')
  AND  A.DISMM != ''
ORDER BY A.WERKS, LTRIM(A.MATNR, '0')
```

## Q1B Params Aprofundado
- **Tipo:** consulta
- **Pergunta:** Q1B — PARÂMETROS APROFUNDAMENTO — v9 FINAL 26/03/2026
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q1B Params Aprofundado" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
SELECT DISTINCT
    A.WERKS                        AS Centro,
    LTRIM(A.MATNR, '0')            AS Cod_Material,
    B.MAKTX                        AS Descricao,
    C.MTART                        AS Tipo_Material,
    A.DISLS                        AS Tamanho_Lote,
    COALESCE(A.LOSGR, 0)           AS Lote_Producao_Validado,
    K.VERID                        AS Versao_Producao,
    COALESCE(C.MHDRZ, 0)          AS Shelf_Life_Min_Restante,
    COALESCE(C.MHDHB, 0)          AS Shelf_Life_Total,
    A.STRGR                        AS Estrategia_Planejamento,
    A.MTVFP                        AS Grupo_Verif_Disponib,
    COALESCE(A.EKGRP, '')          AS Grupo_Compradores,
    CASE
        WHEN C.MTART IN ('FERT','HALB')
         AND K.VERID IS NULL                    THEN '1-SEM VERSAO PROD'
        WHEN A.DISLS = 'FX'
         AND COALESCE(A.LOSGR,0) = 0            THEN '2-LOTE FX SEM VALOR'
        WHEN COALESCE(C.MHDHB,0) = 0
         AND C.MTART = 'FERT'                   THEN '3-SHELF LIFE AUSENTE'
        WHEN COALESCE(A.EKGRP,'') = ''
         AND C.MTART IN ('ROH','VERP')          THEN '4-SEM GRUPO COMPRADORES'
        ELSE 'OK'
    END                            AS Diagnostico_Complementar
FROM MARC AS A
INNER JOIN MAKT AS B  ON A.MATNR = B.MATNR AND B.SPRAS = 'P'
INNER JOIN MARA AS C  ON A.MATNR = C.MATNR
LEFT  JOIN MKAL AS K  ON A.MATNR = K.MATNR AND A.WERKS = K.WERKS
WHERE A.WERKS IN ('1001', '1005')
  AND C.MTART IN ('FERT', 'HAWA', 'HALB', 'ROH', 'VERP')
  AND C.MSTAE NOT IN ('O1', 'Z4')
  AND COALESCE(A.DISMM,'') NOT IN ('','ND')
ORDER BY A.WERKS, Diagnostico_Complementar, LTRIM(A.MATNR,'0')
```

## Q2 Estoque Disponivel
- **Tipo:** consulta
- **Pergunta:** Q2 — ESTOQUE DISPONIVEL POR DEPOSITO (MARD + MARA + MAKT) — ✅ VALIDADA 36.248 linhas
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q2 Estoque Disponivel" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução da equipe no NSQ (Guia Rapido Queries, 25/03/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
-- ✅ VALIDADA 25/03/2026: 36.248 linhas retornadas em QAS (NSQ)
-- LICAO: MARD = NSDM_V_MARD (view, nao tabela fisica). COALESCE obrigatorio.
-- Campos confirmados via SE16N: LABST(Util.livre) INSME(Contr.qualid.) SPEME(Estq.bloqueado)
--                               UMLME(Transf.estoque) EINME(Restrito)
-- Aliases: D=MARD  B=MAKT  C=MARA
SELECT
    D.WERKS                                           AS Centro,
    D.LGORT                                           AS Deposito,
    LTRIM(D.MATNR, '0')                               AS Cod_Material,
    B.MAKTX                                           AS Descricao_Material,
    C.MTART                                           AS Tipo_Material,
    COALESCE(D.LABST, 0)                              AS Estoque_Irrestrito,
    COALESCE(D.INSME, 0)                              AS Estoque_Inspecao_QM,
    COALESCE(D.SPEME, 0)                              AS Estoque_Bloqueado,
    COALESCE(D.UMLME, 0)                              AS Em_Transferencia,
    COALESCE(D.EINME, 0)                              AS EM_Bloqueada,
    COALESCE(D.LABST, 0) + COALESCE(D.INSME, 0)      AS Utilizavel_Potencial_MRP
FROM MARD AS D
INNER JOIN MAKT AS B
    ON D.MATNR = B.MATNR AND B.SPRAS = 'P'
INNER JOIN MARA AS C
    ON D.MATNR = C.MATNR
WHERE
    D.WERKS IN ('1001', '1005')
    AND C.MTART IN ('FERT', 'HAWA', 'HALB', 'ROH', 'VERP')
    AND C.MSTAE NOT IN ('O1', 'Z4')
ORDER BY D.WERKS, D.LGORT, LTRIM(D.MATNR, '0')
```

## Q2B Estoque Saldos Ativos
- **Tipo:** consulta
- **Pergunta:** Q2B — ESTOQUE POR DEPÓSITO (MARD) — CAMPOS CORRETOS — RETORNA ZEROS
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q2B Estoque Saldos Ativos" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
SELECT
    D.WERKS                                            AS Centro,
    D.LGORT                                            AS Deposito,
    LTRIM(D.MATNR, '0')                                AS Cod_Material,
    B.MAKTX                                            AS Descricao_Material,
    C.MTART                                            AS Tipo_Material,
    COALESCE(D.LABST, 0)                               AS Estoque_Irrestrito,
    COALESCE(D.INSME, 0)                               AS Estoque_Inspecao_QM,
    COALESCE(D.SPEME, 0)                               AS Estoque_Bloqueado,
    COALESCE(D.UMLME, 0)                               AS Em_Transferencia,
    COALESCE(D.EINME, 0)                               AS EM_Bloqueada,
    COALESCE(D.LABST, 0) + COALESCE(D.INSME, 0)       AS Utilizavel_Potencial_MRP
FROM MARD AS D
INNER JOIN MAKT AS B ON D.MATNR = B.MATNR AND B.SPRAS = 'P'
INNER JOIN MARA AS C ON D.MATNR = C.MATNR
WHERE D.WERKS IN ('1001', '1005')
  AND C.MTART IN ('FERT','HAWA','HALB','ROH','VERP','ZDES')
  AND C.MSTAE NOT IN ('O1','Z4')
ORDER BY D.WERKS, D.LGORT, LTRIM(D.MATNR, '0')
```

## Q2C Estoque por Lote MCHB
- **Tipo:** consulta
- **Pergunta:** Q2C — ESTOQUE POR LOTE (MCHB) — STEP 2: executar após confirmar Q2C_PreCheck
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q2C Estoque por Lote MCHB" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
SELECT
    M.WERKS                                            AS Centro,
    M.LGORT                                            AS Deposito,
    LTRIM(M.MATNR, '0')                                AS Cod_Material,
    B.MAKTX                                            AS Descricao_Material,
    C.MTART                                            AS Tipo_Material,
    M.CHARG                                            AS Lote,
    COALESCE(M.LABST, 0)                               AS Estoque_Irrestrito,
    COALESCE(M.INSME, 0)                               AS Estoque_Inspecao_QM,
    COALESCE(M.SPEME, 0)                               AS Estoque_Bloqueado,
    COALESCE(M.UMLME, 0)                               AS Em_Transferencia,
    COALESCE(M.EINME, 0)                               AS EM_Restrita,
    COALESCE(M.LABST, 0) + COALESCE(M.INSME, 0)       AS Utilizavel_Potencial_MRP
FROM MCHB AS M
INNER JOIN MAKT AS B ON M.MATNR = B.MATNR AND B.SPRAS = 'P'
INNER JOIN MARA AS C ON M.MATNR = C.MATNR
WHERE M.WERKS IN ('1001', '1005')
  AND C.MTART IN ('FERT','HAWA','HALB','ROH','VERP','ZDES')
  AND C.MSTAE NOT IN ('O1','Z4')
  AND (
       COALESCE(M.LABST, 0) > 0
    OR COALESCE(M.INSME, 0) > 0
    OR COALESCE(M.SPEME, 0) > 0
  )
ORDER BY M.WERKS, M.LGORT, LTRIM(M.MATNR, '0'), M.CHARG
```

## Q3 Lista Tecnica BOM
- **Tipo:** consulta
- **Pergunta:** Q3 — LISTA TECNICA / BOM (MAST+STKO+STPO+MARA) — VALIDADA 4.636 linhas
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q3 Lista Tecnica BOM" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução da equipe no NSQ (Guia Rapido Queries, 25/03/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
SELECT DISTINCT
    G.WERKS                    AS Centro,
    LTRIM(G.MATNR, '0')        AS Cod_PA,
    G.STLNR                    AS Num_BOM,
    G.STLAL                    AS Alt_BOM,
    G.STLAN                    AS Utilizacao_BOM,
    I.STLST                    AS Status_BOM,
    COALESCE(I.BMENG, 0)       AS Qtd_Base,
    I.BMEIN                    AS UM_Base,
    LTRIM(J.IDNRK, '0')        AS Cod_Comp,
    C_CO.MTART                 AS Tipo_Comp,
    COALESCE(J.MENGE, 0)       AS Quantidade,
    J.MEINS                    AS Unidade,
    COALESCE(J.AUSCH, 0)       AS Perc_Sucata,
    J.SCHGT                    AS Fantasma,
    J.LGORT                    AS Deposito,
    J.DATUV                    AS Valido_De,
    J.VALID_TO                 AS Valido_Ate
FROM MAST AS G
INNER JOIN STKO AS I
    ON G.STLNR = I.STLNR AND G.STLAL = I.STLAL
INNER JOIN STPO AS J
    ON I.STLNR = J.STLNR
INNER JOIN MARA AS C_PA
    ON G.MATNR = C_PA.MATNR
INNER JOIN MARA AS C_CO
    ON J.IDNRK = C_CO.MATNR
WHERE G.WERKS IN ('1001', '1005')
  AND G.STLAN = '1'
  AND I.STLST IN ('01', '04')
  AND C_PA.MTART IN ('FERT', 'HALB')
ORDER BY G.WERKS, LTRIM(G.MATNR, '0'), J.DATUV
```

## Q3B BOM Com Descricao FERT+HALB
- **Tipo:** consulta
- **Pergunta:** Q3B — BOM COM DESCRIÇÃO DE COMPONENTES — FERT e HALB — UNIFICADA v12
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q3B BOM Com Descricao FERT+HALB" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
SELECT DISTINCT
    G.WERKS               AS Centro,
    LTRIM(G.MATNR, '0')   AS Cod_PA,
    B_PA.MAKTX            AS Desc_PA,
    C_PA.MTART            AS Tipo_PA,
    G.STLNR               AS Num_BOM,
    G.STLAN               AS Utilizacao_BOM,
    I.STLST               AS Status_BOM,
    COALESCE(I.BMENG, 0)  AS Qtd_Base,
    I.BMEIN               AS UM_Base,
    LTRIM(J.IDNRK, '0')   AS Cod_Comp,
    B_CO.MAKTX            AS Desc_Comp,
    C_CO.MTART            AS Tipo_Comp,
    COALESCE(J.MENGE, 0)  AS Quantidade,
    J.MEINS               AS Unidade,
    COALESCE(J.AUSCH, 0)  AS Perc_Sucata,
    J.DATUV               AS Valido_De,
    J.VALID_TO            AS Valido_Ate
FROM MAST AS G
INNER JOIN STKO AS I    ON G.STLNR = I.STLNR AND G.STLAL = I.STLAL
INNER JOIN STPO AS J    ON I.STLNR = J.STLNR
INNER JOIN MARA AS C_PA ON G.MATNR = C_PA.MATNR
INNER JOIN MARA AS C_CO ON J.IDNRK = C_CO.MATNR
INNER JOIN MAKT AS B_PA ON G.MATNR = B_PA.MATNR AND B_PA.SPRAS = 'P'
INNER JOIN MAKT AS B_CO ON J.IDNRK = B_CO.MATNR AND B_CO.SPRAS = 'P'
WHERE G.WERKS IN ('1001', '1005')
  AND G.STLAN = '1'
  AND I.STLST IN ('01', '04')
  AND C_PA.MTART IN ('FERT', 'HALB')
ORDER BY G.WERKS, C_PA.MTART, LTRIM(G.MATNR, '0'), J.DATUV
```

## Q3B BOM Com Descricao FERT
- **Tipo:** consulta
- **Pergunta:** Q3B — BOM COM DESCRICAO DE COMPONENTES — FERT (repetir para HALB trocando MTART)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q3B BOM Com Descricao FERT" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
SELECT DISTINCT
    G.WERKS               AS Centro,
    LTRIM(G.MATNR, '0')   AS Cod_PA,
    B_PA.MAKTX            AS Desc_PA,
    G.STLNR               AS Num_BOM,
    G.STLAN               AS Utilizacao_BOM,
    I.STLST               AS Status_BOM,
    COALESCE(I.BMENG, 0)  AS Qtd_Base,
    I.BMEIN               AS UM_Base,
    LTRIM(J.IDNRK, '0')   AS Cod_Comp,
    B_CO.MAKTX            AS Desc_Comp,
    C_CO.MTART            AS Tipo_Comp,
    COALESCE(J.MENGE, 0)  AS Quantidade,
    J.MEINS               AS Unidade,
    COALESCE(J.AUSCH, 0)  AS Perc_Sucata,
    J.DATUV               AS Valido_De,
    J.VALID_TO            AS Valido_Ate
FROM MAST AS G
INNER JOIN STKO AS I    ON G.STLNR = I.STLNR AND G.STLAL = I.STLAL
INNER JOIN STPO AS J    ON I.STLNR = J.STLNR
INNER JOIN MARA AS C_PA ON G.MATNR = C_PA.MATNR
INNER JOIN MARA AS C_CO ON J.IDNRK = C_CO.MATNR
INNER JOIN MAKT AS B_PA ON G.MATNR = B_PA.MATNR AND B_PA.SPRAS = 'P'
INNER JOIN MAKT AS B_CO ON J.IDNRK = B_CO.MATNR AND B_CO.SPRAS = 'P'
WHERE G.WERKS IN ('1001', '1005')
  AND G.STLAN = '1'
  AND I.STLST IN ('01', '04')
  AND C_PA.MTART = 'FERT'
ORDER BY G.WERKS, LTRIM(G.MATNR, '0'), J.DATUV
```

## Q3C Versoes de Producao
- **Tipo:** consulta
- **Pergunta:** Q3C — VERSÕES DE PRODUÇÃO (MKAL) — v8 26/03/2026 — CAMPOS CONFIRMADOS VIA SE16N
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q3C Versoes de Producao" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
SELECT DISTINCT
    A.WERKS               AS Centro,
    LTRIM(A.MATNR, '0')   AS Cod_Material,
    B.MAKTX               AS Descricao,
    C.MTART               AS Tipo_Material,
    K.VERID               AS Versao_Producao,
    K.STLAL               AS Alt_BOM_Vinculada,
    K.STLAN               AS Utilizacao_BOM,
    K.PLNTY               AS Tipo_Roteiro,
    K.PLNNR               AS Grupo_Roteiro,
    K.ALNAL               AS Alt_Roteiro,
    K.ADATU               AS Valido_De,
    K.BDATU               AS Valido_Ate,
    K.LOSGR               AS Lote_Validado,
    CASE
        WHEN K.VERID IS NULL                    THEN '0-SEM VERSAO CADASTRADA'
        WHEN K.BDATU < CURRENT_DATE             THEN '1-VERSAO EXPIRADA'
        WHEN COALESCE(K.STLAL,'') = ''         THEN '2-SEM BOM VINCULADA'
        WHEN COALESCE(K.PLNNR,'') = ''         THEN '3-SEM ROTEIRO VINCULADO'
        ELSE 'OK'
    END                   AS Status_Versao
FROM MARC AS A
INNER JOIN MAKT AS B  ON A.MATNR = B.MATNR AND B.SPRAS = 'P'
INNER JOIN MARA AS C  ON A.MATNR = C.MATNR
LEFT  JOIN MKAL AS K  ON A.MATNR = K.MATNR AND A.WERKS = K.WERKS
WHERE A.WERKS IN ('1001', '1005')
  AND C.MTART IN ('FERT', 'HALB')
  AND C.MSTAE NOT IN ('O1', 'Z4')
  AND COALESCE(A.DISMM,'') NOT IN ('', 'ND')
ORDER BY A.WERKS, Status_Versao, LTRIM(A.MATNR, '0')
```

## Q4 Lead Time Fornecimento
- **Tipo:** consulta
- **Pergunta:** Q4 — LEAD TIMES E FORNECIMENTO — v10 CORRIGIDA 27/03/2026
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q4 Lead Time Fornecimento" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
SELECT DISTINCT
    A.WERKS                               AS Centro,
    LTRIM(A.MATNR, '0')                   AS Cod_Material,
    B.MAKTX                               AS Descricao,
    C.MTART                               AS Tipo_Material,
    A.BESKZ                               AS Tipo_Suprimento,
    COALESCE(A.PLIFZ, 0)                  AS Lead_Time_MARC,
    COALESCE(A.WEBAZ, 0)                  AS Prazo_Entrada_GR,
    A.LGPRO                               AS Deposito_Producao,
    A.EKGRP                               AS Grupo_Compradores,
    E.INFNR                               AS Num_Info_Registro,
    E.LIFNR                               AS Fornecedor_Info,
    G.NAME1                               AS Nome_Fornecedor,
    COALESCE(F.MINBM, 0)                  AS Lote_Min_Compra,
    COALESCE(F.NORBM, 0)                  AS Lote_Normal_Compra,
    COALESCE(F.APLFZ, 0)                  AS Lead_Time_Fornecedor,
    COALESCE(F.NETPR, 0)                  AS Preco_Liquido
FROM MARC AS A
INNER JOIN MAKT AS B   ON A.MATNR = B.MATNR AND B.SPRAS = 'P'
INNER JOIN MARA AS C   ON A.MATNR = C.MATNR
LEFT  JOIN EINA AS E   ON A.MATNR = E.MATNR
LEFT  JOIN EINE AS F   ON E.INFNR = F.INFNR AND F.WERKS = A.WERKS
LEFT  JOIN LFA1 AS G   ON E.LIFNR = G.LIFNR
WHERE A.WERKS IN ('1001', '1005')
  AND C.MTART IN ('ROH', 'VERP', 'HAWA')
  AND C.MSTAE NOT IN ('O1', 'Z4')
  AND COALESCE(A.DISMM,'') NOT IN ('', 'ND')
ORDER BY A.WERKS, C.MTART, LTRIM(A.MATNR, '0')
```

## Q5 Ordens Planejadas
- **Tipo:** consulta
- **Pergunta:** Q5 — ORDENS PLANEJADAS (PLAF) — v10 CORRIGIDA 27/03/2026 — Executar após MD01N
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q5 Ordens Planejadas" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
SELECT
    H.PLWRK                               AS Centro,
    LTRIM(H.MATNR, '0')                   AS Cod_Material,
    B.MAKTX                               AS Descricao,
    C.MTART                               AS Tipo_Material,
    H.PAART                               AS Tipo_Ordem,
    COALESCE(H.BDMNG, 0)                  AS Qtd_Necessaria,
    H.MEINS                               AS Unidade,
    H.PEDTR                               AS Data_Fim_Ordem,
    H.PERTR                               AS Data_Abertura,
    H.PSTTR                               AS Data_Inicio,
    H.MDACH                               AS Controle_Acoes,
    H.AUFPL                               AS Num_Plano_Op,
    CASE
        WHEN H.PERTR < CURRENT_DATE               THEN '1-ATRASADA'
        WHEN H.PERTR <= ADD_DAYS(CURRENT_DATE, 7) THEN '2-URGENTE'
        ELSE                                           '3-NORMAL'
    END                                   AS Status_Urgencia
FROM PLAF AS H
INNER JOIN MAKT AS B  ON H.MATNR = B.MATNR AND B.SPRAS = 'P'
INNER JOIN MARA AS C  ON H.MATNR = C.MATNR
WHERE H.PLWRK IN ('1001', '1005')
  AND H.PEDTR >= CURRENT_DATE
  AND H.PEDTR <= ADD_DAYS(CURRENT_DATE, 90)
ORDER BY H.PLWRK, Status_Urgencia, H.PEDTR, LTRIM(H.MATNR, '0')
```

## Q6 Requisicoes de Compra
- **Tipo:** consulta
- **Pergunta:** Q6 — REQUISICOES DE COMPRA GERADAS PELO MRP (EBAN + MAKT + MARA)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q6 Requisicoes de Compra" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
-- PRE-CHECK OBRIGATORIO:
--   SE16N -> EBAN -> verificar se e view -> confirmar: LOEKZ STATU FRGKZ ESTKZ BSART LFDAT BEDAT EKGRP MENGE MEINS
-- LICAO: COALESCE em MENGE (campo numerico). Filtro LOEKZ='' pode falhar em view — usar COALESCE.
-- Alias: I=EBAN  B=MAKT  C=MARA
SELECT
    I.WERKS                               AS Centro,
    I.BANFN                               AS Num_Requisicao,
    I.BNFPO                               AS Item,
    LTRIM(I.MATNR, '0')                   AS Cod_Material,
    B.MAKTX                               AS Descricao,
    C.MTART                               AS Tipo_Material,
    I.BSART                               AS Tipo_Pedido,
    COALESCE(I.MENGE, 0)                  AS Qtd_Solicitada,
    I.MEINS                               AS Unidade,
    I.LFDAT                               AS Data_Entrega_Solic,
    I.BEDAT                               AS Data_Necessidade,
    I.ESTKZ                               AS Cat_Item,
    I.STATU                               AS Status_Req,
    I.FRGKZ                               AS Bloqueio_Liberacao,
    I.EKGRP                               AS Grupo_Compradores,
    LTRIM(COALESCE(I.LIFNR, ''), '0')     AS Fornecedor_Sug,
    CASE
        WHEN COALESCE(I.FRGKZ, '') != ''                THEN '1-BLOQUEADA'
        WHEN I.LFDAT < CURRENT_DATE                     THEN '2-VENCIDA'
        WHEN I.LFDAT <= ADD_DAYS(CURRENT_DATE, 7)       THEN '3-URGENTE'
        ELSE                                                 '4-NORMAL'
    END                                   AS Status_Urgencia
FROM EBAN AS I
INNER JOIN MAKT AS B  ON I.MATNR = B.MATNR AND B.SPRAS = 'P'
INNER JOIN MARA AS C  ON I.MATNR = C.MATNR
WHERE
    I.WERKS IN ('1001', '1005')
    AND COALESCE(I.LOEKZ, '') = ''
    AND I.STATU NOT IN ('U', 'L')
    AND I.LFDAT >= ADD_DAYS(CURRENT_DATE, -30)
ORDER BY I.WERKS, Status_Urgencia, I.LFDAT, LTRIM(I.MATNR, '0')
```

## Q7 Diagnostico Bloqueios
- **Tipo:** consulta
- **Pergunta:** Q7 — DIAGNÓSTICO DE BLOQUEIOS v12 — COLUNAS BINÁRIAS + DIAGNÓSTICO TEXTO
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Q7 Diagnostico Bloqueios" (planilha da equipe, 25 e 26/03/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução da equipe no NSQ (Guia Rapido Queries, 25/03/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx

```sql
SELECT DISTINCT
    A.WERKS                                AS Centro,
    LTRIM(A.MATNR, '0')                    AS Cod_Material,
    B.MAKTX                                AS Descricao,
    C.MTART                                AS Tipo_Material,
    C.MSTAE                                AS Status_Global,
    COALESCE(A.MMSTA,'')                   AS Status_Centro,
    COALESCE(A.DISMM,'')                   AS Tipo_MRP,
    COALESCE(A.BESKZ,'')                   AS Tipo_Suprimento,
    A.DISLS                                AS Tamanho_Lote,
    COALESCE(A.BSTMI,0)                    AS Lote_Minimo,
    COALESCE(A.BSTMA,0)                    AS Lote_Maximo,
    COALESCE(A.BSTFE,0)                    AS Lote_Fixo,
    COALESCE(A.MABST,0)                    AS Estoque_Maximo,
    COALESCE(A.PLIFZ,0)                    AS Lead_Time,
    CASE WHEN COALESCE(A.DISMM,'') NOT IN ('','ND')
         THEN 1 ELSE 0
    END                                    AS MRP_ATIVO,
    CASE WHEN C.MSTAE NOT IN ('O1','Z4')
         THEN 1 ELSE 0
    END                                    AS NAO_OBSOLETO,
    CASE WHEN COALESCE(A.MMSTA,'') = ''
         THEN 1 ELSE 0
    END                                    AS CENTRO_LIBERADO,
    CASE
        WHEN C.MTART IN ('ROH','VERP','HAWA','ZDES')
         AND COALESCE(A.BESKZ,'') = 'F'    THEN 1
        WHEN C.MTART IN ('FERT','HALB')
         AND COALESCE(A.BESKZ,'') = 'E'    THEN 1
        ELSE 0
    END                                    AS SUPRIMENTO_CORRETO,
    CASE
        WHEN COALESCE(A.BSTMI,0) > COALESCE(A.BSTMA,0)
         AND COALESCE(A.BSTMA,0) > 0       THEN 0
        WHEN A.DISLS = 'FX'
         AND COALESCE(A.BSTFE,0) = 0       THEN 0
        WHEN A.DISLS = 'HB'
         AND COALESCE(A.MABST,0) = 0       THEN 0
        ELSE 1
    END                                    AS LOTE_CONSISTENTE,
    CASE
        WHEN COALESCE(A.PLIFZ,0) = 0
         AND C.MTART IN ('ROH','VERP','HAWA','ZDES') THEN 0
        ELSE 1
    END                                    AS LT_PREENCHIDO,
    CASE WHEN COALESCE(A.DISMM,'') IN ('','ND')
         THEN 'SEM MRP | ' ELSE '' END ||
    CASE WHEN C.MSTAE IN ('O1','Z4')
         THEN 'OBSOLETO/BLOQ(' || C.MSTAE || ') | ' ELSE '' END ||
    CASE WHEN COALESCE(A.MMSTA,'') != ''
         THEN 'BLOQ CENTRO(' || A.MMSTA || ') | ' ELSE '' END ||
    CASE WHEN C.MTART IN ('ROH','VERP','HAWA','ZDES')
          AND COALESCE(A.BESKZ,'') != 'F'
         THEN 'SUPRIMENTO ERRADO(esperado F, tem '
              || COALESCE(A.BESKZ,'vazio') || ') | ' ELSE '' END ||
    CASE WHEN C.MTART IN ('FERT','HALB')
          AND COALESCE(A.BESKZ,'') != 'E'
         THEN 'SUPRIMENTO ERRADO(esperado E, tem '
              || COALESCE(A.BESKZ,'vazio') || ') | ' ELSE '' END ||
    CASE WHEN COALESCE(A.BSTMI,0) > COALESCE(A.BSTMA,0)
          AND COALESCE(A.BSTMA,0) > 0
         THEN 'LOTE MIN>MAX | ' ELSE '' END ||
    CASE WHEN A.DISLS = 'FX'
          AND COALESCE(A.BSTFE,0) = 0
         THEN 'LOTE FX SEM VALOR | ' ELSE '' END ||
    CASE WHEN A.DISLS = 'HB'
          AND COALESCE(A.MABST,0) = 0
         THEN 'EST MAX ZERO | ' ELSE '' END ||
    CASE WHEN COALESCE(A.PLIFZ,0) = 0
          AND C.MTART IN ('ROH','VERP','HAWA','ZDES')
         THEN 'LT ZERO COMPRA | ' ELSE '' END
                                           AS DIAGNOSTICO_TEXTO
FROM MARC AS A
INNER JOIN MAKT AS B  ON A.MATNR = B.MATNR AND B.SPRAS = 'P'
INNER JOIN MARA AS C  ON A.MATNR = C.MATNR
WHERE A.WERKS IN ('1001', '1005')
  AND C.MTART IN ('FERT','HAWA','HALB','ROH','VERP','ZDES')
  AND (
       COALESCE(A.DISMM,'') IN ('','ND')
    OR C.MSTAE IN ('O1','Z4')
    OR COALESCE(A.MMSTA,'') != ''
    OR (COALESCE(A.BSTMI,0) > COALESCE(A.BSTMA,0) AND COALESCE(A.BSTMA,0) > 0)
    OR (A.DISLS = 'FX' AND COALESCE(A.BSTFE,0) = 0)
    OR (A.DISLS = 'HB' AND COALESCE(A.MABST,0) = 0)
    OR (COALESCE(A.PLIFZ,0) = 0 AND C.MTART IN ('ROH','VERP','HAWA','ZDES'))
    OR (C.MTART IN ('ROH','VERP','HAWA','ZDES') AND COALESCE(A.BESKZ,'') != 'F')
    OR (C.MTART IN ('FERT','HALB') AND COALESCE(A.BESKZ,'') != 'E')
  )
ORDER BY A.WERKS, LTRIM(A.MATNR, '0')
```
