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
- **Contexto declarado pelo discovery como regulado / crítico / irreversível** (ADR-010): → **reflexivo** + `_shared/high-stakes-gate` + audit trail antes de qualquer promoção. Norma específica e critérios de audit são declarados no `requirements.md` do projeto, não pré-listados aqui.

## Como aplicar
1. Ler a confiança declarada no `requirements.md` da spec (seção `## Escopo declarado pelo discovery`, ADR-010).
2. Se BAIXA (ou discovery declarou regulado/irreversível) → forçar QA-Critic adversarial. **HITL adicional** (hand-off bloqueado até OK humano) é governado pelo modo de execução em vigor (ADR-005): modo `default` bloqueia em mais ações; `avançado` só em git push/merge/PR; `autosuficiente` libera. Roteamento reflexivo NÃO duplica HITL — os dois eixos são independentes.
3. Se ALTA → fluxo linear; QA-Critic ainda roda (sempre); HITL segue o modo de execução.

> O QA-Critic **sempre** executa. O que muda por classe é a **intensidade** da
> arquitetura (linear vs reflexivo). HITL é eixo separado — vive em ADR-005 / execution-modes.
