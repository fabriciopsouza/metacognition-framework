# ADR-131 — Trabalhadores externos orquestrados: outra família por programa, portão de dado e trilha

- **Status:** Proposto (QA r3 aprovou com ressalvas; aguarda merge do dono)
- **Data:** 2026-10-25
- **Decisores:** dono (Fabricio), 24 e 25/10/2026, nas palavras dele:
  - "conseguiríamos gerenciar e orquestrar com o claude como autor principal, outras ias para trabalhar em tarefas de produção de código? Aproveitando as melhores características da tarefa e do llm?";
  - "testes, lentes seguindo regras, simulações de entrevistas (veja na documentação) e testes podem ser feitas com tokens mais baratos";
  - "recomendado para tudo" (respondendo às decisões de dado e de instalação, 25/10);
  - "e como faço para monitorar que tudo está funcionando, as etapas onde estão sendo executadas, logs de execução e rastreio, respostas, ainda que resumidas, como um caminho do trabalho, uma trilha de auditoria" e "o monitor visualmente impactante, porém barato, e informativo".

  Autoria: Opus 5.5.
- **Relação:**
  - preenche o degrau 1 da `heterogeneity_ladder` (ADR-018, ADR-078), que hoje só existia pelo hub de arquivos (ADR-069), operado à mão;
  - não muda o ADR-108: veredito de trabalhador externo não é veredito de qa-critic;
  - usa o registro de trabalhos (ADR-100) como índice da trilha, sem cópia;
  - estende `tools/model-policy.json` (ADR-078) com dado, sem código fixo.

## Contexto
1. O dono assina mais de um provedor e tem uma placa de vídeo que roda modelo local. A governança já dizia que a revisão ideal vem de família diferente do autor, mas o único caminho era o hub, que move arquivos entre sessões e depende de alguém colar o texto no outro lado.
2. A leitura dos cinco repositórios em 25/10 mostrou dois fatos que decidem o desenho:
   - nos projetos, os testes, as esteiras e as lentes de tela já são determinísticos; o espaço para modelo barato está só nos pontos de julgamento (pré-revisão, rascunho de teste, candidato a sabotagem, cliente simulado);
   - dois projetos guardam dado real de empresa e um deles tem a regra "dado da Natulab nunca vai a serviço externo"; nenhum documento dizia qual dado pode ir a qual provedor de IA.
3. Teste de 25/10: o `agy` (CLI do Antigravity) roda em modo plano com sandbox, aceita esquema de resposta e informa tokens. Ele não lê a entrada padrão como conteúdo, e nega o comando que o modelo tenta rodar para ler arquivo. O material grande só chega pela entrada em NDJSON (`{"event":"user","message":{"content":...}}`), documentada em `antigravity.google/docs/cli/headless/`.

## Decisão
1. **Executor único** `tools/trabalhador_externo.py`. Trabalhadores e classes de dado são dado em `model-policy.json` → `trabalhadores_externos`; o executor não nomeia modelo.
2. **Portão de dado fail-closed.** Cada repositório declara a própria classe em `.agent/classe-de-dado.json`, escrito pela sessão dele (write-isolation). Classes, do menos ao mais restrito: `publico`, `sintetico`, `empresa`. Sem declaração, ou com valor desconhecido ou arquivo corrompido, vale `empresa`. Trabalhador que sai da máquina nunca aceita `empresa` (invariante testada no dado).
3. **Só sai o que foi pedido.** O trabalhador roda numa pasta vazia e descartável. O conteúdo vai na mensagem, montado só com os arquivos passados por `--arquivo`, e cada um tem de estar dentro do repositório. O arquivo de pedido é resolvido uma vez, contra a pasta corrente, e só é aberto se estiver no repositório ou na pasta própria de pedidos (`%TEMP%\trab-pedidos`, ou `TRABALHADOR_PEDIDOS`), com teto de 20 KB, porque material vai por `--arquivo`; abre-se exatamente o caminho conferido. Trabalhador declarado local só fala com 127.0.0.1, ::1 ou localhost, e sem proxy do sistema.
4. **Saída validada e consultiva.** O esquema é conferido antes da chamada: palavra-chave fora do subconjunto suportado recusa o pedido, em vez de ser ignorada. Com esquema, resposta fora dele é `INVALIDO` (rc 4). Toda saída leva o aviso de que não substitui o qa-critic nem o veredito de junção.
5. **Trilha e monitor** (`tools/monitor_trabalhadores.py`):
   - uma linha por etapa em `~/.claude/estado/trabalhadores/registro.jsonl`, com trabalho, etapa, spec, quem, status, tokens, segundos, resumo de até 280 caracteres da resposta e o sha256 da mensagem; a mensagem enviada nunca é gravada;
   - a íntegra da resposta fica em `saidas/<id>.json`, local;
   - as etapas feitas dentro do Claude Code (autor, QA, merge) entram na mesma trilha pelo subcomando `evento`;
   - uma página HTML autônoma (`monitor.html`), regerada a cada chamada, sem servidor, sem rede e sem token: indicadores, consumo por trabalhador, linha do tempo por trabalho com resumo e link para a íntegra, filtro e recarga a cada 20 s. Texto de modelo é sempre escapado. Falha do monitor nunca derruba a chamada.
6. **Trabalhadores iniciais:** `gemini-pro` e `gemini-flash` (outra família, saem da máquina), `sonnet-agy` (mesma família do autor, cota de outro provedor, não conta como heterogeneidade) e `local-qwen` (não sai da máquina, único aceito em `empresa`).
7. **IDs de modelo** atualizados para a geração atual (fable 5.1, opus 5.5, sonnet 5.5, haiku 5.5), com o motivo registrado no próprio arquivo.

## Decisões do dono que este ADR registra e não aplica
- **Papéis por modelo (25/10):** "opus 5.5 qa / sonnet 5.5 em geral nesta linha de trabalho, eventualmente fable com qa opus". Isso inverte a invariante "autor sempre default" de 19/08 (autor Opus, 1º QA um degrau abaixo). Mudar `baseline_author` e a escada relativa é decisão de governança com efeito em todos os projetos; fica para o dono confirmar se a frase vale para todos ou só para esta linha de trabalho.
- **Classes dos projetos:** recomendação seguida pelo dono ("recomendado para tudo"): bi-saas `sintetico` (regra AD-21 do próprio repositório: só dado sintético ou base pública); agidesk-cockpit-sistemas e orcamento-natulab `empresa` (nomes reais versionados; NFR-02). Cada declaração é escrita pela sessão do próprio repositório.

## Régua §0
Porta (c) e ordem explícita do dono: destrava o degrau 1 da escada de heterogeneidade, que existia como regra sem mecanismo, editando a política existente em vez de criar outra. O monitor lê o registro de trabalhos que já existe em vez de criar índice próprio. Ganho de token: trabalho de volume e pré-revisão saem da cota da sessão; a trilha mede o quanto, para a decisão de manter ou cortar.

## Limites
- **O portão confia na declaração do repositório.** Uma declaração errada (`sintetico` num repositório com dado real) libera o envio. Mitigação: a declaração tem campo `origem` e é escrita pela sessão do repositório, com revisão.
- **O isolamento do `agy` é pela pasta de trabalho e pelo modo plano com sandbox.** Nos testes de 25/10 ele negou o comando que o modelo tentou rodar para ler arquivo, mas nenhum teste prova que uma ferramenta de leitura não alcança um caminho absoluto fora da pasta. Mitigação: o executor nunca cita caminho de repositório na mensagem; o conteúdo vai inline.
- **O encerramento da árvore de processos no tempo limite não tem teste automático**, porque exigiria um processo que gere netos presos. Ele é lido no código (`taskkill /T`) e cai em ERRO declarado.
- **Mutantes equivalentes declarados (QA r3):** três sabotagens sobrevivem porque uma segunda camada segura o mesmo caso: abrir o pedido pelo nome original (resolve contra a mesma pasta corrente) e tirar a checagem de tipo do esquema (a exceção vira recusa pelo `try` em volta). A QA r3 mostrou que resolver contra o repositório NÃO era equivalente; o canário agora fixa a resolução pela pasta corrente (A3).
- **Link criado de propósito:** junção e link simbólico são resolvidos por `realpath`; hardlink e pasta de pedidos redirecionada são recusados. Um link criado por quem já tem acesso ao disco continua sendo risco de quem o cria.
- **O resumo pode citar o conteúdo enviado.** A trilha e as saídas ficam só nesta máquina, fora de qualquer repositório; não são publicadas.
- **Qualidade do trabalhador barato não é garantida.** No teste de 25/10 o Flash errou uma contagem simples. Toda saída é conferida por execução (teste rodado, sabotagem que reprova) ou pela QA da governança.
- **Cota e limite do provedor externo não são medidos pelo provedor** neste ADR; só os tokens que a via informa.
- **Sem orquestrador automático de fila.** O orquestrador continua sendo a sessão do Claude Code; o executor é a mão dela.

## Prova
`tools/test_trabalhador_externo.py` (sem rede, vias falsas):
- sem declaração, classe desconhecida e arquivo corrompido recusam trabalhador que sai da máquina, sem chamada;
- `empresa` roda no local; `sintetico` roda no externo e a mensagem leva só o arquivo pedido;
- arquivo fora do repositório (`..` e caminho absoluto) é recusado;
- quatro respostas fora do esquema viram `INVALIDO`; a válida passa;
- exceção e status de falha da via viram `ERRO` declarado;
- o registro não guarda conteúdo, guarda sha256 e recusas; a íntegra fica em arquivo próprio e a trilha só no resumo;
- invariantes da política: via com executor, classes declaradas, nada que sai da máquina aceita `empresa`;
- monitor: texto de modelo escapado, etapa do Claude Code na trilha, status inválido recusado, linha corrompida avisada, falha do monitor não derruba a chamada.

Sabotagens provadas pelo autor em cópia (cada uma deixa o canário vermelho): portão desligado; trava de caminho desligada; validação de esquema desligada; mensagem gravada no registro.

Teste real de 25/10 (repositório sintético de teste): `gemini-flash` achou 4 defeitos em 15 s; `local-qwen` achou 1 em 10 s; o portão recusou o repositório sem declaração.

## Emenda — Codex revisor formal alternado (31/10/2026)

Decisão do dono, 30/10/2026, literal: "codex agora pode ser usado livremente, é que estava sem tokens, recarregou. ELE
PODE SER REVISOR formal, como sonnet, alternando com este e economizando tokens claude"; "gemini so pre revisao em geral
/ paralela ou revisao de itens simples". Pedido levado por bi-saas-85 (quadro de coordenação, 30/10/2026); reiterado
pelo dono em 31/10/2026 ("siga o recomendado"; "ja dei a ordem!!!"). Substitui "qa final SEMPRE CLAUDE" e "Codex só a
pedido" (26/10/2026).

1. **Trabalhador `codex`** em `tools/model-policy.json` (família openai, sai da máquina, aceita `publico` e `sintetico`,
   `revisor_formal: true`). Via nova `codex` no executor: `codex exec` com `--ignore-user-config`, `--ignore-rules`,
   `--ephemeral`, sandbox `read-only`, na pasta vazia, material pela entrada; resposta vazia é ERRO.
2. **Exceção ao item 4 da decisão:** a saída do trabalhador com `revisor_formal` é revisão formal que decide, com aviso
   próprio; os demais (Gemini incluído) continuam consultivos: pré-revisão, revisão paralela ou item simples.
3. **Alternância** (`revisao_alternada` na política): a 1ª revisão (junções e passo 1 do QA final) alterna por rodada,
   ímpar Codex, par Sonnet. Risco baixo e o momento 1 começam pelo Codex; o momento 3 começa pela família oposta à da
   última rodada do momento 1 (regra já aplicada no bi-saas, AGENTS.md, PR 196). Codex indisponível: Sonnet, declarado.
   A 2ª revisão não muda (degrau acima, só com autorização ativa).
4. **Atestação:** o veredito do Codex grava `atestacao.registro` (id da chamada na trilha) no lugar de `agentId`;
   `tools/squad_gate.py` aceita um ou outro, com a mesma exigência de modelo diferente do autor.
5. **Regra global, seção 1** (molde `.claude/global/CLAUDE-global.md` e arquivo instalado): a 1ª revisão admite o
   Codex alternado; Gemini só pré-revisão.
6. **Classe deste repositório:** `.agent/classe-de-dado.json` = `sintetico` (código próprio, sem dado de empresa pela
   regra de isolamento da seção 9 da regra global).

Limites: o veredito do Codex não tem a prova de transcrição de `tools/verify_qa_attestation.py` (a trilha local e o
`sha256` da mensagem fazem esse papel, sem verificação automática cruzada); o modelo usado é o padrão da conta no
codex-cli (`padrao-do-codex-cli`), sem nome fixo na política; a via não informa tokens. Prova: canários do executor
(linha de comando, pasta vazia, resposta vazia, classe empresa recusada) e do gate (registro aceito, vazio recusado);
chamada real em 31/10/2026, 4,1 s, resposta correta (trilha `20261031-094120-6c5738`).

## Estado do QA
| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 1 | qa-critic Opus 5.5 isolado | REPROVADO | 5 médios: pedido lido de qualquer pasta (porta lateral do portão); OLLAMA_URL apontava o local para outra máquina; validador ignorava palavra-chave desconhecida; type em lista quebrava depois da chamada, sem rastro; linha fora do formato congelava o monitor. 6 baixos: sabotagem inerte da mensagem nas íntegras e do escape de `quem`; link `javascript:` em spec inexistente; link sem codificação; arquivo inexistente com traceback; isolamento do agy e travamento por processo neto não declarados. 5 de 7 mutações mortas. | pedido só do repo ou temporário, teto de 20 KB; local só em loopback; esquema conferido antes e fail-closed, com additionalProperties, minItems, null e type em lista; validação dentro de try; monitor aceita só registro bem formado; links só para arquivo existente via `as_uri`; OSError vira RECUSADO; taskkill da árvore no tempo limite; limite do agy declarado; 9 casos novos no canário, 5 sabotagens novas mortas |
| 2 | qa-critic Opus 5.5 isolado (novo) | REPROVADO | 2 médios: pedido relativo conferido contra o repositório mas aberto pela pasta corrente (arquivo de repo empresa saía para repo sintético); HTTP_PROXY do sistema recebia a mensagem do modelo local. 5 baixos: esquema malformado com traceback antes do portão; recusa da linha de comando sem rastro; monitor texto quebrava com campo nulo; dois casos do canário não protegiam correções da r1; %TEMP% inteiro liberado para pedido. 8 de 11 mutações mortas. Recomendou nova rodada. | resolver o pedido uma vez e abrir o caminho conferido; pasta própria de pedidos; via local sem proxy; tipo de cada palavra-chave conferido e checagem dentro de try; recusa da linha de comando registrada; campo nulo no texto; 7 casos novos; 6 sabotagens novas (3 mortas, 3 equivalentes declaradas). Rodada além da 2ª reprovação pela regra do dono de 25/10 (seguir a recomendada da QA, registrar no PR). |
| 3 | qa-critic Opus 5.5 isolado (novo) | APROVADO COM RESSALVAS | N1 e N2 resistiram a junção, `..`, UNC, prefixo `\\?\`, caixa, ADS e a 12 combinações de proxy. 8 baixos: resposta ou esquema aninhado profundo davam traceback sem rastro; um mutante declarado equivalente não era (resolução pela pasta corrente sem canário); junção e hardlink sem canário; canário herdava a pasta de pedidos do ambiente; hardlink e pasta de pedidos redirecionada aceitos; tabulação no texto do ADR; checagem de link nunca disparava. 7 de 13 mutações mortas, nenhum vazamento no código. | gravação da íntegra protegida; RecursionError no esquema vira recusa; hardlink e pasta de pedidos redirecionada recusados; canário fixa a pasta de pedidos e ganha casos de pasta corrente, junção e hardlink; checagem de link corrigida; texto do ADR corrigido; 4 sabotagens novas, todas mortas. Ressalva baixa não abre rodada nova (régua). |
