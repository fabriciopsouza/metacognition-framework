# Emendas ao prompt de retomada — medidas em 13-14/08/2026

Cole isto **junto** com o prompt original. Tudo abaixo foi medido, não lido. Cada item traz o
comando que reproduz.

---

## Parte 1 — Quatro afirmações do prompt que não se sustentaram

### 1.1 §3 está errado: a suíte NÃO está vermelha na `main`

Medido em worktree limpo de `origin/main`, duas rodadas idênticas:

    66 PASS · 1 SKIP · 0 FAIL (de 67 canários)

O prompt diz "64 PASS · 1 SKIP · 3 FAIL, 68 canários". Esse resultado é **local de um ramo**, não
da `main` — a hipótese (c) do próprio §3. Seguir o §3 como está manda caçar na `main` um defeito
que ali não existe, e a caçada termina "consertando" o que está certo.

**Substitua o §3 por:** meça a `main` primeiro, em worktree separado. Só depois compare com o ramo,
e a diferença é o achado.

    git worktree add --detach /tmp/wt origin/main && cd /tmp/wt && python tools/run_canaries.py

### 1.2 §2 troca a autoria da colisão do #117

O #117 foi criado às **22:15 (local)** de 13/08 pela sessão do repositório irmão, e **mergeado às
22:57** por `fabriciopsouza`. A outra sessão tentou criá-lo depois e encontrou o dela já existindo —
a colisão é real, mas quem chegou primeiro é o inverso do que o prompt diz.

Hoje o #117 está **MERGED**. Os três PRs abertos que o prompt lista (#118, #116, #108) conferem.

### 1.3 Metade das "anomalias de cronologia" do §2 é fuso horário

`git log` imprime em horário local (−03); `gh` imprime em UTC. O mesmo evento aparece como 22:57 e
como 01:57Z. O "commit 23:10 posterior ao merge de 22:57" some quando os dois lados são lidos no
mesmo fuso.

**Acrescente ao §2:** todo horário citado declara o fuso, e comparação entre `git` e `gh` converte
antes de concluir.

### 1.4 §6 pendência #2: o número 31 não tem fonte

Medido em `capabilities.json`:

- **81** capacidades no total
- o campo `PROVIDES` **não existe no schema** — a string aparece só dentro de um título
- `enforcement` ausente em **35** delas

O ADR-106 (35) está certo; o "31 capacidades PROVIDES" do prompt não vem de lugar nenhum. A
pendência é real; o recorte não é.

---

## Parte 2 — Achado principal: o parecer de QA é sobrescrito no lugar

Três vereditos, um arquivo, uma release:

| quando (local) | commit | veredito |
|---|---|---|
| 13/08 11:13 | `4faf971` | aprovar_com_ressalvas |
| 13/08 11:38 | `9e586fd` | **reprovar** |
| 13/08 22:48 | entrou no merge `30ab957` | aprovar_com_ressalvas |

A terceira rodada é **legítima** — houve correções entre uma e outra. O defeito não é essa; é o
mecanismo:

1. **O parecer não nomeia o código que revisou.** Nenhum SHA, nenhuma árvore. Só o número da
   release, que não muda quando o código muda.
2. **O campo `data` é escrito pelo próprio revisado.** Está literal no arquivo:
   `"data": "2026-08-14T01:48:52Z"`.

**Consequência de primeira mão, nesta sessão:** li o parecer às 22:0x, encontrei `reprovar`, decidi
não mergear e **reportei isso ao dono como fato**. Nove minutos antes do merge existia uma rodada
nova. Eu estava lendo um retrato válido de um estado já superado, e o arquivo não tinha como me
dizer isso.

**Isto qualifica o PR #118.** Ele faz o gate exigir *recência* do veredito — mas contra o campo
`data`, que quem é revisado preenche. Um gate que confere recência num carimbo autodeclarado
**confere uma alegação, não um fato**. É o mesmo defeito de desenho que o §4 já aponta em
`escopo_paths` ("escrito pelo mesmo agente que ele deveria barrar"), e o `data` está no mesmo saco.

**Reparo a levar ao dono (muda contrato, não decidir sozinho):** o parecer grava o SHA da árvore
que revisou; o gate recalcula esse SHA na hora e compara. Aí a pergunta deixa de ser "o carimbo é
recente?" e passa a ser "isto é o código que foi revisado?" — que é verificável sem confiar em
ninguém.

---

## Parte 3 — §9.1 é pior do que a suspeita, e a prova de mutação está feita

O prompt pergunta se `handoff.py` num repo sem remote **falha, avisa, ou entrega pacote
irrecuperável**. Executado:

    T=/tmp/repo-sem-remote; mkdir -p $T; cd $T; git init
    echo "objetivo: teste" > docs/briefing.md; git add -A; git commit -m inicial
    python /caminho/do/framework/tools/handoff.py

Resultado: **EXIT=0**, e a seção Localização do P14 diz

    - origin: https://github.com/fabriciopsouza/metacognition-framework

Não é `"(sem origin)"`. É o remote **do próprio framework**, colado num handoff que descreve outro
projeto. A causa está em `tools/handoff.py:45` — `git -C ROOT`, com `ROOT` derivado de `__file__`.
A ferramenta descreve sempre o repositório onde ela mora, seja lá de onde for chamada.

Isso é pior que degradar em silêncio: a saída é **plausível e errada**. Quem seguir o P14 clona o
repositório errado e nada avisa. E `tools/test_handoff.py` na `main` tem **zero** ocorrências de
"sem origin" — nenhum canário exercita o ramo.

**É insumo direto da pendência #5.** O `ADR-101 — gates portáteis` existe exatamente para o caso
"framework aplicado num repo que não o hospeda", e está parado sem PR. Este é o primeiro defeito
medido que ele cura.

---

## Parte 4 — Três classes de defeito de gate que faltam no §4

Todas as três aconteceram no repositório irmão (`copiloto-automacoes-sap`) e **todas já têm reparo
funcionando lá**, com teste. São candidatas a portar, não ideias.

### 4.1 O gate que casa com a própria documentação

Aconteceu **três vezes seguidas**: o detector procurava padrões em texto, e o texto que explicava o
detector continha os padrões. Cada correção reintroduzia o defeito — a segunda versão sinalizou o
comentário que explicava a primeira.

Cura que funcionou: **analisar a árvore sintática em vez do texto**. Comentário e docstring não
existem na árvore, então o gate deixa de enxergar a própria explicação.

**Pergunta a somar à bateria do §4:** *o gate sobrevive a ser aplicado a si mesmo?*

### 4.2 O gate que mede o commit anterior, e não o que está sendo commitado

O gate de pre-commit conferia o estado já commitado — e **absolvia justamente o commit que estava
causando a defasagem**. Passava verde no único caso que existia para pegar.

Cura: conferir a área de preparação (`git diff --cached --name-only`), não o `HEAD`. Provado com
teste que reprova antes e passa depois.

**Pergunta a somar ao §4:** *o gate mede o estado que o commit vai criar, ou o que ele está
substituindo?*

### 4.3 Degradação silenciosa por captura larga de erro

Duas ocorrências medidas:

- `handoff.py:45` — `except Exception: return ""`. Falha do git e campo vazio ficam
  indistinguíveis.
- No repo irmão, um carregador de módulo com `except` largo fez o gate rodar **com metade dos
  padrões** e imprimir sucesso.

Cura nos dois casos: devolver `None` em falha, distinto de `""` para vazio, e **falhar fechado** com
aviso alto em vez de degradar calado.

---

## Parte 5 — Dois complementos menores, medidos

### 5.1 §4.3 tem um exemplo pronto dentro do próprio framework

A emenda do §4.3 pede que um sintoma com N causas **enumere as causas**. O aviso do hook de liveness
(ADR-061) já faz exatamente isso: lista três causas em ordem de probabilidade e manda **verificar**
em vez de assumir antivírus. Vale citar como referência de forma, não só como regra abstrata.

### 5.2 §9.2 ganhou um segundo vizinho

O prompt aponta `validation-reporting/SKILL.md:82` (censo × amostra) como o vizinho onde encaixar o
eixo piloto × produção. Existe agora um segundo: a seção **"Quando atualizar, e o que entregar ao
fechar"**, que entrou em `_shared/project-docs` pelo #117 e está na `main`. É onde o escopo da
entrega é comunicado a quem não estava na conversa — o mesmo lugar onde "piloto" precisa aparecer
para não ser lido como "pronto".

### 5.3 Um gate novo, do tipo que o §4 procura

`copiloto-automacoes-sap/tools/quadro.py` traz o gate **"ação autocontida"**: reprova texto de ação
que só faz sentido para quem participou da conversa (opção por letra, seção por número, código de
item). Atende às quatro perguntas do §4 com medição: distingue os dois estados, foi exercitado nos
dois sentidos, usa comparação literal em vez de expressão regular (imune a erro de escape) e a
mensagem nomeia o trecho ofensor. A regra correspondente já está na `main` do framework.

---

## Parte 6 — O que muda na lista de entregas do §8

Acrescente:

6. **O parecer de QA vincula-se ao código revisado?** Se não, o veredito é uma opinião datada sobre
   um alvo móvel — e o #118 conserta o sintoma, não a causa.
7. **Cada gate crítico tem prova de mutação registrada?** Um caso que ele deve reprovar, rodado, com
   a saída anexada. O §9.1 mostra o custo de não ter: um falso verde sobreviveu porque ninguém
   executou o caso ruim uma vez.
