# Handoff — v1.90.0 · 2026-08-18T18:12:17-03:00 · papel-alvo: qa-critic

> Pacote P14 (ADR-012) gerado DETERMINISTICAMENTE do estado do repo por `tools/handoff.py` (ADR-076).
> Teste binario (P14): a proxima sessao comeca SEM perguntar nada de volta?

## [modelo sugerido] (regra papel+risco — ADR-076)
- **Proxima sessao: `claude-sonnet-4-6`** (sonnet). Motivo: qa/review -> HETEROGENEO (autor=opus; ADR-018 anti-vies; escada completa em model-policy.json).

## [P14] Artefato consumivel — com versao
- Repo na versao **v1.90.0** (topo do CHANGELOG). Branch `main` @ `088b11c`.

## [P14] Localizacao
- origin: https://github.com/fabriciopsouza/metacognition-framework
- branch/commit: `main` @ `088b11c` · (sem PR aberto para esta branch)
- raiz absoluta desta copia: `C:\Users\fabriciosouza\metacognition-framework` (paths relativos abaixo ancoram AQUI)

## [P14] Acesso
- Nao-protegido (recovery = conta GitHub): nada pendente (tudo pushado/commitado)

## [P14] Prompt pronto-para-colar
- **Papel:** qa-critic · **Modelo:** `claude-sonnet-4-6`
- **Objetivo (do 'Proximo passo'):** amarrar o verificador ao `squad_gate` como bloqueio, hoje ele é canário da
- **Produz/decide:** execute o objetivo acima ate o criterio de aceite citado; rode `tools/run_canaries.py` antes de fechar.

## [P14] Pendencias e premissas herdadas
- (em aberto) **Quitação do override da régua §0 do ADR-102** (aberto em 13/08/2026): o padrão documental
- (em aberto) **[2026-08-07] Débitos de fechamento do bloco v1.77.0 — 3 achados, NADA aplicado.** Handoff completo (com comando de re-validação e predicado "aplicar SÓ SE" po
- (em aberto) **ADR-097 itens 4 e 5 do §Mecanismo** (aberto em 16/08/2026, ao aceitar o ADR): a camada-mestra
- (em aberto) **Pendência permanente (não-código, dono/TI):** exclusão do Kaspersky `.claude\hooks\*` (afeta só os hooks .ps1 remanescentes; ADR-060/079).
- (em aberto) **Backlog ativo (trigger-gated, NÃO WIP):**
- (em aberto) **Canário README × topo do CHANGELOG inexistente** (dívida PRÉ-EXISTENTE exposta pelo qa-critic em v1.73.0, 2026-07-22): a política do repo exige que README, ta

## Extensoes (ADR-016 — evita re-derivar)
- **5 arquivos mais recentes:**
  1. _meta/qa/adr-108-procedencia-do-veredito.json
  2. _meta/qa/adr-108-procedencia-do-veredito.md
  3. _meta/qa/emenda-6-crlf-e-contagem-do-provar.json
  4. _meta/qa/emenda-squad-gate-arquivo-novo.json
  5. _meta/qa/junctions/v1.90.0-procedencia-do-veredito.jsonl
