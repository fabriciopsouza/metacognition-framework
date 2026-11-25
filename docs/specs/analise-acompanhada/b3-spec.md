# B3 — Modelo de runbook de análise e roteiro do pacote documental: especificação de execução

- Origem: plano aprovado pelo dono em 19/11/2026, repositório central de pesquisas, `2026-11-19_analise-acompanhada-humano-ia/relatorio.md`: seção 7.8 (linha B3), 7.3 ("abas da 5.6 com as fases CRISP no Roteiro"), 5.6 (peças e abas); molde da Parte C de `_shared/output-format/SKILL.md`.
- Faixa: F2 (`risk_score.py`: `regra_release_adr`, `multi_sessao_sistema_pessoa`). Autor: Opus. Revisões alternadas: Codex (ímpar), Sonnet (par).
- Branch: `feat/b3-runbook-analise`, worktree própria, a partir de `origin/main` `0375ee9`.

## 1. Entregas

| # | Entrega | Arquivo | Situação |
|---|---|---|---|
| E1 | Gerador e conferência do molde: `gerar [--conteudo c.json] --out x.xlsx` e `conferir x.xlsx [--final]` | `tools/runbook_analise.py` | novo |
| E2 | Conteúdo do modelo, só dado fictício e marcas `[PREENCHER: ...]`, com as 5 fases CRISP no Roteiro | `tools/templates/runbook-analise.json` | novo |
| E3 | Canário: gera, reabre, confere abas e colunas contra literais do teste; sabotagens da seção 3 | `tools/test_runbook_analise.py` | novo |
| E4 | Roteiro do pacote documental proporcional: 10 peças da 5.6 × quando entra × quem produz × pronto quando; três níveis | `.agent/skills/analise-dados/pacote-documental.md` | novo |
| E5 | CHANGELOG | raiz | previsto no plano |
| E6 | Registro `runbook-analise` em `capabilities.json` + `CAPABILITIES.md` (o canário barra ferramenta órfã); números do site | raiz, `guia/web/index.html` | desvio declarado |
| E7 | Ponteiros para E1 e E4 nas seções 5 e 7 da skill `analise-dados`; versão 1.2.0 | `.agent/skills/analise-dados/SKILL.md` | desvio declarado |
| E8 | Handoff de 20/11/2026, só o arquivo datado do commit local `c1fd22d` | `docs/_private/handoffs/2026-11-20-B2-B3-analise-acompanhada.md` | novo (pedido do dono, 24/11/2026) |

**Desvio declarado (E6, E7):** a linha B3 diz "só arquivos novos; CHANGELOG". Ponteiros e contagens são efeito necessário (mapa de impacto): sem ponteiro a entrega fica inalcançável; sem registro o canário reprova. Restrito a ponteiros e contagens. Nada em `qa-critic`.

## 2. Decisões do autor (premissas declaradas)

1. **Abas:** Painel, Leia antes, Roteiro, Copiar e colar, Referência, Links, uma aba por runbook (nome começa por "Runbook"), Pendências, Decisões, Histórico. É a 5.6 na ordem dela, mais a regra da Parte C "uma aba por runbook usado".
2. **Colunas do Roteiro:** texto da Parte C, de que a 5.6 é forma curta: Parte · Nº · Faça · Onde no runbook · Se der errado · Status · Data/hora · Mensagem de erro ou observação · Resposta do dono.
3. **Parte = fase CRISP:** `1+2 Negócio e dados`, `3 Preparação`, `4 Modelagem`, `5 Avaliação`, `6 Implantação`, nesta ordem. O modelo traz as 5; runbook sem modelo estatístico pode omitir fase.
4. **Gerador no framework:** a skill dizia "molde do runbook + gerador do projeto". A Parte C, item 1, exige planilha gerada por script versionado; um gerador único com conteúdo em JSON evita um script por projeto. Fica no projeto o conteúdo (JSON) e o gerador de EF/ET (T9 do plano adiou só o DOCX). A linha da skill passa a dizer isso.
5. **Reuso de `tools/planilhas_projeto.py`, sem alterá-lo:** importa `_aba_tabela` (cabeçalho, quebra, `=` como texto, congelamento), `_aba_texto` e `_abrir` (leitura por bytes). Próprios: Painel (fórmulas, que `_aba_tabela` converteria em texto), Copiar e colar (bloco por lista) e as regras visuais do Status.
6. **Painel:** por fase, Feitos · Pulados · Total · % · Erros. Total desconta Substituído (Parte C); % = (Feitos + Pulados) / Total: Pulado = não se aplica, e sem ele a fase nunca fecha 100%. "Onde parei" = primeira linha Pendente, Erro ou sem status.
7. **Sobrescrita (Parte C, item 9):** recusa qualquer destino já existente, marcado ou não; versão nova tem nome novo.
8. **Alteração em massa (Parte C, itens 7 e 8):** o passo que altera em massa leva `EM MASSA` na ação em maiúsculas e cita `lista "<nome>"` da aba Copiar e colar. Antes dele, nesta ordem: passo que começa por `GUARDAR`, passo com `1 ITEM DE TESTE`, passo que começa por `CONFERIR`. Lista vazia só reprova quando um passo em massa a consome; sem passo em massa, a aba pode dizer "Não se aplica".
9. `gerar` confere o arquivo antes de gravar no destino; reprovou, nada é gravado.
10. Nenhum nome de empresa, tabela, sigla ou valor de projeto (repositório público).
11. **Alcance da conferência:** planilha produzida por este gerador, antes ou depois de marcada. Planilha Parte C feita por outro gerador não é submetida a ela. Passo novo durante a execução entra por versão nova (Parte C, item 9), não por linha digitada.
12. `openpyxl` é dependência de desenvolvimento já declarada; ausente, o canário dá SKIP e a ferramenta sai com exit 2 e a instrução de instalação.

## 3. Regras da conferência (cada uma com sabotagem no canário)

| Regra | Conteúdo |
|---|---|
| R1 | as 9 abas fixas na ordem; ≥ 1 aba de runbook, todas entre Links e Pendências; nenhuma outra aba |
| R2 | cabeçalho do Roteiro com as 9 colunas, na ordem; a coluna que falta é nomeada (aceite: sem Status reprova) |
| R3 | ≥ 1 passo; Parte, Nº, Faça, Onde e Se der errado preenchidos; Nº único, no formato 1.1, em ordem (ordenar linhas quebra o "onde parei"; filtrar não) e sem lacuna (linha apagada some dos erros em aberto); Parte é uma fase da decisão 3, em ordem e contígua |
| R4 | Faça: AÇÃO EM MAIÚSCULAS até o primeiro ponto; clique a clique numerado (`1)` ou `1.`); termina em `Deu certo: <como saber>` |
| R5 | Onde no runbook = `<aba de runbook>, passo <n>`, com a aba e o passo existentes |
| R6 | Se der errado: `Pare` ou `Siga`; `não repita`; `copie o texto exato`; `avise <quem>` |
| R7 | lista do Status (Pendente, Feito, Erro, Pulado, Substituído) cobre todas as linhas, com o texto exato e barrando valor de fora; todo valor de Status está na lista, sem espaço a mais; Erro sem mensagem e Pulado sem motivo reprovam |
| R8 | cor do molde para cada um dos 5 status em todas as linhas, filtro no cabeçalho, cabeçalho congelado |
| R9 | Painel só por fórmula: onde parei, erros em aberto, e uma linha por fase do Roteiro, com as fórmulas exatas da decisão 6 |
| R10 | Leia antes: 3 passos, regras numeradas, palavras usadas, como marcar (Erro, Pulado, Substituído, nome do print) |
| R11 | Copiar e colar: "Como colar" no topo, um valor por linha, como texto (formato `@`, nunca fórmula); nome de lista não se repete |
| R12 | cabeçalhos de Referência (Teste · Esperado), Links, abas de runbook, Pendências, Decisões e Histórico (≥ 1 versão) |
| R13 | com `--final`: nenhuma marca `[PREENCHER` e ≥ 1 linha na Referência |
| R14 | alteração em massa: sequência GUARDAR → 1 ITEM DE TESTE → CONFERIR antes, e lista citada existente e não vazia (decisão 8); passo em massa executado (Feito ou Erro) exige os três Feitos; Substituído nunca conta |

### 3a. Parte C × conferência

| Item da Parte C | Quem confere |
|---|---|
| 1 (xlsx por script), 2 (abas e colunas) | R1, R2, R7 a R12 |
| 3 (uma linha = uma ação; maiúsculas; clique a clique; como saber) | R4; "uma ação só" e os nomes reais de tela: revisão humana (QA isolado) |
| 4 (nome técnico entre parênteses; termo novo explicado), 6 ("(INFERIDO)" ou "a conferir na tela") | revisão humana; critério: todo termo do Roteiro fora do uso comum está em "Palavras usadas" |
| 5 (se der errado) | R6 |
| 7 e 8 (segurança) | R14; passo em massa sem a marca `EM MASSA`: revisão humana |
| 9 (nome novo, não sobrescrever) | `gerar` |
| 10 (QA isolado, uma versão por entrega) | aceite 7; no projeto, passo do Roteiro e linha do pacote documental |

### 3b. Conteúdo mínimo do modelo (E2), conferido no canário por presença e na QA por adequação

| Fase | Passos que o modelo traz |
|---|---|
| 1+2 Negócio e dados | registrar o modo vigente no diário; conferir a ficha de insumo; extrair; perfilar; conferir contra o oficial; painel da fase e decisões D-nn |
| 3 Preparação | declarar invariante; aplicar filtro com funil; `conferir_invariante.py`; unicidade da chave; painel e D-nn |
| 4 Modelagem | linha de base; partição; rodar o cálculo ou modelo; painel e D-nn |
| 5 Avaliação | erro contra a linha de base; viés e robustez; bateria de casos; painel e D-nn de aceite |
| 6 Implantação | ficha de dados e de modelo; guardar os valores de hoje; 1 item de teste; conferir; publicar em massa; canário e monitoramento; QA isolado; fechar versão |

Saída: JSON com veredito e achados; exit 0 passa, 1 reprova, 2 erro de uso (arquivo ausente, não xlsx, JSON inválido, destino existente).

## 4. Aceite

1. O modelo gerado reabre no canário com as abas da 5.6 e as 5 fases; no Excel desta máquina abre sem reparo e o Painel recalcula (evidência anexada ao veredito).
2. Sabotagem do plano: aba Roteiro sem a coluna Status reprova a conferência, com o nome da coluna.
3. Cada regra R1 a R14 tem caso legítimo que passa (inclusive planilha já marcada com os 5 status) e defeito que reprova com o achado daquela regra.
4. `gerar` recusa destino existente, com os bytes intactos; conteúdo que reprova não grava nada.
5. Roteiro do pacote: tabela com as 10 peças da 5.6 × quando entra × quem produz × pronto quando; três níveis (análise pontual; análise com terceiro que confirma; produto de dados) com critério de entrada; diário e D-nn obrigatórios em todos; questionário opcional. O canário confere, por nível, quais peças são obrigatórias, e os ponteiros da skill.
6. Regressão: `test_analise_dados`, `test_skill_contract`, `validate_skills`, `test_capabilities`, `test_web_export`, `test_marketing_claims`, `test_core_no_vendor`, `test_core_agnostic`, `test_planilhas_projeto`, `test_adr_changelog_sync`; bateria `run_canaries.py` sem falha nova.
7. QA isolado do conjunto (Codex r1, Sonnet r2), uma das leituras como quem executa o runbook sozinho, com versão revisada, achados e tratamento registrados.

## 5. Fora

B4 e B5; mudança em `qa-critic`, `_shared/output-format`, `planilhas_projeto.py` ou ADR-134; gerador de EF/ET; leitura das respostas da planilha de volta para o projeto.

## 6. Revisão r1 da especificação (Codex `gpt-6.1-sol`, id `20261124-100118-24e9eb`, REPROVADO, 8 achados) — tratamento

| Achado | Tratamento |
|---|---|
| 1 ALTA sequência de segurança | R14 e decisão 8 |
| 2 ALTA requisitos textuais | R6 completada; seção 3a separa script de revisão humana |
| 3 ALTA fases sem conteúdo | seção 3b |
| 4 ALTA desvio de escopo | mantido e declarado: leitura da sessão que acompanha o plano (24/11/2026, "aceitável se declarado"), não aprovação do dono; levado ao dono no fechamento. Alternativa sugerida (só CHANGELOG) recusada: quem usa a skill não lê o CHANGELOG |
| 5 MEDIA lista vazia | R14: só quando um passo em massa a consome |
| 6 MEDIA convenções arbitrárias | decisão 11 (alcance); R4 aceita `1)` e `1.`; `Deu certo:` e abas fixas mantidos como contrato do gerador |
| 7 ALTA revisão isolada | aceite 7 |
| 8 MEDIA aceite do pacote | aceite 5 reescrito |

## 7. Revisão do conjunto r1 (Codex `gpt-6.1-sol`, id `20261124-103016-a96560`, REPROVADO, 9 achados) — tratamento

| Achado | Tratamento |
|---|---|
| 1 ALTA `Feito ` com espaço passa | Status e Parte lidos sem tirar espaço |
| 2 ALTA fórmula com espaço dentro do texto passa | comparação exata |
| 3 MEDIA ordenar linhas | R3 nomeia a causa e "Como marcar: Filtro" manda não ordenar: o Painel lê a ordem do Roteiro |
| 4 MEDIA resposta que começa por `=` | Roteiro já nasce como texto nas colunas a marcar (provado no Excel); Links também; a regra "fórmula fora do Painel" saiu (excedia R11) |
| 5 MEDIA caractere de controle dá traceback | validado na leitura do JSON, com tamanho e nome de aba |
| 6 MEDIA regra de cor vazia passa | R8 confere a cor do molde |
| 7 MEDIA `2.` depois de "Deu certo" | as duas numerações |
| 8 MEDIA os 8 campos não listados | Runbook Dados, passo 2 |
| 9 MEDIA análise do existente obrigatória em N3 | N3 = `se` |

## 8. Revisão do conjunto r2 (Sonnet, APROVADO COM RESSALVAS, 9 achados e 1 nota) — tratamento

| Achado | Tratamento |
|---|---|
| 1 MEDIA caractere inválido em XML, 2 MEDIA roteiro vazio, 8 BAIXA aninhamento profundo | exit 2, sem traceback; casos no canário |
| 3 MEDIA passo 4 sem `--sep` | aviso repetido no passo 4 |
| 4 MEDIA termos | perfilar, oficial, cobertura e monitoramento em "Palavras usadas" |
| 5 BAIXA R14 × Status | em massa Feito exige os três Feitos; Substituído nunca conta, de propósito |
| 6 BAIXA 5.2 sem marca | `[PREENCHER]` de grupos e de escolhas |
| 7 BAIXA Resposta do dono | linha em "Como marcar" |
| 9 BAIXA pacote × seção 7 | a tabela do pacote detalha e prevalece; comandos dizem a pasta do framework e caminho completo |
| 10 nota, mutações vivas | 5 sabotagens novas no canário |
| 10 nota, texto em Decisões e Pendências | não tratada: as linhas nascem vazias e a conferência não reprova fórmula nelas |

## 9. Revisão do delta r3 (Codex `gpt-6.1-sol`, id `20261124-110330-cd38c3`, REPROVADO, 1 achado) — tratamento

| Achado | Tratamento |
|---|---|
| 1 MEDIA caractere inválido no nome da aba de runbook | nomes de aba entram na mesma validação; 3 casos no canário |

## 10. Revisão do delta r4 (Sonnet, APROVADO COM RESSALVAS, 2 achados) — tratamento

| Achado | Tratamento |
|---|---|
| 1 MEDIA canário cego ao texto do modelo (termos, `--sep`, marcas do 5.2) | três conferências novas no canário |
| 2 BAIXA achado 9 da r2 sem teste | conferências e sabotagens da skill e do pacote |
| notas: "aceite" e "dedup" sem definição | definidos em "Palavras usadas" |

## 11. Retomada de 25/11/2026 (orquestrador, rota T-20261125-0906, risco alto): pré-revisão, r5 e edge-case-hunter

Pré-revisão consultiva Codex `20261125-090744-6969a8`; r5 Codex `gpt-6.1-sol` em só leitura, REPROVADO (4 MÉDIA, 3 notas);
edge-case-hunter Sonnet isolado, APROVADO COM RESSALVAS (2 MÉDIA, 8 BAIXA).

| Achado | Tratamento |
|---|---|
| r5-1 MÉDIA três conferências da r4 contornáveis | definição com 3 palavras ou mais, instrução do `--sep` no fim do comando, marca completa do 5.2; sabotadas |
| r5-2 MÉDIA lista de Status com espaço nas opções passa | texto exato da lista |
| r5-3 MÉDIA fase do Painel com espaço a mais passa | texto exato da célula |
| r5-4 MÉDIA "abre sem reparo" sem evidência | 25/11/2026, Excel 16.0 build 20625, `DisplayAlerts` ligado: modelo abre sem janela de aviso, título "modelo.xlsx", Painel calculado; controle com a validação corrompida de propósito não abre |
| r5 nota, usuário do PC no handoff | não tratada: o mesmo caminho já está em 39 arquivos da `main`; handoff pedido pelo dono |
| pré-revisão MÉDIA nome de lista repetido esconde lista (R11) | R11 reprova nome repetido |
| pré-revisão MÉDIA Nº com milhares de dígitos dá traceback | até 4 dígitos por parte |
| pré-revisão ALTA fórmula fora do Painel | descartada: exige inserção deliberada; regra retirada na r1 por exceder R11, e as colunas a marcar nascem como texto |
| ECH-1 MÉDIA passo em massa com Erro sem a sequência passa | R14 vale para Feito e Erro |
| ECH-2 MÉDIA linha apagada some do Painel | R3 acusa a lacuna. Limite declarado: última linha da fase ou fase inteira apagada não aparece na planilha |
| ECH-3 BAIXA gradiente dá traceback | R8 reprova a cor |
| ECH-6 BAIXA lista que não barra | R7 exige barrar |
| ECH-8 BAIXA arquivo pela metade em disco cheio | `gerar` remove o arquivo que criou |
| ECH-9 BAIXA tamanho em UTF-16 | nome de aba e texto medidos como o Excel conta |
| ECH-10 BAIXA outras quebras de linha na lista | R11 reprova |
| ECH-4, 5, 7 BAIXA (texto do argparse, cor ou célula extra alterada à mão, `--out NUL` ou sem `.xlsx`) | não tratadas: fora do uso previsto; limite declarado |
| ECH notas (marca `EM MASSA` literal, prefixos da R14, `[PREENCHER` literal) | revisão humana (seção 3a) |

## 12. Revisão do delta r6 (Sonnet isolado, 25/11/2026, APROVADO COM RESSALVAS, 2 BAIXA) — tratamento

| Achado | Tratamento |
|---|---|
| 1 BAIXA rótulo "Palavra: " passa do limite do texto | o rótulo inteiro é medido; caso no canário |
| 2 BAIXA "01.1" ao lado de "1.1" | R3 recusa zero à esquerda; sabotagem no canário |
| notas (Ctrl+C na gravação, prova do r5-4 só em texto) | limite declarado |
