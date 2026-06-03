# history.md — Registro append-only do framework

> Single-writer = orquestrador (PMO). Append-only. Cada entrada com timestamp ISO.
> Formalizado pelo ADR-007 (v1.9.0). Já era referenciado pelo `AGENT-FRAMEWORK.md` §2.B
> (sequência de ativação do squad lê últimas 30 linhas).
>
> 3 seções: histórico cronológico de checkpoints (formato em `.agent/workflows/checkpoint.md`),
> `## Em aberto` (WIP — ex-G11), `## Aprendizado` (fracassos — ex-G9, com firewall).

---

## 2026-06-03 — Sessão (architect/docops): Gates de honestidade da vitrine — pesquisa + ADR-059 (Proposto)

> **Pedido do dono:** análise crítica da vitrine pública × capacidades reais, "sem exageros, não depender de prosa"; depois trouxe deep-research dos 3 gaps + companions sênior; "documente, elabore um plano, commit e push (trabalhar de outro PC)".
>
> **Análise (rota pontual→squad-lite):** vitrine tem prosa de marketing **não-gateada** contradizendo o rigor do miolo (`LIMITS.md` gerado por canário). **Bug concreto [CONFIRMADO]:** `test_marketing_claims.py:24` aponta `PROMPT-CHAT-WEB-v4.3.md` (repo tem `v4.4`) → `continue` em arquivo ausente **silencia** o anti-overclaim no prompt web (fail-open). G2: `web_export` não tem gate anti-overclaim (só `anti_jarvis_gate`). G3: claim×LIMITS não cruzado.
>
> **Entregue (docs, NÃO código):** `docs/specs/honesty-gates/research-brief.md` (pesquisa do dono **com proveniência** — citações FTC/NeurIPS classificadas INFERIDO até verificar; tags de maturidade preservadas; §5 reconciliação régua §0 = nativo > dep externa), **ADR-059 Proposto** (3 gates nativos fail-closed, zero dep; LLM-as-judge = EMERGENTE/opt-in fora do core offline), `docs/specs/honesty-gates/plano.md` (4 fases + thresholds binários + cascata). **Memória:** registrada diretiva de cascata original→premium/web/noadmin/public.
>
> **Não implementado** (próximo bloco com developer→qa-critic). ADR-059 vira Aceito quando F1–F3 mergeadas verdes.

## 2026-06-02 — Sessão: Web split público × premium PRIVADO — v1.41.0 (ADR-058)

> **Pedido do dono:** "tier premium web = privado." Split espelhando o não-web (ADR-049):
> `-web` (PÚBLICO, só prompt-web-publico) × `-web-premium` (PRIVADO/pago, orquestrador + 15 skills).
> web_export gera publico/ e premium/ como repo-roots; publish-clean publica em dois destinos com deploy
> keys separadas. Repo privado criado + deploy key PUBLISH_DEPLOY_KEY_WEB_PREMIUM configurada. Deploy key
> do tier público (PUBLISH_DEPLOY_KEY_WEB) também configurada e **auto-push verificado end-to-end** (run
> 26847494133). O `-web` público será republicado sem premium/ no próximo run.

## 2026-06-02 — Sessão (developer): Pacote Web IMPLEMENTADO — v1.40.0 (ADR-054/056/057)

> **Pedido do dono:** "pacote web automatizado (gerar do main + tier premium com skills + repo -web), siga."
> **Entregue (não mais ADR — código):** `tools/web_export.py` (gerador determinístico, dois tiers, 15 skills
> geradas do front-matter + encadeamento + gate anti-JARVIS), `web-phrasing-map.txt`, `test_web_export.py`
> (9 checks PASS), wiring `export-clean.py --web`, estágio WEB na cascata `publish-clean.yml`. **Repo
> `metacognition-framework-web` CRIADO e publicado** (bootstrap manual @ v1.40.0). v4.4 vira tier público carimbado.
>
> **Repos filhos:** `-public`, `-public-nonadmin`, `-premium` atualizados (cascata roda no push); `-web` agora existe.
> **Pendência declarada:** auto-push do `-web` precisa do secret `PUBLISH_DEPLOY_KEY_WEB` (deploy key, setup 1×
> do dono) — sem ele a cascata roda export+gate e pula o push. Evals Gemini (NFR-1) + token público real (GAP-3) follow-up.
> **qa-critic:** test_web_export 9/9 PASS; output verificado limpo (zero vazamento, zero enforcement mentido) antes de publicar.

## 2026-06-02 — Sessão (architect): Pacote Web do framework — discovery→architect (ADR-054/055; alvo v1.40.0, NÃO implementado)

> **Pedido do dono:** sincronizar o chat web (defasado) — e mais: o chat web referencia skills nativas
> (Claude.ai), potencialmente mais autossuficientes que as nossas (que dependem de `_shared/`+companions).
> O dono entregou uma **spec sênior completa** (discovery output) para um `metacognition-framework-web` em
> dois tiers (público sem skills / premium com skills), com cascata main→web anti-defasagem.
>
> **discovery → architect:** spec versionada em `docs/specs/web-package/requirements.md` (verbatim + nota de
> reconciliação: base v1.22.0→**v1.39.0**, discovery v1.9.0→**v1.10.0**; GAP-2 rebaixado — `export-clean.py`
> já é motor de profiles). **ADR-054 (keystone, Aceito):** dois tiers + cascata como **profile `web` do
> export-clean** (não pipeline novo — régua §0) + repo dedicado `-web` + doutrina **`enforcement.chat`**
> (anti-JARVIS: gate→checkpoint declarado, nunca fingir mecanismo). **ADR-055 (Aceito):** desambigua
> "avançado" (eixo execução × eixo profundidade-discovery=`universal`/`reforço-sênior`) + regra anti-silêncio
> de stake no qa-critic (modo alto não pode pular reforço sênior em silêncio — vira achado atacável).
>
> **Decisões do dono (via AskUserQuestion):** GAP-1 = as "4 skills-base web" NÃO existem → **gerar do main**;
> ritmo = ADR-055 agora + commit, 056/057 depois.
>
> **Conjunto architect FECHADO (2026-06-02):** ADR-056 (consolidação papel+companions gerar-do-main +
> injeção determinística de `## Encadeamento` do front-matter) e ADR-057 (profile `web` no export-clean +
> `web-phrasing-map.txt` + gate anti-JARVIS verificável + carimbo de versão anti-defasagem + ordem da cascata)
> escritos e aceitos. **Handoff → developer.**
> **Em aberto (developer WIP):** redigir prompts/skills web (gerar do main via profile); criar repo `-web` +
> workflow; eval Gemini (NFR-1) e token público real (GAP-3) antes de declarar suporte.
> **NÃO houve release** — v1.40.0 sobe só na implementação (honestidade: ADR≠código entregue).

## 2026-06-02 — Sessão: v1.39.0 — execution-report de DOIS TIERS (telemetria de processo anonimizada · ADR-052; realiza ADR-048)

> **Pedido do dono:** relatório de execução tipo o do caso real, mas que **retroalimente o framework** —
> executado por ele (raiz) registra tudo sem filtro; registrado por usuário externo **anonimiza** e respeita
> LGPD, focando em **pontos de falha / decisões / gates** (processo, não conteúdo). Decisões do dono (via
> surface-and-reconcile + high-stakes-gate): destino = **PR ao master** (o PR é o consentimento); payload =
> **só sinais codificados** (fora da LGPD, Art. 12); consentimento = **opt-out documentado** + switch.
>
> **Entregue:** `execution_report.py` dois-tiers (detector por `docs/_private/`), **whitelist de schema**
> como garantia anti-vazamento (não confiança — lição do incidente 2026-05-31) + anti-PII + opt-out;
> 17 testes adversariais PASS; `TELEMETRY.md`/`telemetry/`; cláusula em LICENSE/SECURITY/README; docops
> §Encerramento corrige path `docs/_intake/`→`docs/_private/_intake/` (vazaria no export). ADR-052 Aceito;
> ADR-048 Proposto→Aceito.
>
> **qa-critic (adversarial):** 3 bugs reais pegos — comentário inline em header `##` quebrava o parser de
> seção; `os.makedirs('')` com `--out` relativo; e o token sensível "AIVI" que um teste **distribuível** ia
> carregar (o próprio vazamento que o framework previne). Todos corrigidos e reverificados.
>
> **Bleed de outra sessão (aduaneiro/Power Query):** confirmado file-first que não pertence a este repo. O dono
> pediu para **agnosticar os insights de método** daquela sessão. Verdict régua §0: 4/7 já cobertos (classificação,
> QA adversarial, débito declarado, prosa→mecanismo); 1 net-gain → **ADR-053**: alarga o teste binário do
> **Princípio 14** para incluir o **humano destinatário** (usa sem capacidade oculta — terminal/instalação/path).
> Hardcode de ambiente e tooling oculto reprovam o handoff. Edição cirúrgica em `AGENT-FRAMEWORK.md` §6.

## 2026-06-02 — Checkpoint de RECONCILIAÇÃO retroativa: v1.31.1 + v1.33.0→v1.38.0 (ADR-046/047/049/050/051) [reconstruído]

> **Catch do retrospective gate + consistency-gate (ADR-030)** no `/start-session` de 2026-06-02: o
> `history.md` parou em v1.31.0/ADR-045 (entrada T00:20 abaixo) enquanto a `main` já estava em **v1.38.0**
> (`54a13d8`, PR #45) — **~7 releases sem checkpoint**. Conteúdo abaixo **reconstruído do CHANGELOG (fonte
> canônica) + ADRs + metadados `gh pr`**; append-only (nada reescrito). QA real (process-critic/CI) ocorreu
> nas sessões originais de cada PR (todos mergeados com check verde) — **não re-executado aqui**; esta é
> reconciliação documental, não nova entrega. Tags v1.36.0/v1.37.0/v1.38.0 (antes ausentes) criadas e
> pushadas nesta reconciliação; ADR-051 flipado Proposto→Aceito (estava merged-as-Proposto, meta-recursão de Status já registrada no `## Aprendizado`).

Arco de 2026-06-01 (todos `main`, mergeados via PR, fechados):
- **v1.31.1 (PR #38)** — fix integridade da transparência no público + gates cross-drive. Motivado por **crítica adversarial externa que rodou a suíte no clone público** (grounding > eloquência): `LIMITS.md` público falhava o próprio `--check` (false-PASS na vitrine). ADR-044 `build_limits` `INTERNAL_ONLY`; `export-clean` gate **pós-strip**; guarda `relpath` cross-drive em `check_completeness`/`check_field_mapping`.
- **v1.33.0 (PR #39, ADR-046)** — blueprints de domínio + dicionário-contrato de entrada + ux-gate premium. 3 domínios irmãos (software/processo/projeto) carregados sob demanda (P12 preservado); `data-dictionary.md` + `check_input_contract.py` (auto-detecção/validação de entrada, anti join-a-zero); `ux-designer` §Definição de pronto PREMIUM. Terminologia **"genérico"→"flexível"** nos docs de usuário.
- **v1.33.1 (PR #40)** — harness de teste isolado (`guia/teste-isolado.ps1` + `TESTE-ISOLADO.md`): valida o framework num caso de domínio real com **isolamento estrutural** + checagem de **zero vazamento** (`-LeakCheck`).
- **v1.34.0 (PR #41, ADR-047)** — modo **NON-ADMIN** (sem hooks PS, p/ GPO Restricted) + pipeline **single-source → multi-distribuição**. `settings.nonadmin.json` + `bootstrap.py` (Python puro) + `guia/MODO-NON-ADMIN.md`; doutrina **"gates anunciados"** (agente declara/aplica inline o que o hook faria). ADR-048 registrado **Proposto/futuro** (execution-report).
- **v1.35.0 (PR #42, ADR-049)** — **3 distribuições de fonte única**: public (baseline+hooks) · non-admin (baseline+sem-hooks) · premium (full+hooks, privado/pago). Linha premium×core = **experiência × correção** (baseline NÃO perde discovery/análise). `export-clean` 3 modos; `publish-clean` publica as 3; repo premium privado criado.
- **v1.36.0 (PR #43, ADR-050 Aceito)** — elaboração de **documentos premium flexível por TIPO**: `gen_exec_doc.py` → md/docx/pptx/pdf, 7 templates premium (runbook-validação · apresentação-executiva · decisão · pop-sop · manual · config · manutenção). Anti-fabricação: campo vazio → **`NÃO PREENCHIDO`**. Modelos = **referência, não-determinísticos** (a spec/domínio objetiva a estrutura real). Premium-only (stripado do baseline).
- **v1.37.0 (PR #44, ADR-050 emenda)** — **entrega navegável**: `make_index.py` gera `index.html` + `LEIA-ME.txt` com **ordem de leitura guiada** (baseline, usabilidade); `gen_exec_doc --deliver` monta `output/<datestamp>/` por tipo; `check_delivery_floor.py` mecaniza o piso **"runbook de validação SEMPRE"** (prosa→gate). Fix **truncagem silenciosa** pptx/pdf (agora pagina).
- **v1.38.0 (PR #45, ADR-051)** — **reparo do discovery sênior**: contexto **INFERIDO** + pesquisa de entidade/âncora **MECANIZADA**. Causa-raiz provada (caso de campo regulado, alias AIVI — evidência no cofre, fora do repo): o filtro do `metodo-senior.md` **proibia inferência** e o `check_spec_depth` só media produto → o reforço sênior **nunca carregava**. `_shared/discovery/context-signals.txt` (sinais de STAKE, auto-retroalimentado sem HITL, agnóstico) + `check_context_brief.py` (barra J1 sob sinal de stake sem `context-brief.md` com tabela de verificação de âncora). **Supersede passo-1 do ADR-009**, emenda ADR-010 (inferir STAKE ≠ hardcodar NORMA) + ADR-033 (banco de dimensões). Comportamento **proporcional ao modo** (default valida c/ humano · avançado confirma âncoras · autosuficiente infere e reporta) com **anti-inversão-de-segurança** (efeito T3 segue no gate humano).

Method-audit (registrado também em `## Aprendizado`): o `consistency-gate` (ADR-030) **não disparou no fechamento** dessas 7 sessões — débito de checkpoint/tag/status sobreviveu até o boot manual o pegar. Sinal sobre o **wiring/execução do gate**, não só sobre o history.

RE-ORQUESTRAÇÃO (J6, ADR-045): prosseguir — reconciliação documental fechada; sem re-priorização. Próximo passo aguarda direção do dono.

---

## 2026-06-01T00:20 — Sessão: Remediação v2 (ADR-033..044, v1.23.0→v1.31.0) + ADR-045 (PMO maestro J6)

Implementados os 13 itens do plano de remediação v2 em 9 marcos (v1.23.0→v1.31.0), mergeados (PR #36,
merge `01a9a64`) com **CI verde nos 3 SOs** e público regenerado (`--sensitive` = zero vazamento, 224 arq).
Process-critic adversarial isolado (Sonnet, heterogêneo ADR-018) pegou **falso-PASS crítico** no
`check_spec_depth` (alias por substring); a matriz CI pegou 3 bugs cross-platform que passavam local
(`mission-gate` `$env:USERPROFILE`, `.sh` POSIX-only, stdout cp1252). 12 canários novos + CI cross-platform.
ADR-045 (esta emenda ao ADR-011): **J6 — PMO maestro na fronteira de bloco** (decisão de re-orquestração
registrada; NÃO round-trip por gate — circuit-breaker forward-only preservado).

process-critic: APROVADO_LIMPO (remediação v2 + ADR-045; 19 canários verde, agnosticismo verde, paridade na matriz CI).
RE-ORQUESTRAÇÃO: prosseguir — bloco entregue e mergeado; sem re-priorização pendente. ADR-045 fecha a pergunta do dono sobre o PMO-hub (a cada bloco, não a cada gate). Próximo passo aguarda direção do dono.

## 2026-05-31T03:00 — Sessão: v1.22.0 — entrada determinística (route-gate + wiring self-heal + doc-intake + consistency-gate)

Origem: incidente confirmado (relato AIVI) — agente executou tarefa **regulada/financeira sem rotear**. Causa-raiz dupla por inspeção: (1) roteamento era **prosa** (CLAUDE.md), não mecanismo; (2) auto-boot global **desligado** (settings global sem `hooks` — clobber do mode-apply autosuficiente). Diretiva do dono: "nada importante em prosa → tudo vira ferramenta; ISSO NÃO PODE FALHAR (divulgando)". Execução **autônoma noturna** em modo autosuficiente, autorizada até **merge + limpeza** (override do "parar no PR", só nesta sessão).

Modo: **autosuficiente**. Atrito observado: o IDE (extensão VS Code) **não aplica `bypassPermissions` do settings.json** — é estado de sessão escolhido na UI (modo "Edit automatically"); diferente da CLB que honra o arquivo. Diagnóstico só fechou após **file-first** (inspeção dos settings) — lição: ler doc de retomada ≠ verificar estado da máquina.

Entregue (branch `feat/v1.22.0-entrada-deterministica`, 1 commit/item, pushado a cada passo — resiliência):
- **ADR-027** route-gate (UserPromptSubmit universal, fail-open) + ensure-global-wiring (self-heal hook-preserving; Arquimedes no settings de PROJETO) + §disable-com-memória (session.lock data/motivo + reativação no boot). Escopo de auto-wiring: Windows/PS (.sh = setup manual Unix).
- **ADR-028** output-style ≠ processo: `metacognition-core` §Precedência nível 7 (persona subordinada ao nível 6, nunca suplanta regras/roteamento). Edição de existente (régua §0).
- **ADR-029** doc-intake: `_shared/doc-intake` + `tools/doc_intake.py` + canário (5 testes) — parse determinístico → chunk → manifesto sha256, offline/sem-embeddings; integrado ao discovery.
- **ADR-030** consistency-gate: auditoria fechamento fail-soft (6 dimensões: version-sync, adr-status, checkpoint, contagens, **unpushed**, transientes); wirado no docops. Validado por dogfood (pegou 3 ADRs Proposto, checkpoint ausente, 6 transientes).
- `guia/RESILIENCIA-ACESSO.md` (recovery de conta > chave local). Housekeeping: ADR-024/025/026 → Aceito; checkpoint retroativo v1.21.1+1.21.2. Hooks PS → UTF-8 BOM (cura mojibake observado no route-gate).

QA bicelular: process-critic adversarial **Sonnet isolado** (ADR-018) — **APROVADO_COM_RESSALVA** → 3 MÉDIO + 5 BAIXO **todos emendados** dentro da J4 (forward-only, EMENDA): chunk-id único entre subpastas (+teste), schema no ramo de erro, teste de reconstrução literal, precedência sem ambiguidade, claim de integração honesto (docops wirado + ADR qualificado [INFERIDO]), BOM nos 3 hooks. Linters: check_core_agnostic PASS (núcleo agnóstico preservado), validate_skills PASS, canário doc_intake 5/5.

Próximo passo: PR → merge verificado (`gh pr view --json mergedAt` ANTES de deletar branch — incidente #25) → tag v1.22.0 → remover RETOMADA (transiente). Débito sinalizado (não-bloco): 5 transientes antigos em `docs/_intake/` (sessões maio/v1.14.x) — deixados para revisão do dono (não criados nesta sessão).

---

## 2026-05-31T01:00 — Sessão: v1.21.1 + v1.21.2 — consolidação pós-v1.21.0 (site/docs/autoria/tokens) [checkpoint retroativo]

> Checkpoint adicionado retroativamente (catch do `consistency-gate` ADR-030, 2026-05-31: history pulava de v1.21.0 direto, sem registro de 1.21.1/1.21.2). Conteúdo reconstruído do CHANGELOG (fonte canônica). Append-only respeitado: entrada nova, nada reescrito.

Consolidação do trabalho feito **após** a tag v1.21.0, em PRs separados (#22–#28), cada um parando no gate humano.

Entregue:
- **v1.21.1**: `tools/project_report.py` (**ADR-026** — relatório de tokens + história compactada dos transcripts, sem transmissão, canário 6/6); **LICENSE (CC BY 4.0)** + **NOTICE** (antes ausentes apesar de citados); **`tools/check_attribution.py`** (**ADR-025** — guarda transparente de autoria, quebra o build se LICENSE/NOTICE/crédito sumir; refuta mecanismo oculto); **`/start-session` registrado** (`.claude/commands/start-session.md`, **ADR-024**); reforma do site (`guia/web/`) → site-hub; chat-web v4.3; linha de atribuição no README.
- **v1.21.2**: contador de **tempo/interação** no `project_report.py` (duração + throughput tokens/min; ADR-026 estendido); README com link do site + intro holística; nota OWASP-LLM em `SECURITY.md` (por que 🟡 é o teto honesto de orquestração); **commits/tags assinados (SSH) e Verified** no GitHub (concretiza ADR-025).

Estado pós-bloco: `main` em **v1.21.2**; ADR-024/025/026 implementados (status flipado para **Aceito** na sessão v1.22.0).

---

## 2026-05-30T21:30 — Sessão: v1.21.0 — runtime hooks (compaction/mission) + camada de entrega de produto

Origem: revisão de uma pesquisa/SPEC externa (Perplexity) que **re-derivou contra fontes oficiais** (Anthropic/OpenAI/Google) o núcleo **já mecanizado** na série v1.14.x→v1.20.0 — validação externa, não refatoração. Filtrado o ganho real (lean, régua §0): só o que ainda era prosa virou mecanismo + correção do **viés processo-sobre-produto** (reorientação do dono: o framework culmina em PRODUTO de software/dados — sessão Perplexity l.421/427).

Modo: **autosuficiente** reconfirmado (entrada MANUAL no audit trail; `~/.claude/settings.json` global já tinha `bypassPermissions`; caveat de reload-na-próxima-sessão documentado ao dono — ADR-005).

Entregue (branch `feat/v1.21.0-runtime-hooks-web`, 1 commit/item reversível):
- **ADR-021** `compaction-gate` (PreCompact: bloqueia compaction sem digest persistido; fail-open; backstop conservador) — mecaniza a obrigatoriedade de digest do ADR-016. PreCompact-pode-bloquear = [CONFIRMADO] (doc oficial, via claude-code-guide).
- **ADR-022** `mission-gate` (SessionStart: `product_type`/escopo confirmado por modo de execução; taxonomia na **aplicação**, não no núcleo; PreToolUse backstop deferido — fase 2). Funde com discovery passo 6(f).
- **ADR-023** app `exemplos/dominio-software/` (ux-designer + evals-engineer = os 2 papéis que melhoram o PRODUTO; governance-lead/skill-librarian **não** criados — cobertos por high-stakes-gate/action-safety e pelo campo `classe`). Núcleo `_shared/` **inalterado/agnóstico**.
- Web→v1.21.0 (camada ENFORCEMENT + `_shared` 9 regras + app); refinos de doc (caminho Windows managed-settings → `C:\Program Files\ClaudeCode\`, bug #44642 status, ressalva #37210); 3 canários novos.

QA bicelular: process-critic adversarial Sonnet isolado/heterogêneo (ADR-018) — **R1 REPROVADO** (1 ALTO template↔hook = STANDARD inalcançável + 2 MÉDIO [ADR↔settings; path hardcoded] + 2 BAIXO) → fixes → **R2 APROVADO_COM_RESSALVA** (1 BAIXO cosmético, corrigido). **Forward-only**: nenhum rewind cross-junção; tudo resolvido DENTRO de J4 (EMENDA).

### RRC (ADR-010) — coherence pass
- Artefatos lidos: 3 ADRs novos · ADR-016/015/005/010/012 (vinculadas) · README · CHANGELOG · CLAUDE.md · AGENTS.md · web/index.html · `_shared/` (action-safety, execution-modes) · discovery/SKILL.md · framework-schema.json · validate_skills.py · effect-gate · sync-global · settings.json · exemplos/README.
- Verificações: versões em sync (README 1.21.0 × CHANGELOG [1.21.0] × web v1.21.0 × CLAUDE/AGENTS): **PASSA** · Refs cruzadas (ADR-021/022/023 existem; paths citados existem): **PASSA** · Nomenclatura consistente (product_type, mission-gate, compaction-gate): **PASSA** · Sem contradição semântica (ADR↔código: PreToolUse deferido reconciliado; uma só ESCOLHIDA): **PASSA** · **Contagens em sync** ("9 regras" web = 9 dirs _shared; "3 modos" = BRIEFING/ADVANCE/STANDARD; "8 campos" schema): **PASSA** · Anti-vazamento cross-projeto (check_core_agnostic 37/37 PASS; taxonomia product_type só na app): **PASSA**.
- Inconsistências corrigidas: dupla "ESCOLHIDA" no ADR-022 (alt 3 → "recorte SessionStart-only"); mensagem do canário mission-gate ("3 modos"→4 casos); discovery version/last_review stale.
- Veredito RRC: **PASSA**.

Addendum pós-qa (doc-work, conscientemente **não-bloco** — registrado p/ não pular silencioso, retrospective gate): cobertura de docs que faltou (catch do dono — "o web é mais que o index.html"): **PROMPT-CHAT-WEB v4.2→v4.3** (paridade de comportamento: product_type/escopo no briefing + papéis de entrega; fix ref morta), refs ao filename atualizadas (históricas ADR-010/specs preservadas), **GUIA-EQUIPE §12** catch-up. Depois, **reforma do `guia/web/index.html` em site-hub** (feedback do dono): flexível>genérico, evidência auto-explicativa (A0–A3 em linguagem clara), ADR explicado/jargão reduzido, fluxo corrigido (sem seta órfã + legenda do ciclo), índice de docs agrupado, copy de proposta de valor. 11/11 links resolvem; LF casado; sem novo vazamento (agnóstico PASS). Modo autosuficiente reconfirmado (HOOK_CHANGED do próprio sync).

Próximo passo: ~~abrir PR~~ **FEITO**: mergeado em `main` via **PR #20** (4 commits iniciais, mergeado cedo) **+ PR #21** (4 commits de docs/site, restantes) → `main` em `18ab0c3`, **tag `v1.21.0`** anotada no origin. Gate pós-merge 5/5 verde. (Lição: o #20 foi mergeado antes dos commits de docs entrarem; resolvido com #21 — preferir não mergear enquanto o bloco ainda recebe commits.)

---

## 2026-05-30T14:30 — Sessão: reconciliação de dívida pós-merge série v1.14.x→v1.19.0 + process-critic adversarial

Abertura via `/start-session` com `git fetch` (disciplina do method-audit 2026-05-30, já mecanizada por ADR-019/`check-repo-sync`): `main` em **v1.19.0** (`c866f95`), sync 0/0, tree limpo. **Process-critic adversarial pós-merge** (qa-critic isolado em **Sonnet**, heterogêneo ao Opus gerador — ADR-018) sobre a série consolidada: veredito **SÓLIDO-COM-DÍVIDA** (dimensões A–E; A/B/E PASS-com-ressalva, C/D PASS). **J4 (PMO) pegou false-PASS do próprio crítico** (Achado #1: o crítico disse "schema=5 opcionais"; o schema real tem 8 = 5 contrato + 3 legado) — arquitetura bicelular (ADR-011×018) auto-validada.

Dívidas reconciliadas (branch `chore/reconciliacao-divida-v1.14-v1.19`, 1 commit por item = reversível isolado):
- **#1 [ALTO]** ADR-013 stale count (Alt 3 "4"→"5") + gap ADR↔schema explicitado (5 contrato + 3 legado=8) — `00aa49f`.
- **#4+#6 [MÉD+BAIXO]** digest de pesquisa `git mv` para `docs/_intake/` (traço imutável) + ponteiro SSoT p/ faixas refinadas do ADR-016 (50–69/70–84/≥85) + refs corrigidas — `4cdcf67`.
- **#3 [ALTO]** 6 tags anotadas retroativas v1.14.0–v1.19.0 (ausentes local+origin; violavam política do CHANGELOG).
- **#2+#5 [MÉD+BAIXO]** este checkpoint (fechamento v1.18/v1.19 antes ausente) + ponteiro inverso ADR-019.

**Escopo novo declarado pelo dono nesta sessão (prosa→mecanismo):** regra anti-vazamento de domínio (Princípio 12) é prosa e **falhou ≥2× pega pelo dono** → **ADR-020 candidato**: linter executável de agnosticismo do núcleo + canário + wiring CI/boot. Régua §0(c): destrava o que a prosa não consegue garantir.

Próximo passo: fechar bloco ADR-020 (mecanismo) + PR único + merge. Reversibilidade por item preservada.

---

## 2026-05-28T09:01 — Sessão: v1.10.0 mergeada — método sênior de discovery (domain-agnóstico) + auto-observação (ADR-009)

Absorção pelo framework do método sênior validado no case real **AIVI** (LIMITES-BATENTES-RECALC, branch `claude/discovery-aivi-metodo-2026-05-27`). Substância: memórias `[[senior-discovery-method]]` + `[[framework-self-improvement]]` + `[[framework-gaps-from-aivi-case-2026-05-27]]`.

Aprovado e funcionando:
- **ADR-009 Aceito** após **4 rounds qa-critic adversariais (16 findings endereçados)**: round 1 (2 ALTO A1 colisão namespace ADR-008→009 + A2 template ganha §7 Antecipações + §8 Backlog + M1-M5+B1), round 2 (4 MEDIO + 1 BAIXO + 2 ADV), round 3 (3 MEDIO + 1 BAIXO + 2 ADV stale counts), round 4 LIMPO (único bloqueador foi meta-recursão do próprio campo Status).
- **v1.10.0 mergeada** em main via `--no-ff` (commit `d73244e`), **tag `v1.10.0`** anotada criada, branch `feat/v1.10.0-senior-discovery-method-auto-improvement` deletada (local + remote).
- 5 commits no branch: `11c1289` feat + `01e598a`/`f622f89`/`3d96d94` fixes rounds 1-3 + `3d8c873` promoção a Aceito.
- **Régua §0 mantida**: 2 novos + 9 edições cirúrgicas (escopo cresceu de 2+4+1 para 2+9 pela incorporação adversarial; todas edições de 1-3 linhas; sem nova pasta/workflow/template/skill).

Nomenclaturas estabelecidas:
- **Reforço transversal sênior** = método de discovery domain-agnóstico (não sub-modo; carregado sob demanda quando há fonte canônica/normativa citada).
- **Companion `metodo-senior.md`** = 8 passos auditáveis (mapeamento + **vigência** + complementações + cross-domain + pertinência + elicitação + classificação + adversarial).
- **Method-audit autônomo** = 0-3 notes/sessão substantiva em `## Aprendizado` (plug em ex-G9 de ADR-007).
- **Princípio 11** (`AGENT-FRAMEWORK.md` §6) = auto-observação do framework.
- **ADR-008 candidato** continua reservado para D2/check-execution-mode global (ADR-006 §Pendências).

Decisões permanentes:
- ADR-009: método sênior + auto-observação (Aceito, mergeado `d73244e`).

Próximo passo: **AIVI fechamento** no repo `LIMITES-BATENTES-RECALC` branch `claude/discovery-aivi-metodo-2026-05-27` — implementar REQ-001..007 contra a SPEC + qa-critic round 1+2 + run com `dados_mestre/2026_VAR_INT_CSV.csv` + validar CA-1..CA-6 + gate humano. Trabalho fora deste repo.

Riscos ativos:
- 6 follow-ups em ADR-009 §Pendências (não-bloqueantes): high-stakes-gate auto-load por gatilhos, requirements.md universal+sênior, external research handle (WebSearch), drift detector framework-boot.ps1, ADV1-4 estruturais (revisitar se padrão recorrer), AIVI fechamento.
- Meta-recursão de Status do ADR pode reaparecer em próximo ADR — registrado como method-audit.

---

## 2026-05-27T21:59 — Sessão: pagamento da dívida de eval do G1 (pesquisa-cascata) + 1ª cascata real

Abertura via /start-session reconciliou o repo vivo contra o "PLANO DE OTIMIZAÇÃO" colado pelo mantenedor: o plano é o **intake já entregue** na v1.9.0 (arquivado em `docs/_intake/`, virou ADR-007 Aceito). Nada a re-fazer — confirmado warning #6 (snapshot vs repo vivo). Decisão do mantenedor no gate: **pagar a dívida de eval do G1** (única pendência acionável do próprio plano, §5.2 / ADR-007 §Pendências).

Executado:
- **Eval seção I (funcional, ADR-007:103-112) RODADO: 9/9 PASS** — registrado em `_meta/eval-results-papeis.md` §I [EXECUTADO]. Método: 1 pesquisa-cascata real de ponta a ponta, casos verificados contra a execução. Caso 9 marcado `✅*` (nuance honesta: guard de não-repetição exercido por ausência-de-fonte, não por empty-return técnico).
- **1ª pesquisa-cascata real disparada** (field-validation que o ADR-007 §Validação pedia). Tema: porte cross-platform dos hooks (backlog D4). 2 rodadas, 4 explorers isolados (~104K tokens — confirma empiricamente o custo multi-agente do intake §2). Output: `docs/specs/cross-platform-hooks/research-brief.md`.
- **Achados que destravam decisão futura:** (a) o lock-in PowerShell já é dívida registrada (ADR-004/005/006 + D4, trigger-gated); (b) `bootstrap.sh` já existe mas stuba a instalação de hooks de propósito; (c) **GAP-1** — a bifurcação `pwsh` (PowerShell Core) vs reescrita `.sh` nunca foi avaliada pelos ADRs e decide o custo do porte (recomendação: spike de 1h antes de qualquer ADR); (d) **GAP-2** — caminho absoluto `$env:USERPROFILE` inscrito no `~/.claude/settings.json` global é bug latente multi-PC, não-documentado.

Régua §0 aplicada à própria execução: NÃO abri ADR nem implementei (D4 é trigger-gated; abrir agora seria adição pré-gatilho). NÃO spawn de qa-critic separado — o ataque anti-raso (passo 7 do pipeline) é o gate adversarial do brief, e o eval é a verificação; um qa-critic extra não mudaria o resultado (custo sem ganho).

Sem gatilho de fracasso disparado → nada em `## Aprendizado`. Próximo passo: gate humano (ver `## Em aberto`).

---

## 2026-05-27T20:50 — Sessão: reconciliação de sync + 2 bugs de encoding/boot nos hooks

Abertura via /start-session detectou `main` ahead 1 de origin (commit `5b0b2a2`, fix UTF-8 runtime dos hooks de inject, não pushado). Pushado após avaliação §0 (devido: não pushar regrediria mojibake em outro PC — [[fabricio-multi-pc-workflow]]).

Dois bugs corrigidos + housekeeping:
- **`9321e28` — header v1.6.1 ASCII-safe.** O fix runtime anterior não pegava o literal `—` no heredoc da linha 58 de `inject-start-session.ps1`: PS 5.1 parseia `.ps1` sem BOM como CP-1252 ANTES de `[Console]::OutputEncoding` rodar. Trocado por `-` ASCII (unifica com o header global v1.8.0 que já era ASCII). Convenção registrada em memória.
- **Duplicação de /start-session (gap impl v1.8.0/ADR-006).** Confirmado: o `.claude/settings.json` do repo registra o hook de PROJETO v1.6.1 e o `~/.claude/settings.json` (via bootstrap) registra o GLOBAL — os dois disparam ao abrir o framework-repo. Fix: guard no hook de projeto que cede (`exit 0`) quando `~/.claude/hooks/inject-start-session-global.ps1` existe. Preserva boot de primeira-execução (global ainda ausente), elimina injeção dupla pós-bootstrap. Honra de lock preservada (global checa os locks).
- **Housekeeping:** 5 branches remotas de PRs mergeados deletadas (`chore/backlog-and-summary`, `feat/auto-sync-hook`, `feat/discovery-cascata-v190`, `feat/framework-optimization-v180`, `fix/adr-005-framework-sync-gap`). `_backup/*` preservado.

**v1.9.0 FECHADA:** impl 4/4 + DocOps + ADR-007 mergeados (commits `4ec6f60`, `6bb20ef`, `8c7f8ab`, merge `197b354`). Item removido de `## Em aberto`.

---

## 2026-05-27T03:30 — Sessão noturna: gap intake↔realidade na v1.9.0 reconhecido

Aprendizado documental (não-bloqueante): o intake §4 estimou "~6 edições de 1-3 linhas + 2 linhas de princípio" para a v1.9.0. A realidade do PR foi 428 inserções. O conteúdo é justificável linha a linha pela régua §0 (ADR-007: 160 linhas decisórias; companion + template: ~160 linhas substantivas; edições cirúrgicas: ~100 linhas). Não há regressão funcional — apenas a estimativa do intake estava errada por ~70× porque não considerava ADR+companion+template como artefatos novos legítimos. Lição: estimativas em intake devem distinguir "edições" de "artefatos novos". Não vira ADR (caso isolado, não padrão recorrente — §Aprendizado).

---

## 2026-05-27T01:00 — Sessão noturna: ADR-006 + ADR-007 + Régua §0

Aprovado e funcionando:
- v1.7.1 mergeada em main (PR #7, commit 99cf801) — fix do gap ADR-005 (framework-sync.ps1 espelhado).
- v1.8.0 mergeada em main (PR #8, commit afb98aa) — auto-boot global do squad com allowlist (ADR-006).
- Modo `autosuficiente` ativado em campo (PC do mantenedor); ratchet ADR-005 validado.

Nomenclaturas estabelecidas:
- `framework-sync.ps1` (instância global) ≠ `sync-global.ps1` (fonte versionada) — par fonte/binário.
- `squad-owners.txt` — allowlist de owners para auto-boot global.
- Régua §0 = GANHO LÍQUIDO (princípio 10 do AGENT-FRAMEWORK §6).

Decisões permanentes:
- ADR-005: modos de execução (Aceito, mergeado).
- ADR-006: auto-boot global (Aceito, mergeado em PR #8).
- ADR-007: Régua §0 + G1 pesquisa-cascata + ex-G9 + ex-G11 (Aceito, em implementação v1.9.0).

Próximo passo: completar implementação v1.9.0 + qa-critic código + PR + merge; depois FASE C (backlog) + FASE D (sumário).

Riscos ativos: race condition humano vs orquestrador no history.md (mitigada por convenção append-only com timestamp — ADR-007 Risco 5).

---

## 2026-05-29T19:00 — Sessão: v1.11.0 + v1.12.0 mergeadas — agnosticismo estrito + RRC + arquitetura bicelular de QA (ADR-010 + ADR-011)

Sessão de fôlego longo (~80 turnos) que entregou DOIS releases consecutivos:
- **v1.11.0 (ADR-010)** — framework agnóstico estrito + discovery declara escopo + RRC obrigatório + princípio 11 honestamente reescrito ("auto-observação" → "observação meta-cognitiva — captura estruturada de feedback"). 4 rounds qa-critic (6 ALTO + 8 MEDIO + 5 BAIXO + 5 ADV endereçados). Merge `bd64b08` + tag `v1.11.0` push origin.
- **v1.12.0 (ADR-011)** — arquitetura bicelular de QA: 6 junções binárias forward-only (J0-J5) + process-critic adversarial final com poder de rewind cascata + TODO QA adversarial + SUPLANTA × EMENDA. 4 rounds qa-critic (5 MEDIO + 3 BAIXO + 2 ADV endereçados). Merge `fb637ac` + tag `v1.12.0` push origin.

Aprovado e funcionando:
- ADR-009 promovido na sessão anterior (v1.10.0), validado em uso real nesta sessão.
- ADR-010 + princípio 12 (framework agnóstico) Aceito. V1-A purga = 0 ocorrências em arquivos ativos do núcleo.
- ADR-011 + princípio 13 (arquitetura bicelular) Aceito. 6 junções declaradas em `/handoff` com gates binários explícitos.
- 9 passos método sênior (8 originais ADR-009 + passo 9 Coherence Pass / RRC ADR-010) — sync em CLAUDE/AGENTS/SKILL/companion.
- 3 seções obrigatórias no output do reforço sênior (Antecipações + Backlog + Gaps não-bloqueantes) — sub-§7.1 propagada ao template research-brief.md.
- HITL desacoplado de regulated: HITL via ADR-005 execution-modes; regulated declarado pelo discovery (ADR-010).
- Anti-vazamento cross-projeto registrado como princípio 12 + memória `senior-discovery-method.md` purgada de ALCOA+/ANP/FDA/BACEN.

Nomenclaturas estabelecidas:
- **Observação meta-cognitiva** (captura estruturada de feedback) = nome honesto do princípio 11 (substitui "auto-observação").
- **Escopo declarado pelo discovery** = seção obrigatória no `requirements.md`/`research-brief.md` quando há sinal de contexto especializado (passo 6 do `discovery/SKILL.md`).
- **RRC** (Read-and-Review-for-Coherence) = passo 9 do método sênior + gate de saída no `/checkpoint` com 6 itens binários (5 dimensões coerência + anti-vazamento).
- **Modo Transcribe vs Modo Interview** = passo 6 do discovery; transcribe é determinístico quando briefing tem declaração nominal+ubíqua+stakeholder+sem-contradição; interview é default.
- **Junção binária forward-only** = transição entre papéis com gate explícito; iterações DENTRO até PASS; forward-only ENTRE junções (anti-loop).
- **Process-critic** = qa-critic adversarial final em subagente isolado com poder de rewind cascata a qualquer J_i.
- **SUPLANTA × EMENDA** = política binária: §Decisão/§Alternativas muda → SUPLANTA novo ADR + `Substituído por:`; §Implementação/§Consequências → EMENDA in-place via STATUS-field. Within-junction rounds = EMENDA.
- **BLOCO APROVADO** = unidade de entrega que o autor declara "pronto" (release, ADR aceito, spec fechada, feature delivered) — gatilho mandatório do process-critic.

Decisões permanentes:
- ADR-010: framework agnóstico + discovery declara escopo + RRC + correção honesta princípio 11 (Aceito, mergeado `bd64b08`).
- ADR-011: arquitetura bicelular de QA + 6 junções binárias forward-only + process-critic rewind cascata (Aceito, mergeado `fb637ac`).

Próximo passo: aguardar trigger real (próximo projeto/case) para dogfood completo de J0-J5 via `/handoff` em fluxo real; ADR-010 follow-up (templates ganham `## Escopo declarado pelo discovery`) ativável quando próximo discovery rodar; ADR-011 follow-up (Alt 2 rewind cirúrgico) ativável se aparecer caso onde cascata é custosa.

Riscos ativos: nenhum bloqueante. Risco residual ADR-010 §Riscos (detector de vazamento cross-projeto ausente — mitigado por feedback do dono via method-audit, não eliminado).

---

## Em aberto

> WIP atual (ex-G11). Reconciliar com branches do git e ADRs em status `Proposto` no `/start-session` (modo squad).

- **[2026-05-31 · FECHADA] v1.21.1 — consolidação pós-v1.21.0 (PRs #22–#28, cada um no gate humano)** — site (links GitHub renderizados, **GitHub Pages** no ar, Release; seções Segurança/Riscos/Construção; gates binários; cards de valor tokens/telemetria/método; share; **reestruturação IA** enxugada), chat-web **v4.3**, ergonomia (**`/start-session` comando** — ADR-024; "iniciar" alternativa; não-rígido), **autoria transparente** (LICENSE/NOTICE/`check_attribution` — **ADR-025**, refuta mecanismo oculto/spyware), **relatório de tokens** (`project_report` — **ADR-026**). `main`=`4afeba2`, **tag `v1.21.1` + Release**. Gate consolidado verde (7 checks). qa-critic pegou overclaims reais (segurança/honestidade) → corrigidos; `check_attribution`/`project_report` pegaram bugs ao rodar (dogfooding). **Política nova:** parar no PR; merge = gate humano — [[feedback_pr_human_gate_merge]]. **Recusado (teste do dono):** vigilância oculta/phone-home — ADR-025 §refutado.
- **[2026-05-30 · FECHADA] v1.21.0 — runtime hooks + entrega de produto + chat-web/site (ADR-021/022/023)** — mergeado em `main` via **PR #20** (`6e22936`→`74a1f3d`: hooks compaction/mission + app dominio-software + web + version sync) **+ PR #21** (`c31f0cb`→`11e0083`: chat-web PROMPT v4.3 + GUIA-EQUIPE §12 + site-hub + PITCH.md + index sem jargão ADR). `main`=`18ab0c3`, **tag `v1.21.0`** no origin. qa-critic Sonnet isolado R1 REPROVADO→R2 APROVADO; gate pós-merge 5/5 verde. **Nota:** #20 mergeado cedo (antes dos commits de docs) → #21 completou; lição registrada no checkpoint.
- **[2026-05-30 · FECHADA] Reconciliação pós-merge série v1.14.x→v1.19.0 + ADR-020** — PR #18 mergeado em `main` (`2a8947f`, `--merge` preserva commits atômicos). Dívidas #1/#2/#3/#4/#5/#6 fechadas + **v1.20.0** (ADR-020 linter de agnosticismo, prosa→mecanismo do Princípio 12) após qa-critic round 2 (1 MÉD + 3 BAIXO). **Tags v1.14.0→v1.20.0 todas no origin** (dívida de tags da série inteira fechada). 5/5 gates verdes no main mergeado. 1 commit por item (reversível isolado).
- **[2026-05-30 · fechadas] v1.14.0→v1.19.0** — série "da prosa ao mecanismo" mergeada em `main` (ADR-013..019); gate humano das PRs empilhadas #11→#17 passado; `main`=`c866f95`. Tags retroativas sendo criadas na reconciliação (antes ausentes — Debt #3). CHANGELOG até `[1.19.0]`.
- *(v1.13.0 FECHADA em 2026-05-29 — ADR-012 Aceito após qa-critic round 1; handoff cross-sessão + drift sync + qa-critic rules #6/#7).*
- *(v1.11.0/v1.12.0/v1.12.1 fechadas em 2026-05-29 — merges `bd64b08`/`fb637ac`/`8fb044f` + tags `v1.11.0`/`v1.12.0`/`v1.12.1`).*
- **[2026-05-27/28 · fechado] AIVI fechamento** — PR #20 mergeado em master de `LIMITES-BATENTES-RECALC` (commit `10ecf0b`, 2026-05-28). REQ-001..011 implementadas + gate BABET 2025 = 0 (delta 0.000000) + 3 pendências runtime fechadas. Validação framework SSOT F0-F4 concluída.
- **[2026-06-03 · ATIVA] Gates de honestidade da vitrine (ADR-059 Proposto)** — docs entregues (research-brief + ADR-059 + plano faseado). **Próximo passo:** implementar F1 (corrigir fail-open G1 em `test_marketing_claims.py` — glob+versão-numérica+`pytest.fail`, prioridade: bug ativo) → F2 (`anti_overclaim_gate` no `web_export`) → F3 (`{#CLAIM-NNN}`×LIMITS). Bloco developer→qa-critic. F4 (eval LLM-as-judge p/ companions sênior) = EMERGENTE, ADR próprio com dep declarada. ADR-059→Aceito quando F1–F3 verdes no CI.
- **Backlog ativo (trigger-gated, NÃO WIP):**
  - ~~ADR-010 §Pendências: templates `_template-research/research-brief.md` + `_template/requirements.md` ganham seção `## Escopo declarado pelo discovery`~~ **FECHADO em 2026-05-29 pós-merge v1.12.0** — ambos templates ganharam a seção em commit polish + diagrama Mermaid em ADR-011 §Topologia.
  - ADR-011 §Pendências: Alternativa 2 (rewind cirúrgico) — trigger: caso real onde cascata é custosa.
  - ADR-011 §Pendências: validation.md projeto × release convergir templates — trigger: ficar pesado manter separado.
  - Item D4 (cross-platform hooks Linux/macOS port) — trigger: user em PC não-Windows pedir.

---

## Aprendizado

> Notas de fracassos capturadas via `/checkpoint` (ex-G9). **Firewall:** notas são **inertes** — só viram comportamento via skill/regra destilada, aprovada via ADR e mergeada. Nota errada não propaga.

- **[2026-06-02] Method-audit (princípio 11 / consistency-gate não-disparado no fechamento):** o `/start-session` pegou o `history.md` **~7 releases atrás** da `main` (parou em v1.31.0; main em v1.38.0) + **3 tags ausentes** (v1.36/37/38) + **ADR-051 merged-as-Proposto**. · **Causa-raiz:** o `consistency-gate` (ADR-030, fail-soft no docops §Encerramento) **não rodou no fechamento** dessas 7 sessões — o débito de checkpoint/tag/status só foi pego pelo retrospective gate humano no boot seguinte. Mecanismo existe mas não disparou (≠ "não existe"). · **Proposta (não-preemptiva, aguarda 2ª ocorrência confirmatória):** investigar se o `consistency-gate` está **wired e executando** no encerramento real (vs só documentado no SKILL) — se o padrão "gate fail-soft existe mas não roda" recorrer, vira candidato a fail-closed ou a check no `/checkpoint`. Liga a [[framework-self-improvement]]. **Sem ADR agora** — 1 ocorrência confirmada (régua §0; princípio 11 honesto: mecanismo silencioso ≠ ausente). Débito reconciliado nesta sessão (tags + status + checkpoints).
- **[2026-05-31] Method-audit (operacional / encadear delete com merge não-verificado):** mergeei o PR #25 via `gh pr merge` num comando que **também deletava a branch** (local+remota) logo em seguida; o `gh` deu **network error** (merge não concluiu) mas o delete rodou → PR **auto-fechou sem merge** e a branch sumiu. · **Causa-raiz:** encadeei limpeza destrutiva (branch delete) com a ação principal (merge) no mesmo comando, sem verificar sucesso entre elas. · **Solução (executada):** commit `134d1ad` recuperado (existia local + em `refs/pull/25/head`), recovery-merge direto na main. **Disciplina:** nunca encadear `branch -d`/`push --delete` com o merge; verificar `gh pr view --json mergedAt` ANTES de limpar. Liga a [[feedback_pr_human_gate_merge]].
- **[2026-05-31] Method-audit (qa-critic / overclaim de segurança pego antes de publicar):** ao escrever o `SECURITY.md`/site, afirmei que o `effect-gate` rodava "por default, mesmo com o agente injetado" — mas ele **não estava wired** no `.claude/settings.json` (só no template de managed-settings, instalação manual). **qa-critic adversarial (Sonnet isolado) pegou o overclaim ALTO antes do merge.** · **Causa-raiz:** descrevi a *capacidade pretendida* (ADR-015) como se fosse o *estado instalado*. · **Solução (executada):** wirar o effect-gate como PreToolUse no `settings.json` (ativo por default) + ressalvas de pré-requisito no SECURITY.md (managed-settings = camada não-bypassável). Reforça [[feedback_framework_integral]]: claim de segurança é alto-risco; gate adversarial antes de publicar, não depois.

- **[2026-05-30T21:30] Method-audit (princípio 11 / viés processo-sobre-produto):** meu veredito inicial sobre os 4 papéis SW da SPEC Perplexity foi "vazamento de domínio → fora do núcleo → refutar". **O dono corrigiu** ("reanalise sob a ótica de que fornecemos ao final um produto de dados/software"). · **Causa-raiz:** ao avaliar adição ao núcleo, otimizei a *pureza do agnosticismo* e subponderei o *propósito declarado* (entregar produto) — exatamente o "viés de processo sobre produto" que a própria pesquisa Perplexity nomeou. Agente não auto-detectou; foi feedback do dono (fonte legítima, P11 honesto). · **Proposta (executada):** ADR-023 reconcilia via app bundlada (distribuição especializada, `exemplos/dominio-software/`) — núcleo intacto/agnóstico, produto ganha 2 papéis (ux+evals). Firewall preservado.
- **[2026-05-30T21:30] Method-audit (ADR-018 / teste do gerador herda o ponto-cego do gerador):** o canário `test_mission_gate.py` passava 3/3 **escondendo um bug ALTO** — eu (gerador) escrevi o teste no mesmo formato inline que o hook espera, enquanto o *template* que o usuário segue usava heading markdown; STANDARD era inalcançável pelo caminho documentado. **Pego pelo qa-critic Sonnet heterogêneo** (ADR-018), que leu template×hook×teste como contratos independentes. · **Causa-raiz:** teste autoral do gerador compartilha o viés do gerador — não substitui crítico independente. **Confirma empiricamente o valor do modelo heterogêneo** (ADR-018): R1 reprovou um ALTO que 3 testes verdes não viam. · **Proposta:** sem regra nova (régua §0 — já coberto por "qa-critic heterogêneo obrigatório"). Vigilância: "tests verdes do gerador" ≠ verificação; o crítico independente é necessário, não opcional.

- **[2026-05-28T09:01] Method-audit (ADR-009 / princípio 11):** Stale counts ("4 edições" vs "9 edições") residuais em múltiplos arquivos atravessaram 3 dos 4 rounds qa-critic da v1.10.0. · **Causa-raiz:** scope cresceu por incorporação adversarial sem step de varredura de coerência interna antes de re-submeter — skill ausente: validation pre-commit de contagens/números/listas que possam ter ficado stale após scope-creep. · **Proposta (lean):** +1 linha em `_shared/docops` ou release checklist (`guia/GIT-VERSIONAMENTO.md`): "antes de re-submeter ADR/spec ao qa-critic após scope-creep, varrer documento por contagens stale (totais, listas, tabelas de implementação)".
- **[2026-05-28T09:01] Method-audit (ADR-009 / princípio 11):** Meta-recursão do campo `Status` do ADR — sempre 1 round atrás do qa-critic em curso (cada round novo encontra Status descrevendo o round anterior). · **Causa-raiz:** Status descreve auto-referencialmente um processo que ainda está rodando — impossível fechar sem fork. · **Proposta (lean):** se padrão se repetir em próximo ADR, atualizar template `docs/adr/000-template.md` para que Status use metadado externo (último commit-hash de round qa-critic) em vez de descrever rounds pendentes. **Não-preemptivo** — decisão sob demanda.
- **[2026-05-28T09:01] Method-audit (ADR-009 / princípio 11):** ADV-1 round 1 (localização do companion `metodo-senior.md` em `.agent/skills/discovery/` vs `_shared/`) foi marcado como follow-up sem decisão consciente. · **Causa-raiz:** framework não tem critério explícito para distinguir "transversal entre papéis" (vive em `_shared/`) de "companion-de-skill" (vive ao lado da skill dona). · **Proposta (lean):** se próximo ADR (architect/developer/qa-critic) precisar referenciar `metodo-senior.md`, decidir then — não criar regra preemptiva.
- **[2026-05-29T19:00] Method-audit (ADR-009 / princípio 11 reescrito ADR-010 §C-1):** v1.11.0 absorção falhou no RRC self-applied — agente racionalizou `README.md:4` ("ALCOA+/ANP/FDA/BACEN/GAMP" como exemplo didático) como OK enquanto o gate dizia ZERO refs. **Foi o dono que detectou e corrigiu.** · **Causa-raiz:** agente que se auto-audita defende suas próprias escolhas (viés). Princípio 11 original ("auto-observação") supervalorizava capacidade que não existe. · **Proposta (executada):** princípio 11 reescrito como "observação meta-cognitiva (captura estruturada de feedback)" — agente registra notes proativamente quando consegue E via feedback do dono (fonte legítima). Limite documentado em ADR-010 §C-1.
- **[2026-05-29T19:00] Method-audit (ADR-009 / princípio 11):** v1.11.0 + v1.12.0 cada uma teve 3-4 rounds qa-critic com **mesmo padrão de stale counts** ("8 passos" → "9 passos"; "5 itens" → "6 itens"; "6 edits" → "11 edits"). RRC self-applied pelo agente passou pelos contadores stale em múltiplos arquivos. **3 rounds com mesmo tipo de finding confirma empíricamente o limite previsto em ADR-010 §ii** — RRC tem como objetivo reduzir achados de coerência mas não promete eliminação total; gate humano externo (qa-critic adversarial em subagente isolado) é complemento NECESSÁRIO, não opcional. · **Causa-raiz:** scope-creep durante absorção de findings adversariais não dispara releitura completa cross-document. · **Proposta (executada em ADR-010 §ii.2):** RRC ganhou "contagens em sync" como 5ª dimensão de coerência obrigatória (`/checkpoint` RRC gate em 6 itens; `/checkpoint` workflow e validation.md V7 já refletem).
- **[2026-05-29T19:00] Method-audit (ADR-009 / princípio 11):** v1.12.0 foi dogfood real do v1.11.0 — discovery inline aplicou passo 6 ADR-010 (Escopo declarado: regulado=NÃO, alto-risco=NÃO crítico, semântica=SIM anti-fraude, gaps=flagados) + método sênior 9 passos incluindo RRC + 3 seções obrigatórias. **Pipeline integral funcionou em projeto real, não sintético.** · **Validação positiva:** princípios 10-13 não regrediram à média entre releases consecutivas; ciclo de auto-melhoria do framework é sustentável quando case real está disponível. · **Sinal de saúde:** taxa de princípios novos por release deve cair com o tempo; v1.10.0 = +1, v1.11.0 = +1, v1.12.0 = +1. **Alvo v1.13.0 = ≤1 princípio novo**; se nada surgir natural, saúde confirma maturidade.
- **[2026-05-29T22:30] Method-audit (princípios 10+11+13 / 4 padrões observados na sessão de hoje):** (a) **3 inflações detectadas PELO DONO** antes do commit final (README "ALCOA+/ANP/FDA" como exemplo didático em v1.11.0; "cascata cirúrgica" oxímoro em v1.12.0; §05 nova em web/index.html pós-v1.12.0). (b) **3 polish commits post-v1.12.0** (22cd976/f2fb4a7/16a4ae4) auto-declarados "não-bloco" sem critério binário — f2fb4a7 introduziu Mermaid (surface estrutural) e qualificava como bloco. (c) **Velocidade insustentável** — 3 princípios em 1 dia (11 reescrito + 12 + 13); alvo v1.13.0 = 0 princípios novos sem trigger real (registrado no checkpoint 19:00 mas vale reiterar). (d) **Comandos terse ("siga")** disparam reflexo de "fazer algo proativo" mesmo sem escopo declarado novo. · **Causa-raiz comum:** princípio 11 honesto operacional — agente não detecta próprio overreach sem gate humano. · **Proposta:** **sem nova regra/ADR.** Vigilância apenas: "siga"/"ok" autorizam continuar escopo declarado, NÃO novo escopo. Critério "polish vs bloco" registrado como trigger futuro se padrão repetir (não preemptivo).
- **[2026-05-29T23:55] Method-audit (princípio 11 honesto / dogfood AIVI 6 gaps remanescentes):** Sessão paralela `test-aivi-isolated` identificou 9 gaps de processo. v1.13.0 absorve **3 com evidência empírica forte** (Gaps 4 RCA / 5 cobertura temporal pós-J4 / 8 handoff cross-sessão). **6 gaps remanescentes registrados aqui como method-audit aguardando 2ª ocorrência confirmatória** (não preemptivos): (1) ancoragem em artefato rotulado "validação" — propõe metodo-senior passo 1A hierarquia fontes; (2) fonte citada pela norma não buscada — propõe metodo-senior passo 1B inventário bloqueante; (3) delta=0 amostra ≠ prova correção — propõe qa-critic rule SE/ENTÃO regressão×correção; (6) campo oficial vazio ignorado — propõe anti-hallucination anti-pattern; (7) inferir autoridade de dado sem confirmar — propõe anti-hallucination anti-pattern; (9) telemetria por papel — parte tratável (timestamp output qa-critic) + parte infra externa harness. **Sem ação preemptiva.** Causa-raiz comum: padrões reais mas com 1 ocorrência só não justificam codificação (princípio 11 honesto operacional).
- **[2026-05-29T23:55] Method-audit (observação do dono sobre isolamento/modelo selection per role):** apenas `qa-critic` explicitamente isolado em subagente; PMO/discovery/architect/developer/docops compartilham contexto+modelo (mesmo viés cognitivo). `_meta/subagent-isolation.md` documenta política existente ("isolar reduz context rot mas elimina visão lateral; trade-off por papel"), modelo per role NÃO codificado. Observação do dono honesta e procedente: maior custo é fazer trabalho mal feito; otimização tokens vs qualidade upfront mal balanceada. **Registrado como candidato v1.14.0 se 2ª ocorrência confirmar** (não preemptivo).
- **[2026-05-29T23:30] Method-audit (princípio 13 SE/ENTÃO recém-codificadas vs minha própria execução):** Em v1.12.1 codifiquei SE/ENTÃO rules + 4 dimensões PC em qa-critic SKILL e **NÃO as apliquei pre-commit da própria v1.12.1**. Submeti para qa-critic sem RRC self-applied; round 1 detectou ALTO (citação ADR não-rastreável, dimensão "process compliance") + MEDIO (rule #1 falta qualificador, dimensão "doc consistência"). **Ambos teriam sido detectáveis por self-check com 4 dimensões antes de submeter.** Dono apontou: "1 round = lean" foi judgment não princípio; assertividade UPFRONT > rounds eficientes downstream. · **Causa-raiz:** pattern recorrente do princípio 11 honesto — agente codifica regra e não a aplica em si próprio. · **Proposta:** PRÉ-COMMIT self-check obrigatório (não opcional) — aplicar SE/ENTÃO rules + 4 dimensões PC ANTES de submeter qualquer bloco a qa-critic. **NÃO adicionar como regra (régua §0 — já está em qa-critic SKILL).** Apenas disciplina: trate qa-critic round como confirmação, não descoberta primária. · **Sem ADR; sem v1.12.2.** Apenas vigilância no próximo bloco.
- **[2026-05-30] Method-audit (princípio 11 / bootstrap):** `/start-session` rodou file-first sobre clone **41 commits atrás** (local v1.9.0 vs remoto v1.13.0); só detectado quando o dono perguntou "fez sync?". · **Causa-raiz:** file-first sem `git fetch` lê retrato congelado — prosa sem mecanismo (justamente o que a série v1.14.x ataca). · **Proposta (lean):** `start-session.md` passo 1 ganha `git fetch` + checagem ahead/behind ANTES de reconciliar WIP; ativação de modo deve ser **verificada** (ler de volta), não assumida. Persistido em `memory/feedback_bootstrap_nao_pode_falhar`. **→ RECORREU e foi codificado como mecanismo em ADR-019 (v1.19.0): hook `check-repo-sync` faz `git fetch`+auto-pull seguro no boot.** (ponteiro inverso method-audit→ADR; fecha Debt #5 da reconciliação 2026-05-30.) Firewall preservado.
- **[2026-05-30] Method-audit (ambiente / robustez do run autônomo):** batch grande de tool-calls em paralelo **cancelou ~50 calls em cascata** por 1 erro (`pwsh` ausente no PATH do bash), perdendo 2 ondas não-commitadas. · **Causa-raiz:** ausência de commit atômico por artefato + `pwsh` só acessível via tool PowerShell/Python `subprocess`. · **Proposta (lean):** commit após cada artefato lógico (git preserva contra cancel); batches pequenos sequenciais quando há dependência. Persistido em `memory/feedback_ambiente_buffer_pwsh`. Sem ADR (não é regra do framework; é disciplina operacional do ambiente Claude Code).
- **[2026-05-30T14:30] Method-audit (princípio 12 / vazamento de domínio RECORRENTE → prosa→mecanismo):** na reconciliação pós-merge, **eu mesmo vazei `ALCOA+` como se fosse o princípio** que justifica preservar o traço de pesquisa (era para ser rastreabilidade/proveniência **agnóstica**, P14). **O dono pegou — 2ª/3ª ocorrência** do mesmo padrão (1ª: README v1.11.0 `ALCOA+/ANP/FDA/BACEN/GAMP`, linhas 154 e 157(a) acima; ambas pegas pelo dono, nunca auto-detectadas). · **Causa-raiz:** Princípio 12 é **prosa**; agente que se auto-audita não detecta o próprio vazamento (viés, P11 honesto). Prosa repetida ≠ garantia — exatamente a tese da série v1.14.x. · **Decisão (executada, NÃO mais "candidato"):** o dono declarou explicitamente prosa→mecanismo → **ADR-020**: `tools/check_core_agnostic.py` (linter fail-closed que varre o NÚCLEO — `_shared/`, `.agent/skills/`, `AGENT-FRAMEWORK.md`, `CLAUDE.md`, `AGENTS.md` — por nomes de norma de domínio fora de contexto-exemplo) + denylist em `tools/` (infra, não-núcleo → não viola agnosticismo) + canário + wiring CI/boot. Fecha o risco residual de ADR-010 §Riscos ("detector de vazamento cross-projeto ausente"). Régua §0(c): destrava garantia inalcançável por prosa.

---

## Telemetria

> Coletor único de auto-observação (ADR-017, v1.17.0). **2 métricas que mudam decisão, nada além** (P5).
> Agregar no fim do bloco/dia, não por turno. Método: `_shared/observability` §Telemetria mínima.

### 17-A Blame (fluxo entre junções, por execução)
> Quando process-critic dispara rewind: registrar junção-origem (J0–J5) + rounds de qa-critic até PASS.

- 2026-05-30 (run v1.14.x): rounds de qa-critic por onda — O0=1, O1=2, O2=1, O3=1 (todos resolvidos como emenda DENTRO de J4 qa-critic→docops; **nenhum rewind cascata cross-junção** — forward-only preservado). Sinal: a montante (discovery/architect) não gerou spec rasa; achados foram de implementação, corrigidos em 1–2 rounds. **Nota honesta (P11):** a métrica 17-A "junção-origem do rewind" NÃO foi exercida nesta onda — nenhum rewind ocorreu; só o proxy `qa_rounds` rodou. Capacidade de blame-de-rewind = [INFERIDO/não-exercido] até um rewind real.
- 2026-05-30T14:30 (reconciliação pós-merge + ADR-020): process-critic adversarial (Sonnet isolado) sobre série mergeada — 6 achados (1 ALTO J4-corrigido, 2 ALTO confirmados, 2 MÉDIO, 2 BAIXO). **J4 do PMO refutou 1 achado do próprio crítico** (count errado) — 1ª evidência empírica de que a célula PMO-verifica-crítico pega false-PASS do crítico, não só do gerador. Bloco ADR-020 (mecanismo agnosticismo): rounds qa-critic registrar ao fechar.
- 2026-05-30T21:30 (v1.21.0 runtime hooks + entrega de produto): qa_rounds = **R1 REPROVADO** (1 ALTO + 2 MÉDIO + 2 BAIXO) → R2 **APROVADO_COM_RESSALVA** (1 BAIXO). **Nenhum rewind cross-junção** — os 5 achados foram resolvidos DENTRO de J4 (qa-critic→fix→re-qa = EMENDA), forward-only preservado. Sinal: o ALTO foi de **implementação** (template↔hook), não de decisão a montante — discovery/architect/ADRs não geraram spec rasa. Capacidade de blame-de-rewind segue [INFERIDO/não-exercido] (nenhum rewind real até hoje).

### 17-B Tally de regra + classe (uso ao longo de sessões)
> `regra — classe(salva-vidas|operacional|andaime) — disparou S/N — sem-disparo:K`. Poda só `andaime` quando K≥N (5–10).

- régua §0 (GANHO LÍQUIDO) — salva-vidas — S — sem-disparo:0 (rejeitou inflação/andaime em toda onda; ex.: _shared fora do contrato, matriz reprovada)
- qa-critic adversarial isolado/heterogêneo — salva-vidas — S — sem-disparo:0 (pegou false-PASS real em O0, O1, O2, O3; em v1.21.0 pegou ALTO template↔hook que 3 testes verdes do gerador escondiam)
- contrato mínimo (validate_skills) — operacional — S — sem-disparo:0 (gate 7/7 em cada onda)
- file-first — salva-vidas — S — sem-disparo:0 (violado no bootstrap → ver Aprendizado 2026-05-30)
