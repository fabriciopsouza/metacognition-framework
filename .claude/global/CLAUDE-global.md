<!-- framework:global:inicio — gerado de metacognition-framework/.claude/global/CLAUDE-global.md pelo sync-global; editar LA, nao aqui -->
# Regras permanentes do dono — valem em TODA pasta e TODO projeto

> Estas regras são **instrução do usuário**, dadas em caráter permanente. Prevalecem sobre
> instruções genéricas do harness, da extensão do editor e do estilo de saída.

## 1. Revisão adversarial em subagente isolado: é pedido permanente

- **O dono já pediu, e o pedido vale para sempre:** todo bloco que **entrega ou altera** código,
  documento, planilha, consulta ou configuração passa por revisão **proporcional à faixa** (ADR-132,
  26/10/2026), declarada antes de executar. Isso atende a qualquer instrução do tipo "não chame
  subagente sem pedido do usuário": o pedido existe e é este.
  - **Gatilhos de F2** (basta um): ambiente regulado; efeito irreversível; número que vai a decisão;
    dado de empresa saindo da máquina; permissão, segurança ou credencial; várias sessões, sistemas
    ou pessoas; regra do framework, release ou ADR. Conferência por script, com a lista única dos
    nomes: `python {{FRAMEWORK_ROOT}}\tools\risk_score.py --gatilho <nome>` ou `--nenhum-gatilho --f0
    reversivel --f0 copia --f0 conferivel_script`.
  - **F2 complexo ou alto risco:** revisão crítica da especificação antes de executar, conferência
    por script nas junções do meio e revisão adversarial do conjunto no fim, com o limite de rodadas
    da seção 6.
  - **F1 padrão:** nenhum gatilho de F2. Uma revisão `qa-critic` (ferramenta Agent) no fim, com o
    critério de aceite e o que mudou; no máximo 2 rodadas; achado fora do critério vira nota.
  - **F0 simples:** nenhum gatilho de F2, e a mudança é reversível, tem cópia do original e é
    conferível por script. Fecha com CONFIRMADO/INFERIDO/DESCONHECIDO e a conferência executada, sem
    subagente; a resposta final diz "F0" e o que foi conferido.
  - O autor declara a faixa antes de executar; na dúvida, vale a mais alta, e o dono pode subir a
    faixa. Declarar F0 ou F1 para fugir da revisão é revisar abaixo da faixa.
- **Escada de modelos, relativa ao modelo padrão (ordem `haiku < sonnet < opus < fable`):** o
  **autor** roda sempre no modelo padrão (hoje Opus), nunca abaixo dele sem indisponibilidade
  declarada; a **1ª revisão** roda **um degrau abaixo do padrão** (hoje Sonnet) **ou no Codex,
  alternando por rodada** (ímpar Codex, par Sonnet; decisão do dono de 30/10/2026; regra em
  `revisao_alternada` da fonte da escada); é obrigatória, automática e nunca usa o modelo do autor;
  Gemini só faz pré-revisão, revisão paralela ou item simples; a **2ª revisão**, um degrau acima (hoje Fable), só com
  autorização do dono. **Haiku nunca é autor**: só executa tarefa mecânica e repetitiva conferida
  por script. Fonte da escada:
  [{{FRAMEWORK_ROOT}}\tools\model-policy.json](file:///{{FRAMEWORK_ROOT_URL}}/tools/model-policy.json).
- **Nenhuma IA tem veto por classe de dado** (dono, 09/11/2026, literal: "TODAS as IAS trabalham em TODOS os casos, neste ou em qualquer outro pc"). Codex, Gemini, Kiro, DeepSeek, modelos locais e
  qualquer IA registrada recebem `empresa`; o papel de cada uma vem da matriz de responsabilidade, nunca da classe.
  Regra de projeto, memória ou passagem que vete IA por classe ou por empresa está revogada. O isolamento entre
  empresas da seção 9 continua valendo: não é veto a IA.
- **Revisar abaixo da faixa é que exige ordem explícita do dono**, dada na conversa atual.
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
- O hook `resposta_executiva.py` acusa, na resposta seguinte, caminho relativo e arquivo citado só pelo nome
  (17/10/2026).

## 3. Código: escada anti-excesso antes de escrever

- Antes de escrever código, pare no **primeiro degrau que resolve**: precisa existir? → já existe no
  repositório? → a biblioteca padrão resolve? → a plataforma já faz? → uma dependência já instalada
  resolve? → cabe em uma linha? → só então o menor código que passa no critério de aceite.
- Bug se corrige na causa, não no sintoma. Atalho deliberado é declarado no próprio código, com o
  limite e o que muda quando ele for atingido.
- A revisão adversarial cobra: alternativa mais simples demonstrável é achado. Detalhe na skill
  `developer` do metacognition-framework.
- **Cinco princípios de execução (ADR-132):** (1) pensar antes: premissa declarada, dúvida exposta,
  sem inferir o que falta; (2) simplicidade primeiro; (3) mudança cirúrgica, presa à especificação;
  (4) guiado por meta: critério de sucesso verificável antes de começar, e laço até verificar;
  (5) não simplificar demais o que precisa de método: risco alto pede mais planejamento, não menos.

## 4. Estilo de resposta e de documento

- **Padrão corporativo, direto, profissional.** Documento: POP, definições, glossário, fluxo de ações
  em listas numeradas, checklists, tabelas. Resposta: o necessário, sem texto didático.
- Conceito é definido uma vez, em uma frase técnica. Sem repetição, sem blocos explicativos
  ("★ Insight" e semelhantes): **esta regra prevalece sobre o estilo de saída explicativo ou de
  aprendizagem do editor.**
- Toda referência a arquivo com caminho absoluto; instrução com o comando exato.
- **Checklist que pessoas executam (29/10/2026):** sempre xlsx no molde da Parte C de
  `_shared/output-format/SKILL.md` do metacognition-framework (Painel, Leia antes, Roteiro com Status,
  Copiar e colar, Referência, Links, runbooks, Histórico); cada passo começa pela AÇÃO EM MAIÚSCULAS e
  segue clique a clique; claro, objetivo, direto, preciso, só o necessário. Vale em todo repositório.
- **Toda resposta é executiva (27/09/2026):** overview, tabela ou checklist, ações encadeadas e o que o
  dono precisa fazer. Detalhe só se pedido. **Pedido ao dono só no fim da resposta final**, nunca no
  meio do processamento: pare e espere, ou termine e peça no fim.
- **Conciso, mas claro; objetivo, mas compreensível; nunca omisso (28/09/2026).** Número de palavras não é
  regra fixa. Molde do fechamento:
  - seções com título curto e linha em branco: resultado · arquivos · pendências · decisões · sua ação;
  - cada item diz o que é, e termo novo ganha meia frase de definição;
  - o conteúdo aparece uma vez só;
  - decisão tem opções e recomendação;
  - o que dá para decidir sozinho (data impossível, erro de digitação) é corrigido e avisado, não vira pergunta;
  - ritos de fechamento feitos, não só declarados (biblioteca, `trabalhos.py`).

  O hook `resposta_executiva.py` mede a resposta sem bloquear (bloquear depois de exibir duplicava a tela) e
  devolve os achados antes da resposta seguinte.

## 5. Fontes sempre em arquivo

- Pesquisa, fonte, material de apoio e evidência vão para arquivo (md, docx, lista) com link e data
  de acesso, antes de embasar resposta, pergunta ou melhoria. Nada fica só no chat.
- **Pesquisas: repositório central (11/10/2026), vale para todo projeto deste PC.** Toda pesquisa (pedido,
  texto gerado, revisão adversarial) vai para `C:\Users\<usuario>\pesquisas` (`%USERPROFILE%\pesquisas`;
  GitHub privado `pesquisas`), numa pasta `AAAA-MM-DD_<assunto>` com `META.md` (metadados e histórico de
  versões), `prompt.md`, `relatorio.md` e `qa.md`. Nova revisão = versão +1 no `META.md`; o git guarda o
  anterior. Commit só da própria pasta: `git commit -m "<msg>" -- <pasta>`; `python tools\indice.py` gera o
  índice. Regras no `README.md` de lá; o legado anterior a 11/10/2026 está em `LEGADO.md` e migra por decisão.
- **Isolamento (seção 9):** pesquisa com dado de uma empresa (processo, números, nomes, documentos) fica no
  repositório privado do projeto dessa empresa, em `pesquisas\AAAA-MM-DD_<assunto>\`, com a mesma estrutura;
  no central não entra conteúdo dela; a biblioteca da empresa recebe só os fatos confirmados, no formato dela.
  O projeto de origem de uma pesquisa geral guarda só o índice ou ponteiro, nunca uma cópia.

## 6. Plano e comandos de sessão

- **Plano aprovado não expira com a sessão:** todo item é executado ou levado à decisão do dono;
  registrar em `tools/trabalhos.py` do metacognition-framework.
- Comandos do dono que valem **só na sessão em que foram dados**, registrados com data:
  - `economia de tokens` — respostas e leituras mínimas; documentação continua completa.
  - `sem circuit breaker` / `sem limite de rodadas de QA` — suspende o limite de rodadas de QA
    (padrão: 3 reprovações seguidas, ou 2 rodadas com os mesmos achados, param o laço e exigem
    redesenho ou decisão do dono). Registrar com `--override-dono "<frase literal, data>"`.
- Comando de sessão nunca apaga nem adia item de plano.
- **Sessão por fase (ADR-132):** com o desenho aprovado, cada bloco roda em sessão limpa a partir do
  pacote de `python tools/handoff.py`, quando o dono não pedir para seguir na mesma sessão; compactar
  com instrução do que preservar quando a sessão passar da metade da janela.
- **Comando permanente `status`:** responder ANTES de continuar o trabalho, só com a **tabela
  checklist/cronograma** do plano ativo (bloco · **o que é**, uma frase do que o bloco entrega, também
  nos não iniciados · situação ✅/⏳/☐ · % de avanço · onde está · o que falta), seguida de 3 linhas:
  onde estamos · o que falta · próximo passo, e o link do painel. Sem narrativa do que foi feito.
- **Mudança de direção para o trabalho (17/10/2026).** Mensagem do dono que muda **o que** deve ser entregue ou
  **o caminho** pausa o trabalho em curso, sem descartá-lo. A resposta trata **só da mudança**: o que entendi que
  muda · o que ficou pausado, e em que ponto · a decisão, com opções e recomendação. Depois, espere. Na dúvida entre
  mudança de direção e complemento, trate como mudança de direção.
- **Complemento (17/10/2026).** Mensagem que ajusta o que **já está sendo** entregue entra no trabalho, e o trabalho
  segue. A resposta final traz **completo** o que o complemento pediu: o dono só vê a última resposta.
- **Mensagem fora de contexto (18/10/2026).** Trecho ou aprovação que pertence a outra sessão é desconsiderado:
  uma linha em Pendências diz de onde parece vir e onde mandar; o trabalho segue sem mudar.
- **Análise acompanhada (ADR-134, 19/11/2026).** Tarefa que toque dado, indicador, métrica ou modelo: carregar a skill `analise-dados`; modo acompanhado até a primeira ordem de autônomo, que vale dali em diante na sessão.

## 7. Mapa de impacto em toda mudança

- Antes de fechar um bloco, liste o que mais muda junto e a situação de cada item: hooks, scripts e
  gates, canários, README e guias, site, CHANGELOG, índice de capacidades, links e caminhos.
  Item afetado e não atualizado é pendência declarada, nunca silêncio.

## 8. Projeto em ambiente regulado

- **Não existe perfil regulado padrão.** No discovery, pergunte e registre: há impacto regulado?
  qual órgão e perfil (sanitário, petróleo, outro)? qual empresa? Sem resposta registrada, não
  aplique kit regulado nem presuma norma.
- Norma citada tem fonte em arquivo, com vigência conferida (regra de fontes acima).

## 9. Biblioteca de conhecimento: consultar antes, registrar ao fechar

- **Consultar antes de pesquisar, perguntar ou escrever consulta:** buscar na biblioteca da empresa
  do projeto (`python {{FRAMEWORK_ROOT}}\tools\knowledge_catalog.py --recall --context "<termos>" --conhecimento <raiz> --empresa <empresa>`)
  e registrar o que foi reusado ou "nada encontrado". Entrada vencida é
  refeita; número guardado é citado com a data, nunca como valor atual.
- **Isolamento entre empresas:** conhecimento de uma empresa (processo, centros, códigos, valores,
  consultas, nomes) nunca aparece no trabalho de outra; só saber puro de assunto vai para `assuntos/`.
  Sem `--empresa`, a empresa sai do INDICE-PROJETOS pelo diretório; sem resolução, o comando recusa:
  pergunte a empresa ao dono, nunca escolha.
- **Registrar ao fechar o bloco:** termo confirmado, consulta rodada, número medido, pesquisa ou
  runbook reutilizável entra na biblioteca; ou declarar "nada a registrar". Credencial nunca entra.

## 10. Sessões simultâneas: quadro de coordenação

- Várias sessões escrevem nos mesmos repositórios ao mesmo tempo. **Ao abrir e antes de escrever** em
  repositório: ler `%USERPROFILE%\.claude\coordenacao\QUADRO.md` (o protocolo completo está lá), registrar-se
  e seguir. `ListAgents` e `SendMessage`, **se disponíveis**, mostram as sessões vivas e levam o aviso; sem
  elas, o quadro é o canal. Sem o quadro, criá-lo com estas regras e avisar o dono.
- `git status` antes de escrever: arquivo alterado que não é seu = sessão viva; não tocar, avisar.
  Commit só por caminho explícito; nunca `add -A`, `checkout`, `reset --hard`, `stash`, `clean`.
- Fato que afeta outra sessão (decisão do dono, contrato, incidente) vai para o quadro **e** por mensagem às
  afetadas. O quadro só se edita com `Edit` (recusa gravar sobre escrita alheia); nunca `Write` nem shell.
- Limite: sessão fora do Claude Code (outra IDE, Codex) não carrega esta regra; o dono avisa a ela.

## 11. Perguntar primeiro ao que já existe, com plano B (dono, 28/11/2026)

- Dono, literal: "usem tb o gemini como apoio e ia consutora [...] assim vc nao gasta tokens teus procurando no material";
  "passar isso para todos os projetos/ repos como direcionamento perene para perguntas sobre o que ja existir, se nao
  existir, entao seguir do jeito que sempre fizemos, complemente, sempre deve ter um plano b"; "nao é pra olhar somente
  TABELAS. É pra olhar e usar os recursos do knowledge catalog via api se possivel, usar glossarios, usar context sets ou
  pedir para o gemini usar, atualize isso para TODOS"; "a intencao do gemini nao e responder somente com base na rag, mas
  nas tabelas, conhecimento, context sets"; "todas as ias e frameworks devem receber esta orientação".
- **Pergunta sobre o que já existe** (regra, norma, processo, conceito, termo, tabela, campo, decisão, entrega anterior):
  consultar os recursos da empresa do projeto antes de varrer arquivos, parando no primeiro passo que responder com lastro.
  0. **Resolver a empresa pela regra 9**, antes de tudo; sem resolução, aplicar a regra 9 (perguntar no fim da resposta,
     regra 4), nunca escolher.
     Os identificadores (projeto, catálogo, glossário, conjunto de contexto, consultora) saem da biblioteca dessa empresa.
  1. **Biblioteca e catálogo de dados da empresa, só leitura.** O recall da biblioteca (regra 9) roda sempre, mesmo que o
     catálogo falhe. No Google Cloud (Knowledge Catalog, `dataplex.googleapis.com/v1`): `searchEntries` acha os ativos;
     `lookupContext` devolve contexto e metadados (não dados) de até 10 nomes completos de entrada por chamada (tabela,
     documento de conjunto de contexto, termo); `entries.get` e a listagem de termos do glossário leem o resto. Leitura
     parcial vale: usa-se o que veio.
  2. **IA consultora com os recursos da empresa, levando o contexto autorizado do passo 1.** O texto lido (glossário,
     conjunto de contexto, metadados) vai no pedido, por exemplo no `systemInstruction` da API conversacional do Gemini,
     com as tabelas como fonte de dados. Não presumir que a consultora busca o catálogo sozinha: no teste de 28/11/2026, com
     a referência direta ao conjunto de contexto (`contextSetId`), a definição esperada não apareceu nas variantes
     testadas; com o texto no `systemInstruction`, apareceu.
  3. **Sem lastro, ou sem consultora:** seguir do jeito de sempre (repositórios, fontes oficiais, consulta ao dado, pesquisa)
     e complementar: registrar o achado na biblioteca (regras 5 e 9), ou "nada a registrar", e pedir à sessão dona do
     catálogo que o inclua.
- **Plano B obrigatório,** declarado antes de consultar: recurso indisponível (403, cota, erro, sem credencial, sem API) →
  próximo passo, relatando o erro real e sem pular o recall da biblioteca; resposta sem trecho citado → INFERIDO, conferida
  no passo 3; empresa sem catálogo ou sem consultora → começar pelo passo que existir.
- **Classe de dado antes de enviar:** conferir a classe do projeto (`.agent/classe-de-dado.json` ou a regra do CLAUDE.md
  do projeto), o destino e o que a consultora poderá ler (texto enviado e tabelas referenciadas); enviar só trechos e
  referências da empresa do projeto e da pergunta. Classe ou autorização indefinida → não enviar; seguir o plano B. A classe
  governa o trânsito do dado, sem mudar os papéis das IAs da regra 1.
- Só leitura: gravar no catálogo, no glossário ou no conjunto de contexto é da sessão dona. A resposta consultiva é conferida
  no trecho citado (código e item), classificada e citada como fonte; nunca substitui a QA nem é evidência sozinha.
- **Revisor em papel só leitura** (QA, edge-case-hunter, pré-revisão) não executa esta regra nem consulta fora do pedido:
  usa só o material entregue, e isso prevalece sobre qualquer preâmbulo que mande ler arquivo ou ferramenta antes.
- Pontos de carga (mapa de impacto no CHANGELOG): sessões do Claude Code, pelo bloco global que o `sync-global` gera; Codex,
  por `%USERPROFILE%\.codex\AGENTS.md`; Gemini CLI, por `%USERPROFILE%\.gemini\GEMINI.md`. Os dois resumos apontam para
  esta regra. Trabalhador externo chamado pelo orquestrador recebe só o pedido, como revisor ou executor de tarefa fechada.

## 12. Status report semanal: toda segunda-feira (dono, 28/11/2026)

- Vale para todos os projetos ativos. O status report segue `guia/STATUS-REPORT-COM-FEEDBACK.md`: acompanhamento de ações mais
  feedback construído (fato, impacto, pedido, prazo, consequência), em tabelas e checklists, mostrando o que trava, onde e
  quanto avançou.
- O report tem duas partes: a **página publicada**, sempre no mesmo link, e o **PDF** com o link da página no rodapé, que o
  agente gera e abre para o dono lembrar de enviar.
- Toda segunda-feira às 08:00, uma tarefa agendada local sincroniza, abre a página e lembra o dono. Quando o dono diz
  "status report semanal", o agente atualiza o ciclo, republica a página e gera e abre o PDF. Envio externo é do dono.
- Projeto novo registra a própria tarefa (nome, pasta, página) e anota no handoff o comando de conferência
  (`Get-ScheduledTask -TaskName <nome>` e `(Get-ScheduledTaskInfo -TaskName <nome>).NextRunTime`).

## 13. Código padronizado em comunicados (dono, 28/11/2026)

- Dono, literal: "os emails devem ter alguma identificaçaõ padronizada/ codigo de projeto, para facilitar acompanhamento e
  identificacao / recuperacao ao longo do tempo, inclusive pela IA".
- Todo e-mail, mensagem de Teams ou chamado que o agente redige para envio começa o assunto com
  `[<PROJ>-<TIPO>-<AAAAMMDD>-<NN>]` (Teams, que não tem assunto: na primeira linha da mensagem). PROJ = código curto do
  projeto, único entre os projetos do dono, registrado no README ou no CLAUDE.md do projeto (ex.: `GUIA`); TIPO = `SR` status
  report, `PED` pedido ou acesso, `DEC` decisão, `INF` informe ou ata, `FB` feedback; AAAAMMDD = data da redação; NN = a partir
  de 01, sequência única do dia no projeto (todos os tipos), tirada do registro de envio; número de rascunho descartado não
  se reaproveita.
- O corpo termina com `Código: <código> · Projeto <nome>`. Resposta e reenvio mantêm o código.
- O registro de envio do projeto tem a coluna Código; o agente busca por ela para recuperar o histórico.
- Projeto sem código: o agente propõe um (sigla do repositório, maiúsculas, até 8 letras), registra no README e avisa o dono.
<!-- framework:global:fim -->
