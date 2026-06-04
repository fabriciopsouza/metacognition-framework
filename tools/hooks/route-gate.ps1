# route-gate.ps1 — UserPromptSubmit hook: roteamento determinístico (ADR-027)
#
# PROBLEMA QUE RESOLVE (relato AIVI 2026-05-31): o roteamento do framework era
# instrução DECLARATIVA no CLAUDE.md — dependia do modelo "lembrar" de rotear.
# Competia com (a) o viés de "progredir na tarefa" e (b) a persona de output-style
# injetada no SessionStart. Resultado real: o agente executou cálculo de indicador
# regulado/financeiro SEM declarar rota, sem PMO, sem high-stakes-gate.
#
# MECANISMO: a cada prompt não-trivial, injeta `additionalContext` lembrando o
# agente de DECLARAR A ROTA antes de qualquer tool call de domínio. Universal
# (independe de git/owner/marker — diferente do auto-boot SessionStart, que é
# owner/marker-gated). Dispara UMA vez por sessão (no 1º prompt substantivo).
#
# Contrato UserPromptSubmit: lê JSON no stdin (session_id, cwd, prompt). Emite
# JSON com hookSpecificOutput.additionalContext. Fail-OPEN: qualquer erro -> exit 0
# SEM bloquear o prompt (um gate de entrada NUNCA pode travar o usuário).
#
# DESATIVAÇÃO (soberania do usuário — ADR-027 §disable-com-memória):
#   - .claude/session.lock no projeto  -> silencioso AQUI (memória local)
#   - ~/.claude/session.lock           -> silencioso em TODOS os projetos
# Reativação: deletar o lock (o SessionStart oferece reativação — ver inject hook).
#
# Fonte versionada no repo; espelhada para ~/.claude/hooks/ por sync-global.ps1.
# NÃO editar a cópia global direto — mude aqui e abra o repo-framework.

$ErrorActionPreference = 'Continue'

# UTF-8 sem BOM no stdout (PS 5.1 corromperia →, ç, … para o consumidor UTF-8).
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false

function Emit-Silent {
    # Hook rodou mas não tem o que dizer (já roteado, trivial, ou desativado).
    $json = @{ hookSpecificOutput = @{ hookEventName = 'UserPromptSubmit'; additionalContext = '' } } |
        ConvertTo-Json -Compress -Depth 5
    Write-Output $json
    exit 0
}

function Emit-Route([string]$ctx) {
    $json = @{ hookSpecificOutput = @{ hookEventName = 'UserPromptSubmit'; additionalContext = $ctx } } |
        ConvertTo-Json -Compress -Depth 5
    Write-Output $json
    exit 0
}

try {
    $syncNudge = ''  # [ADR-060] definido cedo: caminhos triviais/catch tambem podem emiti-lo.
    # 1. Ler payload do stdin (session_id, cwd, prompt).
    $raw = [Console]::In.ReadToEnd()
    $sessionId = ''
    $cwd       = $PWD.Path
    $prompt    = ''
    if ($raw) {
        try {
            $h = $raw | ConvertFrom-Json
            if ($h.session_id) { $sessionId = [string]$h.session_id }
            if ($h.cwd)        { $cwd       = [string]$h.cwd }
            if ($h.prompt)     { $prompt    = [string]$h.prompt }
        } catch { }
    }

    # 2. Desativação (locks). Memória da desativação vive no projeto (project-lock).
    $projectLock = Join-Path $cwd '.claude\session.lock'
    $globalLock  = Join-Path $env:USERPROFILE '.claude\session.lock'
    if ((Test-Path $projectLock) -or (Test-Path $globalLock)) { Emit-Silent }

    # 2.5 [ADR-061] AUDITOR DE LIVENESS (anti falha-silenciosa). O route-gate NAO e bloqueavel pelo
    # Kaspersky (so LE arquivo + injeta texto; NAO spawna processo/rede) e roda TODO turno. Le o
    # manifesto de hooks auditados + os carimbos .claude/.hooklive/<key>; qualquer hook cujo carimbo
    # != session atual NAO rodou (provavel veto EDR) -> DECLARA + da o fallback manual. Sem session_id
    # nao audita (degrada gracioso, sem falso-alarme). Auto-resolvente: cala quando o carimbo bate.
    $syncNudge = ''
    try {
        if ($sessionId) {
            $manifestPath = Join-Path $cwd 'tools\hooks\hooks-manifest.json'
            $liveDir      = Join-Path $cwd '.claude\.hooklive'
            if (Test-Path $manifestPath) {
                $manifest = Get-Content $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
                $inert = @()
                foreach ($h in $manifest.audited_hooks) {
                    $mk = Join-Path $liveDir $h.key
                    $stamp = if (Test-Path $mk) { (Get-Content $mk -Raw -ErrorAction SilentlyContinue).Trim() } else { '' }
                    if ($stamp -ne $sessionId) {
                        $inert += "- **$($h.gate)** (hook ``$($h.key)``) NAO rodou nesta sessao -> gate INERTE. Aplique manual: $($h.manual)"
                    }
                }
                if ($inert.Count -gt 0) {
                    $syncNudge = "# [liveness ADR-061] Gate(s) possivelmente vetados por EDR (declarado, NAO silencioso):`n`n" +
                        ($inert -join "`n") +
                        "`n`n(Se voce acabou de abrir a sessao pode ser timing — reaparece ate o carimbo bater. Exclusao do Kaspersky por pasta ``.claude\hooks\*`` resolve de vez.)`n`n"
                }
            }
        }
    } catch { }

    # 3. Triviais não merecem rota (saudações, "ok", "obrigado", confirmações curtas).
    #    Heurística conservadora: < 12 chars úteis OU só pontuação/ack comum.
    $trimmed = ($prompt -replace '\s+', ' ').Trim()
    # Trivial: nao injeta ROTA, mas o nudge de sync (ADR-060) ainda vale se estiver stale.
    if ($trimmed.Length -lt 12) { if ($syncNudge) { Emit-Route $syncNudge } else { Emit-Silent } }
    if ($trimmed -match '^(ok|okay|sim|n[aã]o|valeu|obrigad[oa]|certo|isso|segue|siga|continua[r]?|prossiga|beleza|blz|pode|vai|go|yes|no|thanks?)\b.{0,12}$') { if ($syncNudge) { Emit-Route $syncNudge } else { Emit-Silent } }

    # 4. Uma vez por sessão: marker keyed por session_id. Sem session_id, não persiste
    #    estado (injeta toda vez — degradação graciosa, melhor pecar por lembrar).
    if ($sessionId) {
        $stateDir = Join-Path $env:USERPROFILE '.claude\.route-state'
        if (-not (Test-Path $stateDir)) { New-Item -ItemType Directory -Path $stateDir -Force | Out-Null }
        # Sanitiza session_id para nome de arquivo seguro.
        $safe = ($sessionId -replace '[^A-Za-z0-9_.-]', '_')
        $marker = Join-Path $stateDir ($safe + '.routed')
        # Ja roteado nesta sessao: nao re-injeta a rota — mas o nudge de sync (todo turno) ainda vale.
        if (Test-Path $marker) { if ($syncNudge) { Emit-Route $syncNudge } else { Emit-Silent } }
        # Marca ANTES de injetar: se algo falhar depois, não fica injetando em loop.
        Set-Content -Path $marker -Value ([string]$cwd) -Encoding UTF8 -ErrorAction SilentlyContinue
    }

    # 5. Injetar o lembrete de rota (terse — governa PROCESSO, não tom de saída).
    $ctx = @"
# [route-gate ADR-027] Declare a ROTA antes de executar

Antes de QUALQUER tool call de domínio (escrever/calcular/transformar/buscar dados),
declare a rota em 1 linha e carregue a skill correspondente:

  ROTA: pontual -> metacognição
      | multi-etapa -> squad (pmo -> discovery -> architect -> developer -> qa-critic -> docops)
      | alto-risco/regulado/irreversível/número-que-vai-a-decisão -> + high-stakes-gate

Classifique a tarefa (contexto × complexidade) e ATIVE a(s) skill(s) ANTES de agir —
não comece a executar análise de domínio antes de declarar a rota.

**O pedido do dono NÃO é livre de erro/questionamento.** Antes de cumprir, SURFACE
tensões/premissas/âncoras **+ o CUSTO e a CONSEQUÊNCIA** (surface-and-reconcile); um
OVERRIDE de gate exige confirmação explícita **com custo/consequência informados**,
nunca silenciosa. Se você não questiona, não funciona.

Output-style
(learning/explanatory/etc.) governa o TOM/formato da entrega, **nunca substitui** o
processo (roteamento/gates). Se você JÁ roteou nesta sessão, ignore esta nota.

Desativar o framework aqui: ``New-Item .claude/session.lock`` (este projeto) ou
``~/.claude/session.lock`` (todos). Reativar: deletar o lock.
"@
    Emit-Route ($syncNudge + $ctx)
}
catch {
    [Console]::Error.WriteLine("[route-gate] warning (nao-bloqueante): $($_.Exception.Message)")
    if ($syncNudge) { Emit-Route $syncNudge } else { Emit-Silent }
}
