# `_shared/` — Núcleo SSoT (genérico, agnóstico de domínio)

> Fonte única das regras transversais. Cada regra mora em **um** arquivo;
> papéis e aplicações **referenciam**, não copiam. Nada aqui conhece domínio.

## Skills do núcleo
| Skill | Papel |
|---|---|
| `confidence-classification/` | CONFIRMADO/INFERIDO/DESCONHECIDO + ALTA/MÉDIA/BAIXA |
| `anti-hallucination/` | NÃO SEI, anti-fabricação, gatilhos de tolerância zero |
| `output-format/` | templates de saída + checklist de validação |
| `traceability/` | file-first + anti-rename + preservação + decisão→fonte→versão |
| `metacognition-core/` | anti-loop + precedência + 5 etapas + checkpoint + context engineering |
| `observability/` | OTel GenAI, audit hook, logs imutáveis |
| `high-stakes-gate/` | validação por risco + audit trail + HITL — genérico; normas específicas = config de aplicação |

## Regra de referência
Papel/aplicação instrui "carregar `_shared/X` antes de responder". Em IDE, lê via
filesystem; em chat web, referencia do contexto do Projeto. Nunca duplica.
