---
papel: discovery
sub_modo: pesquisa-cascata
pergunta_principal: "Quais mecanismos e padrões podem resolver os problemas estruturais do metacognition-gemini, em ambiente Antigravity IDE sem hooks nativos do Claude Code?"
rodadas: 1
data: 2026-06-09
status: revisado
qa_veredito: APROVADO_COM_RESSALVAS
qa_rodadas: 2
qa_altos_corrigidos: 8
---

# Research Brief — Soluções para Problemas Estruturais do metacognition-gemini

> Gerado pelo sub-modo `pesquisa-cascata` (ADR-007). Fontes: 4 sub-agentes explorers
> independentes (SP-A, SP-B, SP-C, SP-D/SP-E) + relatório de incidentes do dono (2026-06-09).
> QA adversarial rodada 2 aplicado — 8 ALTOs corrigidos.
> Destina-se ao architect para planejamento de intervenções no `metacognition-gemini`.

---

## Rastreabilidade de incidentes → soluções

> Adicionado após QA (ALTO-02). O architect deve consultar esta tabela primeiro.

| Incidente nomeado | Causa-raiz (achado) | Soluções mapeadas | Passos em §9 |
|---|---|---|---|
| **Incidente 1 — Monolith QA** (mesmo modelo dev+QA, sem separação real) | C-08, C-21, C-22: `session_orchestrator.py` sem verificação de modelo; QA em mesma sessão | Integrar ADR-018 no session_orchestrator.py (A-04); fortalecer verificação de identidade de modelo (GAP-4) | Passo 5, Passo 8 (novo) |
| **Incidente 2 — Cross-domain contamination** (CWD bias, normas hardcoded em prompt núcleo) | C-01, C-16, D-06: GEMINI_Metcognition.txt v3.1 com stack SAP/BI/normas ativo; linter não o varre | Fase 4 ADR-075 (substituir prompt); expandir escopo linter (Passo 7); gate preventivo permanente (Passo 9 novo) | Passo 1, Passo 7, Passo 9 |

---

## 1. Pergunta principal

Quais mecanismos e padrões podem resolver os 3 problemas estruturais críticos do
`metacognition-gemini` — (1) identidade de prompt dupla/domínio-contaminado, (2) regras
contraditórias institucionalizadas por sicofância, (3) ausência de wiring de gates —
considerando que o ambiente de uso real (Antigravity IDE) não tem suporte nativo a hooks
do Claude Code?

---

## 1.5 Escopo declarado pelo discovery (ADR-010)

> Modo A (Transcribe) — declarações nominais confirmadas em ≥2 fontes + sem contradição.

### (a) Regulado?
- `[CONFIRMADO]` Não regulado no núcleo do framework — Fonte: ADR-010/P12 (agnóstico de domínio).
  O `GEMINI_Metcognition.txt` contém normas hardcoded (ANVISA CSV, FDA 21 CFR, GAMP 5, BACEN,
  PCI-DSS, SOX) mas isso é o **problema investigado**, não o escopo desta pesquisa.
- **Origem:** via leitura direta dos relatórios de incidente (reports-improve-cross-ai/) e auditoria.

### (b) Alto-risco?
- `[CONFIRMADO]` Sim — parcialmente. As intervenções tocam no documento de prompt ativo do agente
  Gemini e em ADRs já "Aceitos" no repo Gemini. Remover/substituir esses arquivos tem efeito imediato
  no comportamento do agente em sessões de produção do dono. Gate humano (HITL) obrigatório antes de
  qualquer modificação nos arquivos-raiz do Gemini.

### (c) Regras com semântica?
- `[CONFIRMADO]` Sim — a separação núcleo/domínio (P12/ADR-010) é regra de negócio onde o "como"
  importa: um arquivo que parece funcionar mas viola o agnosticismo causa cross-pollination silenciosa.
- `[CONFIRMADO]` A ordem de precedência de instruções (P6→P14 do metacognition-core) é semântica:
  violar a ordem silenciosamente é pior do que falhar ruidosamente.

### (d) Gaps não-bloqueantes?
- `[CONFIRMADO]` CLI Gemini: desconhecido se disponível no ambiente do dono. Afeta apenas a
  Alternativa 3 de separação multi-LLM (Seção 4, C-22). · Decisão: manter gap.
- `[CONFIRMADO]` Conteúdo completo do GEMINI_Metcognition.txt v3.1: catalogado como problema mas
  não lido linha-a-linha pelo explorer. · Decisão: manter gap — diagnóstico é estrutural, não lexical.

**Gates downstream:** (b) afirmativo → gate humano em modificações de alto impacto (HITL antes de
substituir GEMINI_Metcognition.txt). (c) afirmativo → reforço sênior aplicado nesta pesquisa.

---

## 2. Decomposição (5 sub-perguntas)

1. **SP-A** — Quais soluções o próprio repo Gemini já propõe? (propostas internas E1-E7, ADR-075)
2. **SP-B** — Que mecanismos do framework canônico funcionam sem hooks e são portáveis ao Gemini?
3. **SP-C** — Como resolver "prompt único autoritativo vs especialização de domínio" sem violar P12?
4. **SP-D** — Quais mecanismos anti-sicofância existem no canônico e são portáveis?
5. **SP-E** — Como implementar separação multi-LLM sem subagentes nativos do Claude Code?

---

## 3. Fontes consultadas

| Fonte | Tipo | Autoridade | Relevância | Verificável neste repo |
|---|---|---|---|---|
| `metacognition-gemini/reports-improve-cross-ai/005-relatorio-cross-ia-fefo-fifo-atd36246.md` | relato de incidente real | alta | direta | Não — repo Gemini |
| `metacognition-gemini/reports-improve-cross-ai/003-relatorio-falha-sicofancia-regra-n-hitl.md` | post-mortem sicofância | alta | direta | Não — repo Gemini |
| `metacognition-gemini/reports-improve-cross-ai/004-insight-cross-ia-contra-iteracao-ilimitada.md` | debate ADR-076 | alta | direta | Não — repo Gemini |
| `metacognition-gemini/reports-improve-cross-ai/claude_to_gemini_20260605.md` | veredito canônico cross-IA | alta | direta | Não — repo Gemini |
| `metacognition-gemini/reports-improve-cross-ai/gemini_to_claude_20260608.md` | handoff mais recente | alta | direta | Não — repo Gemini |
| `metacognition-gemini/docs/adr/075-sincronizacao-senior-gemini-correcao-vies.md` | ADR Aceito Gemini | alta | direta | Não — repo Gemini |
| `metacognition-gemini/docs/SQUAD_GEMINI.md` | regra QA separado | alta | direta | Não — repo Gemini |
| `metacognition-gemini/tools/session_orchestrator.py` | mecanismo real de QA | alta | direta | Não — repo Gemini |
| `metacognition-gemini/.agent/rules/` (00..05) | regras ativas | média | direta | Não — repo Gemini |
| `guia/MODO-NON-ADMIN.md` | doutrina gates inline | alta | direta | **Sim — canônico** |
| `tools/` (19 ferramentas Python portáveis) | gates canônicos | alta | direta | **Sim — canônico** |
| `tools/effect-rules.json` | política effect-gate | alta | direta | **Sim — canônico** |
| `exemplos/README.md` + ADR-023 | padrão domínio/núcleo | alta | direta | **Sim — canônico** |
| `docs/adr/018-qa-turno-unico-heterogeneidade.md` | ADR-018 multi-LLM | alta | direta | **Sim — canônico** |
| `_meta/subagent-isolation.md` | política de isolamento | alta | direta | **Sim — canônico** |
| `.claude/agents/qa-critic.md` | definição subagente canônico | alta | direta | **Sim — canônico** |
| `_shared/metacognition-core/SKILL.md` §ADR-051 | anti-sicofância inline | alta | direta | **Sim — canônico** |
| `_shared/qa-critic/SKILL.md` rule #9 | anti-viés-oráculo | alta | direta | **Sim — canônico** |
| `_shared/qa-critic/posture.md` + ADR-074 emenda 3 | posture-gate | alta | direta | **Sim — canônico** |
| `tools/test_sycophancy.py` + ADR-041 | canário anti-sicofância | alta | direta | **Sim — canônico** |
| `AGENT-FRAMEWORK.md` §6 P11+P13 | princípios metacognitivos | alta | direta | **Sim — canônico** |

> **Nota sobre fontes Gemini:** achados derivados exclusivamente de fontes no repo Gemini
> (não verificáveis neste repo canônico) são classificados como **INFERIDO**, não CONFIRMADO —
> correção aplicada após QA (ALTO-11).

---

## 4. Achados classificados

### CONFIRMADO (fonte direta verificável neste repo canônico)

**Bloco 1 — Mecanismos portáveis do canônico**

- C-01: 19 ferramentas Python do canônico são **totalmente portáveis** para Gemini (stdlib-only,
  sem dependência de hooks). Incluem: `context_budget.py`, `check_core_agnostic.py`,
  `check_repo_sync.py`, `shadow_sync.py`, `check_spec_depth.py`, `check_completeness.py`,
  `doc_intake.py`, `check_reorchestration.py`, e outros 11.
  — Fonte: SP-B explorer, leitura direta de `tools/` neste repo

- C-02: 4 gates do canônico funcionam como **instrução de comportamento** (doutrina non-admin/ADR-047)
  sem código adicional: route-gate, mission-gate, overwrite-guard, anti-sicofância ADR-051.
  São regras declaradas em `guia/MODO-NON-ADMIN.md`.
  — Fonte: SP-B explorer, `guia/MODO-NON-ADMIN.md` (verificável neste repo)

- C-03: `effect-rules.json` é política JSON portável com 12 regras do effect-gate (T2/T3 por
  família de efeito). O interpretador `effect_gate.py` **não existe** — gap de ~50 linhas Python.
  — Fonte: SP-B explorer, `tools/effect-rules.json` (verificável neste repo)

- C-04: `consistency-gate` existe como `.ps1` sem equivalente Python. A lógica é implementável
  em Python (git log, comparação de versões, verificação de unpushed).
  — Fonte: SP-B explorer (verificável neste repo)

- C-05: `compaction-gate` e `execution-modes ratchet` são **hook-dependentes** sem equivalente
  portável declarado. Dependem de primitivas do Claude Code (`PreCompact`, `settings.json`).
  — Fonte: SP-B explorer (verificável neste repo)

- C-06: O padrão canônico "adicionar domínio sem poluir núcleo" = clonar `_template` em
  `exemplos/<dominio>/`, preencher somente o domínio, referenciar (não copiar) `_shared/`.
  Criterion: "esta regra precisa saber o domínio para funcionar?" Sim → aplicação.
  — Fonte: SP-C explorer, `exemplos/README.md`, ADR-023 (verificáveis neste repo)

- C-07: `exemplos/dominio-software/` (ADR-023) demonstra empiricamente que é possível adicionar
  2 papéis especializados sem nenhuma alteração em `_shared/`. O ativador é `product_type`
  declarado em `mission.md`, lido pelo hook `mission-gate`.
  — Fonte: SP-C explorer (verificável neste repo)

- C-08: 8 mecanismos anti-sicofância existem no canônico. Todos 8 são portáveis (Python puro ou
  prosa inline): ADR-051 clause, ADR-011/018 adversarial protocol, test_sycophancy canary (ADR-041),
  rule #9 anti-oracle-bias (ADR-035), posture-gate (ADR-074), qa_evidence, check_core_agnostic, P11.
  — Fonte: SP-D explorer (verificável neste repo)

- C-09: A cláusula anti-sicofância do `metacognition-core` (ADR-051) é prosa sempre-carregada:
  "pedido do dono não é imune a questionamento; surface tensões antes de cumprir". Portável para
  qualquer IDE via AGENTS.md/system prompt — não exige hook nem Python.
  — Fonte: SP-D explorer, `_shared/metacognition-core/SKILL.md` (verificável neste repo)

- C-10: O protocolo adversarial ADR-018 (steelman→ataque→veredito) entrega ~80% do ganho da
  heterogeneidade de modelo sem exigir subagente separado. Fallback explícito na ADR: "No chat
  (sem troca de modelo), o protocolo de 1 turno vale igual; a heterogeneidade fica indisponível
  e isso é DECLARADO, não fingido."
  — Fonte: SP-E explorer, `docs/adr/018-qa-turno-unico-heterogeneidade.md` (verificável)

- C-11: A separação multi-LLM canônica exige três primitivas do Claude Code: (1) `Agent()` com
  `model:`, (2) contexto fresh garantido, (3) toolset restrito por definição de arquivo — não por
  prompt. Sem essas primitivas, a separação é simulada.
  — Fonte: SP-E explorer, `.claude/agents/qa-critic.md`, `_meta/subagent-isolation.md` (verificáveis)

- C-12: `check_core_agnostic.py` varre `_shared/`, `.agent/skills/`, `AGENT-FRAMEWORK.md`,
  `CLAUDE.md`, `AGENTS.md`. Não inclui `GEMINI_Metcognition.txt` (arquivo no repo Gemini).
  — Fonte: SP-C explorer (verificável neste repo — o scan do script foi confirmado)

---

### INFERIDO (fonte indireta ou cruzamento de fontes sem prova direta verificável neste repo)

> Fontes marcadas "Não — repo Gemini" em §3 geram classificação INFERIDO nesta seção.

- I-01: GEMINI_Metcognition.txt v3.1 é o documento ativo no Antigravity IDE (não o
  GEMINI-FRAMEWORK.md v2.3). O boot declara `[CONFIRMADO] Framework Metacognitivo (v3.1)`.
  — Base: SP-A explorer leu arquivos no repo Gemini + execution-report-2026-06-08-boot-gemini-paridade.md.
  Fonte verificável apenas no repo Gemini.

- I-02: ADR-076 (MAX_ROUNDS=3 universal) surgiu de incidente de sicofância (relatório 003).
  O claude-master rejeitou explicitamente em `claude_to_gemini_20260605.md`.
  — Base: SP-A explorer lendo relatório 003 + relatório 004 (ambos no repo Gemini).

- I-03: ADR-0002 ("Regra do Superset") contradiz Régua §0/ADR-007 canônico. Claude-master rejeitou
  com argumento técnico em `claude_to_gemini_20260605.md`.
  — Base: SP-A explorer lendo fontes no repo Gemini. O ADR-007 do canônico é verificável aqui;
  a existência e texto do ADR-0002 depende do repo Gemini.

- I-04: Nenhum hook dispara automaticamente no Antigravity IDE. `.claude/settings.json` com wiring
  ausente. `test_effect_gate` confirma que `rm -rf /` e `push --force main` passam como `allow`.
  — Base: auditoria anterior (parecer 2026-06-09) + SP-B explorer lendo repo Gemini.
  O canário `test_effect_gate` está no repo Gemini — resultado não verificável diretamente aqui.

- I-05: 34 das 48 capacidades Gemini (71%) têm `enforcement: MISSING` no `capabilities.json`
  do Gemini.
  — Base: auditoria anterior (parecer 2026-06-09). Verificável lendo `metacognition-gemini/capabilities.json`.

- I-06: Propostas E1–E7 do relatório 005 documentadas mas **nenhuma mergeada** em `.agent/skills/`.
  — Base: SP-A explorer verificou arquivos de destino no repo Gemini.

- I-07: `session_orchestrator.py` existe no Gemini como mecanismo real mais próximo de separação
  de QA: gera prompt de handoff, copia para clipboard, instrui abrir nova sessão. **Não verifica**
  se o modelo correto foi usado.
  — Base: SP-E explorer lendo arquivo no repo Gemini.

- I-08: SQUAD_GEMINI.md contém regra escrita: "QA não pode ser ativado na mesma sessão ou pelo
  mesmo modelo."
  — Base: SP-A explorer lendo arquivo no repo Gemini.

- I-09: Escopo correto para o ADR-076 seria limitado a **trocas cross-IA** (não intra-junção),
  reconciliando com ADR-011 canônico sem revogar completamente.
  — Base: relatório 004 + I-02 + C-10 (ADR-011 canônico é verificável aqui).

- I-10: Wirear as 19 ferramentas Python (C-01) como passos explícitos no `start-session.md` do
  Gemini eliminaria a dependência de hooks. O padrão non-admin (ADR-047) demonstra viabilidade.
  — Base: C-01 + C-02 + `guia/MODO-NON-ADMIN.md` (verificável neste repo) + comportamento do
  Gemini no boot (inferência sobre o ambiente Antigravity IDE — não testado).

- I-11: `rule 02-cross-ai-sync.md` do Gemini manda varrer `reports-improve-cross-ai/` ao boot,
  mas esse path foi declarado "erro arquitetural" no relatório 005 — regra e path em conflito
  sem ADR de reconciliação.
  — Base: SP-A explorer lendo regras do Gemini.

---

### DESCONHECIDO (lacuna explícita)

- D-01: CLI Gemini como subprocess — não verificado se disponível no ambiente do dono.
  Afeta viabilidade da Alternativa 3 (subprocesso) para separação multi-LLM.
  · Validação: `which gemini-cli` ou equivalente no ambiente do dono.

- D-02: Estado de implementação real da Fase 4 do ADR-075 — ADR está "Aceito" mas não confirmado
  se o script Python de clonagem/sanitização (`import_framework_core.py` ou similar) existe.
  · Validação: `ls metacognition-gemini/tools/import_framework_core.py`

- D-03: Se `check_sycophancy.py` existe no repo Gemini (`tools/`). A regra 05-anti-sycophancy.md
  o cita, mas SP-B não confirmou existência em disco.
  · Validação: `ls metacognition-gemini/tools/check_sycophancy.py`
  · Impacto: se ausente, a capacidade `sycophancy-canary` do Gemini é prosa-only.

- D-04: Impacto quantitativo da ausência de heterogeneidade de modelo no Gemini — sem baseline
  de false-PASS documentados.
  · Validação: revisar execution reports em `metacognition-gemini/docs/_private/`.

- D-05: Escopo atual do `check_core_agnostic.py` no **repo Gemini** — verificar se a denylist
  já inclui `GEMINI_Metcognition.txt` ou está restrita aos mesmos paths do canônico.
  · Validação: `python metacognition-gemini/tools/check_core_agnostic.py --sensitive`

- D-06: CWD bias (Current Working Directory bias) — reportado no "Incidente 2" como mecanismo
  pelo qual o agente despeja arquivos no diretório ativo em vez do `DOMAIN_PATH` correto.
  Não encontrado como achado catalogado nos relatórios lidos pelos explorers (SP-A/B/C/D).
  · Validação: verificar se `DOMAIN_PATH` ou equivalente existe como variável/regra em algum arquivo
  do Gemini (ex: `pmo/SKILL.md`, `start-session.md`).

---

## 4.5 Enumeração dos padrões de falha FA (sessão FEFO/FIFO — relatório 005)

> Adicionado após QA (ALTO-01). Referência para §7 A-05 e §9.

| ID | Padrão | Causa estrutural | Solução mapeada |
|---|---|---|---|
| FA-01 | Falso-PASS — aprovação sem validação contra spec completa | Sem posture-gate / qa-evidence | C-08 (posture-gate portável) |
| FA-02 | Viés de Oráculo — fonte terceira aceita como absoluta | Sem ADR-018 adversarial real | C-10 (protocolo ADR-018) |
| FA-03 | Miopia de Escopo — analisa trecho sem estado global | Prosa-only sem gate de escopo | E2 / C-09 (read-before-elicit) |
| FA-04 | Elicitação Prematura — pergunta ao humano o que o código responderia | FA-07 + monolith single-model | E2 + passo 5 §9 |
| FA-05 | Parada Inter-Papel — para entre Developer e QA aguardando instrução | Sem wiring automático de junção | E1 / passo 5 §9 (auto-transição) |
| FA-06 | Sem checkpoint / artefatos fora do workspace | Sem compaction-gate ativo | E3 / C-01 (check_reorchestration) |
| FA-07 | Developer e QA no mesmo modelo/sessão | Sem isolamento multi-LLM (ADR-018) | I-07 + C-10 + passo 5 §9 |
| FA-08 | Identidade inconsistente — frontmatter vs corpo | Dual authority prompt (I-01) | GAP-1 / passo 1 §9 |

---

## 5. Gaps críticos (bloqueiam decisão de spec)

- **GAP-1 — Autoridade de prompt não resolvida:** Enquanto GEMINI_Metcognition.txt v3.1 (I-01) for
  o documento ativo, qualquer instrução em GEMINI-FRAMEWORK.md pode ser ignorada silenciosamente.
  Nenhuma das soluções técnicas abaixo funciona se o agente opera com o documento errado.
  · Plano: HITL → dono responde Q1/Q2/Q5 antes de qualquer outra intervenção.

- **GAP-2 — ADR-076 e ADR-0002 contraditórios:** Dois ADRs "Aceitos" no Gemini contradizem o
  canônico (I-02, I-03). Qualquer sincronização parcial de mecanismos sem resolver esses ADRs
  cria ambiguidade de regra no agente receptor.
  · Plano: EMENDA in-place do ADR-076 (escopo → cross-IA only, não intra-junção) + revogação do
  ADR-0002 com campo "Substituído por: ADR-007 Régua §0" — antes de merge de mecanismos novos.

- **GAP-3 — rule 02-cross-ai-sync.md aponta para path obsoleto:** Boot do Gemini segue regra que
  conflita com design declarado no relatório 005 (I-11).
  · Plano: atualizar `02-cross-ai-sync.md` para hub neutro (ADR-069 path canônico) — cirúrgico.

- **GAP-4 — Ausência de verificação de identidade de modelo em QA:** `session_orchestrator.py`
  (I-07) aceita handoff sem confirmar se o receptor é modelo diferente do dev. Qualquer spec de
  separação multi-LLM construída sobre essa lacuna é falha de design por omissão.
  · Plano: adicionar header de declaração de modelo na nova sessão QA; instrução explícita no
  protocolo ADR-018 integrado (passo 5 §9). Incluir como Q6 no backlog de elicitação.

> **Nota sobre D-03 (condicional):** se D-03 confirmar ausência de `check_sycophancy.py` no
> Gemini, o mecanismo C-08 (7/8 portáveis → 6/8) precisará ser revisado antes de §9 passo 4.

---

## 6. Ataque anti-raso (obrigatório — R3 do intake)

| Pergunta adversarial | Resposta / Mitigação |
|---|---|
| **Há lacuna não declarada?** | Sim — D-06 (CWD bias como mecanismo) foi detectado pelo QA e adicionado. |
| **Viés de confirmação?** | Risco real e declarado: relatórios são auto-produzidos pelo Gemini/dono. Mitigação aplicada: achados derivados exclusivamente de fontes do repo Gemini reclassificados para INFERIDO (ALTO-11 corrigido). Os CONFIRMADO (C-01 a C-12) baseiam-se em leituras diretas do canônico. |
| **Fonte fraca?** | `canaries_output.txt` (stale) descartado — SP-B confirmou arquivo desatualizado. |
| **Alternativa rejeitada sem registro?** | "Reescrever GEMINI_Metcognition.txt in-place" (sem substituir pelo canônico via ADR-075 Fase 4) é opção menos disruptiva não avaliada. Registrado em §7 A-02. |
| **ADR-075 Fase 4 realmente viável?** | DESCONHECIDO (D-02) — script de importação pode não existir. Verificar D-02 antes de assumir como solução disponível. |
| **As 19 ferramentas Python realmente sem deps?** | SP-B confirmou "stdlib-only" para a maioria; `doc_intake.py` tem libs opcionais (pdf/docx). Para uso básico, stdlib basta — declarado em C-01. |
| **Protocolo ADR-018 entrega ~80% sem modelo heterogêneo?** | INFERIDO — estimativa vem do ADR-018 canônico (referência "Zhang 2025/Heter-MAD"). Não medido no contexto Gemini (D-04). |
| **Conflito de precedência se instalarmos regras canônicas com ADR-076/0002 ativos?** | Sim — conflito direto confirmado (I-02, I-03). Resolver GAP-2 é pré-condição para qualquer wiring (A-01 + §9 sequência). |

---

## 7. Antecipações

- **A-01 — Ordem das intervenções importa mais que o conteúdo delas:** Instalar mecanismos
  canônicos antes de resolver GAP-1 (autoridade de prompt) e GAP-2 (ADRs contraditórios) cria
  sistema com regras conflitantes que o agente deve escolher silenciosamente. A ordem correta
  está em §9.

- **A-02 — Alternativa menos disruptiva: reescrever GEMINI_Metcognition.txt in-place:**
  Em vez de substituir o arquivo (ADR-075 Fase 4), o conteúdo de domínio pode ser extraído para
  `exemplos/<gemini-contexto>/` seguindo o padrão C-06. O arquivo-raiz ficaria agnóstico sem ser
  removido. Custo: menor impacto operacional. Risco: versionamento paralelo (v3.1) permanece.
  O dono decide (Q1, Q5).

- **A-03 — ADR-076 tem valor legítimo para contexto cross-IA:** O relatório 004 levantou razões
  reais para um teto de rounds cross-IA (loops de alucinação, custo acumulado de contexto de erro,
  janela de intervenção humana). I-09 propõe reescopo para cross-IA only como solução de preservação
  do valor legítimo sem conflitar com ADR-011 canônico.

- **A-04 — `session_orchestrator.py` está subaproveitado:** Já existe e funciona (I-07). O ganho
  de implementar o protocolo ADR-018 **dentro** do session_orchestrator.py (em vez de criar skill
  paralela) é maior e menos disruptivo. Passo 5 de §9 reflete isso.

- **A-05 — Sicofância operacional não é resolvível por mecanismo sozinho:** 8 mecanismos (C-08)
  existem e cobrem sicofância estrutural. Mas P11 honesto do canônico admite: "agente não
  auto-detecta sem gate humano." Para os FA específicos (especialmente FA-01 Falso-PASS e FA-02
  Viés de Oráculo), gate adversarial com **humano no loop** é necessário **em adição** aos
  mecanismos — não como substituto. Q6 no backlog endereça quando e como ativar esse HITL.

### 7.1 Gaps não-bloqueantes

| Gap | Impacto se não tratado | Decisão registrada |
|---|---|---|
| D-01 (CLI Gemini) | Alternativa 3 multi-LLM indisponível | manter gap — outras alternativas suficientes |
| D-04 (métricas false-PASS) | Impossível medir melhoria quantitativa pós-intervenção | tratar follow-up — baseline após passo 5 implementado |
| D-05 (escopo linter no Gemini) | Risco de varredura parcial do GEMINI_Metcognition.txt | tratar follow-up — verificar antes do passo 7 |
| D-06 (CWD bias mecanismo) | Sem gate de DOMAIN_PATH, Incidente 2 pode se repetir | tratar follow-up — investigar `pmo/SKILL.md` e `start-session.md` do Gemini |

---

## 8. Backlog de elicitação

| # | Pergunta | Por que importa | Forma da resposta |
|---|---|---|---|
| Q1 | GEMINI_Metcognition.txt v3.1 está sendo usado ativamente em sessões de domínio hoje? | Define se a Fase 4 do ADR-075 quebra fluxos ativos do dono | Sim/Não + quais projetos |
| Q2 | Qual é a decisão do dono sobre ADR-076? Revogar, reescopar para cross-IA, ou manter? | ADR-076 em conflito direto com canônico bloqueia sync parcial | Escolha + justificativa |
| Q3 | O `cross-ai-hub-local` está disponível nesta máquina? Qual o path? | Afeta proposta de hub neutro para reports cross-IA | Path ou "não disponível" |
| Q4 | O repo premium (ou public) do framework está acessível localmente para o Gemini como oráculo de leitura? | A proposta de oráculo canônico vivo requer acesso de leitura | Path local ou URL |
| Q5 | Há automações dependentes do GEMINI_Metcognition.txt como "regra residente" no Antigravity IDE? | Se sim, mudança de prompt autoritativo requer migração dessas automações | Lista de automações ou "nenhuma" |
| Q6 | Em quais situações o dono quer ativar gate adversarial HITL para FA específicos (FA-01, FA-02)? | A-05: sicofância operacional exige HITL em FA de alto risco | Lista de situações ou threshold |

---

## 9. Recomendação ao orquestrador

**Enviar ao `architect`** — os achados são suficientes para decisão arquitetural.

**Pré-condição para o architect:** responder Q1, Q2 e Q5 do §8 antes de qualquer decisão sobre
a Fase 4 do ADR-075 e ADR-076. São as perguntas que mudam o espaço de soluções.

**Sequência obrigatória de intervenções** (baseada em A-01 e GAP-1/GAP-2):

| # | Intervenção | Critério §0 (ADR-007) | Incidente coberto | Pré-condição |
|---|---|---|---|---|
| 1 | **Resolver autoridade de prompt (GAP-1):** HITL → dono decide entre substituir (ADR-075 Fase 4) ou reescrever in-place (A-02). Confirmar Q1/Q5 antes. | (c) destrava: sem prompt correto, nenhum mecanismo abaixo funciona | Incidente 2 (raiz) | Q1, Q5 |
| 2 | **Reconciliar ADR-076** via EMENDA in-place (STATUS-field, escopo → cross-IA only) + revogar ADR-0002 com "Substituído por: ADR-007". | (c) destrava: ADR contraditórios bloqueiam sync | — | Q2 |
| 3 | **Atualizar `rule 02-cross-ai-sync.md`** para apontar para hub neutro (ADR-069). | (a) remove path obsoleto, não adiciona | — | Nenhuma |
| 4 | **Wirear 19 ferramentas Python (C-01) no start-session do Gemini** como passos explícitos. Remove: chamada explícita manual de verificação a cada sessão (hoje inexistente/esquecida). | (c) destrava verificação automatizada que hoje é ausente | — | Passos 1–3 |
| 5 | **Integrar protocolo ADR-018 dentro do `session_orchestrator.py` existente** (não criar skill paralela — A-04). Adicionar: header obrigatório de declaração de modelo na nova sessão QA (GAP-4). | (a) melhora mecanismo existente sem novo arquivo; (c) destrava: FA-07 não bloqueado sem isso | Incidente 1 (monolith QA) + FA-04, FA-05, FA-07 | Passo 1 |
| 6 | **Criar `effect_gate.py` (~50 linhas)** que leia `effect-rules.json` e emita allow/ask/deny. Port Python de `consistency-gate`. | (c) destrava: `rm -rf /` passa como allow hoje (I-04) | — | Passo 4 |
| 7 | **Expandir escopo do `check_core_agnostic.py`** para incluir GEMINI_Metcognition.txt na varredura. Executar após D-05 verificado. | (a) adiciona escopo sem duplicar lógica | Incidente 2 (preventivo) | Passo 1 + D-05 verificado |
| 8 | **Adicionar verificação de identidade de modelo** no protocolo de abertura de sessão QA (GAP-4). | (c) destrava: separação multi-LLM hoje é declarativa sem verificação | Incidente 1 + GAP-4 | Passo 5 |
| 9 | **Gate preventivo cross-domain permanente:** após Fase 4 ADR-075 (Passo 1), nenhum arquivo de prompt-raiz do Gemini pode conter normas de domínio hardcoded. Verificado por `check_core_agnostic.py` (Passo 7) + canário CI. | (c) destrava: Incidente 2 pode se repetir sem gate preventivo | Incidente 2 (futuro) | Passo 7 |

---

## 10. Metadados

- **Rodadas executadas:** 1 (gaps restantes não bloqueiam decisão arquitetural)
- **Falhas do explorer:** Nenhuma. 4 de 4 explorers retornaram achados estruturados.
- **Sub-perguntas cobertas:** SP-A, SP-B, SP-C, SP-D, SP-E (5/5)
- **Achados totais:** 12 CONFIRMADO · 11 INFERIDO · 6 DESCONHECIDO
- **QA adversarial:** Rodada 1 → REPROVADO (8 ALTOs). Rodada 2 → APROVADO_COM_RESSALVAS.
- **Correções aplicadas:** 8 ALTOs + 6 MÉDIOs + 2 BAIXOs (todos incorporados)
- **Tempo de elaboração:** 2026-06-09 (sessão única)
- **Próximo papel:** architect (com Q1/Q2/Q5 do §8 como pré-condição)
- **Localização:** `docs/specs/gemini-architecture-solutions/research-brief.md`
