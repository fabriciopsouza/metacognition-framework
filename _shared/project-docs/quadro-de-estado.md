> Parte de `_shared/project-docs/SKILL.md` (entrada enxuta desde 28/09/2026, B3c). Conteúdo copiado integral da versão anterior; a entrada aponta para cá.

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
