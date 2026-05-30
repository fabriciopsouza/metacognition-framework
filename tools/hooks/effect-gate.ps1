# effect-gate.ps1 — PreToolUse hook: deny-backstop de ações T3 por EFEITO (ADR-015)
#
# NÃO é um classificador geral. É um BACKSTOP conservador dos casos T3 inequívocos
# (E1∩E2 ∩ alto impacto): destruição irrecuperável de raiz/home, format/mkfs/dd em device,
# push --force em branch protegida, fork bomb. O julgamento amplo (E1–E6) é da política
# `_shared/action-safety` + humano. Default = ALLOW (deixa o fluxo normal de permissão seguir).
#
# Contrato Claude Code (P1): lê JSON do hook em stdin; para BLOQUEAR, exit 0 + JSON
# {hookSpecificOutput:{permissionDecision:"deny"}} (mais expressivo que exit 2). Precedência deny>ask>allow.
# Erro interno -> loga em stderr e NÃO bloqueia (exit 0): travar todo tool em bug do hook seria DoS;
# a camada fail-closed real é o managed-settings (ADR-015). Falha-segura mora em camadas, não aqui.
#
# Instalar: copiar para ~/.claude/hooks/ e registrar em settings.json hooks.PreToolUse (matcher "Bash").

$ErrorActionPreference = 'Stop'

function Allow {  # deixa o fluxo de permissão padrão seguir (não decide)
    exit 0
}
function Deny([string]$reason) {
    $out = @{
        hookSpecificOutput = @{
            hookEventName    = 'PreToolUse'
            permissionDecision = 'deny'
            permissionDecisionReason = "effect-gate (ADR-015) T3 negado: $reason. Requer gate humano (four-eyes fora do canal)."
        }
    } | ConvertTo-Json -Compress -Depth 6
    Write-Output $out
    exit 0
}

try {
    $raw = [Console]::In.ReadToEnd()
    if (-not $raw) { Allow }
    $hook = $raw | ConvertFrom-Json
    $tool = $hook.tool_name
    # Só inspeciona ferramentas de execução de shell; demais seguem fluxo normal.
    if ($tool -ne 'Bash' -and $tool -ne 'PowerShell') { Allow }
    $cmd = ''
    if ($hook.tool_input -and $hook.tool_input.command) { $cmd = [string]$hook.tool_input.command }
    if (-not $cmd) { Allow }
    $c = $cmd.ToLower()

    # --- Padrões T3 inequívocos (E1∩E2 ∩ E3/E5). Conservador: só o que é claramente catastrófico. ---
    # 1. rm recursivo-forçado de raiz, home ou ~ (lição JARVIS)
    if ($c -match 'rm\s+(-[a-z]*\s+)*-[a-z]*r[a-z]*f|rm\s+(-[a-z]*\s+)*-[a-z]*f[a-z]*r') {
        if ($c -match 'rm\s+.*\s+(/|~|\$home|/\*|\.\s*$|\*\s*$)' -or $c -match 'rm\s+-[rf]+\s+/(\s|$)' -or $c -match '~/?(\s|$|\*)') {
            Deny 'rm recursivo-forçado atingindo raiz/home/~ (E1+E2)'
        }
    }
    # 2. format / mkfs / dd em device de bloco
    if ($c -match '\bmkfs(\.\w+)?\b' -or $c -match 'format-volume' -or $c -match '\bformat\s+[a-z]:' -or $c -match 'dd\s+.*of=/dev/(sd|nvme|disk|hd)') {
        Deny 'format/mkfs/dd sobre device de bloco (E1+E2)'
    }
    # 3. git push --force em branch protegida (main/master/release/*) — E2+E3
    if ($c -match 'git\s+push' -and ($c -match '--force(?!-with-lease)' -or $c -match '\s-f(\s|$)')) {
        if ($c -match '(origin\s+)?(main|master|release|prod)' -or $c -notmatch 'with-lease') {
            Deny 'git push --force (sem --force-with-lease) potencialmente em branch protegida (E2+E3)'
        }
    }
    # 4. fork bomb
    if ($cmd -match ':\(\)\s*\{\s*:\|:&\s*\}\s*;:') {
        Deny 'fork bomb (E2 — exaustão de recursos)'
    }
    # 5. chmod/chown recursivo em raiz, ou desligar firewall — E5
    if ($c -match '(chmod|chown)\s+-[a-z]*r[a-z]*\s+.*\s+/(\s|$)' -or $c -match 'iptables\s+-f' -or $c -match 'netsh\s+advfirewall\s+set\s+allprofiles\s+state\s+off') {
        Deny 'alteração recursiva de permissão em raiz ou desligamento de firewall (E5)'
    }

    Allow
}
catch {
    [Console]::Error.WriteLine("[effect-gate] warning (nao-bloqueante): $($_.Exception.Message)")
    exit 0   # erro interno nao bloqueia; managed-settings e a camada fail-closed (ADR-015)
}
