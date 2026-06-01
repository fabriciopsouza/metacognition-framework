# ADR 049 — Três distribuições de fonte única: public · non-admin · premium (baseline × premium)

- Status: Aceito
- Data: 2026-06-01 · Decisores: dono + squad (architect)
- Tipo: **novo** (camada de tiering no export) — estende ADR-047 (single-source → multi-distribuição) e ADR-046 (blueprints/ux premium). Net-gain: viabiliza modelo free/plus sem fork (uma fonte).
- Origem: dono — "ao final teremos 3 repos: public, non-admin e premium (cobro por este). A filosofia é a mesma nos 3, atualização de fonte única." + "premium = polimento (UX premium, proposta proativa, documentos); **não** tirar análise/briefing/discovery."

## Contexto

As últimas melhorias (blueprints de domínio, ux-gate premium, proposta proativa de produto) têm "cara de
premium". O dono quer **3 distribuições**, todas geradas do **único** repo privado, cada uma com sua
proposta: **public** (baseline + hooks), **non-admin** (baseline + sem hooks), **premium** (full premium +
hooks, privado/pago). A linha que separa **premium × core** é **experiência × correção**: o público entrega
um produto **funcional e correto** com **toda** a capacidade analítica/discovery/briefing/QA/segurança;
o premium adiciona a **camada de experiência** (proposta proativa de produto, UX premium, documentos
executivos). **Nada que mate o discovery sai do baseline.**

## Decisão (1 frase ativa)

Marcar a **camada premium** como removível — arquivos inteiros (`exemplos/dominio-*/blueprint.md`) e seções
entre `<!-- premium:start/end -->` (discovery §Blueprint, ux-designer §gate premium) — e estender
`export-clean` com três modos (default/baseline strip-premium · `--nonadmin` baseline+sem-hooks · `--premium`
mantém-premium), publicando do **mesmo source** os 3 repos via `publish-clean`; o **core** (discovery
profundo, método sênior, QA, anti-viés, segurança, correção, `check_input_contract`) fica em **todas** as
distribuições.

## Alternativas consideradas (≥3)

1. **Forks separados por tier.** Diverge, dobra manutenção, perde "fonte única". **Rejeitada.**
2. **Tirar capacidade analítica/discovery do baseline para diferenciar.** Mataria o valor do público e o que a ideia original propõe. **Rejeitada — proibido pelo dono.**
3. **Premium como repo editado à mão.** Quebra single-source + rastreabilidade. **Rejeitada.**
4. **Camada premium marcada + strip no export + 3 publish do mesmo source (ESCOLHIDA).** Prós: free/plus sem fork; core idêntico em todas; premium = só experiência; rastreável. Contras: exige disciplina de marcar premium com `<!-- premium -->` — canário verifica.

## Consequências

**Positivas:** modelo free (public/non-admin) + plus (premium) de **uma** fonte; o baseline continua
entregando produto correto com toda a análise; o premium agrega experiência (proposta proativa + UX +
documentos). **Negativas:** +1 repo (premium, privado) + 2 modos no export. **Riscos/limite declarado:**
feature premium nova precisa ser **marcada** (`PREMIUM_STRIP_FILES` ou `<!-- premium -->`), senão vaza para
o baseline; o canário `test_premium_tier` prova a marcação + que o core sobrevive ao strip → `LIMITS.md`.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.34-non-admin`→`feat/v1.35-premium-tier` · `2026-06-01` · grep `premium:start|PREMIUM_STRIP|--premium`
- Artefatos: `tools/export-clean.py` (PREMIUM_STRIP_FILES + strip_premium_markers + `--premium`), markers em
  `discovery/SKILL.md` e `ux-designer/SKILL.md`, `publish-clean.yml` (3 publish: public/non-admin/premium),
  repo `metacognition-framework-premium` (privado) + deploy key + secret, `tools/test_premium_tier.py`.
- DONE quando: 3 repos publicados do mesmo source, baseline sem premium, premium com premium, core em todos.
