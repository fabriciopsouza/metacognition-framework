---
name: traceability
description: "Núcleo SSoT de rastreabilidade e preservação de trabalho aprovado. Carregar antes de editar arquivo, referenciar nome de campo/fórmula/variável, ou alterar algo já aprovado. Reúne file-first, anti-rename, preservação e a cadeia decisão→fonte→versão. NÃO carregar para conversa casual."
version: 1.0.0
source: "SQUAD v1.1.0 rules 01 e 03 + master v4.1 §3.4 e §11.2 + metacognição v2.2 §6.2"
last_review: 2026-05-23
---

# Rastreabilidade e Preservação — Fonte Única

## Regra 1 — File-first

Antes de **editar** um arquivo: lê-lo (`view_file`/`cat`/`read_file`).
Antes de **referenciar** (import/require): lê-lo.
Antes de **assumir** estrutura de dados: inspecionar a fonte real
(`df.columns.tolist()`, `DESCRIBE TABLE`, schema inspect).

Nunca assumir: nomes de colunas/campos, estrutura de pastas, estado atual de
arquivo já editado na conversa.

> Causa raiz #2 de retrabalho: reconstruir arquivo do zero por suposição.

## Regra 2 — Anti-rename

Nunca renomear campo, fórmula, variável, função ou tabela registrado no glossário
ou aprovado em iteração anterior — sem ADR.

Procedimento quando o rename for necessário:
1. PARAR; não executar.
2. Criar ADR `docs/adr/NNN-rename-<termo>.md` (nome atual, proposto, razão, impacto).
3. Aguardar aprovação explícita.
4. Aplicar rename + atualizar glossário no mesmo commit.

> Causa raiz #1 de retrabalho: "melhorar" nomes quebra referências externas.

## Regra 3 — Preservação de trabalho aprovado

Trabalho aprovado (explícita ou implicitamente, ao avançar) é **permanente**.
Só alterar mediante conflito real com nova instrução — e então
PARAR, EXPLICITAR, PERGUNTAR. Mostrar sempre, de forma cirúrgica:
**O QUE SAI / O QUE FICA / ONDE ENTRA**.

## Regra 4 — Cadeia de rastreabilidade

Toda decisão relevante registra: **decisão → fonte → versão**.
Em ambiente regulado, esta cadeia é parte do entregável (ver `high-stakes-gate`),
não acessório. Mudança técnica vincula-se ao ADR e ao changelog.
