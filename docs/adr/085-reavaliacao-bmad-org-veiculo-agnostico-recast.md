# ADR 085 — Re-avaliação BMAD org-wide: software/dados/ciência como VEÍCULO do fim agnóstico + integração por RECAST (não por absorção de técnica)

- Status: **Proposto** (2026-06-17 — aguarda gate: qa-critic adversarial + escolha §0 do dono de QUAIS recast construir) · Decisores: dono (3 correções de princípio nesta sessão) + squad
- Tipo: **correção de princípio + emenda** (não adição pura). Régua §0 (ADR-007): a parte que **suplanta** a seção "O que NÃO foi integrado e por quê" do ADR-081 não adiciona — *edita um julgamento existente que o dono declarou inválido*. Cada integração proposta abaixo declara seu próprio enquadramento §0 (a maioria **estende** skill/tool existente; nenhuma é adição pura sem ganho). Override de §0 por **autorização explícita do dono**, declarado (rule #10 / ADR-051).
- Relaciona: **ADR-081** (suplanta a seção de rejeição), ADR-007 (régua §0), ADR-010/020 (agnosticismo), ADR-011/045 (QA bicelular), ADR-072/073 (anti-reinvenção), ADR-077 (qa-evidence), ADR-080 (dieta), ADR-083 (cross-AI web-bundles)

## Contexto

O ADR-081 (Aceito 2026-06-16) integrou 4 padrões do **BMAD-METHOD** (repo principal, v6.8.0, ★49250) e **rejeitou** outros "por escopo produto-de-software / baixo ganho genérico". Duas falhas foram apontadas pelo dono (checkpoint v1.61.0, history.md):

1. **Auditoria rasa:** só **1 de 13 repos** da org `bmad-code-org` foi examinado, e a citação de fonte da rejeição era genérica (sem URL/verificável).
2. **Lógica de rejeição inválida (3 correções do dono, 2026-06-17):**
   - (i) *"a integração deve ir além de absorver a técnica — adequar o método ao nosso: file-first, ferramenta, determinismo, quando aplicável e onde importar"*;
   - (ii) *"não rejeitar por especificidade. Software aqui é um MEIO para atingir o fim agnóstico. É ferramenta e temos que passar por ele"*;
   - (iii) *"para criar uma solução agnóstica precisamos passar por pensamento científico, criação de solução de dados, análise ou SOFTWARE — então as técnicas são relevantes"*.

**Síntese do princípio do dono:** o fim do framework é agnóstico, mas todo fim agnóstico **se realiza através de um veículo concreto** — pensamento científico, solução de dados, análise **ou software**. Logo, técnicas desses veículos **são relevantes por construção**. "Especificidade de software" deixa de ser motivo de rejeição. Os únicos filtros que sobrevivem são: **(a) já temos com igual rigor?** e **(b) régua §0 — onde importar há ganho líquido?**. E o que importar deve ser **recast no nosso idioma** (file-first · ferramenta determinística · gate), não copiado como prosa.

## Decisão de princípio (SUPLANTA a seção "O que NÃO foi integrado e por quê" do ADR-081)

> **Veículo ≠ escopo descartável.** Nenhum padrão BMAD é rejeitado por ser "específico de software/jogo/UX/teste". Cada repo é examinado pelo **método agnóstico que sua instância concreta encapsula**; o veredito é **já-coberto** (com fonte) ou **net-positive→recast** (com desenho ferramental), nunca "rejeitado-por-especificidade".

Esta cláusula **suplanta** as 5 linhas de rejeição do ADR-081 §"O que NÃO foi integrado". O ADR-081 permanece Aceito quanto às 4 integrações que entregou (B1/B2/B3/A1/A2); só o **rationale de exclusão** é revisado aqui.

### Postura epistêmica sobre padrões BMAD (4ª orientação do dono, 2026-06-17)

> *"Se tanta gente usa e funciona, deve ser válido — provar bug [para rejeitar]."*

Reconciliado com a régua §0 como **dois ônus para duas perguntas distintas** (a confusão dos dois é o que infla o núcleo):

1. **"O padrão BMAD é bem-feito?"** → **presumir SIM** (adoção alta ⇒ competência presumida). Um padrão só é descartado por **defeito provado** (bug, inconsistência, falha demonstrável) — **nunca** por especificidade, gosto ou "escopo de software". Este é o ônus que o dono inverte, e está correto contra rejeição-preguiçosa.
2. **"Devemos adicionar ao NOSSO núcleo?"** → **§0 default-deny permanece**: o ônus é provar **ganho líquido** + recast (estende/funde/destrava). Popularidade prova desejabilidade e viabilidade-de-origem, **não** aderência-a-nós nem net-gain. `argumentum ad populum` não estabelece fit.

Resultado: *especificidade* morre como motivo de rejeição; *§0* sobrevive como motivo de não-adoção. **Auto-crítica registrada:** os vereditos (F)/N/A da versão inicial deste ADR violavam (1) — descartavam por asserção não-provada; revisados abaixo.

### Princípio de recast (1ª orientação do dono): determinismo-primeiro, prosa como fallback COM PORTA

> *"O determinismo/ferramental deve estar presente em TUDO; usar a técnica do BMAD (template, prosa, parada-e-orientação) como **fallback**."*

Tensão real: "determinismo em tudo" e "prosa como fallback" se contradizem se o fallback não tiver critério — vira escotilha de fuga que engole a regra (vetor de acreção que a dieta/ADR-080 combate). **Porta obrigatória:** prosa/template/parada-e-orientação só é admissível quando **(a)** a decisão é irredutivelmente de julgamento humano **E (b)** está demonstrado que uma ferramenta determinística não captura o critério. Caso contrário é §0-accretion disfarçada. **Observação que dissolve metade da tensão:** "parada e orientação" feita certa **já é determinística no nosso idioma** — é um *gate file-first* (para o fluxo + injeta instrução fixa), idêntico aos hooks route-gate/mission-gate. Logo, todo recast abaixo busca **gate/tool determinístico primeiro**; cai para template/prosa só pela porta acima, declarando o motivo.

## Sweep org-wide — fonte autoritativa (fecha a falha de auditoria 1/13)

Fonte: `gh api orgs/bmad-code-org/repos` + leitura de conteúdo dos READMEs/docs citados por URL raw. Coletado 2026-06-17. Confiança da coluna "fonte" = **CONFIRMADO** (API/arquivo lido); coluna "veredito" = **INFERIDO** (julgamento §0).

| # | Repo (★) | Veículo / método encapsulado | Fonte verificável | Veredito sob nova lente |
|---|---|---|---|---|
| 1 | **BMAD-METHOD** (★49250, rel. v6.8.0) | 69 métodos de elicitação **convergentes** + 4 padrões | ADR-081 + `gh api repos/.../BMAD-METHOD` | **Já integrado** (ADR-081) |
| 2 | **creative-intelligence-suite (CIS)** (★135) | ideação **divergente** (36 téc / 7 cat) + 5 workflows (brainstorm/design-thinking/innovation/problem-solving/storytelling) | `…/CIS/main/docs/explanation/brainstorming-techniques.md` · `…/docs/reference/workflows.md` | **NET-POSITIVE → recast (A)** |
| 3 | **module-game-dev-studio** (★192) | **calibração de parâmetros por dados**: modelar→isolar→integrar→escalar→medir-vs-alvo c/ red-flags→iterar (balance/certification testing) | `…/game-dev-studio/main/src/agents/gds-agent-game-dev/gametest/knowledge/balance-testing.md` | **NET-POSITIVE → recast (C)** (veículo *dados/análise*) |
| 4 | **test-architecture-enterprise (TEA)** (★71) | **gating determinístico por risco** (Prob×Impacto 3×3 → score 1–9 → gate + cobertura P0–P3, 6 cat TECH/SEC/PERF/DATA/BUS/OPS) + **matriz de rastreabilidade** (oracle 4-tier) → gate decision (PASS/CONCERNS/FAIL/WAIVED) | `…/TEA/main/docs/explanation/risk-based-testing.md` · `…/docs/how-to/workflows/run-trace.md` | **NET-POSITIVE → recast (B)** (o mais forte; veículo *software/ciência*) |
| 5 | **method-wds-expansion** (★70) | deliverables UX (trigger-map, page-spec, design-system, product-brief, platform-prd) + **ativação por step-files** (file-first determinístico) | `…/wds-expansion/main/docs/deliverables/*` · `…/docs/getting-started/agent-activation/activation/step-0*.md` | **NET-POSITIVE → recast (D)** (veículo *análise/UX*) |
| 6 | **bmad-builder** (★166) | empacotar capacidade como unidade portátil instalável conforme **Agent Skills open standard** (cross-platform) | `…/bmad-builder/main/README.md` | **Tangencia cross-AI (ADR-069/083)** → nota de roadmap (G) |
| 7 | **bmad-automator** (★36) | **orquestrador determinístico** do loop create→dev→test→review-adversarial-com-retries→retrospective (child sessions) | `…/bmad-automator/main/README.md` | **Já-coberto (método) — tooling deferido (F)**: é o nosso squad J0–J6 + retrospective-gate; orquestrador conflita com HITL deliberado |
| 8 | **plugins-marketplace** (★25) | distribuição/descoberta/versionamento de capacidades | `gh api repos/.../plugins-marketplace` | **Examinado; sem ganho §0 provado** — sobrepõe web-bundles/`capabilities.json`; revisitar se cross-AI evoluir (não dismissado por especificidade) |
| 9 | **method-ui** (★23) | integração IDE (extensão VS Code) | `gh api repos/.../method-ui` | **Examinado; método = UX de IDE**, fora do nosso veículo (CLI/agente); sem ganho §0 — revisitar se houver frente IDE |
| 10 | **module-template** (★15) | template de novo módulo | `gh api repos/.../module-template` | **Já temos** (`.agent/skills/_template`) — comparar molde p/ melhoria, não adotar |
| 11 | **utility-skills** (★7) | skills p/ autorar/manter conteúdo BMAD | `gh api repos/.../utility-skills` | **Já-coberto** (nosso par `build_*`/`test_*` + canários) |
| 12 | **method-sample-data** (★1) | dados de teste do BMAD | `gh api repos/.../method-sample-data` | **Examinado; é fixture, não método**; sem ganho §0 |
| 13 | **.github** (★0) | meta da org | `gh api repos/.../.github` | Meta-org, não-método; N/A |

> Nota sobre o brainstorming-techniques.md do CIS: o doc afirma "36 técnicas" mas lista 28 nominalmente (8 referenciadas e não listadas no resumo). **DESCONHECIDO** o conjunto completo das 8 restantes sem ler a fonte primária de Carson; não inventar — flagar no recast (A).

## Integrações propostas — RECAST no nosso idioma (file-first · ferramenta · gate)

Cada item declara: ganho líquido §0 · enquadramento (estende vs adiciona) · desenho ferramental determinístico · canário. **Nenhuma é construída por este ADR** — o dono escolhe quais (gate §0).

### (A) CIS divergente → ESTENDE `advanced-elicitation` — recomendado primeiro (menor custo, §0-limpo)
- **Ganho líquido:** nossos 69 métodos são **convergentes** (refinam/validam/stress-testam um artefato existente). Falta a fase **divergente/generativa** (produzir muitas ideias do zero). Net-new ≈ 8–10 técnicas das categorias *Wild* e *Introspective*: Worst-Possible-Idea, 100-Ideas, Exaggeration, Anti-Problems, Incubation, Stream-of-Consciousness, Guided-Imagery, Dream-Capture (este último avaliar — pode ser gimmick).
- **§0:** **estende** `methods.md` (editar tabela existente + nova coluna/seção `fase: divergente|convergente`) — não é arquivo novo. As 5 workflows CIS viram **sub-modos do `discovery`** (já tem o sub-modo "mapeamento de processo" — mesmo molde).
- **Recast determinístico:** seção divergente na tabela `methods.md` com `output_pattern`; regra de seleção "se objetivo=gerar→filtrar fase divergente; se objetivo=refinar→convergente". Mantém o catálogo como **dado**, não prosa.
- **Canário:** estender `test_*` do advanced-elicitation (se houver) ou validar via doc-sync; assert que cada técnica nova tem `fase` + `output_pattern`.
- **Fonte:** brainstorming-techniques.md (CONFIRMADO) · 8 técnicas faltantes = DESCONHECIDO (flagar, não preencher).

### (B) TEA risk-based gating → NOVA ferramenta `tools/risk_score.py` + wire a high-stakes/readiness — net-new mais forte
- **Ganho líquido:** nosso QA bicelular é **binário** (PASS/FAIL) sem **dial de profundidade**. O TEA decide *quanto* rigor por **score de risco determinístico** (Prob×Impacto, 6 categorias) → tier P0–P3 → gate. Isso responde "onde gastar QA" de forma agnóstica e auditável — não temos.
- **§0:** adição de tool, mas **destrava** o gate de profundidade que hoje é implícito/subjetivo; integra (não duplica) com `high-stakes-gate`/`readiness-gate`/`qa-evidence`. Candidato a +1 capability (`risk-gate`) OU extensão de `regulatory-coverage-gate`.
- **Recast determinístico:** `risk_score.py --items risk.json` → entrada `{item, prob:1-3, impact:1-3, cat}` → saída determinística `{score=prob*impact, tier=P0..P3, gate=FAIL|CONCERNS|ADVISORY|NONE}` por matriz fixa (idêntica à do TEA, citada). Grava no ledger qa-evidence. **Sem julgamento subjetivo** — limiares explícitos.
- **Canário:** tabela-verdade da matriz 3×3 (9 casos) + mapeamento score→gate; FAIL-closed se input fora de 1–3.
- **Fonte:** risk-based-testing.md + run-trace.md (CONFIRMADO — matriz e limiares transcritos).
- **Submódulo (B'):** o **oracle de cobertura 4-tier** do `trace` (requisito formal → contrato/OpenAPI → ponteiro externo → inferido do código) pode **enriquecer** `qa-evidence`/`traceability` com fallback explícito de fonte de verdade. Avaliar sobreposição antes (pode já estar coberto pela cadeia decisão→fonte→versão).

### (C) game-dev balance → técnica de veículo *dados* no catálogo + método do `developer`
- **Ganho líquido:** método agnóstico de **calibração de parâmetros**: modelar matematicamente → testar isolado→junto→em escala → medir vs alvo com **red-flags quantificados** → iterar. Aplica a economia, manufatura, dados, software. Hoje o `developer`/`output-format` não tem um loop explícito de tuning-vs-alvo.
- **§0:** **estende** `methods.md` (+1 técnica "Parameter Tuning Loop / Red-Flag Thresholding", fase convergente-empírica) e/ou nota no `developer/SKILL.md`. Baixo custo.
- **Recast:** técnica como dado na tabela; `output_pattern: intent → model → isolate→integrate→scale → measure vs target → red-flag → iterate`.
- **Fonte:** balance-testing.md (CONFIRMADO).

### (D) WDS → step-file activation (file-first) + deliverables UX → `readiness-gate`/`discovery`
- **Ganho líquido:** a **ativação por step-files** é file-first/determinística (passos atômicos em arquivos) — ressoa nosso princípio; pode endurecer o boot de skills. Os deliverables UX (trigger-map, page-spec) alimentam o `readiness-gate` (que já valida UX spec).
- **§0:** **avaliar sobreposição** com nossos `.agent/workflows/*` antes — risco de duplicar. Provável ganho menor; priorizar A/B/C.
- **Fonte:** tree WDS (CONFIRMADO os paths; conteúdo dos steps não lido em profundidade — INFERIDO o valor).

### (F) bmad-automator → veredito SOURCED: método já-coberto; modelo de execução é mismatch-vs-nós (não bug dele)
- **Auto-crítica:** a v1 deste ADR escreveu *"deferir — conflita com HITL"* sem ler — asserção, não defeito provado. Corrigido lendo `docs/how-it-works.md` (CONFIRMADO).
- **Fato:** fases Init→Preflight→Configure→Finalize→**Execution loop (child sessions em tmux)**→Review; "monitor é *advisory*; verificação vem dos **artefatos** (sprint-status.yaml/story-file)". Gates humanos explícitos **não documentados nesta fonte** (o skill `bmad-story-automator-review` + docs "Story Execution/State And Resume" teriam o resto — não lidos).
- **Veredito (bounded, não vibe):** o **método** (orquestrar create→dev→test→review→retro) já é nosso (squad J0–J6 + reorchestration/retrospective gate). A **implementação** do automator otimiza para **autonomia desatendida + verificação por artefato** — arquiteturalmente o **oposto** do nosso HITL (verificação por gate humano, dono-decisor). Isso não é defeito *do automator* (é válido p/ stories desatendidas); é **mismatch provado para nós** → §0 net-gain de adoção é negativo (importaríamos um modelo de autonomia que rejeitamos deliberadamente). **Reaproveitável:** a ideia "monitor advisory + verificação por artefato estruturado" ecoa nosso `qa-evidence` ledger — registrar, não adotar o orquestrador.

### (G) bmad-builder → nota de roadmap cross-AI
- "Agent Skills open standard" para portabilidade cross-platform tangencia ADR-069/083 (web-bundles/cross-AI). Não é integração agora; registrar como referência para evolução do export cross-AI.

## Re-abertura retroativa — o princípio aplicado aos NOSSOS próprios descartes (pedido do dono)

O dono pediu revisitar "assuntos passados, descartados, sob esta ótica". Varredura de `Rejeitad*`/`específic*`/`produto de software` em `docs/adr/*` + `history.md`. **Leitura adversarial (anti re-abertura-preguiçosa):** a maioria das rejeições **sobrevive** — eram *alternativas de implementação* recusadas por motivo §0/determinismo (fail-open, não-determinístico, duplicação), não descartes-por-especificidade. Triagem:

| Item passado | Motivo original | Sob a nova ótica |
|---|---|---|
| ADR-081: `bmad-correct-course` | "scope SW + baixo ganho" | **Especificidade cai; §0 sobrevive parcialmente** — sobrepõe `reorchestration-gate` (RE-ORQUESTRAÇÃO). **Ação:** provar sobreposição; se há gap de "corrigir rota a meio-caminho", é candidato. |
| ADR-081: `bmad-sprint-*` | "scope SW específico" | Especificidade cai; método (decompor em incrementos c/ aceite) **já-coberto** por discovery/architect/pmo. §0 sobrevive (sem ganho). |
| ADR-081: `bmad-retrospective` | "scope SW específico" | Especificidade cai; **já-coberto** por `retrospective-gate` + retrospective do start-session. §0 sobrevive. |
| ADR-036/023: entry-point/requirements/evals "são produto de software → fora do núcleo" | agnosticismo (P12) | **NÃO é descarte — é *colocação na camada de app*** (ADR-023, ativada por `product_type`). Ver tensão abaixo. |

**Tensão load-bearing que levanto contra a leitura ingênua do princípio (adversarial, ADR-027):** "software é veículo, temos que passar por ele" tem duas leituras, e a perigosa quebra um invariante:
- **Leitura 1 (segura):** não *descartar* uma técnica por origem (SW/jogo/UX); extrair o método e integrá-lo — na **camada de app** (ADR-023/046) se for veículo-específico, ou recast agnóstico no núcleo se generaliza. Compatível com a arquitetura atual e com este ADR.
- **Leitura 2 (perigosa):** pôr coisa software-específica **dentro do núcleo `_shared/`**. Isso **viola ADR-010/020 (P12)**, que é *enforced por linter* (`check_core_agnostic.py`, que já pegou vazamentos reais). Adotar a Leitura 2 derruba uma trave.

**Observação crítica:** o framework **já encarna** "passamos pelo software como veículo" — é exatamente a **camada de app (ADR-023)**: suporte de primeira classe a produto de software/dados, ativado por `product_type`, **sem poluir o núcleo agnóstico**. Logo a pergunta retroativa real não é "revisitar rejeições" (a maioria não eram rejeições), e sim: **o dono quer elevar técnicas-de-veículo da camada de app para algo mais central? Se sim, como, sem violar P12?** Isso decide onde os recasts (A)–(D) aterrissam: núcleo (`_shared/`) vs app (`exemplos/`) vs abstração agnóstica.

### Resolução (decisão do dono 2026-06-17): MANTER P12; o bug era classificação, não o princípio

Decidido **Leitura 1** + diagnóstico: o ADR-081 não errou por *excesso* de agnosticismo, e sim por um **teste vago** ("isto é agnóstico?") que **confundiu FORMA com CONTEÚDO** e descartou a forma junto com o conteúdo. P12 permanece (diferenciador do framework vs BMAD software-específico; enforced; anti-contaminação cross-projeto — casos Vibra/Natulab/AIVI). A correção **não é rediscutir P12** — é **afiar o critério**, que o **ADR-046 já enuncia**: *"agnóstico = forma, não conteúdo"*.

**Teste de aterrissagem (substitui "isto é agnóstico?" por algo operável):**
- **FORMA agnóstica** (procedimento/mecanismo neutro: `risco = prob × impacto → gate`; métodos de pensamento) → **núcleo `_shared/`**.
- **CONTEÚDO de domínio** (normas/valores/listas: ±0,05% ANP; entry-point sem TTY; categorias SEC/PERF) → **blueprint na app** (ADR-046/023), default agnóstico + override por `product_type`.

**Aplicação aos recasts:**
- **(B) risk-score** = caso-modelo: mecanismo prob×impacto→gate no **núcleo**; **lista** de categorias de risco como **blueprint configurável** (não hardcodar TECH/SEC/PERF no núcleo — isso seria conteúdo).
- **(A) CIS divergente** = forma pura → estende `methods.md` (núcleo), sem conteúdo de domínio.
- **(C) tuning-loop** = forma (modelar→medir-vs-alvo→iterar) núcleo; os *alvos/red-flags* numéricos são conteúdo → app.

**Custo declarado (auto-crítica):** a linha forma/conteúdo é por vezes borrada, e o `check_core_agnostic.py` hoje barra por *sentinela de domínio* — precisará **evoluir para distinguir forma-permitida de conteúdo-barrado**. Isso é um **ADR próprio pequeno** (backlog), pré-requisito para (B) não ser barrado falso-positivo pelo linter ao colocar o mecanismo de risco no núcleo.

## Alternativas consideradas

1. **Manter ADR-081 como está (rejeições por especificidade).** Rejeitada — o dono declarou o rationale inválido; mantê-lo perpetua o ponto cego.
2. **Absorver as técnicas como prosa (copiar docs BMAD).** Rejeitada — viola o pedido (i): integração é **recast** (ferramenta/determinismo/file-first), não cópia.
3. **Construir todas as integrações A–G agora.** Rejeitada — viola §0 e "não presumir"; cada recast é um BLOCO com PR + qa-critic. Este ADR é **decision-ready**, não implementação.
4. **Recast seletivo gateado por §0 (ESCOLHIDA).** O dono escolhe a ordem; recomendação: **A → B → C** (ganho/custo), D/B' após avaliar sobreposição, F/G deferidos.

## Consequências

**Positivas:** fecha a falha de auditoria (13/13 com fonte verificável vs 1/13 sem fonte); corrige o ponto cego de princípio (veículo ≠ descarte); reabre net-positives reais que a especificidade ocultava (risk-gating determinístico é o mais valioso e estava rejeitado); todo recast nasce **ferramental + gateado**, alinhado ao idioma do framework. **Negativas/limite (declarado):** se todos A–G forem construídos, +1 tool + ≥3 edições de skill — mitigado pela escolha §0 do dono (não tudo). O conjunto das 8 técnicas CIS não-listadas é **DESCONHECIDO** (flagado, não inventado). A avaliação de sobreposição de (B'/D) com qa-evidence/workflows é **pré-requisito** antes de construir.

## Implementação (ponteiro — só após escolha §0 do dono + qa-critic)

- Recomendação de sequência: **(A)** estende advanced-elicitation → **(B)** `tools/risk_score.py` + canário matriz 3×3 → **(C)** técnica tuning no catálogo. Cada um: branch própria + PR + qa-critic heterogêneo (escada ADR-078/082) + qa_evidence.py.
- `capabilities.json`: avaliar `risk-gate` (B) como +1; A/C estendem `advanced-elicitation` (sem nova capability — régua §0).
- `CHANGELOG.md`: entrada ao fechar cada bloco com qa-critic PASS.
