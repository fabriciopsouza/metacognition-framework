# effect-gate.ps1 -- PreToolUse hook: deny/ask-backstop por EFEITO, motor de regras (ADR-039, estende ADR-015)
#
# NAO e um classificador geral. E um BACKSTOP conservador default-ALLOW. A POLITICA vive em
# tools/effect-rules.json (familia -> tier -> decision); este hook so a INTERPRETA. Familias:
# mass-destruction, history-rewrite, escalation-persistence, exfiltration, resource-exhaustion.
# T3 inequivoco -> deny; T2 ambiguo -> ask; resto -> allow. Adicionar regra = editar o .json (dado).
#
# Contrato Claude Code (P1): le JSON do hook em stdin; bloquear = exit 0 + JSON permissionDecision:deny;
# pedir confirmacao = permissionDecision:ask. So inspeciona Bash/PowerShell (nao afetado pelo bug #37210).
# Erro interno / json ausente -> loga em stderr e NAO bloqueia (exit 0): a camada fail-closed e o
# managed-settings (ADR-015), nao este hook.
#
# ASCII-ONLY (proposital): PS 5.1 le fonte sem-BOM como cp1252 e quebra em char multibyte. Manter ASCII.
# Regex em subconjunto comum .NET e POSIX-ERE (sem \s \b \d \w) p/ paridade .ps1 vs .sh (effect-gate.sh).

$ErrorActionPreference = 'Stop'

function Emit([string]$decision, [string]$reason) {
    $out = @{
        hookSpecificOutput = @{
            hookEventName            = 'PreToolUse'
            permissionDecision       = $decision
            permissionDecisionReason = "effect-gate (ADR-039) [$decision]: $reason"
        }
    } | ConvertTo-Json -Compress -Depth 6
    Write-Output $out
    exit 0
}

try {
    $raw = [Console]::In.ReadToEnd()
    if (-not $raw) { exit 0 }
    $hook = $raw | ConvertFrom-Json
    $tool = $hook.tool_name
    if ($tool -ne 'Bash' -and $tool -ne 'PowerShell') { exit 0 }
    $cmd = ''
    if ($hook.tool_input -and $hook.tool_input.command) { $cmd = [string]$hook.tool_input.command }
    if (-not $cmd) { exit 0 }
    $c = $cmd.ToLower()

    $rulesPath = Join-Path (Split-Path (Split-Path $PSCommandPath -Parent) -Parent) 'effect-rules.json'
    if (-not (Test-Path $rulesPath)) {
        [Console]::Error.WriteLine("[effect-gate] effect-rules.json ausente - fail-open (allow)")
        exit 0
    }
    $policy = Get-Content $rulesPath -Raw -Encoding UTF8 | ConvertFrom-Json

    $askReason = $null
    foreach ($rule in $policy.rules) {
        $allMatch = $true
        foreach ($p in @($rule.all)) {
            if ($c -notmatch $p) { $allMatch = $false; break }
        }
        if (-not $allMatch) { continue }
        $blockedByNone = $false
        foreach ($p in @($rule.none)) {
            if ($p -and $c -match $p) { $blockedByNone = $true; break }
        }
        if ($blockedByNone) { continue }
        if ($rule.decision -eq 'deny') {
            Emit 'deny' "$($rule.reason). Requer gate humano (four-eyes fora do canal)."
        }
        elseif ($rule.decision -eq 'ask' -and -not $askReason) {
            $askReason = [string]$rule.reason
        }
    }
    if ($askReason) { Emit 'ask' $askReason }
    exit 0
}
catch {
    [Console]::Error.WriteLine("[effect-gate] warning (nao-bloqueante): $($_.Exception.Message)")
    exit 0
}
