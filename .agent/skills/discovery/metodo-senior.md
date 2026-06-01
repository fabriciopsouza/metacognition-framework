# Discovery — Reforço sênior (método em 9 passos)

> Companion do `discovery` (v1.8.0+). Progressive disclosure (ADR-003):
> carregado SOB DEMANDA quando há **fonte canônica/normativa citada** no contexto.
> Domain-agnóstico — vale para dev/BI/BPM/regulado/qualquer caso onde se cita norma,
> spec, padrão técnico ou doc oficial específico.
> Fonte: ADR-009. NÃO carregar em discovery sem citação de fonte (vira inflação — fere régua §0).

## Filtro de entrada (passo 1 — obrigatório; restritivo por design)

Ativar este reforço **apenas** quando **algum** dos critérios abaixo se verifica de forma explícita. Em dúvida, NÃO carregar (default: discovery universal).

1. **Citação de norma regulatória ou padrão técnico EXTERNO declarado pelo discovery do projeto como pertinente**. Não inclui "convenção" interna. **Domínio é declarado pelo projeto, não inferido por sinais semânticos** (ADR-010).
2. **Referência a documento OFICIAL específico**: resolução, portaria, regulamento técnico, manual oficial de fabricante, spec assinada. **NÃO inclui** contratos comerciais flexíveis, documentação interna de projeto, ou READMEs.
3. **Regra de negócio interna com peso semântico DECLARADO** pelo projeto (ex.: anti-fraude, audit trail, fairness, conformidade regulatória — a regra específica é declarada via discovery, não pré-listada aqui). **NÃO inclui qualquer regra de negócio** — só aquelas cujo impacto envolve perda financeira material ou compliance, confirmado pelo dono.
4. **Decisão downstream de alto impacto confirmada**: executiva irreversível, financeira material, regulatória/auditável.

Se nenhum se verifica → NÃO carregar. Voltar ao método universal do `SKILL.md`. Filtro permissivo demais derrota o progressive disclosure.

## Os 9 passos auditáveis (8 originais ADR-009 + passo 9 RRC ADR-010)

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

9. COHERENCE PASS (RRC, ADR-010 sub-princípio anexo ii — obrigatório
   antes de declarar "pronto") — LER todos os artefatos potencialmente
   afetados (não só os editados): ADRs vinculadas, skills relacionadas,
   CLAUDE/AGENTS/README, CHANGELOG, history "Em aberto", _shared/,
   PROMPT-CHAT-WEB, web/index.html. VERIFICAR coerência em 5 dimensões:
   (i) versões em sync, (ii) referências cruzadas válidas, (iii)
   nomenclatura consistente, (iv) contradições semânticas entre
   documentos, (v) **contagens em sync** (ex.: "N passos" igual em
   SKILL.md, companion, CLAUDE.md, AGENTS.md — falha-pattern observado
   no próprio round 2 da v1.11.0). REPORTAR em formato auditável
   binário. Inconsistência detectada = corrigir ANTES de declarar
   "pronto". Atalhar = não-sênior.
```

## Princípios anexos (parte do método sênior, não bônus)

- **Antecipação sênior é ENTREGA**, não bônus: listar pontos pertinentes que o dono **não pediu** mas pode não ter visto (premissas que mordem, riscos não-óbvios, alternativas não-avaliadas). Vai em seção dedicada do output — `research-brief.md` **§7 Antecipações + §8 Backlog de elicitação** (template `docs/specs/_template-research/`) ou seções equivalentes do `requirements.md`.
- **Crítica do MÉTODO ≠ crítica do PRODUTO** — antes de auditar o output, auditar se a discovery em si está bem-apontada (objetivo do cliente, pertinência, viés, recorte).
- **Conflito instrução-dono × canon = surface-and-reconcile** — quando o dono diz X e o canon diz Y, surfacear EXPLICITAMENTE com análise; o dono decide com meta-contexto (pode estar com entendimento mais novo que o canon).
- **Regra de negócio tem SEMÂNTICA** — anti-fraude, audit, fairness, etc. (regras concretas declaradas pelo discovery do projeto); não despriorizar regra sem entender o papel.
- **Conscious-lean** — cada output passa pelo "isso serve o objetivo, ou estou polindo o lado errado?". Lean operacional, não preguiça.

## Output esperado

Adicionar ao output base do discovery (`requirements.md` ou `research-brief.md`) **3 seções obrigatórias**:

- **§ Antecipações** — coisas que o dono não pediu mas pode não ter visto.
- **§ Backlog de elicitação** — Q1..Qn numerada, com "por que importa" e "forma da resposta".
- **§ Gaps não-bloqueantes** (ADR-010) — gaps detectados que NÃO impedem entrega mas existem: (i) descrição, (ii) impacto se não tratado, (iii) decisão registrada do dono ("manter gap" / "tratar follow-up"). **Silenciar gap não-bloqueante = perda de assertividade sênior.**

E garantir que **toda** afirmação tem classificação + fonte com data/vigência.

## Fronteiras

- **NÃO é sub-modo** — é reforço transversal que se overlay no método universal ou no sub-modo ativado.
- **NÃO substitui** `pesquisa-cascata` — quando o gap é pesquisa antes da spec, ativa-se cascata + este reforço em paralelo.
- **NÃO carregar** sem citação de fonte canônica/normativa — fere a régua §0.

## Referências

- ADR-009 (decisão arquitetural do método sênior).
- **ADR-010 (framework agnóstico — discovery declara escopo; gaps não-bloqueantes flagados).**
- ADR-003 (progressive disclosure companion).
- ADR-007 (régua §0 + ex-G9/ex-G11).
- ADR-005 (HITL via execution-modes — desacoplado de "regulado").
- `_shared/anti-hallucination` (passo 2 validity-check).
- `_shared/confidence-classification` (passo 7).
- `_shared/high-stakes-gate` (carrega SOB DECLARAÇÃO do discovery, não por sinal semântico).
