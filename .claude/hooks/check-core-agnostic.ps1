# check-core-agnostic.ps1 - Hook SessionStart: avisa se o NUCLEO vazou norma de dominio.
# ADR-020 (v1.20.0) - "da prosa ao mecanismo" aplicado ao Principio 12 / regra #5 do qa-critic.
# A regra anti-vazamento era prosa e falhou >=2x (ALCOA+/ANP/... pegos pelo dono). Este hook torna
# a deteccao um MECANISMO em runtime: roda tools/check_core_agnostic.py a cada boot.
#
# Politica (honesta, fail-soft como check-repo-sync):
#  - Roda o linter (read-only). Se achar vazamento (exit!=0), injeta AVISO para o agente/dono.
#  - NUNCA bloqueia a sessao (sempre exit 0). E sinal, nao gate de merge (o gate e CI/pre-commit + canario).
#  - Se python ou o linter nao existirem, silencioso (exit 0) - nao quebra ambientes sem Python.
#
# Espelhado para ~/.claude/hooks/ por sync-global.ps1.

$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false

function Emit([string]$ctx) {
    $json = @{ hookSpecificOutput = @{ hookEventName = 'SessionStart'; additionalContext = $ctx } } |
        ConvertTo-Json -Compress -Depth 5
    Write-Output $json
    exit 0
}

try {
    $cwd = if ($env:CLAUDE_PROJECT_DIR -and (Test-Path $env:CLAUDE_PROJECT_DIR)) {
        $env:CLAUDE_PROJECT_DIR
    } else { (Get-Location).Path }

    $linter = Join-Path $cwd 'tools\check_core_agnostic.py'
    if (-not (Test-Path $linter)) { exit 0 }  # repo sem o linter -> silencioso

    # Resolve interpretador Python (python > py > python3). Sem Python -> silencioso.
    $py = $null
    foreach ($cand in @('python', 'py', 'python3')) {
        $cmd = Get-Command $cand -ErrorAction SilentlyContinue
        if ($cmd) { $py = $cmd.Source; break }
    }
    if (-not $py) { exit 0 }

    Push-Location $cwd
    try {
        $out = & $py 'tools/check_core_agnostic.py' 2>&1
        $code = $LASTEXITCODE
    } finally { Pop-Location }

    if ($code -ne 0) {
        $leaks = ($out | Where-Object { $_ -match '^LEAK ' }) -join "`n"
        if ([string]::IsNullOrWhiteSpace($leaks)) {
            # exit!=0 SEM linhas LEAK = linter nao rodou (denylist ausente/vazia, erro de Python).
            # Aviso PRECISO (nao mascarar como "vazamento"); fail-soft mantido.
            Emit "# AVISO (ADR-020): o linter de agnosticismo retornou erro (exit $code) sem achados de vazamento. Provavel config (tools/agnostic-denylist.txt ausente/vazia) ou ambiente. Rode: python tools/check_core_agnostic.py"
        }
        Emit (@"
# AVISO (ADR-020): vazamento de norma de dominio no NUCLEO

O linter de agnosticismo (``tools/check_core_agnostic.py``) detectou identificador de norma
regulatoria de dominio no nucleo operativo (viola Principio 12 / regra #5 do qa-critic):

$leaks

Acao: remova a mencao (o nucleo e agnostico; norma de dominio vive em ``docs/``, ``exemplos/`` ou
config de aplicacao) OU, se for mencao legitima, adicione o sentinela ``lint-agnostic:allow`` na linha
com justificativa. Rode ``python tools/check_core_agnostic.py`` para reverificar.
"@)
    }
    # núcleo limpo -> silencioso
    exit 0
} catch {
    # fail-soft: qualquer erro nao pode quebrar o boot
    exit 0
}
