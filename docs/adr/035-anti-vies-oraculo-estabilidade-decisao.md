# ADR 035 — Anti-viés-de-oráculo + estabilidade de decisão (gate de campo-fonte)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: remediação v2 (marco v1.26.0) · Tipo: **novo** (1 linter + 1 canário + rule no qa-critic) — net-gain por destravar verificação inalcançável.
- Origem no plano: item 3 ⭐ (`[campo]` item #2 do placar — o erro mais caro). Relaciona: ADR-018 (QA turno único heterogêneo), ADR-041 (sicofância), qa-critic rule #9, ADR-040 (CI).

## Contexto

O erro mais caro da sessão **não foi de elicitação — foi de execução**: existiam colunas-irmãs de nome
próximo; o agente mapeou um termo de domínio para a coluna **literal** por inferência, bateu/quase-bateu
o número-alvo, e **abandonou um resultado já validado** sem prova numérica. Gatilhos: (a) bater valor-alvo
tratado como validar semântica (viés de confirmação); (b) over-correção por rótulo; (c) mapear
termo→coluna por inferência. Nenhuma elicitação previne isto.

> **Nuance confirmada pelo dono (refinamento):** no caso real, a **análise estava correta** — quem
> estava errado era o **próprio oráculo** (dado errado preenchido numa coluna). A lição, portanto, **não**
> é "deferir a quem confirma": é **duvidar e verificar contra a fonte primária**, incluindo duvidar do
> oráculo/dado-fonte. Por isso o gate mecaniza a **exigência de registro** (decisão + justificativa,
> idealmente com prova numérica), mas a **confirmação NÃO é prova de correção** — a verificação semântica
> contra a fonte é a camada adversarial (qa-critic), e o oráculo está no escopo da dúvida.

## Decisão (1 frase ativa)

Criar **`tools/check_field_mapping.py`** (quando o `requirements.md` declara `## Mapeamento de
campo-fonte`, cada linha exige **confirmação do dono + justificativa** — mapeamento por inferência =
FAIL) + canário `tools/test_oracle_bias.py`, e adicionar ao qa-critic a **rule #9**: mecaniza a
**exigência de registro**; e mantém adversariais (não-mecanizáveis) as regras *"que outra interpretação
produziria este número?"* (bater valor ≠ validar semântica) e *"abandonar resultado validado exige prova
numérica"* (reverter por rótulo = REPROVADO).

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** O viés de oráculo + over-correção reaparecem. **Rejeitada — é o gap.**
2. **Mecanizar o julgamento semântico (decidir qual coluna é a certa).** Exige ler o domínio/dados — viola agnosticismo e é não-determinístico. **Rejeitada** — o que se mecaniza é a *exigência de registro*, não o acerto.
3. **Só prosa no qa-critic (sem linter).** Foi o que falhou (a disciplina dependeu do dono). **Rejeitada** — o registro vira gate.
4. **Linter de registro + rules adversariais (ESCOLHIDA).** Prós: o gate recusa abençoar mapeamento por inferência mesmo que bata o número; o julgamento semântico fica explicitamente adversarial. Contras: não garante que a justificativa esteja semanticamente certa → limite **declarado** em `LIMITS.md`.

## Consequências

**Positivas:** mapear termo→coluna por inferência (mesmo batendo o alvo) vira FAIL mecânico; a
over-correção por rótulo é nomeada e barrada pelo qa-critic; o registro do "porquê" fica auditável.
**Negativas:** exige a seção `## Mapeamento de campo-fonte` quando há ambiguidade (adição pequena ao
template, condicional). **Riscos/limite declarado:** o gate prova *registro*, não *acerto semântico*
→ `LIMITS.md` ("mecanizado: exigência de registro; não-mecanizado: correção semântica do mapeamento").

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.23-v1.31-remediacao` · `2026-05-31` · grep `check_field_mapping`
- Artefatos: `tools/check_field_mapping.py`, `tools/test_oracle_bias.py` (4 casos sintéticos agnósticos),
  qa-critic rule #9, `docs/specs/_template/requirements.md` (§Mapeamento de campo-fonte).
- DONE quando: regra no qa-critic com critério binário + canário do registro-obrigatório no CI. [CONFIRMADO]
