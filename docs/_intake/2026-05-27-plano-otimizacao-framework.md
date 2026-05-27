# PLANO DE OTIMIZAÇÃO DO FRAMEWORK — Briefing único para o Claude Code

> **Origem:** colado pelo mantenedor em 2026-05-27 (durante sessão "retome adr005").
> Arquivo é **intake** versionado para audit trail (anti-rename, decisão→fonte→versão).
> Processamento: framework integral (re-auditoria → architect → qa-critic rounds até
> APROVADO LIMPO → developer → docops → PR+merge). Modo `autosuficiente` ativo.

---

## 0. A régua que rege tudo: GANHO LÍQUIDO (subtração primeiro)

Toda mudança deve ser otimização líquida. **Adição pura é rejeitada por padrão.**
Antes de criar arquivo/skill/regra/workflow, pergunte: *"o que dá para remover,
fundir ou simplificar para o mesmo resultado?"*. Aceite só se:
(a) funde/remove superfície ≥ à que adiciona; OU
(b) reduz token/latência comprovadamente; OU
(c) gera ganho de assertividade (eval passando) inalcançável editando um artefato existente.
**Nunca** adicione custo fixo ao caminho pontual/startup sem que ele se pague.

> Esta régua entra como **1 linha** no §6 do `AGENT-FRAMEWORK.md` (sem arquivo novo) —
> e passa no próprio teste: funde-se num artefato existente e previne inflação futura.

---

## 1. Erros e aprendizados a EVITAR (ler antes de tocar em qualquer coisa)

Estes são bugs reais que o próprio plano original cometia. Não repetir:

1. **Branches paralelas no mesmo arquivo = conflito + anti-padrão.** Não rodar G1/G9/G11
   em três branches ao mesmo tempo tocando `CHANGELOG`/`README`/`AGENT-FRAMEWORK`/
   `eval-results`/`start-session`/`qa-critic`. **Uma branch por vez.** Escrita é monólito.
2. **Não acoplar maquinário pesado ao startup/caminho pontual.** Triagem/retro custam
   token a cada sessão. Só em modo squad, opt-in. Tarefa pontual → resposta direta.
3. **Não acumular eval `[DESIGN-TIME, NÃO EXECUTADO]`.** Já há G/H sem rodar. **Pagar a
   dívida de eval antes** de adicionar gap novo — é a política do próprio framework.
4. **Não adicionar superfície líquida.** Reusar artefato existente (history.md, checkpoint,
   ADR, CHANGELOG) antes de criar pasta/workflow/template novos.
5. **"Convergência Claude×Gemini" NÃO é validação independente forte.** As duas pesquisas
   saíram do mesmo prompt/escopo que eu escrevi — corroboração parcial, não prova.
6. **Não confiar em diagnóstico de snapshot.** Este plano nasceu de um zip de 26/05.
   **Re-auditar o repo vivo** (branches `v2.3-refactor`, `feat/discovery-v160-v161` etc.)
   antes de afirmar "ausente" ou "resolvido".
7. **Não criar store de aprendizado paralelo.** Subagentes paralelos escrevendo no mesmo
   arquivo = race condition. Manter **single-writer** (só o orquestrador, no checkpoint).
8. **Coerência:** não importar o princípio anti-estrutura-ad-hoc (Model Harness Fit)
   enquanto se adiciona estrutura ad-hoc. Se a régua §0 reprovar, não fazer.
9. **Anti-alucinação:** autoria do reel (Cod3r/"Leonardo Leitão") é `[INFERIDO]`, não
   `[CONFIRMADO]` — não endurecer sem verificar.

---

## 2. Resultados da pesquisa (condensado — detalhe em `docs/_intake/` se anexado)

**Convergência Claude + Gemini (núcleo de alta confiança, com a ressalva do erro #5):**
pipeline de 5 fases — **A** descoberta (pesquisa em cascata/STORM, multi-hop, perguntas
adversariais) → **B** especificação SDD em EARS sob uma "constituição" imutável → **C**
escrita **monólito single-thread** → **D** crítica adversarial em **contexto limpo** →
**E** rastreabilidade (eval + observabilidade OTel + audit trail). SDD = Spec Kit / Kiro
(EARS) / Tessl. **Multiagente só para leitura/exploração** (risco de divergência = 0);
**monólito para escrita** (coerência de decisões implícitas). Skills + **progressive
disclosure**. Regulado: GAMP 5 / CSA / Annex 22 / ALCOA+ / OTel / HITL. Memória =
documentação Markdown **append-only** (não vector DB para rastros efêmeros).

**Adições reais que o Gemini trouxe** (e o destino de cada uma após a régua §0):
Git Working Tree → adiar p/ G2 · STORM/adversarial → dobrar no G1 (2 linhas) · Context
Quarantine → **já coberto** por `subagent-isolation`/`qa-critic` · Scorer-Critic-Commander
→ **cortado** (inflação; qa-critic já cobre) · Memory Flush + locking → **simplificado**
(single-writer elimina o problema) · Model Harness Fit → adiar (1 linha de guardrail) ·
Golden Datasets/OOS → adiar p/ bloco regulado.

**Ressalvas honestas (evidência ≠ marketing):** o ganho "+90,2%" do multiagente vem com
**15× o custo em tokens** e é eval interna não-replicável; **Annex 22 está em draft**; a
prosa do Gemini é mais retórica mas não traz evidência nova além dos itens acima.

---

## 3. Análise de gaps (corrigida)

**Já resolvido — PRESERVAR, não tocar:** SSoT via `_shared/` (a duplicação histórica já
foi eliminada) · context engineering §2.5 · isolamento de subagente (`_meta/subagent-isolation`)
· roteamento por confiança (`rules/04`) · spec atômica + gate binário (`docs/specs/_template`)
· high-stakes-gate genérico · observabilidade OTel · progressive disclosure (ADR-003).

**Gap real que vale agir AGORA:** **G1 — descoberta em cascata antes da spec.** Ausente,
pedido explicitamente, e barato (companion carregado sob demanda = custo zero no startup).

**Necessidades reais, mas atendidas por EXTENSÃO (não por subsistema novo):**
- *Aprendizado/memória de fracassos (ex-G9):* reusar `/checkpoint` + `history.md` + ADR.
- *Nada parado/pausado/planejado esquecido (ex-G11):* reusar `start-session` + `history.md`.

**Adiar até necessidade comprovada + eval pago:** G2 (orquestração multi-spec + worktree),
G3 (gate analyze), G4 (EARS obrigatório), G5/G7 (regulado: Golden Datasets/OOS/freeze),
G6 (`--quick`), G10 (Harness Fit), e as revisões R2/R4/R5.
**Descartado:** G8 (memória auto-evolutiva — propaga erro) e R4 (Scorer-Critic-Commander).

---

## 4. Proposta final (enxuta e serializada)

**Adicionar (única adição estrutural):** a régua §0 — 1 linha no §6 do `AGENT-FRAMEWORK.md`.

**G1 mínimo (o trabalho desta rodada):**
- `.agent/skills/discovery/pesquisa-cascata.md` — companion (sob demanda). Método:
  decompor → buscar (via `explorer`) → refletir → ramificar → sintetizar `research-brief.md`.
  **R3 dobrado em 2 linhas:** nomear o método STORM + 1 passo de pergunta adversarial
  (persona read-only ataca os achados antes de fechar).
- `docs/specs/_template-research/research-brief.md` — template do artefato de saída.
- `docs/adr/005-discovery-pesquisa-cascata.md` — ADR (Status Proposto).
- Edições cirúrgicas: +1 linha na tabela de sub-modos do `discovery/SKILL.md` (version
  1.6.0→1.7.0); +subseção curta no `AGENT-FRAMEWORK.md` §2.B; +item no `README.md`; +entrada
  no `CHANGELOG.md`.
- Eval seção I escrita; **rodar antes de considerar pronto** (não deixar design-time).

**Aprendizado (ex-G9) — por extensão, sem pasta/workflow/template novos:**
- `/checkpoint`: +1 linha — *se um gatilho de fracasso disparou (anti-loop, qa-critic
  reprovou ≥2×, file-first violado, estouro de token, [CONFIRMADO] que se revelou falso),
  anotar em `history.md` sob `## Aprendizado`.* Single-writer (orquestrador), append-only.
- Checklist de release (`guia/GIT-VERSIONAMENTO.md`): +1 linha — *antes do release, revisar
  `## Aprendizado` do history.md; padrão recorrente (≥3) → propor ADR.* (É o "retro", humano-gated.)
- Firewall (princípio curto): notas de aprendizado são **inertes** — só viram comportamento
  via skill/regra destilada, aprovada e mergeada. Nota errada não propaga.

**WIP / nada esquecido (ex-G11) — por extensão:**
- `history.md`: seção `## Em aberto` (planejado/pausado/bloqueado/em-revisão, com próximo passo).
- `start-session`: o STATUS passa a reconciliar `## Em aberto` + branches do git + ADRs
  `Proposto`. Só em modo squad.
- Regra de WIP-limit (1 linha, no §6 junto da régua): **finalizar antes de iniciar**; item
  só muda de status com razão registrada.

**Delta de superfície:** de ~{3 workflows + 2 pastas + 3 ADRs + templates + 4 evals} para
~{1 companion + 1 template + 1 ADR + ~6 edições de 1–3 linhas + 2 linhas de princípio}.
Mesmo resultado, fração da superfície, zero custo fixo novo no caminho rápido.

---

## 5. Como implantar SEM piorar o framework (protocolo)

1. **Re-auditar o repo vivo** (papel `explorer`, read-only): confirmar o que está
   "resolvido" (§3) e que o G1 segue ausente. Onde divergir do snapshot, **vale o repo**.
2. **Pagar a dívida de eval** pendente (G/H, depois I) antes de declarar qualquer bloco pronto.
3. **Aplicar a régua §0 a cada mudança** antes de fazê-la. Reprovou → não faz.
4. **Uma branch por vez.** Aplicar a régua §0 + G1; rodar `qa-critic`; **gate humano**;
   **medir** tokens/assertividade contra o estado anterior.
5. Só com ganho medido, aplicar as extensões de aprendizado e WIP (são 1–3 linhas cada).
6. **Só então** reavaliar se G2 e os demais ainda valem — com dado real, não com proposta.
7. Toda decisão: `decisão → fonte → versão` no CHANGELOG. Anti-rename só via ADR.

---

## 6. Estado e pendências honestas (não esconder)

- Diagnóstico baseado no **snapshot de 26/05** — re-auditar (item 5 da §1, passo 1 da §5).
- **Evals G/H/I são design-time, não executados** — pagar antes de produção.
- Hook `SessionEnd` (se um dia for usado para commit de aprendizado) tem o **nome do
  evento `[INFERIDO]`** — confirmar na doc do Claude Code; por ora, captura é manual no checkpoint.
- ADR-005 está **Proposto** — vira Aceito só após o gate humano.
- Autoria do reel: `[INFERIDO]`.

---

## 7. Primeira ação

`/start-session` → re-auditar (explorer) → confirmar §3 contra o repo vivo → na branch
`feat/discovery-pesquisa-cascata-v170`: aplicar a régua §0 (1 linha) + o **G1 mínimo** →
rodar o eval I + `qa-critic` → **parar no gate humano** e reportar a medição (tokens/
assertividade antes×depois). Não abrir nenhum outro gap até esse dado existir.

---

## NOTAS DO RECEBIMENTO (adicionadas no intake, NÃO alteram o documento original)

- **Recebido em:** 2026-05-27, sessão "retome adr005 → avançar adr006"
- **Estado do repo na hora do recebimento:** v1.7.1 mergeada (PR #7); modo `autosuficiente` ativo; branches limpas; ADR-006 (auto-boot global) em status `Proposto (revisto pós-v1.7.1)` mas untracked
- **Conflitos de numeração:** doc propõe `005-discovery-pesquisa-cascata.md`, mas ADR-005 já é "Modos de execução" (Aceito em main). Próximo número livre = **ADR-007**. ADR-006 = auto-boot global (Proposto, untracked).
- **Avaliação pendente sob régua §0:** o ADR-006 atual (auto-boot global + allowlist) precisa passar pela régua §0. Pré-análise: provavelmente não passa por adicionar custo fixo a TODA sessão. Decisão a ser registrada via architect.
- **Re-auditoria do §3 ("já resolvido"):** confirmar via explorer antes de prosseguir.
