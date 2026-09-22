# QA-evidence — adr-115-quick-e-regra2-do-service-valuation

- **Data:** 2026-09-21T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Substitui vereditos anteriores deste bloco

- rodada 1 · 2026-09-21T00:00:00Z · **aprovar_com_ressalvas** · sha `d24c9d031e4f` · agentId `a596dac9a2f4c6aaf`
  - cobria 3 caminho(s): .agent/workflows/feature-plan.md, docs/_private/service-valuation/RATE-CARD.md, exemplos/service-valuation/RATE-CARD.example.md
- rodada 101 · 2026-09-21T00:00:00Z · **aprovar_com_ressalvas** · sha `d24c9d031e4f` · agentId `a596dac9a2f4c6aaf`
  - cobria 5 caminho(s): .agent/workflows/feature-plan.md, docs/_private/service-valuation/RATE-CARD.md, exemplos/service-valuation/RATE-CARD.example.md, _meta/qa/adr-115-quick-e-regra2-do-service-valuation.json …
- rodada 1 · 2026-09-21T00:00:00Z · **aprovar_com_ressalvas** · sha `d24c9d031e4f` · agentId `a596dac9a2f4c6aaf`
  - cobria 5 caminho(s): .agent/workflows/feature-plan.md, docs/_private/service-valuation/RATE-CARD.md, exemplos/service-valuation/RATE-CARD.example.md, _meta/qa/adr-115-quick-e-regra2-do-service-valuation.json …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| CRITICO | .agent/workflows/feature-plan.md - secao 'O que --quick corta' | O texto cortava 'o process-critic de J6', conflando o process-critic (ADR-011, QA adversarial mandatorio ao fim de todo BLOCO entregue) com J6 (ADR-045, a decisao de re-orquestracao do PMO, que roda DEPOIS do PC dar APROVADO_LIMPO). Cenario de falha: uma feature --quick e' um bloco entregue pela letra do ADR-011, logo o PC e' mandatorio para ela; mas o criterio de saida do --quick exigia apenas spec.md + 1 veredito de qa-critic (que e' o gate de juncao, equivalente a J4) + aceite verdadeiro. Nao havia PC nenhum no fluxo, e o rotulo 'J6' disfarcava o corte de um gate como corte de cerimonia. Workflow nao revoga ADR Aceito por edicao de arquivo. CORRIGIDO: --quick corta J6 explicitamente, e o process-critic e' FUNDIDO na unica rodada de qa-critic (mesmo subagente isolado, modelo != autor, os dois chapeus declarados em separado no veredito), com limite escrito de que fusao != dispensa e de que exigir rodada separada demandaria ADR proprio. |
| CRITICO | _meta/qa/adr-115-rodada-27-o-escritor-do-ledger-e-o-triturador.json - achado 1, campo estado | O achado CRITICO da 27a rodada seguia com estado 'aberto' embora o defeito que ele denuncia (qa_evidence.write_artifact sobrescrevendo sem cadeia) tivesse sido corrigido em 17-18/09 pela cadeia `substitui`. Consequencia reproduzida ao vivo pelo critico: `_reprovacao_vigente()` invalidava QUALQUER aprovativo novo por causa de um achado fantasma, e o gate empurraria quem fechasse o bloco para --no-verify, que o proprio codigo do gate chama de pior que o buraco que fecha. CORRIGIDO: os 3 achados ja' corrigidos foram fechados com quem, quando e prova dentro da `descricao` (campo canonico), nao num campo de topo novo. |
| ALTA | .agent/workflows/feature-plan.md - tabela do gatilho --quick, condicao 4 | A condicao de reversibilidade dizia 'sem E5/E6 do action-safety'. Conferido contra _shared/action-safety/SKILL.md: os predicados de reversibilidade sao E1 (destroi dado de forma irrecuperavel) e E2 (irreversivel/nao-idempotente); E5 e' alteracao de controle de seguranca e E6 e' comportamento atipico/fora do escopo. Cenario de falha: quem aplicasse a condicao literalmente verificaria a ausencia de E5/E6 e NUNCA checaria E1/E2 — uma mudanca genuinamente destrutiva ou irreversivel, mas dentro do escopo e sem tocar permissao, passaria como 'reversivel'. CORRIGIDO para E1/E2, com a distincao escrita na propria tabela. |
| MEDIA | CHANGELOG.md | O bloco que introduz a regra 'CHANGELOG e' nao-negociavel no --quick' nao a cumpria para si mesmo: nem o bump v1.2->v1.3 do feature-plan.md nem a correcao da Regra 2 do RATE-CARD.md apareciam no CHANGELOG. CORRIGIDO com secao [Nao lancado] propria. |
| MEDIA | tools/ - ausencia de canario para .agent/workflows/*.md | Nenhum canario valida .agent/workflows/*.md estruturalmente. test_skill_contract.py valida as 13 skills e nao tem uma referencia sequer a workflow (confirmado por grep pelo critico), e nenhum outro (test_core_no_vendor, test_project_onboarding, test_shadow_drift, test_squad_gate) o faz. Por isso os dois defeitos acima — a conflacao J6 x process-critic e o E5/E6 — chegaram ate o QA sem barreira automatizada nenhuma. NAO e' defeito introduzido por este bloco, e fica ABERTO de proposito: esta registrado como trabalho `canario-para-workflows`, com criterio de aceite = reintroduzir os dois bugs reais e a suite ficar vermelha. |
| BAIXA | exemplos/service-valuation/RATE-CARD.example.md | Linhas com Origem = travessao receberam Confianca [BAIXA]. Defensavel, mas [DESCONHECIDO] na origem ensina melhor a quem copia o molde, porque 'confianca baixa' sugere que existe uma origem fraca em vez de nenhuma. CORRIGIDO nas 13 linhas. |

## Verificacoes executadas (anti-fabricacao)

- critico leu o diff completo de feature-plan.md (v1.2 -> v1.3, 20 -> 65 linhas confirmado por git show HEAD:... | wc -l contra wc -l atual)
- critico leu docs/adr/011, 045, 110, 111 e _shared/action-safety/SKILL.md, e confirmou por grep em .agent/workflows/handoff.md que J6 e process-critic sao coisas distintas no proprio repo
- critico rodou python tools/test_service_valuation.py -> PASS, e python tools/test_skill_contract.py -> PASS (13 skills validadas)
- critico confirmou por grep que test_skill_contract.py NAO tem uma referencia sequer a workflow, e que nenhum outro canario valida .agent/workflows/*.md estruturalmente
- critico contou os pipes de cada linha das duas tabelas de rate card: 9 em 100% das linhas (cabecalho, separador, 22 e 13 linhas) — tabelas bem formadas
- critico comparou o rate card privado com o exemplo publico linha a linha: nenhum nome de cliente, valor de contrato ou identificador pessoal cruzou para o lado publico
- critico conferiu docs/_private/service-valuation/HISTORICO-ENTREGAS.md e confirmou que nenhuma das 22 linhas T-01..T-22 tem lastro que justificasse [CONFIRMADO]: o default uniforme [INFERIDO]/[MEDIA] e' honesto, nao carimbo indevido
- critico confirmou em export-clean.py que STRIP_BEFORE remove docs/_private inteiro antes de qualquer pacote publico
- autor rodou python tools/test_service_valuation.py e python tools/test_skill_contract.py apos as correcoes: PASS nos dois
