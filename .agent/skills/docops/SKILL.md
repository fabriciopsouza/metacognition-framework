---
name: docops
description: "Ativar ao fim de entrega aprovada pelo qa-critic, antes de fechar o bloco. Nenhum bloco fecha sem documentação proporcional. Dispara compaction/note-taking. Flexível."
version: 1.2.0
source: "SQUAD v1.1.0 (docops) — enxuto"
last_review: 2026-05-23
role_order: 5
consumes:
  - "entrega aprovada (APROVADO_LIMPO) pelo qa-critic"
produces:
  - "CHANGELOG + ADR Aceito + docs sincronizadas"
pass_criteria: "PASS sse CHANGELOG atualizado, ADR marcado Aceito com ponteiro, e specs/docs em sync (sem drift) — bloco não fecha sem doc proporcional."
confidence_required: false
shared_refs:
  - _shared/metacognition-core
  - _shared/traceability
---

# DocOps — Documentação como Código (flexível)

## Carregar de `_shared/`
`metacognition-core` (compaction + structured note-taking) · `traceability`.

## Sequência
1. CHANGELOG.md (Keep a Changelog + SemVer).
2. dicionario-de-dados.md (se campo/cálculo novo).
3. 00-glossario.md (se nome novo via ADR).
4. README.md (se mudou setup).
5. ADR → "Aceito" + hash.
6. Sincronizar a spec se decisões mudaram (anti-drift).

## Encerramento
Sem CHANGELOG + dicionário (se aplicável) + ADR aceito (se havia) → não fecha.
Rodar o **consistency-gate** (ADR-030) antes de fechar release:
`powershell -NoProfile -ExecutionPolicy Bypass -File tools/hooks/consistency-gate.ps1`
— version-sync, ADR-status, checkpoint no history, unpushed, transientes, **execution-report presente** (7ª dim, ADR-062).
Tratar as inconsistências (ou registrá-las como débito declarado) antes do PR de release.
Gerar o **execution-report** (ADR-038/052/062) do bloco **e ao fim de sessão** — auto, não sob cobrança:
`python tools/execution_report.py --from-transcripts`
— o tier é **detectado automaticamente** (ADR-052): no repo-fonte (`docs/_private/` existe) grava o
relatório **completo** em `docs/_private/_intake/execution-report.md` (não distribuído); numa
distribuição grava **só sinais de processo codificados** em `telemetry/telemetry-report.md` (whitelist
anti-vazamento + opt-out `.claude/no-telemetry.lock`/`FRAMEWORK_NO_TELEMETRY`; ver `TELEMETRY.md`).
Conteúdo: tokens (NÃO MEDIDO se a telemetria não estiver exposta — **nunca fabricar**), tempo, turnos,
arquivos, testes, rodadas de retrabalho, o **placar gate × achado** ("quem pegou o quê") e — **ADR-062** —
**detecção framework×humano, gaps, melhorias, boas práticas e lições por skill** (agnóstico de domínio).
**Corpus público — oferta POR SOLUÇÃO no merge (ADR-062/063/064/065):** ao **mergear um PR da solução**
(ou no boot se a solução está mergeada e ofertável), cheque `python tools/execution_report.py --offer-state`;
se `ofertar=SIM` (estado `pending`/`deferred`), apresente o **popup** (`AskUserQuestion`) com a tabela
**vai / NÃO-vai** + 4 opções e aja: **✅ gerar+contribuir** → `--publish` (anonimiza fail-closed → PR
central → auto-merge) + `--set-offer done`; **📄 só local** → `--publish` sem gh + `--set-offer done`;
**⏳ ainda não** → `--set-offer deferred` (re-oferta no próximo merge); **🚫 não p/ esta solução** →
`--set-offer declined`. O popup É a disclosure+consentimento por-solução (conformidade/privacidade detalhada em
`docs/REPORTS-CONTRIBUTION.md`); 1× por solução (estado em `.claude/.report-offers/`). Sem
opt-in/`gh` → fail-soft (gera local ou nem oferta).
**Fail-soft:** sem `gh`/opt-in → gera local e NÃO publica (nunca trava). Opt-in é 1× (bootstrap ou
`--init-consent`); setup do dono é 1 comando guiado (`python tools/setup_central_reports.py`). Ver
`docs/REPORTS-CONTRIBUTION.md`.
Registrar a **decisão de re-orquestração do PMO** (J6, ADR-045) no `history.md`:
`RE-ORQUESTRAÇÃO: <prosseguir | re-priorizar | rewind J_i | injetar escopo | reativar estágio>`
e rodar `python tools/check_reorchestration.py` (último bloco fechado deve ter a decisão).
Perguntar: "Salvar como Knowledge Item?"
