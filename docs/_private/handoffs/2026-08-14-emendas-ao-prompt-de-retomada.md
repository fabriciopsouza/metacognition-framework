# Emendas ao prompt de retomada — o que a sessão de 14/08 (madrugada) acrescenta

Cole **junto** com o prompt original e com as emendas anteriores. Tudo abaixo foi **medido nesta
sessão**, com o comando que reproduz. Onde contradiz o prompt, a medição está declarada.

---

## A. O §3 está RESOLVIDO — a suíte vermelha era deste bloco, e agora está verde

A Parte 1.1 das emendas anteriores acertou ao dizer que a `main` estava verde e que o
"64 PASS · 3 FAIL · 68 canários" era **hipótese (c): local de um ramo**. Confirmado — o ramo era
este trabalho:

- o **68º canário** é `tools/test_audit_enforcement.py`, criado nesta sessão;
- os **3 FAIL** eram os gates de release (`test_qa_evidence`, `test_posture_gate`,
  `test_release_checkpoint`) exigindo veredito e checkpoint para o `v1.80.0` — versão que **esta
  sessão** criou no CHANGELOG. Eles estavam **certos** em barrar.

Depois de registrar o veredito da 3ª rodada e escrever o checkpoint:

    python tools/run_canaries.py
    → 67 PASS · 1 SKIP · 0 FAIL (de 68 canários)

**Substitua o §3 inteiro por:** *"a suíte fecha verde; se algo estiver vermelho, é posterior a
14/08 — meça a `main` em worktree separado antes de atribuir causa."*

---

## B. O §8 item 7 deixou de ser pergunta e virou ferramenta

O §8 pede, como entrega, *"cada gate crítico tem prova de mutação registrada?"*. O mecanismo
existe agora — **ADR-106**, aprovado em 3 rodadas adversariais:

    python tools/audit_enforcement.py                  # modo declaração (roda no CI)
    python tools/audit_enforcement.py --passivo        # relatório do passivo
    python tools/audit_enforcement.py --provar --id X  # sabota e EXIGE vermelho

Capacidade que declara `fail-closed` declara a mutação que faz o canário dela falhar, em campos
executáveis (`arquivo`, `de`, `para`, `canario`). O auditor recusa **seis** formas de fraude, cada
uma com caso de teste nomeado. E há a **rule #12** do `qa-critic`, que torna isso critério binário
de revisão.

**Origem:** a técnica **já existia** no ADR-096 (*"provado por mutação"*, duas vezes) e nunca virou
exigência. Dívida de institucionalização, não de invenção.

---

## C. §6 pendência #2 — decisão tomada, número confirmado, mecanismo entregue

Medido em `capabilities.json`:

| medida | valor |
|---|---|
| capacidades no total | **81** (80 do passivo + 1 nova) |
| sem campo `enforcement` | **35** — confirma a Parte 1.4; o "31 `PROVIDES`" do prompt **não tem fonte** |
| `fail-closed` sem `mutacao` | **22** |
| **passivo total** (soma dos dois acima) | **57** |

Decisão do dono, tomada em 14/08 e já mecanizada: **(a) fail-closed para capacidade nova ·
(b) advisory para o passivo**, congelado em `_meta/enforcement-baseline.json` e **pinado por
sha256** no canário — mexer na lista quebra o CI e exige motivo no mesmo commit.

**A pendência #2 deixa de ser "decidir se `enforcement` é obrigatório" e passa a ser "executar a
migração das 57"**, que é a condição de quitação do override da régua §0 escrita no ADR-106.

---

## D. A Parte 2 pede um reparo que JÁ EXISTE — e sobrou uma lacuna, medida

A Parte 2 recomenda levar ao dono: *"o parecer grava o SHA da árvore que revisou; o gate recalcula e
compara"*. **Isso já está implementado**, aparentemente pelo trabalho do PR #118:

- `tools/qa_evidence.py` carimba `sha_revisado` (via `_head_sha()`, emenda ADR-103);
- `tools/squad_gate.py:133-157` compara por **ancestralidade**: o último commit que tocou o path
  tem de ser ancestral-ou-igual ao `sha_revisado`. **Fail-closed** se o campo faltar.

Isso é mais forte que o campo `data`: ancestralidade é fato do git, não alegação.

**A lacuna que sobrou, medida nesta sessão.** Ao registrar o veredito com o bloco ainda
**não-commitado**, o carimbo aponta para um commit que **não contém os arquivos revisados**:

    git cat-file -e 6792400:tools/audit_enforcement.py
    → fatal: path exists on disk, but not in '6792400...'

O `squad_gate` reage corretamente (bloqueia, dizendo que nenhum veredito cobre esses paths), mas o
**artefato fica com um carimbo enganoso** para quem o ler depois. **Reparo sugerido:**
`qa_evidence.py` deve avisar — ou recusar — quando os `escopo_paths` não existirem no
`sha_revisado`. Hoje ele grava calado.

---

## E. Defeito NOVO reproduzido no `squad_gate` — falha crua em vez de mensagem

    python tools/squad_gate.py --paths tools/audit_enforcement.py
    → AttributeError: 'str' object has no attribute 'get'   (squad_gate.py:89)

**Causa:** `qa_evidence.py` valida o **tipo** de `postura` (exige dict) mas **não** o de
`atestacao`. Uma `atestacao` em string é aceita e gravada; o gate a jusante estoura.

Um gate que estoura não é um gate que reprova: no CI, traceback e bloqueio legítimo ficam
indistinguíveis, e quem lê não sabe se o código foi rejeitado ou se a ferramenta quebrou. É a mesma
classe da **Parte 4.3** (degradação silenciosa), pela porta oposta.

**Duas correções, ambas necessárias:** validar o tipo de `atestacao` em `qa_evidence.py` com
mensagem acionável, **e** o gate não confiar no tipo do que lê. Não apliquei — `squad_gate.py` está
sob trabalho ativo do PR #118 e mexer ali atropelaria a outra sessão.

---

## F. A bateria de 4 perguntas do §4 **aprovaria** o gate que auditamos — e ele era oco

O gate do `agente-copilot-studio` responderia "sim" às quatro perguntas do §4: barra, tem mensagem
legível, é rápido. E ainda assim o teste que o sustentava marcava **9/9 com toda a lógica de
detecção apagada**.

**Corrija a pergunta 1 do §4.** Não basta *"rode-o num caso que DEVE reprovar e veja se reprova"* —
ele reprovava **pelo motivo errado**, porque outra checagem derrubava o processo antes. A pergunta
tem de ser:

> **Ele reprova pelo motivo CERTO?** O teste confere a **mensagem** ou o código específico do
> defeito, nunca só `código de saída ≠ 0`.

E some a quinta pergunta, que é a do ADR-106:

> **O teste que sustenta este gate sabe ficar vermelho?** Sabote o mecanismo e confirme.

---

## G. A Parte 4 ganha três classes novas de defeito de gate, todas medidas

Além das três já listadas (casa com a própria documentação · mede o commit anterior · degradação
por captura larga), medidas no `agente-copilot-studio` em 14/08:

**4.4 — O gate que aprova a declaração VAZIA, com mensagem verde.**
Lista de itens vazia ou chave ausente → `"OK: 0 etapa(s) conferidas, nenhuma divergência"`, exit 0.
Esvaziar a declaração desliga o gate **e ele parabeniza**. Pior que silêncio: é aprovação ativa.
*Pergunta: entrada vazia produz PASS ou ERRO?*

**4.5 — O gate que aceita evidência fora da raiz do projeto.**
Etapa "provada" por `C:/Windows/System32/drivers/etc/hosts` passa. Causa: `RAIZ / alvo` no
`pathlib` **descarta a raiz** quando `alvo` é absoluto, e `..` sobe livremente.
*Pergunta: a evidência precisa estar dentro do que o gate governa — e isso é verificado?*

**4.6 — Frescor por carimbo de tempo em vez de conteúdo.**
`touch` no relatório faz passar conteúdo mentiroso; e `git pull`/checkout reescreve a data de tudo,
barrando todo commit sem nada estar errado. Falso verde e falso vermelho, do mesmo defeito.
*Pergunta: o gate confere o conteúdo, ou só um carimbo que qualquer um reescreve?*

A **4.2** do prompt (índice × árvore de trabalho) foi **confirmada lá também**: o hook conferia o
disco, não o que ia ser commitado.

Registro completo: `agente-copilot-studio/docs/QA-ADVERSARIAL.md`, **Rodada 3** (renumerada pela
sessão paralela; não há duplicata).

---

## H. O §9.1 é o **primeiro item** da migração do passivo — as duas pendências se fecham juntas

`handoff-generator` é `PROVIDES` **sem `enforcement`** → está entre as 35 do passivo. Quando for
migrado para `fail-closed`, a norma do ADR-106 vai **exigir** uma `mutacao` — e a mutação natural é
exatamente o caso da Parte 3: repo sem remote.

Ou seja: a pendência **#2** (enforcement) e o achado **§9.1** (handoff descrevendo o repo errado)
não são duas tarefas. São a mesma, e há um defeito já medido esperando virar o caso de teste.
**Comece a migração por aí** — é o item com melhor relação entre custo e prova.

---

## I. A regra de escalonamento do §5 não disparou aqui — e vale dizer por quê

Este bloco levou **3 rodadas** (`reprovar` → `corrigir` → `aprovar`), mas cada uma num **trecho
diferente**: o texto do ADR, depois o wiring no CI, depois o cross-check. A regra é *"três
reprovações no mesmo trecho = o problema é o desenho"* — nenhum trecho reprovou três vezes.

Vale registrar porque **dois dos três achados bloqueantes foram contra o TEXTO, não contra o
código**: o ADR afirmava que as três fraudes tinham "cada uma seu caso de teste" e uma não tinha.
Afirmação antes da verificação, no documento que institui a norma contra isso. Está registrado
dentro do próprio ADR-106.

**Sugestão ao §5:** a contagem de reprovações deve separar **defeito de código** de **afirmação
falsa em documento**. São classes distintas, com causas distintas, e misturá-las esconde as duas.

---

## K. Pendência #1 (extração do P14) — 7ª ocorrência, medida no checkpoint desta sessão

Ao gerar o P14 de fechamento, o campo saiu **truncado na quebra de linha**. Fonte no `history.md`:

    **Próximo passo:** migrar o passivo das 57 capacidades — cada uma ganha `mutacao` provada ou é
    rebaixada ao `enforcement` que de fato tem. É a condição que quita o override da régua §0.

O que o P14 entregou:

    **Objetivo:** migrar o passivo das 57 capacidades — cada uma ganha `mutacao` provada ou é

**O truncamento é invisível** — *"...provada ou é"* não parece cortado o bastante para alguém
desconfiar, e a próxima sessão receberia o objetivo pela metade sem nenhum aviso. É o defeito #2 da
tabela do ADR-105 (*"truncado parece completo"*) reaparecendo pela porta da continuação de linha,
que é o defeito #5 da mesma tabela.

**Não corrigi o parser.** É núcleo em disputa, a decisão entre *canário que exige campo em linha
própria* × *parser linha-a-linha* é sua, e mexer ali no fim de uma sessão é exatamente o padrão que
produziu seis defeitos consecutivos. Corrigi **o dado**: o `Próximo passo` deste checkpoint está em
uma linha só, com o motivo declarado no próprio texto. O P14 agora extrai o campo inteiro.

**Evidência para a decisão:** o critério do prompt é *"extrair o campo inteiro nos 63 checkpoints,
verificado por detector genérico"*. Este é o **64º**, e ele reprova. Se a opção escolhida for o
canário que exige campo em linha própria, ele precisa **falhar** neste caso — o que é uma prova de
mutação pronta, no sentido do ADR-106.

## J. Estado e autorização — pendente de decisão do dono

O bloco `v1.80.0` está **não-commitado**, na branch `docs/relatorio-sessao-2026-08-13` (ahead 1 de
origin). Não commitei nem mergeei, conforme o §7 do prompt. Arquivos:

| arquivo | estado |
|---|---|
| `tools/audit_enforcement.py`, `tools/test_audit_enforcement.py` | novos |
| `docs/adr/106-*.md`, `_meta/enforcement-baseline.json` | novos |
| `_meta/qa/release-1.80.0-*.json/.md` | novos (veredito da 3ª rodada) |
| `.agent/skills/qa-critic/rules.md`, `capabilities.json`, `CAPABILITIES.md`, `CHANGELOG.md`, `history.md` | alterados |

**Atenção:** há sessões concorrentes. A branch mudou **duas vezes** durante esta sessão, e no
`agente-copilot-studio` o `.githooks/` passou de não-rastreado a commitado no meio da auditoria —
o que gerou uma contradição real entre o que eu medi e o que o crítico mediu depois. Isso reforça
o §2: **declare o horário e o SHA de cada medição**, porque o alvo se move.
