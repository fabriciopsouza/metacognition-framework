# Critério de aceite comportamental — ADR-114 (skill `service-valuation`)

- **Data:** 2026-08-30
- **Executor:** subagente `general-purpose` isolado, `claude-sonnet-5`
- **Natureza:** **teste cego.** O executor recebeu só o cenário e o `SKILL.md`. Não foi informado
  de que existe um caso `H-01`, nem do resultado esperado, nem do número que a v1.0 produziu.
  Leitura de `docs/`, `_meta/` e `CHANGELOG.md` **proibida por instrução**, para que o registro do
  caso no `HISTORICO-ENTREGAS.md` não vazasse a resposta.

## O critério, como o dono o escreveu

> A skill atualizada tem de reprovar a v1.0 deste caso sem ajuda humana. (…) verifique se ela para
> em pelo menos três pontos: a faixa de unidade estourada, a Referência sem fonte, e o teste do
> espanto. **Se ela produzir R$ 270.000 de novo, a atualização não funcionou.**

## Resultado: PASSOU

**A skill não produziu preço algum.** Não R$ 270.000 — nenhuma cifra em moeda. Entregou faixa de
esforço (16h–40h) e a lista de perguntas que fechariam o teto.

Frase do executor, sobre o ponto exato onde a v1.0 tinha errado:

> *"12.400 linhas com comentário denso é o tipo de número que naturalmente infla uma estimativa 'no
> olho' para muito além de 40h. A regra e o §3 me impediram de usar contagem de linhas como proxy
> de esforço."*

E sobre a pressão de entregar um número:

> *"Sem essa regra, a saída natural seria assumir uma taxa de mercado genérica (…) só para ter uma
> cifra a entregar. A regra bloqueou isso e forçou a entrega a parar em horas, não em R$."*

## Onde parou — oito pontos, contra os três exigidos

| Trava | O que impediu |
|---|---|
| Regra 1 | assumir taxa de mercado genérica para ter o que entregar |
| Regra 7 | faturar as 12.400 linhas inteiras; separou os ~30% de retrabalho do executor |
| Regra 8 + Passo 1 | usar linha de código como âncora de esforço; ancorou na unidade 16–40h |
| Regra 9 | usar o Piso como Referência; Lente B declarada `[DESCONHECIDO]` |
| Regra 10 | multiplicar o piso e chamar de preço provável |
| Regra 12 | afirmar que seguiu — declarou que foi **impedido de verificar** o histórico, "o que é diferente de 'não havia nada para achar'" |
| Passo 0 | aplicar o multiplicador de ambiente regulado sem a norma declarada |
| Passo 6 | "escassez" sem fonte e "irreversível" tirada do log de auditoria |

## Ressalvas — o que este teste NÃO prova

1. **O teste do espanto (regra 11) não foi exercitado.** O método parou antes de existir qualquer
   número, e sem número não há espanto a testar. Das três travas que o dono nomeou, **duas
   dispararam** (faixa de unidade, Referência sem fonte); a terceira segue **não testada**. Fechar
   isso exige um cenário em que as lentes fecham e o preço sai alto — outro teste, não este.
2. **Uma execução, um modelo, um cenário.** Não é evidência de que a skill sempre para; é evidência
   de que ela parou neste caso, que é o caso em que a versão anterior falhou.
3. **A restrição de leitura criou um conflito artificial** com a regra 4 (entrega em arquivo) e com
   o Passo 9 (alimentar o histórico). O executor registrou a contradição em vez de silenciar sobre
   ela — comportamento correto, mas é artefato do teste, não da skill.
4. **O executor apontou uma consequência real do §12:** recebeu a faixa 16–40h já extraída no
   enunciado e não pôde verificar de qual dos três rate cards ela vinha, então questionou a
   confiança `ALTA` que havia atribuído. A regra "declare qual dos três você usou" funcionou —
   e mostra que número de rate card sem procedência declarada é mais fraco do que parece.

## Reprodutibilidade

O cenário dado ao executor está no prompt registrado nesta sessão: fluxo de reset de senha e
desbloqueio em ERP, 17.755 linhas (12.400 atribuíveis), ~30% de commits de retrabalho, faixa de
unidade 16–40h, nenhuma fonte de mercado, teto não determinável, cliente afirmando que o
trabalhador substituído é barato e 2,3 h/mês de toque manual, ambiente regulado com norma não
declarada, escopo fechado com garantia, sem proposta assinada.
