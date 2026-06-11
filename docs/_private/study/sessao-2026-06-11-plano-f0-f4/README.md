# Estudo — Sessão 2026-06-11: avaliação do framework → plano F0–F4 → 4 releases mergeados

> **Privado (não distribuído):** vive em `docs/_private/` — `export-clean.py` (STRIP_BEFORE, linha 26)
> remove este cofre de TODA distribuição. Estudos NÃO vão para shadows (regra do dono, 2026-06-11).

**Transcript bruto:** `transcript-a4262039.jsonl` (snapshot ~19:35, sessão ainda ativa ao copiar; formato
JSONL do Claude Code — cada linha um evento: user/assistant/tool_use/tool_result).
**Sessão anterior relacionada:** `319dfbe7…` (port dos hooks, origem do caso v1.55.0).
**Modelos:** orquestrador Claude Fable 5 · qa-critics Sonnet 4.6 isolados (6 spawns).

## A jornada em 6 atos (mapa para leitura do transcript)

1. **Avaliação** — pedido aberto do dono → auditoria read-only do framework inteiro → relatório com
   12 propostas (P1–P12) e plano F0–F4: `docs/_private/reports/avaliacao-processo-framework-2026-06-11.md`.
   Achado-âncora: bloco v1.55.0 mergeado sem fechamento **sem nenhum gate disparar** (malha ancorada no
   evento "versão no CHANGELOG").
2. **F0 (v1.55.0, PR #78)** — fechamento retroativo + qa-evidence retroativo + **deadlock real da suíte**
   descoberto e corrigido (tty-guard × stdin herdado).
3. **F1 (v1.56.0, PR #79, ADR-077)** — version-claim fail-closed + override de CI + **junction-ledger**
   (J0–J3 deixam rastro) + validation.md em J3.
4. **F2 (v1.57.0, PR #80, ADR-078)** — model-policy.json fonte única + escada de heterogeneidade +
   fallback de indisponibilidade (pergunta do dono em sessão, incorporada ao vivo).
5. **F3+F4 (v1.58.0, PR #81, ADR-079/080)** — **RCA dos hooks** (harness=bash; wrapper `cmd /c` matava
   os gates e criava os arquivos espúrios) + dieta de contexto (CLAUDE.md −61%) + rule #11 + cadência de poda.
6. **Merge da pilha** — #78→#79→#80→#81 com OVERRIDE declarado (CI billing) + tags v1.55.0–v1.58.0.

## Momentos didáticos (vale buscar no transcript)

- **O gate pegando o autor (3×):** R1 do F3+F4 pegou regressão real da dieta (`test_nonadmin`); R2 flagrou
  fix declarado-mas-não-efetivado (anti-false-PASS contra o próprio orquestrador); R1 do F2 pegou lixo
  commitado. Evidências: `_meta/qa/v1.5{5,6,7,8}*.{json,md}` + ledger `_meta/qa/junctions/`.
- **`git reset --hard` apagando trabalho não-commitado** do próprio agente (prova negativa do P1) —
  origem da disciplina "WIP commit antes de operação destrutiva" (method-audit no history).
- **RCA dos espúrios em 3 hipóteses sucessivas** (subagente bash → cmd interativo → harness bash):
  exemplo de atribuição inicial ERRADA corrigida por evidência (banner reproduzido + erro revelando
  `/usr/bin/bash`); memória corrigida em vez de empilhada.
- **Catch-22 dos hooks quebrados no meio do fix** (Read/Edit/Bash todos bloqueados) e o escape via
  **arquivos-shim** com os nomes que o bash produzia ao comer as barras.
- **Determinismo contra sondagem:** indisponibilidade de modelo DECLARADA (env), nunca sondada na API.

## Artefatos permanentes da sessão

| Artefato | Onde |
|---|---|
| Relatório de avaliação (12 propostas) | `docs/_private/reports/avaliacao-processo-framework-2026-06-11.md` |
| ADRs do plano | `docs/adr/077…080-*.md` (+ EMENDAs em 060/076) |
| Vereditos qa-critic + postura | `_meta/qa/v1.55.0…v1.58.0*.{json,md}` |
| Ledger de junções (dogfood ADR-077) | `_meta/qa/junctions/*.jsonl` |
| Checkpoints + RRC + OVERRIDE + method-audits | `history.md` (entradas 2026-06-11) |
| Execution-report (telemetria) | `docs/_private/_intake/execution-report.md` |
| CHANGELOG das 4 releases | `CHANGELOG.md` §[1.55.0]–[1.58.0] |
