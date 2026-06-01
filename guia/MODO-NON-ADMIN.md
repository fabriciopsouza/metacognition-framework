# Modo NON-ADMIN — framework em máquina com restrição de scripts (ADR-047)

> Para máquinas corporativas onde a política (GPO) bloqueia execução de PowerShell — os hooks
> (`powershell.exe -ExecutionPolicy Bypass`) **não rodam** e o framework "não inicia". Esta versão
> **inicia sob restrição**, sem perder funcionalidade, pelo trade-off do dono:
> **automação nunca invisível** — o que era hook silencioso vira **gate anunciado e aplicado pelo agente**.
>
> **A versão ADMIN (com hooks) continua e é a default.** A non-admin é uma variante paralela.

## O problema (e por que o admin falha lá)
A política `Restricted` via Group Policy **ignora** `-ExecutionPolicy Bypass` → todo `.ps1` é barrado.
Os hooks de SessionStart/PreToolUse falham → a abertura quebra. **Python NÃO é barrado** pela política de PS.

## A solução non-admin (sem perdas relevantes)
1. **Settings sem hooks** (`settings.nonadmin.json`): nada invoca PowerShell → inicia limpo.
2. **Gates anunciados** (CLAUDE.md §Modo non-admin): o agente **declara e aplica inline** cada gate que
   o hook faria — `ROTA:` (route-gate), `mission`/product_type, `action-safety` por efeito, ler-antes-de-
   sobrescrever (overwrite-guard). **Avisado, solicitado, com orientação** — nunca silencioso.
3. **Linters/gates Python continuam** chamáveis sob demanda (`check_spec_depth`, `check_completeness`,
   `check_input_contract`, `effect-rules`…) — Python roda sob a política. O agente os invoca e anuncia.

## Como ativar (sem admin, sem PowerShell)
**Opção A — pacote pronto (clone-and-go):** clonar o repo público **non-admin** (settings.json já sem
hooks). Funciona ao abrir.
**Opção B — numa instalação existente:** rodar `python bootstrap.py` (Python puro; ativa o perfil
non-admin copiando `settings.nonadmin.json` → `settings.json`, backup em `.bak`; espelha skills p/ `~/.claude`).
**Opção C — manual:** copiar `.claude/settings.nonadmin.json` por cima de `.claude/settings.json`.
Diagnóstico: `python bootstrap.py --check` (diz se o PS roda e se há hooks ativos).

## Trade-off declarado (→ LIMITS.md)
| | Admin (hooks) | Non-admin (anunciado) |
|---|---|---|
| Enforcement | automático/silencioso (hook) | **anunciado + aplicado pelo agente** (visível) |
| Inicia sob GPO restrita | não (PS barrado) | **sim** (sem PS) |
| Gates Python on-demand | sim | sim |
| Risco | hook pode falhar silencioso | depende do agente aplicar — por isso **anunciar é obrigatório** |

**Um aponta para o outro:** o admin referencia esta página como fallback sob restrição; a non-admin
referencia o admin como a versão com enforcement automático quando a máquina permite.

## Toda mudança no framework atualiza AMBOS os públicos
A cada release, o pipeline regenera o público (admin) **e** o público non-admin (settings sem hooks) —
ver ADR-047 §Implementação. A non-admin é o mesmo framework, só sem a camada de hooks.
