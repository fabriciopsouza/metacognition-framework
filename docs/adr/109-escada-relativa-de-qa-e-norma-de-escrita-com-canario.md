# ADR-109 — Escada de QA relativa ao modelo default, e a norma de escrita ganha canário

- **Status:** Aceito
- **Data:** 2026-08-19
- **Decisores:** dono (Fabricio) — decisão explícita em sessão; autoria Opus 5
- **Crítica adversarial:** Sonnet (junção) e Fable (entrega), isolados. **As duas REPROVARAM**, e os
  achados das duas foram tratados. Não há veredito de aprovação: a rodada que avalia as correções
  ainda não rodou. Listar um crítico como decisor antes de ele responder seria escrever o boletim
  antes da prova — apontado pelo próprio QA de entrega.
- **Emendado por:** **ADR-110** (19/08/2026) — o 2º QA passa a exigir autorização ativa, a
  coordenação entre IAs sai do tier `max`, e *autor sempre default* vira invariante testada.
- **Emenda:** ADR-078 (política de modelo como dado) e ADR-082 (baseline de autor). Não substitui
  nenhum dos dois: troca a forma de expressar a regra de crítica, de **nome de modelo** para
  **posição relativa**.

## Contexto

Duas coisas apareceram no mesmo dia, e as duas nasceram de falha observada, não de ideia.

**A primeira.** O dono cobrou, repetidamente, squad e crítica adversarial em modelo isolado — e ela
**não rodou** durante a abertura de um projeto novo. O conjunto foi escrito, commitado três vezes e
declarado pronto sem crítica externa, e o autor ofereceu *autocrítica* no lugar. Quando a crítica
finalmente rodou, **reprovou**: primeiro Sonnet, com treze achados; depois Fable, achando o pior de
todos — as correções tinham mexido nas fontes e ninguém havia regenerado o que o leitor lê. Substituir
crítico independente por autocrítica é o defeito que o ADR-108 fechou de um lado reaparecendo pelo
outro.

Ao registrar a regra, ficou claro que expressá-la por nome de modelo a condena a envelhecer: cada
lançamento obrigaria alguém a lembrar de atualizar três lugares.

**A segunda.** A seção A.0 de `_shared/output-format/SKILL.md` — *o texto se sustenta sozinho* — era
a única regra transversal do núcleo **sem canário**. Prosa boa, apontada por quase todos os papéis, e
nada que reprovasse quem a desobedecesse. O dono cobrou que o método de escrita seja padrão do
framework, e não preferência de sessão.

## Decisão

**1. A escada de QA passa a ser relativa ao modelo default.** Declarada em
`tools/model-policy.json` como `escada_relativa.ordem` (do menos para o mais capaz) e consumida por
`qa_final_duplo`:

| Papel | Degrau | Resolve hoje |
|---|---|---|
| executor, autor, planejador, arquiteto | o **default** | opus |
| QA adversarial de junção | **um abaixo** | sonnet |
| 1º QA adversarial final | **um abaixo** | sonnet |
| 2º QA adversarial, na **entrega** | **um acima** | fable |
| tarefa mecânica, sem decisão | o **mais baixo** | haiku |

Modelo novo entra na ordem e a regra se ajusta sozinha. O 2º QA é de **entrega** — marco, etapa,
resultado, tarefa, funcionalidade — e não de junção interna: o degrau caro em toda junção encareceria
a prática até alguém desligar o gate, que é como um controle deixa de existir. Na borda da escada, usa
o degrau disponível mais próximo e **declara** no veredito; nunca cai no mesmo modelo do autor em
silêncio.

Papéis de decisão (`architect`, `discovery`, `plan`, `design`, `spec`) saíram do tier `max` para o
`baseline`: o degrau acima não fica ligado por padrão.

**Duas exceções, declaradas porque a afirmação acima é categórica e o arquivo a contradizia em
silêncio:** `risk_override` manda alto-risco, regulado e irreversível para o tier `max`, que começa no
degrau acima — inclusive para papel autoral; e os papéis de **coordenação entre IAs** (`cross-ai`,
`handoff`) continuam resolvendo para `max`. A primeira é intencional: risco declarado fala mais alto que
default. A segunda está **pendente de confirmação do dono** — ela sobreviveu à correção sem justificativa,
e quem ler apenas a frase categórica acima conclui o contrário do que o sistema faz. Apontado pelo QA de
entrega. **[RESOLVIDA em 19/08 — ver ADR-110.]**

**2. A norma de escrita ganha canário** (`tools/test_escrita_padrao.py`, capacidade `escrita-padrao`,
`fail-closed`). Ele verifica três coisas objetivas: que a norma **existe** no arquivo dono; que todo
papel do squad **aponta** para ela; e que a prosa entregue não tem **referência solta** — frase cujo
único conteúdo é um código interno.

**Limite declarado, porque gate que promete demais é desligado:** ele **não** julga qualidade de
redação. Gate que adivinha se um texto está bom erra, e gate que erra é desligado por quem tem pressa
— e aí não protege mais nada. A parte não mecanizável da norma continua cobrável em revisão
adversarial. Exceções listadas no próprio arquivo: tabela, bloco de código, citação, linha de ponteiro,
e o acervo histórico (que é append-only por desenho).

## Régua §0 (ADR-007) — aplicada honestamente

A entrega **adiciona** ao núcleo: um canário novo, um bloco novo na política e uma capacidade nova.

- **Porta (a), funde ou remove ≥ adiciona:** não alegada.
- **Porta (b), reduz tokens ou latência:** não alegada.
- **Porta (c), destrava eval editando existente:** **alegada, e com prova.** O canário novo tornou
  executável uma norma que já existia e não tinha mecanismo, e nesse mesmo movimento **reprovou o
  repositório**: dois papéis do squad não apontavam para a norma, e trechos de prosa de entrada
  citavam identificador sem explicar. Não é adição que espera utilidade futura: ela encontrou defeito
  no ato de ser ligada. **Números com lastro, conferidos pelo QA de junção:** dois papéis do squad sem
  ponteiro (`docops` e `explorer`) e **dois** trechos de prosa com referência solta (`AGENTS.md` e
  `AGENT-FRAMEWORK.md`). A primeira versão deste ADR dizia "três trechos" e não tinha prova do terceiro.

A parte da escada relativa é **substituição de forma**, não adição de norma: a regra de
heterogeneidade já existia por nome; passou a existir por posição.

**Débito declarado, para o override não virar permissão permanente:** o `qa_final_duplo` é **dado, não
mecanismo**. Nenhum gate verifica hoje que um bloco fechou com o degrau abaixo e depois com o degrau
acima — `qa_evidence.py`, `verify_qa_attestation.py` e `squad_gate.py` seguem falando de um crítico por
bloco. O que existe é o canário que impede a política de ser apagada ou alterada em silêncio. Cabear o
duplo é parte da pendência prioritária registrada no `history.md` — e o critério de aceite dela **foi
emendado para incluir o duplo**, porque na versão anterior falava de "a crítica adversarial", no
singular, e podia ser fechado com **um** crítico automático enquanto o segundo morria sem ser cobrado.
Apontado pelo QA de entrega. O critério passa a ser: abrir projeto novo em pasta virgem, a crítica do
degrau abaixo rodar **sem ninguém pedir**, a do degrau acima rodar **na entrega**, e o bloco **falhar
visivelmente** se o runtime proibir qualquer uma das duas.

## Consequências

**Boas.** A regra de crítica sobrevive ao próximo lançamento de modelo. O custo fica sob controle: o
crítico barato derruba o óbvio, o caro só paga o que sobrou, e só na entrega. A norma de escrita deixa
de depender de alguém lembrar.

**Ruins, e assumidas.** O núcleo cresce. A ordem da escada é um dado que alguém precisa manter quando
surgir modelo novo — mas é **um** lugar, e o canário reprova quem o esvaziar. E o QA duplo continua
cumprido pelo orquestrador, não imposto por código: até o débito acima fechar, ele é cobrável em
revisão e não travado por mecanismo.

## Alternativas recusadas

**Manter a regra por nome de modelo.** Recusada: envelhece a cada lançamento, e a manutenção depende de
alguém lembrar de três lugares.

**Rodar o degrau acima em toda junção.** Recusada por custo: encareceria a prática até alguém
desligá-la, o que é pior que não tê-la.

**Canário que pontua qualidade de redação.** Recusada: não é mecanizável, e gate que erra é desligado.
Melhor um canário estreito que prende do que um amplo que ninguém deixa ligado.
