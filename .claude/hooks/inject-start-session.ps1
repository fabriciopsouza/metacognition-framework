# inject-start-session.ps1
# Hook SessionStart (v1.6.1) — injeta orientação de boot do squad (/start-session) no
# contexto inicial da sessão, ATIVANDO o PMO automaticamente.
#
# Comportamento:
# - Default: injeta o conteudo de .agent/workflows/start-session.md como additionalContext
#   (via output JSON { hookSpecificOutput: { additionalContext: "..." } }), fazendo o
#   Claude entrar com a instrucao de rodar o PMO antes de qualquer outra coisa.
# - Escape: se existir o arquivo .claude/session.lock no projeto, NAO injeta nada
#   (sessao "rapida" — voce assume controle). Para criar o lock:
#       New-Item .claude/session.lock -ItemType File -Force
#   Para reativar o boot automatico em sessoes futuras, simplesmente deletar o lock.
# - Falha "soft": qualquer erro vira warning no stderr e exit 0 (nao bloqueia sessao).
#
# Disparado pelo SessionStart hook em .claude/settings.json depois do sync-global.ps1.
# Pode rodar a mao para teste.

$ErrorActionPreference = 'Continue'

# UTF-8 sem BOM no stdout: PS 5.1 default emite na codepage do console, corrompendo
# acentos e multibyte (—, →) para o consumidor UTF-8 (Claude Code le o stdout do hook).
# BOM quebraria o parse do JSON, por isso UTF8Encoding($false).
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false

# Anti-duplicacao (ADR-006): se o hook GLOBAL de auto-boot ja esta instalado em
# ~/.claude/hooks/, ELE assume o boot deste repo (owner-match ou marker .agent/) e
# tambem honra os session.lock. Este hook de PROJETO (v1.6.1) entao so atua como
# fallback de primeira execucao, ANTES do bootstrap instalar o global. Sem este guard,
# abrir o framework-repo ja bootstrapped injeta /start-session DUAS vezes (gap v1.8.0).
$globalBootHook = Join-Path $env:USERPROFILE '.claude\hooks\inject-start-session-global.ps1'
if (Test-Path $globalBootHook) { exit 0 }

# Resolver projectRoot (mesma logica de sync-global.ps1).
if ($env:CLAUDE_PROJECT_DIR -and (Test-Path $env:CLAUDE_PROJECT_DIR)) {
    $projectRoot = $env:CLAUDE_PROJECT_DIR
} else {
    $projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
}

$lockFile = Join-Path $projectRoot '.claude\session.lock'
$startSessionDoc = Join-Path $projectRoot '.agent\workflows\start-session.md'

try {
    # Escape: se .claude/session.lock existe, nao injeta nada (sessao rapida).
    if (Test-Path $lockFile) {
        # Sinaliza no statusMessage para o usuario saber que o auto-boot foi pulado.
        $json = @{
            hookSpecificOutput = @{
                hookEventName    = 'SessionStart'
                additionalContext = ''
            }
        } | ConvertTo-Json -Compress -Depth 5
        Write-Output $json
        exit 0
    }

    # Default: injetar orientacao do /start-session no contexto.
    if (-not (Test-Path $startSessionDoc)) {
        [Console]::Error.WriteLine("[auto-start-session] aviso: .agent/workflows/start-session.md nao encontrado; pulando injeção.")
        exit 0
    }

    $startContent = Get-Content -Path $startSessionDoc -Raw -Encoding UTF8

    $context = @"
# Boot automatico do squad - v1.6.1 (auto-start-session)

Esta sessao foi inicializada com o squad em modo auto-boot. Sua **primeira acao**
neste turno DEVE ser ativar o papel PMO e executar o /start-session conforme
abaixo. NAO responder a outra coisa antes disso.

Para o usuario PULAR este auto-boot em sessoes futuras (debug rapido, pergunta
pontual), basta criar o arquivo de escape:
    New-Item .claude/session.lock -ItemType File -Force
e o hook respeitara em todas as sessoes subsequentes ate o lock ser deletado.

---

$startContent
"@

    $json = @{
        hookSpecificOutput = @{
            hookEventName     = 'SessionStart'
            additionalContext = $context
        }
    } | ConvertTo-Json -Compress -Depth 5

    Write-Output $json
}
catch {
    [Console]::Error.WriteLine("[auto-start-session] warning: $($_.Exception.Message)")
}

exit 0
