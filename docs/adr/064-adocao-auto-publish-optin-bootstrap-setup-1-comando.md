# ADR 064 — Adoção: publish AUTOMÁTICO (batch/sessão) + opt-in no bootstrap + setup do dono em 1 comando

- Status: **Aceito** (2026-06-05 — LIVE-verificado: --publish gerou PR no corpus, fail-soft confirmado) · Data: 2026-06-04 · Decisores: dono + squad (architect/developer)
- Onda: telemetria/aprendizado (alvo v1.43.0) · Tipo: **EMENDA do ADR-063** (a §Implementação do publish). Atende: "eu e os usuários precisamos executar estes passos? não vai ter adesão."
- Relaciona/herda: **ADR-063** (repo central via PR — BASE), **ADR-062** (learnings_public, consent), **ADR-006** (auto-boot/bootstrap).

## Contexto

O ADR-063 mecanizou a SEGURANÇA (fail-closed, anti-PII, pseudônimo) mas deixou a ENTREGA **manual** (`gh pr create` por relatório). **Cada passo manual recorrente corta a adesão pela metade** — "PR por relatório" = adoção zero. Telemetria que exige ação humana por evento não é telemetria.

## Decisão (1 frase ativa)

**Tornar a contribuição de baixíssimo atrito: (1) publish AUTOMÁTICO no fechamento de SESSÃO** (batch — 1 PR/sessão, não 1/bloco, p/ não fazer spam), rodado pelo docops **se houver opt-in**, **fail-soft** (sem `gh`/auth → "gerado local, não publicado", nunca trava); **(2) opt-in perguntado 1× no `bootstrap`** (privacy-by-default: pergunta clara, default NÃO; grava consent + pseudônimo OU marca "declinado" p/ não re-perguntar); **(3) setup do dono em 1 comando** (`tools/setup_central_reports`: `gh repo create` + dropa o CI + liga auto-merge/branch-protection via `gh api`). Resultado: dono roda **1 comando 1×**; usuário responde **1 pergunta 1×**; depois **ninguém faz mais nada**.

## Alternativas consideradas

1. **Manter PR manual por relatório (ADR-063 como estava).** Adoção zero. **Rejeitada (o ponto do dono).**
2. **1 PR por BLOCO automático.** Funciona mas faz spam (N PRs/sessão). **Rejeitada → batch por sessão.**
3. **Opt-out (coleta por default).** Maior adesão aparente, mas LGPD/confiança pior; quem não percebeu não consentiu de verdade. **Rejeitada → opt-in privacy-by-default.**
4. **Auto-publish/sessão + opt-in-no-bootstrap + setup-1-comando (ESCOLHIDA).** Atrito recorrente = zero; opt-in sincero; fail-soft.

## Consequências

**Positivas:** adoção real — o atrito recorrente some (automação + opt-in único); o opt-in sincero (default Não) é LGPD-correto **e** mais confiável; batch/sessão controla spam (1 PR/sessão); fail-soft não pune quem não tem `gh`/auth (degrada para "gera local"). **Negativas/limite:** depende de `gh` autenticado (o bootstrap já o exige; sem ele → não publica, fail-soft, declarado); o auto-publish abre PR **sem revisão humana do conteúdo pelo contribuidor** (o gate é o fail-closed client-side + CI central — por isso ambos são obrigatórios); bootstrap **não-interativo** (CI/cron) **não pergunta** → sem consent → não publica (default seguro); a sequência `gh` (fork→PR) é best-effort e **não testável no sandbox** (sem repo central + sem auth) → verificação do dono. **Gap declarado (qa-critic):** o `effect-gate` (ADR-039/015) **NÃO intercepta** o `gh` spawnado como subprocesso dentro do Python (`publish_learnings`/`setup_central_reports`) — ações outward-facing por subprocesso furam o gate (PreToolUse vê o comando Python, não o `gh` neto). Por isso o **único gate outward-facing deste fluxo é o fail-closed client-side** (consent + anonymize + denylist) ANTES do spawn; o CI central é a 2ª barreira. *Caso real: o setup criou o repo público sem passar pelo effect-gate (sessão 2026-06-04).* Candidato a ADR futuro: gate de efeito por subprocesso. **SUPLANTA×EMENDA:** muda o canal de ingestão (PR→API/bot) → novo ADR.

## Implementação (ponteiro)

- `execution_report.py`: `publish_learnings(owner_path, root, run_gh=True)` — consent→learnings_public (fail-closed)→staging `telemetry/learnings-public/<pseudo>/<ts>__<exec>.md`→`gh` PR (fail-soft, `shutil.which('gh')`); CLI `--publish`. Testável: consent/anonimização/staging-path; o `gh` é fail-soft.
- `bootstrap.py`: prompt 1× **TTY-guarded** (não-interativo pula), idempotente (consent OU `~/.claude/exec-report-declined.lock` → não re-pergunta), default NÃO.
- `tools/setup_central_reports.sh`: 1 comando do dono (repo + CI + auto-merge).
- `docops/SKILL.md §Encerramento`: ao FIM DE SESSÃO, se opt-in, `python tools/execution_report.py --publish` (fail-soft).
- `REPORTS-CONTRIBUTION.md`: fluxo automático + bootstrap + 1-comando. **DONE quando:** usuário só responde 1 pergunta no bootstrap e os relatórios chegam sozinhos ao central; sem `gh` → gera local sem travar. Status→Aceito após verificação do dono.
