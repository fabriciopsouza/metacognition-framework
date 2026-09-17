# controle-projeto — política de lançamento, uma vez, para qualquer projeto

> **Fonte única.** Os comandos `/controle-projeto` e `/controle-sharepoint` apontam para cá. ADR-113.

## Quatro blocos, e a divisão não é estética

O pacote nasceu num bloco só e levou **cinco reprovações** de crítica adversarial. Olhando os
achados juntos, quase todos moravam na mesma camada — converter, validar e resolver valor vindo de
fora — e essa camada estava **espalhada entre dois módulos**, o que fez a validação existir num e
faltar no irmão, lendo o mesmo `projeto.json`. Por decisão do dono, o desenho foi reaberto:

| bloco | mecanismo | canário | o que é |
|---|---|---|---|
| **fronteira** | `tools/controle_base.py` | `test_controle_base.py` — **164 verificações** | converte ou **recusa** todo valor externo |
| **política** | `tools/controle_projeto.py` | `test_controle_projeto.py` — **141 verificações** | as 4 regras de lançamento |
| **List** (opção) | `tools/controle_sharepoint.py` | `test_controle_sharepoint.py` — **68 verificações** | a ida e a volta |
| **números da prosa** | `tools/test_numeros_controle.py` | ele mesmo | o que a documentação afirma bate com o medido |

A fronteira é o bloco de maior densidade de defeito da série, e por isso tem canário e crítica
próprios.

## O problema

Um projeto tem sessenta tarefas e a equipe tem quatro pessoas. Lançar as sessenta no portal não
acelera nada: enterra o que importa, e o quadro deixa de ser lido. Mas segurar tarefa pronta também
custa — trabalho automatizável fica parado esperando alguém lembrar.

Sem regra escrita, quem decide é a memória do operador. E memória de operador é o único componente
do sistema sem canário.

## As quatro regras (ADR-113)

| # | regra | natureza |
|---|---|---|
| 1 | só o **sprint corrente** vai ao portal | filtro |
| 2 | só tarefa **com executor** é lançada | filtro |
| 3 | sprint concluído → **perguntar** ao dono antes de adiantar | gate de autorização |
| 4 | automatizável **sem impedimento** → executar o quanto antes | disparo |

A regra 2 **não é um degrau da ordem** — é filtro que vale para todas. A política efetiva de
lançamento é `dentro do sprint` **E** `com executor`.

**Exceção de histórico, e ela não é opcional:** tarefa **em execução** ou **concluída** continua no
quadro mesmo com prazo fora da janela. O quadro é também o histórico; retroceder o histórico apaga
o trabalho feito aos olhos de quem o fez.

**`agente = executor = responsável`** — um campo só. O portal de chamados não tem usuário de agente,
então quem resolve isso é o *adaptador*: `agente_responde_por` diz qual conta humana recebe o cartão.

## Regra 3 — o gate de autorização

Sprint concluído **não** dispara adiantamento: dispara **pergunta**. O comando sai com código 2 e
para. Autorização é ativa (ADR-111) — `"siga"`, `"ok"` e silêncio **não** são autorização.

O `--adiantar N` respeita `capacidade.em_execucao_por_pessoa` e **não puxa tarefa sem executor**:
sem dono não há carga que calcular, e puxar assim transformaria *"sem sobrecarregar"* em enfeite.

> Teto `0` é valor **válido** e significa congelar. Cadeia de `or` não distingue "não declarado" de
> "declarado zero" — foi defeito real, achado pelo canário.

## Regra 4 — o limite que protege a regra do dono

Auto-execução só alcança classe declarada inócua: **ler, coletar, publicar derivado**. Tarefa que
decide, calcula, ou altera sistema de terceiro **para na fila com o resultado pronto**, e o humano
aprova — *"tudo que envolver decisão, número, valor, crítico, deve ser revisado por humano"*.

Impedimento é medido, não suposto: dependência não concluída, dependência inexistente, item
travado, e acesso que o projeto **não declara ter**. O módulo **não executa nada** — ele identifica
e mede. Quem executa é o agente, e deixa prova.

## Como chega em qualquer projeto

Por **resolvedor**, nunca por cópia. Cópia foi descartada por motivo medido: os repos-sombra deste
framework congelaram vinte releases atrás porque ninguém viu a cópia envelhecer.

```
<projeto>/projeto.json     declaração: o que este projeto é e usa
<projeto>/estado.json      dado: as tarefas
<projeto>/tools/nucleo.py  124 linhas, a única coisa que fica no projeto: sabe PROCURAR
<núcleo>/tools/controle_*  o código, uma vez
```

`projeto.json` é a declaração **única** do projeto — o adaptador do portal e este pacote leem o
mesmo arquivo, em namespaces de chave distintos. Dois arquivos seriam duas verdades.

## Revisão de adoção — o que envelhece quando não há cópia

Com resolvedor o **código** chega atualizado sozinho. O que envelhece é a **declaração**: feature
nova nasce sem ninguém ter dito se aquele projeto a usa, e feature que nenhum projeto adota é
feature órfã — exatamente o que o canário de capacidades deste framework existe para barrar.

`--revisar-adocao` obriga o projeto a se pronunciar: **adotou**, ou **dispensou e por quê**.
Dispensa declarada é resposta válida; o que não vale é o silêncio.

## §List do SharePoint — OPÇÃO, não padrão

O laço, e o defeito que ele conserta:

```
IDA    --exportar   -> LIST-backlog.csv   (derivado, SÓ SAI)
VOLTA  automação       LIST-retorno.csv   (insumo, SÓ ENTRA)  ->  --receber
```

**Arquivo que sai nunca é o mesmo que entra.** O desenho ingênuo — automação escrevendo de volta no
próprio backlog — destrói dado em silêncio, porque o backlog é gerado.

**A List manda em:** responsável, situação, **prazo**, prioridade. Prazo foi liberado por correção
do dono: reunião de status replaneja, e bloquear obriga a abrir o repositório no meio da reunião —
ninguém faz, e aí o prazo real diverge do registrado em silêncio.

**A List não manda em:** título, fase, dependência, o que fazer, onde fazer. Isso é *estrutura* —
nasce de elicitação. Alteração nesses campos é ignorada e **relatada**, nunca calada.

Mudança de prazo dispara **checagem de consequência**: dependência que ficou invertida, prazo que
passou do limite externo. Não impede — replanejar é direito da reunião — mas fica dito.

## Régua §0 — por que este pacote existe sem ser adição pura

A regra de lançamento vivia inline no gerador de um projeto e valia só para ele. Aqui ela vive uma
vez, com `test_controle_projeto.py` cobrindo **141 verificações** — 11 por sabotagem — mais
**34 defeitos provados por mutação** (`test_mutacao_controle.py`), e o projeto que a usava
encolheu:
**−490 linhas, +207, líquido −283**. Perdeu `list_sharepoint.py` (352) e `test_list.py` (133);
ganhou `nucleo.py` (124).

> **Onde conferir, e o limite disso.** O commit é `f6a334d` no repositório **`migracao-sac`**, que
> adotou o pacote — não neste. `git show --stat f6a334d` lá devolve `8 files changed, 207
> insertions(+), 490 deletions(-)`, conferido. **Mas esse repositório é local e não tem remoto:**
> o número é auditável nesta máquina, não por terceiro. Até ele ganhar origin, trate como
> [INFERIDO] verificado por mim, não como fonte que você possa checar. *A redação anterior citava
> só o hash, que não resolve em repositório nenhum a partir daqui — achado do QA adversarial.*

> A primeira redação dizia "encolheu 485 linhas" e "~50 linhas", somando só o lado da subtração e
> subestimando o que ficou. **Achado do QA adversarial**, e é o erro mais difícil de pegar em
> leitura: os números eram reais, só eram os números de outra coisa.

As duas causas de recusa do importador do SharePoint viraram teste — antes eram cicatriz na cabeça
de quem viu o erro na tela.
