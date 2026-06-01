# ADR 033 — Elicitação-consultiva mecanizada: banco agnóstico de dimensões + linter de profundidade de spec

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: remediação v2 (marco v1.24.0) · Tipo: **novo** (1 banco agnóstico + 1 linter + 1 canário) — net-gain por **destravar verificação inalcançável** (régua §0 cláusula c): hoje nenhum gate mede se a spec endereçou o produto.
- Origem no plano: item 1 ⭐ (causa-raiz nº1: `[campo]` elicitação rasa + `[GEMINI]` discovery→spec executável). Relaciona: ADR-010/012 (escopo declarado), ADR-020 (gate de agnosticismo), ADR-022 (mission-gate/product_type), ADR-040 (CI que roda o canário).

## Contexto

O incidente de campo provou que **o gap mais caro não foi a segurança de ação — foi a elicitação
proativa**. O agente "fez 4 perguntas (escopo, entrada, stack, oráculo). Não perguntou sobre
produto/GUI." O dono teve de **empurrar** todo o produto (operador, interface, escopo mensal+acumulado,
recortes, persistência, log). O erro **não foi ausência de perguntas — foi perguntas de coletor de
requisitos, não de consultor.** E havia instrução de discovery **em prosa** que foi ignorada. Pela
régua reitora do plano ("nada importante em prosa → tudo vira ferramenta"), a correção tem de ser
mecânica.

**Distinção que preserva o agnosticismo (P12):** há dois tipos de pergunta e só um vive no núcleo:
- **Meta-pergunta de elicitação** ("quem opera?", "qual escopo temporal?", "precisa persistência?") —
  **agnóstica, universal** → pode viver no banco.
- **Pergunta de domínio** ("descartar tais centros?", "a referência é a variação X ou Y?") — específica
  do projeto → **NUNCA** entra no banco; é *gerada* pelo discovery ao ler o material. O
  `check_core_agnostic.py` barra qualquer termo de domínio que vaze para o banco.

## Decisão (1 frase ativa)

Criar **`_shared/discovery/elicitation-dimensions.md`** (banco agnóstico das 9 dimensões universais que
toda elicitação de produto recorrente deve endereçar, em tabela machine-readable com aliases),
**`tools/check_spec_depth.py`** (linter que falha exit 1 se o `requirements.md` não registra uma
**decisão** — não placeholder — para cada dimensão obrigatória) e o canário **`tools/test_spec_depth.py`**,
wirando o linter como **gate antes de J1** (discovery→architect) e reforçando a postura **consultiva**
(default sênior + trade-off, não pergunta em aberto) no `discovery/SKILL.md`.

## Alternativas consideradas (≥3)

1. **Manter em prosa (status quo).** Foi exatamente o que falhou: a instrução existia e foi ignorada. **Rejeitada — é o gap.**
2. **Hardcodar perguntas de produto no núcleo.** Viola P12 (domínio no núcleo) e engessa; perguntas de produto variam por caso. **Rejeitada.**
3. **Linter que avalia a QUALIDADE da resposta (NLP/heurística de "boa decisão").** Frágil, não-determinístico, e a qualidade do default é julgamento sênior, não mecanizável. **Rejeitada** — o gate verifica **cobertura de dimensão**, não acerto.
4. **Banco agnóstico de dimensões + linter de cobertura + postura consultiva (ESCOLHIDA).** Prós: mecaniza o que dá (a dimensão foi endereçada?), mantém o núcleo agnóstico (só meta-perguntas + aliases), barra a spec rasa antes de codar. Contras: não garante que o default seja sênior — limite **declarado** em `LIMITS.md` (mecanizado: cobertura; não-mecanizado: acerto do default).

## Consequências

**Positivas:** a spec rasa (que computa um subconjunto sem endereçar operador/escopo/persistência/log)
**falha o gate** antes de J1 — o developer não começa enquanto a spec não cobrir o produto; a elicitação
vira consultiva por design; o banco é a SSoT editável (régua §0: só dimensões universais entram).
**Negativas:** introduz um artefato de dados em `_shared/discovery/` (não é skill — sem SKILL.md; é
banco lido pelo linter). **Riscos/limite declarado:** cobertura ≠ qualidade da decisão; aliases reduzem
mas não eliminam falso-negativo de casamento termo→dimensão → vai a `LIMITS.md`.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.23-v1.31-remediacao` · `2026-05-31` · grep `check_spec_depth|elicitation-dimensions`
- Artefatos: `_shared/discovery/elicitation-dimensions.md`, `tools/check_spec_depth.py`,
  `tools/test_spec_depth.py` (5 casos sintéticos agnósticos, verde), edição `discovery/SKILL.md`
  (§Elicitação-consultiva), `handoff.md` J1 (gate), `docs/specs/_template/requirements.md` (§Dimensões).
- DONE quando: banco no núcleo + linter barrando J1 + `check_core_agnostic` confirma banco sem termo de
  domínio + ≥3 discoveries reais com cada dimensão decidida (este último depende de uso real → `LIMITS.md`).
