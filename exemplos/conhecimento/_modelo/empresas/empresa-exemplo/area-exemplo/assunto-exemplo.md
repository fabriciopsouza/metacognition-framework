# area-exemplo · assunto-exemplo

## C-01 lotes por situação
- **Tipo:** consulta
- **Pergunta:** quantos lotes existem em cada situação?
- **Sistema:** SISTEMA-X
- **Versão:** 2024
- **Fonte:** projeto-exemplo, arquivo de consultas, linha 20
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por quem executou

```sql
SELECT SITUACAO, COUNT(*) AS LOTES
FROM LOTES
GROUP BY SITUACAO;
```

## F-01 lotes bloqueados
- **Tipo:** fato
- **Classe:** retrato
- **Fonte:** execução da C-01
- **Verificado em:** 26/09/2026
- **Confiança:** CONFIRMADO por quem executou

120 lotes na situação "bloqueado".

## R-01 como exportar o resultado da C-01
- **Tipo:** runbook
- **Pergunta:** como rodar a C-01 e salvar o resultado como evidência?
- **Fonte:** projeto-exemplo
- **Verificado em:** 26/09/2026
- **Confiança:** INFERIDO

1. Abrir a ferramenta de consulta do SISTEMA-X.
2. Colar a C-01 e executar.
3. Exportar para planilha com a data no nome.
