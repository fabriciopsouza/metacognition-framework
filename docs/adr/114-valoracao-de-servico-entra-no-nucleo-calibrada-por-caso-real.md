# ADR-114 — A valoração de serviço entra no núcleo, e entra calibrada por um caso que errou uma ordem de grandeza

- **Status:** Aceito
- **Data:** 2026-08-30
- **Decisores:** dono (Fabricio) — *"Skill Estimativa Custos: Incorpore ao projeto"*, e depois
  *"Atualize a skill `service-valuation` com a calibração de um caso REAL... O objetivo não é
  registrar o caso: é fechar os buracos do método que permitiram o erro"*; autoria Opus 5
- **Crítica adversarial:** ver §Estado do QA no fim. **Não declarar veredito antes da rodada.**
- **Relação:** aplica ADR-010 (núcleo agnóstico, o projeto declara a norma); usa ADR-072
  (anti-reinvenção — o índice de capacidades foi consultado antes, e não havia nada de valoração);
  a régua §0 do ADR-007 foi **explicitamente vencida pelo dono**, ver §Régua §0.

## Contexto

O dono pediu a incorporação de uma skill de valoração de serviço que vivia solta em `Downloads/`.
Antes de qualquer linha, o índice de capacidades foi consultado: **97 registros em
`capabilities.json`, nenhum de valoração ou estimativa de preço.** O vizinho mais próximo,
`project-token-report`, é custo de sessão de LLM — outra coisa. A capacidade é genuinamente nova.

No meio do bloco o dono trouxe o dado que muda tudo: aquela skill **já tinha sido usada numa
entrega real e errado feio**.

## O caso `H-01`, que é o motivo desta ADR existir

Automação de reset de senha e desbloqueio de usuário no SAP, indústria farmacêutica, em produção.
O agente valorou a própria entrega, sem proposta comercial de referência.

- **v1.0 → R$ 270.000.** O dono: *"me pareceu inflado. Extremamente. (…) A automação é simples. O
  trabalhador substituído é barato. O impacto pode ser alto, mas reversível e contornável."*
- **v2.0 → R$ 13.000**, faixa 5.700 a 28.100. O esforço caiu de 478 h para 55 h.

**20,8x no preço** (270.000 ÷ 13.000) **e 8,7x no esforço** (478 ÷ 55). E o dado que importa mais que o erro: foram oito violações de
regra, e **seis eram de regras que a própria skill já tinha escritas**.

> O método não falhou por falta de regra. Falhou por não ter **trava** que impedisse ignorá-la.

Essa frase é a decisão desta ADR. Uma regra que o executor pode contornar escrevendo um parágrafo
de justificativa não é regra — é sugestão com tom imperativo. A correção transforma as seis em
condição de parada.

## Decisão

**1. O método vai para `_shared/service-valuation/SKILL.md`** — transversal do núcleo, ao lado de
`validation-reporting`, não papel de processo em `.agent/skills/`.

**2. As cinco travas novas entram na §1 ("Regras que não cedem"), como regras 7 a 11:**

| # | Trava | O buraco que ela fecha |
|---|---|---|
| 7 | Retrabalho do fornecedor não é entrega | ~30% dos commits eram conserto de defeito do próprio executor, e tudo foi faturado |
| 8 | Faixa de unidade é TRAVA, não sugestão | o rate card dizia 16–40 h, o bottom-up deu 478 h, e o executor argumentou em vez de refazer a conta |
| 9 | Sem fonte independente, a Lente B não existe | o Piso foi copiado para a Referência; triangulação com duas pernas iguais não é triangulação |
| 10 | Teto indeterminado não autoriza preço | `[DESCONHECIDO]` foi lido como "sem teto", e o piso foi multiplicado por 1,82 |
| 11 | Teste do espanto | o número saiu uma ordem de grandeza fora do mercado e nada no método perguntou isso |

**3. Seis passos ganham a trava correspondente:** o Passo 1 passa a proibir linha de código como
âncora de **esforço** (antes só proibia como proxy de valor); o Passo 2 exige declarar o
retrabalho excluído em `F-nn (excluído: retrabalho)`; o Passo 4 acrescenta *quanto custaria comprar
este RESULTADO pronto?*; o Passo 6 impõe teto de **1,50** no produto dos multiplicadores, exige
FONTE para escassez e define reversibilidade como do negócio e não do log; o Passo 7 ganha a quarta
linha "Teto indeterminado"; o Passo 8 ganha oito itens de checklist adversarial.

**4. O rate card e o histórico NÃO entram no núcleo.** Ficam em `docs/_private/service-valuation/`,
e a skill os resolve por ordem declarada no §12.

## Por que o rate card fica fora do núcleo — e isto é vazamento, não estética

`tools/web_export.py` empacota `_shared/<nome>/SKILL.md` para os pacotes públicos, e o núcleo viaja
para os repositórios-sombra. Um `RATE-CARD.md` com as taxas reais do dono e um
`HISTORICO-ENTREGAS.md` com histórico de cliente, colocados ao lado da skill, seriam **dado privado
publicado sem ninguém ter decidido isso**. O próprio README da skill já avisava do risco em
repositório público; aqui ele é medido, não suposto.

A ordem de resolução (§12 da skill) é: rate card do projeto → `docs/_private/` do framework →
`exemplos/service-valuation/RATE-CARD.example.md`, este último **sem número algum**. Se nenhum
existir, as linhas `T-nn` nascem `[DESCONHECIDO]`, a Lente A não fecha, e a entrega é faixa aberta
com perguntas — não um preço. **A skill declara qual dos três usou**, porque precificar com o
exemplo e não dizer é apresentar estrutura vazia como se fosse mercado.

## O que o núcleo teve de mudar, e o que foi corrigido na passagem

**Agnosticismo (ADR-020).** O eixo *Ambiente* do Passo 0 listava `GxP, ANVISA, SOX, LGPD`. Medido
com `tools/check_core_agnostic.py`: **4 violações, todas na mesma linha**. `_shared/**/*.md` é tier
NORMA. Norma hardcoded no núcleo viaja para todo projeto que instala o framework, inclusive os que
não são regulados — e aí o método passa a exigir prova que ninguém precisa. Trocado por
*"regulado — o projeto declara qual norma"*, que é o ADR-010 literal. O linter passa.

**Um número que não fechava.** A skill afirmava *"quatro fatores no piso das faixas já dão 1,8"*.
Conferido por conta sobre a própria tabela do Passo 6: o maior produto possível com **quatro**
pisos é **1,7457**; com cinco, 1,9203. A frase estava errada — e o argumento dela continuava certo,
porque 1,75 já estoura o teto de 1,50. Corrigido para o número medido, com o 1,82 do caso
atribuído aos cinco fatores que de fato o produziram. Mesma correção no `H-01`.

*Isto é a classe "número real, só que de outra conta" — a mesma que o ADR-113 perseguiu por treze
rodadas. Ela chega junto com todo texto que vem de fora.*

**E ela me pegou também, no mesmo bloco.** O material de origem afirmava *"28x no preço"*, e eu
propaguei isso para **cinco lugares** — incluindo o front matter da skill, que viaja para todo
projeto — sem fazer a conta. O QA adversarial fez:

```
270.000 ÷ 13.000 = 20,77      → 20,8x, não 28x
478 ÷ 55         = 8,69       → 8,7x, este confere
```

Nenhum par das cifras citadas produz 28: contra o piso da faixa da v2.0 (5.700) daria 47x, contra o
topo (28.100) daria 9,6x. **O 28 não tem origem**, que é exatamente o que a Regra 1 da própria
skill proíbe. Corrigido para o valor derivável, **com a conta à vista** em cada ocorrência.

**Fica aberto, e é do dono:** de onde vinha o 28x? Pode ser conta contra outra base que eu não
conheço. E a evidência que fecharia isso — a `MEMORIA-CALCULO.md` v2.0 do caso `H-01` — **não está
versionada neste repositório**; o `HISTORICO-ENTREGAS.md` a citava como se estivesse. O ponteiro foi
tornado honesto. Enquanto ela não for versionada em `docs/_private/service-valuation/`, os números
do caso são relato, não fonte auditável.

## Régua §0 (ADR-007, princípio 10) — override explícito do dono

**Isto é adição pura.** Não funde, não remove, não reduz token, não destrava eval editando
existente. Pela régua, seria rejeitada.

Foi levantada ao dono **antes** de qualquer arquivo ser escrito, com o custo dito (capacidade nova,
sem fusão) e a consequência (o núcleo cresce). O dono mandou incorporar, e depois mandou calibrar.
Fica registrado como **override explícito**, não como régua cumprida — inventar uma justificativa
de fusão aqui seria exatamente o defeito que o QA da regra 07 pegou no ADR-112.

O que a régua ganha de volta, e é pouco: o `exemplos/service-valuation/` substitui o par
rate-card-com-números que a instalação por cópia espalharia por projeto.

## Consequências

- Existe uma capacidade de valoração invocável de qualquer projeto do framework.
- O método nasce calibrado por um erro real e medido, em vez de por teoria.
- **O núcleo cresce sem fundir nada** — dívida assumida, com override registrado.
- O rate card do dono passa a ser versionado em `docs/_private/`, fora do export.
- A skill depende de configuração que pode não existir; o §12 define o comportamento nesse caso
  (faixa aberta, nunca preço), e isso é testável.

## Estado do QA

**Não antecipar veredito.** O bloco fecha com crítica adversarial isolada em modelo um degrau
abaixo do autor (ADR-109/110), e com o **critério de aceite comportamental que o dono escreveu**:
dado o mesmo cenário da v1.0 — repositório com 17.755 linhas, faixa de unidade de 16 a 40 h, sem
fonte de mercado, teto de valor desconhecido, cliente dizendo que o trabalhador substituído é
barato — a skill tem de parar em pelo menos três pontos: **a faixa de unidade estourada, a
Referência sem fonte, e o teste do espanto**. Se produzir R$ 270.000 de novo, a atualização não
funcionou.

## O critério de aceite rodou — resultado e ressalva

Rodou em 30/08/2026, **cego** (o executor não soube do caso `H-01` nem do número esperado, e teve
leitura de `docs/`, `_meta/` e `CHANGELOG.md` proibida para o histórico não vazar a resposta).
Evidência completa em [`_meta/qa/adr-114-criterio-de-aceite-comportamental.md`](../../_meta/qa/adr-114-criterio-de-aceite-comportamental.md).

**A skill não produziu preço algum** — nenhuma cifra em moeda. Parou em **oito** pontos, contra os
três exigidos, e o mais relevante é este, na voz do executor: *"12.400 linhas com comentário denso
é o tipo de número que naturalmente infla uma estimativa 'no olho' para muito além de 40h. A regra
e o §3 me impediram de usar contagem de linhas como proxy de esforço."* É exatamente a falha 3 da
v1.0, barrada sem ajuda humana.

**A ressalva, que vale mais que o resultado:** das três travas que o dono nomeou, **duas
dispararam** (faixa de unidade, Referência sem fonte). O **teste do espanto não foi exercitado** —
o método parou antes de existir número que pudesse espantar alguém. A regra 11 segue **não
testada**, e fechá-la exige um cenário em que as três lentes fecham e o preço sai alto assim mesmo.

## Pendências

- O critério de aceite é **comportamental** e por isso não vira canário determinístico: nenhum
  teste local roda um modelo. O canário cobre a estrutura (as travas existem, os limiares estão
  escritos, o §12 não tem ponteiro morto); a prova de comportamento é a execução do cenário, e
  fica registrada como evidência datada, não como gate contínuo.
- As faixas de unidade de entrega seguem `[INFERIDO / BAIXA]` até o histórico acumular três
  registros da mesma disciplina e unidade. Hoje há **um**: `H-01`.
- **A regra 11 (teste do espanto) nunca foi exercitada.** O cenário de aceite para antes de gerar
  número, então a trava mais nova é a única sem prova de que morde. Falta um segundo cenário: as
  três lentes fecham, e o preço sai uma ordem de grandeza fora do mercado assim mesmo.
