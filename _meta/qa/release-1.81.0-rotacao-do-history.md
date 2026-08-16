# QA-evidence — release-1.81.0-rotacao-do-history

- **Data:** 2026-08-16T11:10:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas
- **Fecha release:** v1.81.0

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** comparacao do que a branch trazia originalmente contra o que sobreviveu ao merge, antes de julgar
- **RRC:** PASSA — o critico comparou byte a byte contra o commit anterior via git show, em vez de aceitar a contagem do autor, e foi isso que revelou tanto a duplicata quanto o risco do indice.
- **Metodo-senior:** N/A: desencalhe de branch sob ADR ja aceito.

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| alto | history.md x docs/history/history-archive.md | CORRIGIDO. O merge preservou o quente da main e o frio da branch, duplicando 46 checkpoints e deixando a ferramenta em estado onde usa-la corromperia o arquivo frio. |
| medio | docs/history/history-archive.md (indice do git) | CORRIGIDO antes do commit. O arquivo aparecia como deletado no indice e nao-rastreado na arvore ao mesmo tempo; commit sem `git add` explicito o teria apagado do repositorio. |
| baixo | tools/test_rotate_history.py (docstring) | CORRIGIDO. Citava ADR-092 para a rotacao; quem seguisse a referencia cairia no ADR-092 legitimo, que e' sobre enforcement do squad. |
| baixo | docs/_private/handoffs/2026-08-07-debitos-de-fechamento-v1.77.0.md | NAO corrigido, por acordo entre autor e critico: e' registro datado de epoca e a renumeracao so existe desde ontem. Editar retroativamente violaria a preservacao de registro. |

## Verificacoes executadas (anti-fabricacao)

- R1 em worktree isolado em 1a1b3af: interseccao de cabecalhos entre quente e frio -> 56 duplicados; dry-run confirmando arquivo total=102
- R1: verificou que NAO houve perda de trabalho no merge — ferramenta, canario, ADR-107, arquivo frio e a capacidade sobreviveram; a capacidade aponta para o ADR renumerado
- R1: confirmou que existe um unico docs/adr/092-* (enforcement, legitimo da main) e um unico docs/adr/107-* (rotacao)
- R1: exercitou a ferramenta em history de mentira — zero perda, secoes inteiras no quente, idempotente em duas rodadas
- R2 sobre a correcao: quente 10 + frio 56 = 66 do original; interseccao vazia; zero duplicata interna no frio; todo bloco BYTE-IDENTICO ao que existia em 1a1b3af; CRLF preservado nos dois arquivos
- R2: ordem do frio e' subsequencia da ordem original; `## Em aberto` e `## Aprendizado` inteiras SO' no quente (a ocorrencia no frio era substring em prosa de checkpoint arquivado, nao linha de secao)
- R2: release 1.81.0 e ponteiro para o frio presentes no quente; segunda rotacao devolve changed=False
- R2: `git status --porcelain -uall` mostrando o frio como D no indice e ?? na arvore — risco de o commit apagar o arquivo; encenado e corrigido com `git add` explicito, conferido por `git diff --cached --stat` (152 linhas indo para o commit)
- autor: 66 -> 10 quentes + 56 frios medidos contra `git show HEAD:history.md`; history.md encolheu 836 linhas
