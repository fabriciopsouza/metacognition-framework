# inject-start-session-global.template.ps1
# Hook SessionStart GLOBAL (ADR-006 v1.8.0) - ativacao condicional do squad
# por allowlist de owners do remote OU marker no projeto.
#
# Fonte versionada no repo-framework; espelhada para
# ~/.claude/hooks/inject-start-session-global.ps1 pelo sync-global.ps1.
# NAO editar a copia global direto - mude aqui e abra o repo-framework.
#
# Algoritmo (ADR-006):
#  1. CWD = $env:CLAUDE_PROJECT_DIR ?? $PWD
#  2. ~/.claude/session.lock existe -> SKIP global-lock
#  3. $CWD/.claude/session.lock existe -> SKIP project-lock
#  4. git -C $CWD remote get-url origin -> extrair owner via regex (HTTPS + SSH)
#  5. Ler ~/.claude/squad-owners.txt -> substring match case-insensitive
#  6. Match -> ACTIVATE (motivo owner-allowlist; statusMessage expoe owner completo
#     para diagnostico de falso positivo - qa-critic round 1 C6)
#  7. Sem match -> Test-Path AGENTS.md ou .agent/ -> ACTIVATE (motivo marker)
#  8. Sem match nem marker -> SKIP
# Falha soft: warning stderr + exit 0 (nunca bloqueia sessao).

$ErrorActionPreference = 'Continue'

# UTF-8 sem BOM no stdout: PS 5.1 default emite na codepage do console, corrompendo
# acentos e multibyte (—, →) para o consumidor UTF-8 (Claude Code le o stdout do hook).
# BOM quebraria o parse do JSON, por isso UTF8Encoding($false).
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false

$cwd = if ($env:CLAUDE_PROJECT_DIR -and (Test-Path $env:CLAUDE_PROJECT_DIR)) {
    $env:CLAUDE_PROJECT_DIR
} else {
    (Get-Location).Path
}

function Emit-Result {
    param([string]$AddContext, [string]$Status)
    $json = @{
        hookSpecificOutput = @{
            hookEventName     = 'SessionStart'
            additionalContext = $AddContext
        }
        systemMessage = "auto-boot: $Status"
    } | ConvertTo-Json -Compress -Depth 5
    Write-Output $json
    exit 0
}

try {
    $globalLock  = Join-Path $env:USERPROFILE '.claude\session.lock'
    $projectLock = Join-Path $cwd '.claude\session.lock'
    if (Test-Path $globalLock)  { Emit-Result '' 'skipped (global-lock)' }
    if (Test-Path $projectLock) { Emit-Result '' 'skipped (project-lock)' }

    # Extrair owner do remote origin (HTTPS + SSH)
    $owner = $null
    try {
        $remoteUrl = (git -C $cwd remote get-url origin 2>$null) | Out-String
        $remoteUrl = $remoteUrl.Trim()
        if ($remoteUrl) {
            # Cobre: https://github.com/owner/repo[.git], git@host:owner/repo[.git]
            if ($remoteUrl -match '[:/]([^:/\s]+)/[^/\s]+?(\.git)?\s*$') {
                $owner = $matches[1]
            }
        }
    } catch { }

    # Match contra ~/.claude/squad-owners.txt (substring case-insensitive)
    $matchToken = $null
    if ($owner) {
        $ownersFile = Join-Path $env:USERPROFILE '.claude\squad-owners.txt'
        if (Test-Path $ownersFile) {
            $tokens = Get-Content $ownersFile -ErrorAction SilentlyContinue |
                Where-Object { $_ -and -not ($_.Trim().StartsWith('#')) -and $_.Trim() } |
                ForEach-Object { $_.Trim().ToLower() }
            $ownerLower = $owner.ToLower()
            foreach ($tk in $tokens) {
                if ($tk -and $ownerLower.Contains($tk)) {
                    $matchToken = $tk
                    break
                }
            }
        }
    }

    # Fallback: marker no projeto
    $marker = $null
    if (-not $matchToken) {
        if (Test-Path (Join-Path $cwd 'AGENTS.md')) { $marker = 'AGENTS.md' }
        elseif (Test-Path (Join-Path $cwd '.agent')) { $marker = '.agent' }
    }

    if (-not $matchToken -and -not $marker) {
        $reason = if ($owner) { "skipped (owner=$owner, sem match)" } else { 'skipped (no-match-no-marker)' }
        Emit-Result '' $reason
    }

    # Ler start-session.md (espelhado para ~/.claude/workflows/ pelo sync-global)
    $startDoc = Join-Path $env:USERPROFILE '.claude\workflows\start-session.md'
    if (-not (Test-Path $startDoc)) {
        # Fallback: PC nunca abriu repo-framework para popular workflows global
        Emit-Result '' 'skipped (start-session.md ausente; rode sync no repo-framework primeiro)'
    }

    $startContent = Get-Content $startDoc -Raw -Encoding UTF8
    $status = if ($matchToken) { "owner=$owner match=$matchToken" } else { "marker=$marker" }
    $context = @"
# Boot automatico do squad - global (ADR-006 v1.8.0)

Sessao iniciada com squad em modo auto-boot global. Motivo: $status.
Primeira acao deste turno DEVE ser ativar o PMO via /start-session conforme abaixo.

Para pular em sessoes futuras:
  - New-Item .claude/session.lock        (este projeto apenas)
  - New-Item ~/.claude/session.lock      (todos os projetos)

---

$startContent
"@
    Emit-Result $context $status
}
catch {
    [Console]::Error.WriteLine("[auto-boot-global] warning: $($_.Exception.Message)")
    Emit-Result '' "error: $($_.Exception.Message)"
}
