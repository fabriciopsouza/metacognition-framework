---
name: <nome-do-subagente>
description: "Quando o Claude Code deve delegar a este subagente. 3ª pessoa, gatilhos claros. Use para trabalho longo/ruidoso/paralelizável ou que precise de isolamento de contexto."
tools: Read, Grep, Glob          # liste só o necessário (menor privilégio). Sem Write/Edit = read-only.
model: sonnet                    # idealmente diferente do agente principal p/ evitar viés
skills:                          # subagente NÃO herda skills — liste explicitamente
  - <skill-de-_shared-ou-role>
---

# <nome> — Subagente isolado

Contexto próprio (fresh). Recebe a tarefa, executa, devolve só o destilado.
Carregar de `_shared/`: anti-hallucination, confidence-classification, traceability.

## O que faz
<instruções específicas>

## O que devolve
Resumo destilado + achados classificados (CONFIRMADO|INFERIDO|DESCONHECIDO). Nunca o bruto.
