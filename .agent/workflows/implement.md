# /implement <tarefa> — Implementação supervisionada (v1.2)

## Pré-requisito
ADR aceito + `docs/specs/<feature>/validation.md` com critérios binários
OU tarefa trivial confirmada pelo usuário.

## Roteamento por confiança (NOVO — `rules/04`)
- **Alta confiança operacional** → pipeline linear (abaixo).
- **Baixa confiança / regulado / irreversível** → QA-Critic adversarial
  **obrigatório** + hand-off **bloqueado** até revisão humana sobre diffs.

## Pipeline
PMO → Developer → QA-Critic → [correção] → DocOps

- **PMO:** confirmar ADR + `validation.md`; rotear por confiança; `/handoff developer`.
- **Developer:** checklist file-first + glossário-first + ADR-first; implementar
  contra os critérios da spec; apresentar diff.
- **QA-Critic** (modelo diferente; ver `_meta/subagent-isolation.md`):
  validar **contra `validation.md`** (cada critério VERDADEIRO/FALSO) +
  checklist de `_shared/output-format`. Emitir JSON: aprovar | aprovar_com_ressalvas
  | corrigir | reverter. Qualquer critério FALSO → corrigir.
- Limite: 3 reprovações → pausar, escalar, reabrir spec/ADR.
- **DocOps:** CHANGELOG + dicionário + ADR status; atualizar a spec se decisões
  mudaram (anti-drift); "Salvar como Knowledge Item?".
- **PMO:** atualizar `history.md` (compaction + structured note-taking — `_shared/metacognition-core`).

## Critério de saída
Todos os critérios de `validation.md` = VERDADEIRO. Spec sincronizada com o que foi feito.
