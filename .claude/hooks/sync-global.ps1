# sync-global.ps1
# Espelha o framework do repo para ~/.claude/ (instalacao global do Claude Code).
# - _shared/<name>/         -> ~/.claude/skills/<name>/      (pasta inteira via Copy-Item -Recurse;
#                                                            inclui SKILL.md + qualquer companion *.md ou helpers)
# - .agent/skills/<name>/   -> ~/.claude/skills/<name>/      (idem)
# - .claude/agents/*.md (NAO .txt) -> ~/.claude/agents/
# - este proprio script                              -> ~/.claude/hooks/framework-sync.ps1  (v1.7.1)
# - inject-start-session-global, route-gate, resposta_executiva, ensure-global-wiring -> ~/.claude/hooks/ via
#   ensure-global-wiring, de UMA origem (origin/main por default) junto com o wiring (ADR-130)
# - .agent/workflows/<file>                          -> ~/.claude/workflows/<file>  (v1.8.0 - hook global le start-session.md de la)
# - .claude/global/CLAUDE-global.md                  -> ~/.claude/CLAUDE.md  (bloco entre marcadores; resto do arquivo intacto)
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
$globalNote    = ''

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

    # inject-start-session-global, route-gate, resposta_executiva e ensure-global-wiring NAO sao copiados daqui:
    # o ensure-global-wiring os instala de UMA origem (origin/main por default) junto com o wiring (ADR-130).
    if ($projectRoot) {
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

        # Espelha .agent/workflows/ — o hook global le start-session.md de ~/.claude/workflows/.
        $workflowsRoot = Join-Path $projectRoot '.agent\workflows'
        if (Test-Path $workflowsRoot) {
            Get-ChildItem -Path $workflowsRoot -File -ErrorAction SilentlyContinue | ForEach-Object {
                Copy-Item -Path $_.FullName -Destination (Join-Path $workflowsDest $_.Name) -Force -ErrorAction SilentlyContinue
                $workflowCount++
            }
        }

        # Regras permanentes do dono -> ~/.claude/CLAUDE.md, lido pelo Claude Code em TODA pasta (ADR-116).
        # UMA implementacao so, em Python (bootstrap.py --regras-globais): a copia desta logica em
        # PowerShell divergiu da do Python tres vezes seguidas na revisao (barra final no caminho, CRLF,
        # instalador esquecido). Aqui so se chama e se repassa o resultado. Try proprio: falha aqui nao
        # pode pular o self-heal ADR-027 nem o systemMessage abaixo.
        $bootPy = Join-Path $projectRoot 'bootstrap.py'
        if (Test-Path (Join-Path $projectRoot '.claude\global\CLAUDE-global.md')) {
            try {
                $py = Get-Command python -ErrorAction SilentlyContinue
                if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
                if ($py) {
                    $saida = & $py.Source $bootPy --regras-globais 2>&1 | Select-Object -Last 1
                    $globalNote = if ($LASTEXITCODE -eq 0) { ' + regras globais (~/.claude/CLAUDE.md)' } else { " + regras globais NAO instaladas: $saida" }
                } else {
                    $globalNote = ' + regras globais NAO instaladas: Python ausente (rode python bootstrap.py)'
                }
            } catch {
                $globalNote = " + regras globais FALHARAM: $($_.Exception.Message)"
            }
        }
    }

    # ADR-027 / v1.22.0 — SELF-HEAL: re-afirma a wiring de hooks GLOBAIS no ~/.claude/settings.json.
    # Roda do settings de PROJETO (estável) -> cura o GLOBAL (volátil), derrotando o clobber do
    # mode-apply. Processo separado: o `exit` do ensure não mata este script. Stderr suprimido;
    # decisão vem do exit code (10 = mudou). Fail-soft.
    # ADR-130: o ensure que roda é o do MESMO commit dos scripts que ele instala (origin/main por default; outro ref
    # so com FRAMEWORK_HOOKS_REF). Wiring e script nunca vem de branches diferentes. Sem ref: sonda o instalado.
    $healNote = ''
    if ($projectRoot) {
        # Tres casos: (1) ref resolvido -> ensure DO REF instala do ref; (2) pasta sem git ou WORKTREE (opt-in) ->
        # ensure da propria pasta; (3) git sem o ref, ou ensure do ref anterior ao ADR-130 -> ensure instalado so
        # sonda e corrige o wiring, sem instalar. Nenhum ensure sem ENSURE-CONTRATO >= 2 roda: o antigo ignora -Ref,
        # copia do working tree e liga sem sonda (o incidente de 28/09/2026). Ex.: origin/main local ainda sem fetch.
        function Test-EnsureContrato([string]$p) {
            if (-not (Test-Path $p)) { return $false }
            $m = Select-String -Path $p -Pattern '^# ENSURE-CONTRATO: (\d+)' | Select-Object -First 1
            return [bool]($m -and [int]$m.Matches[0].Groups[1].Value -ge 2)
        }
        $ensureScript = Join-Path $hooksDest 'ensure-global-wiring.ps1'
        $extra = @()
        $origemNota = ''
        $tmpEnsure = Join-Path ([IO.Path]::GetTempPath()) ('ensure-origem-' + [guid]::NewGuid().ToString('N'))
        try {
            $ref = if ($env:FRAMEWORK_HOOKS_REF) { $env:FRAMEWORK_HOOKS_REF } else { 'origin/main' }
            $ehGit = $false
            if (Get-Command git -ErrorAction SilentlyContinue) {
                $null = & git -C $projectRoot rev-parse --is-inside-work-tree 2>$null
                $ehGit = ($LASTEXITCODE -eq 0)
            }
            if (-not $ehGit -or $ref -eq 'WORKTREE') {
                $ensureScript = Join-Path $projectRoot 'tools\hooks\ensure-global-wiring.ps1'
                $extra = @('-RepoDir', $projectRoot)
            } else {
                $commit = "$(& git -C $projectRoot rev-parse --verify --quiet "${ref}^{commit}" 2>$null)".Trim()
                if ($commit) {
                    New-Item -ItemType Directory -Path $tmpEnsure -Force | Out-Null
                    $zip = Join-Path $tmpEnsure 'ensure.zip'
                    & git -C $projectRoot archive --format=zip -o $zip $commit -- 'tools/hooks/ensure-global-wiring.ps1' 2>$null
                    $doRef = Join-Path $tmpEnsure 'tools\hooks\ensure-global-wiring.ps1'
                    if ($LASTEXITCODE -eq 0) {
                        Add-Type -AssemblyName System.IO.Compression.FileSystem
                        [IO.Compression.ZipFile]::ExtractToDirectory($zip, $tmpEnsure)
                    }
                    if (Test-EnsureContrato $doRef) {
                        $ensureScript = $doRef
                        $extra = @('-RepoDir', $projectRoot, '-Ref', $commit)
                    } else {
                        $origemNota = " | hooks NAO instalados: ensure de '$ref' anterior ao ADR-130 (git fetch)"
                    }
                } else {
                    $origemNota = " | hooks NAO instalados: ref '$ref' ausente (outro ref: FRAMEWORK_HOOKS_REF)"
                }
            }
            if (Test-EnsureContrato $ensureScript) {
                & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ensureScript @extra 2>$null
                if ($LASTEXITCODE -eq 10) { $healNote = ' | auto-heal: hooks globais re-wirados (ADR-027)' }
            } elseif (-not $origemNota) {
                $origemNota = ' | wiring global NAO reafirmado: ensure sem ENSURE-CONTRATO 2 (ADR-130)'
            }
            $healNote += $origemNota
        } catch {
        } finally {
            Remove-Item $tmpEnsure -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    $msg  = "Framework sync: $skillCount skills + $agentCount agents + $hookCount hooks + $workflowCount workflows$globalNote -> ~/.claude/$healNote"
    $json = @{ systemMessage = $msg } | ConvertTo-Json -Compress
    Write-Output $json
}
catch {
    [Console]::Error.WriteLine("[framework-sync] warning: $($_.Exception.Message)")
}

exit 0
