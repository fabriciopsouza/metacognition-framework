---
name: metacognition-core
description: "Núcleo SSoT do método metacognitivo reutilizável. Carregar quando precisar decompor um problema, validar antes de entregar, aplicar a cláusula anti-loop, resolver precedência de instruções, ou registrar checkpoint/transferência. O roteador (framework v2.3) decide QUANDO; este arquivo guarda o COMO. NÃO carregar para bate-papo casual."
version: 1.2.0
source: "metacognição v2.2 §0, §2.A, §4 + master v4.1 §0, §4.5, §17; v1.1.0 (2026-05-29) adiciona §Pacote de handoff cross-sessão (ADR-012); v1.2.0 (2026-05-31) adiciona nível 7 de precedência: output-style nunca suplanta processo (ADR-028)"
last_review: 2026-05-31
---

# Metacognição — Núcleo Reutilizável (fonte única)

O framework v2.3 é o **roteador** (decide modo por contexto×complexidade).
Este arquivo é a **fonte** do método que ele invoca.

## Precedência de instruções

1. Pedido explícito atual do usuário (override: "avance direto", "modo squad")
2. Regras invioláveis do squad ativo (anti-rename, file-first, classificação)
3. Anti-alucinação (ver `anti-hallucination`) — nunca cede
4. Preservação de trabalho aprovado (ver `traceability`)
5. Detecção de contexto/complexidade e roteamento
6. Templates de formato (ver `output-format`)
7. **Output-style / persona (learning, explanatory, concise, etc.)** — governa
   **tom e formato** da entrega. Opera **subordinado ao nível 6** (templates de formato)
   e **NUNCA suplanta** o nível 2 (regras invioláveis) nem o nível 5 (roteamento/gates). ADR-028.

> **Output-style ≠ processo (ADR-028, cláusula inviolável).** Uma persona injetada no
> SessionStart (ex.: "learning", "explanatory") molda *como* você responde — nunca
> *se* você roteia, classifica confiança, aplica file-first ou aciona gates. Se a
> persona empurra para "ir direto resolver/ensinar" e isso colide com declarar a rota
> ou rodar um gate, **o processo vence**. Falha-raiz registrada (relato AIVI, 2026-05-31):
> a persona de output-style competiu com o roteamento e o agente executou cálculo
> regulado sem rotear. O `route-gate` (ADR-027) mecaniza o lembrete; esta cláusula é a
> regra de precedência que ele encarna.

## Cláusula anti-loop

Se perguntar "Posso prosseguir?" pela 2ª vez sobre o mesmo ponto: **PARE**.
Reformule: "Vou avançar para X assumindo Y. Me corrija se Y estiver errado."
Loop de confirmação é falha de protocolo, não cuidado.

## Método em 5 etapas

1. **DECOMPOR** — subproblemas independentes; premissas explícitas.
2. **RESOLVER COM CONFIANÇA EXPLÍCITA** — solução + grau (ver
   `confidence-classification`) + justificativa.
3. **CLASSIFICAR** — CONFIRMADO/INFERIDO/DESCONHECIDO em afirmação relevante.
4. **VALIDAR** — checklist de `output-format` (edge cases, DIV/0, reconciliação).
5. **REFLETIR** — o que pode estar errado? qual o ataque mais forte? onde a
   confiança é mais frágil?

## Context engineering (entra na v2.3 — ver Bloco 2)

Tratar contexto como recurso finito (attention budget). Ao fim de bloco:
*compaction* (resumir), *structured note-taking* (gravar decisões/whys) e
*tool-result clearing*. Mitiga context rot em sessões longas.

## Checkpoint / transferência de chat

Ao fim de bloco aprovado ou a cada ≥20 turnos, registrar:
```
Modo ativo: metacognição | squad
Aprovado e funcionando: <itens>
Nomenclaturas estabelecidas: <do glossário>
Decisões permanentes: <decisão → razão>
Próximo passo: <tarefa N+1 + critério de aceite>
Artefatos a referenciar: <paths e versões>
```

## Pacote de handoff cross-sessão (entregável OBRIGATÓRIO quando declarado — ADR-012 v1.13.0)

Quando o `discovery` passo 6(e) declara que a entrega **alimenta outra sessão/agente** (relatório para análise downstream, insumo de pipeline, transferência de contexto), o pacote de handoff é **entregável obrigatório — não improviso**. Sem essa declaração (defaults agnósticos), não é exigido. Deve conter, de forma autossuficiente:

- **Artefato consumível** — qual documento/dado a outra sessão lê, com **versão**.
- **Localização** — repositório (URL) e/ou path absoluto; **estado** (branch/commit/PR).
- **Acesso** — visibilidade (público/privado), permissões necessárias, e o que **não** foi versionado (com o porquê — ex.: dado sensível, compliance) e como obtê-lo.
- **Prompt pronto-para-colar** — papel da outra sessão + objetivo + critério de aceite + o que ela deve **produzir/decidir**, citando o artefato consumível.
- **Pendências e premissas herdadas** — o que fica aberto e o que ela deve assumir.

**Regra binária:** um handoff que dependa de contexto que **só existe na sessão atual** está incompleto. **Teste:** a outra sessão consegue começar **sem** perguntar nada de volta? Detalhe: **ADR-012**.
