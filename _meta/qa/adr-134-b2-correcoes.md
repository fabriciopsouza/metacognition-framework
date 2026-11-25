# QA-evidence — adr-134-b2-correcoes

- **Data:** 2026-11-25
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Substitui vereditos anteriores deste bloco

- rodada 2 · 2026-11-25 · **aprovar** · sha `None` · agentId `ada50489ee1274a55`
  - cobria 6 caminho(s): tools/conferir_invariante.py, tools/test_conferir_invariante.py, CHANGELOG.md, _meta/qa/adr-134-b2-conferencia-invariante.json …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| MEDIA | tools/conferir_invariante.py | Codex r1: digitos Unicode bem formados passaram a ser recusados; re.ASCII removido. |
| BAIXA | tools/test_conferir_invariante.py | Codex r1: stderr descartado; cli devolve stdout+stderr e exige ausencia de Traceback. |
| BAIXA | tools/test_conferir_invariante.py | ECH: faltava caso de expoente com virgula; 1,5e3 incluido. |
| BAIXA | tools/conferir_invariante.py | ECH: espaco e quebra de linha ao redor do numero sao aceitos (strip); anterior a mudanca. |

## Verificacoes executadas (anti-fabricacao)

- canario 46 casos + 42 CLI PASS
- 11 mutacoes: 10 reprovadas; 1 equivalente (segunda virgula ja e recusada por Decimal)
