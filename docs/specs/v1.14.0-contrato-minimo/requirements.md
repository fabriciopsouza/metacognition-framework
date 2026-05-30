# Requirements — v1.14.0 Contrato mínimo de skill (Onda 0, ADR-013, P3)

## Objetivo
Formalizar e tornar verificável o contrato de interface das skills de processo, sem inflar
(régua §0). Fundação de schema para as ondas 1/3/4.

## Escopo IN
- Schema do frontmatter (`tools/framework-schema.json`).
- Validador cross-platform (`tools/validate_skills.py`) — gate IDE.
- Auto-check de 1 linha no chat (texto em `_shared/output-format/SKILL.md`).
- Aplicação do contrato às 7 skills (`pmo, discovery, architect, developer, qa-critic, docops, explorer`) + `_template`.

## Escopo OUT
- Campos `enforcement` e `classe` ficam **declarados como opcionais** no schema, mas só são
  *preenchidos* nas ondas 1 (ADR-015) e 3 (ADR-017) — aqui só reservamos o lugar (anti-retrabalho).
- Integração CI no GitHub Actions: documentada no ADR como caminho, não implementada nesta onda
  (gate roda local/pré-merge via `python tools/validate_skills.py`).

## Requisitos
- REQ-1: Todo SKILL.md das 7 skills tem os 8 campos obrigatórios preenchidos com dado real (não placeholder).
- REQ-2: `name` casa `^[a-z0-9-]+$` e = nome da pasta.
- REQ-3: `pass_criteria` é binário (PASS/não-PASS sem zona cinza).
- REQ-4: `shared_refs` aponta para arquivos que existem em `_shared/`.
- REQ-5: `role_order` reflete a sequência PMO(0)→discovery(1)→architect(2)→developer(3)→qa-critic(4)→docops(5)→release(6); explorer e skills auxiliares = `null`.
- REQ-6: Nenhum campo obrigatório sem verificação correspondente (anti-andaime JARVIS).
- REQ-7: O validador roda sem dependências externas (Python stdlib) — portabilidade.
- REQ-8: Campos legados (`source`, `last_review`, `metadata`) permanecem permitidos (anti-rewrite).

## Fora de risco (defaults fixados, [INFERIDO])
- `role_order` obrigatório com `null` permitido (resolve skills não-sequenciais sem alucinar ordem).
- Limite de cerimônia: 8 obrigatórios (P3 §6); ultrapassar dispara revisão.
