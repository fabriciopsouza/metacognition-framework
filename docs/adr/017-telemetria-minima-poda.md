# ADR 017 — Telemetria mínima de processo + poda temporal de regra (ADR-pai, coletor único)

- Status: Aceito
- Data: 2026-05-30 · Decisores: dono (briefing v1.14.x) + squad (autônomo)
- Onda: 3 (auto-observação mínima) · Pesquisas: **P5 + P7** · Tipo: **EMENDA** (Princípios 10, 11)
- Relaciona: `_shared/observability`, `history.md`, ADR-011 (junções J0–J5), ADR-013 (campo `classe`), `.agent/workflows/checkpoint.md`.
- **Estrutura: ADR-pai com 2 decisões (17-A blame, 17-B poda) sob fronteira de coletor único.**

## Contexto

P5 e P7 disputam o mesmo terreno — "medir o próprio processo" — e o DOSSIÊ §3 alerta: especificá-los
separados cria **dois sistemas de auto-observação sobrepostos**, violando o próprio P5 ("mais sinal ≠
mais clareza"; telemetria não-aberta em decisão real é dívida). Por isso são **um eixo, duas métricas,
um coletor**. O coletor já existe parcialmente: `_shared/observability` tem `framework.junction`
(J0–J5); `history.md` tem `## Em aberto` e `## Aprendizado`.

**Régua §0:** EMENDA — não cria subsistema nem dashboard. Estende `observability` (o método) e
`history.md` (o coletor físico) e **ativa** o campo `classe` já reservado no contrato (ADR-013/Onda 0).
A matriz de relevância instrumentada do plano é **explicitamente rejeitada** (P7): exigiria logits ou
N+1 forward passes — andaime que o JARVIS construiu e desligou.

## Decisão 17-A — Blame-attribution por junção (P5)

Instrumentar **só 2 métricas que mudam decisão** (nenhuma outra):
1. **Junção-origem do rewind:** quando o process-critic dispara rewind cascata, registrar de qual
   junção J0–J5 veio a causa-raiz. → muda a decisão: *onde reforçar spec/checklist a montante.*
2. **Rounds de qa-critic até PASS:** proxy de spec rasa nascendo a montante. → muda a decisão:
   *investir em discovery/architect.*

**Reprovado (P5):** dashboards, latência fina (ms), throughput, "% verde" de junções, custo-por-junção
(exceto como circuit-breaker em automação real com rewind automático). Teste de acionabilidade:
*métrica que ninguém abre numa decisão real é dívida com fatura mensal.*

## Decisão 17-B — Tally de uso + classe + poda Chesterton (P7)

- **Tally S/N por regra-chave** no coletor: "esta regra disparou nesta sessão? S/N", agregado ao longo
  de sessões. Custo ~zero, roda no chat. **Confiabilidade [DESCONHECIDO]:** o agente pode alucinar uso
  → quando possível, cruzar com sinal externo (a regra deixou rastro verificável no output?).
- **Classe da regra** (campo `classe` do contrato ADR-013): `salva-vidas | operacional | andaime`.
- **Contador de desuso (operacionaliza o N):** cada entrada de tally carrega `sem-disparo: K` — o nº
  de sessões **consecutivas** em que a regra não disparou. O PMO, ao agregar no checkpoint, faz `K+1`
  se a regra não disparou na sessão, ou zera (`K=0`) se disparou. Como o `history.md` é append-only,
  `K` também é **derivável** por varredura das entradas anteriores da mesma regra (o campo é o cache
  legível; a varredura é a fonte de verdade). Sem esse contador, "poda após N sessões" seria inaplicável.
- **Poda só na classe `andaime`** quando `sem-disparo ≥ N` (**N = 5–10, [INFERIDO]**, parâmetro do
  ADR, não constante; calibrar por observação). `salva-vidas` (anti-alucinação, gate T3, audit trail,
  DIV/0) **NUNCA** poda por desuso → gera só **nota de verificação**. `operacional` → candidata a
  **consolidação** (não remoção). `unknown`/sem classe → tratada como `salva-vidas` (conservador) até classificar.
- **Protocolo "portão pequeno"** (Chesterton): suspender a regra sob monitoramento reforçado →
  observar efeitos de segunda ordem → só então remover. Nunca remoção automática.

## Fronteira de coletor único (o que evita os dois sistemas)
- **17-A mede:** fluxo *entre junções* nesta execução (onde a falha entrou agora).
- **17-B mede:** uso de regra *ao longo de sessões* (o que é andaime no tempo).
- **Mesmo artefato lógico + mecanismo de reconciliação (não só política):** a seção `## Telemetria`
  do `history.md` (append-only) é a **fonte de verdade única**. No IDE, o span OTel (`framework.junction`)
  é **efêmero e somente-leitura**; o passo concreto que evita dois coletores é: **no checkpoint, o
  agente transcreve os atributos de span do bloco para a seção `## Telemetria`** — o span morre com a
  sessão, o `history.md` perdura. No chat (sem span), o `history.md` é o único coletor desde o início.
  Assim a "fonte única" é garantida por um passo (transcrição no checkpoint), não por aspiração.

## Mecanismo por ambiente
- **IDE/SDK:** atributo no span OTel existente (`framework.junction=J2`, `framework.event=rewind`,
  `framework.qa_rounds=N`); consulta sob demanda, **sem dashboard**. Agrega na seção `## Telemetria`.
- **Chat web:** tudo no `history.md ## Telemetria`, **agregado no fim do bloco/dia** (não por turno —
  cerimônia por turno compete com a tarefa).

## Alternativas consideradas
1. **Não medir (status quo).** Prós: zero custo. Contras: rewind é cego (não sabe onde reforçar);
   regra-andaime acumula sem poda. Rejeitada — P5/P7 mostram o ganho de 2 métricas acionáveis.
2. **Telemetria rica (dashboards, N coletores, latência) + matriz de relevância instrumentada.**
   Prós: "observabilidade completa". Contras: 11-coletores do JARVIS; matriz exige logits/N+1 passes
   (inviável); telemetria não-aberta = dívida. Rejeitada (P5 §1, P7 §6) — é o andaime que derrubou o JARVIS.
3. **2 métricas + tally/classe/poda no coletor único (ESCOLHIDA).** Prós: acionável, ~zero custo,
   sem duplicação. Contras: tally autorreportado é falível (declarado [DESCONHECIDO]).

## Consequências
**Positivas:** rewind direcionado (sabe a junção-origem); regra-andaime poda com segurança
(Chesterton); coletor único evita o anti-padrão de auto-observação redundante.
**Negativas:** tally depende de honestidade do agente; +1 seção no `history.md` + extensão de observability.
**Riscos:** (a) confiabilidade do tally **[DESCONHECIDO]** → cruzar com sinal externo quando possível.
(b) N=5–10 não-calibrado **[DESCONHECIDO]** → parâmetro, não constante. (c) Convenção OTel para
"junção de governança" não é padrão **[DESCONHECIDO]** → atributo custom.

## Implementação (ponteiro após aceito)
- Ponteiro: branch `feat/v1.17.0-telemetria-poda` · `2026-05-30` · grep `Telemetria|blame|junção-origem|classe|Chesterton`
- Artefatos: extensão `_shared/observability/SKILL.md` (2 métricas + poda), seção `## Telemetria` em
  `history.md`, gancho de poda em `.agent/workflows/checkpoint.md`.
- Lit: Barrak 2025 (arXiv 2510.07614) blame attribution; Google SRE (acionabilidade); Chesterton's Fence.
