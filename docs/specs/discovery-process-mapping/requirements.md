# requirements.md — Extensão `discovery` v1.6.0: sub-modo "mapeamento de processo"

> Spec produzida pelo papel **discovery** (auto-elicitação meta) seguindo o
> método universal de `.agent/skills/discovery/SKILL.md` v1.5.0. Os 4 lotes
> temáticos foram conduzidos com a etapa anti-raso obrigatória aplicada.
> NÃO IMPLEMENTAR ainda — esta entrega vai para `architect` decidir o desenho
> e depois para `developer`.

## Identificação

- **Caso/feature:** estender o papel `discovery` com capacidade explícita de **mapeamento de processo** (fluxo de atividades, gatilhos, I/O por etapa, RACI, handoffs, as-is + gap-analysis).
- **Indicador/objeto:** versão do framework alvo = **v1.6.0** (bump MINOR, aditivo).
- **Recorte:** alteração ao papel `discovery` (`.agent/skills/discovery/SKILL.md`), template `docs/specs/_template-process/` (novo), roteador (`AGENT-FRAMEWORK.md`), eval (`_meta/eval-results-papeis.md`), ADR-002.
- **Confiança da tarefa:** **MÉDIA** — escopo bem definido em 4 lotes; modo prospectivo (sem dor vivida) é o vetor de incerteza residual.
- **Revisão adversarial aplicada:** este spec passou por `qa-critic` (12 gaps fechados) + `explorer` (4 oportunidades adjacentes incorporadas). Critério de aceite expandido de 8 → **12 itens** após a revisão; ver seção **Revisão adversarial** logo abaixo.

## Revisão adversarial — gaps fechados e oportunidades incorporadas

Aplicada após a v0 do spec, em 2026-05-25. Resumo dos achados:

**12 gaps corrigidos inline** (3 BLOQUEADORES, 6 MÉDIOS, 3 MENORES):

| # | Sev | Resumo | Onde foi fechado |
|---|---|---|---|
| 1 | BLOQ | NF1 (parseável) × NF4/NF5 (notação/formalidade plugável) — persona 4 podia receber output não-parseável | NF1 reforçado + nova EARS-WH3 |
| 2 | BLOQ | Persona 4 + A4 (validação stakeholder) sem mecanismo de escalação | Nova EARS-I5 |
| 3 | BLOQ | Critério item 1 (e 2, 4, 5) era adjetivado, não-binário | Critério de aceite refeito com seções nomeadas exatas |
| 4 | MÉD | `_template-process/` marcado `[CONFIRMADO]` sem existir | Reclassificado `[A CRIAR — pelo developer]` |
| 5 | MÉD | "Sweep leve" da linha BA/processo sem texto literal | NF3 ganhou texto antes/depois |
| 6 | MÉD | R2 mitigação adjetiva ("M2 mínimo") | Matriz MUST especifica subconjunto exato por modo `quick` |
| 7 | MÉD | OUT O2 (to-be) com handoff vago para architect | Template `gap-analysis.md` ganha seção MUST `## Itens para architect` |
| 8 | MÉD | Eval H+H' com contagem aberta | Fixado em 18 casos (paridade direta com G+G') |
| 9 | MÉD | Sweep "BA/processo" sem ADR explícito | Escopo do ADR-002 inclui mudança subtrativa com texto antes/depois |
| 10 | MEN | EARS-W5 "em paralelo" sem protocolo de sincronização | W5 refinado: define single-thread vs persona 4 |
| 11 | MEN | `exemplos/H1-farma-...` marcado `[CONFIRMADO]` sem existir | Reclassificado `[A CRIAR — pelo developer]` |
| 12 | MEN | Lacunas abertas com framing contraditório | Reformulado |
| + | MÉD | NF7 ("paridade global automática") era enganoso — hook só sync skill | NF7 corrigido: explicita escopo |

**4 oportunidades adjacentes incorporadas ao escopo da v1.6.0** (decisão maximalista após revisão):

| # | Oportunidade | Tratamento em v1.6.0 |
|---|---|---|
| O1 | Divergência de versão da skill (`frontmatter: 1.0.0` vs CHANGELOG `1.5.0`) | Corrigir frontmatter: `1.0.0` → `1.5.0` → `1.6.0`. Vira item 9 do critério de aceite |
| O2 | Template ADR (`docs/adr/000-template.md`) ainda instrui hash de commit (contraria lição do ADR-001) | Atualizar 000-template.md proativamente: ponteiro padrão = branch+data+grep. Vira item 10 do critério |
| O3 | Sub-modo "revisar projeto existente" (v1.5.0) sem filtro formal de ativação — assimétrico com o novo | Harmonizar: criar filtro de entrada para "revisar" também em v1.6.0. Vira item 11 do critério |
| O4 | Pasta `docs/specs/discovery-process-mapping/` sem `validation.md` (template padrão inclui) | Criar `validation.md` com gabarito de validação dos 12 itens do critério. Vira item 12 do critério |

## Resumo executivo (1 parágrafo)

Discovery v1.5.0 elicita por **dimensões genéricas** (objetivo, stakeholders, funcional, não-funcional, dados, restrições, aceite, edge cases, fora de escopo). A trilha "BA/processo" do banco de partida existe mas é **rasa** — uma linha com 6 termos. Quando o trabalho do usuário é de fato um **processo de negócio** (fluxo cross-funcional com gatilhos, donos, regras, handoffs, exceções), o método universal sozinho não convoca o vocabulário sênior de BPM. v1.6.0 introduz um **sub-modo nomeado** dentro do mesmo `discovery` que: (i) filtra falsos positivos na entrada, (ii) conduz elicitação BPM-sênior pelas 13 dimensões definidas neste documento, (iii) entrega 3 artefatos (`requirements.md` + `process-map-as-is.md` + `gap-analysis.md`), (iv) passa o gap ao `architect` para to-be design via ADR. A extensão é **aditiva** — v1.5.0 continua intacto.

## Natureza do trabalho

- **Categoria:** extensão de papel de processo dentro do próprio framework metacognitivo. Meta-feature.
- **Modo:** **prospectivo** (sem dor real vivida; sem caso confirmado de v1.5.0 ter falhado em campo). Critério de aceite ancorado em **método universal cobrindo as 13 dimensões**, não em "resolveu cenário X". `[CONFIRMADO]`
- **Cenários ilustrativos** (não-gabarito, apenas didáticos): H1 farma/liberação de lote · H2 onboarding B2B financeiro · H3 fechamento contábil mensal. Servem para stress-test mental e para o **exemplo trabalhado** que vai em `docs/specs/exemplos/H1-farma/`. `[CONFIRMADO]`

## Objetivo & valor

### Objetivo
Permitir que o papel `discovery` opere com vocabulário e estrutura BPM-sênior quando o trabalho do usuário for um processo de negócio, **sem criar nova skill, sem criar novo subagente, sem quebrar o método universal existente**.

### Valor entregue
- **Para o operador (você + terceiros):** quando a natureza é processo, deixa de produzir um `requirements.md` genérico (lista de features) e passa a produzir um mapa de processo acionável + diagnóstico de gaps.
- **Para o architect:** recebe um `gap-analysis.md` formatado em vocabulário BPM (handoffs quebrados, donos faltando, gargalos, exceções não cobertas) — input direto para ADR(s) de processo to-be.
- **Para o framework:** preenche a lacuna entre "discovery genérico" (universal mas raso em BPM) e "skill BPM dedicada" (cara de manter, padrão novo de delegação inter-skills inexistente hoje).

### Por quê agora
- v1.5.0 acabou de estabilizar discovery genérico. Próximo nível: especialização sem fragmentação. `[INFERIDO ALTA]`
- Auto-sync hook v1.5.0 eliminou divergência repo↔global — extensão se propaga automaticamente em SessionStart. `[CONFIRMADO]`

## Stakeholders & audiência

### Personas-alvo (4 — robustez máxima exigida)
1. **Fabricio em engagements externos.** Implica vocabulário formal, output apresentável a stakeholder, hand-holding moderado. `[CONFIRMADO]`
2. **Fabricio em uso pessoal / projetos próprios.** Implica velocidade, output cru aceitável. `[CONFIRMADO]`
3. **Terceiros que adotam o framework via repo público.** Implica documentação robusta, exemplos, baixa dependência de conhecimento tácito do mantenedor. `[CONFIRMADO]`
4. **Subagente automatizado (pipeline sem humano direto).** Implica output **determinístico e parseável**. `[CONFIRMADO]`

### Implicações cruzadas
- Persona 4 + persona 3 juntas elevam o bar: a skill precisa ser **autoexplicativa** (terceiros) E o output precisa ser **estruturado o suficiente para parse** (subagente). Não é "ou um ou outro" — é os dois ao mesmo tempo.

## Escopo funcional (EARS)

### Ubíquos (sempre verdadeiros)

- **EARS-F1.** O sistema DEVE manter o método universal do discovery v1.5.0 inalterado (1ª pergunta sobre natureza; 9 dimensões genéricas; etapa anti-raso obrigatória; classificação CONFIRMADO/INFERIDO/DESCONHECIDO). `[CONFIRMADO — backward compat aditivo]`
- **EARS-F2.** O sistema DEVE oferecer sub-modos nomeados dentro do mesmo papel `discovery`: (i) método universal puro; (ii) "revisar projeto existente" (já existe em v1.5.0); (iii) **"mapeamento de processo"** (novo em v1.6.0). `[CONFIRMADO — encaixe = sub-modo]`

### WHEN (eventos)

- **EARS-W1.** QUANDO a 1ª pergunta universal do discovery indicar que a natureza é "processo de negócio" (ou termos similares — fluxo, BPM, workflow de negócio, procedimento), o sistema DEVE perguntar o **filtro de entrada explícito**: "isto é processo de negócio ou um dos 4 redirecionáveis (jornada UI, runbook técnico, algoritmo de código, workflow de tool)?". `[CONFIRMADO]`
- **EARS-W2.** QUANDO o usuário confirmar que é processo de negócio (filtro de entrada aprovado), o sistema DEVE entrar no sub-modo "mapeamento de processo" e perguntar o **nível de profundidade**: `quick` (SIPOC + macro) / `standard` (macro + sub-processo, **default**) / `deep` (atividade granular). `[CONFIRMADO]`
- **EARS-W3.** QUANDO o usuário escolher profundidade, o sistema DEVE perguntar a **notação plugável**: markdown-só / +Mermaid flow/sequence / +Mermaid swimlane/BPMN-lite / plug livre. `[CONFIRMADO]`
- **EARS-W4.** QUANDO o usuário escolher notação, o sistema DEVE perguntar o **nível de formalidade**: pragmático/lean · sênior BA prático · BPMN 2.0 estrito · per case. `[CONFIRMADO]`
- **EARS-W5.** QUANDO o processo estiver implementado em código/sistema (BPMS, n8n, Airflow, workflow de SaaS), o sistema DEVE rodar `discovery` (etnografia humana) e `explorer` (auditoria do código/configuração) — **em sequência rápida com síntese explícita** quando o contexto for single-thread (Claude Code sem subagentes reais); **como subagentes reais em paralelo** quando persona=4 (pipeline) E infraestrutura suportar. Em ambos os modos, o cruzamento dos dois outputs detecta o gap entre **as-is-declarado**, **as-is-codificado** e **as-is-real**. O cruzamento é feito pelo discovery (ele consolida em `gap-analysis.md`). `[CONFIRMADO — anti-padrão #1 do BPM como tratamento built-in; protocolo refinado pós-revisão]`
- **EARS-W6.** QUANDO o sub-modo concluir o levantamento, o sistema DEVE produzir 3 arquivos lado a lado em `docs/specs/<caso>/`: `requirements.md` (dimensões), `process-map-as-is.md` (mapa com diagrama na notação configurada), `gap-analysis.md` (diagnóstico para architect). `[CONFIRMADO]`

### IF/THEN (exceções)

- **EARS-I1.** SE o usuário responder ao filtro de entrada indicando um dos 4 redirecionáveis, ENTÃO o sistema DEVE NÃO entrar no sub-modo e DEVE redirecionar: jornada UI → discovery trilha web/produto; runbook → developer/docops; algoritmo → developer/dev; workflow-tool → configuração da ferramenta (fora de discovery). `[CONFIRMADO]`
- **EARS-I2.** SE for greenfield (sem processo rodando hoje), ENTÃO o sistema DEVE pular dimensões as-is-only (pain points + bottlenecks) e produzir apenas `requirements.md` (sem `process-map-as-is.md` nem `gap-analysis.md`). Architect recebe os requisitos e desenha to-be direto. `[CONFIRMADO]`
- **EARS-I3.** SE a tarefa cair em `high-stakes-gate` (regulado, irreversível, decisão crítica), ENTÃO o tratamento de compliance/audit trail/ALCOA+ NÃO é responsabilidade desta extensão — o `high-stakes-gate` é quem pede o que precisa. Esta extensão limita-se a registrar "esta atividade tem controle regulatório? sim/não/desconhecido" como tag descritiva. `[CONFIRMADO — compliance OUT]`
- **EARS-I4.** SE a etapa de validação com stakeholders (anti-raso #4) não puder ser executada (stakeholder indisponível, prazo curto) em modo humano, ENTÃO o `process-map-as-is.md` DEVE ser marcado explicitamente como `[VALIDAÇÃO PENDENTE]` no cabeçalho — sem essa marcação, o mapa não pode ser tratado como verdade. `[CONFIRMADO]`
- **EARS-I5.** SE persona=4 (subagente automatizado) E a validação stakeholder de A4 não for possível (não há humano disponível no pipeline), ENTÃO o `gap-analysis.md` DEVE incluir bloco estruturado `## [BLOQUEADOR: validação humana pendente]` listando exatamente as perguntas que precisam de resposta humana E o pipeline DEVE encerrar com **exit-code não-zero** (sinalização explícita ao orquestrador downstream). Isto evita que pipelines automatizados produzam artefatos estruturalmente válidos mas semanticamente inutilizáveis. `[CONFIRMADO — gap #2 fechado pós-revisão]`

### WHERE (variações de contexto)

- **EARS-WH1.** ONDE o operador for subagente automatizado (persona 4), o sistema DEVE produzir output em estrutura tabular/YAML/JSON-embedded sempre que possível, evitando narrativa livre. `[INFERIDO ALTA — implicação de persona 4]`
- **EARS-WH2.** ONDE o operador for terceiro via repo público (persona 3), a skill DEVE conter exemplos inline e referências cruzadas (não pode depender de conhecimento tácito do mantenedor). `[INFERIDO ALTA — implicação de persona 3]`
- **EARS-WH3.** ONDE o operador for persona=4 (subagente automatizado), CADA um dos 3 artefatos de output (`requirements.md`, `process-map-as-is.md`, `gap-analysis.md`) DEVE conter um **bloco YAML de metadados obrigatório no cabeçalho** (ex.: `mode`, `depth`, `notation`, `formality`, `personas`, `validation_status`, `as_is_classification` por atividade), **independente** da notação de diagrama escolhida (NF4) e da formalidade configurada (NF5). Garante parseabilidade NF1 sem cancelar a flexibilidade de notação. `[CONFIRMADO — gap #1 fechado pós-revisão]`

## Dimensões de processo — matriz MUST × MAY × OUT

### MUST (sempre presentes em todo mapa — 4 blocos · com modulação operacional por profundidade)

| # | Dimensão | Pergunta-chave | Saída no modo `quick` | Saída no modo `standard` (default) | Saída no modo `deep` |
|---|---|---|---|---|---|
| M1 | **Trigger + Output** do processo | O que INICIA? · O que SAI ao final? | 1 trigger + 1 output (campo único) | 1 trigger + 1 output + 1 condição alternativa | Trigger detalhado com tipo (evento/temporal/condicional) + outputs por variação |
| M2 | **Process owner + RACI por atividade** | Quem é accountable do processo? RACI por atividade? | **Apenas process owner** (1 campo, sem RACI) | Owner + RACI agregada por sub-processo | Owner + RACI completa por atividade |
| M3 | **Inputs/Outputs por atividade** (SIPOC granular) | Cada atividade: recebe/produz o quê? | **SIPOC macro** (1 linha para o processo inteiro: 1 supplier, 1 input principal, descrição do processo, 1 output principal, 1 customer) | SIPOC por sub-processo (linha por sub-processo) | SIPOC completo linha-por-atividade |
| M4 | **Business rules + Exceptions + Handoffs** | Regras nos gateways? Sad-paths? Handoffs? | **Apenas rules + exceptions principais** (sem diagrama de handoffs) | Rules + exceptions + handoffs listados em tabela | Rules + exceptions + diagrama visual de handoffs entre papéis/sistemas |

`[CONFIRMADO — 4 blocos com 3 níveis cada · gap #6 fechado pós-revisão]`

**Resumo do que o modo `quick` produz:** M1 (trigger+output) + M2 (owner only) + M3 (SIPOC macro) + M4 (rules+exceptions only) + A2 (boundaries explícitos do anti-raso). Aproximadamente 5-9 etapas no mapa. Cobre alinhamento inicial de reunião sem inundar com vocabulário pesado.

### MAY (opcionais, disparáveis em `deep` ou sob pedido — 4 blocos)

| # | Dimensão | Quando ativar |
|---|---|---|
| MAY1 | **Métricas operacionais** (cycle/lead time, volume, frequência) | `deep` OU diagnóstico de gargalo |
| MAY2 | **Mapa tecnológico** (sistemas e dados tocados) | `deep` OU integração/automação no escopo |
| MAY3 | **Variações** (caminhos por segmento/regional/valor) | Sempre que houver evidência de execução heterogênea |
| MAY4 | **Lean/maturity** (value-add, NVA, CMMI level) | Projeto de melhoria de processo (não só descrever) |

`[CONFIRMADO — todos os 4 blocos]`

### Condicional as-is-only (1 bloco)

| # | Dimensão | Regra |
|---|---|---|
| C1 | **Pain points + bottlenecks** | MUST quando há processo rodando hoje (ancora o `gap-analysis.md`); OUT em greenfield (não há o que doer ainda). `[CONFIRMADO]` |

### Anti-raso BPM (4 itens — trazidos à tona pelo discovery, não pedidos pelo usuário)

| # | Item | Tratamento na extensão |
|---|---|---|
| A1 | **Voice of Customer / CTQ** | Pergunta MUST: "quem é o cliente externo final do processo + o que ele valoriza (Critical-to-Quality)?". Output em cabeçalho do `process-map-as-is.md`. `[CONFIRMADO]` |
| A2 | **Boundaries explícitos** | Pergunta MUST upfront: "onde COMEÇA (1ª atividade) e onde TERMINA (última atividade observável)?". Evita mapear sub-conjunto sem perceber. `[CONFIRMADO]` |
| A3 | **Declarativo vs observacional** (anti-padrão #1) | Cada atividade no mapa recebe tag: `[DECLARADO]` (stakeholder disse) ou `[OBSERVADO]` (fonte direta: log de sistema, observação, baseline golden). Discovery declara qual modo está usando. Quando ambos rodam (EARS-W5), comparar é o ponto. `[CONFIRMADO]` |
| A4 | **Validação com stakeholders antes de fechar** | Passo MUST de encerramento: revisão explícita por process owner + 1 executor antes de fechar `process-map-as-is.md`. Sem revisão → marcar `[VALIDAÇÃO PENDENTE]` (EARS-I4). `[CONFIRMADO]` |

### OUT (fora de escopo desta extensão)

| # | Item | Por quê está fora |
|---|---|---|
| O1 | Compliance/audit trail/ALCOA+ | Tratado por `high-stakes-gate` (separação de responsabilidades já existente) |
| O2 | Desenho do to-be | É decisão de arquitetura — `architect` faz, via ADR de processo |
| O3 | Process simulation (discrete event) | Cerimônia desproporcional — fora do bar do framework genérico |
| O4 | Process automation / RPA recommendation | Trabalho de developer ou de skill futura, não cabe em discovery |
| O5 | Change management planning | Fora do framework — pertence a uma camada organizacional |

## Requisitos não-funcionais

| # | Requisito | Origem |
|---|---|---|
| NF1 | Output **determinístico e parseável** (YAML/tabela/markdown estruturado; evitar prosa livre quando possível). Operacionalizado por EARS-WH3 (cabeçalho YAML de metadados obrigatório em todos os 3 artefatos quando persona=4). Resolve a tensão NF1×NF4×NF5: notação plugável + formalidade configurável **não** cancelam parseabilidade — o cabeçalho estruturado garante o piso, o corpo varia | Persona 4 (subagente automatizado) |
| NF2 | Skill **autoexplicativa** (exemplos inline, referências cruzadas, sem dependência de conhecimento tácito do mantenedor) | Persona 3 (terceiros via repo público) |
| NF3 | **Backward compatibility aditiva** — método universal v1.5.0 inalterado. Única mudança subtrativa: sweep da linha `- **BA/processo:** as-is × to-be, donos do processo, regras de negócio, exceções, indicadores de sucesso, mudança organizacional.` no banco de partida (`.agent/skills/discovery/SKILL.md` linhas 54-55) substituída pelo texto exato: `- **BA/processo:** processo de negócio/BPM → usar sub-modo "mapeamento de processo" (EARS-W1).` Esta mudança subtrativa **DEVE** estar registrada no escopo do ADR-002 com texto antes/depois explícito. Sub-modo "revisar projeto existente" também é tocado em v1.6.0 (harmonização ergonômica O3) — ganha filtro de entrada formal simétrico ao novo sub-modo, mas comportamento existente preservado | Lote 4 + gap #5/#9 + oportunidade O3 |
| NF4 | **Notação plugável** — quem opera escolhe por caso (markdown-só / +Mermaid / +swimlane / BPMN-lite) | Lote 1 |
| NF5 | **Formalidade configurável** — pragmático/lean · sênior BA prático · BPMN 2.0 estrito · per case | Lote 1 |
| NF6 | **Profundidade configurável** — `quick`/`standard` (default) /`deep` | Lote 1 |
| NF7 | **Paridade global automática — escopo refinado pós-ADR-003** — auto-sync hook em SessionStart usa `Copy-Item -Recurse` para espelhar a **pasta inteira** de cada skill (entry point + companion files) para `~/.claude/skills/<name>/`. Logo, `.agent/skills/discovery/SKILL.md` + `mapeamento-de-processo.md` + `revisar-projeto-existente.md` propagam automaticamente. Pré-requisito de "skill válida": ter `SKILL.md` na pasta como entry point. Também espelha `.claude/agents/*.md` (sem `.md.txt`). **Não** propaga: `docs/specs/_template-process/`, `docs/specs/exemplos/H1-farma-*/`, `docs/specs/discovery-process-mapping/`, `docs/adr/002-*.md`, `docs/adr/003-*.md`, atualização do `000-template.md`. Estes artefatos vivem só no repo — terceiros pegam via clone | Auto-sync hook commit `40d6966` + gap NF7 fechado pós-revisão + escopo refinado pós-ADR-003 |
| NF8 | **Anti-alucinação preservada** — qualquer lacuna que o stakeholder não souber responder vira `[DESCONHECIDO]` explícito no mapa, com sugestão de validação (ex.: "consultar log do LIMS para tempo médio") | Regra inviolável `_shared/anti-hallucination` |

## Fluxos de exceção e lógicas limítrofes (explícitos)

- **Stakeholder único / process owner ausente:** discovery NÃO fecha; marca `[VALIDAÇÃO PENDENTE]` no `process-map-as-is.md` e recomenda explicitamente "agendar revisão antes de architect tocar to-be".
- **Processo sem dono claro** (cross-funcional onde ninguém é accountable): discovery captura como **gap crítico** no `gap-analysis.md` ("dono não identificado") — é um dos achados mais comuns e valiosos.
- **As-is divergente entre fontes** (operador A diz X, operador B diz Y, log do sistema diz Z): mapear AS TRÊS no `process-map-as-is.md` com tag `[DIVERGÊNCIA]` + `[DECLARADO|OBSERVADO]` em cada — não escolher um arbitrariamente.
- **Processo com variações infinitas** (raros 2 cases iguais): discovery força agrupamento em **classes de variação** (segmento/valor/região) — máximo 5 classes; se mais, é sinal de processo não-padronizado, vira pain point.
- **Greenfield (sem as-is)**: pula `process-map-as-is.md` e `gap-analysis.md`; produz só `requirements.md` com EARS de processo; architect desenha to-be do zero.

## Fora de escopo (anti-spec gigante)

Reafirmando o que NÃO cobre, para evitar creep:
1. Compliance/audit trail — `high-stakes-gate`.
2. Desenho do to-be — `architect` (via ADR de processo).
3. Simulação de processo (discrete event sim).
4. Recomendação de automação/RPA.
5. Change management planning.
6. Process mining em volume industrial (Celonis-style) — o que cabe é o cruzamento qualitativo via `explorer`, não plataforma de mining.
7. KPIs/OKR design (a extensão **registra** KPIs declarados pelo stakeholder; não os desenha).

## Fontes de dados

- **`.agent/skills/discovery/SKILL.md`** — fonte do método universal a estender. `[CONFIRMADO — lido]`
- **`docs/specs/_template/requirements.md`** — template base a clonar+estender para `_template-process/`. `[CONFIRMADO — lido]`
- **`AGENT-FRAMEWORK.md` (linhas 90-99)** — gatilho atual do discovery, a ser estendido. `[CONFIRMADO — lido]`
- **`_meta/eval-results-papeis.md`** — local da nova seção H+H'. `[CONFIRMADO — existe]`
- **`docs/adr/000-template.md`** — molde para ADR-002. `[CONFIRMADO — existe]`
- **Auto-sync hook (`.claude/hooks/sync-global.ps1`)** — garantia de paridade global. `[CONFIRMADO — commit 40d6966]`

## Critério de aceite (binário — 12 itens com seções nomeadas verificáveis)

v1.6.0 está **PRONTO** quando todos os 12 itens abaixo existirem e passarem `qa-critic`. Cada item é binário (sim/não) — não comporta interpretação de grau. Conferência operacional vive em `validation.md` (item 12).

1. **Skill atualizada.** `.agent/skills/discovery/SKILL.md` v1.6.0 contém as seções nomeadas exatamente: `## Sub-modo "mapeamento de processo"` (com `### Filtro de entrada` listando os 4 redirecionáveis, `### Profundidade` listando `quick`/`standard`/`deep`, `### Matriz de dimensões` com tabela MUST/MAY/condicional/anti-raso, `### Notação plugável`, `### Formalidade configurável`, `### Output em 3 arquivos`, `### Integração com explorer (EARS-W5)`, `### Validação com stakeholders (anti-raso A4)`). Verificável por grep dos cabeçalhos. `[A IMPLEMENTAR pelo developer]`
2. **Template novo.** `docs/specs/_template-process/` (não existe hoje — **a criar pelo developer**) contém os 3 arquivos: `requirements.md` (clonado e estendido de `_template/`), `process-map-as-is.md` (template com cabeçalho YAML obrigatório por EARS-WH3, seções para SIPOC + RACI + diagrama Mermaid + tags `[DECLARADO]`/`[OBSERVADO]` por atividade), `gap-analysis.md` (template com seção MUST `## Itens para architect` listando questões de to-be sem resolvê-las). Verificável por `ls` da pasta + grep de cabeçalhos. `[A CRIAR pelo developer]`
3. **Roteador atualizado.** `AGENT-FRAMEWORK.md` seção "Gatilho do discovery" (linhas 90-99) estendida com bloco nomeado `### Sub-modo mapeamento de processo (v1.6.0)` mencionando filtro de entrada + EARS-W1 + os 3 artefatos. Verificável por grep. `[A IMPLEMENTAR]`
4. **Eval atualizado.** `_meta/eval-results-papeis.md` ganha seção **H** (sub-modo should-trigger, mínimo **9 casos**) **+ seção H'** (sub-modo should-NOT-trigger, mínimo **9 casos**) — total mínimo **18 casos** (paridade direta com G+G' que tem 9+9=18, conforme verificado por explorer). Todos marcados `[EMERGENTE — DESIGN-TIME, NÃO EXECUTADO]`. Estrutura de colunas idêntica a G+G': `# | Frase | Esperado | Roteou para | OK`. Verificável por contagem de linhas da tabela. `[A IMPLEMENTAR pelo developer]`
5. **Exemplo trabalhado H1.** `docs/specs/exemplos/H1-farma-liberacao-de-lote/` (não existe hoje — **a criar pelo developer**) contém os 3 arquivos populados de cabo a rabo no modo `standard` (RACI QC/QA/Produção, tags declarativo×observacional em pelo menos 5 atividades, seção de validação stakeholder marcada `[VALIDADO — fictício para didática]`, compliance OUT delegado ao high-stakes-gate explicitamente). Cabeçalho YAML obrigatório nos 3 artefatos. Vale como golden de referência. Verificável por inspeção dos 3 arquivos. `[A CRIAR pelo developer]`
6. **ADR formal.** `docs/adr/002-discovery-process-mapping-v160.md` registra a decisão arquitetural. **Ponteiro = branch + data + grep**, NÃO hash de commit. Escopo do ADR inclui explicitamente: (a) a feature do sub-modo, (b) a mudança subtrativa do "BA/processo" no banco de partida (com texto antes/depois literal), (c) a harmonização do sub-modo "revisar projeto existente" (filtro de entrada simétrico), (d) o bump de versão da skill, (e) a atualização do `000-template.md`. Verificável por grep das 5 sub-decisões na seção "Decisão" e "Consequências". `[✅ CRIADO pelo architect — 2026-05-25 · ADR contém 7 sub-decisões nomeadas D1-D7 (5 do critério + 2 ratificações: D6 handoff arquivo separado, D7 protocolo EARS-W5) · status Proposto]`
7. **CHANGELOG.** Entrada v1.6.0 (MINOR — feature compatível) documentando: novo sub-modo, 3 artefatos de output, filtro de entrada, 13 dimensões, 4 anti-raso, integração explorer (EARS-W5), exemplo H1, bump de versão da skill, harmonização sub-modos, atualização template ADR. Verificável por grep `## [1.6.0]`. `[A IMPLEMENTAR]`
8. **README tabela de papéis.** Linha do discovery em `README.md` menciona o sub-modo "mapeamento de processo" como capacidade v1.6.0. Verificável por grep. `[A IMPLEMENTAR]`
9. **Versão da skill harmonizada (oportunidade O1).** Frontmatter de `.agent/skills/discovery/SKILL.md` passa por correção: `version: 1.0.0` → `version: 1.5.0` (corrigindo o drift) → `version: 1.6.0` (bump da feature). Documentado no CHANGELOG. Verificável por grep do frontmatter. `[A IMPLEMENTAR — gap-fix retroativo]`
10. **Template ADR atualizado (oportunidade O2).** `docs/adr/000-template.md` seção "Implementação" altera a linha `(commit hash após aceito)` para `Ponteiro: branch + data + grep (padrão preferido — hash é frágil a rewrites; ver lição do ADR-001). Hash apenas como complemento opcional, nunca único.` Verificável por grep do texto literal. `[A IMPLEMENTAR — fix de template proativo]`
11. **Sub-modos harmonizados (oportunidade O3).** A seção `## Modo "revisar projeto existente"` da SKILL.md ganha o mesmo padrão de filtro de entrada formal: cabeçalho `### Filtro de entrada` listando o que ATIVA o modo (input: "sistema que já existe; relatório do explorer; pedido de auditoria/saneamento") e o que NÃO ativa (ex.: pedido de feature nova). Sem alterar comportamento downstream — apenas formalizar a ativação. Verificável por grep dos cabeçalhos simétricos. `[A IMPLEMENTAR — harmonização ergonômica]`
12. **Validation gabarito (oportunidade O4).** `docs/specs/discovery-process-mapping/validation.md` existe e contém um plano de validação para cada um dos 12 itens deste critério + os 12 gaps fechados pós-revisão + os 4 anti-raso BPM. Estrutura: `## Item N — método de validação` por item. Vale como guia para `qa-critic` validar a entrega da v1.6.0. Verificável por contagem de seções. `[A CRIAR pelo discovery — incluído nesta entrega]`

## Edge cases & riscos

| # | Risco | Mitigação |
|---|---|---|
| R1 | **Modo prospectivo erra cobertura** — primeiro caso real (quando vier) revelar dimensão não prevista | Exemplo H1 trabalhado força stress-test em ambiente regulado (caso mais carregado); H2 e H3 ficam como exercício mental no eval. Se algo escapar, vira v1.6.1 (PATCH) |
| R2 | **13 dimensões pesam para operador humano** (cognitive load) | `quick` mode reduz a 5 blocos operacionais (M1 trigger+output · M2 owner only · M3 SIPOC macro · M4 rules+exceptions only · A2 boundaries) — ver matriz MUST com 3 níveis operacionais. `standard` (default) traz ~9 blocos. `deep` traz tudo. Operador escolhe explicitamente em EARS-W2. Gap #6 fechado — não há mais adjetivo "mínimo/superficial" sem definição |
| R3 | **Subagente automatizado não consegue parsear output narrativo** | NF1 fixa estrutura YAML/tabela; exemplo H1 demonstra o padrão. Sem isso, persona 4 fica simbólica |
| R4 | **Conflito com "revisar projeto existente"** (sub-modo já existente) — quando o processo está em código, qual sub-modo entra? | EARS-W5 resolve: ambos rodam em paralelo (discovery faz humano, explorer faz código). Não é "ou-ou", é "e" |
| R5 | **Anti-padrão declarativo×observacional ignorado pela pressa** | Tag obrigatória em cada atividade (A3); sem a tag, o mapa não passa `qa-critic`. Custo: ~1-2s por atividade |
| R6 | **Process owner inexistente** (processo órfão) | Discovery NÃO inventa owner; registra `[DESCONHECIDO]` + recomenda "definir antes de architect" no `gap-analysis.md`. Comum em achados reais |
| R7 | **Auto-sync hook falha em SessionStart** (Windows path quirks, permissões) | Hook já testado em commit `40d6966`; se falhar, fallback é cópia manual documentada em guia/SETUP.md. v1.6.0 não regredi o hook |
| R8 | **ADR-002 escrito com hash de commit** (repetição do problema do ADR-001) | Memory feedback do usuário já registra; ADR-002 vai usar branch+data+grep desde a 1ª versão |

## Cenários ilustrativos (não-gabarito — apenas didáticos)

### H1 — Processo regulado (escolhido para exemplo trabalhado)
**Liberação de lote em farmacêutica.** Stress test: RACI multi-funcional (QC/QA/Produção), gatilhos por evento (CoA, OOS), handoffs entre sistemas (LIMS↔SAP), regras de retrabalho/reprovação, compliance OUT (delega ao high-stakes-gate), anti-padrão declarativo×observacional muito provável (procedimento escrito ≠ rotina de bancada).

### H2 — Processo operacional/transacional
**Onboarding de cliente B2B em serviço financeiro.** Stress test: variações por segmento (PJ pequena vs grande), gateway KYC/AML, SLA por etapa, paralelismo (validação documental ‖ análise de crédito), exceções (KYC reprovado), pain points de rework.

### H3 — Processo gerencial
**Ciclo de fechamento contábil mensal.** Stress test: cross-functional (TI↔Contábil↔FP&A), múltiplos sistemas (ERP+EPM+planilhas), donos conflitantes por etapa, dependências temporais hard (D+5, D+7), reconciliação central, exceções por tipo de lançamento.

## Glossário relevante

- **SIPOC** — Suppliers, Inputs, Process, Outputs, Customers. Cabeçalho clássico de mapa BPM.
- **RACI** — Responsible, Accountable, Consulted, Informed. Matriz por atividade.
- **CTQ** — Critical to Quality. O que o cliente externo valoriza (Six Sigma).
- **Handoff** — transferência de responsabilidade entre papéis/sistemas em um processo. Ponto crítico.
- **Gateway** — ponto de decisão no fluxo (XOR exclusivo, OR inclusivo, AND paralelo — BPMN 2.0).
- **Process owner** — pessoa accountable pelo processo inteiro (UM por processo). Distinto de executor.
- **Declarativo × Observacional** — mapa do que stakeholders DIZEM ser vs do que REALMENTE é. Anti-padrão #1 do BPM.
- **VoC** — Voice of Customer. Quem é o cliente externo final + o que valoriza.
- **Baseline golden** — snapshot de comportamento de referência (vem do método de "revisar projeto existente").
- **As-is / To-be / Gap** — estado atual / estado desejado / diferença entre os dois. Discovery faz as-is + gap; architect faz to-be.

## Lacunas abertas `[DESCONHECIDO]`

Nenhuma lacuna bloqueia a entrega ao `architect`. Duas lacunas residuais registradas, ambas de runtime e não-bloqueantes:

- `[DESCONHECIDO — runtime]` Qual primeiro processo REAL vai exercitar a extensão (modo prospectivo = não há dor vivida). **Validação:** quando vier o 1º caso real, comparar contra exemplo H1 trabalhado; se algo escapar, virar v1.6.1 (PATCH).
- `[FECHADO pós-revisão]` ~~Estrutura de eval-results H' (12 ou 18 casos?)~~ — gap #8 fechado: critério item 4 fixa **mínimo 18 casos** (9 H + 9 H', paridade direta com G+G' verificada pelo explorer).

Todas as 13 dimensões, 4 anti-raso, 4 personas, 3 níveis de profundidade, 2 plugs (notação + formalidade), 12 itens do critério de aceite, ADR-002 com escopo expandido e backward compat estão `[CONFIRMADO]` ou `[INFERIDO ALTA]`. Gap #12 (contradição de framing) corrigido.

## Anti-raso aplicado (registro auditável)

A etapa anti-raso da skill discovery exige que eu (no papel) traga à tona o que o usuário não pediu, e responda proativamente. Registrei 4 itens que o usuário NÃO levantou inicialmente, propus, e todos foram aceitos:

| # | Item levantado (não pedido) | Decisão | Onde virou requisito |
|---|---|---|---|
| 1 | Voice of Customer / CTQ explícito | ACEITO como anti-raso A1 → MUST | Matriz BPM, EARS implícito |
| 2 | Boundaries do processo (início/fim) explícitos | ACEITO como anti-raso A2 → MUST | Matriz BPM, EARS implícito |
| 3 | Declarativo × Observacional (anti-padrão #1) | ACEITO como anti-raso A3 → tag por atividade | EARS-W5 + tabela A |
| 4 | Validação com stakeholders antes de fechar | ACEITO como anti-raso A4 → passo MUST de encerramento | EARS-I4 + tabela A |

Adicionalmente, o discovery propôs ativamente duas recomendações estruturais:
- **Variante híbrida as-is/to-be** (discovery faz as-is + gap; architect faz to-be) — não estava no menu original, aceita.
- **Filtro de entrada explícito** (acoplado aos 4 falsos positivos) — proposta como melhor opção de ativação, aceita.

## Recomendação ao orquestrador

```yaml
papel: discovery
modo: prospectivo (sub-modo meta — estende o próprio papel)
natureza_do_trabalho: extensão do papel discovery com sub-modo de mapeamento de processo (v1.6.0)
revisao_adversarial: aplicada (qa-critic 12 gaps + explorer 4 oportunidades adjacentes, todos endereçados)
dimensoes_cobertas:
  - objetivo_valor
  - stakeholders_audiencia (4 personas)
  - funcional (EARS F1-F2, W1-W6, I1-I5, WH1-WH3)
  - nao_funcional (NF1-NF8 com NF1 e NF7 reforçados pós-revisão)
  - dados_fontes
  - restricoes (anti-rename, backward compat aditivo, hook auto-sync com escopo explícito)
  - criterio_aceite (12 itens binarios com seções nomeadas verificáveis)
  - edge_cases_riscos (R1-R8 com R2 operacionalizada)
  - fora_de_escopo (O1-O5 com O2 handoff endereçado via template gap-analysis.md)
requisitos:
  CONFIRMADO: 97%   # após revisão adversarial, gaps de classificação fechados
  INFERIDO_ALTA: 3% # NF1/NF2 derivados de persona 3+4
  DESCONHECIDO: 1 lacuna runtime (primeiro caso real)
lacunas_abertas:
  - "Primeiro caso real ainda não vivido (modo prospectivo) — risco residual, mitigado por exemplo H1 trabalhado"
anti_raso:
  - "VoC/CTQ explicito (não pedido, aceito como MUST)"
  - "Boundaries explicitos (não pedido, aceito como MUST)"
  - "Declarativo × Observacional anti-padrão #1 (não pedido, aceito como tag por atividade)"
  - "Validação com stakeholders antes de fechar (não pedido, aceito como passo MUST de encerramento)"
revisao_adversarial_aplicada:
  gaps_fechados: 13
  oportunidades_incorporadas: 4
  criterio_aceite_expandido: 8 -> 12 itens
  validation_md_criado: sim (item 12 do critério)
recomendacao_ao_orquestrador: |
  Passar para o ARCHITECT. As decisões arquiteturais a confirmar via ADR-002 (escopo expandido pós-revisão) são:
    1) Encaixe = sub-modo do discovery (vs skill irmã, vs sempre-on, vs template-only).
    2) Handoff = arquivo separado gap-analysis.md (vs embutido, vs acoplamento automático).
    3) Discovery + explorer em sequência rápida (single-thread) ou paralelo real (persona 4) — protocolo definido em EARS-W5.
    4) Backward compat aditivo + sweep da linha "BA/processo" do acelerador com texto antes/depois literal.
    5) Bump de versão da skill 1.0.0 -> 1.5.0 -> 1.6.0 (correção de drift + feature).
    6) Atualização proativa do docs/adr/000-template.md (ponteiro branch+data+grep como padrão).
    7) Harmonização do sub-modo "revisar projeto existente" com filtro de entrada formal simétrico.
  Sequência sugerida: ARCHITECT (ADR-002 com escopo expandido + design dos 3 templates) -> DEVELOPER -> QA-CRITIC (usa validation.md como gabarito) -> DOCOPS.
versao_alvo: 1.6.0 (MINOR — aditivo + correções de drift, sem quebra de compat)
```

---

**Status:** spec fechada · pronta para `architect`. Não implementar antes do ADR-002.
