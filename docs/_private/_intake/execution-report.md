# Execution-report — encerramento de bloco (ADR-038/052 · tier OWNER · privado, não distribuído)

- **Tokens:** input 1,335,369 + output 9,300,810 = 10,636,179 (fonte: transcripts do Claude Code, ADR-026)
- **Tempo (wall-clock):** NÃO MEDIDO
- **Turnos:** NÃO MEDIDO
- **Arquivos tocados:** NÃO MEDIDO
- **Testes:** NÃO MEDIDO
- **Rodadas de retrabalho:** NÃO MEDIDO

## Placar gate × achado (quem pegou o quê)
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| (preencher por bloco) | quem pegou | gate que deveria |

## Detecção: framework × humano (quem pegou o quê — mecanismo vs. revisão humana)
— (nenhum neste bloco)

## Gaps (não-bloqueantes detectados — flagados, não silenciados)
— (nenhum neste bloco)

## Melhorias (do framework/processo — adição passa pela régua §0)
— (nenhum neste bloco)

## Boas práticas (o que funcionou — reutilizável)
— (nenhum neste bloco)

## Lições por skill (agnóstico de domínio — o que daqui serve a OUTRO projeto)
- dev: — (nenhum neste bloco)
- discovery: — (nenhum neste bloco)
- architect: — (nenhum neste bloco)
- qa-critic: — (nenhum neste bloco)
- docops: — (nenhum neste bloco)
- research/spec/ux: — (nenhum neste bloco)

---

## Sessao 2026-07-22 - APLICACAO do framework (dominio: ETL SAP Natulab)

**Natureza:** framework APLICADO a um dominio, nao desenvolvido. Nenhuma
alteracao no nucleo. Entregavel fora do repo (write-isolation ADR-070):
`C:\Users\fabriciosouza\etl-natulab-usmm` (2 commits, 31 arquivos, 118 testes).

**Rota:** squad completo + high-stakes-gate (producao FARMA, transacao de
medicao de sistema em NSP/400).

### Placar gate x achado
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| datefmt com %f zerava o log detalhado em silencio | teste automatizado | teste (pegou) |
| salvaguarda de ambiente comparava mandante (inutil: NSD/NSQ/NSP = 400) | qa-critic adversarial | discovery/architect - premissa nao verificada |
| senha errada -> RedeError retentavel -> bloqueio de conta | agente de fidelidade | qa-critic (taxonomia de erro) |
| vigia de dialogos agia em sessoes/janelas alheias | qa-critic adversarial | architect - escopo de atuacao nao modelado pela allowlist |
| Excel: deteccao por PID novo falha com instancia unica | ambos os revisores | developer - premissa sobre o modelo COM do Excel |
| sendVKey sem argumento travado = furo na allowlist | agente de fidelidade | teste da allowlist (nao cobria) |
| teste de sha256 com assercao morta (del esperado) | qa-critic | code review |

### Deteccao: framework x humano
- Framework (mecanismo): o teste automatizado pegou o bug de datefmt **antes**
  de qualquer revisao humana - e era um bug que so se manifestaria em producao,
  invisivel (logging engole erro de formatacao e descarta o registro).
- Revisao adversarial (2 agentes, angulos distintos): pegou 6 achados
  criticos/altos que nenhum teste pegaria, porque eram **premissas erradas**,
  nao codigo errado. Rodar DOIS revisores com prompts diferentes (um por
  ceticismo, outro por fidelidade-a-fonte) teve retorno claro: os conjuntos de
  achados se sobrepuseram em apenas 2 de 11 itens.

### Licoes por skill (agnostico de dominio)
- **discovery:** verificar se a chave de discriminacao ESCOLHIDA consegue
  discriminar. Comparar mandante entre ambientes que compartilham o mandante e
  uma verificacao que nunca pode falhar - e nunca pode detectar.
- **architect:** allowlist por ID de controle nao modela ESCOPO (qual sessao,
  qual processo). IDs sao iguais em qualquer sessao; o escopo precisa de outra
  chave (session id, PID da imagem).
- **developer:** sleep fixo pedido pelo dono -> tratar como PISO e sondar por
  cima. Atende o requisito ao pe da letra e remove a classe de falha.
- **qa-critic:** procurar assercao morta (del esperado, ssert x != "") e
  divergencia doc-x-codigo. As duas sao invisiveis a suite verde.
- **docops:** documentar a proibicao numa lista que tem TESTE provando que cada
  item e negado - senao doc e codigo divergem sem nada acusar (defeito real
  observado no repo de referencia etl-ysve-monitor).

### Boas praticas reutilizaveis
- **Guarda default-deny com trilha:** embrulhar o objeto externo (COM/API) e
  expor so verbos nomeados que consultam allowlist antes de agir. Efeito
  colateral valioso: a trilha do que foi executado sai de graca e vira evidencia.
- **Ledger append-only encadeado por hash** como resposta a "como voce prova".
- **Commit antes de rodar agente adversarial** (memoria ja registrada) - e usar
  git commit -F arquivo em vez de here-string quando a mensagem tem aspas
  duplas: PS 5.1 quebra a passagem de argumentos para exe nativo.

---

## Sessao 2026-07-22 (bloco 2) - modularizacao + publicacao

**Natureza:** aplicacao do framework, nao desenvolvimento. Entregavel fora do
repo (write-isolation ADR-070).

### Placar gate x achado
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Variavel local sombreando modulo (AttributeError em producao) | o DONO, executando | teste do pipeline - inexistente |
| [sap].conexao obrigatorio contrariando a doc | teste novo do pipeline | teste (pegou, tarde) |
| Vazamento de dominio em docstring do toolkit | test_arquitetura (novo) | teste (pegou, 4 casos) |
| Substituicao sem fronteira corrompeu EXIT_TRANSPORTE | py_compile / teste | revisao do proprio autor |
| Ordem do mapa de anonimizacao (especifico depois de generico) | varredura_sensivel | o proprio gate (pegou) |
| Padrao UNC casando no MEIO do caminho | teste de discriminacao escrito na hora | o proprio gate (pegou parcial) |
| Arquivo espurio `acme` criado por backtick em shell | `git ls-files` na conferencia | memoria ja existente, nao aplicada |
| Encoding duplo em 5 .md (Get-Content/Set-Content PS 5.1) | varredura visual + od | memoria ja existente, nao aplicada |

### Deteccao: framework x humano
- **O dono pegou o bug mais grave.** Nenhum dos 160 testes exercitava
  `pipeline.executar()`, sob a premissa de que "precisa de SAP". Nao precisava:
  os caminhos de falha rapida nao chegam perto do SAP. Premissa errada sobre o
  que e testavel = lacuna que chega em producao.
- **Gates novos pegaram cedo:** `test_arquitetura.py` (4 vazamentos na primeira
  execucao) e `varredura_sensivel.py` (2 bugs reais no mapa de anonimizacao).
- **Duas memorias existiam e nao foram aplicadas** (backticks/arquivos espurios;
  encoding PS 5.1). Memoria escrita nao e memoria consultada.

### Licoes por skill
- **architect:** modularizar so vale se houver TESTE de arquitetura. Mover
  arquivos sem travar a direcao de dependencia produz separacao decorativa - o
  acoplamento volta na primeira pressa.
- **developer:** rename mecanico de modulo colide com variaveis locais de mesmo
  nome. Python nao avisa: o nome vira local a partir da primeira atribuicao.
  Depois de renomear modulo, procurar por variavel homonima.
- **qa-critic:** "precisa de ambiente externo" e quase sempre premissa
  preguicosa. Separe o caminho que precisa do que nao precisa e teste o segundo.
- **docops:** anonimizacao por substituicao exige ORDEM (especifico antes de
  generico) e FRONTEIRA de palavra. Um gate que acusa o proprio placeholder
  ensina o operador a ignora-lo - e ai ele ignora o achado real.
- **pmo:** revisao visual de anonimizacao falha em silencio; o revisor le o que
  espera ler. Gate automatizado com codigo de saida, sempre.

### Boas praticas reutilizaveis
- **Gerador determinístico da variante publica** com mapa como DADO, e varredura
  como gate de saida. Regerar produz sempre o mesmo resultado.
- **Faixa RFC 5737 (192.0.2.0/24)** para IP de exemplo, em vez de inventar 10.x
  que pode coincidir com a rede real de outra organizacao.
- **Teste cuja ancora e "nunca levanta"**: `executar()` devolve exit_code do
  contrato; AttributeError escapando e defeito de codigo por definicao.
- **Mensagem longa sempre via arquivo** (`-F`, `--body-file`). Inline quebra em
  bash (backtick) e em PS 5.1 (aspas duplas).

---

## Sessao 2026-07-22/23 (bloco 3) - ATD-36246 FEFO/FIFO + ADR-095 procedencia

**Natureza: DUPLA.** (a) framework APLICADO a um dominio (chamado SAP EWM em
farma regulado), entregavel fora do repo em pasta corporativa sincronizada;
(b) framework DESENVOLVIDO - o pedido do dono ao fim do (a) virou ADR-095 +
release v1.73.0. A parte (b) so existe porque a parte (a) expos a lacuna.

**Rota:** squad completo + high-stakes-gate (farma regulado, RDC 658/2022,
codigo que vai a producao SAP). Politica de modelo declarada pelo dono e
coincidente com model-policy.json: discovery/architect e QA final em Fable,
developer em Opus 4.8, qa-critic de juncao em Sonnet.

### Placar gate x achado
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| arquivo rotulado AS-IS era identico ao TO-BE (baseline original nunca preservado) | diff do orquestrador | traceability/file-first do ciclo anterior - nao rodou |
| relatorio do ciclo anterior afirmava ter adicionado guarda que ja existia no arquivo | diff | qa-critic do proprio ciclo (auto-aprovacao sem heterogeneidade) |
| analise AS-IS x TO-BE do ciclo anterior comparou o arquivo ja modificado consigo mesmo | diff | file-first - leu o arquivo errado como se fosse baseline |
| data de execucao de teste FABRICADA em matriz de rastreabilidade regulada | QA final adversarial (Fable) | confidence-classification - inferencia entregue como fato |
| resumo numerico da matriz nao batia com a propria tabela (5 PASS x 4 reais) | Fable | revisao propria antes de entregar |
| leitura do precedente de 2024 invertida: fonte diz "versao divergente", texto dizia "configuracao distinta" | Fable | anti-alucinacao na citacao de fonte |
| chave de agregacao ABAP sem CAT: fundiria estoque livre com bloqueado num unico saldo que decide alocacao | qa-critic (Sonnet) | developer - premissa nao verificada sobre granularidade da tabela |
| commonpath levanta ValueError em drive diferente/UNC - o caso de uso PRIMARIO do proprio ADR | qa-critic (Sonnet) | developer + canario - cenario-motivacao nunca testado |
| bypass da guarda dentro-do-repo por case-insensitivity do filesystem Windows | qa-critic (Sonnet) | idem |
| capability sem campo enforcement escapa da auditoria anti-teatro (P15) | qa-critic (Sonnet) | test_capabilities - campo e opcional |
| README 1.72.0 x CHANGELOG 1.73.0 | qa-critic (Sonnet) | NENHUM - nao existe canario para o par |
| ritual de release incompleto (qa-evidence, checkpoint, RRC) | canarios locais | pegou corretamente, fail-closed |

### Deteccao: framework x humano
- **Mecanismo pegou o ritual, nao o conteudo.** Os canarios de release
  (posture/qa-evidence/release-checkpoint/capabilities/marketing-claims)
  dispararam corretamente e fail-closed. Nenhum deles pegaria um dos 11
  achados de conteudo acima - nao e para isso que servem.
- **Todo achado substantivo veio de agente adversarial, nenhum de mecanismo.**
  Confirma o diagnostico do ADR-094: o coracao e o processo, nao o gate.
- **Escopos DIFERENTES rendem conjuntos DISJUNTOS.** Rodei dois revisores no
  mesmo pacote com escopos distintos - um "ataque este codigo", outro
  "verifique cada citacao contra a fonte". Sobreposicao entre os conjuntos de
  achados: ZERO. Modelo diferente e metade do valor; escopo diferente e a
  outra metade.
- **A 1a versao do meu proprio codigo crashava no cenario que meu proprio ADR
  declarava como motivacao.** Relendo o codigo eu nao acharia: os dois bugs
  criticos so aparecem EXECUTANDO. O revisor reproduziu ambos, e na 2a rodada
  criou uma junction Windows real para confirmar o caso que ele mesmo havia
  marcado como INFERIDO na 1a.

### Gaps (nao-bloqueantes, flagados)
- Nenhum canario compara README x topo do CHANGELOG (test_marketing_claims le
  a versao DO PROPRIO README, entao a divergencia passa verde). Registrado em
  history.md ## Em aberto com candidato secao 0: +1 assercao em
  test_consistency_closing.py, nao canario novo.
- 36 de 75 capabilities OMITEM enforcement e ficam invisiveis a auditoria de
  debito de mecanizacao - ponto cego de 48% num mecanismo anti-teatro.
  Registrado.

### Licoes por skill (agnostico de dominio)
- **discovery:** extracao deterministica (doc_intake) ANTES de afirmar
  qualquer coisa sobre documento binario. E declarar o limite: "vazio na
  extracao" NAO e "vazio no documento" - tabelas de .docx nao saem
  confiavelmente. Afirmar "a spec esta sem requisitos" com base em extracao e
  inferencia vestida de fato.
- **architect:** quando duas regras de uma spec COLIDEM, a spec e ambigua - o
  defeito nao e escolher o lado errado, e escolher em silencio. A ADR deve
  registrar a PRECEDENCIA e declarar que a leitura literal aponta para o outro
  lado, para quem ratifica decidir informado.
- **developer:** em artefato regulado, transformacao DETERMINISTICA (script com
  ancora unica + assert) em vez de transcrever centenas de linhas a mao.
  Transcricao manual e como se introduz erro em codigo que vai a producao.
- **qa-critic:** dar ESCOPOS diferentes a revisores diferentes. Mesmo escopo em
  dois modelos rende redundancia; escopos ortogonais rendem cobertura.
- **docops:** minuta nao assinada NAO entra em pasta de dossie regulado - la
  ela pode ser lida como registro valido. Marcar (banner no topo) E segregar
  (pasta propria). Vale para codigo tambem: arquivo .abap sem banner ao lado do
  oficial reproduz o vetor do acidente que a propria pasta documentava.
- **traceability:** a cadeia decisao->fonte->versao quebra no ponto em que o
  artefato SAI do repo. Foi essa observacao, no meio de um trabalho de dominio,
  que virou o ADR-095.

### Boas praticas reutilizaveis
- **Commit antes de agente adversarial** - confirmado de novo (memoria ja
  registrada). Fiz, e foi o que permitiu rodar qa-critic com Bash sem risco.
- **Bash tool NAO e PowerShell.** Usei here-string do PS (@'...'@) numa chamada
  Bash e o @ vazou para o ASSUNTO do commit. Corrigido com
  `git commit -F arquivo`. Regra: mensagem multi-linha SEMPRE via arquivo.
- **Heredoc bash quebra com apostrofo/barra invertida no conteudo.** Script
  Python longo -> escrever em arquivo e executar, nunca heredoc inline.
- **Insercao cirurgica em JSON preserva o diff.** Re-serializar
  capabilities.json com json.dumps gerou 43 insercoes + 26 delecoes de RUIDO
  (o arquivo usa estilo comma-first). Insercao por texto puro, respeitando o
  estilo do arquivo: 17 insercoes, 0 delecoes. Diff limpo e pre-requisito de
  revisao honesta.
- **Ler o modo de escrita do tool antes de rodar.** execution_report.py grava
  com "w" (sobrescreve), mas este arquivo e append-por-sessao e tinha 125
  linhas NAO-COMMITADAS de duas outras sessoes. Rodar o gerador as cegas teria
  destruido as duas. File-first vale para ferramenta, nao so para dado.
- **Gatilho pela FORMA da situacao, nao pelo nome do cliente.** O canario
  core-no-vendor forcou o desenho do ADR-095 a ser agnostico - e no fim ficou
  MELHOR: a regra vale para qualquer pasta externa e o caso concreto vira
  instancia, nao excecao. Constraint de arquitetura como forca de qualidade.
