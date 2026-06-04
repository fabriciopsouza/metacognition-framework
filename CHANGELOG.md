# Changelog — Refatoração do Framework Metacognitivo Agêntico

Formato: Keep a Changelog + SemVer. Cada mudança vincula-se à pesquisa que a sustenta.
Maturidade: [CONSOLIDADO] / [EMERGENTE]. Confiança: [CONFIRMADO] / [INFERIDO].

## Política

- **SemVer + Conventional Commits**: feature nova compatível → MINOR; correção sem
  feature → PATCH; quebra → MAJOR. Tag, número no `README.md` e nome do .zip sobem
  juntos a cada release. Detalhe em `guia/GIT-VERSIONAMENTO.md`.
- **Núcleo × aplicação**: o framework é genérico. Domínio (BI, regulado, contexto X)
  vive FORA do núcleo, criado clonando `.agent/skills/_template`. Ver `exemplos/README.md`.
- **Sincronia PROMPT-CHAT-WEB**: o `PROMPT-CHAT-WEB-v4.x.md` na raiz é a encarnação do
  framework para ambientes sem filesystem (Claude.ai, Gemini). Parte dos mesmos
  princípios e busca os mesmos resultados do núcleo. A cada release, revisar — e se
  necessário, bumpar a versão do prompt (v4.2→v4.3…) e registrar aqui.

## [1.42.0] — 2026-06-04 — Hardening: honestidade da vitrine + resiliência a EDR + auditor de liveness + corpus de aprendizado (ADR-059/060/061/062)

### Added
- **ADR-059** — honestidade da vitrine mecanizada: `overclaim_lexicon.py` (detector absoluto-sem-hedge, consciente de hedge/negação) + gates fail-closed em `test_marketing_claims.py` (prompt web derivado de `PUBLIC_SRC`; anti-drift de versão/link da vitrine; disclosure de alucinação residual). [CONSOLIDADO]
- **ADR-060** — sync resiliente a EDR (Kaspersky AAC veta hooks): `check_repo_sync.py` (porte Python + fallback PowerShell) + `prepush_sync_guard.py` (gate humano se push atrás de `@{upstream}`) + nudge no route-gate. Camadas, graceful-degradation por máquina. [CONSOLIDADO]
- **ADR-061** — **auditor de liveness: falha de hook nunca silenciosa**. `hooks-manifest.json` + carimbo `.claude/.hooklive/<key>=<session_id>`; o route-gate (não-bloqueável) declara gates inertes + fallback manual. +porte `check_core_agnostic_hook.py`. Provado ao vivo. [CONSOLIDADO]
- **ADR-062** — relatório de execução enriquecido (estilo-AIVI: detecção framework×humano, gaps, melhorias, boas práticas, **lições por skill**) + corpus PÚBLICO anonimizado opt-in (`learnings_public`: anonymize + gate `sensitive-denylist`, fail-closed) + `consistency-gate` 7ª dimensão + `docs/REPORTS-CONTRIBUTION.md` (LGPD). EMENDA de ADR-038/052. [CONSOLIDADO]

### Notas
- Gate de aceite dos 4 ADRs: **CI verde (macOS/Ubuntu/Windows) + qa-critic adversarial isolado** (verificação na máquina do dono deferida). Cada bloco passou pelo squad completo.
- Limite honesto (LIMITS.md): "100% anti-bloqueio" = exclusão do Kaspersky (não código); anonimização por regex não-exaustiva. Sem overclaim.

## [1.41.0] — 2026-06-02 — Pacote web em dois repos: público × premium PRIVADO (ADR-058)

### Changed
- **Split do pacote web** (decisão do dono "premium web = privado"): `tools/web_export.py` gera `publico/`
  e `premium/` como **repo-roots independentes** (README por tier). `publish-clean.yml` publica em **dois
  destinos** — tier público → `metacognition-framework-web` (PÚBLICO); tier premium → novo
  `metacognition-framework-web-premium` (**PRIVADO/pago**) — com deploy keys separadas. Espelha o split
  não-web `-public` × `-premium` (ADR-049). O `-web` público é republicado **sem** `premium/`.
- **ADR-058** (EMENDA do ADR-054). Repo privado criado; deploy key `PUBLISH_DEPLOY_KEY_WEB_PREMIUM` configurada.

## [1.40.0] — 2026-06-02 — Pacote web automatizado: gerador do main + repo `-web` + cascata (ADR-054/056/057)

> **Implementa** o que os ADRs 054/056/057 decidiram. O chat web deixa de ser arquivo mantido à mão e
> passa a ser **gerado do main**, com nova distribuição dedicada `metacognition-framework-web`.

### Added
- **`tools/web_export.py`** — gerador determinístico do pacote web (dois tiers): tier PÚBLICO (carimba o
  `PROMPT-CHAT-WEB-v4.4.md`) + tier PREMIUM (orquestrador enxuto + **15 skills** geradas do front-matter —
  `description`=gatilho, `pass_criteria`=checkpoint declarado, **encadeamento** da ordem do pipeline;
  discovery consolida sub-modos). Corpo IDE NÃO é copiado (inerte no chat). Carimbo de versão do main.
- **`tools/web-phrasing-map.txt`** — reescrita determinística IDE→chat + lista FORBIDDEN do **gate anti-JARVIS**.
- **`tools/test_web_export.py`** — 9 checagens (determinismo, encadeamento, gate anti-JARVIS pega enforcement injetado).
- **Repo `metacognition-framework-web`** (público, GERADO, não editar à mão) — bootstrap publicado.

### Changed
- **`tools/export-clean.py`**: `--web` delega ao `web_export` (forma de saída distinta — prompts/skills, não repo full).
- **`.github/workflows/publish-clean.yml`**: estágio WEB ao final da cascata (REQ-CASCADE-6), gated no secret
  `PUBLISH_DEPLOY_KEY_WEB` (sem o secret: roda export+gate em CI e pula o push — padrão dos outros tiers).

### Pendência declarada
- Auto-push para `-web` requer o secret `PUBLISH_DEPLOY_KEY_WEB` (deploy key) — setup manual de uma vez pelo
  dono. Até lá, o `-web` é mantido pelo bootstrap manual (este release). Evals Gemini (NFR-1) e token público
  real (GAP-3) seguem como follow-up antes de declarar suporte amplo.

## [1.39.1] — 2026-06-02 — Prompt do chat web sincronizado ao estado atual (v4.4, tier público)

### Changed
- **`PROMPT-CHAT-WEB-v4.4.md`** substitui o `v4.3` (removido): atualiza de "v1.21.0" para **v1.39.0/roteador v2.3**,
  remove resíduo de domínio (Tableau) tornando o transversal 100% agnóstico, e incorpora as doutrinas novas —
  **`enforcement.chat`/anti-JARVIS** (gate vira checkpoint declarado, nunca finge mecanismo) + Matriz de ambiente,
  **postura de execução** textual (default/avançado/autosuficiente; efeito T3 sempre confirma — REQ-MODE-1),
  **desambiguação "avançado"** (eixo execução × discovery=universal/reforço-sênior — ADR-055), **discovery sênior
  por stake inferido** (ADR-051), e **contagem ≠ conteúdo** na validação adversarial.
- Ponteiros vivos atualizados (README, `guia/INSTALAR-NO-VSCODE`, `guia/ORIENTACAO`). Registro histórico (ADRs/spec)
  preserva a menção ao v4.3.
- **Débito declarado:** o v4.4 ainda é mantido à mão; o alvo (ADR-054/057) é gerá-lo do main via profile `web`.

## [1.39.0] — 2026-06-02 — Execution-report de dois tiers: telemetria de processo anonimizada que retroalimenta o framework (ADR-052)

> **O que destrava:** o placar gate × achado (ADR-038) era gerado só no repo do dono, sob invocação.
> Agora o `execution_report.py` é **dois-tiers, com detecção automática por invariante** (`docs/_private/`
> existir = repo-fonte; o `export-clean` o remove de TODA distribuição). No privado → relatório **completo**
> em `docs/_private/_intake/` (realiza o ADR-048). Numa distribuição → **só sinais de PROCESSO codificados**
> (gates, pontos de falha, correções) em `telemetry/`, para o usuário **abrir PR ao master** (o PR é o
> consentimento). **Zero vazamento por mecanismo** (whitelist de schema, não confiança — lição do incidente
> 2026-05-31): texto livre/PII é rejeitado. Payload não-pessoal → **fora da LGPD** (Art. 12) → **opt-out**.

### Added
- **`tools/execution_report.py`** (estende ADR-038): `detect_tier()` por `docs/_private/`; tier EXTERNAL com
  **whitelist de schema** (`gates_fired`/`failure_points`/`correction_events` + escalares codificados),
  heurística **anti-PII** (e-mail/CPF/CNPJ/telefone/strings longas) e **opt-out** (`.claude/no-telemetry.lock`
  · `~/.claude/no-telemetry.lock` · `FRAMEWORK_NO_TELEMETRY`). Invariante anti-fabricação de tokens preservada.
- **`tools/test_execution_report.py`**: 17 casos adversariais (furam o whitelist com nome de cliente, e-mail,
  CPF, prosa-como-valor, enum inválido, seção forjada → todos barrados) + detector de tier + opt-out.
- **`TELEMETRY.md`** + **`telemetry/README.md`**: política de transparência/privacidade, os dois tiers, o
  loop de consentimento-por-PR, e o opt-out. Zona de pouso dos PRs de terceiros no master.

### Changed
- **ADR-052** (Aceito) + **ADR-048** Proposto→**Aceito** (tier OWNER realizado; alt 2 — passo mandatório no
  docops, cross-modo, sem depender de hook). **EMENDA** de status, decisão original preservada.
- **`docops/SKILL.md` §Encerramento**: comando do execution-report passa a **detectar o tier** e grava no path
  correto por tier (corrige o `docs/_intake/` top-level, que o export NÃO removia → risco de vazamento).
- **`SECURITY.md`** (nova seção Telemetria), **`README.md`** (link no topo), **`LICENSE`** (ciência ao usar).
- **ADR-053 + Princípio 14 alargado** (`AGENT-FRAMEWORK.md` §6): o teste binário de handoff passa a ter **dois destinatários** — a próxima sessão/agente **e** o humano que recebe o artefato (usa **sem capacidade oculta**: terminal/instalação/edição de path). Hardcode de ambiente e dependência de tooling oculto **reprovam** o handoff. Destilado agnóstico de insights de método de uma sessão de campo (régua §0: funde no princípio existente, não cria novo).

### Security/Privacy
- Anonimização do tier externo é **gate verificável** (whitelist), não promessa. Caçado e removido um token
  sensível ("AIVI") que um teste distribuível ia carregar — o próprio vazamento que o framework previne.

## [1.38.0] — 2026-06-01 — Reparo do discovery: contexto INFERIDO + pesquisa de âncora MECANIZADA (ADR-051)

> **Causa-raiz provada (caso de campo regulado, alias AIVI — evidência no cofre, fora do repo):** os ADRs
> de discovery sênior (009/033) **não dispararam nem cobriram** o caso — o filtro de entrada do
> `metodo-senior.md` **proibia inferência** ("não inferir por sinais semânticos") e o `check_spec_depth` só
> media dimensões de produto. Quando a pesquisa de contexto foi **de fato executada**, pegou sozinha que a
> **âncora regulatória citada era de outra atividade da cadeia** (referencial, não mandatória), a
> **materialidade financeira** alta e que o **oráculo usava uma variável ≠ da canônica**. Prosa-only não
> pegou; mecanismo executado pegou. **Não foi feature nova — foi reparo.**

### Added
- **`_shared/discovery/context-signals.txt`** — registro agnóstico de sinais de STAKE (lista-semente
  aberta, **auto-retroalimentada sem HITL** via `check_context_brief.py --learn`). Só termos genéricos
  (`check_core_agnostic` barra nome de norma/domínio).
- **`tools/check_context_brief.py`** + **`tools/test_context_brief.py`** (canário, 8 casos) — gate que
  **barra J1 sob sinal de stake** se faltar o `context-brief.md` com **tabela de verificação de âncora**
  (vigência+pertinência), fonte datada e classificação de confiança. Word-boundary (anti falso-positivo),
  stdout utf-8-safe, **exceção consciente** para spec sem entidade externa (flag-não-silencia).
- **`docs/specs/_template/context-brief.md`** — template de evidência persistida (ABNT/ADR/RAG).

### Changed
- **ADR-051** (reparo): supersede o passo-1 (filtro) do **ADR-009**, reconcilia o **ADR-010** (inferir
  STAKE ≠ hardcodar NORMA) e emenda o banco do **ADR-033** (dimensões `contexto-entidade`+`verificacao-ancora`).
- **`metodo-senior.md`**: filtro passa a **inferir stake**; **comportamento proporcional ao modo** (default
  valida com humano · avançado confirma âncoras de alto impacto · autosuficiente infere e reporta) com
  **anti-inversão-de-segurança** (efeito T3 permanece no gate humano, ortogonal ao modo).
- **`handoff.md`** J1 e **`discovery/SKILL.md`** wirados ao novo gate. **LIMITS.md** ganha a claim ADR-051.

## [1.37.0] — 2026-06-01 — Entrega navegável: índice guiado + piso de validação mecanizado (ADR-050 emenda)

> Pedido do dono: entregas **acessíveis e fáceis de entender** — pasta `output/<datestamp>/` com subpastas
> por tipo + **índice visível (html navegável + txt)** com **ordem de leitura guiada**, explicações curtas,
> para o usuário leigo **não se perder**. + crítica adversarial pediu mecanizar o piso (prosa→gate) e a honestidade.

### Added
- **`tools/make_index.py`** (BASELINE — usabilidade/correção, vale nas 3 distribuições): varre a pasta de
  entrega e gera **`index.html`** (navegável) + **`LEIA-ME.txt`** (universal) com **ordem de leitura guiada**
  (comece-aqui → apresentação → docs → código → dados). **Auto-verificação** (lista só o que existe; nada
  órfão, nenhum link pro vazio); **resumo de 3 linhas** (de arquivo de resumo/decisão; senão `NÃO PREENCHIDO`);
  **duplo-papel handoff** (ADR-012: artefato/local/carimbo). + canário `test_make_index.py`.
- **`gen_exec_doc --deliver LABEL`** (premium): monta `output/<datestamp>-<label>/` com subpastas
  (`codigo/ docs/ apresentacao/ dados/`), roteia cada formato e invoca o `make_index`. Documentos passam a ser
  nomeados pelo título (sem colisão em entrega multi-doc).
- **`tools/check_delivery_floor.py`** (premium): mecaniza o piso "**runbook de validação SEMPRE**" (prosa→gate);
  dispensa só consciente (`--allow-skip`), bloqueada em `--regulated`. + canário `test_delivery_floor.py`.

### Fixed
- **Truncagem silenciosa** no `gen_exec_doc`: pptx cortava em 900 chars e pdf em 8 linhas/seção **sem avisar**
  (perda de conteúdo). Agora **pagina** (slides `(i/n)` + PDF multipágina com quebra de linha).

### Changed
- **LIMITS.md** (anti-overclaim, ADR-044): declara que a geração produz **estrutura correta, não polimento
  visual** (sem gráficos/branding/capa) — deck formatado é ADR futuro. Honestidade mecanizada.

## [1.36.0] — 2026-06-01 — Elaboração de documentos premium, flexível por tipo (ADR-050, premium-only)

> Pedido do dono: o premium deve **elaborar documentos** focados no que o usuário elicitou — proposta/
> orçamento (custo + trade-offs + aprovação de mudança/orçamento), **POP/SOP, manual, config/operação,
> manutenção** — em doc/pdf/pptx. **Qual documento cada situação exige é definido pelo discovery/explorer/
> briefing+PMO** (regra deles, inalterada). Premium-only (stripado do baseline).

### Added
- **ADR-050** (Aceito) — `tools/gen_exec_doc.py`: gerador **flexível por TIPO** (renderiza as seções que a
  spec declarar; `<!-- required: ... -->` por template) → **md/docx/pptx/pdf**. Anti-fabricação: campo vazio
  vira **`NÃO PREENCHIDO`**, nunca número inventado. + `tools/test_gen_exec_doc.py` (canário).
  - 7 templates premium em `docs/specs/_template-documentos/` (+ `README.md` da doutrina): **runbook-validação**
    · **apresentação-executiva** · decisão-executiva · pop-sop · manual-operação · guia-configuração · plano-manutenção.
  - **Modelos = REFERÊNCIA, não-determinísticos** (refino do dono): a estrutura real de cada doc é *objetivada
    pelo briefing/spec do cenário/domínio quando ele vier*; o gerador renderiza o que a spec declarar. Forma
    agnóstica inspirada em entregáveis premium reais de vários domínios (forma, nunca conteúdo/nomes).
  - **Piso de validação não-negociável:** **runbook de validação SEMPRE** (prova que funciona). **Domínio
    regulado** (saúde/alimentos/farma/financeiro — *declarado pelo discovery*, ADR-010/012 + `high-stakes-gate`)
    **expande** o conjunto obrigatório (validação/qualificação, rastreabilidade). Núcleo segue agnóstico — não
    decide "é regulado" sozinho.
  - Tudo em `PREMIUM_STRIP_FILES` (stripado de public/non-admin; presente só no premium). `requirements-dev`
    ganha python-pptx/reportlab (opcionais; degrada para md/docx sem elas).
  - Wiring no `blueprint.md` premium (discovery/PMO definem o tipo; o gerador só renderiza).

## [1.35.0] — 2026-06-01 — Três distribuições de fonte única: public · non-admin · premium (ADR-049)

> Pedido do dono: ao final, **3 repos** gerados do **único** privado — `public` (baseline+hooks),
> `non-admin` (baseline+sem-hooks), `premium` (full premium+hooks, privado/pago). Mesma filosofia nos 3.
> A linha **premium × core = experiência × correção**: o baseline entrega produto **funcional e correto**
> com TODA a capacidade analítica/discovery/briefing/QA/segurança; o premium adiciona a **camada de
> experiência** (proposta proativa + UX premium + documentos executivos). **Não tira discovery/análise.**

### Added
- **ADR-049** — tiering premium/baseline de fonte única:
  - Camada premium **marcada e removível**: arquivos (`exemplos/dominio-*/blueprint.md`) + seções entre
    `<!-- premium:start/end -->` (discovery §Blueprint, ux-designer §gate premium).
  - `tools/export-clean.py`: 3 modos — default (baseline strip-premium) · `--nonadmin` (baseline+sem-hooks)
    · `--premium` (mantém premium). `tools/test_premium_tier.py` (canário interno): prova que o baseline
    remove o premium **e PRESERVA o core do discovery** (não mata análise/elicitação).
  - `publish-clean.yml`: publica **as 3 distribuições** do mesmo source. Repo `metacognition-framework-premium`
    (privado/pago) + deploy key + secret criados.
- **ADR-050 (Proposto)** — elaboração de documentos premium (doc/pdf/pptx, custo + trade-offs, fluxo de
  aprovação de mudança/orçamento) — camada premium, a construir.

### Changed
- `build_limits` ganha o claim do tiering (canário interno, não-distribuído); LIMITS regenerado.

## [1.34.0] — 2026-06-01 — Modo NON-ADMIN (sem hooks PS) + pipeline single-source → multi-distribuição (ADR-047)

> Máquina corporativa com GPO `Restricted` bloqueia PowerShell → o framework não iniciava. A versão
> **admin (com hooks) continua a default**; esta adiciona uma variante **non-admin** que inicia sob
> restrição **sem perder funcionalidade**, pelo trade-off do dono: **automação nunca invisível** — o que
> era hook silencioso vira **gate anunciado e aplicado pelo agente**. Uma única fonte gera todas as
> distribuições (admin + non-admin), cada uma com sua característica própria, a cada release.

### Added
- **ADR-047** — modo non-admin + pipeline multi-distribuição:
  - `.claude/settings.nonadmin.json` (sem hooks → inicia sob restrição) + `bootstrap.py` (setup em Python
    puro, sem PowerShell/admin; `--check` diagnostica) + `guia/MODO-NON-ADMIN.md`.
  - Doutrina **"gates anunciados"** em `CLAUDE.md`/`AGENTS.md` §Modo non-admin: o agente declara e aplica
    inline cada gate (ROTA · mission/product_type · action-safety por efeito · ler-antes-de-sobrescrever).
  - `tools/export-clean.py --nonadmin` (variante: settings.json sem hooks) + `tools/test_nonadmin.py` (canário).
    `publish-clean` passa a regenerar **admin + non-admin** do mesmo source.
- **ADR-048 (Proposto/futuro)** — execution-report automático em todo bloco, **somente no privado**
  (registrado a pedido do dono; gatilho a decidir considerando o modo non-admin).

### Changed
- **README:** clareza restaurada — histórico de versões movido do topo para **§Evolução por onda** (nada
  removido). `build_limits` ganha o claim do non-admin; LIMITS regenerado.

## [1.33.1] — 2026-06-01 — Harness de teste isolado (validação de campo sem vazamento)

### Added
- `guia/teste-isolado.ps1` + `guia/TESTE-ISOLADO.md`: harness **agnóstico** para validar o framework num
  caso de domínio real com **isolamento estrutural** (clone do público + projeto com git/memória próprios)
  e checagem de **zero vazamento de volta** (`-LeakCheck` → `--sensitive` + git limpo). Acceptance test de
  "produz premium com menos interações", rodável em 1 comando — sem nome/termo de domínio no framework.

## [1.33.0] — 2026-06-01 — Blueprints de domínio + dicionário-contrato de entrada + ux-gate premium (ADR-046)

> Feedback de campo: o produto saía sub-premium (GUI básica, difícil p/ leigo, **sem validação de
> arquivos**) e exigia ~12 interações. Faltava ao framework **memória de "como é um entregável premium"**.
> Correção: o discovery **propõe a forma premium de uma vez** (assertividade > perguntas), carregada **sob
> demanda** (não infla o núcleo, P12 preservado). Foco no RESULTADO.

### Added
- **ADR-046** — blueprints de produto por domínio + dicionário-contrato:
  - `exemplos/dominio-software/blueprint.md` + novos `dominio-processo/` e `dominio-projeto/` (blueprint +
    product-types) — **3 domínios** como aplicações irmãs, carregadas sob demanda. O discovery PROPÕE a
    forma completa (launcher fácil-ou-CLI · suíte de saída · auditoria), o dono confirma/ajusta numa batelada.
  - `docs/specs/_template/data-dictionary.md` + `tools/check_input_contract.py` + `tools/test_input_contract.py`:
    **auto-detecção + validação** dos arquivos de entrada na pasta (colunas obrigatórias) — resolve "produto
    sem validação de arquivos" e alerta o anti-pattern de join-a-zero (chave float `5123.0`).
  - `ux-designer/SKILL.md` §Definição de pronto PREMIUM (checklist binário: rodável-por-leigo · launcher
    claro · entrada validada · feedback de estado · saída acessível) — barra GUI que "passava" por existir.

### Changed
- `discovery/SKILL.md`: §Blueprint de domínio (carrega o blueprint e propõe assertivamente).
- **Terminologia "genérico" → "flexível"** nos docs/papéis voltados ao usuário (mantido "agnóstico", termo
  técnico preciso) — "genérico soa mal" (pedido do dono).
- `build_limits` ganha o claim do `check_input_contract` (LIMITS.md regenerado).

## [1.32.0] — 2026-06-01 — PMO maestro: re-orquestração na fronteira de bloco (J6, ADR-045)

> Responde à pergunta do dono ("voltar ao PMO a cada gate?"). Análise adversarial: a cada gate NÃO
> compensa (custo+loop+gargalo, e duplica J0–J3/PC). A cada BLOCO compensa e quase já existia — formalizado.

### Added
- **ADR-045** (emenda ao ADR-011) — junção **J6 — PMO re-orquestração de bloco**:
  - Após o process-critic emitir `APROVADO_LIMPO`, o controle volta ao **PMO** para UMA decisão registrada
    no `history.md`: `RE-ORQUESTRAÇÃO: prosseguir | re-priorizar | rewind J_i | injetar escopo | reativar estágio`.
    **NÃO é round-trip por gate** — o intra-bloco segue forward-only (circuit-breaker do ADR-011 preservado).
  - `tools/check_reorchestration.py` (+ canário): audita que o **último bloco fechado** registrou a decisão
    (markers específicos `APROVADO_LIMPO` + `RE-ORQUESTRAÇÃO:` — robusto a prosa negativa). Qualidade da
    decisão = adversarial/não-mecanizável → LIMITS.md.

### Changed
- `handoff.md` (junção J6 + invariante "PMO a cada bloco, não a cada gate"), `pmo/SKILL.md` (maestro de bloco),
  `docops/SKILL.md` §Encerramento (registrar + rodar o linter). Dogfood: decisão registrada no `history.md`.
## [1.31.1] — 2026-06-01 — Fix: integridade da transparência no pacote público + gates cross-drive

> Patch motivado por **crítica adversarial externa que RODOU a suíte no clone público** e achou o defeito
> (grounding > eloquência). O `export-clean` remove `test_core_agnostic.py` (reconstrói fragmentos de token
> de cliente p/ testar o linter sensível), mas o `LIMITS.md` o referenciava e o pipeline não regenerava/
> checava pós-strip → o público recebia um `LIMITS.md` que falhava o próprio `--check`. É o false-PASS que
> o framework combate, na própria vitrine. Confirmado por export fresco + público 404.

### Fixed
- **ADR-044 (build_limits):** `INTERNAL_ONLY` — canário interno não-distribuído vira status determinístico
  (PROVADO na fonte/CI, com nota¹), independente de presença → `--check` passa no privado **e** no export.
  `test_marketing_claims` não conta canário interno como órfão.
- **export-clean.py:** gate de transparência **PÓS-STRIP** (`build_limits --check` + `test_marketing_claims`)
  — não publica se o `LIMITS.md` público divergir (defesa em profundidade; herdado pelo publish-clean).
- **§13.1 do relato de campo (cross-drive):** `check_completeness` e `check_field_mapping` chamavam
  `os.path.relpath(path, ROOT)` sem guarda → `ValueError` com spec em drive/mount diferente (gate "não
  rodava", disfarçado de erro). `try/except` → fallback abs (espelha `check_spec_depth`).

## [1.31.0] — 2026-05-31 — Remediação v2 (marco 9/9): LIMITS.md mecanizado + marketing ancorado

> Item 13 (último): a transparência estava dispersa em prosa. Agora é um índice único, gerado do estado
> real dos canários, com trava de CI — o doc **não pode mentir**, e o marketing não promete além da prova.

### Added
- **ADR-044** — LIMITS.md mecanizado + marketing ancorado:
  - `tools/build_limits.py`: gera `LIMITS.md` (13 capacidades) com status ✅ PROVADO / 🟡 PARCIAL /
    ⏳ EM DESENVOLVIMENTO derivado do canário; `--check` falha o CI se divergir.
  - `LIMITS.md`: "o que entrega hoje" (cada linha: mecanizado × NÃO-mecanizado) + "o que NÃO fazemos".
  - `tools/test_marketing_claims.py`: reprova claim ✅ PROVADO órfão em README/PITCH; exige README linkar LIMITS.
  - `.github/workflows/ci.yml`: step `build_limits.py --check`.

### Changed
- `README.md`: pointer para `LIMITS.md` no topo (status ancorado em evidência).

> **Remediação v2 COMPLETA** (9 marcos, 13 itens, ADR-033..044). 19 canários (18 PASS + 1 SKIP local de
> paridade — provada na matriz CI). Princípio reitor honrado: cada item entrega par executável; prosa só
> onde não-mecanizável, declarada em `LIMITS.md`.

## [1.30.0] — 2026-05-31 — Remediação v2 (marco 8/9): abrangência regulada (denylist + perfis clonáveis)

> Item 11: a denylist era seed não-exaustiva (ITIL/COBIT/SOX/ISO/SOC 2/CLIA passavam) e o caso regulado
> não tinha andaime de partida. Expande-se a denylist + meta-linter de cobertura + perfis opt-in — núcleo agnóstico intacto.

### Added
- **ADR-043** — denylist expandida + catálogo de perfis regulados:
  - `tools/agnostic-denylist.txt`: +11 padrões (SOX, ISO-13485/27001/9001, COBIT, ITIL, Basel, SOC 2, NIST,
    CLIA, Sarbanes-Oxley). NIST/OWASP fundacionais (REFERENCIAS) seguem permitidos via sentinela na citação.
  - `tools/check_regulatory_coverage.py` (+ canário): meta-linter advisory que avisa famílias sem
    representante, mantendo "não-exaustiva".
  - `exemplos/dominio-regulado/`: README + 3 perfis clonáveis (`compliance-profile-*.json`: saúde-dispositivo,
    financeiro, infosec) — andaime de partida, oferecidos pelo discovery quando regulado=sim.

### Changed
- `_shared/action-safety/SKILL.md`: sentinela `lint-agnostic:allow` na citação fundacional de NIST/OWASP.
- `discovery/SKILL.md` 6(a): oferece o perfil regulado clonável. `test_core_agnostic.py`: samples dos novos padrões.

## [1.29.0] — 2026-05-31 — Remediação v2 (marco 7/9): discovery sai de DESIGN-TIME (eval G/H executado)

> Item 10: os evals dos papéis `discovery` (G) e `mapeamento de processo` (H) estavam não-executados —
> a senioridade central era promessa não-medida. Agora EXECUTADO + reproduzível.

### Added
- **ADR-042** — discovery eval executado:
  - `tools/test_discovery_eval.py`: eval funcional EXECUTADO contra 3 briefings sintéticos agnósticos
    (app de indicador / pipeline / relatório), medindo cobertura das dimensões (ADR-033) + controle raso
    que discrimina. Reproduzível na matriz CI.
  - `_meta/eval-results-discovery.md`: roteamento G/H (should-trigger/should-NOT) + eval funcional.

### Changed
- `_meta/eval-results-papeis.md`: status G/H DESIGN-TIME → **EXECUTADO** (ponteiro para o novo arquivo).

## [1.28.0] — 2026-05-31 — Remediação v2 (marco 6/9): effect-gate vira motor de regras por efeito

> Item 7: o effect-gate eram ~5 padrões grep no código; bypasses conhecidos passavam (find -delete,
> reset --hard, clean -fdx, curl|bash, exfil). Agora a **política é dado** (`effect-rules.json`) e o hook
> é o **interpretador** — adicionar família/regra não toca o hook.

### Changed
- **ADR-039** — effect-gate motor por efeito (refatora ADR-015):
  - `tools/effect-rules.json`: 12 regras / 5 famílias (mass-destruction, history-rewrite,
    escalation-persistence, exfiltration, resource-exhaustion); cada regra `all`[]+`none`[]+tier+decisão.
  - `tools/hooks/effect-gate.ps1` (ASCII-only, dodge do BOM/cp1252) + `.sh` (jq + grep -E): interpretadores;
    regex no subconjunto comum .NET ∩ POSIX-ERE para paridade. default-ALLOW; T3→deny, T2→ask.
  - `tools/test_effect_gate.py`: agora decision-based (deny/ask/allow), ≥2 deny + ≥2 benignos por família +
    fuzzing de flag/aspas/espaço. `tools/test_parity.py`: decisão idêntica .ps1↔.sh (validada local por
    emulação grep -E; prova final na matriz CI).
- OWASP LLM06 segue **🟡** até a matriz CI (3 SOs) + paridade 100% verdes (honestidade via LIMITS.md/ADR-044).

## [1.27.0] — 2026-05-31 — Remediação v2 (marco 5/9): segurança de escrita + governança (overwrite-guard + execution-report)

> Itens 5 + 6 ⭐: o overwrite cego de artefato (E1) passava pelo effect-gate; e tokens/custo/placar nunca
> eram medidos (o framework não aprendia com a própria execução). Dois mecanismos fecham os dois.

### Added
- **ADR-037** — action-safety em overwrite cego:
  - `tools/hooks/overwrite-guard.ps1` + `.sh`: `PreToolUse(Write|Edit)` bloqueia (`exit 2`, robusto ao bug
    #37210) sobrescrita de arquivo com conteúdo **não-lido/não-criado nesta sessão**; `PostToolUse` registra
    os arquivos lidos/criados (manifesto por `session_id`). Wirado no `.claude/settings.json`.
  - `tools/test_overwrite_guard.py`: canário (+ paridade .sh quando há jq). **Dogfood:** o hook pegou a
    própria edição do agente e revelou um bug real (PowerShell desembrulha array de 1 elem → corrigido com List).
- **ADR-038** — execution-report automático (estende ADR-026):
  - `tools/execution_report.py`: tokens (via transcripts; senão **NÃO MEDIDO**, nunca fabricado), tempo,
    turnos, arquivos, testes, retrabalho e **placar gate × achado**. `validate_report()` reprova report
    ausente / sem placar / token fabricado. Wirado no `docops` §Encerramento.
  - `tools/test_execution_report.py`: 5 casos (inclui regressão "token fabricado sem fonte").

## [1.26.0] — 2026-05-31 — Remediação v2 (marco 4/9): estabilidade de decisão (anti-viés-de-oráculo + sicofância)

> Itens 3 + 9 ⭐: o erro mais caro foi de **execução**, não elicitação — mapear termo→coluna por inferência,
> bater o alvo e tratar como validar semântica, abandonar resultado validado sem prova. Mecaniza-se a
> **exigência de registro**; o julgamento semântico fica adversarial (declarado em LIMITS.md).

### Added
- **ADR-035** — gate de ambiguidade de campo-fonte:
  - `tools/check_field_mapping.py`: mapeamento termo→coluna sem **confirmação do dono + justificativa** = FAIL.
  - `tools/test_oracle_bias.py`: 4 casos sintéticos (colunas-irmãs perto do alvo); inferência/over-correção reprovam.
- **ADR-041** — sicofância como dimensão de teste de 1ª classe:
  - `tools/test_sycophancy.py`: prova que o gate **reprova** entrega que bate o alvo mas mapeia por inferência
    (reusa `check_field_mapping` — régua §0). Limite: prova o erro plantado conhecido, não casos novos.

### Changed
- `qa-critic/SKILL.md`: rule #9 (anti-viés-oráculo + "que outra interpretação produz este número?" +
  anti-over-correção) — contagem "9 rules" sincronizada.
- `docs/specs/_template/requirements.md`: seção `## Mapeamento de campo-fonte` (condicional a colunas-irmãs).

## [1.25.0] — 2026-05-31 — Remediação v2 (marco 3/9): entrega vira produto, não script (completude + porta-do-usuário + ambiente limpo)

> Itens 2 + 4 ⭐ do plano: a aritmética bate mas o **produto** falha — entrega cobre subconjunto do pedido,
> entry-point quebra no terminal, requirements nunca testados limpos. Três gates mecânicos fecham os três.

### Added
- **ADR-034** — gate de completude pedido × entrega:
  - `tools/check_completeness.py`: detecta quantificadores de escopo no pedido ("cada X", "mês a mês",
    "acumulado"…) e exige critério binário no `validation.md` para cada um. Wirado como qa-critic **rule #8** (J4).
  - `tools/test_completeness.py`: 4 casos sintéticos agnósticos ("1 mês ≠ mês a mês" reproduzido sem domínio).
- **ADR-036** — teste pela porta do usuário + ambiente limpo (app SW/dados, ADR-023):
  - `tools/check_entrypoint_tty.py`: roda o entry-point sem TTY; `input()` bloqueante como única via = FAIL.
  - `tools/check_clean_env.py`: `pip install` em venv descartável + import; modo `--check --no-network` p/ CI.
  - `tools/test_entrypoint_no_tty.py` + `tools/test_clean_env.py`: canários sintéticos.

### Changed
- `qa-critic/SKILL.md`: rule #8 (completude) — contagem "8 rules" sincronizada.
- `evals-engineer/SKILL.md`: §Gate de entrega de software ("pronto" = porta-do-usuário + ambiente-limpo + completude).

## [1.24.0] — 2026-05-31 — Remediação v2 (marco 2/9): elicitação-consultiva mecanizada (causa-raiz nº1)

> Item 1 ⭐ do plano: o gap mais caro do incidente de campo foi a **antecipação**, não a segurança de
> ação. A elicitação era "de coletor", não "de consultor", e a instrução em prosa foi ignorada. Correção
> mecânica: banco agnóstico de dimensões + linter que **barra J1** se a spec não decidir o produto.

### Added
- **ADR-033** — elicitação-consultiva + linter de profundidade de spec:
  - `_shared/discovery/elicitation-dimensions.md`: banco agnóstico das 9 dimensões universais (operador,
    interface, entrada-validação, escopo-temporal, recortes-saída, persistência, auditoria-log,
    ambiente-execução, formato-saída), tabela machine-readable com aliases. Só **meta-perguntas** (agnósticas);
    perguntas de domínio nunca entram (barradas por `check_core_agnostic`).
  - `tools/check_spec_depth.py`: gate exit 1 se o `requirements.md` não registra **decisão** (não placeholder)
    para cada dimensão obrigatória. Verifica cobertura, não qualidade (limite → `LIMITS.md`).
  - `tools/test_spec_depth.py`: 5 casos sintéticos agnósticos — spec rasa "calcular X" FALHA; spec que decide
    as 9 dimensões PASSA; placeholder `<...>` não conta.

### Changed
- `discovery/SKILL.md`: §Elicitação-consultiva (postura de default sênior + trade-off, não pergunta em aberto).
- `handoff.md` J1: gate `check_spec_depth.py` PASS para produto recorrente.
- `docs/specs/_template/requirements.md`: seção `## Dimensões de elicitação`.

## [1.23.0] — 2026-05-31 — Remediação v2 (marco 1/9): CI cross-platform + paridade `.sh`↔`.ps1` provada

> Onda **remediação v2** — consolida crítica adversarial sobre v1.22.0 + evidência de campo (incidente
> registrado em `docs/_private/`, fora da distribuição). Princípio reitor: **tudo vira hook/linter/teste**;
> prosa só onde não-mecanizável, e então declarada em `LIMITS.md`. Este marco é a BASE que prova todo o resto.

### Added
- **ADR-040** — paridade cross-platform real + CI matriz 3 SOs:
  - `tools/run_canaries.py`: runner único que descobre e roda cada `test_*.py` como subprocesso (exit = nº
    de falhas). Os canários são scripts standalone (não pytest-collectáveis); este é o entrypoint canônico.
  - `tools/test_parity.py`: exige veredito `deny`/`allow` **idêntico** entre `effect-gate.ps1` e `.sh` para
    cada payload (fonte única: importa `CASES` do `test_effect_gate`); SKIP se faltar pwsh/bash/jq.
  - `.github/workflows/ci.yml`: matriz `ubuntu+macos+windows`, roda o runner + o tier norma do
    `check_core_agnostic` em todo push/PR (o tier --sensitive é gate de export, não roda no source privado).
  - `tools/requirements-dev.txt`: parsers opcionais (openpyxl, python-docx); núcleo segue sem dep de runtime.

## [1.22.0] — 2026-05-31 — Entrada determinística: roteamento mecânico + wiring self-heal + doc-intake + consistency-gate

> Onda **prosa→mecanismo da ENTRADA**, motivada por incidente confirmado (relato AIVI): um agente executou
> tarefa regulada/financeira **sem rotear** — o roteamento era prosa (CLAUDE.md) e o auto-boot global estava
> desligado (clobber do mode-apply no settings global). "Nada importante em prosa → tudo vira ferramenta."

### Added
- **ADR-027** — `route-gate` (`tools/hooks/route-gate.ps1`/`.sh`): hook `UserPromptSubmit` **universal**
  (independe de git/owner/marker) que injeta lembrete de rota 1×/sessão, **fail-open**. + `ensure-global-wiring.ps1`:
  **self-heal hook-preserving** chamado pelo `sync-global` (ponto de Arquimedes no settings de PROJETO) que
  re-afirma a wiring global a cada abertura — derrota o clobber mecanicamente. + **§disable-com-memória**
  (session.lock lê CreationTime + `reason:` e oferece reativação no boot).
- **ADR-029** — **doc-intake** (`_shared/doc-intake` + `tools/doc_intake.py` + canário): parse determinístico
  pdf/docx/xlsx/pptx/md/txt → chunk (overlap, fronteira de parágrafo) → **manifesto JSON** com sha256 por
  arquivo/chunk, **offline e SEM embeddings**, degrada com segurança. Integrado ao discovery (proveniência por chunk+sha).
- **ADR-030** — `consistency-gate` (`tools/hooks/consistency-gate.ps1`): auditoria de fechamento **fail-soft**,
  6 dimensões (version-sync, adr-status, checkpoint, contagens, **unpushed**, transientes), exit = nº de
  inconsistências, `-Json`. Wirado no docops §Encerramento. Validado por dogfood.
- **`guia/RESILIENCIA-ACESSO.md`** — recovery de CONTA GitHub > chave local + push cedo (decisão de resiliência).

### Changed
- **ADR-028** — `_shared/metacognition-core` §Precedência ganha **nível 7**: output-style/persona governa
  tom/formato, **subordinado ao nível 6** e **nunca suplanta** regras invioláveis (2) nem roteamento/gates (5).
  O `route-gate` encarna a norma; a cláusula é o lar normativo (corrige a 2ª metade da falha-raiz AIVI).
- **Hooks PS gravados com UTF-8 BOM** (route-gate, ensure-global-wiring, inject-global): PS 5.1 lê fonte
  sem-BOM em ANSI e o não-ASCII vira mojibake no contexto injetado — BOM corrige decode + saída.
- **Housekeeping**: ADR-024/025/026 → **Aceito** (features mergeados); checkpoint retroativo v1.21.1+1.21.2 no `history.md`.

### QA
- Process-critic adversarial isolado (Sonnet, heterogêneo ao Opus — ADR-018): **APROVADO_COM_RESSALVA** →
  3 MÉDIO + 5 BAIXO **todos emendados** dentro da J4 (forward-only): chunk-id único entre subpastas, schema
  no ramo de erro, teste de reconstrução literal, precedência sem ambiguidade, claim de integração honesto, BOM nos hooks.

## [1.21.2] — 2026-05-31 — Polish pós-v1.21.1: site holístico, contador de tempo, OWASP regulado, higiene

### Added
- `tools/project_report.py`: **contador de tempo/interação** (duração por sessão + total + throughput
  tokens/min) — proxy de custo p/ corporações; canário cobre a duração (`session_duration_min`). ADR-026 estendido.

### Changed
- `README.md`: **link do site no topo** + linha "Comece" + intro holística (sem remover conteúdo).
- `SECURITY.md`: nota de enquadramento na tabela OWASP LLM — *por que 🟡 é o teto honesto de uma camada de
  orquestração* + ponteiro "para ambiente regulado" (responsabilidade compartilhada + auditoria independente).
  Cores honestas inalteradas; só contexto que evita o misread "amarelo = fraco".
- Site: parágrafo de gates condensado; fluxo de instalação encurtado.
- `docs/_intake/SUMARIO-NOTURNO-2026-05-27.md` movido da raiz (raiz só load-bearing).

### Security / Autoria
- Commits e tags do repositório agora **assinados (SSH) e Verified** no GitHub — concretiza a recomendação
  do ADR-025 (proteção de autoria transparente); provê proveniência verificável da autoria do método.

## [1.21.1] — 2026-05-31 — Consolidação pós-v1.21.0 (site/docs/ergonomia/autoria + relatório de tokens)

> Consolida o trabalho feito **após** a tag v1.21.0, em PRs separados (#22–#28), cada um parando no
> gate humano. Mecanismos novos (prosa→mecanismo) + reestruturação do site + blindagem de autoria.

### Added
- **`tools/project_report.py`** (**ADR-026**) — relatório de **tokens** (total/média por sessão) +
  **história compactada** lida dos transcripts do Claude Code → base de documentação + reconstrução.
  Sem transmissão (ADR-025); parse tolerante; canário 6/6.
- **`LICENSE`** (CC BY 4.0) — antes **ausente** apesar de citada no README; torna a atribuição ao autor
  obrigatória e a remoção uma violação (recurso legal). + **`NOTICE`** (proveniência).
- **`tools/check_attribution.py`** — guarda **transparente** de autoria (quebra o build se LICENSE/NOTICE/
  crédito no README for removido). **ADR-025**: proteção de autoria transparente — **refuta** mecanismo
  oculto/telemetria silenciosa/"phone-home" (spyware) explicitamente.
- **`/start-session` como comando registrado** (`.claude/commands/start-session.md`, **ADR-024**) +
  esclarecido que **não é rígido** (o agente elicita por prosa/perguntas/inspeção; você preenche só 2
  arquivos por projeto: `briefing.md` + `00-glossario.md`).
- Site: **GitHub Release v1.21.0** (página + .zip de download).

### Changed
- **Site (`guia/web/`)**: links → GitHub renderizado; fluxo de instalação real (instalar Claude Code →
  clone → bootstrap → "iniciar"); seção **Segurança** + **Riscos de operar código por IA**; **Como foi
  construído** (com as falhas); botões de compartilhar (LinkedIn destaque); engenharia de **gates binários**
  (anti-loop/escalação); cards de valor (tokens/telemetria/método); e **reestruturação de IA** (enxugado,
  profundidade nos docs git-linkados). Stack declarada: **testado/desenhado p/ Claude Code; Gemini/Copilot
  em desenvolvimento**.
- **Chat-web `PROMPT-CHAT-WEB-v4.3`** (paridade de comportamento: product_type + papéis de entrega).
- README: linha de **atribuição ao autor** (estava ausente — pega pelo `check_attribution`).

## [1.21.0] — 2026-05-30 — Hooks de runtime (compaction/mission) + camada de entrega de produto

> MINOR. Origem: revisão de uma pesquisa/SPEC externa (Perplexity) que **re-derivou contra fontes
> oficiais** o núcleo já mecanizado na série v1.14.x→v1.20.0 — validação externa. Filtrado o ganho real
> (lean): mecanismos novos onde havia prosa + correção do **viés de processo-sobre-produto** (o framework
> existe para **culminar em produto** de software/dados, reorientação do dono). Núcleo permanece agnóstico
> (P12) e inalterado em `_shared/`. Bloco passou por qa-critic adversarial (Sonnet isolado): REPROVADO
> round 1 (1 ALTO template↔hook + 2 MÉDIO + 2 BAIXO) → corrigido → re-verificado.

### Added
- **ADR-021 — `compaction-gate` (PreCompact hook):** bloqueia compaction quando `history.md` está ausente
  ou sem checkpoint (caso catastrófico); fail-open; backstop conservador (filosofia do `effect-gate`).
  Mecaniza a obrigatoriedade de digest do ADR-016. `tools/hooks/compaction-gate.{ps1,sh}` + canário.
- **ADR-022 — `mission-gate` (SessionStart hook):** declara/confirma `product_type` + escopo (funde com
  o escopo do discovery, ADR-010/012), com confirmação proporcional ao **modo de execução** (ADR-005);
  3 modos BRIEFING/ADVANCE/STANDARD. Taxonomia de tipos é da **aplicação** (agnóstico, P12). PreToolUse
  backstop deferido (fase 2). `tools/hooks/mission-gate.{ps1,sh}` + `docs/specs/_template/mission.md` +
  canário + discovery passo 6(f).
- **ADR-023 — app de entrega `exemplos/dominio-software/`:** distribuição especializada (demonstração
  viva) com `ux-designer` + `evals-engineer` — os 2 papéis que melhoram o **produto** entregue; ativados
  por `product_type` (`product-types.txt`). `governance-lead`/`skill-librarian` **não** criados (cobertos
  por `high-stakes-gate`/`action-safety` e pelo campo `classe`). `validate_skills.py` passa a cobrir
  `exemplos/*/*/SKILL.md`.

### Changed
- `guia/web/index.html` → v1.21.0: camada ENFORCEMENT (runtime hooks), `_shared` corrigido (9 regras,
  +action-safety +execution-modes), cards de enforcement e entrega de produto, app `dominio-software`.
- `tools/managed-settings.template.json`: caminho Windows oficial (`C:\Program Files\ClaudeCode\`) +
  status atual do bug #44642 (aberto, "not planned"). `effect-gate.{ps1,sh}`: ressalva do bug #37210.
- **Sincronia PROMPT-CHAT-WEB:** `PROMPT-CHAT-WEB-v4.2.md` → **v4.3** (paridade de comportamento: declarar
  `product_type`/escopo no briefing + papéis de entrega ux/evals simulados p/ produto SW/dados — sem
  prometer paridade de hook; corrige ref morta `§17`). Refs ao filename atualizadas (README, INSTALAR,
  ORIENTACAO, GIT-VERSIONAMENTO). `GUIA-EQUIPE.md` ganha §12 (catch-up v1.14.x→v1.21.0: enforcement
  mecanizado + entrega de produto). ADRs históricos (010) e specs antigas preservam a ref v4.2 (imutável).

## [1.20.0] — 2026-05-30 — Linter de agnosticismo do núcleo (ADR-020) — último elo "prosa→mecanismo"

> MINOR. Mecaniza o **Princípio 12** (núcleo agnóstico) e a **regra #5 do qa-critic**, que eram prosa e
> falharam ≥2× (vazamentos de norma de domínio — ALCOA+/ANP/… — sempre pegos pelo DONO, nunca pela
> auto-observação do agente; o último foi nesta sessão). EMENDA: mesmo padrão contrato↔validador do
> ADR-013 e regra↔gate do ADR-015. Régua §0(c): destrava garantia inalcançável por prosa.

### Added
- **`docs/adr/020-linter-agnosticismo-nucleo.md`** (Aceito).
- **`tools/check_core_agnostic.py`** — linter stdlib: varre o núcleo operativo, exit 1 + `LEAK arquivo:linha` por vazamento.
- **`tools/agnostic-denylist.txt`** — ruleset (regex/linha) em `tools/` (infra, não-núcleo → não viola o P12); não-exaustivo por design.
- **`tools/test_core_agnostic.py`** — canário 17/17 com efeito (limpo-passa · vazamento-pega · sentinela-isenta · cada padrão detectável · agnóstico-não-falso-positiva).
- **`.claude/hooks/check-core-agnostic.ps1` (+ `.sh` paridade)** — hook SessionStart fail-soft: avisa no boot se o núcleo vazou; nunca bloqueia.

### Changed
- **`.claude/settings.json`** — +1 hook SessionStart (após `check-repo-sync`, antes do `inject-start-session`).
- **`.claude/hooks/sync-global.ps1`** — espelha o novo hook para `~/.claude/hooks/` (padrão ADR-019).
- **`.agent/skills/qa-critic/SKILL.md`** — regra #5 ganha ponteiro ao enforcement executável + sentinela `lint-agnostic:allow` (única menção legítima: a própria definição da regra).

### Notes
- Exceção auditável: sentinela `lint-agnostic:allow` + justificativa (estilo `# noqa`).
- [DESCONHECIDO] honestos: denylist não-exaustiva (normas novas existem — backstop é a regra #5 semântica); paridade `.sh` não testada em Linux/macOS.

## [1.19.0] — 2026-05-30 — Sync de repo no boot via hook (ADR-019) — fecha a dívida da série

> MINOR. Fecha como **mecanismo em runtime** o gap que a série v1.14.x deixara como prosa (method-audit):
> o `/start-session` operava sobre clone local sem `git fetch` (caso real: 41 commits atrás de main).
> Dívida cobrada pelo dono. EMENDA aos Princípios 8 e 11; estende a cadeia SessionStart (ADR-004/005/006).

### Added
- **`docs/adr/019-boot-sync-repo.md`** (Aceito) — política honesta: `git fetch` sempre; auto-`pull --ff-only`
  só quando seguro (tree limpo + fast-forward); avisa sem tocar se sujo/divergiu; falha soft.
- **`.claude/hooks/check-repo-sync.ps1`** (+ `.sh` paridade) — hook SessionStart de propósito único.
- **`tools/test_repo_sync.py`** — canary 5/5: prova auto-update seguro, aviso-quando-sujo, silêncio-em-dia, com efeito verificado.

### Changed
- **`.claude/settings.json`** — registra check-repo-sync no SessionStart (antes do inject-start-session).
- **`.claude/hooks/sync-global.ps1`** — espelha o hook para `~/.claude/hooks/`.
- **`.agent/workflows/start-session.md`** — passo 1 manda `git fetch` + ahead/behind ANTES de reconciliar (superfície chat).

### Pendências (Princípio 11 honesto)
- Registro no SessionStart **global** (outros repos squad via bootstrap.ps1) — follow-up trigger-gated **[DESCONHECIDO]**.
- Paridade `.sh` em Linux/macOS não testada **[DESCONHECIDO]**.

[CONSOLIDADO] / [CONFIRMADO] após merge.

---

> **Série v1.14.x "da prosa ao mecanismo" (Ondas 0–4, 2026-05-30)** — importa o *runtime* do JARVIS
> (hooks, threshold medido, allowlist, gate executável, telemetria) para dentro do método, **filtrado
> pela régua §0** e **agnóstico de domínio**, rejeitando o andaime que derrubou o JARVIS. 6 ADRs
> (013–018), 5 PRs stacked (#11–#15), cada onda com qa-critic adversarial isolado+heterogêneo.
> Lastro: `docs/_intake/v1.14.x-digest-pesquisas.md` (P1–P7; movido p/ _intake na reconciliação 2026-05-30). Os CHANGELOGs das ondas consolidam aqui
> (a stack mergeia em ordem #11→#15).

## [1.18.0] — 2026-05-30 — QA adversarial de turno único + heterogeneidade de modelo (ADR-018) — Onda 4

> MINOR (P6). Captura o útil do "Conclave" de 3 papéis a custo ~zero no qa-critic existente e **rejeita**
> a estrutura de 3 papéis (homogêneo reforça viés; MAD não supera self-consistency). EMENDA ao Princípio 13.

### Added/Changed
- **ADR-018** (Aceito) — protocolo **steelman→ataque→veredito** (1 turno); **heterogeneidade de modelo**
  gerador↔crítico (Zhang 2025 Heter-MAD); **disparo condicional** (Self-Critique Paradox: forçar crítica
  onde o modelo acerta derruba acurácia 15–40% — silencia QA *reforçado*, nunca o adversarial *básico*).
- **`.agent/skills/qa-critic/SKILL.md`** +seção "Protocolo de turno único" + reconciliação de veredito
  (2 eixos: `passou` binário herda modalidade; `recomendacao` = ação ortogonal). **`_meta/subagent-isolation.md`** +nota de heterogeneidade.
- **Rejeitado:** Conclave de 3 papéis (régua §0). qa-critic 2 rounds: round 2 pegou false-PASS auto-gerado (validação empírica do ADR-018).

## [1.17.0] — 2026-05-30 — Telemetria mínima de processo + poda temporal (ADR-017 pai) — Onda 3

> MINOR (P5+P7). Auto-observação mínima: importa a medição do JARVIS, rejeita o andaime (11 coletores,
> matriz instrumentada). EMENDA aos Princípios 10/11. **Coletor único** (DOSSIÊ §3).

### Added/Changed
- **ADR-017** (Aceito, ADR-pai): **17-A blame** (SÓ 2 métricas: junção-origem do rewind + qa_rounds);
  **17-B poda** (tally S/N + `classe` + contador `sem-disparo:K` + poda só `andaime` quando K≥N=5–10;
  `salva-vidas` nunca poda; Chesterton). Fronteira de coletor único com mecanismo (transcrição de span no checkpoint).
- **`_shared/observability`** +§Telemetria; **`history.md`** +`## Telemetria`; **`checkpoint.md`** +gancho. `classe` reusa ADR-013.
- **Rejeitado:** matriz de relevância instrumentada (P7). qa-critic round 1: 3 MÉDIO + 2 BAIXO, corrigidos.

## [1.16.0] — 2026-05-30 — Compaction por threshold medido + digest persistente (ADR-016) — Onda 2

> MINOR (P2). Troca o gatilho qualitativo por **faixas medidas** (degradação é gradiente). EMENDA ao Princípio 8; digest liga ao 14.

### Added/Changed
- **ADR-016** (Aceito) — faixas 🟢<50/🟡50–69/🟠70–84/🔴≥85 (fronteira inclusiva à esquerda); proxy
  chat `chars÷3`; cortes = escolha de engenharia [INFERIDO]. **`§2.5`** + **`checkpoint.md`** faixas;
  **`docs/specs/_template-digest/digest.md`** = Pacote de handoff (§P14) estendido (superset). qa-critic round 1: 1 ALTO + 3 MÉDIO + 3 BAIXO, corrigidos.

## [1.15.0] — 2026-05-30 — Allowlist por efeito (ADR-014) + Enforcement fail-closed (ADR-015) — Onda 1

> MINOR (P4+P1). Par de maior valor: da prosa ao mecanismo na **segurança**. EMENDA aos Princípios 1/13.

### Added/Changed
- **ADR-014** — classifica por **EFEITO** (E1–E6), tiers T1/T2/T3, default-deny, gate humano p/ T3.
- **ADR-015** — gate executável no IDE + honestidade no chat (`enforcement:{ide,chat}` **nunca** afirma paridade).
- **`_shared/action-safety`**, **`tools/hooks/effect-gate.ps1`/`.sh`** (deny-backstop T3), **`managed-settings.template.json`**, **`tools/test_effect_gate.py`** (canary fiel + auto-guarda). qa-critic 2 rounds: 3 ALTO (bypasses de `rm`) corrigidos → APROVADO_LIMPO.

## [1.14.0] — 2026-05-30 — Contrato mínimo de skill (ADR-013) — Onda 0

> MINOR (P3). Contrato de interface das skills vira gate verificável. EMENDA ao Princípio 5.

### Added/Changed
- **ADR-013** — 8 campos obrigatórios + 5 opcionais. **`tools/framework-schema.json`** + **`tools/validate_skills.py`** (stdlib, 7/7 PASS).
- 7 skills + `_template` com frontmatter de contrato; `_shared/` fica fora (rule-holders). qa-critic round 1: 3 MÉDIO + 3 BAIXO, corrigidos.

---

## [1.13.0] — 2026-05-29 — Handoff cross-sessão obrigatório (ADR-012) + drift sync + rules #6 RCA e #7 cobertura temporal pós-J4

> MINOR feature. Derivado de **dogfood real do v1.12.x** em case regulado externo (repo paralelo `test-aivi-isolated`). Sessão paralela aplicou 2 edits globais sem sincronizar framework repo — drift confirmado. Process-critic round 1 desta v1.13.0 identificou: rule #4 SE/ENTÃO v1.12.1 cobre polish post-release, NÃO artefato novo intra-bloco pós-J4 (gap real, rule #7 nova). Princípio 11 honesto aplicado: 6 gaps remanescentes ficam method-audit (não preemptivo).

### Added
- **`docs/adr/012-handoff-cross-sessao.md`** — decisão arquitetural; 5 alternativas; relaciona ADR-010 (passo 6(e)) + ADR-011 (princípio 14 paridade com 13).
- **`docs/specs/v1.13.0-aivi-method-fixes/validation.md`** — gate binário V1-Vn.
- **Princípio 14** em `AGENT-FRAMEWORK.md §6`: Handoff cross-sessão obrigatório quando declarado.

### Changed
- **`_shared/metacognition-core/SKILL.md`** v1.0.0 → v1.1.0: +seção §Pacote de handoff cross-sessão (sync com global).
- **`.agent/skills/discovery/SKILL.md`** passo 6 Modo B: 4 → 5 perguntas (item (e) "Alimenta outra sessão?"; sync com global).
- **`.agent/skills/qa-critic/SKILL.md`** — +rule #6 SE/ENTÃO RCA gate + rule #7 SE/ENTÃO cobertura temporal pós-J4.
- **`CLAUDE.md`** + **`AGENTS.md`** + **`README.md`** + **`guia/GUIA-EQUIPE.md`** + **`guia/web/index.html`** — seções/cards v1.13.0.

### Pendências (princípio 11 honesto)
- 6 gaps remanescentes do dogfood AIVI (Gaps 1/2/3/6/7/9) ficam method-audit aguardando 2ª ocorrência confirmatória.
- Isolation/model selection per role (observação do dono): candidato v1.14.0.

### Pipeline
Dogfood AIVI (relatório externo) → Architect (ADR-012, 5 alt) → Developer (drift sync + 2 rules + ADR + princípio 14) → qa-critic adversarial.

[CONSOLIDADO] / [CONFIRMADO] após merge.

---

## [1.12.1] — 2026-05-29 — Process discipline refinements: retrospective gate + SE/ENTÃO recurrent QA rules + PC critica 4 dimensões (method-audit 2026-05-29)

> PATCH refinements derivados de method-audit notes da sessão 2026-05-29 (não introduz novo princípio; refina aplicação do princípio 13). Régua §0 critério (c): codifica padrões recorrentes observados em ADR-009/010/011 absorptions (stale counts, polish auto-classificado, citações ADR não-rastreáveis) sem criar nova skill/workflow.

### Changed
- **`.agent/workflows/start-session.md`** — passo **2.5 NOVO**: retrospective gate light (PMO adversarial revisa último bloco entregue desde último PASS do process-critic; 4 itens binários: process/RRC/debt/polish-classification). Sem ADR dedicado (formalizar ADR-012 só se padrão persistir). Flexibilidade: dono pode escalar "skip retrospective" em contexto trivial — decisão consciente.
- **`.agent/skills/qa-critic/SKILL.md`** — 2 mudanças:
  - **Modalidade PC ganha 4 dimensões de crítica explícitas** (v1.12.1): (i) lógica/código, (ii) spec/validation cobertura, (iii) doc consistência (cross-refs + contagens em sync + nomenclatura), (iv) process compliance (J0-J5 evidência + RRC + citações rastreáveis). Antes era implícito; agora explícito.
  - **Seção nova "Padrões SE/ENTÃO recorrentes"**: 5 rules derivadas de method-audit (stale counts com qualificador "mesma entidade nomeada"; oxímoros semânticos; STATUS-field inflado; polish auto-classificado; exemplos didáticos de domínio fora de `docs/specs/exemplos/`). Mindset adversarial mantida para novel bugs.

### Pipeline
PMO/Discovery (inline 2026-05-29; user propôs Q1 retrospective gate + Q2 SE/ENTÃO + spec/doc/process explicit) → Architect (sem ADR dedicado; refinamento operacional vincula a ADR-011 + method-audit como fonte) → Developer (3 edits cirúrgicos em 2 arquivos + CHANGELOG) → qa-critic round 1 adversarial (1 ALTO + 1 MEDIO + 2 BAIXO; ALTO=citação ADR não-rastreável corrigida; MEDIO=qualificador "mesma entidade nomeada" adicionado; BAIXOs absorvidos neste mesmo commit) → **decisão lean: 1 round + fixes em pass único + merge** (não iterar; aplica diretiva "lean e realista" do dono — replicar pattern v1.10/11/12 com 4 rounds seria inflação para PATCH).

### Pendências e follow-ups (fora desta v1.12.1)
- ADR-012 candidato: formalizar retrospective gate como decisão arquitetural SE padrão persistir em ≥3 sessões reais. Não preemptivo.
- Eficiência measure: registrar se SE/ENTÃO rules reduzem rounds de qa-critic em próximos blocos (alvo: rule #1 elimina stale counts; rule #4 elimina polish auto-classificado).

[CONSOLIDADO] / [CONFIRMADO] após merge.

---

## [1.12.0] — 2026-05-29 — Arquitetura bicelular de QA: junções binárias forward-only + process-critic adversarial com rewind cascata (ADR-011)

> MINOR feature. Formaliza modelo de QA tácito do framework. Diagnóstico: pipeline squad (PMO → discovery → architect → developer → qa-critic → docops → release) tem **N handoffs** entre papéis, mas **gates binários explícitos só existem em J4 (qa-critic LIMPO) e J5 (validation V1-Vn PASSA)**. J0, J1, J3 eram informais; sem cláusula forward-only entre junções, oscilação era possível em teoria. Risco de loop eterno apontado pelo dono em 2026-05-28. ADR-011 codifica 6 junções binárias (J0-J5) com gates declarados, forward-only entre junções (circuit-breaker), iterações DENTRO da junção até PASS, process-critic adversarial (qa-critic em subagente isolado) ao final de cada BLOCO APROVADO com poder de **rewind cascata** a qualquer junção anterior. **TODO QA é adversarial** (hipótese default = bug). **Política SUPLANTA × EMENDA** binária para rewind.

### Added
- **`docs/adr/011-qa-bicelular-juncoes-binarias-process-critic-rewind.md`** — decisão arquitetural; 6 alternativas avaliadas (bicelular cascata escolhida; cirúrgico fica pendência v1.13.0; forward-only sem rewind rejeitado por bug-órfão; rewind-em-qualquer-junção rejeitado por loop eterno). Discovery inline 2026-05-29 (Q1-Q5 + Antecipações + Backlog + Gaps não-bloqueantes ADR-009/010).
- **`docs/specs/v1.12.0-qa-bicelular/validation.md`** — gate binário V1-V8 do release.

### Changed
- **`AGENT-FRAMEWORK.md §6` — princípio 13 NOVO:** Arquitetura bicelular de QA.
- **`.agent/workflows/handoff.md`** — seção nova com tabela operacional dos 6 gates + invariantes + bloco de declaração antes de `/handoff B`.
- **`.agent/workflows/checkpoint.md`** — esclarecimento: /checkpoint é save-point + RRC, NÃO process-critic automático; backstop opcional sob escalação.
- **`.agent/skills/qa-critic/SKILL.md`** — seção nova "Duas modalidades" (junction-critic intermediate + process-critic final com rewind).
- **`.agent/skills/pmo/SKILL.md`** — seção nova "Junção-check adversarial" (PMO aplica gate binário adversarial em J0-J3).
- **`CLAUDE.md`** + **`AGENTS.md`** — seção v1.12.0 com resumo princípio 13 + topologia.
- **`README.md`** — bump 1.11.0 → 1.12.0 + linha do princípio 13.
- **`guia/GUIA-EQUIPE.md`** — nota "Junções binárias forward-only" no fluxo squad.
- **`guia/web/index.html`** — bump versão + 1 card "QA bicelular".
- **`PROMPT-CHAT-WEB-v4.2.md`** — revisado conforme política do CHANGELOG: **não-afetado** por feature de processo interno (sem bumpar versão; arquitetura bicelular vive em workflows/skills do filesystem, fora do escopo do chat web sem filesystem).

### Como usar
- **Antes de `/handoff B`:** autor declara `junção J_n PASS` + artefato-gate + critério binário com evidência objetiva.
- **Iterações DENTRO da junção:** emendas no mesmo artefato via STATUS-field. Within-junction rounds = EMENDA (não conta como rewind).
- **Process-critic dispara em:** (a) final de cada BLOCO APROVADO — mandatório; (b) on-demand; (c) opcional em `/checkpoint` substantivo.
- **Rewind do process-critic:** cascata default. Cirúrgico fica pendência v1.13.0.
- **SUPLANTA × EMENDA pós-rewind:** §Decisão/§Alternativas → novo ADR + `Substituído por:`. §Implementação/§Consequências → emenda in-place via STATUS-field.

### Pendências e follow-ups (fora desta v1.12.0)
- **Alternativa 2 (rewind cirúrgico)** — ativável se aparecer caso onde cascata é custosa. v1.13.0 candidato.
- **Validation.md projeto × release** — templates podem convergir. Sem inflação por enquanto.

### Pipeline
PMO/Discovery (inline 2026-05-29; Q1-Q5 + Antecipações + Backlog + Gaps registrados) → Architect (ADR-011 com 6 alternativas, escolha Alternativa 1 = bicelular cascata, prevenir loop eterno via forward-only entre junções) → Developer (formalização: 2 novos + 11 edições cirúrgicas — ver tabela em ADR-011 §Implementação) → qa-critic adversarial em rounds até LIMPO.

[CONSOLIDADO] / [CONFIRMADO] (após qa-critic LIMPO + validação operacional).

---

## [1.11.0] — 2026-05-28 — Framework estritamente agnóstico de domínio + discovery declara escopo + anti-vazamento cross-projeto (ADR-010)

> MINOR feature. Diagnóstico: a v1.10.0 declarava-se "domain-agnóstico" mas o próprio `metodo-senior.md`, a memória companheira, `04-confidence-routing.md`, `discovery/SKILL.md` (banco de partida), `mapeamento-de-processo.md`, `high-stakes-gate/SKILL.md`, `AGENT-FRAMEWORK.md` §1 e o `PROMPT-CHAT-WEB-v4.2.md` (raiz) carregavam **listas hardcoded** de normas (ANP, ANVISA, FDA, BACEN, ABNT, ISO, GAMP, ALCOA+, COBIT, CSV/CSA, etc.). Sintoma observado durante a tentativa de absorção do método sênior (mesma sessão 2026-05-28): vazamento cross-projeto materializado — convenções de projetos de outros domínios do mesmo dono entravam como gatilhos do framework para qualquer projeto. A v1.11.0 PURGA esses anchors + introduz princípio 12 (framework agnóstico — discovery declara o escopo).

### Changed (PURGA — subtração em prompts/regras/templates)
- **`.agent/skills/discovery/metodo-senior.md`** — filtro de entrada agnóstico: lista "(ANP, ANVISA, FDA, BACEN, ABNT, ISO, API, GAMP, IEEE, RFC, NBR, etc.)" → "norma regulatória ou padrão técnico EXTERNO declarado pelo discovery do projeto como pertinente". ALCOA+ removido das 2 ocorrências (filtro entrada item 3 + princípio anexo "Regra de negócio tem semântica").
- **`.agent/skills/discovery/SKILL.md`** — banco de partida `regulado:` perde ALCOA+ (reframe: norma específica é declarada pelo dono).
- **`.agent/skills/discovery/mapeamento-de-processo.md`** — "Compliance/audit trail/ALCOA+" → "Compliance/audit trail (quando declarado pelo discovery — ADR-010)".
- **`.agent/rules/04-confidence-routing.md`** — desacoplamento HITL × regulado: ALCOA+ removido; HITL passa a viver inteiramente no eixo `execution-modes` (ADR-005), sem duplicação; roteamento reflexivo carrega SOB DECLARAÇÃO do discovery.
- **`_shared/high-stakes-gate/SKILL.md`** — placeholder agnóstico no "Como uma aplicação especializa este gate" (remove lista "GAMP 5 / ANVISA / SOX / LGPD / ITIL"). Gate carrega SOB DECLARAÇÃO do discovery, não por sinal semântico.
- **`AGENT-FRAMEWORK.md` §1** — "ambiente regulado" como sinal de squad → "ambiente declarado regulado pelo discovery do projeto (ADR-010)".
- **`AGENT-FRAMEWORK.md` §2.B** — "Compliance/ALCOA+" → "Compliance/audit trail" no sub-modo mapeamento de processo.
- **`PROMPT-CHAT-WEB-v4.2.md`** — §1 IDENTIDADE e §5 DOMÍNIO substituídas por **templates com placeholders** (`<PERSONALIZAR AQUI>`). Conteúdo hardcoded (Tableau · distribuição de combustíveis · farmacêutico ANVISA/GAMP/COBIT · ALCOA+ · KPIs combustíveis) **removido** — não distribuir prompt com domínio de uma pessoa cravado. Regras transversais agnósticas em §5 preservadas (Acurácia≠Performance, Agregação≠Dimensão, anti-alucinação, etc.).
- **`docs/specs/_template-process/gap-analysis.md`** — sumário executivo exemplo: ALCOA+ → "trilha de auditoria (norma específica declarada pelo discovery)".

### Added (mínimo, com critério régua §0)
- **`docs/adr/010-framework-agnostico-discovery-declara-escopo.md`** — decisão arquitetural; 6 alternativas avaliadas; relaciona ADR-005 (HITL desacoplado), ADR-007 (régua §0), ADR-009 (método sênior cuja contradição interna detectou o gap).
- **`AGENT-FRAMEWORK.md` §6 — princípio 12 NOVO:** Framework agnóstico de domínio — discovery declara o escopo (4 perguntas) + anti-vazamento cross-projeto + gaps não-bloqueantes flagados.
- **`.agent/skills/discovery/SKILL.md` — passo 6 NOVO no método universal:** lote temático obrigatório "Escopo declarado pelo discovery" com 4 perguntas estruturadas (regulado/alto-risco/regra-com-semântica/gaps-não-bloqueantes). Anti-vazamento explicitado.
- **`.agent/skills/discovery/metodo-senior.md` — seção `§ Gaps não-bloqueantes` NOVA no Output esperado:** abordagem sênior flagua, não silencia.
- **`CLAUDE.md` + `AGENTS.md` + `README.md`** — seção/menção v1.11.0; README bump de versão (1.6.1 drift → 1.11.0).

### Como usar
- **Discovery default** ganha lote temático "Escopo declarado" quando há QUALQUER sinal de contexto especializado. As 4 perguntas vão para `## Escopo declarado pelo discovery` no `requirements.md`/`research-brief.md`.
- **High-stakes-gate / reforço sênior / roteamento reflexivo** carregam SOB DECLARAÇÃO afirmativa do discovery — não por detecção semântica.
- **HITL operacional** continua governado por modo de execução (ADR-005): `default` → prompts amplos; `avançado` → blanket shell + ask em git push/merge/PR; `autosuficiente` → bypassPermissions. Eixo separado de "regulado".
- **PROMPT-CHAT-WEB:** ao plugar no Claude.ai, **customizar §1 (identidade) e §5 (domínio)** OU mover domínio para Project Knowledge (recomendado para manter o prompt genérico).

### Validação executada
- `grep -r "ALCOA\|ANVISA\|\bANP\b\|\bFDA\b\|\bBACEN\b\|GAMP" _shared/ .agent/ AGENT-FRAMEWORK.md CLAUDE.md AGENTS.md` no master pós-merge = **0 ocorrências** (excluindo CHANGELOG histórico e exemplos didáticos rotulados em `docs/specs/exemplos/H1-farma-*/` — diretório nomeado como exemplo, intenção explícita).
- Memória do agente (`~/.claude/projects/.../memory/senior-discovery-method.md`) purgada na mesma sessão (anti-vazamento estrutural).

### Pipeline
PMO/Discovery (auto-observação — princípio 11 da v1.10.0 detectou contradição interna: framework "agnóstico" carregava listas de domínio) → Architect (ADR-010, 6 alternativas, escolha Alternativa 1 = purga estrita + discovery-declara-escopo + decouplagem HITL via ADR-005) → Developer (purga + adições mínimas em 11 arquivos + ADR + companion update) → qa-critic adversarial em rounds.

### Emendas pós-feedback do dono (mesma sessão 2026-05-28, antes do qa-critic)
- **Princípio 11 honestamente reescrito** em `AGENT-FRAMEWORK.md §6`: "Auto-observação" → "Observação meta-cognitiva (captura estruturada de feedback)". Reconhece que auto-detecção do agente é falível (case AIVI: 3 violações apontadas pelo dono, não auto-observadas). Não muda capacidade — muda representação honesta. Detalhe em ADR-010 §C-1.
- **ADR-010 sub-princípio anexo ii-a NOVO** — briefing inequívoco + ubíquo = transcribe-mode determinístico. Discovery passo 6 ganha modo Transcribe (sem re-asking quando briefing tem declaração nominal explícita, sustentada em ≥2 lugares, com stakeholder nomeado, sem contradição) e modo Interview (default, 4 perguntas). Evita teatro burocrático em projetos com briefing maduro.
- **ADR-010 sub-princípio anexo ii-b NOVO** — novas skills só via discovery + gate humano régua §0. Discovery PODE surfacear candidate-skill no `## Antecipações`; dono aplica gate (a)/(b)/(c) régua §0; falha → method-audit-note (firewall). Anti-skill-sprawl com canal estruturado.
- **`docs/specs/v1.11.0-framework-agnostic/validation.md` NOVO** — gate binário V1-V7 do release (purga + versão sync + refs + substância + operacionalização + qa-critic + RRC). Backstop externo do auto-validation do agente.
- **`README.md`** linha 4 — re-purgado meta-referência ("SAP, Tableau, GCP, ALCOA+/ANP/FDA/BACEN/GAMP") detectada pelo dono como RRC-bypass viés. Versão atual: agnóstica estrita, sem siglas didáticas.

### Pendências e follow-ups (fora desta v1.11.0)
- **Templates `_template-research/research-brief.md` e `_template/requirements.md`** ganham seção `## Escopo declarado pelo discovery` no próximo ciclo.
- **Validação operacional em case real** — próximo projeto que dispare discovery declara explicitamente o escopo? Method-audit no `/checkpoint` verifica.
- **Exemplos `docs/specs/exemplos/H1-farma-*/`** ficam intencionalmente intocados — diretório rotulado como exemplo didático regulado-pharma. Quem clona entende que é exemplo, não regra do framework.
- **ADR-011 candidato (v1.12.0)** — QA bicelular (junction-critic binário forward-only + process-critic rewindable global). Em `history.md ## Em aberto`. Caso natural para dogfooding end-to-end dos princípios v1.11.0.

[CONSOLIDADO] / [CONFIRMADO] (após qa-critic LIMPO + validação em campo).

---

## [1.10.0] — 2026-05-28 — Método sênior de discovery (domain-agnóstico) + auto-observação do framework (ADR-009)

> MINOR feature: o framework absorve o método sênior validado no case real **AIVI** (2026-05-27, repo `LIMITES-BATENTES-RECALC` branch `claude/discovery-aivi-metodo-2026-05-27`, commits `74bd613`+`039fd6d`) como **reforço transversal** do discovery (carregado sob demanda quando há fonte canônica/normativa citada — domain-agnóstico) + **princípio 11** de auto-observação (method-audit autônomo). Régua §0 mantida: 2 novos + 9 edições cirúrgicas (escopo original era 2+4+1; cresceu para 2+9 pela incorporação adversarial dos rounds 1 e 2 do qa-critic — todas edições de 1-3 linhas).

### Added
- **`docs/adr/009-metodo-senior-discovery-auto-melhoria-framework.md`** — decisão arquitetural que consolida (a) método sênior em 8 passos como reforço transversal do discovery e (b) princípio 11 de auto-observação. Fonte: case AIVI; substância em memórias `[[senior-discovery-method]]`, `[[framework-self-improvement]]`, `[[framework-gaps-from-aivi-case-2026-05-27]]`.
- **`.agent/skills/discovery/metodo-senior.md`** — companion sob demanda (ADR-003) com os 8 passos auditáveis: mapeamento + **vigência** + complementações + cross-domain + pertinência + elicitação + classificação + adversarial. Output ganha seções obrigatórias **Antecipações** + **Backlog de elicitação**. Carregado quando há fonte canônica/normativa citada (qualquer domínio).

### Changed
- **`AGENT-FRAMEWORK.md` §6** — **princípio 11** novo: auto-observação do framework. Cada checkpoint emite 0-3 `method-audit notes`; padrão recorrente vira ADR.
- **`.agent/skills/discovery/SKILL.md`** — bump versão `1.7.0` → `1.8.0`; +1 seção "Reforço transversal sênior" após a tabela de sub-modos, apontando para o companion.
- **`_shared/anti-hallucination/SKILL.md`** — +1 anti-pattern: "Citar norma/regulamento/spec/padrão externo sem checar **vigência**". SSoT do validity-check.
- **`.agent/workflows/checkpoint.md`** — +1 seção **Method-Audit autônomo (ADR-009)**: PMO emite 0-3 notes em sessão substantiva. Sinais: norma sem vigência, regra despriorizada sem semântica, correções repetidas do dono, violação régua §0, loops/retrabalho. Firewall preservado.
- **`docs/specs/_template-research/research-brief.md`** — passa de 8 para 10 seções: novas **§7 Antecipações** e **§8 Backlog de elicitação** (obrigatórias quando o reforço transversal sênior está ativo); §7 antiga (Recomendação) → §9; §8 antiga (Metadados) → §10.
- **`.agent/skills/discovery/pesquisa-cascata.md`** — +1 bullet no Output obrigatório explicitando que §7 Antecipações + §8 Backlog são obrigatórias quando o reforço sênior está ativo em paralelo (evita omissão silenciosa).
- **`CLAUDE.md`** + **`AGENTS.md`** — nova seção "Método sênior de discovery — reforço transversal (v1.10.0 — ADR-009)".

### Como usar
- **Acionar reforço sênior:** sempre que houver fonte canônica/normativa citada (norma, spec, padrão, regra de negócio com peso semântico) → discovery carrega `metodo-senior.md` em adição ao sub-modo ativo. Aplica os 8 passos; output ganha **Antecipações** + **Backlog**.
- **Method-audit autônomo:** ao rodar `/checkpoint` em sessão substantiva (≥10 turnos ou ambiente regulado), o PMO observa próprias falhas e emite 0-3 notes em `## Aprendizado`. Padrão recorrente (≥3) ou gap isolado high-signal → propor ADR.

### Pendências e follow-ups (do case AIVI, não bloqueantes)
- High-stakes-gate auto-load por gatilhos contextuais — próximo ciclo.
- Antecipações no template padrão de `output-format` — propagar do companion.
- External research handle no discovery pesquisa-cascata (WebSearch/WebFetch) — item J do audit AIVI.
- Detector de drift hook deployado-vs-versionado (framework-boot.ps1 órfão) — item I do audit AIVI.
- **AIVI fechamento** (validar a esteira completa): implementar REQ-001..007 + qa-critic + run CSV 2026 + CA-1..6. Fora deste repo, branch `claude/discovery-aivi-metodo-2026-05-27`.

## [1.9.0] — 2026-05-27 — Régua §0 GANHO LÍQUIDO + Discovery sub-modo pesquisa-cascata (G1) + aprendizado e WIP por extensão (ADR-007)

> MINOR feature: aplica o intake do plano de otimização (`docs/_intake/2026-05-27-plano-otimizacao-framework.md`) ao framework. **Régua §0** entra como princípio 10 do `AGENT-FRAMEWORK.md` §6: adição pura é rejeitada por padrão. **G1 pesquisa-cascata** vira sub-modo do discovery (companion sob demanda, ADR-003) — pipeline 9 passos com ataque anti-raso obrigatório. **Aprendizado de fracassos** (ex-G9) e **WIP/nada esquecido** (ex-G11) atendidos por **extensão** (não subsistema novo): `/checkpoint` + `history.md` + release checklist + `start-session`.

### Added
- **`.agent/skills/discovery/pesquisa-cascata.md`** — companion sob demanda do discovery (G1). Algoritmo: filtro de entrada → decompor (3-5 sub-perguntas multi-hop) → buscar via explorer (paralelo) → refletir → ramificar (≤2 rodadas) → sintetizar → **ataque anti-raso obrigatório (R3)** → refinar com critério binário → handoff. Falha do explorer registra `[DESCONHECIDO]` sem repetir sub-pergunta.
- **`docs/specs/_template-research/research-brief.md`** — template do artefato de saída (cabeçalho YAML + 8 seções: pergunta principal, decomposição, fontes, achados classificados, gaps, ataque anti-raso, recomendação, metadados).
- **`history.md`** (raiz) — arquivo formalizado (já era referenciado pelo `AGENT-FRAMEWORK.md` §2.B sequência de squad). 3 seções: histórico cronológico + `## Em aberto` (WIP) + `## Aprendizado` (fracassos com firewall).

### Changed
- **`AGENT-FRAMEWORK.md` §6** — princípio 10 novo: **Otimização líquida (GANHO LÍQUIDO)**. Adição só passa se (a) funde/remove ≥ adiciona, (b) reduz tokens/latência, ou (c) destrava eval inalcançável editando existente. Detalhe: ADR-007.
- **`.agent/skills/discovery/SKILL.md`** — bump versão `1.6.0` → `1.7.0`; +1 linha na tabela de sub-modos apontando para `pesquisa-cascata.md`.
- **`.agent/workflows/checkpoint.md`** — seção **Aprendizado** (ex-G9): gatilhos de fracasso disparam append em `history.md` `## Aprendizado`. **Firewall**: notas são inertes; só viram comportamento via skill/regra destilada, aprovada via ADR e mergeada.
- **`.agent/workflows/start-session.md`** — passo 2 novo: reconciliar `## Em aberto` do history.md com branches git e ADRs `Proposto` (modo squad apenas). **WIP-limit**: finalizar antes de iniciar; STATUS > 4 linhas → refatorar.
- **`guia/GIT-VERSIONAMENTO.md`** — +1 linha no checklist de release: revisar `## Aprendizado` do history.md; padrão recorrente (≥3) → propor ADR.
- **`CLAUDE.md`** + **`AGENTS.md`** — nota da Régua §0 e do sub-modo pesquisa-cascata.

### Como usar
- **Acionar pesquisa-cascata:** quando o trabalho exige pesquisa antes da spec E não há fonte canônica no contexto E a resposta destrava decisão → `discovery` carrega o companion sob demanda.
- **Registrar aprendizado:** ao rodar `/checkpoint`, se gatilho de fracasso (anti-loop, qa-critic ≥2× reprovou, file-first violado, etc.) → anotar em `history.md` `## Aprendizado` com timestamp.
- **Manter WIP visível:** em modo squad, `/start-session` reconcilia `## Em aberto` + branches + ADRs Proposto. Item só muda de status com razão registrada.
- **Aplicar a régua §0:** antes de criar arquivo/skill/regra, perguntar "o que dá para remover, fundir ou simplificar?". Adição só passa por (a)/(b)/(c).

### Pipeline
PMO (intake colado pelo mantenedor) → Architect (ADR-007 com 6 alternativas, escolha Alternativa 1) → qa-critic adversarial do ADR em subagente isolado, 3 rounds:
- Round 1: APROVADO_COM_RESSALVAS (2 médias + 3 baixas + 3 adversariais) → incorporadas
- Round 2: APROVADO_COM_RESSALVAS (1 cosmética) → incorporada
- Round 3: **APROVADO LIMPO** → ADR Aceito
→ Developer (4 blocos serializados: §6 + companion + template + checkpoint/start-session/history.md + CHANGELOG/CLAUDE/AGENTS/GIT) → qa-critic adversarial do código, 2 rounds:
- Round 1: APROVADO_COM_RESSALVAS (1 média + 2 baixas + 3 adversariais; 2 adversariais arquiteturais aceitos como backlog FASE C) → 3 corrigíveis incorporadas
- Round 2: **APROVADO LIMPO**
→ DocOps → PR + merge no modo `autosuficiente`.

[CONSOLIDADO] / [CONFIRMADO] (após validação operacional em campo).

---

## [1.8.0] — 2026-05-27 — Auto-boot global do squad com allowlist de owners (ADR-006)

> MINOR feature: promove o auto-boot do squad para `~/.claude/settings.json`
> global com ativação condicional. Em qualquer IDE/projeto cujo owner do
> remote `origin` bata com `~/.claude/squad-owners.txt` (substring match
> case-insensitive), o squad acorda sozinho — sem precisar pedir "aplique
> o framework" manualmente. Fallback para marker explícito (`AGENTS.md` ou
> `.agent/`) em repos sem remote ou em colaboração ativa com terceiros.
> Locks (`.claude/session.lock` por projeto, `~/.claude/session.lock` global)
> pulam por sessão única. Reusa infra `~/.claude/hooks/` já criada na v1.7.1.

### Added
- `.claude/hooks/inject-start-session-global.template.ps1` — fonte versionada
  do hook global. Algoritmo: CWD → locks → extrair owner do remote (regex
  HTTPS + SSH) → substring match em `squad-owners.txt` → fallback marker
  (`AGENTS.md`/`.agent/`) → injeta `additionalContext` lendo
  `~/.claude/workflows/start-session.md` + `statusMessage` formato
  `owner=<completo> match=<token>` para diagnóstico de falso positivo
  (qa-critic round 1 ADR-006, C6). Falha soft.
- `~/.claude/squad-owners.txt` (criado por bootstrap, não versionado) —
  allowlist com 7 tokens default: `fpsouza`, `fpsouz`, `fsouza`,
  `fabriciosouza`, `fabriciopsouza`, `vibraenergia`, `natulab`.
- `~/.claude/workflows/` (criado pelo sync-global) — espelhamento de
  `.agent/workflows/` para o hook global ler `start-session.md`.

### Changed
- `.claude/hooks/sync-global.ps1` — agora também copia
  `inject-start-session-global.template.ps1` → `~/.claude/hooks/inject-start-session-global.ps1`
  e `.agent/workflows/*` → `~/.claude/workflows/*`. `systemMessage` final
  ganha contador `workflows`.
- `bootstrap.ps1` — passo 7 novo: cria `squad-owners.txt` (preserva customização
  se já existe), faz merge não-destrutivo de `hooks.SessionStart` em
  `~/.claude/settings.json` (backup `.modeswap.bak`-style; rollback automático
  se JSON ficar inválido), roda sync inicial.
- `bootstrap.sh` — passo 7 paridade subset: cria `squad-owners.txt`; avisa
  que hooks PowerShell ficam inativos em Linux/macOS até porte cross-platform.
- `CLAUDE.md` + `AGENTS.md` — seção curta "Auto-boot global" com critérios
  de ativação e ponteiro para `~/.claude/squad-owners.txt`.
- `docs/adr/006-auto-boot-global-squad-allowlist-owners.md` — status mudou
  para `Aceito (2026-05-27)`.

### Como usar
- **Repos do mantenedor** (`github.com/fabriciopsouza/foo`, etc.): squad ativa
  automaticamente após `bootstrap.ps1` rodar uma vez por PC.
- **Repo de terceiro com colaboração ativa**: `New-Item AGENTS.md` na raiz
  local → próximas sessões ativam.
- **Pular sessão única**: `New-Item .claude/session.lock` (projeto) ou
  `~/.claude/session.lock` (global).
- **Customizar allowlist**: editar `~/.claude/squad-owners.txt`.
- **Diagnóstico** ("por que não ativou?"): olhar `statusMessage` na barra de
  status — formato `owner=<completo> match=<token>` ou `skipped (<motivo>)`.

### Migração de PC com v1.7.1 já instalado
Quem já tem v1.7.1 ativa não rodou `bootstrap.ps1` recentemente — o auto-boot global não aparece sozinho. Passos manuais (idempotentes):
```powershell
cd <caminho-para-o-repo>
git pull --ff-only
pwsh ./bootstrap.ps1        # roda apenas o passo 6 efetivamente (resto detecta "já existe")
```
O passo 6 do bootstrap cria `~/.claude/squad-owners.txt` (preserva customização se já existe) e faz merge não-destrutivo de `hooks.SessionStart` em `~/.claude/settings.json` com backup `.modeswap.bak`. Idempotente: rodar 2× não duplica nada.

### Pipeline
PMO/Discovery (sessão "retome adr005" 2026-05-27) → Architect (ADR-006
revisto pós-v1.7.1, escopo enxuto: gap do ADR-005 já resolvido) → qa-critic
round 1 do ADR (4 ressalvas: C5 USERPROFILE, C6 statusMessage formato,
C8 divergência hook global×project-level, adversarial extra pré-requisito
test plan — todas incorporadas no próprio ADR) → mantenedor aprovou ADR
("o que aprovamos para adr06, sem inflar, sem piorar") → Developer (esta
implementação) → qa-critic adversarial em rounds até APROVADO LIMPO →
DocOps → PR + merge no modo `autosuficiente`.

[CONSOLIDADO] / [CONFIRMADO] · validação operacional em campo pós-merge.

---

## [1.7.1] — 2026-05-27 — Fix do gap do ADR-005 — espelhar sync-global como framework-sync.ps1

> PATCH operacional: o `check-execution-mode.ps1` da v1.7.0 monitora SHA-256 de
> `~/.claude/hooks/framework-sync.ps1`, mas nada na v1.7.0 cria esse arquivo —
> nem o `sync-global.ps1` (que só espelhava skills/agents), nem o bootstrap.
> Resultado observado: gate de modos de execução **dormente desde a v1.7.0**
> (hook cai sempre no branch `Test-Path = false` → exit silencioso → nenhuma
> ativação dispara). Auditoria 2026-05-27 (sessão "retome adr005"): em PC
> ativo do mantenedor, `~/.claude/hooks/` sequer existe; `framework-mode.json`
> ausente; nenhum modo foi ativado em campo desde o merge da v1.7.0.

### Fixed
- `.claude/hooks/sync-global.ps1` — cria `~/.claude/hooks/` e espelha a si mesmo
  como `~/.claude/hooks/framework-sync.ps1` (rolling overwrite via `Copy-Item -Force`).
  Nome diferente é deliberado: `sync-global.ps1` é o **fonte** (project-level);
  `framework-sync.ps1` é a **instância instalada** (global-level). Par fonte/binário,
  não rename. Resolução do path do próprio script usa cadeia robusta
  `$PSCommandPath → $MyInvocation.MyCommand.Path → $null` (também aplicada ao
  `$projectRoot` por consistência); guard `if ($projectRoot)` evita falha
  terminante no `Join-Path` quando ambos são nulos (iex/dot-source). Contador
  `$hookCount` na `systemMessage` final.

### Validação manual
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .claude\hooks\sync-global.ps1
Test-Path ~/.claude/hooks/framework-sync.ps1   # → True
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .claude\hooks\check-execution-mode.ps1
# → JSON com additionalContext motivo INITIAL (após estado limpo); silencioso após ativação.
```

### Limitações conhecidas
- ACL ruim em `~/.claude/hooks/` → `hookCount=0`; sessão não bloqueia; diagnosticar com `New-Item` manual.
- Diagnóstico via cópia instalada copia self sobre self (Windows trunca+recópia; sem efeito).

### Pipeline
PMO (auditoria casual detectou gap) → Developer (commit `2fb46d8`) →
qa-critic 3 rounds adversariais em subagente isolado: round 1
(`APROVADO_COM_RESSALVAS`: 1 médio + 2 baixos + 1 adversarial) → incorporado
(`7e63023`) → round 2 (`APROVADO_COM_RESSALVAS`: 1 médio derivado, consistência
`$projectRoot`) → incorporado (`96b2a81`) → round 3 (**`APROVADO LIMPO`**) →
algoritmo `execution-modes` 8 passos: modo `avancado` ativado em campo
2026-05-27T00:42-03:00; gate agora silencioso → DocOps (`d106a0f`).

[CONSOLIDADO] / [CONFIRMADO] · validado em campo (2026-05-27).

---

## [1.7.0] — 2026-05-26 — Modos de execução com ratchet por hash de hook (ADR-005)

> MINOR feature: framework passa a operar sob 1 de 3 níveis explícitos
> (`default` / `avançado` / `autosuficiente`) registrados em
> `~/.claude/framework-mode.json`. Templates declarativos em
> `_shared/execution-modes/`. Reativação dispara SÓ quando o estado é ausente
> OU o SHA-256 de `~/.claude/hooks/framework-sync.ps1` muda — em sessões
> normais o hook é silencioso. Ratchet forward-only no fluxo normal
> (escalação livre default→avançado→autosuficiente); downgrade apenas via
> edição manual do state file. Resolve a falta de estado explícito sobre o
> regime de confiança em vigor, evita downgrade silencioso, e conecta a
> revisão de permissões ao update da automação de sync.

### Added
- `_shared/execution-modes/SKILL.md` — núcleo SSoT dos 3 modos: descrição, ratchet, formato do state file, algoritmo de aplicação (merge ao settings.json global), relações com `traceability` e `high-stakes-gate`.
- `_shared/execution-modes/default.json` — template do modo conservador: `defaultMode: default`, allow só de Read/Edit/Write, ask em git push/merge/pr, deny destrutivo robusto (20 regras: rm variantes, git push force, git reset hard, PowerShell Remove-Item/rm/rmdir/del/erase/ri/Clear-Content).
- `_shared/execution-modes/avancado.json` — template do modo avançado: + bare `Bash`/`PowerShell` em allow; mesmo ask + deny do default.
- `_shared/execution-modes/autosuficiente.json` — template do modo autosuficiente: `defaultMode: bypassPermissions`, allow blanket, deny mínimo de guard-rails absolutos (push --force, mkfs, dd if=, Format-Volume, Clear-Disk, Initialize-Disk, Remove-Partition).
- `.claude/hooks/check-execution-mode.ps1` — hook SessionStart que computa SHA-256 do `~/.claude/hooks/framework-sync.ps1`, lê `~/.claude/framework-mode.json`, e emite `additionalContext` pedindo ativação se estado ausente (INITIAL) ou hash mudou (HOOK_CHANGED). Silencioso nos demais casos. Falha "soft" com warning em stderr + exit 0.
### Changed
- `.claude/settings.json` — **restruturado** de 1 grupo SessionStart com 2 hooks (v1.6.1) para **3 grupos paralelos** com 1 hook cada (`sync-global.ps1` → `check-execution-mode.ps1` → `inject-start-session.ps1`). Motivo: dentro do mesmo grupo, hooks sequenciais que emitem `hookSpecificOutput.additionalContext` podem disputar a chave (último-ganha); grupos separados preservam isolamento de contexto. Achado do qa-critic round 1 (B1).

### Added (continuação)
- `docs/adr/005-niveis-de-execucao-framework.md` — ADR formal. 6 alternativas avaliadas (hash de wrapper local vencedora; HEAD do repo rejeitado por fricção). Ponteiro = branch+data+grep.
- `CLAUDE.md` (raiz) e `AGENTS.md` — seção curta "Modos de execução" com ponteiro para a skill.

### Como usar
- **Primeira instalação** (state ausente): próxima sessão recebe `additionalContext` pedindo escolha entre os 3 modos.
- **Update do framework que altera `framework-sync.ps1`:** próxima sessão pede reconfirmação (motivo `HOOK_CHANGED`).
- **Sessões normais:** zero fricção — hook silencioso.
- **Downgrade emergencial:** editar `~/.claude/framework-mode.json` à mão. Não normalizado.

### Pipeline
PMO (recebe pedido "incorpore como segundo nível de execução") → Architect (ADR-005, 6 alternativas, escolha hash-local + ratchet + escape manual após elicitação em 4 dimensões com mantenedor) → Developer (ADR + 3 templates + SKILL + hook + settings + CLAUDE/AGENTS/CHANGELOG; pipe-test do hook validou caminho INITIAL: JSON correto, SHA calculado, exit 0; caminho silent inferido por simetria). qa-critic round adversarial pendente.

[CONSOLIDADO] / [CONFIRMADO].

---

## [1.6.1] — 2026-05-26 — Auto-boot do squad via SessionStart hook (ADR-004)

> PATCH operacional: `/start-session` deixa de depender de memória humana. Um
> 2º hook SessionStart, paralelo ao `sync-global.ps1` existente, injeta a
> orientação de boot do squad no contexto inicial — Claude entra com PMO ativo
> por default. Flag de escape `.claude/session.lock` permite sessão rápida
> (debug, pergunta pontual) sob controle manual. Resolve a discrepância
> arquitetural detectada pelo mantenedor: sync mecânico já era automático;
> boot cognitivo continuava dependendo de o usuário lembrar do comando.

### Added
- `.claude/hooks/inject-start-session.ps1` — script PowerShell que injeta `additionalContext` (conteúdo de `.agent/workflows/start-session.md`) via `hookSpecificOutput` JSON. Detecta `.claude/session.lock` e pula injeção quando presente.
- `.claude/settings.json` — 2º hook SessionStart registrado em paralelo ao `sync-global.ps1`, com `statusMessage` que mostra a instrução de escape ao usuário.
- `.gitignore` — `.claude/session.lock` adicionado (flag é pessoal por cópia de trabalho, não versionada).
- `docs/adr/004-auto-start-session-com-escape.md` — ADR formal. Ponteiro = branch+data+grep.

### Como usar
- **Default** (sem lock): toda sessão entra com PMO ativo; Claude produz STATUS no 1º turno automaticamente.
- **Pular o auto-boot:** `New-Item .claude/session.lock -ItemType File -Force` → sessões subsequentes pulam o boot até o lock ser deletado.
- **Reativar:** `Remove-Item .claude/session.lock`.

### Pipeline
PMO/Discovery (elicitação da pergunta "preciso dar /start-session?") → Architect (ADR-004, 5 alternativas, escolha Opção C) → Developer (script + settings + .gitignore + CHANGELOG). qa-critic não rodou neste PATCH — feature pequena, validação manual via abrir sessão nova com e sem lock.

[CONSOLIDADO] / [CONFIRMADO].

---

## [1.6.0] — 2026-05-25 — `discovery` ganha sub-modo "mapeamento de processo" (ADR-002) + 4 saneamentos adjacentes + progressive disclosure via companion files (ADR-003)

> Estende o papel `discovery` (v1.5.0) com uma capacidade BPM-sênior para
> processo de negócio. Critério de aceite: 12 itens binários, validação via
> gabarito em `docs/specs/discovery-process-mapping/validation.md`. Em paralelo,
> 4 saneamentos adjacentes detectados na revisão adversarial entram no mesmo
> ciclo (correção de drift de versão da skill, atualização proativa do template
> ADR, harmonização ergonômica do sub-modo "revisar projeto existente",
> criação do `validation.md` companion da spec). Após qa-critic round 2 (PASS)
> + revisão arquitetural questionando o tamanho monolítico (190 linhas vs
> média 37), aplicado **progressive disclosure**: SKILL.md reduzida a 100 linhas
> + 2 companion files (`mapeamento-de-processo.md`, `revisar-projeto-existente.md`)
> carregados sob demanda. Coerente com Bloco 2.5 do framework (context engineering).

### Added — progressive disclosure via companion files (ADR-003)
- `.agent/skills/discovery/SKILL.md` reduzida de 190 → **100 linhas** (entry point: princípio · método universal · banco de partida · tabela de apontadores para sub-modos · output obrigatório · fronteiras).
- `.agent/skills/discovery/mapeamento-de-processo.md` (~97 linhas) — companion novo do sub-modo BPM (filtro de entrada, profundidade, notação plugável, formalidade, matriz de 13 dimensões, output em 3 arquivos, integração com explorer, validação A4). Carregado sob demanda.
- `.agent/skills/discovery/revisar-projeto-existente.md` (~20 linhas) — companion extraído do sub-modo v1.5.0 (filtro de entrada + 3 passos preservados). Carregado sob demanda.
- `.claude/hooks/sync-global.ps1` — header atualizado documentando suporte automático a companion files (já existia via `Copy-Item -Recurse`; agora declarado).
- **Ganho operacional:** modo universal puro (caso mais comum) carrega 100 linhas em vez de 190 (−47% context budget). Manutenção isolada por sub-modo.
- **Regra de aplicação futura:** ADR-003 define gatilhos para outras skills adotarem o padrão (>80 linhas OU 2+ sub-modos identificáveis).

### Added — sub-modo "mapeamento de processo"
- Conteúdo movido para `.agent/skills/discovery/mapeamento-de-processo.md` (companion file). Inclui:
  - **Filtro de entrada** rejeitando 4 falsos positivos: jornada UI · runbook técnico · algoritmo de código · workflow de tool de aprovação.
  - **3 níveis de profundidade configuráveis:** `quick` (SIPOC + macro), `standard` (default, macro + sub-processo), `deep` (atividade granular).
  - **Notação plugável:** markdown-só / +Mermaid flow/sequence / +Mermaid swimlane/BPMN-lite / plug livre.
  - **Formalidade configurável:** pragmático/lean · sênior BA prático · BPMN 2.0 estrito · per case.
  - **Matriz de 13 dimensões:** 4 MUST (Trigger+Output, Owner+RACI, SIPOC por atividade, Rules+Exceptions+Handoffs) modulada por profundidade; 4 MAY (métricas operacionais, mapa tecnológico, variações, lean/maturity); 1 condicional as-is-only (pain points/bottlenecks); 4 anti-raso BPM (VoC/CTQ, Boundaries, Declarativo×Observacional, Validação stakeholders).
  - **Output em 3 arquivos** lado a lado: `requirements.md` + `process-map-as-is.md` + `gap-analysis.md`. Cabeçalho YAML obrigatório em cada quando persona=subagente-automatizado (NF1 garantida sem cancelar plugabilidade — gap #1 da revisão adversarial).
  - **Integração com explorer (EARS-W5):** quando processo está em código (BPMS, n8n, Airflow), discovery + explorer rodam em paralelo — sequência rápida em single-thread, subagentes reais em persona-4 pipeline. Discovery consolida o cruzamento em `gap-analysis.md` (anti-padrão #1 do BPM tratado como built-in).
  - **Escalação automática (EARS-I5):** persona-4 sem stakeholder → bloco `[BLOQUEADOR: validação humana pendente]` + exit-code não-zero.
- `docs/specs/_template-process/` — novo template (3 arquivos com cabeçalho YAML e seções nomeadas).
- `docs/specs/exemplos/H1-farma-liberacao-de-lote/` — exemplo trabalhado de cabo a rabo (cenário regulado: RACI QC/QA/Produção, 6+ tags `[DECLARADO]`/`[OBSERVADO]`, 5 gaps detectados, compliance OUT delegado ao `high-stakes-gate`).

### Added — saneamentos adjacentes (oportunidades incorporadas pós-revisão adversarial)
- **Versão da skill harmonizada (oportunidade O1):** frontmatter de `.agent/skills/discovery/SKILL.md` corrigido `1.0.0` → `1.5.0` → `1.6.0` (drift detectado pelo explorer).
- **Template ADR atualizado (oportunidade O2):** `docs/adr/000-template.md` seção "Implementação" agora instrui `Ponteiro: branch + data + grep` como padrão, com hash apenas como complemento opcional — codifica a lição do ADR-001 (hash é frágil a rewrites).
- **Sub-modos harmonizados (oportunidade O3):** sub-modo "revisar projeto existente" (v1.5.0) ganha cabeçalho `### Filtro de entrada` simétrico ao do novo sub-modo. Comportamento downstream preservado.
- **validation.md companion (oportunidade O4):** `docs/specs/discovery-process-mapping/validation.md` com gabarito de validação binária dos 12 itens do critério de aceite + 13 gaps fechados + 4 anti-raso BPM + 4 invioláveis preservados. Cinco blocos com reprovação binária para `qa-critic`.

### Changed — sweep do banco de partida (mudança subtrativa registrada em ADR-002 D2)
- `.agent/skills/discovery/SKILL.md` linha `BA/processo` no banco de partida:
  - **Antes:** `as-is × to-be, donos do processo, regras de negócio, exceções, indicadores de sucesso, mudança organizacional.`
  - **Depois:** `processo de negócio/BPM → usar sub-modo "mapeamento de processo" (ver seção dedicada abaixo).`
  - Os 6 termos não desapareceram — foram relocados, expandidos e refinados dentro do sub-modo dedicado.

### Added — ADR e governança
- `docs/adr/002-discovery-process-mapping-v160.md` — ADR formal cobrindo **7 sub-decisões** (D1-D7): encaixe sub-modo · sweep BA/processo · harmonização revisar · bump versão skill · template ADR atualizado · handoff 3 arquivos · protocolo discovery+explorer. Ponteiro = branch + data + grep (NÃO hash de commit).
- `_meta/eval-results-papeis.md` ganha seções **H + H'** com 18 casos (9 should-trigger + 9 should-NOT) marcados `[EMERGENTE — DESIGN-TIME, NÃO EXECUTADO]`, paridade direta com G+G' de v1.5.0.

### Spec e revisão adversarial
- `docs/specs/discovery-process-mapping/requirements.md` — spec sênior (auto-elicitação meta) com 13 gaps fechados pós-revisão adversarial (`qa-critic` + `explorer` rodaram em paralelo): 3 BLOQUEADORES + 6 MÉDIOS + 3 MENORES + NF7 enganoso. Critério de aceite expandido de 8 → 12 itens com seções nomeadas verificáveis por grep.

### Pipeline
PMO/Discovery → Discovery (auto-elicitação meta, 4 lotes temáticos) → revisão adversarial (qa-critic + explorer em paralelo) → Discovery (13 gaps fechados + 4 oportunidades incorporadas) → Architect (ADR-002 com 7 sub-decisões) → Developer (12 itens implementados) → QA-Critic (validation.md) → DocOps. Merge bloqueado por gate humano.

[CONSOLIDADO] / [CONFIRMADO].

---

## [1.5.0] — 2026-05-24 — Papel `discovery` + molde de subagente ocultado (ADR-001)

> Adiciona um papel genérico que faltava entre PMO e architect: a elicitação
> profunda. PMO faz UMA pergunta e segue; `discovery` mergulha — combate a
> *spec rasa* (limitada ao que o usuário já sabe pedir). Genérico e agnóstico
> de domínio. Em paralelo, o molde de subagente sai da lista `/agents` via
> renomeação consciente (ADR-001), respeitando a regra anti-rename.

### Added — papel `discovery`
- `.agent/skills/discovery/SKILL.md` — **elicitação profunda universal**.
  Método por dimensões de spec (objetivo, stakeholders, funcional, não-funcional,
  dados, restrições, aceite, edge cases, fora de escopo); perguntas em
  **lotes temáticos** (não 1 a 1, não 50 de uma vez); etapa **anti-raso
  obrigatória** ("o que um sênior NESTE campo levantaria que ainda não
  cobrimos?") antes de fechar. Anti-alucinação: o que o usuário não souber
  vira `[DESCONHECIDO]` explícito no requirements — nunca chute disfarçado.
  Fonte: pedido do usuário + fundamentos A0 (decomposição) + A2 (spec-driven).
  [CONSOLIDADO] / [CONFIRMADO].
- **Banco de partida editável** (acelerador, NUNCA gaiola): conjuntos-semente
  para dev/software, BI/analytics, BA/processo, web/produto, dados/ETL,
  regulado. Estender à vontade; se o assunto for novo, gerar pelas dimensões
  universais. A ausência de trilha não impede o discovery.
- **Modo "revisar projeto existente"** dentro de `discovery` (um caso de uso,
  não outro papel): delega a varredura ao subagente `explorer` (read-only) e
  **exige baseline golden** antes de mexer em lógica. Critério de aceite =
  "comportamento idêntico ao golden + critérios de limpeza atingidos".

### Fronteiras do `discovery` (registradas para não colidir com papéis adjacentes)
- NÃO implementa (developer) · NÃO decide arquitetura (architect) · NÃO audita
  código por conta própria (delega ao explorer). Entrega `requirements.md` de
  nível sênior, com cada requisito classificado, que alimenta `feature-plan` /
  `architect`. Encerra quando o requirements tem critério de aceite binário e
  as lacunas `[DESCONHECIDO]` estão explícitas.

### Changed — molde de subagente ocultado (ADR-001)
- `.claude/agents/_template.md` renomeado para `.claude/agents/_template.md.txt`
  para que o Claude Code não o liste em `/agents` como subagente ativável (a
  extensão `.md` válida na pasta o registrava como "<nome-do-subagente>",
  poluindo a lista e arriscando invocação por engano). Conteúdo preservado e
  versionado. Decisão e alternativas em `docs/adr/001-ocultar-template-agente.md`.
  **Regra anti-rename** (`_shared/traceability`) respeitada via ADR formal.
  Fonte: auto-auditoria do `explorer` (sinal anterior: `name: _template-application`
  × pasta `_template`). [CONSOLIDADO] / [CONFIRMADO].
- `guia/SETUP.md` — referência ao molde atualizada para `_template.md.txt`
  (sweep de órfãs após o rename, exigência da regra anti-rename).

### Added — integração do `discovery` no resto do núcleo (qa-critic v1.5.0 ressalvas #2 e #3)
- `README.md` — papel `discovery` incluído na tabela de camadas (campo PROCESSO).
- `AGENT-FRAMEWORK.md` — nova subseção "Gatilho do `discovery`" sob §2.B Modo
  Squad, formalizando a fronteira PMO (UMA pergunta) → discovery (mergulha em
  spec rasa) → architect (decide). Sem isso o papel ficaria invisível para quem
  segue só o roteador.

### Added — eval-set do `discovery` (qa-critic v1.5.0 ressalva #1)
- `_meta/eval-results-papeis.md` — seção G (9 should-trigger) + G' (9 should-NOT)
  para o papel `discovery`. Marcado **[EMERGENTE — DESIGN-TIME, NÃO EXECUTADO]**
  conforme `anti-hallucination`: casos escritos e revisados, execução real é
  pendência registrada para o próximo ciclo de release. Header e tabela de
  resultado final atualizados para distinguir 6 papéis EXECUTADOS (A–F) de 1
  EMERGENTE (G). [EMERGENTE] / [CONFIRMADO].

### Added — auto-sync repo → `~/.claude/` global (fecha pendência do ADR-001)
- `.claude/hooks/sync-global.ps1` — script PowerShell idempotente que espelha
  `_shared/`, `.agent/skills/` e `.claude/agents/*.md` (NÃO `*.md.txt`) do
  working tree do repo para `~/.claude/skills/` e `~/.claude/agents/` (instalação
  global usada por todas as outras sessões/projetos). Self-healing
  (`Remove-Item` antes de `Copy-Item` para evitar aninhamento). Falha "soft":
  warning no stderr + `exit 0` (nunca bloqueia sessão).
- `.claude/settings.json` — hook `SessionStart` que invoca o script a cada
  abertura de sessão neste projeto. Project-level (commitado, não personal):
  funciona para qualquer dev em Windows que clonar o repo, sem hardcodar
  caminho (usa `$env:USERPROFILE`).
- Resolve a pendência registrada no ADR-001 ("instalação GLOBAL é cópia
  separada — sem owner/prazo") nascida da auto-auditoria do `explorer`.
  Owner agora = este hook. Mesmo critério de exclusão do `_template.md.txt`
  vale no global (não vaza pra `/agents` em outros projetos).
- Pipe-test capturou 2 bugs antes do deploy: (1) `Split-Path` com nível
  errado fez `projectRoot` apontar pra `.claude/` em vez do repo
  (sync silencioso de 0 skills); (2) `Copy-Item -Recurse` em destino
  existente aninhava `<name>/<name>/SKILL.md`. Ambos corrigidos no script
  publicado. [CONSOLIDADO] / [CONFIRMADO].

### Changed — system version
- Versão do sistema: 1.4.0 → 1.5.0 (feature nova compatível = MINOR, conforme
  política registrada em `## Política`).

### Pipeline auditável desta entrega
- PMO orquestra → developer aplica BLOCO C + rename do `_template` →
  `qa-critic` (subagente adversarial, contexto fresh) **round 1**: C1–C6 todos
  V; C7 (adversarial extra) achou **3 itens principais** (#1 BLOQUEADOR: eval-set
  ausente para discovery — viola política do próprio framework; #2 MÉDIO:
  discovery não listado em `README.md:11`; #3 MÉDIO: gatilho de discovery
  ausente em `AGENT-FRAMEWORK.md`) **+ 3 ressalvas menores** acionáveis fora
  deste PR (global install `~/.claude/agents/` espelhado / monitorar pattern
  `.md.txt` / zona cinzenta PMO×discovery) → user decidiu `resolver #1+#2+#3
  neste PR` → developer aplicou os fixes → **round 2 do qa-critic**:
  aprovado_com_ressalvas (2 BAIXA, ambas incorporadas neste commit:
  reconciliação desta narrativa de pipeline + reescrita do caso G'#12 do
  eval-set para teste isolado) → docops (esta entrada). Merge **bloqueado**:
  gate humano.

## [1.0.0] — 2026-05-23 — Consolidação dos Blocos 1–5

### Bloco 1 — Núcleo `_shared/` (fonte única)
- **Added** 6 skills de núcleo desduplicadas dos 3 documentos existentes.
  Fonte: A2 (SSoT por arquivo) + princípio já declarado em v2.2 §6.6 / SQUAD Seção 1.
  [CONSOLIDADO] / [CONFIRMADO].
- **Changed** regras transversais: de triplicadas → referência única.
- **Preservado** conteúdo idêntico às fontes (rótulos, prefixos, categorias).

### Bloco 2 — Roteador Metacognição v2.2 → v2.3
- **Added** §2.5 Context Engineering nomeada (attention budget, compaction,
  structured note-taking, tool-result clearing, isolamento). Fonte: A0. [CONSOLIDADO].
- **Changed** precedência/anti-loop/5 etapas/checkpoint → referência a `_shared/`.
- **Changed** versão 2.2→2.3; nota de carregamento IDE vs chat web.

### Bloco 3 — Squad v1.1 → v1.2
- **Added** spec atômica (`docs/specs/_template/requirements.md` + `validation.md`,
  gate binário). Fonte: A2. [CONSOLIDADO].
- **Added** `_meta/subagent-isolation.md` (contexto fresh, menor privilégio).
  Fonte: A1/A2. [CONSOLIDADO].
- **Added** `.agent/rules/04-confidence-routing.md` (linear vs reflexivo por risco).
  Fonte: A3. [CONSOLIDADO].
- **Changed** `rules/01·02·03` → ponteiros para `_shared/` (dedup).
- **Changed** workflows `feature-plan` e `implement` → v1.2 com gate de spec +
  roteamento por confiança + validação contra `validation.md`.

### Bloco 4 — Master v4.1 → `roles/`
- **Added** `roles/tableau-senior-analyst`, `roles/python-fuel-forecaster`,
  `roles/pharma-systems-analyst`, `roles/_template`. Fonte: A2. [CONSOLIDADO].
- **Changed** master v4.1 superado: transversais→`_shared/`, domínio→`roles/`.
- **Fixed** conflito de domínio BI fragmentado (bi-sap vs §5) → casa única em roles.
- **Note** decisão de granularidade: 3 roles (premissa anunciada; reversível).

### Bloco 5 — Observabilidade + eval-sets
- **Added** `_shared/observability/SKILL.md` (OTel GenAI, audit hook, logs imutáveis).
  Fonte: A3. [EMERGENTE] / [CONFIRMADO].
- **Added** `_meta/eval-template.md` (should-trigger / should-NOT por skill).
  Fonte: A2. [EMERGENTE].

### Ressalvas de ambiente (transversais) [CONFIRMADO]
- Isolamento real de subagente, hooks e leitura de filesystem: só em Claude Code/SDK.
- Chat web: regras idênticas, mecanismos degradam para referência/manual.

### Pendências conhecidas
- `roles/aivi-indicator-analyst`: aplicação específica — aguarda as regras de
  "AIVI emergencial" (repo indisponível na sessão). [DESCONHECIDO].
- Versão do master prompt citava "v2.1" — corrigida no roteador para 2.3.

## [1.0.0-generico] — 2026-05-23 — Correção: framework genérico vs aplicações

### Changed (separação núcleo × aplicação)
- **Movido** `roles/tableau-senior-analyst`, `python-fuel-forecaster`,
  `pharma-systems-analyst` → `exemplos/` (são APLICAÇÕES, não núcleo). Fonte: A2
  (skill de papel ≠ domínio; manter simplicidade do núcleo). [CONFIRMADO].
- **Generalizado** `_shared/validation-gamp5` → `_shared/high-stakes-gate`
  (validação por risco + audit trail + HITL, agnóstico). Normas setoriais viram
  config de aplicação (`exemplos/regulated-pharma`). Fonte: A3. [CONSOLIDADO].
- **Papéis de processo** (pmo/architect/developer/qa-critic/docops) reescritos
  enxutos, referenciando `_shared/` — preservados em nome (anti-rename).

### Added (gaps da pesquisa, GENÉRICOS)
- `.agent/skills/explorer` — subagente read-only de exploração/auditoria. Fonte: A1/A2.
- `_meta/external-access.md` — padrão de conectividade MCP, vendor-agnóstico. Fonte: A2.
- `.agent/skills/_template` — molde para criar QUALQUER aplicação (escala por clonagem).
- `exemplos/README.md` — separa explicitamente aplicação de núcleo.

### Princípio reforçado
Núcleo agnóstico de domínio; específico nasce por clonagem. Sem roles especulativas
(antipadrão "tudo agente" / skill sprawl — pesquisa). [CONFIRMADO].

## [1.1.0] — 2026-05-24 — Camada Claude Code + guias de uso

> Correção de versionamento: as entregas anteriores foram indevidamente mantidas
> como 1.0.0. Conforme SemVer, features novas = MINOR bump. Consolidado aqui.

### Added (features novas desde 1.0.0)
- Camada nativa Claude Code: `CLAUDE.md` (raiz) + `.claude/agents/` + `.claude/skills/`.
- Subagentes isolados: `explorer` (read-only) e `qa-critic` + `_template`.
  Fonte: doc oficial Claude Code (skills em .claude/skills, subagentes em .claude/agents).
- `SETUP.md` (entrada, 3 modos: greenfield / revisar / migrar).
- `INSTALAR-NO-VSCODE.md` (instalação + remoção do antigo, passo a passo).
- `COMO-REVISAR-OUTRO-REPO.md` (multi-root + explorer).
- `aivi-indicator-analyst` (scaffold) + spec — exemplo de aplicação por clonagem.
- Eval-set executado dos papéis (`_meta/eval-results-papeis.md`, 33/33).

### Changed
- Versão do sistema: 1.0.0 → 1.1.0.

### Política de versionamento (registrada para não repetir o erro)
- Feature nova compatível → MINOR (1.x.0). Correção → PATCH (1.0.x). Quebra → MAJOR.
- O número da versão e o nome do arquivo .zip devem subir juntos a cada release.

## [1.2.0] — 2026-05-24 — Reorganização, referências, git e versão web

### Added
- `guia/` consolida toda a documentação humana (raiz fica enxuta).
- `guia/ORIENTACAO.md` — mapa de leitura humano × IA.
- `guia/GIT-VERSIONAMENTO.md` — git + SemVer + Conventional Commits + tags.
- `guia/REFERENCIAS.md` — bibliografia completa com links (fontes Anthropic
  verificadas, padrão Agent Skills, SemVer/Keep a Changelog/MADR, pesquisas A0–A3).
- `guia/web/index.html` — versão web single-file, offline, navegável.

### Changed
- Estrutura: guias humanos movidos para `guia/`. Mantidos na raiz só os arquivos
  load-bearing (CLAUDE.md, AGENTS.md, AGENT-FRAMEWORK.md, README.md, CHANGELOG.md, .gitignore).
- Referências cruzadas (README/SETUP/CLAUDE) atualizadas para os novos caminhos.
- Versão do sistema: 1.1.0 → 1.2.0 (features novas = MINOR, conforme política registrada).

## [1.3.0] — 2026-05-24 — Prompt do chat web (v4.2, híbrido)

### Added
- `guia/PROMPT-CHAT-WEB-v4.2.md` — instruções para o campo "Instruções para o Claude"
  (Claude.ai), alinhadas ao framework v2.3. Núcleo transversal inline; domínio
  RESUMIDO inline + detalhe no Project Knowledge (escolha: híbrido).
- §10 do prompt: REGRA DE MANUTENÇÃO CRUZADA — ao revisar regra de domínio, atualizar
  o resumo no prompt + o detalhe no Project + a aplicação em exemplos/. Evita divergência.

### Changed
- Corrigida a compatibilidade do prompt de chat: v2.1 (antigo v4.1) → v2.3 (v4.2).
- Versão do sistema: 1.2.0 → 1.3.0 (feature nova = MINOR).

### Nota de design
- v4.2 é uma APLICAÇÃO do framework para o ambiente de chat (sem filesystem; papéis
  simulados). O núcleo genérico no zip permanece a fonte única; o prompt o encarna inline.

## [1.4.0] — 2026-05-24 — Repo 100% genérico + drift fix + PROMPT-CHAT-WEB consolidado

> Distribuição do framework deixa de carregar aplicações específicas. Aplicações
> de domínio vivem **FORA do núcleo** a partir desta versão (criadas clonando
> `.agent/skills/_template` no repositório de cada equipe). Fonte: A2 (núcleo
> agnóstico de domínio; antipadrão "skill sprawl" evitado). [CONSOLIDADO] / [CONFIRMADO].

### Removed (BLOCO A — repo genérico)
- `exemplos/aivi-indicator-analyst/`, `exemplos/python-fuel-forecaster/`,
  `exemplos/regulated-pharma/`, `exemplos/tableau-senior-analyst/` — aplicações
  de domínio específicas que não pertencem ao núcleo distribuído.
- `exemplos/workflows/{bi-deliverable.md, sap-change.md}` — workflows de domínio
  (BI/SAP), também aplicação-específicos.
- `docs/specs/aivi-recalculo-limites/` — spec específica que estava bloqueada por
  domínio (pendência registrada na entrada [1.0.0] "Pendências conhecidas"). Sai
  junto com a aplicação correspondente.
- `guia/PROMPT-CHAT-WEB-v4.2.md` — duplicata. A cópia canônica é a da RAIZ.

### Added (BLOCO A — guia de criação substitui exemplos prontos)
- `exemplos/README.md` reescrito como **guia de como criar aplicações** (clonando
  `_template` no SEU repositório). Deixa de listar aplicações pré-prontas.

### Added (BLOCO D — sincronia formal do PROMPT-CHAT-WEB)
- `guia/GIT-VERSIONAMENTO.md` checklist de release ganha item: revisar e, se
  necessário, bumpar `PROMPT-CHAT-WEB-v4.x.md` da raiz a cada release. Liga o
  ciclo de vida do prompt web ao do núcleo.
- `CHANGELOG.md` ganha seção `## Política` no topo (SemVer + núcleo×aplicação +
  sincronia PROMPT-CHAT-WEB). Consolida políticas vivas dispersas. [CONFIRMADO].

### Changed (BLOCO B — PROMPT-CHAT-WEB consolidado na RAIZ)
- A cópia canônica do prompt é `PROMPT-CHAT-WEB-v4.2.md` na RAIZ (par de
  `CLAUDE.md`/`AGENTS.md`/`AGENT-FRAMEWORK.md` — load-bearing).
- `README.md` e `guia/ORIENTACAO.md` atualizados: descrevem o arquivo como
  "encarnação do framework para ambientes sem filesystem (Claude.ai, Gemini) —
  mesmos princípios, mesmos resultados, papéis/subagentes simulados".

### Fixed (BLOCO C — drift detectado pela auditoria do `explorer` em 2026-05-24)
- `guia/INSTALAR-NO-VSCODE.md`: contagem 56→54 arquivos; lista de raiz corrigida
  (`SETUP.md` vive em `guia/`, não na raiz desde v1.2.0); referência ao zip
  `v1.0.0` → `v1.4.0`. Causa-raiz: o guia não acompanhou a reorganização da v1.2.0.
- `guia/GUIA-EQUIPE.md`: linha 38 referência órfã `roles/` → atualizada para
  "aplicação criada clonando `_template`, fora do núcleo". Linha 33 (comandos):
  removidos `/sap-change` e `/bi-deliverable` (eram aplicação-específicos);
  adicionada nota de que comandos de domínio vivem na aplicação.
- `guia/GIT-VERSIONAMENTO.md`: exemplos atualizados de v1.2.0 → v1.4.0.
- `guia/web/index.html`: versão visível e camada APLICAÇÕES atualizadas.
- Back-references órfãs varridas e corrigidas em: `AGENTS.md`, `CLAUDE.md`,
  `AGENT-FRAMEWORK.md`, `_meta/eval-template.md`, `.agent/workflows/handoff.md`,
  `.agent/skills/_template/SKILL.md`, `_shared/high-stakes-gate/SKILL.md`,
  `PROMPT-CHAT-WEB-v4.2.md` (§10).

### Changed (system version)
- Versão do sistema: 1.3.0 → 1.4.0 (feature/refactor compatível = MINOR).

### Não tocado nesta entrega (registro deliberado — BLOCO E adiado)
- Renome `_template-application` (no frontmatter) ↔ pasta `_template/`:
  inconsistência menor detectada pelo `explorer`. **Exige ADR pela regra
  anti-rename** (`.agent/rules/01-anti-rename.md` → `_shared/traceability`).
  Fica para entrega separada, com ADR próprio.

### Pipeline auditável desta entrega
- PMO orquestra → `explorer` (subagente read-only) auditou o repo → developer
  executou A–D na branch `chore/repo-generico-drift-e-prompt-web` → `qa-critic`
  (subagente adversarial) validou contra critérios binários C1–C6 (todos
  V; recomendação `aprovar_com_ressalvas` — ressalva 1 incorporada neste
  commit: bump do `index.html` para v1.4.0) → docops (esta entrada).
- Merge **bloqueado**: gate humano. Branch espera revisão antes de cair em `main`.
