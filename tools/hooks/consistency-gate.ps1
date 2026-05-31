# consistency-gate.ps1 — auditoria de consistência do repo-framework (ADR-030)
#
# PROBLEMA QUE RESOLVE: ao fechar um bloco/release, divergências silenciosas se acumulam —
# versão do README ≠ CHANGELOG; ADR ainda "Proposto" depois do feature mergeado; sem
# checkpoint no history; artefato transiente (docs/_intake/) esquecido no repo; e — pior
# para "estou divulgando" — COMMITS NÃO-PUSHADOS (trabalho que existe só no PC; decisão #5:
# o recovery real é a CONTA GitHub, então o que não subiu não está protegido).
#
# MECANISMO: lê o estado do repo e reporta 6 dimensões. NÃO bloqueia (fail-soft): é um
# espelho para o /checkpoint, o retrospective gate (start-session 2.5) e o fechamento de
# release. Exit code = nº de inconsistências (0 = limpo) para uso programático.
#
# Uso:  consistency-gate.ps1 [-RepoDir <path>] [-Json]
#   -RepoDir: raiz do repo (default: resolve a partir do caminho do script).
#   -Json:    emite resultado estruturado em vez do relatório humano.
#
# Domínio-agnóstico no MÉTODO (lê o que o repo declara); os caminhos (README/CHANGELOG/
# docs/adr/history) são convenção DESTE repo-framework — outro projeto adapta os ponteiros.

param([string]$RepoDir = "", [switch]$Json)

$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false

# Resolver raiz do repo.
if (-not $RepoDir) {
    $RepoDir = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
}
if (-not (Test-Path $RepoDir)) {
    [Console]::Error.WriteLine("[consistency-gate] RepoDir inexistente: $RepoDir"); exit 0
}

$issues  = New-Object System.Collections.ArrayList
$results = [ordered]@{}

function Add-Issue([string]$dim, [string]$msg) {
    [void]$issues.Add([pscustomobject]@{ dimension = $dim; message = $msg })
}
function Rel([string]$p) { Join-Path $RepoDir $p }

# --- Dim 1: version-sync (README badge × CHANGELOG topo × git tag) -------------
$verReadme = $null; $verChangelog = $null; $verTag = $null
try {
    # -Encoding UTF8 obrigatório: PS 5.1 lê em ANSI por default e 'Versão' viraria 'VersÃ£o'
    # (mojibake), fazendo o regex com 'ã' não casar. Mesmo motivo de [Console]::OutputEncoding.
    $readme = Get-Content (Rel 'README.md') -Raw -Encoding UTF8 -ErrorAction Stop
    if ($readme -match '(?im)^\s*>\s*\*\*Vers[ãa]o:\*\*\s*([0-9]+\.[0-9]+\.[0-9]+)') { $verReadme = $matches[1] }
} catch { }
try {
    $clog = Get-Content (Rel 'CHANGELOG.md') -Encoding UTF8 -ErrorAction Stop
    foreach ($ln in $clog) { if ($ln -match '^\s*##\s*\[([0-9]+\.[0-9]+\.[0-9]+)\]') { $verChangelog = $matches[1]; break } }
} catch { }
try {
    $tags = git -C $RepoDir tag --sort=-v:refname 2>$null
    if ($tags) { $verTag = ([string]($tags | Select-Object -First 1)).TrimStart('v') }
} catch { }

if ($verReadme -and $verChangelog -and ($verReadme -ne $verChangelog)) {
    Add-Issue 'version-sync' "README ($verReadme) != CHANGELOG topo ($verChangelog)"
}
$results['version-sync'] = [ordered]@{ readme = $verReadme; changelog = $verChangelog; latest_tag = $verTag }

# --- Dim 2: ADR-status (Proposto que podem precisar virar Aceito) -------------
$proposed = @()
$adrDir = Rel 'docs/adr'
if (Test-Path $adrDir) {
    Get-ChildItem $adrDir -Filter '*.md' | Where-Object { $_.Name -notmatch '^000' } | ForEach-Object {
        $c = Get-Content $_.FullName -Raw
        if ($c -match '(?im)^\s*-?\s*Status:\s*Proposto') { $proposed += $_.Name }
    }
}
if ($proposed.Count -gt 0) {
    Add-Issue 'adr-status' "$($proposed.Count) ADR(s) em 'Proposto' (rever no merge): $($proposed -join ', ')"
}
$results['adr-status'] = [ordered]@{ proposed = $proposed }

# --- Dim 3: checkpoint no history para a versão corrente -----------------------
$histHasCheckpoint = $false
try {
    $hist = Get-Content (Rel 'history.md') -Raw -Encoding UTF8 -ErrorAction Stop
    $verForCheck = if ($verChangelog) { $verChangelog } else { $verReadme }
    if ($verForCheck -and ($hist -match [regex]::Escape($verForCheck))) { $histHasCheckpoint = $true }
    if (-not $histHasCheckpoint) {
        Add-Issue 'checkpoint' "history.md sem referência à versão corrente ($verForCheck) — checkpoint ausente?"
    }
} catch {
    Add-Issue 'checkpoint' "history.md não encontrado/legível na raiz"
}
$results['checkpoint'] = [ordered]@{ history_has_current_version = $histHasCheckpoint }

# --- Dim 4: contagens (ADRs: range, gaps, duplicatas) --------------------------
$adrNums = @()
if (Test-Path $adrDir) {
    Get-ChildItem $adrDir -Filter '*.md' | ForEach-Object {
        if ($_.Name -match '^(\d{3})-') { $adrNums += [int]$matches[1] }
    }
}
$dups = @(); $adrMin = $null; $adrMax = $null
if ($adrNums.Count -gt 0) {
    $adrMin = ($adrNums | Measure-Object -Minimum).Minimum
    $adrMax = ($adrNums | Measure-Object -Maximum).Maximum
    # Só DUPLICATAS são inconsistência. Lacunas de numeração são NORMAIS (ADRs podem ser
    # mesclados/abandonados); flagá-las geraria falso-positivo. Range/contagem = informativo.
    $seen = @{}
    foreach ($n in $adrNums) { if ($seen.ContainsKey($n)) { $dups += $n } else { $seen[$n] = $true } }
    if ($dups.Count -gt 0) { Add-Issue 'contagens' "ADRs com número DUPLICADO: $($dups -join ', ')" }
}
$results['contagens'] = [ordered]@{ adr_count = $adrNums.Count; adr_min = $adrMin; adr_max = $adrMax; adr_dups = $dups }

# --- Dim 5: commits não-pushados (decisão #5 — o que não subiu não está protegido) -
$unpushed = $null; $branch = $null
try {
    $branch = (git -C $RepoDir rev-parse --abbrev-ref HEAD 2>$null) | Out-String
    $branch = $branch.Trim()
    $cnt = (git -C $RepoDir rev-list --count '@{upstream}..HEAD' 2>$null) | Out-String
    $cnt = $cnt.Trim()
    if ($cnt -match '^\d+$') {
        $unpushed = [int]$cnt
        if ($unpushed -gt 0) { Add-Issue 'unpushed' "$unpushed commit(s) não-pushado(s) em '$branch' (recovery real = conta GitHub; push)" }
    } else {
        Add-Issue 'unpushed' "branch '$branch' sem upstream configurado (commits locais não protegidos)"
    }
} catch {
    Add-Issue 'unpushed' "não foi possível avaliar commits não-pushados"
}
$results['unpushed'] = [ordered]@{ branch = $branch; ahead = $unpushed }

# --- Dim 6: artefatos transientes em docs/_intake/ (remover no fechamento) ------
$transients = @()
$intakeDir = Rel 'docs/_intake'
if (Test-Path $intakeDir) {
    $transients = @(Get-ChildItem $intakeDir -File -Recurse | ForEach-Object { $_.Name })
    if ($transients.Count -gt 0) {
        Add-Issue 'transients' "$($transients.Count) artefato(s) transiente(s) em docs/_intake/ (remover no fechamento): $($transients -join ', ')"
    }
}
$results['transients'] = [ordered]@{ files = $transients }

# --- Saída ---------------------------------------------------------------------
$summary = [ordered]@{
    repo            = $RepoDir
    n_issues        = $issues.Count
    consistent      = ($issues.Count -eq 0)
    dimensions      = $results
    issues          = @($issues)
}

if ($Json) {
    Write-Output ($summary | ConvertTo-Json -Depth 8)
    exit $issues.Count
}

Write-Output "==== consistency-gate (ADR-030) — $RepoDir ===="
Write-Output ("versão: README={0} | CHANGELOG={1} | tag={2}" -f $verReadme, $verChangelog, $verTag)
Write-Output ("ADRs: {0} arquivo(s); Proposto: {1}" -f $adrNums.Count, ($(if($proposed){$proposed -join ', '}else{'nenhum'})))
Write-Output ("checkpoint history: {0}" -f $(if($histHasCheckpoint){'OK'}else{'AUSENTE'}))
Write-Output ("não-pushados em '{0}': {1}" -f $branch, $(if($null -ne $unpushed){$unpushed}else{'?'}))
Write-Output ("transientes _intake: {0}" -f $(if($transients.Count){$transients -join ', '}else{'nenhum'}))
Write-Output "----------------------------------------------"
if ($issues.Count -eq 0) {
    Write-Output "RESULTADO: CONSISTENTE (0 inconsistências)"
} else {
    Write-Output "RESULTADO: $($issues.Count) inconsistência(s):"
    foreach ($i in $issues) { Write-Output ("  [{0}] {1}" -f $i.dimension, $i.message) }
}
exit $issues.Count
