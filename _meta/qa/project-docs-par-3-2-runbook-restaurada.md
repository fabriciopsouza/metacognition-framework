# QA-evidence — project-docs-par-3-2-runbook-restaurada

- **Data:** 2026-09-23T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** —
- **Metodo-senior:** —

## Substitui vereditos anteriores deste bloco

- rodada 3 · 2026-09-23T00:00:00Z · **aprovar_com_ressalvas** · sha `4584462` · agentId `a9123f9d95a2d7f3c`
  - cobria 1 caminho(s): _shared/project-docs/SKILL.md
- rodada 3 · 2026-09-23T00:00:00Z · **aprovar_com_ressalvas** · sha `4584462` · agentId `a9123f9d95a2d7f3c`
  - cobria 3 caminho(s): _shared/project-docs/SKILL.md, _meta/qa/project-docs-par-3-2-runbook-restaurada.json, _meta/qa/project-docs-par-3-2-runbook-restaurada.md

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| MEDIA | _shared/project-docs/SKILL.md par.3 (tabela de porte) | RUNBOOK ficava orfao: nao aparecia na tabela de porte nem declarava a que se aplica, ao contrario do par.3.1 que declara 'vale para o porte medio em diante'. Corrigido com paragrafo explicitando que RUNBOOK e' condicional a NATUREZA da tarefa, nao ao porte. |
| MEDIA | _shared/project-docs/SKILL.md par.3.2.1 | Os 6 pontos de credencial de servico eram apresentados como norma universal sem marca de confianca, sob uma skill que declara obedecer a propria par.2.2 - o modo de falha 3 do proprio par.5 ('nome sem procedencia sob cabecalho que afirma verificacao'). Corrigido: marcados INFERIDO, de um caso so', com a origem distinta das marcas R1-R5 declarada. |
| MEDIA | _shared/project-docs/SKILL.md par.8 | A capacidade nova nao tinha entrada de debito, ao contrario de par.3, par.4 e par.3.1. Corrigido com entrada declarando que as 5 marcas nao tem gate, que so' R1/R2/R5 sao mecanizaveis, e com criterio de quitacao no segundo projeto que produzir runbook por este padrao. |
| MEDIA | _shared/project-docs/SKILL.md par.8 (evidencia do debito) | A alegacao quantitativa ('falhou R5 em 100% dos itens', 'R1 em duas das tres portas') estava sem data nem ancora, violando a propria par.2.4. Corrigido: 22-23/09/2026, tres rodadas, e a natureza do artefato de origem declarada sem nomear projeto (anti-vazamento). |
| MEDIA | capabilities.json (id project-docs-standard) | O registro segue descrevendo a skill como '7 propriedades + conjunto graduado + 4 gates', sem citar par.3.1 nem par.3.2. NAO corrigido por decisao de escopo: o autor havia acabado de comunicar a duas sessoes-irmas que tocaria um unico caminho nesta arvore compartilhada, e ampliar o footprint depois de declarar o contrario seria pior que o defeito. Declarado como debito irmao no par.8, com criterio de quitacao. O QA da rodada 3 classificou a decisao como defensavel e o achado como tecnicamente aberto - as duas coisas, e concordo. |

## Verificacoes executadas (anti-fabricacao)

- r1: conferiu se a reconstrucao de memoria tinha corrupcao - frase truncada, tabela malformada, link morto, termo sem definicao: nenhuma encontrada
- r1: conferiu encaixe da par.3.2 entre par.3.1 e par.4 sem quebrar numeracao, fluxo ou vocabulario
- r1: conferiu se a par.3.2 contradiz as 7 propriedades do par.2, o conjunto graduado do par.3 ou o par.3.1 - nao contradiz
- r1: apontou que RUNBOOK ficava orfao da tabela de porte do par.3, que os 6 pontos do par.3.2.1 nao tinham marca de confianca, e que o par.8 nao declarava debito da capacidade nova
- r2: git diff --cached e git diff para isolar exatamente o que mudou entre rodadas
- r2: apontou que a alegacao quantitativa do par.8 estava sem data nem ancora verificavel
- r3: conferiu que o par.8 passou a citar 22-23/09/2026, o numero de rodadas e a natureza do artefato de origem
- r3: grep em capabilities.json (id project-docs-standard) confirmando que title/mechanism/tags seguem sem citar par.3.1 nem par.3.2
- r3: git diff --cached de SKILL.md confirmando que a unica mudanca e' a insercao no par.8, sem edicao colateral em outro arquivo
