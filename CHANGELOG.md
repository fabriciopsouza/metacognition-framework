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

## [1.10.0] — 2026-05-28 — Método sênior de discovery (domain-agnóstico) + auto-observação do framework (ADR-009)

> MINOR feature: o framework absorve o método sênior validado no case real **AIVI** (2026-05-27, repo `LIMITES-BATENTES-RECALC` branch `claude/discovery-aivi-metodo-2026-05-27`, commits `74bd613`+`039fd6d`) como **reforço transversal** do discovery (carregado sob demanda quando há fonte canônica/normativa citada — domain-agnóstico) + **princípio 11** de auto-observação (method-audit autônomo). Régua §0 mantida: 2 novos + 4 edições cirúrgicas.

### Added
- **`docs/adr/009-metodo-senior-discovery-auto-melhoria-framework.md`** — decisão arquitetural que consolida (a) método sênior em 8 passos como reforço transversal do discovery e (b) princípio 11 de auto-observação. Fonte: case AIVI; substância em memórias `[[senior-discovery-method]]`, `[[framework-self-improvement]]`, `[[framework-gaps-from-aivi-case-2026-05-27]]`.
- **`.agent/skills/discovery/metodo-senior.md`** — companion sob demanda (ADR-003) com os 8 passos auditáveis: mapeamento + **vigência** + complementações + cross-domain + pertinência + elicitação + classificação + adversarial. Output ganha seções obrigatórias **Antecipações** + **Backlog de elicitação**. Carregado quando há fonte canônica/normativa citada (qualquer domínio).

### Changed
- **`AGENT-FRAMEWORK.md` §6** — **princípio 11** novo: auto-observação do framework. Cada checkpoint emite 0-3 `method-audit notes`; padrão recorrente vira ADR.
- **`.agent/skills/discovery/SKILL.md`** — bump versão `1.7.0` → `1.8.0`; +1 seção "Reforço transversal sênior" após a tabela de sub-modos, apontando para o companion.
- **`_shared/anti-hallucination/SKILL.md`** — +1 anti-pattern: "Citar norma/regulamento/spec/padrão externo sem checar **vigência**". SSoT do validity-check.
- **`.agent/workflows/checkpoint.md`** — +1 seção **Method-Audit autônomo (ADR-009)**: PMO emite 0-3 notes em sessão substantiva. Sinais: norma sem vigência, regra despriorizada sem semântica, correções repetidas do dono, violação régua §0, loops/retrabalho. Firewall preservado.

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
