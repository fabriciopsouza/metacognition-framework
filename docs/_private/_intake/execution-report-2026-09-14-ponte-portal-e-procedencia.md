# Execution report — 2026-09-14 — a ponte com o portal, e o gate que nenhum teste podia dar

> Rota: **squad** + `high-stakes-gate`. QA: **Opus adversarial isolado, primeiro plano**.
> **Nove rodadas. Cinco FAIL. PASS na nona.**
> Entrega: `natulab-agidesk-projetos` PR #5 **merged** (6 commits). 511 testes, 191 mutações.

## Placar

| | bloco 1 | bloco 2 | bloco 3 | **este** |
|---|---|---|---|---|
| Testes | 172 | 230 | 304 | **511** |
| Mutações | 39 | 67 | 95 | **191** |
| Rodadas de QA | 1 | 1 | 1 | **6** |

## O número que justifica o trabalho

Cópia do projeto 82, dado vivo do portal:

```
ANTES   21 itens · executado  0,0% ·  0 concluídas
DEPOIS  31 itens · executado 51,6% · 16 concluídas
```

O relatório dizia que o projeto **não tinha feito nada**. O portal dizia que estava
mais da metade pronto. Esse é o custo dos "2 trabalhos" que o dono recusou, medido
e não argumentado.

## A lição central: procedência não se deduz, registra-se

O ledger de procedência foi reescrito **três vezes**, e cada versão errada só
apareceu porque o QA a procurou:

1. **Licença por string** — o ledger dizia "esteve no backlog". Tira-se `A5` do
   backlog (que é para isso que `--remover` existe), alguém cria `[A5] Ata da
   reunião` na tela, e a ferramenta ganha DELETE irreversível sobre o cartão da
   pessoa.
2. **Vínculo adotado** — amarrado ao `portal_id`, mas preenchendo quando vazio: a
   entrada criada antes do cartão existir adotava o id do primeiro cartão que
   aparecesse.
3. **Trava permanente** — ao fechar isso, trancou junto o **cartão legítimo**, e a
   mensagem de erro mandava fazer exatamente o que não reabre.

As três tinham a mesma raiz: **deduzir, na leitura, quem criou o cartão**. Não dá.
O conserto foi separar duas coisas que estavam juntas:

| campo | responde | quem escreve |
|---|---|---|
| `portal_id` | **qual cartão** é este item — *identidade* | a leitura; é seguro |
| `criado_por_nos` | **quem criou** — *autoridade* | só quem **cria**, ou o operador em `--adotar` |

> **Regra que fica:** quando um sistema precisa decidir *permissão*, o dado que a
> concede tem de ser gravado por quem tem autoridade **no instante do ato** —
> nunca inferido depois, a partir de indício.

## O gate que nem teste nem mutação podiam dar

`espelhar.registrar_procedencia` usava `RAIZ`, constante inexistente naquele
módulo. Levantava `NameError` na primeira tarefa criada, depois do POST e da
prova de vínculo, derrubando o lote.

**Passou por 431 testes e 165 mutações verdes, porque nenhum chamava a função.**

```
teste     prova o COMPORTAMENTO de quem é chamado
mutação   prova que o GATE barra
nenhum    vê a linha que NINGUÉM executa
```

Esta foi a **quinta rodada seguida** em que o achado principal é *"a função pura
tem teste, o ponto onde ela é chamada não tem"* — rodada 4 `sincronizar.main`,
rodada 5 `manutencao_espelho.main`, rodada 6 `colher`, rodada 7 uma função que
teste nenhum chamava, rodada 9 a linha que entrega a pasta.

Quando um achado se repete cinco vezes, a resposta deixa de ser mais um teste e
passa a ser um **mecanismo**. `testes/verificar_nomes.py` resolve cada nome lido
contra nível de módulo, corpo de classe, corpo de função, decorators e defaults.

**E ele pegou um erro meu minutos depois de nascer** — escrevi
`args.backlog.parent` dentro de `criar_e_provar`, onde `args` não existe. Mesma
classe do `RAIZ`; teria passado por 487 testes de novo.

## Lições por skill

### architect
- **Um campo que responde duas perguntas responde mal às duas.** Identidade e
  autoridade moravam no mesmo `portal_id`, e o custo foram três versões erradas
  em três rodadas. O sintoma de que são coisas diferentes estava visível desde a
  primeira: cada correção de um lado quebrava o outro.
- **Fail-closed precisa de porta de saída, e ela precisa ser humana.** A versão
  que trancou o cartão legítimo estava *correta* como proteção e *inútil* como
  ferramenta. `--adotar` lista cartão a cartão, avisa antes o que a assinatura
  significa, e recusa o que nasceu no portal — a regra-título não é revogável
  por flag.

### developer
- **Decidir sobre um conjunto exige ver o conjunto.** Resolver o nome de uma
  pessoa registro a registro fundia `Amanda Lopes` e `Amanda Ferreira` numa
  `Amanda` só, e o painel somava o trabalho de duas. `colher` passou a ler tudo
  antes de resolver.
- **Escolher por ordem é escolher por acaso.** Dois cartões no mesmo `[id]`: a
  última gravação vencia e `sorted` é crescente, então o cartão mais novo —
  tipicamente o que a pessoa acabou de criar — levava a assinatura.
- **Identidade é a chave externa, não o texto.** Derivar o ident do título fazia
  a mesma tarefa virar dois itens quando alguém editava o texto na tela.

### qa-critic
- **Afirmação minha que não se sustenta é achado ALTA.** Três números meus
  estavam errados contra a leitura viva: ids atribuídos ao projeto errado,
  denominador do portal trocado pelo do arquivo local, e uma fixture que dizia
  modelar "a forma real do endpoint" e modelava o oposto — justamente no campo
  que o portão de exclusão lê.
- **A contagem própria de mutação é auto-avaliação.** Em cinco rodadas, das
  mutações que eu mesmo escrevi, **escaparam 5, 4, 2, 5 e 2** — quase nunca por
  código errado, quase sempre por teste que não discrimina ou âncora ambígua.
- **Alarme que dispara à toa deixa de ser lido.** A primeira versão do
  verificador deu **72 falso positivo** e quase foi entregue assim — com a
  proibição escrita no docstring do próprio arquivo.

### docops
- **Número em documento é afirmação: ou tem de onde sair, ou não entra.** E
  número lido de sistema vivo precisa de **carimbo de leitura**: escrevi "o
  portal tem 30 tarefas" no presente, e às 09:06 daquele dia virou 31.

## Custo, e por que valeu

Seis rodadas de QA neste bloco, cinco delas reprovando. Cada FAIL achou coisa
real: um relatório que renomeava 19 de 21 pessoas, um ledger que dava permissão
sobre o cartão de terceiros, um mecanismo central que nunca executou. Nenhuma
teria aparecido em revisão de código — quatro das cinco exigiram **rodar contra
o portal de verdade**.

## Fronteira — declarada

- O sync **não escreve no portal**; só lê de lá.
- **Não apaga item do backlog**: sumir da tela vira `AUSENTES`, declarado.
- Os 10 itens absorvidos do projeto 82 **nunca voltam a ter autoridade**. Foram
  criados pela ferramenta numa era anterior ao ledger, mas o sistema não
  consegue distinguir isso de um cartão humano — e fail-closed é a postura certa.
  Registrado para ninguém redescobrir como bug.
- `.pptx` sai depois, dos mesmos dados.

Handoff em `~/.claude/trabalhos/agidesk-skill-projetos-natulab.md`, com o que o
dono precisa fazer uma vez por projeto antigo e as seis decisões dele em aberto.
