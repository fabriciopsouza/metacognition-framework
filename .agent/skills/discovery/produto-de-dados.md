# Discovery — Sub-modo Produto de dados

> Companion file do `discovery`. Progressive disclosure (ADR-003): carregado SOB DEMANDA.
> Fonte: ADR-134 (análise acompanhada); método recuperado de quatro produtos de dados do dono (pesquisa de 19/11/2026,
> só o método, sem dado de empresa). Conduzido em conversa, em lotes pequenos (regra do discovery de 19/08/2026).

## Filtro de entrada

Carregar quando **todos** valem:

1. O trabalho entrega um número, indicador, previsão, recomendação ou modelo que alguém usa para decidir.
2. A regra, a população ou a métrica ainda não estão congeladas em decisão registrada.
3. Há dado disponível ou a obter (a elicitação intercala com o perfil do dado, fase 1+2 da skill `analise-dados`).

Rejeita: painel só visual sobre regra já congelada (use `ux-design`), validação de migração contra referência
(use `validation-reporting`), processo de negócio (use `mapeamento-de-processo.md`).

## Banco de perguntas (priorizar as que mudam o trabalho)

| Tema | Perguntas-tipo |
|---|---|
| Problema de negócio | Qual o sintoma medido hoje? Quem sofre e com que frequência? O que já existe (planilha, protótipo, painel) e o que se aproveita? O que fica fora do MVP? |
| Decisão apoiada | Que decisão o gestor toma com o número, e com que frequência? Qual a pergunta literal (valor, série, ranking, meta, decomposição, regra, vigência)? O que o produto deve recusar? |
| Usuário | Quem usa, em qual canal e com qual credencial? O dado pode trafegar nesse canal? Quem é o dono do indicador, quem valida, quem publica? |
| População e universo | Herda a população de outro indicador? Cada motivo de exclusão entra ou sai? Quais status contam? Qual a unidade de contagem? Registro repetido, dividido ou republicado? A regra da fonte mudou no tempo? Há lista oficial de entidades? O pedido contradiz decisão congelada? |
| Métrica | Qual fórmula ou intervalo? Precisão e fuso? Marco vazio? A regra escrita reproduz o número publicado? Média, mediana ou ambas? Agregado ponderado ou simples? Polaridade e meta? |
| Janela | Data de competência? Mês fechado que muda: recalcula, congela ou congela com ressalva? Quando o período fecha? Período padrão? Rótulo de período aberto e sem dado? |
| Outliers e exclusões | Zero ou negativo? Teto e piso de sanidade? Corte estatístico ou gerencial? Limite inclusivo? Dispersão zero? Valores sintéticos repetidos? |
| Fonte e grão | Chave da entidade e de-para? Grão da linha? Cada dado necessário existe (OK, PARCIAL, FALTA, A VALIDAR)? Lacuna de acesso? Vigência do cadastro? |
| Validação | Qual número é o oficial? Quais casos reais de teste de mesa (típico, maior valor, fora de cada filtro, marco vazio, limite exato)? O export oficial está completo (contagem e cobertura, não só valores)? |
| Aceite | Critério binário? Métricas de escolha do modelo (erro escalado, cobertura de intervalo, viés)? Partição treino, validação e cega? Linha de base a superar? Limite de tempo de execução? |

## Procedimento (seis passos)

1. Teste de mesa primeiro (casos reais escolhidos com o dono).
2. Opções sem revelar a regra atual, em ordem aleatória, nas decisões de alto risco; nas demais, mostrar a recomendação.
3. Aceitar sempre "outro" e "não sei / quem sabe é X".
4. Mostrar o impacto medido de cada opção, sem adjetivo.
5. Registrar resposta literal, data e autor (D-nn; Parte I quando depende de terceiro).
6. Recalcular a amostra e comparar com o oficial.

## Saída

- Ficha de insumo completa (passo 4.1 do discovery, 8 campos).
- Problema, decisão apoiada, usuário e aceite na Parte A do `spec.md` único.
- Teste de mesa e inventário de dados (dado necessário × OK, PARCIAL, FALTA, A VALIDAR).
- D-nn das respostas; DEF-nn/VER-nn para o que depende da área (ADR-122).
- Questionário xlsx só sob pedido do dono ou quando a resposta depende de terceiros.
