# QA-evidence — release-1.80.1-fechamento-automatico-e-anti-passividade

- **Data:** 2026-08-16T09:20:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas
- **Fecha release:** v1.80.1

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** leitura do original em PowerShell antes de julgar o port
- **RRC:** PASSA — o critico foi buscar o arquivo original no git e comparou dimensao a dimensao, em vez de aceitar a alegacao de equivalencia do commit; foi exatamente isso que derrubou a alegacao.
- **Metodo-senior:** N/A: port e ferramenta nova sob ADR ja aceito.

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| medio | tools/hooks/consistency_gate.py (laco sobre docs/adr) | CORRIGIDO nesta rodada. O filtro de `000-*` era aplicado tambem a contagem de numero, perdendo a deteccao de duplicata entre templates. Divergencia real contra o `.ps1` original. |
| baixo | tools/hooks/consistency_gate.py (docstring) | CORRIGIDO. O texto afirmava equivalencia 'verificada linha a linha' que o autor nao havia verificado de forma independente — overclaim em documentacao, a classe que o proprio framework persegue. |
| baixo | tools/decisoes_que_governam.py (_dividas_abertas) | CORRIGIDO defensivamente. Continuacao de item sem recuo era descartada em silencio; nao dispara no history.md atual, que usa recuo consistente, mas dependia disso. |

## Verificacoes executadas (anti-fabricacao)

- critico em worktree isolado em b459ca9; comparacao linha a linha do port Python contra `git show b459ca9^:tools/hooks/consistency-gate.ps1`
- achado MEDIO reproduzido por leitura: dois arquivos `000-*` fariam o original acusar duplicata e o port nao
- correcao aplicada: numero conta ANTES do filtro de `000-*`; caso de regressao nomeado no canario
- correcao do docstring: a alegacao de equivalencia linha a linha era do autor, sem verificacao independente — reescrita para dizer o que de fato houve
- suspeita 3 do critico (parser de item multilinha sem recuo) fechada: qualquer linha nao-vazia que nao inicie item novo passa a ser continuacao
- AUTOR, porque o critico nao conseguiu (usou pytest, que por decisao do ADR-040 nao coleta estes canarios): prova de mutacao das 3 guardas — 'nunca acusar version-sync' -> FAIL(1); '000-* fora da contagem' -> FAIL(1) exatamente no caso de regressao novo; 'nunca ligar divida aberta' -> FAIL(2). Restaurados, os dois canarios voltam a 0
- canarios: consistency_gate 13/13, decisoes_que_governam 9/9
