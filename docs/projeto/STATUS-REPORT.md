# Status report

> Gerado por `python tools/projeto_docs.py` a partir do estado real do repositório.
> Não é digitado: se o dado mudar, este arquivo muda na próxima execução.

## Onde chegamos

| release | data | o quê |
|---|---|---|
| 1.90.0 | 2026-08-18 | O boletim deixa de ser escrito só pelo avaliado (ADR-108) |
| 1.89.0 | 2026-08-18 | O passivo do registro acabou (ADR-106 fechado) |
| 1.88.0 | 2026-08-17 | Nenhuma capacidade declara bloquear sem prova (ADR-106, emenda 5) |
| 1.87.0 | 2026-08-17 | O silêncio das distribuições vira número (ADR-049) |
| 1.86.0 | 2026-08-17 | A vitrine promete menos e prova mais, e não pode mais envelhecer mentindo |

## Estado agora

- Branch **feat/enforcement-que-viaja-para-projeto-novo**, commit `d24c9d0 docs(intake): execution-report runbooks linkedin-diagnostico — gate por regex precisa de oraculo dos dois lados`
- Última tag: **v1.90.0**
- Commits não enviados: **0**
- Árvore de trabalho: **com alterações não commitadas**
- Canários: **86 PASS · 1 SKIP · 2 FAIL (de 89 canários) — medido em 2026-09-21T10:06, commit `d24c9d0` (árvore suja na medição) — **DESATUALIZADO: 3 arquivo(s) rastreado(s) mudaram depois da medição — rode `python tools/run_canaries.py`****

## O que falta

| id | item | tipo | quem |
|---|---|---|---|
| B001 | Pedido novo chegando no meio do trabalho deve ir para uma FILA ESCRITA, nao para a memoria do agente (aberto e… | dívida | squad |
| B002 | REFORÇADO PELO DONO EM 21/08/2026, terceira vez: | dívida | squad |
| B003 | PRIORIDADE MÁXIMA DO PRÓXIMO BLOCO — o squad e a crítica adversarial não são determinísticos fora do repo do f… | dívida | squad |
| B004 | Quitação do override da régua §0 do ADR-102 (aberto em 13/08/2026): | dívida | squad |
| B005 | [2026-08-07] Débitos de fechamento do bloco v1.77.0 — 3 achados, NADA aplicado. | dívida | squad |
| B006 | ADR-097 itens 4 e 5 do §Mecanismo (aberto em 16/08/2026, ao aceitar o ADR): | dívida | squad |
| B007 | Pendência permanente (não-código, dono/TI): | dívida | squad |
| B008 | Backlog ativo (trigger-gated, NÃO WIP): | dívida | squad |
| B009 | Backlog ativo (trigger-gated, NÃO WIP): · Canário README × topo do CHANGELOG inexistente (dívida PRÉ-EXISTENTE exposta pelo qa-critic em v1. | dívida | squad |
| B010 | Backlog ativo (trigger-gated, NÃO WIP): · 36 capabilities sem campo enforcement são invisíveis à auditoria anti-teatro (observado 2026-07-22 | dívida | squad |
| B011 | Backlog ativo (trigger-gated, NÃO WIP): · Proveniência de raciocínio POR-TURNO (gap empírico 2026-06-22, sessão ee8a9a49): | dívida | squad |
| B012 | Backlog ativo (trigger-gated, NÃO WIP): · Corrida do 1º prompt do liveness (route-gate dispara antes do carimbo dos SessionStart; | dívida | squad |
| B013 | Backlog ativo (trigger-gated, NÃO WIP): · Cascata v1.55.0–v1.60.0 para os shadows via export-clean — trigger: | dívida | squad |
| B014 | Backlog ativo (trigger-gated, NÃO WIP): · ADR-011 §Pendências: | dívida | squad |
| B015 | Backlog ativo (trigger-gated, NÃO WIP): · ADR-011 §Pendências: | dívida | squad |
| B016 | Backlog ativo (trigger-gated, NÃO WIP): · Item D4 (cross-platform hooks Linux/macOS port) — trigger: | dívida | squad |
| B017 | Backlog ativo (trigger-gated, NÃO WIP): · Integração protocolo cross-IA no fluxo J0-J5 — trigger: | dívida | squad |

## Ação

Nenhum item bloqueado por decisão do dono. O squad segue pelo backlog acima.

## Detalhe dos itens

### B001 — Pedido novo chegando no meio do trabalho deve ir para uma FILA ESCRITA, nao para a memoria do agente (aberto e…

_history.md · Em aberto_

**Pedido novo chegando no meio do trabalho deve ir para uma FILA ESCRITA, nao para a memoria do agente** (aberto em 21/08/2026, pelo dono: *"nao pare de fazer o que esta fazendo. adicione os pedidos na fila -> este tb deve ser um comportamento PADRAO do framework ou qualquer ferramenta relacionada"*). **O que falta.** O ADR-112 ja resolve METADE: nao abandonar trabalho em curso. A outra metade nao existe — o pedido que chega no meio precisa ficar REGISTRADO em arquivo no momento em que chega. Hoje ele fica na cabeca do agente ate o fim do bloco, e cabeca de agente e' o unico lugar do sistema sem canario: a sessao compacta, o contexto vira resumo, e o pedido some sem erro e sem aviso. Ja aconteceu nesta sessao — o dono precisou repetir "Um comando NAO anula o outro" e "Qd peco uma coisa, NAO ELIMINA o que pedi antes". **Escopo:** comportamento padrao do framework, nao de um projeto. Gravar na chegada, sem interromper; devolver a fila ao dono no fecho do bloco; e um canario que prove que pedido registrado nao evapora entre um bloco e o seguinte. **Nao confundir com** o item de enforcement abaixo: aquele e' sobre o squad nao viajar para projeto novo; este e' sobre o pedido do dono nao sobreviver dentro da mesma sessao.

### B002 — REFORÇADO PELO DONO EM 21/08/2026, terceira vez:

_history.md · Em aberto_

**REFORÇADO PELO DONO EM 21/08/2026, terceira vez:** *"este deve ser o comportamento em TODOS os projetos. qd eu mandar atualizar ou iniciar nova sessao, ativar a skill/ capacidade projetos agidesk, etc, o repo em trabalho deve atuar exatamente como o framework pede e como as capacidades invocadas pedem"*. **Escopo que isto acrescenta ao item abaixo:** não basta o enforcement (hooks, gates, squad) viajar — a ATIVAÇÃO das capacidades declaradas pelo projeto também tem de ser automática no boot e no "atualizar", em vez de depender de o agente lembrar. Hoje o `projeto.json` de um projeto já declara o que ele usa (`adotado`, `adaptadores`); falta o boot LER essa declaração e se comportar de acordo. Medido em 21/08/2026: `migracao-sac` não tinha `.agent/`, `.claude/`, nem uma menção ao framework — ele foi aplicado por sessão, nunca instalado.

### B003 — PRIORIDADE MÁXIMA DO PRÓXIMO BLOCO — o squad e a crítica adversarial não são determinísticos fora do repo do f…

_history.md · Em aberto_

**PRIORIDADE MÁXIMA DO PRÓXIMO BLOCO — o squad e a crítica adversarial não são determinísticos fora do repo do framework** (aberto em 18/08/2026, por reclamação do dono; **não é a primeira vez que ele reclama exatamente disto** — o gatilho declarado no ADR-097 item 4 está atingido duas vezes: o dono declarou E o passo desapareceu sem ninguém notar, por horas). **O que aconteceu, medido em 18/08/2026 na abertura do projeto `migracao-sac`:** o conjunto documental inteiro foi escrito, commitado três vezes e declarado pronto **sem uma única rodada de crítica adversarial em modelo isolado**. Pior: o autor ofereceu *autocrítica* no lugar, e o dono precisou dizer que nunca pediu autocrítica — é sempre adversarial. Substituir o crítico independente por autocrítica é exatamente o defeito que o ADR-108 fechou do outro lado (o avaliado escrevendo o próprio boletim), reaparecendo por outra porta. **As quatro causas, todas verificadas por comando, não supostas:** **(1) A aplicação é por repositório e o repositório novo nasceu sem ela.** `migracao-sac/.git/hooks/pre-commit` **não existe**; `tools/install_git_hooks.py` existe e ninguém o chamou na criação do projeto. O `.claude/settings.json` do framework (route-gate, mission-gate) não vale em outra pasta — então nenhum gate de boot ou de turno rodou lá. **(2) O gate é de COMMIT, e o que precisa ser barrado é a ENTREGA.** O `pre-commit` bloqueia `git commit`; ele não tem como impedir o agente de dizer "pronto" no chat, que é onde a entrega acontece de fato. Um gate que só vive no commit é cego para o canal principal. **(3) O `squad_gate` depende de `behaviors/manifest.json`, que só existe no núcleo.** Projeto de domínio não tem manifesto, então não há o que cobrar — o gate passaria mesmo instalado. **(4) A CAUSA NOVA, e a mais grave porque é invisível: o runtime pode VETAR o subagente e o framework não detecta o veto.** A sessão rodou com instrução de não disparar subagente sem pedido explícito do usuário. O framework declara o crítico isolado como obrigatório, o runtime proibiu, e o efeito foi o passo obrigatório **desaparecer em silêncio** — o agente seguiu trabalhando e pedindo autorização em vez de falhar ruidosamente. Enquanto o framework não distinguir "não rodou porque passou" de "não rodou porque foi proibido", o mecanismo é opcional na prática. **O que o dono pediu, e é o veículo da correção:** empacotar o framework como **plugin instalável a partir de repositório** — um stack que o time da Natulab configura UMA vez e que traz junto, em sequência: skills, subagentes com `model:` fixado (crítico != autor por definição, não por lembrança), hooks de boot/turno/entrega, e comandos. **Verificado em 18/08/2026: não existe.** Não há `.claude-plugin/` nem `marketplace.json` no repo — hoje a instalação é manual, por guia. **Candidatos de mecanismo, a decidir por ADR no próximo bloco (nenhum implementado):** (a) gate de ENTREGA, não de commit — o bloco não fecha sem veredito de crítico isolado no ledger; (b) semeadura de projeto novo: um comando único que instala hooks + settings + manifesto mínimo ao criar projeto de domínio, para o enforcement viajar com o trabalho em vez de ficar no núcleo; (c) **fail-closed no veto**: se o subagente não pode ser disparado, o framework anuncia e trava, em vez de continuar; o veto vira registro, não silêncio; (d) empacotamento como plugin, com o subagente crítico declarando `model:` diferente do autor. **Critério de aceite, binário (EMENDADO em 19/08/2026 por achado do QA de entrega):** abrir um projeto novo de domínio numa pasta virgem, o crítico do **degrau abaixo** rodar **sem ninguém pedir** nas junções, **e o crítico do degrau acima rodar na entrega quando autorizado** — e a ausência dele, quando não houver autorização, aparecer **declarada** no veredito em vez de silenciosa (ADR-110; achado MÉDIA do QA de junção de 19/08, que pegou este critério exigindo incondicionalmente o degrau caro e portanto impossível de fechar sem violar a política que ele mesmo deveria cobrar) — a versão anterior falava de "a crítica adversarial" no singular, e podia ser quitada com um crítico só, deixando o segundo morrer sem cobrança — e, se o runtime proibir, o bloco falhar visivelmente em vez de seguir. Enquanto isso não passar, esta pendência não fecha. **Rastro desta ocorrência:** o projeto em `migracao-sac` (3 commits sem veredito) e o registro em `~/.claude/trabalhos/migracao-sac.md`.

### B004 — Quitação do override da régua §0 do ADR-102 (aberto em 13/08/2026):

_history.md · Em aberto_

**Quitação do override da régua §0 do ADR-102** (aberto em 13/08/2026): o padrão documental entrou como **adição pura** sob override explícito do dono. Duas condições fecham o débito, e enquanto não fecharem o override permanece visível aqui: **(a)** aplicar o padrão em **dois projetos de portes diferentes** e registrar o que sobrou e o que faltou — os portes *mínimo* e *médio* do §3 são hoje **INFERIDOS** de um caso só; **(b)** extrair os gates 1 e 2 do §4 (link quebrado, fronteira) para utilitário do framework **se e quando repetirem em três projetos** — aí o registro sobe de `PARTIAL/prose` para `PROVIDES` com canário. Gatilho: toda vez que um segundo projeto adotar o padrão, reavaliar (a). **[2026-08-16 — DECISÃO DO DONO que desfaz um impasse do desenho original]** A condição (a) era circular e ninguém tinha notado: o padrão só seria promovido depois de um segundo projeto usá-lo, mas nenhum segundo projeto consegue usá-lo enquanto ele não estiver na `main`. O dono apontou a circularidade e decidiu: **o padrão sobe para a `main` marcado como pendente de validação em segundo projeto, e a marca só sai depois desse uso.** Disponibilidade e prova deixam de ser a mesma coisa. O override continua aberto — o que mudou é que agora ele *pode* ser quitado. Marca sugerida: campo `status: PARTIAL` + `validado_em_projetos: 1` no registro da capacidade, conferido pelo canário do registro.

### B005 — [2026-08-07] Débitos de fechamento do bloco v1.77.0 — 3 achados, NADA aplicado.

_history.md · Em aberto_

**[2026-08-07] Débitos de fechamento do bloco v1.77.0 — 3 achados, NADA aplicado.** Handoff completo (com comando de re-validação e predicado "aplicar SÓ SE" por item) em `docs/_private/handoffs/2026-08-07-debitos-de-fechamento-v1.77.0.md`. Resumo: **F1** ordem do `history.md` invertida (v1.77.0 abaixo de v1.76.0) — quebra a invariante mais-novo-primeiro e faz `handoff.py` emitir o "Próximo passo" errado, em silêncio · **F2** tags `v1.76.0`/`v1.77.0` ausentes (local e `origin`) — **2ª ocorrência** da falha catalogada em 2026-06-02, gatilho atingido · **F3** registro do ADR-100 nunca alimentado (`~/.claude/trabalhos/` inexistente) — critério de aceite do próprio checkpoint não atendido; **não verificável de outra máquina**. Candidato §0: 2 asserções em `test_consistency_closing.py`, fundindo com o item de backlog "Canário README × topo do CHANGELOG". **Aplicar só após revisão e re-validação contra a versão vigente** — o handoff congela o estado em `main` @ `8820608`. Fechar = remover esta linha + checkpoint datado.

### B006 — ADR-097 itens 4 e 5 do §Mecanismo (aberto em 16/08/2026, ao aceitar o ADR):

_history.md · Em aberto_

**ADR-097 itens 4 e 5 do §Mecanismo** (aberto em 16/08/2026, ao aceitar o ADR): a camada-mestra (canário fail-closed sobre o event log) está entregue; faltam o **hook PreToolUse** que nega ação de papel downstream sem PASS upstream — camada rápida, best-effort por desenho — e cabear o **HITL criptográfico** como pré-condição de ação T3 em bloco high-stakes (`verify_hitl_proofs.py` já existe; falta a ligação). Nenhum dos dois é pré-requisito da conformance: o ADR declara o canário como a lei e o hook como conveniência. Gatilho: dono declarar, ou primeira vez que uma ação downstream sem upstream passar despercebida até a release.

### B007 — Pendência permanente (não-código, dono/TI):

_history.md · Em aberto_

**Pendência permanente (não-código, dono/TI):** exclusão do Kaspersky `.claude\hooks\*` (afeta só os hooks .ps1 remanescentes; ADR-060/079).

### B008 — Backlog ativo (trigger-gated, NÃO WIP):

_history.md · Em aberto_

**Backlog ativo (trigger-gated, NÃO WIP):**

### B009 — Backlog ativo (trigger-gated, NÃO WIP): · Canário README × topo do CHANGELOG inexistente (dívida PRÉ-EXISTENTE exposta pelo qa-critic em v1.

_history.md · Em aberto › Backlog ativo (trigger-gated, NÃO WIP):_

**Canário README × topo do CHANGELOG inexistente** (dívida PRÉ-EXISTENTE exposta pelo qa-critic em v1.73.0, 2026-07-22): a política do repo exige que README, tag e .zip subam junto com o CHANGELOG, mas **nenhum canário compara esse par**. `test_marketing_claims` cobre vitrine × README e **lê a versão do próprio README** — então README(1.72.0) × CHANGELOG(1.73.0) passou verde. Em v1.73.0 o sintoma foi corrigido à mão; o mecanismo não existe. **Candidato §0:** +1 asserção em `test_consistency_closing.py` (que já é o gate de version-claim), não canário novo. Trigger: 2ª ocorrência OU dono declarar.

### B010 — Backlog ativo (trigger-gated, NÃO WIP): · 36 capabilities sem campo enforcement são invisíveis à auditoria anti-teatro (observado 2026-07-22

_history.md · Em aberto › Backlog ativo (trigger-gated, NÃO WIP):_

**36 capabilities sem campo `enforcement` são invisíveis à auditoria anti-teatro** (observado 2026-07-22 ao corrigir achado do qa-critic): entradas que **omitem** o campo não contam nem como OK nem como débito na lista `[debito-mecanizacao]` (P15/ADR-085) — o registro de v1.73.0 foi declarado `manual` e passou a aparecer, os outros 36 seguem fora do radar. Um mecanismo anti-teatro com ponto cego de 48% mede menos do que parece. **Candidato §0:** tornar o campo obrigatório em `test_capabilities.py` (fail-closed) e classificar os 36 num único passe. Trigger: dono declarar OU próxima revisão de P15.

### B011 — Backlog ativo (trigger-gated, NÃO WIP): · Proveniência de raciocínio POR-TURNO (gap empírico 2026-06-22, sessão ee8a9a49):

_history.md · Em aberto › Backlog ativo (trigger-gated, NÃO WIP):_

**Proveniência de raciocínio POR-TURNO** (gap empírico 2026-06-22, sessão `ee8a9a49`): gates elicit/pesquisa/crítica são de **MARCO** (release/junção), não de TURNO — entre marcos, raciocínio sem gatilho nem recibo (o "tudo na mão" cobrado pelo dono). **Extratos:** 4 interações, único recibo = `.claude/boot-proof.json` (manual, pós-nag); `elicitation-gate`/`context-brief-gate`/`qa_evidence` não dispararam — sem ficha, sem brief, sem ledger novo. **Causa NÃO-EDR** (hooks cabeados + UserPromptSubmit dispara; atribuir a Kaspersky foi hint-virou-causa). **Candidato §0:** emissor por-turno (`PostToolUse`/fim-de-turno) que declara ao vivo + grava recibo, reusando `qa_evidence.py` como sink, com fallback inline — **NÃO reinventar** ledger, estender. Análogo: o "evento" do OpenMetadata vs. nossa proveniência por-marco. Trigger: dono declarar OU 2ª recorrência. Detalhe: `docs/research/OpenMetadata-analise-contribuicoes-processo-com-fontes.md` §Addendum 2026-06-22. Pré-gate: architect (ADR) + qa-critic heterogêneo.

### B012 — Backlog ativo (trigger-gated, NÃO WIP): · Corrida do 1º prompt do liveness (route-gate dispara antes do carimbo dos SessionStart;

_history.md · Em aberto › Backlog ativo (trigger-gated, NÃO WIP):_

Corrida do 1º prompt do liveness (route-gate dispara antes do carimbo dos SessionStart; banner se auto-cura no 2º prompt — observado 2026-06-11 sessão `9f01bd9e`) — trigger: incomodar o dono OU 3ª ocorrência reportada. Candidato: tolerar carimbo < N min de outra sessão.

### B013 — Backlog ativo (trigger-gated, NÃO WIP): · Cascata v1.55.0–v1.60.0 para os shadows via export-clean — trigger:

_history.md · Em aberto › Backlog ativo (trigger-gated, NÃO WIP):_

Cascata v1.55.0–v1.60.0 para os shadows via `export-clean` — trigger: decisão de publicação do dono.

### B014 — Backlog ativo (trigger-gated, NÃO WIP): · ADR-011 §Pendências:

_history.md · Em aberto › Backlog ativo (trigger-gated, NÃO WIP):_

ADR-011 §Pendências: Alternativa 2 (rewind cirúrgico) — trigger: caso real onde cascata é custosa.

### B015 — Backlog ativo (trigger-gated, NÃO WIP): · ADR-011 §Pendências:

_history.md · Em aberto › Backlog ativo (trigger-gated, NÃO WIP):_

ADR-011 §Pendências: validation.md projeto × release convergir templates — trigger: ficar pesado manter separado.

### B016 — Backlog ativo (trigger-gated, NÃO WIP): · Item D4 (cross-platform hooks Linux/macOS port) — trigger:

_history.md · Em aberto › Backlog ativo (trigger-gated, NÃO WIP):_

Item D4 (cross-platform hooks Linux/macOS port) — trigger: user em PC não-Windows pedir.

### B017 — Backlog ativo (trigger-gated, NÃO WIP): · Integração protocolo cross-IA no fluxo J0-J5 — trigger:

_history.md · Em aberto › Backlog ativo (trigger-gated, NÃO WIP):_

**Integração protocolo cross-IA no fluxo J0-J5** — trigger: 2ª sessão cross-IA real OU dono declarar. Problema: o protocolo hoje é bolt-on (ad-hoc, sem wiring em nenhuma junção, sem qa-critic gate, sem entrada automática em `history.md`). Candidatos: `docops §Encerramento` dispara `outbox→hub` no J5; `qa-critic` revisa conteúdo cross-IA antes do dispatch; threads abertas geram entrada em `## Em aberto` no boot seguinte; `consistency-gate` checa threads cross-IA no encerramento. Evidência empírica: sessão 2026-06-08 (thread atd36246-fefo-fifo, 3 rounds); gap registrado no round 3 (sealed-partial). ADR-espelho do lado claude-master = candidato arquitecto pós-gate.

