# Andamento — sessão de 23/09/2026: abertura, limpeza de boot e alinhamento de 5 sessões

**Escopo:** o que esta sessão (`FRAMEWORK [61ce85]`) fez desde o `iniciar`. Não cobre o projeto
inteiro nem o backlog do framework — para isso, `history.md` e `python tools/trabalhos.py listar`.
**Atualizado:** 23/09/2026 · **Modelo:** autor `claude-opus-5` · QA adversarial `sonnet` isolado,
1 rodada, **REPROVADA** (3 ALTA + 1 MEDIA) — as correções estão aplicadas e declaradas no fim.
**Formato:** o painel de fases aprovado pelo dono em 21/09 (`ANDAMENTO-API-SAC.md`).

> **Os percentuais desta versão são DERIVADOS, não digitados.** Cada fase mostra `(concluídos/total)`
> ao lado do número, e a barra tem 12 blocos = `round(% × 12/100)`. Qualquer leitor pode conferir
> contando os `[✓]` da própria fase. Na primeira versão deste arquivo eles foram digitados a olho, e
> o QA adversarial provou que dois mentiam por 10 e 11 pontos — no mesmo documento em que eu
> denunciava a dívida `painel-de-fase-gerado`, que é exatamente sobre isso.

---

## Onde estamos, em uma linha

> **A limpeza acabou, o PR mergeou, e o dia produziu um achado maior que a tarefa.** Os dois
> registros obsoletos foram tratados e o commit represado entrou na main (`efa7374`). No caminho,
> o cruzamento de plataformas do mesmo commit revelou que **a regra central do ADR-115 — a união
> por caminho — não tem teste que a distinga de um `any`**, e que o único check capaz de barrar
> merge é estruturalmente cego para isso. E **5 sessões vivas** na mesma árvore passaram a operar
> sob regras comuns depois de três correções mútuas.

---

## O cronograma

```
FASE 1 · ABERTURA DE SESSÃO (protocolo PMO)              (5/5) ████████████ 100%
  [✓] 23/09  modo = dev (master canônico) · repo_mode.py
  [✓] 23/09  git fetch --prune · main sincronizada com origin (0/0)
  [✓] 23/09  boot_check OK · 2 skips DECLARADOS (cross-ai, env-applicability)
  [✓] 23/09  history.md lido pelo topo · handoff.py gerado
  [✓] 23/09  WIP reconciliado: 37 trabalhos, 2 com afirmação obsoleta

FASE 2 · LIMPEZA DO BACKLOG DE BOOT                      (4/4) ████████████ 100%
  [✓] 23/09  adr-113-veredito-aprovativo → TRATADO (o bloco entrou em 5305ae2)
  [✓] 23/09  skill-service-valuation → título corrigido, registro MANTIDO ABERTO
  [✓] 23/09  decisão do dono: atualizar, não fechar (preserva a ressalva do caso H-01)
  [✓] 23/09  1 registro fechado (37 → 36) · `criado:` preservado nos dois

FASE 3 · PUBLICAR O COMMIT REPRESADO                     (7/7) ████████████ 100%
  [✓] 23/09  cabeçalho do arquivo corrigido (afirmava sobre si que estava untracked)
  [✓] 23/09  commit 4584462 por CAMINHO EXPLÍCITO — índice alheio preservado
  [✓] 23/09  push direto na main RECUSADO pelo servidor (GH006, branch protegida)
  [✓] 23/09  branch docs/intake-bloco3-linkedin criada SEM checkout (HEAD é compartilhado)
  [✓] 23/09  PR #142 aberto
  [✓] 23/09  canarios-local = success no sha 4584462 (88 PASS · 1 SKIP · 0 FAIL)
  [✓] 23/09  MERGEADO como efa7374 · branch deletada · origin/main em dia

FASE 4 · ALINHAMENTO DAS 5 SESSÕES VIVAS                 (9/9) ████████████ 100%
  [✓] 23/09  ListAgents: 4 interativas no framework + 1 Remote Control (PR #140)
  [✓] 23/09  mensagem enviada às 4 · as 4 responderam
  [✓] 23/09  `da`  → NÚCLEO: canário de workflows (test_skill_contract.py, +215/-3)
  [✓] 23/09  `c4`  → NÚCLEO: RUNBOOK §3.2 em _shared/project-docs/SKILL.md
  [✓] 23/09  `5e`  → DOMÍNIO: CAPA GQ (capa-sharepoint)
  [✓] 23/09  `67`  → DOMÍNIO: budget-opex (OPEX, entregável a diretor hoje)
  [✓] 23/09  escopo corrigido PELO DONO: unificar só quem MELHORA o framework
  [✓] 23/09  ordem dos PRs acordada: o meu primeiro (squash reescreveria o SHA)
  [✓] 23/09  bastão do núcleo aceito por esta sessão, após `da` fechar o canário

FASE 5 · RELATÓRIO NO FORMATO COBRADO                    (5/6) ██████████░░  83%
  [✓] 23/09  precedente localizado: migracao-sac/docs/ANDAMENTO-API-SAC.md
  [✓] 23/09  dívida correspondente achada: painel-de-fase-gerado (aberto 21/09)
  [✓] 23/09  v1 escrita nas 4 partes do formato aprovado
  [✓] 23/09  QA adversarial isolado rodado — REPROVOU com 3 ALTA + 1 MEDIA
  [✓] 23/09  v2: percentuais DERIVADOS, procedência rebaixada, achados incorporados
  [ ]        commit deste arquivo

FASE 6 · O ACHADO DO GATE (união × any)                  (3/6) ██████░░░░░░  50%
  [✓] 23/09  cruzamento de plataformas no MESMO sha 4584462:
             Windows local  88 PASS · 1 SKIP · 0 FAIL  → 37/37 mortas, merge liberado
             GHA ubuntu     88 PASS · 0 SKIP · 1 FAIL  → 36/37, 2 execuções, mesmo resultado
             GHA macos/win  pass
  [✓] 23/09  registrado: uniao-por-caminho-sem-teste-que-distinga
  [✓] 23/09  atribuição CONFIRMADA por linha literal, após a `da` contestar:
             "FALHARAM: test_mutacao_squad_gate.py" · "SOBREVIVEU: uniao vira `any`"
             · "PASS test_parity.py" · "0 SKIP" — o canário NÃO pula no Windows
  [ ]        rodar o canário num Linux imprimindo os `escopo_paths` efetivos de cada
             veredito da fixture, nos dois ramos — decide a hipótese sem adivinhar
  [ ]        escrever o teste que MATA a mutação (aceite: trocar união por any → VERMELHO)
  [ ]        decidir com o dono o que fazer com a cegueira de plataforma do ADR-088

FASE 7 · PRÓXIMO BLOCO — simetria de `trabalhos.py`      (2/5) █████░░░░░░░  40%
  [✓] 23/09  3 portas de perda medidas por 3 sessões (ver tabela abaixo)
  [✓] 23/09  fixture de reprodução da `5e` disponível (4 casos, 3 perdem)
  [ ]        decisão de desenho do dono
  [ ]        implementação (`_escrever` simétrico a `_ler`, ou parser com chave própria)
  [ ]        canário que reintroduza OS TRÊS gatilhos, não um
  ← ESTAMOS AQUI: bastão do núcleo aceito, esperando `da` fechar o canário dela
```

---

## De onde saímos → onde chegamos

| Na abertura se achava | Hoje se sabe | Como |
|---|---|---|
| 1 registro com afirmação obsoleta | **2** — o do ADR-114 também. Só 1 foi FECHADO; o outro ficou aberto porque tinha resíduo real | leitura dos 37 registros, não do resumo |
| fechar o registro gera commit | **não gera** — mora em `~/.claude/trabalhos/`, fora do repo | `tools/trabalhos.py:40` (ADR-100) |
| docs-only vai direto na main | **main é protegida** — GH006 do servidor, exige PR + `canarios-local` | o push falhou; eu tinha assumido |
| uma outra sessão na árvore | **quatro** + 1 Remote Control; 2 no núcleo, 2 em domínio | ListAgents + as 4 respostas |
| `_shared/project-docs/SKILL.md` é passivo órfão | **bloco vivo da `c4`**, e já foi DESTRUÍDO uma vez hoje | `c4` reivindicou; `git reflog` confirma o `reset` |
| `--force` do trabalhos.py preserva | **3 portas de perda**, nenhuma com aviso | ver tabela própria abaixo |
| o status do canário certifica o que rodou | **certifica o HEAD, roda a árvore suja** — e o PR #142 foi calculado com 215 linhas de outra sessão dentro | registrado em `status-certifica-commit-testa-arvore` |
| canário verde = mecanismo provado | **a união do ADR-115 não é distinguível de um `any`** | mutação `0→0 falhas`, GHA ubuntu |
| o canário que falha no Linux é o que pula no Windows | **falso — ele roda nos dois e só discrimina num**: Windows 37/37, ubuntu 36/37. Pior que a versão anterior deste relatório dizia | a `da` contestou; a linha literal do log deu razão a ela |

---

## `trabalhos.py` — três portas de perda, três sessões, nenhuma certa sozinha

| Caso | Comportamento | Quem provou |
|---|---|---|
| Seção `## ` não-canônica, **sem** passar a flag daquela seção | **preservada** (absorvida na canônica anterior) | eu, por leitura; `5e` por fixture (caso C) |
| Seção `## ` não-canônica, **passando** a flag (`--feito`) | **DESTRUÍDA** — `secoes[chave] = valor` sobrescreve o absorvido | `5e`, por fixture (caso B) |
| Conteúdo **antes** do primeiro título canônico | **DESTRUÍDA** | eu, por leitura; `5e` confirmou (caso A) — era o caso real dela |
| Chave de frontmatter fora das 6 de `CAMPOS` | **DESTRUÍDA** | `5e` por acidente; `da` e eu confirmamos (caso D) |

**A causa, em uma frase:** `_escrever` não é simétrico a `_ler` — o leitor aceita mais do que o
escritor sabe regravar, e a diferença some com exit 0. **`--force` não é o gatilho**: ele só libera
a sobrescrita quando o `--nome` diverge; a perda acontece igual sem ele.

**Meu registro não perdeu nada**, e a prova é independente do código em questão: `cmd_mostrar`
imprime o arquivo **cru** (`print(f.read())`), rodei antes de escrever, e a saída tinha só as 6
chaves e as 3 seções canônicas. Se tivesse algo fora do canônico, essa prova não veria a perda.

---

## O que o QA adversarial me reprovou, e o que mudou

| # | Achado | Veredito meu | O que fiz |
|---|---|---|---|
| 1 | ALTA — FASE 3 dizia 60% com 5/7 itens (71%); FASE 5 dizia 85% com 3/4 (75%) | **procede, e é o pior** | percentuais agora derivados, com `(n/total)` exposto |
| 2 | ALTA — Procedência dizia CONFIRMADO a autoria do SKILL.md que o próprio texto dava como desconhecida | **procede** | a `c4` reivindicou depois; agora é CONFIRMADO **com** a evidência certa |
| 3 | ALTA — a contaminação do status já era fato registrado e o relatório tratava como hipótese | **procede** | virou linha da tabela e FASE 6 |
| 4 | MEDIA — "2 registros obsoletos" contradizia manter um aberto | **procede** | reescrito: 2 com afirmação obsoleta, 1 fechado |

**Onde o QA errou, e digo por justiça:** ele marcou como não verificável a recusa `GH006` do push,
por não achar rastro no reflog. Rastro não existe mesmo — push recusado não deixa reflog local. A
evidência é a resposta do servidor, que está na transcrição da sessão e não no repositório.

---

## Procedência

| Afirmação | Origem | Classificação |
|---|---|---|
| ADR-113/114 entregues em 5305ae2 (137 arq., 22.649 ins.) | `git show --stat`; ADRs em Aceito | CONFIRMADO |
| main protegida, exige `canarios-local` | resposta GH006 + `gh api .../protection` | CONFIRMADO |
| PR #142 mergeado como `efa7374` | `gh pr view 142` · `git log origin/main` | CONFIRMADO |
| 5 sessões, 2 no núcleo e 2 em domínio | as 4 responderam nominalmente | CONFIRMADO |
| SKILL.md é da `c4` (RUNBOOK §3.2) | `c4` reivindicou; `da`, `5e` e `67` negaram | CONFIRMADO |
| as 47 linhas foram destruídas por um `reset` hoje | `git reflog` HEAD@{4} + relato da `c4` | CONFIRMADO |
| a mutação `união → any` sobrevive | log do GHA: `SOBREVIVEU (0->0 falhas)` | CONFIRMADO |
| o `.md` do PR #142 CAUSOU o FAIL no ubuntu | main passava, meu sha falha — mas o nexo não foi testado | **DESCONHECIDO** |
| a hipótese do fixture que lê o repo | raciocínio meu, não reproduzido | INFERIDO |
| `da` termina em ~20 min | estimativa dela | INFERIDO |
