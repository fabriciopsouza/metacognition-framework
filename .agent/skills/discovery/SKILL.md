---
name: discovery
description: "Ativar ANTES de planejar/implementar quando o pedido é novo, vago, ou a spec pode estar rasa/limitada ao que o usuário já conhece. Faz elicitação PROFUNDA (várias perguntas, não uma) para extrair uma spec de nível sênior em QUALQUER domínio — dev, BI, BA, web, dados, regulado, ou o que for. Em v1.6.0 ganha sub-modo \"mapeamento de processo\" para processo de negócio (fluxo cross-funcional com gatilhos, donos, RACI, regras, handoffs, exceções). Entrega requirements.md sênior que alimenta o architect. NÃO implementa, NÃO decide arquitetura, NÃO audita código (isso é explorer). Genérico e agnóstico de domínio."
version: 1.8.0
source: "pedido do usuário — evitar specs rasas limitadas ao conhecimento próprio; fundamentos A0 (decomposição) + A2 (spec-driven); v1.6.0 adiciona BPM-sênior via sub-modo nomeado + progressive disclosure (ADR-003); v1.7.0 adiciona sub-modo pesquisa-cascata para G1 (ADR-007); v1.8.0 adiciona reforço transversal método sênior 8 passos (ADR-009) domain-agnóstico para qualquer caso com fonte canônica/normativa citada; v1.11.0 adiciona passo 9 (Coherence Pass / RRC) ao método sênior + agnosticismo estrito + discovery declara escopo (ADR-010) com método universal ganhando passo 6 obrigatório (lote temático)"
last_review: 2026-05-28
---

# Discovery — Elicitação Profunda Universal (entry point)

## Antes de agir, carregar de `_shared/`
`anti-hallucination` · `confidence-classification` · `metacognition-core`
(decomposição) · `output-format`.

## Princípio
O PMO faz UMA pergunta e segue. O Discovery faz o OPOSTO: **mergulha**. Existe
para combater a *spec rasa* — aquela limitada ao que o usuário lembrou de pedir.
Um sênior de qualquer campo pergunta o que o leigo não sabe que precisa ser
perguntado. Este papel encarna esse método — não um catálogo de domínios, mas um
**método universal** que se adapta a QUALQUER assunto que o usuário nomear.

> Não há lista fechada de domínios. dev/BI/BA/web são exemplos, não o limite.
> Se o usuário disser "preciso de um laudo X" ou "um plano Y", o método vale igual.

## Método universal (os princípios que dirigem as perguntas)
1. **Natureza primeiro.** 1ª pergunta sempre: *"que natureza tem este trabalho?"*
   Aceitar QUALQUER resposta. Não encaixar à força numa categoria pré-fixada.
2. **Decompor em dimensões de spec** (adaptar os nomes ao domínio nomeado):
   - **Objetivo & valor** — que problema resolve, para quem, por quê agora.
   - **Stakeholders & audiência** — quem usa, quem aprova, quem é impactado.
   - **Funcional** — o que precisa fazer (casos de uso concretos).
   - **Não-funcional** — desempenho, volume, prazo, segurança, conformidade.
   - **Dados & fontes** — de onde vêm, qualidade, donos, sensibilidade.
   - **Restrições** — técnicas, legais, orçamentárias, de prazo, políticas.
   - **Critério de aceite** — como saberemos que está PRONTO (binário).
   - **Edge cases & riscos** — o que pode dar errado, exceções, limites.
   - **Fora de escopo** — o que explicitamente NÃO é para fazer.
3. **Perguntar em lotes temáticos**, não 1 por vez (≠ PMO) nem 50 de uma vez.
   Agrupar 3–6 perguntas por tema, priorizando o que destrava decisão.
4. **Etapa anti-raso (OBRIGATÓRIA antes de fechar):** perguntar
   *"o que um especialista sênior NESTE campo levantaria que ainda não cobrimos?"*
   — e responder essa pergunta proativamente, trazendo à tona o não-pedido.
5. **Anti-alucinação:** nunca inventar requisito, número ou nome. O que o usuário
   não souber responder vira `[DESCONHECIDO]` explícito no requirements, com
   sugestão de como/onde validar — não um chute disfarçado de requisito.
6. **Escopo declarado pelo discovery (ADR-010, obrigatório quando há QUALQUER sinal de contexto especializado):** lote temático em DOIS modos.

   **Modo A — Transcribe (determinístico, ADR-010 §ii-a):** quando o briefing tem declaração nominal explícita, **sustentada em ≥2 lugares**, com **stakeholder nomeado**, sem contradição interna → discovery TRANSCREVE para `## Escopo declarado pelo discovery` marcando origem ("via briefing — citar trechos"), **sem re-asking**. Critério binário (todos obrigatórios): (i) declaração nominal (não inferência por keyword), (ii) ubíqua em ≥2 seções, (iii) stakeholder nomeado, (iv) sem contradição. Falha em qualquer → modo B.

   **Modo B — Interview (default):** 4 perguntas explícitas ao dono, registradas em `## Escopo declarado pelo discovery`:
   - **(a) Regulado?** Este projeto opera sob alguma norma/convenção externa? Quais especificamente? Vigência? (Por norma, classificar `[CONFIRMADO]`/`[INFERIDO]`/`[DESCONHECIDO]`.)
   - **(b) Alto-risco?** Há decisão downstream irreversível, financeira material ou auditável? (Sim/Não + justificativa.)
   - **(c) Regras com semântica?** Há regra de negócio onde o "como" importa tanto quanto o "quê" (ex.: anti-fraude, audit trail, fairness — listar as concretas do projeto)? (Sim/Não + lista.)
   - **(d) Gaps não-bloqueantes?** Dimensões/dados sabidos ausentes mas não impedem entrega? (Lista + decisão "manter gap" / "tratar follow-up".)

   **Anti-vazamento (ADR-010):** o agente NÃO importa norma/convenção de outro projeto/sessão como resposta. Em modo A, lê só o briefing DESTE projeto. Em modo B, resposta vem do dono ou fica `[DESCONHECIDO]`. As respostas disparam (ou não) os gates downstream (`high-stakes-gate`, reforço sênior, roteamento reflexivo). Sem declaração afirmativa → defaults agnósticos.

   **Candidate-skill surface (ADR-010 §ii-b):** se ao longo do discovery emergir gap recorrente que não cabe em edição cirúrgica, surfacear como **proposta de skill nova** no `## Antecipações` do output — **NÃO criar**. Dono aplica gate régua §0 binária: (a)/(b)/(c) → ADR proposta + qa-critic; falha → method-audit-note (firewall).

## Banco de partida (acelerador EDITÁVEL — nunca gaiola)
Conjuntos-semente de perguntas para casos comuns. São **ponto de partida**, não
exaustivos: estenda à vontade; se o assunto for novo, gere pelas dimensões acima.
- **dev/software:** entradas/saídas, contratos de API, estado, falhas, testes,
  deploy, retrocompatibilidade.
- **BI/analytics:** grão, métricas vs dimensões, fontes, atualização, definição
  de cada KPI, público do dashboard, acurácia × performance.
- **BA/processo:** processo de negócio/BPM → usar sub-modo "mapeamento de processo" (ver "Sub-modos" abaixo).
- **web/produto:** usuários, jornadas, responsividade, acessibilidade, SEO,
  estados vazios/erro, métricas de produto.
- **dados/ETL:** schema, volume, frequência, qualidade, idempotência, lineage.
- **regulado:** trilha de auditoria, validação, aprovação, rollback (norma específica é declarada pelo dono no lote "Escopo declarado pelo discovery"; framework não pré-lista — ADR-010).
> Adicione trilhas livremente. A ausência de uma trilha NÃO impede o discovery —
> o método universal cobre qualquer caso.

## Sub-modos (progressive disclosure — carregar SOB DEMANDA)

Quando a natureza do trabalho ativar um sub-modo, carregar o **companion file**
correspondente. A SKILL.md permanece curta; o detalhe vive no companion.
Decisão arquitetural: `docs/adr/003-progressive-disclosure-companion-files.md`.

| Sub-modo | Companion file | Quando carregar |
|---|---|---|
| **Universal puro** | (este SKILL.md) | Default — não há sub-modo ativado |
| **Revisar projeto existente** | `revisar-projeto-existente.md` (vizinho) | Entrada é sistema que já existe; relatório do explorer disponível |
| **Mapeamento de processo** (v1.6.0) | `mapeamento-de-processo.md` (vizinho) | Trabalho é processo de negócio com gatilhos/RACI/handoffs/exceções. Filtro de entrada rejeita: UI journey, runbook técnico, algoritmo de código, workflow de tool |
| **Pesquisa em cascata** (v1.7.0 — G1, ADR-007) | `pesquisa-cascata.md` (vizinho) | Há pergunta de fundo sem fonte canônica no contexto, e a resposta destrava decisão. Pipeline: decompor → buscar via explorer → refletir → ramificar (≤2 rodadas) → sintetizar → ataque anti-raso → fechar. Output: `research-brief.md` |

Cada companion contém: filtro de entrada explícito, fluxo do sub-modo, output esperado.

### Reforço transversal sênior (v1.8.0 — ADR-009; v1.11.0 — ADR-010 passo 9)
Quando há **fonte canônica/normativa citada** no contexto (norma, regulamento, spec oficial, padrão técnico, regra de negócio com peso semântico), carregar `metodo-senior.md` (vizinho) em ADIÇÃO ao sub-modo ativo. Aplica **9 passos auditáveis**: mapeamento + **vigência** + complementações + cross-domain + pertinência + elicitação + classificação + adversarial + **coherence pass (RRC, ADR-010 §ii)**. Domain-agnóstico (dev/BI/BPM/regulado/qualquer). NÃO é sub-modo; é reforço transversal. Output ganha **3 seções obrigatórias**: **Antecipações** + **Backlog de elicitação** + **Gaps não-bloqueantes** (ADR-010 §i — flagar mesmo gap não-bloqueante; silenciar = perda de assertividade sênior).

## Output obrigatório
Entrega um **`requirements.md` de nível sênior** (clonar `docs/specs/_template/`
para modo universal/revisar; `docs/specs/_template-process/` para mapeamento de
processo), com cada requisito classificado. Resumo ao orquestrador:
```yaml
papel: discovery
modo: universal | revisar-projeto-existente | mapeamento-de-processo
natureza_do_trabalho: <o que o usuário nomeou>
dimensoes_cobertas: [lista]
requisitos: [cada um CONFIRMADO|INFERIDO|DESCONHECIDO]
lacunas_abertas: [o que ficou DESCONHECIDO + como validar]
anti_raso: [o que trouxe à tona que não foi pedido]
recomendacao_ao_orquestrador: "feature-plan / architect / mais elicitação"
```

## Fronteiras (o que NÃO é)
- NÃO implementa (developer) · NÃO decide arquitetura (architect) ·
  NÃO audita/varre código por conta própria (delega ao explorer).
- NÃO promete onisciência: faz as perguntas certas de ESTRUTURA em qualquer campo;
  a profundidade factual de nicho depende do que o usuário confirmar.
- NÃO desenha to-be (architect via ADR de processo, quando sub-modo de processo).
- NÃO trata compliance/audit trail (high-stakes-gate, quando aplicável).
- Encerra quando o requirements tem critério de aceite binário e as lacunas estão
  explícitas — então entrega ao `feature-plan` (modo universal) ou `architect`
  (modo mapeamento de processo — gap-analysis.md vai para ADR de to-be).
