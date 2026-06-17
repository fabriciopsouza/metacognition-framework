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

    # === Dimensao 1 (ADR-019/060): sincronia vs o PROPRIO upstream da branch (auto-pull --ff-only). ===
    $upstream = (git -C $cwd rev-parse --abbrev-ref '@{upstream}' 2>$null)
    if (-not $upstream) { $upstream = 'origin/main' }

    # FETCH (sempre - read-only, seguro). Timeout real vem do settings.json (campo timeout do hook).
    git -C $cwd fetch --quiet 2>$null | Out-Null

    $upstreamMsg = ''
    $counts = (git -C $cwd rev-list --left-right --count "$upstream...HEAD" 2>$null)
    if ($counts) {
        $parts = $counts -split '\s+'
        $behind = [int]$parts[0]
        $ahead  = if ($parts.Count -gt 1) { [int]$parts[1] } else { 0 }
        if ($behind -gt 0) {
            # Esta atras. Seguro auto-atualizar? SEM modificacoes RASTREADAS (untracked NAO bloqueia --
            # --ff-only e a trava final) + fast-forward (HEAD ancestral do upstream).
            $dirty = (git -C $cwd status --porcelain --untracked-files=no 2>$null)
            $isClean = [string]::IsNullOrWhiteSpace($dirty)
            $ffPossible = $false
            if ($isClean) {
                git -C $cwd merge-base --is-ancestor HEAD "$upstream" 2>$null
                $ffPossible = ($LASTEXITCODE -eq 0)
            }
            if ($isClean -and $ffPossible) {
                git -C $cwd pull --ff-only --quiet 2>$null | Out-Null
                $pullRc = $LASTEXITCODE
                $newBehind = (git -C $cwd rev-list --count "HEAD..$upstream" 2>$null)
                if ($pullRc -eq 0 -and ($newBehind -eq '0' -or $newBehind -eq 0)) {
                    $upstreamMsg = "✅ Repo estava $behind commit(s) atras de ``$upstream`` e foi AUTO-ATUALIZADO (fast-forward, sem modificacoes rastreadas). Agora em dia. Reconcilie WIP sobre o estado novo."
                } else {
                    $upstreamMsg = "⚠️ Tentei auto-atualizar (estava $behind atras de ``$upstream``) mas ``pull --ff-only`` NAO concluiu (rc=$pullRc). Rode ``git pull`` manual e verifique ANTES de reconciliar WIP."
                }
            } else {
                if (-not $isClean) {
                    $motivo = 'working tree com modificacoes RASTREADAS'; $acao = 'commit ou stash, depois ``git pull``'
                } else {
                    $motivo = 'historico DIVERGIU (nao-fast-forward)'; $acao = 'rebase/merge manual de ``' + $upstream + '``'
                }
                $upstreamMsg = "⚠️ Repo esta $behind commit(s) atras de ``$upstream`` (e $ahead a frente). NAO auto-atualizei: $motivo. **Antes de reconciliar WIP / afirmar estado:** $acao. Operar agora = ler retrato congelado."
            }
        }
    }

    # === Dimensao 2 (ORTOGONAL, ADR-084): defasagem vs a branch de INTEGRACAO (origin/HEAD). ===
    # O gap do method-audit: uma feature branch pode estar 0 atras do PROPRIO upstream e ainda assim
    # N atras de origin/main = retrato congelado do framework. Baseline AGNOSTICA (ADR-020) via
    # origin/HEAD -> fallback origin/main -> origin/master. NAO auto-pula (nao se faz ff de main numa
    # feature branch): escreve marker persistente que o route-gate repete por-turno ate resolver/reconhecer.
    $baselineMsg = ''
    $base = ''
    $ref = (git -C $cwd symbolic-ref --quiet refs/remotes/origin/HEAD 2>$null)
    if ($ref -and $ref.StartsWith('refs/remotes/')) { $base = $ref.Substring('refs/remotes/'.Length) }
    if (-not $base) {
        foreach ($cand in @('origin/main','origin/master')) {
            git -C $cwd rev-parse --verify --quiet $cand 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { $base = $cand; break }
        }
    }
    $marker  = Join-Path $cwd '.claude/.stale-vs-main'
    $ackFile = Join-Path $cwd '.claude/.stale-vs-main.ack'
    if ($base -and $base -eq $upstream) {
        # Branch de integracao E o proprio upstream (ex.: estou NA main) -> dimensao 1 ja cobre.
        # Cirurgico: nada de marker (preserva C1-C5). Limpa marker orfao de outra branch.
        Remove-Item -Force -ErrorAction SilentlyContinue $marker, $ackFile
        $base = ''
    }
    if ($base) {
        $cntBase = (git -C $cwd rev-list --count "HEAD..$base" 2>$null)
        if ($cntBase) {  # so age se o git RESPONDEU (cnt nao-vazio) -> NUNCA limpa marker por erro de git (qa-critic ADR-084)
            $behindBase = [int]$cntBase
            if ($behindBase -eq 0) {
                Remove-Item -Force -ErrorAction SilentlyContinue $marker, $ackFile  # resolvido -> limpa
            } else {
                $baseSha = (git -C $cwd rev-parse --short $base 2>$null)
                $cur = (git -C $cwd rev-parse --abbrev-ref HEAD 2>$null)
                try {
                    New-Item -ItemType Directory -Force -Path (Join-Path $cwd '.claude') | Out-Null
                    # session= omitido de proposito no fallback ps1 (nao le stdin de SessionStart); campo e informacional, sem consumidor.
                    "behind=$behindBase`nbase=$base`nbase_sha=$baseSha`nsession=`n" | Set-Content -Encoding utf8 -NoNewline $marker
                } catch {}
                $baselineMsg = "⚠️ Voce esta $behindBase commit(s) ATRAS de ``$base`` (branch ``$cur``). O framework MOVEU desde que esta branch saiu: voce le um RETRATO CONGELADO. NAO afirme estado/versao nem edite codigo do nucleo antes de ``git rebase $base`` (ou merge). Persistido em ``.claude/.stale-vs-main`` -> o route-gate REPETE por-turno ate (a) atualizar a branch ou (b) reconhecer: ``git rev-parse --short $base > .claude/.stale-vs-main.ack``."
            }
        }
    }

    $bodies = @($upstreamMsg, $baselineMsg) | Where-Object { $_ }
    if ($bodies.Count -eq 0) { Emit '' }  # em dia nas duas dimensoes -> silencioso
    Emit ("# Repo sync (ADR-019/060/084)`n" + ($bodies -join "`n`n"))
}
catch {
    [Console]::Error.WriteLine("[check-repo-sync] warning (nao-bloqueante): $($_.Exception.Message)")
    exit 0
}
