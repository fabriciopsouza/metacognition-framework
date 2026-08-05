# ADR-100 — Registro de trabalhos: o handoff sobrevive à sessão e é oferecido até ser tratado

- Status: **Aceito** (2026-08-03 — pedido do dono: *"o handoff não deve ser perdido se eu iniciar os
  trabalhos, mas deve ser oferecido até que eu trate o assunto"*)
- Decisores: dono + squad (architect) · Pré-gate: qa-critic heterogêneo isolado
- Tags: handoff, boot, continuidade, P14

## Contexto — o gap é real e foi medido

O Pacote P14 (ADR-012) e seu gerador determinístico (`tools/handoff.py`, ADR-076) resolvem **o que
o handoff contém**. Não resolvem **o que acontece com ele depois**: o pacote é gerado, exibido no
chat e **perdido**. A próxima sessão não é lembrada de que existe trabalho aguardando decisão.

Consequência observada na própria sessão que originou este ADR: um trabalho de validação com
2,88 milhões de comparações, 17 objetos pendentes e três decisões esperando o dono terminaria sem
nenhum mecanismo que o trouxesse de volta — dependeria de o dono lembrar, ou de reconstituir o
estado lendo commits.

**O que já existia e por que não bastava:**

| Mecanismo | O que faz | Por que não resolve |
|---|---|---|
| `tools/handoff.py` (ADR-076) | Gera o Pacote P14 do estado do repo | Efêmero: gera e descarta. Um repo por vez |
| `cross_ai_hub.py` boot-scan (ADR-069) | Oferece handoffs abertos **entre IAs** | Escopo é comunicação entre agentes, não os trabalhos do dono. Exige hub externo clonado |
| `history.md` `## Em aberto` (ADR-007) | WIP do repositório | Preso a um repo; some ao abrir outra pasta |

## Decisão

Registro **persistente, por trabalho, fora do repositório**, oferecido no boot enquanto estiver
aberto.

**Local:** `~/.claude/trabalhos/<slug>.md` — fora do repositório de propósito: um trabalho pode
envolver vários repositórios (o caso que originou o ADR envolve dois), e não pode depender de qual
pasta foi aberta.

**Organização por trabalho, não por repo nem por sessão.** Cada registro responde, nesta ordem:

1. **Qual é o trabalho** e **onde** ele vive;
2. **Para que serve** — o objetivo, em uma linha;
3. **O que foi feito** — resumo com os números que sustentam;
4. **O que está pendente**;
5. **Próximo passo — e o que ele decide.**

**Ciclo de vida:** `aberto` → `tratado`. Enquanto `aberto`, **reaparece a cada sessão**. Só o dono
encerra (`trabalhos.py tratar`), porque quem executa não decide que a pendência do dono acabou.

**Dois pontos de integração**, e os dois são necessários:

- `boot_check.py` ganha o gate `trabalhos-abertos` — **nunca falha o boot** (trabalho pendente é
  informação, não erro) e **nunca fica silencioso**: "nenhum aberto" é resultado declarado.
- O workflow `start-session` obriga o agente a **mencionar na resposta de abertura**. Registro que
  existe e não é oferecido é igual a não existir — e essa é justamente a falha que o ADR corrige.

## Régua §0 (ADR-007) — por qual porta passa

Porta **(c): destrava o uso de mecanismo existente**. O P14 já é gerado e já é completo; sem
persistência ele é produzido e descartado, e o custo de reconstituir estado a cada sessão é o que
este registro elimina. Não reimplementa o gerador: o conteúdo técnico continua vindo de
`handoff.py`. Este módulo **guarda e oferece**.

## Alternativas consideradas

1. **Estender `history.md ## Em aberto`** — rejeitada: é por repositório. Um trabalho com dois
   repositórios ficaria partido, e mudar de pasta esconderia a pendência.
2. **Usar o hub cross-IA** — rejeitada: o hub existe para handoff **entre agentes**, exige clone
   externo e endereçamento por destinatário. Um trabalho do dono não tem destinatário-agente.
3. **Bloquear o boot enquanto houver trabalho aberto** — rejeitada: transformaria informação em
   obstáculo e treinaria o dono a ignorar o aviso. Oferece-se; não se obstrui.

## Consequências

**Positivas.** O handoff deixa de depender de memória humana. O `boot_check` **garante que o
trabalho aberto seja exibido** a cada sessão. O formato uniforme torna comparável o estado de
trabalhos diferentes.

> A garantia mecânica para na **exibição**. Que o agente *comente* o trabalho na resposta de
> abertura é norma do `start-session`, **sem verificador** — por isso a capacidade está registrada
> como `advisory`, não como garantida. Afirmar "a abertura passa a ter continuidade explícita"
> seria superafirmar: o boot mostra; comentar depende do agente.

**Negativas, declaradas.**

1. **Não é portátil entre máquinas.** `~/.claude/trabalhos/` é local e não versionado: um trabalho
   registrado num PC **não aparece** no boot de outro. O framework trata multi-PC como problema
   real em outros pontos (gates de sync, `bootstrap.ps1`), e aqui a limitação é aceita como preço
   de ser cross-repositório. Quem trabalha em mais de uma máquina precisa saber disso.
2. **Não é versionado nem tem backup.** Some com a máquina.
3. **Registro desatualizado é pior que ausente** — se o dono tratar o assunto e ninguém marcar
   `tratado`, o aviso vira ruído e treina a ignorá-lo. Mitigação: o `listar` sempre mostra o
   comando de encerramento.
4. **O conteúdo é escrito pelo agente** — a qualidade do resumo não é mecanizável, só o ciclo de
   vida é.
5. ⚠️ **Fica FORA dos gates de agnosticismo do núcleo.** `check_core_agnostic.py` não alcança
   `~/.claude/`. Texto de domínio colado verbatim ali — nome de cliente, valor, identificador —
   não é barrado por mecanismo algum. Dado o histórico (o repositório virou privado depois de um
   vazamento de dado de cliente), a regra é: **descrever, não colar**. O registro guarda *estado
   do trabalho*, não amostra de dado.

## Pendências

- O registro não valida se o "o que foi feito" corresponde ao estado real do repositório. Um gate
  futuro poderia cruzar com `handoff.py` e acusar divergência.
- O parser de frontmatter é o terceiro do repositório (`cross_ai_hub.py` e `handoff.py` têm os
  seus). Um utilitário compartilhado satisfaria a porta (a) da régua §0 melhor que a (c) — fica
  como dívida consciente, não como omissão.
