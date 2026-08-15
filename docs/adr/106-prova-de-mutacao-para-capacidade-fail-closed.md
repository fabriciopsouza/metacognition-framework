# ADR-106 — Prova de mutação para capacidade `fail-closed`: verde só conta depois de saber ficar vermelho

- **Status:** Aceito
- **Data:** 2026-08-14
- **Decisores:** dono (Fabricio), após auditoria de um gate num projeto que usa o framework
- **Tipo:** **EMENDA** ao `docs/adr/015-enforcement-executavel-fail-closed.md` — o ADR-015 exigiu
  que enforcement fosse executável; esta emenda exige que a **execução seja verificada**.
- **Relaciona:** ADR-072 (índice de capacidades), ADR-077 (ledger de evidência), ADR-096
  (primeiro uso de prova por mutação, sem institucionalizar), rule **#12** do `qa-critic`.

## Contexto — a mesma falha, três vezes, e a técnica já estava na casa

O ADR-015 estabeleceu que enforcement sem mecanismo é prosa. Ele não previu o degrau seguinte:
**mecanismo cujo teste não sabe reprovar** também é prosa — só que com um número verde na frente,
o que é pior, porque produz confiança.

Três ocorrências confirmadas, o bastante para o critério de rule nova do `qa-critic`:

| # | onde | o que aconteceu |
|---|---|---|
| 1 | **ADR-096, achado A2** (2026-07) | o canário aferia só o `returncode`, nunca o `stdout`; a mutação que removia `hitl_requerido` do JSON **passava** |
| 2 | **v1.79.0** (2026-08) | o canário fazia *monkeypatch da própria função* que deveria testar e ficava verde com a extração quebrada — 3 defeitos passaram por ali |
| 3 | **projeto externo `agente-copilot-studio`** (2026-08-14) | um teste que anunciava *"9/9 — o gate BLOQUEIA mesmo"* continuou **9/9 com toda a lógica do gate apagada**, porque conferia só `rc != 0` e outra checagem já derrubava o processo |

O ADR-096 registra, com todas as letras, *"provado por mutação"*. **A técnica foi usada, funcionou,
achou defeito real — e nunca virou exigência.** Ficou como boa prática de um bloco. Esta emenda não
inventa nada: institucionaliza o que já sabíamos fazer e paramos de fazer.

O passivo medido em 2026-08-14, antes desta emenda: **80 capacidades, 35 sem nenhum campo
`enforcement`, 22 declaradas `fail-closed` sem que ninguém jamais tivesse verificado que o canário
correspondente sabe ficar vermelho, e zero ferramentas cruzando declaração com realidade.**

## A decisão

**Capacidade que declara `enforcement: fail-closed` declara também a mutação que faz o canário dela
falhar** — em campos executáveis por máquina (`arquivo`, `de`, `para`, `canario`), não em prosa.
O auditor aplica a mutação num worktree isolado e **exige** que o canário fique vermelho.

Três exigências:

1. **Prova de mutação.** Canário que continua verde sob mutação não sustenta capacidade.
2. **Falha pelo motivo certo.** O teste confere a mensagem ou o código específico, nunca só
   "saiu diferente de zero". Sem isso, duas falhas distintas se confundem e uma mascara a outra —
   foi exatamente o mecanismo da ocorrência #3.
3. **Declaração honesta.** `prose` e `advisory` são valores legítimos; o que não se admite é
   descrever como vinculante o que está marcado assim.

### Escopo — a divisão que o dono decidiu

| modo | a quem se aplica | efeito |
|---|---|---|
| **(a) fail-closed** | capacidade **nova** — id fora do baseline congelado | sem `mutacao` declarada, o auditor sai 1 e barra |
| **(b) advisory** | as 80 do passivo, congeladas em `_meta/enforcement-baseline.json` | relatório por `--passivo`; não barra o CI |

A divisão existe porque a alternativa — fail-closed retroativo — reprovaria 57 capacidades de uma
vez e o time desligaria o auditor no primeiro dia. Passivo migra por decisão, não por susto.

## Alternativas consideradas

- **Fail-closed para tudo, já.** Rejeitada: 57 reprovações imediatas, incluindo o
  `squad-enforcement-gate`, que está em disputa no v1.79.0. Norma que ninguém consegue cumprir vira
  norma que todo mundo contorna.
- **Só relatório periódico (modo b para tudo).** Rejeitada como regime único: volta a depender de
  alguém lembrar, que é precisamente como esta dívida nasceu. Fica valendo apenas para o passivo.
- **Cobertura de teste como métrica.** Rejeitada: cobertura mede linha executada, não defeito
  detectado. Um canário que executa a linha e não confere o resultado tem 100% de cobertura e zero
  poder — é literalmente a ocorrência #1.

## Como isto pode virar teatro — e a salvaguarda

Levantado pelo crítico adversarial desta rodada, e é o risco central: *"prova que bloqueia"* pode
ser operacionalizada como *"N/N verde no canário"* — e acabamos de reproduzir 9/9 verde com a lógica
central apagada. Um autor sob pressão satisfaz a **letra** citando o ledger sem satisfazer o
**espírito**, porque ninguém audita o auditor.

**Salvaguarda:** a evidência aceita não é o número verde. É o **par** *(mutação aplicada, canário
vermelho)*, executável e reproduzível por terceiro. O auditor recusa seis formas de fraude. Cada
uma tem caso de teste nomeado em `tools/test_audit_enforcement.py` — a lista abaixo foi escrita
**depois** de os testes existirem, não antes:

| fraude | caso de teste |
|---|---|
| mutação que não sabota nada (`de` == `para`) | *"`mutacao` com `de` == `para`"* |
| mutação **obsoleta** — o trecho `de` já não existe, logo nunca foi aplicada | *"mutacao obsoleta e' acusada"* |
| canário que já estava vermelho **antes** da mutação, caso em que a prova não diz nada | *"canario ja vermelho ANTES da mutacao e' acusado"* |
| mutação apontando para arquivo que **não é o mecanismo** da capacidade — provaria outra coisa | *"`mutacao.arquivo` diferente do `mechanism` declarado"* |
| canário declarado na mutação diferente do `test` da capacidade | *"`mutacao.canario` diferente do `test` declarado"* |
| capacidade que **omite** `mechanism`/`test`, desligando o cross-check em silêncio | *"`fail-closed` sem `mechanism`/`test` declarados"* |

**Como a rodada 1 deste próprio ADR caiu na armadilha.** A versão inicial afirmava três fraudes
*"cada uma coberta por caso de teste"* — e a terceira **não tinha teste**. O crítico adversarial
sabotou aquela checagem no auditor e o canário seguiu 12/12 verde. A afirmação tinha vindo antes da
verificação: exatamente o defeito que este ADR institui norma para impedir, cometido no texto que o
institui. Fica registrado porque o caso é a melhor evidência de que a norma é necessária.

**Segundo vetor, mais óbvio que os seis acima: mexer no passivo.** Bastaria acrescentar o próprio
id à lista de `_meta/enforcement-baseline.json` para a capacidade nova virar "herdada" e escapar do
modo (a). Mitigado por **pino**: `tools/test_audit_enforcement.py` fixa a contagem e o `sha256` dos
ids do passivo; alterar a lista quebra o canário e exige atualizar o pino no mesmo commit, com
motivo. Migração de passivo passa a ser decisão declarada, não edição silenciosa.

## Consequências

**Positivas.** O índice de capacidades passa a distinguir o que prende do que apenas se anuncia.
A rule #12 dá ao `qa-critic` um critério binário onde antes havia julgamento.

**Negativas, declaradas.** O índice encolhe antes de crescer: 57 capacidades entram como passivo
reconhecido. Toda capacidade nova custa mais — escrever a mutação e prová-la. O modo `--provar`
opera sobre o **HEAD commitado**, não sobre a árvore de trabalho: capacidade recém-escrita e ainda
não commitada não é provável, por desenho. E se o processo morrer no meio de uma prova, resta um
worktree órfão — mitigado com `git worktree prune` antes de cada execução, não eliminado.

**Régua §0 (ADR-007) — override explícito, não porta.** Este bloco **adiciona** três arquivos e não
funde nem remove nada; não reduz tokens nem latência. Nenhuma das portas (a)/(b)/(c) se aplica, e
alegá-las seria a racionalização que o ADR-099 cometeu. Segue por **override do dono**, declarado em
2026-08-14 ao aprovar a divisão (a)/(b). **Condição de quitação:** o override se quita quando o
passivo for migrado — cada capacidade herdada ou ganha `mutacao` provada, ou é rebaixada ao
`enforcement` que de fato tem. Enquanto isso não ocorrer, o bloco é dívida reconhecida, não entrega
fechada.

**O que esta emenda NÃO mecaniza.** A exigência 3 (declaração honesta) segue sem auditor: nada
impede, hoje, o `CAPABILITIES.md` descrever como vinculante uma capacidade marcada `advisory`.
Fica registrado como pendência, não como entrega.

## Artefatos

- `tools/audit_enforcement.py` — auditor. Modos `--declaracao` (padrão), `--passivo`, `--provar`.
- `tools/test_audit_enforcement.py` — canário, **19 verificações**. Além das fixtures, ele roda o
  auditor contra o `capabilities.json` **real** e pina o passivo — é essa chamada que transforma o
  modo (a) em gate de CI (via `tools/run_canaries.py`) em vez de script que alguém precisa lembrar
  de rodar. Traz também a **prova de mutação de si mesmo**.
- `_meta/enforcement-baseline.json` — passivo congelado (80 ids).
- `.agent/skills/qa-critic/rules.md` — rule #12.
- Dívida de origem: `docs/_private/handoffs/2026-08-14-divida-gate-que-nao-barra-nao-conta.md`.

## Pendências

- Migrar o passivo: 35 capacidades sem `enforcement` e 22 `fail-closed` sem `mutacao`.
- Mecanizar a exigência 3 (coerência entre o adjetivo no índice e o campo `enforcement`).
- Revisão adversarial deste bloco por modelo diferente do autor — **não realizada até o registro**.
