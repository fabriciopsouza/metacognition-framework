# QA-evidence — adr-120-emenda-4-til-no-bloqueio-de-outra-empresa

- **Data:** 2026-10-09T17:21:31Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Substitui vereditos anteriores deste bloco

- rodada 1 · 2026-10-09T11:00:20Z · **aprovar_com_ressalvas** · sha `e07a75ca830d` · agentId `ad0e92ad2bc54cd7c`
  - cobria 0 caminho(s) (nenhum)
- rodada 2 · 2026-10-09T13:09:01Z · **aprovar_com_ressalvas** · sha `a88307cb9142` · agentId `a16fc079488882302`
  - cobria 0 caminho(s) (nenhum)
- rodada 3 · 2026-10-09T15:54:10Z · **corrigir** · sha `ae19998dede9` · agentId `af76ab8c880bbb2bf`
  - cobria 0 caminho(s) (nenhum)
- rodada 4 · 2026-10-09T15:55:43Z · **aprovar_com_ressalvas** · sha `ae19998dede9` · agentId `afa4a16b1612eccaa`
  - cobria 0 caminho(s) (nenhum)

## Steelman
o simulador poderia aceitar qualquer caminho; só devolve intacto o que está sob o diretório simulado inexistente

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| BAIXA | tools/test_conhecimento_isolamento.py:378 | startswith sem separador no simulador |
| BAIXA | tools/test_conhecimento_isolamento.py:377 | base_real sem normcase no primeiro ramo |

## Verificacoes executadas (anti-fabricacao)

- crítico: canário PASS; 2 mutações reexecutadas em cópia, mortas
- autor: canário PASS; mutações mortas
