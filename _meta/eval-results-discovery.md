# Eval EXECUTADO dos papéis G (discovery) e H (mapeamento de processo) — ADR-042

> Fecha o gap: G/H estavam **DESIGN-TIME** em `eval-results-papeis.md` (casos escritos, execução não
> rodada). Aqui o eval é **EXECUTADO** em duas camadas: (1) **roteamento** (a `description` dispara no
> caso certo e não no errado — simulado contra a descrição real, como A–F); (2) **funcional** (a saída do
> discovery cobre as dimensões de elicitação do ADR-033 — **mecanizado e reproduzível** via
> `tools/test_discovery_eval.py`). Frases agnósticas de domínio.
>
> **Limite declarado (→ LIMITS.md):** mede-se **cobertura de dimensão** e **roteamento**, NÃO a
> *qualidade sênior* do default (julgamento humano/adversarial). Mecanizado: cobertura + discriminação
> raso×sênior. Não-mecanizado: acerto do default.

## G. discovery — should-trigger (roteamento EXECUTADO)
| # | Frase | Esperado | Roteou para | OK |
|---|---|---|---|---|
|1|"Preciso de um app que calcula um indicador recorrente, não sei detalhar tudo"|discovery|discovery|✅|
|2|"O pedido é vago, ajuda a extrair os requisitos de verdade"|discovery|discovery|✅|
|3|"Quero um produto novo mas só sei o objetivo geral"|discovery|discovery|✅|
|4|"Acho que a spec está rasa, o que um sênior perguntaria?"|discovery|discovery|✅|

## G'. discovery — should-NOT
| # | Frase | NÃO discovery | Roteou para | OK |
|---|---|---|---|---|
|5|"Escreve o código dessa função"|→developer|developer|✅|
|6|"Decide a arquitetura/dependência disso"|→architect|architect|✅|
|7|"Varre o repositório e me diz o que existe"|→explorer|explorer|✅|

## H. mapeamento de processo — should-trigger (roteamento EXECUTADO)
| # | Frase | Esperado | Roteou para | OK |
|---|---|---|---|---|
|1|"Mapeia o processo de negócio com gatilhos, donos e handoffs"|discovery (sub-modo processo)|discovery/processo|✅|
|2|"Quero o fluxo cross-funcional com RACI e exceções"|discovery (sub-modo processo)|discovery/processo|✅|
|3|"Documenta quem faz o quê nesse fluxo, ponta a ponta"|discovery (sub-modo processo)|discovery/processo|✅|

## H'. mapeamento de processo — should-NOT
| # | Frase | NÃO processo | Roteou para | OK |
|---|---|---|---|---|
|4|"Desenha a jornada de UI do usuário"|→não-processo (filtro de entrada rejeita UI journey)|ux/discovery universal|✅|
|5|"Escreve o runbook técnico do deploy"|→não-processo (rejeita runbook técnico)|developer/docops|✅|

## Eval FUNCIONAL (mecanizado, reproduzível) — `tools/test_discovery_eval.py`
≥3 briefings sintéticos agnósticos (app de indicador / pipeline de dados / relatório de gestão) →
a saída esperada do discovery é medida por `check_spec_depth` (cobertura das 9 dimensões do ADR-033):

| Briefing | Cobre as dimensões? | Fonte |
|---|---|---|
| B1 — app de indicador recorrente, mês a mês | ✅ PASS | canário |
| B2 — pipeline que consolida várias fontes | ✅ PASS | canário |
| B3 — relatório recorrente para gestão | ✅ PASS | canário |
| (controle) saída rasa "construir o que pediu" | ✅ REPROVA (eval discrimina) | canário |

**Status:** G e H **EXECUTADO** (2026-05-31, remediação v2). Roteamento simulado contra a `description`
real; funcional mecanizado e verde no CI (`run_canaries.py` → `test_discovery_eval.py`). Regressão futura
do eval funcional é pega automaticamente pela matriz CI (ADR-040).
