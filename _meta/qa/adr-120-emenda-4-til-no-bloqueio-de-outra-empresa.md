# QA-evidence — adr-120-emenda-4-til-no-bloqueio-de-outra-empresa

- **Data:** 2026-10-09T13:09:01Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Substitui vereditos anteriores deste bloco

- rodada 1 · 2026-10-09T11:00:20Z · **aprovar_com_ressalvas** · sha `e07a75ca830d` · agentId `ad0e92ad2bc54cd7c`
  - cobria 0 caminho(s) (nenhum)

## Steelman
a troca de basename poderia mudar a identidade de repositórios já indexados; a equivalência foi medida contra o código antigo

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| BAIXA | tools/conhecimento.py:_nome_repo | strip só nas pontas de crase divergia do strip antigo em formatos exóticos |
| BAIXA | tools/test_conhecimento_isolamento.py:213 | caso de caminho de projeto em assuntos/ não prova mais que o achado vem do caminho |
| BAIXA | tools/conhecimento.py:547,593 | os.sep no Linux não enxerga barra invertida em identificador |

## Verificacoes executadas (anti-fabricacao)

- crítico: test_conhecimento_isolamento PASS; equivalência de _nome_repo em 15 entradas
- autor: equivalência em 8 entradas após a correção (0 diferenças); test_conhecimento e test_conhecimento_isolamento PASS
