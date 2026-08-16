# consistency-gate.ps1 — ENCAMINHADOR. A lógica vive em consistency_gate.py (ADR-030).
#
# POR QUE VIROU CASCA (2026-08-16): a implementação foi portada para Python para poder ser
# cabeada no evento `Stop` — a classe de hook comprovadamente viva nesta máquina — e para
# ganhar canário próprio (`tools/test_consistency_gate.py`). Manter as duas implementações
# lado a lado seria convite a divergirem em silêncio, que é a dívida que o próprio ADR-030
# combate; e apagar este arquivo quebraria dez ponteiros, entre eles ADRs, que são registro
# histórico e não se reescreve. Encaminhar resolve os dois: uma lógica só, dois caminhos.
#
# Comportamento preservado: mesmos parâmetros, mesma saída, exit code = nº de pendências.
# Uso:  consistency-gate.ps1 [-RepoDir <path>] [-Json]

param([string]$RepoDir = "", [switch]$Json)

$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false

$alvo = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'consistency_gate.py'
if (-not (Test-Path $alvo)) {
    [Console]::Error.WriteLine("[consistency-gate] destino ausente: $alvo")
    exit 0
}

$argumentos = @($alvo)
if ($RepoDir) { $argumentos += @('--repo', $RepoDir) }
if ($Json)    { $argumentos += '--json' }

& python @argumentos
exit $LASTEXITCODE
