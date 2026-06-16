# ADR 082 — Baseline de autor relativo/evolutivo + gate de tier da sessão (emenda ADR-078)

- Status: **Aceito** (2026-06-16 — gate: process-critic heterogêneo Opus 4.8; nasceu de falha de campo no v1.59.0) · Data: 2026-06-16 · Decisores: dono (diretriz explícita) + squad
- Onda: incidente v1.59.0 — autor Sonnet por omissão da política auto-aprovou gate vermelho · Tipo: **emenda ADR-078** (fecha a cegueira do modelo-autor da sessão) + correção de omissão (papel `developer` ausente das roles)
- Relaciona: ADR-078 (model-policy fonte única — esta ADR adiciona o eixo AUTOR), ADR-018/011 (heterogeneidade anti-viés), ADR-061 (boot_check — host do novo gate)

## Contexto

No bloco v1.59.0 (integração BMAD), a sessão rodou inteira em **Sonnet 4.6** como autor, e o próprio Sonnet rodou seu qa-critic (mesmo modelo) e declarou "APROVADO_LIMPO / 50 PASS" enquanto os canários estavam **VERMELHOS** (artefato qa com `release="v1.59.0"` vs gate que compara `"1.59.0"`). Só foi pego quando o dono **trocou manualmente para Opus 4.8**.

Pergunta do dono: *"o framework não era todo determinístico? por que mudou para Sonnet e ficou nele?"*

**Diagnóstico (causa-raiz):** o determinismo do `model-policy.json` (ADR-078) cobre **um caminho só — qual modelo o orquestrador escolhe ao SPAWNAR um subagente**. O modelo da **sessão principal** (o autor interativo) é definido pelo **harness / comando `/model`**, FORA do alcance do framework. E:
1. o papel `developer` **nem estava na lista `roles`** → caía no `default_tier: balanced` (= Sonnet). A política, por omissão, **normalizava Sonnet como autor**.
2. nenhum gate jamais comparava o **modelo-autor da sessão** com um baseline.

Resultado: Sonnet entrou por config de sessão, virou autor por omissão, auto-aprovou — silencioso de ponta a ponta. O oposto de "declarar, não fingir".

## Decisão (1 frase ativa)

Adicionar ao `model-policy.json` o bloco **`baseline_author`** (RELATIVO e evolutivo: `model` = o modelo PADRÃO/standard atual — hoje `opus`, não `fable` que é preview/situacional) + o tier **`baseline`** + o papel **`developer`/autoral → tier baseline**, estabelecendo a regra **autor roda ≥ baseline; crítico/QA e docops-mecânico rodam ABAIXO do baseline**; e adicionar em `boot_check.py` o gate **`check_author_tier`** que detecta o modelo-autor da sessão (via `--author-model`/env, nunca probe de rede) e emite **banner LOUD** quando autor < baseline com baseline disponível — exigindo `/model <baseline>` ou declaração de indisponibilidade. Quando `fable`/`mythos`/+ virar o default/standard, **promove-se `baseline_author.model`** (editar DADO) e `opus`/`sonnet` descem automaticamente para crítico/docops.

## Alternativas consideradas

1. **Só nota de Aprendizado.** Prosa inerte — repetiria no próximo boot em Sonnet. **Rejeitada** (framework = prosa→mecanismo).
2. **Hardcode "autor deve ser Opus".** Quebra na próxima geração (Fable/Mythos vira standard). **Rejeitada** — a regra é relativa ao baseline declarado no dado.
3. **Framework troca o modelo da sessão automaticamente.** Não é possível: o modelo interativo é do harness. **Rejeitada por limite real** — mitigação = detectar + anunciar LOUD + exigir troca.
4. **Baseline relativo no dado + gate LOUD de boot + developer nas roles (ESCOLHIDA).** Determinismo preservado (entrada = dado + arg/env); evolui editando dado; a não-determinância do modelo-sessão deixa de ser silenciosa.

## Consequências

**Positivas:** o modelo-autor da sessão deixa de ser ponto cego — autor sub-baseline vira banner LOUD no boot (teste de campo: `--author-model sonnet` → "TROQUE /model opus"; `opus` → ✅); `developer`/autoral resolve ao baseline no dispatch de subagente (era `balanced`=Sonnet); a regra é relativa — sobe sozinha quando o standard sobe, sem tocar código; crítico/docops abaixo do baseline = heterogeneidade barata por construção. **Negativas/limite (declarado):** o gate é **fail-soft** (anuncia, não trava — `boot_check` nunca pode travar o boot) e **não troca** o modelo da sessão (limite do harness, mesma classe do ADR-078); a detecção do modelo-autor depende de `--author-model`/env (sem isso → status "warn: declare", ainda LOUD, nunca falso-OK); `baseline_author.model` é atualização manual por designação humana do "standard atual" (deliberado — preview ≠ standard).

## Mecanismo em 3 camadas (checar + alertar + trocar — pedido do dono 2026-06-16)

1. **CHECAR (auto, sem cooperação do agente):** `boot_check.detect_session_model()` lê o **modelo ATIVO do transcript JSONL** da sessão (último turn assistant; path derivado de `CLAUDE_CODE_SESSION_ID`). Determinístico (arquivo local, nunca probe de rede). Teste de campo: detectou `claude-opus-4-8` sozinho.
2. **ALERTAR (auto, a cada turno):** hook `UserPromptSubmit` `tools/hooks/check_author_tier.py` — lê o transcript, e se autor < baseline emite **banner LOUD** (`additionalContext`). Onde Kaspersky/EDR veta hook → inerte; o boot_check (camada 1, manual EDR-proof) cobre no boot. Teste: transcript Sonnet → banner; Opus → silêncio.
3. **TROCAR (auto, para NOVAS sessões):** `.claude/settings.json` `"model": "opus"` (= baseline) → toda nova sessão **lança no baseline**. Manter em sync com `baseline_author.model`; o gate alerta se houver drift.

**Limite honesto (declarado):** nenhuma camada **força a troca de uma sessão JÁ rodando** — o `/model` interativo é do harness. O framework detecta + alerta LOUD + lança novas sessões no baseline. Forçar mid-session exigiria recurso do harness (mesma classe do limite do ADR-078).

## Implementação (ponteiro)

- `tools/model-policy.json`: bloco `baseline_author` + tier `baseline` (chain opus→sonnet→haiku) + role `developer`→`baseline`.
- `tools/boot_check.py`: `detect_session_model()` (auto via transcript) + `check_author_tier()` no `CHECKS` (arg/env/auto-detect; ordem de capacidade data-driven max→balanced→economy).
- `tools/hooks/check_author_tier.py`: hook UserPromptSubmit (alerta per-turn) — registrado em `.claude/settings.json`.
- `.claude/settings.json`: `"model": "opus"` (lança novas sessões no baseline) + hook acima.
- `tools/test_handoff.py`: schema de `baseline_author` (b3.1) + `developer` (autoral) resolve ao baseline + caso `developer,low,opus→opus`.
- `.agent/workflows/start-session.md`: passo de boot roda `boot_check.py --author-model <modelo-da-sessao>` (o agente conhece o próprio modelo; o boot_check também auto-detecta do transcript).
- `capabilities.json`: `author-tier-gate` (+1; enforcement=fail-soft, declarado).
