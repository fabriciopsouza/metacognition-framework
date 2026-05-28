# Discovery — Reforço sênior (método em 8 passos)

> Companion do `discovery` (v1.8.0+). Progressive disclosure (ADR-003):
> carregado SOB DEMANDA quando há **fonte canônica/normativa citada** no contexto.
> Domain-agnóstico — vale para dev/BI/BPM/regulado/qualquer caso onde se cita norma,
> spec, padrão técnico ou doc oficial específico.
> Fonte: ADR-009. NÃO carregar em discovery sem citação de fonte (vira inflação — fere régua §0).

## Filtro de entrada (passo 1 — obrigatório; restritivo por design)

Ativar este reforço **apenas** quando **algum** dos critérios abaixo se verifica de forma explícita. Em dúvida, NÃO carregar (default: discovery universal).

1. **Citação de norma regulatória ou padrão técnico EXTERNO** (ANP, ANVISA, FDA, BACEN, ABNT, ISO, API, GAMP, IEEE, RFC, NBR, etc.). Não inclui "convenção" interna.
2. **Referência a documento OFICIAL específico**: resolução, portaria, regulamento técnico, manual oficial de fabricante, spec assinada. **NÃO inclui** contratos comerciais genéricos, documentação interna de projeto, ou READMEs.
3. **Regra de negócio interna com peso semântico DECLARADO** — anti-fraude, ALCOA+, audit trail, fairness, conformidade regulatória. **NÃO inclui qualquer regra de negócio** — só aquelas cujo impacto envolve perda financeira material ou compliance.
4. **Decisão downstream de alto impacto confirmada**: executiva irreversível, financeira material, regulatória/auditável.

Se nenhum se verifica → NÃO carregar. Voltar ao método universal do `SKILL.md`. Filtro permissivo demais derrota o progressive disclosure.

## Os 8 passos auditáveis

```
1. MAPEAR fontes — internas (repo/docs/specs) + externas (autoridade,
   norma, padrão setorial/internacional, doutrina).

2. VERIFICAR VIGÊNCIA de cada fonte citada — em vigor? alterada?
   REVOGADA? por qual sucessora? Datas. NUNCA citar norma/spec sem
   checar atualidade. Liga com _shared/anti-hallucination (anti-pattern).

3. COMPLEMENTAÇÕES — normas/specs complementares que cada fonte cita
   ou recebe; alterações posteriores; emendas/portarias/instruções.

4. RECONCILIAR CROSS-DOMAIN — quando prática de um domínio importa
   convenção de outro, marcar como "baliza por analogia" ≠ "regra
   obrigatória". Não importar AC como regulação direta.

5. PERTINÊNCIA método↔objetivo declarado — o que se mede/produz serve
   o objetivo? Há vieses (físicos, semânticos, regulatórios,
   estatísticos) que invalidam parte?

6. BACKLOG DE ELICITAÇÃO ao dono — fatos pertinentes não-documentados;
   PERGUNTAR, não calar gaps. Lista numerada com "por que importa".

7. CLASSIFICAR cada afirmação CONFIRMADO|INFERIDO|DESCONHECIDO + fonte
   (_shared/confidence-classification + _shared/anti-hallucination).

8. PASS ADVERSARIAL — sobreviveria a um auditor/regulador/revisor
   sênior? Antecipar perguntas que NÃO foram feitas mas mordem.
```

## Princípios anexos (parte do método sênior, não bônus)

- **Antecipação sênior é ENTREGA**, não bônus: listar pontos pertinentes que o dono **não pediu** mas pode não ter visto (premissas que mordem, riscos não-óbvios, alternativas não-avaliadas). Vai em seção dedicada do output — `research-brief.md` **§7 Antecipações + §8 Backlog de elicitação** (template `docs/specs/_template-research/`) ou seções equivalentes do `requirements.md`.
- **Crítica do MÉTODO ≠ crítica do PRODUTO** — antes de auditar o output, auditar se a discovery em si está bem-apontada (objetivo do cliente, pertinência, viés, recorte).
- **Conflito instrução-dono × canon = surface-and-reconcile** — quando o dono diz X e o canon diz Y, surfacear EXPLICITAMENTE com análise; o dono decide com meta-contexto (pode estar com entendimento mais novo que o canon).
- **Regra de negócio tem SEMÂNTICA** — anti-fraude, audit, ALCOA+, fairness; não despriorizar regra sem entender o papel.
- **Conscious-lean** — cada output passa pelo "isso serve o objetivo, ou estou polindo o lado errado?". Lean operacional, não preguiça.

## Output esperado

Adicionar ao output base do discovery (`requirements.md` ou `research-brief.md`) **2 seções obrigatórias**:

- **§ Antecipações** — coisas que o dono não pediu mas pode não ter visto.
- **§ Backlog de elicitação** — Q1..Qn numerada, com "por que importa" e "forma da resposta".

E garantir que **toda** afirmação tem classificação + fonte com data/vigência.

## Fronteiras

- **NÃO é sub-modo** — é reforço transversal que se overlay no método universal ou no sub-modo ativado.
- **NÃO substitui** `pesquisa-cascata` — quando o gap é pesquisa antes da spec, ativa-se cascata + este reforço em paralelo.
- **NÃO carregar** sem citação de fonte canônica/normativa — fere a régua §0.

## Referências

- ADR-009 (decisão arquitetural).
- ADR-003 (progressive disclosure companion).
- ADR-007 (régua §0 + ex-G9/ex-G11).
- `_shared/anti-hallucination` (passo 2 validity-check).
- `_shared/confidence-classification` (passo 7).
- `_shared/high-stakes-gate` (carregar em paralelo se decisão é alto-risco).
