# ADR 006 — Auto-boot global do squad com allowlist de owners

- **Status:** Aceito (2026-05-27 — pelo mantenedor; aprovação em sessão noturna "o que aprovamos para adr06, sem inflar, sem piorar")
- **Data:** 2026-05-26 (original) · 2026-05-27 (revisão de escopo + aceite) · **Decisores:** Fabricio (mantenedor) + Claude (papel `architect`)
- **Substitui:** nenhum · **Substituído por:** nenhum
- **Relaciona-se a:** ADR-001 (sync-global hook), ADR-004 (auto-boot project-level), ADR-005 (modos de execução; gap resolvido em v1.7.1)

## Histórico desta revisão (2026-05-27)

A versão original (2026-05-26) tinha escopo coordenado: auto-boot global **+** fix do defeito de execução do ADR-005 (referência órfã a `~/.claude/hooks/framework-sync.ps1`). O fix foi extraído em PR separado (v1.7.1, branch `fix/adr-005-framework-sync-gap`, mergeado em main como commit `99cf801`) por pedido do mantenedor: *"retome adr005, finalize, e então avancemos do jeito certo"* — validar ADR-005 em campo antes de empilhar features. Modo `avancado` ativado em 2026-05-27T00:42-03:00.

Este ADR-006 agora cobre apenas o que resta: **auto-boot global + allowlist**. Infra `~/.claude/hooks/` já existe; `framework-sync.ps1` já é espelhado a cada SessionStart.

## Estado pós-implementação (v1.8.0, 2026-05-27)

- **Implementado** na branch `feat/framework-optimization-v180`. 6 arquivos efetivos.
- **qa-critic adversarial em 2 rounds** (subagente isolado, contexto fresh):
  - Round 1: APROVADO_COM_RESSALVAS — 1 média (WORKING-CONTEXT.md violava Régua §0), 2 baixas (statusMessage exemplo + numeração de passos), 3 adversariais (%USERPROFILE% ambíguo, migração v1.7.1→v1.8.0, multi-repo race).
  - Round 2: **APROVADO LIMPO** — 6 incorporações verificadas, zero regressão.
- **Validação operacional em campo** (2026-05-27, PC do mantenedor):
  - sync rodou: `16 skills + 2 agents + 2 hooks + 5 workflows -> ~/.claude/`
  - Teste 1 (allowlist match): `owner=fabriciopsouza match=fabriciopsouza` ✓
  - Teste 2 (project-lock): `skipped (project-lock)` ✓
  - Teste 3 (CWD=temp, sem marker): `skipped (no-match-no-marker)` ✓
- **`squad-owners.txt`** criado em `~/.claude/` com os 7 tokens default.
- **HOOK_CHANGED orgânico** esperado após este merge (sync-global.ps1 estendido → hash mudou) — próxima sessão dispara reconfirmação do modo `autosuficiente` (ratchet ADR-005 funcionando como projetado).

[CONSOLIDADO] / [CONFIRMADO] · validação operacional em campo confirmada.

## Contexto

O auto-boot do squad introduzido pelo ADR-004 (v1.6.1) vive **apenas no `.claude/settings.json` deste repositório-framework**. Consequência operacional reportada pelo mantenedor (sessão 2026-05-26): em qualquer outra IDE/projeto, o squad não acorda sozinho — é preciso pedir "aplique o framework" manualmente. Skills estão instaladas globalmente em `~/.claude/skills/` (efeito colateral benigno do ADR-001/sync-global), mas dormem até alguém invocar.

Pedido textual do mantenedor: *"se o repo for MEU, criado por ferramentas com minhas contas (fpsouza, fpsouz, fsouza, fabriciosouza, fabriciopsouza, vibraenergia, natulab), quero POR PADRÃO sempre ativo — pois na IDE sempre será trabalho técnico"*. Granularidade adicional: ativação condicional por repo (default ON em repos do mantenedor; default OFF em repos de terceiros).

A v1.7.1 (PR #7) já criou a infraestrutura `~/.claude/hooks/` e o `sync-global.ps1` espelha a si mesmo lá como `framework-sync.ps1`. Este ADR aproveita essa infraestrutura para colocar o hook global do auto-boot no mesmo destino.

## Decisão (1 frase ativa)

Promover o auto-boot do squad para o **nível global** (`~/.claude/settings.json` + `~/.claude/hooks/inject-start-session-global.ps1`) com **ativação condicional** por allowlist de owners do remote `origin` (config externa em `~/.claude/squad-owners.txt`) e fallback para marker explícito (`AGENTS.md` ou `.agent/` no projeto), reusando a infraestrutura `~/.claude/hooks/` já criada em v1.7.1; `bootstrap.ps1` garante o setup inicial em PC novo.

## Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **Auto-boot global com allowlist + fallback marker (escolhida)** | Default ON em repos do mantenedor (sem config por-projeto). Default OFF em terceiros (não polui). Override granular (allowlist, marker, locks). Reusa infra já posta em v1.7.1. | ~6 arquivos novos/alterados. Substring match na allowlist pode dar falso positivo (mitigável editando allowlist). Hook global + project-level coexistem com `additionalContext` duplicado (cleanup como follow-up). |
| 2 | Hook global "sempre ativo" sem allowlist | Simples; 1 hook + 1 settings.json change. | Mantenedor rejeitou: poluiria sessões em repos de terceiros (clones para estudar). |
| 3 | Manter project-level (status quo) | Zero esforço. | Mantém a fricção: em IDE com outro projeto seu, squad não acorda — exige pedido manual a cada sessão. |
| 4 | Migração radical: TODA infra de hooks vive só em `~/.claude/`, repo-framework só fornece fontes | Precedência cristalina. Repos clonados não dependem de hook project-level. | Revogaria parcialmente ADR-001 e ADR-004. Mudança grande, fora de escopo. Candidata futura. |

## Justificativa

A escolha do mantenedor pela ativação **condicional por owner** (Alternativa 1) equilibra três axiomas:

- **Default ON onde faz sentido** (repos do mantenedor): coerente com *"na IDE sempre será trabalho técnico"*.
- **Default OFF onde não faz sentido** (repos de terceiros): preserva a higiene de clonar/estudar código alheio sem o framework impor `/start-session`.
- **Override explícito disponível** (`AGENTS.md`/`.agent/` ou edição da allowlist): caminho para adotar repos sem GitHub remote ou em colaboração ativa com terceiros.

### Decisões internas do architect (que o mantenedor aceita ou reverte no review)

1. **Allowlist em arquivo externo** (`~/.claude/squad-owners.txt`), uma linha por token, `#` para comentário, criado por bootstrap com os 7 tokens fornecidos. Razão: usuário edita sem recompilar PowerShell; bootstrap dá o estado inicial; o arquivo serve como audit trail de "quem é considerado eu".
2. **Logar decisão de ativação no `statusMessage` do hook** (formato normativo: `auto-boot: owner=<owner-completo> match=<token>` quando allowlist match, `auto-boot: marker=<arquivo>` quando marker, ou `auto-boot: skipped (<motivo>)`). Razão: sem isso, o mantenedor não consegue diagnosticar "por que não ativou aqui?" sem rodar o script à mão. Custo: 1 linha de PowerShell.

## Implementação

### Arquivos criados/alterados na v1.8.0

Escopo enxuto após v1.7.1 (infra `~/.claude/hooks/` e `framework-sync.ps1` já existem):

| Arquivo | Mudança |
|---|---|
| `.claude/hooks/inject-start-session-global.template.ps1` (repo) | **NOVO** — fonte versionada do hook global. Variante do `inject-start-session.ps1` project-level que: (a) determina CWD via `$env:CLAUDE_PROJECT_DIR` ou `$PWD`; (b) tenta `git -C $cwd remote get-url origin`; (c) extrai owner via regex (HTTPS `github.com/owner/repo` e SSH `git@host:owner/repo`); (d) lê `~/.claude/squad-owners.txt`; (e) substring match case-insensitive do owner contra cada token; (f) **OR**: `Test-Path $cwd/AGENTS.md` OU `$cwd/.agent`; (g) respeita `.claude/session.lock` (projeto) e `~/.claude/session.lock` (global); (h) se ACTIVATE: injeta `additionalContext` lendo de `~/.claude/skills/pmo/start-session.md` ou fallback `~/.claude/skills/_shared/.../start-session.md`; (i) `statusMessage` com decisão (`owner-allowlist` / `marker` / `project-lock` / `global-lock` / `no-match-no-marker`). |
| `.claude/hooks/sync-global.ps1` (repo) | **ESTENDIDO** — adiciona 1 cópia: `.claude/hooks/inject-start-session-global.template.ps1` → `~/.claude/hooks/inject-start-session-global.ps1`. Mantém todo o resto da v1.7.1. |
| `bootstrap.ps1` | **ESTENDIDO** — adiciona passo "7. Configurar auto-boot global": (a) cria `~/.claude/squad-owners.txt` com tokens default se ausente (NÃO sobrescreve se já existe — respeita customização); (b) faz merge não-destrutivo de `hooks.SessionStart` em `~/.claude/settings.json` se ausente (preserva `permissions`, `enabledPlugins`, `autoUpdatesChannel` — backup `.modeswap.bak`-style antes do merge); (c) rodada inicial: invoca `sync-global.ps1` do repo recém-clonado para popular `~/.claude/hooks/inject-start-session-global.ps1`. |
| `bootstrap.sh` | **ESTENDIDO** — paridade do passo 7 em Bash (subset: cria `squad-owners.txt`; PowerShell em si só roda em Windows, mas o setup do destino é cross-platform). |
| `~/.claude/squad-owners.txt` | **NOVO** (criado por bootstrap, não versionado) — uma linha por token. Default inicial: `fpsouza`, `fpsouz`, `fsouza`, `fabriciosouza`, `fabriciopsouza`, `vibraenergia`, `natulab`. Comentários com `#`. |
| `~/.claude/settings.json` | **ESTENDIDO via bootstrap** — chave `hooks.SessionStart` com 1 grupo contendo o `inject-start-session-global.ps1`. Preserva `permissions` (modo `avancado` ativo da v1.7.1), `enabledPlugins`, `autoUpdatesChannel`. |
| `CHANGELOG.md` | Bloco v1.8.0 (MINOR — feature nova compatível). |
| `CLAUDE.md` (raiz) + `AGENTS.md` (raiz) | Seção "Auto-boot global" curta com critérios de ativação + ponteiro para `~/.claude/squad-owners.txt`. |

**Total:** 6 arquivos no escopo da v1.8.0 (3 no repo + 3 no global instalados via bootstrap+sync). Vs versão original do ADR (escopo coordenado): −3 arquivos por extração da infra `~/.claude/hooks/` para a v1.7.1.

### Algoritmo de decisão do hook global (resumo)

```
1. Determinar CWD: $env:CLAUDE_PROJECT_DIR ?? $PWD
2. Se ~/.claude/session.lock existe → SKIP (kill switch global)
3. Se $CWD/.claude/session.lock existe → SKIP (kill switch por projeto)
4. Tentar git -C $CWD remote get-url origin
5. Se ok → extrair owner via regex; ler ~/.claude/squad-owners.txt; substring match case-insensitive
6. Se match → ACTIVATE (motivo: "owner-allowlist")
7. Senão → testar $CWD/AGENTS.md e $CWD/.agent → se existir → ACTIVATE (motivo: "marker")
8. Senão → SKIP (motivo: "no-match-no-marker")
9. Em ACTIVATE: ler ~/.claude/skills/.../start-session.md, montar additionalContext, emitir JSON, statusMessage formato OBRIGATÓRIO `auto-boot: owner=<owner-completo> match=<token>` (allowlist) ou `auto-boot: marker=<arquivo>` — owner completo permite detectar falso positivo de substring (qa-critic round 1, C6)
10. Em SKIP: additionalContext vazio, statusMessage formato `auto-boot: skipped (owner=<owner-completo>, sem match)` ou `skipped (<motivo>)`
11. Qualquer erro → falha soft, warning em stderr, exit 0
```

### Convivência com ADR-004 (hook project-level do mesmo repo-framework)

O `.claude/settings.json` deste repo continua tendo seu hook `inject-start-session.ps1` project-level — **não removido**. Razão: redundância benigna. Quando este repo é aberto:

- Hook global dispara primeiro (owner=fabriciopsouza match=fpsouza → ACTIVATE).
- Hook project dispara depois (sem lock → ACTIVATE).
- Os dois retornam `additionalContext` com conteúdo idêntico (mesma fonte `start-session.md`).
- Claude Code concatena ambos no contexto — duplicação inofensiva.

Alternativa de remover o hook project-level foi rejeitada: introduzir ordem de implementação ("aplicar ADR-006 antes de ADR-007 que remove o project-level") gera fricção. Quem clona o repo-framework e ainda não rodou bootstrap.ps1 perde o auto-boot. Manter project-level garante funcionamento em **qualquer ordem de bootstrap**.

Cleanup do hook project-level fica como follow-up opcional (ADR-007 candidato), depois que o global estiver provadamente robusto em 2-3 PCs.

> **Atualização 2026-05-27:** follow-up implementado via guard (commit `cd0bc3e`), não por remoção — o hook de projeto faz `exit 0` quando `~/.claude/hooks/inject-start-session-global.ps1` existe, preservando o caso pré-bootstrap (qualquer ordem) que motivou a não-remoção em L108. Gatilho antecipado por observação em campo; sem ADR próprio (§0 — fix trivial).

### Convivência com ADR-005 (gate de modos de execução)

Gap do ADR-005 já foi resolvido em v1.7.1 (PR #7). O `check-execution-mode.ps1` do projeto-framework continua sendo o que monitora hash — não é promovido ao global neste ADR. Razão: o gate de modos é decisão sobre **permissões da IA**, que faz sentido reconfirmar quando o **mecanismo de sync** muda; faz menos sentido reconfirmar quando o usuário abre projeto qualquer.

Promover `check-execution-mode.ps1` para global é decisão futura (ADR-008 candidato), depois que a base de PCs/projetos justifique.

**Nota operacional:** modo `avancado` foi ativado em 2026-05-27. A v1.8.0 deste ADR-006 vai modificar `framework-sync.ps1` (estensão para também copiar o `inject-start-session-global.template.ps1`) — isso muda o hash do hook → dispara `HOOK_CHANGED` → mantenedor será prompted para reconfirmar `avancado` ou escalar para `autosuficiente`. Validação orgânica do ratchet do ADR-005.

### Como o usuário usa

- **Repos do mantenedor** (`github.com/fabriciopsouza/foo`, `github.com/vibraenergia/dashboards`, etc.): auto-boot dispara automaticamente em qualquer IDE com este `~/.claude/` instalado. Zero configuração por projeto.
- **Repo de terceiro com colaboração ativa** (`github.com/anthropics/claude-code`, etc.): criar `AGENTS.md` ou pasta `.agent/` na raiz local → próximas sessões ativam. Reversível: deletar.
- **Pular sessão única em repo seu:** `New-Item .claude/session.lock` na raiz do repo.
- **Pular tudo globalmente** (todas as sessões em todos os repos): `New-Item ~/.claude/session.lock`. Apagar para reativar.
- **Adicionar novo handle/org à allowlist:** editar `~/.claude/squad-owners.txt`, adicionar linha. Imediato (próxima sessão).
- **Diagnóstico** ("por que não ativou aqui?"): olhar `statusMessage` na barra de status do Claude Code — mostra owner extraído e decisão.

## Consequências

### Positivas

1. **Default ON onde faz sentido.** Squad ativo em todo repo do mantenedor sem configuração por-projeto.
2. **Default OFF onde não faz sentido.** Repos de terceiros clonados para estudo entram limpos.
3. **Override granular.** 3 níveis: edição da allowlist (persistente), marker no projeto (persistente, por projeto), lock file (efêmero, sessão única).
4. **Audit trail explícito.** `squad-owners.txt` é o registro canônico de "quem é considerado eu". `statusMessage` registra a decisão por sessão.
5. **Compatibilidade retroativa.** Hook project-level do ADR-004 não é removido; redundância benigna. Quem clona o repo continua tendo auto-boot mesmo antes de rodar `bootstrap.ps1`.
6. **Multi-PC simplificado.** Bootstrap idempotente; setup em PC novo: `pwsh bootstrap.ps1` → próxima sessão funciona.
7. **Reusa infra v1.7.1.** Escopo enxuto: `~/.claude/hooks/` já existe; só adiciona 1 hook novo e 1 config.

### Negativas

1. **2 arquivos a mais no global** (`hooks/inject-start-session-global.ps1`, `squad-owners.txt`). Manutenção aceitável — ambos têm fonte versionada (template do hook) ou são config simples (allowlist).
2. **Mais um ponto de falha silencioso.** Se o hook global falhar antes de extrair owner (PowerShell bloqueado, regex match vazio), nenhuma ativação acontece. Mitigação: `statusMessage` mostra estado; teste manual via `pwsh ~/.claude/hooks/inject-start-session-global.ps1` reproduz.
3. **Setup inicial dependente de ordem.** Em PC novo: bootstrap.ps1 precisa rodar antes da primeira sessão útil. Mitigação: README/SETUP enfatiza a sequência; bootstrap é idempotente.
4. **Substring match pode dar falso positivo.** Owner contendo "fsouza" como substring (improvável mas possível) ativaria indevidamente. Mitigação: tokens são específicos; mantenedor edita allowlist removendo tokens genéricos se aparecer caso real.

### Riscos

1. **`squad-owners.txt` perdido em backup/migração.** Sem o arquivo, hook só ativa por marker. Mitigação: bootstrap recria com defaults; arquivo é claramente nomeado.
2. **`additionalContext` duplicado** quando hook global + hook project-level disparam no mesmo repo. Em tese inofensivo (mesmo conteúdo), mas infla system prompt em ~30 linhas. Mitigação: aceitável a curto prazo; cleanup do project-level vira ADR-007 candidato após validação multi-PC.
3. **Mudança no formato do `additionalContext`** (ex.: nova versão do start-session.md) não propaga automaticamente para o global em PCs que não abriram o repo-framework recentemente. Mitigação: sync-global roda em toda sessão do repo-framework; só PCs que nunca abriram o repo ficam atrás. Bootstrap valida com `git pull`.
4. **PowerShell-only.** Hook global, bootstrap, e regex de extração de owner são PowerShell. Linux/macOS precisará versão `.sh` análoga. Já é constraint conhecido do framework (ADR-001/004/005). Porte cross-platform fica para ADR de cross-platform futuro.
5. **Conflito com `permissions` em `~/.claude/settings.json` existente.** O merge não-destrutivo do bootstrap pode ser frágil se o usuário tiver estrutura customizada. Mitigação: backup `.modeswap.bak`-style antes do merge (paridade com ADR-005).
6. **Dependência implícita de `$env:USERPROFILE` estático** (qa-critic round 1, C5). Em ambientes com múltiplos perfis Windows, SSO empresarial que troca USERPROFILE, ou cópias entre máquinas, o path `~/.claude/squad-owners.txt` não é encontrado e o hook cai silenciosamente para marker-only. Mitigação: `statusMessage` mostra `skipped (allowlist missing)`; SETUP documenta que o path assume `$env:USERPROFILE` estático.
7. **Divergência de conteúdo entre hook global e project-level** (qa-critic round 1, C8). A premissa "mesmo `additionalContext`" só vale após sync recente. Se um PC ficou meses sem abrir o repo-framework, `~/.claude/skills/.../start-session.md` pode divergir do `.agent/workflows/start-session.md` do projeto; os dois `additionalContext` chegam sem critério de desambiguação. Mitigação: `sync-global.ps1` roda em todo SessionStart no repo-framework — abrir o repo regularmente fecha a janela. Cleanup do project-level (ADR-007 candidato) eliminaria o vetor.

## Implementação (ponteiro após aceito)

- **Ponteiro:**
  - Branch: `feat/auto-boot-global-v180` (a criar pelo developer)
  - Data: 2026-05-26 (proposta)
  - Grep para localizar implementação: `git log --all --grep "v1.8.0" --grep "auto-boot-global"`
- **Hash de commit:** opcional como complemento — NUNCA único (lição ADR-001 / ADR-003).
- **Validação (test plan para o developer):**
  > **Pré-requisito:** branch `feat/auto-boot-global-v180` implementada (bootstrap.ps1 com passo 7, hook template `.claude/hooks/inject-start-session-global.template.ps1` criado, sync-global.ps1 estendido). Test plan NÃO é executável antes da implementação — passo #1 falha por definição se rodado contra bootstrap.ps1 atual (que termina no passo 6). Lição registrada pelo qa-critic round 1 (adversarial extra).

  1. **Bootstrap em PC limpo:** rodar `pwsh bootstrap.ps1` em VM/container sem `~/.claude/`. Verificar: `~/.claude/squad-owners.txt`, `~/.claude/settings.json` com hook SessionStart, `~/.claude/hooks/inject-start-session-global.ps1`, `~/.claude/skills/` populado. Abrir Claude Code em diretório qualquer sem remote → SKIP (`no-match-no-marker`). Abrir em diretório com remote do mantenedor → ACTIVATE.
  2. **Allowlist match:** clonar `github.com/fabriciopsouza/foo`; abrir sessão → `statusMessage` mostra `owner=fabriciopsouza match=fpsouza`; Claude ativa PMO.
  3. **Owner não-match:** clonar `github.com/anthropics/claude-code`; abrir sessão → `statusMessage` mostra `skipped (owner=anthropics, sem match)`; Claude entra livre.
  4. **Marker fallback:** num repo sem remote/de terceiro, `New-Item AGENTS.md`; abrir sessão → `statusMessage` mostra `marker=AGENTS.md`; Claude ativa PMO.
  5. **Lock global:** `New-Item ~/.claude/session.lock`; abrir sessão em repo do mantenedor → SKIP (`global-lock`). Deletar → próxima ativa.
  6. **Lock por projeto:** num repo do mantenedor, `New-Item .claude/session.lock`; abrir sessão → SKIP (`project-lock`). Deletar → próxima ativa.
  7. **Idempotência:** rodar `bootstrap.ps1` duas vezes; `squad-owners.txt` customizado não é sobrescrito; `~/.claude/settings.json` não duplica hook.
  8. **Falha soft:** renomear `~/.claude/squad-owners.txt` para `.bak`; abrir sessão → hook não trava; `statusMessage` mostra `skipped (allowlist missing)`; cai para teste de marker.
  9. **Coexistência com modo `avancado`** (ratchet ADR-005): após primeira sessão pós-v1.8.0, `check-execution-mode` dispara `HOOK_CHANGED` (hash do `framework-sync.ps1` mudou — agora copia também o template do auto-boot global). Reconfirmar `avancado` ou escalar.

## Pendências e follow-ups

- **ADR-007 candidato:** remover o hook `inject-start-session.ps1` project-level do repo-framework após v1.8.0 estabilizar em ≥2 PCs (eliminar redundância).
- **ADR-008 candidato:** promover `check-execution-mode.ps1` para global, caso a base justifique (vários PCs entrando em modos diferentes).
- **ADR cross-platform:** porte `.sh` de toda a cadeia de hooks. Quando houver caso de uso real (mantenedor em macOS/Linux).
- **Vigiar:** falsos positivos da substring match em allowlist. Se aparecer caso real, refinar regra (match em fronteira de palavra, ou exact-match opcional).

## Referências

- Script global a criar: `~/.claude/hooks/inject-start-session-global.ps1` (fonte versionada em `.claude/hooks/inject-start-session-global.template.ps1`)
- Config global a criar: `~/.claude/squad-owners.txt`
- Settings global a estender: `~/.claude/settings.json`
- Bootstrap a estender: [`bootstrap.ps1`](../../bootstrap.ps1) · [`bootstrap.sh`](../../bootstrap.sh)
- Infra reusada (v1.7.1): `~/.claude/hooks/` + `~/.claude/hooks/framework-sync.ps1`
- ADR-001 (sync-global hook original) · ADR-004 (auto-boot project-level) · ADR-005 (modos de execução; gap resolvido em v1.7.1)
- `_shared/traceability` (audit trail) · `_shared/high-stakes-gate` (escalonamento)
- Glossário: termos `owner`, `allowlist`, `marker`, `lock` a serem adicionados em `.agent/rules/00-glossario.md` na implementação
