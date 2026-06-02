# ADR 048 — Execution-report automático em TODO trabalho (somente no privado)

- Status: **Aceito — implementado e estendido por [ADR-052](052-execution-report-dois-tiers-telemetria-processo-anonimizada.md)** (2026-06-02). O tier OWNER deste ADR foi realizado; o ADR-052 adicionou o tier EXTERNAL (telemetria de processo anonimizada). *(EMENDA de status; a decisão original permanece válida.)*
- Data: 2026-06-01 · Decisores: dono + squad (architect)
- Tipo: futuro (mecanismo de fechamento) — estende ADR-038 (execution_report) e ADR-030 (consistency-gate).
- Origem: dono — "tudo que fizermos deve gerar relatório de execução similar [ao que usamos para melhorar o framework] → **somente no privado**".

## Contexto

Os relatórios de execução (placar gate × achado, interações, erros, limites) foram o insumo que mais
acelerou a melhoria do framework. Hoje o `execution_report.py` (ADR-038) é gerado **sob invocação** no
docops. O dono quer que **todo bloco de trabalho no repo privado** gere automaticamente um relatório
similar — como **comportamento padrão do privado** (não da distribuição pública, que é artefato gerado).

## Decisão proposta (1 frase ativa)

**[PROPOSTA]** Tornar o `execution-report` **automático no fechamento de bloco do repo PRIVADO** —
disparado pelo `docops`/`consistency-gate` ou por um hook de fim-de-sessão — gravando em
`docs/_intake/execution-report-<bloco>.md` (transiente, não distribuído), com o placar gate × achado,
interações, retrabalho e limites; **somente no privado** (o export `STRIP_BEFORE`/`docs/_intake` já não
publica). Mecaniza o que hoje depende de lembrar.

## Alternativas a avaliar (quando implementar)

1. **Hook de SessionEnd/Stop** que gera o report — automático, mas depende de runtime (e do modo non-admin não ter hooks).
2. **Passo obrigatório no docops §Encerramento** (já há a linha; tornar mandatório + gate) — funciona em admin e non-admin (anunciado).
3. **consistency-gate** ganha dimensão "execution-report do bloco presente?" — fail-soft advisory.

## Consequências (esperadas)

**Positivas:** o framework passa a **aprender de cada bloco** sem cobrança; trilha de melhoria contínua.
**A decidir:** onde disparar (hook vs docops vs consistency-gate) considerando o **modo non-admin** (sem
hooks → tem de ser via docops/anunciado); granularidade (por sessão? por release?); retenção. **Limite:**
só no privado (anti-vazamento + o público é artefato gerado).

## Implementação

- **Implementado em 2026-06-02 via [ADR-052](052-execution-report-dois-tiers-telemetria-processo-anonimizada.md).** Gatilho escolhido = **alt 2** (passo mandatório no `docops §Encerramento`, robusto cross-modo, funciona em non-admin sem hooks). O `execution_report.py` ganhou detecção de tier por `docs/_private/`: OWNER grava o report completo em `docs/_private/_intake/` (stripped do export); EXTERNAL grava telemetria de processo codificada em `telemetry/`. Débito declarado → quitado.
