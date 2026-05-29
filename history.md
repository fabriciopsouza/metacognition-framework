# history.md — Registro append-only do framework

> Single-writer = orquestrador (PMO). Append-only. Cada entrada com timestamp ISO.
> Formalizado pelo ADR-007 (v1.9.0). Já era referenciado pelo `AGENT-FRAMEWORK.md` §2.B
> (sequência de ativação do squad lê últimas 30 linhas).
>
> 3 seções: histórico cronológico de checkpoints (formato em `.agent/workflows/checkpoint.md`),
> `## Em aberto` (WIP — ex-G11), `## Aprendizado` (fracassos — ex-G9, com firewall).

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

## Em aberto

> WIP atual (ex-G11). Reconciliar com branches do git e ADRs em status `Proposto` no `/start-session` (modo squad).

- **[2026-05-28 · em-curso] v1.11.0 — ADR-010 Proposto** — framework agnóstico estrito + discovery declara escopo + RRC obrigatório (sub-princípio anexo ii) + gaps não-bloqueantes flagados. Branch `feat/v1.11.0-framework-agnostic`. **Próximo passo:** qa-critic round 1 (adversarial) → iterar → merge main + tag `v1.11.0`.
- **[2026-05-28 · backlog] ADR-011 candidato — Arquitetura de QA bicelular (junction-critic binário forward-only + process-critic rewindable global)** — dono propôs em 2026-05-28 (sessão v1.11.0). Mapeia ao que já é emergente: `validation.md` binário (junções), `qa-critic` adversarial (process). Falta formalizar topologia: nomear cada junção do fluxo discovery→architect→developer→docops, exigir binário forward-only em cada uma, separar do process-critic global que pode rewindar. **Próximo passo (v1.12.0):** discovery → architect → ADR-011 dedicada com mapeamento das junções existentes + política de rewind + how-to. **NÃO bundlar com v1.11.0** (eixo independente; bundlar dobra risco qa-critic).
- **[2026-05-27/28 · em-revisão→fechado] AIVI fechamento** — PR #20 mergeado em master de `LIMITES-BATENTES-RECALC` (commit `10ecf0b`, 2026-05-28). REQ-001..011 implementadas + gate BABET 2025 = 0 (delta 0.000000) + 3 pendências runtime fechadas (Batentes 84%, YSMM 100%, NaN 0). Fixes C5+D4 do master preservados via merge consciente. Branch `claude/discovery-aivi-metodo-2026-05-27` deletada. Validação framework SSOT F0-F4 concluída.
- Insumo de backlog **D4** (cross-platform hooks, trigger-gated, Windows-only hoje): brief `docs/specs/cross-platform-hooks/research-brief.md` permanece como referência futura — não é WIP ativo. **GAP-2 DESCARTADO** como não-bug (settings global é local de cada máquina; bootstrap regenera).

---

## Aprendizado

> Notas de fracassos capturadas via `/checkpoint` (ex-G9). **Firewall:** notas são **inertes** — só viram comportamento via skill/regra destilada, aprovada via ADR e mergeada. Nota errada não propaga.

- **[2026-05-28T09:01] Method-audit (ADR-009 / princípio 11):** Stale counts ("4 edições" vs "9 edições") residuais em múltiplos arquivos atravessaram 3 dos 4 rounds qa-critic da v1.10.0. · **Causa-raiz:** scope cresceu por incorporação adversarial sem step de varredura de coerência interna antes de re-submeter — skill ausente: validation pre-commit de contagens/números/listas que possam ter ficado stale após scope-creep. · **Proposta (lean):** +1 linha em `_shared/docops` ou release checklist (`guia/GIT-VERSIONAMENTO.md`): "antes de re-submeter ADR/spec ao qa-critic após scope-creep, varrer documento por contagens stale (totais, listas, tabelas de implementação)".
- **[2026-05-28T09:01] Method-audit (ADR-009 / princípio 11):** Meta-recursão do campo `Status` do ADR — sempre 1 round atrás do qa-critic em curso (cada round novo encontra Status descrevendo o round anterior). · **Causa-raiz:** Status descreve auto-referencialmente um processo que ainda está rodando — impossível fechar sem fork. · **Proposta (lean):** se padrão se repetir em próximo ADR, atualizar template `docs/adr/000-template.md` para que Status use metadado externo (último commit-hash de round qa-critic) em vez de descrever rounds pendentes. **Não-preemptivo** — decisão sob demanda.
- **[2026-05-28T09:01] Method-audit (ADR-009 / princípio 11):** ADV-1 round 1 (localização do companion `metodo-senior.md` em `.agent/skills/discovery/` vs `_shared/`) foi marcado como follow-up sem decisão consciente. · **Causa-raiz:** framework não tem critério explícito para distinguir "transversal entre papéis" (vive em `_shared/`) de "companion-de-skill" (vive ao lado da skill dona). · **Proposta (lean):** se próximo ADR (architect/developer/qa-critic) precisar referenciar `metodo-senior.md`, decidir then — não criar regra preemptiva.
