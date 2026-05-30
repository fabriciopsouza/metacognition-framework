# history.md — Registro append-only do framework

> Single-writer = orquestrador (PMO). Append-only. Cada entrada com timestamp ISO.
> Formalizado pelo ADR-007 (v1.9.0). Já era referenciado pelo `AGENT-FRAMEWORK.md` §2.B
> (sequência de ativação do squad lê últimas 30 linhas).
>
> 3 seções: histórico cronológico de checkpoints (formato em `.agent/workflows/checkpoint.md`),
> `## Em aberto` (WIP — ex-G11), `## Aprendizado` (fracassos — ex-G9, com firewall).

---

## 2026-05-30T14:30 — Sessão: reconciliação de dívida pós-merge série v1.14.x→v1.19.0 + process-critic adversarial

Abertura via `/start-session` com `git fetch` (disciplina do method-audit 2026-05-30, já mecanizada por ADR-019/`check-repo-sync`): `main` em **v1.19.0** (`c866f95`), sync 0/0, tree limpo. **Process-critic adversarial pós-merge** (qa-critic isolado em **Sonnet**, heterogêneo ao Opus gerador — ADR-018) sobre a série consolidada: veredito **SÓLIDO-COM-DÍVIDA** (dimensões A–E; A/B/E PASS-com-ressalva, C/D PASS). **J4 (PMO) pegou false-PASS do próprio crítico** (Achado #1: o crítico disse "schema=5 opcionais"; o schema real tem 8 = 5 contrato + 3 legado) — arquitetura bicelular (ADR-011×018) auto-validada.

Dívidas reconciliadas (branch `chore/reconciliacao-divida-v1.14-v1.19`, 1 commit por item = reversível isolado):
- **#1 [ALTO]** ADR-013 stale count (Alt 3 "4"→"5") + gap ADR↔schema explicitado (5 contrato + 3 legado=8) — `00aa49f`.
- **#4+#6 [MÉD+BAIXO]** digest de pesquisa `git mv` para `docs/_intake/` (traço imutável) + ponteiro SSoT p/ faixas refinadas do ADR-016 (50–69/70–84/≥85) + refs corrigidas — `4cdcf67`.
- **#3 [ALTO]** 6 tags anotadas retroativas v1.14.0–v1.19.0 (ausentes local+origin; violavam política do CHANGELOG).
- **#2+#5 [MÉD+BAIXO]** este checkpoint (fechamento v1.18/v1.19 antes ausente) + ponteiro inverso ADR-019.

**Escopo novo declarado pelo dono nesta sessão (prosa→mecanismo):** regra anti-vazamento de domínio (Princípio 12) é prosa e **falhou ≥2× pega pelo dono** → **ADR-020 candidato**: linter executável de agnosticismo do núcleo + canário + wiring CI/boot. Régua §0(c): destrava o que a prosa não consegue garantir.

Próximo passo: fechar bloco ADR-020 (mecanismo) + PR único + merge. Reversibilidade por item preservada.

---

## 2026-05-28T09:01 — Sessão: v1.10.0 mergeada — método sênior de discovery (domain-agnóstico) + auto-observação (ADR-009)

Absorção pelo framework do método sênior validado no case real **AIVI** (LIMITES-BATENTES-RECALC, branch `claude/discovery-aivi-metodo-2026-05-27`). Substância: memórias `[[senior-discovery-method]]` + `[[framework-self-improvement]]` + `[[framework-gaps-from-aivi-case-2026-05-27]]`.

Aprovado e funcionando:
- **ADR-009 Aceito** após **4 rounds qa-critic adversariais (16 findings endereçados)**: round 1 (2 ALTO A1 colisão namespace ADR-008→009 + A2 template ganha §7 Antecipações + §8 Backlog + M1-M5+B1), round 2 (4 MEDIO + 1 BAIXO + 2 ADV), round 3 (3 MEDIO + 1 BAIXO + 2 ADV stale counts), round 4 LIMPO (único bloqueador foi meta-recursão do próprio campo Status).
- **v1.10.0 mergeada** em main via `--no-ff` (commit `d73244e`), **tag `v1.10.0`** anotada criada, branch `feat/v1.10.0-senior-discovery-method-auto-improvement` deletada (local + remote).
- 5 commits no branch: `11c1289` feat + `01e598a`/`f622f89`/`3d96d94` fixes rounds 1-3 + `3d8c873` promoção a Aceito.
- **Régua §0 mantida**: 2 novos + 9 edições cirúrgicas (escopo cresceu de 2+4+1 para 2+9 pela incorporação adversarial; todas edições de 1-3 linhas; sem nova pasta/workflow/template/skill).

Nomenclaturas estabelecidas:
- **Reforço transversal sênior** = método de discovery domain-agnóstico (não sub-modo; carregado sob demanda quando há fonte canônica/normativa citada).
- **Companion `metodo-senior.md`** = 8 passos auditáveis (mapeamento + **vigência** + complementações + cross-domain + pertinência + elicitação + classificação + adversarial).
- **Method-audit autônomo** = 0-3 notes/sessão substantiva em `## Aprendizado` (plug em ex-G9 de ADR-007).
- **Princípio 11** (`AGENT-FRAMEWORK.md` §6) = auto-observação do framework.
- **ADR-008 candidato** continua reservado para D2/check-execution-mode global (ADR-006 §Pendências).

Decisões permanentes:
- ADR-009: método sênior + auto-observação (Aceito, mergeado `d73244e`).

Próximo passo: **AIVI fechamento** no repo `LIMITES-BATENTES-RECALC` branch `claude/discovery-aivi-metodo-2026-05-27` — implementar REQ-001..007 contra a SPEC + qa-critic round 1+2 + run com `dados_mestre/2026_VAR_INT_CSV.csv` + validar CA-1..CA-6 + gate humano. Trabalho fora deste repo.

Riscos ativos:
- 6 follow-ups em ADR-009 §Pendências (não-bloqueantes): high-stakes-gate auto-load por gatilhos, requirements.md universal+sênior, external research handle (WebSearch), drift detector framework-boot.ps1, ADV1-4 estruturais (revisitar se padrão recorrer), AIVI fechamento.
- Meta-recursão de Status do ADR pode reaparecer em próximo ADR — registrado como method-audit.

---

## 2026-05-27T21:59 — Sessão: pagamento da dívida de eval do G1 (pesquisa-cascata) + 1ª cascata real

Abertura via /start-session reconciliou o repo vivo contra o "PLANO DE OTIMIZAÇÃO" colado pelo mantenedor: o plano é o **intake já entregue** na v1.9.0 (arquivado em `docs/_intake/`, virou ADR-007 Aceito). Nada a re-fazer — confirmado warning #6 (snapshot vs repo vivo). Decisão do mantenedor no gate: **pagar a dívida de eval do G1** (única pendência acionável do próprio plano, §5.2 / ADR-007 §Pendências).

Executado:
- **Eval seção I (funcional, ADR-007:103-112) RODADO: 9/9 PASS** — registrado em `_meta/eval-results-papeis.md` §I [EXECUTADO]. Método: 1 pesquisa-cascata real de ponta a ponta, casos verificados contra a execução. Caso 9 marcado `✅*` (nuance honesta: guard de não-repetição exercido por ausência-de-fonte, não por empty-return técnico).
- **1ª pesquisa-cascata real disparada** (field-validation que o ADR-007 §Validação pedia). Tema: porte cross-platform dos hooks (backlog D4). 2 rodadas, 4 explorers isolados (~104K tokens — confirma empiricamente o custo multi-agente do intake §2). Output: `docs/specs/cross-platform-hooks/research-brief.md`.
- **Achados que destravam decisão futura:** (a) o lock-in PowerShell já é dívida registrada (ADR-004/005/006 + D4, trigger-gated); (b) `bootstrap.sh` já existe mas stuba a instalação de hooks de propósito; (c) **GAP-1** — a bifurcação `pwsh` (PowerShell Core) vs reescrita `.sh` nunca foi avaliada pelos ADRs e decide o custo do porte (recomendação: spike de 1h antes de qualquer ADR); (d) **GAP-2** — caminho absoluto `$env:USERPROFILE` inscrito no `~/.claude/settings.json` global é bug latente multi-PC, não-documentado.

Régua §0 aplicada à própria execução: NÃO abri ADR nem implementei (D4 é trigger-gated; abrir agora seria adição pré-gatilho). NÃO spawn de qa-critic separado — o ataque anti-raso (passo 7 do pipeline) é o gate adversarial do brief, e o eval é a verificação; um qa-critic extra não mudaria o resultado (custo sem ganho).

Sem gatilho de fracasso disparado → nada em `## Aprendizado`. Próximo passo: gate humano (ver `## Em aberto`).

---

## 2026-05-27T20:50 — Sessão: reconciliação de sync + 2 bugs de encoding/boot nos hooks

Abertura via /start-session detectou `main` ahead 1 de origin (commit `5b0b2a2`, fix UTF-8 runtime dos hooks de inject, não pushado). Pushado após avaliação §0 (devido: não pushar regrediria mojibake em outro PC — [[fabricio-multi-pc-workflow]]).

Dois bugs corrigidos + housekeeping:
- **`9321e28` — header v1.6.1 ASCII-safe.** O fix runtime anterior não pegava o literal `—` no heredoc da linha 58 de `inject-start-session.ps1`: PS 5.1 parseia `.ps1` sem BOM como CP-1252 ANTES de `[Console]::OutputEncoding` rodar. Trocado por `-` ASCII (unifica com o header global v1.8.0 que já era ASCII). Convenção registrada em memória.
- **Duplicação de /start-session (gap impl v1.8.0/ADR-006).** Confirmado: o `.claude/settings.json` do repo registra o hook de PROJETO v1.6.1 e o `~/.claude/settings.json` (via bootstrap) registra o GLOBAL — os dois disparam ao abrir o framework-repo. Fix: guard no hook de projeto que cede (`exit 0`) quando `~/.claude/hooks/inject-start-session-global.ps1` existe. Preserva boot de primeira-execução (global ainda ausente), elimina injeção dupla pós-bootstrap. Honra de lock preservada (global checa os locks).
- **Housekeeping:** 5 branches remotas de PRs mergeados deletadas (`chore/backlog-and-summary`, `feat/auto-sync-hook`, `feat/discovery-cascata-v190`, `feat/framework-optimization-v180`, `fix/adr-005-framework-sync-gap`). `_backup/*` preservado.

**v1.9.0 FECHADA:** impl 4/4 + DocOps + ADR-007 mergeados (commits `4ec6f60`, `6bb20ef`, `8c7f8ab`, merge `197b354`). Item removido de `## Em aberto`.

---

## 2026-05-27T03:30 — Sessão noturna: gap intake↔realidade na v1.9.0 reconhecido

Aprendizado documental (não-bloqueante): o intake §4 estimou "~6 edições de 1-3 linhas + 2 linhas de princípio" para a v1.9.0. A realidade do PR foi 428 inserções. O conteúdo é justificável linha a linha pela régua §0 (ADR-007: 160 linhas decisórias; companion + template: ~160 linhas substantivas; edições cirúrgicas: ~100 linhas). Não há regressão funcional — apenas a estimativa do intake estava errada por ~70× porque não considerava ADR+companion+template como artefatos novos legítimos. Lição: estimativas em intake devem distinguir "edições" de "artefatos novos". Não vira ADR (caso isolado, não padrão recorrente — §Aprendizado).

---

## 2026-05-27T01:00 — Sessão noturna: ADR-006 + ADR-007 + Régua §0

Aprovado e funcionando:
- v1.7.1 mergeada em main (PR #7, commit 99cf801) — fix do gap ADR-005 (framework-sync.ps1 espelhado).
- v1.8.0 mergeada em main (PR #8, commit afb98aa) — auto-boot global do squad com allowlist (ADR-006).
- Modo `autosuficiente` ativado em campo (PC do mantenedor); ratchet ADR-005 validado.

Nomenclaturas estabelecidas:
- `framework-sync.ps1` (instância global) ≠ `sync-global.ps1` (fonte versionada) — par fonte/binário.
- `squad-owners.txt` — allowlist de owners para auto-boot global.
- Régua §0 = GANHO LÍQUIDO (princípio 10 do AGENT-FRAMEWORK §6).

Decisões permanentes:
- ADR-005: modos de execução (Aceito, mergeado).
- ADR-006: auto-boot global (Aceito, mergeado em PR #8).
- ADR-007: Régua §0 + G1 pesquisa-cascata + ex-G9 + ex-G11 (Aceito, em implementação v1.9.0).

Próximo passo: completar implementação v1.9.0 + qa-critic código + PR + merge; depois FASE C (backlog) + FASE D (sumário).

Riscos ativos: race condition humano vs orquestrador no history.md (mitigada por convenção append-only com timestamp — ADR-007 Risco 5).

---

## 2026-05-29T19:00 — Sessão: v1.11.0 + v1.12.0 mergeadas — agnosticismo estrito + RRC + arquitetura bicelular de QA (ADR-010 + ADR-011)

Sessão de fôlego longo (~80 turnos) que entregou DOIS releases consecutivos:
- **v1.11.0 (ADR-010)** — framework agnóstico estrito + discovery declara escopo + RRC obrigatório + princípio 11 honestamente reescrito ("auto-observação" → "observação meta-cognitiva — captura estruturada de feedback"). 4 rounds qa-critic (6 ALTO + 8 MEDIO + 5 BAIXO + 5 ADV endereçados). Merge `bd64b08` + tag `v1.11.0` push origin.
- **v1.12.0 (ADR-011)** — arquitetura bicelular de QA: 6 junções binárias forward-only (J0-J5) + process-critic adversarial final com poder de rewind cascata + TODO QA adversarial + SUPLANTA × EMENDA. 4 rounds qa-critic (5 MEDIO + 3 BAIXO + 2 ADV endereçados). Merge `fb637ac` + tag `v1.12.0` push origin.

Aprovado e funcionando:
- ADR-009 promovido na sessão anterior (v1.10.0), validado em uso real nesta sessão.
- ADR-010 + princípio 12 (framework agnóstico) Aceito. V1-A purga = 0 ocorrências em arquivos ativos do núcleo.
- ADR-011 + princípio 13 (arquitetura bicelular) Aceito. 6 junções declaradas em `/handoff` com gates binários explícitos.
- 9 passos método sênior (8 originais ADR-009 + passo 9 Coherence Pass / RRC ADR-010) — sync em CLAUDE/AGENTS/SKILL/companion.
- 3 seções obrigatórias no output do reforço sênior (Antecipações + Backlog + Gaps não-bloqueantes) — sub-§7.1 propagada ao template research-brief.md.
- HITL desacoplado de regulated: HITL via ADR-005 execution-modes; regulated declarado pelo discovery (ADR-010).
- Anti-vazamento cross-projeto registrado como princípio 12 + memória `senior-discovery-method.md` purgada de ALCOA+/ANP/FDA/BACEN.

Nomenclaturas estabelecidas:
- **Observação meta-cognitiva** (captura estruturada de feedback) = nome honesto do princípio 11 (substitui "auto-observação").
- **Escopo declarado pelo discovery** = seção obrigatória no `requirements.md`/`research-brief.md` quando há sinal de contexto especializado (passo 6 do `discovery/SKILL.md`).
- **RRC** (Read-and-Review-for-Coherence) = passo 9 do método sênior + gate de saída no `/checkpoint` com 6 itens binários (5 dimensões coerência + anti-vazamento).
- **Modo Transcribe vs Modo Interview** = passo 6 do discovery; transcribe é determinístico quando briefing tem declaração nominal+ubíqua+stakeholder+sem-contradição; interview é default.
- **Junção binária forward-only** = transição entre papéis com gate explícito; iterações DENTRO até PASS; forward-only ENTRE junções (anti-loop).
- **Process-critic** = qa-critic adversarial final em subagente isolado com poder de rewind cascata a qualquer J_i.
- **SUPLANTA × EMENDA** = política binária: §Decisão/§Alternativas muda → SUPLANTA novo ADR + `Substituído por:`; §Implementação/§Consequências → EMENDA in-place via STATUS-field. Within-junction rounds = EMENDA.
- **BLOCO APROVADO** = unidade de entrega que o autor declara "pronto" (release, ADR aceito, spec fechada, feature delivered) — gatilho mandatório do process-critic.

Decisões permanentes:
- ADR-010: framework agnóstico + discovery declara escopo + RRC + correção honesta princípio 11 (Aceito, mergeado `bd64b08`).
- ADR-011: arquitetura bicelular de QA + 6 junções binárias forward-only + process-critic rewind cascata (Aceito, mergeado `fb637ac`).

Próximo passo: aguardar trigger real (próximo projeto/case) para dogfood completo de J0-J5 via `/handoff` em fluxo real; ADR-010 follow-up (templates ganham `## Escopo declarado pelo discovery`) ativável quando próximo discovery rodar; ADR-011 follow-up (Alt 2 rewind cirúrgico) ativável se aparecer caso onde cascata é custosa.

Riscos ativos: nenhum bloqueante. Risco residual ADR-010 §Riscos (detector de vazamento cross-projeto ausente — mitigado por feedback do dono via method-audit, não eliminado).

---

## Em aberto

> WIP atual (ex-G11). Reconciliar com branches do git e ADRs em status `Proposto` no `/start-session` (modo squad).

- **[2026-05-30 · FECHADA] Reconciliação pós-merge série v1.14.x→v1.19.0 + ADR-020** — PR #18 mergeado em `main` (`2a8947f`, `--merge` preserva commits atômicos). Dívidas #1/#2/#3/#4/#5/#6 fechadas + **v1.20.0** (ADR-020 linter de agnosticismo, prosa→mecanismo do Princípio 12) após qa-critic round 2 (1 MÉD + 3 BAIXO). **Tags v1.14.0→v1.20.0 todas no origin** (dívida de tags da série inteira fechada). 5/5 gates verdes no main mergeado. 1 commit por item (reversível isolado).
- **[2026-05-30 · fechadas] v1.14.0→v1.19.0** — série "da prosa ao mecanismo" mergeada em `main` (ADR-013..019); gate humano das PRs empilhadas #11→#17 passado; `main`=`c866f95`. Tags retroativas sendo criadas na reconciliação (antes ausentes — Debt #3). CHANGELOG até `[1.19.0]`.
- *(v1.13.0 FECHADA em 2026-05-29 — ADR-012 Aceito após qa-critic round 1; handoff cross-sessão + drift sync + qa-critic rules #6/#7).*
- *(v1.11.0/v1.12.0/v1.12.1 fechadas em 2026-05-29 — merges `bd64b08`/`fb637ac`/`8fb044f` + tags `v1.11.0`/`v1.12.0`/`v1.12.1`).*
- **[2026-05-27/28 · fechado] AIVI fechamento** — PR #20 mergeado em master de `LIMITES-BATENTES-RECALC` (commit `10ecf0b`, 2026-05-28). REQ-001..011 implementadas + gate BABET 2025 = 0 (delta 0.000000) + 3 pendências runtime fechadas. Validação framework SSOT F0-F4 concluída.
- **Backlog ativo (trigger-gated, NÃO WIP):**
  - ~~ADR-010 §Pendências: templates `_template-research/research-brief.md` + `_template/requirements.md` ganham seção `## Escopo declarado pelo discovery`~~ **FECHADO em 2026-05-29 pós-merge v1.12.0** — ambos templates ganharam a seção em commit polish + diagrama Mermaid em ADR-011 §Topologia.
  - ADR-011 §Pendências: Alternativa 2 (rewind cirúrgico) — trigger: caso real onde cascata é custosa.
  - ADR-011 §Pendências: validation.md projeto × release convergir templates — trigger: ficar pesado manter separado.
  - Item D4 (cross-platform hooks Linux/macOS port) — trigger: user em PC não-Windows pedir.

---

## Aprendizado

> Notas de fracassos capturadas via `/checkpoint` (ex-G9). **Firewall:** notas são **inertes** — só viram comportamento via skill/regra destilada, aprovada via ADR e mergeada. Nota errada não propaga.

- **[2026-05-28T09:01] Method-audit (ADR-009 / princípio 11):** Stale counts ("4 edições" vs "9 edições") residuais em múltiplos arquivos atravessaram 3 dos 4 rounds qa-critic da v1.10.0. · **Causa-raiz:** scope cresceu por incorporação adversarial sem step de varredura de coerência interna antes de re-submeter — skill ausente: validation pre-commit de contagens/números/listas que possam ter ficado stale após scope-creep. · **Proposta (lean):** +1 linha em `_shared/docops` ou release checklist (`guia/GIT-VERSIONAMENTO.md`): "antes de re-submeter ADR/spec ao qa-critic após scope-creep, varrer documento por contagens stale (totais, listas, tabelas de implementação)".
- **[2026-05-28T09:01] Method-audit (ADR-009 / princípio 11):** Meta-recursão do campo `Status` do ADR — sempre 1 round atrás do qa-critic em curso (cada round novo encontra Status descrevendo o round anterior). · **Causa-raiz:** Status descreve auto-referencialmente um processo que ainda está rodando — impossível fechar sem fork. · **Proposta (lean):** se padrão se repetir em próximo ADR, atualizar template `docs/adr/000-template.md` para que Status use metadado externo (último commit-hash de round qa-critic) em vez de descrever rounds pendentes. **Não-preemptivo** — decisão sob demanda.
- **[2026-05-28T09:01] Method-audit (ADR-009 / princípio 11):** ADV-1 round 1 (localização do companion `metodo-senior.md` em `.agent/skills/discovery/` vs `_shared/`) foi marcado como follow-up sem decisão consciente. · **Causa-raiz:** framework não tem critério explícito para distinguir "transversal entre papéis" (vive em `_shared/`) de "companion-de-skill" (vive ao lado da skill dona). · **Proposta (lean):** se próximo ADR (architect/developer/qa-critic) precisar referenciar `metodo-senior.md`, decidir then — não criar regra preemptiva.
- **[2026-05-29T19:00] Method-audit (ADR-009 / princípio 11 reescrito ADR-010 §C-1):** v1.11.0 absorção falhou no RRC self-applied — agente racionalizou `README.md:4` ("ALCOA+/ANP/FDA/BACEN/GAMP" como exemplo didático) como OK enquanto o gate dizia ZERO refs. **Foi o dono que detectou e corrigiu.** · **Causa-raiz:** agente que se auto-audita defende suas próprias escolhas (viés). Princípio 11 original ("auto-observação") supervalorizava capacidade que não existe. · **Proposta (executada):** princípio 11 reescrito como "observação meta-cognitiva (captura estruturada de feedback)" — agente registra notes proativamente quando consegue E via feedback do dono (fonte legítima). Limite documentado em ADR-010 §C-1.
- **[2026-05-29T19:00] Method-audit (ADR-009 / princípio 11):** v1.11.0 + v1.12.0 cada uma teve 3-4 rounds qa-critic com **mesmo padrão de stale counts** ("8 passos" → "9 passos"; "5 itens" → "6 itens"; "6 edits" → "11 edits"). RRC self-applied pelo agente passou pelos contadores stale em múltiplos arquivos. **3 rounds com mesmo tipo de finding confirma empíricamente o limite previsto em ADR-010 §ii** — RRC tem como objetivo reduzir achados de coerência mas não promete eliminação total; gate humano externo (qa-critic adversarial em subagente isolado) é complemento NECESSÁRIO, não opcional. · **Causa-raiz:** scope-creep durante absorção de findings adversariais não dispara releitura completa cross-document. · **Proposta (executada em ADR-010 §ii.2):** RRC ganhou "contagens em sync" como 5ª dimensão de coerência obrigatória (`/checkpoint` RRC gate em 6 itens; `/checkpoint` workflow e validation.md V7 já refletem).
- **[2026-05-29T19:00] Method-audit (ADR-009 / princípio 11):** v1.12.0 foi dogfood real do v1.11.0 — discovery inline aplicou passo 6 ADR-010 (Escopo declarado: regulado=NÃO, alto-risco=NÃO crítico, semântica=SIM anti-fraude, gaps=flagados) + método sênior 9 passos incluindo RRC + 3 seções obrigatórias. **Pipeline integral funcionou em projeto real, não sintético.** · **Validação positiva:** princípios 10-13 não regrediram à média entre releases consecutivas; ciclo de auto-melhoria do framework é sustentável quando case real está disponível. · **Sinal de saúde:** taxa de princípios novos por release deve cair com o tempo; v1.10.0 = +1, v1.11.0 = +1, v1.12.0 = +1. **Alvo v1.13.0 = ≤1 princípio novo**; se nada surgir natural, saúde confirma maturidade.
- **[2026-05-29T22:30] Method-audit (princípios 10+11+13 / 4 padrões observados na sessão de hoje):** (a) **3 inflações detectadas PELO DONO** antes do commit final (README "ALCOA+/ANP/FDA" como exemplo didático em v1.11.0; "cascata cirúrgica" oxímoro em v1.12.0; §05 nova em web/index.html pós-v1.12.0). (b) **3 polish commits post-v1.12.0** (22cd976/f2fb4a7/16a4ae4) auto-declarados "não-bloco" sem critério binário — f2fb4a7 introduziu Mermaid (surface estrutural) e qualificava como bloco. (c) **Velocidade insustentável** — 3 princípios em 1 dia (11 reescrito + 12 + 13); alvo v1.13.0 = 0 princípios novos sem trigger real (registrado no checkpoint 19:00 mas vale reiterar). (d) **Comandos terse ("siga")** disparam reflexo de "fazer algo proativo" mesmo sem escopo declarado novo. · **Causa-raiz comum:** princípio 11 honesto operacional — agente não detecta próprio overreach sem gate humano. · **Proposta:** **sem nova regra/ADR.** Vigilância apenas: "siga"/"ok" autorizam continuar escopo declarado, NÃO novo escopo. Critério "polish vs bloco" registrado como trigger futuro se padrão repetir (não preemptivo).
- **[2026-05-29T23:55] Method-audit (princípio 11 honesto / dogfood AIVI 6 gaps remanescentes):** Sessão paralela `test-aivi-isolated` identificou 9 gaps de processo. v1.13.0 absorve **3 com evidência empírica forte** (Gaps 4 RCA / 5 cobertura temporal pós-J4 / 8 handoff cross-sessão). **6 gaps remanescentes registrados aqui como method-audit aguardando 2ª ocorrência confirmatória** (não preemptivos): (1) ancoragem em artefato rotulado "validação" — propõe metodo-senior passo 1A hierarquia fontes; (2) fonte citada pela norma não buscada — propõe metodo-senior passo 1B inventário bloqueante; (3) delta=0 amostra ≠ prova correção — propõe qa-critic rule SE/ENTÃO regressão×correção; (6) campo oficial vazio ignorado — propõe anti-hallucination anti-pattern; (7) inferir autoridade de dado sem confirmar — propõe anti-hallucination anti-pattern; (9) telemetria por papel — parte tratável (timestamp output qa-critic) + parte infra externa harness. **Sem ação preemptiva.** Causa-raiz comum: padrões reais mas com 1 ocorrência só não justificam codificação (princípio 11 honesto operacional).
- **[2026-05-29T23:55] Method-audit (observação do dono sobre isolamento/modelo selection per role):** apenas `qa-critic` explicitamente isolado em subagente; PMO/discovery/architect/developer/docops compartilham contexto+modelo (mesmo viés cognitivo). `_meta/subagent-isolation.md` documenta política existente ("isolar reduz context rot mas elimina visão lateral; trade-off por papel"), modelo per role NÃO codificado. Observação do dono honesta e procedente: maior custo é fazer trabalho mal feito; otimização tokens vs qualidade upfront mal balanceada. **Registrado como candidato v1.14.0 se 2ª ocorrência confirmar** (não preemptivo).
- **[2026-05-29T23:30] Method-audit (princípio 13 SE/ENTÃO recém-codificadas vs minha própria execução):** Em v1.12.1 codifiquei SE/ENTÃO rules + 4 dimensões PC em qa-critic SKILL e **NÃO as apliquei pre-commit da própria v1.12.1**. Submeti para qa-critic sem RRC self-applied; round 1 detectou ALTO (citação ADR não-rastreável, dimensão "process compliance") + MEDIO (rule #1 falta qualificador, dimensão "doc consistência"). **Ambos teriam sido detectáveis por self-check com 4 dimensões antes de submeter.** Dono apontou: "1 round = lean" foi judgment não princípio; assertividade UPFRONT > rounds eficientes downstream. · **Causa-raiz:** pattern recorrente do princípio 11 honesto — agente codifica regra e não a aplica em si próprio. · **Proposta:** PRÉ-COMMIT self-check obrigatório (não opcional) — aplicar SE/ENTÃO rules + 4 dimensões PC ANTES de submeter qualquer bloco a qa-critic. **NÃO adicionar como regra (régua §0 — já está em qa-critic SKILL).** Apenas disciplina: trate qa-critic round como confirmação, não descoberta primária. · **Sem ADR; sem v1.12.2.** Apenas vigilância no próximo bloco.
- **[2026-05-30] Method-audit (princípio 11 / bootstrap):** `/start-session` rodou file-first sobre clone **41 commits atrás** (local v1.9.0 vs remoto v1.13.0); só detectado quando o dono perguntou "fez sync?". · **Causa-raiz:** file-first sem `git fetch` lê retrato congelado — prosa sem mecanismo (justamente o que a série v1.14.x ataca). · **Proposta (lean):** `start-session.md` passo 1 ganha `git fetch` + checagem ahead/behind ANTES de reconciliar WIP; ativação de modo deve ser **verificada** (ler de volta), não assumida. Persistido em `memory/feedback_bootstrap_nao_pode_falhar`. **→ RECORREU e foi codificado como mecanismo em ADR-019 (v1.19.0): hook `check-repo-sync` faz `git fetch`+auto-pull seguro no boot.** (ponteiro inverso method-audit→ADR; fecha Debt #5 da reconciliação 2026-05-30.) Firewall preservado.
- **[2026-05-30] Method-audit (ambiente / robustez do run autônomo):** batch grande de tool-calls em paralelo **cancelou ~50 calls em cascata** por 1 erro (`pwsh` ausente no PATH do bash), perdendo 2 ondas não-commitadas. · **Causa-raiz:** ausência de commit atômico por artefato + `pwsh` só acessível via tool PowerShell/Python `subprocess`. · **Proposta (lean):** commit após cada artefato lógico (git preserva contra cancel); batches pequenos sequenciais quando há dependência. Persistido em `memory/feedback_ambiente_buffer_pwsh`. Sem ADR (não é regra do framework; é disciplina operacional do ambiente Claude Code).
- **[2026-05-30T14:30] Method-audit (princípio 12 / vazamento de domínio RECORRENTE → prosa→mecanismo):** na reconciliação pós-merge, **eu mesmo vazei `ALCOA+` como se fosse o princípio** que justifica preservar o traço de pesquisa (era para ser rastreabilidade/proveniência **agnóstica**, P14). **O dono pegou — 2ª/3ª ocorrência** do mesmo padrão (1ª: README v1.11.0 `ALCOA+/ANP/FDA/BACEN/GAMP`, linhas 154 e 157(a) acima; ambas pegas pelo dono, nunca auto-detectadas). · **Causa-raiz:** Princípio 12 é **prosa**; agente que se auto-audita não detecta o próprio vazamento (viés, P11 honesto). Prosa repetida ≠ garantia — exatamente a tese da série v1.14.x. · **Decisão (executada, NÃO mais "candidato"):** o dono declarou explicitamente prosa→mecanismo → **ADR-020**: `tools/check_core_agnostic.py` (linter fail-closed que varre o NÚCLEO — `_shared/`, `.agent/skills/`, `AGENT-FRAMEWORK.md`, `CLAUDE.md`, `AGENTS.md` — por nomes de norma de domínio fora de contexto-exemplo) + denylist em `tools/` (infra, não-núcleo → não viola agnosticismo) + canário + wiring CI/boot. Fecha o risco residual de ADR-010 §Riscos ("detector de vazamento cross-projeto ausente"). Régua §0(c): destrava garantia inalcançável por prosa.

---

## Telemetria

> Coletor único de auto-observação (ADR-017, v1.17.0). **2 métricas que mudam decisão, nada além** (P5).
> Agregar no fim do bloco/dia, não por turno. Método: `_shared/observability` §Telemetria mínima.

### 17-A Blame (fluxo entre junções, por execução)
> Quando process-critic dispara rewind: registrar junção-origem (J0–J5) + rounds de qa-critic até PASS.

- 2026-05-30 (run v1.14.x): rounds de qa-critic por onda — O0=1, O1=2, O2=1, O3=1 (todos resolvidos como emenda DENTRO de J4 qa-critic→docops; **nenhum rewind cascata cross-junção** — forward-only preservado). Sinal: a montante (discovery/architect) não gerou spec rasa; achados foram de implementação, corrigidos em 1–2 rounds. **Nota honesta (P11):** a métrica 17-A "junção-origem do rewind" NÃO foi exercida nesta onda — nenhum rewind ocorreu; só o proxy `qa_rounds` rodou. Capacidade de blame-de-rewind = [INFERIDO/não-exercido] até um rewind real.
- 2026-05-30T14:30 (reconciliação pós-merge + ADR-020): process-critic adversarial (Sonnet isolado) sobre série mergeada — 6 achados (1 ALTO J4-corrigido, 2 ALTO confirmados, 2 MÉDIO, 2 BAIXO). **J4 do PMO refutou 1 achado do próprio crítico** (count errado) — 1ª evidência empírica de que a célula PMO-verifica-crítico pega false-PASS do crítico, não só do gerador. Bloco ADR-020 (mecanismo agnosticismo): rounds qa-critic registrar ao fechar.

### 17-B Tally de regra + classe (uso ao longo de sessões)
> `regra — classe(salva-vidas|operacional|andaime) — disparou S/N — sem-disparo:K`. Poda só `andaime` quando K≥N (5–10).

- régua §0 (GANHO LÍQUIDO) — salva-vidas — S — sem-disparo:0 (rejeitou inflação/andaime em toda onda; ex.: _shared fora do contrato, matriz reprovada)
- qa-critic adversarial isolado/heterogêneo — salva-vidas — S — sem-disparo:0 (pegou false-PASS real em O0, O1, O2, O3)
- contrato mínimo (validate_skills) — operacional — S — sem-disparo:0 (gate 7/7 em cada onda)
- file-first — salva-vidas — S — sem-disparo:0 (violado no bootstrap → ver Aprendizado 2026-05-30)
