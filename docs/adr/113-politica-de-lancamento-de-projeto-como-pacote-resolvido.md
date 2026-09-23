# ADR-113 — A política de lançamento vira pacote do núcleo, achado por resolvedor

- **Status:** Aceito
- **Data:** 2026-08-21
- **Decisores:** dono (Fabricio) — *"Este metodo que acabamos de tratar deve ser uma opcao da
  ferramenta, algo tipo '/controle-sharepoint'. O padrao será a ferramenta ajudar no planejamento,
  execução, criacao de acoes no agidesk, cronograma… Estas caracteristicas… devem ser incorporadas
  e possivel de ser chamada em qualquer projeto do framework"*; autoria Opus 5
- **Crítica adversarial:** Sonnet isolado, degrau abaixo (ADR-109/110). **TREZE rodadas, as treze
  REPROVARAM** — cinco no bloco único, e as demais depois de o dono mandar reabrir o desenho. A quinta
  cobrou, com razão, que a régua manda **escalar ao dono na terceira**; foi escalado, o dono decidiu
  reabrir, e as rodadas seguintes correram sob essa decisão. Ver "O que o dono precisa decidir". A rodada 2 acertou o diagnóstico que importa mais que os achados: *"é a terceira
  rodada nesta classe (string vs. data) sobrevivendo ao próprio processo desenhado para pegá-la"*.
  Ver a seção **"Consertar instância não conserta classe"**. Todos os achados verificados por
  comando antes de corrigir; **34 correções provadas por mutação**. **Sem veredito de aprovação:**
  nenhuma rodada aprovou este bloco até aqui. A rodada 13 (29/08/2026) achou um ALTA **neste
  próprio cabeçalho**: ele dizia "9 correções" enquanto o mecanismo declarava 34 — número real, de
  outra rodada, congelado no resumo executivo. Ver **"A rodada 13, e o sinônimo como rota de fuga"**.
- **Relação:** aplica ADR-111 (autorização ativa) à regra 3; usa ADR-010 (núcleo agnóstico, o
  projeto declara o escopo); paga a régua §0 do ADR-007 encolhendo o projeto que a usava.

## Contexto

Um projeto tem sessenta tarefas e a equipe tem quatro pessoas. Lançar as sessenta no portal de
chamados não acelera nada: enterra o que importa, e o quadro deixa de ser lido. Segurar tarefa
pronta também custa — trabalho automatizável fica parado esperando alguém lembrar.

A regra que resolvia isso existia, mas **inline no gerador de um projeto** (`migracao-sac/tools/
backlog.py`), valendo só para ele e sem canário. Fora dali, quem decidia era a memória do operador
— e memória de operador é o único componente do sistema sem canário.

Duas medições feitas em 21/08/2026, por comando, antes de projetar:

1. `CAPABILITIES.md` já tem `projeto-docs-derivados` (`tools/projeto_docs.py`), mas ele deriva do
   estado do **próprio framework** — history.md, ADRs, capabilities.json. Não serve a projeto de
   domínio. **Colide no caminho de saída** `docs/projeto/backlog.csv`, o que é dívida separada.
2. `migracao-sac` **não referenciava o framework**: sem `.agent/`, sem `.claude/`, sem uma menção.
   O framework era aplicado *por sessão*, nunca instalado. Logo, "chamável em qualquer projeto"
   exigia um mecanismo de distribuição que não existia.

## Decisão

### 1. Quatro regras de lançamento, escritas e testadas

| # | regra | natureza |
|---|---|---|
| 1 | só o sprint corrente vai ao portal | filtro |
| 2 | só tarefa com executor é lançada | filtro |
| 3 | sprint concluído → **perguntar** antes de adiantar | gate de autorização |
| 4 | automatizável sem impedimento → executar o quanto antes | disparo |

A regra 2 **não é degrau da ordem**: é filtro que vale para todas. A política efetiva é
`dentro do sprint` **E** `com executor`.

**`agente = executor = responsável`** — um campo só (correção do dono, 21/08/2026). O portal não
tem usuário de agente; quem resolve é o *adaptador*, por `agente_responde_por`.

### 2. Regra 3 é gate, não automação

Sprint concluído sai com **código 2** e para. `--adiantar N` respeita
`capacidade.em_execucao_por_pessoa` e **não puxa tarefa sem executor** — sem dono não há carga que
calcular, e puxar assim transformaria *"sem sobrecarregar"* em enfeite.

### 3. Regra 4 é limitada por outra regra do dono

Auto-execução só alcança classe declarada inócua — ler, coletar, publicar derivado. O resto para na
fila para revisão humana: *"tudo que envolver decisão, número, valor, crítico, deve ser revisado por
humano"*. O módulo **não executa**: identifica e mede impedimento.

### 4. Distribuição por resolvedor, nunca por cópia

O projeto guarda `projeto.json` (declaração), o seu estado (dado) e `tools/nucleo.py` (124 linhas
que só sabem **procurar**). O código vive uma vez, no núcleo.

Cópia foi descartada por motivo **medido**, não por preferência: os repos-sombra deste framework
congelaram vinte releases atrás porque ninguém viu a cópia envelhecer.

`projeto.json` é declaração **única**: o adaptador do portal e este pacote leem o mesmo arquivo, em
namespaces de chave distintos. Dois arquivos seriam duas verdades.

### 5. Revisão de adoção — o que envelhece quando não há cópia

Com resolvedor o **código** chega atualizado sozinho; o que envelhece é a **declaração**. Feature
nova nasce sem ninguém ter dito se aquele projeto a usa — e feature que nenhum projeto adota é
feature órfã, exatamente o que o canário de capacidades existe para barrar.

`--revisar-adocao` obriga o projeto a se pronunciar: adotou, ou dispensou **e por quê**. Dispensa
declarada é resposta válida; o que não vale é o silêncio.

### 6. A List do SharePoint é OPÇÃO

`/controle-sharepoint` é opt-in por `adotado.sharepoint-list`. Projeto que dispensou é **recusado
com mensagem**, não servido em silêncio.

## Régua §0 — o que isto funde

| | antes | depois |
|---|---|---|
| regra de lançamento | inline em 1 projeto, sem canário | `test_controle_projeto.py` com 141 verificações, 11 por sabotagem, mais 34 defeitos provados por mutação |
| laço da List | 352 linhas no projeto + 133 de teste | 0 no projeto |
| o que fica no projeto | — | `nucleo.py`, 124 linhas |

O projeto **removeu 490 linhas e adicionou 207** — líquido **−283**. O commit é `f6a334d` no
repositório **`migracao-sac`** (não neste), onde `git show --stat` devolve `8 files changed, 207
insertions(+), 490 deletions(-)` — conferido. Esse repositório é **local, sem remoto**, então o
número é auditável nesta máquina e não por terceiro; até lá, [INFERIDO] verificado, não fonte
pública. *A redação anterior citava o hash sem dizer onde ele vive, e ele não resolve a partir
deste repo — achado do QA adversarial.*
A primeira redação desta seção dizia "encolheu 485 linhas", somando só o lado da subtração e
omitindo o `nucleo.py` e o `projeto.json` do mesmo diff. **Achado do QA adversarial**, e é o tipo de
erro que não se pega em leitura: o número era real, só era o número de outra coisa.

As duas causas de recusa do importador do SharePoint viraram teste — antes eram cicatriz na cabeça
de quem viu o erro na tela.

## O desenho foi reaberto, e o que isso mostrou

**Decisão do dono, 21/08/2026:** depois de cinco reprovações no bloco único, *reabrir o desenho* em
vez de seguir iterando. A costura veio dos próprios achados: quase todos moravam na camada que
**converte, valida e resolve valor vindo de fora**, e essa camada estava espalhada entre dois
módulos — o que fez a validação de tipo existir num e faltar no irmão, lendo o mesmo `projeto.json`.

Ela virou `tools/controle_base.py`, com canário e crítica próprios. Quatro blocos:

| bloco | mecanismo | canário |
|---|---|---|
| fronteira | `controle_base.py` | `test_controle_base.py` — **164 verificações** |
| política | `controle_projeto.py` | `test_controle_projeto.py` — **141 verificações** |
| List (opção) | `controle_sharepoint.py` | `test_controle_sharepoint.py` — **70 verificações** |
| números da prosa | `test_numeros_controle.py` | ele mesmo |

**A hipótese do escopo menor se sustentou, com uma ressalva.** No bloco único, as cinco rodadas
acharam 4 → 3 → 3 → 4 → 6 defeitos, todos espalhados. No bloco isolado:

- **rodada 1:** 3 ALTA no *mecanismo* — parse de JSON sem guarda, encoding sem guarda, Unicode não
  normalizado (`"José"` NFC e NFD davam duas pessoas). Todos da mesma família: **guarda assimétrica**
  — proteção de um lado e ausência do outro.
- **rodada 2:** **zero ALTA no mecanismo.** Os achados que sobraram foram MÉDIA/BAIXA de contrato
  (forma malformada, `frozenset`, cobertura de dois ramos do resolvedor).

A convergência em severidade é real. A ressalva é que a rodada 2 achou **uma ALTA no canário**, e
ela era grave — ver abaixo.

## O erro de método que quase passou

O canário da fronteira imprimia glifos crus (`"３"`, `"١٢٣"`) para provar uma decisão sobre dígito
não-ASCII. No console default do Windows o stdout é **cp1252**, e `print` levanta
`UnicodeEncodeError`: o canário morria no meio — sem PASS, sem FAIL — e o traceback subia pelo
`run_canaries.py` e **matava o runner**, levando junto os 68 canários seguintes.

**E por que ninguém viu:** o autor rodava tudo com `PYTHONIOENCODING=utf-8` exportado. O ambiente de
verificação não era o ambiente real, e todo verde relatado para aquele canário valia sob uma
condição que a máquina do dono não tem. **Isso é mais grave que o defeito** — é a diferença entre
"o teste passa" e "o teste passa onde a pessoa vai rodar".

Consertado em três camadas, porque uma só deixaria o buraco aberto por outro lado: a mensagem usa
`ascii()` em vez do glifo; os quatro canários reconfiguram o próprio stdout, como as ferramentas já
faziam; e o **runner** deixa de morrer pelo que um canário imprime — byte estranho vira FAIL daquele
canário, nunca queda da suíte.

## A rodada 8, e o que ela ensinou sobre escrever a lição

Dois ALTA, e o primeiro é o mais desconfortável da série: `_detalhe()` e `_pessoas()` — os dois
arquivos auxiliares que um projeto **mais edita à mão** — liam JSON **cru**, fora da fronteira. BOM,
Latin-1 e forma errada derrubavam `--exportar` e `--receber` com traceback.

O desconforto é que a lição já estava **escrita em comentário neste mesmo módulo**, desde a rodada 5:
*"fronteira não é o `--receber`: é TODO ponto onde valor de fora vira valor usado, nos DOIS módulos"*.
**Escrever a lição não aplica a lição.** A verificação que faltava era mecânica, não literária — e
virou canário: uma checagem por **AST** exige que nenhuma das **seis** formas conhecidas de ler
JSON — `json.loads(x.read_text())`, `from json import loads`, alias do módulo, `getattr`,
`json.load(open(p))` e `json.loads(open(p).read())` — escape de `_ler_json`. As seis são testadas
uma a uma no auto-teste do detector.

> A precisão desta frase custou duas correções. A primeira versão usava **regex** e acusou o próprio
> docstring que **cita** o defeito para explicá-lo — grep confunde código com prosa. A segunda usava
> AST mas só reconhecia a forma canônica, enquanto o ADR afirmava "nenhuma": cinco escritas
> equivalentes driblavam. **Ou a checagem cobre, ou a frase muda** — cobrir era barato.

O segundo ALTA foi o quarto número estale da série — a contagem de aprovações da suíte, escrita
numa hora e conferida noutra — e a conclusão
dele mudou uma regra: **contagem de PASS/SKIP/FAIL saiu da prosa e passou a ser proibida**. Ela não
pode ser medida de dentro da suíte (o canário de números faz parte dela; medi-la seria recursão), e
número que nenhum mecanismo confere já envelheceu quatro vezes aqui. Quem quiser o número roda
`python tools/run_canaries.py`, que é a fonte. **Afirmação que não dá para verificar de dentro não
deve ser feita** — é mais honesto apontar onde olhar.

E a alegação *"N defeitos provados por mutação"* deixou de ser prosa: virou
`tools/test_mutacao_controle.py`, que copia o pacote para uma pasta temporária, reintroduz cada um
dos **34** defeitos já corrigidos na cópia e exige que o canário reprove — o repositório nunca é
tocado. Ele acusou na primeira execução: as duas correções desta mesma rodada estavam no código e
**sem rede**.

## A rodada 9, e o segundo mascaramento de ambiente

Dois ALTA. O primeiro é o achado mais instrutivo da série inteira:

**A máquina tem dois Pythons, e eles discordam.** `python` é 3.12 e `python3` é 3.14. Em 3.12,
`Path("...\0...").resolve()` levanta `ValueError`; em 3.14 **não levanta nada**. O único teste que
exercitava a guarda de caminho usava exatamente esse gatilho — então, sob 3.14, a mutação daquela
guarda **não era detectada** e a prova de mutação ficava vermelha.

É o irmão exato do `PYTHONIOENCODING` da rodada 7: **troca de interpretador**, não de variável de
ambiente, produzindo resultado diferente. A lição é a mesma e agora está aplicada duas vezes — *o
que prova não pode depender de detalhe do ambiente que ninguém declarou*. A guarda passou a cobrir
`TypeError`, que vale em qualquer versão; o caso do NUL continua testado, mas como verificação
**condicional que se declara** quando o interpretador não o produz. Skip dito, nunca skip calado.

O segundo ALTA: o `LIST-retorno.csv` era lido com `.read_text()` **cru** e derrubava `--receber` com
`UnicodeDecodeError`, enquanto os JSON irmãos já tinham guarda — a mesma classe que a rodada 8
corrigiu, no único CSV que o pacote lê, e que o próprio docstring chama de *"preenchido por gente
numa planilha"*. Agora há **uma leitura de texto só** (`ler_texto`), servindo JSON e CSV, para não
haver um terceiro caminho amanhã.

## A rodada 10, e o canário que tinha o defeito que existe para impedir

Dois ALTA, e o primeiro é o mais irônico da série.

**O canário anti-número-falso checava PERTENCIMENTO, não CORRESPONDÊNCIA.** Ele perguntava *"este
número está no conjunto {fronteira, política, List}?"* — e não *"ele bate com o canário que a frase
CITA?"*. Então a prosa pôde atribuir à **fronteira** o número que era da **política**, e passar.
É
literalmente a frase do achado da rodada 8 — *"números reais, só eram os números de outra coisa"* —
reaparecendo **dentro do mecanismo construído para fechá-la**.

O conserto é de classe: o número passou a exigir **atribuição**. A prosa tem de dizer de qual
canário ele é — pelo nome do arquivo ou do bloco — e o teste confere contra **aquele**. Número de
verificação sem fonte declarada vira FAIL, não por estar errado, mas por não dar para conferir. É a
mesma regra que a rodada 8 adotou para a contagem da suíte, aplicada a mais uma família.

O auto-teste do detector ganhou o caso que faltava e que define a diferença: **número verdadeiro
atribuído ao módulo errado**.

**O segundo ALTA:** `--iniciar` — o comando de entrada de um projeto **novo**, o primeiro contato de
qualquer projeto com o pacote — não passava pela fronteira. `Path(x).resolve()` e `mkdir` crus, e a
chamada em `main()` ficava **fora** do `try` que captura o erro: nem a mensagem chegava. Terceiro
ponto de entrada a escapar da mesma promessa, e o padrão já tem nome nesta série — **guarda
assimétrica**.

## A rodada 11: a assimetria maior estava na palavra

Três ALTA, e os dois primeiros são a mesma coisa vista pela primeira vez.

**A fronteira só olhava a ENTRADA.** `--receber --confirmar` gravava o estado com `write_text` cru e
`--exportar` abria o CSV com `open("w")` cru: arquivo somente-leitura derrubava os dois com
`PermissionError` e traceback completo. E o `--receber --confirmar` é o **único comando do pacote que
persiste mudança** — o de maior consequência, e o que crashava pior.

Onze rodadas perseguindo *guarda assimétrica*, e a assimetria maior estava na palavra: eu li
"fronteira" como **leitura** o tempo todo. O docstring do módulo sempre disse *"nunca **gravar** nem
comparar o que não se sabe ler"* — a palavra estava lá, e só o "ler" tinha sido tratado. Agora há
`escrever_texto`, simétrica de `ler_texto`, e a checagem estrutural por AST passou a exigir que
**nenhuma escrita** escape dela, com detector auto-testado.

**O terceiro:** o gate de atribuição de números casava `"list"` como **substring**, e "list" cabe
dentro de **"lista"** — palavra corriqueira em português. Um número **certo** sobre a política seria
acusado de errado porque a frase falava de uma "lista". É falso positivo, e o próprio cabeçalho do
canário diz que falso positivo é pior que canário ausente: *ensina a pessoa a ignorar o vermelho*.

E é a **terceira aparição da mesma família** nesta série — a primeira foi `Ana-Maria` tratada como
marcador porque `-` cabia dentro dela. Casamento por substring não respeita palavra, e agora a
atribuição usa fronteira de palavra.

**A prova de mutação pegou o autor duas vezes nesta rodada**, e isso vale registrar: acusou uma
âncora órfã quando uma guarda mudou de lugar, e mostrou que a armadilha que eu tinha escrito para o
falso positivo era **decorativa** — a palavra-armadilha estava mais longe do número que a atribuição
correta, então o teste passava com o código bom *e* com o mutado.

## A rodada 12: o achado mais sério de todos

Três ALTA, e o segundo muda a natureza da conversa.

**Sem contenção de caminho.** `raiz / nome` do `pathlib` **descarta a raiz** se `nome` for absoluto,
e sobe livremente com `..`:

```python
Path("C:/projetos/meu") / "C:/Windows/win.ini"   # -> WindowsPath('C:/Windows/win.ini')
```

Um `"estado": "../fora/alvo.json"` — ou um caminho absoluto colado por engano ao editar
`projeto.json` à mão, que é **o cenário que esta fronteira inteira existe para tratar** — fazia
`--receber --confirmar` ler, mesclar e **sobrescrever um arquivo qualquer do disco**. E a mensagem
de sucesso nem revelava que o alvo não era o do projeto.

Os outros defeitos desta série produziam crash ou número errado. Este **destrói arquivo de terceiro
em silêncio**, e por isso a regra ficou dura: todo caminho vindo da declaração é confinado à raiz.

**Escrita não-atômica.** `open("w")` **trunca no momento do open**, antes de escrever um byte: falha
no meio — disco cheio — destruía o conteúdo antigo sem gravar o novo. O crítico reproduziu com
`estado.json`, o arquivo de maior consequência do pacote, e o que restou foi `'{"ite'`.

E pior que o defeito: **o meu teste afirmava** *"escrita que falha não pode deixar o arquivo pela
metade"* — mas só exercitava o caso em que o `open` falha **antes** de truncar. A alegação do teste
era mais forte que o mecanismo. Agora grava num temporário ao lado e troca com `os.replace()`, que é
atômico: ou o arquivo velho inteiro, ou o novo inteiro.

**A fronteira de palavra era ASCII pura.** `[0-9a-z_]` não inclui letra acentuada, então `"listável"`
reabria o falso positivo que a rodada 11 fechou para `"lista"`. Num canário que audita prosa **em
português**, ignorar acento é ignorar o alfabeto do texto.

## A rodada 13, e o sinônimo como rota de fuga

A rodada que faltava — a que avalia as correções — rodou em 29/08/2026 e **reprovou**, com um ALTA
só. O alvo foi o **cabeçalho deste próprio ADR**: ele citava, como se fosse o total atual, o número
da rodada 2 na série da tabela acima, enquanto `test_mutacao_controle.py` declarava **34**. Número
real, só que de outra hora, congelado no resumo executivo do documento — a mesma classe *"número
certo de outra hora"* que as rodadas 3, 8 e 10 já tinham tratado como ALTA aqui dentro.

**O que faz este caso valer uma seção é por onde ele escapou.** `test_numeros_controle.py` existe
inteiro para impedir essa classe, e ele não pegou: a família de regex exigia a palavra literal
`defeito`, e o cabeçalho usou o sinônimo `correções`. **O número furou o gate pela palavra, não pelo
valor.** É o irmão exato do achado da rodada 11 — `"list"` casando dentro de `"lista"` —, só que
espelhado: lá o detector via demais por substring, aqui ele via de menos por sinônimo. Nos dois
casos o defeito estava na **forma do padrão**, não no valor comparado.

A correção tem duas metades, porque consertar só a prosa deixaria a porta aberta para a próxima
palavra: o cabeçalho passou a dizer 34, e a família passou a cobrir `defeitos|correções|correcoes`
com a concordância (`provad\w+`). Provado na ordem certa — com o padrão ampliado e a prosa ainda
errada, o canário sai **exit 1** apontando *"a prosa diz 9 (mutacoes (medido: 34))"*; e há dois
casos novos de auto-teste por sinônimo, um exigindo que o número errado seja pego e outro que o
certo continue passando, para a ampliação não virar falso positivo.

**A lição, que é sobre este ADR e não sobre o pacote:** treze rodadas depois, o defeito restante não
estava no código — estava na frase que resume o código. O mecanismo mede o mecanismo; quem escreve o
resumo executivo continua sendo o autor, e é ali que o número velho sobrevive.

## O que o dono precisa decidir

**Cinco rodadas de crítica adversarial, cinco reprovações.** A régua do QA bicelular manda escalar
na terceira, e isso não foi feito na hora — o crítico da rodada 5 cobrou, e estava certo.

O que os números dizem, e eles não contam a mesma história:

| | |
|---|---|
| achados por rodada | 4 → 3 → 3 → 4 → 4+2 |
| **crashes reproduzidos na CLI** | 0 → 0 → **1** → **1** → **2** |
| defeitos provados por mutação | 3 → 9 → 13 → 17 → **23** |
| cobertura do canário | 49 → 66 → 85 → 124 → **138** |

A leitura otimista é que cada rodada encontra defeitos **mais fundos** e a rede fica mais densa. A
pessimista é que cinco rodadas não convergiram, e a sexta provavelmente acha mais.

**As duas leituras são compatíveis, e é por isso que a decisão é do dono:**

1. **Seguir iterando** até uma rodada aprovar. Custo: tokens e tempo, sem prazo previsível.
2. **Aceitar com dívida declarada** — o pacote está verde, o projeto real não regrediu em
   nenhuma rodada, e o que sobrar entra em `history.md` como passivo. Os números por bloco
   estão na tabela acima, atribuídos ao canário de onde saem.
3. **Reabrir o desenho** — se cinco rodadas acham defeito na mesma família, talvez o problema seja o
   pacote fazer coisas demais (política + List + números da prosa num só bloco).

**Recomendação do autor:** opção 2. O que resta é caso-limite de configuração malformada, não o
caminho que o projeto percorre todo dia; o caminho real está provado por reconciliação contra o
comportamento vivo, e o CSV do projeto saiu byte-idêntico em todas as cinco rodadas.

## Um erro do autor, no meio da rodada 5

Ao remover `_executores_agente` (código morto, régua §0), o recorte foi **por posição** — "de `def
_executores_agente` até `def _sem_executor`" — e nesse intervalo tinham sido inseridas, ao longo das
rodadas, **seis funções**. Foram todas junto.

`ast.parse` passou: função ausente é erro de **execução**, não de sintaxe. A verificação em que eu
confiava deu falso conforto, e o que denunciou foi o teste de fumaça logo depois.

Virou canário: o teste agora exige que **todo nome chamado pelo módulo exista de fato**, e a
remoção passou a ser por nome, nunca por intervalo de posição.

## Consequências

**Boas.** A regra passa a ser legível e testável. Projeto novo herda a política sem copiar código.
Feature nova obriga cada projeto a se pronunciar.

**Custo.** O projeto passa a depender do clone do núcleo existir na máquina. `nucleo.py` degrada com
mensagem que diz o que fazer (variável de ambiente ou `nucleo.local.json`), nunca com palpite.

**Dívida declarada, não escondida:**
- `tools/projeto_docs.py` e este pacote escrevem em `docs/projeto/`. A colisão de nome de arquivo
  ainda **não** foi tratada.
- As demais ferramentas genéricas de `migracao-sac` — cronograma em Excel, publicação em pasta,
  pasta de modelos, gate do quadro — **continuam no projeto**. A migração delas é bloco próprio.
- A ativação automática das capacidades no boot (o dono pediu em 21/08/2026, terceira vez) é o item
  de prioridade máxima em `history.md`, e **não** é resolvida aqui.

## Consertar instância não conserta classe

O crítico da rodada 2 disse a frase que reorganizou este bloco: *"é a terceira rodada nesta classe
sobrevivendo ao próprio processo desenhado para pegá-la"*. E o padrão era esse mesmo — cada rodada
apontava **um lugar**, eu consertava **aquele lugar**, e o vizinho ficava:

| rodada | onde a comparação frágil estava | quem achou |
|---|---|---|
| pré-QA | marcador de ausência por substring (`Ana-Maria` sumia) | eu, escrevendo o briefing do crítico |
| 1 | identidade de executor por string crua; prazo no filtro | QA rodada 1 |
| 2 | prazo na **ordenação** do adiantamento; corte zero | QA rodada 2 |

Na rodada 2 a resposta mudou: em vez de consertar o apontado, **varri a classe inteira por comando**
— toda comparação que toca data, e todo ponto em que zero é valor válido mas cai como *falsy*.

A rodada 4 mostrou que **nem isso bastava**, e por um motivo que fecha o argumento: eu tratei
"fronteira" como sendo o `--receber`. Errado — fronteira é **todo ponto onde valor de fora vira
valor usado**, e `projeto.json` é tão de fora quanto a List. O teto de capacidade escrito como `"3"`
reproduzia o mesmo `TypeError`, pela porta que eu não tinha olhado. Além disso, `_num` aceitava
`"nan"` (o `float()` do Python reconhece o literal): o valor atravessava a fronteira, gravava `NaN`
no `estado.json` — que **não é JSON válido** pela RFC 8259 — ordenava em **primeiro** lugar no
adiantamento, e **escapava do relatório de ilegibilidade**, porque o teste era `is None` e `nan` não
é `None`. Corrompia sem deixar rastro. E valor de `situacao` fora do de-para **sumia** sem entrar em
nenhuma das três listas de relato — o oposto exato do que o módulo promete no próprio cabeçalho.

Agora todo número de configuração passa por um acessor único que converte ou recusa, e nada é
descartado sem ser dito.

A rodada 3 tinha mostrado que a normalização por comparação não bastava, e o achado é o melhor da
série: alguém digita
`-1` ou `3.5` na coluna Prioridade da List; `receber()` fazia `int(v) if v.isdigit() else v` — e
`.isdigit()` recusa sinal e ponto — então gravava a **string** no estado, calado. O `--adiantar`
seguinte **crashava** com `TypeError`. Não era ordem errada: era o comando inteiro morrendo, para o
projeto todo, num vetor que o próprio ADR desenha como fluxo suportado.

**Aí a correção mudou de lugar, e essa é a lição da série.** Eu vinha normalizando **no ponto de
comparação** — cada rodada apontava uma comparação, eu normalizava aquela, e a próxima aparecia.
Enquanto o dado sujo puder **entrar**, sempre haverá uma comparação ainda não normalizada. Agora a
normalização é **na fronteira**: `--receber` converte ou **recusa** o valor no momento em que ele
entra, e o uso segue defensivo porque estado escrito à mão não passa por fronteira nenhuma.

A varredura da rodada 2 achou os dois do crítico **e um terceiro que nenhuma rodada tinha visto**:
`i.get("prioridade") or 999` — prioridade `0` significa a **mais alta**, é falsy, e virava `999`, a
mais baixa. A tarefa mais urgente do projeto seria a **última** a ser adiantada.

Também virou mecanismo: prazo de item ilegível já era relatado, mas **janela de sprint** ilegível
desligava o filtro em silêncio — assimetria sem motivo. Agora `sprint.inicio = "2026-13-40"` diz, em
voz alta, que a regra 1 está desligada, em vez de deixar as sessenta tarefas parecerem lançáveis.

**A verificação também tinha ponto cego.** Eu varri os números com `grep "~50 linhas"` e o grep
respondeu "nenhum". O grep estava certo: a frase estava **quebrada em duas linhas** e não existia
como texto contíguo. Virou canário — os números da prosa agora são conferidos sobre o texto
*achatado*, contra a realidade medida, e número já refutado não pode reaparecer como afirmação.

## O que o QA adversarial pegou, e por que nenhum apareceria em leitura

**Identidade por string crua.** `carga_atual` contava `"Bruno"`, `"BRUNO"` e `"bruno "` como três
pessoas: a carga real de 3 aparecia como 1+1+1 e o teto de 2 parava de proteger quem já estava
cheio. A regra 3 do dono — *"sem sobrecarregar"* — furada em silêncio por grafia inconsistente, que
é o normal em preenchimento manual.

**Data comparada como texto.** `'2026-8-25'` — 25 de agosto, **dentro** do sprint — dava `False`
contra `'2026-09-02'`, porque `'8' > '0'`. Tarefa legítima retida como "fora do sprint", sumindo do
portal sem erro. Agora a data é normalizada, e prazo **ilegível** é relatado em vez de tratado como
fora — "não tem prazo" e "tem prazo quebrado" são coisas diferentes.

**Fallback de título perdido na migração.** A ferramenta antiga fazia `titulo or o_que[:80]`; a
generalização deixou só a primeira origem, e item ainda sem entrada no de-para exportaria com título
**vazio**. Minha alegação de "idêntico byte a byte" não era falsa, mas era mais fraca do que a
apresentei: valia para **um** estado, aquele em que todos os ids batiam. Sobrevivência do estado
testado não é invariante do código.

**Os canários não pegavam nenhum dos três.** Era a lacuna que o cabeçalho do próprio arquivo dizia
temer. Escrever *"teste que só confirma o estado bom não prova que a regra prende"* não faz o teste
deixar de ser isso — a frase é fácil; a fixture com o caso feio é que é trabalho.

**Três números errados** (ver seção da régua §0). O padrão dos três: nenhum era invenção, todos eram
números **reais de outra coisa** — e um deles coincidia com o de uma capacidade alheia citada no
ADR-106. É o modo de erro mais difícil de pegar em leitura, porque o texto soa conferido.

## Dois defeitos que o método já tinha pegado antes do QA

**Teto falsy.** `teto = config or estado or 3`. Com `em_execucao_por_pessoa: 0` — que significa
*congelar* — o `0` é falsy e caía no default `3`: o comando que deveria travar a equipe inteira
liberaria três por pessoa, em silêncio. **Achado pelo canário**, ao testar o valor extremo *válido*.

**Histórico do quadro.** A primeira versão da regra 1 olhava só o prazo, e teria **tirado 3 tarefas
do quadro** do projeto real — as já em execução ou concluídas com prazo fora da janela. **Achado ao
reconciliar contra o comportamento vivo**, não contra o modelo mental do autor: o número bateu
16 = 16 só depois da correção. Testar contra a própria cabeça não teria achado.
