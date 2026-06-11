# ADR 077 — Enforcement determinístico de junção e release: version-claim, override de CI, ledger de junções e validation.md como pré-condição de J3

- Status: **Aceito** (2026-06-11 — gate: **qa-critic adversarial** (Sonnet isolado, process-critic) `aprovar_com_ressalvas` com 1 MÉDIO + 2 BAIXO, os 2 acionáveis **corrigidos pré-merge** (regex híbrida do version-claim + corrupção do ledger fail-closed) + **suíte local verde**; CI billing-blocked → validação pela suíte cross-platform local) · Data: 2026-06-11 · Decisores: dono + squad
- Onda: anti-bypass fase 2 (F1 do plano `docs/_private/reports/avaliacao-processo-framework-2026-06-11.md`) · Tipo: **emenda a mecanismos existentes** justificada pela régua §0(c) — destrava garantia inalcançável por prosa (J0–J3 sem rastro; release sem trigger-canário) **editando** `test_consistency_closing.py`, `qa_evidence.py`, `test_qa_evidence.py` e 2 skills — **zero ferramenta nova, zero canário novo**.
- Relaciona: ADR-011 (junções binárias — este ADR dá rastro mecânico a J0–J3), ADR-030/emenda E2 v1.53.0 (consistency fail-closed — ganha a dim version-claim), ADR-051 (override com custo/consequência — ganha registro mecânico p/ CI pulado), ADR-074 (qa-evidence — o ledger vive no mesmo artefato/ferramenta). Evidência-motriz: **caso real v1.55.0** (2026-06-11) — bloco mergeado declarando versão no commit **sem** CHANGELOG/qa-evidence/checkpoint, com CI pulado por admin-merge; **nenhum dos 4 gates fail-closed disparou** porque todos ancoram no evento "versão nova no CHANGELOG".

## Contexto

A malha fail-closed do fechamento (`test_release_checkpoint`, `test_adr_changelog_sync`, `test_qa_evidence`, `test_posture_gate`) valida o **conteúdo** do release, mas ninguém valida o **trigger**: se o autor não cria a entrada no CHANGELOG, a malha inteira fica inerte (Escape A). Se o CI é pulado por admin-merge, fail-closed vira fail-open sem rastro (Escape B). E as junções J0–J3 do ADR-011 são prosa pura — o PMO "adversarial" não deixa evidência mecânica de que o gate foi aplicado; a dimensão (iv) "process compliance" do process-critic audita em prosa contra prosa. Por fim, o developer declara consumir `validation.md`, mas nada barra J2→J3 sem ele (a cláusula mais frouxa da cadeia spec-driven).

## Decisão (1 frase ativa)

Mecanizar **trigger e rastro** em 4 emendas: **(P1)** `test_consistency_closing.py` ganha a dim **version-claim** (fail-closed: todo `vX.Y.Z` citado em mensagem de commit do histórico recente DEVE ter heading `## [X.Y.Z]` no CHANGELOG — o inverso do `adr-changelog-sync`; provado sem falso-positivo em 200 commits reais); **(P2)** override de CI vira evento registrado — advisory no mesmo canário (último PR mergeado com check vermelho/pulado → exige `OVERRIDE:` no history) + **rule SE/ENTÃO #10** no qa-critic; **(P3)** `qa_evidence.py` ganha `--junction` — apêndice de 1 linha JSONL por junção PASS em `_meta/qa/junctions/<bloco>.jsonl` (junção, artefato-gate, evidência, timestamp; forward-only validado na escrita), dando matéria-prima objetiva à dim (iv) do process-critic; **(P4)** registro de **J3 exige** `--validation <path existente>` **ou** `--justificativa` explícita (fecha o "se aplicável" silencioso).

## Alternativas consideradas

1. **Status quo (prosa + disciplina).** O caso v1.55.0 prova que falha exatamente quando mais importa (bloco mecânico, CI fora, pressa). **Rejeitada.**
2. **Ferramenta nova `junction_ledger.py` + canário novo.** Viola régua §0 (adição pura): `qa_evidence.py` já é o lar do rastro de QA e `test_qa_evidence.py` já o valida. **Rejeitada.**
3. **Hook PreToolUse barrando push sem CHANGELOG.** Vetável por EDR (tese ADR-060/061) e não cobre chat/web. O canário na suíte/CI é não-vetoável. **Rejeitada como mecanismo primário** (pode virar defesa-em-profundidade futura).
4. **Emendas aos mecanismos existentes (ESCOLHIDA).** 2 arquivos Python editados + 2 skills + 1 workflow; rastro mínimo (1 linha por junção, ~5 linhas/bloco); fail-closed só onde determinístico (version-claim, J3-precondição, forward-only); advisory onde depende de rede (`gh`).

## Consequências

**Positivas:** o Escape A morre (commit que declara versão sem CHANGELOG → suíte vermelha **na hora**, não no release seguinte); o Escape B deixa rastro obrigatório (`OVERRIDE:` no history — ADR-051 mecanizado p/ CI); J0–J3 deixam evidência objetiva auditável pelo process-critic e pelo dono; `validation.md` deixa de ser pulável em silêncio. **Negativas/limite (declarado):** o ledger depende de o orquestrador **rodar o comando** ao declarar PASS — é rastro, não trava física (a trava é o process-critic reprovar bloco sem ledger, dim iv); a dim P2 via `gh` é advisory (rede/auth indecidíveis no CI — mesmo padrão das dims advisory existentes); version-claim varre os últimos 200 commits (janela móvel — claims além disso são história fechada, mesma doutrina forward-only do `test_release_checkpoint`); **escopo do claim (achado MÉDIO do process-critic, corrigido):** `vX.Y.Z` conta em qualquer posição; `X.Y.Z` **sem prefixo** só conta quando o subject tem contexto de versão (changelog/release/vers/bump) — evita falso-positivo tipo "python 3.12.1"; risco residual declarado: versão de dependência citada num subject de release pode gerar FP raro (tratável como exceção consciente). **Corrupção do ledger é fail-closed** (achado BAIXO corrigido): linha não-JSON → recusa registrar e manda investigar (não zera o forward-only em silêncio); custo de ~5 linhas JSONL por bloco (aceito; reverter se virar formulário — método-audit vigia).

## Implementação (ponteiro)

- `tools/test_consistency_closing.py`: dim (3) version-claim fail-closed + advisory (4) CI-override (gh, best-effort).
- `tools/qa_evidence.py`: subcomando `--junction` (validação de sequência forward-only + precondição J3) gravando `_meta/qa/junctions/<bloco>.jsonl`.
- `tools/test_qa_evidence.py`: casos do ledger (append válido, ordem violada, J3 sem validation/justificativa).
- `.agent/workflows/handoff.md` §Antes de invocar: registrar a junção via comando. `.agent/skills/pmo/SKILL.md` §Junção-check: ponteiro. `.agent/skills/qa-critic/SKILL.md`: rule #10 (CI pulado sem OVERRIDE → REPROVADO).
- `capabilities.json`: `junction-ledger` (+1 registro; enforcement=ci via test_qa_evidence) + rebuild `CAPABILITIES.md`.
