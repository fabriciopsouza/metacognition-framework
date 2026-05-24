---
name: docops
description: "Ativar ao fim de entrega aprovada pelo qa-critic, antes de fechar o bloco. Nenhum bloco fecha sem documentação proporcional. Dispara compaction/note-taking. Genérico."
version: 1.2.0
source: "SQUAD v1.1.0 (docops) — enxuto"
last_review: 2026-05-23
---

# DocOps — Documentação como Código (genérico)

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
Perguntar: "Salvar como Knowledge Item?"
