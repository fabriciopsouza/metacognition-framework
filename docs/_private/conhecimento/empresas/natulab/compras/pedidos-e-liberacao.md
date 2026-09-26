# compras · pedidos-e-liberacao

Gerado em 26/09/2026 por `C:\Users\fabriciosouza\sap-mrp-natulab\gestao\_migracao-scripts\gerar_biblioteca_natulab.py`
a partir das fontes apontadas em cada entrada (SQL copiado sem edição). Consulta em uso num projeto continua no projeto.
## Q-A itens de pedido em aberto com remessa vencida
- **Tipo:** consulta
- **Pergunta:** Quais itens de pedido de compra estão em aberto com a remessa vencida (passivo desde 2022)?
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\gestao\RESPOSTA-questionamentos-MRP.md, seção 3, linha 183
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\gestao\RESPOSTA-questionamentos-MRP.md

```sql
-- Itens de pedido ABERTOS com remessa vencida, e o que os separa
SELECT  k.EKORG, k.LIFNR AS fornecedor, k.BEDAT AS data_documento,
        p.EBELN AS pedido, p.EBELP AS item, p.MATNR AS material, p.WERKS AS centro,
        p.MENGE AS qtd_pedida, p.MEINS,
        p.LOEKZ AS ind_eliminacao_ou_bloqueio,   -- '' aberto | 'S' bloqueado | 'L' eliminado
        p.ELIKZ AS entrega_final,                -- 'X' = nao espera mais nada
        e.EINDT AS data_remessa,
        e.MENGE AS qtd_programada, e.WEMNG AS qtd_recebida,
        (e.MENGE - e.WEMNG) AS saldo_em_aberto
FROM    EKKO k
JOIN    EKPO p ON p.EBELN = k.EBELN
JOIN    EKET e ON e.EBELN = p.EBELN AND e.EBELP = p.EBELP
WHERE   p.LOEKZ <> 'L'          -- eliminados ja' saem do MRP
  AND   p.ELIKZ <> 'X'          -- entrega final ja' encerra a expectativa
  AND   (e.MENGE - e.WEMNG) > 0
  AND   e.EINDT < '20260922'    -- remessa ja' vencida
ORDER BY e.EINDT;
```

## SP02-159 pré-voo 3 — os indicadores de liberação que existem de fato
- **Tipo:** consulta
- **Pergunta:** Pré-voo 3 — os indicadores de liberação que existem de fato
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linha 159
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT FRGKZ AS indicador, COUNT(*) AS qtd,
       SUM(CASE WHEN EBELN <> '' THEN 1 ELSE 0 END) AS viraram_pedido
FROM   EBAN
WHERE  MANDT = '400' AND LOEKZ = '' AND WERKS IN ('1001','1005')
GROUP BY FRGKZ ORDER BY qtd DESC;
```

## SP02-331 q-d — qual dos três furos da liberação existe? **(f1 · f2)**
- **Tipo:** consulta
- **Pergunta:** Q-D — Qual dos três furos da liberação existe? **(F1 · F2)**
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linha 331
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT  CASE WHEN q.FRGGR = '' OR q.FRGGR IS NULL
             THEN 'F2 - SEM ESTRATEGIA' ELSE 'com estrategia' END AS enquadramento,
        q.FRGGR AS grupo_liberacao, q.FRGST AS estrategia, q.FRGKZ AS indicador,
        q.BSART AS tipo_documento,
        COUNT(*) AS qtd_requisicoes,
        SUM(CASE WHEN q.EBELN <> '' THEN 1 ELSE 0 END) AS viraram_pedido
FROM    EBAN q
WHERE   q.LOEKZ = ''
  AND   q.WERKS IN ('1001','1005')
  AND   q.BADAT >= '20260101'
GROUP BY q.FRGGR, q.FRGST, q.FRGKZ, q.BSART
ORDER BY enquadramento, qtd_requisicoes DESC;
```

## SP02-355 q-e ⭐⭐ — o furo já foi usado? *(a diferença entre risco e achado)*
- **Tipo:** consulta
- **Pergunta:** Q-E ⭐⭐ — O furo já foi USADO? *(a diferença entre risco e achado)*
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linha 355
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT  q.BANFN AS requisicao, q.BNFPO AS item_req,
        q.EBELN AS pedido, q.EBELP AS item_pedido,
        q.MATNR AS material, q.WERKS AS planta, q.MENGE AS qtd,
        q.BADAT AS data_requisicao,
        q.FRGGR AS grupo_liberacao, q.FRGKZ AS indicador_hoje,
        q.ERNAM AS criou_a_requisicao,
        k.ERNAM AS criou_o_pedido, k.BEDAT AS data_pedido
FROM    EBAN q
JOIN    EKKO k ON k.EBELN = q.EBELN
JOIN    EKPO i ON i.EBELN = q.EBELN AND i.EBELP = q.EBELP
               AND i.BANFN = q.BANFN AND i.BNFPO = q.BNFPO   -- confirma a origem
WHERE   q.EBELN <> '' AND q.LOEKZ = ''
  AND   q.WERKS IN ('1001','1005')
  AND   q.BADAT >= '20260101'      -- <- mesma janela de Q-D; ampliar se quiser histórico
  AND   ( q.FRGGR = '' OR q.FRGGR IS NULL
          OR q.FRGKZ IN ( <<indicadores de NAO liberado>> ) )
ORDER BY q.BADAT DESC;
```

## SP02-409 q-f — f3: requisição alterada depois de liberada
- **Tipo:** consulta
- **Pergunta:** Q-F — F3: requisição alterada depois de liberada
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linha 409
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT  h.OBJECTID AS requisicao, h.UDATE AS data_mudanca, h.UTIME,
        h.USERNAME AS quem, d.FNAME AS campo,
        d.VALUE_OLD AS de, d.VALUE_NEW AS para
FROM    CDHDR h
JOIN    CDPOS d ON d.OBJECTCLAS = h.OBJECTCLAS
                AND d.OBJECTID  = h.OBJECTID
                AND d.CHANGENR  = h.CHANGENR
WHERE   h.OBJECTCLAS = 'BANF'          -- <- CONFERIR
  AND   d.FNAME IN ('MENGE','PREIS','LIFNR','FLIEF','LFDAT','FRGKZ')
  AND   h.UDATE >= '20260101'
ORDER BY h.OBJECTID, h.UDATE;
```

## SP02-438 q-g — d-13: o plano de entregas pode ser editado depois de aprovado?
- **Tipo:** consulta
- **Pergunta:** Q-G — D-13: o plano de entregas pode ser editado depois de aprovado?
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linha 438
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT  h.OBJECTID AS documento, h.UDATE, h.USERNAME AS quem,
        d.FNAME AS campo, d.VALUE_OLD AS de, d.VALUE_NEW AS para
FROM    CDHDR h
JOIN    CDPOS d ON d.OBJECTCLAS = h.OBJECTCLAS AND d.OBJECTID = h.OBJECTID
                AND d.CHANGENR = h.CHANGENR
WHERE   h.OBJECTCLAS = 'EINKBELEG'     -- <- CONFERIR: classe dos documentos de compra
  AND   d.FNAME IN ('KDATB','KDATE','KTWRT','ZBD1T','FRGKE','LIFNR')
  AND   h.UDATE >= '20260101'
ORDER BY h.OBJECTID, h.UDATE;
```

## SP02-463 q-h — d-14: segregação de função no objeto que concentra o controle
- **Tipo:** consulta
- **Pergunta:** Q-H — D-14: segregação de função no objeto que concentra o controle
- **Sistema:** SAP S/4HANA (DBACOCKPIT, HANA nativo)
- **Versão:** 2023 SP03
- **Fonte:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md, linha 463
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO
- **Aponta para:** C:\Users\fabriciosouza\sap-mrp-natulab\consultas\SPEC-02-medicoes-que-destravam.md

Rascunho de 22/09/2026, anterior às definições do PCP: conferir valores marcados antes de rodar.

```sql
SELECT  k.EBELN AS documento, k.BSART AS tipo, k.LIFNR AS fornecedor,
        k.ERNAM AS criou,
        (SELECT MAX(h2.USERNAME) FROM CDHDR h2
          JOIN CDPOS d2 ON d2.OBJECTCLAS = h2.OBJECTCLAS
                        AND d2.OBJECTID = h2.OBJECTID
                        AND d2.CHANGENR = h2.CHANGENR
          WHERE h2.OBJECTID = k.EBELN AND d2.FNAME = 'FRGKE') AS liberou
FROM    EKKO k
WHERE   k.BSTYP IN ('L','K')      -- <- CONFERIR: plano de entregas e contrato
  AND   k.BEDAT >= '20260101';
```
