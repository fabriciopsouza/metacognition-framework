# ADR-111 — Confirmação interativa de bloco é o default

- **Status:** Aceito
- **Data:** 2026-08-19
- **Decisores:** dono (Fabricio) — *"confirmar cada tarefa/bloco comigo interativamente é ação
  DEFAULT"*; autoria Opus 5
- **Crítica adversarial:** o QA do degrau abaixo (Sonnet, isolado) **rodou e REPROVOU** o bloco (cinco
  achados, nenhum nesta decisão em si — todos em ADR-110, `handoff.py`, `history.md` e no linter).
  Tratados; **sem veredito de aprovação** até a rodada que avalia as correções.
- **Relação:** complementa ADR-110 (autorização ativa do degrau caro). São gates **diferentes**, e
  confundi-los foi o erro que originou o carve-out abaixo.

## Contexto

Numa sessão só, o dono pediu três coisas e recebeu **sete decisões que nunca viu** — contadas por
assunto, não por edição: uma regra nova adicionada ao núcleo, um ADR emendado em vez de outro aberto,
um teste com o portador trocado, o escopo de documentação decidido sozinho (três vezes, o mesmo
assunto), a memória reescrita, asserções acrescentadas a um canário e a decisão de não commitar.
Nenhuma foi maliciosa e várias eram razoáveis — mas o dono só soube delas depois de prontas. Ao
revisar, ele **mandou revisitar três**: a regra nova, a escolha de emendar em vez de abrir ADR, e o
escopo de documentação. Só a primeira era regra; as outras duas eram decisão de rastro e de volume.

Antes disso, na mesma sessão, o dono já havia dito: *"isto deve ser interativo, não mds"* — depois de
receber, como se fosse consulta, um documento com perguntas em aberto.

O padrão é velho neste repositório e está no `history.md` com nome: o agente não detecta o próprio
overreach; quem detecta é o dono, sempre depois. Todas as correções até aqui foram **posteriores**.

## Decisão

**Antes de executar um bloco, o agente apresenta o plano e espera.** Bloco é um conjunto de edições
com um objetivo. O plano cabe em uma tela: o que será tocado, as **decisões em aberto** com
alternativas reais e uma recomendação, e o que fica de fora. Uma interrupção por bloco — não por
arquivo, que seria caro e ninguém sustentaria.

**Interativo significa conversa.** Pergunta feita e respondida no diálogo. Entregar documento com
perguntas abertas não é elicitar: é devolver o trabalho e chamar de consulta.

**Não passam por este gate:** ler, buscar, inspecionar e rodar canário — investigação não muda estado,
e file-first (regra 03) exige que ela venha **antes**, de modo que pedir licença para ler inverteria a
ordem; os gates anunciados do próprio framework (ADR-047); e —

> **O QA adversarial obrigatório.** O degrau **abaixo** do default é **automático**, roda em toda
> junção e no fechamento, e **não pede autorização a ninguém**. Isto está escrito porque foi violado
> no ato: ao montar o próprio plano desta decisão, o agente pediu autorização para o QA obrigatório.
> O dono corrigiu — *"o 1º QA em sonnet deve e tem que ser automático. Fui claro em especificar que
> somente o segundo em FABLE teria que ter autorização ativa"*. Um gate de processo novo não pode
> engolir um gate de qualidade que já existia: seria trocar controle por permissão.

**`"siga"`, `"ok"` e `"pode continuar"` não são autorização para escopo novo.** Autorizam prosseguir
no escopo já declarado. Silêncio nunca autoriza. (O mesmo critério do ADR-110, por coerência: lá vale
para custo, aqui para escopo.)

**Mecanismo.** A regra vive em `.agent/rules/06-confirmacao-interativa.md` — o diretório que **viaja
para projeto novo**, que é o propósito da branch onde isto nasceu — e é nomeada em `CLAUDE.md` e
`AGENTS.md`. O `check_rules_parity` ganhou uma **guarda de ponteiro morto**: regra citada por nome num
arquivo de autoridade tem de existir. Não exigimos que toda regra seja nomeada — o ponteiro genérico
para o diretório é o desenho deste repo — mas quem é nomeada fica presa: apagar o arquivo e deixar o
ponteiro, ou renomear e esquecer o ponteiro, passa a reprovar. Provado por sabotagem no
`test_rules_parity`.

## Régua §0 (ADR-007)

**Porta (c), destrava eval editando existente:** alegada. A guarda foi acrescentada ao linter que já
existia, não a um canário novo, e cobre uma **classe** — qualquer regra futura que vire link quebrado —
não só esta. Sem ela, a regra 06 poderia sumir de um clone sem nada apitar, que é precisamente o furo
que a branch inteira ataca.

## Consequências

**Boas.** O dono vê as decisões **antes**, e não depois. As alternativas viram escolha dele em vez de
julgamento do agente. E a regra viaja: quem clonar o projeto herda o comportamento, não a boa intenção.

**Ruins, e assumidas.** Mais idas e voltas por bloco, e latência maior em trabalho que o agente
resolveria sozinho. O risco real é o gate virar cerimônia — plano genérico, sem decisão em aberto
declarada, aprovado no automático. Por isso a regra exige que o plano **nomeie o que está em aberto**:
plano sem isso é plano incompleto, e é o sintoma a vigiar.

**Limite declarado, porque prometer mais seria a sobre-promessa que o próprio framework proíbe.**
Nenhum hook obriga o agente a perguntar — o harness não expõe esse ponto de controle. O canário
garante que a regra não seja apagada em silêncio e que ela viaje. O cumprimento é **cobrável em
revisão**, não imposto por código. É a mesma classe de limite já declarada no `qa_final_duplo`.

## Alternativas recusadas

**Confirmar arquivo a arquivo.** Recusada: quatro a oito idas e voltas por bloco. Gate caro demais é
desligado, e aí não protege nada — o mesmo raciocínio que manteve o degrau caro fora das junções no
ADR-110.

**Confirmar só regra/política e irreversível.** Era a opção enxuta, e foi recusada pelo dono. A
evidência sustenta a recusa: das três decisões que ele mandou revisitar, **só uma era regra** — as
outras duas (emendar um ADR em vez de abrir outro; o volume de documentação) não eram regra nem
irreversíveis, e a opção enxuta as teria deixado passar. **Correção de honestidade:** a primeira
versão deste parágrafo dizia que ele "mandou desfazer" decisões que "não eram regra", enquanto o
Contexto dizia que a desfeita **era** uma regra — as duas não podiam ser verdade, e a contradição
sustentava justamente esta recusa. Achado ALTA do 2º QA (Fable).

**Registrar só na memória do agente.** Recusada: não viaja para projeto novo, não vale para outra IA
nem para outra conta. Era exatamente o furo que esta branch existe para fechar.
