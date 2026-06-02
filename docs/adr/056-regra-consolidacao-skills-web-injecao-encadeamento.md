# ADR 056 — Regra de consolidação skill+companions para o chat + injeção determinística de `## Encadeamento (chat)`

- Status: **Aceito** · Data: 2026-06-02 · Decisores: dono + squad (architect)
- Onda: encarnação web (v1.40.0) · Tipo: derivado do ADR-054 · Atende: REQ-PREM-2, REQ-PREM-3, REQ-PREM-4, REQ-CASCADE-3 (iii, iv) da spec web. GAP-1 resolvido = **gerar do main** (sem moldes externos).
- Política: NOVO. Relaciona: ADR-054 (keystone), ADR-049 (marcadores premium), ADR-051 (companions do discovery), ADR-012 (consumes/produces no front-matter).

## Contexto

No main, um papel é `SKILL.md` + companions on-demand (ex.: `discovery` + 4 companions) — progressive disclosure mecanizado pelo agente que lê o companion certo na hora. **No chat não há progressive disclosure**: ou o arquivo está no contexto, ou não está. Fragmentar um papel em 5 arquivos web cria **companions órfãos** (o modelo pode não puxar o reforço). E os papéis precisam se **encadear** sem runtime. GAP-1 confirmou que não há skills-web pré-feitas → o build **gera do main**, e precisa de uma regra determinística de (a) o que funde com o quê e (b) como o encadeamento é injetado.

## Decisão (1 frase ativa)

**(a) Consolidação:** o build web **funde cada papel + seus companions num único arquivo** (roteador interno em prosa no topo — ex.: `discovery` + `metodo-senior` + `pesquisa-cascata` + `mapeamento-de-processo` + `revisar-projeto-existente` + `elicitation-dimensions` → 1 skill `discovery` web), **mantém papéis distintos separados** (pmo/architect/developer/qa-critic/docops/explorer — encadeiam entre si), e **mantém `_shared` atômico** (referenciado, nunca recopiado). **(b) Encadeamento:** o build **injeta `## Encadeamento (chat)`** em cada skill, **derivado deterministicamente do front-matter** (`role_order` → próximo papel do pipeline; `produces`/`consumes` → artefato-gate de transição; `pass_criteria` → condição binária), nunca escrito à mão.

## Regra de consolidação (determinística)

| Sinal no main | Ação no build web |
|---|---|
| `role_order` igual / companions de um mesmo `name` | **FUNDE** num arquivo; companions viram seções `## (sub-modo) <nome>` sob um roteador de entrada em prosa |
| `role_order` distinto (papel do pipeline) | **MANTÉM SEPARADO**; encadeia via `## Encadeamento (chat)` |
| Vive em `_shared/` | **ATÔMICO**; entra como skill referenciável; skills apontam por nome, não recopiam |
| Companion executável (`*.py`/`*.ps1`/`*.json`) | **REMOVE** (inerte no chat); se era um gate, o conceito vira checkpoint declarado (ADR-057) |

## Injeção de `## Encadeamento (chat)` (determinística do front-matter)

Para cada skill, o build emite ao final:
```
## Encadeamento (chat)
- Próxima: <papel com role_order+1 no pipeline>  (condição: <pass_criteria deste papel>)
- Gate declarado: <se o papel tem efeito T3/E-irreversível em produces → "⚠ checkpoint: confirmação informada antes de avançar">
- Volta para: <papel anterior, se pass_criteria falhar (rewind declarado)>
```
A ordem do pipeline é a canônica (pmo→discovery→architect→developer→qa-critic→docops); `explorer` é chamável lateralmente (read-only), não tem sucessor fixo. Sem `pass_criteria` no front-matter → o build **falha** (não inventa condição) — força o main a declarar.

## Alternativas consideradas

1. **Portar 1:1 (cada companion vira 1 arquivo web).** Cria órfãos; o modelo pode não puxar o reforço sênior. **Rejeitada.**
2. **Fundir TUDO num arquivo gigante (todos os papéis juntos).** Mata o encadeamento por intenção e estoura tamanho (NFR-2). **Rejeitada.**
3. **Fundir por papel + encadear papéis + injeção do front-matter (ESCOLHIDA).** Preserva o roteamento por intenção, elimina órfãos, e o encadeamento é determinístico/auditável (não prosa à mão que defasa).

## Consequências

**Positivas:** o `discovery` web é um arquivo coeso que roteia os 5 ramos internamente (REQ-PREM-3); os papéis encadeiam sem buraco (REQ-PREM-4); o encadeamento nunca defasa do main (é gerado). **Negativas/limite:** skills consolidadas podem se aproximar do teto de tokens (NFR-2 ~5k) → se exceder, dividir **por papel**, nunca por companion; `pass_criteria` vira campo obrigatório no front-matter dos papéis (gate de build). **Anti-JARVIS:** o "gate declarado" injetado carrega sempre a ressalva de ambiente (ADR-054/057) — nunca chama de bloqueio o que o chat não barra.

## Implementação (ponteiro)

- Regras consumidas pelo profile `web` do `export-clean` (ADR-057). DONE-do-architect quando ADR-056+057 aceitos. Canário sugerido (developer): gerar `discovery` web e verificar 5 ramos + `## Encadeamento` presente e correto contra o front-matter.
