# Execution report — MRP Natulab: as tréplicas viram consulta, e o revisor também erra

**Sessão de 24/09/2026** · projeto de domínio em `C:\Users\fabriciosouza\Downloads\2026-09-11-MRP`
(pasta sem git e sem o framework instalado) · nenhuma escrita no núcleo do framework

- **Tokens:** NÃO MEDIDO por sessão. `execution_report.py --from-transcripts` devolve 27.076.260, que é a
  soma dos transcripts do diretório de projeto inteiro, não desta sessão.
- **Tempo (wall-clock):** NÃO MEDIDO
- **Turnos:** 7 mensagens do dono (contadas na conversa)
- **Arquivos tocados:** 7 criados, nenhum existente alterado:
  - `CONSULTAS-DBACOCKPIT-treplicas.md`, `RETOMAR-nova-sessao_2026-09-24.md` e as 2 medições brutas em
    `medicoes-2026-09-24/`, na pasta do projeto;
  - este report;
  - a memória `consulta-pronta-sem-placeholder.md`, mais a linha nova no `MEMORY.md`.
- **Testes:** não se aplica (entregável é SQL executado por humano; conferência por DD03L e QA isolado)
- **Rodadas de retrabalho:** 3 (consultas: QA FAIL, FAIL, PASS; retomada: QA FAIL na rodada 1)

## Placar gate × achado

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Placeholder `'???'` no mandante | O dono, pelo print de 0 linhas | Nenhum: a consulta saiu em chat, sem passar por QA |
| C10 misturava os centros | QA isolado, rodada 1 | QA isolado (funcionou) |
| `IN ('', ' ')` em campo CHAR(4) | QA isolado, rodada 2 | QA isolado (funcionou) |
| QA afirmou que BSTMI/BSTMA não existem | Autor, medindo no DD03L | Medição antes de aplicar o achado (funcionou) |
| E-mail "pronto" com 5 afirmações sem sustentação | Autor, relendo contra a fonte na retomada | QA de 23/09 não pegou; data relativa envelheceu |
| Autor afirmou "ME11 e ME21N concluídos nos 7 cenários" contando a presença da transação, não o status | QA isolado do handoff | Autor: contar o status, não a palavra (real: ME11 6/7, ME21N 3/7) |
| "79 famílias" sem artefato bruto | QA isolado do handoff | Autor: medição durável em `medicoes-2026-09-24/` |

## Detecção: framework × humano

O humano pegou o placeholder. O QA isolado pegou 2 defeitos silenciosos. A medição pegou 1 erro do próprio QA.

## Gaps

- Pasta do projeto sem git e sem gate (BLOCO 0 da retomada).
- Datasphere sem leitura em MARA/MARC e sem replicação de EINA/EINE/EORD/MKAL.
- `MEMORY.md` passou de 19,6 KB, perto do limite de leitura. Compactar numa sessão do framework.

## Melhorias

Nenhuma adição proposta ao núcleo (régua §0). O item de prioridade máxima do `history.md` (squad fora do
repo) ganhou mais uma ocorrência. É evidência para ele, não item novo.

## Boas práticas

- Conferir campo SAP no DD03L pelo Datasphere antes de entregar SQL.
- `TRIM(campo) = ''` como teste de vazio.
- Consulta com a data e o sistema escritos no arquivo.

## Lições por skill

- dev: SQL entregue para um humano rodar é código de produção. Vai sem placeholder, e o erro de premissa
  tem que aparecer como erro, nunca como 0 linhas.
- qa-critic: achado que afirma fato verificável se mede antes de aplicar. O revisor erra com a mesma confiança do autor.
- docops: entregável aprovado ontem não prova o texto de hoje quando ele tem data relativa.

---

## O que foi entregue

- **17 consultas prontas para a DBACOCKPIT** (`CONSULTAS-DBACOCKPIT-treplicas.md`), cobrindo as 21 tréplicas
  em aberto do checklist de cadastro do MRP. Todos os campos foram conferidos contra o dicionário SAP antes
  da entrega. Passaram por QA adversarial isolado em três rodadas: FAIL, FAIL e depois PASS.
- **Primeira medição direta no SAP de produção** (C01, executada pela colaboradora do dono): tipo de MRP por
  tipo de material nos centros 1001 e 1005.
- **Mapa do que o Datasphere alcança**: MARA, MARC, STKO e STPO dão erro de privilégio; EINA, EINE, EORD,
  EQUK e MKAL nem estão replicadas. Nenhum dos 21 campos em aberto é legível por lá.
- **Retomada para outra IDE** (`RETOMAR-nova-sessao_2026-09-24.md`), com o BLOCO 0 de instalação do
  framework na pasta do projeto como primeira decisão do dono.

## Números medidos em 24/09/2026

| | |
|---|---:|
| Linhas MARC, centro 1001 / 1005 | 20.893 / 5.884 |
| Combinações planejadas nos cinco tipos do MRP, 1001 / 1005 | 3.031 / 1.374 |
| Produtos acabados com tipo de MRP X0, 1001 / 1005 | 248 / 73 |
| Materiais dos cinco tipos sem tipo de MRP | 11 |
| Famílias de material (só existem no acabado) | 79 em 511 |

---

## Os defeitos desta sessão, e o que cada um ensinou

### 1. Placeholder que roda

Entreguei uma consulta de exemplo com `MANDT = '???'`. A colaboradora a executou em produção como estava.
Voltou "0 linhas chamadas", com sucesso e sem erro, e isso parece "não há dado".

**Remédio:** consulta entregue para colar vem pronta, e o que falta se pergunta antes. Virou memória
(`consulta-pronta-sem-placeholder`). O mesmo defeito de fundo do gate vazio: verde que não julgou nada.

### 2. O revisor afirmou um fato falso, e a correção dele quebraria a entrega

Na rodada 1, o QA isolado afirmou que `MKAL.BSTMI/BSTMA` não existiam e propôs `LOSVN/LOSBS`. O dicionário
SAP, lido pelo Datasphere (`STAGE_S4.VW_SVPL_DD03L`), mostrou o contrário: `BSTMI` e `BSTMA` existem, e
`LOSVN` e `LOSBS` não existem no MKAL.

**Remédio:** achado de QA que afirma fato verificável se mede antes de aplicar. O QA adversarial vale pelo
ceticismo, não pela autoridade; aplicar achado sem medir é trocar um autor que erra por outro.

### 3. Número plausível e errado, duas vezes, sem erro nem vazio

- A C10 agregava o registro info só por material e misturava os centros 1001 e 1005.
- O teste de vazio `IN ('', ' ')` não pega campo de 4 caracteres gravado com 4 espaços.

Nenhum dos dois dá erro nem volta vazio. O QA pegou os dois.

**Remédio:** `TRIM(campo) = ''` em todas as consultas, e a chave de centro preservada em toda subquery.

### 4. O e-mail "pronto" tinha cinco afirmações que a medição não sustenta

O e-mail de 23/09 tinha passado por QA. Medido em 24/09:
- "48 dias úteis" é contagem sem feriado;
- "61 etapas" é média;
- "validou sem passar pela compra" é contrariado em parte pelo roteiro, que tem a ME21N concluída em 3 dos 7 cenários;
- "lista de fontes comprovada" não tem evidência;
- "cinco linhas" confunde regra com carga.

**Remédio:** reler o entregável contra a fonte quando a sessão muda. QA aprovado ontem não prova o texto de
hoje, porque a data relativa ("a partir de amanhã") muda sozinha.

### 5. O framework não está instalado onde o trabalho acontece

É a quarta ocorrência do item de prioridade máxima do `history.md`: o squad e o QA adversarial não são
determinísticos fora do repo do framework. Nesta sessão o QA rodou porque o agente o rodou, não porque
algum gate exigiu.

**Remédio:** o BLOCO 0 do documento de retomada põe a instalação (git local, `install_git_hooks.py`,
briefing, glossário, mission) como primeira decisão do dono, com prova de que o gate barra.

## Pendências entregues à próxima sessão

- Corrigir o e-mail e o painel (aguardando três decisões do dono).
- Rodar as consultas C02 a C17.
- As pendências 2 a 9 do RETOMAR de 22/09.
- Instalar o framework na pasta do projeto (BLOCO 0).
