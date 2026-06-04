# ADR 061 — Auditor de liveness de hooks: falha de hook NUNCA é silenciosa (+ porte do 2º hook vetado)

- Status: **Aceito** (2026-06-04 — gate de aceite: CI verde 3 SOs + qa-critic; verificação na máquina deferida pelo dono) · Data: 2026-06-04 · Decisores: dono + squad (architect/developer)
- Onda: resiliência de runtime (alvo v1.42.0) · Tipo: **adição reconciliada** (estende ADR-060). Atende: "checar todos os vetados + os que podem ser vetados; 100% anti-bloqueio; falha silenciosa quebra a confiança".
- Relaciona: ADR-060 (sync resiliente a EDR), ADR-019/020 (gates de boot), ADR-027 (route-gate), ADR-047 (gates anunciados / non-admin).

## Contexto

O Kaspersky AAC veta hooks que `powershell.exe` usa para spawnar processo+rede. Inventário (explorer, file-first) dos 17 pontos de hook: **2 confirmados vetados** (`check-repo-sync`, `check-core-agnostic`); **3 "podem ser vetados"** por spawnarem processo/rede (`sync-global`/`framework-sync`, `framework-boot` [GLOBAL, hand-maintained em `~/.claude`, maior exposição], `inject-start-session-global`); os demais ~8 são BAIXO (só leem arquivo + injetam texto — o rule "PowerShell ofuscado" não dispara). O hook é **fail-soft** → quando vetado, a sessão prossegue **como se** o gate tivesse rodado. **Esse silêncio quebra a confiança** (o dono não sabe que o gate está inerte).

**Verdade adversarial (anti-overclaim, dogfood do ADR-059):** "100% anti-bloqueio" **puramente em código é impossível** contra um EDR adaptativo — o único 100% anti-bloqueio é a **exclusão/allowlist** (ou assinatura). O que código **garante 100%** é a **ausência de falha silenciosa**: se um hook não roda, o framework **detecta e declara**. Reescrever a maquinaria de BOOT (`sync-global`/`framework-boot`) para Python seria grande, **não-testável neste ambiente** (sem pwsh) e roda em TODA sessão de TODA máquina — merge cego arriscaria quebrar o boot em todo lugar (quebra-confiança maior). Logo: não reescrever boot cego.

## Decisão (1 frase ativa)

**Instituir um AUDITOR DE LIVENESS não-bloqueável que torna toda falha de hook auditado DECLARADA (nunca silenciosa):** cada hook auditado **carimba** `.claude/.hooklive/<key>=<session_id>` quando roda; o **route-gate** (que só lê arquivo + injeta texto → não é bloqueável pela regra AAC, e roda todo turno) lê o **manifesto** (`tools/hooks/hooks-manifest.json`) + os carimbos e **declara qualquer gate cujo carimbo ≠ sessão atual** (com o fallback manual). **+ Portar o 2º hook vetado** (`check-core-agnostic` → `check_core_agnostic_hook.py`, python+fallback) para reduzir a superfície. Boot machinery (`sync-global`/`framework-boot`) **NÃO** é editada às cegas — fica coberta pela **exclusão do Kaspersky** (o 100% real) e, transitivamente, o auditor pega seus efeitos via os gates auditados.

## Alternativas consideradas

1. **Portar TODOS os hooks (incl. boot) para Python.** Grande, não-testável aqui, roda em toda máquina → merge cego quebra boot. **Rejeitada (risco > benefício; o auditor já mata o silêncio).**
2. **Só portar + confiar no fail-soft.** Mantém o silêncio (o que quebra a confiança). **Rejeitada.**
3. **Auditor de liveness + porte do caso contido + exclusão p/ o resto (ESCOLHIDA).** Garante 100% anti-silêncio (alcançável), reduz superfície no que é seguro/testável, e é honesto sobre o 100% anti-bloqueio (= exclusão).

## Consequências

**Positivas:** nenhum gate auditado falha em silêncio — o route-gate declara "hook X não rodou → gate INERTE → aplique manual: <hint>", auto-resolvente (cala quando o carimbo bate); o 2º hook vetado vira python (escapa do AAC); o auditor é session_id-keyed (sem falso-alarme em sessão longa) e não-bloqueável (só lê arquivo). **Negativas/limite (caminhos de silêncio/ruído residual — declarados honestamente, pós-qa-critic):**
- o auditor cobre os hooks **no manifesto** (os que carimbam) — hoje os 2 confirmados; `sync-global`/`framework-boot` **não** são auto-auditados (editar boot é arriscado/untestável) → cobertos pela **exclusão** + transitivamente; se o AAC um dia vetar um hook BAIXO, basta adicioná-lo ao manifesto + carimbo (extensível).
- **Manifesto ausente** (`tools/hooks/hooks-manifest.json` deletado/clone parcial) → o auditor pula **em silêncio** (não avisa que ELE mesmo está inativo). Mitigação: o manifesto é versionado no repo (presente em clone normal).
- **Sem `session_id`** no stdin do route-gate → auditor pula (degradação graciosa, sem falso-alarme). O engine envia session_id em produção.
- **route-gate ele mesmo vetado/com erro** → silêncio total. É o pressuposto: route-gate só lê arquivo → não-bloqueável pela regra AAC; se a premissa falhar, **só a exclusão garante**.
- **Falso-alarme benigno do fallback:** quando o fallback `.ps1` roda (python ausente), ele **não carimba** (predates ADR-061) → o auditor declara o gate "inerte" mesmo tendo rodado. O conselho ("rode git fetch / o linter") é **inócuo**; ocorre só em máquina sem Python (raro). Fix futuro: stdin+carimbo no .ps1 (evitado agora por ser PS untestável). O `route-gate` ganha um invariante: **nunca pode spawnar processo/rede** (senão vira bloqueável e o auditor cai junto). **Verificação na máquina do dono pendente** (sem pwsh + AV local). **Cascata:** entra no admin/premium; non-admin não tem hooks.

## Implementação (ponteiro)

`tools/hooks/hooks-manifest.json` (hooks auditados + fallback manual); `check_repo_sync.py` + `check_core_agnostic_hook.py` carimbam `.claude/.hooklive/<key>` (session_id via stdin SessionStart, tty-guard); `route-gate.ps1` §2.5 = auditor (lê manifesto+carimbos, declara inertes, só-leitura, fail-soft); `settings.json` check-core-agnostic → `cmd /c "python || powershell"`; `.gitignore` (`.claude/.hooklive/`). **DONE quando:** na máquina do dono, abrir sessão com os hooks vetados → o route-gate DECLARA os gates inertes (não silencioso) e some quando a exclusão é aplicada. **Não-testável no sandbox:** disparo real + comportamento do Kaspersky. Status→Aceito após verificação do dono + merge.
