# compaction-gate.ps1 — PreCompact hook: backstop de digest (ADR-021, prosa→mecanismo do ADR-016)
#
# NÃO é o juiz de completude do digest. É um BACKSTOP conservador que bloqueia SÓ o caso
# catastrófico inequívoco: history.md ausente OU sem nenhum checkpoint (= nada foi persistido
# nesta sessão e a compaction destruiria o WIP). Fora disso: ALLOW + lembrete não-bloqueante.
# A verificação de digest *atual* (freshness) é disciplina do /checkpoint — o hook não detecta
# freshness de forma stateless (limitação declarada no ADR-021; Princípio 11 honesto).
#
# Contrato PreCompact (Claude Code): lê JSON do hook em stdin (trigger: auto|manual; cwd).
# Para BLOQUEAR: stdout {"decision":"block","reason":...} (exit 0). Allow: exit 0 sem decision.
# Erro interno -> stderr + exit 0 (fail-open): travar toda compaction por bug do hook seria pior
# que o risco que ele mitiga (mesma filosofia do effect-gate / ADR-015).
#
# Instalar: wired em .claude/settings.json (hooks.PreCompact) com path tools\hooks\compaction-gate.ps1.

$ErrorActionPreference = 'Stop'

function Allow { exit 0 }
function Block([string]$reason) {
    $out = @{ decision = 'block'; reason = $reason } | ConvertTo-Json -Compress -Depth 4
    Write-Output $out
    exit 0
}

try {
    $raw = [Console]::In.ReadToEnd()
    $cwd = $PWD.Path
    if ($raw) {
        try {
            $hook = $raw | ConvertFrom-Json
            if ($hook.cwd) { $cwd = [string]$hook.cwd }
        } catch { }   # payload malformado não bloqueia
    }

    # Localiza o store persistente de notas (history.md na raiz; fallbacks).
    $candidates = @(
        (Join-Path $cwd 'history.md'),
        (Join-Path $cwd 'HISTORY.md'),
        (Join-Path $cwd '.claude/memory/HISTORY.md')
    )
    $hist = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1

    if (-not $hist) {
        Block ('history.md nao encontrado em "' + $cwd + '": nada foi persistido nesta sessao. ' +
               'Rode /checkpoint (grava history.md / digest) ANTES de compactar — ADR-016/021. ' +
               'Compactar agora perderia o WIP nao salvo.')
    }

    $content = Get-Content -Raw -LiteralPath $hist -ErrorAction Stop
    # Checkpoint = heading de sessao com data ISO no inicio da linha (## YYYY-MM-DD...).
    if ($content -notmatch '(?m)^##\s+\d{4}-\d{2}-\d{2}') {
        Block ('history.md existe mas nao tem nenhum checkpoint (## YYYY-MM-DD): ' +
               'rode /checkpoint antes de compactar (ADR-016/021).')
    }

    # Caso normal: há histórico persistido. Allow + lembrete não-bloqueante.
    [Console]::Error.WriteLine('[compaction-gate] compaction prestes a ocorrer — confirme que o ' +
        'digest/checkpoint reflete o WIP atual (ADR-016). Nao-bloqueante.')
    Allow
}
catch {
    [Console]::Error.WriteLine("[compaction-gate] warning (nao-bloqueante): $($_.Exception.Message)")
    exit 0   # fail-open
}
