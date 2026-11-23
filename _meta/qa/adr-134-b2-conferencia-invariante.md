# QA-evidence — adr-134-b2-conferencia-invariante

- **Data:** 2026-11-23
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/conferir_invariante.py conferir_juncao | Codex r1: juncao so contava linhas; agora compara o multiconjunto das linhas esperadas. |
| ALTA | tools/conferir_invariante.py filtro/dedup | Codex r1: intersecao de colunas escondia coluna perdida; exige as colunas de antes. |
| ALTA | tools/conferir_invariante.py ler_csv | Codex r1: cabecalho repetido/vazio e linha com campos a mais -> exit 2. |
| MEDIA | tools/conferir_invariante.py main | Codex r1: lista de colunas vazia e opcao indevida -> exit 2. |
| MEDIA | tools/test_conferir_invariante.py | Codex r1: teste cego da soma por grupo na identidade -> item isolado. |
| MEDIA | tools/conferir_invariante.py conferir_agregacao | Sonnet r2: grupo repetido no agregado e grupo so com vazios -> grupo unico e mesmos grupos. |
| MEDIA | tools/conferir_invariante.py conferir_agregacao | Sonnet r2: falso REPROVA por ponto flutuante -> --tolerancia (padrao 0). |
| MEDIA | tools/test_conferir_invariante.py | Sonnet r2: testes cegos --saiu, mesmas colunas, chave unica esquerda, orfas -> casos novos. |
| BAIXA | tools/conferir_invariante.py numero | Sonnet r2: NaN/Infinity/sNaN -> exit 2. |
| ALTA | tools/conferir_invariante.py soma_por_grupo | Codex r3: contexto decimal de 28 digitos arredondava -> contexto EXATO com Inexact como erro. |
| MEDIA | tools/conferir_invariante.py | Codex r3: Overflow com traceback -> excecao decimal vira exit 2. |
| MEDIA | tools/conferir_invariante.py numero | Sonnet r4: expoente extremo travava -> limite \|e\| <= 10000, exit 2; teste com timeout de 30 s. |
| BAIXA | tools/test_conferir_invariante.py | Sonnet r4: colisao, chave repetida na identidade, subconjunto de grupos, --tolerancia na CLI -> casos novos. |
| BAIXA | tools/conferir_invariante.py tol | Sonnet r4: mensagem de --tolerancia invalida. |
| BAIXA | tools/conferir_invariante.py | Notas: soma por grupo nao ve troca no mesmo grupo (declarado; usar --chave); juncao com sufixo _x/_y exige renomear; filtro nao confere unicidade (fora do criterio). |

## Verificacoes executadas (anti-fabricacao)

- tools/test_conferir_invariante.py 46 casos + 21 CLI, PASS
- 16 sabotagens em copia do conferir_invariante.py (soma por grupo, chave, multiconjunto, valores da juncao, colunas, grupo unico, mesmos grupos, --saiu, mesmas colunas, nao finito, orfas, contexto exato, limite de expoente, colisao, chave repetida, subconjunto de grupos), todas reprovadas
- tools/test_analise_dados.py PASS (17 sabotagens); test_capabilities, test_marketing_claims, test_skill_contract, validate_skills PASS
- bateria run_canaries.py: 102 PASS, 1 SKIP, 1 FAIL (test_marketing_claims, numeros do site) corrigido e PASS
