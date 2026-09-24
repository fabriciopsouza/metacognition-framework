# Andamento — 24/09/2026 (bloco D): CAPA — a retomada, e o teste que passaria verde sem provar nada

> Execution-report de encerramento de sessão (ADR-038/052/062 · tier **OWNER** · privado,
> não distribuído). Sessão aberta no framework (`/start-session`) e usada para trabalho de
> **domínio** no repositório `capa-sharepoint`. Nada do núcleo foi alterado.

## Onde estamos, em uma linha

O dono retomou o projeto CAPA, pediu análise comparada com o projeto de Excelência Operacional
e documentação nova; **nenhum bloco de escrita foi autorizado** (os dois ficaram em proposta), e a
sessão fechou entregando o **prompt de retomada** para outra IDE — revisado por QA isolado até
APROVADO na 3ª rodada.

## Métricas

| Métrica | Valor |
|---|---|
| Tokens | **NÃO MEDIDO** — sessão única, sem `--from-transcripts` rodado |
| Commits no repo de domínio | 3 (`bee7095`, `790711c`, `7de640f`), push `2c871f4..7de640f` |
| Commits no framework | este report |
| Arquivos escritos no domínio | 1 (`docs/PROMPT-RETOMADA.md`, +~180 linhas, retomada nova **por cima**; a anterior só teve o cabeçalho riscado) |
| QA adversarial | 3 rodadas, `qa-critic` isolado em **sonnet** (autor opus): APROVADO COM RESSALVAS → **REPROVADO** → APROVADO |
| Achados de domínio medidos (não registrados no repo, a pedido da regra de confirmação) | 4: A-06(a/b), A-07, A-08, A-09 |

## De onde saímos → onde chegamos

**O que o dono trouxe:** o prompt de retomada de 24/09 manhã, com duas perguntas que só ele
responde e um bloco de 4 itens não autorizado.

**Tudo o que o prompt afirmava foi medido antes de repetido** — `grep -c` = 2 nas linhas 248/352,
ausência de data ISO no runbook, `.gitignore` por extensão (`check-ignore` confirmou os dois
caminhos de risco, e 0 e-mails nos 21 arquivos versionados de `entrada/dados/saida`).

**Duas tensões levantadas ao dono, não resolvidas por mim:**
1. O item "regra nova M-11" do bloco proposto era **prosa para corrigir a falha de uma prosa** — a
   M-10 também era prosa e não impediu o A-06. Proposto o mecanismo (registro de rótulos capturados
   + conferidor no publicador), com custo.
2. Corrigir o `.gitignore` ignorando `saida/` inteira quebraria a regra 2 do projeto (entregas
   versionadas moram em `saida/runbooks/`) — a correção certa é allowlist.

**Os prints da executora mudaram o "onde estamos":** o prompt dizia Passo 6; o print de 11:34
mostra o Passo 11.2. E um defeito que ninguém tinha visto: o **fixture DEMO não tem a coluna
Pessoa**, então o teste do F1 agruparia tudo num grupo só e **passaria verde sem provar o
"um e-mail por pessoa"** — o coração do fluxo. Calculei o resultado esperado dos Passos 12/13 a
partir das 12 datas, e o Passo 13 virou detector do recuo de data (1 ação cai no múltiplo de 7 se a
data recuar um dia).

## O placar gate × achado

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Fixture DEMO sem a coluna que o teste agrupa (A-08) | **eu**, conferindo o Mapa contra o xlsx do R-05 | nenhum — não existe conferência "o dado de teste exercita a propriedade testada" |
| Ponto de parada do prompt atrás do real | **eu**, lendo o relógio dos prints | nenhum |
| "OData" citado como conteúdo do runbook, sem estar nele | **QA r1 (sonnet isolado)** | — funcionou |
| Vocabulário de marcas incompleto (INCONCLUSIVO) | **QA r1** | — funcionou |
| **Correção minha introduziu afirmação falsa** (M-11 "registrada") | **QA r2** | — funcionou; é o modo de falha 6 da `project-docs` (polimento que escapa) |

## Lições (para o framework)

- **Prompt de retomada é documento que afirma estado, e o QA pega afirmação de estado futuro como
  presente.** Ao acrescentar um glossário para fechar "termo sem explicação", listei um intervalo
  (`M-1…M-11`) que incluía o item proposto. A varredura de classe feita por mim (M-10, D1/D4, P-05)
  **não pegou** isso: eu varri "termo sem explicação", e o defeito era "proposto dito como
  existente". **A classe certa só aparece a quem não escreveu.**
- **Fixture que não exercita a propriedade.** Mesmo padrão de "teste cujo fixture lê a própria
  constante": aqui, o dado de demonstração não tem a dimensão que o teste agrupa. Candidato a item
  de checklist do `qa-critic` para runbooks de teste: *o dado de teste tem variação na coluna que o
  teste promete provar?*
- **Aplicar o framework em repo sem ele instalado**: o prompt manda ler de fora, anunciar gates
  inline (modo non-admin) e **não copiar** o framework — write-isolation. Não há mecanismo que
  confira isso na outra IDE; é prosa, e está declarado como tal.

## Procedência

- Repo de domínio: `C:\Users\fabriciosouza\capa-sharepoint` @ `7de640f`, `main` sincronizado com origin.
- Repo lido como referência, **somente leitura, zero escrita**: `C:\Users\fabriciosouza\excelencia-master-plan` @ `463d1c4`.
- Framework: `main` @ `219bb44`, 0/0 com origin no início. Gates inertes desta sessão (ADR-061)
  aplicados à mão: `check-repo-sync` → 0/0 · `check-core-agnostic` → PASS (norma).
- **O que este report não mede:** tokens e tempo de parede; e não sabe o resultado da execução do
  R-06 que o dono fez em outra conversa — é a primeira pergunta do prompt entregue.
