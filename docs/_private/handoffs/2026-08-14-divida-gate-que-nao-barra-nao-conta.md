# Dívida do framework — gate que não barra não conta como capacidade

- **Aberto em:** 2026-08-14
- **Origem:** cobrança do dono após auditoria de um gate num projeto que USA o framework
- **Natureza:** emenda ao **ADR-015** (*Enforcement executável + fail-closed*), não ADR novo
- **Régua §0:** passa pela porta **(c)** — destrava avaliação editando norma existente. Adiciona
  **um** auditor executável e **remove** a possibilidade de declarar capacidade sem mecanismo.
  Nenhuma skill nova, nenhum princípio novo.

---

## O caso empírico, medido fora do framework

Repo `agente-copilot-studio`. Um gate de status de projeto (`src/status_projeto.py`), um hook de
pre-commit que o chama, e um teste (`testes/test_gate_status.py`) cujo propósito declarado é
*"provar que o gate BLOQUEIA de verdade"*. O teste imprimia **9/9 verificações passaram**.

Apaguei do gate **toda** a detecção de divergência por etapa. O gate ficou incapaz de detectar
qualquer coisa sobre o que vigia.

**O teste continuou verde: 9/9.** Reproduzido de forma independente por crítico em modelo diferente.

Causa: os seis casos de "o gate TEM de barrar isto" rodavam num estado em que uma *outra* checagem
já derrubava o processo, e o teste conferia apenas `código de saída ≠ 0` — nunca **por que** barrou.

Na mesma auditoria apareceram três bypasses completos em que **o gate responde OK**: evidência
apontando para fora do projeto por caminho absoluto, relatório com conteúdo mentiroso (só a data é
conferida), e declaração de etapas vazia. Registro completo:
`agente-copilot-studio/docs/QA-ADVERSARIAL.md`, rodada 2.

## Por que isto é dívida do framework, e não problema alheio

O framework produziu esse projeto e produziu o hábito de fechar bloco citando canário verde. A mesma
classe de defeito está **dentro de casa**, documentada por nós mesmos:

- **v1.79.0, registrado no `history.md`:** um canário fazia *monkeypatch da própria função* que
  deveria testar, e ficava verde com a extração quebrada. Três defeitos passaram por ali.
- **Trabalho aberto `framework-v1790-fechamento-e-mapa-premissas`:** o `elicitation-gate` está
  marcado como `PROVIDES`, descrito como vinculante, e por mecanismo tem uma seção de prosa mais
  um canário de 74 linhas que só confere **se a prosa está escrita**.
- **`doc_intake` (ADR-029)** é fail-open: anuncia e segue.

E a medição do próprio `capabilities.json`, em 2026-08-14:

| medida | valor |
| --- | --- |
| capacidades registradas | 80 |
| **sem campo `enforcement`** — invisíveis a qualquer auditoria | **35** |
| declaradas `prose` | 5 |
| declaradas `advisory` | 5 |
| declaradas `manual` | 3 |
| ferramenta que cruze a declaração com a realidade | **nenhuma** |

`tools/test_marketing_claims.py` audita as promessas da vitrine, não o enforcement dos gates. Nada
no repo confere se uma capacidade que se declara `fail-closed` tem mesmo um executável que sai com
código diferente de zero quando a condição é violada.

**O ADR-015 se chama "enforcement executável". A norma que exige mecanismo é, ela própria, prosa
não verificada.** É exatamente o defeito que fomos auditar lá fora.

## A técnica não é nova — e é isso que dói

**O framework já sabe fazer isto.** O ADR-096 registra, com todas as letras, *"provado por
mutação"* — duas vezes. E o achado A2 daquele ADR é **exatamente** o defeito de hoje:

> *"O canário aferia **só o `returncode`**, nunca o `stdout`. Mutação removendo `hitl_requerido`
> do JSON **passava**."*

A técnica foi aplicada, funcionou, achou defeito real — e **nunca virou exigência**. Ficou como
boa prática de um bloco. Dois blocos depois, a mesma classe reapareceu no v1.79.0 (canário fazendo
monkeypatch da própria função), e agora reapareceu num projeto que usa o framework.

Isto não é dívida de invenção. É dívida de **institucionalização**: sabíamos, usamos, não exigimos.

## A norma a adotar

> Gate, canário, hook ou script de verificação **só conta como capacidade** se existir prova de que
> ele sabe reprovar. A prova é **executável e específica**: sabota-se deliberadamente o que ele
> vigia, e ele tem de ficar vermelho — pelo motivo certo, não por qualquer motivo.

Três exigências, todas verificáveis por máquina:

1. **Prova de mutação.** Todo canário que sustenta uma capacidade `fail-closed` declara, ao lado, a
   mutação que o faz falhar. Um auditor aplica a mutação numa cópia, roda o canário e exige falha.
   Canário que continua verde sob mutação **perde o registro de capacidade**.
2. **Falha pelo motivo certo.** O teste confere a mensagem ou o código específico do defeito, não
   só "saiu diferente de zero". Sem isso, duas falhas distintas se confundem e uma mascara a outra.
3. **Declaração honesta.** Capacidade sem `enforcement` não entra no `capabilities.json`.
   `prose` e `advisory` são valores legítimos — mas o índice **não pode** descrever como vinculante
   nada que esteja marcado assim. Divergência entre o adjetivo e o campo é falha do auditor.

## Como esta norma vira teatro — e a salvaguarda

Apontado pelo crítico adversarial, e é o risco central: *"prova que bloqueia"* pode ser
operacionalizada como *"N/N verde no canário"* — e acabamos de reproduzir 9/9 verde com a lógica
central apagada. Um autor sob pressão satisfaz a **letra** citando o ledger, sem satisfazer o
**espírito**, porque ninguém audita o auditor. O ADR-077 pede rastro; não pede falseabilidade.

**Salvaguarda:** a evidência aceita não é o número verde. É o **par** (mutação aplicada, canário
vermelho), gravado junto do veredito. Sem o par, a capacidade fica `advisory` — e o índice tem de
dizer `advisory`.

## O que fazer, em ordem

| # | passo | efeito |
| --- | --- | --- |
| 0 | **FEITO em 2026-08-14** — rule **#12** do `qa-critic` (`.agent/skills/qa-critic/rules.md`): canário que sustenta bloqueio exige prova de mutação, com as 3 ocorrências citadas | o crítico passa a pegar a classe; **pendente de revisão adversarial** |
| 1 | Emenda ao ADR-015 com a norma acima | fixa a regra na fonte certa, sem ADR novo |
| 2 | Campo `mutacao` nos registros de `capabilities.json` que declaram `fail-closed` | torna a prova declarável |
| 3 | Auditor executável que aplica a mutação em cópia e exige falha | dá dente à norma |
| 4 | Rebaixar para `advisory` toda capacidade que não passar | honestidade do índice |
| 5 | Preencher `enforcement` nas 35 capacidades sem o campo | fecha o ponto cego |

## Custo, declarado antes de começar

Isto **abre** frente, não fecha. O auditor vai reprovar as 13 capacidades já publicadas como
`prose`/`advisory`/`manual` — incluindo o `squad-enforcement-gate`, que está no meio da disputa do
v1.79.0 — e provavelmente algumas das 22 marcadas `fail-closed` que nunca foram sabotadas para
conferir. O resultado é certo e desagradável: o índice de capacidades vai encolher antes de crescer.

É o preço de parar de contar promessa como entrega.

## Pergunta em aberto para o dono

O QA adversarial do framework **não vinha pegando esta classe**. Ele confere se o canário passou;
não confere se o canário sabe reprovar. Duas saídas, e a escolha é do dono:

- **(a)** A prova de mutação vira exigência do gate de release — todo canário que sustenta capacidade
  `fail-closed` precisa do par (mutação, vermelho) antes do PASS. Custa mais por release.
- **(b)** Fica como auditoria periódica, fora do caminho crítico. Mais barato, e volta a depender de
  alguém lembrar — que é como esta dívida nasceu.

Recomendação: **(a)** para capacidade nova, **(b)** para o passivo das 80 já registradas.
