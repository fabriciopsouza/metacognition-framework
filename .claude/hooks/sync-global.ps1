# sync-global.ps1
# Espelha o framework do repo para ~/.claude/ (instalacao global do Claude Code).
# - _shared/<name>/         -> ~/.claude/skills/<name>/      (pasta inteira via Copy-Item -Recurse;
#                                                            inclui SKILL.md + qualquer companion *.md ou helpers)
# - .agent/skills/<name>/   -> ~/.claude/skills/<name>/      (idem)
# - .claude/agents/*.md (NAO .txt) -> ~/.claude/agents/
# - este proprio script    -> ~/.claude/hooks/framework-sync.ps1  (v1.7.1 — fecha o gap do ADR-005)
# Pre-requisito de "skill valida": ter SKILL.md na pasta (entry point).
# Companion files (ex.: discovery/mapeamento-de-processo.md, ADR-003 progressive disclosure) sao
# copiados automaticamente porque o -Recurse copia a pasta inteira. Nao precisa adicionar regra nova.
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
$hooksDest   = Join-Path $dest 'hooks'

$skillCount = 0
$agentCount = 0
$hookCount  = 0

try {
    if (-not (Test-Path $skillsDest)) { New-Item -ItemType Directory -Path $skillsDest -Force | Out-Null }
    if (-not (Test-Path $agentsDest)) { New-Item -ItemType Directory -Path $agentsDest -Force | Out-Null }
    if (-not (Test-Path $hooksDest))  { New-Item -ItemType Directory -Path $hooksDest -Force | Out-Null }

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

    # ADR-005 / v1.7.1 — espelha este proprio sync-global.ps1 para ~/.claude/hooks/framework-sync.ps1.
    # Resolve a referencia orfa do check-execution-mode.ps1 (linha 18) que monitora SHA-256 deste arquivo
    # no destino global. Sem isso, o gate de modos de execucao (ADR-005) cai sempre no branch silencioso
    # "Test-Path $hookFile = false" e nunca dispara reativacao. Nome diferente e deliberado: sync-global.ps1
    # e o FONTE (project-level), framework-sync.ps1 e a INSTANCIA INSTALADA (global-level). Par fonte/binario.
    #
    # Resolucao do caminho do proprio script (qa-critic round 1, C3 [MEDIO]): preferir $PSCommandPath
    # (PowerShell 3+, robusto em todos os modos de invocacao); fallback para $MyInvocation.MyCommand.Path
    # (que retorna $null em iex/dot-source). Sem essa cadeia, o gap reaparece silenciosamente se o
    # runtime do hook do Claude Code invocar o script via iex em vez de -File.
    #
    # Edge conhecida (qa-critic round 1, adversarial extra): se este script for invocado a partir da
    # PROPRIA copia em ~/.claude/hooks/framework-sync.ps1 (uso manual como diagnostico), $selfSource
    # apontaria para ~/.claude/hooks/framework-sync.ps1 e $selfTarget para o mesmo path -> Copy-Item de
    # si para si. Comportamento do Windows: truncamento + recopia do mesmo conteudo, sem efeito pratico.
    $selfSource = if ($PSCommandPath) { $PSCommandPath }
                  elseif ($MyInvocation.MyCommand.Path) { $MyInvocation.MyCommand.Path }
                  else { $null }
    $selfTarget = Join-Path $hooksDest 'framework-sync.ps1'
    if ($selfSource -and (Test-Path $selfSource)) {
        Copy-Item -Path $selfSource -Destination $selfTarget -Force -ErrorAction SilentlyContinue
        if (Test-Path $selfTarget) { $hookCount++ }
    }

    $msg  = "Framework sync: $skillCount skills + $agentCount agents + $hookCount hooks -> ~/.claude/"
    $json = @{ systemMessage = $msg } | ConvertTo-Json -Compress
    Write-Output $json
}
catch {
    [Console]::Error.WriteLine("[framework-sync] warning: $($_.Exception.Message)")
}

exit 0
