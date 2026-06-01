# guia/teste-isolado.ps1 - harness de TESTE ISOLADO do framework num caso de dominio real,
# SEM vazamento cross-sessao (ADR-010). Isolamento ESTRUTURAL, nao disciplinar:
#   - Framework: clone do PUBLICO (prova que o distribuido funciona e nao carrega cliente).
#   - Projeto: pasta SEPARADA, git proprio -> commits/artefatos nunca tocam o framework.
#   - Memoria: deriva do cwd -> pasta de teste = memoria separada (automatico).
#
# ASCII-only de proposito (PS 5.1 le fonte sem-BOM como cp1252 e quebra em char multibyte).
#
# Uso:
#   pwsh ./guia/teste-isolado.ps1 -DataSource "C:\caminho\dos\dados" [-TestDir F:\teste-isolado]
#   pwsh ./guia/teste-isolado.ps1 -LeakCheck    # apos o teste: prova zero vazamento de volta
#
# Parametros:
param(
  [string]$PublicRepo    = "https://github.com/fabriciopsouza/metacognition-framework-public.git",
  [string]$FrameworkClone = "$HOME\mfw-clone",
  [string]$TestDir       = "$HOME\teste-isolado",
  [string]$DataSource    = "",
  [switch]$LeakCheck,
  [switch]$NoBootstrap
)

$ErrorActionPreference = 'Stop'

function Say($m) { Write-Host "[teste-isolado] $m" }

if ($LeakCheck) {
  # --- Modo checagem de vazamento de VOLTA (rodar depois do teste) ---
  Say "Checando que NADA do dominio vazou para o framework..."
  if (-not (Test-Path $FrameworkClone)) { Say "Clone do framework nao encontrado em $FrameworkClone"; exit 2 }
  Push-Location $FrameworkClone
  try {
    Say "1/2 gate sensivel (zero token de cliente na arvore):"
    & python tools/check_core_agnostic.py --sensitive
    $gate = $LASTEXITCODE
    Say "2/2 git status (deve estar limpo - nada do teste commitado no framework):"
    $status = git status --porcelain
    if ($status) { Say "ATENCAO: ha mudancas nao-commitadas no framework:"; $status } else { Say "limpo." }
    if ($gate -eq 0 -and -not $status) { Say "OK: zero vazamento de volta." } else { Say "REVISAR: ver acima." ; exit 1 }
  } finally { Pop-Location }
  exit 0
}

# --- Modo setup do teste isolado ---
# 1. Clona o PUBLICO (idempotente)
if (-not (Test-Path $FrameworkClone)) {
  Say "Clonando o PUBLICO em $FrameworkClone (prova: distribuido funciona + sem cliente)..."
  git clone $PublicRepo $FrameworkClone
} else { Say "Clone do framework ja existe em $FrameworkClone (pulando)." }

# 2. Instala o framework globalmente (skills em ~/.claude)
if (-not $NoBootstrap) {
  $bs = Join-Path $FrameworkClone "bootstrap.ps1"
  if (Test-Path $bs) { Say "Instalando o framework (bootstrap.ps1)..."; & $bs } else { Say "bootstrap.ps1 ausente no clone." }
}

# 3. Projeto de teste ISOLADO (git proprio, FORA do framework)
if (-not (Test-Path $TestDir)) { New-Item -ItemType Directory -Force -Path $TestDir | Out-Null }
$dataDir = Join-Path $TestDir "dados"
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
Push-Location $TestDir
try {
  if (-not (Test-Path ".git")) { Say "git init no projeto de teste (repo SEPARADO)..."; git init -q }
  if ($DataSource -and (Test-Path $DataSource)) {
    Say "Copiando dados de '$DataSource' para '$dataDir'..."
    Copy-Item (Join-Path $DataSource '*') $dataDir -Recurse -Force
  } else {
    Say "AVISO: -DataSource nao informado/inexistente. Coloque os arquivos do caso em: $dataDir"
  }
} finally { Pop-Location }

Say "PRONTO. Abra o Claude Code com cwd = $TestDir (NAO o clone do framework)."
Write-Host ""
Write-Host "=== PROMPT pronto para colar (na sessao em $TestDir) ===" -ForegroundColor Cyan
@"
Tarefa de dominio (classifique: regulado? alto-risco? auditavel?). Os dados estao em ./dados.
NAO escreva nenhum termo deste dominio em arquivos do framework (~/.claude ou qualquer clone do
metacognition-framework) - so neste projeto. Rote pelo squad (pmo -> discovery -> architect ->
developer -> qa-critic -> docops) + high-stakes-gate se aplicavel.

Quero validar se o framework produz o resultado PREMIUM com MENOS interacoes:
1. Carregue o blueprint de dominio adequado (exemplos/dominio-*/blueprint.md) e PROPONHA a forma
   completa do produto de uma vez (launcher facil-ou-CLI; auto-deteccao+validacao dos arquivos de
   ./dados via data-dictionary + check_input_contract; suite de saida; auditoria) - eu confirmo/ajusto.
2. Construa; rode no encerramento: check_spec_depth, check_completeness, check_input_contract,
   check_entrypoint_tty, check_clean_env + o ux-gate premium. Gere o execution-report (placar gate x achado).
3. Me entregue: (a) quantas interacoes minhas foram necessarias; (b) tabela gate x resultado;
   (c) o que ficou como limite honesto.

Trabalhe autonomo; pare no PR do PROJETO (nao toque o repo do framework).
"@
Write-Host ""
Say "Depois do teste, rode:  pwsh ./guia/teste-isolado.ps1 -LeakCheck   (prova zero vazamento de volta)"
