# ADR 083 — Coaches cross-IA (web-bundles): planejamento em Gemini/ChatGPT como builder+manifesto+canário

- Status: **Aceito** (2026-06-16 — gate: qa-critic heterogêneo) · Data: 2026-06-16 · Decisores: dono (pedido explícito "incluindo artefatos cross ai", "ferramental, não prosa, determinismo") + squad
- Onda: conclusão do mapa de integração BMAD (item deferido em v1.59.0) · Tipo: **adição autorizada pelo dono** — destrava planejamento cross-IA com artefatos prontos (régua §0: autorização explícita + plugado no mecanismo existente, não duplicado)
- Relaciona: ADR-054/056/057 (web-export — mesmo molde de geração determinística + anti-JARVIS), ADR-069 (protocolo cross-IA), ADR-072 (capabilities derivado + canário), ADR-081 (Spec Kernel reusado no product-brief-coach)

## Contexto

O mapa de integração BMAD (ADR-081) deferiu os **web bundles / coaches** (planejamento em Gemini/ChatGPT, implementação no IDE). O dono pediu para concluir, com ênfase: **"ferramental, não prosa, determinismo"** — ou seja, não 6 markdowns soltos, mas um pipeline gerado-e-gateado como o resto do framework.

O BMAD-METHOD shippa web-bundles (brainstorming, product-brief, prd, prfaq, ux, market-research) como Gems/GPTs para fazer o upfront-planning fora do IDE metered. O metacognition já tinha a *encarnação web* do framework (`web_export.py` → `PROMPT-CHAT-WEB`), mas não coaches por-artefato.

## Decisão (1 frase ativa)

Criar **`web-bundles/coaches.json`** (fonte única — 6 coaches como DADO) + **`tools/build_web_bundles.py`** (builder DETERMINÍSTICO que reusa o phrasing-map anti-JARVIS e o `main_version` do `web_export.py`, gerando `web-bundles/<id>.md` autocontidos) + **`tools/test_web_bundles.py`** (canário FAIL-CLOSED: determinismo [2 builds idênticos] + sem-drift [committed == rebuild] + seções obrigatórias + gate anti-JARVIS) — mesmo molde gerado+committed+canário do par `build_capabilities`/`test_capabilities`. Cada coach carrega o núcleo do método (classificar confiança · file-first-por-pergunta · anti-raso sênior · ressalva anti-JARVIS) + elicitação em lotes + template de saída do artefato + handoff para o IDE.

## Alternativas consideradas

1. **6 markdowns escritos à mão.** É prosa — drift garantido, sem determinismo, sem gate. **Rejeitada** (exatamente o que o dono vetou).
2. **Importar os web-bundles do BMAD as-is.** Convenção/tooling estrangeiros (resolve_config, customize.toml); não plugam no web-export/anti-JARVIS do metacognition. **Rejeitada.**
3. **coaches.json + builder + canário, reusando web_export (ESCOLHIDA).** Dado → derivado → gateado. Atualizar coach = editar dado + regenerar; o canário barra drift. Ferramental e determinístico por construção.

## Consequências

**Positivas:** planejamento cross-IA com artefatos prontos sem inflar o IDE; geração determinística (canário prova 2 builds idênticos); drift impossível (fail-closed committed==rebuild); herda o gate anti-JARVIS (nenhum coach finge mecanismo que o chat não executa); product-brief-coach reusa o Spec Kernel (ADR-081). **Negativas/limite (declarado):** o conteúdo dos coaches é heurística de elicitação (qualidade auditável, não prova de completude — herda a ressalva dos métodos sênior); a versão é carimbada do README (`main_version`) — bump de release deve regenerar (o canário pega o drift); os `.md` são gerados — editar à mão quebra o canário (intencional).

## Implementação (ponteiro)

- `web-bundles/coaches.json` (fonte) · `tools/build_web_bundles.py` (builder; `--check` = modo drift) · `web-bundles/<id>.md` (6 gerados) · `web-bundles/README.md` (deploy Gem/GPT/Projeto).
- `tools/test_web_bundles.py` (canário fail-closed) · `capabilities.json`: `web-bundles-coaches` (+1; enforcement=fail-closed via canário).
- Reuso: `web_export.load_map`/`phrase`/`main_version`/`anti_jarvis_gate` (sem duplicar — régua §0).
