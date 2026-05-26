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

# 6. Resumo final
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " Setup concluido. Proximos passos:" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " 1. cd `"$ProjectDir`""
Write-Host " 2. Abrir Claude Code neste diretorio."
Write-Host "    -> SessionStart hook roda automaticamente:"
Write-Host "       * sync-global.ps1 espelha skills para ~/.claude/"
Write-Host "       * inject-start-session.ps1 ativa PMO no 1o turno"
Write-Host " 3. Para pular o auto-boot em sessao rapida:"
Write-Host "       New-Item .claude/session.lock -ItemType File -Force"
Write-Host ""
Write-Host " Pronto." -ForegroundColor Green
