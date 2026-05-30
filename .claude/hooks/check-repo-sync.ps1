# check-repo-sync.ps1 - Hook SessionStart: detecta (e, quando seguro, corrige) repo desatualizado.
# ADR-019 (v1.19.0) - "da prosa ao mecanismo" no boot: o /start-session fazia file-first sobre o
# clone local sem git fetch, lendo retrato congelado (caso real: sessao operou 41 commits atras de
# origin/main sem saber). Este hook torna a sincronizacao um MECANISMO em runtime, nao prosa.
#
# Politica de seguranca (honesta - nao promete o que e arriscado):
#  - `git fetch` e SEMPRE feito (read-only, seguro).
#  - AUTO-PULL so quando provadamente seguro: working tree LIMPO E fast-forward possivel -> pull --ff-only.
#  - Caso contrario (tree sujo, ou nao-ff/divergiu): NAO mexe; injeta AVISO para o agente/dono decidir.
#  - Nunca faz merge, rebase, pull nao-ff, ou toca tree sujo. Falha soft (warning + exit 0): nunca bloqueia.
#
# Disparado em SessionStart (.claude/settings.json) ANTES do inject-start-session, para que o
# STATUS do PMO ja reflita o estado real. Espelhado para ~/.claude/hooks/ por sync-global.ps1.

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

    # Nao e repo git -> nada a fazer (silencioso).
    $inside = (git -C $cwd rev-parse --is-inside-work-tree 2>$null)
    if ($inside -ne 'true') { Emit '' }

    # Branch atual + upstream. Sem upstream, compara com origin/main (alvo de integracao do framework).
    $branch = (git -C $cwd rev-parse --abbrev-ref HEAD 2>$null)
    $upstream = (git -C $cwd rev-parse --abbrev-ref '@{upstream}' 2>$null)
    if (-not $upstream) { $upstream = 'origin/main' }

    # FETCH (sempre - read-only, seguro). Timeout real vem do settings.json (campo timeout do hook).
    git -C $cwd fetch --quiet 2>$null | Out-Null

    # behind/ahead vs upstream.
    $counts = (git -C $cwd rev-list --left-right --count "$upstream...HEAD" 2>$null)
    if (-not $counts) { Emit '' }
    $parts = $counts -split '\s+'
    $behind = [int]$parts[0]
    $ahead  = if ($parts.Count -gt 1) { [int]$parts[1] } else { 0 }

    if ($behind -eq 0) { Emit '' }  # em dia -> silencioso (sem ruido).

    # Esta atras. Seguro auto-atualizar? Criterio: SEM modificacoes RASTREADAS (untracked NAO bloqueia
    # -- qa-critic ADR-019: o caso comum "clone + nota local + main avancou" deve auto-atualizar; o
    # --ff-only e a trava final, aborta com seguranca se um untracked fosse sobrescrito) + fast-forward.
    $dirty = (git -C $cwd status --porcelain --untracked-files=no 2>$null)
    $isClean = [string]::IsNullOrWhiteSpace($dirty)
    $ffPossible = $false
    if ($isClean) {
        # ff possivel sse HEAD e ancestral do upstream (nenhum commit local divergente).
        git -C $cwd merge-base --is-ancestor HEAD "$upstream" 2>$null
        $ffPossible = ($LASTEXITCODE -eq 0)
    }

    if ($isClean -and $ffPossible) {
        git -C $cwd pull --ff-only --quiet 2>$null | Out-Null
        $pullRc = $LASTEXITCODE   # exit code do pull e o sinal autoritativo (nao inferir so por behind)
        $newBehind = (git -C $cwd rev-list --count "HEAD..$upstream" 2>$null)
        if ($pullRc -eq 0 -and ($newBehind -eq '0' -or $newBehind -eq 0)) {
            Emit "# Repo sync (ADR-019)`n✅ Repo estava $behind commit(s) atras de ``$upstream`` e foi AUTO-ATUALIZADO (fast-forward, sem modificacoes rastreadas). Agora em dia. Reconcilie WIP sobre o estado novo."
        } else {
            Emit "# Repo sync (ADR-019)`n⚠️ Tentei auto-atualizar (estava $behind atras de ``$upstream``) mas ``pull --ff-only`` NAO concluiu (rc=$pullRc; ex.: untracked colidiria, lock, ou pre-merge hook). Rode ``git pull`` manual e verifique ANTES de reconciliar WIP."
        }
    } else {
        if (-not $isClean) {
            $motivo = 'working tree com modificacoes RASTREADAS'
            $acao   = 'commit ou stash, depois ``git pull``'
        } else {
            $motivo = 'historico DIVERGIU (nao-fast-forward)'
            $acao   = 'rebase/merge manual de ``' + $upstream + '``'
        }
        Emit "# Repo sync (ADR-019)`n⚠️ Repo esta $behind commit(s) atras de ``$upstream`` (e $ahead a frente). NAO auto-atualizei: $motivo. **Antes de reconciliar WIP / afirmar estado:** $acao. Operar agora = ler retrato congelado (licao method-audit 2026-05-30)."
    }
}
catch {
    [Console]::Error.WriteLine("[check-repo-sync] warning (nao-bloqueante): $($_.Exception.Message)")
    exit 0
}
