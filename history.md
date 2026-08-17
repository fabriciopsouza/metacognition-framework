# history.md — Registro append-only do framework

> Single-writer = orquestrador (PMO). Checkpoints append-only, **mais-novo-primeiro** (o estado
> atual é o checkpoint do TOPO; `## Em aberto` é WIP mutável; `## Aprendizado` append-only no fim).
> Formalizado pelo ADR-007 (v1.9.0); boot lê o checkpoint do topo via `AGENT-FRAMEWORK.md` §2.B.
>
> 3 seções: histórico cronológico de checkpoints (formato em `.agent/workflows/checkpoint.md`),
> `## Em aberto` (WIP — ex-G11), `## Aprendizado` (fracassos — ex-G9, com firewall).

---

<!-- history-archive-pointer -->
> **Poda de contexto (ADR-107):** este arquivo quente mantem os ultimos **10** checkpoints + `## Em aberto` + `## Aprendizado`. **56** checkpoints mais antigos estao em [`docs/history/history-archive.md`](docs/history/history-archive.md) (nada deletado — so realocado). Rotacao: `python tools/rotate_history.py`.
<!-- history-archive-pointer -->

## 2026-08-17 — Release v1.87.0 (MINOR): o silêncio das distribuições vira número (ADR-049)

Fecha o único ponto de falha silencioso que restava. As cinco distribuições são geradas do
canônico por um workflow do GitHub Actions; quando ele esteve desligado por billing, elas
**congelaram por vinte releases sem nenhum alarme**, e a deriva só apareceu quando alguém foi
olhar à mão, meses depois. O workflow voltou a funcionar — medido nesta sessão —, mas o risco é
estrutural: se cair de novo, o silêncio volta igual.

`tools/shadow_drift.py` mede a distância em commits, lendo o SHA que o próprio workflow grava na
mensagem de publicação de cada distribuição. Melhor que comparar versão: pega também o caso em que
o export rodou e falhou no meio.

**A decisão que mais importa:** sem rede ou sem credencial, ele declara `SKIP` e diz por quê, em
vez de reportar "em dia". Foi exatamente assim que a deriva passou despercebida da primeira vez —
ausência de medição lida como aprovação. O canário protege essa propriedade de forma explícita: se
o `SKIP` virar aprovação, ele fica vermelho. E não reprova por falta de internet, porque
verificador que trava offline é desligado na primeira viagem.

**O canário de vitrine funcionou como projetado, na mesma sessão em que nasceu.** Ao registrar a
capacidade nova, os números da página ficaram defasados e a suíte caiu na hora. Corrigi e passou.
É a primeira vez que o mecanismo cobra o próprio autor.

**Próximo passo:** o passivo — dezessete capacidades que declaram bloquear falha e nunca foram
provadas, e trinta e quatro que não declaram como se protegem. Volume, com método já validado em
doze migrações.

## 2026-08-17 — Release v1.86.0 (MINOR): a vitrine promete menos, prova mais, e não pode mais envelhecer mentindo

**Correção de premissa antes do trabalho.** O dono pediu para atualizar todas as distribuições
relacionadas, dizendo que deveria ser automático. Eu tinha registrado que as cinco sombras estavam
congeladas porque o GitHub Actions morreu por billing — **fui medir e não é mais verdade**. O
workflow rodou três vezes no dia, todas com sucesso; as cinco estão no commit da v1.85.0, com as
ferramentas novas presentes e o cofre `docs/_private/` ausente (404). Já era automático e já tinha
funcionado. A memória foi corrigida, porque teria feito a próxima sessão refazer trabalho
desnecessário. **O ponto único de falha continua real:** se o Actions cair de novo, as sombras
envelhecem sem alarme — não existe canário comparando a versão delas com a do canônico. Candidato
a próximo bloco.

**A vitrine.** Ela já era boa, e a parte difícil ela acertava: tinha uma seção sobre o que os gates
**não** resolvem, coisa que quase ninguém escreve. O defeito era outro — prometia em adjetivos onde
podia provar em número. A abertura empilhava quatro promessas não-verificáveis; virou uma ideia só,
*onde verde significa alguma coisa*, que é a tese real do repositório.

Seção nova com os dois lados no mesmo destaque visual: o verificado (38 de 89 provadas, 77
canários, zero pendências) e o não-verificado (51 desconhecidas, o teto de auto-atestação, o que
não se mecaniza). Sem exagero e sem o inverso — modéstia performática é sicofância ao contrário.

**O mecanismo que impede a página de virar propaganda.** Número em site de divulgação envelhece
calado, e propaganda desmentida pelo próprio repositório é pior que número nenhum. O canário de
vitrine passa a derivar os três números das mesmas fontes que o auditor usa e a exigir que a página
os afirme. Provado plantando um número falso: fica vermelho.

**Próximo passo:** o passivo de 51 capacidades — volume, não descoberta. E, como candidato de menor
esforço e bom retorno, o canário de deriva das sombras: comparar a versão publicada em cada uma
com a do canônico, para que o ponto único de falha deixe de ser silencioso.

## 2026-08-16 — Release v1.85.0 (MINOR): quadro de gestão que não envelhece, e dois canários que mentiam passam a cobrir o que prometem (ADR-102)

**Documentação de gestão derivada, não digitada.** `tools/projeto_docs.py` monta backlog,
cronograma e status report a partir do que está aberto de fato — `## Em aberto`, ADRs em
`Proposto`, o passivo medido, o CHANGELOG e o git. Na primeira execução cobrou uma dívida minha:
um item listado como pendente que eu havia **entregue na release anterior** e esquecido de riscar.
É exatamente o que quadro manual faz, e por isso ele não é manual. Sai em CSV que importa direto
no Trello e no Planner; o `CONTEXTO.md` (objetivo, visão, quem é afetado, o que está em jogo) é o
único escrito à mão, porque nenhum dado revela propósito.

**O crítico reprovou com dois achados altos, e o primeiro foi contra o meu canário.** O caso "nota
de higiene não vira item" passava **por vácuo**: a fixture punha a nota antes do primeiro item,
onde o parser a descarta por outro motivo — sabotar a proteção não deixava o teste vermelho. O
segundo: os nove sub-itens de "Backlog ativo" colapsavam num card só, e como o verificador
comparava apenas títulos, acrescentar trabalho novo não mudava nada e o CSV velho seguia dado como
em dia. Corrigidos: sub-item virou card próprio (6 → 15), e a verificação passou a comparar os CSV
byte a byte. Mais dois: o verificador rodava a suíte inteira sob timeout menor que a própria
duração — **fail-open por relógio** —, e o `---` de fim de seção entrava no detalhe.

**Os dois canários que não cobriam o que prometiam, consertados aqui e não empurrados.** O
`test_qa_evidence` **redefinia** a constante que deveria guardar, em vez de importá-la do
mecanismo: tinha a própria cópia da regra e por isso não dependia do código — sabotar
`qa_evidence.py` não o afetava. Teste que duplica a regra confirma a si mesmo. E o
`test_post_canary_status` não cobria o **nome do status publicado**, que é o único elo entre o
script e a proteção da branch: trocar a constante travaria todo PR para sempre, em silêncio. Os
dois agora falham quando devem, provado por sabotagem.

**Documentação alinhada virou mecanismo:** o canário de consistência passa a exigir que todo
`tools/*.py` citado nos guias exista. Guia que manda rodar ferramenta inexistente é pior que guia
ausente — quem segue descobre errando e passa a desconfiar do resto. Varredura atual: zero
ponteiros mortos.

**Lição cross-IA publicada** em `docs/_private/cross-ai/outbox/`: nove defeitos em mecanismos de
garantia, todos reproduzidos nesta sessão, com o cenário que expõe cada um. Oito dos nove estavam
dentro de mecanismos construídos para garantir alguma coisa.

**Próximo passo:** o passivo de 54 capacidades sem prova. É volume, não descoberta — o método está
validado em onze migrações e o instrumento foi consertado três vezes até parar de mentir. Critério
de aceite por lote: cada capacidade só entra no registro depois de `--provar` verde, e quem não
passar vira dívida nomeada com o canário a consertar, nunca prova forçada.

## 2026-08-16 — Release v1.84.0 (MINOR): "o processo foi seguido?" deixa de ser opinião e vira número (ADR-097 Aceito)

Fecha o **último ADR em `Proposto`**. Ele nasceu de uma frase sua em 23/06 — *"onde sou advisory
dá pra ficar hard?"* — e trazia um critério de aceite escrito por ele mesmo: *"sem isso há intenção
de HARD, não HARD"*.

**As três pendências.** O ledger virou event log: `status` explícito (antes o sucesso era
implícito e o rewind ficava invisível), `resource` e `prova` — ponteiro que resolve, recusado na
escrita se não resolver. O fluxo J0–J6 virou modelo versionado. E `tools/conformance.py` compara
executado contra desenhado, devolvendo fitness e violações nomeadas por regra.

**Na primeira execução sobre o ledger real:** 6 blocos, um com **fitness 0.0** — a junção final
registrada sem nenhuma anterior. Estava lá desde sempre; ninguém tinha como ver.

**O crítico reprovou minha primeira versão com o pior achado possível para este mecanismo.** A
flag `rewind: true` sozinha desligava as duas checagens de topologia, em qualquer direção — um
bloco com um único registro, a junção final com a flag pendurada, devolvia fitness 1.0 e zero
violações. "Processo completo e conforme" sem ter passado por etapa alguma. O verificador criado
para provar que o processo foi seguido aprovava o inverso. Mais três: `status` inventado passava
silencioso, trace vazio valia 1.0, e o meu próprio canário usava `CLAUDE.md` como prova das oito
junções — **demonstrando o buraco que eu não tinha declarado**.

**Padrão que se repete e vale registrar:** das nove rodadas adversariais desta sessão, cinco
reprovaram, e em quatro delas o defeito estava no mecanismo *criado para impedir aquele mesmo tipo
de defeito*. Não é coincidência — é o que acontece quando se escreve a régua e se mede com ela na
mesma sessão.

**Próximo passo:** o documento cross-IA de aprendizado com erros, e a varredura de alinhamento dos
demais guias contra o estado real. Nenhum ADR permanece em `Proposto`.

## 2026-08-16 — Release v1.83.0 (MINOR): "NÃO SEI" só vale depois de busca provada, e a instalação passa a se verificar (ADR-092 fechado)

Fecha a última peça do ADR-092 e responde ao pedido do dono de um runbook que permita instalar em
qualquer máquina sem erros.

**A peça que faltava era a que não tinha saída.** O manifesto declara dois comportamentos cujo
campo `check` aponta para `tools/research_evidence.py` — e a ferramenta nunca existiu. O
`squad_gate.py` devolvia "falta" fixo para esse papel: fail-closed correto, e **sem nenhum caminho
para passar**. Quem tocasse num número regulado ficava barrado para sempre. Gate sem caminho de
saída não é rigor, é bloqueio.

Dois caminhos agora, e o segundo é tão legítimo quanto o primeiro: **pesquisa** com ao menos dois
domínios distintos, cada fonte com endereço, hash do que foi lido e data de vigência conferida; ou
**ratificação humana**, o campo `ratificado_por`. Há número que não está em fonte nenhuma e alguém
assume. O que não se aceita é o silêncio. A fraude central que o canário barra: citar o mesmo
domínio duas vezes e chamar de triangulação.

**A instalação passa a dizer se funciona.** O `--check` do bootstrap respondia duas perguntas e
chamava aquilo de diagnóstico; quem clonava em outra máquina descobria o que faltava errando, um
erro por vez. Agora separa o que impede de operar do que só reduz garantia, cada pendência vem com
o comando que a resolve, e no fim **roda um canário de verdade** — instalação que não executa o
próprio portão não está instalada. Baixar o `.zip` virou bloqueio explícito: sem histórico do git,
vários portões não falham, passam mentindo.

**Nenhum documento novo foi criado.** Já existiam três guias de instalação; o runbook virou a
primeira seção do `SETUP.md`, que era o mais próximo disso e não mencionava verificação nenhuma.
Régua §0 respeitada por fusão, não por adição.

**Próximo passo:** o ADR-097, único ainda em `Proposto`. Medido: `tools/conformance.py` não existe
e o ledger não tem os campos `resource` e `status`. Critério de aceite escrito por ele mesmo —
*"sem isso há intenção de rigor, não rigor"*.

## 2026-08-16 — Release v1.82.0 (MINOR): o gate do squad passa a rodar sozinho — a quarta peça do ADR-092, que nunca foi escrita (ADR-092 Aceito)

O dono mandou implementar os ADRs 092 e 097. A primeira coisa foi medir, não codar: **o 092 já
estava 60% pronto** desde junho. A matriz declarativa de quais papéis são obrigatórios por tipo de
mudança existia, o gate que a lê existia, o canário dele existia. **A quarta peça — o instalador
do gancho — nunca foi escrita**, e era justamente a que faz as outras rodarem sem alguém pedir.

Medido antes de escrever: `.git/hooks/pre-commit` não existia neste repositório, e na integração
contínua o gate roda com `|| echo "::warning::"`. Construído e desligado — a falha mais repetida
deste repo, agora na sua terceira aparição nesta mesma sessão (o gate de consistência do ADR-030
e o cache de bytecode foram as outras duas).

**Quatro decisões para o gancho não virar o gancho que alguém desinstala:** bloqueia só quando o
gate diz que falta evidência (ferramenta quebrada libera o commit); a saída de emergência
`--no-verify` é declarada no próprio texto do bloqueio; recusa sobrescrever gancho alheio; e
respeita `core.hooksPath`, porque instalar onde o git não lê dá falsa sensação de proteção.

Instalado e exercitado aqui — era o item 4 das pendências do próprio ADR. Com isso o **ADR-092
passa a Aceito**, com uma pendência remanescente declarada: `tools/research_evidence.py`.

**O ADR-097, ao contrário, é trabalho real e não começou.** Medido: `tools/conformance.py` não
existe e o ledger não tem os campos `resource` e `status` que ele exige. As três pendências
listadas no próprio documento continuam abertas.

**Próximo passo:** implementar o ADR-097. Critério de aceite escrito por ele mesmo:
`tools/conformance.py` + canário rodando verde na suíte — *"sem isso há intenção de rigor, não
rigor"*. Pré-requisito: estender o schema do ledger com `resource` e `status`, e escrever o modelo
formal das junções J0–J6, que é o que o verificador compara contra o executado.

## 2026-08-16 — Release v1.81.0 (MINOR): rotação determinística do `history.md` — a branch de dois meses entra sem levar junto uma colisão de numeração (ADR-107)

Bloco de **desencalhe**, não de invenção. O trabalho existia desde 20/06 numa branch aberta em
24/06 e nunca revisada: `tools/rotate_history.py` mantém quentes os últimos N checkpoints mais as
seções `## Em aberto` e `## Aprendizado` inteiras, e move os antigos para
`docs/history/history-archive.md`. Nada some, e rodar duas vezes não muda o resultado.

**O que quase entrou junto.** O ADR chegava numerado como **092**, e a `main` já usa esse número
para a camada de enforcement do squad. Mergear assim criaria **dois ADRs com o mesmo número** —
exatamente a dimensão de duplicata que o gate de consistência, cabeado nesta mesma sessão, acabou
de ganhar. Renumerado para **107**, com as referências corrigidas no documento, na ferramenta, no
arquivo frio e no registro de QA da época. A colisão foi detectada por leitura antes do merge, não
pelo gate — o gate teria pego depois, o que já é melhor do que ninguém pegar.

**Dois meses de divergência.** A branch tocava README, CHANGELOG, registro de capacidades e os
seis pacotes web, todos alterados desde então. Reconciliado por **merge** e não rebase — force-push
segue negado por regra da máquina, e rebase orfanaria vereditos de QA. Arquivos gerados resolvidos
na versão da `main` e regenerados a partir do dado, nunca editados à mão.

**Também nesta sessão, fora do bloco:** as quatro tags de release ausentes desde 02/06 foram
criadas e publicadas (v1.76.0, v1.77.0, v1.79.0, v1.80.0), fechando o achado F2 do handoff de
07/08; o PR #116 foi fechado porque dois dos três achados dele já não existiam; e o recibo do gate
de fechamento, que eu criara sem entrada no `.gitignore`, parou de sujar a árvore a cada sessão.

**Próximo passo:** implementar o ADR-092 (manifesto de comportamento com portão automático) e o
ADR-097 (medir executado × desenhado), ambos ratificados pelo dono nesta sessão. Critério de
aceite do 097 está escrito no próprio documento: `tools/conformance.py` verde na suíte — *"sem
isso há intenção de rigor, não rigor"*.

## 2026-08-16 — Release v1.80.1 (PATCH): a prova de mutação não provava — três defeitos no auditor recém-nascido (ADR-106, emendas 2 e 3)

O dono abriu a sessão pedindo sete coisas do framework: gates e canários que sejam reais e não
vazios; determinismo onde hoje só há prosa; comunicação direta e sem jargão interno; documentação
ágil de projeto com status report; que tudo se atualize sem cobrança humana; e que o framework
critique tudo o que ele pedir, **inclusive ele mesmo** — *"não deve e NÃO PODE ser passivo"*.

**A crítica veio antes do plano.** Um crítico independente (Fable) cruzou os sete pedidos com o
que o framework já decidiu em meses. Resultado que mudou a ordem de ataque: os pedidos 1 e 2 são
**a mesma ação** e o mecanismo foi aceito dois dias antes (ADR-106) — falta quitar, não inventar.
O pedido 5 **colide** com a dívida do ADR-102, cuja condição de quitação é aplicar o padrão num
segundo projeto antes de promovê-lo. E quatro dos sete repetem tentativas já registradas no
`## Aprendizado` como fracassos. Decisões do dono: começar por 1+2, CSV antes de xlsx, adiar o 5.

**Correção de premissa, medida ao vivo:** hooks **Python funcionam** nesta máquina — um deles
disparou durante a auditoria. O que quebra é menor e consertável: o gate de consistência não está
ligado a evento nenhum e não existe hook de fim de sessão. O pedido 6 não depende do antivírus.

**Três defeitos no auditor, cada um a classe que ele existe para impedir.** Os dois primeiros
vieram do qa-critic Sonnet, que **reprovou**: crash em mecanismo `.json` escapava da recusa
(o traceback do `JSONDecodeError` nunca cita o arquivo de dados, e `model-policy` é exatamente
isso), e `mutacao.espera` aceitava curinga tipo `"Error"`. O terceiro apareceu na própria
migração: a prova era **anulável por cache de bytecode**. Sabotagem que preserva o tamanho do
arquivo e cai no mesmo segundo faz o Python rodar o bytecode velho — o canário fica verde e o
auditor conclui "não prova nada" sobre código que nunca executou. Intermitente, portanto pior que
ausente. Provado congelando o `mtime`: cache ligado → verde; desligado → vermelho.

**Um quarto defeito foi contra o próprio trabalho.** O caso de teste novo do mecanismo `.json`
passava **pelo motivo errado**: o traceback imprime a linha de código, e a fixture tinha o literal
`dados.json` escrito nela. Só apareceu porque cada guarda foi sabotada para conferir se sabia
ficar vermelha — a guarda que não mudou de cor denunciou o teste, não o código.

**Entregue:** 22 → 28 verificações, cada guarda nova vista reprovando antes de valer; passivo
57 → 54, com `risk-gate`, `rules-parity-guard` e `autonomy-retry-policy` migradas sob a regra do
segundo crítico (só entra no registro depois de `--provar` verde). `byo-ci-gate` e
`qa-evidence-gate` ficaram de fora: seus canários **não cobrem** os caminhos sabotados — dívida
nomeada, não prova forçada.

**O achado colateral foi fechado na mesma sessão (emenda 4).** O cache afetava a suíte inteira, e
o executor que decide PASS/FAIL dos 67 canários **não tinha canário próprio** — quem governa a
suíte não era governado por ninguém. **Duas correções minhas foram reprovadas pelo canário novo
antes de a terceira valer:** proibir a escrita de bytecode não impede a *leitura* de um arquivo
compilado que já exista (era a suspeita do crítico, confirmada por execução); proibir escrita e
apontar o cache para um diretório vazio funcionou e levou a suíte de 72s para mais de dois
minutos, porque cada subprocesso recompilava a biblioteca padrão inteira. A que ficou: diretório
novo por execução, com escrita liberada — 72s → 76s. O canário também se corrigiu: passava
sozinho e reprovava dentro da suíte, porque herdava o ambiente já corrigido e media o chamador em
vez do código. E a sabotagem declarada da capacidade nova era **neutralizada pelo próprio
auditor**, que define a variável de ambiente que ela lia.

**4ª rodada (Fable) aprovou sem ressalvas de código**, depois de refazer a sabotagem por conta
própria e derrubar o ataque mais promissor por varredura: nenhum canário escreve `.py` sob a raiz
do repositório, então o prefixo compartilhado não reabre o defeito entre canários.

**Próximo passo:** item 6 dos sete pedidos — ligar o fechamento automático a um evento real. Os
hooks Python **funcionam** nesta máquina (medido ao vivo), mas o gate de consistência não está
ligado a evento nenhum e não existe hook de fim de sessão. Critério de aceite: fechar uma sessão
sem pedir nada e o `history.md`, o registro de trabalhos e o status report saírem atualizados,
com canário de release como lei para quando o hook não disparar.

## 2026-08-14 — Release v1.80.0 (MINOR): prova de mutação para capacidade `fail-closed` — verde só conta depois de saber ficar vermelho (ADR-106)

Bloco nascido **fora** do framework. O dono mandou auditar um gate de status de projeto no
repositório `agente-copilot-studio` com uma pergunta seca: *"é real ou hardcodado? funciona
de verdade ou engana?"*. O teste que sustentava aquele gate anunciava **9/9 verificações
passaram**. Apagada **toda** a lógica de detecção do gate, o teste continuou **9/9** — porque
conferia só `código de saída ≠ 0` e outra checagem já derrubava o processo. Crítico
independente reproduziu.

**O que isso expôs aqui dentro.** A mesma classe já tinha acontecido duas vezes: ADR-096
achado A2 (canário aferia só o `returncode`; a mutação que removia o campo **passava**) e
v1.79.0 (canário fazia *monkeypatch da própria função* que deveria testar). E o ADR-096
registra, com todas as letras, *"provado por mutação"* — **a técnica já existia, funcionou,
achou defeito real, e nunca virou exigência.** Dívida de institucionalização, não de invenção.

Passivo medido antes da emenda: **80 capacidades · 35 sem nenhum campo `enforcement` · 22
`fail-closed` que ninguém jamais sabotou para conferir · zero auditores**. O ADR-015 se chama
"enforcement executável" e era, ele próprio, prosa não verificada.

**Entregue:** `tools/audit_enforcement.py` — capacidade `fail-closed` declara a mutação que
faz o canário dela falhar, em campos executáveis; `--provar` aplica num worktree isolado e
**exige vermelho**. Recusa seis formas de fraude, cada uma com caso de teste nomeado. Decisão
do dono sobre escopo: **(a) fail-closed para capacidade nova · (b) advisory para o passivo**,
congelado e **pinado por sha256**. Mais a rule **#12** do `qa-critic` e
`tools/test_audit_enforcement.py` (**19 verificações**), que roda o auditor contra o
`capabilities.json` **real** — é essa chamada que faz do modo (a) um gate de CI e não um
script que alguém precisa lembrar de rodar.

**Três rodadas adversariais: `reprovar` → `corrigir` → `aprovar`.** Os dois bloqueantes da
rodada 1 foram contra o **texto**, não contra o código: (i) o ADR afirmava que as três fraudes
tinham *"cada uma seu caso de teste"* e **uma não tinha** — o crítico sabotou justamente essa
checagem e o canário seguiu verde; (ii) nada chamava o auditor contra o estado real. A rodada 2
achou o cross-check `mutacao` × `mechanism`/`test` sendo **opt-in**: bastava omitir os campos
para a proteção sumir em silêncio. Afirmação antes da verificação, no documento que institui a
norma contra isso — registrado no ADR porque é a melhor evidência de que a norma é necessária.

**Régua §0:** adição pura, sem porta (a)/(b)/(c). Segue por **override explícito do dono**, com
condição de quitação escrita: migrar o passivo. **Não mecanizado, declarado:** coerência entre
o adjetivo do índice e o campo `enforcement`.

**Próximo passo:** migrar o passivo das 57 capacidades, começando por `handoff-generator` — cada uma ganha `mutacao` provada ou é rebaixada ao `enforcement` que de fato tem; é a condição que quita o override da régua §0. (Campo em UMA linha de propósito: o extrator do P14 trunca na quebra, medido em 14/08 — pendência #1, decisão do dono.)

## 2026-08-13 — Release v1.79.0 (MINOR): padrão documental de projeto; matriz de revisão ampliada; ativação do gate desacoplada (ADR-102, ADR-103, ADR-104)

Bloco nascido de uma **falha do próprio agente**, não de um pedido. Ao fechar a entrega
anterior, a sessão declarou: *"revisão adversarial por modelo diferente do autor não foi
feita"*. O dono perguntou o óbvio — **por que não?** — e a resposta expôs dois problemas
distintos, um de comportamento e um de mecanismo.

**O de comportamento:** o agente resolveu um conflito entre uma restrição de harness e a
regra do projeto **escolhendo declarar em vez de pular em silêncio** — o que é correto — mas
surfou a lacuna **no fim do relato**, não no momento. Declarar tarde não é surface-and-reconcile;
é aviso post-mortem. Quem lê descobre que o gate ficou aberto quando já não pode decidir.

**O de mecanismo, medido:** `behaviors/manifest.json` exigia `qa_critic` para `.py` e
`docs/adr/` e **para mais nada de comportamento**. Rodando o gate nos paths do commit:
`papeis exigidos: nenhum`. Alterar uma linha de código exigia revisão adversarial;
**reescrever a skill que governa toda sessão futura não exigia nada.** E o `squad_gate`,
construído no ADR-092 e testado a cada rodada de canário, estava **desligado** por decisão
registrada no ADR-094 — que escrevera a condição de ativação: *"se o dono concluir que
advisory+reforço ainda não bastam"*. Não bastaram. Este bloco é o caso empírico.

**Entregue:** `_shared/project-docs/SKILL.md` (ADR-102) — padrão do conjunto documental de
projeto, em **propriedades** e não em lista de arquivos, com conjunto **graduado por porte**
para não virar burocracia em projeto pequeno. Base da régua §0: **override explícito do dono**,
com condição de quitação escrita; nenhuma das portas (a)/(b)/(c) foi alegada, porque alegá-las
seria a racionalização que o ADR-099 cometeu. E a **matriz ampliada** para `_shared/`,
`.agent/skills/`, `.agent/rules/`, a própria matriz e os roteadores da raiz — usando `prefix`,
já suportado, **sem tocar no código do gate**.

**O `squad_gate` chegou a ser ATIVADO como bloqueio (ADR-103) e foi DESACOPLADO na mesma sessão
(ADR-104).** Três rodadas de revisão reprovaram, e a distribuição dos achados decidiu: 1ª rodada
6 achados, todos no padrão documental; 2ª rodada 6, **todos na ativação**; 3ª rodada 4, **todos na
ativação e zero no padrão**. A norma estava pronta e reprovando por defeito que não era dela. O
dono aplicou a regra de escalonamento e mandou separar: o CI voltou a `continue-on-error: true`
— **avalia e avisa, não barra** — e o endurecimento ficou preservado na branch
`feat/adr-103-squad-gate-endurecimento`, com a condição de reativação escrita no ADR-104.
Permanecem entregues, porque não dependem da ativação: a matriz, o `escopo_paths` obrigatório na
evidência, o match ancorado de versão, a cobertura de teste do gate (eram 8; conte com
`pytest tools/test_squad_gate.py -q`) e o canário de integridade.

**QA heterogêneo (Sonnet isolado, ≠ autor Opus) — 1ª rodada REPROVOU: 2 bloqueantes, 1 grave,
2 médios, 1 menor.** O mais instrutivo: o registro em `capabilities.json` nasceu
`PROVIDES/enforcement:manual` apontando um canário que só valida a integridade do próprio
registro — **reincidência do achado A2 do ADR-099**, poucos dias depois de corrigido no mesmo
repositório. Corrigido para `PARTIAL/prose`, seguindo o precedente. O 2º bloqueante era uma
frase com poder de barrar release inserida no `docops` **sem nenhum mecanismo por trás** —
rebaixada para advisory, porque gate sem canário é o teatro que o ADR-085/P15 proíbe.

**Débito quitado de tabela:** o F1 dos débitos de fechamento do v1.77.0 — `history.md` fora de
ordem, com o bloco de 08-03 abaixo do de 08-02, corrompendo em silêncio o "próximo passo" que
o `handoff.py` extrai por posição. Reordenado nesta entrega.

**Próximo passo:** decidir o desenho da extração de campo do `handoff.py` — 6 defeitos consecutivos na mesma regex provaram que enumerar fronteira de campo em prosa livre é problema ilimitado; as opções são impor campo em linha própria (lint) ou trocar por parser linha-a-linha. Critério de aceite: o P14 extrai o campo inteiro em todos os 63 checkpoints do corpus, verificado por detector genérico, sem lista de vocabulário.

**Lição, e ela é maior que o bloco:** capacidade construída e não aplicada é indistinguível de
capacidade ausente. O gate certo existia, testado, há semanas — e não impediu nada. O índice de
capacidades ainda a exibia como `PROVIDES`. `status` tem que descrever o que está **aplicado**,
não o que está **disponível**.

---

## 2026-08-03 — Release v1.77.0 (MINOR): o handoff sobrevive à sessão e é oferecido até ser tratado (ADR-100)

Bloco nascido de um pedido preciso do dono ao fim de uma validação real: *"o handoff não deve ser perdido se eu iniciar os trabalhos, mas deve ser oferecido até que eu trate o assunto"* — organizado **por trabalho**, com objetivo, resumo do feito e pendências.

**O gap era real e foi observado na própria sessão.** O Pacote P14 (ADR-012) e seu gerador determinístico (ADR-076) resolvem **o que o handoff contém**; nada resolvia **o que acontece com ele depois**. Era gerado, exibido no chat e **perdido**. Um trabalho de validação com 2,88 milhões de comparações, 17 objetos pendentes e três decisões esperando o dono terminaria sem nenhum mecanismo que o trouxesse de volta — dependeria de memória humana.

**Entregue:** `tools/trabalhos.py` — registro persistente em `~/.claude/trabalhos/<slug>.md`, **fora do repositório de propósito**, porque um trabalho pode envolver vários repositórios (o caso de origem envolve dois) e não pode depender de qual pasta foi aberta. Ciclo `aberto` → `tratado`; **só o dono encerra**, porque quem executa não decide que a pendência do dono acabou. Gate `trabalhos-abertos` no `boot_check` — **nunca falha o boot** (trabalho pendente é informação, não erro) e **nunca fica silencioso** ("nenhum aberto" é resultado declarado). Passo 3.5 no `start-session` obriga o agente a **mencionar na abertura**: registro que existe e não é oferecido é igual a não existir, que é exatamente a falha corrigida.

**Anti-reinvenção respeitada (ADR-072):** o índice de capacidades foi consultado ANTES de projetar. Existiam `handoff-generator` (P14) e o boot-scan cross-IA — o primeiro é efêmero, o segundo é comunicação **entre agentes** e exige hub externo. Nenhum guarda os trabalhos do dono. O módulo novo **não regera** o pacote: guarda e oferece; o conteúdo técnico continua vindo de `handoff.py`. Régua §0 pela porta (c).

**Dois erros próprios, pegos pelos canários do próprio repo — e vale registrar por isso.** Numerei o ADR como 099 e **colidi** com o ADR-099 já existente (validation-reporting): renumerado para 100, mesma classe de erro que já ocorrera em 095→097. E registrei a capacidade com campo `canary` e status `OK`, quando o schema exige `test` e `PROVIDES` — o `test_capabilities` acusou os dois. Canário que pega o erro de quem o mantém é o melhor argumento a favor dele.

Nomenclaturas: "trabalho" (unidade de continuidade, acima de repo e de sessão) · "aberto até ser tratado" · "oferecer, não obstruir".
Decisões permanentes: **ADR-100 Aceito**. Persistência fora do git é escolha declarada, com a consequência dita: **não é versionado nem tem backup** — é o preço de ser cross-repositório.
Riscos ativos: registro desatualizado é pior que ausente (mitigação: `listar` sempre mostra o comando de encerramento) · o conteúdo do resumo é escrito pelo agente e **não é mecanizável** — só o ciclo de vida é.
**RRC:** ADR-100 no CHANGELOG [1.77.0] · `capabilities.json` + `CAPABILITIES.md` regerados (78 capacidades) · canário `test_trabalhos.py` (16 verificações) · `test_boot_check.py` estendido para 7 checks.

**Próximo passo:** validar o mecanismo no uso real — abrir a próxima sessão e confirmar que o trabalho registrado é oferecido na abertura sem que ninguém peça. Critério de aceite: o agente cita nome e próximo passo do trabalho aberto na primeira resposta, e o dono consegue encerrá-lo com um comando.

## 2026-08-02 — Release v1.76.0 (MINOR): método de validação ponto a ponto com reporte para humano (ADR-099)

Bloco nascido **fora** do núcleo: uma sessão de validação de dados em repositório de domínio,
onde o executor produziu **números corretos e um reporte inutilizável**. O dono corrigiu oito
vezes — sobre o que estava validado, sobre o que não estava, sobre linguagem, sobre veredito e
sobre onde o arquivo estava. Nenhuma correção foi de gosto: cada uma apontou defeito que
**mudava a decisão de quem lia**. O padrão exposto é do framework, não da sessão: havia regra
para *fazer* validação (file-first, confidence-classification, traceability) e **nenhuma** para
*reportá-la a quem decide*. Resultado: executor tecnicamente rigoroso e praticamente inútil —
apresentou "não conferido" com cara de "ok", reprovou por 0,01% em campo descritivo, declarou
impedimento inexistente, e gerou artefato dizendo "PASSOU" com um portão reprovando três linhas
acima.

**Entregue:** `_shared/validation-reporting/SKILL.md` — quatro categorias (validado · não
conferido · **não obtenível** · não se aplica), níveis por **consequência do campo** (A
dinheiro/documento tolerância zero · B operacional aceito se caracterizado **e testado** que
não altera decisão · C descritivo · **B-DEC** flag derivada = métrica de impacto), total
agregado nunca sozinho (é cego a erro compensatório, que é o que fraude produz), diferença
**nomeada com resíduo zero** em vez de faixa de tolerância, materialidade restrita a B/C, e
**VALIDADO COM RESSALVA é validado** — negá-lo por perfeccionismo desserve quem decide.

**QA heterogêneo (Fable isolado, ≠ autor Opus) — 1ª rodada NÃO LIBERADO: 1 bloqueante, 5
graves, 4 menores.** O bloqueante é o que mais importa registrar: o ADR alegava a régua §0
pela **porta (c)** ("destrava eval editando existente") e o crítico derrubou os **três**
predicados — entrega 100% aditiva, nenhum eval criado, nenhuma fusão executada
(`confidence-classification` ficou intocada, e a skill nem a referenciava). Era
**racionalização**, e exatamente o defeito que o ADR-098 sofreu — citado como lição **dentro
do ADR que o cometia**. Corrigido trocando a alegação falsa pela base real, que existia:
**override explícito do dono (ADR-051)**, com débito e condição de quitação. Um ADR que
racionaliza a régua §0 vira precedente citável; registrar isso vale mais que a release.

Outros: `enforcement: advisory` afirmava um avisador inexistente (→ `prose`, como os
precedentes) · sem ponte para `confidence-classification`/`high-stakes-gate`, dual-SSoT
latente · materialidade sem escopo de nível permitia aprovar divergência de **dinheiro**
sub-limiar · "ressalva" indefinida permitia empacotar **não-conferido** como ressalva e
carimbar VALIDADO — o pecado que a §2 proíbe, pela porta dos fundos · a decisão "formato
recomendado, conteúdo obrigatório" vivia **só no ADR**, que sessão futura não carrega, enquanto
a SSoT prescrevia planilha e `.xlsx`.

Nomenclaturas: "não obtenível não é pendência" · "nível por consequência do campo" · "resíduo
zero é prestação de contas, não tolerância" · "validado com ressalva é validado".
Decisões permanentes: **ADR-099 Aceito**. Régua §0 por **override declarado**, não por porta.
Riscos ativos: método **provado uma vez**, num domínio — generalização é [INFERIDO]; o gatilho
da §1 é conjuntivo para limitar o dano.
Dívida aceita: **a skill não tem canário próprio** e portanto **viola a §10 dela mesma**
("declarar a regra não a implementa"). Declarado em três lugares e refletido em
`PARTIAL`/`prose`. Quita quando houver canário sobre artefato-exemplo com veredito derivado —
o bloco de origem já construiu um gerador assim, logo é alcançável.
**RRC:** ADR-099 no CHANGELOG [1.76.0] · README 1.75.0 → 1.76.0 · `capabilities.json` +
`CAPABILITIES.md` regerados (77) · qa-evidence
`_meta/qa/adr-099-metodo-de-validacao-ponto-a-ponto-com-reporte-para-humano.json`.

**Próximo passo:** escrever o canário da `validation-reporting` — um artefato-exemplo mínimo
cujo veredito seja derivado de códigos de saída, e um teste que **mute** o artefato e exija
que o veredito vire REPROVADO. Critério de aceite: o canário foi **visto reprovar**, e o
registro sobe de `PARTIAL`/`prose` para `PROVIDES`, quitando o débito §0.

## 2026-08-01 — Release v1.75.0 (MINOR): referência a arquivo resolve no cwd do DESTINATÁRIO (ADR-098)

Bloco nascido de **quatro falhas do próprio autor na mesma sessão**, nenhuma percebida por ele. Entregou um prompt de contextualização apontando para o **scratchpad temporário**; usou **link markdown relativo** num documento destinado a outra IA em outro repositório; passou um path com espaço (`Projeto Cliente`) **sem aspas** — e foi o dono quem viu o erro do PowerShell primeiro; e declarou **"pasta inexistente"** um diretório que **existia no repo pai**, por não ter declarado a qual dos dois repositórios o path pertencia. Mesmo defeito nos quatro: **referência que só resolve no `cwd` de quem escreveu**.

**Entregue:** Regra 8 no `_shared/traceability/SKILL.md`. A invariante **não** é "path absoluto sempre" — é **resolver do ponto de vista do destinatário**: absoluto na mesma máquina, URL/permalink em consumo web. Um `F:\metacognition-framework\tools\handoff.py` numa página do GitHub é tão morto quanto um relativo. Derivadas: path com espaço citado no dialeto do shell alvo · diretório temporário não é entrega · declarar a qual repositório o path pertence · verificar antes de emitir.

**Mecanização entregue JUNTO, não prometida** — e essa foi a correção mais substantiva do QA. `tools/handoff.py` passa a declarar a **raiz absoluta** da cópia no Pacote P14 (sem ela, os paths relativos que o pacote já listava só resolviam no `cwd` de quem gerou) e `audit_paths()` audita o próprio pacote, emitindo `⚠️` para diretório temporário e link relativo. Canário novo `tools/test_path_absoluto.py`, 10 casos — **5 que devem acusar e 5 que NÃO devem** (URL, âncora, absoluto Win, absoluto POSIX, path sem link), porque falso positivo derruba a confiança no gate e gate em que ninguém acredita é pior que nenhum.

**QA heterogêneo (Fable isolado, ≠ autor Opus) — 1ª rodada NÃO LIBERADO, 2 bloqueantes e 7 graves.** O achado nº1 foi de **segurança**: o diff carregava `.claude/settings.json` com 16 entradas `Read(//c/Users/<user>/<repo-de-cliente>/**)` num arquivo **rastreado** — `check_core_agnostic.py --sensitive` acusava `LEAK`, exatamente a classe de vazamento de dado de cliente que tornou este repositório privado. O nº2 derrubou a justificativa: o ADR reformulava a **régua §0** como custo-benefício genérico (*"paga o peso"*) — racionalização, não enquadramento; nenhuma das três portas era satisfeita, e a 098 seria a primeira regra **prose-only** da série (as Regras 5 e 7 passaram porque vieram com mecanismo). A correção foi trocar promessa por mecanismo, enquadrando em **(c)**.

Outros: **overclaim** — "nenhuma regra cobria emissão de path" era falso, o **P14** (ADR-012) já exigia *"repositório (URL) e/ou path absoluto"* no handoff, e o ADR agora reconhece que **generaliza** o P14 em vez de inaugurar · **mitigação inexistente** — o ADR remetia ao `export-clean` para anonimizar `C:\Users\<user>`, e verificou-se que `anonymize-map.txt` só tem um token de username **legado** enquanto o `sensitive-denylist.txt` declara que o username do mantenedor **não entra**; a consequência foi reescrita admitindo que a mitigação não existe · **débito invisível** — sem registro em `capabilities.json`, o `test_capabilities` passava por omissão · **blockquote órfão** — a causa-raiz do ADR-094 estava posicionada após a Regra 7 e a inserção da Regra 8 a deixou lida como parte dela (defeito pré-existente em main); devolvida à Regra 6.

Nomenclaturas: "resolve no cwd do destinatário" · "temporário não é entrega" · "declarar a qual repo o path pertence".
Decisões permanentes: **ADR-098 Aceito**. **ADR de conformance de topologia renumerado 095 → 097** — colisão com o ADR de procedência que o PR #110 já havia mergeado em main; as 4 referências stale foram corrigidas, inclusive um ponteiro para branch inexistente.
Riscos ativos: cobertura **parcial** — auditado no handoff, **advisory** no restante do output (resposta ao dono, relatório, mensagem de PR não têm canário). Registrado como `enforcement: advisory`, não como completo.
Dívida aceita: anonimização de path de usuário no pipeline público **não existe** (pendência 1 do ADR-098) · fronteiras de julgamento da Regra 8 ("quando houver mais de um repositório em jogo") não são auditáveis mecanicamente.
**RRC:** ADR-098 no CHANGELOG [1.75.0] · `README.md` de 1.73.0 → 1.75.0 (o bump de 1.74.0 não havia sido feito — dívida herdada) · `capabilities.json` + `CAPABILITIES.md` regerados (76 capacidades) · qa-evidence `_meta/qa/v1.75.0-path-resolve-no-destinatario.json` (posture RRC=PASSA).

**Próximo passo:** decidir a pendência 1 do ADR-098 — adicionar regra genérica `C:\Users\<qualquer>` ao `anonymize-map`, ou registrar explicitamente que o layout do mantenedor é aceitável na distribuição pública. Critério de aceite: `export-clean` roda e o token do operador não aparece na saída, OU decisão registrada no ADR.

## 2026-07-28 — Release v1.74.0 (MINOR): HITL mecanizado, corte `score ≥ 6` com exit code próprio (ADR-096)

Bloco que **fecha um wire declarado e nunca ligado**. O ADR-086 entregou o cálculo de risco (`prob × impacto` → `gate` + `tier`) e deixou o consumo como possibilidade: *"`qa-evidence`/`readiness-gate` **podem** consumir o `gate_agregado`"*. Grep por `risk_score|gate_agregado|CONCERNS` em `tools/` confirmou que **nenhum consumidor existia** — as únicas ocorrências eram o próprio tool, seu canário e prosa. Consequência prática: o item 4 do `high-stakes-gate` — *"hand-off bloqueado até revisão humana"* — era **prosa**. Nada bloqueava, e mesmo um agente disposto a respeitar não tinha o que ler, porque o tool sai com `exit 0` em todos os vereditos por desenho do ADR-086.

**Entregue:** `HITL_MIN_SCORE = 6` (corte escolhido pelo dono entre três opções); campos `hitl` por item e `hitl_requerido` agregado, **ortogonais** ao `gate`, que fica intacto — colapsar `6 → FAIL` destruiria a faixa CONCERNS e faria o canário exaustivo mentir sobre a matriz; flag `--gate-exit` → **exit 2**, com contrato legível por hook **0 = liberado · 1 = entrada inválida · 2 = HITL requerido**; precedência fail-closed > gate. Zero arquivo novo, zero capability nova — extensão do `risk_score.py` e do seu canário (régua §0).

**QA heterogêneo (Fable isolado em worktree, ≠ autor Opus) — 2 rodadas, a 1ª REJEITOU.** O CRÍTICO é instrutivo: **erro de uso do `argparse` saía com exit 2**, o código reservado a "HITL requerido". `--prob abc`, valor faltando ou typo de flag eram indistinguíveis de bloqueio legítimo, e um hook registraria "aguardando humano" como evidência de item que **nunca foi avaliado** — exatamente a confusão que a Alternativa 2 do próprio ADR declara ter rejeitado, cometida pela porta dos fundos. **O autor encontrou esse defeito empiricamente durante a implementação, viu o exit 2, concluiu "invocação minha errada" e seguiu** — o revisor o achou em 26 casos. É o viés que o gate heterogêneo existe para pegar, e fica registrado por isso. Corrigido com `_ParserFailClosed`; confirmado na 2ª rodada por 20 vetores de ataque.

Segundo achado, sobre o próprio gate: **o canário aferia só o `returncode`, nunca o `stdout`** — mutação removendo `hitl_requerido` do JSON **passava**, enquanto o SKILL manda o consumidor ler exatamente esse campo. Um teste que não falha quando deveria é pior que nenhum, porque dá licença. Terceiro: lista de não-dicts atravessava o guard (o operador `in` casa substring em `str`) e o exit 1 vinha do interpretador **por acidente**. Na 2ª rodada o revisor mostrou que a guarda nova **também não tinha dentes** — e o bloco `(c3)` fechou isso.

Quarto achado, de honestidade textual: as correções da 1ª rodada foram escritas em **apêndice** enquanto as frases derrubadas — *"compatibilidade retroativa total"* e a mitigação `action-safety` sem qualificador — **permaneciam nas seções principais**. Quem lesse só o corpo receberia a afirmação que o QA tinha derrubado. Emenda em apêndice não corrige o corpo; corrigido nas duas fontes.

Nomenclaturas: "HITL mecanizado" · "corte multiplicativo" · "eixo ortogonal ao gate" · "contrato 0/1/2 legível por hook" · "fail-closed precede o gate".
Decisões permanentes: **ADR-096 Aceito**. Corte em `score ≥ 6`, escolhido pelo dono **contra a recomendação do autor** (regra de impacto absoluto), com a divergência registrada para auditoria e não para relitígio.
Riscos ativos: **`1 × 3 = 3` não trava — raro × catastrófico passa livre.** É a forma dos incidentes históricos registrados na memória do projeto (segredo em log; teste gravando em estado global do Windows). A mitigação de segunda linha existe, mas o QA a dimensionou: o `effect_gate` só inspeciona `Bash`/`PowerShell`, é **fail-open** em erro e com regras ausentes, e o julgamento T3 pleno segue sendo prosa. Para item `1×3` cujo dano não vira comando de shell casando com padrão, **nenhum dos dois pega**. Aceito com a consequência na mesa; se um incidente dessa forma ocorrer, revisitar com a alternativa de impacto absoluto.
Dívida aceita: `capabilities.json` não referencia o ADR-096 no registro `risk-gate` — o drill-down não revela o HITL. E `ensure_ascii=False` com pipe cp1252 no Windows rotula entrada **válida** com caractere fora do cp1252 como inválida (pré-existente ao ADR-086, backlog).
**RRC:** ADR-096 no CHANGELOG [1.74.0] · `_shared/high-stakes-gate/SKILL.md` v1.1.0 com o dimensionamento · qa-evidence `_meta/qa/v1.74.0-hitl-corte-score-6.json` (posture RRC=PASSA) · `capabilities.json` regerado sem bytes alterados, coerente com a régua §0.

---

## 2026-07-22 — Release v1.73.0 (MINOR): carimbo de PROCEDÊNCIA em trabalho executado fora do repositório (ADR-095)

Bloco nascido de **caso de campo, não de ideia de mesa**: sessão de aplicação do framework a um chamado SAP em ambiente farmacêutico regulado, executada inteiramente numa pasta de projeto em drive corporativo sincronizado. Foram produzidas ali minutas de dossiê de validação, uma proposta de código não compilada e um ADR não ratificado — ao lado de material migrado e de documentos oficiais do cliente. Pedido do dono ao fim: *"indique em um arquivo o nome do repo/sessão/framework que está tratando, número chamado, etc"* + *"insira esta prática"*. A lacuna real: a cadeia decisão→fonte→versão (`_shared/traceability` Regra 4) **quebra no ponto em que o artefato SAI do repo** — quem abre a pasta meses depois não sabe qual framework/versão/sessão produziu, nem **o que ali é minuta e o que é registro**. Em ambiente regulado, minuta lida como registro é achado de auditoria.

**Entregue:** `tools/handoff.py --provenance DIR [--write]` (reusa `repo_state()`/`_git()`/timestamp determinístico do commit HEAD já existentes para o Pacote P14 — sem tool nova, sem hook novo, sem dependência nova; régua §0); `_shared/traceability` **Regra 7** + `.agent/rules/05-procedencia-trabalho-externo.md` (ponteiro fino); `capabilities.json` +`external-work-provenance` (`enforcement: manual`); canário 11 checks em `test_handoff.py`. **Desenho agnóstico por construção:** o gatilho é a **FORMA da situação** (destino de escrita fora do repo), nunca o nome do cliente/produto — exigido pelo canário `core-no-vendor` (ADR-091) e, no fim, engenharia melhor: a regra vale para qualquer pasta externa e o caso concreto vira instância, citada só no ADR onde proveniência é sancionada.

**QA heterogêneo (Sonnet isolado, ≠ autor Opus 4.8) — 2 rodadas, a 1ª REJEITOU.** Achados reproduzidos empiricamente, não deduzidos: (a) `os.path.commonpath` **levanta ValueError** em drive diferente e em UNC — que é *justamente o caso de uso primário declarado pelo ADR* (drive corporativo/share de rede); a feature crashava com stack trace cru no seu próprio cenário-motivação; (b) **bypass da guarda por case** — filesystem Windows é case-INsensitive, `commonpath` compara case-SENSITIVE, então alvo DENTRO do repo passava como externo e o carimbo seria escrito na árvore do git (mesma classe do incidente de arquivos espúrios já registrado neste repo); (c) append cego em arquivo pré-existente que não é carimbo; (d) `--write <caminho>` aceito e descartado em silêncio; (e) capability sem `enforcement` escapando da auditoria anti-teatro do próprio framework; (f) README 1.72.0 × CHANGELOG 1.73.0 **sem canário cobrindo o par**. Corrigido com `realpath`+`normcase`+`try/except`, validação de cabeçalho, falha-alto no CLI, canário 7→11 checks. **2ª rodada = APROVAR_COM_RESSALVAS**, com o revisor criando uma **junction Windows real** para confirmar o caso (d-symlink) que na 1ª rodada ficara INFERIDO; sem regressão nos 60 canários restantes.

Nomenclaturas: "carimbo de procedência" · "trabalho externo ao repo" · "SLOT explícito" (lacuna visível, não silêncio) · "status por artefato: MINUTA / PROPOSTA / MIGRADO / APROVADO" · "Regra 7".
Decisões permanentes: **ADR-095 Aceito**. Release **v1.73.0** cortado (RRC completo). Gatilho é a FORMA da situação, nunca o nome do cliente — núcleo agnóstico preservado.
Próximo passo: ATD-36246 segue **bloqueado em diagnóstico, não em código** — Passo 0 do `ROTEIRO-DEBUG-NSQ-C5-C6.md` exige sessão de debug em NSQ com acesso a SAP (fora do alcance do agente). Decisões pendentes do dono: ratificar ADR-002 (precedência lote-aberto × FIFO) · semântica de "lote já iniciado" · comportamento em saldo insuficiente.
Riscos ativos: a Regra 7 **não é forçada por mecanismo** (nenhum hook observa escrita fora do repo) — mesmo teto declarado no ADR-094; `enforcement: manual` é a declaração honesta disso. Guarda passou a fazer I/O (`realpath`) — latência possível em share de rede inacessível (INFERIDO, BAIXO, aceito).
**RRC (completo):** ADR-095 no CHANGELOG [1.73.0] · README + vitrine (`guia/web/index.html`, 9 ocorrências) + web-bundles(6 regenerados) em 1.73.0 · qa-evidence v1.73.0 (`_meta/qa/v1.73.0-procedencia-trabalho-externo.json`, posture RRC=PASSA) · CAPABILITIES.md em sync.

---

## 2026-06-23 — Release v1.72.0 (MINOR): processo adversarial mandatório-default + canônico-prevalece + autonomia-limitada + EDR verificável (ADR-094)

Fechamento do release do ADR-094, que já estava mergeado em main (#106 @ `23655d9`) mas com o ritual de release não-cortado (CHANGELOG em `[Não lançado]`). Diretriz do dono: *"o PROCESSO adversarial é o CORAÇÃO do framework e precisa ser mandatório; ANTES funcionava SEM bloquear; advisory parou de funcionar"*. O defeito era NÃO seguir regras que já existiam e funcionavam (ADR-011/027/007), não ausência de regra → correção ADITIVA (sem hook novo, sem hard-block; régua §0). Fechamento executado em sessão separada (máquina `9TRP7H4`, não-kerberus) após verificar origin sem trabalho de release in-flight (sem branch/tag/WIP de v1.72).

**Entregue (já em main via #106; este bloco apenas CORTA o release):** `_shared/traceability` **Regra 6** (desafiar o pedido · qa-critic isolado por-default até-PASS com rewind · elicitação/pesquisa exaustivas · **canônico-prevalece** · **autonomia≠bypass**); `boot_check` ganha `kind=process` (`_process_running`, cross-platform/determinístico) tornando a premissa "Kaspersky veta hooks" **verificável** (APLICA/ESTALE), não assumida; canário `test_environment_applicability` cobre o caso `process`. **Decisão de NÃO fazer:** hard-block de merge — `squad_gate` permanece **pronto-mas-não-ativado** (escalada futura, decisão do dono).

**QA heterogêneo (Sonnet, isolado):** sobre o código (#106) — APROVAR_COM_RESSALVAS, 3 ALTO corrigidos (incl. NÃO commitar `settings.json` com paths de cliente). Sobre o **fechamento do release** (esta sessão, qa-critic isolado para o posture-gate) — APROVAR_COM_RESSALVAS, `rrc=PASSA`: conteúdo verificado correto (bump completo, CHANGELOG honesto vs main, Regra 6/kind=process/squad_gate-dormante confirmados no código, SemVer MINOR correto, ADR-094 Aceito+citado); 3 ressalvas BAIXO = passos mecânicos de fechamento (persistir artefato qa-evidence + checkpoint + commit), não defeitos. Reconciliação registrada: os 3 canários inicialmente-FAIL (posture/qa-evidence/release-checkpoint) eram **pré-condicionados ao próprio veredito a persistir**, não bug — verificável em `test_posture_gate.py:95`/`test_qa_evidence.py:14`. Suíte final: 63 PASS / 1 SKIP / 0 FAIL.

Nomenclaturas: "processo adversarial mandatório-default" · "canônico-prevalece" · "autonomia≠bypass" · "EDR verificável (kind=process)" · "Regra 6".
Decisões permanentes: **ADR-094 Aceito**. `squad_gate` pronto-mas-dormante (hard-block é decisão futura do dono). Release **v1.72.0** cortado (RRC completo). Dono autorizou "verificar, revalidar e finalizar até pr merge".
Próximo passo: tarefas B/C (Copilot→Gemini↔RAG) — prompt de handoff portável + discovery file-first da pasta `F:\Downloads\1- Agente Copilot Studio...`.
Riscos ativos: corte do release feito de `9TRP7H4` (não-kerberus); se kerberus tiver corte não-pushed, reconciliar CHANGELOG/README (conflito trivial, aditivo).
**RRC (completo):** ADR-094 no CHANGELOG [1.72.0] · README+web-bundles(6)+vitrine(`guia/web/index.html`) 1.72.0 · qa-evidence v1.72.0 (posture, `_meta/qa/v1.72.0-adversarial-process-edr.json`) · suíte 63 PASS/1 SKIP/0 FAIL · tag v1.72.0.
**OVERRIDE (ADR-051):** PR #107 mergeado com o required-check GHA "canários" VERMELHO — **causa: os jobs do GitHub Actions NÃO iniciaram por falha de billing/spending-limit da conta** (anotação literal do run), não é falha de código/canário; red idêntico em #104/#105/#106 (já em main) prova pré-existência. **Gate real** = `run_canaries.py` local = 63 PASS/0 FAIL. **Custo/consequência:** GHA segue inoperante até o billing ser resolvido (dívida de infra, ação dono/TI; sem risco de código). Declarado, não-silencioso (memória `github-actions-not-the-gate`).

---

## Em aberto

- **Quitação do override da régua §0 do ADR-102** (aberto em 13/08/2026): o padrão documental
  entrou como **adição pura** sob override explícito do dono. Duas condições fecham o débito, e
  enquanto não fecharem o override permanece visível aqui: **(a)** aplicar o padrão em **dois
  projetos de portes diferentes** e registrar o que sobrou e o que faltou — os portes *mínimo* e
  *médio* do §3 são hoje **INFERIDOS** de um caso só; **(b)** extrair os gates 1 e 2 do §4 (link
  quebrado, fronteira) para utilitário do framework **se e quando repetirem em três projetos** —
  aí o registro sobe de `PARTIAL/prose` para `PROVIDES` com canário. Gatilho: toda vez que um
  segundo projeto adotar o padrão, reavaliar (a).
  **[2026-08-16 — DECISÃO DO DONO que desfaz um impasse do desenho original]** A condição (a)
  era circular e ninguém tinha notado: o padrão só seria promovido depois de um segundo projeto
  usá-lo, mas nenhum segundo projeto consegue usá-lo enquanto ele não estiver na `main`. O dono
  apontou a circularidade e decidiu: **o padrão sobe para a `main` marcado como pendente de
  validação em segundo projeto, e a marca só sai depois desse uso.** Disponibilidade e prova
  deixam de ser a mesma coisa. O override continua aberto — o que mudou é que agora ele *pode*
  ser quitado. Marca sugerida: campo `status: PARTIAL` + `validado_em_projetos: 1` no registro da
  capacidade, conferido pelo canário do registro.

> WIP atual (ex-G11). Reconciliar com branches do git e ADRs em status `Proposto` no `/start-session` (modo squad).

> **Higiene v1.58.1:** itens FECHADOS saem desta seção (o fechamento já vive nos checkpoints datados
> acima — aqui era duplicação que poluía o `handoff.py` e enganou um boot em 2026-06-11). Item só
> entra/permanece se está ABERTO; fechar = remover daqui + checkpoint registra.

- **[2026-08-07] Débitos de fechamento do bloco v1.77.0 — 3 achados, NADA aplicado.** Handoff completo (com comando de re-validação e predicado "aplicar SÓ SE" por item) em `docs/_private/handoffs/2026-08-07-debitos-de-fechamento-v1.77.0.md`. Resumo: **F1** ordem do `history.md` invertida (v1.77.0 abaixo de v1.76.0) — quebra a invariante mais-novo-primeiro e faz `handoff.py` emitir o "Próximo passo" errado, em silêncio · **F2** tags `v1.76.0`/`v1.77.0` ausentes (local e `origin`) — **2ª ocorrência** da falha catalogada em 2026-06-02, gatilho atingido · **F3** registro do ADR-100 nunca alimentado (`~/.claude/trabalhos/` inexistente) — critério de aceite do próprio checkpoint não atendido; **não verificável de outra máquina**. Candidato §0: 2 asserções em `test_consistency_closing.py`, fundindo com o item de backlog "Canário README × topo do CHANGELOG". **Aplicar só após revisão e re-validação contra a versão vigente** — o handoff congela o estado em `main` @ `8820608`. Fechar = remover esta linha + checkpoint datado.
- **ADR-097 itens 4 e 5 do §Mecanismo** (aberto em 16/08/2026, ao aceitar o ADR): a camada-mestra
  (canário fail-closed sobre o event log) está entregue; faltam o **hook PreToolUse** que nega ação
  de papel downstream sem PASS upstream — camada rápida, best-effort por desenho — e cabear o
  **HITL criptográfico** como pré-condição de ação T3 em bloco high-stakes (`verify_hitl_proofs.py`
  já existe; falta a ligação). Nenhum dos dois é pré-requisito da conformance: o ADR declara o
  canário como a lei e o hook como conveniência. Gatilho: dono declarar, ou primeira vez que uma
  ação downstream sem upstream passar despercebida até a release.
- **Pendência permanente (não-código, dono/TI):** exclusão do Kaspersky `.claude\hooks\*` (afeta só os hooks .ps1 remanescentes; ADR-060/079).
- **Backlog ativo (trigger-gated, NÃO WIP):**
  - **Canário README × topo do CHANGELOG inexistente** (dívida PRÉ-EXISTENTE exposta pelo qa-critic em v1.73.0, 2026-07-22): a política do repo exige que README, tag e .zip subam junto com o CHANGELOG, mas **nenhum canário compara esse par**. `test_marketing_claims` cobre vitrine × README e **lê a versão do próprio README** — então README(1.72.0) × CHANGELOG(1.73.0) passou verde. Em v1.73.0 o sintoma foi corrigido à mão; o mecanismo não existe. **Candidato §0:** +1 asserção em `test_consistency_closing.py` (que já é o gate de version-claim), não canário novo. Trigger: 2ª ocorrência OU dono declarar.
  - **36 capabilities sem campo `enforcement` são invisíveis à auditoria anti-teatro** (observado 2026-07-22 ao corrigir achado do qa-critic): entradas que **omitem** o campo não contam nem como OK nem como débito na lista `[debito-mecanizacao]` (P15/ADR-085) — o registro de v1.73.0 foi declarado `manual` e passou a aparecer, os outros 36 seguem fora do radar. Um mecanismo anti-teatro com ponto cego de 48% mede menos do que parece. **Candidato §0:** tornar o campo obrigatório em `test_capabilities.py` (fail-closed) e classificar os 36 num único passe. Trigger: dono declarar OU próxima revisão de P15.
  - **Proveniência de raciocínio POR-TURNO** (gap empírico 2026-06-22, sessão `ee8a9a49`): gates elicit/pesquisa/crítica são de **MARCO** (release/junção), não de TURNO — entre marcos, raciocínio sem gatilho nem recibo (o "tudo na mão" cobrado pelo dono). **Extratos:** 4 interações, único recibo = `.claude/boot-proof.json` (manual, pós-nag); `elicitation-gate`/`context-brief-gate`/`qa_evidence` não dispararam — sem ficha, sem brief, sem ledger novo. **Causa NÃO-EDR** (hooks cabeados + UserPromptSubmit dispara; atribuir a Kaspersky foi hint-virou-causa). **Candidato §0:** emissor por-turno (`PostToolUse`/fim-de-turno) que declara ao vivo + grava recibo, reusando `qa_evidence.py` como sink, com fallback inline — **NÃO reinventar** ledger, estender. Análogo: o "evento" do OpenMetadata vs. nossa proveniência por-marco. Trigger: dono declarar OU 2ª recorrência. Detalhe: `docs/research/OpenMetadata-analise-contribuicoes-processo-com-fontes.md` §Addendum 2026-06-22. Pré-gate: architect (ADR) + qa-critic heterogêneo.
  - Corrida do 1º prompt do liveness (route-gate dispara antes do carimbo dos SessionStart; banner se auto-cura no 2º prompt — observado 2026-06-11 sessão `9f01bd9e`) — trigger: incomodar o dono OU 3ª ocorrência reportada. Candidato: tolerar carimbo < N min de outra sessão.
  - Cascata v1.55.0–v1.60.0 para os shadows via `export-clean` — trigger: decisão de publicação do dono.
  - ADR-011 §Pendências: Alternativa 2 (rewind cirúrgico) — trigger: caso real onde cascata é custosa.
  - ADR-011 §Pendências: validation.md projeto × release convergir templates — trigger: ficar pesado manter separado.
  - Item D4 (cross-platform hooks Linux/macOS port) — trigger: user em PC não-Windows pedir.
  - **Integração protocolo cross-IA no fluxo J0-J5** — trigger: 2ª sessão cross-IA real OU dono declarar. Problema: o protocolo hoje é bolt-on (ad-hoc, sem wiring em nenhuma junção, sem qa-critic gate, sem entrada automática em `history.md`). Candidatos: `docops §Encerramento` dispara `outbox→hub` no J5; `qa-critic` revisa conteúdo cross-IA antes do dispatch; threads abertas geram entrada em `## Em aberto` no boot seguinte; `consistency-gate` checa threads cross-IA no encerramento. Evidência empírica: sessão 2026-06-08 (thread atd36246-fefo-fifo, 3 rounds); gap registrado no round 3 (sealed-partial). ADR-espelho do lado claude-master = candidato arquitecto pós-gate.

---

## Aprendizado

> Notas de fracassos capturadas via `/checkpoint` (ex-G9). **Firewall:** notas são **inertes** — só viram comportamento via skill/regra destilada, aprovada via ADR e mergeada. Nota errada não propaga.

- **[2026-06-16] Method-audit (qa-critic mesmo-modelo deixou passar gate VERMELHO — heterogeneidade declarada "indisponível" era na verdade disponível):** no BLOCO v1.59.0 (integração BMAD), o **author Sonnet 4.6** rodou o próprio qa-critic (R1/R2, mesmo modelo) e declarou "APROVADO_LIMPO / 50 PASS / 0 FAIL" — mas os canários estavam **VERMELHOS** (`test_qa_evidence` + `test_posture_gate`) por um defeito determinístico que o auto-review não pegou: o artefato qa foi gravado com `release="v1.59.0"` enquanto o gate compara contra `"1.59.0"` (sem prefixo `v`, convenção de TODOS os 9 artefatos anteriores). Só foi pego quando o dono **trocou para Opus 4.8** (R3, process-critic heterogêneo) e mandou revisar. · **Causa-raiz dupla:** (1) viés de auto-aprovação — o mesmo modelo que escreve o artefato e declara "50 PASS" é o que deveria tê-lo verificado; sem heterogeneidade, o false-PASS não tem contraparte que o derrube (exatamente o que ADR-011/078 preveem). (2) Sonnet declarou heterogeneidade "indisponível", mas ela estava **DISPONÍVEL** via `Agent(subagent_type: qa-critic, model: <distinto>)` — o mecanismo existe (qa-critic é subagente real; escada ADR-078), e foi confundido "não troquei de modelo" com "não posso trocar". · **Firewall/proposta (não-preemptiva, 1ª ocorrência):** quando author = tier-médio/baixo (sonnet/haiku) e o bloco fecha release, o orquestrador DEVE spawnar o qa-critic via `Agent(model: tier-max)` ANTES de declarar PASS — não rodar o adversarial no próprio modelo e chamar de heterogêneo. Candidato a regra se recorrer. Liga a [[feedback-prosa-vira-mecanismo]] e à postura adversarial permanente.
- **[2026-06-08] Method-audit (start-session / passos 0.5/0.6 pulados sem hook):** executei o `/start-session` e saltei as verificações de step 0.5 (boot-scan cross-IA via `cross_ai_hub.py boot-scan`) e 0.6 (relatório de execução do repo público via `knowledge_catalog.py --build`) — o dono teve que cobrar: "vc rodou a verificacao reports execucao do repo publico e o cross ia?". · **Causa-raiz:** sem hook SessionStart rodando essas verificações automaticamente, o agente confia que "boot-scan anuncia" sem verificar se o boot-scan realmente anunciou (assumiu silêncio=vazio, sem testar). Falha anti-suposição (regra inviolável do CLAUDE.md). · **Impacto:** o protocolo cross-IA ADR-069 diz que o boot-scan detecta handoffs pendentes — mas sem execução e sem confirmação, o agente prosseguiu como se não houvesse handoff, quando havia (thread atd36246, 2 rounds já no hub). · **Proposta (não-preemptiva):** memória criada `start-session-manual-steps-when-hooks-inert.md` registrando que na máquina 9TRP7H4, com hooks inertes, TODOS os passos manuais do start-session (incluindo 0.5/0.6) devem ser rodados pelo agente, não assumidos. Consistente com [[kaspersky-aac-blocks-hooks]] atualizada.
- **[2026-06-08] Method-audit (princípio 11 / doc-intake não usado até ser provocado) — REPORTE DA FALHA pedido pelo dono:** li `history.md` INTEIRO no contexto principal (~38k tokens, truncado a 25k pelo harness) em vez de fracionar via `doc-intake` (ADR-029: chunks + sha256). **Auto-detecção falhou** — só corrigi quando o dono provocou (mesma falha admitida na sessão premium no mesmo dia). · **Causa-raiz:** princípio 11 honesto — agente não detecta o próprio desperdício de contexto sem gate; e a regra "usar doc-intake p/ fonte grande" era **prosa**, sem mecanismo que force. Distinção honesta: `doc_intake.py` é p/ fontes EXTERNAS (proveniência chunk+sha); p/ arquivos do próprio repo que edito, `Read` é correto — o erro foi **ler grande inteiro** quando devia ser cirúrgico (grep+offset). · **Decisão (executada, não "candidato"):** `tools/context_budget.py` + canário (decide LER-INTEIRO vs FRACIONAR por limiar de tokens, aponta `doc_intake`) + doutrina no `start-session`. **Limite declarado:** enforcement pleno das chamadas `Read` exige hook `PreToolUse(Read)` (Kaspersky/non-admin veta → doutrina). Liga a [[feedback-prosa-vira-mecanismo]].
- **[2026-06-08] Method-audit (regressão do modo autosuficiente / clobber reincidente do settings global):** o dono relatou "autosuficiente antes funcionava, agora não". File-first achou: `~/.claude/settings.json` = `{}` (clobber total), `~/.claude/framework-mode.json` AUSENTE (state file do ratchet sumiu). · **Causa-raiz:** o self-heal `ensure-global-wiring` (ADR-027, que reafirmaria a wiring global a cada boot) é **hook-gated**, e o **Kaspersky/non-admin veta hooks PS** nesta máquina (ADR-047) → o clobber recorre sem o self-heal. 2ª face do mesmo padrão "mecanismo existe mas é hook-dependente onde hook está bloqueado". · **Solução (executada):** restaurei `framework-mode.json` (autosuficiente) + apliquei o template `autosuficiente.json` ao `settings.json` global. **Limite honesto:** no VS Code extension o prompt de permissão também é toggle de UI (registrado 2026-05-31) — settings.json sozinho pode não bastar. **Candidato (2ª ocorrência confirmada → considerar):** um self-heal NÃO-hook (re-aplicar o modo via passo Python no `start-session`, como o `repo_mode --mode` faz) p/ máquinas Kaspersky. Liga a [[feedback-prosa-vira-mecanismo]].
- **[2026-06-02] Method-audit (princípio 11 / consistency-gate não-disparado no fechamento):** o `/start-session` pegou o `history.md` **~7 releases atrás** da `main` (parou em v1.31.0; main em v1.38.0) + **3 tags ausentes** (v1.36/37/38) + **ADR-051 merged-as-Proposto**. · **Causa-raiz:** o `consistency-gate` (ADR-030, fail-soft no docops §Encerramento) **não rodou no fechamento** dessas 7 sessões — o débito de checkpoint/tag/status só foi pego pelo retrospective gate humano no boot seguinte. Mecanismo existe mas não disparou (≠ "não existe"). · **Proposta (não-preemptiva, aguarda 2ª ocorrência confirmatória):** investigar se o `consistency-gate` está **wired e executando** no encerramento real (vs só documentado no SKILL) — se o padrão "gate fail-soft existe mas não roda" recorrer, vira candidato a fail-closed ou a check no `/checkpoint`. Liga a [[framework-self-improvement]]. **Sem ADR agora** — 1 ocorrência confirmada (régua §0; princípio 11 honesto: mecanismo silencioso ≠ ausente). Débito reconciliado nesta sessão (tags + status + checkpoints).
- **[2026-05-31] Method-audit (operacional / encadear delete com merge não-verificado):** mergeei o PR #25 via `gh pr merge` num comando que **também deletava a branch** (local+remota) logo em seguida; o `gh` deu **network error** (merge não concluiu) mas o delete rodou → PR **auto-fechou sem merge** e a branch sumiu. · **Causa-raiz:** encadeei limpeza destrutiva (branch delete) com a ação principal (merge) no mesmo comando, sem verificar sucesso entre elas. · **Solução (executada):** commit `134d1ad` recuperado (existia local + em `refs/pull/25/head`), recovery-merge direto na main. **Disciplina:** nunca encadear `branch -d`/`push --delete` com o merge; verificar `gh pr view --json mergedAt` ANTES de limpar. Liga a [[feedback_pr_human_gate_merge]].
- **[2026-05-31] Method-audit (qa-critic / overclaim de segurança pego antes de publicar):** ao escrever o `SECURITY.md`/site, afirmei que o `effect-gate` rodava "por default, mesmo com o agente injetado" — mas ele **não estava wired** no `.claude/settings.json` (só no template de managed-settings, instalação manual). **qa-critic adversarial (Sonnet isolado) pegou o overclaim ALTO antes do merge.** · **Causa-raiz:** descrevi a *capacidade pretendida* (ADR-015) como se fosse o *estado instalado*. · **Solução (executada):** wirar o effect-gate como PreToolUse no `settings.json` (ativo por default) + ressalvas de pré-requisito no SECURITY.md (managed-settings = camada não-bypassável). Reforça [[feedback_framework_integral]]: claim de segurança é alto-risco; gate adversarial antes de publicar, não depois.

- **[2026-05-30T21:30] Method-audit (princípio 11 / viés processo-sobre-produto):** meu veredito inicial sobre os 4 papéis SW da SPEC Perplexity foi "vazamento de domínio → fora do núcleo → refutar". **O dono corrigiu** ("reanalise sob a ótica de que fornecemos ao final um produto de dados/software"). · **Causa-raiz:** ao avaliar adição ao núcleo, otimizei a *pureza do agnosticismo* e subponderei o *propósito declarado* (entregar produto) — exatamente o "viés de processo sobre produto" que a própria pesquisa Perplexity nomeou. Agente não auto-detectou; foi feedback do dono (fonte legítima, P11 honesto). · **Proposta (executada):** ADR-023 reconcilia via app bundlada (distribuição especializada, `exemplos/dominio-software/`) — núcleo intacto/agnóstico, produto ganha 2 papéis (ux+evals). Firewall preservado.
- **[2026-05-30T21:30] Method-audit (ADR-018 / teste do gerador herda o ponto-cego do gerador):** o canário `test_mission_gate.py` passava 3/3 **escondendo um bug ALTO** — eu (gerador) escrevi o teste no mesmo formato inline que o hook espera, enquanto o *template* que o usuário segue usava heading markdown; STANDARD era inalcançável pelo caminho documentado. **Pego pelo qa-critic Sonnet heterogêneo** (ADR-018), que leu template×hook×teste como contratos independentes. · **Causa-raiz:** teste autoral do gerador compartilha o viés do gerador — não substitui crítico independente. **Confirma empiricamente o valor do modelo heterogêneo** (ADR-018): R1 reprovou um ALTO que 3 testes verdes não viam. · **Proposta:** sem regra nova (régua §0 — já coberto por "qa-critic heterogêneo obrigatório"). Vigilância: "tests verdes do gerador" ≠ verificação; o crítico independente é necessário, não opcional.

- **[2026-05-28T09:01] Method-audit (ADR-009 / princípio 11):** Stale counts ("4 edições" vs "9 edições") residuais em múltiplos arquivos atravessaram 3 dos 4 rounds qa-critic da v1.10.0. · **Causa-raiz:** scope cresceu por incorporação adversarial sem step de varredura de coerência interna antes de re-submeter — skill ausente: validation pre-commit de contagens/números/listas que possam ter ficado stale após scope-creep. · **Proposta (lean):** +1 linha em `_shared/docops` ou release checklist (`guia/GIT-VERSIONAMENTO.md`): "antes de re-submeter ADR/spec ao qa-critic após scope-creep, varrer documento por contagens stale (totais, listas, tabelas de implementação)".
- **[2026-05-28T09:01] Method-audit (ADR-009 / princípio 11):** Meta-recursão do campo `Status` do ADR — sempre 1 round atrás do qa-critic em curso (cada round novo encontra Status descrevendo o round anterior). · **Causa-raiz:** Status descreve auto-referencialmente um processo que ainda está rodando — impossível fechar sem fork. · **Proposta (lean):** se padrão se repetir em próximo ADR, atualizar template `docs/adr/000-template.md` para que Status use metadado externo (último commit-hash de round qa-critic) em vez de descrever rounds pendentes. **Não-preemptivo** — decisão sob demanda.
- **[2026-05-28T09:01] Method-audit (ADR-009 / princípio 11):** ADV-1 round 1 (localização do companion `metodo-senior.md` em `.agent/skills/discovery/` vs `_shared/`) foi marcado como follow-up sem decisão consciente. · **Causa-raiz:** framework não tem critério explícito para distinguir "transversal entre papéis" (vive em `_shared/`) de "companion-de-skill" (vive ao lado da skill dona). · **Proposta (lean):** se próximo ADR (architect/developer/qa-critic) precisar referenciar `metodo-senior.md`, decidir then — não criar regra preemptiva.
- **[2026-05-29T19:00] Method-audit (ADR-009 / princípio 11 reescrito ADR-010 §C-1):** v1.11.0 absorção falhou no RRC self-applied — agente racionalizou `README.md:4` ("ALCOA+/ANP/FDA/BACEN/GAMP" como exemplo didático) como OK enquanto o gate dizia ZERO refs. **Foi o dono que detectou e corrigiu.** · **Causa-raiz:** agente que se auto-audita defende suas próprias escolhas (viés). Princípio 11 original ("auto-observação") supervalorizava capacidade que não existe. · **Proposta (executada):** princípio 11 reescrito como "observação meta-cognitiva (captura estruturada de feedback)" — agente registra notes proativamente quando consegue E via feedback do dono (fonte legítima). Limite documentado em ADR-010 §C-1.
- **[2026-05-29T19:00] Method-audit (ADR-009 / princípio 11):** v1.11.0 + v1.12.0 cada uma teve 3-4 rounds qa-critic com **mesmo padrão de stale counts** ("8 passos" → "9 passos"; "5 itens" → "6 itens"; "6 edits" → "11 edits"). RRC self-applied pelo agente passou pelos contadores stale em múltiplos arquivos. **3 rounds com mesmo tipo de finding confirma empíricamente o limite previsto em ADR-010 §ii** — RRC tem como objetivo reduzir achados de coerência mas não promete eliminação total; gate humano externo (qa-critic adversarial em subagente isolado) é complemento NECESSÁRIO, não opcional. · **Causa-raiz:** scope-creep durante absorção de findings adversariais não dispara releitura completa cross-document. · **Proposta (executada em ADR-010 §ii.2):** RRC ganhou "contagens em sync" como 5ª dimensão de coerência obrigatória (`/checkpoint` RRC gate em 6 itens; `/checkpoint` workflow e validation.md V7 já refletem).
- **[2026-05-29T19:00] Method-audit (ADR-009 / princípio 11):** v1.12.0 foi dogfood real do v1.11.0 — discovery inline aplicou passo 6 ADR-010 (Escopo declarado: regulado=NÃO, alto-risco=NÃO crítico, semântica=SIM anti-fraude, gaps=flagados) + método sênior 9 passos incluindo RRC + 3 seções obrigatórias. **Pipeline integral funcionou em projeto real, não sintético.** · **Validação positiva:** princípios 10-13 não regrediram à média entre releases consecutivas; ciclo de auto-melhoria do framework é sustentável quando case real está disponível. · **Sinal de saúde:** taxa de princípios novos por release deve cair com o tempo; v1.10.0 = +1, v1.11.0 = +1, v1.12.0 = +1. **Alvo v1.13.0 = ≤1 princípio novo**; se nada surgir natural, saúde confirma maturidade.
- **[2026-05-29T22:30] Method-audit (princípios 10+11+13 / 4 padrões observados na sessão de hoje):** (a) **3 inflações detectadas PELO DONO** antes do commit final (README "ALCOA+/ANP/FDA" como exemplo didático em v1.11.0; "cascata cirúrgica" oxímoro em v1.12.0; §05 nova em web/index.html pós-v1.12.0). (b) **3 polish commits post-v1.12.0** (22cd976/f2fb4a7/16a4ae4) auto-declarados "não-bloco" sem critério binário — f2fb4a7 introduziu Mermaid (surface estrutural) e qualificava como bloco. (c) **Velocidade insustentável** — 3 princípios em 1 dia (11 reescrito + 12 + 13); alvo v1.13.0 = 0 princípios novos sem trigger real (registrado no checkpoint 19:00 mas vale reiterar). (d) **Comandos terse ("siga")** disparam reflexo de "fazer algo proativo" mesmo sem escopo declarado novo. · **Causa-raiz comum:** princípio 11 honesto operacional — agente não detecta próprio overreach sem gate humano. · **Proposta:** **sem nova regra/ADR.** Vigilância apenas: "siga"/"ok" autorizam continuar escopo declarado, NÃO novo escopo. Critério "polish vs bloco" registrado como trigger futuro se padrão repetir (não preemptivo).
- **[2026-05-29T23:55] Method-audit (princípio 11 honesto / dogfood AIVI 6 gaps remanescentes):** Sessão paralela `test-aivi-isolated` identificou 9 gaps de processo. v1.13.0 absorve **3 com evidência empírica forte** (Gaps 4 RCA / 5 cobertura temporal pós-J4 / 8 handoff cross-sessão). **6 gaps remanescentes registrados aqui como method-audit aguardando 2ª ocorrência confirmatória** (não preemptivos): (1) ancoragem em artefato rotulado "validação" — propõe metodo-senior passo 1A hierarquia fontes; (2) fonte citada pela norma não buscada — propõe metodo-senior passo 1B inventário bloqueante; (3) delta=0 amostra ≠ prova correção — propõe qa-critic rule SE/ENTÃO regressão×correção; (6) campo oficial vazio ignorado — propõe anti-hallucination anti-pattern; (7) inferir autoridade de dado sem confirmar — propõe anti-hallucination anti-pattern; (9) telemetria por papel — parte tratável (timestamp output qa-critic) + parte infra externa harness. **Sem ação preemptiva.** Causa-raiz comum: padrões reais mas com 1 ocorrência só não justificam codificação (princípio 11 honesto operacional).
- **[2026-05-29T23:55] Method-audit (observação do dono sobre isolamento/modelo selection per role):** apenas `qa-critic` explicitamente isolado em subagente; PMO/discovery/architect/developer/docops compartilham contexto+modelo (mesmo viés cognitivo). `_meta/subagent-isolation.md` documenta política existente ("isolar reduz context rot mas elimina visão lateral; trade-off por papel"), modelo per role NÃO codificado. Observação do dono honesta e procedente: maior custo é fazer trabalho mal feito; otimização tokens vs qualidade upfront mal balanceada. **Registrado como candidato v1.14.0 se 2ª ocorrência confirmar** (não preemptivo).
- **[2026-05-29T23:30] Method-audit (princípio 13 SE/ENTÃO recém-codificadas vs minha própria execução):** Em v1.12.1 codifiquei SE/ENTÃO rules + 4 dimensões PC em qa-critic SKILL e **NÃO as apliquei pre-commit da própria v1.12.1**. Submeti para qa-critic sem RRC self-applied; round 1 detectou ALTO (citação ADR não-rastreável, dimensão "process compliance") + MEDIO (rule #1 falta qualificador, dimensão "doc consistência"). **Ambos teriam sido detectáveis por self-check com 4 dimensões antes de submeter.** Dono apontou: "1 round = lean" foi judgment não princípio; assertividade UPFRONT > rounds eficientes downstream. · **Causa-raiz:** pattern recorrente do princípio 11 honesto — agente codifica regra e não a aplica em si próprio. · **Proposta:** PRÉ-COMMIT self-check obrigatório (não opcional) — aplicar SE/ENTÃO rules + 4 dimensões PC ANTES de submeter qualquer bloco a qa-critic. **NÃO adicionar como regra (régua §0 — já está em qa-critic SKILL).** Apenas disciplina: trate qa-critic round como confirmação, não descoberta primária. · **Sem ADR; sem v1.12.2.** Apenas vigilância no próximo bloco.
- **[2026-05-30] Method-audit (princípio 11 / bootstrap):** `/start-session` rodou file-first sobre clone **41 commits atrás** (local v1.9.0 vs remoto v1.13.0); só detectado quando o dono perguntou "fez sync?". · **Causa-raiz:** file-first sem `git fetch` lê retrato congelado — prosa sem mecanismo (justamente o que a série v1.14.x ataca). · **Proposta (lean):** `start-session.md` passo 1 ganha `git fetch` + checagem ahead/behind ANTES de reconciliar WIP; ativação de modo deve ser **verificada** (ler de volta), não assumida. Persistido em `memory/feedback_bootstrap_nao_pode_falhar`. **→ RECORREU e foi codificado como mecanismo em ADR-019 (v1.19.0): hook `check-repo-sync` faz `git fetch`+auto-pull seguro no boot.** (ponteiro inverso method-audit→ADR; fecha Debt #5 da reconciliação 2026-05-30.) Firewall preservado.
- **[2026-05-30] Method-audit (ambiente / robustez do run autônomo):** batch grande de tool-calls em paralelo **cancelou ~50 calls em cascata** por 1 erro (`pwsh` ausente no PATH do bash), perdendo 2 ondas não-commitadas. · **Causa-raiz:** ausência de commit atômico por artefato + `pwsh` só acessível via tool PowerShell/Python `subprocess`. · **Proposta (lean):** commit após cada artefato lógico (git preserva contra cancel); batches pequenos sequenciais quando há dependência. Persistido em `memory/feedback_ambiente_buffer_pwsh`. Sem ADR (não é regra do framework; é disciplina operacional do ambiente Claude Code).
- **[2026-05-30T14:30] Method-audit (princípio 12 / vazamento de domínio RECORRENTE → prosa→mecanismo):** na reconciliação pós-merge, **eu mesmo vazei `ALCOA+` como se fosse o princípio** que justifica preservar o traço de pesquisa (era para ser rastreabilidade/proveniência **agnóstica**, P14). **O dono pegou — 2ª/3ª ocorrência** do mesmo padrão (1ª: README v1.11.0 `ALCOA+/ANP/FDA/BACEN/GAMP`, linhas 154 e 157(a) acima; ambas pegas pelo dono, nunca auto-detectadas). · **Causa-raiz:** Princípio 12 é **prosa**; agente que se auto-audita não detecta o próprio vazamento (viés, P11 honesto). Prosa repetida ≠ garantia — exatamente a tese da série v1.14.x. · **Decisão (executada, NÃO mais "candidato"):** o dono declarou explicitamente prosa→mecanismo → **ADR-020**: `tools/check_core_agnostic.py` (linter fail-closed que varre o NÚCLEO — `_shared/`, `.agent/skills/`, `AGENT-FRAMEWORK.md`, `CLAUDE.md`, `AGENTS.md` — por nomes de norma de domínio fora de contexto-exemplo) + denylist em `tools/` (infra, não-núcleo → não viola agnosticismo) + canário + wiring CI/boot. Fecha o risco residual de ADR-010 §Riscos ("detector de vazamento cross-projeto ausente"). Régua §0(c): destrava garantia inalcançável por prosa.

---

## Telemetria

> Coletor único de auto-observação (ADR-017, v1.17.0). **2 métricas que mudam decisão, nada além** (P5).
> Agregar no fim do bloco/dia, não por turno. Método: `_shared/observability` §Telemetria mínima.

### 17-A Blame (fluxo entre junções, por execução)
> Quando process-critic dispara rewind: registrar junção-origem (J0–J5) + rounds de qa-critic até PASS.

- 2026-05-30 (run v1.14.x): rounds de qa-critic por onda — O0=1, O1=2, O2=1, O3=1 (todos resolvidos como emenda DENTRO de J4 qa-critic→docops; **nenhum rewind cascata cross-junção** — forward-only preservado). Sinal: a montante (discovery/architect) não gerou spec rasa; achados foram de implementação, corrigidos em 1–2 rounds. **Nota honesta (P11):** a métrica 17-A "junção-origem do rewind" NÃO foi exercida nesta onda — nenhum rewind ocorreu; só o proxy `qa_rounds` rodou. Capacidade de blame-de-rewind = [INFERIDO/não-exercido] até um rewind real.
- 2026-05-30T14:30 (reconciliação pós-merge + ADR-020): process-critic adversarial (Sonnet isolado) sobre série mergeada — 6 achados (1 ALTO J4-corrigido, 2 ALTO confirmados, 2 MÉDIO, 2 BAIXO). **J4 do PMO refutou 1 achado do próprio crítico** (count errado) — 1ª evidência empírica de que a célula PMO-verifica-crítico pega false-PASS do crítico, não só do gerador. Bloco ADR-020 (mecanismo agnosticismo): rounds qa-critic registrar ao fechar.
- 2026-05-30T21:30 (v1.21.0 runtime hooks + entrega de produto): qa_rounds = **R1 REPROVADO** (1 ALTO + 2 MÉDIO + 2 BAIXO) → R2 **APROVADO_COM_RESSALVA** (1 BAIXO). **Nenhum rewind cross-junção** — os 5 achados foram resolvidos DENTRO de J4 (qa-critic→fix→re-qa = EMENDA), forward-only preservado. Sinal: o ALTO foi de **implementação** (template↔hook), não de decisão a montante — discovery/architect/ADRs não geraram spec rasa. Capacidade de blame-de-rewind segue [INFERIDO/não-exercido] (nenhum rewind real até hoje).

### 17-B Tally de regra + classe (uso ao longo de sessões)
> `regra — classe(salva-vidas|operacional|andaime) — disparou S/N — sem-disparo:K`. Poda só `andaime` quando K≥N (5–10).

- régua §0 (GANHO LÍQUIDO) — salva-vidas — S — sem-disparo:0 (rejeitou inflação/andaime em toda onda; ex.: _shared fora do contrato, matriz reprovada)
- qa-critic adversarial isolado/heterogêneo — salva-vidas — S — sem-disparo:0 (pegou false-PASS real em O0, O1, O2, O3; em v1.21.0 pegou ALTO template↔hook que 3 testes verdes do gerador escondiam)
- contrato mínimo (validate_skills) — operacional — S — sem-disparo:0 (gate 7/7 em cada onda)
- file-first — salva-vidas — S — sem-disparo:0 (violado no bootstrap → ver Aprendizado 2026-05-30)
