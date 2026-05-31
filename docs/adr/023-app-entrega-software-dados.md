# ADR 023 — Aplicação de entrega SW/dados de primeira classe (evals-engineer + ux-designer)

- Status: Aceito (qa-critic Sonnet isolado: R1 REPROVADO → fixes → R2 APROVADO, ADR-011/018)
- Data: 2026-05-30 · Decisores: dono (reorientação explícita) + squad (architect)
- Onda: camada-de-produto (v1.21.0) · Pesquisa: SPEC Perplexity §2/§4/§5 (squad SW) + prompts do dono (sessão l.421/427/1591) · Tipo: **aplicação** (NÃO altera o núcleo)
- Relaciona: `exemplos/README.md` §"Quando faz sentido ter algo aqui", ADR-022 (mission-gate ativa os papéis), `_template`, `high-stakes-gate`, `framework-schema.json` (campo `classe`).

## Contexto

Reorientação do dono (sessão Perplexity, verbatim): *"desenvolvimento de software… **é um domínio, mas apropriado ao que fazemos**, pois iremos desenvolver soluções, ou analisar dados e fazer ciência de dados… **geralmente culminando em código**; o objetivo é **facilitar para o usuário final: ide, exe, código ide facilitado com gui"* (l.421); *"a gui não é para o framework, mas **para o produto**… por isso os agentes sugeridos"* (l.427); *"não deve forçar mudanças. Apenas atualização e melhoria do código atual"* (l.1591).

O framework existe para **entregar um produto** de dados/software conforme briefing. A análise inicial classificou os 4 papéis SW (ux-designer, evals-engineer, governance-lead, skill-librarian) como "vazamento de domínio → fora do núcleo". **Isso foi viés de processo-sobre-produto** (diagnosticado pela própria pesquisa Perplexity): otimizou a pureza do agnosticismo e subponderou o propósito declarado. A distinção núcleo-agnóstico × aplicação-de-domínio continua certa — mas a entrega SW/dados não é "clonar `_template` um dia"; é a **aplicação canônica**, e merece suporte de primeira classe. O `exemplos/README.md` já prevê o encaixe: *"em **distribuições especializadas**… você pode manter uma aplicação… para servir de **demonstração viva**."*

**Reveredito por papel — critério: melhora o PRODUTO entregue?**
- **evals-engineer** — SIM (forte): gold-set, regressão, reprodutibilidade; distinto do qa-critic (adversarial 1-turno). Lacuna real: hoje não há validação **sistemática** de produto. Quase-agnóstico (dados E software).
- **ux-designer** — SIM (quando o produto tem UI): ux-spec é o contrato produto→developer.
- **governance-lead** — função já coberta por `high-stakes-gate` + `action-safety` + discovery-escopo; dono (l.1415) quer **detectar** regime regulado, não fixar papel. **Não criar.**
- **skill-librarian** — é *meta* (cura das skills do framework), não o produto; já coberto pelo campo `classe` (poda Chesterton, ADR-017) + `validate_skills.py`. **Não criar.**

## Decisão (1 frase ativa)

Criar uma **aplicação de entrega SW/dados de primeira classe** em `exemplos/dominio-software/` (distribuição especializada / demonstração viva — `exemplos/README.md`), clonada de `_template`, declarando `domain: software-data`, contendo **dois** papéis novos — `evals-engineer` (validação sistemática: gold-set/regressão) e `ux-designer` (ux-spec quando o produto tem UI) — ativados pelo `product_type` do mission-gate (ADR-022); **governance-lead e skill-librarian NÃO são criados** (cobertos por `high-stakes-gate`/`action-safety` e pelo campo `classe`/`validate_skills`); **o núcleo `_shared/` e o squad base permanecem agnósticos e inalterados**.

## Alternativas consideradas (≥3)

1. **Não fazer / usuário clona `_template` quando precisar (status quo — meu veredito #14 inicial).** Prós: núcleo purista. Contras: o produto entregue fica órfão; o propósito declarado não tem suporte; cada projeto reinventa ux/evals. **Rejeitada — foi o erro corrigido pelo dono.**
2. **Adicionar os papéis ao squad base do núcleo.** Prós: sempre disponíveis. Contras: **viola P12** (domínio no núcleo) e P10 (adição pura). **Rejeitada.**
3. **Os 4 papéis no app.** Prós: paridade com a SPEC Perplexity. Contras: governance-lead e skill-librarian **duplicam** mecanismos do núcleo (high-stakes-gate; campo `classe`) — adição com ganho líquido negativo. **Rejeitada.**
4. **App SW/dados com ux+evals; governance/librarian cobertos pelo núcleo (ESCOLHIDA).** Prós: cumpre o propósito, núcleo intacto e agnóstico, lean (só os 2 papéis que pagam o peso). Contras: `exemplos/` deixa de ser vazio → o repo se declara **distribuição especializada** (documentado, não acidental).

## Consequências

**Positivas:** produto de software/dados ganha suporte de primeira classe (ux-spec + evals sistemáticas) sem tocar no núcleo; ativação automática via product_type (ADR-022); demonstração viva para quem clona.
**Negativas:** o princípio "`exemplos/` vazio na distribuição oficial" passa a ter exceção declarada (somos distribuição especializada) — `exemplos/README.md` é atualizado para refletir.
**Riscos:** (a) o app divergir do contrato do núcleo — mitigado: `validate_skills.py` cobre os SKILL.md do app (8 campos). (b) `evals-engineer` virar "evals como bala de prata" (viés que a pesquisa nomeia) — mitigado: gold-set exige gate humano no início + cada métrica precisa de pergunta de design. (c) escopo do app crescer (skill-sprawl) — mitigado pelo campo `classe` + tally.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.21.0-runtime-hooks-web` · `2026-05-30` · grep `dominio-software|evals-engineer|ux-designer`
- Artefatos: `exemplos/dominio-software/` com `README.md` (declara domain + product-types.txt + mapa tipo→papel), `evals-engineer/SKILL.md`, `ux-designer/SKILL.md` (ambos clonando `_template`, contrato de 8 campos, carregando `_shared/`); atualização de `exemplos/README.md` (exceção da distribuição especializada). Núcleo: **nenhuma alteração** em `_shared/` nem no squad base.
