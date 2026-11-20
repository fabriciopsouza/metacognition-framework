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
1. **Hooks desligados:** no pacote pronto, `settings.json` sem hooks (`settings.nonadmin.json`); numa
   instalação existente, `"disableAllHooks": true` em `.claude/settings.local.json` (não versionado).
   Nada invoca PowerShell → inicia limpo.
2. **Gates anunciados** (CLAUDE.md §Modo non-admin): o agente **declara e aplica inline** cada gate que
   o hook faria — `ROTA:` (route-gate), `mission`/product_type, `action-safety` por efeito, ler-antes-de-
   sobrescrever (overwrite-guard). **Avisado, solicitado, com orientação** — nunca silencioso.
3. **Linters/gates Python continuam** chamáveis sob demanda (`check_spec_depth`, `check_completeness`,
   `check_input_contract`, `effect-rules`…) — Python roda sob a política. O agente os invoca e anuncia.

## Como ativar (sem admin, sem PowerShell)
**Opção A — pacote pronto (clone-and-go):** clonar o repo público **non-admin** (settings.json já sem
hooks). Funciona ao abrir.
**Opção B — numa instalação existente:** rodar `python bootstrap.py` (Python puro; espelha skills p/
`~/.claude`). Ele testa se o PowerShell executa um `.ps1` como os hooks executam. Se **não**, grava
`"disableAllHooks": true` em `.claude/settings.local.json`, preservando as demais chaves; se **sim**,
mantém os hooks e não altera configuração. O `.claude/settings.json` versionado nunca é tocado
(ADR-047, emenda 20/11/2026).
**Opção C — manual:** acrescentar `"disableAllHooks": true` ao objeto JSON de
`.claude/settings.local.json` (criar o arquivo com `{"disableAllHooks": true}` se não existir).

- Vale a partir da **próxima sessão**, para **todas as sessões deste clone**. Sessão já aberta: efeito
  não garantido.
- Para remover o override local: apagar a chave `disableAllHooks` do `.claude/settings.local.json`.
- Sonda sem resposta (timeout ou erro): o bootstrap não grava nada e sai com código 1; rodar de novo
  ou usar a opção C.
- Host sem `powershell.exe` (Mac/Linux): `python bootstrap.py` grava o override e desliga **todos** os
  hooks do clone, inclusive os em Python. Nesses hosts use `bootstrap.sh`.
- A regravação reformata o `settings.local.json` (indentação 2; chave duplicada fica só a última).
- Instalação antiga, de quando o bootstrap copiava o perfil por cima do `settings.json`: conferir
  `git diff .claude/settings.json`, salvar a versão atual se houver ajuste próprio, e recuperar a versão
  do git.

Diagnóstico: `python bootstrap.py --check` (diz se o PS executa os hooks, se o `settings.json` do
projeto tem hooks e se o override local está ativo).

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
