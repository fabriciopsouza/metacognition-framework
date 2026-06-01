# ADR 038 — execution-report automático + telemetria honesta (estende ADR-026)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: remediação v2 (marco v1.27.0) · Tipo: **EMENDA** (estende `project_report.py`/ADR-026) — net-gain por destravar aprendizado de processo inalcançável.
- Origem no plano: item 6 ⭐ (`[campo]` meta-gap nº1: tokens/custo/tempo NÃO MEDIDOS; placar "quem pegou o quê" só existiu porque o dono cobrou). Relaciona: ADR-026 (project_report), ADR-030 (consistency-gate), docops §Encerramento.

## Contexto

Sem trilha de consumo por sessão não há **accountability** (crítico em regulado), **controle de custo**
(os retrabalhos teriam custo acionável), nem **aprendizado de processo** (cada lição dependeu de o dono
cobrar). O `project_report.py` (ADR-026) já lê tokens/tempo dos transcripts, mas faltava (a) o **placar
gate × achado** e as rodadas de retrabalho, e (b) a geração **automática** no encerramento.

## Decisão (1 frase ativa)

Criar `tools/execution_report.py` (estende ADR-026): gera, no encerramento de bloco, um relatório com
tokens (via transcripts quando disponíveis; senão literalmente **"NÃO MEDIDO"** — **nunca fabricado**),
tempo, turnos, arquivos, testes, **rodadas de retrabalho** e o **placar gate × achado**; com
`validate_report()` que reprova report ausente, sem placar, ou com **número de token sem fonte declarada**
(anti-fabricação) — wirado no `docops` §Encerramento.

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** O framework não aprende com a própria execução; placar depende do dono. **Rejeitada — é o gap.**
2. **Fabricar/estimar tokens quando a telemetria falta.** Viola anti-fabricação (P1). **Rejeitada** — "NÃO MEDIDO" é a única saída honesta sem fonte.
3. **Novo subsistema de telemetria paralelo ao ADR-026.** Duplicaria leitura de transcripts (régua §0). **Rejeitada** — estende `project_report.py`.
4. **execution-report que estende ADR-026 + invariante anti-fabricação validada (ESCOLHIDA).** Prós: reusa a leitura de tokens, adiciona o placar/retrabalho, e mecaniza a recusa de fabricar. Contras: expor telemetria de token ao agente **em tempo real** é dependência do host (não-mecanizável pelo framework) → `LIMITS.md`.

## Consequências

**Positivas:** todo encerramento ganha relatório auto-gerado + placar; "token fabricado" vira FAIL de
validação; accountability/custo/aprendizado deixam de depender de cobrança. **Negativas:** o report é tão
rico quanto a fonte disponível (transcripts) — sem telemetria real-time, tokens ficam "NÃO MEDIDO".
**Riscos/limite declarado:** telemetria de token exposta ao agente é pré-requisito de governança e
**dependência externa** → `LIMITS.md` ("mecanizado: report + placar + anti-fabricação; não-mecanizado:
telemetria real-time — depende do host").

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.23-v1.31-remediacao` · `2026-05-31` · grep `execution_report`
- Artefatos: `tools/execution_report.py`, `tools/test_execution_report.py` (5 casos), wiring no
  `docops/SKILL.md` §Encerramento. DONE quando: report auto-gerado em todo encerramento de bloco. [CONFIRMADO]
