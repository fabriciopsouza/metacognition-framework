# Execution report — 21–22/09/2026 — o bloco represado sai, e o gate para de medir o que não muda

**Repo:** `metacognition-framework` · **PR:** [#139](https://github.com/fabriciopsouza/metacognition-framework/pull/139) · **Merge:** `ed087b5..5305ae2`
**Entregue:** 137 arquivos, 22.649 inserções · ADR-113/114/115 · 3 rodadas de QA adversarial nesta sessão (37ª, 38ª, 39ª), 39 no total do bloco
**Rota:** squad (pmo → developer → qa-critic → docops)

---

## O que o bloco produziu

Três ADRs represados havia semanas entraram na `main`. Não commitavam porque o `squad_gate` —
corretamente — não tinha evidência que os cobrisse.

- **ADR-113** política de lançamento de projeto: skill `controle-projeto`, `controle-sharepoint`,
  dois comandos de barra, três ferramentas, quatro canários.
- **ADR-114** `service-valuation` no núcleo: skill, template de memória de cálculo, rate card
  privado e exemplo público.
- **ADR-115** fail-closed no veredito, e duas correções de semântica do gate.

E o pedido que abriu a sessão: o grau `--quick` no `/feature-plan` (`Requerimentos → Design →
Tasks`), que **não virou um fluxo novo** — a crítica file-first mostrou que ele já existia em
`/feature-plan` + `/implement`, e o que faltava era o custo de entrada, não o fluxo.

---

## As lições que valem para o framework

### 1. Um campo raramente tem um consumidor só

O achado CRÍTICO da 37ª rodada, e o melhor da sessão. Ao otimizar o caminho novo de
`_recente_o_bastante`, pulei a validação de `sha_revisado` raciocinando que "o hash de conteúdo
é mais forte que a ancestralidade". **Verdade para aquela função, falso para o sistema:**
`sha_revisado` também é a **chave** que `_reprovacao_vigente` usa para achar a reprovação irmã.
Com sha inválido a chave virava string vazia, e uma reprovação legítima com CRÍTICO aberto
deixava de ser vigente — reabrindo o defeito que as rodadas 8, 9 e 10 levaram três tentativas
para fechar.

O dano estava numa função que eu não toquei, e **nenhum teste do caminho otimizado podia vê-lo.**

> Antes de pular a validação de um campo, procurar quem MAIS o lê.

### 2. O gate roda numa plataforma só, e é cego a uma família inteira

Dois defeitos existiam havia semanas e **nenhuma das 38 rodadas anteriores podia vê-los**, porque
todas rodaram no mesmo Windows:

- os 20 pinos de hash dos vereditos legados foram calculados de bytes **CRLF**; o repo guarda
  **LF**. No Windows o checkout converte de volta e bate; no macOS/Linux **nunca** bate. Um
  mecanismo de integridade que só podia passar numa plataforma;
- um canário tornava o **arquivo** somente-leitura para provar que a escrita falha — mas
  `escrever_texto` é atômico, e no POSIX trocar um arquivo depende da permissão do **diretório**.
  No macOS a gravação sucedia e o teste reprovava uma garantia que existe.

O ADR-088 escolheu BYO-CI com esse trade-off **declarado** ("1 OS, não a matriz 3-OS"). A escolha
segue defensável; o que faltava era alguém **medir o custo** dela em vez de só citá-lo. E vale o
registro: o GHA, que não é o gate, estava **certo** — quando ele reprovar, ler antes de descartar.

### 3. Onde o mecanismo está bem coberto, o defeito migra para a prosa

Três rodadas seguidas tiveram o achado principal no **texto**, não no código:

| Rodada | O defeito |
|---|---|
| 37ª | comentário afirmando um critério de aceite **falso sobre o próprio arquivo** onde vivia |
| 38ª | a palavra "mais estrito" onde o correto era "mais cirúrgico" — descrevia garantia que o código não dá |
| memória | o gancho do `MEMORY.md` envelheceu enquanto o corpo foi atualizado |

**Nenhum canário lê prosa.** É o trabalho `canario-auto-afirmacao-verificavel`, aberto, e ele
serviria também para o índice de memória.

### 4. A regra que fabricava o artefato que depois era criticado

`_qa_critic_attested` exigia **um** veredito cobrindo **todos** os caminhos. Para fechar um bloco
de 91 era preciso declarar os 91 num artefato só — e nenhum crítico sozinho revisou 91 arquivos.
A regra **produzia** a forma enganosa que depois era criticada como teatro. Agora cada caminho
exige algum veredito válido que o cubra.

Medido: **57 dos 91** caminhos dependiam de um único veredito-cobertor. A união não afrouxa por
caminho — o crítico da 38ª corrigiu a minha redação: o veto de reprovação fica mais *cirúrgico*,
não mais *estrito*.

### 5. Seis sessões na mesma árvore, e a atribuição por proximidade temporal é sempre errada

O HEAD andou **quatro vezes** durante a sessão. Eu culpei a `7c` por um commit que não era dela;
ela me culpou por outro que não era meu. Nenhuma das duas era responsável — era uma terceira
frente. A única atribuição confiável foi olhar autor, timestamp e `--stat` do commit.

O que impediu estrago não foi gate nenhum: foi ela ter parado para perguntar antes de commitar, e
eu ter relido `qa_evidence.py` antes de editar. **A defesa contra concorrência ainda é disciplina,
não mecanismo** — o `squad_gate` é fail-closed contra veredito faltando e completamente cego a
"outra sessão está escrevendo nesta árvore agora".

---

## Gaps declarados (abertos, com trabalho registrado)

- **Composição de vereditos de SHAs diferentes** pode atestar um commit que nunca existiu inteiro
  num snapshot revisado. Três desenhos na mesa; consertar custa um ADR. → `veredito-composto-shas-diferentes`
- **60 vereditos legados** cobrem por ancestralidade, que não vê edição não commitada. Encolhe
  sozinho (todo veredito novo carrega `blobs_revisados`). → `vereditos-legados-sem-blobs`
- **Nenhum canário valida `.agent/workflows/*.md`** estruturalmente — foi por isso que a conflação
  J6 × process-critic e o E5/E6 chegaram ao QA sem barreira. → `canario-para-workflows`
- **`post_canary_status.py` fica ~10 min em silêncio.** Gate que parece travado é gate que se
  aprende a interromper — aconteceu nesta sessão. Candidato a débito, não consertado para não
  violar a régua §0 depois de tanto mexer no gate.
- **Ramo POSIX do canário de escrita** corrigido por raciocínio, não por execução: autor e crítico
  rodam em Windows. Declarado como INFERIDO nos dois vereditos.

---

## Boas práticas que se confirmaram

- **File-first salvou três vezes:** o `--quick` já existia; `qa_evidence.py` já tinha sido
  consertado por outra sessão (quase sobrescrevi); e `legados_declarados()` já era o molde de
  transição que a `7c` ia pedir ao dono como custo inexistente.
- **Medir antes de afirmar, sempre.** A hipótese de que o ALTA contaminava a cobertura era minha
  e **a medição a refutou**. A hipótese de que a CI era "vermelha pré-existente" era da memória e
  o histórico a refutou.
- **Crítica cruzada entre sessões funcionou** porque as duas mediram antes de afirmar e cederam
  quando a medida contrariou. As duas vezes em que alguém cedeu, quem cedeu não tinha lido um arquivo.

---

## Prova

- `tools/run_canaries.py`: **88 PASS · 1 SKIP · 0 FAIL**, exit 0
- `tools/test_squad_gate.py`: **96 PASS / 0 FAIL** (13 canários novos, a maioria negativos)
- `tools/test_mutacao_squad_gate.py`: **37/37 mutações mortas** (3 novas)
- `canarios-local=success` postado em `bb14c42` — o gate do ADR-088, satisfeito honestamente
- `squad_gate` exit 0 com os três papéis atestados, **sem override**
