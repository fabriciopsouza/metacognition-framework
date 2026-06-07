# ADR 067 — Onboarding na 1ª abertura: popup (usar×desenvolver), instala global, "feche o instalador e abra seu projeto"

- Status: **Aceito** (2026-06-05 — CI verde 3 SOs + qa-critic; detector testado) · Data: 2026-06-05 · Decisores: dono + squad (architect)
- Onda: onboarding/adoção · Tipo: **EMENDA** de ADR-006 (auto-boot global) — torna a 1ª abertura explícita. Atende: "ao clonar, popup GUI com link p/ instruções + ativação automática; instruir a NÃO modificar o repo (exceto intencional); instala, configura, fecha o instalador e abre a pasta do projeto".

## Contexto

O repo-framework é o **instalador** (espelha p/ `~/.claude`, ADR-006), não um workspace — o usuário trabalha nos **projetos dele**, onde o framework auto-boota. Mas nada deixa isso claro na 1ª abertura: o usuário pode tratar o instalador como workspace e modificá-lo. **Realidade técnica:** não há hook "ao clonar" (git clone não dispara nada); o 1º gatilho é a **abertura na IDE** (SessionStart). E "popup GUI" no Claude Code = **`AskUserQuestion`** (ato do agente). O canal de injeção que sinaliza (`inject-start-session`) **não é bloqueado** pelo Kaspersky (só os que spawnam processo são).

## Decisão (1 frase ativa)

**Na 1ª abertura do REPO-FRAMEWORK na IDE (detectado por `tools/framework_onboarding.py`: `AGENT-FRAMEWORK.md`+`_shared/`+`tools/web_export.py` na raiz **E `MASTER-CANÔNICO` pelo repo-identity-gate ADR-070** — ver Emenda abaixo, e marker `~/.claude/.framework-onboarded` ausente), o agente apresenta um popup `AskUserQuestion` com link p/ `guia/SETUP.md` e 2 opções:** **(a) Usar nos meus projetos** → roda o `bootstrap` (instala/ativa global, automático), marca onboarded, e **orienta: "instalei global; FECHE este instalador e abra a pasta do SEU projeto — o framework auto-boota lá (ADR-006); NÃO modifique o instalador"**; **(b) Desenvolver o framework** → marca `dev` e segue (o "exceto se intencionalmente"). Marca **1×** (não re-pergunta). Num **projeto que USA** (sem a assinatura da fonte), o passo é pulado. O passo é o **step 0 do `/start-session`** (doutrina; o popup é gate anunciado ADR-047, sinalizado pela injeção não-bloqueada).

## Alternativas consideradas

1. **Hook "ao clonar".** Não existe (git clone não dispara nada). **Impossível.**
2. **Popup só por hook de runtime.** Os hooks que spawnam são vetáveis (Kaspersky); e popup nativo não há. **Rejeitada → AskUserQuestion (agente) sinalizado por injeção.**
3. **Nada (deixar o auto-boot ADR-006 implícito).** O usuário confunde instalador com workspace e modifica. **Rejeitada (o ponto do dono).**
4. **Detector + popup no step 0 + marca 1× (ESCOLHIDA).** Explícito, idempotente, anti-modificação, ativação automática via bootstrap, separa usar×desenvolver.

## Consequências

**Positivas:** 1ª abertura deixa claro que é instalador (não workspace) → usuário não modifica por engano; ativação automática (bootstrap, idempotente); orienta a fechar e abrir o projeto (onde auto-boota — ADR-006); 1× (não nag); usar×desenvolver cobre o intencional; o popup funciona mesmo com Kaspersky (AskUserQuestion + injeção não-bloqueada). **Negativas/limite:** é 1ª-**abertura na IDE**, não 1ª-**clonagem** (sem hook de clone — declarado); o popup é ato do AGENTE (doutrina/gate anunciado, não mecanismo de runtime — coerente com ADR-047); a parte mecanizável é o detector + marker (testado), o popup é runtime. **Cascata:** o detector + a doutrina vão nas distribuições; o `--mark`/marker é por-máquina. **EMENDA** de ADR-006.

## Implementação (ponteiro)

`tools/framework_onboarding.py` (`is_framework_repo`/`is_canonical_master`/`needs_onboarding`/`mark_onboarded`, CLI `--check`/`--mark`); `tools/test_framework_onboarding.py` (detecta fonte, ignora projeto, **shadow→sem-popup**, master→popup, 1× idempotente); `.agent/workflows/start-session.md` step 0 (doutrina do popup). **DONE quando:** abrir o repo-framework 1ª vez → popup com link + opções; "usar" instala global e orienta a abrir o projeto; não re-pergunta. Status→Aceito após verificação.

## Emenda (2026-06-06 — escopo do gate amarrado ao ADR-070; EMENDA in-place, decisão preservada)

**Motivação (bug de escopo, `[CONFIRMADO]`):** `is_framework_repo` casava só a *assinatura da fonte* (`AGENT-FRAMEWORK.md`+`_shared/`+`tools/web_export.py`). Mas `export-clean.py` faz `copytree` da fonte inteira → os repos **public/premium** (e qualquer clone) **herdam a assinatura** e disparavam o popup "usar×desenvolver" no **usuário final** — contra o princípio "uso geral facilitado" (pedido do dono 2026-06-06). A pergunta deve existir **só na main**.

**Decisão da emenda:** `needs_onboarding` passa a exigir **`is_canonical_master()`** (verdito `MASTER-CANÔNICO` do repo-identity-gate, ADR-070) além da assinatura. Reuso puro (régua §0): a *trava física* já existe — `export-clean.py` carimba `.repo-identity.json` `role=shadow`, e o ADR-070 prova master via ancestralidade git. Export/clone/foreign (public/web/premium/gemini/etc) **nunca** disparam o popup. Fail-safe: em qualquer dúvida (sem git, ambíguo) → não interroga.

**Bugfix acoplado (EMENDA de §Implementação do ADR-070):** ao amarrar aqui, expôs-se que `repo_identity.py` não normalizava remote **SSH↔HTTPS** → o master com `origin` SSH caía em `FOREIGN` (`writable_master=False`), o que (a) quebraria este gate (popup jamais no master real) e (b) já fazia o repo-identity-gate dizer "escrita exige confirmação" no próprio master. Corrigido com `_norm_remote()` (canoniza p/ `host/owner/repo`); canário `tools/test_repo_identity.py`. **Decisão do ADR-067 inalterada** — só o predicado de "instalador" ficou mais preciso. Status segue **Aceito**.
