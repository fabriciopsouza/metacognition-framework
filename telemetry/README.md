# telemetry/ — zona de pouso da telemetria de processo (ADR-052)

Esta pasta recebe **relatórios de processo anonimizados e estruturados** gerados pelo
`tools/execution_report.py` no tier EXTERNAL (qualquer distribuição do framework).

## Para quem usa o framework (tier external)

- Ao fechar um bloco, pode surgir aqui um `telemetry-report.md` com **apenas sinais de processo
  codificados** (gates, pontos de falha, correções) — **sem conteúdo de domínio, sem texto livre,
  sem dado pessoal**. Veja [`../TELEMETRY.md`](../TELEMETRY.md).
- **Nada é enviado automaticamente.** Para contribuir com a melhoria do framework, faça commit do
  arquivo e abra um **PR** para `github.com/fabriciopsouza/metacognition-framework`.
  **O PR é o seu consentimento** (você revê o arquivo, que é legível, antes de enviar).
- Não quer nem gerar? `.claude/no-telemetry.lock` ou `FRAMEWORK_NO_TELEMETRY=1`.

## Para o mantenedor (no repo master)

PRs de telemetria pousam aqui. Cada arquivo é validável por whitelist:
`python tools/execution_report.py --validate telemetry/<arquivo>.md` (PASS = só sinais codificados).
Agregue os `failure_points`/`correction_events` para priorizar conserto de gates/regras.

> No **repo-fonte do mantenedor** o tier é OWNER (não external): o relatório completo do dono vai para
> `docs/_private/_intake/` (não distribuído), não para cá. Esta pasta é para os PRs de terceiros.
