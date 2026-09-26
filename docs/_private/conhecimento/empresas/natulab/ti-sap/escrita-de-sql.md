# ti-sap · escrita-de-sql

Gerado em 26/09/2026 por `C:\Users\fabriciosouza\sap-mrp-natulab\gestao\_migracao-scripts\gerar_biblioteca_natulab.py`
a partir das fontes apontadas em cada entrada (SQL copiado sem edição). Consulta em uso num projeto continua no projeto.
## R-01 regras de SQL no DBACOCKPIT
- **Tipo:** runbook
- **Pergunta:** Como escrever SQL nativo para o Editor SQL do DBACOCKPIT sem retrabalho?
- **Fonte:** C:\Users\fabriciosouza\biblioteca-consultas-sap\REGRAS-SQL.md (26/09/2026) e erros registrados nos projetos citados
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por erros reais registrados nos projetos MRP e budget TI

| # | Regra | Origem |
|---|---|---|
| 1 | Consulta sai **pronta**, sem valor a trocar. Mandante escrito (`MANDT = '400'`; em CDHDR/CDPOS o campo é `MANDANT`). Não sabe um valor: pergunta antes de entregar. | Placeholder `'???'` rodou em produção e voltou 0 linhas sem erro (MRP, 24/09/2026) |
| 2 | NSD, NSQ e NSP usam todos o **mandante 400**; só o SID distingue o sistema. Registrar o SID junto do resultado. | ETL USMM (22/07/2026) |
| 3 | Vazio testado como `TRIM(COALESCE(campo, '')) = ''`; zero como `COALESCE(campo, 0) = 0`. NULL não é igual a vazio. | Mapeamento MRP Live v14 da equipe; MRP 26/09/2026 |
| 4 | Sem comentário `--` e sem ponto e vírgula no fim: o editor corta a consulta. Uma consulta por vez. | MRP 24/09/2026 |
| 5 | O editor limita a 1.000 linhas. Resultado com exatamente 1.000 linhas foi cortado; preferir consulta agregada. | MRP 24/09/2026 |
| 6 | Campo existir no dicionário (DD03L) não prova que o SQL o enxerga. Antes de uma bateria nova, rodar `SELECT * FROM <tabela> WHERE MANDT = '400' LIMIT 1` para ver as colunas reais. | Campo do dicionário ausente na view do MARC (equipe, Mapeamento v14) |
| 7 | Material obsoleto: excluir com `COALESCE(m.MSTAE, '') NOT IN ('O1', 'Z4')` quando a pergunta é sobre cadastro ativo; manter quando a pergunta é o universo inteiro, e dizer qual das duas. | Consultas da casa (Mapeamento v14); decisão D17 do projeto MRP |
| 8 | Tabela grande (CDHDR, CDPOS, ACDOCA, BSEG, MSEG): filtrar por data e rodar primeiro no QAS. | MRP 26/09/2026; budget TI |
| 9 | "0 linhas" sem o arquivo exportado não é prova. Exportar a grade e guardar com o ID da consulta no nome. | Consulta 29b do budget TI, cega por construção |
| 10 | Tabela de repositório (TADIR, DDDDLSRC, TSTC, USOBT, ARS_*) não tem mandante: não filtrar. | Pré-voo MRP 26/09/2026 |
| 14 | A ACDOCA usa `RCLNT`, não `MANDT`; a ACDOCP usa `RYEAR`, não `GJAHR`. | Budget TI, `CONSULTAS-SAP-FINAL-v17.sql` |
| 15 | BSAK e BSIK não existem como tabela no HANA: partida de fornecedor por SQL é na BSEG. | Budget TI, erro em produção |
| 16 | `SYS.TABLES` não lista view: descobrir objeto em `SYS.TABLES` e `SYS.VIEWS`; coluna existente em `SYS.TABLE_COLUMNS`. | MRP RUNBOOK-01; budget blocos 31, 34c, 50-sonda |
| 17 | `DAYS_BETWEEN(d1, d2)` devolve d2 − d1; invertido não dá erro. Testar com duas datas conhecidas em cada ambiente. | MRP SPEC-02 |
| 18 | `NULL > 0` é falso no HANA: saldo que "voltou zero" pode ser NULL (MARD, MCHB); usar COALESCE (regra 3). | Mapa Operacional MRP |

## R-02 regras de SQL no Datasphere
- **Tipo:** runbook
- **Pergunta:** Como consultar o Datasphere sem cair no espaço errado ou em campo inexistente?
- **Fonte:** C:\Users\fabriciosouza\biblioteca-consultas-sap\REGRAS-SQL.md (26/09/2026) e erros registrados nos projetos citados
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por uso nos projetos MRP e Datasphere

| # | Regra | Origem |
|---|---|---|
| 11 | Conferir campo pela view do dicionário `STAGE_S4.VW_SVPL_DD03L` (tem descrição do campo) antes de usar. | MRP 24/09/2026 |
| 12 | Nome de objeto sempre qualificado pelo espaço (`"STAGE_S4"."VW_..."`): sem qualificar, cai no espaço de sandbox. | Projeto Datasphere |
| 13 | Armadilhas próprias do Datasphere (view parametrizada, modelo analítico): ver `C:\Users\fabriciosouza\Datasphere\agente-datasphere\ARMADILHAS.md`. | Projeto Datasphere |
