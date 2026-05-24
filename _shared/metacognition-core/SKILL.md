---
name: metacognition-core
description: "Núcleo SSoT do método metacognitivo reutilizável. Carregar quando precisar decompor um problema, validar antes de entregar, aplicar a cláusula anti-loop, resolver precedência de instruções, ou registrar checkpoint/transferência. O roteador (framework v2.3) decide QUANDO; este arquivo guarda o COMO. NÃO carregar para bate-papo casual."
version: 1.0.0
source: "metacognição v2.2 §0, §2.A, §4 + master v4.1 §0, §4.5, §17"
last_review: 2026-05-23
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
