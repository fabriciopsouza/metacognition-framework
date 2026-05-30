# ADR 015 — Enforcement executável + fail-closed (gate no IDE, honestidade no chat)

- Status: Aceito
- Data: 2026-05-30 · Decisores: dono (briefing v1.14.x) + squad (autônomo)
- Onda: 1 (segurança executável) · Pesquisa: **P1** · Tipo: **EMENDA** (Princípios 1, 13)
- Relaciona: ADR-014 (política por efeito — o *quê*; este ADR é o *como*), ADR-013 (campo `enforcement`), ADR-005.

## Contexto

ADR-014 define a política (classes de efeito + tiers). Sem **mecanismo**, é prosa. P1 mostra como
dar dente no IDE — e onde o dente **não existe** (chat).

Achados centrais de P1 [CONFIRMADO]:
- Hook `PreToolUse` do Claude Code: **exit 2 bloqueia** (stderr volta ao Claude); exit 0 → parseia
  JSON de decisão; **qualquer outro código, incluindo exit 1, é não-bloqueante — a ação PROSSEGUE.**
  → um hook bugado **falha aberto**. Logo, o hook deve ser conservador e testado por canary.
- Forma expressiva preferível ao exit 2 puro: exit 0 + `hookSpecificOutput.permissionDecision:
  "deny"` + `permissionDecisionReason`; precedência entre hooks `deny > ask > allow`.
- Fail-closed em camadas (bug #44642 — `disableBypassPermissionsMode` falhou em macOS): **nunca
  toggle único.** `managed-settings.json` (`disableBypassPermissionsMode`, `allowManagedHooksOnly`,
  `allowManagedPermissionRulesOnly`) + deny `Bash(claude *)` + **teste adversarial canary em CI**.
- **No chat web NÃO existe equivalente real ao exit 2.** Self-check garante forma, não cumprimento.
  Sem verificador externo ao chat, "gate" no chat é texto que o próximo turno renegocia.

**Régua §0:** EMENDA — não cria papel; converte regras já existentes (prosa do `high-stakes-gate`,
denylist do ADR-005) em gate executável onde é real, e marca honestamente onde não é.

## Decisão (1 frase ativa)

Migrar para **gate executável no IDE** as regras T3 inequívocas via hook `PreToolUse` que emite
`permissionDecision: deny` por **efeito** (backstop conservador, não classificador geral), protegido
por `managed-settings` fail-closed em camadas e por **teste canary** que tenta furar a política e
falha em furar; e declarar em cada skill o nível de garantia por ambiente via campo
`enforcement: {ide, chat}` que **nunca afirma paridade**.

### Mecanismo
1. **Hook `tools/hooks/effect-gate.ps1`** (+ paridade `.sh` documentada): lê `tool_input`,
   classifica por **padrões de efeito inequívocos T3** (E1∩E2: `rm -rf /` e variantes de home/raiz,
   `mkfs`, `Format-Volume`, `dd of=/dev/`, `git push --force` em protegida, `:(){ :|:& };:`),
   emite `permissionDecision: deny` + razão. **Default do hook = allow** (não classifica o universo;
   é backstop). Falha → exit 2 fail-closed só nos padrões reconhecidos; erro interno → loga e não bloqueia (P1).
2. **`tools/managed-settings.template.json`** — template de defense-in-depth para o dono instalar em
   `C:\ProgramData\ClaudeCode\` (Windows) / `/Library/Application Support/ClaudeCode/` (macOS):
   `disableBypassPermissionsMode`, `allowManagedHooksOnly`, `allowManagedPermissionRulesOnly`,
   deny `Bash(claude *)`. Documentado como **não-desativável por config de conveniência** (anti-JARVIS).
3. **Canary `tools/test_effect_gate.py`** — alimenta o hook com payloads T3 e confirma `deny`;
   alimenta payloads benignos (ls, git status) e confirma que NÃO bloqueia (anti-falso-positivo).
   Critério de aceite P1: *existe teste que tenta furar e falha em furar*.
4. **Campo `enforcement: {ide, chat}`** populado nas skills que carregam regra T3
   (qa-critic, developer, high-stakes via shared_ref). Ex.: `{ide: "hook:deny + managed-settings",
   chat: "self-declared + verificador-externo-ausente"}`. **Nunca** `ide == chat`.

## Alternativas consideradas
1. **Só prosa (status quo).** Prós: zero código. Contras: regra que o próximo turno renegocia; sem
   dente no IDE. Rejeitada — é o problema que a série ataca.
2. **Hook classificador geral por efeito (intercepta tudo).** Prós: cobertura ampla. Contras:
   FNR alto → falsos-negativos perigosos; falsos-positivos travam trabalho legítimo; e como exit≠2
   falha aberto, bug no classificador = sem proteção. Rejeitada — fail-open é a direção errada.
3. **Hook backstop conservador + managed-settings + canary + honestidade chat (ESCOLHIDA).**
   Prós: defense-in-depth, fail-closed nos casos certos, testável, honesto. Contras: não cobre o
   universo (por design — o julgamento amplo é da política ADR-014 + humano).

## Consequências
**Positivas:** T3 inequívoco bloqueado deterministicamente no IDE; governança em camadas resiste ao
bug #44642; honestidade cross-ambiente codificada (não promete o que não entrega).
**Negativas:** +1 hook + 1 template + 1 canary (~3 arquivos pequenos); o dono precisa instalar o
managed-settings manualmente (documentado) para a camada não-desativável valer.
**Riscos:** (a) bug #44642 status atual **[DESCONHECIDO]** — por isso defense-in-depth, não toggle
único. (b) hook em PowerShell é Windows-first; paridade `.sh` documentada mas não testada aqui
**[DESCONHECIDO]** em Linux/macOS. (c) Aceitação regulatória do gate-LLM como evidência **[DESCONHECIDO]**.

## Implementação (ponteiro após aceito)
- Ponteiro: branch `feat/v1.15.0-allowlist-enforcement` · `2026-05-30` · grep `effect-gate|managed-settings|enforcement`
- Artefatos: `tools/hooks/effect-gate.ps1`, `tools/hooks/effect-gate.sh`, `tools/managed-settings.template.json`, `tools/test_effect_gate.py`, campo `enforcement` em skills T3.
