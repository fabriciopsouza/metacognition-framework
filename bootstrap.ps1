# bootstrap.ps1 — Setup do framework metacognitivo em PC novo (Windows)
#
# Idempotente: rodar 2x não destrói nada. Faz git config (com confirmação se
# já existe), garante gh CLI autenticado, clona o repo principal e
# opcionalmente o repo privado de memória.
#
# USO:
#   pwsh ./bootstrap.ps1 [-MemoryRepo "<owner/repo>"] [-ProjectDir "<path>"]
#
# Exemplos:
#   # Setup só do framework (sem memória própria):
#   pwsh ./bootstrap.ps1
#
#   # Setup completo (mantenedor, com seu repo de memória privado):
#   pwsh ./bootstrap.ps1 -MemoryRepo "fabriciopsouza/claude-memory-metacognition-framework"
#
#   # Custom path (default = ~/dev/metacognition-framework):
#   pwsh ./bootstrap.ps1 -ProjectDir "D:\code\metacognition-framework"
#
# Equivalente macOS/Linux: bootstrap.sh (mesma raiz).

param(
    [string]$MemoryRepo = "",
    [string]$ProjectDir = "$env:USERPROFILE\dev\metacognition-framework",
    [string]$GitEmail = "",
    [string]$GitName = ""
)

$ErrorActionPreference = 'Stop'

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    OK  $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "    !!  $msg" -ForegroundColor Yellow }

# 1. Pre-checks: git e gh instalados
Write-Step "Verificando pre-requisitos (git, gh)"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git nao encontrado. Instalar: https://git-scm.com/download/win"
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "gh CLI nao encontrado. Instalar: https://cli.github.com/"
}
Write-Ok "git e gh instalados"

# 2. Git config global (so seta se nao existir; nao sobrescreve)
Write-Step "Verificando git config global"
$currentEmail = git config --global user.email 2>$null
$currentName  = git config --global user.name 2>$null

if (-not $currentEmail) {
    if (-not $GitEmail) {
        $GitEmail = Read-Host "user.email nao configurado. Informar"
    }
    git config --global user.email $GitEmail
    Write-Ok "user.email setado para: $GitEmail"
} else {
    Write-Ok "user.email ja configurado: $currentEmail"
}

if (-not $currentName) {
    if (-not $GitName) {
        $GitName = Read-Host "user.name nao configurado. Informar"
    }
    git config --global user.name $GitName
    Write-Ok "user.name setado para: $GitName"
} else {
    Write-Ok "user.name ja configurado: $currentName"
}

# 3. gh CLI autenticado
Write-Step "Verificando autenticacao gh CLI"
$ghStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warn "gh CLI nao autenticado. Abrindo fluxo interativo..."
    gh auth login
    if ($LASTEXITCODE -ne 0) { throw "gh auth login falhou" }
}
Write-Ok "gh CLI autenticado"

# 4. Clone do repo principal (skip se ja existir)
Write-Step "Clonando metacognition-framework em $ProjectDir"
if (Test-Path $ProjectDir) {
    Write-Warn "Diretorio ja existe; pulando clone (use 'git pull' la dentro se quiser atualizar)"
} else {
    New-Item -ItemType Directory -Path (Split-Path $ProjectDir) -Force | Out-Null
    gh repo clone fabriciopsouza/metacognition-framework $ProjectDir
    if ($LASTEXITCODE -ne 0) { throw "Clone falhou" }
    Write-Ok "Repo principal clonado"
}

# 5. Clone do repo de memoria (opcional, so se -MemoryRepo passado)
if ($MemoryRepo) {
    Write-Step "Configurando memoria do Claude Code a partir de $MemoryRepo"
    $memoryPath = "$env:USERPROFILE\.claude\projects\f--metacognition-framework\memory"

    if (Test-Path $memoryPath) {
        # Backup nao-destrutivo
        $backupPath = "$memoryPath.backup.$(Get-Date -Format yyyyMMdd-HHmmss)"
        Move-Item -Path $memoryPath -Destination $backupPath
        Write-Warn "Memoria existente movida para: $backupPath"
    }

    New-Item -ItemType Directory -Path (Split-Path $memoryPath) -Force | Out-Null
    gh repo clone $MemoryRepo $memoryPath
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "Clone do repo de memoria falhou. Repo existe e voce tem acesso? URL informada: $MemoryRepo"
    } else {
        Write-Ok "Memoria do Claude Code sincronizada"
    }
} else {
    Write-Ok "Sem -MemoryRepo informado; pulando setup de memoria (terceiros que clonam o framework usam memoria propria)"
}

# 7. Configurar auto-boot global (ADR-006 v1.8.0)
Write-Step "Configurando auto-boot global (ADR-006)"
$globalDir   = Join-Path $env:USERPROFILE '.claude'
$ownersFile  = Join-Path $globalDir 'squad-owners.txt'
$globalSettings = Join-Path $globalDir 'settings.json'
if (-not (Test-Path $globalDir)) { New-Item -ItemType Directory -Path $globalDir -Force | Out-Null }

# squad-owners.txt: nao sobrescrever se ja existe (respeita customizacao do usuario)
if (-not (Test-Path $ownersFile)) {
    $defaultOwners = @(
        '# squad-owners.txt - allowlist de owners para auto-boot global (ADR-006).'
        '# Uma linha por token; substring match case-insensitive contra owner do remote origin.'
        '# Use # para comentar; linhas vazias ignoradas.'
        'fpsouza'
        'fpsouz'
        'fsouza'
        'fabriciosouza'
        'fabriciopsouza'
        'vibraenergia'
        'natulab'
    )
    Set-Content -Path $ownersFile -Value $defaultOwners -Encoding UTF8
    Write-Ok "squad-owners.txt criado com 7 tokens default"
} else {
    Write-Ok "squad-owners.txt ja existe; preservando customizacao"
}

# Merge nao-destrutivo de hooks.SessionStart no ~/.claude/settings.json
# Backup antes de qualquer escrita; restaura se JSON ficar invalido.
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$globalHookCmd = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.claude\hooks\inject-start-session-global.ps1"'

if (Test-Path $globalSettings) {
    $backupPath = "$globalSettings.modeswap.bak"
    Copy-Item $globalSettings $backupPath -Force
    try {
        $cfg = Get-Content $globalSettings -Raw | ConvertFrom-Json
        $needsHook = $true
        if ($cfg.hooks -and $cfg.hooks.SessionStart) {
            $existing = $cfg.hooks.SessionStart | ConvertTo-Json -Depth 10 -Compress
            if ($existing -like '*inject-start-session-global*') { $needsHook = $false }
        }
        if ($needsHook) {
            if (-not $cfg.hooks) { $cfg | Add-Member -NotePropertyName hooks -NotePropertyValue ([pscustomobject]@{}) -Force }
            $newGroup = [ordered]@{
                hooks = @(
                    [ordered]@{
                        type    = 'command'
                        command = $globalHookCmd
                        timeout = 10
                        statusMessage = 'Auto-boot global (ADR-006)'
                    }
                )
            }
            if ($cfg.hooks.SessionStart) {
                $cfg.hooks.SessionStart = @($cfg.hooks.SessionStart) + $newGroup
            } else {
                $cfg.hooks | Add-Member -NotePropertyName SessionStart -NotePropertyValue @($newGroup) -Force
            }
            $newJson = $cfg | ConvertTo-Json -Depth 10
            $null = $newJson | ConvertFrom-Json -ErrorAction Stop
            [System.IO.File]::WriteAllText($globalSettings, $newJson, $utf8NoBom)
            Write-Ok "hooks.SessionStart adicionado a $globalSettings (backup: .modeswap.bak)"
        } else {
            Write-Ok "hooks.SessionStart ja contem auto-boot global; preservando"
        }
    } catch {
        Move-Item -Path $backupPath -Destination $globalSettings -Force
        Write-Warn "Merge falhou ($($_.Exception.Message)); restaurado do backup"
    }
} else {
    $initial = [ordered]@{
        hooks = [ordered]@{
            SessionStart = @(
                [ordered]@{
                    hooks = @(
                        [ordered]@{
                            type = 'command'
                            command = $globalHookCmd
                            timeout = 10
                            statusMessage = 'Auto-boot global (ADR-006)'
                        }
                    )
                }
            )
        }
    }
    [System.IO.File]::WriteAllText($globalSettings, ($initial | ConvertTo-Json -Depth 10), $utf8NoBom)
    Write-Ok "$globalSettings criado com hooks.SessionStart"
}

# Rodada inicial do sync-global para popular ~/.claude/hooks/ + workflows/
$syncScript = Join-Path $ProjectDir '.claude\hooks\sync-global.ps1'
if (Test-Path $syncScript) {
    Write-Step "Rodada inicial do sync-global"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $syncScript | Out-Null
    Write-Ok "Sync inicial executado"
}

# 8. Resumo final
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " Setup concluido. Proximos passos:" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " 1. cd `"$ProjectDir`""
Write-Host " 2. Abrir Claude Code (em qualquer projeto seu)."
Write-Host "    -> SessionStart hook global ativa PMO automaticamente"
Write-Host "       se o owner do remote bate com ~/.claude/squad-owners.txt"
Write-Host "       ou se o projeto tem AGENTS.md / .agent/"
Write-Host " 3. Para pular auto-boot:"
Write-Host "       New-Item .claude/session.lock -ItemType File -Force   (este projeto)"
Write-Host "       New-Item ~/.claude/session.lock -ItemType File -Force (todos)"
Write-Host " 4. Para adicionar owner: editar ~/.claude/squad-owners.txt"
Write-Host ""
Write-Host " Pronto." -ForegroundColor Green
