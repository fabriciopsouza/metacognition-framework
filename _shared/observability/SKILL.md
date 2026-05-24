---
name: observability
description: "Carregar quando a tarefa exige rastreabilidade auditável de execução de agente: ambiente regulado, decisão de alto risco, ou auditoria de custo/qualidade. Define o que logar (OTel GenAI), o hook de auditoria e a regra de logs imutáveis. NÃO necessária para conversa casual ou tarefa pontual de baixo risco."
version: 1.0.0
source: "pesquisa A3 (observabilidade agêntica, OTel GenAI) + A2 (audit hook)"
last_review: 2026-05-23
---

# Observabilidade GenAI — Rastreabilidade Ponta a Ponta

> Em ambiente regulado, o log **é parte do entregável**. Trabalha com
> `_shared/traceability` (cadeia decisão→fonte→versão).

## O que capturar por execução de agente
- Prompt completo, ferramentas chamadas, parâmetros, retornos.
- Modelo/versão, tokens, latência.
- **Multi-agente:** a árvore completa (parent → child) com identificadores correlacionados.
- Vincular cada run à **versão da spec** (`spec_sha`) que a originou.
- Domínio regulado: **logs imutáveis**.

## Campos OTel GenAI (semantic conventions)
```
gen_ai.usage.input_tokens
gen_ai.agent.name
error.type
```
Permitem associar microscopicamente cada subida de custo ou desvio de atenção ao
trabalhador individual acionado — auditável a reguladores.

## Hook de auditoria (Claude Code — PostToolUse)
Logar em `audit-log.jsonl` versionado, por chamada:
```
(timestamp, skill_versions_loaded, model, tools_used, sources, output_hash)
```

## ⚠️ Ressalva de ambiente [CONFIRMADO]
- **Claude Code / SDK:** hooks e traces automáticos.
- **Chat web:** sem hook — degrada para **checklist manual**. O bloco de saída por
  papel (`_shared/output-format`, modo squad) já captura `fontes_consultadas` e
  `artefatos`; em regulado, registrar manualmente model/versão/spec no checkpoint.
