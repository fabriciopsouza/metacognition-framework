# ADR 088 — A segurança do GHA SEM GHA: gate de merge dirigido pelos canários LOCAIS (BYO-CI)

- Status: **Aceito** (2026-06-17 — gate: qa-critic heterogêneo Sonnet em worktree PASS após corrigir `parse_repo` não-ancorado; recursão verificada ausente; canário do tool PASS) · Decisores: dono ("não estamos com github actions"; "atender a segurança sem ele"; "não quebrar o que funciona; melhorar com o que agrega") + squad
- Tipo: **correção de regressão de segurança + adição que mecaniza** (P15). Régua §0 (ADR-007): satisfaz (c) — *destrava o enforcement de merge que ficou inerte* ao remover o required-check morto do GHA; reusa a suíte de canários existente (não duplica gate). +1 capability `byo-ci-gate`.
- Relaciona: ADR-040 (run_canaries cross-platform), ADR-019/060 (boot/sync), P15 (determinismo-primeiro), ADR-074/077 (qa-evidence), [[github-actions-not-the-gate]]

## Contexto

Durante v1.62.0–v1.64.0, o merge para `main` ficou **bloqueado** pela branch protection que exigia 3 status checks do GitHub Actions (`canários (ubuntu/macos/windows)`). Esses checks estavam **vermelhos na própria `main`** (pré-existente) — não eram segurança viva, eram um **portão emperrado fechado** que bloqueava *todo* merge. Removi o required-check (`gh api -X DELETE …/required_status_checks`) para destravar (dono: "não estamos com github actions").

**Risco introduzido (apontado pelo dono):** remover o required-check tirou o *enforcement no nível do GitHub* — agora um commit com canário vermelho **poderia** ser mergeado (a trava virou disciplina). Pergunta do dono: *"conseguimos atender a segurança do GHA sem ele?"*

**Insight central:** a "segurança do GHA" e a suíte de canários são a **mesma coisa** — o `ci.yml` rodava literalmente `python tools/run_canaries.py`. O GHA era só um **gatilho/driver** desse gate. Logo, basta **reconectar a suíte viva (local) à trava do GitHub**, trocando o driver morto pelo vivo.

## Decisão

**(1)** `tools/post_canary_status.py` — roda `run_canaries.py` e posta um **commit-status** no SHA atual via `gh api repos/<repo>/statuses/<sha>`: `state=success` **somente** se 0 FAIL; senão `failure`. Context fixo `canarios-local`. Atrelado ao SHA + resultado real (não é carimbo); novo commit invalida o status anterior (strict mode). `--dry-run` (sem rede) para teste.

**(2)** Re-adicionar branch protection em `main` exigindo o status check **`canarios-local`** (strict). Um SHA sem run verde **não pode** ser mergeado — **mesmo modelo de enforcement do GHA** (required status check), driver local. A proteção de PR-review permanece.

**(3)** Canário `tools/test_post_canary_status.py` (fail-closed, sem rede): `parse_repo` (https/ssh/.git + fail-closed em não-GitHub); `decide_state` (0→success; **qualquer** !=0→failure — nunca verde por engano); `--dry-run` não chama `gh`. +1 capability `byo-ci-gate`.

## Alternativas consideradas

1. **Manter o required-check do GHA (e consertar a CI).** Rejeitada — dono declarou "não usamos github actions"; consertar/ manter GHA é o que não se quer.
2. **Pre-push git hook rodando os canários.** Rejeitada como *primária* — local-only, vetável por EDR (a classe de problema que já temos), bypassável com `--no-verify`; não bloqueia no nível do GitHub. (Pode coexistir como conveniência local.)
3. **Só disciplina de processo (squad roda canários antes do merge).** Rejeitada como *garantia* — é a fraqueza hook-mediada/disciplina-dependente que esta sessão expôs (qa-evidence pulado até o dono cobrar). Vira o caminho honesto-por-default SOB a trava (2), não a trava em si.

## Consequências

**Positivas:** restaura enforcement de merge no nível do GitHub usando a suíte que **já funciona** (não quebra o que funciona; reusa, não duplica); verde só com 0 FAIL no SHA exato; destrava merges legítimos que o portão morto barrava. **Negativas/limite (declarado, vs GHA):** (a) **1 OS** — o run é na máquina do mantenedor, não na matriz ubuntu/macos/windows (parcialmente coberto por `test_rules_parity` e canários cross-platform por construção, ADR-040); (b) **auto-atestação** — o status é postado pelo runner local, não por infra neutra; para repo de dono único iguala o limite de confiança já existente (admin pode mergear tudo), mas torna o caminho honesto o default e **bloqueia merge acidental de vermelho**. Mitigação futura possível (não agora): rodar `post_canary_status` num runner neutro se um dia voltar a haver CI.
