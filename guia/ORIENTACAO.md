# ORIENTAÇÃO — Quem lê o quê (Humano × IA)

> Mapa de leitura. Nem todo arquivo é para você; nem todo é para a IA.

## Para o HUMANO (você)
| Arquivo | Para quê |
|---|---|
| `README.md` (raiz) | visão geral + índice mestre — comece aqui |
| `guia/INSTALAR-NO-VSCODE.md` | instalar no VS Code, remover o antigo (passo a passo) |
| `guia/SETUP.md` | os 3 modos de uso (greenfield / revisar / migrar) |
| `guia/COMO-REVISAR-OUTRO-REPO.md` | revisar outro repo sem mexer nele |
| `guia/GUIA-EQUIPE.md` | uso diário, 5 min — para a equipe |
| `guia/GIT-VERSIONAMENTO.md` | como versionar com git |
| `guia/REFERENCIAS.md` | bibliografia e pesquisas-base |
| `guia/web/index.html` | versão web (abre no navegador) |
| `PROMPT-CHAT-WEB-v4.4.md` (raiz) | instruções p/ colar no Claude.ai chat — encarnação do framework para ambientes sem filesystem (mesmos princípios, mesmos resultados, papéis/subagentes simulados) |
| `CHANGELOG.md` (raiz) | o que mudou, versão a versão |

## Para a IA (Claude Code e afins) — você normalmente NÃO edita à mão
| Arquivo/pasta | Função |
|---|---|
| `CLAUDE.md` (raiz) | entrada que o Claude Code lê sozinho |
| `AGENTS.md` (raiz) | entrada cross-tool (Cursor, Cline, etc.) |
| `AGENT-FRAMEWORK.md` (raiz) | o roteador (decide o modo) |
| `_shared/` | núcleo SSoT — regras transversais (fonte única) |
| `.agent/skills/` | papéis de processo (pmo, architect, …, explorer, _template) |
| `.agent/rules/` | regras sempre ativas |
| `.agent/workflows/` | slash commands (/start-session, /implement, …) |
| `.claude/agents/` | subagentes isolados (explorer, qa-critic) |
| `.claude/skills/` | espelho opcional p/ auto-trigger |
| `_meta/` | isolamento de subagente, external-access, evals |
| `exemplos/README.md` | guia de como criar aplicações de domínio (aplicações vivem FORA do núcleo) |

## Os dois únicos arquivos que VOCÊ preenche por projeto
- `docs/briefing.md` — objetivo, escopo, critério de aceite.
- `.agent/rules/00-glossario.md` — nomes/termos do projeto (fonte da verdade).
O resto a IA usa; você só ajusta quando decidir mudar uma regra.

## Regra mental
"Raiz + `guia/` = humano. `_shared/`, `.agent/`, `.claude/`, `_meta/` = IA."
