---
name: output-format
description: "Núcleo SSoT do formato de entrega e da validação obrigatória. Carregar antes de entregar qualquer fórmula, cálculo, código, visualização ou modelo. Define os templates de saída por modo e o checklist único de validação (edge cases, DIV/0, NULL, agregação). NÃO carregar para conversa casual."
version: 1.0.0
source: "master v4.1 §9 e §10 + metacognição v2.2 §3 + SQUAD v1.1.0 (developer/qa-critic/bi-deliverable)"
last_review: 2026-05-23
---

# Formato de Saída e Validação — Fonte Única

## Parte A — Formato por modo

**Casual / factual:** resposta direta, sem tags, sem cabeçalho. Anti-alucinação
em modo silencioso.

**Metacognição (tarefa pontual):**
```
[ENTENDIMENTO] reformulação do pedido em 1-2 frases
[ABORDAGEM]    método proposto
[SOLUÇÃO]      código/fórmula/explicação
[VALIDAÇÃO]    edge cases testados, premissas, ressalvas
[CONFIANÇA]    classificação por afirmação relevante
```

**Squad (por papel):**
```yaml
papel: <pmo|architect|developer|qa-critic|docops|explorer>
classificacao: [CONFIRMADO|INFERIDO|DESCONHECIDO]
fontes_consultadas: [arquivos/docs lidos]
artefatos: [paths gerados/alterados]
proximos_passos: [...]
escalacoes: [...]
```

Anti over-formatting: sem ASCII boxes; emojis só com função semântica
(⚠️ alerta, 🛑 stop, 📍 checkpoint); listas só com ≥3 itens paralelos;
tabelas só quando comparam algo de fato.

## Parte B — Checklist único de validação (antes de entregar)

**Técnico**
- [ ] Sintaxe sem erro (linter / compilador / checagem da ferramenta)
- [ ] Tipos consistentes; conversão explícita antes de lógica numérica
- [ ] NULL tratado (`IFNULL`/`ZN`/`try/except`)
- [ ] DIV/0 tratado (`ZN`, `DIVIDE`, `IIF` com guard, `IFERROR`)
- [ ] Edge cases: zero, NULL, negativo, extremo, string vazia
- [ ] Agregação no nível correto (sem mix AGG/non-AGG)

**Lógico**
- [ ] Resultado em ordem de magnitude esperada
- [ ] Cross-check com fonte alternativa quando possível
- [ ] Reconciliação Total = Soma das Partes (quando aplicável)
- [ ] Premissas explícitas

**Visual (quando aplicável)**
- [ ] Título + subtítulo com guia de leitura inline (ex.: `BARRA=Real | ◆=Meta`)
- [ ] Cores acessíveis; eixos com range apropriado
- [ ] Aspect ratio igual em scatter/quadrante

**Test cases obrigatórios** para fórmula/cálculo crítico: tabular Normal / Zero /
NULL / Negativo / Extremo com input, esperado, resultado, status.
