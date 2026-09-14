# Execution report — 2026-09-13 — carteira executiva e o slide que não cabia (Agidesk/Natulab)

> Rota: **squad** + `high-stakes-gate`. QA: **Opus adversarial isolado, primeiro plano** — reprovou.
> Entrega: `natulab-agidesk-projetos` PR #3 **merged** (`5f8efdb` → `9f6295e`).
> Terceiro bloco do dia; antes vieram o PR #1 (painel) e o PR #2 (one page por entregável).

## Placar

| | bloco 1 | bloco 2 | bloco 3 |
|---|---|---|---|
| Testes | 172 | 230 | **304** |
| Mutações | 39 | 67 | **95 — todas PEGAS** |
| Achados do QA | 6 ALTA | 4 ALTA + 7 MÉDIA | **3 ALTA + 7 MÉDIA** |

Suíte re-executada na árvore mergeada: **304 passed**.

## A lição central: restrição declarada não é restrição garantida

O dono escreveu uma restrição numérica e verificável: *"o one page deve caber em
um pptx para full hd a 125% de visualização"*. Disso sai, sem ambiguidade,
`1920/1,25 = 1536` × `1080/1,25 = 864` — 16:9 exato.

Eu escrevi as constantes. Eu escrevi um comentário dizendo que o corte de linhas
*"mantém a página dentro do slide"*. E a página media **1199px** — 39% além do
limite. Impressa, saía em **três** páginas.

O erro técnico é pequeno: `min-height` é **piso, não teto**. O erro de processo é
o que importa: **a restrição era mensurável e ninguém mediu.** Havia 289 testes,
todos sobre a lógica que produz os dados, e zero sobre a geometria que era a
promessa literal do pedido.

O conserto virou ferramenta — `ferramentas/medir_slide.py` renderiza em navegador
headless e devolve a altura real, com `exit 2` quando **não consegue medir**
(distinto de `exit 1`, "mediu e não coube"). Caminho medido, um passo por vez:

| passo | altura |
|---|---|
| como estava | 1199px |
| régua do Gantt corrigida | 1142px |
| densidade | 940px |
| corte em 4 linhas | 912px |
| identificação absorvida pelo cabeçalho | 902px |
| últimas entregas/riscos/oportunidades → página 2 | **864px** |

> **Regra que fica:** quando o pedido do dono contém um número, o número vira
> gate executável no mesmo bloco — não comentário no código.

## O bug que só a medição revelou

`.g-corpo>div` punha o rótulo **e** o trilho do Gantt em linhas próprias de
largura total, em vez de duas colunas. As barras eram desenhadas numa régua
(x=46) e o eixo de datas e a linha do "hoje" em outra (x=236).

**Uma entrega que termina depois de hoje era desenhada terminando antes.**

O gráfico mostrava o contrário do dado — exatamente a doença do Gantt do APOEMA
que este módulo existe para não repetir. Pré-existente desde o bloco anterior, e
invisível para os 289 testes, porque **teste de lógica não vê layout**. Só
apareceu porque alguém renderizou.

## Lições por skill

### architect
- **Painel de carteira não pode ter métrica própria.** A carteira é projeção
  lateral do que o one page já calcula; qualquer número novo na visão agregada é
  uma segunda verdade esperando contradizer a primeira. O QA achou a contradição
  exata: carteira dizia `NORMAL` onde o one page do **mesmo projeto** dizia
  `ATENÇÃO`. O one page já tinha sido consertado no bloco 2 *"para o relatório
  não se contradizer"* — e o painel reintroduziu a contradição um nível acima.
  Conserto: `entregas.status_geral()` como fonte única dos dois.
- **Descoberta por evidência, não por catálogo.** Um projeto é *uma pasta com
  `backlog.json`*. Catálogo separado é mais um registro para derivar da realidade.
- **CTA não é navegação.** "Ver detalhes" não é chamada à ação. CTA nomeia
  **verbo + objeto + com quem**, e sai **uma só** por projeto — duas já viram
  lista, e lista é o relatório de que o executivo estava fugindo.

### developer
- **Ausência precisa de estado próprio.** Projeto sem nenhuma data dava desvio
  0,0 e o farol devolvia `NORMAL`: o projeto mais descuidado da carteira aparecia
  como o mais saudável. Daí `SEM PRAZO` como estado explícito. **Este achado veio
  da pesquisa do DGO 360 OPER**, onde 11% a 40% das linhas caem em `SEM_META` e a
  Sobreestadia fica verde por estrutura — fui conferir no meu código e era pior.
- **`UnicodeDecodeError` não é `JSONDecodeError`.** Um `backlog.json` em UTF-16 —
  **o default do PowerShell 5.1**, que é o shell desta casa — derrubava o painel
  inteiro: nenhum HTML gravado, todos os outros projetos sumindo junto. `except
  Exception` por linha é largo **por desenho**: numa varredura de N projetos, a
  falha de um é dado, não exceção.
- **Ordem de arquivo não é ordem.** O destinatário da cobrança mudava com a ordem
  do `backlog.json` (o `sort` é estável, e o arquivo vem sincronizado do portal).
  A **mesma** cobrança chegava a pessoas diferentes em dois dias, sem nada na tela
  deixando ver que houve escolha. Desempate determinístico explícito.
- **Falta de dado é sufixo, não substituição.** "Repactuar Go-live — venceu há 43
  dias" virava "Definir responsável de Go-live", e o fato mais caro da linha
  **desaparecia**. Preencher o buraco não pode apagar o motivo.

### qa-critic
- **O achado mais duro do dia:** *"83/83 PEGA mede as sabotagens que o autor
  escolheu, não a força da suíte."* **Sete das dez mutações escritas pelo QA
  passaram pelos 289 testes.** A contagem própria de mutação é auto-avaliação; o
  número só vale contra sabotagens de terceiro.
- **Teste auto-referente, terceira ocorrência.** A fixture lia a própria constante
  (`ENTREGAS_NO_GANTT + 3`, `PROJETOS_POR_PAGINA + 1`), então se ajustava a
  qualquer mutação dela. Escrevi isso **depois** de o QA já ter apontado
  exatamente esse erro no teste do CSV, no bloco anterior. Correção de classe não
  se propagou para o código novo do mesmo bloco — que é literalmente o que a regra
  *lições propagam a todos os fluxos* manda fazer.
- **QA que renderiza acha o que QA que lê não acha.** Os dois achados mais caros
  (slide e Gantt) exigiram executar o artefato, não revisar o fonte.

### explorer
- **Pesquisar a referência do dono muda o código, não só a documentação.** Ler o
  DGO 360 OPER a fundo produziu um bug real no meu código (o falso verde). E
  produziu também a lista do que **não** transferir, com motivo escrito: média de
  % entre projetos (não tem semântica), cascata de meta da hierarquia (é a causa
  do verde estrutural), sparkline e variação mês a mês (exigem snapshots).
- **Não achar é resultado.** O MEREO ficou de fora: a busca não achou artefato,
  só referências. Descrever um layout que ninguém viu seria fabricação — a mesma
  classe do incidente registrado em `fabricacao-em-prosa-e-o-ponto-cego`.

### docops
- **Link, nunca cópia.** O rodapé aponta TAP/5W2H, escopo, backlog e portal, de
  `projeto.json.documentos`; chave ausente = nenhum link. Há teste provando que o
  escopo **não** é copiado para dentro da página: duas cópias do escopo são duas
  verdades.
- **Mensagem de erro precisa distinguir "errado" de "ainda não".** O `termo.py`
  acusava esquema inválido quando o problema era *"você ainda não preencheu"* — e
  o gatilho era o **exemplo do próprio repo**.

## Custo de processo que virou ferramenta

`provar_mutacao.py` passou a **validar todas as âncoras antes** de clonar o repo
95 vezes. Âncora obsoleta custava ~90s cada e só aparecia no fim da rodada: **4
de 8 "escapes" de uma execução eram isso**, não teste fraco. O pré-check pegou
uma âncora morta logo na primeira execução.

## Fronteira — o que NÃO foi entregue, e por quê

Quatro pedidos do dono continuam abertos, e são **uma dívida só**: "interligável
com Agidesk", "Agidesk reflete o one page", "reorganizar sem destruir
conhecimento" e "docs/andamento/portal alinhados". Todos dependem da **ponte com
o portal** + **ledger de procedência de existência**. Marcados como ❌ no placar
entregue ao dono, não como "parcial".

Registrado em `~/.claude/trabalhos/agidesk-skill-projetos-natulab.md`, com as
seis decisões do dono que seguem em aberto.
