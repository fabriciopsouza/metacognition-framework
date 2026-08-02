# ADR-099 — Método de validação ponto a ponto com reporte legível por humano

- **Status:** Aceito
- **Data:** 2026-08-02
- **Decisores:** dono (Fabricio) + squad
- **Substitui/emenda:** nada. Complementa `qa-critic` (que revisa CÓDIGO) e
  `high-stakes-gate` (que trata RISCO). Esta ADR trata de **validar DADO contra referência
  e reportar o resultado a quem decide**.

## Contexto

Um bloco de validação real (2026-08-02) produziu números corretos e um **reporte
inutilizável**. O dono corrigiu o executor **oito vezes** — sobre o que estava validado,
sobre o que não estava, sobre linguagem, sobre veredito e sobre onde o arquivo estava. As
correções não foram de gosto: cada uma apontou um defeito que **mudava a decisão de quem
lia**.

Padrão observado: o framework tinha regras para *fazer* a validação (file-first,
confidence-classification, traceability) e **nenhuma** para *reportá-la a um humano que
decide*. O resultado foi um executor tecnicamente rigoroso e praticamente inútil — que
apresentou "não conferido" com aparência de "ok", reprovou por 0,01% em campo descritivo,
declarou impedimento inexistente, e produziu um artefato que dizia "PASSOU" com um portão
reprovando três linhas acima.

Declaração do dono ao fim do bloco: *"este último foi MUITO melhor (o excel), o método,
abordagem, esclarecimento, mas ainda teve algumas falhas. INCORPORE como um dos métodos
quando pedir validação ponto a ponto e com clareza. ESTE É O MÉTODO QUE DEVE VALER PARA O
FRAMEWORK AGORA."*

## Decisão

Criar `_shared/validation-reporting/SKILL.md` como **núcleo SSoT** do método, carregado
quando: há referência externa · o resultado responde "isto está validado?" · quem lê decide
algo. As regras derivam de **oito correções reais**, nomeadas nas seções §2, §3, §6, §7 e §9:

1. **Quatro categorias, nunca três** — VALIDADO · NÃO CONFERIDO · **NÃO OBTENÍVEL** · NÃO SE
   APLICA. "Não conferido" jamais aparece como "ok"; "não obtenível" não é pendência.
2. **Níveis por CONSEQUÊNCIA do campo**, não por percentual — A (dinheiro/documento,
   tolerância zero) · B (operacional, aceito se caracterizado **e testado** que não altera
   decisão) · C (descritivo) · **B-DEC** (flag derivada = métrica de impacto de B, não erro
   independente).
3. **Total agregado nunca sozinho** — é cego a erro compensatório, que é o que fraude e erro
   operacional produzem. Sempre com conferência um-a-um e agregado na granularidade de uso.
4. **Diferença nomeada uma a uma com resíduo zero** — prestação de contas, não faixa de
   tolerância. Fail-closed inclusive contra item que **deixou de divergir**.
5. **Materialidade por unidade de veredito**, com limiar declarado antes de medir.
6. **Antes de declarar impedimento, procurar a segunda via** — e antes de inferir mapeamento,
   procurá-lo no código que faz a transformação.
7. **Veredito VALIDADO COM RESSALVA é validado.** Negá-lo por perfeccionismo desserve quem
   decide.
8. **Conteúdo obrigatório do reporte** (o formato é recomendado, não normativo): abre pelo
   que NÃO está validado; código de saída por conferência; número **derivado** dos artefatos,
   nunca digitado; veredito condicionado aos códigos medidos; nome de arquivo **estável**
   além do datado; glossário. Planilha por abas é a instância recomendada — Markdown ou
   equivalente atende, e a §9 da skill declara isso no próprio texto normativo (e não só
   aqui, onde nenhuma sessão futura leria).
9. **Regra de ouro**: declarar a regra não a implementa — todo mecanismo precisa ter sido
   **visto reprovar** ao menos uma vez. *(Esta ADR é o primeiro caso a violá-la: ver §Régua
   §0 e §Verificação.)*

## Régua §0 — esta entrega NÃO passa pelas três portas. Entra por override declarado.

**A versão anterior deste ADR alegava a porta (c) ("destrava eval editando existente"). Era
racionalização, e o gate adversarial derrubou os três predicados:**

| Predicado da porta (c) | Verdade |
|---|---|
| "editando existente" | **FALSO** — entrega 100% aditiva; os únicos arquivos existentes tocados são bump de versão e índices |
| "destrava eval" | **FALSO** — nenhum eval passou a existir: sem canário, sem tool, sem artefato-exemplo |
| "funde prosa dispersa" (alegação auxiliar) | **FALSO** — fundir exige remover ou redirecionar na origem; `confidence-classification` ficou intocada |

Registrar isto importa mais que a release: um ADR que racionaliza a régua §0 vira
**precedente citável** para a próxima adição pura. É o mesmo defeito que o ADR-098 sofreu, e
que este ADR citava como lição enquanto o cometia.

**A base real é o override explícito do dono (ADR-051):** *"incorpore como um dos métodos
quando pedir validação ponto a ponto e com clareza. **Este é o método que deve valer para o
framework agora.**"* — decisão tomada ao fim do bloco em que ele corrigiu o executor oito
vezes, com o custo conhecido (mais uma skill no núcleo) e a consequência conhecida (sem
mecanismo, por ora).

**Débito §0 assumido, com condição de quitação:** a porta (c) passa a ser verdadeira quando
existir canário sobre um artefato-exemplo com veredito derivado dos códigos de saída — o
bloco de origem **já construiu** um gerador assim, logo isto é alcançável, não hipotético.
Enquanto não existir, a capacidade fica registrada como `PARTIAL` / `enforcement: prose`,
que é a lista de débito de mecanização, e não como entrega completa.

## Alternativas rejeitadas

- **Estender `qa-critic`** — rejeitada: `qa-critic` revisa CÓDIGO com postura adversarial.
  Validação de DADO contra referência tem régua e entregável diferentes; misturar as duas
  degradaria ambas.
- **Estender `output-format`** — rejeitada: aquele núcleo trata do formato de uma ENTREGA
  técnica; aqui o entregável é um veredito para decisão de negócio, com categorias próprias.
- **Deixar como memória de projeto** — rejeitada pelo pedido explícito do dono ("deve valer
  para o framework agora"), e porque memória de projeto não é carregável por outra sessão.
- **Prescrever a planilha como formato obrigatório** — rejeitada: o formato é *recomendado*
  e o que é **obrigatório** é o conteúdo (as quatro categorias, o veredito condicionado, o
  poder do teste declarado). Um relatório em Markdown que cumpra §2, §8 e §9 atende.

## Consequências

- **Positivas:** sessão de validação passa a ter formato e veredito reprodutíveis; o dono
  recebe "o que está validado / o que não está / por quê" sem pedir; ressalva deixa de ser
  sinônimo de reprovação.
- **Custo:** mais uma skill no núcleo (~180 linhas). Mitigado por ser carregada só sob o
  gatilho da §1.
- **Risco declarado:** a skill descreve um método **provado uma vez**. Generalização para
  outros domínios de validação é [INFERIDO], não confirmado — a §1 restringe o gatilho para
  limitar o dano de uma generalização errada.

## Verificação

- [x] `check_core_agnostic.py` → PASS para `_shared/validation-reporting/SKILL.md`
      (a skill não cita cliente, produto ou domínio).
- [x] Registro em `capabilities.json` + `CAPABILITIES.md` regerado.
- [x] Entrada no CHANGELOG (canário `adr-changelog-sync` exige para ADR Aceito).
- [ ] **Pendência:** a skill não tem canário próprio — sua conformidade é avaliada por
      leitura, não por mecanismo. Contraria a §10 da própria skill ("declarar a regra não a
      implementa") e fica **declarado como débito**, não como completo. Um canário
      verificável exigiria um artefato-exemplo com o veredito derivado, ainda não desenhado.
