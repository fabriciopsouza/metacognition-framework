# /start-session — Abertura canônica (genérico)

Primeiro turno de cada sessão. Obrigatório.

## Sequência (PMO)
0.0. **MODO POR IDENTIDADE — user × dev (ADR-070/072, MECANISMO não prosa):** `python tools/repo_mode.py --mode`. Se **`user`** (= `SOMBRA-EXPORT`: premium/public/web de QUALQUER IA), esta sessão é **MODO-USUÁRIO**: você **APLICA** o framework a um domínio — **NÃO** desenvolve o framework, **NÃO** trata ADR/WIP, **NÃO** reconcilia history de dev, **NÃO** pergunta como resolver sync (o `shadow_sync` já casou com origin automaticamente). **Pule os passos 1–3 dev abaixo**; foco = briefing do domínio do usuário. Única ação de framework-dev permitida: **relatório opt-in**. Write-back está bloqueado (`shadow_write_guard`). Se **`dev`** (= `MASTER-CANÔNICO`), siga o protocolo dev completo (passos 0–4). O hook já injeta isso no boot; sem hook (Kaspersky), VOCÊ roda `--mode`.
0. **ONBOARDING — repo-framework × projeto (ADR-067 + EMENDA ADR-070):** se `python tools/framework_onboarding.py --check` disser `precisa_popup=SIM` (= você abriu o **REPO-FRAMEWORK / instalador no MASTER-CANÔNICO**, 1ª vez), apresente um **popup `AskUserQuestion`**. **Só dispara no master canônico** — export/clone/public/web/premium/gemini (carimbados `role=shadow` ou reprovados na ancestralidade git) **NÃO** disparam (anti-vazamento: o usuário final nunca é interrogado "usar×desenvolver"). Em dúvida, `--check` mostra `master_canonico=...`; se `False`, pule este passo. com link para `guia/SETUP.md` e 2 opções: **(a) Usar nos meus projetos** → rode o `bootstrap` (instala global), `python tools/framework_onboarding.py --mark use`, e **oriente: "instalei global; FECHE este repo e abra a pasta do SEU projeto — o framework auto-boota lá (ADR-006). NÃO modifique o instalador."**; **(b) Desenvolver o framework** → `--mark dev` e siga normal (o "exceto se intencionalmente"). Marca 1× (não re-pergunta). Num **projeto** que USA o framework (sem `AGENT-FRAMEWORK.md` na raiz), pular este passo.
0.4. **Indice de capacidades (ADR-072 — file-first OBRIGATORIO):** LER `CAPABILITIES.md` (raiz) ANTES de afirmar que uma feature falta ou de (re)projetar mecanismo — e o mapa vivo feature->{executavel, canario, ADR, doc}. *Evita o modo de falha 2026-06-06: reportar "X nao existe" quando X ja estava implementado.* Recall direcionado: grep no `CAPABILITIES.md`/`capabilities.json`. Onde o hook roda, ele injeta o indice no boot; onde Kaspersky veta hook (ADR-047), VOCE le o arquivo. Manutencao: ao entregar feature nova, adicionar 1 registro em `capabilities.json` + `python tools/build_capabilities.py` (canario `test_capabilities.py` barra drift).
0.5. **Insights do corpus (ADR-068 — fail-soft):** o hook já injetou `session-insights.md` no contexto se o catálogo existir — leia os insights presentes. Para recall on-demand: `python tools/knowledge_catalog.py --recall --context "keywords"`. Rebuild após novos relatórios: `python tools/knowledge_catalog.py --build`.
0.6. **Hub scan cross-IA no boot (ADR-069, file-first OBRIGATÓRIO — não-silencioso):** `python tools/cross_ai_hub.py boot-scan --me <id>` (ex. `claude-master`). Descobre handoffs ABERTOS endereçados a mim no hub cross-IA clonado, resolvendo o path por `CROSS_AI_HUB` (env) → `~/.claude/cross-ai-hub-path.txt` → `.agent/cross-ai-hub-path.txt`. **Boot ANUNCIA** os handoffs (ou anuncia que o hub não está configurado, com como configurar) — nunca silêncio. *Ler ≠ aceitar:* agir sobre um handoff exige passar pelo qa-critic adversarial (ADR-011) → `cross_ai_gate` → `equivalence_gate`/`verify_hitl_proofs`. Onde a máquina permite hook, espelhe isto num `SessionStart` (settings); onde Kaspersky/non-admin veta hook (ADR-047), **VOCÊ roda o comando** neste passo.
0.7. **Self-check de boot consolidado (emenda ADR-061 — anti-bypass; recomendado onde hooks estão inertes):** se o `route-gate` declarar gates INERTES (Kaspersky veta PS), rode **UMA vez** `python tools/boot_check.py --author-model <id-do-modelo-desta-sessao>` (você conhece o próprio modelo pelo system-prompt; ex. `claude-opus-4-8`). Funde, num comando à prova de EDR, o **sync** (passo 1) + **agnosticismo** (ADR-020) + **boot-scan cross-IA** (passo 0.6) + **âncora de versão canônica** (anti "versão fantasma") + **tier-autor da sessão** (ADR-082 — banner LOUD se você, o autor, roda ABAIXO do baseline com baseline disponível: Sonnet/Haiku só como crítico/docops, nunca como autor; **troque `/model <baseline>` ou declare indisponibilidade**); grava `.claude/boot-proof.json` e **carimba os liveness keys** → o banner se cala. Não substitui ler history/briefing/WIP abaixo — é a forma executável única dos passos que de outro modo seriam manuais-e-skippáveis.
1. **Sincronizar ANTES de ler (ADR-019 — obrigatório; falha-soft em erro de rede):** `git fetch` + checar ahead/behind vs `@{upstream}`/`origin/main`. Se atrás e seguro (sem modificações rastreadas + fast-forward) → `git pull --ff-only` (untracked não bloqueia); se atrás e inseguro (modificações rastreadas/divergiu) → **avisar e NÃO afirmar estado até resolver**. No IDE o hook faz isso no SessionStart (Python `check_repo_sync.py` → fallback PowerShell, ADR-060); no chat (sem hook) é passo manual. **Não assuma que o hook sincronizou (ADR-060): se um EDR/AAC vetou o hook — sinal: o `route-gate` injeta nudge de sync velho/ausente, ou o marker `.claude/.repo-sync-marker` está velho/ausente — VOCÊ roda `git fetch` + `git status -sb`.** *File-first sem fetch lê retrato congelado — caso real: sessão operou 41 commits atrás de main (method-audit 2026-05-30); reincidente por Kaspersky AAC em 2026-05/06.* **Depois** ler: AGENTS.md → .agent/rules/*.md → docs/briefing.md → **checkpoint do TOPO do history.md** (o arquivo é **mais-novo-primeiro**: 1 Read com `limit≈30` do INÍCIO; nunca o arquivo inteiro, e nunca "últimas linhas" — o fim é telemetria/aprendizado antigos, não o estado atual).
2. **Reconciliar WIP** (ex-G11 / ADR-007 — modo squad apenas): cruzar `## Em aberto` do history.md com branches do git e ADRs em status `Proposto`. Apontar inconsistências (item em aberto sem branch; branch sem item; ADR `Proposto` sem decisão).
2.5. **Retrospective gate (v1.12.1 — refinamento operacional do J0 adversarial ADR-011; method-audit 2026-05-29; ADR-012 v1.13.0 adicionou handoff cross-sessão como princípio 14 separado — retrospective gate continua sem ADR dedicado próprio):** revisar último bloco entregue desde último PASS do process-critic. Checklist binário adversarial (PMO assume há gap):
   - Process seguido (J0-J5 com gates declarados em `/handoff`)? `[PASSA/FALHA]`
   - RRC executado no `/checkpoint` final do bloco anterior? `[PASSA/FALHA]`
   - Debt deferido registrado explicitamente em `## Em aberto` ou ADR §Pendências? `[PASSA/FALHA]`
   - Polish post-release com surface estrutural > 5 linhas (Mermaid, seção nova, refactor skill/workflow) recebeu process-critic OU foi auto-classificado "não-bloco"? Se SIM segundo → **debt detectado**.

   **Se qualquer FALHA → primeira ação é tratar debt antes de novo escopo.** Sem retrospective gate, polish-skipped-process-critic acumula (padrão observado 2026-05-29). **Flexibilidade:** dono pode escalar "skip retrospective" se contexto é pergunta isolada/trivial — decisão consciente, não default.
3. Produzir STATUS — **fonte primária = geradores determinísticos (boot barato, v1.58.1):**
   `python tools/boot_check.py` (sync + agnosticismo + versão canônica, já no passo 0.7) +
   `python tools/handoff.py` (versão · branch/commit · `## Em aberto` · próximo passo do último
   checkpoint · arquivos recentes). Custam ~0 de output e não erram extração (caso real 2026-06-11:
   regex ad-hoc no `## Em aberto` reportou "vazio" com 6 itens presentes). Ler history diretamente
   SÓ por exceção declarada (retomada profunda · auditoria/process-critic · consulta a method-audit).
   Campos do STATUS: onde paramos · ADRs aceitos · nomenclaturas · próximo passo · riscos · **WIP**
   (itens em aberto reconciliados) · **debt retrospective** (gaps detectados no 2.5, se houver).
3.5. **Trabalhos em aberto — OFERECER, não só listar (ADR-100):** `python tools/trabalhos.py listar`
   (o `boot_check` já o executa e resume). Cada trabalho aberto traz **objetivo · o que foi feito ·
   o que está pendente · próximo passo e o que ele decide**. **Enquanto o status for `aberto`, o
   trabalho reaparece a cada sessão** — é o mecanismo que impede o handoff de se perder.
   **O agente DEVE mencioná-lo na resposta de abertura**, ainda que o dono traga outro assunto: um
   registro que existe e não é oferecido é igual a não existir. Detalhe:
   `python tools/trabalhos.py mostrar --slug <slug>`.
   **Só o dono encerra:** `python tools/trabalhos.py tratar --slug <slug> [--nota "..."]`.
   Ao FECHAR um bloco que deixa pendência, registrar/atualizar com
   `python tools/trabalhos.py registrar --slug <s> --nome ... --objetivo ... --pendente ... --proximo ...`
   — é o passo que transforma o Pacote P14 (efêmero) em pendência que sobrevive à sessão.
4. Responder: "Sessão aberta. [STATUS 2-3 linhas] [se houver trabalho aberto: citar nome + próximo
   passo] Retomar o próximo passo ou mudou direção?"

## Bloqueios
Sem briefing.md → primeira tarefa é criá-lo. Sem 00-glossario.md → bloquear
(sem source of truth o squad é inviável). Sem AGENTS.md → instalar via framework.

## WIP-limit (ADR-007 — modo squad)
**Finalizar antes de iniciar.** Item em `## Em aberto` só muda de status (planejado→ativo→pausado→bloqueado→fechado) com razão registrada. Reconciliação no passo 2 acima é o gate operacional. Se STATUS infla > 4 linhas, refatorar.
