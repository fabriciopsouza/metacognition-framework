# QA-evidence — planilhas-leia-aba-valores

- **Data:** 2026-10-20T22:16:22Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** inline: defeito observado na planilha enviada ao SSMA (ssma-plataforma, 20/10/2026)
- **RRC:** N/A: correcao de texto de uma linha
- **Metodo-senior:** N/A: sem fonte canonica nova

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| MEDIA | tools/test_planilhas_projeto.py | r2: nenhum teste cobria o texto condicional da LEIA; corrigido com asserts nos dois ramos |
| BAIXA | tools/test_planilhas_projeto.py | r3: valores lista/dict vazio nao testado; comportamento coerente (falsy), so observacao |

## Verificacoes executadas (anti-fabricacao)

- r2: test_planilhas_projeto.py PASS; apontou falta de teste da condicao (MEDIO)
- r3: test_planilhas_projeto.py PASS (0 falhas)
- r3: mutacao d['valores'] -> True em copia no TEMP: teste 'sem valores' FALHA (mutacao capturada)
- r3: confirmacao_v7.xlsx do ssma-plataforma so com abas LEIA e REGRAS e texto 'da aba REGRAS'
