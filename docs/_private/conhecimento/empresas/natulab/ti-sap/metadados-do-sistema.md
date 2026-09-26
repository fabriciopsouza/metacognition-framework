# ti-sap · metadados-do-sistema

Gerado em 26/09/2026 por `C:\Users\fabriciosouza\sap-mrp-natulab\gestao\_migracao-scripts\gerar_biblioteca_natulab.py`
a partir das fontes apontadas em cada entrada (SQL copiado sem edição). Consulta em uso num projeto continua no projeto.
## PV-C1 o objeto de negócio existe neste sistema? (pergunta 1)
- **Tipo:** consulta
- **Pergunta:** O objeto de negócio existe neste sistema? (pergunta 1)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md, seção PV-C1, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP, mandante 400 (dono, 26/09/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\PV-C1.xlsx

```sql
SELECT PGMID, OBJECT, OBJ_NAME, DEVCLASS FROM TADIR WHERE OBJ_NAME IN ('I_PRODUCTIONVERSIONTP', 'I_PRODUCTIONVERSION') ORDER BY OBJ_NAME, OBJECT
```

## PV-C2 código-fonte da view, com os nomes exatos dos campos (pergunta 1)
- **Tipo:** consulta
- **Pergunta:** Código-fonte da view, com os nomes exatos dos campos (pergunta 1)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md, seção PV-C2, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP, mandante 400 (dono, 26/09/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\PV-C2.xlsx

```sql
SELECT DDLNAME, AS4LOCAL, SOURCE FROM DDDDLSRC WHERE DDLNAME IN ('I_PRODUCTIONVERSIONTP', 'I_PRODUCTIONVERSION') AND AS4LOCAL = 'A'
```

## PV-C3 objetos de autorização cadastrados para a c223 e a c252 (proposta para a pergunta 3)
- **Tipo:** consulta
- **Pergunta:** Objetos de autorização cadastrados para a C223 e a C252 (proposta para a pergunta 3)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md, seção PV-C3, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP, mandante 400 (dono, 26/09/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\PV-C3.xlsx

```sql
SELECT NAME, OBJECT, FIELD, LOW, HIGH FROM USOBT_C WHERE TYPE = 'TR' AND NAME IN ('C223', 'C252') ORDER BY NAME, OBJECT, FIELD

SELECT NAME, OBJECT, FIELD, LOW, HIGH FROM USOBT WHERE TYPE = 'TR' AND NAME IN ('C223', 'C252') ORDER BY NAME, OBJECT, FIELD
```

## PV-C4 programa por trás da c252 e da c223 (pergunta 4)
- **Tipo:** consulta
- **Pergunta:** Programa por trás da C252 e da C223 (pergunta 4)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md, seção PV-C4, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP, mandante 400 (dono, 26/09/2026)
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\PV-C4.xlsx

```sql
SELECT TCODE, PGMNA FROM TSTC WHERE TCODE IN ('C223', 'C252')
```

## PV-C9 o objeto está liberado para uso por programa? (pergunta 1, estado de liberação)
- **Tipo:** consulta
- **Pergunta:** O objeto está liberado para uso por programa? (pergunta 1, estado de liberação)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md, seção PV-C9, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md

```sql
SELECT TADIR_OBJECT, TADIR_OBJ_NAME, OBJECT_TYPE, OBJECT_KEY, CONTRACT, STATE FROM ARS_API_BY_CTRCT WHERE TADIR_OBJ_NAME IN ('I_PRODUCTIONVERSIONTP', 'I_PRODUCTIONVERSION') ORDER BY TADIR_OBJ_NAME, CONTRACT
```

## PV-C10 fonte da camada que o objeto projeta (pergunta 1, de onde vem cada campo)
- **Tipo:** consulta
- **Pergunta:** Fonte da camada que o objeto projeta (pergunta 1, de onde vem cada campo)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md, seção PV-C10, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md

```sql
SELECT DDLNAME, AS4LOCAL, SOURCE FROM DDDDLSRC WHERE DDLNAME = 'R_PRODUCTIONVERSIONTP' AND AS4LOCAL = 'A'

SELECT DDLNAME, AS4LOCAL FROM DDDDLSRC WHERE DDLNAME LIKE 'R\_PRODUCTIONVERSION%' ESCAPE '\'
```

## PV-C11 comportamento do objeto: permite alterar? tem trava e controle de concorrência? (pergunta 1)
- **Tipo:** consulta
- **Pergunta:** Comportamento do objeto: permite alterar? tem trava e controle de concorrência? (pergunta 1)
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md, seção PV-C11, catalogada em 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\programa-faixa-lote\CONSULTAS-PRE-VOO-DBACOCKPIT.md

```sql
SELECT * FROM RBDEF_ENTITY WHERE UPPER(NAME) LIKE '%PRODUCTIONVERSION%' OR UPPER(RAW_NAME) LIKE '%PRODUCTIONVERSION%'
```

## RB01-87 passo 1 — descobrir o mandante *(não presuma que é 400)*
- **Tipo:** consulta
- **Pergunta:** PASSO 1 — Descobrir o mandante *(não presuma que é 400)*
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md, linha 87
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT DISTINCT MANDT FROM T000 ORDER BY MANDT;
```

## RB01-108 passo 2 — descobrir o schema *(não presuma que é `saphanadb`)*
- **Tipo:** consulta
- **Pergunta:** PASSO 2 — Descobrir o schema *(não presuma que é `SAPHANADB`)*
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md, linha 108
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT SCHEMA_NAME, COUNT(*) AS qtd_objetos FROM (
    SELECT SCHEMA_NAME, TABLE_NAME AS OBJ FROM SYS.TABLES
     WHERE TABLE_NAME IN ('MARA','MCHB','EBAN','EKKO')
    UNION ALL
    SELECT SCHEMA_NAME, VIEW_NAME  AS OBJ FROM SYS.VIEWS
     WHERE VIEW_NAME  IN ('MARA','MCHB','EBAN','EKKO')
) AS objetos_sap
GROUP BY SCHEMA_NAME
ORDER BY qtd_objetos DESC;
```

## RB01-141 passo 2 — descobrir o schema *(não presuma que é `saphanadb`)*
- **Tipo:** consulta
- **Pergunta:** PASSO 2 — Descobrir o schema *(não presuma que é `SAPHANADB`)*
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md, linha 141
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SET SCHEMA <NOME_QUE_VOCE_ANOTOU>;
```

## RB01-156 passo 3 — pré-voo 1: conferir o sinal da função de data
- **Tipo:** consulta
- **Pergunta:** PASSO 3 — Pré-voo 1: conferir o sinal da função de data
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md, linha 156
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT DAYS_BETWEEN(CURRENT_DATE, ADD_DAYS(CURRENT_DATE,  30)) AS deve_dar_MAIS_30,
       DAYS_BETWEEN(CURRENT_DATE, ADD_DAYS(CURRENT_DATE, -30)) AS deve_dar_MENOS_30
FROM DUMMY;
```

## RB01-181 passo 4 — pré-voo 2: descobrir onde mora a validade do lote
- **Tipo:** consulta
- **Pergunta:** PASSO 4 — Pré-voo 2: descobrir onde mora a validade do lote
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md, linha 181
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT 'MCHA' AS tabela, COUNT(*) AS lotes_com_validade
FROM   MCHA WHERE MANDT = '400' AND VFDAT IS NOT NULL
UNION ALL
SELECT 'MCH1' AS tabela, COUNT(*) AS lotes_com_validade
FROM   MCH1 WHERE MANDT = '400' AND VFDAT IS NOT NULL;
```

## RB01-210 passo 5 — pré-voo 3: descobrir os indicadores de liberação
- **Tipo:** consulta
- **Pergunta:** PASSO 5 — Pré-voo 3: descobrir os indicadores de liberação
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md, linha 210
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT FRGKZ AS indicador, COUNT(*) AS qtd,
       SUM(CASE WHEN EBELN <> '' THEN 1 ELSE 0 END) AS viraram_pedido
FROM   EBAN
WHERE  MANDT = '400' AND LOEKZ = '' AND WERKS IN ('1001','1005')
GROUP BY FRGKZ ORDER BY qtd DESC;
```

## USOBT_C e USOBT sem mandante
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** dicionário SAP (DD03L pelo Datasphere), 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por dicionário SAP (DD03L lido pelo Datasphere)

`USOBT_C` e `USOBT` não têm o campo MANDT (valem para todos os mandantes).

## autorização da C223 e C252
- **Tipo:** fato
- **Classe:** configuração
- **Fonte:** consulta PV-C3, 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP, mandante 400 (dono, 26/09/2026)
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\PV-C3.xlsx

Proposta da SU24: C223 e C252 usam o objeto `C_FVER_WRK` (campos ACTVT e WERKS). Confirmação pelo trace pendente.

## programas da C223 e C252
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** consulta PV-C4, 26/09/2026
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por execução no NSP, mandante 400 (dono, 26/09/2026)
- **Evidência:** C:\Users\fabriciosouza\sap-mrp-natulab\medicoes\PV-C4.xlsx

A transação C223 roda `R_TRANSACT_PROD_VERS`; a C252 roda `RCPDRK02`.

## MCHB é view de compatibilidade
- **Tipo:** fato
- **Classe:** estrutura
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\RUNBOOK-01-rodar-as-medicoes.md, linhas 124-137
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por documentação de simplificação do S/4HANA

No S/4HANA a MCHB é view de compatibilidade, não tabela física.

## validade do lote em MCHA ou MCH1
- **Tipo:** fato
- **Classe:** configuração
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linhas 194-206
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO

A validade do lote (VFDAT) pode estar no nível centro (MCHA) ou material (MCH1); juntar só na MCHA pode voltar vazio. Decide-se pela OMCT.
