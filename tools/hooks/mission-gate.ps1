# mission-gate.ps1 — SessionStart hook: gate de product_type/escopo (ADR-022)
#
# Injeta additionalContext orientando o PMO a declarar/confirmar `product_type` (e o escopo do
# discovery) conforme o MODO DE EXECUÇÃO (ADR-005). 3 modos espelham o Mission Gate da pesquisa:
#   BRIEFING  — sem mission.md           -> PMO deve declarar antes de avançar a J2+.
#   ADVANCE   — mission.md sem product_type -> declarar/confirmar.
#   STANDARD  — product_type presente     -> ecoa o tipo + papéis ativados (se a app definir o mapa).
# Confirmação proporcional ao modo: autosuficiente confirma 1× no briefing; avançado/padrão durante.
#
# AGNÓSTICO (P12): a taxonomia de product_type e o mapa tipo->papel são da APLICAÇÃO ativa,
# lidos de exemplos/dominio-software/product-types.txt se existir; ausente -> default agnóstico.
# Fail-soft: nunca bloqueia a sessão (exit 0). Contrato SessionStart: additionalContext em stdout.

$ErrorActionPreference = 'Stop'

function Emit([string]$ctx) {
    $out = @{ hookSpecificOutput = @{ hookEventName = 'SessionStart'; additionalContext = $ctx } } |
        ConvertTo-Json -Compress -Depth 6
    Write-Output $out
    exit 0
}

try {
    $raw = [Console]::In.ReadToEnd()
    $cwd = $PWD.Path
    if ($raw) { try { $h = $raw | ConvertFrom-Json; if ($h.cwd) { $cwd = [string]$h.cwd } } catch { } }

    # Modo de execução (ADR-005) — define a fraseologia da confirmação.
    $mode = 'default'
    # $HOME e a variavel automatica cross-platform (PS 5.1 Windows + pwsh POSIX); $env:USERPROFILE
    # e NULL no Linux/macOS e fazia o Join-Path lancar sob ErrorActionPreference=Stop -> stdout vazio
    # (pego pelo CI cross-platform, ADR-040). mission-gate.sh ja usa $HOME.
    $homeDir = if ($env:USERPROFILE) { $env:USERPROFILE } elseif ($HOME) { $HOME } else { '~' }
    $modeFile = Join-Path $homeDir '.claude/framework-mode.json'
    if (Test-Path $modeFile) {
        try { $m = Get-Content -Raw -LiteralPath $modeFile | ConvertFrom-Json; if ($m.mode) { $mode = [string]$m.mode } } catch { }
    }
    $confDuring = if ($mode -eq 'autosuficiente') { 'autonomia (product_type ja confirmado no briefing).' }
                  else { 'confirme product_type com o dono antes de avancar a juncao (J2+).' }

    # mission.md (lar do escopo declarado + product_type — ADR-022/010/012).
    $missionCandidates = @(
        (Join-Path $cwd 'mission.md'),
        (Join-Path $cwd 'docs/mission.md'),
        (Join-Path $cwd 'docs/specs/mission.md')
    )
    $mission = $missionCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

    if (-not $mission) {
        Emit ("[mission-gate ADR-022] BRIEFING: sem mission.md. Antes de avancar para implementacao (J2+), " +
              "o PMO deve declarar em mission.md: product_type + escopo (regulado? alto-risco? semantica? gaps? handoff?). " +
              "Modo=$mode -> $confDuring")
    }

    $content = Get-Content -Raw -LiteralPath $mission -ErrorAction Stop
    $pt = $null
    # Formato canônico (inline, estilo YAML): "product_type: <valor>".
    if ($content -match '(?m)^\s*product_type:\s*(.+?)\s*$') { $pt = $Matches[1].Trim() }
    # Fallback tolerante: heading markdown "## product_type" seguido do valor na próxima linha não-vazia.
    if (-not $pt -or $pt -match '^<.*>$') {
        if ($content -match '(?ims)^\s*#{1,6}\s*product_type\s*\r?\n+\s*([^\s<#].*?)\s*$') { $pt = $Matches[1].Trim() }
    }

    if (-not $pt -or $pt -match '^<.*>$') {
        Emit ("[mission-gate ADR-022] ADVANCE: mission.md presente mas sem product_type valido. " +
              "Declare 'product_type: <tipo>' antes de J2+. Modo=$mode -> $confDuring")
    }

    # Mapa tipo->papel da aplicação ativa (agnóstico: 1º product-types.txt sob qualquer app em
    # exemplos/*/ — convenção, não acoplado a uma distribuição específica). Só se existir.
    $roles = ''
    $mapFile = Get-ChildItem -Path (Join-Path $cwd 'exemplos') -Filter 'product-types.txt' -Recurse -Depth 1 -ErrorAction SilentlyContinue |
        Select-Object -First 1 -ExpandProperty FullName
    if ($mapFile -and (Test-Path $mapFile)) {
        $line = Select-String -LiteralPath $mapFile -Pattern ('^\s*' + [regex]::Escape($pt) + '\s*[:=]') -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($line) { $roles = ' Papeis ativados (app): ' + (($line.Line -replace '^[^:=]*[:=]\s*', '').Trim()) + '.' }
    }

    Emit ("[mission-gate ADR-022] STANDARD: product_type='$pt' declarado. Modo=$mode -> $confDuring$roles")
}
catch {
    [Console]::Error.WriteLine("[mission-gate] warning (nao-bloqueante): $($_.Exception.Message)")
    exit 0
}
