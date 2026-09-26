# Handoff — v1.91.0 · 2026-09-26T19:28:59-03:00 · papel-alvo: developer

> Pacote P14 (ADR-012) gerado DETERMINISTICAMENTE do estado do repo por `tools/handoff.py` (ADR-076).
> Teste binario (P14): a proxima sessao comeca SEM perguntar nada de volta?

## [modelo sugerido] (regra papel+risco — ADR-076)
- **Proxima sessao: `claude-opus-5`** (opus). Motivo: developer -> tier baseline (opus): papel AUTORAL roda no baseline (= modelo padrao/standard); custo do erro a montante > custo do token (ADR-082). Subagente developer spawnado < baseline = proibido; risco sobrepoe p/ tier max. POSICAO IMPORTA E E' DELIBERADA (ADR-110, achado ALTA do QA de juncao 19/08/2026): esta regra tem de vir ANTES da regra `docops`/economy. A ordem de `roles` E' a precedencia do casador — seguranca (qa/critic) > autoral > mecanico — e com a mecanica na frente, um papel composto como 'developer docops' resolvia para HAIKU, dois degraus abaixo do default. O canario testa o PRODUTO CARTESIANO chave-autoral x chave-mecanica, nao um exemplo: exemplo que passa nao prova classe..

## [P14] Artefato consumivel — com versao
- Repo na versao **v1.91.0** (topo do CHANGELOG). Branch `docs/ritos-2026-09-26-framework` @ `5cc80ce`.

## [P14] Localizacao
- origin: https://github.com/fabriciopsouza/metacognition-framework
- branch/commit: `docs/ritos-2026-09-26-framework` @ `5cc80ce` · (sem PR aberto para esta branch)
- raiz absoluta desta copia: `C:\Users\fabriciosouza\wt-ritos` (paths relativos abaixo ancoram AQUI)

## [P14] Acesso
- Nao-protegido (recovery = conta GitHub): 2 arquivo(s) nao-commitado(s)

## [P14] Prompt pronto-para-colar
- **Papel:** developer · **Modelo:** `claude-opus-5`
- **Objetivo (do 'Proximo passo'):** B3a-2, planilhas de confirmação e de verificação. Depende das decisões 1 a 3 do dono sobre a
- **Produz/decide:** execute o objetivo acima ate o criterio de aceite citado; rode `tools/run_canaries.py` antes de fechar.

## [P14] Pendencias e premissas herdadas
- (em aberto) **Pedido novo chegando no meio do trabalho deve ir para uma FILA ESCRITA, nao para a memoria do
- (em aberto) **REFORÇADO PELO DONO EM 21/08/2026, terceira vez:** *"este deve ser o comportamento em TODOS
- (em aberto) **PRIORIDADE MÁXIMA DO PRÓXIMO BLOCO — o squad e a crítica adversarial não são determinísticos
- (em aberto) **Quitação do override da régua §0 do ADR-102** (aberto em 13/08/2026): o padrão documental
- (em aberto) **[2026-08-07] Débitos de fechamento do bloco v1.77.0 — 3 achados, NADA aplicado.** Handoff completo (com comando de re-validação e predicado "aplicar SÓ SE" po
- (em aberto) **ADR-097 itens 4 e 5 do §Mecanismo** (aberto em 16/08/2026, ao aceitar o ADR): a camada-mestra

## Extensoes (ADR-016 — evita re-derivar)
- **5 arquivos mais recentes:**
  1. .agent/workflows/start-session.md
  2. CAPABILITIES.md
  3. CHANGELOG.md
  4. CLAUDE.md
  5. _meta/qa/b3d-metodo-e-processo.json
