# overwrite-guard.ps1 - protege contra sobrescrita CEGA de artefato (ADR-037)
#
# GAP de campo: o agente sobrescreveu um relato que JA TINHA conteudo, sem ler nem avisar.
# action-safety classifica por efeito, mas o effect-gate so inspeciona Bash/PowerShell -
# overwrite via tool Write/Edit sobre arquivo com conteudo nao-criado/nao-lido nesta sessao
# (efeito E1 destrutivo) passava.
#
# MECANISMO: dois modos num so script (dispatch por hook_event_name):
#   - PreToolUse(Write|Edit) = GATE: se o path existe, tem conteudo, e NAO esta no manifesto
#     da sessao (nao foi lido nem criado nesta sessao) -> exit 2 (bloqueia, pede LER antes).
#   - PostToolUse(Read|Write|Edit|NotebookEdit) = RECORD: registra o path no manifesto da sessao.
# Intencao: "ler/criar antes de sobrescrever". Ter LIDO o arquivo nesta sessao = overwrite informado.
#
# Anti-viol bug #37210 (permissionDecision:deny ignorado p/ Edit/MCP): usa exit 2 (robusto),
# nao JSON deny. exit 2 devolve o controle ao MODELO com a mensagem (nao e popup humano).
# Manifesto: .agent/brain/session-files.json keyed por session_id (gitignored). Override de teste:
# env OVERWRITE_GUARD_MANIFEST. Fail-open em erro interno (exit 0); record nunca bloqueia.

$ErrorActionPreference = 'Stop'
try {
    $raw = [Console]::In.ReadToEnd()
    if (-not $raw) { exit 0 }
    $hook = $raw | ConvertFrom-Json
    $evt = [string]$hook.hook_event_name
    $tool = [string]$hook.tool_name
    $sid = if ($hook.session_id) { [string]$hook.session_id } else { 'default' }

    $fp = $null
    if ($hook.tool_input) {
        if ($hook.tool_input.file_path) { $fp = [string]$hook.tool_input.file_path }
        elseif ($hook.tool_input.notebook_path) { $fp = [string]$hook.tool_input.notebook_path }
    }
    if (-not $fp) { exit 0 }

    $manifest = $env:OVERWRITE_GUARD_MANIFEST
    if (-not $manifest) {
        $cwd = if ($hook.cwd) { [string]$hook.cwd } else { (Get-Location).Path }
        $manifest = Join-Path $cwd '.agent/brain/session-files.json'
    }

    $data = @{}
    if (Test-Path $manifest) {
        try {
            $json = Get-Content $manifest -Raw -Encoding UTF8 | ConvertFrom-Json
            foreach ($p in $json.PSObject.Properties) { $data[$p.Name] = @($p.Value) }
        } catch {}
    }
    $full = try { [System.IO.Path]::GetFullPath($fp) } catch { $fp }
    # Lista tipada: PowerShell desembrulha array de 1 elemento para escalar (vira string e o
    # '+=' concatena em vez de anexar). [List[string]] evita o bug e mantem semantica de array.
    $known = New-Object 'System.Collections.Generic.List[string]'
    if ($data.ContainsKey($sid)) {
        foreach ($x in @($data[$sid])) { if ($x) { [void]$known.Add([string]$x) } }
    }
    $isKnown = $false
    foreach ($k in $known) { if ($k -ieq $full) { $isKnown = $true; break } }

    if ($evt -eq 'PreToolUse' -and ($tool -eq 'Write' -or $tool -eq 'Edit')) {
        if (-not (Test-Path $full)) { exit 0 }            # arquivo novo
        if ((Get-Item $full).Length -eq 0) { exit 0 }     # vazio
        if ($isKnown) { exit 0 }                          # lido/criado nesta sessao
        [Console]::Error.WriteLine("[overwrite-guard ADR-037] BLOQUEADO: '$fp' existe com conteudo e NAO foi lido nem criado nesta sessao. LEIA o arquivo antes de sobrescrever (anti-overwrite cego).")
        exit 2
    }

    if ($evt -eq 'PostToolUse') {
        if (-not $isKnown) {
            [void]$known.Add($full)
            $data[$sid] = $known.ToArray()
            try {
                $dir = Split-Path $manifest -Parent
                if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
                # ConvertTo-Json pode desembrulhar array de 1 elem para escalar no DISCO; ok, pois
                # a leitura usa @($data[$sid]) que re-arrayza. -AsArray e PS7+ (quebra 5.1) -> nao usar.
                ($data | ConvertTo-Json -Depth 6) | Set-Content -Path $manifest -Encoding UTF8
            } catch {}
        }
    }
    exit 0
}
catch {
    [Console]::Error.WriteLine("[overwrite-guard] warning (nao-bloqueante): $($_.Exception.Message)")
    exit 0
}
