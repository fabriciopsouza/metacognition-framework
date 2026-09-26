# Andamento — 25–26/09/2026 (bloco C): CAPA — desenho CAPA ↔ BAU, runbooks R-07..R-16 e o pacote documental

> Execution-report de encerramento (ADR-038/052/062 · tier OWNER · privado). Trabalho de **domínio**
> no repositório `capa-sharepoint`; nada do núcleo alterado. Continua o bloco D de 24/09.

## Onde estamos, em uma linha

O dono assumiu a construção do F1; o processo foi redesenhado sobre o BPMN dele (CAPA ↔ BAU, só por
mensagem), e o projeto ganhou runbooks do processo inteiro, glossário, ontologia, dicionário de dados,
ponto de retomada e pastas limpas — publicado por PR após QA isolado aprovado com ressalvas.

## Métricas

| Métrica | Valor |
|---|---|
| Tokens | **NÃO MEDIDO** |
| Commits no domínio publicados neste PR | 23 (medido: `git rev-list --count origin/main..main`) |
| Rodadas de QA isolado (Sonnet, autor Opus) | 18, em 7 blocos; 8 reprovações |
| Correções de rumo pelo dono | 3 no mesmo assunto (sentido CAPA ↔ BAU) |

## O que aconteceu

1. **R-06 v4 e R-07:** achados A-06 a A-09 registrados (rótulo escrito de memória, `M` no lugar do `T`,
   Outlook 404, fixture DEMO sem coluna Pessoa). R-07 virou montagem direta em 10 PARTES, no formato
   enxuto do runbook OAuth do migracao-sac, com calendário do modo exato calculado das 12 linhas DEMO.
2. **Desenho para a GQ** (HTML com SVG à mão): o dono preferiu ao BPMN em mermaid — layout automático
   ilegível e o VS Code não renderiza mermaid sem extensão.
3. **CAPA ↔ BAU:** li o `.bpm` do Bizagi pelo XML (2 diagramas; o `CAPA-BAU-2.bpm` era um PDF
   renomeado). Correções em BPMN 2.0: link entre pools → mensagem; gateway complexo e paralelo com
   condição → exclusivo; tipo de tarefa em vez de raia de sistema.
4. **Pacote documental:** runbooks R-08..R-16, `GLOSSARIO`, `ONTOLOGIA`, `DICIONARIO-DE-DADOS`,
   `ONDE-ESTAMOS`, README como porta única; obsoletos para `arquivo/` com `INDICE.md`.

## O placar gate × achado

| Achado | Quem pegou |
|---|---|
| Li "ao inserir a ação no BAU ela vai para o CAPA" como a **ação**; era a **resposta** | **o dono**, três correções seguidas |
| Chamei de "defeito mais grave" o subprocesso que o dono desenhou de propósito | **o dono** |
| Dias da semana deslocados no calendário (vinha da v1, passou por 3 revisões) | QA isolado, 4ª revisão |
| Resíduo vivo de `BAU_ID`/B-2 que minha varredura não viu (o grep excluía a linha inteira quando havia trecho riscado) | QA isolado r2 |
| Mapeamento do F6 que tornava "Encerrada pela GQ" inatingível | QA isolado r1 |
| Gateway baseado em eventos saindo direto para tarefa; mensagem terminando em gateway | QA isolado |

## Lições (para o framework)

- **Modelo do dono é fonte.** Divergência entre fala e BPMN se resolve perguntando o **sentido**; eu
  ofereci "as duas (Recomendado)" e o dono escolheu uma opção que eu mesmo tinha deformado. Memória:
  `modelo-do-dono-e-fonte-nao-defeito`.
- **Varredura de resíduo precisa remover o texto riscado antes de buscar**, não excluir a linha: com a
  regra 1 (riscar, não apagar), quase toda linha corrigida tem trecho riscado, e o `grep -v` escondia
  justamente as linhas meio-corrigidas.
- **Diagrama para humano: SVG à mão; mermaid é fonte técnica.** Memória:
  `diagrama-svg-a-mao-melhor-que-mermaid`.
- **`--dump-dom` do Edge headless devolve a página antes do script terminar** — não serve de prova de
  render; a captura de tela com o status escrito pela própria página serve.

## Procedência

- Domínio: `C:\Users\fabriciosouza\capa-sharepoint`, publicado por PR em 26/09.
- Fontes lidas, só leitura: `C:\Users\fabriciosouza\OneDrive - Natulab Laboratorio S.A\Documents\CAPA-BAU.bpm`;
  `C:\Users\fabriciosouza\excelencia-master-plan` (referência de estilo).
- A reunião que o dono citou **não foi encontrada** no disco; a única transcrição (02/09) não menciona o BAU.
- **Não medido:** tokens, tempo; o resultado da execução do R-07 pelo dono.
