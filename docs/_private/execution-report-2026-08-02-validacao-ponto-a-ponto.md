# Execution report — 2026-08-02 · validação ponto a ponto e o método que dela nasceu

> Tier: **telemetria de processo** (anonimizado — ADR-052). O trabalho de domínio vive no
> repositório do projeto; aqui só o que é reutilizável pelo núcleo.
> Releases fechadas: **v1.76.0** (ADR-099).

## 1. O que a sessão produziu

**No repositório de domínio** (fora do núcleo): validação de uma camada analítica migrada,
contra os arquivos que o dono havia extraído do sistema transacional de origem. Sete
conferências, todas verdes ao fim; veredito **VALIDADO COM RESSALVA**.

**No núcleo:** `_shared/validation-reporting/SKILL.md` + ADR-099 + release v1.76.0.

## 2. O padrão que a sessão expôs — e é sobre o framework, não sobre a tarefa

Os **números estavam certos desde cedo**. O que não funcionava era o **reporte**. O dono
corrigiu o executor **oito vezes**, e nenhuma correção foi de estilo:

| # | Correção do dono | O que estava errado |
|---|---|---|
| 1 | *"faz parecer que está ok"* | tabela mostrava o que passou e omitia o que nunca fora olhado |
| 2 | *"usa termos de código não contextualizados"* | jargão interno e IDs de achado no texto para quem decide |
| 3 | *"a cada passo: o que está validado, o que não, e por quê"* | reporte só ao fim, e sem a terceira coluna |
| 4 | *"se não é erro, então passou"* | rigor **incoerente com a régua acordada** na própria sessão |
| 5 | *"foi um único caso? então não está reprovado"* | reprovação por 0,01% em campo descritivo |
| 6 | *"qual o impedimento?"* | impedimento **declarado sem procurar a segunda via** — não existia |
| 7 | *"você pode pescar o mapeamento"* | de-para inferido por similaridade quando estava **no código** |
| 8 | *"que arquivo?"* | três artefatos datados na pasta, nenhum com nome estável |

**Diagnóstico:** o framework tinha regra para *fazer* validação e **nenhuma** para
*reportá-la a quem decide*. O resultado foi um executor tecnicamente rigoroso e
**praticamente inútil** — que transferia ao dono o trabalho de separar sinal de ruído.

## 3. Lições de processo, generalizáveis

1. **Rigor mal calibrado não protege — atrapalha.** Reprovar por diferença que a própria
   régua mandava aceitar depois de testada é ruído com aparência de zelo.
2. **"A fonte X não está disponível" só é impedimento depois de verificar que X é a única
   via.** No caso, havia duas outras, e o executor perdeu meia sessão declarando bloqueio.
3. **Antes de inferir um mapeamento, procurá-lo no código que faz a transformação.** Quem
   transforma sabe o de-para, e costuma tê-lo escrito.
4. **Total agregado é cego a erro compensatório** — e erro operacional preserva o total.
   Validação que só soma não serve a quem quer detectar falha.
5. **Entregável para humano precisa de caminho estável.** Artefato datado sem nome fixo
   força o leitor a adivinhar qual é o atual.

## 4. Falhas do próprio executor, registradas

- **Racionalização da régua de ganho líquido.** O ADR alegava passar pela porta "destrava
  eval editando existente". O gate adversarial derrubou os **três** predicados: entrega
  100% aditiva, nenhum eval criado, nenhuma fusão executada. Corrigido para a base real —
  **override explícito do dono** — com débito declarado. *Um ADR que racionaliza a régua
  vira precedente citável; por isso a correção ficou no texto, não silenciosa.*
- **Regra declarada e não implementada.** O gerador do artefato dizia, na primeira linha,
  *"nenhum número é digitado aqui"* — e tinha os números fixos no texto, com veredito
  estático que continuaria dizendo "PASSOU" com um portão reprovando três linhas acima.
- **Falso alarme de ordem de grandeza.** Um confronto novo acusou divergência enorme; era
  defeito **dele mesmo** (agregava um lado por pasta e o outro por data). Só a implausibilidade
  do número motivou investigar antes de reportar.
- **Falso positivo em massa.** Uma comparação acusou 100% de divergência em duas colunas por
  comparar `"SIM"` com `True`. Teria condenado dois campos corretos da classe mais crítica.

## 5. O que o gate adversarial pegou (duas rodadas, modelo ≠ autor)

| Rodada | Objeto | Veredito | Achados |
|---|---|---|---|
| 1 | código de validação | NÃO LIBERADO | 1 bloqueante, 5 graves, 7 menores |
| 2 | código + artefato humano | NÃO LIBERADO | 1 bloqueante, 5 graves, 9 menores |
| 3 | skill de núcleo + ADR | NÃO LIBERADO | 1 bloqueante, 5 graves, 4 menores |

**Três rodadas, três bloqueantes — todos do mesmo tipo:** algo declarado como garantido que
não estava mecanizado. O gate heterogêneo pagou seu custo em cada uma.

## 6. Débito aberto

A skill nova **não tem canário** e portanto **viola a própria regra de ouro** que enuncia.
Está registrada como `PARTIAL`/`prose` — na lista de débito de mecanização, não como entrega
completa. Quitação definida no checkpoint: artefato-exemplo + teste que o **mute** e exija
veredito REPROVADO. O gerador construído no bloco de origem já provou que isso funciona —
quando um portão reprovou, o veredito virou sozinho.
