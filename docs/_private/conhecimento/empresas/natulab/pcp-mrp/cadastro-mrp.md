# pcp-mrp · cadastro MRP

Gerado em 26/09/2026 por `C:\Users\fabriciosouza\sap-mrp-natulab\gestao\_migracao-scripts\gerar_biblioteca_natulab.py`
a partir das fontes apontadas em cada entrada (SQL copiado sem edição). Consulta em uso num projeto continua no projeto.
## C00 pré-checagem: colunas reais de cada tabela (rodar antes das demais)
- **Tipo:** consulta
- **Pergunta:** Pré-checagem: colunas reais de cada tabela (rodar antes das demais)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C00, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução de 7 das 13 tabelas no NSP (dono, 26/09/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\C00_colunas-reais_NSP-400_2026-09-26.md

```sql
SELECT * FROM MARC WHERE MANDT = '400' AND WERKS = '1001' LIMIT 1

SELECT * FROM MKAL WHERE MANDT = '400' AND WERKS = '1001' LIMIT 1

SELECT * FROM STKO WHERE MANDT = '400' LIMIT 1

SELECT * FROM STPO WHERE MANDT = '400' LIMIT 1

SELECT * FROM EORD WHERE MANDT = '400' AND WERKS = '1001' LIMIT 1

SELECT * FROM EQUK WHERE MANDT = '400' LIMIT 1

SELECT * FROM MARA WHERE MANDT = '400' LIMIT 1

SELECT * FROM MAST WHERE MANDT = '400' AND WERKS = '1001' LIMIT 1

SELECT * FROM EINA WHERE MANDT = '400' LIMIT 1

SELECT * FROM EINE WHERE MANDT = '400' LIMIT 1

SELECT * FROM T438A WHERE MANDT = '400' LIMIT 1

SELECT * FROM T438T WHERE MANDT = '400' LIMIT 1

SELECT * FROM T438M WHERE MANDT = '400' AND WERKS = '1001' LIMIT 1
```

## C01 tipo de mrp por tipo de material (item 2.2) — já executada
- **Tipo:** consulta
- **Pergunta:** Tipo de MRP por tipo de material (item 2.2) — JÁ EXECUTADA
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C01, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP, mandante 400 (colaboradora, 24/09/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\C01_dismm_NSP-400_2026-09-24.tsv

```sql
SELECT m.MTART, c.WERKS, c.DISMM, COUNT(*) AS N FROM MARC c JOIN MARA m ON m.MANDT = c.MANDT AND m.MATNR = c.MATNR WHERE c.MANDT = '400' AND c.WERKS IN ('1001','1005') GROUP BY m.MTART, c.WERKS, c.DISMM
```

## C02 significado dos tipos de mrp em uso (item 2.2)
- **Tipo:** consulta
- **Pergunta:** Significado dos tipos de MRP em uso (item 2.2)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C02, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT * FROM T438A WHERE MANDT = '400' AND DISMM IN ('M0','ND','PD','X0')

SELECT * FROM T438T WHERE MANDT = '400' AND SPRAS = 'P' AND DISMM IN ('M0','ND','PD','X0')
```

## C03 tamanho de lote, lote fixo e refugo de montagem (itens 2.4 e 9.7)
- **Tipo:** consulta
- **Pergunta:** Tamanho de lote, lote fixo e refugo de montagem (itens 2.4 e 9.7)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C03, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT m.MTART, c.WERKS, c.DISMM, c.DISLS, COUNT(*) AS N, SUM(CASE WHEN COALESCE(c.BSTFE, 0) > 0 THEN 1 ELSE 0 END) AS COM_LOTE_FIXO, SUM(CASE WHEN COALESCE(c.AUSSS, 0) > 0 THEN 1 ELSE 0 END) AS COM_REFUGO_MONTAGEM FROM MARC c JOIN MARA m ON m.MANDT = c.MANDT AND m.MATNR = c.MATNR WHERE c.MANDT = '400' AND c.WERKS IN ('1001','1005') AND COALESCE(m.MSTAE, '') NOT IN ('O1','Z4') AND TRIM(COALESCE(c.DISMM, '')) <> '' GROUP BY m.MTART, c.WERKS, c.DISMM, c.DISLS ORDER BY c.WERKS, m.MTART, c.DISMM, c.DISLS
```

## C04 campos de compra por tipo de suprimento (itens 3.3, 3.5 e 8.5)
- **Tipo:** consulta
- **Pergunta:** Campos de compra por tipo de suprimento (itens 3.3, 3.5 e 8.5)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C04, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT m.MTART, c.WERKS, c.BESKZ, COUNT(*) AS N, SUM(CASE WHEN COALESCE(c.PLIFZ, 0) = 0 THEN 1 ELSE 0 END) AS SEM_PRAZO_ENTREGA, SUM(CASE WHEN TRIM(COALESCE(c.EKGRP, '')) = '' THEN 1 ELSE 0 END) AS SEM_GRP_COMPRADORES, SUM(CASE WHEN c.KORDB = 'X' THEN 1 ELSE 0 END) AS FONTE_OBRIGATORIA FROM MARC c JOIN MARA m ON m.MANDT = c.MANDT AND m.MATNR = c.MATNR WHERE c.MANDT = '400' AND c.WERKS IN ('1001','1005') AND COALESCE(m.MSTAE, '') NOT IN ('O1','Z4') AND TRIM(COALESCE(c.DISMM, '')) <> '' GROUP BY m.MTART, c.WERKS, c.BESKZ ORDER BY c.WERKS, m.MTART, c.BESKZ
```

## C05 grupos de compradores em uso (item 3.5)
- **Tipo:** consulta
- **Pergunta:** Grupos de compradores em uso (item 3.5)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C05, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT c.WERKS, c.EKGRP, COUNT(*) AS N FROM MARC c JOIN MARA m ON m.MANDT = c.MANDT AND m.MATNR = c.MATNR WHERE c.MANDT = '400' AND c.WERKS IN ('1001','1005') AND COALESCE(m.MSTAE, '') NOT IN ('O1','Z4') AND TRIM(COALESCE(c.DISMM, '')) <> '' AND c.BESKZ IN ('F','X') GROUP BY c.WERKS, c.EKGRP ORDER BY c.WERKS, N DESC
```

## C06 depósito de produção, estratégia, seleção de lista técnica e estoque de segurança (itens 3.7, 4.1, 4.3 e 5.2)
- **Tipo:** consulta
- **Pergunta:** Depósito de produção, estratégia, seleção de lista técnica e estoque de segurança (itens 3.7, 4.1, 4.3 e 5.2)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C06, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT m.MTART, c.WERKS, c.BESKZ, c.STRGR, c.ALTSL, COUNT(*) AS N, SUM(CASE WHEN TRIM(COALESCE(c.LGPRO, '')) = '' THEN 1 ELSE 0 END) AS SEM_DEP_PRODUCAO, SUM(CASE WHEN COALESCE(c.EISBE, 0) > 0 THEN 1 ELSE 0 END) AS COM_EST_SEGURANCA FROM MARC c JOIN MARA m ON m.MANDT = c.MANDT AND m.MATNR = c.MATNR WHERE c.MANDT = '400' AND c.WERKS IN ('1001','1005') AND COALESCE(m.MSTAE, '') NOT IN ('O1','Z4') AND TRIM(COALESCE(c.DISMM, '')) <> '' GROUP BY m.MTART, c.WERKS, c.BESKZ, c.STRGR, c.ALTSL ORDER BY c.WERKS, m.MTART, c.BESKZ, c.STRGR, c.ALTSL
```

## C07 grupo mrp por tipo de material (item 4.3 e achado e-01)
- **Tipo:** consulta
- **Pergunta:** Grupo MRP por tipo de material (item 4.3 e achado E-01)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C07, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT m.MTART, c.WERKS, c.DISGR, COUNT(*) AS N, SUM(CASE WHEN COALESCE(c.EISBE, 0) > 0 THEN 1 ELSE 0 END) AS COM_EST_SEGURANCA FROM MARC c JOIN MARA m ON m.MANDT = c.MANDT AND m.MATNR = c.MATNR WHERE c.MANDT = '400' AND c.WERKS IN ('1001','1005') AND COALESCE(m.MSTAE, '') NOT IN ('O1','Z4') AND TRIM(COALESCE(c.DISMM, '')) <> '' GROUP BY m.MTART, c.WERKS, c.DISGR ORDER BY c.WERKS, m.MTART, c.DISGR
```

## C08 configuração dos grupos mrp dos dois centros (achado e-01)
- **Tipo:** consulta
- **Pergunta:** Configuração dos grupos MRP dos dois centros (achado E-01)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C08, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT * FROM T438M WHERE MANDT = '400' AND WERKS IN ('1001','1005')
```

## C09 controle de lote e validade no cadastro (itens 6.1, 6.2 e 6.3)
- **Tipo:** consulta
- **Pergunta:** Controle de lote e validade no cadastro (itens 6.1, 6.2 e 6.3)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C09, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT m.MTART, c.WERKS, m.XCHPF AS LOTE_MANDANTE, c.XCHPF AS LOTE_CENTRO, COUNT(*) AS N, SUM(CASE WHEN COALESCE(m.MHDHB, 0) > 0 THEN 1 ELSE 0 END) AS COM_VALIDADE_TOTAL, SUM(CASE WHEN COALESCE(m.MHDRZ, 0) > 0 THEN 1 ELSE 0 END) AS COM_VALIDADE_MINIMA FROM MARC c JOIN MARA m ON m.MANDT = c.MANDT AND m.MATNR = c.MATNR WHERE c.MANDT = '400' AND c.WERKS IN ('1001','1005') AND COALESCE(m.MSTAE, '') NOT IN ('O1','Z4') AND TRIM(COALESCE(c.DISMM, '')) <> '' GROUP BY m.MTART, c.WERKS, m.XCHPF, c.XCHPF ORDER BY c.WERKS, m.MTART, m.XCHPF, c.XCHPF
```

## C10 registro info e prazo do registro (itens 8.1 e 8.2)
- **Tipo:** consulta
- **Pergunta:** Registro info e prazo do registro (itens 8.1 e 8.2)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C10, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT m.MTART, c.WERKS, COUNT(*) AS N_MATERIAIS_COMPRADOS, SUM(CASE WHEN i.MATNR IS NULL THEN 1 ELSE 0 END) AS SEM_REGISTRO_INFO, SUM(CASE WHEN i.MATNR IS NOT NULL AND i.N_COM_PRAZO = 0 THEN 1 ELSE 0 END) AS INFO_SEM_PRAZO, SUM(CASE WHEN i.N_FORNECEDORES > 1 THEN 1 ELSE 0 END) AS MAIS_DE_1_FORNECEDOR FROM MARC c JOIN MARA m ON m.MANDT = c.MANDT AND m.MATNR = c.MATNR LEFT JOIN (SELECT a.MATNR, '1001' AS CENTRO, COUNT(DISTINCT a.LIFNR) AS N_FORNECEDORES, SUM(CASE WHEN COALESCE(e.APLFZ, 0) > 0 THEN 1 ELSE 0 END) AS N_COM_PRAZO FROM EINA a JOIN EINE e ON e.MANDT = a.MANDT AND e.INFNR = a.INFNR WHERE a.MANDT = '400' AND TRIM(COALESCE(a.LOEKZ, '')) = '' AND TRIM(COALESCE(e.LOEKZ, '')) = '' AND (e.WERKS = '1001' OR TRIM(COALESCE(e.WERKS, '')) = '') GROUP BY a.MATNR UNION ALL SELECT a.MATNR, '1005' AS CENTRO, COUNT(DISTINCT a.LIFNR) AS N_FORNECEDORES, SUM(CASE WHEN COALESCE(e.APLFZ, 0) > 0 THEN 1 ELSE 0 END) AS N_COM_PRAZO FROM EINA a JOIN EINE e ON e.MANDT = a.MANDT AND e.INFNR = a.INFNR WHERE a.MANDT = '400' AND TRIM(COALESCE(a.LOEKZ, '')) = '' AND TRIM(COALESCE(e.LOEKZ, '')) = '' AND (e.WERKS = '1005' OR TRIM(COALESCE(e.WERKS, '')) = '') GROUP BY a.MATNR) i ON i.MATNR = c.MATNR AND i.CENTRO = c.WERKS WHERE c.MANDT = '400' AND c.WERKS IN ('1001','1005') AND COALESCE(m.MSTAE, '') NOT IN ('O1','Z4') AND TRIM(COALESCE(c.DISMM, '')) <> '' AND c.BESKZ IN ('F','X') GROUP BY m.MTART, c.WERKS ORDER BY c.WERKS, m.MTART
```

## C11 lista de fontes vigente hoje (item 8.3)
- **Tipo:** consulta
- **Pergunta:** Lista de fontes vigente hoje (item 8.3)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C11, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT m.MTART, c.WERKS, COUNT(*) AS N_MATERIAIS_COMPRADOS, SUM(CASE WHEN f.MATNR IS NULL THEN 1 ELSE 0 END) AS SEM_FONTE_VIGENTE, SUM(CASE WHEN f.N_RELEV_MRP > 0 THEN 1 ELSE 0 END) AS COM_FONTE_RELEV_MRP, SUM(CASE WHEN f.N_FIXA > 0 THEN 1 ELSE 0 END) AS COM_FONTE_FIXA FROM MARC c JOIN MARA m ON m.MANDT = c.MANDT AND m.MATNR = c.MATNR LEFT JOIN (SELECT MATNR, WERKS, SUM(CASE WHEN AUTET IN ('1','2') THEN 1 ELSE 0 END) AS N_RELEV_MRP, SUM(CASE WHEN FLIFN = 'X' THEN 1 ELSE 0 END) AS N_FIXA FROM EORD WHERE MANDT = '400' AND WERKS IN ('1001','1005') AND VDATU <= TO_VARCHAR(CURRENT_DATE, 'YYYYMMDD') AND BDATU >= TO_VARCHAR(CURRENT_DATE, 'YYYYMMDD') AND TRIM(COALESCE(NOTKZ, '')) = '' GROUP BY MATNR, WERKS) f ON f.MATNR = c.MATNR AND f.WERKS = c.WERKS WHERE c.MANDT = '400' AND c.WERKS IN ('1001','1005') AND COALESCE(m.MSTAE, '') NOT IN ('O1','Z4') AND TRIM(COALESCE(c.DISMM, '')) <> '' AND c.BESKZ IN ('F','X') GROUP BY m.MTART, c.WERKS ORDER BY c.WERKS, m.MTART
```

## C12 rateio entre fornecedores vigente hoje (item 8.4)
- **Tipo:** consulta
- **Pergunta:** Rateio entre fornecedores vigente hoje (item 8.4)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C12, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT m.MTART, c.WERKS, COUNT(*) AS N_MATERIAIS_COMPRADOS, SUM(CASE WHEN q.MATNR IS NULL THEN 0 ELSE 1 END) AS COM_RATEIO_VIGENTE FROM MARC c JOIN MARA m ON m.MANDT = c.MANDT AND m.MATNR = c.MATNR LEFT JOIN (SELECT DISTINCT MATNR, WERKS FROM EQUK WHERE MANDT = '400' AND WERKS IN ('1001','1005') AND VDATU <= TO_VARCHAR(CURRENT_DATE, 'YYYYMMDD') AND BDATU >= TO_VARCHAR(CURRENT_DATE, 'YYYYMMDD')) q ON q.MATNR = c.MATNR AND q.WERKS = c.WERKS WHERE c.MANDT = '400' AND c.WERKS IN ('1001','1005') AND COALESCE(m.MSTAE, '') NOT IN ('O1','Z4') AND TRIM(COALESCE(c.DISMM, '')) <> '' AND c.BESKZ IN ('F','X') GROUP BY m.MTART, c.WERKS ORDER BY c.WERKS, m.MTART
```

## C13 cabeçalho da lista técnica: status, utilização e data de início (itens 9.1, 9.2 e 9.3)
- **Tipo:** consulta
- **Pergunta:** Cabeçalho da lista técnica: status, utilização e data de início (itens 9.1, 9.2 e 9.3)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C13, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT m.MTART, s.WERKS, s.STLAN, k.STLST, COUNT(*) AS N_REGISTROS, COUNT(DISTINCT s.MATNR) AS N_MATERIAIS, SUM(CASE WHEN k.DATUV > TO_VARCHAR(CURRENT_DATE, 'YYYYMMDD') THEN 1 ELSE 0 END) AS INICIO_NO_FUTURO FROM MAST s JOIN STKO k ON k.MANDT = s.MANDT AND k.STLTY = 'M' AND k.STLNR = s.STLNR AND k.STLAL = s.STLAL JOIN MARA m ON m.MANDT = s.MANDT AND m.MATNR = s.MATNR WHERE s.MANDT = '400' AND s.WERKS IN ('1001','1005') AND COALESCE(m.MSTAE, '') NOT IN ('O1','Z4') AND TRIM(COALESCE(k.LKENZ, '')) = '' GROUP BY m.MTART, s.WERKS, s.STLAN, k.STLST ORDER BY s.WERKS, m.MTART, s.STLAN, k.STLST
```

## C14 refugo do componente na lista técnica (item 9.7)
- **Tipo:** consulta
- **Pergunta:** Refugo do componente na lista técnica (item 9.7)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C14, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT s.WERKS, h.MTART AS TIPO_PRODUTO, COUNT(*) AS N_POSICOES, SUM(CASE WHEN COALESCE(p.AUSCH, 0) > 0 THEN 1 ELSE 0 END) AS COM_REFUGO_COMPONENTE FROM STPO p JOIN (SELECT DISTINCT t.MANDT, t.MATNR, t.WERKS, t.STLNR FROM MAST t JOIN STKO k ON k.MANDT = t.MANDT AND k.STLTY = 'M' AND k.STLNR = t.STLNR AND k.STLAL = t.STLAL WHERE t.MANDT = '400' AND t.WERKS IN ('1001','1005') AND TRIM(COALESCE(k.LKENZ, '')) = '') s ON s.MANDT = p.MANDT AND s.STLNR = p.STLNR JOIN MARA h ON h.MANDT = s.MANDT AND h.MATNR = s.MATNR WHERE p.MANDT = '400' AND p.STLTY = 'M' AND COALESCE(h.MSTAE, '') NOT IN ('O1','Z4') AND TRIM(COALESCE(p.LKENZ, '')) = '' GROUP BY s.WERKS, h.MTART ORDER BY s.WERKS, h.MTART
```

## C15 os onze materiais dos cinco tipos sem tipo de mrp (item 2.2)
- **Tipo:** consulta
- **Pergunta:** Os onze materiais dos cinco tipos sem tipo de MRP (item 2.2)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C15, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT c.WERKS, m.MTART, c.MATNR, m.MSTAE, c.MMSTA, c.BESKZ FROM MARC c JOIN MARA m ON m.MANDT = c.MANDT AND m.MATNR = c.MATNR WHERE c.MANDT = '400' AND c.WERKS IN ('1001','1005') AND m.MTART IN ('FERT','HALB','HAWA','ROH','VERP') AND TRIM(COALESCE(c.DISMM, '')) = '' ORDER BY c.WERKS, m.MTART, c.MATNR
```

## C16 versões de produção: vigência, bloqueio e faixa de lote (itens 11.3 e 11.6)
- **Tipo:** consulta
- **Pergunta:** Versões de produção: vigência, bloqueio e faixa de lote (itens 11.3 e 11.6)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C16, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT m.MTART, v.WERKS, COUNT(*) AS N_VERSOES, COUNT(DISTINCT v.MATNR) AS N_MATERIAIS, SUM(CASE WHEN v.ADATU <= TO_VARCHAR(CURRENT_DATE, 'YYYYMMDD') AND v.BDATU >= TO_VARCHAR(CURRENT_DATE, 'YYYYMMDD') THEN 1 ELSE 0 END) AS VIGENTES_HOJE, SUM(CASE WHEN TRIM(COALESCE(v.MKSP, '')) = '' THEN 0 ELSE 1 END) AS BLOQUEADAS, SUM(CASE WHEN COALESCE(v.BSTMI, 0) > 0 THEN 1 ELSE 0 END) AS COM_LOTE_MINIMO, SUM(CASE WHEN COALESCE(v.BSTMA, 0) > 0 THEN 1 ELSE 0 END) AS COM_LOTE_MAXIMO FROM MKAL v JOIN MARA m ON m.MANDT = v.MANDT AND m.MATNR = v.MATNR WHERE v.MANDT = '400' AND v.WERKS IN ('1001','1005') AND COALESCE(m.MSTAE, '') NOT IN ('O1','Z4') GROUP BY m.MTART, v.WERKS ORDER BY v.WERKS, m.MTART
```

## C17 material produzido e planejado sem versão de produção vigente hoje (item 11.3)
- **Tipo:** consulta
- **Pergunta:** Material produzido e planejado sem versão de produção vigente hoje (item 11.3)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md, seção C17, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\CONSULTAS-DBACOCKPIT-treplicas.md

```sql
SELECT m.MTART, c.WERKS, COUNT(*) AS N_PRODUZIDOS, SUM(CASE WHEN v.MATNR IS NULL THEN 1 ELSE 0 END) AS SEM_VERSAO_VIGENTE FROM MARC c JOIN MARA m ON m.MANDT = c.MANDT AND m.MATNR = c.MATNR LEFT JOIN (SELECT DISTINCT MATNR, WERKS FROM MKAL WHERE MANDT = '400' AND WERKS IN ('1001','1005') AND ADATU <= TO_VARCHAR(CURRENT_DATE, 'YYYYMMDD') AND BDATU >= TO_VARCHAR(CURRENT_DATE, 'YYYYMMDD') AND TRIM(COALESCE(MKSP, '')) = '') v ON v.MATNR = c.MATNR AND v.WERKS = c.WERKS WHERE c.MANDT = '400' AND c.WERKS IN ('1001','1005') AND COALESCE(m.MSTAE, '') NOT IN ('O1','Z4') AND TRIM(COALESCE(c.DISMM, '')) <> '' AND c.BESKZ IN ('E','X') GROUP BY m.MTART, c.WERKS ORDER BY c.WERKS, m.MTART
```

## views NSDM_V das tabelas de material
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Guia Rapido Queries"
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução da equipe no NSQ (Guia Rapido Queries, 25/03/2026)

MARC, MARD, STKO e STPO são views `NSDM_V_*` neste ambiente; campo do dicionário ABAP pode não existir na view.

## STKO-STLST com zero à esquerda
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Guia Rapido Queries"
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução da equipe no NSQ (Guia Rapido Queries, 25/03/2026)

Status da lista técnica com zero à esquerda: `'01'`, não `'1'`.

## STPO-DATUB inexistente
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Guia Rapido Queries"
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução da equipe no NSQ (Guia Rapido Queries, 25/03/2026)

`STPO-DATUB` não existe na view; usar `VALID_TO`.

## utilização da lista técnica em MAST
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Guia Rapido Queries"
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução da equipe no NSQ (Guia Rapido Queries, 25/03/2026)

`STKO-STLAN` não existe; a utilização da lista técnica está em `MAST-STLAN`.

## junção STKO e STPO
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Guia Rapido Queries"
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução da equipe no NSQ (Guia Rapido Queries, 25/03/2026)

Juntar cabeçalho e item da lista técnica só por `STLNR`; `STPO` não tem `STLAL`.

## MARD filtro sem COALESCE
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, aba "Guia Rapido Queries"
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução da equipe no NSQ (Guia Rapido Queries, 25/03/2026)

25/03/2026: filtro `> 0` sem COALESCE na MARD voltou 0 linhas (NULL); com COALESCE, 36.248 linhas.

## acabados com tipo de MRP X0
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** consulta C01, NSP 400, 24/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP (colaboradora, 24/09/2026)
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\C01_dismm_NSP-400_2026-09-24.tsv

24/09/2026: 321 acabados com tipo de MRP X0 (sem MRP, com explosão da lista técnica): 248 no centro 1001 e 73 no 1005; inclui obsoletos.

## status de material obsoleto
- **Tipo:** fato
- **Classe:** configuração
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapeamento_MRP_Live_Natulab_v14.0.xlsx, consultas validadas da equipe
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução da equipe no NSQ (Guia Rapido Queries, 25/03/2026)

Status `MARA-MSTAE` O1 e Z4 marcam material obsoleto; as consultas da casa excluem os dois quando a pergunta é sobre cadastro ativo.

## família de material só no acabado
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** Datasphere, view VW_MD_MATERIAL, 24/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por medição no Datasphere (24/09/2026)

24/09/2026: família de material só existe no acabado (79 famílias em 511 FERT); nos demais tipos o nível é o grupo de mercadoria.

## MRP padrão não olha validade de lote
- **Tipo:** fato
- **Classe:** conceito
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\gestao\GLOSSARIO.md, seção 4b (teste do dono, 16/09/2026)
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por teste do dono (16/09/2026)

O MRP padrão não considera a validade do lote e conta lote vencido como disponível.

## MHDHB zero desliga FEFO
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapa_Operacional_MRP_Natulab_AVA03405_v1.md, linhas 47-48
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO

Com `MARA-MHDHB`/`MHDRZ` zero o SAP não aplica FEFO; 78% dos materiais medidos tinham MHDHB zero (número citado pelo Mapa Operacional, fonte terceira).

## prazo do fornecedor APLFZ ou KAUTL
- **Tipo:** fato
- **Classe:** configuração
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapa_Operacional_MRP_Natulab_AVA03405_v1.md, linhas 230-253
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Contestado em:** 26/09/2026

Conflito entre fontes do projeto: `EINE-APLFZ` × `EINE-KAUTL` como prazo do fornecedor no registro info. Não resolvido; não usar como fato.

## lote fixo BSTFE ou LOSGR
- **Tipo:** fato
- **Classe:** configuração
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapa_Operacional_MRP_Natulab_AVA03405_v1.md, linhas 230-253
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Contestado em:** 26/09/2026

Conflito entre fontes do projeto: `MARC-BSTFE` × `MARC-LOSGR` como lote fixo da visão MRP 1. Não resolvido; não usar como fato.

## onde fica VERID
- **Tipo:** fato
- **Classe:** configuração
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\referencias\Mapa_Operacional_MRP_Natulab_AVA03405_v1.md, linhas 230-253
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Contestado em:** 26/09/2026

Conflito entre fontes do projeto: `VERID` na MKAL (versão de produção) × na visão MRP 4 do material. Não resolvido; não usar como fato.
