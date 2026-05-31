# ensure-global-wiring.ps1 — self-heal da wiring de hooks globais (ADR-027)
#
# PROBLEMA: o ~/.claude/settings.json global pode ficar SEM a chave `hooks` (clobber
# do mode-apply autosuficiente — o algoritmo execution-modes §5 manda "preservar hooks",
# mas isso é PROSA: o disco mostrou zero hooks). Sem wiring global, abrir o Claude em
# QUALQUER pasta não-framework dispara zero hooks (falha-raiz do relato AIVI).
#
# MECANISMO (ponto de Arquimedes): este script é chamado pelo sync-global.ps1, que roda
# do settings.json de PROJETO (versionado, estável). Logo, toda vez que o repo-framework
# abre, a wiring GLOBAL é re-afirmada — derrotando o clobber de forma mecânica, não por
# promessa. Idempotente, hook-preserving (NUNCA dropa chave existente), backup + validação.
#
# Garante no ~/.claude/settings.json:
#   - hooks.SessionStart     contém inject-start-session-global.ps1 (auto-boot, ADR-006)
#   - hooks.UserPromptSubmit contém route-gate.ps1                  (roteamento, ADR-027)
#
# EXIT CODES (consumidos por bootstrap/sync-global p/ transparência ao usuário):
#   0  = nada a fazer (já wirado)
#   10 = wiring (re)aplicada — houve mudança (ex.: clobber curado)
#   1  = erro; settings restaurado do backup .heal.bak
#
# Uso:  ensure-global-wiring.ps1 [-RepoDir <path>]
#   -RepoDir (opcional): se passado, espelha route-gate.ps1 + inject-global do repo p/
#   ~/.claude/hooks/ antes de wirar (torna o script autossuficiente fora do sync-global).

param([string]$RepoDir = "")

$ErrorActionPreference = 'Stop'

$globalDir = Join-Path $env:USERPROFILE '.claude'
$hooksDir  = Join-Path $globalDir 'hooks'
$settings  = Join-Path $globalDir 'settings.json'
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

$injectGlobal = Join-Path $hooksDir 'inject-start-session-global.ps1'
$routeGate    = Join-Path $hooksDir 'route-gate.ps1'

function Log($m) { [Console]::Error.WriteLine("[ensure-global-wiring] $m") }

try {
    if (-not (Test-Path $globalDir)) { New-Item -ItemType Directory -Path $globalDir -Force | Out-Null }
    if (-not (Test-Path $hooksDir))  { New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null }

    # 0. Auto-suficiência: se -RepoDir, espelhar os scripts-fonte p/ ~/.claude/hooks/.
    if ($RepoDir -and (Test-Path $RepoDir)) {
        $srcRoute  = Join-Path $RepoDir 'tools\hooks\route-gate.ps1'
        $srcInject = Join-Path $RepoDir '.claude\hooks\inject-start-session-global.template.ps1'
        if (Test-Path $srcRoute)  { Copy-Item $srcRoute  $routeGate    -Force -ErrorAction SilentlyContinue }
        if (Test-Path $srcInject) { Copy-Item $srcInject $injectGlobal -Force -ErrorAction SilentlyContinue }
    }

    $injectCmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$injectGlobal`""
    $routeCmd  = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$routeGate`""

    # 1. Carregar settings (ou iniciar objeto vazio).
    $cfg = $null
    if (Test-Path $settings) {
        $cfg = Get-Content $settings -Raw | ConvertFrom-Json
    }
    if (-not $cfg) { $cfg = [pscustomobject]@{} }
    if (-not $cfg.hooks) { $cfg | Add-Member -NotePropertyName hooks -NotePropertyValue ([pscustomobject]@{}) -Force }

    $changed = $false

    # Helper: garante que um evento de hook contém um grupo cujo command casa o needle.
    function Ensure-HookEvent {
        param($Cfg, [string]$EventName, [string]$Needle, [string]$Command, [string]$StatusMessage)
        $present = $false
        $existing = $Cfg.hooks.$EventName
        if ($existing) {
            $serialized = $existing | ConvertTo-Json -Depth 10 -Compress
            if ($serialized -like "*$Needle*") { $present = $true }
        }
        if ($present) { return $false }

        $newGroup = [ordered]@{
            hooks = @(
                [ordered]@{
                    type          = 'command'
                    command       = $Command
                    timeout       = 10
                    statusMessage = $StatusMessage
                }
            )
        }
        if ($existing) {
            $Cfg.hooks.$EventName = @($existing) + $newGroup
        } else {
            $Cfg.hooks | Add-Member -NotePropertyName $EventName -NotePropertyValue @($newGroup) -Force
        }
        return $true
    }

    if (Ensure-HookEvent -Cfg $cfg -EventName 'SessionStart' -Needle 'inject-start-session-global' `
            -Command $injectCmd -StatusMessage 'Auto-boot global do squad (ADR-006)') { $changed = $true }

    if (Ensure-HookEvent -Cfg $cfg -EventName 'UserPromptSubmit' -Needle 'route-gate' `
            -Command $routeCmd -StatusMessage 'Roteamento determinístico (route-gate ADR-027)') { $changed = $true }

    if (-not $changed) {
        Log 'wiring ja presente; nada a fazer.'
        exit 0
    }

    # 2. Backup + validação + escrita atômica (hook-preserving: serializamos $cfg inteiro).
    if (Test-Path $settings) { Copy-Item $settings "$settings.heal.bak" -Force }
    $newJson = $cfg | ConvertTo-Json -Depth 12
    $null = $newJson | ConvertFrom-Json -ErrorAction Stop   # valida antes de gravar
    [System.IO.File]::WriteAllText($settings, $newJson, $utf8NoBom)
    Log 'wiring (re)aplicada — hooks globais re-afirmados (auto-heal).'
    exit 10
}
catch {
    Log "ERRO: $($_.Exception.Message)"
    if (Test-Path "$settings.heal.bak") {
        Move-Item "$settings.heal.bak" $settings -Force -ErrorAction SilentlyContinue
        Log 'settings restaurado do backup .heal.bak.'
    }
    exit 1
}
