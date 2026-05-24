# /feature-plan <descricao> — Plano técnico com Spec + ADR (v1.2)

## Pré-requisito
briefing.md preenchido + glossário com termos relevantes.

## Sequência
1. **PMO:** confirmar escopo, sinais de complexidade e **classe de confiança**
   (governa o roteamento — `rules/04`).
2. **Criar spec atômica** (NOVO): clonar `docs/specs/_template/` →
   `docs/specs/<feature>/` e preencher `requirements.md` + `validation.md`
   (critério de aceite **binário**). Sem `validation.md` → não avança.
3. `/handoff architect`
4. **Architect:** 3 alternativas + recomendação + ADR rascunho. O ADR **referencia
   a spec** (vincular decisão → `requirements.md`).
5. **PMO:** apresentar ADR + spec ao usuário — aguardar aprovação.
6. ADR aceito → `/implement`.
7. `/handoff docops` — salvar ADR em `docs/adr/NNN-titulo.md`.

## Critério de saída
ADR com Status "Aceito" + `validation.md` com critérios binários definidos.
