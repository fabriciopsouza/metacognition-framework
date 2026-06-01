# Blueprint de produto — domínio Mapeamento de Processos (ADR-046)

> Carregado **sob demanda** quando `product_type` é de processo de negócio. O `discovery` (sub-modo
> *mapeamento de processo*, já existente) elicita; este blueprint define a **forma premium do
> entregável** que o discovery **propõe de uma vez**. Agnóstico (forma, não conteúdo de domínio).

## Proposta assertiva (default sênior — confirmar/ajustar numa batelada)

Para `product_type ∈ {process-map, bpmn, process-improvement}`, propor:

1. **Mapa as-is + to-be** com, por etapa: **gatilho** · **dono** · **entradas/saídas** · **regras de
   negócio** · **handoffs** (quem→quem) · **exceções/caminhos de erro**. (É o que o sub-modo elicita.)
2. **Diagrama visual** (BPMN ou Mermaid) — o entregável premium é **visual**, não só tabela. Um
   fluxograma legível por não-técnico + a tabela RACI ao lado.
3. **Gap analysis as-is→to-be** com recomendações priorizadas (impacto × esforço) — o valor está na
   *diferença*, não no desenho.
4. **Sumário executivo** (1 página): dores, ganhos do to-be, riscos da transição, próximos passos.
5. **Rastreabilidade:** cada regra/exceção referencia a fonte (entrevista/documento) — anti-fabricação.

## Definição de pronto
Spec cobre as dimensões do sub-modo (gatilhos/RACI/handoffs/exceções) · diagrama gera sem erro ·
gap analysis tem recomendação por gap · sumário executivo presente. A decisão to-be que muda
arquitetura de processo vira **ADR de processo** (architect), não decisão implícita.

## Ativação
Ver `product-types.txt`. O sub-modo do discovery é o motor de elicitação; o `architect` decide o to-be
(ADR de processo). Sem aplicação → defaults flexíveis.
