# ADR 019 — Sincronização do repo no boot (da prosa ao mecanismo no /start-session)

- Status: Aceito
- Data: 2026-05-30 · Decisores: dono (cobrança explícita: "é dívida") + squad
- Pesquisa: nenhuma (gap operacional confirmado em campo, não candidato de pesquisa) · Tipo: **EMENDA** (Princípios 8, 11; estende ADR-004/005/006 — cadeia SessionStart)
- Relaciona: `.agent/workflows/start-session.md`, `.claude/hooks/`, `sync-global.ps1`, method-audit 2026-05-30.

## Contexto

A série v1.14.x mecanizou 5 regras do plano ("da prosa ao mecanismo"), **mas deixou como method-audit
note (prosa) justamente o gap que estourou em campo:** o `/start-session` faz file-first sobre o clone
local **sem `git fetch`**, lendo um retrato congelado. Caso real desta linha de sessões: o agente operou
**41 commits atrás** de `origin/main` (v1.9.0 local vs v1.13.0 remoto) e só percebeu quando o dono
perguntou "fez sync?". Repetiu-se em escala menor depois (merge feito no GitHub que o clone local não viu).

O dono cobrou isto explicitamente como **dívida** e pediu desde o início que a sincronização de boot
fosse **hook em runtime**, não prosa. Princípio 8 (context/estado é recurso) + Princípio 11 (observação
metacognitiva) + a própria tese da série exigem fechar o gap **como mecanismo**.

**Régua §0:** EMENDA — não cria papel nem subsistema; adiciona 1 hook de propósito único à cadeia
SessionStart já existente (irmão de `sync-global`/`check-execution-mode`/`inject-start-session`) e
estende `start-session.md` passo 1. Ganho: elimina uma **classe confirmada de falha silenciosa**
(operar sobre repo defasado) — o tipo de adição que a régua aprova por critério (c).

## Decisão (1 frase ativa)

Adicionar um hook `check-repo-sync.ps1` ao SessionStart que **sempre faz `git fetch`** (read-only),
**auto-atualiza com `git pull --ff-only` somente quando provadamente seguro** (working tree limpo +
fast-forward) e **avisa sem tocar** caso contrário (tree sujo ou histórico divergiu); e tornar o
`git fetch` + checagem ahead/behind o **passo 1 explícito** do `start-session.md` (superfície universal,
inclusive chat sem hook).

### Política de segurança (honesta — não promete o que é arriscado)
| Situação | Ação do hook |
|---|---|
| Em dia (behind=0) | silencioso (sem ruído) |
| Atrás + **sem modificações rastreadas** + **fast-forward** | **AUTO-PULL `--ff-only`** → injeta "✅ auto-atualizado". **Untracked NÃO bloqueia** (caso comum: clone + nota local; `--ff-only` aborta com segurança se um untracked fosse sobrescrito → vira aviso) |
| Atrás + **modificações rastreadas** | **NÃO mexe** → injeta "⚠️ commit/stash + `git pull` antes de reconciliar" |
| Atrás + **divergiu** (não-ff) | **NÃO mexe** → injeta "⚠️ rebase/merge manual antes de reconciliar" |
| Auto-pull tentado mas falhou (rc≠0: untracked colidiria, lock, pre-merge hook) | injeta "⚠️ pull não concluiu, rode manual" (exit code do pull é o sinal autoritativo) |
| Não é repo git / offline / erro | falha **soft** (warning stderr + exit 0) — nunca bloqueia |

**Por que não auto-pull sempre:** pull em tree sujo ou não-ff pode gerar merge inesperado, conflito ou
perda de contexto. O hook **detecta sempre** e **corrige só quando é seguro** — "atualizar" no caso
comum (main limpo atrás), "avisar alto" no caso arriscado. Detecção é o piso garantido; correção é o
bônus seguro.

### Verificação por ambiente (mesma regra, mecanismo diferente)
- **IDE/SDK:** hook `check-repo-sync.ps1` no SessionStart (registrado em `.claude/settings.json`;
  espelhado a `~/.claude/hooks/` por `sync-global.ps1`). Canary `tools/test_repo_sync.py` prova os 3 caminhos.
- **Chat web (sem hook):** `start-session.md` passo 1 instrui o agente a rodar `git fetch` + ahead/behind
  manualmente antes de reconciliar WIP. É instrução, não gate — declarado, não fingido (honestidade P1).

## Alternativas consideradas
1. **Deixar como method-audit note (status quo).** Prós: zero código. Contras: é a dívida que o dono
   cobrou; o gap já falhou 2× em campo. Rejeitada.
2. **Auto-`git pull` incondicional no boot.** Prós: "sempre atualizado". Contras: perigoso em tree sujo
   (merge/conflito) ou não-ff; pode corromper trabalho local não-commitado. Rejeitada — viola fail-safe.
3. **Hook fetch + auto-pull-quando-seguro + aviso-quando-não + passo no workflow (ESCOLHIDA).** Prós:
   fecha o gap como mecanismo, seguro por construção, honesto sobre o teto (detecta sempre, corrige
   quando dá). Contras: +1 hook + 1 canary + edições (pago pela classe de falha eliminada).

## Consequências
**Positivas:** boot nunca mais opera sobre repo defasado sem avisar; no caso comum (main limpo atrás)
ele se atualiza sozinho; canary garante que o mecanismo é real, não afirmado.
**Negativas:** +1 hook + 1 canary + 1 entrada no settings.json; `git fetch` adiciona latência de boot
(mitigado: timeout 30s, falha soft).
**Riscos:** (a) **registro global** para *outros* repos squad (auto-boot ADR-006) é **follow-up
trigger-gated** — o hook é espelhado a `~/.claude/hooks/` mas o merge no SessionStart global (via
`bootstrap.ps1`) não foi feito nesta versão; no **repo-framework** já está wired pelo settings do projeto.
**[DESCONHECIDO]** se vale a pena para todo repo ou só os de framework. (b) paridade `.sh` (Linux/macOS)
documentada, **não testada** **[DESCONHECIDO]** — consistente com ADR-015. (c) `fetch` offline → falha
soft (sem rede, segue com o que tem; aceitável).

## Implementação (ponteiro após aceito)
- Ponteiro: branch `feat/v1.19.0-boot-sync` · `2026-05-30` · grep `check-repo-sync|fetch|--ff-only`
- Artefatos: `.claude/hooks/check-repo-sync.ps1` (+ `.sh` paridade), `tools/test_repo_sync.py` (canary
  5/5 PASS), `.claude/settings.json` (SessionStart), `sync-global.ps1` (espelho), `start-session.md` (passo 1).
