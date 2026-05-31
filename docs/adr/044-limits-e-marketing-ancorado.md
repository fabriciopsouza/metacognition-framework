# ADR 044 — LIMITS.md mecanizado + marketing ancorado em evidência

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: remediação v2 (marco v1.31.0, último) · Tipo: **novo** (1 gerador + 1 canário + LIMITS.md) — net-gain: mecaniza a transparência (substitui promessa por prova ligada ao CI).
- Origem no plano: item 13 (`[CRÍTICA]` + decisão do dono: marketing honesto). Relaciona: TODOS os ADRs 033–043 (cada um declarou um "limite") + ADR-040 (CI) + ADR-025 (transparência).

## Contexto

A transparência do framework estava **dispersa** (cada ADR declarava seu limite em prosa). Faltava um
**índice único, mecanizado e ligado ao CI** do que o framework **garante**, **prova** e **NÃO faz** — e
uma trava que impeça o marketing (README/site) de prometer mais do que os canários sustentam. A régua
reitora do plano exige: prosa só onde não-mecanizável, **e então declarada em `LIMITS.md`**.

## Decisão (1 frase ativa)

Criar **`tools/build_limits.py`** (gera `LIMITS.md` a partir do estado real dos canários: canário verde
no CI → ✅ PROVADO; ausente → ⏳ EM DESENVOLVIMENTO; cada linha com o que É e o que NÃO é mecanizado) com
modo **`--check`** que **falha o CI se `LIMITS.md` divergir** dos canários, e o canário
**`tools/test_marketing_claims.py`** que reprova claim `✅ PROVADO` órfão (sem canário) em
README/PITCH e exige o README **linkar** o `LIMITS.md`.

## Alternativas consideradas (≥3)

1. **Manter limites dispersos em prosa (status quo).** Sem índice, sem trava — o marketing pode driftar do real. **Rejeitada — é o gap.**
2. **LIMITS.md escrito à mão.** Mente com o tempo (drift). **Rejeitada** — `--check` no CI garante sync.
3. **Selos de marketing manuais sem linter.** Claim ✅ órfão passa. **Rejeitada** — `test_marketing_claims` reprova órfão.
4. **Gerador a partir dos canários + `--check` no CI + linter de claims (ESCOLHIDA).** Prós: honestidade mecanizada, doc não-mente, marketing ancorado. Contras: "PROVADO" = canário existe + CI verde (não re-roda no gerador, por custo) — declarado: a prova viva é a matriz CI (ADR-040).

## Consequências

**Positivas:** transparência vira artefato versionado e verificado; o README aponta para um `LIMITS.md`
que **não pode mentir** (CI trava drift); claims ✅ sem canário são reprovados. **Negativas:** o status
`PROVADO` assume que o CI roda a suíte verde (semântica documentada). **Riscos/limite declarado:** o
gerador checa **existência** do canário (não re-executa) — a execução verde é responsabilidade da matriz
CI (ADR-040); por isso "PROVADO" lê-se como "há canário e o CI está verde", não "certificado".

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.23-v1.31-remediacao` · `2026-05-31` · grep `build_limits|LIMITS.md|test_marketing_claims`
- Artefatos: `tools/build_limits.py`, `LIMITS.md` (gerado, 13 capacidades), `tools/test_marketing_claims.py`,
  step `--check` no `.github/workflows/ci.yml`, pointer no `README.md`.
- DONE quando: `LIMITS.md` em sync com CI, linkado no topo; zero claim ✅ órfão. [CONFIRMADO]
