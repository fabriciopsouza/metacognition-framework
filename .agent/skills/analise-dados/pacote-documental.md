# Pacote documental proporcional da análise (companion da skill `analise-dados`, ADR-134, B3)

Diz quais documentos uma análise produz, quando cada um entra e quando está pronto. Os arquivos vivem no repositório do
projeto, nunca no framework.

## 1. Níveis

| Nível | Critério de entrada |
|---|---|
| N1 análise pontual | responde uma pergunta uma vez; quem pede decide sozinho; nada roda de novo |
| N2 com terceiro | outra área confirma definição ou verifica resultado |
| N3 produto de dados | roda de novo (rotina, painel, modelo, indicador publicado) ou altera sistema |

1. DECLARAR o nível na fase 1+2, no diário. Na dúvida entre dois, vale o maior.
2. SUBIR de nível quando o critério aparecer no meio; registrar a mudança como D-nn. Nível não desce sem decisão do dono.
3. Ambiente regulado: o nível não dispensa documento exigido pelo perfil do projeto.
4. N3 sem terceiro não exige a Parte I/Parte J; N3 com terceiro soma as exigências de N2.

## 2. Peças

Sempre, em qualquer nível: diário da análise (linha de modo e painel de cada fase) e decisões D-nn.

`sim` = obrigatória; `se` = só na condição da coluna "Quando entra"; `não` = não se produz sem pedido do dono.

| Peça | N1 | N2 | N3 | Quando entra | Quem produz | Pronto quando |
|---|---|---|---|---|---|---|
| Briefing | se | sim | sim | fase 1+2; em N1, se o projeto ainda não tem um | discovery | objetivo, usuário, regras do repositório e estado por fase preenchidos |
| Diagnóstico e proposta | não | se | sim | fim da fase 1+2; em N2, se a proposta muda um processo da área | discovery e architect | métodos alternativos, métricas, riscos e decisões do dono escritos |
| Análise crítica do existente | se | se | se | fase 1+2, se já há solução ou número publicado | explorer | o que faz, achados e o que se aproveita, com a prova de cada achado |
| Inventário de dados | sim | sim | sim | fase 1+2 | esta skill | cada dado necessário com OK, PARCIAL, FALTA ou A VALIDAR |
| Decisão de arquitetura | não | não | se | antes da fase 6, se há escolha de arquitetura | architect | ADR do projeto com alternativa descartada |
| Especificação funcional (EF) | não | não | sim | antes da fase 6 | docops, com o gerador do projeto | cenários, fora de escopo, riscos e aprovações preenchidos no molde da empresa |
| Especificação técnica (ET) | não | não | sim | antes da fase 6 | developer e docops, com o gerador do projeto | dados, infraestrutura, segurança e desempenho preenchidos no molde da empresa |
| Questionário de elicitação | não | se | se | só a pedido do dono ou quando a resposta depende de terceiros | discovery | toda pergunta com resposta literal, nome e data |
| Checklist/runbook de execução | não | se | sim | fase 6; em N2, se outra pessoa executa passos | developer | `python tools/runbook_analise.py conferir <planilha> --final` passa e a leitura isolada foi registrada |
| Pedidos e respostas de QA por rodada | sim | sim | sim | fim de cada bloco, pela faixa (F0 registra só a conferência executada) | qa-critic | pedido, resposta e tratamento de cada achado guardados |

Com terceiro que confirma ou verifica: Parte I (DEF-nn) e Parte J (VER-nn) do arquivo único, pelas planilhas de
`python tools/planilhas_projeto.py` (ADR-122).

## 3. Roteiro

1. ABRIR o diário, escrever a linha de modo e o nível (seção 1).
2. LISTAR as peças do nível na tabela da seção 2; para cada `se`, escrever no diário a condição e a resposta.
3. PRODUZIR cada peça na fase da coluna "Quando entra"; peça `não` só com pedido literal do dono.
4. GERAR o runbook, quando entra:
   1. na pasta do framework, copiar `tools/templates/runbook-analise.json` para o repositório do projeto e preencher as marcas `[PREENCHER: ...]`;
   2. na pasta do framework: `python tools/runbook_analise.py gerar --conteudo "<caminho completo do JSON>" --out "<caminho completo, nome novo>.xlsx"`;
   3. na pasta do framework: `python tools/runbook_analise.py conferir "<caminho completo>.xlsx" --final`;
   4. mandar para a leitura isolada e tratar os achados; correção = nome novo.
5. GERAR EF e ET com o gerador e o molde do projeto (o framework não tem molde corporativo).
6. CONFERIR na fase 6 cada peça contra "Pronto quando"; peça que falta vira pendência com responsável e data.
