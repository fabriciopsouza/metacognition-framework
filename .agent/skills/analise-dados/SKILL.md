---
name: analise-dados
description: "Ativar em toda tarefa que toque dado, indicador, métrica ou modelo, em qualquer repositório: análise exploratória, conferência de número, regra de indicador, consulta que gera número, estatística, previsão ou modelo de ML. Conduz a análise por fases CRISP-DM no modo ACOMPANHADO (padrão de toda sessão): a cada fase mostra o painel com dado e procedimento, para nas decisões de escopo, métrica, exclusão, dado faltante, método, aceite e número publicado, e registra diário e decisões D-nn. Muda para AUTÔNOMO só por ordem do dono ('siga sozinha', 'autônoma', 'segue com CRISP-DM', 'me mostra no fim'), que vale dali em diante na sessão. NÃO ativar em tarefa sem dado (texto, configuração, código sem número). Validação de dado contra referência: esta skill conduz e usa validation-reporting como método do reporte."
version: 1.0.0
source: "pedido do dono e plano aprovado em 19/11/2026 (repositório central de pesquisas, pasta 2026-11-19_analise-acompanhada-humano-ia, seções 7.1 a 7.7, e prompt-uso-imediato.md da mesma pasta); ADR-134"
last_review: 2026-11-19
role_order: null
consumes:
  - "pedido que toque dado, indicador, métrica ou modelo"
  - "ficha de insumo do discovery (passo 4.1, ADR-089) ou fonte inequívoca para autopreenchê-la"
produces:
  - "diário da análise (md, só acréscimo) com o modo vigente e o painel de cada fase"
  - "registro de decisões analíticas D-nn (md) com literal, data, alternativa descartada e efeito"
  - "itens DEF-nn/VER-nn na Parte I/Parte J quando a decisão depende de terceiros (ADR-122)"
pass_criteria: "PASS sse: (1) o diário tem a linha de modo (modo, origem, literal) antes do primeiro painel e o primeiro painel de cada análise começa pelo modo vigente; (2) nenhuma fase avança sem painel gravado com os 7 itens do conteúdo mínimo; (3) toda decisão das 7 classes tem D-nn com literal do dono, ou marca PRELIMINAR revisada no fim quando em autônomo; (4) toda operação de filtro, junção, agregação, deduplicação ou identidade tem invariante declarada antes e conferida por script depois, com a saída anexada; (5) gatilho F2 (efeito irreversível, dado saindo da máquina, permissão ou credencial) parou a execução mesmo em autônomo."
confidence_required: true
enforcement:
  ide: "self-declared: prosa conduzida pelo agente; a fiação (skill, regra global, sub-modo do discovery) é conferida por tools/test_analise_dados.py e a ficha por tools/test_elicitation_gate.py; a conferência por invariante vira ferramenta no B2 do plano"
  chat: "self-declared: o agente segue as fases e grava o diário na conversa quando não há arquivo"
shared_refs:
  - _shared/confidence-classification
  - _shared/anti-hallucination
  - _shared/output-format
  - _shared/validation-reporting
---

# analise-dados — análise acompanhada humano-IA (CRISP-DM)

## Definições

- **Modo acompanhado:** a IA executa a fase, mostra o painel e para nas decisões das classes abaixo **antes de aplicá-las**, em lote por fase. Padrão de toda sessão.
- **Modo autônomo:** a IA segue as fases sem parar nas decisões; aplica a opção padrão, marca a decisão PRELIMINAR e apresenta a revisão no fim.
- **Diário da análise:** arquivo md do projeto, só acréscimo, com a linha de modo e o painel de cada fase.
- **D-nn:** decisão analítica numerada no registro de decisões do projeto (literal, data, autor, alternativa descartada, efeito medido).
- **Invariante:** propriedade que a operação de dado deve preservar, declarada antes e conferida por script depois.
- **Painel da fase:** resumo fixo que a IA entrega ao fim de cada fase (conteúdo mínimo abaixo).

## 1. Modos e regras de sessão

| Regra | Conteúdo |
|---|---|
| Padrão | acompanhado desde o início de toda sessão, inclusive sessão nova por fase |
| Ordem de autônomo | "siga sozinha", "autônoma", "segue com CRISP-DM", "me mostra no fim": vale **dali em diante na sessão**, para todas as análises da sessão |
| Volta | "análise acompanhada", "guiada", "quero acompanhar" |
| Onde o modo mora | no diário: `modo: <acompanhado|autônomo>, ordem de HH:MM, "<literal>"`, lido no início de cada fase; nunca só da memória (sobrevive a compactação) |
| Análise nova na mesma sessão | o primeiro painel diz na primeira linha `modo herdado: autônomo, ordem de HH:MM` |
| Ficha de insumo | autônomo só depois da ficha confirmada quando o risco for alto (passo 4.1 do discovery, ADR-089) |
| Gatilhos F2 | efeito irreversível, dado saindo da máquina, permissão ou credencial **param mesmo em autônomo** |
| Delegação | pedido a outra IA **dentro da sessão** leva o modo vigente; pacote para **sessão nova** (`python tools/handoff.py --modo <acompanhado|autonomo> --modo-origem "<literal, hora>"`) registra o modo da origem só como histórico, e a sessão nova começa acompanhada |
| Decisão aberta em autônomo | aplica a opção padrão, registra D-nn com as alternativas não executadas e marca PRELIMINAR; revisão das PRELIMINAR no fim é obrigatória |
| Opção padrão (nesta ordem) | (1) a regra já decidida em documento do projeto; (2) a regra que reproduz o número oficial publicado; (3) a mais conservadora: não excluir (marcar em vez de remover), não imputar, linha de base antes de modelo complexo, partição temporal quando houver tempo. Nenhuma se aplica: **para e pergunta, mesmo em autônomo** |
| Comandos em qualquer modo | "mostre <etapa>" executa a etapa do catálogo; "o que é X?" dá definição de uma frase com fonte; "questiono D-03" ou "volte à fase 2" reabre, com a versão anterior no registro; "pare em cada decisão" troca o lote pela pausa individual |

## 2. Ciclo por fase

Processo: CRISP-DM; com modelo, CRISP-ML(Q) (linha de base ingênua, divisão sem vazamento, métrica de negócio, ficha do
modelo, monitoramento). **Abertura de toda análise:** dizer em uma linha o modo vigente, oferecer o autônomo e abrir a
fase 1+2.

1. **Inspecionar:** rodar as etapas do catálogo que não dependem de decisão.
2. **Propor:** painel da fase, com o conteúdo mínimo:
   1. modo vigente e origem (linha do diário);
   2. fase e o que foi feito, com dado e procedimento (tabela ou gráfico, e a consulta ou o código);
   3. problemas de dados;
   4. decisões abertas, cada uma com alternativas e efeito medido, ou "efeito DESCONHECIDO: mede-se depois de <passo>";
   5. invariantes conferidas e resultado;
   6. confiança (CONFIRMADO, INFERIDO, DESCONHECIDO);
   7. o que preciso de você (no fim).
3. **Decidir:** acompanhado para nas decisões das classes da seção 4 **antes de aplicá-las**, em lote por fase; autônomo segue a regra de decisão aberta.
4. **Aplicar** e conferir a invariante da operação.
5. **Registrar:** painel no diário (só acréscimo); decisão no D-nn; o que depende da área vai para a Parte I (DEF-nn) ou a Parte J (VER-nn) do arquivo único (`tools/planilhas_projeto.py`, ADR-122).

Fase 1+2 (negócio e dados juntas) começa pela **ficha de insumo** do discovery (passo 4.1, 8 campos), em qualquer risco; com fonte inequívoca, autopreencher e declarar. Produto de dados novo ou indicador a definir: carregar o sub-modo `produto-de-dados` do discovery.

## 3. Invariante por operação

Declarada antes de aplicar; conferida por script depois; saída anexada ao painel. Até a ferramenta do B2 existir, a conferência usa o script do projeto.

| Operação | Invariante |
|---|---|
| Filtro ou exclusão | contagem cai pelo número esperado e o funil fecha (entrou = ficou + saiu, por motivo) |
| Junção | cardinalidade esperada declarada (1:1, 1:N); linhas órfãs contadas dos dois lados |
| Agregação | soma da medida preservada entre o detalhe e o agregado |
| Deduplicação | chave única depois; removidas = duplicadas contadas antes |
| Sem operação de dado (renomear, reordenar) | identidade: contagem e soma iguais |

Contagem e soma iguais não provam integridade sozinhas: troca de valores entre linhas preserva as duas; conferir soma por grupo.

## 4. Classes de decisão que param o acompanhado

| Classe | Exemplo |
|---|---|
| Escopo e população | quem entra, quem sai, unidade de contagem |
| Métrica e janela | fórmula, competência, congelamento |
| Exclusão e outlier | corte estatístico × gerencial, limite |
| Dado faltante | descartar, imputar, marcar |
| Método e modelo | explicar × prever, família, variável-alvo, partição |
| Aceite | limiar, métrica de escolha |
| Número publicado | mudança que altera número já divulgado |

Fora dessas classes a IA segue e registra; qualquer D-nn pode ser reaberta depois. Nas decisões de alto risco destas classes, mostrar as opções antes da recomendação (o dono decide antes de ver a preferência da IA); nas demais, mostrar a recomendação.

## 5. Catálogo de etapas invocáveis

Escrito aqui para valer em qualquer IA. Skills de dados do ambiente, quando houver (ex.: `explore-data`, `statistical-analysis`, `validate-data`), são acelerador, não requisito.

| Fase | Etapa | Executor |
|---|---|---|
| Dados | resumo estatístico; top N e bottom N; nulos e vazios; cardinalidade; duplicidade de chave; distribuição; cauda e outliers; série temporal e períodos incompletos; segmentação | esta skill + perfil do projeto |
| Dados | conferência contra o oficial (contagem, cobertura, reprodução do número publicado); inconsistências classificadas por efeito (número, regra, dado) | consulta do projeto + conferência por invariante |
| Preparação | funil bruto → filtro → elegível; efeito de cada exclusão; unicidade da chave depois das exclusões | script do projeto + conferência por invariante |
| Inferência estatística | pergunta (explicar × prever); pressupostos e diagnóstico (resíduos, normalidade, independência); tamanho de efeito com intervalo; múltiplas comparações | esta skill |
| Modelagem preditiva | linha de base ingênua; partição sem vazamento (temporal quando houver tempo); candidatos; métrica de negócio | esta skill + script do projeto |
| Avaliação | erro contra a linha de base; cobertura de intervalo; viés; robustez às alternativas (multiverso reduzido: as 2 ou 3 escolhas mais contestáveis, com o efeito de cada uma); bateria de casos | script do projeto |
| Implantação | ficha de dados e de modelo; canário; monitoramento; runbook xlsx (molde Parte C); EF/ET quando virar produto | molde do runbook + gerador do projeto |

## 6. Entregas mínimas por fase

| Fase | Entrega mínima |
|---|---|
| 1+2 Negócio e dados | ficha de insumo; problema, decisão apoiada, usuário, aceite; teste de mesa; inventário de dados; perfil; conferência contra o oficial |
| 3 Preparação | funil, efeito de cada exclusão, unicidade da chave |
| 4 Modelagem | linha de base, partição, candidatos, métrica; na inferência, pressupostos e diagnóstico |
| 5 Avaliação | erro contra a linha de base, viés, robustez às alternativas, bateria |
| 6 Implantação | ficha de dados e de modelo, canário, monitoramento, runbook; EF/ET quando virar produto |

## 7. Documentação proporcional

- Sempre: diário e D-nn.
- Quando há terceiro que confirma ou verifica: Parte I (DEF-nn) e Parte J (VER-nn).
- Quando vira produto: runbook xlsx (molde Parte C) e EF/ET.
- Artefatos de cada análise vivem no repositório do projeto, nunca no framework.

## 8. Verificações da QA da análise

1. A regra escrita não é a regra calculada: reproduzir o publicado antes de aceitar o texto.
2. Conferir contagem e cobertura, não só valores presentes (export truncado passa).
3. Todo gate audita o universo, não só uma amostra.
4. Separar fórmula (determinística), mapeamento (verificável) e regra de negócio (decisão do dono).
5. Perguntar de onde veio o alvo de comparação.
6. Anomalia vista exige causa-raiz.
7. Exclusão reescreve o espaço de chaves: conferir unicidade depois dela.
8. Ler as decisões já tomadas antes de perguntar.
9. "Aprovado" ou "validado" só com consulta executada **e** conferência com o oficial; antes disso, "candidato".
10. Exemplo neutro, nunca número real do projeto.

## Fronteiras

- NÃO decide no lugar do dono as classes da seção 4 em modo acompanhado.
- NÃO substitui o `qa-critic` (revisão adversarial do bloco). Na validação ponto a ponto contra referência, esta skill conduz as fases e o `validation-reporting` dá o método e o reporte.
- NÃO grava artefato de análise de empresa no framework (isolamento entre empresas).
