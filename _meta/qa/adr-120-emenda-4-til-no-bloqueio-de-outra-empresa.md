# QA-evidence — adr-120-emenda-4-til-no-bloqueio-de-outra-empresa

- **Data:** 2026-10-09T11:00:20Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Steelman
a correção poderia mudar o tratamento de caminho relativo; _expandir devolve o texto intacto quando não começa com ~, e _caminho_existe recebe o v original

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| BAIXA | tools/test_conhecimento_isolamento.py | título do bloco da emenda 4 não cobria o caso de bloqueio entre empresas |
| BAIXA | tools/test_conhecimento_isolamento.py | espaço faltando depois de '=' |
| BAIXA | docs/adr/120-biblioteca-de-conhecimento-metodo-e-verificador.md | fim de arquivo sem quebra e linha em branco dupla antes da emenda 4 |
| BAIXA | tools/test_conhecimento_isolamento.py | ~ sozinho ou com crase sem caso no canário |

## Verificacoes executadas (anti-fabricacao)

- crítico: test_conhecimento_isolamento.py PASS 0 falhas; leitura de _expandir, _norm_caminho, _projetos, resolver_empresa, identificadores_de_empresa
- autor: caso AL-C6 falha no código do main e passa com a correção (mutação morta)
