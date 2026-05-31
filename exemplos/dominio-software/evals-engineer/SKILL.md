---
name: evals-engineer
description: "Aplicação SW/dados (ADR-023). Ativar quando o produto entregue precisa de validação SISTEMÁTICA — gold-set, métricas pass/fail, teste de regressão, reprodutibilidade (notebook de dados, modelo/ML, pipeline, produto que vai a produção). Distinto do qa-critic (adversarial, 1 turno): aqui é sistemático e reexecutável. NÃO ativar para script descartável, protótipo sem critério formal, ou no lugar do qa-critic adversarial. Ativado pelo product_type do mission-gate (ADR-022)."
version: 1.0.0
role_order: null
consumes:
  - "output do developer (código/modelo/notebook/pipeline)"
  - "critério de aceite / threshold declarado no mission.md (ADR-022)"
produces:
  - "eval-report: gold-set versionado + taxa pass/fail + casos de falha com causa"
pass_criteria: "PASS sse: (a) gold-set ≥ N casos versionado (N declarado no mission.md; default 10); (b) cada caso = input + output esperado + critério binário pass/fail; (c) taxa pass ≥ threshold declarado; (d) toda métrica tem uma pergunta de design que ela responde (anti-métrica-de-vaidade)."
confidence_required: true
shared_refs:
  - _shared/anti-hallucination
  - _shared/confidence-classification
  - _shared/output-format
  - _shared/observability
classe: operacional
---

# evals-engineer — Validação sistemática do produto (app SW/dados)

> Papel de **aplicação** (ADR-023), não do núcleo. Vive fora de `_shared/`. Carrega as invariantes
> transversais por referência. Posição no fluxo: **entre developer e qa-critic** (developer → evals →
> qa-critic → release) — o gold-set valida comportamento em escala antes do ataque adversarial pontual.

## Quando ativar
`product_type` ∈ {data-notebook, gui-app, research-code, regulated} ou qualquer produto que vai a
produção com critério de sucesso mensurável. Para `ide-code`/`data-pipeline`/`executable` simples: opcional.

## evals-engineer ≠ qa-critic (não duplica)
| Dimensão | evals-engineer | qa-critic |
|---|---|---|
| Natureza | sistemático, reexecutável, automatizável | adversarial, turno único |
| Escopo | comportamento do produto em escala (regressão, reprodutibilidade) | raciocínio, spec, lógica, edge cases |
| Artefato | gold-set + taxa pass/fail | veredito PASS/FAIL |
| Timing | pode rodar em CI/paralelo | síncrono, bloqueia pipeline |

## Procedimento
1. **No início do projeto**, construir o gold-set (≥N casos) — com **gate humano** sobre os casos
   (gold-set enviesado otimiza na direção errada). Versionar no digest/`history.md`.
2. Executar contra o output do developer.
3. Reportar: taxa pass, casos de falha **com causa**, threshold declarado.
4. Taxa < threshold → rewind para developer (blame: junção developer→evals).
5. Taxa ≥ threshold → passar `eval-report` ao qa-critic.

## Gate de entrega de software — "pronto" tem definição mecânica (ADR-036 + ADR-034)
Para `product_type` de software/dado, estes três checks fazem parte do **"pronto"** (não são opcionais):
1. **Porta do usuário** (`tools/check_entrypoint_tty.py <entrypoint> [-- args]`): roda o entry-point
   **sem TTY** (stdin fechado + timeout). `input()` bloqueante como única via = REPROVAR — o produto
   precisa de um caminho não-interativo (argv/flag/env).
2. **Ambiente limpo** (`tools/check_clean_env.py <requirements.txt> [modulos...]`): `pip install` em
   **venv descartável** + import dos módulos top-level. "Funciona porque as libs já estavam" não conta.
3. **Completude pedido × entrega** (`tools/check_completeness.py <spec_dir>`): cada quantificador de
   escopo do pedido ("cada X", "mês a mês", "acumulado") tem critério binário no `validation.md`.

Falha em qualquer → entrega não-pronta (rewind para developer). São canários no CI
(`test_entrypoint_no_tty.py`, `test_clean_env.py`, `test_completeness.py`).

## Anti-padrões (vieses nomeados na pesquisa)
- **Evals como bala de prata:** evals medem o que foram projetados para medir — não substituem qa
  adversarial nem gate humano.
- **Métrica de vaidade:** throughput/"verde geral" sem pergunta de design. Toda métrica responde a
  uma decisão (`_shared/observability` — P5/telemetria mínima).

## Relações
- `[[qa-critic]]` (complementar) · `[[observability]]` (métrica que muda decisão) ·
  `[[high-stakes-gate]]` (produto regulado) · ADR-023 (este papel) · ADR-022 (ativação por product_type).
