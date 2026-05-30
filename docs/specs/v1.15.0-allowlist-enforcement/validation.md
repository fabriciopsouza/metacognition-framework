# Validation — v1.15.0 Allowlist por efeito + Enforcement fail-closed (gate binário)

| # | Critério | Como verificar | V/F |
|---|---|---|---|
| V1 | `python tools/test_effect_gate.py` retorna exit 0 (ou SKIP se sem pwsh) | rodar | — |
| V2 | Canary bloqueia TODOS os payloads T3 (rm -rf /, ~, mkfs, dd, push --force, fork bomb, firewall off) | V1 | — |
| V3 | Canary NÃO bloqueia benignos (ls, git status, push normal, --force-with-lease, rm local, mkdir) | V1 (anti-fail-open) | — |
| V4 | `_shared/action-safety/SKILL.md` passa o contrato? (N/A — _shared fora do gate; mas frontmatter bem-formado) | inspeção | — |
| V5 | ADR-014 define E1–E6 + T1/T2/T3 + default-deny; ADR-015 define hook+managed+canary+enforcement | leitura | — |
| V6 | Honestidade: nenhuma skill afirma paridade ide=chat em `enforcement` | grep enforcement | — |
| V7 | managed-settings.template.json é JSON válido com os 3 toggles booleanos + deny Bash(claude *) | parse + grep | — |
| V11 | Canary cobre bypasses (rm -r -f /, --recursive --force, alvo entre aspas, /bin/rm) | grep CASES + V1 | — |
| V8 | hook default = ALLOW (não classifica universo; erro interno não bloqueia) — P1 fail-open consciente | leitura do código | — |
| V9 | Régua §0: EMENDA (absorve denylist ADR-005 como camada), agnóstico, sem papel novo | PC | — |
| V10 | Contrato (Onda 0) ainda PASS após edição de skills com `enforcement` | `python tools/validate_skills.py` | — |

## Nota de honestidade (P1 §4)
V2/V3 provam o gate **no IDE**. No **chat** não há equivalente — V6 garante que isso é declarado, não
mascarado. O canary é a evidência "tenta furar e falha em furar"; ele NÃO prova cobertura do universo
(por design: o hook é backstop, o julgamento E1–E6 é da política + humano).
