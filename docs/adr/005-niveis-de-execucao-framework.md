# ADR 005 — Níveis de execução do framework (default / avançado / autosuficiente) com ratchet por hash de hook

- **Status:** Aceito (2026-05-26 — pelo mantenedor; aplicado em v1.7.0)
- **Data:** 2026-05-26 · **Decisores:** Fabricio (mantenedor) + Claude (papel `architect`)
- **Substitui:** nenhum · **Substituído por:** nenhum
- **Relaciona-se a:** ADR-001 (sync-global hook), ADR-004 (auto-boot do squad), `_shared/high-stakes-gate`, `_shared/traceability`

## Contexto

Até a v1.6.x, o framework opera sob um único nível de permissões: aquilo que o usuário deixa em `~/.claude/settings.json`. Conforme o mantenedor amadurece o uso, surgem três regimes operacionais diferentes — cada um com tradeoff próprio entre **fricção** e **autonomia da IA**:

1. **Conservador** — quase tudo pergunta. Apropriado para trabalho em produção, mudanças irreversíveis, ambiente regulado.
2. **Avançado** — confia no shell em geral, pede confirmação só em operações que afetam outros (push, merge, PR). Apropriado para desenvolvimento ativo em projeto pessoal/equipe pequena.
3. **Autosuficiente** — `bypassPermissions` para tudo exceto guard-rails absolutos. Apropriado para ciclos de iteração intensa, experimentação isolada, automação noturna.

Hoje o usuário transita entre regimes editando settings.json à mão. Isso produz três problemas:
- **Estado oculto:** ninguém (nem ele, nem o Claude) sabe em que regime está. O nível é "o que está no JSON agora".
- **Sem ratchet:** pode descer acidentalmente para autosuficiente em sessão errada e nunca perceber.
- **Sem trigger de revisão:** se o framework atualiza o hook que controla auto-sync, o usuário continua no mesmo regime sem ser convidado a reconsiderar — apesar de a base de confiança ter mudado.

Mantenedor pediu (2026-05-26): incorporar esses regimes como **segundo nível de execução do framework**, ativados explicitamente uma vez ao sync-com-repo, reconfirmados a cada update de hook, com semântica forward-only.

## Decisão (1 frase ativa)

Introduzir três **níveis de execução** explícitos (`default` / `avançado` / `autosuficiente`) com templates declarativos em `_shared/execution-modes/`, estado persistido em `~/.claude/framework-mode.json`, hook `check-execution-mode.ps1` que dispara reativação somente quando o estado é ausente OU o SHA-256 de `~/.claude/hooks/framework-sync.ps1` muda, semântica de **ratchet forward-only no fluxo normal** (escalação livre default→avançado→autosuficiente; downgrade apenas via edição manual do `framework-mode.json` — escape de segurança).

## Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **3 modos + ratchet + hash-trigger (escolhida — Opção C da elicitação)** | Estado explícito e auditável. Trigger só quando faz sentido (hook mudou). Ratchet evita downgrade acidental. Escape manual existe para reverter foot-gun. Templates são SSoT do framework, não snowflake por usuário. | 4 arquivos novos (3 templates + 1 hook). Lock-in do PowerShell (já compartilhado com ADR-001/004). State file pode dessincronizar se o usuário editar settings.json à mão sem usar o ativador. |
| 2 | Slash command `/mode <nome>` sem trigger automático | Mais simples: zero hook novo, só um workflow. | Sem trigger, depende de memória do usuário (mesmo problema do `/start-session` antes do ADR-004). Quando o framework muda o hook, ninguém reconsidera o nível. |
| 3 | Prompt em todo SessionStart | Visibilidade máxima do regime ativo. | Fricção alta — o usuário pediu explicitamente para evitar isso. Prompt vira ruído. |
| 4 | Modo permanente único (status quo) | Zero código. | Não resolve o pedido. Mantém o estado oculto. |
| 5 | Modos por-projeto (cada `.agent/.mode-state.json`) | Granularidade. Cada projeto decide seu nível. | Para single-user dev na mesma máquina é over-engineering. Custo de manutenção 3× sem ganho real. Pode entrar em v2.x se a base de projetos crescer. |
| 6 | Trigger por hash do HEAD do repo | Vigilância máxima — qualquer pull dispara reconfirmação. | "Praticamente todo início de sessão" — exatamente o cenário de fricção que o mantenedor quis evitar na elicitação. |

## Justificativa

A escolha do mantenedor (Opção C, validada por elicitação em 4 dimensões) combina três princípios já presentes no núcleo:

- **`_shared/traceability`**: o framework-mode.json é o registro auditável do regime. Sem isso, "qual modo estou?" não tem resposta canônica.
- **`_shared/high-stakes-gate`**: subir para `autosuficiente` é decisão de alto risco — deve ser explícita, registrada, e reconfirmada quando a base muda (hook atualizado).
- **ADR-004 (auto-boot)**: paridade arquitetural — `/start-session` já é injetado via `additionalContext`. O check de modo segue o mesmo padrão, no mesmo SessionStart, antes do inject (modo determina permissões; permissões determinam o que o boot pode fazer).

O hash de `framework-sync.ps1` (e não do repo HEAD) foi escolhido porque o wrapper local muda **raramente, intencionalmente** — só em release que afeta a cadeia de sync. Re-confirmar quando esse wrapper muda é coerente: a base de confiança da automação genuinamente mudou; vale revisitar o regime. Já o HEAD muda a cada `git pull`, frequência muito maior que a janela em que o regime de confiança realmente se altera.

**Ratchet forward-only no fluxo normal** vem da observação de que o tempo correto para descer um modo é "calmo, pensado, em zero pressão" — ou seja, edição manual do state file. Permitir downgrade automático cria um vetor para o Claude (ou um hook futuro) reduzir o regime sem o usuário perceber. O escape manual via editor preserva a possibilidade sem normalizá-la.

## Implementação

### Arquivos criados/alterados na v1.7.0

| Arquivo | Mudança |
|---|---|
| `_shared/execution-modes/SKILL.md` | **NOVO** — entry point: descreve os 3 modos, semântica de ratchet, regra de hash-trigger, formato do state file, algoritmo de aplicação. Carregado quando a ativação dispara. |
| `_shared/execution-modes/default.json` | **NOVO** — template do modo conservador. Allow só de Read/Edit/Write; ask para git push/merge/pr; deny destrutivo robusto (20 regras). `defaultMode: default`. |
| `_shared/execution-modes/avancado.json` | **NOVO** — template do modo avançado. Allow + bare `Bash`/`PowerShell`; mesmo ask + deny do default. `defaultMode: default`. |
| `_shared/execution-modes/autosuficiente.json` | **NOVO** — template do modo autosuficiente. `defaultMode: bypassPermissions`. Allow blanket. Deny mínimo (guard-rails absolutos: `git push --force`, `Format-Volume`, `mkfs`). |
| `.claude/hooks/check-execution-mode.ps1` | **NOVO** — hook SessionStart. Computa SHA-256 do framework-sync.ps1, lê framework-mode.json, emite `additionalContext` se hash mudou OU estado ausente. Falha "soft" (exit 0 silencioso em erro). |
| `.claude/settings.json` | **Restruturado** de 1 grupo SessionStart com 2 hooks (v1.6.1) para **3 grupos paralelos** com 1 hook cada — preserva isolamento de `additionalContext` (qa-critic round 1, B1: dentro de um mesmo grupo, hooks sequenciais podem disputar a chave `hookSpecificOutput.additionalContext`; grupos separados garantem que cada `additionalContext` chegue concatenado ao modelo). Ordem dos grupos: `sync-global.ps1` → `check-execution-mode.ps1` → `inject-start-session.ps1`. Justificativa: sync primeiro (estado dos arquivos espelhado), check depois (modo decide permissões), inject por último (boot opera sob o modo já decidido). |
| `CLAUDE.md` (raiz) | Seção "Modos de execução" com tabela das 3 opções e ponteiro para `_shared/execution-modes/`. |
| `AGENTS.md` (raiz) | Mesma menção, formato cross-tool. |
| `CHANGELOG.md` | Bloco v1.7.0 (MINOR — feature nova compatível). |

### Estado persistido (`~/.claude/framework-mode.json`)

Esquema:
```json
{
  "mode": "default | avancado | autosuficiente",
  "hookSha256": "<sha256 do framework-sync.ps1 no momento da ativação>",
  "activatedAt": "<ISO 8601>",
  "history": [
    { "mode": "<modo>", "at": "<ISO>", "fromMode": "<anterior>", "reason": "INITIAL|HOOK_CHANGED|MANUAL" }
  ]
}
```

### Algoritmo de ativação (resumo — algoritmo canônico está no SKILL.md)

> **Nota:** este é resumo. O algoritmo canônico, com todos os passos (backup, validação, rollback, regra anti-downgrade binding), está em `_shared/execution-modes/SKILL.md` seção "Algoritmo de aplicação". Em caso de divergência, SKILL.md vence.

1. **Ler state file** (se existir) — determinar `currentMode` e `reason` (INITIAL/HOOK_CHANGED).
2. **Perguntar ao usuário** via `AskUserQuestion` qual modo ativar, respeitando ratchet.
3. **Aplicar ratchet:** sem opções de downgrade — `default→avancado`, `avancado→autosuficiente`, ou confirmar atual.
4. **Backup obrigatório:** `~/.claude/settings.json` → `.modeswap.bak` antes do merge.
5. **Ler o template** do modo escolhido em `~/.claude/skills/execution-modes/<modo>.json`.
6. **Merge ao settings.json global:**
   - Substituir: `permissions.allow`, `permissions.ask`, `permissions.deny`, `permissions.defaultMode`.
   - Preservar: `permissions.additionalDirectories`, `hooks`, `enabledPlugins`, `autoUpdatesChannel`, qualquer outra chave.
   - Validar com `ConvertFrom-Json` antes de gravar; se inválido, restaurar do .bak.
7. **Gravar state file** com SHA-256 atual, modo, timestamp, e append em `history`.
8. **Confirmar ao usuário:** "Modo X ativado. Backup em .modeswap.bak. Próxima reconfirmação só quando framework-sync.ps1 mudar."

### Como o usuário usa

- **Default operacional:** ao instalar o framework pela primeira vez (state file ausente), próxima sessão dispara ativação. Usuário escolhe entre os 3.
- **Update do framework que toca o hook:** próxima sessão dispara reconfirmação. Usuário confirma o modo atual OU escala.
- **Sessões normais:** check é silencioso (hash bate, estado existe). Zero fricção.
- **Downgrade emergencial:** editar `~/.claude/framework-mode.json` manualmente (trocar `mode`) + editar `~/.claude/settings.json` ou rodar o ativador novamente em sessão limpa. Não é caminho normalizado.

### Como pular o check pontualmente

Não há flag de escape para o check em si — ele é silencioso quando não há trigger. Se precisar pular para sessão única, o lock do ADR-004 (`.claude/session.lock`) pula APENAS o `inject-start-session.ps1` (auto-boot do squad); o check de modo continua. Para pular ambos, o caminho é remover o hook do settings.json — não recomendado.

## Consequências

### Positivas

1. **Estado explícito e auditável.** "Qual modo estou?" tem resposta canônica em `framework-mode.json`. `history` registra escalações.
2. **Trigger inteligente.** Reconfirmação só quando a base de confiança muda (hook atualizado) — não em toda sessão.
3. **Ratchet protege contra downgrade silencioso.** Movimento descendente exige edição manual deliberada.
4. **Templates são SSoT do framework.** Quem clona o repo herda os 3 modos sem snowflake. Mudança no template propaga via `sync-global.ps1`.
5. **Paridade arquitetural com ADR-004.** Mesmo padrão de `additionalContext` no SessionStart; cadeia de hooks linear e legível.
6. **Escape de segurança existe.** Edição manual permite reverter foot-gun de `autosuficiente` acidental. Não normalizado, mas possível.

### Negativas

1. **State file pode dessincronizar.** Se o usuário editar `~/.claude/settings.json` à mão (e não via ativador), `framework-mode.json` mente sobre o regime real. Mitigação parcial: SKILL.md do execution-modes pede ao Claude para validar settings vs state em sessões críticas. Total não dá — não vamos hashear settings.json (mudaria toda sessão).
2. **Mais 5 arquivos no núcleo.** 1 SKILL.md + 3 templates + 1 hook. Manutenção: aceitável, são arquivos estáveis (mudanças são raras).
3. **Lock-in PowerShell.** Hook só funciona em Windows. Já é constraint conhecido do framework (ADR-001, ADR-004). Porte para `.sh` fica pra um ADR de cross-platform.
4. **Sem suporte por-projeto.** Modo global, não por-projeto. Para o uso atual (single-user, vários projetos seguindo o mesmo regime) é o ponto certo. Se a base de projetos crescer, alternativa #5 vira candidata real.

### Riscos

1. **Usuário escala para `autosuficiente` e esquece.** Trabalho em produção pode rodar com `bypassPermissions`. Mitigação: `framework-mode.json` é visível no `~/.claude/` e `statusMessage` do hook mostra o modo na barra de status (a definir).
2. **Hook silencioso por erro.** Se o `check-execution-mode.ps1` falhar antes de calcular hash (PowerShell bloqueado, file ACL ruim), nunca dispara reativação. Mitigação: falha "soft" com warning em stderr, mas como o SessionStart hook output é mostrado, o stderr aparece pro usuário.
3. **History cresce indefinidamente.** Pequeno (poucas escalações na vida do usuário), mas eventualmente pode inflar. Truncar últimas 50 entradas no ativador.
4. **Conflito com `parentSettingsBehavior` / managed settings.** Se o usuário usar policy/admin tier (`policySettings`), o merge precisa respeitar precedence. Hoje não usa; vigiar.

## Implementação (ponteiro após aceito)

- **Ponteiro:**
  - Branch: `feat/execution-modes-v170` (mergeada em main via PR #6 em 2026-05-26)
  - Data: 2026-05-26 (aplicado em série pós-ADR)
  - Grep para localizar implementação: `git log --all --grep "v1.7.0" --grep "execution-modes"`
- **Hash de commit:** opcional, NUNCA único (lição ADR-001 / ADR-003).

### Pós-merge — defeito de execução detectado e corrigido (v1.7.1 / 2026-05-27)

A v1.7.0 mergeou com um **gap de execução**: o `check-execution-mode.ps1`
referencia `~/.claude/hooks/framework-sync.ps1` (linha 18), mas nenhum
arquivo da v1.7.0 cria esse destino — nem o `sync-global.ps1` (que só
espelhava `_shared/`, `.agent/skills/`, `.claude/agents/`), nem o
bootstrap. Resultado em campo: hook caiu sempre no branch
`Test-Path $hookFile = $false` → exit silencioso → **gate de modos
ficou dormente desde o merge**.

Auditoria 2026-05-27 (sessão "retome adr005, finalize") confirmou em PC ativo
do mantenedor: `~/.claude/hooks/` não existia, `framework-mode.json` ausente,
nenhum modo ativado desde 2026-05-26. A decisão arquitetural deste ADR está
correta; faltou o vínculo entre fonte (project-level) e instância instalada
(global-level).

**Fix aplicado em v1.7.1** (branch `fix/adr-005-framework-sync-gap`):
`.claude/hooks/sync-global.ps1` passa a também criar `~/.claude/hooks/` e
copiar a si mesmo (via `$MyInvocation.MyCommand.Path`) para
`~/.claude/hooks/framework-sync.ps1` — rolling overwrite idempotente. Nome
diferente é deliberado: `sync-global.ps1` é o **fonte** versionado;
`framework-sync.ps1` é a **instância instalada** no global. Par fonte/binário,
não rename (regra anti-rename não acionada).

**Lição:** ADRs aceitos precisam de validação em campo (ao menos uma
ativação real) **antes** que features dependentes empilhem em cima. A
sessão imediatamente seguinte ao merge da v1.7.0 começou a desenhar
o ADR-006 — só o passo de "auditar estado real do `~/.claude/`" revelou
o gap. Critério de aceite de ADRs futuros: incluir 1 passo de
"validação operacional pós-merge" antes de marcar [CONFIRMADO].

### Estado pós-fix (v1.7.1, branch `fix/adr-005-framework-sync-gap`)

- **Gap:** RESOLVIDO. `~/.claude/hooks/framework-sync.ps1` é criado e mantido
  em sincronia pelo `sync-global.ps1` (cópia byte-a-byte rolling-overwrite).
- **qa-critic adversarial (3 rounds, subagente isolado):** APROVADO LIMPO no
  round 3. Round 1 e 2 produziram 4 ressalvas (1 médio + 1 médio derivado +
  2 baixos + 1 observação adversarial); todas incorporadas em código (médios)
  ou documentação (baixos + adversarial).
- **Ativação operacional:** modo `avancado` ativado pela primeira vez em
  2026-05-27T00:42-03:00 no PC do mantenedor, seguindo os 8 passos canônicos
  do `execution-modes/SKILL.md` (backup, template, merge validado, state
  file, confirmação). State file ativo. Gate agora satisfeito (silencioso até
  o hash do hook mudar).
- **Lição validada:** o defeito só apareceu porque uma sessão posterior fez
  auditoria casual — confirmou que "validação operacional pós-merge" deve
  virar passo formal do ciclo de release. Já registrado como memória de
  feedback `feedback-framework-integral` (2026-05-27).
- **Validação:**
  1. State ausente: deletar `~/.claude/framework-mode.json` (se existir) → abrir nova sessão → Claude deve receber `additionalContext` pedindo ativação → escolher um modo → settings.json muda + state file aparece.
  2. State presente, hash bate: abrir sessão normal → nenhum prompt de ativação → settings.json intocado.
  3. Hash muda: editar `framework-sync.ps1` (mudar um comentário) → abrir nova sessão → Claude deve receber `additionalContext` de reconfirmação com motivo HOOK_CHANGED.
  4. Tentativa de downgrade automático: estando em `autosuficiente`, ativador NÃO deve oferecer `default` ou `avancado` na lista de opções (só `autosuficiente` para confirmar).
  5. Downgrade manual: editar `framework-mode.json` à mão → próxima sessão respeita o novo modo registrado.

## Referências

- Templates: [`_shared/execution-modes/`](../../_shared/execution-modes/)
- Hook: [`.claude/hooks/check-execution-mode.ps1`](../../.claude/hooks/check-execution-mode.ps1)
- Hook irmão (sync mecânico): [`.claude/hooks/sync-global.ps1`](../../.claude/hooks/sync-global.ps1)
- Hook irmão (auto-boot cognitivo): [`.claude/hooks/inject-start-session.ps1`](../../.claude/hooks/inject-start-session.ps1)
- Settings do projeto: [`.claude/settings.json`](../../.claude/settings.json)
- CLAUDE.md (entrada): [`CLAUDE.md`](../../CLAUDE.md)
- ADR-001 (sync hook original) · ADR-004 (auto-boot do squad)
