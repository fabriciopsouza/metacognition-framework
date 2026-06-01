# ADR 037 — Action-safety em overwrite de artefato não-criado/não-lido nesta sessão

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: remediação v2 (marco v1.27.0) · Tipo: **novo** (1 hook .ps1/.sh + 1 canário) — net-gain por fechar um efeito destrutivo (E1) que passava pelo effect-gate.
- Origem no plano: item 5 ⭐ (`[campo]` #13 — agente sobrescreveu um relato com conteúdo anterior sem ler nem avisar). Relaciona: `_shared/action-safety` (efeito), ADR-015 (effect-gate só vê Bash/PowerShell), ADR-040 (paridade), bug GitHub #37210.

## Contexto

`action-safety` classifica por efeito, mas o `effect-gate` (ADR-015) só inspeciona Bash/PowerShell.
Overwrite via tool **`Write`/`Edit`** sobre arquivo **com conteúdo anterior não-criado/não-lido nesta
sessão** é efeito destrutivo (E1) que **passava**. No incidente, um relato com conteúdo foi sobrescrito
sem leitura prévia. A intenção de segurança é simples: **ler/criar antes de sobrescrever** — ter LIDO o
arquivo nesta sessão torna o overwrite informado.

## Decisão (1 frase ativa)

Criar `tools/hooks/overwrite-guard.ps1` (+ `.sh`), wirado em `PreToolUse(Write|Edit)` como **gate** (se
o path existe, tem conteúdo, e **não está no manifesto da sessão** — não foi lido nem criado nesta
sessão — então **`exit 2`** bloqueando e pedindo leitura) e em `PostToolUse(Read|Write|Edit|NotebookEdit)`
como **record** (registra o path no manifesto `.agent/brain/session-files.json`, keyed por `session_id`),
usando **`exit 2`** (não `permissionDecision:deny`) por causa do bug #37210.

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** O overwrite cego (E1) continua passando. **Rejeitada — é o gap.**
2. **Estender o effect-gate para gatear Write/Edit com `permissionDecision:deny`.** O bug #37210 pode IGNORAR `deny` para Edit/MCP — false-PASS. **Rejeitada** — usar `exit 2` (robusto) num hook dedicado.
3. **Gate estático "não sobrescreva nunca sem flag".** Bloquearia o fluxo legítimo de editar arquivos lidos. **Rejeitada** — a chave é "lido/criado nesta sessão", não "nunca".
4. **Hook PreToolUse(gate) + PostToolUse(record) com manifesto por sessão (ESCOLHIDA).** Prós: bloqueia só o overwrite **cego** (não-lido); editar o que se leu passa; `exit 2` devolve ao MODELO (não é popup humano). Contras: depende do manifesto — mitigado por fail-open e por o record cobrir Read.

## Consequências

**Positivas:** sobrescrever um artefato com conteúdo sem tê-lo lido vira bloqueio mecânico; alinha
`action-safety` ao efeito real do tool Write/Edit (não só shell). **Negativas:** adiciona 2 wirings de
hook (PreToolUse + PostToolUse). **Riscos/aprendizado (dogfood real nesta sessão):**
(a) **PowerShell desembrulha array de 1 elemento para escalar** → `+=` concatenou paths no manifesto e o
gate passou a super-bloquear; corrigido com `[System.Collections.Generic.List[string]]`. (b) `$event` é
**variável automática** do PowerShell — renomeada para `$evt`. (c) `-AsArray` é PS7+ (quebraria 5.1) —
removido. O hook **pegou a própria edição do agente** durante a implementação — prova viva do mecanismo.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.23-v1.31-remediacao` · `2026-05-31` · grep `overwrite-guard`
- Artefatos: `tools/hooks/overwrite-guard.ps1` + `.sh`, `tools/test_overwrite_guard.py` (testa .ps1 +
  paridade .sh quando há jq), wiring em `.claude/settings.json` (PreToolUse Write|Edit + PostToolUse).
- DONE quando: hook no CI + paridade `.sh`/`.ps1` (canário próprio + matriz ADR-040). [CONFIRMADO]
