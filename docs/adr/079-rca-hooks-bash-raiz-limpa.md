# ADR 079 — RCA do wiring de hooks: harness executa via bash (wrapper `cmd /c` quebrava TUDO) + guard de raiz-limpa

- Status: **Aceito** (2026-06-11 — gate: qa-critic adversarial Sonnet isolado, 2 rounds J4: R1 `corrigir` [ALTO regressão test_nonadmin pega pelo gate + 2 BAIXO] → fixes → R2 aprovativo; suíte local verde; validação AO VIVO dos hooks na própria sessão) · Data: 2026-06-11 · Decisores: dono + squad
- Onda: F4 do plano de melhoria (P10 + guard prometido no method-audit dos espúrios) · Tipo: **correção de infra** (emenda à §Implementação do ADR-060 — padrão de wiring muda; o porte Python em si permanece).
- Relaciona: ADR-060/061 (porte Python + liveness — o "gate inerte" atribuído ao EDR era, ao menos nesta máquina, **wiring quebrado**), ADR-030/077 (consistency — ganha a dim raiz-limpa).

## Contexto

Três sintomas crônicos com a mesma causa, descoberta em sessão: (1) banners de cmd interativo no boot (5×, um por hook `cmd /c`); (2) liveness ADR-061 acusando gates "não rodaram" mesmo com hooks wirados; (3) **arquivos vazios espúrios na raiz** (~33 em 4 ondas nesta sessão; 8+13 chegaram a commits e foram removidos via amend) com nomes = palavras de payloads de tool-calls. **RCA [CONFIRMADO pelo formato do banner + erro revelador]:** o harness (Claude Code neste ambiente) executa hooks via **`/usr/bin/bash`**, não cmd. O wrapper próprio `cmd /c "python tools\hooks\x.py …"`: o bash come as barras invertidas fora de aspas (`toolshooksx.py`) e quebra o aninhamento de aspas → o cmd interno caía em **modo interativo lendo o stdin (JSON do hook) como comandos digitados** — os `\"` do JSON alternam o estado de aspas do cmd e um `->` solto vira redirect, criando o arquivo espúrio. Efeito mais grave: **o python dos hooks não executava** — effect-gate, mission-gate, overwrite-guard, compaction-gate etc. estavam mortos por wiring.

## Decisão (1 frase ativa)

Reescrever os 12 comandos de hook do `.claude/settings.json` para a forma **bash-correta** — `python tools/hooks/xxx.py` (barras normais), fallback `|| powershell.exe … -File "caminho/aspeado.ps1"` (o `||` é válido em bash; paths aspeados preservam o que precisar de `\`), e `|| true` no lugar do cmd-ism `exit /b 0` — **e** adicionar ao `test_consistency_closing.py` a dim **raiz-limpa**: arquivo **rastreado** na raiz com 0 bytes e sem extensão = destroço de shell → **FAIL** (não existe arquivo legítimo nesse formato); arquivos não-rastreados nesse formato → advisory.

## Alternativas consideradas

1. **Manter `cmd /c` e investigar caso a caso.** O wrapper é a causa; manter = continuar com gates mortos e contaminação. **Rejeitada.**
2. **Wrapper PowerShell.** `||` não existe em PS 5.1; voltaria ao problema de sintaxe por shell. **Rejeitada.**
3. **Detectar o shell do harness em runtime.** Complexidade sem ganho: a forma bash funciona no shell observado e, se o harness um dia usar cmd, `python a/b/c.py` roda igual (barras normais são válidas no Windows). **Rejeitada.**
4. **Forma bash direta + guard de raiz-limpa (ESCOLHIDA).** Validada ao vivo na própria sessão (hooks python passaram a executar; o guard pegou 13 destroços no primeiro disparo, dentro do próprio commit que o introduziu).

## Consequências

**Positivas:** os gates de runtime executam **de fato** (possivelmente pela primeira vez nesta máquina); fim da contaminação por payload; o liveness ADR-061 passa a refletir EDR real, não wiring; contaminação residual commitada agora é fail-closed na suíte/CI. **Negativas/limite (declarado):** o diagnóstico "harness = bash" é desta instalação [CONFIRMADO aqui; outras instalações podem variar — a forma escolhida é a mais portátil]; a janela pré-fix deixou sessões antigas com hooks mortos — comportamento histórico atribuído a "EDR vetou" deve ser relido com ceticismo (memória corrigida); `exit /b 0`→`|| true` preserva a semântica fail-open original.

## Implementação (ponteiro)

`.claude/settings.json` (12 comandos) · `tools/test_consistency_closing.py` (dim raiz-limpa fail-closed + advisory untracked) · memória do agente corrigida (RCA real ≠ atribuição inicial a bash de subagente) · EMENDA ADR-060 §Implementação (padrão de wiring: sem wrapper próprio).
