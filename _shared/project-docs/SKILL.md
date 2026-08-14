---
name: project-docs
version: 1.0.0
source: "Padrão extraído de um conjunto documental real (projeto de domínio, 12-13/08/2026) submetido a 5 rodadas de revisão adversarial, REPROVADO 3 vezes antes de aprovar"
last_review: 2026-08-13
description: Núcleo SSoT do CONJUNTO DOCUMENTAL DE PROJETO — a forma padrão de documentar um projeto ágil para que ele sobreviva à troca de pessoa, de sessão e de IA. Carregar quando a tarefa for criar, reorganizar ou auditar a documentação de um projeto (não de um bloco). Define as 7 propriedades obrigatórias, o conjunto graduado por porte, os 4 gates executáveis e os 6 modos de falha já observados. NÃO carregar para fechar bloco (isso é docops) nem para validar dado contra referência (isso é validation-reporting).
---

# Documentação de projeto que sobrevive à troca de dono

> **O que este padrão resolve:** projeto cuja documentação existe, é bonita, e mesmo assim
> obriga quem chega a perguntar tudo de novo — porque o que está escrito não é verificável,
> não tem dono, ou envelheceu sem avisar.
>
> **Origem:** conjunto documental real submetido a revisão adversarial por modelo diferente do
> autor, em 5 rodadas, com **3 reprovações**. Os 6 modos de falha do §5 são os achados que
> barraram o merge — não são hipóteses.

## §0 — Onde esta skill se encaixa

Não substitui os núcleos vizinhos; **instancia** três deles para o caso "documentar um projeto":

- **`confidence-classification`** continua sendo a única definição de origem de afirmação
  (CONFIRMADO · INFERIDO · DESCONHECIDO). Aqui ela ganha um quarto estado de projeto,
  **REFUTADO** (§2.2), e a exigência de que a marca apareça no texto, não só na cabeça de quem
  escreveu.
- **`traceability`** define o rastro. Aqui ele vira exigência de formato: prova com **consulta
  reproduzível** (§2.3).
- **`validation-reporting`** é dona de **validar dado contra uma referência** (campo a campo, com
  níveis por consequência e veredito). Esta skill é dona de **registrar um fato de projeto** com
  rastro. Fronteira: *"os valores conferem com a referência?"* é lá; *"como este projeto guarda o
  que já provou?"* é aqui. O §2.3 usa o formato de prova, não redefine método de validação.
- **`docops`** fecha o *bloco* (CHANGELOG, ADR, execution-report). Esta skill trata do *projeto*.
  Ordem: docops chama esta quando o bloco entrega ou altera documentação de projeto.

**Esta skill é PROSA, não gate.** Não tem canário próprio (registro `project-docs-standard`:
PARTIAL/prose). Ela orienta e é cobrável em revisão adversarial; não bloqueia release. Tratá-la
como bloqueio sem mecanismo seria o teatro de conformidade que o próprio framework proíbe.

**Régua §0 (ganho líquido) se aplica a esta skill também.** O conjunto do §3 é **graduado**:
adotar os 15 arquivos num projeto de duas semanas é o mesmo defeito que esta skill combate.

---

## §1 — O teste binário, antes de tudo

Um conjunto documental está pronto quando:

> **Uma pessoa nova — ou outra sessão de IA — retoma o projeto sem precisar perguntar nada a
> ninguém.**

Não é métrica de estilo. É verificável: entregue a documentação a quem não participou e peça que
diga qual é o próximo passo. Se a pessoa perguntar, o documento falhou — e a correção é do
documento, não da pessoa.

Corolário que muda o que se escreve: **o leitor-alvo não é quem já sabe.** Todo documento é escrito
para quem chega depois, inclusive você daqui a três meses.

---

## §2 — As 7 propriedades obrigatórias

Estas são o padrão. O conjunto de arquivos (§3) é consequência delas, não o contrário.

### 2.1 Dono único por fato
Cada afirmação tem **um** arquivo dono. Os demais **apontam**, nunca copiam.
Um mapa de fontes declara quem é dono do quê e o que vive fora do repositório.

*Por que:* duas cópias divergem, e a divergência é descoberta pelo leitor, não pelo autor.
*Modo de falha real:* uma métrica-chave da base aparecia por extenso em cinco arquivos — e o próprio
mapa de fontes afirmava que os demais "apontavam". Não apontavam.

### 2.2 Marca de confiança em toda afirmação relevante
`CONFIRMADO` (medido ou em fonte oficial, com prova apontada) · `INFERIDO` (deduzido, dizendo de
onde) · `DESCONHECIDO` (**resposta válida; inventar não é**) · `REFUTADO` (acreditávamos, medimos,
estava errado).

**Crença refutada nunca é apagada.** Fica registrada com a prova.
*Por que:* crença apagada volta sozinha. Num caso observado, voltou **seis semanas** depois de
derrubada, e voltou pela boca de quem tinha participado da refutação.

### 2.3 Prova com consulta reproduzível
Um arquivo por verificação, contendo: pergunta em uma frase · **a consulta exatamente como
executada** · resultado · conclusão em uma frase, com a marca.

*Por que a consulta é obrigatória:* sem ela ninguém reproduz, ninguém confere se ainda vale, e
ninguém descobre que a conclusão dependia de um recorte que mudou. **O número envelhece; a consulta
continua respondendo.**

### 2.4 Número sempre com data
Número sem data é retrato sem legenda: não dá para saber se ainda vale. Todo número no repositório
é retrato com data — a fonte é a consulta.

### 2.5 Ponto de retomada explícito
Um documento único responde, nessa ordem: onde estamos · o que foi feito nesta sessão · **o próximo
passo, em ordem** · o que está travado e **por quem** · o que você precisa saber para não errar ·
decisões em aberto e **quem decide cada uma** · como conferir que tudo isto é verdade.

*Detalhe que separa útil de decorativo:* bloqueio sem **nome de quem destrava** não é bloqueio, é
lamento. Decisão em aberto sem **nome de quem decide** não é decisão, é desejo.

### 2.6 Vocabulário e jargão
Termo técnico ou código interno aparece **com a explicação junto, na primeira vez**. Nunca
"aplicamos o INV-9" — escreva o que a verificação faz.

Em domínio sensível ou regulado, o produto **sinaliza, não julga**: "fora do padrão, a verificar",
nunca veredito de irregularidade. Isso não é estilo — é o que torna o resultado defensável.

### 2.7 Fronteira declarada entre as partes
Se o repositório tem uma parte reutilizável e outra específica de domínio, a fronteira é escrita e
**verificada por comando** (§4). Sem isso, a parte reutilizável é contaminada em silêncio e perde a
razão de existir.

---

## §3 — Conjunto graduado por porte

**Adote o menor conjunto que sustente as 7 propriedades.** Crescer é barato; encolher, não.

> **Marca de confiança desta tabela (a skill obedece à própria §2.2):** só a linha **Completo** é
> **CONFIRMADO** — é o conjunto do caso real que originou o padrão. As linhas **Mínimo** e **Médio**
> são **INFERIDAS** por decomposição desse mesmo caso; **nenhum projeto as adotou e reportou ainda**.
> Trate-as como ponto de partida a ajustar, não como norma medida. Débito no §8.

| Porte | Conjunto mínimo | Marca | O que cada um responde |
|---|---|---|---|
| **Mínimo** (1 pessoa, semanas) | `README` · `HANDOFF` · `GLOSSARIO` · `provas/` | INFERIDO | O que é · onde paramos · como se chamam as coisas · o que está provado |
| **Médio** (equipe, meses) | + `AGENTS`/contrato · `DECISOES` · `BLOQUEIOS` · `MAPA-DE-FONTES` | INFERIDO | Como se trabalha aqui · o que já foi decidido e a que custo · o que trava e quem destrava · quem é dono de dizer o quê |
| **Completo** (regulado, multi-time) | + `CONCEITOS-E-PROVAS` · `CRITICA-DOS-METODOS` · `HIPOTESES` · `ELICITACAO` · `COMO-VERIFICAR` · `QUADRO` · `PLANO-IMPLANTACAO` | **CONFIRMADO** | Conhecimento estável e refutado · onde a lógica atual quebra · o que ainda é aposta · o que falta perguntar ao dono · como conferir cada afirmação · o dia a dia · o que a implantação custa |

**Três documentos carregam peso desproporcional** — se só três existirem, sejam estes:
`HANDOFF` (§2.5), `GLOSSARIO` (fonte da verdade dos nomes, com as crenças refutadas) e `provas/`.

**Um arquivo diz onde cada tipo de ideia vai** (um `CONTRIBUINDO` de dois minutos). Sem ele, ideia
boa vira mensagem perdida, e o conjunto cresce por acúmulo em vez de por decisão.

---

## §3.1 — Estado do projeto: o que o `QUADRO` tem de conter

As 7 propriedades acima governam o **conhecimento** do projeto (o que se sabe, com que prova, quem é
dono do quê). Elas não dizem nada sobre o **estado do trabalho** — o que está para fazer, o que está
sendo feito, o que terminou, quem espera o quê. Um conjunto pode passar em todas as 7 e ainda assim
não responder *"o que eu faço hoje?"*.

Esta seção fecha isso. Vale para o porte médio em diante; num projeto de uma pessoa e duas semanas o
`HANDOFF` (§2.5) já basta, e criar quadro é o mesmo excesso que esta skill combate.

### Fonte única, artefato gerado

Quadro, cronograma, entregáveis, envolvidos e ações vêm **de um só arquivo de estado**, e os
documentos de leitura são **gerados** dele. Escritos à mão em paralelo, eles divergem — e o leitor
descobre a divergência sem saber qual dos dois está velho. É a propriedade 2.1 (dono único por fato)
aplicada ao estado do trabalho.

### Os campos que não são opcionais, e a mentira que cada um evita

| Campo | Onde é obrigatório | A mentira que ele evita |
|---|---|---|
| `responsável` | **sempre** em execução | o item que "todo mundo cuida" é o que ninguém faz |
| `travado_em` (nome de quem destrava) | todo item travado | bloqueio sem nome não é bloqueio, é lamento: não há a quem cobrar, então nunca sai |
| `prova` (como conferir) | todo item concluído | "feito" sem como conferir é opinião, e opinião não sobrevive à troca de pessoa |
| `prazo` | toda ação | ação sem data não é ação, é intenção |
| `depende_de` (id existente) | onde houver dependência | apontar para item inexistente faz o cronograma parecer coerente e ser mentira |
| `limite de itens em execução` | no estado do projeto | trabalho em andamento além do que o time sustenta é a forma mais comum de nada terminar |

**As três colunas são fixas** — para fazer, em execução, concluído. Coluna criada por conveniência
vira coluna-limbo: item entra e não sai, porque não existe critério de saída escrito.

### Entregáveis e envolvidos

**Entregável** declara `estado · onde está · como conferir`. "Pronto" sem apontar o artefato e o
comando é a mesma opinião do parágrafo acima. E o estado admite meio-termo honesto: *pronto e
testado, não validado contra o sistema real* é uma resposta melhor que "pronto".

**Envolvido** declara `papel · decide sobre o quê`. Lista de nomes sem o que cada um decide não
resolve a pergunta que importa na hora do impasse, que é *quem bate o martelo nisto*.

### Quando atualizar, e o que entregar ao fechar

**Não é sob demanda.** O quadro se atualiza a cada entrega que muda o estado do
projeto — não quando alguém lembra, e não quando o dono cobra. Cobrança do dono
para atualizar documentação é sintoma de que o mecanismo não existe.

**Ao fechar uma sessão de trabalho, entregue sempre:** onde a documentação está
(caminho), a situação em uma linha, o que ficou parado e **em quem**, e as ações
com responsável e prazo. Curto — relatório longo no fim de conversa longa não é
lido, e relatório não lido não informa ninguém.

**O conteúdo sai do estado, não da memória de quem escreveu.** Se for redigido à
mão, ele diverge do quadro na primeira pressa, e aí existem duas versões da
situação do projeto.

### Ação tem que ser entendida por quem não estava na conversa

Este é o defeito que mais reduz o valor de um quadro, e ele passa despercebido
porque quem escreveu **entende o que escreveu**.

> *"Decidir entre A, B, C e D"* — o próprio dono não soube dizer o que era, e não
> tinha como repassar a um gerente.

A ação diz **o que fazer, em palavras**. O ponteiro para o documento vai num campo
**separado**: assim a referência continua existindo para quem quer conferir, sem
virar pré-requisito para entender.

É verificável por comparação de texto: reprova ação que cite opção por letra,
seção por número ou identificador de item. Não tenta julgar se o texto "está bom"
— isso não é mecanizável, e gate que adivinha qualidade erra e acaba desligado.

### O gate

O estado é verificável por comando, e ele **reprova antes de gerar**: um quadro gerado a partir de
estado inconsistente é pior que quadro nenhum, porque parece confiável. O gate precisa ser
exercitado contra entrada que **deve** reprovar — gate nunca testado é decoração.

---

## §4 — Gates executáveis (nenhum é opinião)

Documentação sem gate apodrece sem avisar. Todo conjunto declara comandos com resposta objetiva.
Os quatro abaixo são o mínimo; adapte os alvos ao projeto.

1. **Link quebrado** — nenhum documento cita arquivo inexistente. *Esperado: 0.*
2. **Fronteira** — a parte reutilizável não cita o domínio consumidor. *Esperado: 0.*
3. **Anti-duplicação** — um número-chave (contagem de referência, total do conjunto) aparece por
   extenso só no arquivo declarado dono. *Esperado: um arquivo, nem mais.*
   **Cuidado:** contar em quantos arquivos a string aparece é gate SINTÁTICO — ele passa enquanto o
   número já está velho. O gate útil confere o número **contra a fonte viva**, não contra si mesmo.
4. **Verdade contra o mundo** — uma consulta que confere as invariantes do produto contra a fonte
   viva. *Esperado: tudo PASS.*

**O gate precisa listar suas próprias exceções e por quê.** Gate que reprova por motivo legítimo é
desligado por quem tem pressa, e nunca mais volta.

---

## §5 — Os 6 modos de falha já observados

Cada um foi pego por revisão adversarial, não por inspeção do autor.

| # | Falha | Como se manifesta | Antídoto |
|---|---|---|---|
| 1 | **Duplicação que o mapa nega** | O mapa afirma que os outros "apontam"; eles copiam | Gate 3 + §2.1 |
| 2 | **Glossário perdido na consolidação** | Termos somem na reorganização e passam a ser usados sem explicação — violando a regra que os próprios documentos formulam | §2.6 + conferir termos antes/depois de toda consolidação |
| 3 | **Nome sem procedência sob cabeçalho que afirma verificação** | Os nomes até existiam; o defeito era a falta de rastro **sob um título que prometia rastro** | §2.2 — a marca vale para o cabeçalho também |
| 4 | **Junção que não dá erro e devolve resultado corrompido** | Chave incompleta combina linhas de origens diferentes; a consulta roda, o número sai, e está errado | §2.3 — a consulta na prova é o que permite alguém ver a junção |
| 5 | **Corrigir só onde o revisor apontou** | O achado é tratado como incidente, não como classe; o mesmo defeito segue vivo em outros cinco lugares | Ao receber achado, **varrer onde o problema existe**, não onde foi apontado |
| 6 | **Polimento que escapa da revisão** | Mudança "pequena" pós-entrega com superfície estrutural real entra sem crítica | Toda mudança estrutural passa por revisão adversarial, inclusive a que parece cosmética |

**O padrão por trás de 1, 3 e 5 é o mesmo: afirmar sem lastro.** Ele só se quebrou quando consertar
um gate defeituoso revelou sozinho uma sexta duplicação que ninguém tinha pedido para procurar.

---

## §6 — Revisão adversarial: quem, e com que instrução

O conjunto documental **não é aprovado por quem o escreveu**.

- **Revisor ≠ autor.** Modelo diferente, ou pessoa diferente. Auto-revisão encontra erro de
  digitação e não encontra racionalização.
- **A instrução é encontrar defeito, não aprovar.** Hipótese default: existe defeito.
- **Veredito explícito:** aprovar · aprovar com ressalvas · reprovar — com achados e evidência.
- **Regra de escalonamento:** três reprovações seguidas na mesma entrega significam que o problema
  é o **desenho**, não a execução. Pare de iterar e reabra a decisão.

*Evidência de que funciona:* no conjunto que originou esta skill, o revisor reprovou 3 vezes em 5
rodadas, e o achado mais grave (modo de falha 4) estava justamente na consulta usada para provar
uma refutação regulatória.

---

## §7 — Prompt de partida

Para iniciar o conjunto num projeto novo, ou auditar um existente:

```
Você vai produzir (ou auditar) o conjunto documental deste projeto segundo o padrão
_shared/project-docs.

ANTES DE ESCREVER:
1. Leia o que já existe. Não crie arquivo para "organizar melhor" — a régua do ganho
   líquido rejeita adição pura.
2. Declare o PORTE (mínimo · médio · completo, §3) e justifique em uma linha.
3. Liste o que já está coberto e por qual arquivo — se houver dono, aponte, não recopie.

AO ESCREVER, cada documento carrega:
- marca de confiança nas afirmações relevantes (§2.2), e DESCONHECIDO onde não se sabe;
- número sempre com data (§2.4);
- termo técnico explicado na primeira aparição (§2.6);
- bloqueio com NOME de quem destrava; decisão em aberto com NOME de quem decide (§2.5).

ENTREGUE JUNTO:
- o ponto de retomada (§2.5), que passa no teste binário do §1;
- as provas do que foi afirmado como CONFIRMADO, cada uma com a consulta exata (§2.3);
- os gates executáveis (§4), rodados, com o resultado colado.

NÃO FAÇA:
- não invente nome de tabela, coluna, número ou regra — DESCONHECIDO é resposta válida;
- não apague crença refutada;
- não renomeie nada já aprovado sem decisão registrada com o custo declarado.

FECHAMENTO: submeta a revisão adversarial por modelo diferente do seu (§6). Você não
aprova o próprio conjunto.
```

---

## §8 — Débito declarado desta skill

- O conjunto graduado do §3 vem de **um** caso real bem-sucedido. Os portes "mínimo" e "médio"
  são **INFERIDOS** por decomposição, não medidos em projeto que os tenha adotado. Quitação:
  aplicar em dois projetos de portes diferentes e registrar o que sobrou e o que faltou.
- Os gates do §4 são descritos por intenção, não entregues como executável genérico — cada projeto
  escreve os seus. Quitação: extrair os dois primeiros (link quebrado, fronteira) para um
  utilitário do framework, se e quando repetirem em três projetos.
- **O §3.1 tem implementação de referência em UM projeto, não no framework.** O gerador de quadro
  com o gate das seis invariantes existe e está exercitado (8 casos que devem reprovar + a
  contraprova de que estado íntegro passa), mas vive no projeto onde nasceu:
  `copiloto-automacoes-sap/tools/quadro.py`. **Deliberadamente não foi promovido aqui**: um
  utilitário genérico extraído de um caso só é exatamente a adição preemptiva que a régua §0
  rejeita, e seria entregar como reutilizável algo nunca exercitado fora do berço. Quitação: ao
  segundo projeto que adotar o §3.1, comparar as duas instâncias e promover **o que sobreviver a
  ambas** — não a união das duas.
- **O registro em `capabilities.json` desta capacidade é `status: PARTIAL` / `enforcement: prose`
  / sem canário — e isso está correto:** o padrão é prosa aqui. Só sobe para determinístico quando
  o utilitário for promovido; declarar mecanismo que não existe neste repositório seria o teatro que
  a auditoria anti-teatro procura. *(A 1ª versão registrou `enforcement: manual`, que neste
  vocabulário significa "script existe, só não está no CI" — e nenhum script existia. Corrigido na
  1ª rodada de revisão; o texto acima ficou desatualizado e foi corrigido na 2ª.)*
