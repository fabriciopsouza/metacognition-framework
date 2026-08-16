# ADR-092 — Camada de enforcement de comportamentos: manifesto declarativo (forma BMAD) + gate determinístico por git-hook

- **Status:** **Aceito** (2026-08-16 — ratificado pelo dono; implementação fechada em v1.82.0). Histórico: v1 foi **reprovada** pelo qa-critic com 3 achados críticos; a v2 corrigiu e ficou parada em Proposto por dois meses. Ao retomar, foi medido que 3 das 4 peças já existiam e faltava o instalador do gancho — escrito e instalado em v1.82.0. Pendência remanescente, registrada em `## Em aberto`: `tools/research_evidence.py`. qa-critic REPROVOU a v1 (3 CRÍTICOS);
  esta v2 corrige. Aguarda ratificação do dono + novo qa-critic.
- **Autor:** sessão `claude-opus-4-8` (papel architect). Decide e documenta; NÃO implementa aqui.

> **Correções v2 (do qa-critic):** (C1) git-hook NÃO é imune a EDR — o ADR-088 já rejeitou pre-push por
> isso; a TRAVA real passa a ser o **commit-status no SHA via `post_canary_status.py`** (ADR-088, provado),
> com git-hook só como conveniência local **a ser provada empiricamente, não assumida**. (C2) o gate media
> "existe JSON" → agora exige **atestação de isolamento**: a evidência de qa-critic só vale se carregar o
> `agentId`/sessão do subagente isolado (≠ autor; ADR-074). (C3) a **matriz mudança→papéis** sai de pendência
> e entra concreta abaixo.

## Contexto (falha observada, não hipótese)
O dono cobrou — repetidamente, numa sessão real — que o agente **não atua como squad**: executa reativo,
roda qa-critic só quando provocado, pula discovery/architect/docops, faz "deep-research" virar busca
ad-hoc, e **declara `[DESCONHECIDO]` cedo demais** em vez de buscar exaustivamente antes de dizer "não sei".
O agente **reconheceu e reverteu na mesma sessão** — prova de que **regra/prosa não corrige comportamento**.

Causa-raiz (mecânica, não moral): os papéis/gates do squad são **aspiração em prosa**; o **gatilho** depende
de **hooks do Claude Code**, que são **vetados em PC não-admin** (ADR-047 → "aplicar inline" = discricionário).
Sem gatilho mecânico, a execução **deriva para o caminho reativo**. Princípio violado: *prosa vira mecanismo*.

O dono apontou a forma da solução: **(1) template para comportamentos e papéis (como o BMAD)** e **(2) uma
camada de gates determinísticos abrangendo isso**. O framework já tem as PEÇAS (ADR-077 `qa_evidence`,
ADR-086 gating por risco, ADR-088 CI-local-sem-Actions, dezenas de `check_*.py`); falta a **costura + o gatilho**.

## Decisão — duas camadas
### Camada 1 — MANIFESTO de comportamento/papel (declarativo, forma BMAD; dado, não prosa)
Cada papel/comportamento (discovery, architect, developer, qa-critic, docops, deep-research, **busca-exaustiva-
antes-de-DESCONHECIDO**) ganha um registro **machine-readable** em `behaviors/manifest.yaml` (ou `.json`):
```
id, papel, GATILHO (quando é OBRIGATÓRIO: tipo de mudança/risco — reusa ADR-086),
EVIDENCIA_EXIGIDA (artefato que prova que rodou), CHECK (script que valida a evidência).
```
BMAD contribui a **FORMA** (persona + comandos + dependências + checklist declarativos). O que o BMAD
**não** tem e nós acrescentamos: a **evidência exigida + o check** — as "garras". É *prosa vira mecanismo*
aplicado ao próprio squad.

### Camada 2 — GATE determinístico que ENVOLVE o manifesto (fail-closed, disparo por git-hook)
Um enforcer (`tools/squad_gate.py`, **extensão de `run_canaries.py`** — não binário novo; corrige régua §0)
que, no momento do check:
1. classifica a mudança pelos **PATHS staged** (determinístico, não julgamento — corrige C3): ver matriz abaixo;
2. lê o manifesto → papéis/evidências **OBRIGATÓRIOS**;
3. consulta o ledger (`qa_evidence.py`) **exigindo ATESTAÇÃO DE ISOLAMENTO** (corrige C2): a evidência de
   qa-critic só conta se tiver `agentId` do subagente isolado **+ `modelo` ≠ autor do bloco** (ADR-074); string
   solta não passa. (Limite honesto: o `agentId` prova que um subagente isolado rodou, não a profundidade do
   julgamento dele — mas elimina a auto-atestação trivial.)
4. **BLOQUEIA** (status failure no SHA) se faltar evidência atestada.

### Matriz mudança→papéis (determinística por path — núcleo, não pendência)
| Path staged casa | Papéis/evidência OBRIGATÓRIOS |
|---|---|
| `**/*.py` (código) | qa-critic atestado (agentId, modelo≠autor) |
| `docs/adr/*.md` (ADR novo/alterado) | architect (o próprio ADR) + qa-critic atestado |
| `CHANGELOG`/bump de versão (release) | junção completa J0–J6 (ADR-077) + qa-evidence |
| `data/catalog/{bindings,spec_faixas}.json` ou número regulado | **research-evidence** (busca) + ratificação humana declarada |
| só `*.md` de doc comum | docops (proporcional) — sem qa-critic |
> Regra de desempate: casou em ≥2 linhas → vale a **mais exigente**. A matriz é DADO (no manifesto), versionada.

**Gatilho — TRAVA real no SHA, não no hook local (corrige C1):** a trava primária é o **commit-status do
GitHub** escrito por `tools/post_canary_status.py` (ADR-088, Python puro, **já provado verde** sob este EDR):
`squad_gate.py` roda como **check do canário** e, se faltar evidência, escreve status **failure** no SHA →
a branch-protection/merge fica barrada **server-side** (o agente não falsifica o status remoto). O **git-hook
`pre-push`** entra só como **conveniência local** e é tratado como **NÃO-CONFIÁVEL até prova empírica** (probe
no bootstrap: cria um hook que grava um marcador e verifica se rodou; se o EDR vetar `sh.exe`, o probe detecta
e o gate **anuncia** que só o commit-status protege — doutrina ADR-047). `--no-verify` pula o hook local mas
**NÃO** muda o commit-status no SHA → o bypass local não destrava o merge (fecha o honor-system da v1).

### O comportamento "buscar exaustivamente antes de dizer NÃO SEI" (o pedido explícito)
Vira item do manifesto com evidência própria (`tools/research_evidence.py`). Para medir **exaustão, não
contagem** (corrige C-busca): exigir, para cada `[DESCONHECIDO]` que vai a decisão — (a) **≥K domínios
DISTINTOS** consultados (não a mesma query repetida); (b) cada tentativa com **resultado real anexado**
(URL + hash/sha do conteúdo recuperado, não string declarada); (c) ao menos uma tentativa na **fonte
primária/oficial** do tipo (ex.: ato regulatório no domínio oficial); (d) verificação de **vigência**
(ADR-009). O gate FALHA se um entregável marca algo desconhecido sem esse rastro. **Limite honesto:** nenhum
check prova "esgotei o mundo"; ele prova "busquei em ≥K fontes distintas, oficiais, com resultado anexado" —
o que elimina o punt preguiçoso (o problema real), não garante onisciência.

### Validação (corrige a falta de canário — não fica em prosa)
Entregável obrigatório junto da implementação: `tools/test_squad_gate.py` (pytest) com **canário fail-closed**:
(1) mudança em `*.py` SEM evidência atestada → gate retorna failure; (2) com evidência atestada (agentId,
modelo≠autor) → passa; (3) `[DESCONHECIDO]` com 1 fonte → falha; com ≥K distintas+resultado → passa;
(4) evidência com `agentId` == autor → rejeitada. Sem este teste verde, J3 deste bloco NÃO fecha (ADR-077).

## Consequências
- (+) Squad/qa-critic/deep-research/busca-exaustiva deixam de depender da minha discrição → **não-opcionais**.
- (+) Funciona em **PC não-admin** (git-hook), fechando o gap do ADR-047.
- (+) Reusa o que já existe (qa_evidence, check_*, risk-gating) — costura, não reinvenção (régua §0).
- (+) Comportamentos viram **dado versionado** (manifesto) — auditável, evoluível sem mexer em código.
- (−) Git-hook é local: clone novo precisa rodar o bootstrap (mitigação: `install_git_hooks.py` no boot/start-session).
- (−) `--no-verify` ainda existe (git): mitigado por **registro de débito** + canário de auditoria (não eliminável 100% sem server-side; ADR-088 já assume BYO-CI).
- (−) Definir GATILHOS bons (o que exige qual papel) é a parte difícil → elicitação + iteração.

## Alternativas descartadas
- **Só regra/prosa (status quo):** falhou nesta sessão — é a causa do ADR.
- **Hooks do Claude Code:** vetados em não-admin (ADR-047). Git-hook contorna.
- **BMAD puro (template sem gate):** dá forma, não dá enforcement — o dono pediu explicitamente o gate.
- **Server-side (GitHub Actions/branch protection):** ideal, mas ADR-088 já registrou que não há Actions aqui; git-hook local é o BYO viável.

## Pendências / próximos passos (este ADR é o passo de architect)
1. **qa-critic (process-critic)** sobre este desenho — antes de qualquer código.
2. Elicitar/definir os **GATILHOS** por tipo de mudança (matriz mudança→papéis exigidos) — reusa ADR-086.
3. Implementar `behaviors/manifest.yaml` + `tools/squad_gate.py` + `tools/research_evidence.py` +
   `tools/install_git_hooks.py`; canário que prova o gate bloqueando (teste no pytest, fail-closed).
4. Rodar o próprio fluxo (discovery→architect→dev→qa-critic) **sobre esta implementação** — dogfooding.
