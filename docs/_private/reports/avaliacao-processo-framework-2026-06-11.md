# Avaliação do Framework de Metacognição — processo, papéis, modelos, contexto

**Data:** 2026-06-11 · **Autor do bloco:** Claude Fable 5 (`claude-fable-5`) · **Modo:** dev (MASTER-CANÔNICO)
**Rota declarada:** multi-etapa → squad (pmo → explorer → architect-propositivo → docops) — auditoria read-only; nenhuma mudança de código executada.
**Pedido do dono:** avaliar o framework e propor melhorias em 6 eixos — (1) garantia de fluxo + QA adversarial entre papéis; (2) otimização de troca de modelo por papel; (3) desenvolvimento sênior (arquitetura, harness, spec-driven, UX); (4) melhor resultado (eficiência/eficácia/efetividade); (5) otimização de contexto; (6) economia de tokens. Remoções = SUGESTÃO + plano, não execução.

---

## 0. Sumário executivo

O framework está **maduro no desenho e desigual no enforcement**. O desenho das junções J0–J6, do QA bicelular e dos gates fail-closed de release é sólido e raro de se ver; o ponto fraco sistêmico é que **a malha fail-closed está ancorada no evento "release no CHANGELOG"** — quando esse evento não acontece (ou o CI é pulado), a malha inteira fica inerte. Esta sessão encontrou **prova viva**: o bloco v1.55.0 (ADR-060, port dos hooks PS→Python) foi mergeado na main **sem entrada no CHANGELOG, sem qa-evidence e com CI pulado por admin-bypass** (billing) — exatamente o cenário "bypass, não ausência" que a v1.53.0 diagnosticou.

As 12 propostas abaixo seguem a régua §0 (cada uma declara o que funde/remove ou que eval destrava). As 3 de maior alavancagem:

1. **P1 — version-claim canary**: fecha o buraco demonstrado pelo v1.55.0 (commit declara versão → CHANGELOG deve ter a entrada).
2. **P5 — `model-policy.json` única fonte**: hoje a política de modelo vive em 3 lugares divergentes (handoff.py, frontmatter dos subagentes, prosa do ADR-018) e **não conhece o tier Fable/Mythos**.
3. **P9 — dieta do CLAUDE.md**: o arquivo virou acreção histórica (resumo de ~15 ADRs já linkadas) e é pago **em todo turno de toda sessão** — maior ganho de token disponível sem perder garantia nenhuma.

---

## 1. Escopo da auditoria (file-first)

**Lido integralmente [CONFIRMADO]:** `AGENT-FRAMEWORK.md` v2.3 · `CLAUDE.md` · `CAPABILITIES.md` (57 capacidades) · skills de processo (pmo, architect, developer, qa-critic + 9 rules SE/ENTÃO, docops, discovery completo, explorer via descrição) · `_shared/metacognition-core` · `_meta/subagent-isolation.md` · workflows `/handoff` e `/checkpoint` · subagentes `.claude/agents/{qa-critic,explorer}.md` · `tools/handoff.py` (regras de modelo) · topo do CHANGELOG · execution-report 2026-06-11 (untracked).

**NÃO lido nesta sessão [DESCONHECIDO — declarado, não silenciado]:** `exemplos/dominio-software/` (ux-designer, evals-engineer, blueprint), `.agent/rules/0*.md` conteúdo, `posture.md`, `_shared/execution-modes` detalhe, corpo das ADRs 011/018/045/074/076. Afirmações sobre esses arquivos abaixo estão marcadas [INFERIDO] a partir das referências cruzadas.

---

## 2. Achados imediatos de housekeeping (anteriores a qualquer melhoria)

| # | Achado | Evidência | Classificação |
|---|---|---|---|
| H1 | **Bloco v1.55.0 mergeado sem fechamento**: commit `7225df6` declara "v1.55.0", mas CHANGELOG topo = 1.54.0 (sem entrada 1.55.0), último qa-evidence = `_meta/qa/v1.54.0-release.md`, execution-report do bloco está **untracked**. O próprio report registra: "CI falhou por billing → enforce_admins desabilitado via API → merge admin". | `git show 7225df6` + `Select-String CHANGELOG 1.55.0` (vazio) + `_meta/qa/` listing | CONFIRMADO |
| H2 | Diretório `Python/` **vazio e untracked** na raiz — transiente acidental. | `Get-ChildItem Python -Recurse -Force` → vazio | CONFIRMADO |
| H3 | Hook SessionStart **injetou o boot ~5× na mesma abertura** (5 banners + 2 cópias do contexto de 11KB persistido) — desperdício direto de contexto a cada sessão. | transcript desta sessão | CONFIRMADO (sintoma) / INFERIDO (causa: múltiplos matchers ou re-disparo do harness) |
| H4 | `docops/SKILL.md` §Encerramento ainda manda rodar `consistency-gate.ps1` (PowerShell) — vetável por EDR na máquina afetada; ADR-060 portou 4 hooks mas não este. | docops SKILL linha 35 | CONFIRMADO |

**Recomendação H1 (fechar antes de qualquer bloco novo):** ou (a) registrar a entrada 1.55.0 no CHANGELOG + qa-evidence retroativo com postura + checkpoint datado + commit do execution-report, ou (b) reclassificar o port como parte do fechamento 1.54.x. O estado atual viola `test_adr_changelog_sync`/`test_release_checkpoint` *em espírito* sem disparar nenhum deles — ver P1. O admin-bypass do CI deve ser registrado como **override declarado** (ADR-051: custo+consequência informados), não como nota de rodapé do report.

---

## 3. Diagnóstico e propostas por eixo

### Eixo 1 — Garantir que o fluxo seja seguido (junções + QA adversarial)

**O que já existe e funciona [CONFIRMADO]:** J0–J6 com artefato-gate e critério binário declarados; forward-only com process-critic de rewind; qa-evidence fail-closed (`test_qa_evidence` + `test_posture_gate` + `test_release_checkpoint` + `test_adr_changelog_sync`); 9 rules SE/ENTÃO determinísticas no qa-critic; route-gate + boot_check com liveness anti-veto.

**Lacuna estrutural:** a malha fail-closed dispara **só quando há versão nova no CHANGELOG e o CI roda**. Dois modos de escape, ambos observados:
- *Escape A — não declarar o release:* commit faz o trabalho e declara a versão na mensagem, mas o CHANGELOG não ganha a entrada → nenhum gate de release acorda (caso H1).
- *Escape B — CI pulado:* admin-merge com CI vermelho por motivo não-relacionado (billing) → fail-closed virou fail-open na prática, sem registro de override.

E as junções J0–J3 são **prosa pura**: o PMO "adversarial" é o mesmo contexto/modelo que está fazendo o trabalho — não há rastro mecânico de que o gate foi aplicado (o PC checa "process compliance" depois, mas também em prosa).

**Propostas:**

- **P1 — Canário version-claim (fail-closed, CI + boot_check).** Se a mensagem de qualquer commit no range `origin/main..HEAD` (e do HEAD da main) casa `v\d+\.\d+\.\d+`, a versão citada deve existir como heading no CHANGELOG. É o **inverso** do `adr-changelog-sync` existente e fecha o Escape A. Régua §0: estende `test_consistency_closing.py` (não cria arquivo novo); destrava eval inalcançável (H1 passou por 4 gates sem disparar nenhum).
- **P2 — Override de CI é evento de processo.** Regra SE/ENTÃO nº 10 no qa-critic + 1 verificação no consistency/closing: SE o PR foi mergeado com check vermelho/pulado (via `gh api`), ENTÃO exige linha `OVERRIDE:` no history.md com motivo+custo+consequência (ADR-051). Advisory onde `gh` não está disponível (declarado). Régua §0: edita skill existente + 1 função no teste existente.
- **P3 — Ledger mínimo de junções (J0–J3 deixam rastro).** Ao declarar `/handoff B — junção J_n PASS`, o orquestrador apensa 1 linha JSON em `_meta/qa/<bloco>-junctions.jsonl` (junção, artefato-gate, evidência, timestamp). O process-critic e o `test_qa_evidence` ganham matéria-prima objetiva para a dimensão (iv) "process compliance" — hoje invisível. Régua §0: estende `tools/qa_evidence.py` (não cria ferramenta); funde com o que o PC já deveria checar em prosa. **Custo declarado:** +1 escrita por junção (~5 linhas/bloco) — barato; o risco a evitar é inflar isso em formulário.
- **P4 — `validation.md` como pré-condição mecânica de J3.** O developer declara consumir `validation.md`, mas nada barra J2→J3 sem ele (os linters `check_completeness`/`check_spec_depth` atuam sobre a spec quando ela existe). Check binário: J3 PASS exige `docs/specs/<feature>/validation.md` existente OU justificativa declarada no ledger P3 ("trivial — N/A", herda o padrão do RRC). Fecha o caminho "fluxo informal pula a spec e o qa-critic valida contra nada". Régua §0: 1 condição no mesmo ledger.

### Eixo 2 — Otimizar a troca de modelo entre papéis

**O que existe [CONFIRMADO]:** `tools/handoff.py::suggest_model` (papel+risco → opus/sonnet, determinístico, com canário); ADR-018 heterogeneidade gerador↔crítico (família ≠ autor, Zhang 2025); subagentes com `model: sonnet` fixo no frontmatter; hub cross-IA Claude↔Gemini (ADR-069, não configurado nesta máquina).

**Lacunas:**
- A política de modelo vive em **3 lugares que já divergem**: `suggest_model` (só retorna opus/sonnet; conhece `fable` apenas como `--author`), frontmatter dos subagentes (sonnet fixo, ignora quem é o autor), e prosa (ADR-018/checkpoint.md). Com o tier **Fable/Mythos acima do Opus** disponível, a regra "architect/discovery → mais capaz (Opus)" ficou **stale por construção** — está hardcoded a um nome de modelo, não a um tier.
- "Família diferente" dentro do Claude Code é inalcançável (opus/sonnet/haiku/fable = mesma família). A heterogeneidade real exige o hub cross-IA; hoje a degradação não é explicitada como escada.
- Haiku não é usado em lugar nenhum — papéis mecânicos (docops bulk, varreduras do explorer, gerar índices) pagam preço de sonnet/opus sem necessidade.

**Propostas:**

- **P5 — `tools/model-policy.json` como fonte única da política de modelo.** Tabela papel×risco→**tier** (`max-capability` / `balanced` / `economy` / `heterogeneous`) + mapa tier→model-id vigente (hoje: max=fable, balanced=sonnet, economy=haiku; opus = fallback de max onde fable indisponível). Consumidores: `handoff.py` (lê o JSON em vez das constantes), instrução de spawn dos subagentes (o orquestrador passa `model:` do policy na chamada `Agent(...)`, sobrepondo o frontmatter), e o canário `test_handoff.py` (valida o JSON, não os literais). Régua §0: **remove** as regras hardcoded de `suggest_model` e a divergência de 3 fontes → funde em 1; atualizar modelo novo vira edição de dado, não de código.
- **P6 — Escada de heterogeneidade declarada (emenda ao ADR-018).** Ordem de preferência para qa-critic/PC: (1) **família diferente** via hub cross-IA quando configurado (Gemini revisa bloco Claude e vice-versa — o mecanismo de outbox já existe); (2) **modelo diferente, mesma família** (autor fable/opus → crítico sonnet; autor sonnet → crítico opus/fable — *nunca* o sonnet fixo de hoje quando o autor já é sonnet); (3) **mesmo modelo, contexto fresh** — permitido mas **declarado no veredito** ("heterogeneidade indisponível"), nunca silencioso. Régua §0: edita `_meta/subagent-isolation.md` + frontmatter dos 2 subagentes; zero arquivo novo.
- **P7 — Papéis mecânicos → economy tier.** docops (sync de contagens, índices, CHANGELOG), explorer em varredura ampla (mapa de estrutura, sem julgamento) e geração de relatórios determinísticos rodam em haiku via policy. Julgamento (qa-critic, architect, discovery) **nunca** desce de balanced. Ganho direto de token/latência sem tocar em garantia (os gates que validam a saída mecânica são canários Python, não o modelo).

### Eixo 3 — Desenvolvimento sênior (arquitetura, harness, spec-driven, UX)

**O que existe [CONFIRMADO]:** cadeia spec-driven completa (discovery profundo com anti-raso obrigatório + elicitação consultiva com defaults sênior + linters de spec; architect com ≥3 alternativas e ADR; developer com file/glossário/ADR/spec-first; qa-critic adversarial com 9 rules). UX e evals vivem na aplicação `dominio-software` (ux-designer, evals-engineer) [INFERIDO do ADR-023 — app não lida nesta sessão], o que é o desenho certo para núcleo agnóstico.

**Lacunas:**
- **"Testes (se aplicável)" em J3 é a única cláusula frouxa da cadeia.** Tudo o mais na junção é binário; "se aplicável" sem justificativa registrada é onde a senioridade escorre. (O caso v1.55.0 de novo: testes locais PASS, mas CI nunca validou — combinação de "se aplicável" + Escape B.)
- **O harness do produto não tem gate de fumaça.** O framework valida *processo* com canários, mas a entrega de software depende de o evals-engineer da app existir e ser carregado; no núcleo, nada exige "o artefato roda" (a capability `entrypoint-tty-gate` cobre o entrypoint do *framework*, não do produto do usuário).
- **UX só entra se `product_type` casa com a app** — se o mission-gate não rodar (EDR) e o agente não declarar inline, um gui-app pode atravessar o fluxo sem o papel de UX. O modo non-admin já prevê "gates anunciados"; falta o item product_type→papéis na lista de inline-gates anunciados? [INFERIDO — `MODO-NON-ADMIN.md` não lido; verificar antes de editar.]

**Propostas:**

- **P8 — Fechar a cláusula "se aplicável".** Em J3, ausência de teste exige justificativa de 1 linha no ledger (P3): `testes: N/A — <motivo>`. O qa-critic ganha rule SE/ENTÃO: SE diff toca código executável E ledger diz N/A sem motivo OU motivo é "trivial" com >2 arquivos tocados, ENTÃO REPROVADO. Régua §0: edita skill existente; mecaniza padrão já cobrado em prosa.
- **P8b — Smoke-gate de produto (na app, não no núcleo).** Para `product_type` executável/gui/pipeline: J4 exige evidência de **1 execução real do entrypoint** (saída capturada), não só testes unitários. Lar: `exemplos/dominio-software/evals-engineer` (mantém núcleo agnóstico). Verificar primeiro o que o evals-engineer já cobre — pode já existir; se existir, a proposta degrada para "wirar no ledger P3". [INFERIDO]

### Eixos 4–6 — Resultado, contexto e tokens

**O que existe [CONFIRMADO]:** ADR-016 (compaction por faixa medida) + compaction-gate; context-budget hook no Read; doc-intake determinístico; progressive disclosure (companions sob demanda); isolamento por subagente; telemetria "placar gate×achado" no history; J6 re-orquestração.

**Lacunas e propostas:**

- **P9 — Dieta do CLAUDE.md (maior ganho de token disponível).** O CLAUDE.md hoje carrega ~12 seções que são **resumos de ADRs já linkadas** (v1.7→v1.46: modos, non-admin, auto-boot, régua, cascata, método sênior, agnosticismo, handoff, bicelular, runtime hooks, entrada determinística, capabilities). Isso é pago em **todo turno de toda sessão**. Proposta: reduzir cada seção a 1–3 linhas de *regra operacional + ponteiro* (a regra que o agente precisa AGORA fica; o histórico/justificativa vai para a ADR, que já existe). Estimativa: corte de 40–60% do arquivo sem perda de garantia — a fonte única continua sendo `_shared/` e as ADRs (aliás, o CLAUDE.md gordo **viola a própria régua §0 e o princípio 5**: recopia resumo de regra que tem lar). Mesmo tratamento para o campo `source:` dos frontmatters de skill (a história de versões do discovery tem 9 linhas dentro de um frontmatter carregado em listagens). **SUGESTÃO de remoção — requer aprovação + ADR** (anti-rename/traceability: é edição de arquivo de autoridade).
- **P10 — Corrigir o boot 5× (H3).** Investigar matchers do SessionStart em `.claude/settings.json` + comportamento do harness; aplicar carimbo de idempotência por sessão (mesmo padrão do route-gate 1×/sessão). Ganho: ~20–40KB de contexto recuperados por sessão antes do primeiro turno útil.
- **P11 — Poda guiada por telemetria (fechar o loop que já existe).** O history já registra "placar gate×achado" e `sem-disparo` (ADR-017); falta o passo que a régua §0 pede: **revisão periódica** (a cada N releases, no J6) dos gates/rules com `sem-disparo` alto → candidatos a fusão/remoção via ADR. Hoje o framework só adiciona gate; o mecanismo de REMOVER por evidência está desenhado mas sem cadência. Régua §0: é a régua §0 aplicada a si mesma.
- **P12 — qa-critic SKILL em progressive disclosure.** 12.6KB carregados em toda ativação; as 9 rules SE/ENTÃO + notas de reconciliação de vocabulário podem ir a companion `rules.md` carregado em J4/PC (mesmo padrão dos companions do discovery, ADR-003). Corte de ~50% no custo de ativação do papel mais frequente depois do PMO. **SUGESTÃO** — mesma família da P9.

---

## 4. Plano faseado (sugestão — nada executado)

| Fase | Conteúdo | Esforço | Pré-req |
|---|---|---|---|
| **F0 — housekeeping (antes de tudo)** | Fechar H1 (CHANGELOG 1.55.0 + qa-evidence retroativo + checkpoint + commitar execution-report + registrar override do CI) · remover `Python/` vazio · H4 (apontar docops para caminho Python-first) | horas | decisão do dono sobre (a)/(b) em H1 |
| **F1 — enforcement do fluxo** | P1 (version-claim) → P2 (override de CI) → P3 (ledger de junções) → P4 (validation.md em J3) | 1 bloco com ADR única ("enforcement de junção e release") | F0 |
| **F2 — política de modelo** | P5 (model-policy.json) → P6 (escada de heterogeneidade) → P7 (economy tier) | 1 bloco, ADR emendando ADR-018/076 | — (independente de F1) |
| **F3 — senioridade da entrega** | P8 (testes N/A justificado) → P8b (smoke-gate na app, após verificar evals-engineer) | 1 bloco | P3 (ledger) |
| **F4 — dieta de contexto** | P10 (boot 5×) → P9 (CLAUDE.md) → P12 (qa-critic companion) → P11 (cadência de poda no J6) | 1 bloco; P9/P12 exigem ADR própria (SUGESTÃO de remoção) | — |

Cada fase fecha com o próprio fluxo do framework (J0–J5 + PC + qa-evidence) — dogfood obrigatório, e F1 cria exatamente os trilhos que as fases seguintes usarão.

## 5. Tensões surfadas (surface-and-reconcile, ADR-051)

1. **"Garantir o fluxo" × economia de tokens:** todo gate novo custa contexto/latência. As propostas P1–P4 foram desenhadas como *dados apensados a mecanismos existentes* (1 linha de ledger, 1 função em teste existente) precisamente para não recriar o problema que a régua §0 combate. Se o dono preferir, P3 pode degradar para "só em bloco substantivo" (mesmo critério do method-audit).
2. **Heterogeneidade real exige sair da família Claude:** dentro do Claude Code, "família diferente" (ADR-018) é tecnicamente impossível; a escada P6 declara a degradação em vez de fingir. A alternativa plena é ativar o hub cross-IA (clonar `metacognition-hub`) — hoje skip declarado no boot.
3. **P9 mexe em arquivo de autoridade:** corte do CLAUDE.md muda o que TODA sessão futura lê. Por isso é SUGESTÃO com ADR + RRC completo, nunca edição direta.

## 6. Método-audit notes (princípio 11 — candidatas a `history.md ## Aprendizado`)

- `Method-audit: bloco v1.55.0 mergeado sem fechamento e sem disparar nenhum gate · Causa-raiz: malha fail-closed ancorada exclusivamente no evento "versão nova no CHANGELOG" + override de CI sem registro · Proposta (lean): P1+P2 (estender test_consistency_closing + rule SE/ENTÃO nº 10).`
- `Method-audit: política de modelo divergente em 3 fontes e cega ao tier mais capaz disponível · Causa-raiz: model-ids hardcoded em código/frontmatter em vez de policy-as-data · Proposta (lean): P5 (fundir em model-policy.json).`
- `Method-audit: boot injetou o mesmo contexto ~5× na abertura · Causa-raiz: [INFERIDO] matcher duplicado ou re-disparo de SessionStart sem carimbo de idempotência · Proposta (lean): P10 (carimbo 1×/sessão, padrão route-gate).`

---

*Relatório read-only; nenhum arquivo do núcleo foi alterado. Próximo passo sugerido: decisão do dono sobre F0-H1 (fechamento retroativo do v1.55.0) e aprovação das fases — cada fase vira bloco com ADR própria via PR-flow.*
