# Andamento — 24/09/2026 (bloco C): dois QA reprovaram, e a tabela do meu próprio documento me refutou

> Execution-report de encerramento de bloco (ADR-038/052/062 · tier **OWNER** · privado).
> **Terceiro bloco do dia.** O bloco A fechou no PR #148, o bloco B no #149; nenhum dos dois
> cobre o que veio depois.

## Onde estamos, em uma linha

O pacote do Sistema de Pesagem ganhou evidência de campo, uma medição no SAP Datasphere, dois
painéis para diretoria e — o que mais importa — **duas rodadas de QA adversarial em modelos
diferentes e isolados que REPROVARAM o meu resultado**, uma delas mostrando que minha
conclusão central era refutada por uma tabela do próprio documento.

## Métricas

| Métrica | Valor |
|---|---|
| Tokens | **NÃO MEDIDO CONFIAVELMENTE** (mesma razão dos blocos A e B) |
| Commits | 4 no repo de domínio (`5dfc588`, `c16e7ce`, `e2e6587`, `43d3968`) + este report |
| Escrita em repo de terceiro | 4 correções + 7 canários em `info-projetos-sistemas`, **com backup prévio** porque a pasta não tem git |
| Achados de QA recebidos | 16 (7 ALTA) em duas rodadas, modelos diferentes |
| Testes | `verifica.py` do pacote: 6 gates · `test_gate.py`: **18 casos** (13 barram, 5 contraprova) · `verifica.py` do repo vizinho: 54 → **61 checagens** |
| Rodadas de retrabalho | **2 reprovações** no mesmo artefato, mais 3 consertos em cascata dentro da primeira |

## De onde saímos → onde chegamos

**Quatro frentes, e a ordem importa porque uma expôs a outra.**

1. **As 4 ressalvas do `gut.py`** (do bloco B) foram aplicadas no repo vizinho, com backup
   porque não há git ali. A de severidade ALTA virou `assert`: chave órfã em `DECIDIDAS`
   agora sai 1. Provei com a sabotagem — sem o assert, a nota do diretor caía de
   `100/prioridade 2` para `36/prioridade 15` e o script saía 0.
2. **Evidência de campo:** 12 fotos das cabines. Dois achados ganharam preço: a pressão
   diferencial é **manômetro de ponteiro**, então o requisito obrigatório que depende dela
   exige CAPEX de instrumentação ausente da ERU; e a ERU fala em "2 cabines" quando as
   antecâmaras também têm pressão e limpeza próprias.
3. **A medição no Datasphere**, que o dono apontou. Descartei uma rota **por medição** (o
   mestre de equipamento não está lá, nos 6 espaços) e achei fonte para o requisito de
   desempenho que faltava.
4. **Dois painéis para diretoria**, publicados como artifact, com macrocronograma em janelas
   relativas marcadas SUGESTÃO e o formulário das 29 perguntas.

**E o framework passou a valer no repo de domínio** por `CLAUDE.md`, não por lembrança —
medido que não há `.agent/`, `.claude/`, hook, semeadura nem plugin.

## O placar gate × achado

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| **Minha conclusão central era falsa** — "a unidade muda em 0,5 kg" quando **83,7% do que está abaixo de 0,5 kg está em quilo** | **QA adversarial (fable)** | **nenhum.** Refutada por uma tabela duas linhas acima, no mesmo arquivo. Nenhum gate lê prosa contra tabela |
| **A consulta publicada como "exatamente como executada" não executava** (erro HANA 277) | **QA adversarial (sonnet)** | nenhum — não há gate que rode o SQL publicado |
| **Minha causa para o bug do `--profile` estava errada** (culpei hífen; é case-folding de alias) | **QA adversarial (sonnet)**, lendo o código | nenhum |
| Premissa `BDMNG`/`ERFME` nunca testada, e quebra fora do recorte | **QA adversarial (sonnet)** | nenhum |
| População minoritária é tabela **viva** (1.179 → 1.195 → 1.203) | **QA adversarial (sonnet)** | nenhum |
| "poucos pontos de distância" = **8,3 pp** | **os dois QA** | nenhum |
| `KGA` e `Z61` excluídos sem saber o que são | **QA adversarial (sonnet)** | nenhum |
| 6 derivas do pacote com os 6 gates em **PASS** | **QA adversarial (fable)** | `G6` era **lista de 10 endereços**, cego a número em outra linha. Hoje: `G6b`, varredura |
| Marca `INFERIDO` perdida ao propagar para os arquivos da diretoria | **QA adversarial (fable)** | nenhum |
| Chave órfã em `DECIDIDAS` derrubando a nota do diretor | **eu**, sabotando em cópia | nenhum lá; hoje `assert` + canário |
| **`--profile` quebrado para QUALQUER view** | **eu**, ao duvidar da causa do QA e medir em duas outras views | nenhum |
| **Meu próprio `G6c` com 7 falsos positivos** | **a contraprova `G6 nao acusa pacote real`** | **funcionou** — barrou um gate que reprovava o pacote correto |
| Âncora inventada num link novo | **`G1`** | **funcionou** |
| Croma do verde em **0,096**, abaixo do piso 0,10 | **o validador de paleta**, portado para Python | **funcionou** — olho nenhum vê 0,096 vs 0,10 |
| Barra `F5` transbordando e suporte do cronograma com **43,75% em vez de 17,5%** | **eu**, conferindo a aritmética do eixo antes de publicar | nenhum |
| Heredoc colapsando `\\` → `\` e quebrando o payload | **o interpretador**, com erro | nenhum; a memória avisa e eu reincidi |

## Detecção: framework × humano

- **O QA adversarial pegou 9 dos 16, e os 4 mais graves.** Nenhum deles era mecanizável:
  prosa contra tabela, SQL publicado que não roda, diagnóstico de causa errado, premissa não
  testada. **Dois modelos diferentes acharam coisas diferentes** — o de raciocínio pegou o
  salto lógico e a deriva; o numérico pegou o SQL, a tabela viva e a causa do bug.
- **O mecanismo pegou o que é forma:** `G1` a âncora, o validador de paleta o croma, a
  contraprova o meu gate defeituoso, o `I2` (blocos anteriores) os defeitos de refactor.
- **Eu peguei duas coisas por hábito, não por gate:** conferir a aritmética do eixo antes de
  publicar, e duvidar da causa que o QA me deu e medir em duas outras views — o que mostrou
  que o bug era universal, não desta view.

## O que eu errei, e o que derrubou cada erro

1. **Afirmei uma fronteira que os meus próprios números refutavam.** É a fabricação em prosa
   no seu pior formato: não inventei dado, **interpretei o dado contra o próprio dado** e
   propaguei para dois arquivos que a diretoria lê, perdendo a marca `INFERIDO` no caminho.
   Derrubou: o QA de raciocínio.
2. **Reescrevi uma consulta para ficar legível e publiquei sem rodar a versão reescrita** —
   num arquivo cujo padrão é "a consulta exatamente como executada". Derrubou: o QA numérico,
   rodando o que eu publiquei.
3. **Dei um diagnóstico de causa sem ler a função.** Culpei o hífen; a função já citava o
   nome. Derrubou: o QA numérico, lendo o código.
4. **Construí um gate com 7 falsos positivos** (relação por proximidade de texto). Derrubou:
   a contraprova que existe exatamente para isso.
5. **Reincidi no heredoc** que colapsa barra-invertida dupla, e quebrei o script que
   escreveria o próprio prompt. A memória registra e prescreve o remédio; eu não apliquei.

## Gaps (flagados, não silenciados)

- **Não há gate que confronte prosa com a tabela que está no mesmo arquivo.** Foi onde o
  defeito mais grave do dia morou. Provavelmente não mecanizável de forma geral.
- **Não há gate que execute o comando publicado numa prova.** Este **é** mecanizável para
  comandos locais (rodar o bloco ```bash e comparar a saída), e é o candidato mais concreto
  que o dia produziu. Para consulta a sistema externo, não — depende de credencial e de
  tabela viva.
- **Regra escrita não vincula sem mecanismo**, e tenho duas evidências novas: reincidi no
  heredoc com a memória escrita, e o `CLAUDE.md` que acabei de criar é uma aposta de que ler
  basta — por isso o prompt de retomada **exige confirmação citando o que leu**.

## Melhorias candidatas (régua §0 — nenhuma promovida)

- **Gate que roda o comando publicado na prova.** Tem duas instâncias no mesmo dia (a
  consulta que não executava, e a conferência que só cobria a parte estável). Mesmo assim
  não promovo: as duas vivem no mesmo projeto. Quitação: ao segundo projeto com provas
  executáveis, extrair.
- **`G6b` (varredura por padrão em todo `.md`)** substituiu uma lista de endereços por uma
  varredura. É o mesmo padrão do candidato do bloco A, agora com **segunda instância**. Segue
  sem promoção pelo mesmo motivo: ambas em repo de domínio.

## Boas práticas (reutilizável)

- **Duvidar do achado do QA e medir.** O QA disse que o `--profile` falhava por case-folding;
  medi em duas outras views e descobri que o alcance é **universal**, o que ele não tinha
  afirmado. Aceitar o achado sem medir teria subdimensionado o defeito.
- **Portar o validador quando a ferramenta não roda.** Node não está instalado; em vez de
  trocar "computar" por "olhar", li os limiares e as matrizes no fonte e portei os checks.
  Pegou um croma de 0,096 contra piso 0,10.
- **Backup antes de escrever em pasta sem git**, com hash conferido contra o original.
- **Contar o que a página afirma sobre si mesma antes de publicar** (29 perguntas, 8 blocos).

## Lições por skill (agnóstico de domínio)

- **qa-critic:** *dois modelos diferentes acham defeitos de classes diferentes.* O de
  raciocínio pegou o salto lógico e a deriva documental; o numérico pegou o SQL que não roda,
  a tabela viva e a causa errada. Rodar um só teria deixado metade em pé.
- **developer:** *reescrever para legibilidade é uma mudança de código.* Consulta,
  comando ou trecho publicado tem de ser executado **na forma publicada**.
- **architect:** *gate que adivinha relação é pior que gate nenhum.* Sete falsos positivos
  fizeram meu gate reprovar o pacote correto; quem tem pressa desliga, e aí não barra mais
  nada. A contraprova é o que impede isso de entrar.
- **discovery:** *a conclusão mais perigosa é a que interpreta o dado contra o próprio dado.*
  Não é dado inventado — é leitura invertida, e passa por qualquer gate de número.
- **docops:** *marca de confiança se perde na propagação.* `INFERIDO` na prova virou fato no
  arquivo que a diretoria lê. Propagar exige reconferir a marca, não só o número.
- **design/dataviz:** *a parte de cor é computável, então compute.* E verde+âmbar+vermelho
  não se torna um trio discriminável para daltonismo — medido: o par verde/tijolo dá CVD 5,3
  no claro e 2,7 no escuro. A saída é severidade por **palavra**, com a cor como reforço.

## Procedência

- Repo de domínio: `C:\Users\fabriciosouza\sistema-pesagem` @ `43d3968`, 6 gates PASS,
  18 casos de teste.
- Repo de terceiro alterado: `C:\Users\fabriciosouza\info-projetos-sistemas` — 4 correções e
  7 canários, **backup prévio no scratchpad com hash conferido**, esteira de 7 geradores e os
  3 guardas em `EXIT=0`, `verifica.py` de 54 para 61 checagens.
- QA adversarial: **dois subagentes isolados, modelos diferentes entre si e do autor** (autor
  Opus 5 → um degrau abaixo, Sonnet, no número; um acima, Fable, no raciocínio), com
  autorização explícita do dono para o degrau acima. Vereditos: **corrigir** e **reprovar**.
- Artifacts publicados: painel estratégico e formulário de levantamento (privados).
- Gates inertes desta sessão (ADR-061), aplicados à mão em cada turno: `check-repo-sync` →
  0/0 · `check-core-agnostic` → PASS (norma).
- **O que este report não mede:** tokens, tempo de parede, turnos; e não mede se os painéis
  serão enviados — isso é decisão do dono.
