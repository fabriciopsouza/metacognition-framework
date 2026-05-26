# check-execution-mode.ps1
# Hook SessionStart (v1.7.0) - dispara reativacao de modo de execucao quando:
#   a) estado ausente (~/.claude/framework-mode.json nao existe), OU
#   b) SHA-256 de ~/.claude/hooks/framework-sync.ps1 mudou desde a ultima ativacao.
# Em qualquer outro caso, e SILENCIOSO (exit 0 sem stdout) - nenhum prompt pro usuario.
#
# Quando dispara, emite `additionalContext` via JSON do hookSpecificOutput pedindo ao
# Claude para carregar a skill `execution-modes` e seguir o algoritmo de aplicacao
# (perguntar modo via AskUserQuestion, aplicar template, gravar state file).
#
# Falha "soft": qualquer erro vira warning em stderr e exit 0 (nao bloqueia sessao).
# Disparado pelo SessionStart hook em .claude/settings.json apos sync-global.ps1 e
# antes de inject-start-session.ps1 (modo decide permissoes -> permissoes determinam
# o que o boot pode fazer).

$ErrorActionPreference = 'Continue'

$hookFile  = Join-Path $env:USERPROFILE '.claude\hooks\framework-sync.ps1'
$stateFile = Join-Path $env:USERPROFILE '.claude\framework-mode.json'

function Write-SilentResult {
    # Output JSON com additionalContext vazio - hook executou sem ter o que dizer.
    # exit 0 aqui termina o PROCESSO inteiro (PowerShell propaga exit de dentro de funcao
    # chamada do escopo do script). Refatoracoes futuras precisam manter essa semantica.
    $json = @{
        hookSpecificOutput = @{
            hookEventName     = 'SessionStart'
            additionalContext = ''
        }
    } | ConvertTo-Json -Compress -Depth 5
    Write-Output $json
    exit 0
}

function Write-ActivationResult {
    param(
        [string]$Reason,
        [string]$CurrentMode,
        [string]$CurrentSha
    )

    $modeDisplay = if ($CurrentMode) { $CurrentMode } else { '(nenhum)' }

    # Ratchet: quais modos oferecer com base no atual.
    # Linguagem PROHIBITIVA, nao advisory - mesmo se o usuario pedir downgrade
    # explicitamente, o ativador deve recusar e instruir edicao manual.
    $ratchetHint = switch ($CurrentMode) {
        'default'        { 'Pode confirmar default OU escalar para avancado. NAO oferecer autosuficiente diretamente. NAO oferecer downgrade. Se o usuario pedir downgrade, recuse e instrua edicao manual de ~/.claude/framework-mode.json (ver SKILL.md "Regra anti-downgrade").' }
        'avancado'       { 'Pode confirmar avancado OU escalar para autosuficiente. NAO oferecer downgrade nem default. Se o usuario pedir downgrade, recuse e instrua edicao manual.' }
        'autosuficiente' { 'Apenas confirmar autosuficiente. NAO oferecer downgrade nem default nem avancado. Mesmo se o usuario insistir: recuse e instrua edicao manual de ~/.claude/framework-mode.json.' }
        default          { 'Estado inicial - oferecer os 3 modos (default, avancado, autosuficiente).' }
    }

    $context = @"
# ATIVACAO de Modo de Execucao do Framework (REQUER ACAO)

**Motivo do trigger:** $Reason
**Modo atual registrado:** $modeDisplay
**SHA-256 atual de framework-sync.ps1:** $CurrentSha

## Sua acao (Claude), ANTES de qualquer outra coisa neste turno:

**Carregue a skill ``execution-modes``** lendo ``~/.claude/skills/execution-modes/SKILL.md`` e siga o algoritmo canonico ali (8 passos: ler state, perguntar ao usuario, ratchet, BACKUP obrigatorio do settings.json, ler template, merge validado, gravar state file, confirmar). NAO improvise — o algoritmo cobre backup .modeswap.bak, rollback, e a regra anti-downgrade binding.

**Ratchet a aplicar agora** (ANTES de chamar AskUserQuestion):
- $ratchetHint

**Valores que voce ja sabe** (use direto, nao recalcule):
- hookSha256 para gravar no state file: ``$CurrentSha``
- Motivo a registrar no history: ``$Reason``
- Modo atual (fromMode na entrada do history): ``$modeDisplay``

**Esta ativacao so dispara em:** (a) primeira instalacao (state ausente), (b) framework-sync.ps1 mudou (hash diferente). Em sessoes normais este hook e silencioso.

**Referencias:** ADR-005 (``docs/adr/005-niveis-de-execucao-framework.md``) · SKILL.md de execution-modes (algoritmo canonico).
"@

    $json = @{
        hookSpecificOutput = @{
            hookEventName     = 'SessionStart'
            additionalContext = $context
        }
    } | ConvertTo-Json -Compress -Depth 5
    Write-Output $json
    exit 0
}

try {
    # 1. Computar SHA-256 do hook.
    if (-not (Test-Path $hookFile)) {
        [Console]::Error.WriteLine("[check-execution-mode] aviso: $hookFile nao encontrado - hook ainda nao instalado, pulando check.")
        Write-SilentResult
    }

    $currentSha = $null
    try {
        $currentSha = (Get-FileHash -Path $hookFile -Algorithm SHA256 -ErrorAction Stop).Hash
    } catch {
        [Console]::Error.WriteLine("[check-execution-mode] warning ao calcular SHA: $($_.Exception.Message)")
        Write-SilentResult
    }

    if (-not $currentSha) {
        Write-SilentResult
    }

    # 2. Ler state file (se existir).
    $state = $null
    if (Test-Path $stateFile) {
        try {
            $raw = Get-Content -Path $stateFile -Raw -ErrorAction Stop
            $state = $raw | ConvertFrom-Json -ErrorAction Stop
        } catch {
            [Console]::Error.WriteLine("[check-execution-mode] state file corrompido ($stateFile): $($_.Exception.Message). Tratando como ausente.")
            $state = $null
        }
    }

    # 3. Decidir se precisa de ativacao.
    $needsActivation = $false
    $reason = ''
    $currentMode = ''

    if ($null -eq $state -or -not $state.mode -or -not $state.hookSha256) {
        $needsActivation = $true
        $reason = 'INITIAL'
        $currentMode = ''
    } elseif ($state.hookSha256 -ne $currentSha) {
        $needsActivation = $true
        $reason = 'HOOK_CHANGED'
        $currentMode = [string]$state.mode
    }

    if (-not $needsActivation) {
        # Hash bate, estado integro - silencio.
        Write-SilentResult
    }

    Write-ActivationResult -Reason $reason -CurrentMode $currentMode -CurrentSha $currentSha
}
catch {
    [Console]::Error.WriteLine("[check-execution-mode] warning: $($_.Exception.Message)")
    Write-SilentResult
}
