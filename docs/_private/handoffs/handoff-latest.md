# Handoff — v1.87.0 · 2026-08-17T08:33:37-03:00 · papel-alvo: developer

> Pacote P14 (ADR-012) gerado DETERMINISTICAMENTE do estado do repo por `tools/handoff.py` (ADR-076).
> Teste binario (P14): a proxima sessao comeca SEM perguntar nada de volta?

## [modelo sugerido] (regra papel+risco — ADR-076)
- **Proxima sessao: `claude-opus-4-8`** (opus). Motivo: developer -> tier baseline (opus): papel AUTORAL roda no baseline (= modelo padrao/standard); custo do erro a montante > custo do token (ADR-082). Subagente developer spawnado < baseline = proibido; risco sobrepoe p/ tier max..

## [P14] Artefato consumivel — com versao
- Repo na versao **v1.87.0** (topo do CHANGELOG). Branch `feat/alarme-de-deriva-das-sombras` @ `3b7cef3`.

## [P14] Localizacao
- origin: https://github.com/fabriciopsouza/metacognition-framework
- branch/commit: `feat/alarme-de-deriva-das-sombras` @ `3b7cef3` · (sem PR aberto para esta branch)
- raiz absoluta desta copia: `C:\Users\fabriciosouza\metacognition-framework` (paths relativos abaixo ancoram AQUI)

## [P14] Acesso
- Nao-protegido (recovery = conta GitHub): estado de push DESCONHECIDO (branch sem upstream — pode haver commits locais nao protegidos), 18 arquivo(s) nao-commitado(s)

## [P14] Prompt pronto-para-colar
- **Papel:** developer · **Modelo:** `claude-opus-4-8`
- **Objetivo (do 'Proximo passo'):** o passivo — dezessete capacidades que declaram bloquear falha e nunca foram
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
  1. CHANGELOG.md
  2. PROMPT-CHAT-WEB-v4.5.md
  3. README.md
  4. _meta/qa/release-1.86.0-vitrine-com-numeros-verificados.json
  5. _meta/qa/release-1.86.0-vitrine-com-numeros-verificados.md
