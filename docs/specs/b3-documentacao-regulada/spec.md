<!-- spec-unico:v1 -->
# B3 — Documentação de projeto enxuta para ambiente regulado — Especificação

> Arquivo único de especificação (ADR-117). Estado: **PLANO EM APROVAÇÃO** · 25/09/2026 · autor: sessão Opus 5.5.
> Nasce da cobrança do dono: *"pedi mínima, mas pedi crítica. O ambiente é regulado. [...] Tem que ser
> agile, mas tem que ser para ambiente regulado."* A proposta anterior do B3 ("kit de 4 documentos")
> foi feita **sem** pesquisa regulatória, sem crítica e sem revisão — está substituída por esta.

## Painel

<!-- painel:inicio -->
| Fase | Feitas | Andamento | % |
|---|---|---|---|
| B3a — Kit neutro e ferramentas | 6/6 | `████████████` | 100% |
| B3b — Perfil farma/ANVISA (fora do núcleo) | 1/1 | `████████████` | 100% |
| B3d — Método único de projeto (depende de D7/D8) | 4/4 | `████████████` | 100% |
| B3e — Conhecimento contextual reutilizável (D9) | 4/4 | `████████████` | 100% |
| B3f — Acompanhamento de projeto (REQ-07) | 1/1 | `████████████` | 100% |
| B3c — Skill `project-docs` | 1/1 | `████████████` | 100% |
<!-- painel:fim -->

**Avanço:** discovery ✅ · requisitos aprovados pelo dono (26/09) · execução: B3a-1 ✅ (PR #161) · B3e ✅ (PR #163) · B3d ✅ (PR #168) · B3a-2 ✅ (PR #170) · B3a-3 ✅ (PR #174) · B3c ✅ (PR #175) · B2b ✅ (PR #176) · B3b ✅ (PR #177) · B3f em revisão (ADR-127) · depois: perfil ANP (`trabalhos.py`, `perfil-anp`)

| # | Assunto | Situação | Quem age | Resultado / próximo |
|---|---|---|---|---|
| D1 | Perfil regulado padrão | ✅ **decidido pelo dono (26/09): sem perfil padrão.** Perfil é por projeto, perguntado no discovery (ANVISA, ANP, outros ou nenhum) | — | recomendação (a) descartada; REQ-08 e T6 passam a tratar o perfil ANVISA como o primeiro de vários |
| D9 | Dicionário semântico + ontologia por perfil regulado e por empresa, e índice de projetos | ✅ decidido (26/09): incluir B3e | — | REQ-16 a REQ-18 |
| D2 | Categoria GAMP padrão do SAP configurado | ✅ decidido (26/09): conforme recomendação | — | ver Decisões |
| D3 | Fonte da verdade: repositório × planilha das áreas | ✅ decidido (26/09): conforme recomendação | — | ver Decisões |
| D4 | Aprovação formal | ✅ decidido (26/09): conforme recomendação | — | ver Decisões |
| D5 | Ordem dos blocos | ✅ decidido (26/09): conforme recomendação | — | ver Decisões |
| D6 | Mapeamento planilha ↔ especificação | ✅ decidido (26/09): conforme recomendação | — | ver Decisões |
| D7 | Incluir B3d: método único de projeto + desenho de processo gerado | ✅ decidido (26/09): conforme recomendação | — | ver Decisões |
| D8 | Desenho do processo em HTML (revisão) **e** docx (documento controlado) | ✅ decidido (26/09): conforme recomendação | — | ver Decisões |

## Resumo executivo

**Onde estamos.** A pesquisa confirmou o pacote vigente: RDC nº 658/2022 (BPF de medicamentos), IN nº
134/2022 (sistemas computadorizados), IN nº 138/2022 (qualificação e validação) e o Guia ANVISA nº
33/2020 (validação de sistemas computadorizados, **não vinculante**). A lista de documentos que uma
inspeção espera tem cerca de 20 itens, mas **o próprio guia manda escalonar pelo risco** e permite
pular etapas quando o risco já é aceitável. Os dois arquivos do MRP do dono já são, na prática, dois
desses documentos (confirmação de requisitos e roteiro de verificação).

**O que falta.** Transformar isso num kit que o time use sem esforço extra: poucos arquivos, cada
documento de auditoria saindo **gerado** do mesmo lugar, e um verificador que barre o que a auditoria
barraria (requisito sem teste, risco alto sem mitigação, teste sem evidência, aprovação sem nome e data).

**Próximos passos.** Revisão adversarial deste plano; o dono decide D1–D5; execução em três blocos.

## Quem precisa, o quê, para quê

| Quem | Precisa de | Para |
|---|---|---|
| Dono (coordenação de sistemas) | documentação enxuta, ágil e **conforme** | passar em auditoria sem transformar o projeto em papelada |
| Áreas (PCP, P&D, Qualidade...) | confirmar regras e executar verificações numa planilha simples | responder sem precisar entender o repositório |
| Qualidade (GQ) | ERU, análise de risco, rastreabilidade, relatório, aprovação | liberar o sistema e responder ao inspetor |
| Inspetor (ANVISA) | evidência de que o sistema faz o que deve, com risco controlado e dados íntegros | inspeção |
| Quem retoma o projeto | tudo num lugar, com versão | continuar sem perguntar |

## Crítica do pedido

1. **"Mínimo" em ambiente regulado não é um número fixo de documentos.** O Guia 33/2020 escala por
   risco, complexidade e categoria do software (§4.1.3). O mínimo é **o suficiente para o risco**:
   um software de prateleira (categoria 3) tem ciclo abreviado; um SAP configurado (categoria 4)
   precisa de especificação de configuração e rastreabilidade completa. Propor "4 documentos" para
   tudo foi erro meu.
2. **O guia não obriga formato, obriga substância.** Ele é não vinculante (p. 2); a obrigação vem da
   RDC 658 e da IN 134. Isso **permite** ser ágil: o que o inspetor precisa ver é a cadeia requisito →
   risco → teste → evidência → aprovação, não 20 arquivos Word.
3. **O guia está desatualizado:** a base legal dele ainda cita normas revogadas em 2022 (RDC 301/2019,
   IN 43/2019, IN 47/2019). Documento nosso não pode repetir essas citações.
4. **Planilha como assinatura não é assinatura controlada.** "Nome e data" numa planilha mostra quem
   confirmou, mas a **aprovação formal** (ERU, relatório de validação) é da Qualidade, no sistema de
   documentos controlados da empresa. O framework não substitui esse sistema; ele gera o conteúdo.
5. **Duas fontes divergem.** Se a planilha da área e o repositório forem editados em paralelo, um
   envelhece. Precisa de ida e volta: o repositório gera a planilha, a área preenche, a resposta volta.
6. **O núcleo do framework não pode citar ANVISA** (neutralidade, ADR-010). O kit é genérico; o
   perfil farma/ANVISA é um pacote de aplicação que liga cada peça à norma.
7. **Nem todo projeto é GxP.** A primeira pergunta do discovery tem de ser "o sistema tem impacto em
   BPF (produto, paciente, dado de qualidade)?" — se não, o kit regulado não se aplica.

# Parte A — Requisitos

## Identificação
- **Caso/feature:** B3 — documentação de projeto enxuta para ambiente regulado
- **Indicador/objeto:** kit de documentos de projeto e as ferramentas que o geram e verificam
- **Recorte:** todo projeto de sistema com impacto em BPF; projetos sem impacto usam o kit comum
- **Confiança da tarefa:** MÉDIA — a norma é pública e foi lida; a aplicação ao dia a dia do time não foi testada

## Escopo declarado pelo discovery

### (a) Regulado?
- `[CONFIRMADO]` Sim, quando o sistema tem impacto em BPF de medicamentos: RDC nº 658/2022, IN nº 134/2022, IN nº 138/2022; Guia ANVISA nº 33/2020 como referência não vinculante. Fontes na Parte C.
- **Origem:** declaração do dono (25/09/2026) + pesquisa.

### (b) Alto-risco?
- Sim: documentação que vai a inspeção e sustenta a liberação de sistema GxP.

### (c) Regras com semântica?
- Sim: a obrigatoriedade de cada documento depende da categoria do software e do risco; o texto do documento não pode citar norma revogada.

### (d) Gaps não-bloqueantes?
- ~~Texto primário integral da IN 134/2022 e IN 138/2022 não foi lido~~ · **resolvido no B3b (28/09/2026):** texto integral lido; peça → artigo em `exemplos/dominio-regulado/farma-anvisa-mapa-normas.md`.
- ALCOA+ como sigla está ausente do texto oficial (confirmado por busca literal em 28/09/2026) · impacto: não citar a sigla como exigência literal da norma · decisão: usar a substância (dado atribuível, legível, contemporâneo, original, exato) sem atribuir a sigla à norma.

## Dimensões de elicitação
- operador: equipe de sistemas (autor) e áreas de negócio e Qualidade (confirmam e executam verificação) — as áreas usam planilha, não o repositório
- interface: arquivo único no repositório para o time; planilha gerada para as áreas; documento de auditoria gerado (md, docx, pdf, pptx)
- entrada-validacao: requisitos e testes entram com identificador (REQ, RISCO, TESTE); o verificador reprova identificador órfão ou referência inexistente
- escopo-temporal: ciclo de vida do sistema — abertura, especificação, testes, liberação, operação, mudança, aposentadoria
- recortes-saida: por projeto, por sistema, por categoria de software, por criticidade do requisito
- persistencia: git no repositório do projeto; planilhas preenchidas guardadas como evidência com versão
- auditoria-log: histórico do git + seção "o que mudou" + nome e data em cada confirmação e execução
- ambiente-execucao: Python sem dependência obrigatória (openpyxl opcional para gerar planilha), máquina corporativa Windows
- formato-saida: planilhas no padrão dos arquivos do MRP; relatório e matriz em md/docx/pdf; pptx executivo
- biblioteca-consultada: nada encontrado — a biblioteca de conhecimento nasce neste plano (B3e, ADR-120)
- escopo-e-prazo: sem marco declarado para o framework; acima: kit completo do guia de validação (cerca de 20 documentos por sistema), descartado por excesso — o próprio guia manda escalonar pelo risco; abaixo: kit comum sem verificador, descartado por não passar em inspeção (fontes.md)
- contexto-entidade: indústria farmacêutica regulada pela ANVISA; sistemas SAP S/4HANA configurados, sistemas de pesagem e automações
- verificacao-ancora: tabela de âncoras na Parte C, com vigência, pertinência, confiança e fonte datada

## Cobertura exigida pelo pedido
- dicionário semântico e de dados e ontologia por perfil regulado e por empresa; índice de projetos e pesquisas
- evidências de desenvolvimento: consultas, extrações em planilha, runbooks e passo a passo de cada etapa
- todos os projetos de sistema com impacto em BPF (o kit regulado vale para todos eles; os demais usam o kit comum)
- cronograma do projeto
- testes E2E
- checklist de verificação por área (modelo `Checklist_Validacao_Cadastros_MRP_v1_1_TREPLICA-v3.xlsx`)
- confirmação de definições com a área (modelo `DEFINICOES-PCP-para-confirmacao_v2.xlsx`)
- ERU quando for sistema novo
- análise de risco
- matriz de rastreabilidade
- evidências dos testes

## Requisitos
- REQ-01: O kit tem um conjunto essencial fixo e peças **condicionais por risco e categoria**; a regra de escalonamento está escrita e é verificável.
- REQ-02: Toda peça que a auditoria pede é **gerada** do arquivo único do projeto (ou de um arquivo de dados dele), nunca escrita duas vezes.
- REQ-03: Requisito, risco e teste têm identificador; a matriz requisito → risco → teste → evidência é gerada automaticamente.
- REQ-04: Um verificador reprova: requisito sem teste; risco alto sem mitigação ou sem teste; teste sem resultado ou sem evidência; confirmação ou execução sem nome e data; citação de norma revogada.
- REQ-05: A confirmação de definições com a área sai como planilha com as **13 colunas reais** do modelo (aba REGRAS): Nº · Tema · Regra, como entendemos · Exemplo · Como fica no sistema · Exige alterar o cadastro de muitos materiais? · Situação hoje · É possível? Como? Em massa? · Links (fonte e tutorial) · De onde tiramos · Área confirma? · Correção da área · Nome e data; mais as abas LEIA e VALORES POR TIPO — no núcleo, "VALORES POR CATEGORIA", opcional (abas do arquivo atual, conferidas em 25/09 às 23:50; a versão `_v2` anterior tinha também "O QUE MUDOU", hoje coberta pelo REQ-12). A resposta volta ao repositório.
- REQ-06: O roteiro de verificação e de E2E sai como planilha com as **15 colunas de base reais** do modelo: No · Onde olhar · Campo como aparece na tela · Nome técnico · O que o campo faz · Aplica-se a · Regra / valor esperado · Como conferir vários de uma vez · Se estiver errado, o que acontece · Criticidade · Natureza da decisão · Confiança · Valor encontrado · Conclusão da área · Data / Visto; mais as colunas de **rodada** — no modelo real são 12 colunas de três rodadas diferentes empilhadas (TIPO · TRÉPLICA / MEDIÇÃO · PERGUNTA DE VOLTA · RESPOSTA · Visto · PARECER · VALOR A CADASTRAR · ONDE (tela correta) · QUEM FAZ · O QUE FAZER AGORA · SITUAÇÃO · RESPOSTA DA ÁREA); no núcleo, uma **rodada padrão** de formato fixo (Pergunta de volta · Resposta da área · O que fazer (valor, onde, quem) · Situação · Nome e data), uma no modelo e repetível com a data no título (decisão do dono, 27/09), e as abas COMO USAR, ANTES DE COMEÇAR, ACHADOS DO AMBIENTE, CORREÇÕES DA BASE, CONTROLE DE VERSÃO. Em sistema com impacto em BPF, as categorias de teste **integridade de dados, trilha de auditoria, controle de acesso e backup/restauração** são obrigatórias no roteiro.
- REQ-07: O cronograma sai do estado do projeto (pacote de controle de projeto), não de planilha mantida à mão.
- REQ-08: O núcleo do framework fica neutro; a ligação de cada peça com artigo de norma vive num perfil de aplicação. **Sem perfil padrão:** o discovery pergunta a empresa e o perfil regulado de cada projeto (ANVISA, ANP, outro ou nenhum) e registra a resposta; o perfil ANVISA é o primeiro, não o único.
- REQ-09: O relatório de validação é gerado com requisitos, riscos, testes executados, desvios e campo de aprovação; a aprovação formal acontece no sistema de documentos controlados da Qualidade.
- REQ-10: Para sistema em uso, um checklist de prontidão cobre descrição do sistema, POPs, treinamento, acesso, backup e restauração, continuidade, revisão periódica.
- REQ-13: Método único de projeto: um documento de entrada (`guia/METODO-DE-PROJETO.md`) com o fluxo numerado — elicitação → confirmação da área → especificação → desenho do processo → testes e evidências → liberação → operação — e onde mora cada peça; citado no `CLAUDE.md` e no início de sessão; todo projeto aberto registrado em `tools/trabalhos.py`.
- REQ-14: Desenho do processo gerado da especificação (parte Processo: passos, papéis, regras, gatilhos, a partir do mapeamento de processo existente), em HTML para revisão das áreas no padrão de `C:\Users\fabriciosouza\capa-sharepoint\saida\DESENHO-DO-PROCESSO-v5.html` e em docx para o sistema de documentos controlados (via `tools/gen_exec_doc.py`, que já gera docx).
- REQ-15: Evidência de desenvolvimento: consultas (SQL e outras), extrações em planilha, runbooks e passo a passo de cada etapa são arquivados como evidência e conhecimento explícito. O repositório guarda um **manifesto** (caminho absoluto, sha256, data, consulta que gerou, requisito ou teste que embasa), gerado por `tools/doc_intake.py`; arquivo com dado real ou sensível fica em pasta controlada, fora do git; conteúdo mudou = nome novo, versão anterior em `_obsoleto/` com o motivo no nome. Referências de método (não de domínio): projetos OPEX e MRP (ver Fontes de dados).
- REQ-16: Dicionário semântico e de dados em três níveis — perfil regulado, empresa, projeto — com cada termo definido uma vez no seu nível: termo, definição, dado ou campo (quando houver), relações (é um · parte de · regulado por · medido por · sinônimo de), marca de confiança (CONFIRMADO com quem e data · INFERIDO · REFUTADO), fonte e data. Termo nasce no ato da confirmação ou da pesquisa. Conhecimento de empresa em `docs\_private\conhecimento\`, fora das distribuições públicas.
- REQ-17: Índice de projetos `docs\_private\conhecimento\INDICE-PROJETOS.md`: uma linha por projeto — empresa, perfil regulado, caminho absoluto, repositório, estado, onde estão a especificação e o dicionário.
- REQ-18: Consulta sob demanda: o `knowledge_catalog` indexa `docs\_private\conhecimento\`; nada disso é carregado a cada sessão.
- REQ-11: A ERU (requisitos do usuário) é **gerada** da Parte A — requisitos com identificador, criticidade em BPF e origem — no formato do documento controlado da Qualidade; o código do documento vem da Qualidade, nunca é inventado. Obrigatória para sistema novo e para mudança que altere requisito.
- REQ-12: Gestão de mudança e de versão segue o padrão das planilhas do MRP: registro "o que mudou" (item, tipo, o que mudou, por quê), "correções da base" (o que constava, correção, motivo) e "controle de versão" (versão, data, autor, conteúdo, base utilizada), gerados do histórico do repositório.

## Mapeamento de campo-fonte
- Regra, como entendemos -> coluna "Regra, como entendemos" (REGRAS) | confirmação: [CONFIRMADO] pelo dono em 26/09/2026 (D6) | porque: coluna do modelo do dono, sem transformação
- Área confirma / Correção / Nome e data -> colunas "PCP confirma?", "Correção do PCP", "Nome e data" (REGRAS) | confirmação: [CONFIRMADO] pelo dono em 26/09/2026 (D6) | porque: generalização de "PCP" para a área que confirma
- Valor esperado -> coluna "Regra / valor esperado" (CHECKLIST CADASTRO) | confirmação: [CONFIRMADO] pelo dono em 26/09/2026 (D6) | porque: coluna do modelo do dono
- Evidência de execução -> colunas "Valor encontrado", "Conclusão da área", "Data / Visto" (CHECKLIST CADASTRO) | confirmação: [CONFIRMADO] pelo dono em 26/09/2026 (D6) | porque: o modelo não tem coluna "evidência" separada; a evidência é o valor encontrado + visto

## Fora de escopo
- Substituir o sistema de documentos controlados da Qualidade ou assinatura eletrônica.
- Validar sistemas existentes da empresa (o kit é a ferramenta; cada validação é um projeto).
- Perfis regulatórios além do farma/ANVISA neste momento.
- Avaliação de fornecedor, qualificação de infraestrutura, migração de dados e aposentadoria de sistema: processos da empresa, fora deste kit nesta rodada; o checklist de prontidão (REQ-10) só registra se existem e onde estão.

## Fontes de dados
- Referência de evidência de desenvolvimento — projeto OPEX, `C:\Users\fabriciosouza\budget-opex\` (lido em 26/09, só leitura): consultas versionadas no nome (`CONSULTAS-SAP-FINAL-v15.sql`); `_obsoleto\` com o motivo no nome (`...-substituido-pelo-v15.sql`, `...-CONTEM-O-BUG-DO-AWKEY.sql`, `...-v1-travava.sql`); `RUNBOOK-OPEX-CAIXA.md`, `ESTADO-ATUAL.md`, `RETOMADA-PROXIMA-SESSAO.md`, `DICIONARIO-SEMANTICO.md`, `OPEX-TI-2026-PREMISSAS.md`, `RELATORIO-OPEX-TI-2026.md`, `APRESENTACAO-EXECUTIVA-OPEX.pptx`; planilhas geradas (`OPEX TI 2026 - Validacao.xlsx`, `OPEX TI 2026 - Orcado x Caixa.xlsx`); verificadores `confere_entrega.py`, `confere_limite.py`, `check_referencias.py`; pasta `_qa\`.
- Pesquisa de 25/09/2026: `C:\Users\fabriciosouza\metacognition-framework\docs\specs\b3-documentacao-regulada\fontes.md` (resumo na Parte C).
- ADR-043 e perfis clonáveis em `C:\Users\fabriciosouza\metacognition-framework\exemplos\dominio-regulado\` (base do perfil farma/ANVISA) e `C:\Users\fabriciosouza\metacognition-framework\tools\check_regulatory_coverage.py`.
- `C:\Users\fabriciosouza\sap-mrp-natulab\checklist-cadastro\Checklist_Validacao_Cadastros_MRP_v1_1_TREPLICA-v3.xlsx` e `C:\Users\fabriciosouza\sap-mrp-natulab\pcp\DEFINICOES-PCP-para-confirmacao_v1.xlsx` (só leitura; conferidos de novo em 27/09/2026 com openpyxl: REGRAS 13 colunas, CHECKLIST 15 de base + 12 de rodada). Lidos pela primeira vez em 25/09 em `Downloads\2026-09-11-MRP\`, pasta que deixou de existir com a migração do projeto MRP para o repositório `sap-mrp-natulab` em 26/09.

# Parte B — Aceite
- **Requisitos aprovados pelo dono em:** 26/09/2026 (D1–D9) · **Aceite escrito em:** 26/09/2026, depois da aprovação · **Aceite ratificado pelo revisor isolado em:** 26/09/2026 (a6e29bb1bb764020e, RATIFICADO-COM-AJUSTES; 8 ajustes aplicados)
> Parte B escrita **depois** que o dono aprovar a Parte A (ADR-117). Rascunho de critérios, para a revisão:

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 1 | REQ-01: escalonamento por categoria | projeto de teste categoria 3 gera o conjunto SEM especificação funcional/de configuração; categoria 4 gera COM ela (Parte C, linha "Especificação funcional / de configuração"); comparar pelo nome da peça, não pela contagem | ☐ |
| 2 | REQ-04: Verificador reprova os 5 casos do REQ-04 | 5 entradas que devem reprovar, reprovam; 1 correta passa; sabotagem pega | ☐ |
| 3a | REQ-05: planilha de confirmação | as 13 colunas e as abas batem com o modelo real **em estrutura** (mesma ordem e papel; o texto do cabeçalho é o rótulo do projeto e, com os rótulos do modelo, sai idêntico a ele); ida e volta preserva a resposta da área; regravar cria vN+1 e só apaga a anterior depois de comparar | ✅ `tools/test_planilhas_projeto.py` (b), (c), (d) |
| 3b | REQ-06: roteiro de verificação | as 15 colunas de base batem com o modelo real em estrutura; cada rodada acrescenta as 5 colunas da rodada padrão sem perder as anteriores; as categorias obrigatórias do perfil (no farma: integridade de dados, trilha de auditoria, controle de acesso, backup/restauração) aparecem como blocos obrigatórios em todo projeto com impacto regulado; ausência de qualquer uma reprova `verificar` e o `gerar` a acrescenta | ✅ `tools/test_planilhas_projeto.py` (b), (e), (g) |
| 4 | REQ-04: Nenhuma citação a norma revogada nos modelos | verificador varre RDC 301/2019, IN 43/2019, IN 47/2019 (refina o caso "norma revogada" do critério 2) | ☐ |
| 5 | REQ-08: núcleo neutro | `python tools/check_core_agnostic.py` PASS, com RDC, IN, ANVISA, ANP e GAMP na `tools/agnostic-denylist.txt`; esses termos só aparecem em `exemplos/dominio-regulado/` e em `docs/_private/` | ☐ |
| 6 | Recorte (Parte A) + REQ-08: impacto em BPF | o discovery pergunta e registra o impacto em BPF de todos os projetos; os que têm impacto recebem o kit regulado, os demais o comum; sem a resposta registrada, o verificador não libera o kit | ☐ |
| 7 | REQ-02: nenhuma peça de auditoria é escrita à mão | cada peça sai de um gerador; editar a peça gerada e gerar de novo desfaz a edição (canário) | ☐ |
| 8 | REQ-03: matriz gerada | projeto de teste com 3 REQ, 2 RISCO, 4 TESTE gera a matriz completa; REQ sem teste aparece como lacuna | ☐ |
| 9 | REQ-07: cronograma sai do estado do projeto | cronograma gerado das Tarefas do `spec.md` (`prazo:` e `depende:` na linha; ver Replanejamento de 28/09); alterar uma data na tarefa muda o cronograma | ✅ `test_plano` (g) |
| 10 | REQ-09: relatório de validação gerado | contém requisitos, riscos, testes, desvios e campos de aprovação (dono do processo + Qualidade) | ✅ `test_documento_regulado` (ADR-124) |
| 11 | REQ-10: checklist de prontidão | itens: descrição do sistema, POPs, treinamento, acesso, backup/restauração, continuidade, revisão periódica, cada um com situação e onde está | ✅ `test_documento_regulado` (ADR-124) |
| 12 | REQ-11: ERU gerada da Parte A | todo REQ da Parte A aparece na ERU com identificador, criticidade e origem; campo do código do documento fica vazio até a Qualidade preencher | ✅ `test_documento_regulado` (ADR-124) |
| 13 | REQ-12: mudança e versão | registros "o que mudou", "correções da base" e "controle de versão" gerados do histórico; nenhuma versão sem data e autor | ✅ `test_documento_regulado` (ADR-124) |
| 14 | REQ-13: método único encontrável | `CLAUDE.md` e o início de sessão apontam para `guia/METODO-DE-PROJETO.md`; projeto aberto aparece em `trabalhos.py listar` | ☐ |
| 15 | REQ-14: desenho do processo gerado | alterar um passo na especificação e gerar de novo muda o HTML e o docx; nenhum dos dois é editado à mão | ☐ |
| 16 | REQ-15: evidência de desenvolvimento rastreável | todo arquivo citado no manifesto existe no caminho com o sha256 registrado; arquivo alterado sem nome novo é apontado; nenhum arquivo marcado como sensível no manifesto está rastreado pelo git (`git ls-files` não o lista) | ☐ |
| 17 | REQ-16: dicionário verificável | verificador reprova: termo sem fonte ou data; relação apontando para termo inexistente; termo definido em dois níveis; CONFIRMADO sem quem confirmou | ☐ |
| 18 | REQ-17: índice de projetos | todo caminho do índice existe; projeto em `trabalhos.py` sem linha no índice é apontado | ☐ |
| 19 | REQ-18: consulta sob demanda | `knowledge_catalog --recall` com um termo do dicionário devolve o arquivo certo; o boot não carrega o dicionário | ☐ |
| 20 | REQ-08 (D1): perfil regulado por projeto, sem padrão | 3 projetos de teste (ANVISA, ANP, nenhum): o discovery grava o perfil escolhido e o kit gerado difere conforme o perfil; projeto sem perfil registrado é bloqueado pelo verificador | ☐ |
| 21 | REQ-01 (D2): categoria GAMP do SAP | projeto SAP com categoria diferente de 4 tem registro de quem decidiu e por quê; ausência reprova | ☐ |

# Parte C — Contexto e âncoras

## Verificação de âncora (vigência e pertinência)

| Âncora | Vigência | Pertinência | Confiança | Fonte |
|---|---|---|---|---|
| RDC nº 658, de 30/03/2022 — BPF de medicamentos | vigente desde 02/05/2022; revogou a RDC 301/2019 | norma vinculante de fundo | CONFIRMADO (texto integral lido em 28/09/2026; revogação da RDC 301/2019 no art. 379; alterada só pela RDC 972/2025, no art. 372, fora de sistemas computadorizados) | AnvisaLegis e DOU — URLs em `fontes.md`, seção 6 (acesso em 28/09/2026) |
| IN nº 134, de 30/03/2022 — sistemas computadorizados | vigente desde 02/05/2022, sem alterações; revogou a IN 43/2019 (art. 47) | vinculante para sistemas GxP | CONFIRMADO (texto integral lido em 28/09/2026, conferido no DOU) | AnvisaLegis e DOU — URLs em `fontes.md`, seção 6 (acesso em 28/09/2026) |
| IN nº 138, de 30/03/2022 — qualificação e validação | vigente desde 02/05/2022, sem alterações; revogou a IN 47/2019 (art. 132) | vinculante; a definição de protocolo inclui sistema computadorizado (art. 3º, XVI) | CONFIRMADO (texto integral lido em 28/09/2026, conferido no DOU) | AnvisaLegis e DOU — URLs em `fontes.md`, seção 6 (acesso em 28/09/2026) |
| Guia ANVISA nº 33/2020, versão 1 — validação de sistemas computadorizados | vigente desde 14/04/2020; **não vinculante**; base legal cita normas revogadas | lista os entregáveis e permite escalonar por risco | CONFIRMADO (íntegra do PDF lida em 28/09/2026) | https://anexosportal.datalegis.net/arquivos/1860250.pdf (acesso em 28/09/2026) |
| GAMP 5, 2ª edição (ISPE, jul/2022) | referência de mercado, não norma | aceita métodos ágeis e "pensamento crítico" | INFERIDO (fontes secundárias; texto pago não lido) | https://www.scilife.io/blog/gamp5-for-gxp-compliant-computerized-systems (acesso em 25/09/2026) |

## Entregáveis que uma inspeção espera (Guia 33/2020, escalonado por risco)

| Entregável | Base | Obrigatoriedade | Quando |
|---|---|---|---|
| Inventário de sistemas | Guia §8, §10 | boa prática forte | sempre |
| Política / plano mestre de validação | Guia §9.1 | expectativa de inspeção; corporativo — **fora deste kit** (documento da Qualidade; o kit só aponta onde está) | corporativo |
| Categorização GAMP (1, 3, 4, 5) | Guia §7 | ferramenta de escalonamento — **entra no kit**: define o conjunto de peças (REQ-01, D2) | sistema novo; mudança |
| Integridade de dados | IN 134/2022, arts. 26, 28, 32, 39 e 45; RDC 658/2022, arts. 116, 124 e 125 (vinculantes; lidos em 28/09/2026) | **obrigatório, não escalonável** — entra como categoria obrigatória de teste (REQ-06) e item do checklist de prontidão (REQ-10) | todo o ciclo |
| Plano de validação | Guia §9.2 | proporcional ao risco | sistema novo, mudança maior |
| ERU (requisitos do usuário) | Guia §9.3 | obrigatório na substância | categorias 3, 4, 5 |
| Avaliação de fornecedor | Guia §9.4 | proporcional ao risco | aquisição |
| Especificação funcional / de configuração | Guia §9.5–9.6 | categorias 4 e 5; dispensável na 3 | sistema novo |
| Gestão de risco (inicial e funcional) | Guia §6 (ICH Q9) | obrigatório na substância | ciclo de vida |
| Matriz de rastreabilidade | Guia §9.8.5 | obrigatória; categoria 3: requisito → teste | sistema novo |
| Plano, protocolos e relatório de testes | Guia §9.7 (terminologia livre) | obrigatório | sistema novo, mudança relevante |
| Descrição do sistema | Guia §9.8.1.1 | obrigatório | antes da liberação, mantida |
| Gestão de configuração e mudança | Guia §9.8.2, §11.7 | obrigatório | projeto e operação |
| Relatório de validação | Guia §9.9 (aprovação: dono do processo + Qualidade) | obrigatório | encerramento |
| POPs, treinamento | Guia §9.2.2, §9.9.2 | obrigatório | operação |
| Revisão periódica, backup e restauração, continuidade, segurança e acesso, registros | Guia §11.9–11.14; IN 134/2022 | obrigatório | operação |
| Migração de dados; aposentadoria | Guia §12, §13 | obrigatório quando ocorre | troca e fim de vida |

## O que permite ser ágil (citações)
- Guia §4.1.3: as atividades do ciclo de vida *"devem ser escalonadas de acordo com: o impacto do sistema..., a complexidade..., o resultado da avaliação do fornecedor..."*.
- Guia §6.3.1: *"pode não ser necessário realizar as etapas subsequentes se o risco já estiver em um nível aceitável."*
- Guia §7.3.2 (categoria 3): *"Uma abordagem simplificada para o ciclo de vida pode ser aplicada [...] A verificação consiste basicamente em uma fase de testes única."*
- Guia p. 2: instrumento *"não normativo, de caráter recomendatório e não vinculante"*.

# Decisões
| # | Decisão | Alternativas | Recomendação | Resposta do dono |
|---|---|---|---|---|
| D1 | Perfil regulado padrão | (a) farma/ANVISA · (b) genérico sem perfil · (c) vários ao mesmo tempo | **(a)**: é o ambiente real hoje; os outros entram como perfis novos sem mexer no núcleo | ✅ **sem perfil padrão**: perfil é por projeto, perguntado no discovery (26/09) |
| D2 | Categoria GAMP padrão para SAP configurado | (a) 4 · (b) decidir caso a caso sem padrão | **(a)**, com revisão caso a caso registrada | ✅ conforme recomendação (26/09) |
| D3 | Fonte da verdade | (a) repositório gera planilha e importa resposta · (b) planilha é a fonte | **(a)**: uma fonte; a área continua trabalhando só na planilha | ✅ conforme recomendação (26/09) |
| D4 | Aprovação formal | (a) sistema de documentos controlados da Qualidade · (b) "nome e data" na planilha basta | **(a)**: planilha registra confirmação; aprovação é da Qualidade | ✅ conforme recomendação (26/09) |
| D5 | Ordem | (a) B3a kit neutro + ferramentas → B3b perfil ANVISA → B3c skill `project-docs` · (b) perfil primeiro | **(a)**: o perfil precisa do kit pronto para apontar | ✅ conforme recomendação (26/09) |
| D7 | B3d — método único de projeto | (a) incluir: `guia/METODO-DE-PROJETO.md` como entrada única (citado no `CLAUDE.md` e no início de sessão) + parte Processo na especificação, vinda do mapeamento de processo que já existe (`docs/specs/_template-process/`) + gerador do desenho no padrão de `C:\Users\fabriciosouza\capa-sharepoint\saida\DESENHO-DO-PROCESSO-v5.html` · (b) não incluir | **(a)**: o método espalhado em 6 lugares é o problema de "achar"; o desenho gerado da fonte não diverge | ✅ conforme recomendação (26/09) |
| D8 | Formato do desenho | (a) HTML para revisão + docx para o sistema de documentos controlados · (b) só HTML | **(a)**: HTML não é documento controlado | ✅ conforme recomendação (26/09) |
| D9 | Conhecimento contextual (B3e) | (a) dicionário + relações por perfil regulado e por empresa + índice de projetos, em `docs\_private\conhecimento\`, consultado sob demanda pelo `knowledge_catalog` · (b) não fazer | **(a)** | ✅ incluir (26/09) |
| D6 | Mapeamento planilha ↔ especificação (seção abaixo) | (a) confirmar como está · (b) ajustar colunas | **(a)**: colunas copiadas dos modelos reais do dono; só a renomeação "PCP"→"área" e "SAP"→"sistema" é minha | ✅ conforme recomendação (26/09) |

# Tarefas

### B3a — Kit neutro e ferramentas
- [x] T1 (B3a-1, ADR-119 — prova: `tools/test_regulado.py`; modelo `docs/specs/_template-spec-unico/spec.md`; campo de impacto renomeado, ver Replanejamento) Partes novas no modelo de arquivo único: **F — Riscos** (identificador, requisito, falha, impacto em produto/paciente/dado, probabilidade, detecção, classe, mitigação, teste) e **G — Testes e evidências** (identificador, requisito, roteiro, esperado, resultado, evidência, nome e data); regra de escalonamento por categoria.
- [x] T2 `tools/regulado.py verificar`: os 5 casos do REQ-04, com canário e sabotagem. — prova: `test_regulado` (32 sabotagens, 6 exceções) e 32/32 mutações mortas; `--planejamento` para uso durante o projeto.
- [x] T3 `tools/regulado.py matriz`: requisito → risco → teste → evidência, gerada. — prova: `test_regulado` (d), projeto de 3 REQ, 2 RISCO, 4 TESTE (critério 8).
- [x] T4 (B3a-2, ADR-122 — prova: `tools/test_planilhas_projeto.py`; Partes I e J do modelo de arquivo único) Geração das duas planilhas no padrão do MRP e importação da resposta da área, com versão vN, `_obsoleto/` e comparação antes de apagar.
- [x] T5 (B3a-3, ADR-124 — prova: `tools/test_documento_regulado.py`) Relatório de validação e checklist de prontidão para operação, gerados pelo perfil (`regulado.py documento`).
- [x] T5b (B3a-3, ADR-124) ERU gerada da Parte A pelo perfil farma/alimentos (REQ-11) e registros de mudança e versão gerados (`mudancas_spec.py`, REQ-12).

### B3b — Perfil farma/ANVISA (fora do núcleo)
- [x] T6 (B3b, ADR-126, 28/09/2026 — prova: `exemplos/dominio-regulado/farma-anvisa-mapa-normas.md` e `tools/test_regulado.py` (h); só medicamentos, ver Replanejamento) Clonar `exemplos\dominio-regulado\compliance-profile-saude-dispositivo.json` para `compliance-profile-farma-anvisa.json` (ADR-043) e preencher: normas (RDC 658/2022, IN 134/2022, IN 138/2022, Guia 33/2020), controles, e o mapa peça do kit → artigo num arquivo ao lado, `exemplos\dominio-regulado\farma-anvisa-mapa-normas.md` (o schema do perfil não tem campo para isso; não estender o schema), com a marca de confiança de cada citação; leitura primária da IN 134/2022 antes de marcar CONFIRMADO.

### B3d — Método único de projeto (depende de D7/D8)
- [x] T8 (ADR-121; prova: `tools\test_desenho_processo.py` (e)) `guia\METODO-DE-PROJETO.md`: fluxo numerado (elicitação → confirmação da área → especificação → desenho do processo → testes e evidências → liberação → operação), onde mora cada peça; citado no `CLAUDE.md` e no início de sessão.
- [x] T9 (Parte H do arquivo único, ADR-121) Parte Processo na especificação (passos, papéis, regras, gatilhos), a partir do mapeamento de processo existente. — prova: `tools/test_desenho_processo.py` (PR #168)
- [x] T10 (`tools\desenho_processo.py`; prova: `test_desenho_processo` e 20/20 mutações mortas; raias verticais por papel e macroações acima de 15 passos, decisões do dono de 26/09) Gerador especificação → desenho do processo em HTML de revisão, no padrão do modelo de CAPA, com papéis genéricos no núcleo; o docx controlado sai do `tools/gen_exec_doc.py` existente.
- [x] T11 (`tools\doc_intake.py evidencia registrar | verificar`; prova: `tools\test_evidencia.py`) Manifesto de evidência de desenvolvimento (REQ-15) com `tools/doc_intake.py`; verificador de existência e sha256.

### B3e — Conhecimento contextual reutilizável (D9)
- [x] T12 Estrutura `docs\_private\conhecimento\` (perfis, empresas, `INDICE-PROJETOS.md`) e modelo de `DICIONARIO.md`. — ADR-120: modelo agnóstico em `exemplos\conhecimento\_modelo\` (termo, consulta, fato, pesquisa, runbook; empresa → área de negócio → assunto); instância vazia em `docs\_private\conhecimento\`.
- [x] T13 Verificador do dicionário e do índice (critérios 17 e 18), com sabotagem. — `tools\conhecimento.py verificar | vencidos`; prova: `tools\test_conhecimento.py` e 38/38 mutações mortas.
- [x] T14 `knowledge_catalog` indexa o conhecimento (critério 19). — `--recall --conhecimento <raiz>`, lido ao vivo; sem a opção nada é carregado; retrato sai com a data. Prova: `test_conhecimento` (e).
- [x] T15 Discovery pergunta empresa e perfil regulado sem padrão (REQ-08) e grava termo confirmado no nível certo. — discovery (item 0 do método), docops (passo 7), regra global §9, dimensão `biblioteca-consultada` cobrada no arquivo único. `[~]` A semente a partir de conteúdo de projetos foi retirada desta sessão (ver Replanejamento). — prova: `tools/test_spec_unico.py` caso (j) e `tools/test_conhecimento.py` (PR #163)

### B3f — Acompanhamento de projeto (REQ-07)
- [x] T16 (ADR-127 — prova: `tools/test_plano.py` (f) e (g)) Cronograma e painel de fases gerados das Tarefas do arquivo único (`plano.py cronograma | painel`), com verificador: painel editado à mão, prazo ilegível, dependência inexistente ou fora de ordem. Critério 9 adaptado: a fonte é a linha da tarefa no `spec.md` (D2 do plano modo planejado), não um `estado.json`. — prazo: 29/09/2026

### B3c — Skill `project-docs`
- [x] T7 (B3c, 28/09/2026 — `_shared/project-docs/SKILL.md` v2.0.0: 402 → 80 linhas; conteúdo integral em 8 arquivos por assunto, soma conferida linha a linha) A tabela de 15 documentos vira: kit essencial (TAP, arquivo único, HANDOFF, glossário, cronograma gerado, confirmação e verificação com a área) + kit regulado pelo perfil (`regulado.py kit | documento`).

# Mapa de impacto

| Item | Muda? | Situação |
|---|---|---|
| hooks | não previsto | |
| scripts e gates | sim: `regulado.py` novo; `spec_fonte.py` ganha partes F, G, H, I e J; `planilhas_projeto.py` novo (B3a-2); `plano.py` ganha `painel` e `cronograma` (B3f) | B3a-2: ✅ · B3f: ✅ |
| canários | sim: novo canário do verificador | ✅ test_regulado (inclui o mapa peça → norma, B3b), test_desenho_processo, test_evidencia, test_planilhas_projeto, test_documento_regulado |
| README / guias | sim: `guia/` com o kit regulado e `guia/METODO-DE-PROJETO.md` | ✅ guia/METODO-DE-PROJETO.md (ADR-121), project-docs enxuta (B3c) e `exemplos/dominio-regulado/README.md` com o perfil farma e a regra do mapa (B3b) |
| `CLAUDE.md` | sim: 1 linha de ponteiro para o método (dieta do ADR-080) | ✅ ponteiro ao método (ADR-121, PR #168) |
| site | sim: contagem de capacidades | ✅ contagem de capacidades e canários atualizada a cada PR (test_marketing_claims) |
| CHANGELOG | sim | ✅ uma entrada por bloco (ADR-119 a ADR-124, B3c) |
| índice de capacidades | sim | ✅ registros por bloco (test_capabilities) |
| links e caminhos | modelos do MRP citados por caminho absoluto | |

# Replanejamento
| Data | Item | O que mudou | Por quê | Quem aprovou |
|---|---|---|---|---|
| 25/09/2026 | B3 inteiro | "kit de 4 documentos" substituído por kit escalonado por risco para ambiente regulado | a proposta anterior não tinha pesquisa, crítica nem revisão; o dono cobrou | dono (cobrança de 25/09) |
| 26/09/2026 | B3e + débito DB1 | a biblioteca de consultas reutilizáveis (pedido do dono, débito DB1) entra no B3e em vez de plano próprio: tipos consulta, fato, pesquisa e runbook ao lado do termo; empresa → área de negócio → assunto; validade por classe (estrutura até mudar a versão do sistema; configuração 6 meses; regra de negócio e conceito 12; retrato não vence e é citado com data); qualquer fonte, não só um sistema; local continua o do D9 | pedido do dono (26/09) e respostas D1–D6; "siga no plano" após o autor apontar que o DB1 duplicava o D9 | dono (26/09) |
| 26/09/2026 | T15 (semente) | semear a biblioteca com conteúdo dos projetos sai desta sessão; o framework entrega só modelo, verificador e método | ordem do dono: "você está trabalhando APENAS no que é agnóstico" | dono (26/09) |
| 26/09/2026 | Recorte, critério 6, T1 | campo "impacto em BPF" passa a `**Impacto regulado:**` no motor e no modelo; "BPF" fica no perfil farma | BPF é termo sanitário; com perfil por projeto (D1: ANP e outros) o termo no núcleo seria errado | decorre de D1 (dono, 26/09); a confirmar pelo dono na entrega do B3a-1 |
| 26/09/2026 | T1, Parte G | coluna **Categoria** acrescentada à Parte G | o REQ-06 exige as categorias de teste obrigatórias do perfil; sem a coluna o verificador não as vê | autor; a confirmar pelo dono na entrega do B3a-1 |
| 26/09/2026 | REQ-04 | `verificar` estrito na liberação e `--planejamento` durante o projeto | o REQ-04 reprova teste sem resultado; aplicado sempre, o verificador reprovaria todo projeto em andamento | autor; a confirmar pelo dono na entrega do B3a-1 |
| 27/09/2026 | REQ-06, critério 3b | as 12 colunas de rodada viram uma rodada padrão de 5 colunas, uma no modelo, com instrução para acrescentar outra | as 12 do modelo são três rodadas diferentes empilhadas; copiadas, cada volta criaria colunas de formato próprio e a importação não teria formato fixo | dono (27/09): "faça com uma rodada e a instrução para adicionar rodada quando for necessário" |
| 27/09/2026 | REQ-05, critério 3a | cabeçalhos neutros no núcleo; o texto do projeto vem de `### Rótulos`; "igual ao modelo" passa a ser estrutura | termo de sistema no núcleo quebra o agnosticismo | dono (27/09): "não é só SAP, é requisitos de projeto, seja qual for" |
| 27/09/2026 | REQ-05 | VALORES POR TIPO vira VALORES POR CATEGORIA, opcional, com as categorias declaradas no projeto | as colunas do modelo são tipos de registro de um sistema | dono (27/09): "ok, ajustar e a skill adapta" |
| 27/09/2026 | B3a-3, B3c, B2b, B3b | ERU e documentos regulados saem do PERFIL farma/alimentos (motor neutro); skill enxuta e verificador do plano são gerais; perfil ANVISA é de aplicação, só farma/alimentos, sem citar empresa; virão perfis ANP e outros | o núcleo não pode carregar documento de um tipo de regulação | dono (27/09) |
| 28/09/2026 | REQ-09, REQ-11, T5, T5b | desvios em `### Desvios` (Parte G); código do documento em `### Documentos controlados` (Parte A); atributos dos requisitos em `### Atributos dos requisitos`; motor `regulado.py documento` com modelo no perfil | decisões D1–D3 do B3a-3 | dono (28/09): "todas a" |
| 28/09/2026 | REQ-07, critério 9, B3f | o cronograma sai das Tarefas do `spec.md` (`prazo:`, `depende:`), não de um `estado.json`; painel de fases gerado e verificado; o REQ-07 não tinha tarefa e o painel o escondia como 100% — ganhou a T16 | fonte única do arquivo único (ADR-117; D2 do plano modo planejado) | dono (28/09): D5 "a" — "cronograma e painel por fase gerados do spec.md, com verificador" |
| 28/09/2026 | T6, T5b | o perfil `farma-anvisa` cobre só medicamentos; alimentos saem (entram só se houver projeto); o próximo perfil é ANP; a trilha de auditoria passa a "por risco" e a assinatura eletrônica a "quando usada", conforme o texto da IN 134 | leitura primária: IN 134 art. 33 ("deve ser considerada") e art. 41 ("podem ser assinados") | dono (28/09): "vamos começar com o que temos: medicamentos. Depois será ANP, não alimentos" · "D2 farma" |
| 27/09/2026 | REQ-05, REQ-06 | toda gravação cria vN+1, move a anterior para `_obsoleto/`, compara e só então apaga a anterior; divergência reprova e restaura a anterior | regerar apagaria as respostas da área | dono (27/09) |

# Revisões adversariais
| Rodada | Revisor (modelo, agentId) | Veredito | Achados | O que mudou |
|---|---|---|---|---|
| 1 | Sonnet isolado, primeiro plano (ac87255d7a82c79af) | PASS-COM-RESSALVAS | 2 ALTA: ERU sem entregavel; reinvencao do ADR-043. 5 MEDIA: marca de confianca de IN 134/138; colunas diferentes das reais; mapeamento ausente; integridade de dados nao obrigatoria no teste; fornecedor/mudanca/migracao sem dono. 1 BAIXA: paginas lidas x secoes citadas | REQ-11 (ERU), REQ-12 (mudanca/versao), colunas medidas, secao de mapeamento, T6 clona perfil do ADR-043, categorias de teste GxP obrigatorias, fora de escopo declarado, marcas corrigidas |
| 3 | Sonnet isolado, segundo plano (aa60851910274dd28) | PASS-COM-RESSALVAS | 2 ALTA: B3d sem REQ nem critério; REQ-06 com 6 das 12 colunas de rodada. 3 MÉDIA: renomeação "materiais"→"itens" não declarada; narrativa do `check_field_mapping` desatualizada; `CLAUDE.md` fora do mapa de impacto; T10 recriava docx que `gen_exec_doc.py` já faz. 1 BAIXA: prefixo REQ nos critérios 1–6 | REQ-13/14/15 + critérios 14–16; 12 colunas reais; nome real da coluna; narrativa corrigida; `CLAUDE.md` no mapa; T10 reusa `gen_exec_doc.py`; prefixos. REQ-15 nasce do pedido do dono de 26/09 (evidência de desenvolvimento) |
| 2 | Sonnet isolado, segundo plano (a4289d562f1499e00) | PASS-COM-RESSALVAS | 3 ALTA: aba "O QUE MUDOU" ausente no arquivo atual (existia na `_v2`, trocada por outra sessão); 7 requisitos sem critério de aceite; 3 entregáveis da pesquisa omitidos sem declarar (inclui integridade de dados, vinculante). 2 MÉDIA: PASS falso do mapeamento; painel repetindo as decisões. 2 BAIXA: onde vive o mapa peça→artigo; ordem dos REQ. Revisora declarou ter gravado `__pycache__` no repo (ignorado pelo git; removido) | abas corrigidas; critérios 7–13; 3 entregáveis com destino; painel só referencia; T6 com arquivo próprio; REQ reordenados; B3d (D7, D8) incluído como proposta |
| — | achado do autor ao rodar os gates | — | `check_field_mapping` aceitava 'confirmação: pendente' como confirmado (regex) | corrigido no B4 (ADR-118); o gate agora reprova este arquivo até D6 |
