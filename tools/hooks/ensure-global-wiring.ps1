# ensure-global-wiring.ps1 — self-heal da wiring de hooks globais (ADR-027)
#
# PROBLEMA: o ~/.claude/settings.json global pode ficar SEM a chave `hooks` (clobber
# do mode-apply autosuficiente — o algoritmo execution-modes §5 manda "preservar hooks",
# mas isso é PROSA: o disco mostrou zero hooks). Sem wiring global, abrir o Claude em
# QUALQUER pasta não-framework dispara zero hooks (falha-raiz do relato AIVI).
#
# MECANISMO (ponto de Arquimedes): este script é chamado pelo sync-global.ps1, que roda
# do settings.json de PROJETO (versionado, estável). Logo, toda vez que o repo-framework
# abre, a wiring GLOBAL é re-afirmada — derrotando o clobber de forma mecânica, não por
# promessa. Idempotente, hook-preserving (NUNCA dropa chave existente), backup + validação.
#
# Garante no ~/.claude/settings.json:
#   - hooks.SessionStart     contém inject-start-session-global.ps1 (auto-boot, ADR-006)
#   - hooks.UserPromptSubmit contém route-gate.ps1                  (roteamento, ADR-027)
#   - hooks.Stop             contém resposta_executiva.py --hook      (mede o formato, sem bloquear; ADR-129)
#   - hooks.UserPromptSubmit contém resposta_executiva.py --lembrete  (molde + achados da resposta anterior)
#
# ADR-130 (incidente de 28/09/2026: wiring novo + script antigo bloqueou TODO prompt):
#   - SONDA: antes de ligar Stop/UserPromptSubmit, roda o script INSTALADO com um JSON de teste do evento e exige
#     exit 0 e stdout vazio. Falhou: não liga e REMOVE a entrada existente daquela flag.
#   - ORIGEM ÚNICA: com -RepoDir, os scripts wirados e este próprio script vêm do MESMO commit, no mesmo passo
#     (git archive), gravado em ~/.claude/hooks/hooks-origem.json. Default origin/main; outro ref só por opt-in
#     (-Ref <ref> ou FRAMEWORK_HOOKS_REF; WORKTREE = arquivos não commitados). Pasta sem git: a própria pasta.
#     Ref ausente: nada é instalado e evento cujo script não existe não é ligado.
#
# EXIT CODES (consumidos por bootstrap/sync-global p/ transparência ao usuário):
#   0  = nada a fazer (já wirado)
#   10 = wiring (re)aplicada — houve mudança (ex.: clobber curado, entrada incompatível removida)
#   1  = erro; settings restaurado do backup settings.json.heal-<timestamp>.bak desta execução
#
# Uso:  ensure-global-wiring.ps1 [-RepoDir <path>] [-Ref <ref>]

param([string]$RepoDir = "", [string]$Ref = "")
# ENSURE-CONTRATO: 2 — o sync-global só executa um ensure com contrato >= 2 (aceita -Ref, sonda, origem única).
# Um ensure anterior ao ADR-130 ignoraria -Ref e copiaria do working tree: exatamente o incidente de 28/09/2026.

$ErrorActionPreference = 'Stop'

$globalDir = Join-Path $env:USERPROFILE '.claude'
$hooksDir  = Join-Path $globalDir 'hooks'
$settings  = Join-Path $globalDir 'settings.json'
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

$injectGlobal = Join-Path $hooksDir 'inject-start-session-global.ps1'
$routeGate    = Join-Path $hooksDir 'route-gate.ps1'

function Log($m) { [Console]::Error.WriteLine("[ensure-global-wiring] $m") }
$esteScript = $PSCommandPath

# Fonte no repo -> nome instalado. Tudo que este script liga, mais ele mesmo: uma versão só (ADR-130).
$fontes = [ordered]@{
    'tools/hooks/route-gate.ps1'                             = 'route-gate.ps1'
    '.claude/hooks/inject-start-session-global.template.ps1' = 'inject-start-session-global.ps1'
    'tools/hooks/resposta_executiva.py'                      = 'resposta_executiva.py'
    'tools/hooks/ensure-global-wiring.ps1'                   = 'ensure-global-wiring.ps1'
}

function Install-HookScripts {
    param([string]$Repo, [string]$RefPedido)
    $ErrorActionPreference = 'Continue'   # PS 5.1: stderr de programa nativo com 'Stop' vira exceção
    $ref = if ($RefPedido) { $RefPedido } elseif ($env:FRAMEWORK_HOOKS_REF) { $env:FRAMEWORK_HOOKS_REF } else { 'origin/main' }
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ('hooks-origem-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    try {
        $ehGit = $false
        if (Get-Command git -ErrorAction SilentlyContinue) {
            $null = & git -C $Repo rev-parse --is-inside-work-tree 2>$null
            $ehGit = ($LASTEXITCODE -eq 0)
        }
        $commit = ''
        if ($ehGit -and $ref -ne 'WORKTREE') {
            $commit = "$(& git -C $Repo rev-parse --verify --quiet "${ref}^{commit}" 2>$null)".Trim()
            if ($LASTEXITCODE -ne 0 -or -not $commit) {
                Log "ref '$ref' nao resolvido em $Repo; scripts NAO instalados (mantidos os atuais)."
                return
            }
            $presentes = @($fontes.Keys | Where-Object { & git -C $Repo cat-file -e "${commit}:$_" 2>$null; $LASTEXITCODE -eq 0 })
            if ($presentes.Count -eq 0) { Log "ref '$ref' nao contem os scripts de hook; NAO instalados."; return }
            $zip = Join-Path $tmp 'fontes.zip'
            & git -C $Repo archive --format=zip -o $zip $commit -- @presentes 2>$null
            if ($LASTEXITCODE -ne 0) { Log "git archive falhou ($ref); scripts NAO instalados."; return }
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            [IO.Compression.ZipFile]::ExtractToDirectory($zip, $tmp)   # byte a byte: sem recodificar UTF-8
            $origem = $ref
        } else {
            # WORKTREE é opt-in explícito; pasta sem git tem uma versão só, sem branch para divergir.
            $origem = if ($ehGit) { 'WORKTREE' } else { 'DIRETORIO' }
            foreach ($rel in $fontes.Keys) {
                $s = Join-Path $Repo $rel
                if (Test-Path $s) {
                    $d = Join-Path $tmp $rel
                    New-Item -ItemType Directory -Path (Split-Path $d) -Force | Out-Null
                    Copy-Item $s $d -Force
                }
            }
        }
        # Arquivo travado (outra sessão, antivírus) não aborta o resto: fica em `incompleto` no carimbo, e a sonda
        # abaixo testa o que de fato ficou instalado.
        $hashes = [ordered]@{}
        $incompleto = @()
        foreach ($rel in $fontes.Keys) {
            $s = Join-Path $tmp $rel
            if (Test-Path $s) {
                $d = Join-Path $hooksDir $fontes[$rel]
                try {
                    Copy-Item $s $d -Force -ErrorAction Stop
                    $hashes[$fontes[$rel]] = (Get-FileHash $d -Algorithm SHA256).Hash
                } catch { $incompleto += $fontes[$rel] }
            }
        }
        # ensure_executado: hash do ensure que fez o wiring; igual ao instalado = wiring e scripts da mesma versão.
        $marca = [ordered]@{ ref = $origem; commit = $commit; repo = $Repo; instalado_em = (Get-Date).ToString('s')
                             ensure_executado = (Get-FileHash $esteScript -Algorithm SHA256).Hash; arquivos = $hashes
                             incompleto = $incompleto }
        [System.IO.File]::WriteAllText((Join-Path $hooksDir 'hooks-origem.json'), ($marca | ConvertTo-Json -Depth 4), $utf8NoBom)
        if ($incompleto) { Log "instalacao INCOMPLETA de $origem ${commit}: $($incompleto -join ', ') nao copiados (arquivo em uso?)." }
        else { Log "scripts de hook instalados de $origem $commit" }
    } finally {
        Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Sonda: o script instalado aceita a flag? Exige exit 0 e stdout vazio (no UserPromptSubmit o stdout vira contexto
# de todo prompt; no Stop, JSON no stdout pode bloquear). Estado isolado em pasta temporária. '' = passou.
# 'SEM-PYTHON' = não dá para sondar: não liga, mas também não remove (sem python o shell sai com 127/1, que não
# bloqueia; remover entrada boa por falta momentânea de PATH seria perda sem ganho). Script ausente é falha: o
# python sai com 2 ao não achar o arquivo, e 2 bloqueia.
function Test-HookScript {
    param([string]$Script, [string]$Flag, [string[]]$Eventos)
    $ErrorActionPreference = 'Continue'
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) { return 'SEM-PYTHON' }
    if (-not (Test-Path $Script)) { return "script ausente em $Script" }
    $estado = Join-Path ([IO.Path]::GetTempPath()) ('sonda-hook-' + [guid]::NewGuid().ToString('N'))
    $antes = $env:RESPOSTA_EXECUTIVA_DIR
    $env:RESPOSTA_EXECUTIVA_DIR = $estado
    try {
        foreach ($ev in $Eventos) {
            $saida = $ev | & python $Script $Flag 2>$null
            if ($LASTEXITCODE -ne 0) { return "exit $LASTEXITCODE com $Flag" }
            if ("$saida".Trim()) { return "stdout inesperado com $Flag" }
        }
        return ''
    } finally {
        $env:RESPOSTA_EXECUTIVA_DIR = $antes
        Remove-Item $estado -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Remove do evento toda entrada cujo command casa o padrão (flag incompatível). $true se removeu algo.
function Remove-HookEntries {
    param($Cfg, [string]$EventName, [string]$Pattern)
    if (-not $Cfg.hooks.$EventName) { return $false }
    $mudou = $false
    $grupos = @()
    foreach ($g in @($Cfg.hooks.$EventName)) {
        $todos = @($g.hooks)
        $ficam = @($todos | Where-Object { -not ("$($_.command)" -like $Pattern) })
        if ($ficam.Count -ne $todos.Count) { $mudou = $true }
        if ($ficam.Count -gt 0) { $g.hooks = $ficam; $grupos += $g }
    }
    if (-not $mudou) { return $false }
    if ($grupos.Count -gt 0) { $Cfg.hooks.$EventName = $grupos } else { $Cfg.hooks.PSObject.Properties.Remove($EventName) }
    return $true
}

$bak = $null
try {
    if (-not (Test-Path $globalDir)) { New-Item -ItemType Directory -Path $globalDir -Force | Out-Null }
    if (-not (Test-Path $hooksDir))  { New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null }

    # 0. Com -RepoDir: instala os scripts de UMA origem (ADR-130), antes de sondar e wirar.
    if ($RepoDir -and (Test-Path $RepoDir)) { Install-HookScripts -Repo $RepoDir -RefPedido $Ref }

    $injectCmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$injectGlobal`""
    $routeCmd  = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$routeGate`""

    # 1. Carregar settings (ou iniciar objeto vazio).
    $cfg = $null
    if (Test-Path $settings) {
        $cfg = Get-Content $settings -Raw | ConvertFrom-Json
    }
    if (-not $cfg) { $cfg = [pscustomobject]@{} }
    if (-not $cfg.hooks) { $cfg | Add-Member -NotePropertyName hooks -NotePropertyValue ([pscustomobject]@{}) -Force }

    $changed = $false

    # Helper: garante que um evento de hook contém um grupo cujo command casa o needle.
    function Ensure-HookEvent {
        param($Cfg, [string]$EventName, [string]$Needle, [string]$Command, [string]$StatusMessage)
        $present = $false
        $existing = $Cfg.hooks.$EventName
        if ($existing) {
            $serialized = $existing | ConvertTo-Json -Depth 10 -Compress
            if ($serialized -like "*$Needle*") { $present = $true }
        }
        if ($present) { return $false }

        $newGroup = [ordered]@{
            hooks = @(
                [ordered]@{
                    type          = 'command'
                    command       = $Command
                    timeout       = 10
                    statusMessage = $StatusMessage
                }
            )
        }
        if ($existing) {
            $Cfg.hooks.$EventName = @($existing) + $newGroup
        } else {
            $Cfg.hooks | Add-Member -NotePropertyName $EventName -NotePropertyValue @($newGroup) -Force
        }
        return $true
    }

    # Só liga o que está instalado: sem origem resolvida (ADR-130) o script pode não existir.
    if (-not (Test-Path $injectGlobal)) { Log "SessionStart NAO ligado: $injectGlobal ausente." }
    elseif (Ensure-HookEvent -Cfg $cfg -EventName 'SessionStart' -Needle 'inject-start-session-global' `
            -Command $injectCmd -StatusMessage 'Auto-boot global do squad (ADR-006)') { $changed = $true }

    if (-not (Test-Path $routeGate)) { Log "UserPromptSubmit route-gate NAO ligado: $routeGate ausente." }
    elseif (Ensure-HookEvent -Cfg $cfg -EventName 'UserPromptSubmit' -Needle 'route-gate' `
            -Command $routeCmd -StatusMessage 'Roteamento determinístico (route-gate ADR-027)') { $changed = $true }

    # Formato executivo (regra do dono, 27/09/2026; ADR-129, 28/09/2026): o Stop MEDE e guarda os achados, sem
    # bloquear (bloquear depois de exibir duplicava a resposta na tela); o UserPromptSubmit injeta o molde e os
    # achados da resposta anterior antes da próxima. Cada evento só é ligado se a SONDA passar (ADR-130).
    $respExec = Join-Path $hooksDir 'resposta_executiva.py'
    $sondas = @(
        @{ evento = 'Stop'; flag = '--hook'; msg = 'Formato executivo: mede a resposta (regra do dono)'
           json = @('{"hook_event_name":"Stop","session_id":"sonda-wiring","transcript_path":"","last_assistant_message":"ok","stop_hook_active":false}') },
        @{ evento = 'UserPromptSubmit'; flag = '--lembrete'; msg = 'Formato executivo: molde e achados da resposta anterior'
           json = @('{"hook_event_name":"UserPromptSubmit","session_id":"sonda-wiring","prompt":"oi"}',
                    '{"hook_event_name":"UserPromptSubmit","session_id":"sonda-wiring","prompt":"<task-notification>sonda</task-notification>"}') }
    )
    foreach ($s in $sondas) {
        $falha = Test-HookScript -Script $respExec -Flag $s.flag -Eventos $s.json
        if ($falha -eq 'SEM-PYTHON') {
            Log "$($s.evento) $($s.flag) NAO sondado: python ausente no PATH; wiring existente mantido, nada ligado."
        } elseif ($falha) {
            Log "$($s.evento) $($s.flag) NAO ligado: sonda falhou ($falha)."
            if (Remove-HookEntries -Cfg $cfg -EventName $s.evento -Pattern "*resposta_executiva*$($s.flag)*") {
                $changed = $true
                Log "$($s.evento): entrada resposta_executiva $($s.flag) removida (script instalado incompativel)."
            }
        } elseif (Ensure-HookEvent -Cfg $cfg -EventName $s.evento -Needle 'resposta_executiva' `
                -Command "python `"$respExec`" $($s.flag)" -StatusMessage $s.msg) { $changed = $true }
    }

    if (-not $changed) {
        Log 'wiring ja presente; nada a fazer.'
        exit 0
    }

    # 2. Backup com timestamp (nunca sobrescreve backup anterior) + validação + escrita (hook-preserving).
    if (Test-Path $settings) {
        $bak = "$settings.heal-$(Get-Date -Format 'yyyyMMdd-HHmmss-fff').bak"
        Copy-Item $settings $bak
    }
    $newJson = $cfg | ConvertTo-Json -Depth 12
    $null = $newJson | ConvertFrom-Json -ErrorAction Stop   # valida antes de gravar
    [System.IO.File]::WriteAllText($settings, $newJson, $utf8NoBom)
    Log 'wiring (re)aplicada — hooks globais re-afirmados (auto-heal).'
    exit 10
}
catch {
    Log "ERRO: $($_.Exception.Message)"
    if ($bak -and (Test-Path $bak)) {   # só o backup DESTA execução; um .bak antigo nunca volta por engano
        Copy-Item $bak $settings -Force -ErrorAction SilentlyContinue
        Log "settings restaurado de $bak."
    }
    exit 1
}
