# ADR 054 — Pacote Web do framework: dois tiers + cascata como PROFILE do export-clean + doutrina enforcement.chat

- Status: **Aceito** · Data: 2026-06-02 · Decisores: dono + squad (architect)
- Onda: encarnação web (v1.40.0) · Tipo: keystone do bloco web · Atende: `docs/specs/web-package/requirements.md` v1.0.0 (REQ-PUB-*, REQ-PREM-*, REQ-SAFE-*, REQ-CASCADE-*).
- Política: NOVO. Relaciona: ADR-049 (tiers premium/baseline + marcadores `premium:start`), ADR-028 (output-style ≠ processo), ADR-005 (execution-modes), ADR-010/P12 (agnosticismo), incidente 2026-05-31 (anonimização-gate no export). Sucede de fato o `PROMPT-CHAT-WEB-v4.3.md` (que para de ser editado à mão).

## Contexto

O chat web é servido hoje por um único `PROMPT-CHAT-WEB-v4.3.md`, editado à mão, que **recopia** regras das skills, **defasa** (escrito contra v1.22.0/v2.2 enquanto o main está v1.39.0/v2.3) e **não tem tier público**. A spec (discovery) pede uma encarnação web paritária-em-resultado, em dois tiers, que **nunca divirja** do main. Restrição-raiz (REQ-SAFE): o web é a porta por onde decisão regulada passa **sem** os gates mecânicos da IDE — tratar o chat como se tivesse as salvaguardas da IDE é o risco a mitigar.

Descoberta que muda o desenho (file-first nesta sessão): o `export-clean.py` **já é um motor de profiles** (premium × baseline, com `<!-- premium:start -->` e listas de strip). Logo a "cascata main→web" não é infra nova.

## Decisão (1 frase ativa)

Construir o pacote web como **dois tiers** (público = 1 prompt autocontido sem skills; premium = orquestrador enxuto + skills planas referenciadas), gerados por um **terceiro PROFILE (`web`) do `export-clean.py` existente** (não um pipeline paralelo), publicados num **repo dedicado `metacognition-framework-web`** (análogo ao `-public`, sentido único main→web, não-editável-à-mão), sob a doutrina inviolável **`enforcement.chat`**: onde a IDE *barra* (hook/gate), o web *declara* um checkpoint + ressalva de ambiente — **nunca finge mecanismo (anti-JARVIS)**.

## Alternativas consideradas

**Eixo A — como gerar (o crux régua §0):**
1. **Pipeline web paralelo** (novo script dedicado). Duplica leitura de skills, anonimização e o gate sensível. **Rejeitada — adição pura (régua §0).**
2. **Edição manual continuada do PROMPT-CHAT-WEB.** É o status quo que causa a defasagem. **Rejeitada.**
3. **Profile `web` no `export-clean.py` (ESCOLHIDA).** Reusa strip-lists, marcadores premium e o gate `--sensitive`. Adiciona só as transformações web (remover executáveis, gate→checkpoint, consolidar discovery, injetar `## Encadeamento`, condensar público). Net-gain: estende um `if`, não cria pipeline.

**Eixo B — onde publicar:**
1. **Subpasta/branch do `-public`.** Menos infra, mas mistura dois produtos de natureza distinta (arquivos vs prompts colaveis) e confunde o usuário. **Rejeitada.**
2. **Repo dedicado `-web` (ESCOLHIDA).** Espelha o padrão `-public` já existente; descoberta limpa; mesma regra "gerado, não editar à mão". Custo aceito: +1 repo + +1 workflow (barato, padrão conhecido).

**Eixo C — paridade:**
1. **Paridade de mecanismo** (simular hooks/subagentes no chat). É o anti-padrão JARVIS — finge salvaguarda inexistente. **Rejeitada — proibida por REQ-SAFE-1.**
2. **Paridade de RESULTADO com mecanismo declarado (ESCOLHIDA).** Mesmo método/papéis/junções; gate vira checkpoint declarado + ressalva. Honestidade > ilusão de equivalência.

## Consequências

**Positivas:** (a) web deixa de defasar — versão carimbada do main em cada artefato (REQ-CASCADE-5); (b) zero duplicação prompt×skill no premium (REQ-PREM-1) e zero pipeline novo (régua §0); (c) tier público dá "melhor que o comum" sem instalar nada; (d) a doutrina `enforcement.chat` impede o pacote de mentir gate em contexto regulado. **Negativas/limite declarado:** o chat **não** tem isolamento real de subagente, heterogeneidade de modelo no QA, hooks/audit automático nem progressive disclosure — isso é **degradação declarada** (REQ-SAFE-3), não disfarçada; o efeito T3 (irreversível+alto impacto) permanece em confirmação informada em qualquer postura (REQ-MODE-1). **Bloqueio downstream:** GAP-1 (as "4 skills-base web" existem? — confirmar com o dono) gate o `developer`; GAP-3/4 (token público real, paridade Gemini) ficam para eval na implementação.

## ADRs derivados (este é o keystone; os demais detalham)

- **ADR-055** — desambiguação do namespace "avançado" (eixo execução × eixo profundidade-de-discovery) + regra anti-silêncio-de-stake no qa-critic (REQ-SAFE-2). *Pendente desta sessão.*
- **ADR-056** — regra de consolidação skill+companions para chat (§5.1) + injeção determinística de `## Encadeamento (chat)` a partir de `consumes`/`produces`/`role_order` (REQ-CASCADE-3.iv). *Pendente.*
- **ADR-057** — contrato do profile `web` do `export-clean.py` + ordem da cascata + carimbo de versão/consistency-gate (REQ-CASCADE-3/5/6). *Pendente (depende de detalhe de implementação do build).*

## Implementação (ponteiro — NÃO neste ADR; é decisão, não código)

- Spec: `docs/specs/web-package/requirements.md`. Build: estender `tools/export-clean.py` com `--profile web`. Repo destino: `metacognition-framework-web` (criar quando o `developer` começar). DONE-do-architect quando: ADR-054 + 055 + 056 + 057 aceitos e o `developer` tem critério binário. Eval antes de declarar suporte Gemini (NFR-1).
