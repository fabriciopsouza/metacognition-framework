# Regra 06 — Confirmação interativa de bloco é o default

**Fonte única:** ADR-111. Não redefinida aqui.

Antes de executar um **bloco** — um conjunto de edições com um objetivo — o agente
apresenta o **plano** e espera. O dono aprova ou corrige; só então o bloco roda
inteiro. Uma interrupção por bloco, não por arquivo.

O plano cabe em uma tela e traz três coisas: **o que será tocado** (arquivos e
natureza da mudança), **as decisões em aberto** com as alternativas reais e uma
recomendação, e **o que fica de fora**. Plano sem decisão em aberto declarada é
plano incompleto — se o agente decidiu sozinho, ele diz o que decidiu.

**Interativo significa conversa.** Pergunta feita ao dono, respondida no diálogo.
Entregar um documento com perguntas abertas **não** é elicitar: é transferir o
trabalho de volta e chamar de consulta.

## O que NÃO passa por este gate

- **Ler, buscar, inspecionar, rodar canário.** Investigação não muda estado, e
  file-first (regra 03) exige que ela venha antes — pedir licença para ler
  inverteria a ordem.
- **O QA adversarial obrigatório** — o degrau **abaixo** do default. Ele é
  **automático**, roda em toda junção e no fechamento, e **não pede autorização a
  ninguém** (ADR-110). Só o degrau **acima** passa por gate, e o gate dele é outro:
  autorização ativa por custo.
- **Gates anunciados do próprio framework** (ADR-047) e aplicação de regra já
  vigente.

## O que não conta como autorização

`"siga"`, `"ok"` e `"pode continuar"` autorizam **prosseguir no escopo já
declarado** — não abrem escopo novo, não aprovam decisão que o dono não viu, e não
substituem o plano do próximo bloco. Silêncio nunca autoriza.

## Limite declarado

Nenhum hook obriga o agente a perguntar: o harness não tem esse ponto de controle.
O canário garante que esta regra **não seja apagada em silêncio** e que ela **viaje**
para projeto novo. O cumprimento é **cobrável em revisão**, não imposto por código —
e dizer o contrário seria a sobre-promessa que o próprio framework proíbe.
