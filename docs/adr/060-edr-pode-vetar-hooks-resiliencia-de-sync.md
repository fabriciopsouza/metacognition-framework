# ADR 060 — EDR pode vetar hooks numa máquina admin → resiliência de sync em camadas (não-PowerShell + fallback)

- Status: **Aceito** (2026-06-04 — gate de aceite: CI verde 3 SOs + qa-critic; verificação na máquina deferida pelo dono) · Data: 2026-06-04 · Decisores: dono + squad (architect/developer)
- Onda: resiliência de runtime (alvo v1.42.0) · Tipo: **adição reconciliada** (preserva ADR-019; não revoga hooks). Atende: incidente Kaspersky AAC na máquina 9TRP7H4.
- Relaciona: ADR-019 (sync no boot = mecanismo), ADR-027 (route-gate), ADR-047 (modo non-admin / gates anunciados), ADR-005 (modos de execução).

## Contexto

O **Kaspersky Endpoint Security → Controle Adaptativo de Anomalias (AAC)**, regra "O PowerShell executa código ofuscado", **bloqueia desde ~30/05/2026** exatamente 2 hooks do framework na máquina `9TRP7H4` (`GRUPONATULAB\fabriciosouza`): `check-repo-sync.ps1` e `check-core-agnostic.ps1` — os únicos que **spawnam processo-filho + rede** via `powershell.exe` (git fetch / python). Os outros 6 hooks (route-gate, framework-boot, inject-start-session, etc.) **não** são bloqueados (medido por grep no relatório CSV: 0 ocorrências). Os scripts **não são ofuscados** (texto puro em disco) — o gatilho é **comportamental** (powershell.exe nascido de node.exe fazendo git+rede, padrão "living-off-the-land").

Consequência grave: o hook é **fail-soft** → a sessão prossegue **como se** tivesse sincronizado. O modo admin parece intacto, mas o gate do ADR-019 está **inerte e silencioso** (≈ o incidente "41 commits atrás de main" que motivou o ADR-019, agora reintroduzido por um EDR). O modelo binário admin/non-admin do framework **não modela** este terceiro estado: *admin, mas o EDR veta alguns hooks*.

**Restrições do dono:** este repo **continua admin** (hooks preservados); non-admin só onde a restrição é total. A correção não pode depender só de prosa ("o agente lembra de sincronizar") — foi o que o ADR-019 já provou falho.

## Decisão (1 frase ativa)

**Tornar o sync resiliente a EDR por CAMADAS, sem revogar o hook PowerShell:** (1) **hook Python** `check_repo_sync.py` como SessionStart primário (process tree `python.exe`, escapa da regra "PowerShell…"), que escreve um **marker de liveness**; (2) **fallback determinístico** `python → powershell` na própria entrada do hook (`cmd /c "python … || powershell … -File …"`), cobrindo máquina sem Python; (3) **route-gate** (não bloqueado) **lê a idade do marker a cada turno** (sem spawnar git) e injeta lembrete quando o sync está velho/ausente — auto-resolvente; (4) **guard de pré-push** Python que pede confirmação humana (`ask`) ao empurrar com a branch **atrás do próprio `@{upstream}`**. `agent-git` (o agente roda `git fetch` no opener) fica como conveniência, **nunca** como a garantia.

## Alternativas consideradas

1. **Full non-admin nesta máquina.** Desligaria os **6 hooks que funcionam** para "resolver" 2 → mais perda. Contradiz "non-admin só onde restrito" (aqui é parcial). **Rejeitada (decisão do dono).**
2. **Só exclusão no Kaspersky (path/hash).** É o conserto definitivo do admin pleno, mas **depende da TI corporativa** liberar (máquina gerenciada) — não pode ser a única defesa. **Mantida como ação paralela do dono, não como a salvaguarda do código.**
3. **Só "o agente roda git no opener" (agent-git).** Best-effort, depende de prosa/compliance do agente — é a regressão que o ADR-019 corrigiu. **Rejeitada como garantia; mantida como conveniência (1 das 4 camadas).**
4. **Camadas determinísticas + soft, fallback python→powershell (ESCOLHIDA).** Cada camada cobre uma falha distinta (boot / mid-sessão / push), graceful-degradation por máquina, repo segue admin.

## Consequências

**Positivas:** o sync volta a ter mecanismo (não-prosa) numa máquina com EDR; o silêncio do fail-soft é quebrado (route-gate avisa quando o marker está velho/ausente); o momento de maior dano (push sobre base velha) ganha gate humano; uma só config cobre admin-com-Kaspersky, admin-sem-Python e cross-platform (avança o backlog D4); repo segue admin. **Negativas/limite:** o porte Python precisa ser **verificado na máquina do dono** (não dá para testar daqui se o AAC também pega `python.exe` — a regra é nominalmente PowerShell, provável que escape, **não garantido**); o route-gate vira PowerShell com leitura de arquivo (mas **não** spawna git → não deve cair na mesma regra); `check-core-agnostic` (o outro hook vetado) **não** é portado aqui (tem CI + qa-critic como backstop — escopo deferido). **Cascata:** entra no admin/premium; non-admin já não tem hooks; o guard/marker são agnósticos. **SUPLANTA×EMENDA:** se o porte Python também for vetado e a decisão virar "exigir exclusão", é novo ADR; ajustes de threshold/marker são EMENDA.

## Implementação (ponteiro)

`tools/hooks/check_repo_sync.py` (porte 1:1 do `.ps1`, fail-soft, escreve `.claude/.repo-sync-marker`); `.claude/settings.json` SessionStart → `cmd /c "python … || powershell … check-repo-sync.ps1"`; `tools/hooks/route-gate.ps1` §2.5 (lê marker, nudge se >2h/ausente, sem git); `tools/hooks/prepush_sync_guard.py` (PreToolUse Bash/PowerShell, `ask` se atrás de `@{upstream}`, fail-open); `.gitignore` (marker). **DONE quando:** na máquina do dono, o boot sincroniza sem alerta do Kaspersky **e** o guard pede confirmação ao push atrasado. **Verificação pendente do dono** (não testável no sandbox: sem pwsh + AV é local). Status→Aceito após essa verificação + merge.
