# QA-evidence — adr-120-emenda-4-til-no-bloqueio-de-outra-empresa

- **Data:** 2026-10-09T15:55:43Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Substitui vereditos anteriores deste bloco

> **ATENCAO: este veredito substitui uma REPROVACAO.** Leia os antecedentes antes de tratar o bloco como aprovado.

- rodada 1 · 2026-10-09T11:00:20Z · **aprovar_com_ressalvas** · sha `e07a75ca830d` · agentId `ad0e92ad2bc54cd7c`
  - cobria 0 caminho(s) (nenhum)
- rodada 2 · 2026-10-09T13:09:01Z · **aprovar_com_ressalvas** · sha `a88307cb9142` · agentId `a16fc079488882302`
  - cobria 0 caminho(s) (nenhum)
- rodada 3 · 2026-10-09T15:54:10Z · **corrigir** · sha `ae19998dede9` · agentId `af76ab8c880bbb2bf`
  - cobria 0 caminho(s) (nenhum)

## Steelman
a segunda tentativa com realpath poderia mascarar o caminho escrito; ela só entra quando a forma escrita não casa, e o identificador guardado continua o escrito

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| BAIXA | tools/test_conhecimento_isolamento.py:379-382 | negativa do caso (b) comparava com lower(), vazia no POSIX |
| BAIXA | tools/conhecimento.py:673 | projeto-atalho para pasta de outra empresa pode atribuir Evidência pelo caminho resolvido |
| BAIXA | tools/conhecimento.py:385-386 | realpath por projeto em rede fora do ar pode ser lento |

## Verificacoes executadas (anti-fabricacao)

- crítico: canário PASS; leitura de _norm_caminho, _dentro, _contem e do bloqueio
- autor: 2 mutações mortas com FAIL limpo
