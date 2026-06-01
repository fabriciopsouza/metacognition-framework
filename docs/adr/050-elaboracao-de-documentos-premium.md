# ADR 050 — Elaboração de documentos premium (doc/pdf/pptx, custo + trade-offs, fluxo de aprovação)

- Status: **Proposto** (premium, private/premium-only — a construir; registrado a pedido do dono)
- Data: 2026-06-01 · Decisores: dono + squad (architect)
- Tipo: futuro (capacidade premium) — camada premium (ADR-049), nunca no baseline.
- Origem: dono — "elaboração de documentos pelo script focado no que o usuário elicitar (aprovar alteração, aprovar orçamento, propor o software sendo construído) — flexível: doc, pdf, pptx, informando o custo maior e trade-offs".

## Contexto

Um produto premium não entrega só o cálculo: entrega **documentos executivos** que apoiam DECISÃO —
proposta do software a construir, **orçamento com custo e trade-offs**, pedido de **aprovação de mudança/
orçamento** — em formatos flexíveis (doc/pdf/pptx), focados no que o usuário elicitou. Hoje o framework
mecaniza o **execution-report** (ADR-038, técnico); falta a camada de **entregável executivo premium**.

## Decisão proposta (1 frase ativa)

**[PROPOSTA]** Criar uma capacidade premium (na camada premium ADR-049, ausente no baseline) que **gera
documentos executivos** a partir do que o discovery elicitou — proposta/orçamento com **custo + trade-offs
+ alternativas** e fluxo de **aprovação** (aprovar mudança / aprovar orçamento) — exportáveis em **doc/pdf/
pptx**, agnóstica de domínio (a estrutura é padrão; o conteúdo vem do projeto). Provável lar: papel
`docs-executivos`/extensão do `ux-designer`/`docops` na app premium, com gerador (python-docx/reportlab/
python-pptx, já dependências opcionais declaradas).

## Alternativas a avaliar (quando implementar)

1. **Gerador único multi-formato** (markdown → doc/pdf/pptx via libs). Simples; formato premium consistente.
2. **Templates por tipo de decisão** (proposta de software · orçamento · pedido de aprovação) parametrizados.
3. **Integrar ao blueprint** (a "suíte de saída" do blueprint premium já prevê apresentação executiva).

## Consequências (esperadas)

**Positivas:** o premium entrega o que diferencia (decisão apoiada por documento), focado na elicitação.
**A decidir:** libs (python-docx/reportlab/python-pptx — opcionais, degradar sem elas), o modelo de
custo/trade-off (agnóstico: campos, não números hardcoded), e a marcação premium (`<!-- premium -->` +
arquivos em `exemplos/dominio-software/`). **Limite:** premium-only (ADR-049); custo/trade-off são
**campos a preencher**, nunca valores inventados (anti-fabricação).

## Implementação

- **Pendente.** Marcador da decisão (régua §0: débito declarado). Quando priorizado: gerador + templates +
  marcação premium + canário (documento gera sem erro; custo/trade-off são campos, não fabricados) + LIMITS.md.
