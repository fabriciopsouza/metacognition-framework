# Execution Report — Falha determinística na EXECUÇÃO de gates/canários (não no design)

- **Data:** 2026-06-08 · **Sessão:** claude-master · modo squad · repo MASTER-CANÔNICO
- **Pedido do dono:** "tudo isso tem que ser determinístico" + "relatórios sobre a falha determinística das
  execuções dos gates/canários".
- **Tese central:** os mecanismos **existem e são corretos** (provei ponta-a-ponta nesta sessão). A falha
  é de **GATILHO**: parte deles **não DISPARA deterministicamente** — degrada para "o agente deveria
  lembrar" (= prosa). Cerne [[feedback-prosa-vira-mecanismo]].

## A cisão que explica tudo: 2 classes de mecanismo

| Classe | Determinístico? | Por quê |
|---|---|---|
| **Canários de CI** (`run_canaries.py`, 3 SOs, required check) | ✅ SIM | rodam no servidor, fail-closed, fora do alcance do host/EDR. Provado: PR #3 (hub `gate`) e #73 (42 PASS/0 FAIL × 3 SOs) barram/passam sem intervenção. |
| **Gates de SESSÃO** (SessionStart hooks, passos de boot, fail-soft de fechamento) | ⚠️ NÃO, onde hook é vetado ou passo é manual | dependem de hook PS (Kaspersky/non-admin VETA — ADR-047) ou de o agente "lembrar" de rodar um passo opcional. |

**Conclusão:** determinismo **server-side** está sólido; determinismo **session-time** tem furos onde o
gatilho é hook-dependente numa máquina que bloqueia hooks, ou onde o passo é anunciado mas pulável.

## 4 falhas de EXECUÇÃO observadas (esta sessão + corroboradas no history.md)

1. **Boot-sync não forçado → DIVERGÊNCIA paralela (incidente desta sessão).**
   Pulei o `/start-session` (sync de boot é passo, não gate fail-closed). Trabalhei sobre base desatualizada e
   **refiz em paralelo** trabalho que outra sessão já mergeara (#71/#72). Detectado só quando o `git fetch`
   tardio mostrou `behind 2`. **Custo:** retrabalho + risco de clobber (evitado por rebase limpo).
   **Determinístico seria:** boot que **bloqueia ação de escrita até `git fetch`+reconciliação** terem rodado.

2. **Boot-scan ASSUMIDO-vazio (history.md, method-audit 2026-06-08).** A sessão canônica "assumiu
   silêncio=vazio sem testar" o `cross_ai_hub.py boot-scan` — prosseguiu como se não houvesse handoff,
   havendo (thread já no hub, 2 rounds). **Viola a regra anti-suposição** (inviolável). **Determinístico
   seria:** o resultado do boot-scan ser **confirmado por execução**, não inferido do silêncio.

3. **Mecanismos hook-gated INERTES no Kaspersky (history.md, 2 ocorrências).** `ensure-global-wiring`
   (self-heal do clobber autosuficiente), `context-budget PreToolUse(Read)`, `route-gate` — todos
   hook-dependentes; onde o EDR veta hooks PS, **não disparam**. Padrão: "mecanismo existe mas é
   hook-dependente onde hook está bloqueado". **Determinístico seria:** self-heal **NÃO-hook** (passo Python
   no `start-session`, como `repo_mode --mode` já faz — Python não é barrado).

4. **fail-soft que não roda no fechamento (history.md, method-audit 2026-06-02).** `consistency-gate`
   (ADR-030, fail-soft no docops) **não disparou** no encerramento de ~7 releases → `history.md` 7 versões
   atrás, 3 tags ausentes, ADR merged-as-Proposto. **Mecanismo existe ≠ executou.** Já parcialmente mitigado
   pelo `release-checkpoint-gate`/`process-evidence` fail-closed (ADR-074).

## Prova de que o DESIGN é são (o gatilho é o problema, não o mecanismo)
Nesta sessão executei a cadeia determinística **à mão** e ela funcionou 100%:
`boot-scan` (anunciou hub vazio→depois 5 handoffs) → `deposit` (gate verde local) → **PR #3** → CI `gate`
success → merge → `scan --me gemini-master` = **5 handoffs visíveis**. O mecanismo morde quando roda. O que
faltou foi ele **rodar sozinho**.

## Causa-raiz única
**Enforcement anunciado/advisory/hook-gated ≠ enforcement forçado.** Onde o gatilho é hook (vetável) ou
passo manual (pulável), o gate vira **doutrina**. A régua é o Princípio "prosa→mecanismo": enquanto o
gatilho for prosa, o gate é débito visível, não garantia.

## Direção de correção (alinhada ao item JÁ aberto em history.md)
O `origin/main` já registra o item aberto **"Integração protocolo cross-IA no fluxo J0-J5"**. Consolidando:
1. **Boot fail-closed mínimo:** escrita bloqueada até `git fetch`+reconciliação+boot-scan terem **executado**
   (não assumido). Não-hook (passo Python no `start-session`), p/ sobreviver ao Kaspersky.
2. **docops §Encerramento dispara `outbox→hub`** no J5 (determinístico, não "lembrar de depositar").
3. **consistency-gate checa threads cross-IA abertas** + version-sync no fechamento, fail-closed no subset.
4. **Self-heal não-hook** do modo de execução (re-aplica `framework-mode.json` via Python no boot).

**Teste binário de pronto:** uma 2ª sessão abrindo **não consegue** escrever sem ter sincronizado, e o
boot-scan **prova** (não assume) que viu/não-viu handoff. Hoje: não — por isso esta sessão divergiu.
