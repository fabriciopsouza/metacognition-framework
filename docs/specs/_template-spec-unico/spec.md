<!-- spec-unico:v1 -->
# <feature> — Especificação

> **Arquivo único de especificação (ADR-117).** Substitui `requirements.md` + `validation.md` +
> `context-brief.md` + `mission.md` + `data-dictionary.md` da feature: mesmo conteúdo, mesmos gates
> (`check_spec_depth`, `check_completeness`, `check_field_mapping`, `check_context_brief` leem as
> partes daqui). Não renomeie os títulos `# Parte X — ...`: é por eles que os gates acham cada parte.
> Ordem de trabalho: pesquisa e elicitação → crítica → decisões **em conversa** → requisitos
> aprovados → aceite escrito e ratificado pelo revisor isolado → execução → revisão → fechamento.

## Painel
> Acumula toda decisão pedida em qualquer resposta (decidida, pendente, adiada) e quem age. A
> resposta no chat traz só um status curto com o link absoluto para cá. IDs fixos: D = decisão do
> dono, T = trabalho, S = assunto.

**Avanço:** <bloco> <x>% · <bloco> <y>%

| # | Assunto | Situação | Quem age | Resultado / próximo |
|---|---|---|---|---|
| D1 | <decisão> | ⏳ pendente | **dono** | <recomendação> |

## Resumo executivo
**Onde estamos.** <resultado com número medido>
**O que falta.** <itens restantes, nomeados, motivo em meia frase>
**Próximos passos.** <ação + dono/decisão>

## Quem precisa, o quê, para quê
| Quem | Precisa de | Para |
|---|---|---|
| <papel> | <o quê> | <para quê> |

## Crítica do pedido
<premissas, tensões, custo e consequência — antes de agir>

# Parte A — Requisitos
<!-- origem: requirements.md -->
<!-- titulo original: requirements.md — Especificação Atômica de uma Feature/Caso -->

> Clonar esta pasta para cada feature/caso: `docs/specs/<nome>/`.
> Fonte do método: pesquisa A2 (camada atômica do SDD). Esta é a **intenção**,
> não a implementação — não ditar classes/libs aqui.

## Identificação
- **Caso/feature:** <nome>
- **Indicador/objeto:** <o que se analisa ou constrói>
- **Recorte:** <ano | regional | total | n/a>
- **Confiança da tarefa:** ALTA | MÉDIA | BAIXA  → governa o roteamento (ver `rules/04`)

### Enquadramento regulado (ADR-119 — lido por `tools/regulado.py`)
> Não há perfil padrão: o projeto declara o seu. Sem ambiente regulado: `**Impacto regulado:** não` e
> `**Perfil regulado:** nenhum`, e as Partes F e G podem ser apagadas.
- **Impacto regulado:** sim | não — <por quê, em meia frase; ex.: afeta boas práticas de fabricação, qualidade do produto ou dado regulado>
- **Perfil regulado:** <nome do perfil em `exemplos/dominio-regulado/compliance-profile-<nome>.json`> | nenhum
- **Empresa:** <empresa da biblioteca de conhecimento> | nenhuma — opcional; soma ao perfil a camada privada da empresa (`perfis/compliance-profile-<perfil>.json` na biblioteca dela). Declarada e ausente na máquina, o kit é recusado
- **Sistema:** <sistema afetado>
- **Categoria de software:** 1 | 3 | 4 | 5
- **Categoria decidida por:** <nome, dd/mm/aaaa — motivo> _(obrigatório quando diverge do padrão do perfil para o sistema)_
- **Requisitos confirmados por:** <nome da área, dd/mm/aaaa>
> Verificação: `python tools/regulado.py verificar <spec.md> --planejamento` durante o projeto;
> sem `--planejamento` na liberação (todo teste executado, com evidência, nome e data).

### Requisitos numerados
- REQ-01: <requisito verificável>

### Atributos dos requisitos
> _(com impacto regulado, quando o perfil pede; apague se não se aplica)_ Colunas depois de **Requisito** = as do
> perfil (`requisito_campos`), com o nome exato dele; os documentos do perfil saem daqui (`regulado.py documento`,
> ADR-124).

| Requisito | <coluna 1 do perfil> | <coluna 2 do perfil> |
|---|---|---|
| REQ-01 | <valor> | <valor> |

### Documentos controlados
> _(com impacto regulado)_ Código e versão de cada documento gerado. O código vem da Qualidade: deixe vazio até ela
> preencher, nunca invente.

| Documento | Código | Versão |
|---|---|---|
| <tipo do documento no perfil> |  | 1 |

## Spec Kernel — HEAD (opcional; ADR-081 / padrão bmad-spec)

> 5 campos compactos consumidos por skills downstream (architect, developer, qa-critic) sem precisar ler o requirements inteiro. Preencher ao fechar a elicitação. **Não substitui o requirements completo** — é um resumo executável.

- **Why:** <o problema concreto que este caso resolve — 1–2 frases>
- **Capabilities:** <o que o sistema/entrega será capaz de fazer — lista curta>
- **Constraints:** <limites não-negociáveis (técnicos / negócio / regulatórios)>
- **Non-goals:** <o que explicitamente não está no escopo — evitar escopo-deslizante>
- **Success signal:** <condição objetiva binária de "pronto" — quando a Parte B — Aceite existir, citar o critério de PASS correspondente em vez de redefinir aqui>

---

## Escopo declarado pelo discovery (ADR-010 — obrigatório quando há sinal de contexto especializado)

> Lote temático do passo 6 do `discovery/SKILL.md`. **Modo A (Transcribe-mode determinístico):** se briefing tem declaração nominal+ubíqua+stakeholder+sem-contradição → transcrever do briefing (citar trechos). **Modo B (Interview-mode, default):** preencher abaixo via elicitação com dono.

### (a) Regulado?
Este projeto opera sob alguma norma/convenção externa? Quais? Vigência?
- `[CONFIRMADO|INFERIDO|DESCONHECIDO]` <norma> — <vigência> · fonte: <doc/dono>
- **Origem:** [via briefing — citar trecho] | [via interview]

### (b) Alto-risco?
Decisão downstream irreversível, financeira material ou auditável?
- Sim/Não + justificativa.

### (c) Regras com semântica?
Regra de negócio onde o "como" importa tanto quanto o "quê" (anti-fraude, audit trail, fairness, etc.)?
- Sim/Não + lista concreta.

### (d) Gaps não-bloqueantes?
Dimensões/dados sabidos ausentes mas não impedem entrega?
- <gap> · impacto se não tratado · decisão dono: manter gap / tratar follow-up.

**Sem declaração afirmativa em (a)/(b)/(c) → defaults agnósticos.** Gates downstream (`high-stakes-gate`, reforço sênior `metodo-senior.md`, roteamento reflexivo) carregam SOB DECLARAÇÃO, não por sinal semântico (ADR-010 §Princípio 12).

## Dimensões de elicitação (banco agnóstico — ADR-033)

> Obrigatório para **produto recorrente** (software/dado/pipeline/relatório-ferramenta). Para cada
> dimensão, registrar a **decisão** (não a pergunta). O discovery recomenda um default sênior com o
> trade-off; aqui fica a decisão confirmada/alterada. `tools/check_spec_depth.py` **barra J1**
> (discovery→architect) se alguma dimensão obrigatória ficar sem decisão. Banco e aliases:
> `_shared/discovery/elicitation-dimensions.md` (aliases permitem usar o vocabulário do domínio).

- operador: <quem opera — técnico/leigo → consequência na interface>
- interface: <CLI | GUI | web | planilha — proporcional ao operador>
- entrada-validacao: <como entram os dados; lista/valida/orienta a fonte?>
- escopo-temporal: <ponto único | intervalo | total | realizado+acumulado>
- recortes-saida: <por quais cortes a saída é vista; "todos"?>
- persistencia: <memória entre execuções? histórico? reprocesso?>
- auditoria-log: <registra quem rodou/quando/insumos/versão da regra?>
- ambiente-execucao: <instala/roda em máquina limpa? entry-point não-interativo?>
- formato-saida: <relatório/export; faixas/metas visíveis; rastreável à fonte?>
- biblioteca-consultada: <o que a biblioteca da empresa já tinha e foi reusado, ou "nada encontrado"; `python tools/knowledge_catalog.py --recall --context "<termos>" --conhecimento <raiz> --empresa <empresa>`>
- escopo-e-prazo: <marco que governa (ou "sem marco") e posição no caminho crítico; acima: <escopo maior, custo, cabe no marco?>; abaixo: <escopo menor, custo>>

## Mapeamento de campo-fonte (ADR-035 — obrigatório quando há colunas-irmãs ambíguas)

> Quando um termo do pedido pode casar com mais de um campo/coluna de nome parecido (um componente vs.
> o total, "interna" vs. "manual" vs. soma), o mapeamento termo→coluna é **decisão registrada do dono**,
> não inferência. `tools/check_field_mapping.py` exige, por linha: **confirmação do dono** +
> **justificativa (`porque:`)**. Remover esta seção se não houver ambiguidade de campo-fonte.

- <termo> -> <coluna escolhida> | confirmação: [CONFIRMADO] pelo dono | porque: <justificativa, idealmente com prova numérica> | irmãs descartadas: <colunas candidatas e por que não>

## Cobertura exigida pelo pedido (ADR-034)

> Liste cada **quantificador de escopo** do pedido ("cada X", "por X", "mês a mês"/mensal, "acumulado",
> "ano inteiro"/anual, "intervalo", "todos"). `tools/check_completeness.py` cruza cada um com um critério
> binário da Parte B — Aceite — quantificador do pedido sem critério = FAIL antes do PASS (J4). Remover
> esta seção se o pedido não tem quantificadores de escopo.

- <quantificador 1 — ex.: por unidade / cada entidade>
- <quantificador 2 — ex.: mês a mês ao longo do intervalo>
- <quantificador 3 — ex.: acumulado além do realizado>

## Escopo funcional (EARS — opcional, mas recomendado)
- **Ubíquo:** "O sistema DEVE <comportamento>."
- **WHEN:** "QUANDO <evento>, o sistema DEVE <resposta>."
- **IF/THEN:** "SE <condição de exceção>, ENTÃO o sistema DEVE <tratamento>."
- **WHERE:** "ONDE <contexto específico>, o sistema DEVE <variação>."

## Fluxos de exceção e lógicas limítrofes (explícitos)
- <NULL / zero / negativo / extremo / string vazia — como tratar>
- <divergência de fonte / dados ausentes>

## Fora de escopo (anti-spec gigante)
- <o que este caso NÃO cobre>

## Fontes de dados
- <tabela/dataset/arquivo + como acessar — file-first antes de assumir colunas>

## Glossário relevante
- <termos deste caso; remeter a 00-glossario.md>

# Parte B — Aceite
- **Requisitos aprovados pelo dono em:** <data> · **Aceite escrito em:** <data, sempre depois da aprovação> · **Aceite ratificado pelo revisor isolado em:** <data> (agentId: <id>)
> Depois de ratificado, o aceite só muda pelo registro de Replanejamento.
<!-- origem: validation.md -->
<!-- titulo original: validation.md — Critério de Aceite Binário (o gate de "pronto") -->

> O arquivo mais importante da spec. Declara **objetivamente** quando a tarefa
> transita de *incompleta* para *finalizada*. Fonte: pesquisa A2.
> O QA-Critic valida contra ESTE arquivo. Sem critério binário → não fecha.

## Critérios de aceite (cada um VERDADEIRO ou FALSO — nada subjetivo)

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 1 | <ex.: campos aderem ao glossário> | comparar termo a termo | ☐ |
| 2 | <ex.: reconciliação Total = Σ partes bate (tolerância X)> | somar regionais vs total | ☐ |
| 3 | <ex.: edge cases tratados: NULL, zero, neg., extremo> | test cases tabulados | ☐ |
| 4 | <ex.: DIV/0 explícito> | inspeção da fórmula | ☐ |
| 5 | <ex.: toda afirmação numérica classificada> | ver `_shared/confidence-classification` | ☐ |
| 6 | <ex.: número rastreável à query/arquivo de origem> | trilha decisão→fonte | ☐ |

## Test cases obrigatórios (referência: `_shared/output-format`)

| Caso | Input | Esperado | Resultado | OK? |
|---|---|---|---|---|
| Normal | <típico> | <…> | | ☐ |
| Zero | denom=0 | NULL ou 0 | | ☐ |
| NULL | campo NULL | tratado | | ☐ |
| Negativo | < 0 | conforme regra | | ☐ |
| Extremo | outlier | conforme regra | | ☐ |

## Regra de transição
Tarefa = **FINALIZADA** somente quando **todos** os critérios acima = VERDADEIRO.
Qualquer FALSO → volta ao Developer. Limite: circuit breaker de QA (ADR-118); grave toda rodada, inclusive reprovação.

# Parte C — Contexto e âncoras
> _(opcional — só quando há sinal de stake (ADR-051); apague a parte se não se aplica)_
<!-- origem: context-brief.md -->
---
artefato: context-brief
projeto: <nome do projeto>
entidade: <empresa/cliente/órgão — a entidade real>
dominio: <atividade VERIFICADA no dado/documento, não suposta>
data_geracao: <YYYY-MM-DD>
autor: <agente/role>
status: evidência de discovery (prova da decisão)
confianca_global: <ALTA|MÉDIA|BAIXA — com base nas fontes>
tags: [<dominio>, <entidade>, <regulatorio>, <metodo>, discovery, context-research]
rag_ready: true
estilo_citacao: ABNT
---

<!-- titulo original: Context-Brief <projeto> — Evidência de Discovery (prova da decisão) -->

> Persiste, de forma auditável e recuperável (RAG/ABNT/ADR-style), a investigação de contexto
> que fundamenta o desenho da solução. Disparado por sinal de STAKE (`context-signals.txt`, ADR-051).
> Cada afirmação material é classificada **CONFIRMADO** (fonte) / **INFERIDO** / **DESCONHECIDO**.
> Validado por `tools/check_context_brief.py` antes de J2. (Gate prova ESTRUTURA, não qualidade.)

## 0. Sumário executivo (3 fatos que mudam o design)
1. <fato + impacto no design> `[CONFIRMADO|INFERIDO]`
2. ...
3. ...

## 1. Perfil da entidade (eixos de discovery sênior)
| Eixo | Fato | Confiança |
|---|---|---|
| Identidade / controle | <…> | <…> |
| Setor / enquadramento | <…> | <…> |
| Porte (receita/volume/share) | <…> | <…> |
| Cadeia (faz/onde/vende/compra) | <…> | <…> |
| Modelo (B2C/B2B/B2B2C) | <…> | <…> |
| Escopo (nicho vs amplo) | <…> | <…> |
| Como controla o processo medido | <…> | <…> |
| Posição de mercado / concorrência | <…> | <…> |

## 2. Verificação de âncora (vigência + pertinência) — OBRIGATÓRIA
> Cada norma/benchmark citado é **vigente** e **pertinente a ESTE tipo de entidade**?
> Acusar **mesmo quando a escolha foi deliberada** (registro consciente, não acusação de erro).

| Norma / âncora citada | Vigência | Pertinência ao tipo de entidade | Decisão registrada |
|---|---|---|---|
| <norma> | <em vigor? revogada? por quem?> | <aplica a este tipo? ou é de outra atividade → referencial> | <manter/descartar/usar como referência> |

## 3. Materialidade (computada do dado quando possível — foco, não amplitude)
<quanto se perde/vale; número que justifica o rigor> `[CONFIRMADO dos dados]`

## 4. Benchmark de método (vs prática do domínio)
<o método é aderente? pontos fortes/fracos vs alternativas> `[CONFIRMADO|INFERIDO]`

## 5. Lacunas não-bloqueantes a elicitar
(a) … (b) … (c) …

## 6. Fontes (ABNT-style, com data de acesso)
- AUTOR. *Título*. Disponível em: <URL>. Acesso em: <DD mmm. AAAA>.

*Termos proprietários sem fonte pública = DESCONHECIDO declarado, não inventado.*

# Parte D — Missão
> _(opcional — missão desta feature; a `mission.md` da raiz do projeto continua existindo, o hook de boot a lê)_
<!-- origem: mission.md -->
<!-- titulo original: mission.md — Missão do projeto/feature (ADR-022) -->

> **Lar persistente** do escopo declarado pelo discovery (ADR-010/012) **+** o `product_type` que
> ativa os papéis especializados (ADR-023). Não é artefato paralelo: funde a declaração de escopo
> num só lugar (régua §0). O hook `mission-gate` (SessionStart, ADR-022) lê este arquivo e injeta a
> diretriz BRIEFING/ADVANCE/STANDARD conforme o modo de execução (ADR-005). Sem `product_type`
> declarado, o pipeline não deve avançar para implementação (J2+) sem confirmação.
>
> Clonar para a raiz do projeto (`mission.md`) ou `docs/specs/<caso>/mission.md` e preencher.

## Produto (campo lido pelo mission-gate — ADR-022)

Declare o tipo de produto na forma **inline** `product_type: <valor>` (uma linha; NÃO como heading):

```
product_type: <ide-code | executable | gui-app | data-notebook | data-pipeline | research-code | report | spec | regulated>
```

> Os valores são a taxonomia da app SW/dados (`exemplos/dominio-software/product-types.txt`), que ativa
> os papéis especializados. Sem aplicação de domínio → declare livremente o FORMATO de entrega esperado.
> Enquanto o valor for o placeholder `<...>`, o mission-gate mantém o estado ADVANCE.

## Objetivo (1 frase) e critério de aceite
- Objetivo: <o que entregar>
- Aceite (binário): <condição objetiva de "pronto">

## Escopo declarado pelo discovery (ADR-010/012 — passo 6)
- (a) Regulado? quais normas? vigência? <...>
- (b) Alto-risco / decisão downstream irreversível/financeira/auditável? <...>
- (c) Regra de negócio com peso semântico (anti-fraude, audit trail, fairness)? <...>
- (d) Gaps não-bloqueantes (flagados, não silenciados)? <...>
- (e) Alimenta outra sessão/agente? → Pacote de handoff obrigatório (ADR-012). <...>
- (f) **product_type** confirmado pelo dono? <sim/não> · modo de execução no momento: <default|avançado|autosuficiente>

# Parte E — Dicionário de dados
> _(opcional — só quando há dados; apague a parte se não se aplica)_
<!-- origem: data-dictionary.md -->
<!-- titulo original: Dicionário-contrato de entrada (ADR-046) — `<caso>` -->

> **Contrato verificável** dos arquivos de entrada do produto. O `discovery` produz; o produto
> **auto-detecta** esses arquivos na pasta selecionada e **valida** (via `tools/check_input_contract.py`)
> que as colunas obrigatórias existem — antes de processar. É o antídoto a "produto sem validação de
> arquivos" e a join-silencioso-a-zero. Remover esta seção se o produto não consome arquivos.
>
> Formato machine-readable (lido pelo gate): um bloco `### arquivo: <glob>` por arquivo + tabela de colunas.

## Contrato de entrada

### arquivo: <glob, ex.: fonte_*.xlsx>  | obrigatório
| coluna | tipo | obrigatória | regra/observação (ex.: prioridade de mapeamento, normalização de chave) |
|---|---|---|---|
| <nome-padronizado> | string\|int\|float\|date | sim | <ex.: normalizar `5123.0`→`5123` antes do join; nunca misturar antes/depois> |

### arquivo: <glob, ex.: dimensao_*.xlsx>  | opcional
| coluna | tipo | obrigatória | regra/observação |
|---|---|---|---|
| <nome> | string | sim | — |

> **Regra de mapeamento (quando há colunas-irmãs):** declarar a prioridade explícita (ex.: "usar a
> coluna *após* tratamento; nunca a bruta") — isto alimenta também o `## Mapeamento de campo-fonte`
> (ADR-035). **Alerta de join:** toda chave de junção deve ter regra de normalização declarada (o
> anti-pattern recorrente é inteiro lido como float → join retorna zero match silencioso).

# Parte F — Riscos
> _(obrigatória com impacto regulado; apague se não se aplica)_ Uma linha por risco. Classe: alto |
> médio | baixo. Risco alto exige mitigação e teste. `python tools/regulado.py verificar <spec.md>`.

| Risco | Requisito | Falha | Impacto | Probabilidade | Detecção | Classe | Mitigação | Teste |
|---|---|---|---|---|---|---|---|---|
| RISCO-01 | REQ-01 | <o que pode falhar> | <efeito no produto, no paciente ou no dado> | <alta/média/baixa> | <como a falha é percebida> | alto | <controle> | TESTE-01 |

# Parte G — Testes e evidências
> _(obrigatória com impacto regulado; apague se não se aplica)_ Todo requisito tem teste. Resultado:
> `aprovado` ou `reprovado` (ou `pendente` enquanto não executado). Resultado preenchido exige evidência (caminho do arquivo: print, xlsx, consulta, log) e nome e data de quem
> executou. Matriz de rastreabilidade: `python tools/regulado.py matriz <spec.md>`.

| Teste | Requisito | Categoria | Roteiro | Esperado | Resultado | Evidência | Nome e data |
|---|---|---|---|---|---|---|---|
| TESTE-01 | REQ-01 | <funcional \| integridade de dados \| trilha de auditoria \| ...> | <passos> | <resultado esperado> | pendente | pendente | pendente |

### Desvios
> Teste reprovado exige desvio registrado, com tratamento e nome e data (entra no relatório de validação).

| Desvio | Teste | Descrição | Tratamento | Nome e data |
|---|---|---|---|---|

### Prontidão para operação
> _(sistema que entra em uso)_ Itens obrigatórios vêm do perfil (documento de prontidão do perfil, ADR-124).

| Item | Situação | Onde está |
|---|---|---|
| <item do perfil> | <existe/pendente> | <caminho ou documento> |

# Parte H — Processo
> _(quando o projeto muda ou cria um processo; apague se não se aplica)_ Fonte do desenho do processo:
> `python tools/desenho_processo.py <spec.md> --out-dir <pasta>` gera o HTML de revisão e o docx — nunca
> edite os gerados. Uma linha por passo, em ordem. **Próximo:** `P-02`, ou em decisão `sim: P-03; não: P-05`
> (vazio = fim). Mais de 15 passos: agrupe em **Macroação** (o desenho sai em dois níveis) ou registre
> `--aceito-mais-de-15 "<frase do dono, dd/mm/aaaa>"`. A área responde na planilha de confirmação, não no HTML.

| Passo | Macroação | Descrição | Papel | Gatilho | Saída | Próximo | Regra | Controle |
|---|---|---|---|---|---|---|---|---|
| P-01 | <macroação> | <o que se faz> | <papel> | <o que dispara> | <o que sai> | P-02 | <regra de negócio> | <ponto de controle> |
| P-02 | <macroação> | <decisão> | <papel> | — | — | sim: P-03; não: P-01 | — | — |
| P-03 | <macroação> | <o que se faz> | <papel> | — | <o que sai> | | — | — |

### Pontos para aprovação
> Viram linhas `H-n` da planilha de confirmação (Parte I). As três colunas de resposta são preenchidas
> pelo `importar`; não as escreva à mão.

| # | Ponto | Por que importa |
|---|---|---|
| 1 | <o que a área precisa aprovar> | <consequência> |

### Perguntas em aberto
| # | Pergunta | Quem decide |
|---|---|---|
| 1 | <pergunta> | <papel> |

# Parte I — Definições a confirmar
> _(quando a área precisa confirmar regras ou valores; apague se não se aplica)_ Fonte da planilha de
> confirmação: `python tools/planilhas_projeto.py gerar <spec.md> --out-dir <pasta>`. Cada gravação cria
> `confirmacao_vN.xlsx`; a anterior só é apagada depois de comparada. A resposta da área volta com
> `importar <spec.md> --planilha <xlsx> --out-dir <pasta>`, que grava as três últimas colunas aqui e gera a
> versão seguinte. Os campos `**...:**` abaixo formam a aba LEIA. As colunas valem para qualquer projeto;
> o texto do cabeçalho se adapta ao domínio em `### Rótulos` (a ordem e o papel da coluna não mudam).

**Para que serve:** <reunir as regras para a área confirmar>
**Quem responde:** <área>
**Prazo:** <dd/mm/aaaa>
**Como devolver:** <canal>

| Definição | Tema | Regra, como entendemos | Exemplo | Como fica no sistema | Exige alterar muitos registros? | Situação hoje | É possível? Como? Em massa? | Links (fonte e tutorial) | De onde tiramos | Área confirma? | Correção da área | Nome e data |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DEF-01 | <tema> | <regra> | <exemplo concreto> | <onde e como fica> | <sim/não> | <conforme/diverge/sem definição> | <como fazer, em massa?> | <links> | <reunião, documento> | | | |

### Valores por categoria
> _(opcional; apague se não se aplica)_ Matriz de valores esperados por categoria (tipo de registro, perfil,
> unidade). As colunas entre **Nome técnico** e **Regra** são as categorias do projeto.

| Item | Nome técnico | <categoria 1> | <categoria 2> | Regra | Área confirma? | Correção da área | Nome e data |
|---|---|---|---|---|---|---|---|
| <item> | <nome técnico> | <valor> | <valor> | DEF-01 | | | |

### Rótulos
> _(opcional)_ Texto do cabeçalho neste projeto. Ex.: `| Como fica no sistema | Como fica no ERP |`.

| Coluna | Rótulo neste projeto |
|---|---|

# Parte J — Roteiro de verificação
> _(quando a área confere o sistema contra as regras; apague se não se aplica)_ Fonte da planilha de
> verificação (`verificacao_vN.xlsx`), gerada e importada como a Parte I. Uma subseção `### Bloco: <nome>`
> por grupo de verificações. Com impacto regulado, o `gerar` acrescenta um bloco para cada categoria
> obrigatória do perfil que faltar. **Rodadas:** o modelo traz uma; para devolver perguntas à área,
> `python tools/planilhas_projeto.py rodada <spec.md> --data dd/mm/aaaa --ids VER-01,VER-03` acrescenta a
> próxima; escreva a pergunta de volta e gere de novo. O que a área já respondeu:
> `python tools/planilhas_projeto.py situacao <spec.md> [--exigir]`. Os campos `**...:**` abaixo formam a aba
> COMO USAR.

**Para que serve:** <conferir, item a item, se o sistema segue as regras confirmadas>
**Quem preenche:** <área>

### Antes de começar
- <armadilha que muda a leitura da conferência>

### Bloco: <nome do bloco>
| Verificação | Onde olhar | Item como aparece na tela | Nome técnico | O que o item faz | Aplica-se a | Regra / valor esperado | Como conferir vários de uma vez | Se estiver errado, o que acontece | Criticidade | Natureza da decisão | Confiança | Valor encontrado | Conclusão da área | Data / Visto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VER-01 | <tela, relatório, tabela> | <nome na tela> | <nome técnico> | <função do item> | <a quais registros> | <valor esperado, DEF-nn> | <consulta em massa> | <consequência> | <bloqueador/alto/médio/baixo> | <quem decide> | <CONFIRMADO/INFERIDO> | | | |

### Rodada 1 — <dd/mm/aaaa>
| Verificação | Pergunta de volta | Resposta da área | O que fazer (valor, onde, quem) | Situação | Nome e data |
|---|---|---|---|---|---|

### Achados do ambiente
| Achado | O que foi constatado | Por que muda a leitura | O que fazer | Confiança |
|---|---|---|---|---|

### Correções da base
| Correção | O que constava | Correção aplicada | Motivo |
|---|---|---|---|

### Controle de versão
| Versão | Data | Autor | Conteúdo | Base utilizada |
|---|---|---|---|---|

# Decisões
| # | Decisão | Alternativas | Recomendação | Resposta do dono |
|---|---|---|---|---|
| D1 | <decisão> | (a) ... · (b) ... | **(a)**: <por quê> | _pendente_ |
> ADR só para decisão de arquitetura (mais de um arquivo, dependência, contrato); o resto fica aqui.

# Tarefas
Legenda: `[ ]` a fazer · `[x]` feito, **com prova** ao lado · `[~]` replanejado, **com motivo** em Replanejamento.
> Se o projeto usa o pacote de controle de projeto, as tarefas vêm do `estado.json` e esta lista é
> gerada dele — não mantenha as duas à mão.

### <entregável> (faz o papel de épico)
- [ ] T1 <quem precisa · o quê · para quê> — aceite: <critério da Parte B>

# Mapa de impacto
> O que mais muda junto com este bloco. Cada linha: situação e prova.

| Item | Muda? | Situação |
|---|---|---|
| hooks | <sim/não> | |
| scripts e gates | | |
| canários | | |
| README / guias | | |
| site | | |
| CHANGELOG | | |
| índice de capacidades | | |
| links e caminhos | | |

# Replanejamento
| Data | Item | O que mudou | Por quê | Quem aprovou |
|---|---|---|---|---|

# Revisões adversariais
| Rodada | Revisor (modelo, agentId) | Veredito | Achados | O que mudou |
|---|---|---|---|---|
