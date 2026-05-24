# Regra 04 — Roteamento por Classe de Confiança

> Decide QUAL arquitetura o squad usa, conforme o risco da tarefa.
> Fonte: pesquisa A3 (governança em ambiente regulado). Liga contexto operacional ↔ contexto regulado.

## A confiança da spec governa a arquitetura

| Classe | Quando | Arquitetura | Aprovação |
|---|---|---|---|
| **Alta confiança operacional** | Módulo interno isolado, script trivial, rotina de alto volume previsível | **Orquestrador-Trabalhador Linear** — trabalhadores independentes | Bateria de validação unitária do `validation.md` basta |
| **Baixa confiança estratégica** | Módulo regulado, rota exposta, controle de banco, número que vai a decisão executiva | **Multi-agente Reflexivo** — invoca Subagente Crítico obrigatório | Hand-off **bloqueado**; só fecha após revisão humana sobre *diffs* estruturados |

## Mapeamento aos dois ambientes
- **Contexto operacional de alto volume:** rotina previsível → **linear**. (Otimizar com
  model cascading + cache semântico — pesquisa A2.)
- **Contexto regulado / crítico / irreversível:** → **reflexivo** + `_shared/high-stakes-gate`
  + ALCOA+ / audit trail antes de qualquer promoção.

## Como aplicar
1. Ler a confiança declarada no `requirements.md` da spec.
2. Se BAIXA (ou tarefa regulada/irreversível) → forçar QA-Critic adversarial +
   hand-off bloqueado até OK humano. Nunca tratar como rotina linear.
3. Se ALTA → fluxo linear; QA-Critic ainda roda (sempre), mas sem bloqueio humano
   obrigatório.

> O QA-Critic **sempre** executa. O que muda por classe é a **intensidade** da
> arquitetura e a obrigatoriedade da revisão humana no hand-off.
