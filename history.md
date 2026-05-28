# history.md — Registro append-only do framework

> Single-writer = orquestrador (PMO). Append-only. Cada entrada com timestamp ISO.
> Formalizado pelo ADR-007 (v1.9.0). Já era referenciado pelo `AGENT-FRAMEWORK.md` §2.B
> (sequência de ativação do squad lê últimas 30 linhas).
>
> 3 seções: histórico cronológico de checkpoints (formato em `.agent/workflows/checkpoint.md`),
> `## Em aberto` (WIP — ex-G11), `## Aprendizado` (fracassos — ex-G9, com firewall).

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

- *(nenhum item em aberto.)* O brief `cross-platform-hooks` é insumo do backlog **D4** (trigger-gated, Windows-only hoje) — rastreado lá, não é WIP ativo. **GAP-2 DESCARTADO** como não-bug: `~/.claude/settings.json` é local de cada máquina e o `bootstrap` regenera o caminho ao rodar; nunca é copiado entre PCs. (Correção: eu havia inflado "cuidado com origin" em requisito multi-PC — não era.)

---

## Aprendizado

> Notas de fracassos capturadas via `/checkpoint` (ex-G9). **Firewall:** notas são **inertes** — só viram comportamento via skill/regra destilada, aprovada via ADR e mergeada. Nota errada não propaga.

- *(nenhum aprendizado registrado nesta sessão — sem gatilho de fracasso disparado)*
