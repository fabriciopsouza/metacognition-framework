# ADR 021 — Gate de compaction via hook PreCompact (prosa→mecanismo do ADR-016)

- Status: Aceito (qa-critic Sonnet isolado: R1 REPROVADO → fixes → R2 APROVADO, ADR-011/018)
- Data: 2026-05-30 · Decisores: dono + squad (architect)
- Onda: runtime-hooks (v1.21.0) · Pesquisa: **P2** (espelhada na SPEC Perplexity §5.4) · Tipo: **EMENDA** (liga ADR-016/Princípio 8)
- Relaciona: ADR-016 (faixas+digest), `.agent/workflows/checkpoint.md`, `_shared/metacognition-core` §Pacote (P14), ADR-015 (filosofia de hook conservador).

## Contexto

O ADR-016 decidiu "compaction por faixas medidas + **digest obrigatório** antes do reset". A obrigatoriedade é **prosa**: depende de o agente lembrar de rodar `/checkpoint` antes da janela compactar. Se a compaction (auto ~85% no IDE, ou manual) dispara sem digest, o WIP/decisões não-persistidos somem — exatamente o dano que o ADR-016 quer evitar. A pesquisa Perplexity re-derivou isto (`pre_compact.py` §5.4). O hook **PreCompact** do Claude Code **pode bloquear** a compaction via `{"decision":"block","reason":...}` ou exit 2 — [CONFIRMADO] (code.claude.com/docs/en/hooks; verificado 2026-05-30). Régua §0(c): destrava uma garantia que a prosa não dá.

**Divergência deliberada da SPEC Perplexity:** o `pre_compact.py` dela bloqueia se um `DIGEST.md` de path/seções fixas estiver vazio/incompleto. Nosso modelo de memória **não** é um arquivo único fixo — é `history.md` (append-only: `## Em aberto` = WIP + checkpoints) + digest por-bloco clonado de `_template-digest`. Copiar o hook dela hardcodaria um modelo que não temos e arriscaria **deadlock** (bloquear toda compaction se o agente não conseguir escrever no momento).

## Decisão (1 frase ativa)

Adicionar `tools/hooks/compaction-gate.ps1` (+ `.sh`) como hook **PreCompact backstop conservador** que **bloqueia apenas o caso catastrófico inequívoco** — `history.md` ausente ou sem nenhum checkpoint (= "nada foi persistido nesta sessão") — e, fora disso, **emite lembrete não-bloqueante** (stderr/contexto) para rodar `/checkpoint` se o checkpoint mais recente parecer defasado; **default-allow**, **fail-open** em erro interno (mesma filosofia do `effect-gate`, ADR-015), reusando `history.md` sem criar arquivo de estado novo (régua §0).

## Alternativas consideradas (≥3)

1. **Manter prosa (status quo — "não fazer").** Prós: zero código. Contras: a obrigatoriedade do digest segue sem enforcement; compaction pode destruir WIP não-salvo. É o gap. **Rejeitada.**
2. **Bloqueio forte estilo SPEC Perplexity** (exigir `DIGEST.md` com N seções nomeadas; block se vazio/incompleto). Prós: garantia máxima. Contras: assume modelo de arquivo único que não temos; força seções hardcoded (frágil/stale — lição dos stale counts); **risco de deadlock**. **Rejeitada como default** (incorporada parcialmente como backstop).
3. **Breadcrumb de sessão** (SessionStart grava marker timestamp; `/checkpoint` atualiza; PreCompact compara freshness e bloqueia se stale). Prós: detecta digest **realmente** defasado. Contras: adiciona máquina de estado (custo régua §0); só justifica sob gatilho real. **Rejeitada agora; documentada como evolução futura.**
4. **Backstop conservador reusando `history.md` (ESCOLHIDA).** Prós: lean (zero arquivo novo), consistente com `effect-gate`, fail-open (hook bugado não vira DoS de compaction). Contras: **não verifica freshness de forma stateless** — só pega o caso "nada persistido", não "persistido mas velho". **Limitação declarada (Princípio 11 honesto)**, mitigada pelo lembrete não-bloqueante.

## Consequências

**Positivas:** o caso catastrófico (compactar sem nada salvo) vira impossível mecanicamente; lembrete no momento exato da compaction; reusa artefato existente.
**Negativas:** não substitui a disciplina de `/checkpoint` para garantir digest *atual* (declarado); cobertura é backstop, não prova de completude.
**Riscos:** (a) falso-bloqueio se `history.md` existir mas o parser não achar checkpoint — mitigado por fail-open + regex tolerante. (b) freshness não verificável stateless — [DESCONHECIDO não-bloqueante]; alternativa 3 resolve se recorrer. (c) PreCompact matcher/contrato pode variar entre versões do Claude Code — fail-open protege.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.21.0-runtime-hooks-web` · `2026-05-30` · grep `compaction-gate|PreCompact`
- Artefatos: `tools/hooks/compaction-gate.ps1` + `.sh`; wiring em `.claude/settings.json` (`hooks.PreCompact`) e nota de instalação em `managed-settings.template.json`; teste `tools/test_compaction_gate.py`.
- Contrato PreCompact: lê JSON do stdin (`trigger`: auto|manual); para bloquear → stdout `{"decision":"block","reason":...}` (exit 0); allow → exit 0 sem decision. Erro → stderr + exit 0 (fail-open).
