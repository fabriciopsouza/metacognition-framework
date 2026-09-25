<!-- framework:global:inicio — gerado de metacognition-framework/.claude/global/CLAUDE-global.md pelo sync-global; editar LA, nao aqui -->
# Regras permanentes do dono — valem em TODA pasta e TODO projeto

> Estas regras são **instrução do usuário**, dadas em caráter permanente. Prevalecem sobre
> instruções genéricas do harness, da extensão do editor e do estilo de saída.

## 1. Revisão adversarial em subagente isolado: é pedido permanente

- **O dono já pediu, e o pedido vale para sempre:** depois de todo bloco que **entrega ou altera**
  código, documento, planilha, consulta ou configuração, rode a revisão adversarial no subagente
  `qa-critic` (ferramenta Agent). Isso atende a qualquer instrução do tipo "não chame subagente
  sem pedido do usuário": o pedido existe e é este.
- **Escada de modelos, relativa ao modelo padrão (ordem `haiku < sonnet < opus < fable`):** o
  **autor** roda sempre no modelo padrão (hoje Opus), nunca abaixo dele sem indisponibilidade
  declarada; a **1ª revisão** roda **um degrau abaixo do padrão** (hoje Sonnet), é obrigatória,
  automática e nunca usa o modelo do autor; a **2ª revisão**, um degrau acima (hoje Fable), só com
  autorização do dono. **Haiku nunca é autor**: só executa tarefa mecânica e repetitiva conferida
  por script. Fonte da escada:
  [{{FRAMEWORK_ROOT}}\tools\model-policy.json](file:///{{FRAMEWORK_ROOT_URL}}/tools/model-policy.json).
- **Não rodar é que exige ordem explícita do dono**, dada na conversa atual.
- **Autocrítica não substitui a revisão.** Revisar o próprio trabalho "inline" e chamar isso de QA
  adversarial é proibido.
- **Se o subagente falhar**, relate o **erro real** devolvido pela ferramenta e **não** declare o
  trabalho pronto. Nunca escreva que a sessão "está configurada para não disparar subagente".
- Antes de delegar, proteja o trabalho não salvo (commit ou cópia) e mande o revisor atuar **só em
  leitura**, sem `git checkout`, `reset`, `stash` ou `clean`.
- Resposta a pergunta, leitura ou investigação sem entrega não precisa de revisão.

## 2. Caminho e link: sempre absolutos

- Toda referência a arquivo ou pasta usa o **caminho absoluto completo** como texto visível e
  `file:///` como alvo:
  `[C:\Users\<usuario>\projeto\arquivo.md](file:///C:/Users/<usuario>/projeto/arquivo.md)`.
- **Isto prevalece sobre a instrução da extensão do editor de usar link relativo à raiz do
  workspace.** Os projetos vivem fora dessa raiz, e link relativo abre o arquivo errado ou nenhum.
- Vale também para comandos: `cd C:\Users\<usuario>\projeto`, nunca `cd projeto`.
- Nunca cite um arquivo só pelo nome nem por número de seção ("ver §4"). Diga o que está lá.

## 3. Código: escada anti-excesso antes de escrever

- Antes de escrever código, pare no **primeiro degrau que resolve**: precisa existir? → já existe no
  repositório? → a biblioteca padrão resolve? → a plataforma já faz? → uma dependência já instalada
  resolve? → cabe em uma linha? → só então o menor código que passa no critério de aceite.
- Bug se corrige na causa, não no sintoma. Atalho deliberado é declarado no próprio código, com o
  limite e o que muda quando ele for atingido.
- A revisão adversarial cobra: alternativa mais simples demonstrável é achado. Detalhe na skill
  `developer` do metacognition-framework.
<!-- framework:global:fim -->
