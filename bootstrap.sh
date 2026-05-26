#!/usr/bin/env bash
# bootstrap.sh — Setup do framework metacognitivo em PC novo (macOS/Linux)
#
# Idempotente: rodar 2x não destrói nada. Faz git config (com confirmação se
# já existe), garante gh CLI autenticado, clona o repo principal e
# opcionalmente o repo privado de memória.
#
# USO:
#   ./bootstrap.sh [--memory-repo "<owner/repo>"] [--project-dir "<path>"]
#
# Exemplos:
#   # Setup só do framework (sem memória própria):
#   ./bootstrap.sh
#
#   # Setup completo (mantenedor, com seu repo de memória privado):
#   ./bootstrap.sh --memory-repo fabriciopsouza/claude-memory-metacognition-framework
#
# Equivalente Windows: bootstrap.ps1 (mesma raiz).

set -euo pipefail

MEMORY_REPO=""
PROJECT_DIR="$HOME/dev/metacognition-framework"
GIT_EMAIL=""
GIT_NAME=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --memory-repo)   MEMORY_REPO="$2"; shift 2 ;;
        --project-dir)   PROJECT_DIR="$2"; shift 2 ;;
        --git-email)     GIT_EMAIL="$2"; shift 2 ;;
        --git-name)      GIT_NAME="$2"; shift 2 ;;
        -h|--help)
            grep '^#' "$0" | sed 's/^#//'
            exit 0
            ;;
        *) echo "Argumento desconhecido: $1"; exit 1 ;;
    esac
done

step() { printf "\033[36m==> %s\033[0m\n" "$1"; }
ok()   { printf "    \033[32mOK  %s\033[0m\n" "$1"; }
warn() { printf "    \033[33m!!  %s\033[0m\n" "$1"; }

# 1. Pre-checks
step "Verificando pre-requisitos (git, gh)"
command -v git >/dev/null || { echo "git nao encontrado"; exit 1; }
command -v gh >/dev/null  || { echo "gh CLI nao encontrado: https://cli.github.com/"; exit 1; }
ok "git e gh instalados"

# 2. Git config global (so seta se nao existir)
step "Verificando git config global"
CURRENT_EMAIL="$(git config --global user.email || true)"
CURRENT_NAME="$(git config --global user.name || true)"

if [[ -z "$CURRENT_EMAIL" ]]; then
    if [[ -z "$GIT_EMAIL" ]]; then
        read -r -p "user.email nao configurado. Informar: " GIT_EMAIL
    fi
    git config --global user.email "$GIT_EMAIL"
    ok "user.email setado para: $GIT_EMAIL"
else
    ok "user.email ja configurado: $CURRENT_EMAIL"
fi

if [[ -z "$CURRENT_NAME" ]]; then
    if [[ -z "$GIT_NAME" ]]; then
        read -r -p "user.name nao configurado. Informar: " GIT_NAME
    fi
    git config --global user.name "$GIT_NAME"
    ok "user.name setado para: $GIT_NAME"
else
    ok "user.name ja configurado: $CURRENT_NAME"
fi

# 3. gh CLI autenticado
step "Verificando autenticacao gh CLI"
if ! gh auth status >/dev/null 2>&1; then
    warn "gh CLI nao autenticado. Abrindo fluxo interativo..."
    gh auth login
fi
ok "gh CLI autenticado"

# 4. Clone do repo principal
step "Clonando metacognition-framework em $PROJECT_DIR"
if [[ -d "$PROJECT_DIR" ]]; then
    warn "Diretorio ja existe; pulando clone (use 'git pull' la dentro)"
else
    mkdir -p "$(dirname "$PROJECT_DIR")"
    gh repo clone fabriciopsouza/metacognition-framework "$PROJECT_DIR"
    ok "Repo principal clonado"
fi

# 5. Clone do repo de memoria (opcional)
if [[ -n "$MEMORY_REPO" ]]; then
    step "Configurando memoria do Claude Code a partir de $MEMORY_REPO"
    MEMORY_PATH="$HOME/.claude/projects/f--metacognition-framework/memory"

    if [[ -d "$MEMORY_PATH" ]]; then
        BACKUP_PATH="${MEMORY_PATH}.backup.$(date +%Y%m%d-%H%M%S)"
        mv "$MEMORY_PATH" "$BACKUP_PATH"
        warn "Memoria existente movida para: $BACKUP_PATH"
    fi

    mkdir -p "$(dirname "$MEMORY_PATH")"
    if gh repo clone "$MEMORY_REPO" "$MEMORY_PATH"; then
        ok "Memoria do Claude Code sincronizada"
    else
        warn "Clone do repo de memoria falhou. Repo existe e voce tem acesso? URL informada: $MEMORY_REPO"
    fi
else
    ok "Sem --memory-repo informado; pulando setup de memoria"
fi

# 6. Resumo
echo ""
echo "================================================================"
echo " Setup concluido. Proximos passos:"
echo "================================================================"
echo " 1. cd \"$PROJECT_DIR\""
echo " 2. Abrir Claude Code neste diretorio."
echo "    -> SessionStart hook roda automaticamente:"
echo "       * sync-global.ps1 espelha skills para ~/.claude/"
echo "       * inject-start-session.ps1 ativa PMO no 1o turno"
echo " 3. Para pular o auto-boot em sessao rapida:"
echo "       touch .claude/session.lock"
echo ""
echo " Pronto."
