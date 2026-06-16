# web-bundles — Coaches cross-IA (planejamento em Gemini/ChatGPT, implementação no IDE)

> **GERADOS** de [`coaches.json`](coaches.json) por [`tools/build_web_bundles.py`](../tools/build_web_bundles.py) — **não editar os `.md` à mão**. Canário de drift fail-closed: [`tools/test_web_bundles.py`](../tools/test_web_bundles.py) (ADR-083).

## O que é

Cada coach é um **prompt autocontido** que carrega o método do Framework Metacognitivo (classificar confiança, file-first-por-pergunta, anti-raso sênior, anti-alucinação) focado em **um artefato de planejamento**. A ideia (padrão BMAD web-bundles, adaptado): faça o **planejamento upfront** na sua assinatura flat-rate de web LLM (Gemini/ChatGPT/Claude.ai) e traga o artefato pronto para o **IDE** (`metacognition-framework`), onde o squad implementa com gates reais. Planejamento não consome tokens metered do IDE.

## Coaches disponíveis

| Coach | Artefato |
|---|---|
| [brainstorming-coach](brainstorming-coach.md) | Mapa de ideias priorizado (divergir → convergir) |
| [product-brief-coach](product-brief-coach.md) | Product Brief de uma página (kernel de 5 campos) |
| [prd-coach](prd-coach.md) | PRD sênior (requisitos + critérios binários + riscos) |
| [prfaq-coach](prfaq-coach.md) | PRFAQ (working-backwards: press release + FAQ) |
| [ux-coach](ux-coach.md) | UX spec (fluxos + estados + casos de borda) |
| [market-and-industry-research](market-and-industry-research.md) | Brief de pesquisa com fontes graduadas (triangulação) |

## Como usar (3 passos)

1. Escolha o coach e **copie o conteúdo do `.md`**.
2. Cole como instrução: **Gemini** (Gem → Instruções), **ChatGPT** (Custom GPT → Instructions) ou **Claude.ai** (Projeto → Instruções).
3. Converse — o coach elicita em lotes, classifica confiança e entrega o artefato estruturado. Traga o resultado para o IDE.

## O que esperar (e o que NÃO)

- ✅ Método: confiança (CONFIRMADO/INFERIDO/DESCONHECIDO), elicitação sênior, anti-fabricação, [DESCONHECIDO] explícito.
- ❌ **Sem gates de runtime** — no chat não há filesystem nem execução; o método vale por **leitura**, não por mecanismo. Efeito irreversível **sempre pede sua confirmação** (anti-JARVIS: nunca finge mecanismo que o chat não executa).

## Manutenção

Editar coach = editar [`coaches.json`](coaches.json) (o **dado**) → `python tools/build_web_bundles.py` → commitar os `.md` regenerados. O canário barra qualquer `.md` fora de sync com a fonte.
