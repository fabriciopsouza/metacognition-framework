# ADR 040 — Paridade cross-platform real + CI matriz 3 SOs (não `[DESCONHECIDO]`)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: remediação v2 (marco v1.23.0) · Tipo: **novo** (1 workflow CI + 1 runner + 1 canário de paridade) — net-gain por **destravar verificação inalcançável** (régua §0 cláusula c): hoje os `.sh` são paridade não-provada.
- Origem no plano: item 8 (`[CRÍTICA]` + backlog D4). Relaciona: ADR-015 (effect-gate fail-closed), ADR-020 (gate de agnosticismo), todos os hooks `.ps1`/`.sh`.

## Contexto

Toda a cadeia de hooks (`effect-gate`, `mission-gate`, `compaction-gate`, `route-gate`) nasceu
**PowerShell-first**; as versões `.sh` carregam header `[DESCONHECIDO]` — paridade **declarada,
não validada**. Isso limita o teto regulado: um ambiente que valida em Linux (comum em
conformidade) herdaria um gate de segurança **não-testado naquele SO**. Pior: sem prova de
veredito idêntico, uma divergência silenciosa `.sh`↔`.ps1` (ex.: um bypass que o `.ps1` pega e o
`.sh` deixa passar) só apareceria em incidente. Além disso, os `tools/test_*.py` são **canários
standalone** (exit 0/!=0), não casos pytest — não havia entrypoint único de CI.

## Decisão (1 frase ativa)

Criar **`tools/run_canaries.py`** (descobre e roda cada `test_*.py` como subprocesso, exit = nº de
falhas, cross-platform por só usar `sys.executable`), **`tools/test_parity.py`** (exige veredito
`deny`/`allow` **idêntico** entre `effect-gate.ps1` e `.sh` para cada payload, SKIP se faltar
pwsh/bash/jq) e **`.github/workflows/ci.yml`** (matriz `ubuntu+macos+windows`, roda o runner + os
dois tiers do `check_core_agnostic`), de modo que **só com 3 SOs verdes + paridade 100%** seja
honesto remover o `[DESCONHECIDO]` dos headers `.sh`.

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** Paridade fica na fé; teto regulado limitado. **Rejeitada — é o gap (item 8).**
2. **`pytest tools/` como entrypoint.** Quebra: os canários executam em import-time e chamam `sys.exit()` (não são casos coletáveis). Reescrever todos para `def test_*` seria churn grande contra a régua §0 (adição/refactor sem ganho proporcional). **Rejeitada** — runner que respeita a convenção existente é mais barato e fiel.
3. **Reescrever os `.sh` para chamar o `.ps1` via pwsh (eliminar a duplicação).** Prós: zero divergência possível. Contras: mata a razão de existir do `.sh` (rodar onde só há bash); acopla POSIX a PowerShell. **Rejeitada.**
4. **Runner standalone + canário de paridade + matriz CI (ESCOLHIDA).** Prós: prova mecânica nos 3 SOs, fonte única de casos (importa `CASES` do `test_effect_gate`), SKIP honesto quando o ambiente não tem o shell (ambiente nunca reprova build). Contras: paridade hoje cobre só o `effect-gate` (único veredito binário) — hooks de `additionalContext` ficam com paridade estrutural; declarado, não escondido.

## Consequências

**Positivas:** divergência `.sh`↔`.ps1` vira erro de CI, não incidente; entrypoint único e
agnóstico para todo canário futuro (cada item subsequente deste plano só adiciona `test_*.py` e é
pego automaticamente); gate de agnosticismo (2 tiers) roda em todo push/PR.
**Negativas:** a matriz adiciona custo de CI (3 SOs) — aceitável, é a base que prova todo o resto
do plano. **Riscos/limite declarado:** paridade binária só existe para o `effect-gate`; quando o
`overwrite-guard` (ADR-037) ganhar `.sh`, entra na mesma matriz. Vai a `LIMITS.md` (ADR-044) como
"paridade provada: effect-gate; demais hooks: estrutural".

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.23-v1.31-remediacao` · `2026-05-31` · grep `run_canaries|test_parity|ci.yml`
- Artefatos: `tools/run_canaries.py`, `tools/test_parity.py`, `.github/workflows/ci.yml`,
  `tools/requirements-dev.txt`. Canário = `test_parity.py` (verde nos 3 SOs do CI; SKIP local sem jq).
- DONE quando: 3 SOs verdes + paridade 100% → remover `[DESCONHECIDO]` dos headers `.sh` e atualizar
  a matriz de ambiente do README (item 8 do plano).
