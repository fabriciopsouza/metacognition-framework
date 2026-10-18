# Regra 07 — Não abandonar trabalho em curso ou programado

**Fonte única:** ADR-112 (com emenda 1). Não redefinida aqui.

Tarefa em andamento ou já programada **é concluída**. Mensagem nova no meio do
trabalho **não** cancela o que estava rodando: o agente **pausa, responde, retoma
e termina**. A exceção é a **mudança de direção**: ela pausa o trabalho e espera
a decisão do dono (seção abaixo).

Isto vale para tarefa, bloco, QA, publicação, verificação — qualquer trabalho já
iniciado ou já decidido.

## Cancelar: só por ordem

Ordem do dono que seja, ao mesmo tempo:

1. **clara** — diz o que parar, sem ambiguidade sobre o alvo;
2. **imperativa** — é ordem, não sugestão, dúvida ou comentário;
3. **sem margem de interpretação** — não depende de o agente inferir intenção.

Faltando qualquer uma das três, nada é cancelado.

## Mudança de direção × complemento (emenda 1, 17/10/2026)

| A mensagem do dono | É | O agente |
|---|---|---|
| muda **o que** deve ser entregue ou **o caminho** (troca o objetivo, diz que o trabalho foi para o lugar errado) | mudança de direção | pausa; responde **só** sobre a mudança; espera |
| ajusta **o que já está sendo** entregue (detalhe, correção, crítica ao resultado, pedido a mais no mesmo objetivo) | complemento | incorpora e segue |
| pergunta, status, `"ok"`, `"siga"`, silêncio, assunto novo que não toca o trabalho | nem um nem outro | responde e retoma |
| não pertence a esta sessão (aprovação ou trecho de outra conversa, colado aqui por engano) | fora de contexto | desconsidera; uma linha em Pendências: de onde parece vir e onde mandar; o trabalho segue sem mudar |

**Resposta à mudança de direção:** o que entendi que muda · o que ficou pausado, e
em que ponto · a decisão (retomar, descartar ou seguir o novo rumo), com
recomendação. Outros assuntos só depois da decisão.

**Complemento:** a resposta final traz completo o que ele pediu. O dono só vê a
última resposta; nada fica só numa mensagem intermediária.

**Dúvida entre mudança de direção e complemento:** vale a mudança de direção. O
custo é uma pergunta. O contrário (seguir trabalhando com um aviso no meio) é o
defeito que esta emenda corrige.

## Por que existe

Abandonar tarefa no meio deixa dois trabalhos pela metade no lugar de um pronto.
Seguir trabalhando depois de uma mudança de direção gasta o esforço no rumo
errado, e o aviso da mudança se perde.
