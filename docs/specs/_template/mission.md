# mission.md — Missão do projeto/feature (ADR-022)

> **Lar persistente** do escopo declarado pelo discovery (ADR-010/012) **+** o `product_type` que
> ativa os papéis especializados (ADR-023). Não é artefato paralelo: funde a declaração de escopo
> num só lugar (régua §0). O hook `mission-gate` (SessionStart, ADR-022) lê este arquivo e injeta a
> diretriz BRIEFING/ADVANCE/STANDARD conforme o modo de execução (ADR-005). Sem `product_type`
> declarado, o pipeline não deve avançar para implementação (J2+) sem confirmação.
>
> Clonar para a raiz do projeto (`mission.md`) ou `docs/specs/<caso>/mission.md` e preencher.

## Produto (campo lido pelo mission-gate — ADR-022)

Declare o tipo de produto na forma **inline** `product_type: <valor>` (uma linha; NÃO como heading):

```
product_type: <ide-code | executable | gui-app | data-notebook | data-pipeline | research-code | report | spec | regulated>
```

> Os valores são a taxonomia da app SW/dados (`exemplos/dominio-software/product-types.txt`), que ativa
> os papéis especializados. Sem aplicação de domínio → declare livremente o FORMATO de entrega esperado.
> Enquanto o valor for o placeholder `<...>`, o mission-gate mantém o estado ADVANCE.

## Objetivo (1 frase) e critério de aceite
- Objetivo: <o que entregar>
- Aceite (binário): <condição objetiva de "pronto">

## Escopo declarado pelo discovery (ADR-010/012 — passo 6)
- (a) Regulado? quais normas? vigência? <...>
- (b) Alto-risco / decisão downstream irreversível/financeira/auditável? <...>
- (c) Regra de negócio com peso semântico (anti-fraude, audit trail, fairness)? <...>
- (d) Gaps não-bloqueantes (flagados, não silenciados)? <...>
- (e) Alimenta outra sessão/agente? → Pacote de handoff obrigatório (ADR-012). <...>
- (f) **product_type** confirmado pelo dono? <sim/não> · modo de execução no momento: <default|avançado|autosuficiente>
