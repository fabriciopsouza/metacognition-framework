# Isolamento de Subagente

> Quando um papel deixa de ser *hat sequencial* e vira **subagente com contexto
> isolado**. Fonte: pesquisas A1/A2 (orquestrador-trabalhador, contexto fresh).

## Princípio: menor privilégio cognitivo
O Orquestrador lê o `plan.md`/`requirements.md`, decompõe e despacha. Trabalhadores
são instâncias **efêmeras** — não herdam a memória da conversa do Orquestrador.

## O subagente recebe, e só:
1. O **extrato relevante** da constituição (mission/tech-stack/regras aplicáveis).
2. A **tarefa específica** delimitada pelo `requirements.md`.
3. **Exclusivamente** os fragmentos de código/dados afetados.

## Regras de comunicação
- Contexto do subagente começa **fresh** (reconstruído do zero).
- Pai e filho se comunicam **só** pela string do tool e pelo retorno final.
- Subagente **não** invoca subagente (por design — evita explosão combinatória).
- Trade-off: isolar reduz *context rot* mas elimina visão lateral → passar
  **explicitamente** todos os file paths, mensagens de erro e decisões necessárias.

## Quando isolar (resumo da matriz de decisão — A2)
| Isolar SE… | NÃO isolar SE… |
|---|---|
| subtarefa precisa de tools diferentes | depende fortemente do raciocínio anterior |
| polui o contexto principal (busca, exploração) | decisão irreversível (manter no principal + confirmação humana) |
| pode rodar em paralelo e compensa o custo (~15×) | tokens são restrição dura |

Candidatos naturais a subagente: **QA-Critic** (contexto fresh evita viés de
auto-aprovação) e **explore read-only** (mapeia código/dados sem poluir o principal).

## Heterogeneidade de modelo gerador↔crítico (ADR-018 v1.18.0)
Isolar o qa-critic não basta: a alavanca que **paga** é rodá-lo em **família de modelo diferente** do
developer/gerador — Zhang et al. 2025 (Heter-MAD) mostra que heterogeneidade > número de papéis, e que
multi-agent debate homogêneo não supera self-consistency. No Claude Code: `Agent(..., model: <distinto
do gerador>)`. **Priorizar isso sobre qualquer estrutura de debate/Conclave** (reprovado por P6). No
chat sem troca de modelo, a heterogeneidade fica indisponível — **declarar, não fingir** independência.

## ⚠️ Ressalva de ambiente [CONFIRMADO]
- **Claude Code / SDK:** isolamento **real** (subagente com contexto e tools próprios).
- **Chat web (Claude.ai / Gemini):** **não há** subagente — degrada para *hats*
  sequenciais com enquadramento isolado simulado. O conteúdo das regras não muda;
  só o mecanismo. Para QA-Critic, usar modelo diferente do Developer continua valendo.
