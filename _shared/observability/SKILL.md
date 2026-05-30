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

## Telemetria mínima de processo (ADR-017 — coletor único, v1.17.0)
> **2 métricas que mudam decisão, nada além** (P5). Teste: métrica não-aberta em decisão real = dívida.
> Coletor físico = `history.md ## Telemetria` (cross-sessão); IDE complementa lendo o span OTel
> existente. **Não** é dashboard nem coletor novo (anti-andaime JARVIS).

**17-A Blame-attribution (fluxo entre junções, nesta execução):**
- `framework.junction` da **origem do rewind** — decisão que muda: onde reforçar spec/checklist a montante.
- `framework.qa_rounds` — rounds de qa-critic até PASS (proxy de spec rasa nascendo a montante).
- **NÃO** medir: dashboards, latência fina, throughput, "% verde", custo-por-junção (salvo circuit-breaker).

**17-B Tally + classe + poda Chesterton (uso de regra ao longo de sessões):**
- **Tally S/N** por regra-chave (agregado no fim do bloco/dia, **não** por turno) + contador
  `sem-disparo: K` (sessões consecutivas sem disparo; K+1 se não disparou, K=0 se disparou — derivável
  da varredura append-only). É o `K` que torna a poda por N operacionalizável.
- **Classe** (campo `classe` do contrato, ADR-013): `salva-vidas | operacional | andaime`.
- **Poda só `andaime`** quando `sem-disparo ≥ N` (N=5–10, parâmetro [INFERIDO], não constante).
  `salva-vidas` nunca poda por desuso → **nota de verificação**. `operacional` → consolidar, não remover.
  Sem classe → tratar como `salva-vidas` (conservador). **Portão pequeno:** suspender→observar→remover.
- **Tally autorreportado é falível** [DESCONHECIDO]: cruzar com sinal externo (rastro no output?) quando possível.

> **Fronteira (coletor único):** 17-A mede *fluxo entre junções agora*; 17-B mede *uso de regra no tempo*.
> Mesma seção física (`history.md ## Telemetria`), duas métricas — **não** dois sistemas. A matriz de
> relevância instrumentada é **reprovada** (P7): exigiria logits/N+1 passes — andaime que o JARVIS desligou.
