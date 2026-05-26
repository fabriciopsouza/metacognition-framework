---
name: execution-modes
description: Núcleo SSoT dos 3 níveis de execução do framework (default · avançado · autosuficiente). Carregar quando o hook check-execution-mode emitir `additionalContext` pedindo ativação ou reconfirmação. Define os 3 modos, semântica de ratchet forward-only, formato do state file `~/.claude/framework-mode.json` e o algoritmo de aplicação (merge ao settings.json global). NÃO carregar em sessões normais — o hook é silencioso quando o modo está bem registrado.
metadata:
  type: shared
  version: 1.7.0
  adr: 005
---

# execution-modes — Níveis de execução do framework

Ponto de entrada para a **ativação/reconfirmação** de um dos 3 modos de execução do framework. Esta skill é carregada **apenas** quando o hook `check-execution-mode.ps1` injeta `additionalContext` no SessionStart pedindo ação — caso contrário, o framework opera silenciosamente sob o modo registrado.

## Os 3 modos (resumo executivo)

| Modo | `defaultMode` | Allow shell | Ask | Deny | Quando usar |
|---|---|---|---|---|---|
| **default** | `default` (prompts) | só Read/Edit/Write | git push/merge/pr | destrutivo robusto (20 regras) | trabalho em produção, mudança irreversível, ambiente regulado |
| **avançado** | `default` (prompts) | + bare Bash/PowerShell | git push/merge/pr | destrutivo robusto (20 regras) | desenvolvimento ativo, projeto pessoal/equipe pequena |
| **autosuficiente** | `bypassPermissions` | tudo | (ignorado) | mínimo (guard-rails absolutos) | ciclo de iteração intensa, experimentação isolada, automação noturna |

Templates declarativos: [`default.json`](default.json) · [`avancado.json`](avancado.json) · [`autosuficiente.json`](autosuficiente.json).

## Ratchet forward-only

A sequência permitida no fluxo normal é:

```
default → avançado → autosuficiente
```

- **Confirmar** o modo atual (mesmo modo) é sempre permitido.
- **Escalar** para o próximo nível é permitido.
- **Descer** (autosuficiente→avançado, avançado→default, autosuficiente→default) NÃO é oferecido pela UI do ativador. Caminho de saída: edição manual de `~/.claude/framework-mode.json`. Escape deliberado, não normalizado — protege contra Claude (ou hook futuro) reduzir o regime sem o usuário perceber.

## State file

Caminho canônico: `~/.claude/framework-mode.json` (global, fora do repo).

Esquema:
```json
{
  "mode": "default | avancado | autosuficiente",
  "hookSha256": "<sha256 do framework-sync.ps1 no momento da ativação>",
  "activatedAt": "<ISO 8601>",
  "history": [
    { "mode": "<modo>", "at": "<ISO>", "fromMode": "<anterior ou null>", "reason": "INITIAL | HOOK_CHANGED | MANUAL" }
  ]
}
```

`history` é truncado nas últimas 50 entradas pelo ativador.

## Trigger (quando o hook dispara)

`check-execution-mode.ps1` calcula SHA-256 de `~/.claude/hooks/framework-sync.ps1` em todo SessionStart e emite `additionalContext` **apenas quando**:

- `INITIAL` — `~/.claude/framework-mode.json` não existe (primeira instalação).
- `HOOK_CHANGED` — `state.hookSha256 != currentSha` (framework-sync.ps1 mudou desde a última ativação).

Nos demais casos, é silencioso (exit 0 sem output).

Justificativa: hash do wrapper local muda raramente e intencionalmente — coincide com o momento certo para revisar o regime de confiança. Hash do repo HEAD foi rejeitado por gerar fricção em toda sessão.

## Algoritmo de aplicação (executado pelo Claude após receber `additionalContext`)

1. **Ler o state file** (se existir): `~/.claude/framework-mode.json`. Determinar `currentMode` e `reason` (INITIAL ou HOOK_CHANGED).

2. **Perguntar ao usuário** via `AskUserQuestion` qual modo ativar. Mostrar:
   - Motivo do trigger.
   - Modo atual (ou "nenhum" se INITIAL).
   - Opções respeitando o ratchet:
     - INITIAL → 3 opções (default, avançado, autosuficiente).
     - currentMode = default → 2 opções (default-confirmar, avançado-escalar).
     - currentMode = avançado → 2 opções (avançado-confirmar, autosuficiente-escalar).
     - currentMode = autosuficiente → 1 opção (autosuficiente-confirmar).

3. **Ler o template** do modo escolhido em `~/.claude/skills/execution-modes/<modo>.json` (sincronizado pelo `sync-global.ps1`). Fallback para `~/.claude/projects/<repo>/_shared/execution-modes/<modo>.json` se necessário.

4. **Backup ANTES do merge** (passo obrigatório, não pular):
   - Antes de qualquer escrita, copiar `~/.claude/settings.json` → `~/.claude/settings.json.modeswap.bak` (sobrescreve qualquer .bak anterior — é rolling).
   - Se a cópia falhar (ACL ruim, disco cheio), **abortar a ativação** e avisar o usuário — não prosseguir sem ponto de retorno.

5. **Merge ao `~/.claude/settings.json`** (global):
   - **Substituir:** `permissions.allow`, `permissions.ask`, `permissions.deny`, `permissions.defaultMode`.
   - **Preservar:** `permissions.additionalDirectories`, `hooks`, `enabledPlugins`, `autoUpdatesChannel`, qualquer outra chave existente.
   - **Validar** com `ConvertFrom-Json` o JSON novo ANTES de sobrescrever o arquivo. Se inválido: abortar, restaurar do `.modeswap.bak`, avisar.
   - **Rollback path:** se Claude Code recusar a sessão pós-update, instruir usuário: `Move-Item ~/.claude/settings.json.modeswap.bak ~/.claude/settings.json -Force` (note: `Remove-Item` está em deny no avançado/default — usar `Move-Item` ou edição manual).

6. **Gravar `~/.claude/framework-mode.json`** com:
   - `mode` = modo escolhido.
   - `hookSha256` = SHA-256 atual do `~/.claude/hooks/framework-sync.ps1`.
   - `activatedAt` = ISO 8601 do agora.
   - `history` = (history anterior, se existir) + nova entrada `{mode, at, fromMode, reason}`. Truncar nas últimas 50.

7. **Confirmar ao usuário** com uma frase: "Modo `<X>` ativado. Backup em `~/.claude/settings.json.modeswap.bak`. Próxima reconfirmação só quando `framework-sync.ps1` mudar."

8. **Avisar sobre reload:** mudanças no `settings.json` global podem precisar de reload do Claude Code para `defaultMode` entrar em efeito. Permissões individuais (allow/deny/ask) são re-lidas em runtime na próxima invocação de tool.

## Regra anti-downgrade (binding, não advisory)

Mesmo se o usuário **pedir explicitamente** "me mostre a opção default" ou "quero descer para avançado", o Claude operando o ativador NÃO pode oferecer downgrade no `AskUserQuestion`. Resposta canônica: *"Downgrade via ativador não é caminho normalizado (ratchet forward-only do ADR-005). Para descer: edite `~/.claude/framework-mode.json` à mão, troque o campo `mode`, e abra nova sessão — o trigger HOOK_CHANGED não dispara só por isso, então edite também o `hookSha256` para um valor sentinela tipo `MANUAL_DOWNGRADE` que forçará reativação."* Isso protege contra o próprio Claude (lendo um prompt persuasivo) executar downgrade automaticamente.

## Falhas conhecidas e mitigações

- **Corrupção de settings.json no merge:** se a gravação falhar (escape errado, truncamento), Claude Code pode recusar todas as sessões. Mitigação obrigatória: backup `~/.claude/settings.json.modeswap.bak` antes do merge (passo 4 do algoritmo); validar JSON antes de sobrescrever.
- **State drift:** se o usuário editar `~/.claude/settings.json` à mão e bypassar o ativador, `framework-mode.json` mente sobre o regime real. Em sessões de alto risco, validar manualmente (`Get-Content ~/.claude/settings.json`) antes de operar.
- **Hook silencioso por erro:** se `check-execution-mode.ps1` falhar (PowerShell bloqueado, ACL ruim), nunca dispara. Verificar `~/.claude/hooks/check-execution-mode.ps1` existe e roda manualmente.
- **Reload tardio:** `defaultMode: bypassPermissions` aplicado em sessão ativa não vale para a sessão corrente — vale a partir da próxima abertura. O ativador deve avisar.
- **Crossover Bash↔PowerShell:** `deny PowerShell(Format-Volume:*)` **não** bloqueia `Bash(powershell.exe -Command Format-Volume ...)` — o matcher casa pelo nome do tool. Em `autosuficiente` (bypassPermissions), isso significa que o Claude pode executar cmdlets bloqueados via `powershell.exe` chamado por Bash sem prompt. Mitigação parcial: adicionar pareados `Bash(powershell.exe:*Format-Volume:*)` é frágil (matcher é prefix-only). Tratar como limitação conhecida; reduzir o vetor evitando `autosuficiente` em produção.

## Relações

- `[[traceability]]` — state file é audit trail do regime.
- `[[high-stakes-gate]]` — escalar para `autosuficiente` é decisão de alto risco; aplicar critério.
- `[[anti-hallucination]]` — não inventar modo. Se state corrompido, perguntar antes de assumir.
- ADR-005 — decisão arquitetural.
- ADR-001 (sync hook) · ADR-004 (auto-boot do squad) — irmãos no SessionStart chain.

## Quando NÃO carregar

- Sessões normais (hash bate, estado existe): hook é silencioso, esta skill não é necessária.
- Bate-papo casual sem mudança de configuração.
- Tarefas de domínio (BI, regulado, etc.) — modo já está ativo, não precisa ser revisitado.
