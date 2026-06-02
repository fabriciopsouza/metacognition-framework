# requirements.md — Pacote Web do Framework Metacognitivo (prompt + skills)

> **Tipo:** spec sênior (saída de `discovery`, entrada de `architect`).
> **Produto:** `metacognition-framework-web` — encarnação do framework para ambientes sem filesystem (Claude.ai, Gemini), em dois tiers (público / premium).
> **Princípio fundador:** mesmo método, mesmos resultados, mecanismo diferente. Onde a IDE *mecaniza* (hooks, gates, runtime), o chat *declara* (instrução de leitura encadeada, checkpoint declarado). Fingir mecanismo que não existe é o anti-padrão JARVIS — proibido.
> **Versão da spec:** 1.0.0 · **Idioma:** PT-BR · **Licença:** CC BY 4.0
> **Base verificada:** repo `metacognition-framework-public` v1.22.0 (roteador v2.3); skills `_shared`/papéis anexadas; `discovery` v1.9.0 + 4 companions; `PROMPT-CHAT-WEB-v4.3.md`.

> **── NOTA DE RECONCILIAÇÃO (PMO/architect, 2026-06-02) ──**
> Esta spec foi recebida do dono e versionada VERBATIM (traceability). File-first contra o estado real do main
> revelou que as premissas de versão estão defasadas (a spec foi escrita contra um snapshot v1.22.0):
> - **Base real:** main **v1.39.0** (não v1.22.0). Roteador **v2.3** (a spec já citava v2.3 no corpo; o "v2.2" do diagnóstico §1 está superado).
> - **`discovery`:** **v1.10.0** (não v1.9.0) — bump de 2026-06-02 integrando o reparo do método sênior (ADR-051).
> - **GAP-2 parcialmente fechado:** o build de cascata (`tools/export-clean.py`) FOI inspecionado — já é um motor de
>   *profiles* (premium × baseline) com marcadores `<!-- premium:start -->` e listas de strip. A cascata web é um
>   **terceiro profile**, não um pipeline paralelo (vira insumo do ADR-054, alinhado à régua §0).
> A ARQUITETURA da spec permanece válida; só os carimbos de versão e o status do GAP-2 mudam. ADRs em `docs/adr/054+`.

---

## 0. Escopo declarado pelo discovery (ADR-010)

Lote temático respondido na origem deste pedido (modo Interview):

- **(a) Regulado?** SIM — o framework serve, entre outros, ambiente farmacêutico (ANVISA, GAMP 5, ALCOA+, 21 CFR Part 11/Annex 11). A spec do pacote web NÃO hardcoda nenhuma dessas normas (P12/ADR-010); ela garante o **mecanismo** (audit trail declarado, validação por risco) e deixa a norma ser declarada por projeto. `[CONFIRMADO]`
- **(b) Alto-risco?** SIM — o pacote web é a porta pela qual decisões reguladas/executivas passarão sem os gates mecânicos da IDE. O risco-raiz desta spec é **falsa equivalência**: o usuário tratar o chat como se tivesse as salvaguardas da IDE. Mitigação é requisito de primeira classe (REQ-SAFE-*). `[CONFIRMADO]`
- **(c) Regras com semântica?** SIM — anti-alucinação, preservação de trabalho aprovado, e a doutrina `enforcement.chat` (declarar ≠ fingir gate) são regras onde o "como" importa tanto quanto o "quê". `[CONFIRMADO]`
- **(d) Gaps não-bloqueantes?** Listados em §11. `[CONFIRMADO]`
- **(e) Alimenta outra sessão/agente?** SIM — esta spec é insumo direto do `architect` e do `developer` do framework. Pacote de handoff em §12. `[CONFIRMADO]`
- **(f) `product_type`?** `spec` (este documento) que culmina em `data-pipeline` de geração + `report`-artefatos (os prompts/skills web). `[CONFIRMADO]`

---

## 1. Objetivo & valor

**Problema que resolve:** o framework existe em dois mundos (IDE/SDK com filesystem; chat web sem). Hoje o chat web é servido por um único arquivo (`PROMPT-CHAT-WEB-v4.3.md`) que **recopia inline** regras que já vivem nas skills `_shared/`, está **defasado** (roteador v2.2 vs v2.3 do main; sem `discovery`; URL canônica apontando para repo errado) e **não tem tier público** (quem não tem skills instaladas não tem encarnação dedicada). `[CONFIRMADO — diagnóstico desta sessão]`

**Valor entregue:**
1. Uma encarnação web **paritária em resultado** com a IDE, não em mecanismo.
2. **Dois tiers**: público (sem skills — só o prompt) e premium (prompt + skills instaladas).
3. **Propagação em cascata** que mantém web e não-web sincronizados a partir de uma fonte única, eliminando a defasagem manual atual.

**Para quem:** (i) usuário público do Claude.ai/Gemini sem nada instalado; (ii) usuário premium com as skills do framework instaladas; (iii) o mantenedor, que precisa que web nunca divirja do núcleo.

---

## 2. Stakeholders & audiência

| Ator | Papel | Stake |
|---|---|---|
| Usuário público (sem skills) | consome só o prompt colado | precisa de algo "melhor que o comum" sem instalar nada |
| Usuário premium (com skills) | consome prompt + skills referenciadas | precisa de paridade-de-resultado com a IDE |
| Mantenedor / `docops` | gera e propaga | precisa que a cascata seja determinística e auditável |
| `architect` / `developer` do framework | consome esta spec | precisa de critério de aceite binário para construir |

---

## 3. Arquitetura de tiers (decisão central)

A spec define **dois produtos web**, não um. A diferença é o que o ambiente oferece, não a doutrina.

### 3.1 Tier PÚBLICO — `prompt-web-publico`
- **O que é:** um único arquivo de prompt, colável em "Instruções para o Claude" ou no início de um chat, **sem dependência de skills instaladas**.
- **Autocontido:** todo o transversal essencial (anti-alucinação, classificação de confiança, preservação, validação, anti-loop, roteamento por contexto×complexidade) vive **inline**, condensado.
- **Degradação consciente:** declara explicitamente, ao usuário, o que NÃO tem (sem isolamento real de subagente, sem heterogeneidade de modelo no QA, sem hooks/audit automático, sem progressive disclosure). "Melhor que o comum" = método metacognitivo + classificação + anti-alucinação + QA adversarial declarado. **Não promete** o que não pode cumprir.
- **Tamanho:** alvo ≤ ~12k tokens (cabe num campo de instruções sem estourar). Critério em REQ-PUB-3.

### 3.2 Tier PREMIUM — `prompt-web-premium` + conjunto de skills web
- **O que é:** um prompt-orquestrador **enxuto** (não recopia regra — *referencia* skill) + um conjunto de skills `.md` planas instaladas no Claude.ai.
- **Mecanismo de orquestração:** instrução de leitura encadeada (ver §4). O prompt diz "quando X, aplique a skill Y"; cada skill diz qual vem depois.
- **Paridade-de-resultado com a IDE:** mesmos papéis, mesmas junções, mesmo método sênior, mesma classificação — com mecanismo declarado em vez de mecanizado.

### 3.3 O que os DOIS tiers compartilham (invariante)
- A doutrina `enforcement.chat`: gate vira checkpoint declarado.
- A matriz de ambiente honesta (o que o chat não tem).
- A precedência de instruções (§7 do prompt).
- A classificação de confiança e o anti-alucinação como invioláveis.

---

## 4. Mecanismo de orquestração no chat (o "como funciona")

> Esta é a decisão de design mais importante e deve ser replicada em TODA skill do pacote.

**Na IDE:** um hook executa "se condição então carrega/barra". Determinístico, fora do modelo.

**No chat:** não há runtime. A orquestração é **instrução imperativa em prosa, lida pelo modelo**:
- "Ativação" de skill = o modelo lê seu pedido, casa com a *descrição* da skill, e lê o corpo dela. (roteamento por intenção lida)
- "Encadeamento" = cada skill **termina declarando a próxima** e sob qual condição. Ex.: a skill `developer` termina com *"Ao concluir, NÃO trate como final: aplique `qa-critic` antes de qualquer aprovação."* O modelo cumpre porque leu, não porque um runtime barrou.
- "Gate" = **checkpoint declarado**: a skill afirma *"não avance até X"* e rotula o efeito (ex.: "⚠ E1/E2 irreversível — exige confirmação informada do dono"). É higiene declarada, não enforcement.

**Regra de redação obrigatória para o pacote:** toda skill do pacote web encerra com uma seção `## Encadeamento (chat)` que nomeia: (i) a(s) skill(s) seguinte(s), (ii) a condição de transição, (iii) o checkpoint declarado se houver. Sem essa seção, a skill não passa no QA da spec.

---

## 5. Estrutura de consolidação (o que vira o quê)

> Fronteira derivada do caso `discovery` (decidido nesta sessão): **um arquivo por unidade-de-orquestração**; `_shared` atômico; consolidar variações de um mesmo papel, separar papéis distintos.

### 5.1 Regra de consolidação
- **CONSOLIDAR** quando os arquivos são **um papel + suas variações/reforços** que se roteiam internamente (ex.: `discovery` + 4 companions → 1 arquivo, porque o progressive disclosure perde propósito no chat e fragmentar cria companions órfãos).
- **MANTER SEPARADO** quando são **papéis distintos do pipeline** (pmo, architect, developer, qa-critic, docops, explorer) — chamam-se *entre si* por encadeamento; cada um dispara pelo próprio gatilho de intenção.
- **`_shared` ATÔMICO** — anti-hallucination, confidence-classification, traceability, output-format, action-safety, high-stakes-gate, observability, metacognition-core: cada um permanece arquivo único, referenciado por todos (nunca recopiado — preserva single-source-of-truth).

### 5.2 Mapa de arquivos do pacote PREMIUM web

**Núcleo `_shared` (8 arquivos — portados da IDE com ajuste de ambiente):**
- `anti-hallucination` · `confidence-classification` · `traceability` · `output-format` · `metacognition-core` · `action-safety` · `high-stakes-gate` · `observability`

**Papéis (7 arquivos — portados, encadeados):**
- `pmo` · `discovery` (CONSOLIDADO: SKILL v1.9.0 + 4 companions + elicitation-dimensions inline) · `architect` · `developer` · `qa-critic` · `docops` · `explorer`

**Orquestrador:**
- `prompt-web-premium` (raiz — enxuto, referencia as skills acima)

**NÃO portar para o pacote web (inertes no chat — registrar a exclusão, não silenciar):**
- `execution-modes` — depende de `~/.claude/settings.json`, hooks PowerShell, companions `.json`. Sem runtime no chat. **Substituto:** o conceito de "modo de execução" vira uma **declaração textual de postura** no prompt (default/avançado/autosuficiente como *nível de confirmação que o usuário pede*), não um state file. Ver REQ-MODE-1.
- `doc-intake` — depende de `tools/doc_intake.py` (Python runtime). No chat, ingestão de documento usa a leitura nativa do modelo sobre anexos. **Substituto:** instrução no `discovery` de citar proveniência do anexo (nome + trecho) em vez de sha256 de chunk.
- Todos os `tools/*.py`, `*.ps1`, `default.json` etc. — companions executáveis não existem no chat.

### 5.3 Tier PÚBLICO
- **1 arquivo só:** `prompt-web-publico`. Condensa inline o essencial dos 8 `_shared` + roteamento. NÃO referencia skills (não há). Declara degradação.

---

## 6. Requisitos funcionais (REQ-*)

### Tier público
- **REQ-PUB-1** — O prompt público deve operar sem nenhuma skill instalada, produzindo: classificação de confiança ([CONFIRMADO]/[INFERIDO]/[DESCONHECIDO]), postura anti-alucinação (NÃO SEI direto), decomposição metacognitiva, validação antes de entregar, anti-loop, e QA adversarial declarado em decisão sensível. **Aceite:** um pedido técnico sensível recebe classificação + validação + ressalva, sem skill alguma.
- **REQ-PUB-2** — Deve declarar ao usuário, em ≤3 linhas no início, o que é o tier público e o que ele NÃO tem (sem subagente real, sem audit automático), oferecendo o caminho premium. **Aceite:** a declaração existe e é factualmente correta contra a matriz de ambiente.
- **REQ-PUB-3** — Caber em ≤ ~12k tokens. **Aceite:** contagem de tokens do arquivo final ≤ limite; se exceder, cortar profundidade de domínio antes de cortar transversal.

### Tier premium
- **REQ-PREM-1** — O prompt premium NÃO recopia regra transversal; **referencia** a skill por nome e instrui o modelo a aplicá-la. **Aceite:** zero duplicação de conteúdo normativo entre prompt e skills (um diff prompt×skill não acha parágrafos repetidos de anti-alucinação/validação/etc.).
- **REQ-PREM-2** — Toda skill encerra com `## Encadeamento (chat)` (ver §4). **Aceite:** as 15 skills têm a seção; cada uma nomeia próxima skill + condição.
- **REQ-PREM-3** — `discovery` consolidado roteia internamente entre universal / revisar-projeto / mapeamento-de-processo / pesquisa-cascata / reforço-sênior, por filtro de entrada em prosa no topo. **Aceite:** os 5 filtros de entrada estão presentes e mutuamente exclusivos/priorizados; um pedido de cada tipo cai no ramo certo.
- **REQ-PREM-4** — O pipeline encadeia pmo → discovery → architect → developer → qa-critic → docops, com explorer chamável para leitura. **Aceite:** seguir o encadeamento de um pedido multi-etapa do início ao fim sem buraco (cada papel aponta o próximo).

### Modo de execução (substituto do execution-modes)
- **REQ-MODE-1** — O prompt declara três posturas de confirmação (default = confirma antes de avançar; avançado = confirma só alto-impacto; autosuficiente = avança e reporta) como **escolha textual do usuário**, NÃO como state file. Em qualquer postura, o **efeito T3** (irreversível + alto impacto) permanece em confirmação informada — a postura afrouxa só a confirmação de baixo risco. **Aceite:** mudar de postura muda a cadência de confirmação mas nunca dispensa o checkpoint de efeito T3.

---

## 7. Requisitos de segurança / honestidade (REQ-SAFE-*) — não-negociáveis

- **REQ-SAFE-1 (anti-JARVIS)** — Nenhum arquivo do pacote pode chamar de "gate"/"bloqueio"/"barra" um mecanismo que o chat não executa. Onde a IDE barra, o texto web diz "checkpoint declarado — exige confirmação informada; não há enforcement automático". **Aceite:** busca textual por "barra/bloqueia/gate determinístico" no pacote web só acha ocorrências acompanhadas da ressalva de ambiente.
- **REQ-SAFE-2 (resolução da colisão "avançado")** — O pacote resolve, via nota explícita, a colisão de namespace diagnosticada: "avançado" é termo do **eixo modo-de-execução**; o eixo profundidade-de-discovery usa "universal/reforço-sênior", nunca "avançado". E declara a propriedade contraintuitiva: **subir o modo de execução afrouxa a validação humana do método sênior** — logo, em postura autosuficiente, a decisão "este caso não tem stake → não aplico método sênior" é um **achado registrado e atacável** pelo qa-critic, não um silêncio. **Aceite:** a nota existe no prompt e no `discovery`; o qa-critic tem a regra de atacar a ausência-de-stake em postura autosuficiente.
- **REQ-SAFE-3 (degradação declarada)** — A matriz de ambiente (o que o chat não tem) aparece em local canônico do pacote e é referenciada, não recopiada. **Aceite:** existe uma seção única "Matriz de ambiente"; skills apontam para ela.
- **REQ-SAFE-4 (regulado sem hardcode)** — Nenhuma norma setorial aparece hardcoded em nenhum arquivo do pacote (P12/ADR-010). O mecanismo regulado (`high-stakes-gate`, audit declarado) é genérico; a norma é declarada por projeto. **Aceite:** `check_core_agnostic` (ou equivalente de revisão) não acha termo de domínio/norma no pacote web.

---

## 8. Requisitos da cascata de propagação (REQ-CASCADE-*) — o coração do "atualizar como os demais"

### 8.1 Topologia da cascata
> O usuário declarou: a cascata para os não-web já existe (main → premium → noadmin → premium ...). A spec ADICIONA os nós web, sem inverter o sentido: **a fonte é sempre o repo privado/main; web é destino, nunca origem.**

```
metacognition-framework (PRIVADO / main)  ← ÚNICA fonte de verdade (SSoT)
        │  (build/sanitização automática — já existe para os não-web)
        ├─→ metacognition-framework-public            (não-web público)   [JÁ EXISTE]
        ├─→ <distribuições não-web premium/noadmin>                        [JÁ EXISTEM]
        │
        └─→ metacognition-framework-web (NOVO repo dedicado)
                ├─→ tier PÚBLICO   (prompt-web-publico)         — gerado, sanitizado
                └─→ tier PREMIUM   (prompt-web-premium + skills) — gerado, sanitizado
```

- **REQ-CASCADE-1 (repo dedicado)** — Criar repositório separado `metacognition-framework-web` (análogo ao `-public`), gerado automaticamente do main, **nunca editado à mão** (mesma regra do `-public`: "gerada automaticamente do repo privado; não editar a mão"). **Aceite:** o repo web tem o aviso "não editar a mão" e um workflow que o regenera.
- **REQ-CASCADE-2 (sentido único)** — A geração é sempre main → web. Correção de bug detectado no web vira issue/PR no **main**, depois propaga. **Aceite:** não existe caminho de escrita web → main; a doutrina single-source-of-truth é preservada.
- **REQ-CASCADE-3 (transformação determinística)** — O build web aplica transformações determinísticas sobre as skills do main: (i) remove companions executáveis (`*.py`, `*.ps1`, `*.json`); (ii) substitui "hook/gate determinístico" por "checkpoint declarado + ressalva de ambiente"; (iii) consolida `discovery` + companions num arquivo; (iv) injeta `## Encadeamento (chat)` derivado dos campos `consumes`/`produces`/`role_order` do front-matter de cada skill; (v) gera o tier público condensando os `_shared`. **Aceite:** rodar o build 2× sobre o mesmo main produz output idêntico (determinismo); cada transformação é rastreável a uma regra.
- **REQ-CASCADE-4 (sanitização premium/público)** — A mesma lógica de blocos `<!-- premium:start --> ... <!-- premium:end -->` que o framework já usa (visto em `discovery` v1.9.0, ADR-049) governa o que entra no tier premium-web vs. público-web. **Aceite:** blocos `premium` não aparecem no tier público; aparecem no premium.
- **REQ-CASCADE-5 (versão em sync — anti-defasagem)** — O build carimba a versão do main em cada artefato web gerado. Um web nunca declara versão diferente do main que o gerou. Isto mata o bug atual (prompt v4.3 / roteador v2.2 enquanto main está v1.22.0 / v2.3). **Aceite:** `consistency-gate` (ou equivalente) falha se a versão web ≠ versão main do commit que gerou.
- **REQ-CASCADE-6 (ordem da cascata)** — A propagação respeita a ordem declarada: main atualiza → premium (não-web) → noadmin → ... → **web premium → web público** (web por último, pois é o mais derivado/condensado). **Aceite:** o workflow executa os estágios na ordem; um estágio só roda se o anterior passou.

### 8.2 Tabela de geração por origem→destino

| Artefato no main | Tier público web | Tier premium web | Transformação |
|---|---|---|---|
| `_shared/*` (8) | condensado inline no prompt público | portado como skill, ajuste de ambiente | sanitiza executável; adiciona ressalva chat |
| papéis (7) | resumidos no roteamento do prompt público | portados como skills encadeadas | injeta `## Encadeamento (chat)` |
| `discovery` + 4 companions | resumo do método universal no prompt público | 1 skill consolidada | funde companions; roteador interno em prosa |
| `execution-modes` | postura textual de confirmação | postura textual de confirmação | NÃO porta state file; vira declaração |
| `doc-intake` | leitura nativa de anexo | leitura nativa de anexo | NÃO porta Python; vira instrução de proveniência |
| `PROMPT-CHAT-WEB-v4.3` | substituído por `prompt-web-publico` | substituído por `prompt-web-premium` | reescrito sob esta spec; para de recopiar |

---

## 9. Requisitos não-funcionais

- **NFR-1 (portabilidade Gemini)** — O pacote deve funcionar em Claude.ai e Gemini. Como Gemini não tem o sistema de skills do Claude.ai, o tier premium degrada para "colar o prompt premium + as skills concatenadas como contexto". **Aceite:** o prompt premium declara como operar em ambiente sem instalação de skills.
- **NFR-2 (tamanho premium)** — Skills individuais ≤ ~5k tokens cada (progressive disclosure perdido; manter enxuto). **Aceite:** nenhuma skill web excede o limite; se exceder, dividir por papel, não por companion.
- **NFR-3 (legibilidade)** — Anti over-formatting (regra `output-format`): sem ASCII boxes, emoji só funcional, listas só com ≥3 itens, tabelas só quando comparam. **Aceite:** revisão visual passa.
- **NFR-4 (auditabilidade da geração)** — Cada commit no repo web carrega: commit-sha do main de origem, versão, e changelog da transformação. **Aceite:** `git log` do web rastreia ao main.

---

## 10. Critérios de aceite globais (binários — o "garanta o resultado")

O pacote está PRONTO quando TODOS verdadeiros:

1. **[ ]** Tier público opera sem skills e entrega método metacognitivo + classificação + anti-alucinação + QA declarado (REQ-PUB-1..3).
2. **[ ]** Tier premium tem 16 arquivos (8 `_shared` + 7 papéis + 1 orquestrador), zero duplicação prompt×skill (REQ-PREM-1).
3. **[ ]** Toda skill premium tem `## Encadeamento (chat)` válido (REQ-PREM-2).
4. **[ ]** `discovery` consolidado roteia os 5 ramos corretamente (REQ-PREM-3).
5. **[ ]** Pipeline encadeia ponta a ponta sem buraco (REQ-PREM-4).
6. **[ ]** Nenhum "gate" mentido; toda mecânica IDE-only carrega ressalva de ambiente (REQ-SAFE-1, 3).
7. **[ ]** Colisão "avançado" resolvida + regra anti-silêncio-de-stake no qa-critic (REQ-SAFE-2).
8. **[ ]** Zero norma hardcoded (REQ-SAFE-4).
9. **[ ]** Repo `metacognition-framework-web` dedicado, gerado, não-editável-à-mão, sentido único (REQ-CASCADE-1, 2).
10. **[ ]** Build determinístico, versão em sync com main, ordem de cascata respeitada (REQ-CASCADE-3, 5, 6).
11. **[ ]** Funciona em Gemini com degradação declarada (NFR-1).

---

## 11. Gaps não-bloqueantes (ADR-010 — declarados, não silenciados)

- **GAP-1** — As "4 skills-base já reescritas para web" mencionadas pelo usuário em sessão anterior **nunca foram recebidas**. Esta spec assume que NÃO existem e que o framework as gerará a partir do main via cascata. *Impacto se errado:* se elas existem, o build deve usá-las como molde em vez de gerar do zero. *Decisão registrada:* tratar como follow-up — confirmar com o dono antes do `developer` começar.
- **GAP-2** — O mecanismo exato de geração automática dos não-web (o "build/sanitização que já existe") não foi inspecionado nesta sessão (é privado). A spec assume que ele é extensível para os nós web. *Impacto:* se o build atual for rígido, pode precisar de refactor. *Decisão:* `explorer` audita o build privado antes do `architect` decidir REQ-CASCADE-3. — **[RECONCILIADO 2026-06-02: build inspecionado; `export-clean.py` já é motor de profiles premium/baseline com strip-lists e `<!-- premium:start -->`; extensível por um profile `web`. GAP rebaixado.]**
- **GAP-3** — Limite de tokens do tier público (~12k) é `[INFERIDO]` de campos de instrução típicos; não medido contra o limite real do Claude.ai/Gemini. *Decisão:* `developer` valida contra o limite real na implementação.
- **GAP-4** — Paridade Gemini é `[INFERIDO]`; o comportamento de Gemini com prompts longos + "skills concatenadas" não foi testado. *Decisão:* eval-set dedicado (NFR-1) antes de declarar suporte.

---

## 12. Pacote de handoff cross-sessão (ADR-012 — esta spec alimenta o architect)

- **Artefato consumível:** este documento (`SPEC-metacognition-framework-web.md` v1.0.0).
- **Localização:** entregue nesta sessão; deve ser versionado em `docs/specs/web-package/requirements.md` no main.
- **Próximo papel:** `architect` — produzir ADRs para: (i) criação do repo `-web` dedicado; (ii) extensão do build de cascata (REQ-CASCADE-3); (iii) resolução da colisão "avançado" (a desambiguação que ficou pendente da sessão anterior); (iv) regra de consolidação de skills (§5.1).
- **Prompt pronto-para-colar para o architect:**
  > "Você é o architect. Leia `docs/specs/web-package/requirements.md`. Produza os ADRs (MADR, ≥3 alternativas cada) para: criação do repo web dedicado, extensão do build de cascata main→web, desambiguação do namespace 'avançado' (eixo execução × eixo discovery), e a regra de consolidação skill+companions para chat. Cada ADR referencia o REQ que atende. Não implemente — decida e registre."
- **Pendências herdadas:** GAP-1 (confirmar inexistência das 4 skills-base), GAP-2 (auditar build privado via explorer).
- **Premissa herdada:** a cascata é sentido-único main→web; web nunca é fonte.

---

## 13. Fora de escopo (o que esta spec NÃO cobre)

- A **redação** dos prompts e skills finais (isso é `developer`, depois desta spec aprovada).
- O **desenho to-be** do build de cascata (isso é `architect` via ADR).
- Qualquer **norma de domínio** concreta (declarada por projeto, nunca aqui).
- O sistema de skills do Claude.ai em si (infra da Anthropic, fora do controle do framework).
- Migração dos chats/históricos existentes para o novo pacote.
