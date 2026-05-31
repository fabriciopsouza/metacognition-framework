# Guia de Equipe — Uso Diário

> Material curto para capacitar a equipe. 5 minutos de leitura.

## 1. O modelo decide o modo sozinho
- Pergunta rápida / 1 fórmula / debug → **metacognição** (resposta direta validada).
- Projeto / >2 arquivos / >2 etapas / **regulado declarado pelo discovery** → **squad** (papéis + workflows).
- Você pode forçar: "use o squad" ou "responde direto".

> **v1.11.0 (ADR-010) + v1.13.0 (ADR-012):** "regulado" NÃO é mais inferido por palavras-chave — o **discovery pergunta ao dono** (5 perguntas: regulado? quais normas? · alto-risco? · regra com semântica? · gaps não-bloqueantes? · **alimenta outra sessão/agente?**). Sem declaração afirmativa → defaults agnósticos. Anti-vazamento cross-projeto.

## 2. As 4 regras que nunca caem (de `_shared/`)
1. **Classificar** toda afirmação relevante: CONFIRMADO / INFERIDO / DESCONHECIDO.
2. **Anti-rename** — não renomear campo aprovado sem ADR.
3. **File-first** — ler o arquivo / inspecionar colunas antes de assumir.
4. **NÃO SEI** dito na cara, sem inventar.

## 3. Começar um caso novo (o jeito reprodutível)
1. Preencher `docs/briefing.md` + `00-glossario.md`.
2. `/feature-plan <X>` → gera a spec (`requirements.md` + `validation.md`).
3. `/implement <X>` → Developer → QA-Critic (valida contra `validation.md`) → DocOps.
4. `/checkpoint` ao fim do bloco.

## 4. Frameworks de decisão (do A2)
| Se… | Então… |
|---|---|
| feature crítica, multi-arquivo, regulada | spec completa (SDD) |
| bug < 30 min, < 3 arquivos | direto, com testes |
| padrão repete em 3+ contextos | virar skill, não spec ad-hoc |
| subtarefa polui contexto / tools diferentes | isolar em subagente |
| decisão irreversível | manter no principal + confirmação humana |
| número vai a decisão executiva ou é regulado | roteamento reflexivo (QA + revisão humana) |

## 5. Comandos
`/start-session` (toda sessão) · `/feature-plan` · `/implement` · `/handoff <papel>` · `/checkpoint`
> Comandos específicos de domínio (ex.: `/sap-change`, `/bi-deliverable`) são adicionados
> pela sua aplicação — não vivem no núcleo. Crie em `<sua-aplicacao>/workflows/`.

## 6. Onde mudar uma regra
Regra transversal → edite **um** arquivo em `_shared/` (propaga p/ todas as aplicações).
Domínio específico (BI, regulado, contexto X) → a aplicação correspondente (criada
clonando `.agent/skills/_template`); vive FORA do núcleo. Ver `exemplos/README.md`.
Nunca duplique — se a regra existe em `_shared/`, referencie.

## 7. Sinais de que algo saiu do trilho
- Pediram "posso prosseguir?" 2× → deveria ter avançado com premissa.
- Campo renomeado sem ADR → reverter.
- Número entregue sem classificação ou sem rastreio à fonte → recusar.

## 8. Papéis emergentes são *hats*, não skills novas (pesquisa A2)
Em equipe pequena, a mesma pessoa veste o chapéu quando necessário — não cria arquivo:
- **skill-librarian** — cura, versiona e revisa as skills; evita "skill sprawl".
- **evals-engineer** — dono dos eval-sets (`_meta/eval-template`); skill nova só entra passando.
- **governance-lead** — políticas, auditoria, compliance; aciona `_shared/high-stakes-gate`.

## 9. Núcleo × aplicação (regra de ouro — ADR-010 v1.11.0)
O framework é **estritamente agnóstico**. Domínio (linguagens, ferramentas, normas regulatórias, padrões técnicos, regras de negócio com peso semântico — quaisquer) nasce **declarado pelo discovery do projeto** + clonando `.agent/skills/_template` → vai para uma aplicação. **Nunca coloque domínio no núcleo nem em prompts/guias distribuídos.** Anti-vazamento cross-projeto: agente não importa convenção/norma de outra sessão sem confirmação.

## 10. Junções binárias forward-only (regra de ouro — ADR-011 v1.12.0)
Fluxo squad tem **6 junções (J0-J5)** com gates binários declarados em `/handoff` + **process-critic adversarial final** (qa-critic em subagente isolado) com poder de **rewind cascata**. **DENTRO da junção:** iterações até PASS (binário). **ENTRE junções:** forward-only (uma vez passada, não volta sem ação do process-critic — circuit-breaker contra loop eterno). **TODO QA é adversarial** (hipótese default = bug). **Process-critic dispara em:** (a) final de cada BLOCO APROVADO; (b) on-demand; (c) opcional em `/checkpoint` substantivo. **SUPLANTA × EMENDA:** §Decisão/§Alternativas muda → novo ADR + `Substituído por:`; §Implementação/§Consequências → emenda in-place via STATUS-field.

## 11. Handoff cross-sessão obrigatório quando declarado (ADR-012 v1.13.0)
discovery passo 6(e) pergunta "alimenta outra sessão/agente?". Se SIM → **Pacote de handoff** (`metacognition-core` §Pacote) é entregável obrigatório via J5: artefato consumível com versão; localização (repo/URL/path + branch/commit/PR); acesso (visibilidade + permissões + o que não foi versionado); prompt pronto-para-colar; pendências herdadas. **Teste binário:** outra sessão começa **sem perguntar nada de volta**? Princípio 14 §6. +qa-critic ganha rule #6 (RCA gate: anomalia detectada exige causa-raiz antes de resolver) e rule #7 (cobertura temporal pós-J4: artefato novo intra-bloco re-disparo cirúrgico mandatório).

## 12. Enforcement mecanizado + entrega de produto (v1.14.x→v1.21.0 — ADR-013..023)
"Da prosa ao mecanismo": regras que dependiam de boa-vontade ganharam **par executável** que roda sozinho no boot/runtime — você não precisa fazer nada, eles rodam:
- **No boot (SessionStart):** `check-repo-sync` (git fetch + pull seguro, ADR-019) · `check-core-agnostic` (linter de agnosticismo do núcleo, ADR-020) · `check-execution-mode` (modo default/avançado/autosuficiente, ADR-005) · `mission-gate` (pede o **`product_type`** no briefing, ADR-022).
- **Em runtime:** `effect-gate` (PreToolUse: bloqueia ação destrutiva T3 por efeito, ADR-015) · `compaction-gate` (PreCompact: não deixa compactar sem digest salvo, ADR-021).
- **No CI/pré-merge:** `validate_skills.py` (contrato de 8 campos por skill, ADR-013).
- **Entrega de produto (ADR-023):** o framework **culmina em produto** de software/dados. Declare o `product_type` no briefing; para produto com UI ou com dados/ML, a app `exemplos/dominio-software/` adiciona `ux-designer` + `evals-engineer`. `governance-lead`/`skill-librarian` não existem como papéis — já cobertos pelo `high-stakes-gate` e pelo campo `classe`.
