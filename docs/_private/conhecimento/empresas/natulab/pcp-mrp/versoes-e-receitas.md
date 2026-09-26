# pcp-mrp · versoes-e-receitas

Gerado em 26/09/2026 por `C:\Users\fabriciosouza\sap-mrp-natulab\gestao\_migracao-scripts\gerar_biblioteca_natulab.py`
a partir das fontes apontadas em cada entrada (SQL copiado sem edição). Consulta em uso num projeto continua no projeto.
## PV-C5 a c223 grava documento de alteração? (pergunta 5, pelo histórico desde 01/01/2026)
- **Tipo:** consulta
- **Pergunta:** A C223 grava documento de alteração? (pergunta 5, pelo histórico desde 01/01/2026)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md, seção PV-C5, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md

```sql
SELECT h.OBJECTCLAS, p.TABNAME, p.FNAME, COUNT(*) AS N, MAX(h.UDATE) AS ULTIMA FROM CDHDR h JOIN CDPOS p ON p.MANDANT = h.MANDANT AND p.OBJECTCLAS = h.OBJECTCLAS AND p.OBJECTID = h.OBJECTID AND p.CHANGENR = h.CHANGENR WHERE h.MANDANT = '400' AND h.TCODE = 'C223' AND h.UDATE >= '20260101' GROUP BY h.OBJECTCLAS, p.TABNAME, p.FNAME ORDER BY N DESC
```

## PV-C7 quantas receitas mestre têm regra de modificação (pergunta 2)
- **Tipo:** consulta
- **Pergunta:** Quantas receitas mestre têm regra de modificação (pergunta 2)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md, seção PV-C7, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP, mandante 400 (dono, 26/09/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\PV-C7.xlsx

```sql
SELECT WERKS, CHRULE, CRTYPE, COUNT(DISTINCT PLNNR || '|' || PLNAL) AS N_ALTERNATIVAS_RECEITA FROM PLKO WHERE MANDT = '400' AND PLNTY = '2' AND WERKS IN ('1001', '1005') AND TRIM(COALESCE(LOEKZ, '')) = '' GROUP BY WERKS, CHRULE, CRTYPE ORDER BY WERKS, CHRULE
```

## PV-C7b existe plano de outro tipo além de receita mestre? (pergunta 2, confirma o filtro da pv-c7)
- **Tipo:** consulta
- **Pergunta:** Existe plano de outro tipo além de receita mestre? (pergunta 2, confirma o filtro da PV-C7)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md, seção PV-C7b, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md

```sql
SELECT WERKS, PLNTY, COUNT(*) AS N_LINHAS FROM PLKO WHERE MANDT = '400' GROUP BY WERKS, PLNTY ORDER BY WERKS, PLNTY
```

## PV-C8 quantos materiais e versões dependem de receita com regra de modificação (pergunta 2)
- **Tipo:** consulta
- **Pergunta:** Quantos materiais e versões dependem de receita com regra de modificação (pergunta 2)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md, seção PV-C8, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP, mandante 400 (dono, 26/09/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\PV-C8.xlsx

```sql
SELECT v.WERKS, COUNT(DISTINCT v.MATNR) AS N_MATERIAIS, COUNT(DISTINCT v.MATNR || '|' || v.VERID) AS N_VERSOES FROM MKAL v JOIN PLKO k ON k.MANDT = v.MANDT AND k.PLNTY = v.PLNTY AND k.PLNNR = v.PLNNR AND k.PLNAL = v.ALNAL WHERE v.MANDT = '400' AND v.WERKS IN ('1001', '1005') AND v.PLNTY = '2' AND TRIM(COALESCE(k.LOEKZ, '')) = '' AND TRIM(COALESCE(k.CHRULE, '')) <> '' GROUP BY v.WERKS
```

## PV-C6 o histórico de alteração de versões de receita está em uso? (pergunta 5)
- **Tipo:** consulta
- **Pergunta:** O histórico de alteração de versões de receita está em uso? (pergunta 5)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md, seção PV-C6, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md

```sql
SELECT WERKS, COUNT(*) AS N_REGISTROS, COUNT(DISTINCT MATNR) AS N_MATERIAIS FROM MKAL_AEND WHERE MANDT = '400' AND WERKS IN ('1001', '1005') GROUP BY WERKS
```

## C18 produtos com versões de produção sobrepostas no tempo
- **Tipo:** consulta
- **Pergunta:** Quantos produtos têm duas ou mais versões de produção válidas ao mesmo tempo, por centro?
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\C18_versoes-sobrepostas_NSP-400_2026-09-25.md, linha 5
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP, mandante 400 (dono, 25/09/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\C18_versoes-sobrepostas_NSP-400_2026-09-25.md
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\C18_versoes-sobrepostas_NSP-400_2026-09-25.md

```sql
SELECT a.WERKS, COUNT(DISTINCT a.MATNR) AS PRODUTOS_COM_VERSOES_SOBREPOSTAS FROM MKAL a JOIN MKAL b ON b.MANDT = a.MANDT AND b.MATNR = a.MATNR AND b.WERKS = a.WERKS AND b.VERID > a.VERID WHERE a.MANDT = '400' AND a.WERKS IN ('1001','1005') AND a.ADATU <= b.BDATU AND b.ADATU <= a.BDATU AND a.BDATU >= TO_VARCHAR(CURRENT_DATE, 'YYYYMMDD') AND b.BDATU >= TO_VARCHAR(CURRENT_DATE, 'YYYYMMDD') GROUP BY a.WERKS
```

## MKAL-MKSP bloqueio da versão
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\gestao\GLOSSARIO.md, seção 4b, 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por dicionário SAP (DD03L lido pelo Datasphere)

O bloqueio da versão de produção é `MKAL-MKSP`. `MKAL-SPERR` não existe.

## MKAL-BSTMI e BSTMA faixa da versão
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\gestao\GLOSSARIO.md, seção 4b, 24/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por dicionário SAP (DD03L lido pelo Datasphere)

Lote mínimo e máximo da versão de produção (faixa de lote).

## PLKO-LOSVN e LOSBS faixa da receita
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\gestao\GLOSSARIO.md, seção 4b, 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por dicionário SAP (DD03L lido pelo Datasphere)

Faixa de lote da receita mestre.

## MAST-LOSVN e LOSBS faixa da lista técnica
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\gestao\GLOSSARIO.md, seção 4b, 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por dicionário SAP (DD03L lido pelo Datasphere)

Faixa de lote da alternativa da lista técnica.

## PLKO-CHRULE e CRTYPE regra de modificação
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\gestao\GLOSSARIO.md, seção 4b, 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por dicionário SAP (DD03L lido pelo Datasphere)

Regra de modificação da receita e tipo de registro exigido.

## receitas sem regra de modificação
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** consulta PV-C7, NSP 400, 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP, mandante 400 (dono, 26/09/2026)
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\PV-C7.xlsx

26/09/2026: `PLKO-CHRULE` vazio em todas as alternativas ativas de receita: 1.521 no centro 1001 e 256 no 1005.

## tipo de roteiro só receita mestre
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\gestao\GLOSSARIO.md, linha R2
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por medição no Datasphere (22, 23 e 26/09/2026)

Todos os planos vistos são tipo de roteiro 2 (receita mestre, PP-PI): 1.899 em 22/09/2026, 1.905 em 23/09 e 1.906 linhas em 26/09 na view `PRODUCAO.VW_FD_PP_PLKO_PLANO_CABECALHO_01`. A definição da view não é visível; a confirmação direta na PLKO é a PV-C7b, pendente.

## versões sobrepostas
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** consulta C18, NSP 400, 25/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP (dono, 25/09/2026)
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\C18_versoes-sobrepostas_NSP-400_2026-09-25.md

25/09/2026: 216 produtos no centro 1001 e 46 no 1005 com duas ou mais versões válidas ao mesmo tempo (teto: inclui bloqueadas e obsoletas).

## I_ProductionVersionTP objeto de alteração
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** consulta PV-C2 (código-fonte da view), 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por código-fonte CDS lido no NSP (26/09/2026)
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\PV-C2-fonte-das-views_2026-09-26.txt

Objeto RAP liberado para alterar versão de produção (pacote VDM_PP_MD_PRV, contrato PUBLIC_LOCAL_API). Campos: `MaterialMinLotSizeQuantity`, `MaterialMaxLotSizeQuantity`, `ChangeNumber`, `ProductionVersionLock`, `ValidityStartDate`, `ValidityEndDate`; chaves `Material`, `Plant`, `ProductionVersion`.

## I_ProductionVersion view de leitura
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** consulta PV-C2, 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por código-fonte CDS lido no NSP (26/09/2026)
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\PV-C2-fonte-das-views_2026-09-26.txt

View de leitura sobre a MKAL. O bloqueio aqui se chama `ProductionVersionIsLocked` (no objeto de alteração, `ProductionVersionLock`).
