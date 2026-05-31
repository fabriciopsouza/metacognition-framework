# ADR 042 — Discovery: sair de DESIGN-TIME (eval G/H executado)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: remediação v2 (marco v1.29.0) · Tipo: **novo** (1 canário de eval + registro) — net-gain por destravar verificação inalcançável: a senioridade do discovery era promessa não-medida.
- Origem no plano: item 10 (`[CRÍTICA]` + backlog D3). Relaciona: ADR-033 (dimensões de elicitação), `_meta/eval-results-papeis.md` (A–F executado, G/H design-time), ADR-040 (CI).

## Contexto

Os evals dos papéis `discovery` (G) e `mapeamento de processo` (H) estavam **NÃO EXECUTADOS**
(DESIGN-TIME / [EMERGENTE] desde v1.5.0). A senioridade central do framework — "o discovery extrai uma
spec de nível sênior" — era **promessa não-medida**. A régua reitora ("nada importante em prosa") pede
prova executável.

## Decisão (1 frase ativa)

**Executar** o eval de G e H em duas camadas: (1) **roteamento** (should-trigger/should-NOT contra a
`description` real, como A–F) registrado em `_meta/eval-results-discovery.md`; e (2) **funcional
mecanizado e reproduzível** via `tools/test_discovery_eval.py` — ≥3 briefings sintéticos agnósticos cuja
saída de discovery é medida por `check_spec_depth` (cobertura das dimensões do ADR-033), incluindo um
controle "raso" que DEVE reprovar (o eval discrimina) — marcando G/H **EXECUTADO**.

## Alternativas consideradas (≥3)

1. **Deixar DESIGN-TIME (status quo).** A senioridade fica como claim não-provado. **Rejeitada — é o gap.**
2. **Rodar um eval com LLM-juiz medindo "qualidade sênior".** Não-determinístico/caro no CI; a qualidade do default é julgamento. **Rejeitada** — mede-se cobertura + roteamento; qualidade fica adversarial (LIMITS.md).
3. **Tabela executada uma vez (sem canário).** Não regride: uma mudança futura no discovery não seria pega. **Rejeitada** — o eval funcional vira canário reproduzível no CI.
4. **Roteamento (tabela) + funcional (canário reproduzível) (ESCOLHIDA).** Prós: G/H deixam de ser promessa; regressão pega pela matriz CI. Contras: não mede qualidade sênior do default → `LIMITS.md`.

## Consequências

**Positivas:** G e H deixam DESIGN-TIME; a cobertura de dimensões do discovery é medida e protegida
contra regressão (CI). **Negativas:** nenhuma estrutural (reusa `check_spec_depth`). **Riscos/limite
declarado:** o eval mede **cobertura + discriminação raso×sênior**, não a *qualidade sênior* do default
(não-mecanizável) → `LIMITS.md`.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.23-v1.31-remediacao` · `2026-05-31` · grep `test_discovery_eval|eval-results-discovery`
- Artefatos: `tools/test_discovery_eval.py` (3 briefings + controle raso), `_meta/eval-results-discovery.md`
  (roteamento G/H + funcional), atualização do status em `_meta/eval-results-papeis.md`.
- DONE quando: G e H **EXECUTADO** (não design-time). [CONFIRMADO — canário verde no CI]
