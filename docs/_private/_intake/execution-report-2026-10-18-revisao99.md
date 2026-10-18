# Execution-report — encerramento de bloco (ADR-038/052 · tier OWNER · privado, não distribuído)

> Sessão Claude Code de 16/10 (abertura) a 18/10/2026: Revisão 99 do painel de atendimento, entregue ao Kiro por ordem do dono.

- **Tokens:** input 88,902 + output 49,636,124 = 49,725,026 (fonte: transcripts do Claude Code, ADR-026)
- **Tempo (wall-clock):** NÃO MEDIDO (sessão de cerca de 2 dias corridos, com pausas; o relógio exato não está exposto)
- **Turnos:** NÃO MEDIDO
- **Arquivos tocados:** 8 PRs no repositório do painel (#27 a #33 mesclados; #34 em rascunho): #27 a #29 são registros na FILA e #30 a #34 são código; cerca de 57 commits em `pesquisas` desde 16/10, número que pode incluir outras sessões; framework com 1 arquivo (este)
- **Testes:** suítes rápidas, caracterização e `07_testa_app` verdes a cada PR mesclado; sabotagens em toda regra nova (mais de 30 no total)
- **Rodadas de retrabalho:** QA isolado em todas as entregas, quase sempre 2 rodadas (R1 com ressalvas, R2 PASS); a spec do B11 passou por 4 rodadas (fonte: §14 de `especificacoes\B11.md`)

## Placar gate × achado (quem pegou o quê)
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Seta "▲" fixa para "piora" numa tela e para "melhora" noutra | Diagnóstico do B37 (crítica por capturas) | Teste de contrato de seta e cor; não existia; criado no B38-a (`testa_cores.py`) |
| "Hoje" ancorado na data do último dado, coleta parada há 8 dias em silêncio | Dono, ao ver "Esta semana" até 09/10 em 17/10 (fonte: `R99-28-critica-tempo-comparacao-one-page.md`, achado T1) | Monitor de frescor; existia só na tela 0 e na TV; levado a todas as telas no B42a |
| Fila de agora com números diferentes entre telas | Diagnóstico do B37 | Prova de recorte por medida; inexistente; virou lição 7 do produto-bi (fonte: `2026-10-17_painel-operacional-licoes-para-produto-bi\relatorio.md`; P125 em `pedidos-durante-a-revisao.md`) |
| `DECISOES.md` convertido inteiro para CRLF num commit | QA isolado do B38-a | Comparar `git diff --stat` com e sem `--ignore-space-at-eol` antes do commit; virou passo do procedimento |
| Sabotagem que não mordeu: `.pyc` em cache e regex sensível a maiúsculas | O próprio autor, ao conferir a saída da sabotagem | Rodar sabotagem com `python -B`; casar padrão sem distinção de maiúsculas |
| Faixa de coleta parada dizendo "os períodos contam até" a data errada | QA isolado do B42a | Teste de texto contra a fonte do corte (`M.HOJE`); acrescentado |
| Trava de HTML reprovando `ESTADO[..][..]` | `07_testa_app` (trava do B10) | Funcionou como deveria |
| Barra de topo de 280 px empurrando os dados | Dono, ao ver a prévia | Aceite medido de "cartões até X px do topo"; criado depois (R99-30) |
| Texto verborrágico em todo o painel | Dono | Lei do texto com trava executável; criada (R99-29) e ainda não implantada (B39) |
| Spec referindo seletor que "não existia", mas existia | QA da spec do B11 | Conferir âncora por grep antes de afirmar ausência |

## Detecção: framework × humano (quem pegou o quê — mecanismo vs. revisão humana)
- **Mecanismo pegou:** a trava de HTML do B10; as caracterizações (cada texto trocado aparecia no diff); o QA isolado em todas as entregas (CRLF, ponto de corte, sentido trocado na B37-176, sequência × sobreposto, "firme" na face); `07_testa_app`.
- **Humano (dono) pegou:** o "hoje" errado; a verborragia; a barra gigante; a ordem errada da fila (textos aprovados atrás do código); o pedido de pesquisar antes de fazer. **Todos de experiência de uso, nenhum de código.** O mecanismo cobre bem a correção e mal a experiência.

## Gaps (não-bloqueantes detectados — flagados, não silenciados)
- A conferência visual (P-M.12) só existiu porque o autor a fez à mão; não há gate de "prévia mostrada ao dono antes do merge" em mudança visível.
- O agente desenvolvedor caiu por erro de API ("connection refused") com 22 arquivos sem commit; o trabalho só foi salvo porque o orquestrador fez um commit WIP. Não há mecanismo de proteção automática.
- O `07_testa_app` leva de 6 a 20 min e às vezes estoura tempo sob carga; a sessão perdeu rodadas interrompendo-o para aplicar QA.
- A sessão do produto-bi saiu do ar entre duas mensagens; aviso por mensagem a sessão morta falha. O quadro de coordenação foi o canal durável.

## Melhorias (do framework/processo — adição passa pela régua §0)
- **Prévia antes do merge** em toda mudança visível: um passo do procedimento, não um bloco novo. Funde com o QA de capturas que já existe.
- **Commit WIP automático** do orquestrador antes de delegar implementação longa: transforma a regra "proteja o trabalho não salvo" num passo executável.
- **Lei do texto como regra do framework, com trava reutilizável:** decisão do dono pendente; recomendado depois de provada no B39.

## Boas práticas (o que funcionou — reutilizável)
- Escolher cor por cálculo (contraste WCAG mais simulação de daltonismo), transformar o critério em teste e provar com sabotagem.
- Movimento puro de código com prova por AST e fichas de tokenize, comparação de captura pixel a pixel e caracterização sem diferença: refatoração grande sem risco.
- Pesquisa de referências **antes** de redesenhar, quando o dono rejeita algo visual; a pesquisa trouxe padrões convergentes e o que não copiar.
- Registro de toda decisão do dono com a frase literal e o destino (bloco), em arquivo versionado.
- Troca de lições nos dois sentidos com o produto irmão, neutra de empresa.

## Lições por skill (agnóstico de domínio — o que daqui serve a OUTRO projeto)
- dev: sabotagem precisa rodar sem cache de bytecode; trava de texto com regex sem distinção de maiúsculas; edição de arquivo por script que aborta quando a âncora não existe evita troca errada em lote.
- discovery: quando o dono corrige um exemplo, perguntar-se qual é o método por trás. Ele quase sempre quer a regra geral, não a troca pontual.
- architect: período e "hoje" são decisões de produto, não detalhe: "hoje = último dado" esconde coleta parada.
- qa-critic: a revisão adversarial pegou sentido trocado, fim de linha e afirmação falsa de ausência. Vale pedir explicitamente "conflito com decisões do dono" no prompt do revisor.
- docops: texto de handoff e de spec segue a mesma lei do texto que a interface.
- research/spec/ux: controle que quebra linha ou empurra o dado para baixo é defeito; o dado vem antes da navegação; mostrar a prévia antes do merge.
