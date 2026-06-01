# ADR 050 — Elaboração de documentos premium (doc/pdf/pptx, custo + trade-offs, fluxo de aprovação)

- Status: **Aceito** (premium-only — implementado em v1.36.0)
- Data: 2026-06-01 · Decisores: dono + squad (architect)
- Tipo: capacidade premium — camada premium (ADR-049), **nunca no baseline** (stripada do public/non-admin).
- Origem: dono — "elaboração de documentos pelo script focado no que o usuário elicitar (aprovar alteração, aprovar orçamento, propor o software) — flexível: doc, pdf, pptx, custo maior e trade-offs" + "deve incluir POPs, manuais, como configurar/operar, manutenção, etc conforme cada situação; discovery, explorer e briefing+PMO definem".

## Contexto

Um produto premium não entrega só o cálculo: entrega **documentos executivos** que apoiam DECISÃO —
proposta do software a construir, **orçamento com custo e trade-offs**, pedido de **aprovação de mudança/
orçamento** — em formatos flexíveis (doc/pdf/pptx), focados no que o usuário elicitou. Hoje o framework
mecaniza o **execution-report** (ADR-038, técnico); falta a camada de **entregável executivo premium**.

## Decisão (1 frase ativa)

Criar `tools/gen_exec_doc.py` (gerador **flexível por TIPO**, premium-only) que **renderiza qualquer
documento que a spec declarar** — decisão/orçamento (custo + trade-offs + alternativas + aprovação),
**POP/SOP**, **manual de operação**, **guia de configuração**, **plano de manutenção** — em **md/docx/
pptx/pdf**, sendo **QUAL documento cada situação exige decidido pelo discovery/explorer/briefing+PMO**
(papel deles, inalterado — o gerador NÃO decide, só renderiza), agnóstico (estrutura da spec, conteúdo do
projeto) e **anti-fabricação** (campo vazio → `NÃO PREENCHIDO`, nunca número inventado).

## Alternativas consideradas (≥3)

1. **Gerador hardcodado num tipo (só "decisão executiva").** Não cobre POP/manual/config/manutenção. **Rejeitada** — o dono pediu "conforme cada situação".
2. **Hardcodar a lista de tipos no gerador.** Engessaria; a definição de qual doc cada situação pede é do discovery/PMO (regra existente, não mudar). **Rejeitada.**
3. **Gerador doc-type-agnóstico que renderiza as seções da spec + `<!-- required: ... -->` por template (ESCOLHIDA).** Prós: 1 gerador, N tipos (templates premium clonáveis); o discovery/PMO escolhe o template; anti-fabricação embutida; degrada sem libs (md sempre). Contras: "completude" (quais seções) depende da spec/template — coerente com a regra de definição existente.

## Consequências

**Positivas:** o premium entrega o documento que apoia decisão/operação (proposta, orçamento, POP, manual,
config, manutenção), focado na elicitação; 1 gerador serve todos os tipos; campos vazios nunca viram número
inventado. **Negativas:** +1 ferramenta + 5 templates premium (stripados do baseline). **Limite declarado:**
premium-only (ADR-049); pptx/pdf dependem de libs opcionais (degrada para md/docx); **custo/trade-off são
campos do projeto, nunca fabricados** (canário `test_gen_exec_doc` prova).

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.36-doc-premium` · `2026-06-01` · grep `gen_exec_doc|_template-documentos`
- Artefatos: `tools/gen_exec_doc.py` + `tools/test_gen_exec_doc.py` (canário) + `docs/specs/_template-documentos/`
  (+ `README.md` da doutrina): **runbook-validacao · apresentacao-executiva** · decisao-executiva · pop-sop ·
  manual-operacao · guia-configuracao · plano-manutencao — **todos em `PREMIUM_STRIP_FILES`** (stripados do
  baseline). `requirements-dev` ganha python-pptx/reportlab (opcionais). Wiring no blueprint premium
  (discovery/PMO definem o tipo). NÃO listado no `build_limits`/LIMITS (capacidade premium; prova pelo canário
  + ADR, evita desync premium×baseline no LIMITS).
- **Refino do dono (2026-06-01):** templates são **REFERÊNCIA não-determinística** — a estrutura real é
  *objetivada pelo briefing/spec do cenário/domínio quando vier*. **Piso:** runbook de validação SEMPRE; em
  domínio **regulado declarado pelo discovery** (ADR-010/012 + `high-stakes-gate`) o conjunto obrigatório
  expande. O núcleo permanece agnóstico (não hardcoda normas; o discovery declara).
- DONE quando: gerador + templates premium (inclui runbook) + canário verde; baseline NÃO recebe (export strip); premium recebe.
- **Emenda v1.37.0 (entrega navegável + piso mecanizado):** `tools/make_index.py` (**baseline** — usabilidade:
  `index.html` navegável + `LEIA-ME.txt` com ordem de leitura guiada, auto-verificação, resumo-3-linhas,
  duplo-papel handoff ADR-012). `gen_exec_doc --deliver` monta `output/<datestamp>-<label>/` com subpastas por
  tipo e invoca o índice. `tools/check_delivery_floor.py` (**premium**) mecaniza o piso "runbook SEMPRE"
  (prosa→gate; dispensa consciente, bloqueada em regulado). Corrigida a **truncagem silenciosa** (pptx/pdf agora
  paginam). LIMITS declara: gera **estrutura, não polimento visual** (deck formatado = ADR futuro).
