# ADR 012 — Handoff cross-sessão como entregável obrigatório quando declarado + RCA gate + cobertura temporal pós-J4

- **Status:** Aceito (2026-05-29) — qa-critic round 1 endereçado em commit `2efbf92` (1 ALTO listas inline CLAUDE/AGENTS + 2 MEDIO reorder GUIA + ADR-012 §Mudanças incompleto + 1 BAIXO mindset fechamento + 1 BAIXO metadados aceito como convenção). Decisão anti-loop: 1 round + fix em pass único (diretiva "lean e realista" do dono).
- **Data:** 2026-05-29 · **Decisores:** Fabricio (mantenedor) + Claude (papel `architect`)
- **Substitui:** nenhum · **Substituído por:** nenhum
- **Relaciona-se a:** ADR-007 (régua §0), ADR-010 (discovery declara escopo passo 6), ADR-011 (junções binárias + process-critic)
- **Fonte:** sessão paralela 2026-05-29 (repo `test-aivi-isolated`) — dogfood real do v1.12.x em caso regulado real; relatório `RELATORIO-VALIDACAO-FRAMEWORK.md` §4.1/§4.2/§11.3 identificou 9 gaps de processo, dos quais 3 são tratados aqui (Gaps 4, 5, 8); os outros 6 ficam como method-audit aguardando 2ª ocorrência confirmatória.

## Contexto

Sessão paralela executou cálculo regulatório real (domínio combustíveis) usando metacognition-framework v1.12.1. Resultado: gate binário PASS após rework v2.0; mas o processo revelou **3 padrões de falha metodológicos agnósticos de domínio** que o framework v1.12.x NÃO previne:

1. **Detecção-sem-ação (Gap 4):** agente DETECTOU divergência entre fontes, CLASSIFICOU ("provavelmente erro de uma das fontes"), e RESOLVEU por default ("escolher a fonte X como autoritativa") **sem investigar causa-raiz**. O defeito mais grave da sessão (não foi falha de detecção — foi falha de julgamento). Resolver anomalia por default sem RCA citada = violação de processo sênior.

2. **Cobertura temporal QA pós-J4 (Gap 5):** process-critic adversarial rodou sobre arquivo A; arquivo B foi criado **depois** (extensão da entrega) **dentro do mesmo bloco**, mas **nunca submetido a QA adversarial**. Princípio 13 + rule #4 SE/ENTÃO cobrem polish post-release e classificação bloco-novo; **não cobrem** artefato novo intra-bloco pós-J4. Gap real identificado pelo process-critic round 1 desta ADR.

3. **Handoff cross-sessão improviso (Gap 8):** quando a entrega alimenta outra sessão/agente (relatório de análise, pipeline downstream), o pacote de transferência foi improvisado em vez de produzido com estrutura mínima auditável. Sintoma: a próxima sessão precisaria perguntar de volta para começar.

Sessão paralela aplicou edições globais (`~/.claude/skills/`) para (3): `metacognition-core` v1.1.0 §Pacote de handoff + `discovery` passo 6(e). Framework repo (`metacognition-framework/main`) **NÃO foi sincronizado** → drift global ↔ repo. Este ADR ratifica + sincroniza + adiciona Gaps 4 e 5.

**Outros 6 gaps (1, 2, 3, 6, 7, 9) ficam como method-audit notes** aguardando 2ª ocorrência (princípio 11 honesto: agente codifica regra após padrão confirmado, não preemptivamente).

## Decisão (1 frase ativa)

Introduzir **princípio 14 (handoff cross-sessão obrigatório quando declarado)** + sincronizar drift global ↔ framework repo de `discovery` passo 6(e) e `metacognition-core` §Pacote de handoff + adicionar **rules #6 (RCA gate) e #7 (cobertura temporal pós-J4) em qa-critic SKILL** como SE/ENTÃO determinísticos derivados de method-audit confirmado.

## Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **Escopo enxuto: Gaps 4 + 5 + 8 + sync drift (escolhida)** | Resolve 3 padrões com evidência empírica forte (case real); drift sync fecha débito v1.12.x; régua §0: 3 EDITs + 1 ADR + 1 princípio. | Outros 6 gaps ficam abertos como method-audit (não esquecidos; não preemptivos). |
| 2 | Absorver todos os 9 gaps em v1.13.0 | Lições reais absorvidas completas. | Replica padrão v1.10/11/12 (3-4 rounds qa-critic, ~80 turnos). Princípio 11 honesto: codificar 6 gaps com 1 caso = preemptivo, violou disciplina pre-commit. |
| 3 | EMENDA ADR-010 ou ADR-011 (não ADR-012 standalone) | Reduz número total de ADRs. | ADR-010 já tem 4 sub-princípios; ADR-011 trata pipeline interno. Handoff cross-sessão é eixo separado (entre sessões). Process-critic round 1 explicitamente recomendou ADR-012 standalone para auditabilidade. |
| 4 | Princípio 14 não — só EDIT de skills | Mais lean. | Handoff cross-sessão é eixo arquitetural novo (entre sessões, não dentro). Sem princípio em §6, fica enterrado em skill. ADR-010/011 ambos têm princípios — paridade. |
| 5 | Não fazer (status quo) | Zero esforço. | Drift global ↔ repo permanece; padrões reais identificados não absorvidos; v1.14.0 reabre tudo. |

## Justificativa

Escolha pela **Alternativa 1** por 4 razões:

- **Princípio 11 honesto (ADR-010 §C-1):** padrões com 1 ocorrência só não justificam codificação preemptiva. Gaps 4, 5, 8 são exceção porque tiveram evidência empírica robusta (post-mortem detalhado + process-critic confirmou estrutura). Gaps 1, 2, 3, 6, 7, 9 ficam method-audit aguardando 2ª ocorrência.
- **Régua §0 (ADR-007):** 1 ADR novo + 1 princípio novo + 3 EDITs cirúrgicos + drift sync. Critério (c): destrava decisão arquitetural sobre handoff cross-sessão que não cabia em ADR-010 nem ADR-011 sem sobrecarga.
- **Process-critic round 1 incorporado:** primeira tentativa rejeitava Gap 5 como "já coberto"; process-critic adversarial detectou que rule #4 v1.12.1 cobre polish post-release, não artefato novo intra-bloco pós-J4. Rule #7 nova é correção empírica.
- **Coerência com princípios existentes:** princípio 13 (pipeline interno PMO→docops); princípio 14 (transição entre sessões). Eixos distintos, ambos formalizados.

## Mudanças por arquivo

| Arquivo | Mudança | Tipo |
|---|---|---|
| `docs/adr/012-handoff-cross-sessao.md` | **NOVO** (este arquivo) | Adição — critério (c) régua §0 |
| `_shared/metacognition-core/SKILL.md` | v1.0.0 → v1.1.0 + §Pacote de handoff cross-sessão (sync com global aplicado em 2026-05-29) | Drift sync + adição condicional |
| `.agent/skills/discovery/SKILL.md` | Passo 6 ganha item **(e)** "Alimenta outra sessão/agente?" (sync com global) | Drift sync + 4→5 perguntas |
| `.agent/skills/qa-critic/SKILL.md` | **+rule #6** SE/ENTÃO (RCA gate) + **+rule #7** SE/ENTÃO (cobertura temporal pós-J4) | Adição cirúrgica — critério (c) destrava |
| `AGENT-FRAMEWORK.md` §6 | **+princípio 14** (handoff cross-sessão obrigatório quando declarado) | Adição mínima (1 linha) |
| `CHANGELOG.md` | **+bloco [1.13.0]** | Convenção |
| `CLAUDE.md` + `AGENTS.md` + `README.md` + `guia/GUIA-EQUIPE.md` + `guia/web/index.html` | Seções/cards v1.13.0 | Convenção |
| `history.md` | Close v1.13.0 + method-audit notes (6 gaps remanescentes + isolation/model observação do dono) | Convenção |
| `docs/specs/v1.13.0-aivi-method-fixes/validation.md` | **NOVO** — gate binário V1-Vn release | Adição — gate per release |
| `.agent/workflows/start-session.md` | Passo 2.5: ref ADR-012 atualizada (era "futuro"; agora link válido) | Edit cirúrgico (1 linha) |
| `docs/adr/010-framework-agnostico-discovery-declara-escopo.md` | **EMENDA in-place** §72 (Interview-mode 4 perguntas + nota) e §148 (Consequências negativas 4 perguntas + nota): "EMENDA v1.13.0: 4 → 5 com adição de (e) alimenta outra sessão?" — pattern SUPLANTA × EMENDA mantido | EMENDA conforme ADR-011 política |

**Total:** 2 novos + 10 edições. Mais drift sync (3 arquivos já alinhados ao global). Sem nova pasta/workflow/skill/papel.

## Consequências

### Positivas

1. **Drift global ↔ repo eliminado** — `~/.claude/skills/` e `metacognition-framework/main` em sync para `discovery` passo 6 e `metacognition-core` §Pacote.
2. **RCA gate codificado** — anomalia → root-cause antes de resolver vira REPROVADO automático no qa-critic.
3. **Cobertura temporal pós-J4** — artefato novo intra-bloco re-disparo cirúrgico mandatório.
4. **Handoff cross-sessão estruturado** — defaults agnósticos quando não declarado; obrigatório quando passo 6(e) afirmativo.
5. **Princípio 14 formaliza eixo entre sessões** — paridade com princípio 13 (eixo dentro de sessão).
6. **Princípio 11 honesto aplicado** — 6 gaps remanescentes ficam method-audit (não preemptivos); confirma disciplina anti-inflação.

### Negativas

1. **Princípio 14 = +1 princípio em §6** — viola alvo declarado "v1.13.0 = ≤1 princípio novo" (registrado em method-audit 19:00 hoje). Mitigação: trigger real (case AIVI) justifica; não foi preemptivo.
2. **Qa-critic SKILL ganha 2 rules (5 → 7)** — superfície cresce. Mitigação: rules são SE/ENTÃO determinísticas que **reduzem rounds futuros** (catch recorrente).
3. **6 gaps abertos como method-audit** — risco de "vazar para sempre". Mitigação: 2ª ocorrência confirmatória codifica; sem ocorrência = padrão não confirmado, descartar OK.

### Riscos

1. **Rule #6 (RCA gate) pode disparar em demais falsos positivos** — toda divergência detectada exige RCA. Mitigação: RCA aceita formato compacto ("causa-raiz: X; mecanismo: Y; ação: Z" em 1 parágrafo).
2. **Rule #7 (cobertura pós-J4) pode duplicar process-critic em polish trivial** — risco de over-QA. Mitigação: re-disparo é cirúrgico (sobre artefato novo, não bloco inteiro); rule #4 v1.12.1 continua para polish > 5 linhas.

## Method-audit notes — 6 gaps remanescentes (não codificados)

Registrados em `history.md ## Aprendizado` aguardando 2ª ocorrência confirmatória (princípio 11 honesto):

- **Gap 1 (ancoragem em rótulo):** propõe hierarquia explícita de fontes em metodo-senior passo 1A — aguarda 2º caso.
- **Gap 2 (inventário de fontes citadas):** propõe metodo-senior passo 1B bloqueante — aguarda 2º caso.
- **Gap 3 (regressão × correção):** propõe rule SE/ENTÃO em qa-critic — aguarda 2º caso.
- **Gap 6 (campo vazio rebaixa confiança):** propõe anti-pattern em anti-hallucination — aguarda 2º caso.
- **Gap 7 (inferir autoridade):** propõe anti-pattern em anti-hallucination — aguarda 2º caso.
- **Gap 9 (telemetria por papel):** parte é infra externa (harness); parte tratável (timestamp output qa-critic) — aguarda 2º caso para codificar campo obrigatório.

**Observação do dono (separada, 2026-05-29T22:30):** isolation/model selection per role — só qa-critic explicitamente isolado; outros papéis compartilham contexto+modelo = mesmo viés cognitivo. `_meta/subagent-isolation.md` documenta política mas modelo per role NÃO codificado. **Registrado como method-audit — candidato a v1.14.0 se 2ª ocorrência confirmar.**

## Referências

- ADR-007 (régua §0 + firewall workflow).
- ADR-010 (discovery declara escopo — passo 6 base que ganha item (e)).
- ADR-011 (princípio 13 — pipeline interno; complementado por princípio 14 — entre sessões).
- `_meta/subagent-isolation.md` (política existente de isolamento).
- Repo externo: `test-aivi-isolated` (case real validação) — `RELATORIO-VALIDACAO-FRAMEWORK.md` §4.1 + §4.2 + §11.3.
