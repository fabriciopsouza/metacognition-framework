# Handoff — v1.80.0 · 2026-08-14T22:14:03-03:00 · papel-alvo: cross-ai

> Pacote P14 (ADR-012) gerado DETERMINISTICAMENTE do estado do repo por `tools/handoff.py` (ADR-076).
> Teste binario (P14): a proxima sessao comeca SEM perguntar nada de volta?

## [modelo sugerido] (regra papel+risco — ADR-076)
- **Proxima sessao: `claude-fable-5`** (fable). Motivo: cross-ai -> tier max (fable): coordenacao cross-IA -> mais capaz.

## [P14] Artefato consumivel — com versao
- Repo na versao **v1.80.0** (topo do CHANGELOG). Branch `docs/relatorio-sessao-2026-08-13` @ `8ddcfc8`.

## [P14] Localizacao
- origin: https://github.com/fabriciopsouza/metacognition-framework
- branch/commit: `docs/relatorio-sessao-2026-08-13` @ `8ddcfc8` · (sem PR aberto para esta branch)
- raiz absoluta desta copia: `C:\Users\fabriciosouza\metacognition-framework` (paths relativos abaixo ancoram AQUI)

## [P14] Acesso
- Nao-protegido (recovery = conta GitHub): 7 commit(s) NAO-pushado(s), 4 arquivo(s) nao-commitado(s)

## [P14] Prompt pronto-para-colar
- **Papel:** cross-ai · **Modelo:** `claude-fable-5`
- **Objetivo (do 'Proximo passo'):** migrar o passivo das 57 capacidades, começando por `handoff-generator` — cada uma ganha `mutacao` provada ou é rebaixada ao `enforcement` que de fato tem; é a condição que quita o override da régua §0. (Campo em UMA linha de propósito: o extrator do P14 trunca na quebra, medido em 14/08 — pendência #1, decisão do dono.)
- **Produz/decide:** execute o objetivo acima ate o criterio de aceite citado; rode `tools/run_canaries.py` antes de fechar.

## [P14] Pendencias e premissas herdadas
- (em aberto) **Quitação do override da régua §0 do ADR-102** (aberto em 13/08/2026): o padrão documental
- (em aberto) **[2026-08-07] Débitos de fechamento do bloco v1.77.0 — 3 achados, NADA aplicado.** Handoff completo (com comando de re-validação e predicado "aplicar SÓ SE" po
- (em aberto) **Pendência permanente (não-código, dono/TI):** exclusão do Kaspersky `.claude\hooks\*` (afeta só os hooks .ps1 remanescentes; ADR-060/079).
- (em aberto) **Backlog ativo (trigger-gated, NÃO WIP):**
- (em aberto) **Canário README × topo do CHANGELOG inexistente** (dívida PRÉ-EXISTENTE exposta pelo qa-critic em v1.73.0, 2026-07-22): a política do repo exige que README, ta
- (em aberto) **36 capabilities sem campo `enforcement` são invisíveis à auditoria anti-teatro** (observado 2026-07-22 ao corrigir achado do qa-critic): entradas que **omitem
- (ADR Proposto pendente) 097-conformance-topologia-hard-event-log-canario-process-mining.md

## Extensoes (ADR-016 — evita re-derivar)
- **5 arquivos mais recentes:**
  1. _meta/qa/release-1.80.0-prova-de-mutacao-adr-106.json
  2. _meta/qa/release-1.80.0-prova-de-mutacao-adr-106.md
  3. .agent/skills/qa-critic/rules.md
  4. CAPABILITIES.md
  5. CHANGELOG.md
