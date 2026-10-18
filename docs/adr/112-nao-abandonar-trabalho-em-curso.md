# ADR-112 — Trabalho em curso não é abandonado por mensagem nova

- **Status:** Aceito
- **Data:** 2026-08-20
- **Decisores:** dono (Fabricio) — *"Não interrompa ou termine as tarefas em andamento e
  programadas… exceto se o usuário ORDENAR DE FORMA CLARA, IMPERATIVA e sem margem de
  interpretação"*; autoria Opus 5
- **Crítica adversarial:** Sonnet isolado, degrau abaixo. **REPROVOU** — a alegação de
  régua §0 era falsa (ver seção corrigida). Tratado. Sem veredito de aprovação: a
  rodada que avalia esta correção ainda não rodou.
- **Relação:** generaliza a regra que já existia só para QA. Complementa ADR-111 (confirmação de
  bloco): lá o gate é para **começar**; aqui a regra é para **não parar**.

## Contexto

O padrão apareceu várias vezes na mesma sessão: mensagem nova chegava no meio de um trabalho, o
agente atendia a mensagem e **não voltava**. Duas vezes o dono precisou cobrar — *"as tarefas
lançadas ainda estão no agidesk, não fez o que pedi?????"* — sobre trabalho que o próprio agente
havia anunciado e deixado pela metade.

A causa não é distração: é ordem de prioridade errada. Mensagem nova **parece** ser a prioridade por
ser a mais recente, e o agente trata recência como precedência.

## Decisão

**Tarefa em andamento ou já programada é concluída.** Mensagem nova não cancela o que estava
rodando: o agente **pausa, responde, retoma e termina**.

**A única exceção é ordem que seja, ao mesmo tempo, clara, imperativa e sem margem de
interpretação.** Faltando qualquer uma das três, o trabalho continua.

**Não são ordem de parar:** pergunta sobre andamento · pedido de status · crítica ao resultado ·
pedido novo que chega junto · silêncio · `"ok"` · `"siga"` · mudança de assunto · correção de
detalhe. Vários desses **acrescentam** trabalho, e o que já estava em curso segue valendo.

A regra vive em `.agent/rules/07-nao-abandonar-trabalho-em-curso.md` — o diretório que viaja para
projeto novo — e é nomeada em `CLAUDE.md`, ficando sob a guarda de ponteiro morto do ADR-111.

## Régua §0 (ADR-007) — corrigida pelo QA

**A primeira versão deste ADR alegou a porta (a), e a alegação era falsa.** Ela dizia que a regra
absorvia *"QA só para com STOP explícito"*. Essa regra **nunca esteve no repositório**: vive num
arquivo de memória do agente, fora do git, que **não viaja para projeto novo** — justamente o que
esta branch existe para resolver. Nada foi fundido, nada foi removido: foi **adição pura**, com
justificativa que não sobrevive a `grep`. Achado ALTA do QA de junção, e é o defeito que a régua §0
existe para barrar.

**O que é verdade:**

- **Isto é adição ao núcleo.** Uma regra nova, um ADR novo, cinco linhas em `CLAUDE.md`.
- **Nenhuma das três portas se aplica.** Não funde, não reduz custo, não destrava eval.
- **Passa por ORDEM EXPLÍCITA do dono**, e isso é registrado como override, não disfarçado de
  fusão. A régua §0 admite decisão do dono; o que ela não admite é justificativa inventada.
- **A absorção passou a ser real depois do achado:** a regra de memória deixou de ser regra
  independente e virou ponteiro para esta. Passa a haver uma regra só — mas por correção posterior,
  não pela versão original.

**Evidência que sustenta a decisão, e ela é medida:** duas vezes na mesma sessão o dono precisou
cobrar trabalho anunciado e deixado pela metade.

## Consequências

**Boas.** Trabalho anunciado é trabalho entregue. Quem lê o histórico não encontra dois trabalhos
pela metade no lugar de um pronto.

**Ruins, e assumidas.** O agente pode continuar algo que o dono já não quer, quando a vontade de
parar veio implícita. O preço é aceito: o dono corrige com uma frase, e isso custa menos que
descobrir semanas depois que nada foi terminado. A saída explícita está declarada e é barata de usar.

**Limite declarado.** Nenhum mecanismo obriga o agente a retomar — o harness não expõe esse ponto de
controle. O canário garante que a regra não seja apagada em silêncio e que ela viaje. O cumprimento
é cobrável em revisão, não imposto por código.

## Emenda 1 (17/10/2026) — mudança de direção pausa e pergunta

**Status:** Aceito, por ordem do dono. **EMENDA** a seção Decisão. "Pausa, responde, retoma" passa
a ter uma exceção, a mudança de direção. "Crítica ao resultado" continua sem parar nada, porque
ajusta o que já está sendo entregue. "Mudança de assunto" também continua, quando o assunto novo
não toca o trabalho em curso.

**Contexto.** O dono, em 17/10: *"o pmo não está segurando os trabalhos na direção desejada, ou pelo
menos quando a direção muda não está claro o suficiente. o aviso se perde pois vc vai trabalhando.
tem que parar. tem que ser só sobre a mudança, depois demais assuntos"*. E também: *"qd interrompo
com prompt para complementar vc corta a resposta que deveria ser completa"*. A versão original
mandava pausar, responder e retomar. Em mudança de direção, isso fazia o aviso da mudança se perder
no meio do trabalho retomado.

**Decisão.**
1. **Mudança de direção** muda o que deve ser entregue ou o caminho para entregar. Ela pausa o
   trabalho, sem descartá-lo. A resposta trata só da mudança, e depois o agente espera a decisão.
2. **Complemento** ajusta o que já está sendo entregue. Ele entra no trabalho, o trabalho segue, e a
   resposta final traz completo o que o complemento pediu.
3. **Dúvida entre os dois:** vale a mudança de direção. A recusa a "perguntar a cada mensagem"
   continua valendo, porque pergunta, status e "ok" não entram nessa dúvida.

O texto operacional, com a tabela de casos, está em `.agent/rules/07-nao-abandonar-trabalho-em-curso.md`.
A seção 6 de `.claude/global/CLAUDE-global.md` leva a regra a todo projeto. É adição por ordem do
dono (régua §0). O cumprimento é cobrável em revisão; nenhum hook o impõe.

## Emenda 2 (18/10/2026) — trava de rumo, produto novo e mensagem fora de contexto

**Status:** Aceito; decisões D1a e D2a do dono em 18/10/2026. **EMENDA** a emenda 1, acrescentando casos.

**Contexto.** No caso do produto de BI (16 e 17/10/2026), a lista que o dono chamou de *"EXEMPLO de REFERENCIA, nao
exaustivo"* virou escopo. Foram cerca de 28 h e 320 chamadas de ferramenta num leitor fiscal, aprovado com outras
14 decisões num "conforme recomendação". O R1 passou em 145 testes e foi reprovado quando o dono viu a tela. Nada
ligava a tarefa ao pedido.

**Decisão.**
1. **Pedido literal do dono** vira seção da Parte A da spec (`### Pedido literal do dono`, itens `P<n>`). Toda
   tarefa cita `atende: P<n>`. `tools/plano.py verificar` reprova o que não cita (checagem 9). As duas specs
   abertas antes da regra só recebem aviso (D1a; atalho declarado em `LEGADO_SEM_PEDIDO`).
2. **PMO:** bloco sem `P<n>` volta ao dono antes de começar. Aprovação em lote só cobre o núcleo, e o extra pede
   um sim próprio (`.agent/skills/pmo/SKILL.md`).
3. **Discovery, produto novo:** 5 perguntas antes de construir: o que é e para quem · geral ou de domínio ·
   exemplo ou escopo · como o dono verá que está pronto · o que fica de fora (`.agent/skills/discovery/SKILL.md`).
4. **Produto com tela:** o critério de aceite inclui demonstração vista pelo dono, com print ou link e data (D2a;
   critério 7 do modelo de spec).
5. **Mensagem fora de contexto** (de outra sessão): é desconsiderada, com uma linha em Pendências, e o trabalho
   segue (linha nova na tabela da regra 07; molde dado pelo dono, 18/10/2026).

**Régua §0.** Adição por ordem do dono. Os itens 1 e 2 são o mecanismo que faltou à regra escrita do PMO.

## Alternativas recusadas

**Tratar a mensagem mais recente como prioridade.** É o comportamento que gerou o problema. Recência
não é precedência.

**Perguntar, a cada mensagem nova, se deve parar.** Recusada: transfere ao dono uma decisão que a
regra já resolve, e transforma cada interrupção em duas.
