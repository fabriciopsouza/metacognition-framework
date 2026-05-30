# Requirements — v1.15.0 Allowlist por efeito + Enforcement fail-closed (Onda 1)

## Objetivo
Dar **dente executável** à segurança de ações onde é real (IDE) e declarar honestamente onde não é
(chat). Importa o runtime de segurança do JARVIS filtrado pela régua §0 — rejeitando o anti-padrão
que derrubou o JARVIS (governança autodeclarada segura, sem allowlist). Par de maior valor (P4+P1).

## Escopo IN
- `_shared/action-safety/SKILL.md` — política por efeito (E1–E6) + tiers (T1/T2/T3) + default-deny (ADR-014).
- `tools/hooks/effect-gate.ps1` (+ `.sh` paridade documentada) — deny-backstop T3 no IDE (ADR-015).
- `tools/managed-settings.template.json` — defense-in-depth fail-closed (instalação manual pelo dono).
- `tools/test_effect_gate.py` — canary "tenta furar e falha em furar".
- Campo `enforcement: {ide, chat}` em developer e qa-critic (skills que executam/auditam ação).

## Escopo OUT
- Classificador LLM geral por efeito (FNR 17% — rejeitado como gate único; ADR-014 alt 2).
- Instalação automática do managed-settings (exige privilégio fora do repo; documentada como passo do dono).
- Validação real do hook `.sh` em Linux/macOS (paridade documentada, não testada — [DESCONHECIDO]).

## Requisitos
- REQ-1: O canary bloqueia 100% dos payloads T3 inequívocos (rm -rf raiz/home, mkfs, dd device, push --force, fork bomb, firewall off).
- REQ-2: O canary NÃO bloqueia benignos (anti-fail-open / anti-falso-positivo).
- REQ-3: O hook falha de modo consciente: default=allow (backstop, não classificador); erro interno não bloqueia (managed-settings é o fail-closed) — documentado.
- REQ-4: Nenhuma skill afirma paridade `ide == chat` no campo `enforcement` (honestidade P1 §4).
- REQ-5: A política é agnóstica de domínio (classifica por efeito, não por nome/domínio).
- REQ-6: managed-settings.template.json contém os 3 toggles booleanos fail-closed (`disableBypassPermissionsMode`, `allowManagedHooksOnly`, `allowManagedPermissionRulesOnly`) + lista `deny` com `Bash(claude *)`.
- REQ-7: O contrato da Onda 0 continua PASS após adicionar `enforcement`/`action-safety` às skills.

## Bloqueadores honestos (P11 — documentar, não travar)
- Bug #44642 status atual [DESCONHECIDO] → defense-in-depth, não toggle único.
- Paridade `.sh` em Linux/macOS [DESCONHECIDO].
- Aceitação regulatória do gate-LLM como evidência de validação [DESCONHECIDO].
