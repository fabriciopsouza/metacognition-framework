# Blueprint de produto — domínio Gestão de Projetos (ADR-046)

> Carregado **sob demanda** quando `product_type` é de gestão de projeto. O `discovery` elicita escopo/
> stakeholders/restrições; este blueprint define a **forma premium do entregável** que o discovery
> **propõe de uma vez**. Agnóstico (forma, não conteúdo).

## Proposta assertiva (default sênior — confirmar/ajustar numa batelada)

Para `product_type ∈ {project-plan, status-dashboard, project-charter}`, propor:

1. **Escopo + WBS** (decomposição em entregáveis verificáveis) + **fora-de-escopo** explícito.
2. **Marcos + dependências** (sequência, caminho crítico) e **RACI** por entregável.
3. **Riscos** (probabilidade × impacto + mitigação/contingência) — registrados, não implícitos.
4. **Dashboard de status** (planejado × realizado, % por marco, bloqueios) — atualizável, não estático.
5. **Apresentação executiva** (1 deck): objetivo, marcos, riscos-chave, decisão pedida ao patrocinador.
6. **Rastreabilidade + cadência:** cada número de status tem fonte; mudança de escopo vira decisão
   registrada (change control), não silenciosa (alinha ADR-034 completude).

## Definição de pronto
Escopo IN/OUT + WBS + marcos + RACI + riscos + dashboard + deck executivo presentes; cada estimativa
classificada `[CONFIRMADO|INFERIDO|DESCONHECIDO]` (anti-fabricação); mudança de escopo com change control.

## Ativação
Ver `product-types.txt`. `pmo` orquestra; `architect` para decisões técnicas; `discovery` para elicitação
de escopo/risco. Sem aplicação → defaults flexíveis.
