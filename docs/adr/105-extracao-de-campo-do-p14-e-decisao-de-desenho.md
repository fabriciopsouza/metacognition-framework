# ADR-105 — A extração de campo do P14 é decisão de desenho, não mais uma correção

- **Status:** Aceito
- **Data:** 2026-08-13
- **Decisores:** dono (Fabricio), após a 9ª reprovação consecutiva
- **Substitui/emenda:** nada. **Desacopla** de `docs/adr/102` (padrão documental) o trabalho sobre
  `tools/handoff.py`, que entrou de carona e não era escopo do ADR-102.

## Contexto — seis defeitos na mesma função

`latest_checkpoint_field` extrai o "Próximo passo" do checkpoint mais recente. Esse campo vira o
**Objetivo do Pacote P14** — o que a próxima sessão vai fazer. Se sai errado, a próxima sessão
começa com a tarefa errada, **e não recebe nenhum erro**.

Em uma única sessão, seis defeitos consecutivos, **cinco deles introduzidos por correção**:

| # | defeito | como saía |
|---|---|---|
| 1 | o regex não previa campo em negrito | placeholder **visível** |
| 2 | `(.+)$` sem DOTALL | campo **truncado** — e truncado *parece* completo |
| 3 | terminador só via linha em branco/negrito/fim | **engolia** o campo seguinte (26 casos no corpus) |
| 4 | todo terminador exigia `\n` antes do rótulo | engolia quando o rótulo estava na **mesma linha** |
| 5 | "whitelist de continuações" era blacklist disfarçada | **perdia cláusulas** em 3 checkpoints reais |
| 6 | terminador exige pontuação antes do rótulo; rótulo com sufixo vaza | engole se falta o ponto; `Riscos ativos (2):` devolve `(2): ...` |

Cada correção fechou um caso e abriu outro. O canário ficava verde a cada rodada, porque os casos
de teste eram escritos a partir do defeito recém-descoberto — nunca da classe.

## A decisão

**Parar de corrigir dentro da função.** O `tools/handoff.py` volta ao estado do `main` e o assunto
vira bloco próprio, com decisão de desenho a tomar. O ADR-102 fecha sem ele.

## Por que é desenho, e não execução

O padrão dos seis defeitos aponta para a mesma causa: **uma regex de alternação tentando enumerar
onde um campo termina, dentro de prosa livre escrita por humanos.** Esse conjunto é ilimitado —
qualquer rótulo novo que alguém escreva num checkpoint futuro é um caso não coberto.

Três evidências de que o problema não é a regex específica, e sim a abordagem:

1. O comentário do código afirmava "conjunto FECHADO, definido em `checkpoint.md`". **Falso**: o
   template documenta 5 campos; o código listava 11, e o corpus real usa pelo menos 9 rótulos
   fora da lista — `Nomenclaturas:` puro aparece **26 vezes**, mais que a forma canônica.
2. Cada rodada de correção foi validada por um detector que eu escrevi, e **duas vezes o detector
   estava incompleto** — achava só o que eu já esperava.
3. A extração falha em silêncio. Não há sinal de que o campo saiu errado.

## As duas saídas, para a decisão do bloco próprio

**(a) Impor o formato.** Um canário exige que todo campo de checkpoint comece em **linha própria**.
Elimina a classe "mesma linha" inteira — os defeitos 4, 5 e 6 deixam de existir. Custo: passa a
haver formato obrigatório no `history.md`.

**(b) Trocar por parser linha-a-linha.** Uma linha cuja **forma** seja `Rótulo:` abre campo novo;
o resto é continuação. Não enumera vocabulário — reconhece forma. Custo: reescrita, e é código
novo que precisa de revisão.

**Critério de aceite, qualquer que seja a escolha:** o P14 extrai o campo **inteiro** nos 63
checkpoints do corpus, verificado por **detector genérico** — sem lista de rótulos conhecidos.
Essa exigência existe porque foi a lista que falhou duas vezes.

## Consequências

**Positiva.** O padrão documental (ADR-102), que não recebe achado há várias rodadas, deixa de
ficar refém de um problema que não é dele. É o mesmo movimento do ADR-104, e pelo mesmo motivo:
maturidade diferente pede bloco diferente.

**Negativa, declarada.** A limitação antiga volta: **campo escrito como parágrafo sai truncado no
P14**. É limitação conhecida e anterior a esta sessão — não um defeito novo. Mitigação imediata,
já aplicada no checkpoint do v1.79.0: **escrever o "Próximo passo" em uma linha**, formato que a
versão do `main` sempre leu corretamente.

## Lição

Três reprovações dizem que o desenho está errado. **Seis dizem que eu insisti.** A regra de
escalonamento existia e foi acionada na 3ª rodada — mas para o outro bloco, e eu não a apliquei a
este. Regra de escalonamento vale por *trecho de código em disputa*, não por entrega.
