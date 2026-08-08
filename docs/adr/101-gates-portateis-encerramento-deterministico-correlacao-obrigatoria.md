# ADR-101 — Gates portáteis, encerramento determinístico e correlação obrigatória

- **Status:** Aceito
- **Data:** 2026-08-07
- **Autor da sessão:** `claude-opus-5` — **MEDIDO no transcript** (194 ocorrências), não declarado. O dono rodou `/model claude-fable-5`, o harness não aplicou (indisponível), e o agente chegou a declarar `--author-model claude-fable-5` ao `boot_check`: a flag sobrepôs a detecção e o gate repetiu a suposição. Pego pelo dono, não pelo agente. Correção mecanizada nesta mesma release (ver §Decisão item 8). Autoria em `opus` = **igual ao `baseline_author`**, portanto conforme (ADR-082).
- **Crítico:** qa-critic adversarial isolado em `claude-sonnet-5` — modelo ≠ autor (ADR-011/078). Uma primeira chamada foi spawnada em `opus` (= modelo do autor) por consequência do mesmo erro; **não conta como gate heterogêneo** e está registrada como auto-revisão.
- **Origem:** auditoria falada do dono, 2026-08-07 — onze queixas sobre o framework "só funcionar se provocado"
- **Relacionadas:** ADR-006 (auto-boot) · ADR-019/060/084 (sync) · ADR-027 (route-gate) · ADR-047 (non-admin) · ADR-061 (liveness) · ADR-072 (capacidades) · ADR-093/094 (ambiente verificável) · ADR-100 (trabalhos)

## Contexto — onze queixas, três buracos

O dono listou onze falhas recorrentes. A tentação era tratá-las como onze itens. Elas são **três
buracos estruturais**, e cada queixa é sintoma de um deles:

**Buraco A — espacial: o enforcement não viajava.** Medição, não impressão:

| wiring | gates |
|---|---|
| `.claude/settings.json` (repo-framework) | **17** |
| `~/.claude/settings.json` (global) | **2** — e ambos `.ps1` |

O global é o que vale ao abrir **qualquer outro repo**. Lá faltavam mission-gate, effect-gate,
overwrite-guard, context-budget, author-tier, compaction-gate. Sobrava a prosa do `CLAUDE.md` — que
nem sequer está nos outros repos. Isto explica de uma vez: *"ritos não são seguidos exceto se
provocados"*, *"a troca de modelos não acontece todas as vezes"*, *"ferramentas que deveriam ser
determinísticas só ocorrem se provocadas"* e *"mais comum ao abrir repos que não este"*.

Duas causas por baixo: (1) `sync-global.ps1` espelhava skills/agents/workflows mas **nunca
`tools/`** — sem código lá, o global não tinha o que chamar, então sobreviveram só dois hooks PS
autocontidos; (2) `bootstrap.py`, o instalador, tinha como **função declarada** instalar o perfil
non-admin *"settings.json sem hooks"*. O medo de EDR virou política permanente do instalador.

**Buraco B — temporal: nada vigiava o fim.** Os 17 gates disparavam em `SessionStart`,
`UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PreCompact`. **Zero** em `Stop`/`SessionEnd`.
Logo: *"encerramentos parciais, sem commit pr e merge, mesmo já solicitados explicitamente"*,
*"a memória e melhoria (relatório final) não é determinística"*, *"relatórios cross-IA não são
registrados há muito tempo"*, *"documentação contínua só ocorre se provocada"*. Os mecanismos
existiam (`consistency-gate`, `dev-dogfood-gate`, `trabalhos.py`, `qa_evidence.py`); faltava
**quem os chamasse na hora certa** — e a hora certa é o fim.

**Buraco C — relacional: acoplamento não era modelado.** *"Se estou atualizando as regras para um
agente vertexai/reasoning, o par text-2-sql só é atualizado se eu provocar. DEVERIA ser
automaticamente. TEM QUE SER TUDO."* Nenhum dos 78 registros de `capabilities.json` modelava
relação **entre** artefatos. O `completeness-gate` compara escopo-pedido × entrega — mede o que foi
**dito**; acoplamento é justamente o que **não** se diz, porque o dono presume que o agente sabe
que os dois andam juntos. "Atualizou metade do par" era literalmente inavaliável.

**A queixa do Kaspersky é de outra natureza e o dono está certo.** O EDR é problema de **uma**
máquina, já tratado. Mas a prosa do repo afirmava o veto como fato universal em 20+ arquivos, e o
agente passou a **supor bloqueio onde não há** — degradando para modo manual sem medir. O ADR-093/094
já previa exatamente isto (`kind: process`, nota literal *"NÃO assumir o veto, VERIFICAR"*), mas o
manifesto `.agent/environment.json` **nunca foi instanciado**: era um `.example.json` esperando cópia
manual, e o gate vivia em skip permanente.

## Decisão

**1. O wiring vira função de um manifesto, nos dois escopos.** `tools/gates-manifest.json` é SSoT;
`tools/wire_gates.py` gera o settings do projeto **e** o global, com `scope` (`framework` | `both`)
decidindo quem viaja. No global os comandos levam o path absoluto do framework, resolvido no ato —
por isso é re-executado a cada boot do repo-mãe (ponto de Arquimedes herdado do
`ensure-global-wiring.ps1`, que este script substitui). **Resultado medido: global 2 → 13 gates.**

**2. Todo hook é Python.** `route-gate` e `inject-start-session` foram portados (`route_gate.py`,
`inject_start_session.py`), preservando o algoritmo. Hook `.ps1` é refém de EDR/GPO e inexistente
fora do Windows — foi exatamente o que sobrou capado no global. As versões PS ficam como fallback.

**3. Gates passam a resolver o projeto do usuário, não o framework.** `tools/hooks/_project.py`
funde as três resoluções ad-hoc que já existiam. Bug real corrigido: `mission_gate` e
`compaction_gate` faziam `cwd = ROOT` — wirados globalmente, auditariam o framework enquanto o dono
trabalha noutro repo, produzindo **falso-OK**, que é pior que gate ausente.

**4. `closing_gate.py` no evento `Stop`.** Mede o estado real (commit/push pendente, correlato não
atualizado, raiz poluída, checkpoint do dia ausente, trabalho não registrado) e **bloqueia a parada**,
devolvendo a lista. Não infere intenção — lê estado. Anti-loop obrigatório: honra `stop_hook_active`
e bloqueia no máximo 1× por sessão. Soberania: `session.lock` ou `.claude/.closing.ack` liberam.

**5. `correlated.py` + `.agent/correlations.json`.** Grupos de globs que mudam juntos; tocar um
membro sem tocar os outros é violação. Por projeto — o par `vertexai ↔ text2sql` é do dono, não do
núcleo (agnosticismo, ADR-010). Sem manifesto → **skip declarado**, nunca falso-OK.

**6. `boot_check.py --init-env` instancia o ambiente por MEDIÇÃO.** Nada de copiar `.example` à mão.
Nesta máquina o resultado foi: `EDR-da-lista rodando: NÃO`. A prosa que mandava supor o veto saiu de
`CLAUDE.md`, `start-session.md` e `boot_check.py`; os ADRs históricos ficam intactos (são registro
datado, não regra viva).

**7. `boot_brief.py` no `SessionStart`** injeta o inventário do que **já está decidido** (briefing,
glossário, ADRs, regras, correlações) com ponteiros, não conteúdo (ADR-029). Perguntar o que consta
no inventário passa a ser erro visível, não esquecimento.

**8. Declaração não pode superestimar a medição (`boot_check.py`).** Falha observada *dentro desta
sessão*, e é a mais instrutiva do bloco: o `author-tier-gate` (ADR-082) **detecta** o modelo pelo
transcript e funciona — mas aceitava `--author-model <X>` como override incondicional. O agente
declarou `claude-fable-5` (suposição, porque o `/model` foi digitado) enquanto o transcript dizia
`claude-opus-5`; o gate obedeceu e carimbou `autor='fable'`. **Um gate que aceita a autodeclaração
do auditado não é gate.** Agora a declaração só vale para **rebaixar** (declarar-se abaixo é
confissão); tentar superestimar cai para o detectado, com aviso explícito. Consequência colateral
do mesmo erro: o qa-critic foi spawnado no modelo do próprio autor, quebrando a heterogeneidade —
refeito em `sonnet`. **Quem pegou foi o dono, não o agente** (princípio 11 honesto).

## Régua §0 — ganho líquido

| Mecanismo | Porta | Justificativa |
|---|---|---|
| `wire_gates.py` | (a) funde/remove | Substitui `ensure-global-wiring.ps1` + `sync-global.ps1` + o perfil non-admin como default do bootstrap; elimina o wiring escrito à mão em 2 lugares |
| `_project.py` | (a) funde | Funde 3 resoluções ad-hoc de raiz em 1 |
| `route_gate.py` / `inject_start_session.py` | (a) substitui | Portes; PS vira fallback |
| `closing_gate.py` | (c) destrava eval | `consistency-gate`, `dev-dogfood-gate`, `trabalhos.py` existiam e **nunca disparavam** — não havia evento de fim |
| `--init-env` | (c) destrava eval | `env-applicability` estava em **skip permanente** por falta do manifesto |
| `correlated.py` | (c) destrava eval | "Atualizou metade do par" era inavaliável por qualquer gate existente |
| `boot_brief.py` | (c) destrava eval | "Leia a doc antes" era prosa que não existe fora deste repo |

**Custo honesto:** +7 executáveis e +2 canários contra −1 hook PS (`ensure-global-wiring`) e −2
dependências de PowerShell no caminho crítico. Não é redução líquida de arquivos; passa por (c) em
5 dos 7 casos, e o eval destravado é verificável — cada gate tem canário.

## Consequências

**Positivas.** Abrir qualquer repo passa a herdar 13 gates. O fim da sessão deixa de ser terra de
ninguém. Acoplamento vira dado declarado, versionado e reprovável. A premissa de EDR vira medição
com data e host.

**Negativas e riscos, ditos.**
- **O `closing_gate` bloqueia trabalho real.** Mitigação: 1× por sessão, `stop_hook_active` honrado,
  dois escapes documentados. Ainda assim é o gate mais intrusivo do framework — se incomodar, o
  ajuste é o limiar, não remover.
- **Gates globais rodam em repos de terceiros.** São read-only ou advisory; o único que bloqueia é
  o `closing_gate`, e só sobre estado do próprio git local.
- **O path absoluto do framework no settings global quebra se o repo for movido.** Mitigação: é
  re-afirmado a cada boot do repo-mãe; se o path morrer, o hook falha-soft (exit 0).
- **`correlations.json` é escrito à mão** — grupo mal declarado gera ruído. É dado versionado e
  revisável; o canário valida a forma, não a intenção.

## Pendências

- Espelhar o `PROMPT-CHAT-WEB` (ambiente sem filesystem não tem hook — lá o equivalente é prosa,
  e isso é limite honesto, não descuido).
- `bootstrap.py` continua oferecendo o perfil non-admin; agora como **escolha informada por medição**
  e não default silencioso. Revisar se o modo ainda se justifica após o `--init-env`.
- Porte dos hooks PS remanescentes (`check-execution-mode`) — trigger: 2ª máquina sem PS.
