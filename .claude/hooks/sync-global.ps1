# sync-global.ps1
# Espelha o framework do repo para ~/.claude/ (instalacao global do Claude Code).
# - _shared/<name>/         -> ~/.claude/skills/<name>/      (pasta inteira via Copy-Item -Recurse;
#                                                            inclui SKILL.md + qualquer companion *.md ou helpers)
# - .agent/skills/<name>/   -> ~/.claude/skills/<name>/      (idem)
# - .claude/agents/*.md (NAO .txt) -> ~/.claude/agents/
# - este proprio script                              -> ~/.claude/hooks/framework-sync.ps1  (v1.7.1)
# - .claude/hooks/inject-start-session-global.template.ps1 -> ~/.claude/hooks/inject-start-session-global.ps1  (v1.8.0)
# - .agent/workflows/<file>                          -> ~/.claude/workflows/<file>  (v1.8.0 - hook global le start-session.md de la)
# Pre-requisito de "skill valida": ter SKILL.md na pasta (entry point).
# Companion files (ex.: discovery/mapeamento-de-processo.md, ADR-003 progressive disclosure) sao
# copiados automaticamente porque o -Recurse copia a pasta inteira. Nao precisa adicionar regra nova.
# Idempotente. Falha "soft": warning no stderr, exit 0 (nao bloqueia sessao).
# Disparado pelo SessionStart hook em .claude/settings.json. Tambem pode rodar a mao.

$ErrorActionPreference = 'Continue'
# projectRoot: $env:CLAUDE_PROJECT_DIR (Claude Code) ou walking up 3 niveis do script.
# Cadeia $PSCommandPath -> $MyInvocation.MyCommand.Path -> $null cobre iex/dot-source (ADR-005 pos-merge).
if ($env:CLAUDE_PROJECT_DIR -and (Test-Path $env:CLAUDE_PROJECT_DIR)) {
    $projectRoot = $env:CLAUDE_PROJECT_DIR
} else {
    $scriptPath = if ($PSCommandPath) { $PSCommandPath }
                  elseif ($MyInvocation.MyCommand.Path) { $MyInvocation.MyCommand.Path }
                  else { $null }
    $projectRoot = if ($scriptPath) { Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $scriptPath)) } else { $null }
}
$dest          = Join-Path $env:USERPROFILE '.claude'
$skillsDest    = Join-Path $dest 'skills'
$agentsDest    = Join-Path $dest 'agents'
$hooksDest     = Join-Path $dest 'hooks'
$workflowsDest = Join-Path $dest 'workflows'

$skillCount    = 0
$agentCount    = 0
$hookCount     = 0
$workflowCount = 0

try {
    if (-not (Test-Path $skillsDest))    { New-Item -ItemType Directory -Path $skillsDest -Force | Out-Null }
    if (-not (Test-Path $agentsDest))    { New-Item -ItemType Directory -Path $agentsDest -Force | Out-Null }
    if (-not (Test-Path $hooksDest))     { New-Item -ItemType Directory -Path $hooksDest -Force | Out-Null }
    if (-not (Test-Path $workflowsDest)) { New-Item -ItemType Directory -Path $workflowsDest -Force | Out-Null }

    # Guard $projectRoot=$null: Join-Path com $null lanca erro terminante (try/catch
    # captura mas mata o self-copy junto). Guardar mantem o self-copy alcancavel.
    if ($projectRoot) {
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
    } else {
        [Console]::Error.WriteLine("[framework-sync] aviso: projectRoot nao resolvido ($PSCommandPath e $MyInvocation.MyCommand.Path ambos nulos, e CLAUDE_PROJECT_DIR ausente). Pulando sync de skills/agents; self-copy ainda tentara rodar.")
    }

    # Self-copy: espelha este script como ~/.claude/hooks/framework-sync.ps1 (par fonte/binario,
    # ADR-005 pos-merge). Necessario porque check-execution-mode.ps1 (linha 18) monitora SHA-256
    # desse path — sem este espelhamento o gate de modos de execucao fica dormente.
    # Edge: rodar manualmente do path instalado faz Copy-Item de si para si (Windows trunca+recopia,
    # sem efeito pratico).
    $selfSource = if ($PSCommandPath) { $PSCommandPath }
                  elseif ($MyInvocation.MyCommand.Path) { $MyInvocation.MyCommand.Path }
                  else { $null }
    $selfTarget = Join-Path $hooksDest 'framework-sync.ps1'
    if ($selfSource -and (Test-Path $selfSource)) {
        Copy-Item -Path $selfSource -Destination $selfTarget -Force -ErrorAction SilentlyContinue
        if (Test-Path $selfTarget) { $hookCount++ }
    }

    # ADR-006 / v1.8.0 — espelha o template do hook global (fonte versionada) para a
    # instancia executavel em ~/.claude/hooks/. Par fonte/binario igual ao framework-sync.
    if ($projectRoot) {
        $hookGlobalSource = Join-Path $projectRoot '.claude\hooks\inject-start-session-global.template.ps1'
        $hookGlobalTarget = Join-Path $hooksDest 'inject-start-session-global.ps1'
        if (Test-Path $hookGlobalSource) {
            Copy-Item -Path $hookGlobalSource -Destination $hookGlobalTarget -Force -ErrorAction SilentlyContinue
            if (Test-Path $hookGlobalTarget) { $hookCount++ }
        }

        # ADR-019 / v1.19.0 — espelha check-repo-sync.ps1 (sync de boot) para a instancia global,
        # disponivel a outros repos squad. Registro no SessionStart global e follow-up (bootstrap.ps1);
        # no repo-framework ja esta wired pelo .claude/settings.json do projeto.
        $repoSyncSource = Join-Path $projectRoot '.claude\hooks\check-repo-sync.ps1'
        $repoSyncTarget = Join-Path $hooksDest 'check-repo-sync.ps1'
        if (Test-Path $repoSyncSource) {
            Copy-Item -Path $repoSyncSource -Destination $repoSyncTarget -Force -ErrorAction SilentlyContinue
            if (Test-Path $repoSyncTarget) { $hookCount++ }
        }

        # ADR-020 / v1.20.0 — espelha check-core-agnostic.ps1 (linter de agnosticismo do nucleo) para a
        # instancia global. Fail-soft: em repos sem tools/check_core_agnostic.py o hook sai silencioso.
        $agnosticSource = Join-Path $projectRoot '.claude\hooks\check-core-agnostic.ps1'
        $agnosticTarget = Join-Path $hooksDest 'check-core-agnostic.ps1'
        if (Test-Path $agnosticSource) {
            Copy-Item -Path $agnosticSource -Destination $agnosticTarget -Force -ErrorAction SilentlyContinue
            if (Test-Path $agnosticTarget) { $hookCount++ }
        }

        # ADR-027 / v1.22.0 — espelha route-gate (roteamento determinístico, UserPromptSubmit)
        # e ensure-global-wiring (self-heal) para a instância global. Pares fonte/binário.
        foreach ($pair in @(
            @{ src = 'tools\hooks\route-gate.ps1';           dst = 'route-gate.ps1' },
            @{ src = 'tools\hooks\ensure-global-wiring.ps1';  dst = 'ensure-global-wiring.ps1' }
        )) {
            $s = Join-Path $projectRoot $pair.src
            $d = Join-Path $hooksDest   $pair.dst
            if (Test-Path $s) {
                Copy-Item -Path $s -Destination $d -Force -ErrorAction SilentlyContinue
                if (Test-Path $d) { $hookCount++ }
            }
        }

        # Espelha .agent/workflows/ — o hook global le start-session.md de ~/.claude/workflows/.
        $workflowsRoot = Join-Path $projectRoot '.agent\workflows'
        if (Test-Path $workflowsRoot) {
            Get-ChildItem -Path $workflowsRoot -File -ErrorAction SilentlyContinue | ForEach-Object {
                Copy-Item -Path $_.FullName -Destination (Join-Path $workflowsDest $_.Name) -Force -ErrorAction SilentlyContinue
                $workflowCount++
            }
        }
    }

    # ADR-027 / v1.22.0 — SELF-HEAL: re-afirma a wiring de hooks GLOBAIS no ~/.claude/settings.json.
    # Roda do settings de PROJETO (estável) -> cura o GLOBAL (volátil), derrotando o clobber do
    # mode-apply. Processo separado: o `exit` do ensure não mata este script. Stderr suprimido;
    # decisão vem do exit code (10 = mudou). Fail-soft.
    $healNote = ''
    if ($projectRoot) {
        $ensureScript = Join-Path $hooksDest 'ensure-global-wiring.ps1'
        if (Test-Path $ensureScript) {
            try {
                & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ensureScript -RepoDir $projectRoot 2>$null
                if ($LASTEXITCODE -eq 10) { $healNote = ' | auto-heal: hooks globais re-wirados (ADR-027)' }
            } catch { }
        }
    }

    $msg  = "Framework sync: $skillCount skills + $agentCount agents + $hookCount hooks + $workflowCount workflows -> ~/.claude/$healNote"
    $json = @{ systemMessage = $msg } | ConvertTo-Json -Compress
    Write-Output $json
}
catch {
    [Console]::Error.WriteLine("[framework-sync] warning: $($_.Exception.Message)")
}

exit 0
