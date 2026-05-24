# /sap-change <CR-ID> — EXEMPLO de workflow de domínio (regulado)

> Aplicação do framework a um contexto de change regulado. NÃO é núcleo.
> Usa `_shared/high-stakes-gate` (genérico) + a config de domínio em
> `exemplos/regulated-pharma`.

Sequência: PMO → aplicação de domínio → developer → qa-critic → docops.
Gate: high-stakes (HITL obrigatório, audit trail, rollback documentado, logs imutáveis).
Critérios específicos (normas setoriais) vivem na config da aplicação, não aqui.
