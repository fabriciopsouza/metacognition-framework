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
— version-sync, ADR-status, checkpoint no history, unpushed, transientes em `docs/_intake/`.
Tratar as inconsistências (ou registrá-las como débito declarado) antes do PR de release.
Gerar o **execution-report** (ADR-038) do bloco — auto, não sob cobrança:
`python tools/execution_report.py --from-transcripts --out docs/_intake/execution-report.md`
— tokens (NÃO MEDIDO se a telemetria não estiver exposta — **nunca fabricar**), tempo, turnos,
arquivos, testes, rodadas de retrabalho e o **placar gate × achado** ("quem pegou o quê").
Registrar a **decisão de re-orquestração do PMO** (J6, ADR-045) no `history.md`:
`RE-ORQUESTRAÇÃO: <prosseguir | re-priorizar | rewind J_i | injetar escopo | reativar estágio>`
e rodar `python tools/check_reorchestration.py` (último bloco fechado deve ter a decisão).
Perguntar: "Salvar como Knowledge Item?"
