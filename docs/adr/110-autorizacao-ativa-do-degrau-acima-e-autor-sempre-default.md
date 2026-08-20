# ADR-110 — O degrau acima só roda autorizado, e o autor é sempre o default

- **Status:** Aceito
- **Data:** 2026-08-19
- **Decisores:** dono (Fabricio) — três decisões explícitas em sessão; autoria Opus 5
- **Crítica adversarial (degrau abaixo, Sonnet isolado, duas rodadas):** a **rodada 1 REPROVOU** com
  cinco achados — dois ALTA, dois MÉDIA, um BAIXA — e um dos ALTA falsificou por execução uma
  afirmação categórica deste próprio ADR (§Decisão 4). Tratados. A **rodada 2**, sobre as correções,
  devolveu **APROVADO_COM_RESSALVAS** e achou **um defeito novo**, introduzido pela própria correção:
  o teste de espaço cobria um subconjunto do espaço declarado. Também tratado, e provado por mutação.
  **Não há veredito de aprovação limpa**, e este campo não antecipa nenhum — é a classe fechada pelo
  ADR-108 e cometida no ADR-109 no dia anterior.
- **Emenda por seção:** ADR-109 (escada relativa de QA). Não o substitui: a escada continua relativa e
  a tabela continua valendo. O que muda é **quando** o degrau acima dispara, **quem** alcança o tier
  `max`, e o **casador** que resolve papel → tier.

## Contexto

Três coisas apareceram no mesmo dia, e nenhuma nasceu de ideia.

**A primeira foi conta.** O ADR-109 mandou todo bloco fechar com dois QA adversariais finais, o
segundo no degrau acima do default. Rodado por reflexo, esse degrau **esgotou a janela de 5h de tokens
de uma sessão inteira**. O custo dele não recai sobre a tarefa que o invocou: recai sobre a sessão,
inclusive sobre o trabalho que ainda nem começou.

**A segunda era dívida.** O ADR-109 afirmava, de forma categórica, que o degrau acima não fica ligado
por padrão — e o próprio arquivo o contradizia: os papéis de coordenação entre IAs continuavam
resolvendo para o tier `max`, com a exceção marcada como *pendente de confirmação do dono*.

**A terceira apareceu ao escrever a segunda.** Ao fixar que o autor roda sempre no default, ficou a
pergunta: isso é regra ou é expectativa? Era expectativa — e ao virar teste, caiu na primeira execução.

## Decisão

**1. O degrau ACIMA do default só roda com autorização ativa.** Ele roda em dois casos, e só nesses
dois: o dono **ordenou**, ou o orquestrador **perguntou** — dizendo o que seria criticado e que o
degrau acima custa mais — e o dono **autorizou**. Sem resposta ativa, o bloco fecha com o 1º QA e o
veredito **declara** que o 2º não rodou e por quê. `"siga"`, `"ok"` e o silêncio não autorizam:
autorizam continuar o escopo declarado, que é outra coisa.

A entrega é **quando ele deve ser oferecido**, não quando ele dispara. Omitir a oferta na entrega é
falha do orquestrador; dispará-lo sem autorização também.

> **O 1º QA não mudou, e isto precisa estar escrito porque foi violado no ato:** o degrau **abaixo** do
> default é **automático e obrigatório**, em toda junção e no fechamento, e **roda sem pedir licença a
> ninguém**. No dia desta decisão o orquestrador pediu autorização para ele — e não devia. Só o degrau
> acima, que é o caro, passa pelo gate. Nenhuma regra posterior de confirmação interativa cobre o QA
> obrigatório (ver ADR-111).

Dado em `qa_final_duplo.passo_2.autorizacao` e `passo_2.default_sem_resposta = "NAO RODA"`. O default
na ausência de resposta tem de ser *não roda*: qualquer outro devolve o automatismo pela porta dos
fundos.

**2. Coordenação entre IAs (`cross-ai`, `handoff`) desce do tier `max` para o `baseline`.** Coordenar
handoff é coordenação, não crítica adversarial — não é o papel que justifica pagar o degrau caro, e era
a última porta que o abria **por papel**, sem autorização e sem ninguém perceber.

**Consequência estrutural, que é o ponto:** o tier `max` **deixa de ser alcançável por papel**. Só por
`risk_override` — alto-risco, regulado, irreversível — que **fica de propósito**, porque é gate de
segurança e não de custo. Verificado resolvendo **todos** os papéis declarados, não por leitura: nenhum
abre o degrau acima sem risco declarado, e o canário reprova quem devolver `cross-ai` ao tier `max`.

**3. O autor é sempre o default — invariante, não expectativa.** Nenhum papel autoral roda **abaixo**
do baseline, e nenhum roda **acima** sem autorização. A única saída por baixo é indisponibilidade
declarada, e mesmo essa é anunciada. Com ela valendo, o ramo `heterogeneous_preference.order_otherwise`
— o último que ainda apontaria um crítico para o tier `max` — fica **dormente**.

**4. O casador de papel foi consertado na raiz.** A invariante caiu na primeira execução:
`docops-generative` estava declarado como papel autoral desde o ADR-082 e resolvia para `haiku`, dois
degraus abaixo do default — o *"proibido silencioso"* que o próprio `baseline_author` descreve.

A causa **não era a lista, era o casador**: ele parava no primeiro casamento por substring **na ordem
do arquivo**, então a chave curta `docops` engolia a longa `docops-generative`. Agora, entre chaves em
relação de **contenção**, vence a que **contém** a outra — e para esse par a posição no arquivo deixou
de importar, provado permutando a ordem. Só para esse par: ver a correção abaixo.

**Fora da contenção, a ordem continua mandando — e ela É a precedência.** `roles` é lido em ordem, e
essa ordem codifica **segurança > autoral > mecânico**: a regra `qa/critic` é a primeira para que QA vá
sempre a modelo heterogêneo (ADR-018), e a regra autoral (`developer`) vem **antes** da mecânica
(`docops`/`economy`). A exceção de contenção resolve só o caso genérico-engole-específico.

**Correção, porque a primeira versão deste ADR afirmou mais do que entregou.** Ela dizia que com o
conserto *"a classe de bug some para todo papel futuro"*. **O QA de junção falsificou a frase com
execução**: `developer docops` resolvia para `haiku` — papel autoral dois degraus abaixo do default —
porque `developer` e `docops` são chaves **independentes**, nenhuma contém a outra, e a regra mecânica
vinha antes no arquivo. O conserto tinha coberto **um par**, e o autor chamou isso de classe. A ordem
foi acertada e a asserção passou a percorrer o **produto cartesiano** chave-autoral × chave-mecânica
(`test_handoff.py`), que sob mutação acusa **112** composições — enquanto o crítico havia achado seis.
A lição fica registrada porque reaparece: *"consertei na raiz"* é afirmação de classe, e afirmação de
classe exige teste de espaço, não exemplo que passa.

**E a lição reapareceu na rodada seguinte, uma camada acima.** O conjunto de chaves autorais do teste
cartesiano vinha de uma lista **escrita à mão** — `developer`, `author`, `autor` — que deixava
`architect` e `discovery` de fora, embora ambos estejam em `author_roles`. Reordenar a regra
`architect` reproduziria o mesmo bug sem nada apitar. O conjunto passou a ser **derivado do próprio
arquivo** (toda regra de tier `baseline`), e a mutação que antes passava muda agora acusa 96
composições. Lista escrita à mão dentro de um teste envelhece igual à prosa que o teste deveria
substituir — foi preciso um segundo crítico para ver isso, e é o argumento empírico a favor do QA
que roda sempre, e não quando alguém acha que precisa.

**A recusa do longest-match puro também foi medida, e a medição virou artefato.** Trocar a regra por
ele resolvia este bug e criava dois piores — `qa do docops` caía para `haiku` (heterogeneidade do
ADR-018 perdida) e `verificar o design` ia para o arquiteto. A prova durável não são os números desta
sessão: é o canário, que reprova qualquer reordenação que ponha um papel autoral abaixo do default e
qualquer configuração que tire QA do degrau heterogêneo — esta segunda metade **era falsa quando
foi escrita** e só passou a ser verdade depois que o 2º QA a falsificou por execução e o cartesiano
QA × demais entrou no canário. Números de sessão sem artefato foram achado
MÉDIA do mesmo QA, e esta versão os substitui por asserção executável.

## Régua §0 (ADR-007)

- **Porta (a), funde ou remove ≥ adiciona:** parcial. A decisão 2 **remove** uma rota; a 4 **substitui**
  lógica em vez de acrescentar. A decisão 3 adiciona um campo e uma regra de papel.
- **Porta (c), destrava eval editando existente:** **alegada, com prova.** O laço sobre `author_roles`
  transformou lista decorativa em contrato e **reprovou no ato**, achando um papel autoral em `haiku`.
  Três correções desta série foram verificadas por **teste de mutação**, não por leitura.

**Honestidade sobre a primeira tentativa:** a correção original do achado 4 foi **adicionar uma rota de
modelo para uma string que ninguém envia** — o defeito era de documentação e foi "corrigido" inchando o
núcleo, que é exatamente o que a régua §0 rejeita. O dono mandou revisar; a revisão achou a causa real.

## Consequências

**Boas.** O degrau caro deixa de consumir orçamento por inércia. O tier `max` vira exceção pedida, não
default herdado. E a ordem de `roles`, que era uma armadilha silenciosa, passa a ser **declarada como
precedência e testada**: quem reordenar as regras e puser um papel autoral abaixo do default é
reprovado, em vez de descobrir meses depois que um autor rodava em haiku.

**Ruins, e assumidas.** O 2º QA passa a depender de alguém lembrar de autorizá-lo, e a classe de defeito
que só ele pega volta a escapar quando ninguém autoriza. É preço aceito: o gate que estoura o orçamento
da sessão é desligado de vez, e gate desligado protege menos que gate ofertado. A mitigação é o dever de
**oferecer**, cobrável em revisão.

**Débito declarado.** Este bloco continua **dado, não mecanismo**: nenhum gate verifica que um bloco
fechou com o 1º QA nem que o 2º, quando rodou, foi autorizado. O que existe é o canário
`test_handoff.py`, que impede a política de ser apagada ou afrouxada em silêncio. Cabear o duplo segue
na pendência prioritária do `history.md`.

## Alternativas recusadas

**Longest-match puro no casador.** Implementada e **medida** sobre o conjunto de frases de papel da
sessão: mudou resoluções, duas delas regressões sérias — `qa do docops` para o degrau mecânico e
`verificar o design` para o arquiteto. Recusada por evidência, não por gosto. O que ficou no repositório
não é o número da medição, e sim o canário que reprova as duas regressões.

**Tirar `docops-generative` da lista de papéis autorais.** Era a opção mais enxuta e teria fechado o
achado sem tocar em código. Recusada pelo dono, que preferiu consertar a raiz — decisão que se
pagou: a classe de contenção deixou de depender da ordem do arquivo. **Não** "some para todo papel
futuro": essa é exatamente a frase que o QA falsificou acima, e ela havia ressuscitado aqui,
verbatim, no mesmo documento que narra a falsificação — achado BAIXA do 2º QA (Fable). Contar a
mesma história em cinco lugares é como uma versão corrigida sobrevive ao lado da versão errada.

**Manter o degrau acima automático na entrega.** Era a decisão do ADR-109, e durou um dia. Recusada por
evidência: esgotou a janela de tokens de uma sessão de 5h.
