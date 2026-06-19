---
name: advanced-elicitation
description: "Aprofundar qualquer artefato com métodos estruturados de pensamento. Ativar quando o discovery ou o dono pede crítica mais profunda, refinamento de spec, exploração de alternativas, validação de premissas, ou nomeia um método (ex: pre-mortem, steelman, first principles, source triangulation). NÃO ativar para QA de código (isso é edge-case-hunter + qa-critic) nem para exploração de repositório (isso é explorer)."
version: 1.1.0
source: "integração externa seletiva — proveniência completa nas ADRs (ADR-081 convergente #1–69; ADR-085 divergente #70–76 + calibração #77). Adaptado para metacognition."
last_review: 2026-06-17
role_order: null
consumes:
  - "artefato a aprofundar (spec, PRD, decisão, análise, rascunho)"
produces:
  - "versão enriquecida do artefato (mesma estrutura, conteúdo aprofundado)"
pass_criteria: "PASS sse: (a) pelo menos um método foi EXECUTADO no conteúdo (evidenciado por mudança de substância no artefato, não apenas descrição do que o método faria); (b) dono confirmou com [s] no loop interativo OU chamador recebeu versão enriquecida via [x]; (c) claims novos inseridos pelo método estão classificados [CONFIRMADO]/[INFERIDO]/[DESCONHECIDO]."
confidence_required: true
shared_refs:
  - _shared/confidence-classification
  - _shared/anti-hallucination
---

# Advanced Elicitation — Aprofundamento por Método Estruturado

## Carregar de `_shared/`
`confidence-classification` · `anti-hallucination`

## Princípio

Recebe um artefato e o enriquece aplicando métodos de pensamento estruturado. O método é *executado no conteúdo* — não descrito em prosa. A versão enriquecida substitui a original no fluxo do chamador.

Quando invocado pelo **discovery**: aprofunda uma seção do requirements.md antes de finalizar.
Quando invocado pelo **architect**: refina uma decisão antes de fechar a ADR.
Quando invocado pelo **dono diretamente**: aprofunda qualquer artefato em contexto.

## FLOW

### Passo 1 — Receber e analisar o conteúdo

- Identificar: o artefato a enriquecer (spec, PRD, ADR, análise, decisão, rascunho)
- Se não fornecido e não há contexto claro: pedir ao chamador e aguardar
- **Ler o arquivo `methods.md` vizinho a este SKILL.md** (mesmo diretório) — sem esta leitura, a seleção de métodos não tem base. Se o arquivo não for encontrado: pausar e avisar o dono antes de continuar.
- Analisar contexto: tipo de conteúdo · complexidade · stakeholders · nível de risco · potencial criativo

### Passo 2 — Selecionar 5 métodos e apresentar menu

Selecionar 5 métodos do companion que melhor se encaixam no contexto:
- **Determinar a FASE primeiro (eixo de seleção do companion):** objetivo = **GERAR** (artefato vazio/raso, poucas opções) → priorizar fase **divergente** (#70–#76 + #24/#35/#37/#38/#39/#40/#41). Objetivo = **REFINAR/VALIDAR** (artefato já existe) → priorizar fase **convergente** (o restante). Em dúvida/trabalho longo: **divergir primeiro, convergir depois** — não misturar geração e crítica na mesma rodada.
- **FALLBACK determinismo → parada-e-orientação (via porta do ADR-085):** se o objetivo/fase for **ambíguo** ou o artefato não der base para decidir a fase, **NÃO adivinhar** — parar, apresentar o menu equilibrado e pedir ao dono que declare o objetivo (gerar × refinar). Determinismo onde decide; prosa-com-parada onde o julgamento é irredutível. *(A execução de um método sobre o conteúdo é, por natureza, julgamento — é a parte prosa legítima desta skill; o catálogo + canário são a parte determinística.)*
- Dentro da fase convergente, equilibrar: ao menos 1 método de risco/premissas + 1 colaborativo/multi-perspectiva + 1 criativo/estrutural
- Priorizar métodos cujo `output_pattern` se encaixa no tipo de artefato

Apresentar no formato:

```
**Elicitação Avançada — escolha um método:**
_(party-mode disponível para métodos colaborativos)_

1. [Nome do Método] — [descrição curta]
2. [Nome do Método] — [descrição curta]
3. [Nome do Método] — [descrição curta]
4. [Nome do Método] — [descrição curta]
5. [Nome do Método] — [descrição curta]

[r] Novos 5 métodos  [a] Listar todos  [x] Concluir
```

### Passo 3 — Executar o método escolhido

**1–5 (método numerado):**
- Aplicar o método *ao conteúdo concreto* usando a descrição do companion como guia
- Adaptar complexidade ao contexto (não forçar profundidade onde não há substância)
- Exibir a versão enriquecida com o que o método revelou ou melhorou
- Perguntar: "Aplicar esta versão ao documento? [s/n/outro]" — AGUARDAR resposta
- Se sim: enriquecimento aceito; re-apresentar menu para nova rodada
- Se não: descartar o enriquecimento proposto; re-apresentar menu
- Cada rodada constrói sobre a versão já aceita

**[r] Embaralhar:**
- Selecionar 5 métodos diferentes, cobrindo categorias distintas
- Re-apresentar menu com nova seleção

**[a] Listar todos:**
- Exibir tabela compacta de todos os métodos do companion (nome · categoria · output_pattern)
- Permitir seleção por nome ou número

**[x] Concluir:**
- Retornar a versão final enriquecida ao chamador
- Se ativado pelo discovery: versão enriquecida alimenta o requirements.md
- Se ativado pelo architect: versão enriquecida alimenta a ADR
- Se ativado diretamente: exibir versão final consolidada

**Feedback direto do dono:** aplicar ao conteúdo atual e re-apresentar menu

### Passo 4 — Regras de execução

- **Método é ação, não descrição:** executar o método no artefato; nunca apenas explicar o que ele faria
- **Loop obrigatório:** sempre re-apresentar o menu 1–5/r/a/x após cada execução — até [x]
- **Construção acumulativa:** cada método aplicado parte da versão já enriquecida, não do original
- **Preservar substância:** quando há party-mode ativo, não alterar posições que agentes assumiram — tecer a entrega, não reescrever argumentos
- **Classificação epistêmica:** claims novos introduzidos pelo método recebem marcação `[CONFIRMADO]`/`[INFERIDO]`/`[DESCONHECIDO]` antes de entrar no artefato

## Integração com party-mode

Métodos das categorias `collaboration` e `competitive` (ex.: Debate Club Showdown, Red Team vs Blue Team, Stakeholder Round Table) se beneficiam do `party-mode` ativo. Quando estes métodos são selecionados: avisar o dono e oferecer ativar `party-mode` para executar com personas reais em vez de perspectivas vocalizadas pelo agente único. Sem party-mode: agente único vocaliza — válido, porém com menor independência cognitiva; declarar.

## Output

Versão enriquecida do artefato no mesmo formato do original (não adicionar seções não solicitadas).
Claims novos classificados. Sem prosa explicativa que não esteja no artefato final.
