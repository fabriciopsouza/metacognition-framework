# ADR 091 — Núcleo product-free: nenhum nome de produto/vendor externo no conteúdo operativo; proveniência só nos ADRs

- Status: **Aceito** (2026-06-19 — constraint explícito do dono "este repo não pode ter domínios, produtos" + "siga"; gate: qa-critic heterogêneo + canário do próprio guard) · Decisores: dono + squad
- Tipo: **enforcement de princípio existente** (P12 / ADR-010/020) + correção de regressão que eu mesmo introduzi. Régua §0 (ADR-007): satisfaz (c) — *destrava* enforcement que o linter de norma não cobria (vendor ≠ norma) reusando o padrão denylist+canário existente; +1 capability `core-no-vendor` (guard).
- Relaciona: **ADR-010/020** (núcleo agnóstico, P12), **ADR-085** (recast — origem do vazamento), ADR-046 (forma vs conteúdo), ADR-072 (anti-reinvenção)

## Contexto

A integração BMAD (v1.62.0–v1.66.0, recasts do ADR-085) deixou **nomes de produto externo** (`bmad-*`, `creative-intelligence-suite`, `game-dev-studio`) no **conteúdo operativo do núcleo** — `methods.md` (descrição do método #77, seção de fase), `execution-modes/SKILL.md`, `source:` de 5 skills, tags do `capabilities.json`. O `check_core_agnostic.py` (ADR-020) **passava**, porque ele barra **NORMAS regulatórias** (ANVISA/ANP/…), não **produtos**. O dono flagou: *"este repo não pode ter domínios, produtos, etc."*

**Distinção que resolve (estende ADR-046 forma-vs-conteúdo):** o **conteúdo operativo** (o que o agente LÊ PARA AGIR — skills, roteador) deve ser **product-free**; a **proveniência** (de onde a técnica veio: BMAD/CIS/etc., com URLs e veredito) é **registro de decisão** e vive nos **ADRs** (`docs/`, que legitimamente citam externo). Citar o *arquivo de ADR* que registra a integração é legítimo; nomear o produto na prosa operativa não é.

## Decisão

**(1) Política:** núcleo operativo (`_shared/`, `.agent/skills|rules|workflows`, roteador `AGENT-FRAMEWORK.md`/`CLAUDE.md`/`AGENTS.md`, e o metadado `capabilities.json`) **não nomeia produto/vendor externo**. A proveniência vai para o ADR; o operativo aponta para o ADR. Linhagem **interna** do framework (ex.: "master v4.1") permanece.

**(2) Mecanismo:** `tools/test_core_no_vendor.py` (fail-closed) — varre o núcleo por slugs de vendor inequívocos (`bmad`, `creative-intelligence-suite`, `game-dev-studio`); **exclui referências a arquivo de ADR** (`docs/adr/0NN-…md`) antes do check (proveniência legítima). Exceção auditável: sentinela `vendor-ok:allow`. Não usa acrônimos ambíguos (CIS/TEA) — evita falso-positivo. +1 capability `core-no-vendor`.

**(3) Limpeza aplicada:** conteúdo operativo + `source:` de 5 skills + `execution-modes` + tags `capabilities.json` → ponteiro ao ADR. ADRs 081/085 retêm a proveniência completa (verificado: continuam nomeando as fontes).

## Alternativas consideradas

1. **Estender o `check_core_agnostic` (denylist de norma) com produtos.** Rejeitada — mistura semânticas (norma regulatória × produto); o `agnostic-denylist.txt` é regulatório. Guard separado é mais claro.
2. **Renomear os arquivos de ADR que têm "bmad" no nome.** Rejeitada — o ADR é *sobre* BMAD (o nome descreve o assunto, como título de paper); quebra todas as referências. O canário exclui ADR-paths.
3. **Deixar como prosa (só limpar, sem guard).** Rejeitada — regrediria (foi assim que vazou). P15: mecanismo, não disciplina.

## Consequências

**Positivas:** núcleo operativo product-free e **verificável mecanicamente** (não só prosa); proveniência preservada nos ADRs (zero perda de rastreabilidade); fecha o vazamento de *produto* que o gate de *norma* não pegava; guard previne regressão futura (incl. em `capabilities.json`, após o qa-critic apontar a lacuna). **Negativas/limite (declarado):** +1 canário/capability; o guard cobre slugs conhecidos (não detecta um vendor *novo* nunca visto — mas o qa-critic + este ADR são a rede); `tools/` (comentários de código) e `docs/` (ADRs) ficam fora de escopo por design (proveniência/infra).
