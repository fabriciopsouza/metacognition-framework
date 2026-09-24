# Andamento — 24/09/2026: pacote do Sistema de Pesagem, e o gate que comparava o artefato com o próprio gerador

> Execution-report de encerramento de bloco (ADR-038/052/062 · tier **OWNER** · privado,
> não distribuído). Preenchido à mão: `tools/execution_report.py` entrega o esqueleto e a
> contagem de tokens dele é **agregada de vários transcripts**, não deste bloco.

## Onde estamos, em uma linha

Entregue o pacote de estruturação do projeto **Sistema de Pesagem** (Natulab) em repo
próprio (`C:\Users\fabriciosouza\sistema-pesagem`, 3 commits, local e sem remoto), a partir
da ERU `A1-GQ.01.036 v.01` e de uma transcrição de reunião que **não registra a reunião**.
O núcleo do framework não foi tocado — o write-isolation do ADR-070 valeu na prática.

## Métricas

| Métrica | Valor |
|---|---|
| Tokens | **NÃO MEDIDO CONFIAVELMENTE.** O `--from-transcripts` devolveu `output 25.680.271`, que é agregado de vários transcripts e não deste bloco. Registrar o número como se fosse do bloco seria a fabricação por conveniência que o próprio framework caça. |
| Commits | 3 (`f8d1e58` estrutura · `5097670` QA · `267e40d` prompt de retomada) |
| Arquivos entregues | 12 markdown + 3 python + 2 fontes + 5 provas |
| Gates criados | 6 (verificador único) · 8 invariantes no extrator |
| Casos de teste | 17 (12 provam que barra, 5 contraprovas) |
| Rodadas de retrabalho | 1 rodada de QA adversarial + 3 consertos em cascata dentro dela |

## De onde saímos → onde chegamos

**Pedido:** estruturar o projeto a partir da ERU e dos direcionamentos da reunião, sem fixar
prazo nem atribuir tarefa, porque o dono **não é o executor**.

**O que mudou o trabalho antes de ele começar:** a transcrição da reunião cobre **3 dos 96
minutos** (lacuna única de 69min46s; as falas de uma participante saíram em inglês, idioma
errado no canal de áudio). Ou seja, a metade do pedido — "os direcionamentos vistos na
reunião" — **não tinha fonte**. Medi e declarei DESCONHECIDO em vez de preencher com prosa
plausível. Quando o dono reafirmou que a transcrição estava na pasta, mostrei a medição (30
marcas de tempo, o salto de 0:01:15 para 1:11:01) em vez de recuar ou de insistir sem
número.

**O que substituiu a fonte perdida:** 29 perguntas em 8 blocos, cada uma dizendo o que muda
na decisão. A lacuna virou pauta, não invenção.

**O que a ERU revelou:** 13 achados (8 ALTA). Os três que governam o projeto não estão em
nenhum documento oficial como risco — conectividade não declarada das 8 balanças (se alguma
não tiver saída de dados, o projeto ganha CAPEX de equipamento), `A.6.6.33` cálculo de
TEOR sem fórmula (altera quantidade de ativo, logo erro de dose), e integração SAP/EWM sem
dono do lado SAP.

## O placar gate × achado (quem pegou o quê)

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Transcrição cobre 3 de 96 min | **eu**, medindo antes de usar a fonte | **nenhum** — não existe gate de qualidade de fonte |
| ERU com 7 campos de assinatura vazios | **eu**, lendo o PDF | nenhum |
| **Matriz com 16 de 76 linhas contaminadas** pelo cabeçalho da página | **QA adversarial** (modelo ≠ autor) | **G5 não podia pegar: é tautológico** — compara o arquivo com o que o gerador produz, e o defeito estava no gerador. Hoje: `I7` |
| `"O"` de "O sistema" lido como GRAU | **`I2`**, o invariante mais chato do extrator | `I2` — **o gate funcionou** |
| Palavra `"no"` confundida com o N-ordinal do cabeçalho | **`I2`** | `I2` — funcionou de novo, no conserto do conserto |
| 19/57 anotações quando eram 20/56 | QA adversarial | nenhum → hoje `G6` |
| 24 perguntas quando eram 29 | QA adversarial | nenhum → hoje `G6` |
| 14 riscos quando eram 15 | **eu**, contando | nenhum → hoje `G6` |
| 3 crenças refutadas quando eram 5 | **eu** | nenhum → hoje `G6` |
| **`G6` nasceu com chave morta** (contava crenças e nunca comparava) | **eu**, ao exercitar a checagem contra um número errado de propósito | nenhum → hoje rede anti-chave-órfã **com teste** |
| Slugger removendo acento (falso positivo do `G1`) | `G1` acusou 2 links; investigar mostrou que o **gate** errava, não os links | faltava contraprova → hoje teste de slug |
| 3 citações com aspas que eram paráfrase | QA adversarial | nenhum — **não mecanizável**, é leitura |
| 3 nomes de funcionários internos em peça destinada a sair da casa | QA adversarial | nenhum |
| Controle de mudanças ausente da ERU **e** do pacote | QA adversarial | nenhum |
| `git checkout -- RISCOS.md` apagou minha edição não commitada | **eu**, ao ver `falhas: []` onde devia haver falha | o classificador de ação não barra `checkout` de arquivo do próprio autor |

## Detecção: framework × humano

- **Mecanismo pegou 2 dos 3 defeitos mais graves do extrator** — e os dois eram invisíveis a
  olho nu, porque produziam saída plausível. `I2` (exigir TIPO e GRAU legíveis em todos os
  76) pagou o aluguel exatamente quando mexi no código que o alimenta.
- **O crítico adversarial pegou o que mecanismo nenhum podia** — o defeito dentro do próprio
  gerador. É a evidência mais limpa de por que o QA é por modelo diferente do autor: eu
  rodei os 5 gates, todos PASS, e teria fechado o bloco.
- **Eu peguei o que era contagem e o que era conduta** — os números em prosa e o comando
  destrutivo que usei contra meu próprio trabalho.

## O que eu errei, e o que derrubou cada erro

1. **Contei em prosa quatro vezes errado** (anotações, perguntas, riscos, crenças). Não é
   descuido isolado: **é a regra de dono único por fato sendo violada por mim, no pacote que
   prega essa regra**. Derrubou: o QA nas duas primeiras, eu nas duas seguintes. Resposta:
   `G6` compara afirmação com realidade — e onde a contagem é volátil (casos de teste),
   **parei de afirmá-la** em vez de perseguir o número.
2. **Consertei o parser com regex de remoção** (`re.sub` com `.*?` e `re.S`), que comeu
   texto real: `A.6.1.7` perdeu o "O" inicial. Derrubou: conferência de amostra contra o
   PDF. Resposta: cortar na primeira linha de moldura, não remover padrões.
3. **A segunda tentativa reconheceu moldura por prefixo e sem caixa**, e o padrão do
   N-ordinal casou com a palavra "no". Dois requisitos perderam classificação e as contagens
   caíram para 51/23. Derrubou: `I2`.
4. **`git checkout -- RISCOS.md`** para desfazer um `replace` mal feito — apaguei minha
   própria edição não commitada. Recuperável do contexto, mas é o padrão destrutivo que eu
   mesmo registro como proibido. Derrubou: nada automático; eu vi a perda no grep seguinte.
5. **Escrevi `> #` no início de um comentário Python**, quebrando o arquivo — lixo de
   markdown vazando para código. Derrubou: a leitura imediata.

## Gaps (flagados, não silenciados)

- **Não existe gate de qualidade de fonte.** Uma transcrição plausível e vazia passa por
  todos os gates do framework, porque nenhum deles pergunta "esta fonte cobre o que diz
  cobrir?". Neste bloco a medição foi manual e por iniciativa. Candidato fraco a
  mecanismo genérico (a medida é específica por tipo de fonte); registro como **gap
  conhecido**, não como débito com prazo.
- **Citação literal não é mecanizável por gate simples**, e foi onde o QA achou 3 defeitos.
  Verificar aspas contra a fonte exige a fonte em texto — que neste projeto existe, e por
  isso o `I8` cobre o corpo dos requisitos, mas **não** cobre citações dentro de prosa.

## Melhorias candidatas (régua §0 — nenhuma promovida)

- **O padrão do `G6`** (número afirmado em prosa × número real contado no conteúdo) é o
  candidato mais forte que saiu deste bloco, porque o defeito que ele pega apareceu **4
  vezes em um único bloco**. Mas veio de **um** projeto: promover agora seria a adição
  preemptiva que a régua §0 rejeita. **Quitação:** ao segundo projeto que sofrer o mesmo
  defeito, comparar as duas instâncias e promover o que sobreviver a ambas.
- **`I8` (todo corpo aparece literalmente na fonte)** generaliza para qualquer artefato
  gerado a partir de documento. Mesma régua, mesma espera.

## Boas práticas (reutilizável)

- **Exercitar o gate contra entrada que deve reprovar, no mesmo bloco em que ele nasce.**
  Foi assim que descobri a chave morta do `G6` — um gate que passava sem comparar nada.
- **Quando o gate acusa, suspeitar do gate antes do conteúdo.** Os 2 links que o `G1`
  reprovou estavam corretos; o slugger estava errado. Gate com falso positivo é gate que
  alguém desliga.
- **Fonte copiada para dentro do repo com sha256 registrado em arquivo dono único.** A pasta
  de origem era `Downloads`, que é área de passagem.

## Lições por skill (agnóstico de domínio)

- **qa-critic:** *gate que compara um artefato com o próprio gerador é tautológico.* Passa
  sempre que o defeito está no gerador — e é onde os defeitos estão. Todo gate de
  "artefato == gerado agora" precisa de um irmão que compare o artefato com a **fonte**.
- **developer:** *conserto de parser por regex de remoção come texto real.* Preferir cortar
  (truncar no primeiro marcador) a remover (substituir padrões), e nunca usar `.*?` com
  `re.S` atravessando fronteira de registro.
- **docops:** *número dentro de prosa é dono duplicado.* Ou a comparação é mecanizada, ou a
  afirmação sai do texto e fica no comando que a imprime.
- **discovery:** *fonte que parece fonte é pior que fonte ausente.* Medir cobertura antes de
  extrair conclusão — e quando o dono reafirmar a fonte, responder com a medição, não com
  recuo nem com insistência.
- **architect:** *invariante entediante sobre campo obrigatório é o que pega o defeito do
  refactor.* `I2` só exige "todo requisito tem tipo e grau legíveis", e foi ele que salvou
  duas vezes.

## Procedência

- Repo do domínio: `C:\Users\fabriciosouza\sistema-pesagem` — 3 commits, branch `main`,
  local, **sem remoto** (publicar é decisão em aberto D7).
- Framework: `main` @ `ec9d573`, **limpo e 0/0 com origin** ao fim do bloco; nada escrito no
  núcleo além deste report.
- Gates inertes desta sessão (ADR-061), aplicados à mão: `check-repo-sync` → `git fetch
  --prune` + `status` = 0/0 · `check-core-agnostic` → `python tools/check_core_agnostic.py`
  = PASS (norma).
- Registro persistente: `python tools/trabalhos.py mostrar --slug sistema-pesagem-natulab`.
- QA adversarial: modelo um degrau abaixo do autor (autor Opus 5 → crítico Sonnet), com
  instrução de encontrar defeito. Veredito: **aprovar com ressalvas**, 1 ALTA + 8
  MÉDIA/BAIXA, todas endereçadas no commit `5097670`.
- **O que este report não mede:** tokens, tempo de parede e turnos. O gerador não os entrega
  por bloco, e estimar seria inventar.
