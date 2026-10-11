# Execution-report — encerramento de bloco (ADR-038/052 · tier OWNER · privado, não distribuído)

> Sessão de 11/10/2026: abertura ("iniciar") e pesquisa profunda sobre painéis operacionais de service desk
> (fila viva, TV, alerta, incidente), com QA isolado, publicada no repositório central de pesquisas.

- **Tokens:** NÃO MEDIDO — sem telemetria de token exposta ao agente. Parcial visível: 3 subagentes de pesquisa
  (~132 mil, ~195 mil e ~214 mil tokens) e 2 rodadas de QA (~216 mil e ~121 mil tokens), conforme o retorno de cada
  subagente
- **Tempo (wall-clock):** NÃO MEDIDO para a sessão; subagentes de pesquisa de 22 min, 31 min e 6,5 h (o de
  ferramentas ITSM esbarrou em páginas de aplicativo de página única)
- **Turnos:** NÃO MEDIDO
- **Arquivos tocados:** 3 entregáveis (relatorio.md, qa.md, META.md) + INDICE.md no repositório de pesquisas; 1
  rascunho criado e removido no projeto de origem; quadro de coordenação (fora de repositório)
- **Testes:** não se aplica (pesquisa, sem código)
- **Rodadas de retrabalho:** 2 rodadas de QA (11 achados → 5 baixos); circuit breaker não atingido

## Placar gate × achado (quem pegou o quê)
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Recomendação "manter tela X como visão de parede" contradizia o critério do próprio relatório (tabela longa na TV) | qa-critic rodada 1 | autor, ao cruzar seção de aplicação com a seção de critérios |
| Exemplo de "empate" na ordenação já era resolvido pelo desempate existente no código | qa-critic rodada 1 | autor: ler a linha de ordenação, não só a de pontuação |
| Citação entre aspas não localizável na fonte (veio da nota do subagente) | qa-critic rodada 1 | autor: aspas só para trecho conferido |
| Critério de "alerta permanente" aplicado a um cartão e não aos outros (viés) | qa-critic rodada 1 | autor |
| Norma citada sem a exceção ("salvo essencial") e "melhor prática" lida como requisito | qa-critic rodada 1 | autor / subagente de pesquisa |
| Decisões do projeto atribuídas sem base (comentário de código citado como decisão) | qa-critic rodadas 1 e 2 | autor: conferir o texto da decisão citada |
| Pontos verificados pelo autor no código antes do QA (estado "bom" sem uso; incidente já listado por serviço; três regras de pico) | autor (leitura do código) | — |
| Edição interrompida pela queda da sessão não gravou (N4) | autor ao retomar (grep do texto esperado) | — |

## Detecção: framework × humano (quem pegou o quê — mecanismo vs. revisão humana)
- Mecanismo (qa-critic isolado, Sonnet): 16 achados em 2 rodadas; nenhum alto.
- Humano (dono): nenhum achado; decisões vieram por outras sessões (destino central das pesquisas; texto conciso).
- Hook de resposta executiva apontou pedido ao dono no meio da resposta final e prosa longa.

## Gaps (não-bloqueantes detectados — flagados, não silenciados)
- Biblioteca de conhecimento sem pasta `assuntos/`; o saber geral passou a viver no repositório central de pesquisas. A
  regra 7 dos prompts de pesquisa ("registrar em assuntos/") ficou desatualizada em relação à decisão de destino central.
- Sessões encerradas não recebem mensagem (SendMessage falha); o quadro de coordenação é o único canal durável.
- Subagente de pesquisa deixou pasta temporária no scratchpad (downloads) e não conseguiu removê-la (effect-gate).

## Melhorias (do framework/processo — adição passa pela régua §0)
- Prompt de pesquisa: trocar "registrar em assuntos/" por "o repositório central de pesquisas é o registro" (edita o
  gerador de prompts existente; não adiciona).
- Instrução ao subagente de pesquisa: "aspas só para trecho literal conferido; paráfrase sem aspas" (1 linha no prompt).

## Boas práticas (o que funcionou — reutilizável)
- Três subagentes de pesquisa em paralelo por grupo de perguntas, cada um gravando notas em arquivo com URL, trecho e
  classificação; o autor redige a partir das notas e lê o código do projeto em paralelo.
- Ler o código citado na seção de aplicação antes do QA derrubou 3 recomendações erradas sem custo de rodada.
- Cópia do entregável antes de delegar o QA permitiu ao revisor da rodada 2 fazer diff contra a versão anterior.
- Mudança de destino no meio do bloco: conferir a decisão no arquivo de decisões antes de obedecer à mensagem da outra
  sessão.

## Lições por skill (agnóstico de domínio — o que daqui serve a OUTRO projeto)
- dev: — (sem código)
- discovery: pergunta "o que o mercado faz" precisa separar documentação oficial, fórum e snippet; documentação em
  aplicativo de página única costuma não abrir por ferramenta e vira DESCONHECIDO, não suposição.
- architect: — (nenhum neste bloco)
- qa-critic: o revisor deve receber as notas brutas além do relatório, para detectar distorção nota → texto (pegou
  aspas inventadas e "pausa existe" lido como "pausa visível").
- docops: ao retomar após queda de sessão, conferir por grep cada edição pendente antes de commitar.
- research/spec/ux: recomendação "manter X" exige aplicar ao próprio painel os critérios que o relatório definiu
  (consistência interna), e o mesmo critério a todos os elementos equivalentes (anti-viés).
