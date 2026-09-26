# Execution report — MRP Natulab: pré-voo, biblioteca de consultas, análise de dogfood, migração e IDE autônoma

**Sessão de 26/09/2026, segunda parte** (continua o relatório `execution-report-2026-09-26-mrp-natulab-definicoes-pcp-e-pre-voo.md`) ·
projeto de domínio migrado nesta sessão para `C:\Users\fabriciosouza\sap-mrp-natulab` (git local, sem remoto) ·
escrita no framework: só o débito DB1 no backlog (PR #160) e este relatório

- **Tokens:** NÃO MEDIDO por sessão (o `--from-transcripts` soma o diretório inteiro).
- **Tempo (wall-clock):** NÃO MEDIDO
- **Turnos:** cerca de 25 mensagens do dono nesta parte (contagem aproximada na conversa)
- **Arquivos tocados:** 159 itens movidos (157 na execução e 2 na correção do QA da migração) e 10 apagados
  (manifesto em `gestao\_migracao-2026-09-26.json`), 32 documentos com caminhos reescritos (lista do ensaio
  `gestao\_migracao-scripts\relink_dry.txt`, 32 linhas "ALTERA"; a execução gravou os mesmos 32 e a conferência de
  links depois dela não achou caminho antigo; não há log separado da execução; scripts `relinkar_mrp.py` e
  `migrar_mrp.py` guardados na mesma pasta), 4 geradores ajustados, pacote do programa 1 (comece-aqui v2, prompt v2,
  respostas do pré-voo, consultas, análise do dogfood), checklist v3 regerado, biblioteca de consultas (5 arquivos),
  backlog do framework, 4 memórias novas e 1 atualizada.
- **Testes:** geradores com asserts de cópia integral (lista única) e de 60 itens (checklist); conferência de links
  por script antes e depois; hash antes de apagar cada cópia.
- **Rodadas de retrabalho:** cerca de 18 rodadas de QA isolado (uma travou por timeout e foi repetida); o circuit breaker disparou após 3 reprovações seguidas e o
  dono o suspendeu para a sessão ("sem limite de QA; QA continua obrigatório").

## O que foi entregue
- **Pré-voo rodada 1 registrado** (nomes dos campos do objeto de alteração; nenhuma receita com regra de modificação;
  autorização proposta; programa da C252) e **rodada 2** (PV-C5, C6, C7b, C9, C10, C11), com lista única do que rodar
  gerada por cópia integral das seções canônicas.
- **Biblioteca de consultas SAP** entre projetos (README, regras de escrita aprendidas com erro, índice, semântica),
  catálogo completo do MRP; **débito DB1** registrado no backlog do framework sem tocar o núcleo; handoff à sessão
  do framework, que ficou só com o modelo agnóstico.
- **Análise do feedback de outra IA (dogfood)**: veredito por achado, crítica (o escopo estreito foi decisão do dono;
  o prazo foi elicitado mas não propagado ao pacote) e 8 mudanças propostas para decisão.
- **Achado de prazo**: o repositório de discovery de 22/09 diz que o marco real é 01/11; o plano dizia 01/12.
- **Migração do projeto** para pasta única organizada por assunto, sem cópias, com links reescritos e conferidos.
- **Pacote "IDE conduz, revisora aprova"**: a outra IDE faz pré-voo, código, acompanhamento do DEV e dos testes
  IQ/OQ/PQ; a aprovação final volta para a IA autora da especificação, com critérios escritos.

## Placar gate × achado
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| "1.899 planos em 23/09" era número de 22/09; o erro estava copiado em 6 lugares, inclusive gerador e planilha | QA isolado, em 5 rodadas (cada uma achou mais uma cópia) | Autor: fato citado com fonte única, não copiado |
| Lista única de consultas resumida perdeu o "como ler" de 6 consultas (2 reprovações) | QA isolado | Redesenho: gerador copia a seção inteira e verifica por assert |
| C16 citada como retrato do "antes", mas é agregada | QA isolado | Autor: ler a consulta antes de citá-la |
| "Recai sempre na V5": generalização falsa para material de versão única | QA isolado | Autor: procurar o contraexemplo |
| `LIKE 'R_...'` sem `ESCAPE` (o `_` é curinga) | QA isolado | Autor |
| Heredoc colapsou barras invertidas (2 vezes na sessão), apesar de memória registrada | Python acusou erro de escape | Mecanismo, não memória: payload com barra vai pela ferramenta de edição |
| Reescrita de links por prefixo mandou a Q-A para a pasta errada; link `file:///` com acento não foi reescrito; correção parcial deixou a segunda ocorrência | QA isolado da migração (3 rodadas) | Conferência de links por script sobre todas as ocorrências |
| `.gitignore` do repo não cobria Word, PowerPoint e imagem recebidos das áreas | Autor, no ensaio do `git add` | Ensaio antes do commit |
| Recomendação de versionar planilhas contrariava a regra escrita do repositório | Autor, ao ler o `.gitignore` | Ler a regra do destino antes de recomendar |
| Marco 01/11 do discovery ausente do plano | Autor, no inventário para a migração | Projeto num só lugar |

## Detecção: framework × humano
O dono decidiu o escopo das três frentes novas (biblioteca como débito do framework, migração, IDE autônoma) e
suspendeu o circuit breaker. O QA isolado pegou todos os erros de conteúdo desta parte, mas precisou de várias
rodadas porque o mesmo fato estava copiado em vários arquivos. O inventário feito para a migração achou a
contradição de prazo que nenhum gate viu.

## Gaps
- Projeto espalhado (discovery em um repositório, análise em Downloads) esconde contradição entre documentos: o
  marco 01/11 passou 4 dias sem chegar ao plano.
- Não há ferramenta do framework para migrar projeto (manifesto, hash antes de apagar, reescrita e conferência de
  links); foi feita por scripts avulsos.
- Memória escrita (heredoc) não impediu a reincidência: prosa é lembrete, não trava.

## Melhorias (propostas ao framework, régua §0)
- **Fato com fonte única**: número medido vive num lugar (mapa de fontes) e os demais citam, em vez de copiar;
  reduz as rodadas de QA por propagação (régua §0 b).
- **Derivado por cópia integral**: artefato montado a partir de outro copia a seção inteira e verifica por assert,
  em vez de resumir (substitui revisão por mecanismo).
- **Pacote de desenvolvimento "IDE conduz, revisora aprova"** como padrão: fases F0 a F5 com critério de entrega
  escrito; funde com o padrão já pedido pelo dono (comece-aqui + prompt pronto).
- **Enquadramento de escopo e prazo no próprio pacote** (achado do dogfood): a leitora externa precisa ver por que o
  escopo é este e qual é o marco.

## Boas práticas
- Manifesto em ensaio antes de mover; hash conferido de novo imediatamente antes de apagar cada cópia.
- Arquivo de terceiro (registro da outra IA) preservado como recebido, fora da reescrita automática.
- Ensaio do `git add` antes do commit, e commit por lista explícita.

## Lições por skill
- **developer**: gerador que sobrescreve planilha guarda a anterior com carimbo até o segundo e sem colisão.
- **qa-critic**: pedir varredura completa (todas as ocorrências), não só a conferência dos pontos da rodada
  anterior; foi a varredura completa que fechou a migração.
- **docops**: ao mover um documento, procurar todas as referências a ele, inclusive `file:///` codificado.
- **pmo**: inventário antes de reorganizar revela contradição entre fontes; registrar como decisão do dono (D28).
