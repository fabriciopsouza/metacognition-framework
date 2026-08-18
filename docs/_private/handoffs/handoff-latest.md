# Handoff — v1.88.0 · 2026-08-17T23:19:13-03:00 · papel-alvo: developer

> Pacote P14 (ADR-012) gerado DETERMINISTICAMENTE do estado do repo por `tools/handoff.py` (ADR-076).
> Teste binario (P14): a proxima sessao comeca SEM perguntar nada de volta?

## [modelo sugerido] (regra papel+risco — ADR-076)
- **Proxima sessao: `claude-opus-4-8`** (opus). Motivo: developer -> tier baseline (opus): papel AUTORAL roda no baseline (= modelo padrao/standard); custo do erro a montante > custo do token (ADR-082). Subagente developer spawnado < baseline = proibido; risco sobrepoe p/ tier max..

## [P14] Artefato consumivel — com versao
- Repo na versao **v1.88.0** (topo do CHANGELOG). Branch `main` @ `d7f0a37`.

## [P14] Localizacao
- origin: https://github.com/fabriciopsouza/metacognition-framework
- branch/commit: `main` @ `d7f0a37` · (sem PR aberto para esta branch)
- raiz absoluta desta copia: `C:\Users\fabriciosouza\metacognition-framework` (paths relativos abaixo ancoram AQUI)

## [P14] Acesso
- Nao-protegido (recovery = conta GitHub): nada pendente (tudo pushado/commitado)

## [P14] Prompt pronto-para-colar
- **Papel:** developer · **Modelo:** `claude-opus-4-8`
- **Objetivo (do 'Proximo passo'):** classificar as 34 capacidades sem o campo `enforcement` pela leitura do que o
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
  1. tools/post_canary_status.py
  2. .github/workflows/ci.yml
  3. tools/test_qa_evidence_integrity.py
  4. CHANGELOG.md
  5. README.md
