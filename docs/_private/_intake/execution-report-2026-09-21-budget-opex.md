# Execution report — 21/09/2026 — budget-opex (OPEX de TI em regime de caixa)

**Projeto:** `C:\Users\fabriciosouza\budget-opex` (repo privado)
**Estado do projeto:** [`ESTADO-ATUAL.md`](../../../../budget-opex/ESTADO-ATUAL.md)
**Entregue:** `OPEX TI 2026.xlsx`, 2 abas · 21 commits · 12 gates · 5 guardas · 2 rodadas de QA adversarial

---

## O que o bloco produziu

Extração do realizado de TI no SAP em **regime de caixa** (`AUGDT`), conciliada contra a
planilha de budget, entregue em duas abas: a **resposta** (311 linhas × 14 colunas, só
contas geridas pela TI) e a **base filtrável** (3.625 × 31).

Números de fechamento: caixa **R$ 2.682.350,66** · competência-faturas R$ 2.894.120,40 ·
competência-resultado R$ 2.674.215,42. Os três corretos, filtros diferentes.

---

## As lições que valem para o framework

### 1. O eixo de um gate tem que ser ALHEIO à regra que ele julga

Aconteceu **duas vezes na mesma sessão**, e a segunda depois de eu ter escrito a lição da
primeira.

**Primeira:** o gate era `soma dos baldes == soma da fonte`. Com partição exaustiva essa
igualdade é verdadeira para *qualquer* regra de classificação. Sabotando o critério, o
entregável caía de R$ 2,83 mi para **R$ 385,40** com tudo verde.

**Segunda:** troquei por gates de propriedade, mas os novos consultavam `dim_conta.csv` —
a **mesma fonte que decidia o balde**. Apagar `area_gestora` de **uma** conta tirava
**R$ 1.184.547,35** da aba do diretor com os **11 gates verdes**.

> Um gate só prova alguma coisa se o eixo dele for **independente da decisão**. O eixo
> que funcionou foi o **arquivo de budget**, de onde a dimensão nasce.

### 2. Partição tem DUAS bordas, e balde novo exige gate novo

Guardei "nada patrimonial entra na aba do diretor" e esqueci "nada de resultado sai dela".
O erro grave é quase sempre o de **exclusão** — silencioso, o número só encolhe. Depois,
ao criar um terceiro balde, repeti: balde novo sem gate novo é buraco, e a mutação pegou
no mesmo minuto.

### 3. Guarda que não consegue barrar é relatório

`python guarda.py | tail -2 && git commit` — o `tail` é o último comando do pipe, então o
código de saída é **dele**. O `&&` nunca bloqueia. Commitei duas vezes com guarda
vermelha, e caí na mesma armadilha *ao testar o hook que a corrigia*.
Saída: um `verifica.py` único, sem pipe, ligado como **pre-commit**, e **provado** com um
commit que deve falhar.

### 4. Literal copiado de uma medição não sabe que a premissa mudou

Digitei 7 contas numa consulta a partir de uma medição com filtro `006`. O filtro do
entregável depois virou `006+007`, e a conta nova entrou no escopo **sem entrar na lista**.
A correção não foi acrescentar a conta — foi **trocar o literal por uma subconsulta**.

### 5. Duas listas mantidas à mão divergem, e a divergência começa pequena

A semântica estava em **cinco lugares**. Uma cópia já tinha derivado: R$ 289,00 caindo em
"sem categoria" por uma lista desatualizada. Hoje é R$ 289; é o mecanismo que produz erro
grande depois.

### 6. Medir o catálogo errado é concluir ausência que não existe

`SYS.TABLES` não lista *views*. Concluí que `BSAK` não existia, **reescrevi a documentação
afirmando isso**, e ela funcionava. Errei duas vezes no mesmo ponto, e a segunda foi a
"correção".

### 7. Probe serve para decidir o que escrever — não depois

Escrevi que o bloco de probe devia rodar **antes** da consulta principal e, mesmo assim,
já tinha posto o campo não confirmado dentro dela. Quem executasse de cima para baixo
batia no erro nas duas.

### 8. O dado desmentiu os dois lados de uma discussão de dicionário

Eu usei `ZBD1T`; o QA apontou pelo dicionário SAP que o prazo líquido é `ZBD3T`; aceitei e
corrigi. Medido: **`ZBD3T` = 0 em 422 de 422** e `ZBD1P` = 0 — sem desconto, `ZBD1T` **é**
o prazo. A crítica estava certa no dicionário e errada no sistema.
**Quem salvou foi a cascata**, que não precisou escolher.

### 9. Canário que grita sempre é canário ignorado

A primeira versão do verificador de referências acusou 40 quebradas, quase todas falsas.
Joguei fora e refiz: só cita em `code span`, conhece os diretórios externos, e **separa
PENDENTE de QUEBRADA** — "ainda não" não é "errado".

### 10. A legenda do próprio arquivo pode ser o oráculo do leitor

A planilha grava a legenda em **RGB literal** e os dados em **cor de tema** — duas
gravações da mesma cor. Resolver o tema tem que cair em cima do RGB da legenda
(`E2EFDA` × `E2F0D9`, distância 1). O valor esperado fica **no arquivo do dono**, não no
código — o oposto do teste que lê a própria constante.

---

## Onde o framework não me pegou

| Falha | Gate que existia | Por que não pegou |
|---|---|---|
| Gate tautológico (2×) | mutação | a mutação só cobria a fronteira antiga |
| Commit com guarda vermelha (2×) | canário | o pipe engolia o código de saída |
| Heredoc colapsando `\` (3×) | memória registrada | a memória existia; eu não a apliquei sob pressa |
| Documentação apontando para arquivo renomeado (3×) | nenhum, no início | virou o canário de referências |

> O padrão: **três das quatro já tinham lição escrita na memória.** O que faltou não foi
> conhecimento — foi **mecanismo que impedisse**. Toda lição desta sessão que virou
> ferramenta (`verifica.py`, `check_referencias.py`, mutação da dimensão, teste da
> legenda) nasceu de um erro que a prosa não tinha evitado.

---

## Sugestão ao núcleo (não aplicada — bloco de outra sessão)

A árvore do framework está na branch `feat/enforcement-que-viaja-para-projeto-novo` com
**97 arquivos staged de outra sessão**. Não toquei em nada além deste relatório, e **não
dei push** — push moveria o `HEAD` da branch dela e pode orfanar `sha_revisado` de QA
alheio.

Duas coisas que talvez mereçam virar regra do núcleo, para o dono decidir:

1. **`verifica.py` + pre-commit** como padrão de projeto de domínio: guarda que não
   consegue barrar não é guarda. O template poderia nascer com isso.
2. **Critério de aceite de gate**: "os gates passaram" não é evidência. O critério é
   *a sabotagem foi pega* — e a sabotagem precisa cobrir **cada fronteira**, não a
   primeira. Hoje a régua §0 fala de ganho líquido; não há régua sobre cobertura de gate.
