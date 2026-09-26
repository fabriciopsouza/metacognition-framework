# Execution-report — sessão framework 25–26/09/2026 (ADR-038/052 · tier OWNER · privado, não distribuído)

- **Tokens:** NÃO MEDIDO — sem telemetria de token exposta ao agente (dependência do host; ver LIMITS.md)
- **Tempo (wall-clock):** NÃO MEDIDO
- **Turnos:** NÃO MEDIDO
- **Blocos entregues (mesclados na main):** 8 — PR #154/#156 (ADR-116), #157 (ADR-117), #158 (ADR-118), #159 (plano
  B3), #161 (ADR-119), #163 (ADR-120), #165 (emenda 2 do ADR-033), #168 (ADR-121)
- **Canários:** 94 na suíte ao fim; último `canarios-local` 93 PASS, 1 SKIP, 0 FAIL (PR #168)
- **Rodadas de retrabalho (QA isolado, reprovações corrigidas):** B3a-1 1 · B3e 2 · B3d 2 · M1 0

## Placar gate × achado (quem pegou o quê)
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Requisito escrito com `*` sumia e a especificação passava (B3a-1) | revisão isolada, rodada 1 | `test_regulado` (não tinha o caso; passou a ter) |
| Parte F vazia passava com impacto regulado (B3a-1) | revisão isolada, rodada 1 | idem |
| Campos antes do 1º `##` e entrada com `###` sumiam em silêncio (B3e) | revisão isolada, rodada 1 | `test_conhecimento` |
| Falso positivo criado pela própria correção (campo depois do SQL) (B3e) | revisão isolada, rodada 2 | idem |
| Manifesto corrompido derrubava o registro; docx aberto deixava gerados inconsistentes (B3d) | revisão isolada, rodada 1 | `test_evidencia`, `test_desenho_processo` |
| Falha no meio da escrita não voltava ao estado anterior (B3d) | revisão isolada, rodada 2 | `test_desenho_processo` |
| Frase só com códigos no CHANGELOG | `test_escrita_padrao` (canário da suíte completa) | — o gate pegou; eu não tinha rodado a suíte antes do PR |
| Justificativa falsa na proposta do dogfood (9 de 11 especificações já reprovavam) | revisão isolada | autor não rodou o gate antes de afirmar |
| Regra global nova não instalada na máquina após o merge | sessão MRP (outra sessão) | nenhum: lacuna registrada (`regra-global-instalar-apos-merge`) |

## Detecção: framework × humano (quem pegou o quê — mecanismo vs. revisão humana)
- Mecanismo: revisão isolada (Sonnet) pegou 100% dos defeitos de código antes do merge; mutação do autor achou 8
  sobreviventes ao longo dos blocos (teste que reprovava pelo motivo errado, regra redundante, legenda mascarando o
  retorno), todos convertidos em caso de teste ou remoção.
- Humano (dono): pegou que o autor executava sem criticar e sem responder às perguntas feitas ("saiu fazendo como
  web chat"), que o DB1 duplicava o D9 já aprovado, e que o formato de "status" pedido várias vezes não era seguido.

## Gaps (não-bloqueantes detectados — flagados, não silenciados)
- Regra global só chega à máquina no próximo início de sessão (`regra-global-instalar-apos-merge`).
- Revisor em só-leitura continua em prosa, sem bloqueio (`subagente-revisor-so-leitura`).
- Índice de projetos da biblioteca vazio: `conhecimento.py verificar --trabalhos` acusa os projetos de domínio com
  trabalho aberto até as sessões de domínio preencherem.

## Melhorias (do framework/processo — adição passa pela régua §0)
- Dimensões `obr=unico`: obrigação nova vale só no formato novo, sem reprovar nem fabricar resposta para o passado.
- Comando permanente `status` com formato fixo na regra global (tabela com % + 3 linhas).
- Método único de projeto como porta de entrada, ligado aos guias existentes em vez de reescrevê-los.

## Boas práticas (o que funcionou — reutilizável)
- Mutação própria rodada depois do canário verde: pegou teste que reprovava pelo motivo errado em 3 blocos.
- Renderizar o entregável visual (Edge headless) antes de declarar pronto: pegou rótulos sobrepostos.
- Gravação "tudo ou nada" para gerados: afastar os anteriores, escrever, conferir os três, e voltar em qualquer falha.
- Conferir fato do outro lado antes de responder a outra sessão (repositório privado × público).

## Lições por skill (agnóstico de domínio — o que daqui serve a OUTRO projeto)
- dev: correção que muda a regra de parsing pede caso que prove que a regra antiga não voltou E que a nova não
  criou falso positivo (B3e rodada 2).
- discovery: pergunta do dono se responde antes de virar opção numa tabela; decisão nova que cruza decisão aprovada
  (D2 × D9) se aponta, não se executa.
- architect: antes de plano novo, procurar se o pedido é extensão de decisão já aprovada (DB1 = D9 estendido).
- qa-critic: com 2 reprovações seguidas, a 3ª rodada pede escopo curto e só achado reproduzido.
- docops: rodar a suíte completa de canários ANTES de abrir o PR, não um subconjunto.
- research/spec/ux: relatório de outra IA é dado a validar arquivo por arquivo (o registro de dogfood afirmava um
  arquivo "vazio" que tinha 4 respostas).
