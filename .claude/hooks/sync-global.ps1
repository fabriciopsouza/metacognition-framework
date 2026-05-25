# sync-global.ps1
# Espelha o framework do repo para ~/.claude/ (instalacao global do Claude Code).
# - _shared/<name>/SKILL.md      -> ~/.claude/skills/<name>/
# - .agent/skills/<name>/SKILL.md -> ~/.claude/skills/<name>/
# - .claude/agents/*.md (NAO .txt) -> ~/.claude/agents/
# Idempotente. Falha "soft": warning no stderr, exit 0 (nao bloqueia sessao).
# Disparado pelo SessionStart hook em .claude/settings.json. Tambem pode rodar a mao.

$ErrorActionPreference = 'Continue'
# Script vive em <projectRoot>/.claude/hooks/sync-global.ps1 — 3 niveis acima.
# Preferir $env:CLAUDE_PROJECT_DIR quando Claude Code o setar; fallback walking up.
if ($env:CLAUDE_PROJECT_DIR -and (Test-Path $env:CLAUDE_PROJECT_DIR)) {
    $projectRoot = $env:CLAUDE_PROJECT_DIR
} else {
    $projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
}
$dest        = Join-Path $env:USERPROFILE '.claude'
$skillsDest  = Join-Path $dest 'skills'
$agentsDest  = Join-Path $dest 'agents'

$skillCount = 0
$agentCount = 0

try {
    if (-not (Test-Path $skillsDest)) { New-Item -ItemType Directory -Path $skillsDest -Force | Out-Null }
    if (-not (Test-Path $agentsDest)) { New-Item -ItemType Directory -Path $agentsDest -Force | Out-Null }

    $sharedRoot      = Join-Path $projectRoot '_shared'
    $agentSkillsRoot = Join-Path $projectRoot '.agent\skills'
    $agentsRoot      = Join-Path $projectRoot '.claude\agents'

    if (Test-Path $sharedRoot) {
        Get-ChildItem -Path $sharedRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            if (Test-Path (Join-Path $_.FullName 'SKILL.md')) {
                $target = Join-Path $skillsDest $_.Name
                # Remove destino existente antes de copiar — evita aninhamento (Copy-Item -Recurse copia INTO se destino existe).
                if (Test-Path $target) { Remove-Item -Path $target -Recurse -Force -ErrorAction SilentlyContinue }
                Copy-Item -Path $_.FullName -Destination $target -Recurse -Force -ErrorAction SilentlyContinue
                $skillCount++
            }
        }
    }

    if (Test-Path $agentSkillsRoot) {
        Get-ChildItem -Path $agentSkillsRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            if (Test-Path (Join-Path $_.FullName 'SKILL.md')) {
                $target = Join-Path $skillsDest $_.Name
                # Remove destino existente antes de copiar — evita aninhamento (Copy-Item -Recurse copia INTO se destino existe).
                if (Test-Path $target) { Remove-Item -Path $target -Recurse -Force -ErrorAction SilentlyContinue }
                Copy-Item -Path $_.FullName -Destination $target -Recurse -Force -ErrorAction SilentlyContinue
                $skillCount++
            }
        }
    }

    if (Test-Path $agentsRoot) {
        Get-ChildItem -Path $agentsRoot -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -eq '.md' } |
            ForEach-Object {
                Copy-Item -Path $_.FullName -Destination (Join-Path $agentsDest $_.Name) -Force -ErrorAction SilentlyContinue
                $agentCount++
            }
    }

    $msg  = "Framework sync: $skillCount skills + $agentCount agents -> ~/.claude/"
    $json = @{ systemMessage = $msg } | ConvertTo-Json -Compress
    Write-Output $json
}
catch {
    [Console]::Error.WriteLine("[framework-sync] warning: $($_.Exception.Message)")
}

exit 0
