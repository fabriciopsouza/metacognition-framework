# ADR 026 — Relatório de tokens + história compactada por projeto (prosa→mecanismo da observabilidade)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: observabilidade aplicada (pós-v1.21.0) · Tipo: novo (1 script + teste)
- Relaciona: `_shared/observability` (ADR-017, OTel GenAI + 2 métricas), ADR-016 (digest/reconstrução), `tools/project_report.py`.

## Contexto

Companhias e pessoas precisam de **noção de consumo de tokens (médio/total) por projeto** e de uma
**história compactada** das interações (inputs/processamento/saídas) que sirva de base para
**documentação ao final + reconstrução**. O framework já define *o que* logar (observabilidade: tokens,
OTel) e *como* reconstruir (digest, ADR-016) — faltava o **executável** que lê os dados e agrega.

**Viabilidade [CONFIRMADO]:** os transcripts do Claude Code (`~/.claude/projects/<slug>/*.jsonl`) gravam
`input_tokens`, `output_tokens`, `cache_read_input_tokens` por mensagem (verificado: uma sessão somou
~3,1M output tokens, agregável). Logo, dá para gerar o relatório lendo o que já existe — sem instrumentar nada novo.

## Decisão (1 frase ativa)

Adicionar `tools/project_report.py` que **lê os transcripts locais** do Claude Code e emite um relatório
Markdown com **tokens (total + média por sessão)**, **tempo (duração/interação por sessão + total +
throughput tokens/min — proxy de custo p/ corporações)** e **timeline compactada** (por sessão: período,
duração, # mensagens, # tool calls, tokens) — base auditável de documentação/reconstrução — **sem transmitir nada**
(ADR-025) e degradando com segurança se um campo faltar.

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** Consumo de tokens invisível ao dono. **Rejeitada — é o gap.**
2. **Instrumentar OTel completo + dashboard de telemetria.** Prós: rico. Contras: infra cara, "andaime morto"
   (JARVIS — reprovado em P7); a régua §0 e o ADR-017 já limitam telemetria a 2 métricas. **Rejeitada.**
3. **Script que lê os transcripts existentes (ESCOLHIDA).** Prós: lean (zero infra nova), usa dado que já
   existe, sem transmissão. Contras: Claude Code-only; formato do transcript é **interno/version-dependent**
   (mitigado: parse tolerante, degrada para 0 se faltar campo); não copia conteúdo de prompts (privacidade/tamanho).

## Consequências

**Positivas:** visibilidade de custo por projeto; base de documentação + reconstrução (o quê/quanto/quando);
complementa o digest (decisões) e a observabilidade (métricas que mudam decisão).
**Negativas:** restrito ao Claude Code; depende do formato interno do transcript (declarado).
**Riscos:** mudança de formato do transcript quebra a agregação — mitigado por parse tolerante + teste-canário;
re-validar se o Claude Code mudar o schema. [DESCONHECIDO não-bloqueante] estabilidade do schema entre versões.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/project-report` · `2026-05-31` · grep `project_report`
- Artefatos: `tools/project_report.py` (+ `--dir`/`--out`), `tools/test_project_report.py` (canário: agrega
  tokens de um .jsonl sintético + degrada em linha malformada). docops pode invocá-lo no fechamento de bloco
  para anexar o relatório à documentação.
