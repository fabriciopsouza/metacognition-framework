# ADR 057 — Contrato do profile `web` no `export-clean.py` + ordem da cascata + carimbo de versão anti-defasagem

- Status: **Aceito** · Data: 2026-06-02 · Decisores: dono + squad (architect)
- Onda: encarnação web (v1.40.0) · Tipo: derivado do ADR-054 (último do conjunto architect) · Atende: REQ-CASCADE-1..6, REQ-SAFE-1/3 da spec web.
- Política: NOVO. Relaciona: ADR-054 (keystone), ADR-056 (consolidação), ADR-049 (profiles premium/baseline + `premium:start`), incidente 2026-05-31 (`anonymize.py` + gate `--sensitive` como padrão reusável).

## Contexto

ADR-054 decidiu que a cascata web é um **profile do `export-clean.py`**, não pipeline novo. Falta o **contrato**: que transformações o profile `web` aplica, em que ordem a cascata roda, e como o carimbo de versão mata a defasagem (o bug atual: prompt v4.3 / roteador v2.x enquanto o main está v1.39.0). O `export-clean.py` já oferece o padrão reusável: `STRIP_*` (listas de remoção), `strip_premium_markers` (blocos `<!-- premium:start -->`), `anonymize.py` (substituição determinística por mapa) e o **gate `--sensitive`** (aborta se token proibido sobrevive).

## Decisão (1 frase ativa)

Adicionar `--profile {baseline,premium,web}` ao `export-clean.py`: o profile `web` aplica, **deterministicamente e nesta ordem**, (1) STRIP de companions executáveis (`*.py`/`*.ps1`/`*.json`); (2) consolidação papel+companions (ADR-056); (3) injeção de `## Encadeamento (chat)` (ADR-056); (4) substituição IDE→chat via **`web-phrasing-map.txt`** (mesmo padrão do `anonymize-map.txt`: "hook/gate/barra determinístico" → "checkpoint declarado + ressalva de ambiente"); (5) geração do tier público (condensa `_shared`); (6) **carimbo** do `commit-sha` + versão do main em cada artefato; finalizando com um **gate anti-JARVIS** (análogo ao `--sensitive`) que **aborta** se sobreviver termo de enforcement sem ressalva. Saída → repo dedicado `-web` (sentido único main→web).

## Por que map + gate (não rewrite cego) — régua §0

O reword IDE→chat **não** pode ser regex cega (corromperia usos legítimos). Reusa-se o **par já provado** do incidente: um **mapa determinístico** (`web-phrasing-map.txt`, ordenado, como o `anonymize-map.txt`) faz o grosso; um **gate de fechamento** (como `check_core_agnostic --sensitive`) **falha o build** se algum "gate/barra/bloqueio" sobreviver sem a ressalva de ambiente. Assim "anti-JARVIS" é **verificável**, não confiança — mesma doutrina do tier de telemetria (ADR-052) e do export sensível.

## Ordem da cascata (REQ-CASCADE-6)

```
main (SSoT) → baseline/premium não-web [JÁ EXISTEM] → web premium → web público
```
Web por último (mais derivado/condensado). Cada estágio só roda se o anterior passou. O profile `web` roda **depois** dos não-web, lendo a MESMA árvore-fonte sanitizada.

## Carimbo anti-defasagem (REQ-CASCADE-5)

Cada artefato web gerado recebe, no topo, `framework_version: <X.Y.Z>` + `source_commit: <sha>` do main que o gerou. O `consistency-gate` ganha dimensão fail-soft: **se a versão de um artefato web ≠ versão do main do commit, sinaliza**. Mata o bug "web declara v4.3 enquanto main é v1.39.0" porque a versão deixa de ser escrita à mão.

## Alternativas consideradas

1. **Script web separado.** Duplica strip/anonimização/gate. **Rejeitada (régua §0).**
2. **Rewrite cego IDE→chat por regex.** Corrompe texto legítimo; sem gate de verificação. **Rejeitada.**
3. **Profile no export-clean + map + gate anti-JARVIS + carimbo (ESCOLHIDA).** Reusa STRIP/anonymize/`--sensitive`; o anti-JARVIS vira gate verificável; a versão vira carimbo (não prosa). Net-gain.

## Consequências

**Positivas:** web nunca mais defasa (carimbo + consistency-gate); "anti-JARVIS" é gate, não promessa; zero pipeline novo. **Negativas/limite:** o `web-phrasing-map.txt` precisa de manutenção (como o `anonymize-map`) — mas é a mesma disciplina já existente; determinismo exige que a consolidação (ADR-056) seja estável (ordenação fixa de companions). **Repo `-web`:** criado quando o `developer` implementar (não neste ADR). **Eval:** token público real (GAP-3) e paridade Gemini (GAP-4/NFR-1) validados na implementação, antes de declarar suporte.

## Implementação (ponteiro — developer)

- Estender `tools/export-clean.py` (`--profile web`), criar `tools/web-phrasing-map.txt` + gate anti-JARVIS (espelhar `check_core_agnostic --sensitive`), wirar carimbo + dimensão no `consistency-gate`, criar repo `metacognition-framework-web` + workflow (espelhar `publish-clean.yml`). DONE quando: build web determinístico (2× = idêntico), versão carimbada == main, gate anti-JARVIS verde, tiers público/premium gerados. Conjunto architect (ADR-054/055/056/057) **fechado** → handoff ao developer.
