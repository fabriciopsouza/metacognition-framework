<!-- spec-unico:v1 -->
# Isolamento entre empresas na biblioteca de conhecimento — Especificação

> Arquivo único de especificação (ADR-117). Estado: **EM EXECUÇÃO** · 27/09/2026 · autor: sessão Opus 5.5.
> Nasce do pedido do dono de 27/09/2026 (itens a–e), com a regra: *"conhecimento de uma empresa (processo, centros,
> códigos, valores, consultas, nomes) nunca aparece no trabalho de outra. Só o saber puro de assunto (SAP MM não
> customizado, EWM, SE Suite, gestão de projetos) pode ser compartilhado entre empresas."*

## Painel

**Avanço:** investigação ✅ · crítica ✅ · revisão do plano ✅ · itens a–e implementados com canário ✅ · revisão do código ⏳ · decisões D1, D2, D3 e D5 com o dono

| # | Assunto | Situação | Quem age | Resultado / próximo |
|---|---|---|---|---|
| D1 | Separação física: a biblioteca de cada empresa sai do repositório do framework | ✅ executado 27/09 (emenda 2 do ADR-120) | — | ver Tarefas T5–T8 |
| D2 | Identificadores de empresa que outra máquina não tem (verificação de `assuntos/`) | ✅ executado 27/09 (emenda 2 do ADR-120) | — | ver Tarefas T5–T8 |
| D3 | Relatórios de sessão no `--recall` | ✅ executado 27/09 (emenda 2 do ADR-120) | — | ver Tarefas T5–T8 |
| D4 | Sessão do próprio framework (fora de projeto): `--empresa nenhuma` | ✅ aplicada (reversível) | — | informativa; o dono pode reverter |
| D5 | Versão de sistema da Natulab no `conhecimento.json` da raiz | ✅ executado 27/09 (emenda 2 do ADR-120) | — | ver Tarefas T5–T8 |

## Resumo executivo
**Onde estamos.** Os três problemas do pedido foram reproduzidos contra o código do `origin/main` (`f9753ae`) com
duas empresas sintéticas, na investigação de 27/09 (subagente explorador, só leitura, fixture em `%TEMP%`). Achei mais dois: os relatórios de sessão entram no mesmo `--recall` sem filtro (12 de 38 citam empresa) e o
`INDICE-PROJETOS.md`, que resolve a empresa, é ele mesmo dado de empresa. No `origin/main` só existe
`empresas/natulab/`; a `vibra` e o `sap-mm-generico.md` estão em outra máquina.
**O que falta.** Filtro por empresa, relações escopadas, camada `assuntos/` verificada e canário (itens a–e); decisões
D1–D4.
**Próximos passos.** Executar a–e com os padrões recomendados, sem mesclar antes das decisões D1–D4 do dono.

## Crítica do pedido
1. **Filtro não é isolamento.** A biblioteca inteira é versionada no repositório do framework (decisão de 26/09) e
   clonada em toda máquina: na máquina de uma empresa, o conhecimento da outra continua no disco e é lido por `grep`,
   por leitura direta ou por outra ferramenta. O `--empresa` isola o que o agente recebe pela busca, não o que está
   na máquina. É a decisão D1.
2. **A lista de identificadores (item d) só enxerga as empresas presentes na máquina.** Na máquina da Vibra não há o
   dicionário da Natulab, e vice-versa: o verificador de `assuntos/` não reconhece os códigos da empresa ausente.
   Trazer a lista para todas as máquinas em texto claro é, em si, vazamento. É a decisão D2. Os padrões que não
   dependem de empresa (namespace de cliente Z*/Y*, campos ZZ*/YY*, tipos de movimento 9xx e X/Y/Z, caminhos de
   projeto) valem em qualquer máquina e entram já.
3. **Os dicionários das empresas não têm hoje a lista de identificadores.** `empresas/natulab/` não tem
   `DICIONARIO.md`. O item d precisa de um lugar determinístico para a lista: entrada `## Identificadores` de tipo
   `identificadores` no `DICIONARIO.md` da empresa, com o campo `**Valores:**`; o nome da pasta e os caminhos e
   repositórios do índice entram sozinhos.
4. **Resolver a empresa pelo cwd depende do caminho absoluto de cada máquina.** O índice guarda caminhos desta
   máquina; na outra, o projeto pode estar em outro lugar. Por isso, sem resolução, o comando falha fechado e pede
   `--empresa`, como o pedido manda.
5. **Os relatórios de sessão também vazam.** O `--recall` junta os insights de `docs/_private/_intake/` (38
   relatórios, 12 citam empresa) na mesma resposta, sem filtro. O pedido não cobre isso. É a decisão D3.
7. **Outros canais achados na revisão do plano:**
   - `conhecimento.json` da raiz guarda a versão de sistema de uma empresa (D5; o motor já aceita
     `empresas/<e>/conhecimento.json`);
   - a checagem de trabalhos abertos citava repositório de outra empresa (agora só na manutenção);
   - o `INDICE-PROJETOS.md` é lido inteiro para resolver a empresa: seguem visíveis os projetos das outras empresas,
     o que só a D1 resolve.
6. **Os 27 achados desta máquina não são de outra empresa:** são caminhos da própria Natulab que mudaram de lugar
   (ex.: `CONSULTAS-SAP-FINAL-v17.sql`). O escopo por empresa resolve o item 3 do pedido, não esses; ficam com as
   sessões de domínio.

# Parte A — Requisitos

## Identificação
- **Caso/feature:** isolamento entre empresas na biblioteca de conhecimento (emenda do ADR-120)
- **Indicador/objeto:** `tools/conhecimento.py`, `tools/knowledge_catalog.py --recall`, modelo em
  `exemplos/conhecimento/_modelo/`
- **Recorte:** n/a
- **Confiança da tarefa:** ALTA

### Enquadramento regulado (ADR-119 — lido por `tools/regulado.py`)
- **Impacto regulado:** não — ferramenta do framework; não toca sistema nem dado regulado
- **Perfil regulado:** nenhum
- **Requisitos confirmados por:** dono, 27/09/2026 (itens a–e do pedido)

### Requisitos numerados
- REQ-01 (a): camada compartilhada `<raiz>/assuntos/<assunto>/`, com `DICIONARIO.md` e `<tema>.md`, sem dado de
  empresa. Empresa pode apontar para assunto e para perfil; assunto e perfil não apontam para empresa; empresa não
  aponta para outra empresa.
- REQ-02 (b): `knowledge_catalog --recall --conhecimento` e `conhecimento.py verificar | vencidos` aceitam
  `--empresa <e>` e devolvem só `empresas/<e>/` + `assuntos/` + `perfis/`. Sem `--empresa`, a empresa é resolvida pelo
  `INDICE-PROJETOS.md` a partir do diretório atual (projeto cujo **Caminho** contém o diretório); sem resolução, o
  comando falha fechado e diz como informar a empresa. As outras empresas não são lidas como conteúdo.
- REQ-03 (c): relações resolvidas só no escopo visível; relação para termo de outra empresa e **Aponta para** ou
  **Evidência** em caminho de projeto de outra empresa (pelo índice) são achados bloqueantes.
- REQ-04 (d): entrada em `assuntos/` com identificador de empresa reprova: (1) padrões de cliente que não dependem de
  empresa — objeto Z*/Y*, campo ZZ*/YY*, tipo de movimento 9xx ou iniciado por X/Y/Z, caminho absoluto de usuário;
  (2) nome de qualquer empresa presente, e os **Valores:** da entrada `## Identificadores` do `DICIONARIO.md` de cada
  empresa, e o caminho e o repositório de cada projeto do índice.
- REQ-05 (e): canário com duas empresas falsas prova REQ-02, REQ-03 e REQ-04, e que o verificador de uma empresa não
  reprova pelo que é da outra.

## Spec Kernel — HEAD
- **Why:** uma sessão de uma empresa recebe conhecimento de outra pela busca e é reprovada por caminhos de outra.
- **Capabilities:** busca e verificação escopadas por empresa; camada de assunto compartilhada verificada.
- **Constraints:** falhar fechado sem empresa resolvida; nenhuma norma ou empresa real no núcleo.
- **Non-goals:** mover conteúdo de empresa entre máquinas ou repositórios (D1); limpar os 27 caminhos da Natulab.
- **Success signal:** critérios 1–7 da Parte B.

## Escopo declarado pelo discovery (ADR-010)
### (a) Regulado?
- `[CONFIRMADO]` não — ferramenta interna · **Origem:** [via interview] pedido do dono de 27/09
### (b) Alto-risco?
- Sim: vazamento de dado de uma empresa para o trabalho de outra (confidencialidade entre clientes).
### (c) Regras com semântica?
- Sim: o que é "saber puro de assunto" × "dado de empresa" (REQ-04).
### (d) Gaps não-bloqueantes?
- identificadores de empresa ausente na máquina · assunto verificado só contra empresas locais · decisão D2.
- relatórios de sessão no `--recall` · vazamento fora do pedido · decisão D3.

## Dimensões de elicitação (banco agnóstico — ADR-033)
- operador: agente em sessão de domínio e o mantenedor do framework
- interface: CLI
- entrada-validacao: `--empresa <e>` ou resolução pelo índice a partir do diretório atual; falha fechada
- escopo-temporal: ponto único (cada execução)
- recortes-saida: por empresa; `assuntos/` e `perfis/` sempre
- persistencia: nenhuma nova; a biblioteca continua em arquivos
- auditoria-log: a saída diz a empresa usada e como foi resolvida
- ambiente-execucao: roda em máquina com uma empresa só, sem as outras
- formato-saida: a mesma do `--recall` e do `verificar`, com a linha "empresa: <e> (resolvida por ...)"
- biblioteca-consultada: nada encontrado sobre isolamento na biblioteca; reusados ADR-120, `conhecimento.py` e `test_conhecimento.py`
- escopo-e-prazo: sem marco. Acima: separação física por repositório (D1), custo alto, depende do dono. Abaixo: só
  `--empresa` explícito, sem resolução pelo índice, custo baixo, mas deixa a regra na memória de quem roda.

## Cobertura exigida pelo pedido (ADR-034)
- cada empresa: a busca e a verificação de uma não recebem nem reprovam pela outra
- cada projeto do índice: o diretório dentro dele resolve a empresa daquele projeto
- qualquer identificador de empresa em `assuntos/` reprova

## Fora de escopo
- Mover `empresas/vibra/dados-gcp/sap-mm-generico.md` para `assuntos/sap-mm/`: o arquivo não está nesta máquina nem no
  `origin/main`; a sessão da Vibra roda o verificador nele depois do merge.
- Separação física das bibliotecas (D1), até a decisão do dono.

## Fontes de dados
- Código lido no `origin/main` `f9753ae`: `tools/conhecimento.py` (`carregar` 197-233, `verificar` 236-279),
  `tools/knowledge_catalog.py` (`cmd_recall` 464-488); `docs/_private/conhecimento/` (12 arquivos, só natulab);
  `docs/_private/_intake/` (38 relatórios, 12 citam empresa). Medido em 27/09/2026.

# Parte B — Aceite
- **Requisitos aprovados pelo dono em:** 27/09/2026 (itens a–e) · **Aceite escrito em:** 27/09/2026 · **Aceite ratificado pelo revisor isolado em:** 27/09/2026 (a222cd5cfd0828201, RATIFICADO-COM-AJUSTES; ajustes nos critérios 3 e 6 e critério 8 novo, aplicados)

| # | Critério | Como verificar | Status |
|---|---|---|---|
| 1 | REQ-02: cada empresa: busca da empresa A não devolve entrada da empresa B; devolve `assuntos/` | canário, duas empresas falsas com o mesmo termo e a mesma consulta | ✅ `test_conhecimento_isolamento` (b) |
| 2 | REQ-02: sem `--empresa` e sem resolução pelo índice, `--recall` e `verificar` falham fechado (exit ≠ 0) e dizem como informar | canário | ✅ (b) |
| 3 | REQ-02: diretório dentro do **Caminho** de um projeto do índice resolve a empresa dele; vale o projeto mais específico; prefixo sem separador não casa; dois projetos de empresas diferentes no mesmo caminho recusam | canário | ✅ (b) |
| 4 | REQ-03: relação para termo de outra empresa e caminho de projeto de outra empresa reprovam; relação para termo de assunto passa | canário | ✅ (c) |
| 5 | REQ-04: qualquer identificador de empresa em `assuntos/` reprova: nome, valor de `## Identificadores`, caminho e repositório do índice, e cada padrão de cliente; saber puro de assunto não reprova | canário, um caso por padrão e casos limpos | ✅ (d) |
| 6 | REQ-05: `verificar --empresa A` não reprova por caminho inexistente da empresa B nem cita repositório de trabalho aberto de outra empresa | canário | ✅ (e), (c) |
| 7 | nenhuma empresa real no motor nem no canário | `check_core_agnostic`; canário usa empresas falsas | ✅ |
| 8 | `--empresa <e>` usa a versão de sistema do `conhecimento.json` da própria empresa, que prevalece sobre o da raiz | canário | ✅ (c) |

# Parte C — Contexto e âncoras
---
artefato: context-brief
projeto: isolamento-empresas-biblioteca
entidade: biblioteca de conhecimento do mantenedor do framework (uso interno, várias empresas atendidas)
dominio: ferramenta interna de conhecimento reutilizável entre projetos, verificada no código em 27/09/2026
data_geracao: 2026-09-27
autor: Opus 5.5 (pmo/architect/developer)
status: evidência de discovery (prova da decisão)
confianca_global: ALTA
tags: [conhecimento, isolamento, confidencialidade, discovery, context-research]
rag_ready: true
estilo_citacao: ABNT
---

## 0. Sumário executivo (3 fatos que mudam o design)
1. A biblioteca é lida inteira pelo `--recall` e pelo `verificar`, sem recorte de empresa `[CONFIRMADO]` (código do
   `origin/main` `f9753ae`, reproduzido com duas empresas sintéticas).
2. A biblioteca é versionada no repositório do framework, clonado em toda máquina: filtro não é isolamento físico
   `[CONFIRMADO]` (decisão de 26/09 registrada na memória do mantenedor; `git ls-files docs/_private/conhecimento`).
3. Cada máquina guarda uma empresa diferente: nesta, só a Natulab; a Vibra está em outra `[CONFIRMADO]`
   (`git ls-tree origin/main`, sem `empresas/vibra`).

## 1. Perfil da entidade
| Eixo | Fato | Confiança |
|---|---|---|
| Identidade / controle | ferramenta do mantenedor do framework, repositório privado | CONFIRMADO |
| Setor / enquadramento | uso interno; sem norma externa aplicável ao motor | CONFIRMADO |
| Porte | 12 arquivos de biblioteca, 1 empresa nesta máquina; 38 relatórios de sessão | CONFIRMADO |
| Cadeia | sessões de domínio escrevem; o framework verifica e busca | CONFIRMADO |
| Modelo | uma pessoa atende várias empresas, em máquinas diferentes | CONFIRMADO (memória `fabricio-multi-pc-workflow`) |
| Escopo | método agnóstico; conteúdo de cada empresa é das sessões de domínio | CONFIRMADO |
| Como controla o processo medido | canário + gate `verificar` com exit ≠ 0 | CONFIRMADO |
| Posição de mercado | não se aplica | — |

## 2. Verificação de âncora (vigência + pertinência)
| Norma / âncora citada | Vigência | Pertinência ao tipo de entidade | Decisão registrada |
|---|---|---|---|
| Regra do dono de 27/09/2026 (isolamento entre empresas) | vigente desde 27/09/2026 | é a âncora do bloco | manter |
| ADR-120 (biblioteca de conhecimento) | Aceito em 26/09/2026 | é o que se emenda | manter, com a emenda 1 |
| Nenhuma norma externa (proteção de dados ou regulação setorial) citada | — | o motor não trata dado pessoal; o conteúdo de cada empresa segue a regra dela | não citar norma sem fonte |

## 3. Materialidade
12 de 38 relatórios de sessão citam empresa e entram no `--recall` sem filtro; a biblioteca desta máquina reprova com
27 achados, todos de caminhos da própria Natulab `[CONFIRMADO dos dados, 27/09/2026]`.

## 4. Benchmark de método
Isolamento por recorte de leitura com falha fechada é o padrão de multi-inquilino por filtro; o isolamento forte é
por armazenamento separado (D1) `[INFERIDO]`.

## 5. Lacunas não-bloqueantes a elicitar
(a) D1 separação física · (b) D2 identificadores de empresa ausente · (c) D3 relatórios de sessão · (d) D5 versão na raiz.

## 6. Fontes
- `tools/conhecimento.py` e `tools/knowledge_catalog.py` no `origin/main` `f9753ae`. Acesso em: 27 set. 2026.
- `docs/adr/120-biblioteca-de-conhecimento-metodo-e-verificador.md`. Acesso em: 27 set. 2026.

# Decisões
| # | Decisão | Alternativas | Recomendação | Resposta do dono |
|---|---|---|---|---|
| D1 | Separação física | (a) cada empresa em repositório privado próprio (ou no repositório de domínio), o framework guarda só modelo, `assuntos/` e `perfis/`; `--conhecimento` aceita mais de uma raiz · (b) manter tudo no framework e confiar no filtro | **(a)**: o filtro não impede leitura direta nem a cópia do dado na máquina da outra empresa. Custo: migrar a Natulab e reverter a decisão de 26/09 | ✅ (a) — dono, 27/09/2026: "todas a" |
| D2 | Identificadores de empresa ausente na máquina | (a) cada empresa publica em `assuntos/_identificadores/<hash-da-empresa>.sha256` o sha256 dos identificadores normalizados; o verificador compara hash de cada termo de `assuntos/` · (b) só empresas locais + padrões genéricos | **(a)**: fecha o furo sem expor texto claro. Custo: gerador e o passo de publicar; nome curto tem risco de colisão baixo | ✅ (a) — dono, 27/09/2026: "todas a" |
| D3 | Relatórios de sessão no `--recall` | (a) com `--empresa`, só relatórios cujo cabeçalho declare a mesma empresa ou nenhuma · (b) deixar como está | **(a)**: é o mesmo vazamento por outro canal. Custo: campo de empresa no relatório de execução | ✅ (a) — dono, 27/09/2026: "todas a" |
| D4 | Sessão do framework, fora de projeto | (a) `--empresa nenhuma` = só `assuntos/` e `perfis/` · (b) sem valor especial, sempre exige empresa | **(a)**, aplicada nesta entrega (reversível) | informativa |
| D5 | Versão de sistema da Natulab no `conhecimento.json` da raiz | (a) a sessão da Natulab move a chave para `empresas/natulab/conhecimento.json`; a raiz fica só com assunto · (b) manter | **(a)**: versão de sistema de uma empresa é dado dela. Custo: 1 chave, feito pela sessão de domínio | ✅ (a) — dono, 27/09/2026: "todas a" |

# Tarefas
- [x] T1 `conhecimento.py`: escopo por empresa em `carregar`, `verificar`, `vencidos`, `carregar_entradas`; nível `assuntos/`; tipo `identificadores`; resolução pelo índice; `conhecimento.json` por empresa. — prova: `test_conhecimento_isolamento`
- [x] T2 `knowledge_catalog.py --recall --empresa`. — prova: idem (b)
- [x] T3 `tools/test_conhecimento_isolamento.py` (duas empresas falsas); mutação declarada em `capabilities.json` morta.
- [x] T5 D1: Natulab em `conhecimento-natulab`, submódulo de `conhecimento-negocio` (decisão b); marcador e `bibliotecas`. — prova: `test_conhecimento_isolamento` (emenda 2)
- [x] T6 D2: `publicar` e hash em `assuntos/_identificadores`.
- [x] T7 D3: `--recall` omite relatório que cita outra empresa.
- [x] T8 D5: versão do S/4HANA na biblioteca da Natulab.
- [x] T4 modelo com `assuntos/` e `## Identificadores`; README do modelo e da instância; emenda 1 do ADR-120; regra global §9; skills discovery e docops; guia do método; banco de dimensões; modelo de arquivo único; site.

# Mapa de impacto
| Item | Muda? | Situação |
|---|---|---|
| hooks | não | |
| scripts e gates | sim: `conhecimento.py`, `knowledge_catalog.py` | |
| canários | sim: canário novo; `test_conhecimento` continua | |
| README / guias | sim: README do modelo; regra global §9; skills discovery e docops | |
| site | sim se a contagem de canários mudar | |
| CHANGELOG | sim | |
| índice de capacidades | sim: registro da capacidade | |
| links e caminhos | não | |

# Replanejamento
| Data | Item | O que mudou | Por quê | Quem aprovou |
|---|---|---|---|---|

# Revisões adversariais
| Rodada | Revisor (modelo, agentId) | Veredito | Achados | O que mudou |
|---|---|---|---|---|
| plano 1 | Sonnet isolado, segundo plano (a222cd5cfd0828201; travou 600 s e foi retomado) | PASS-COM-RESSALVAS | 1 ALTA: `conhecimento.json` global com versão de empresa. 3 MÉDIA: redação "reproduzidos"; trabalho aberto cita repositório de outra empresa; D4 marcada pendente já aplicada. 1 BAIXA: índice lido inteiro. Regex de objeto de cliente não pegava tabela sem dígito; armadilhas de cwd (já tratadas) | `conhecimento.json` por empresa e D5; trabalhos só na manutenção; redação; D4 informativa; regex nova com casos limpos; critérios 3, 6 e 8 |
