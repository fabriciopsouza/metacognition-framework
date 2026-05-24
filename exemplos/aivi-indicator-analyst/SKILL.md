---
name: aivi-indicator-analyst
description: "APLICAÇÃO (exemplo) — análise pontual de um indicador a partir de dados brutos, recortada por período/regional/total, para públicos executivo e analítico. Acessa dados via padrão external-access (consulta a sistema externo) OU recebe arquivo. Ativar quando o usuário pede análise de um indicador específico a partir de dados. NÃO é núcleo do framework."
version: 0.1.0-scaffold
source: "clone de .agent/skills/_template; domínio AIVI pendente das regras emergenciais"
last_review: 2026-05-23
status: SCAFFOLD — bloqueado no domínio até regras de 'AIVI emergencial' chegarem
---

# AIVI Indicator Analyst — APLICAÇÃO (esqueleto)

> Esta é uma **aplicação** do framework, não o núcleo. Tudo que é transversal vem
> de `_shared/` e dos papéis de processo. Abaixo, só o que é específico de AIVI.

## Carregar de `_shared/` (já herdado)
`anti-hallucination` · `confidence-classification` · `traceability` (file-first nas
colunas reais) · `output-format` (reconciliação Total=Σpartes) ·
`high-stakes-gate` (ver justificativa abaixo).

## Gatilhos
- Positivos: "analisa o indicador X"; "como está o indicador Y por período/regional";
  "recálculo de limites a partir destes dados".
- Exclusões: construir dashboard do zero (→ aplicação de BI); decidir arquitetura
  (→ architect); varrer/auditar muitos arquivos só leitura (→ explorer).

## Acesso a dados (padrão `_meta/external-access`)
Duas portas, **mesma saída** (dataframe validado contra schema):
1. **Consulta a sistema externo** — via MCP (qual server = config a definir).
2. **Arquivo recebido** — CSV/XLSX/outro.
> File-first / schema-first obrigatório: inspecionar colunas reais antes de qualquer
> lógica. Nunca assumir nome de campo.

## Recorte (parametrizado, não duplicado)
período | regional | total — como dimensões de filtro. Cada pedido vira uma spec
atômica em `docs/specs/<caso>/`.

## Por que high-stakes-gate
"Emergencial" + "recálculo de limites" + saída que pode ir a decisão executiva
sugere **baixa confiança estratégica** → arquitetura reflexiva (qa-critic + revisão
humana antes de entregar). [INFERIDO do nome — confirmar com as regras reais.]

## Saída em dois modos (`_shared/output-format`)
- **Executivo:** o número + variação vs período/meta + "e daí" + próximo movimento.
- **Analista:** o mesmo + a query/origem + premissas + validações + drill-down.

## ⚠️ DOMÍNIO PENDENTE — [DESCONHECIDO], não inventar
As regras de cálculo do "AIVI emergencial" (limites/batentes, recálculo, critérios
de disparo) **não foram fornecidas** — repo `LIMITES-BATENTES-RECALC` inacessível.
Sem elas, NÃO definir: fórmula de recálculo, gatilho de "emergencial", thresholds.
→ Preencher esta seção e o `validation.md` da spec quando as regras chegarem.
