<!-- GERADO por tools/build_capabilities.py a partir de capabilities.json — NAO editar a mao -->
# CAPABILITIES — indice de capacidades (nivel 1: id + title)

> **42 capacidades** — 37 ✅ PROVIDES · 5 🟡 PARTIAL · 🔗 = cross-IA. Fonte: [capabilities.json](capabilities.json). Canario anti-drift: [test_capabilities.py](tools/test_capabilities.py) (ADR-072).
> **Como usar (file-first, boot):** leia esta lista p/ achar o `id`; o registro completo (mecanismo · canario · ADR · doc) vem por **`python tools/build_capabilities.py --show <id>`** ou `grep -A8 '"<id>"' capabilities.json`. Nao reexplore o repo antes disto.
> **Manutencao:** feature nova -> +1 registro em `capabilities.json` + `python tools/build_capabilities.py`. Canario barra canario orfao (cobertura).

## Cross-IA (claude ↔ gemini — entra no manifest de equivalencia)

- ✅ 🔗 `cross-ai-antiloop-gate` — Trava fisica anti-loop da troca cross-IA (terminacao garantida)
- ✅ 🔗 `cross-ai-hub-tooling` — Scan/manifest/deposit do hub cross-IA (descoberta no boot + deposit validado pelo gate)
- ✅ 🔗 `equivalence-gate` — Equivalencia de capacidade entre repos-mae (PROVIDES|JUSTIFIED_ABSENT + hitl_proof)
- ✅ 🔗 `execution-report` — Relatorio de execucao (telemetria de processo + licoes), opt-in anonimizado
- ✅ 🔗 `execution-report-builder` — Builder do relatorio de execucao (dois tiers: telemetria processo + anonimizada)
- 🟡 🔗 `export-shadow-stamp` — Carimbo fisico role=shadow no export (trava contra sombra se passar por master)
- ✅ 🔗 `repo-identity-gate` — Classificador de identidade de repo (master|shadow|clone|foreign), ancestry-first

## Nucleo (local ao repo-mae)

- ✅ `agnostic-core-linter` — Linter fail-closed: nucleo nao carrega norma de dominio (agnosticismo)
- ✅ `capability-index` — Indice de capacidades derivado + canario anti-drift
- ✅ `clean-env-gate` — Teste porta-do-usuario + ambiente limpo (sem residuo de dev na entrega)
- ✅ `compaction-gate` — Bloqueia compaction sem digest persistido (history.md sem checkpoint), fail-open
- ✅ `completeness-gate` — Cobertura escopo-pedido x entrega: quantificador sem criterio em validation falha
- 🟡 `consistency-gate` — Auditoria de fechamento (version-sync, adr-status, checkpoint, unpushed), fail-soft
- ✅ `context-brief-gate` — Contexto inferido vira ancora de pesquisa mecanizada (reparo do discovery)
- ✅ `delivery-floor-gate` — Piso de entregabilidade ao humano (teste binario de entrega minima)
- ✅ `discovery-eval` — Discovery com eval executado (nao so prosa de plano)
- ✅ `doc-intake` — Parse deterministico offline (pdf/docx/xlsx/...) -> chunks + sha256, sem embeddings
- ✅ `effect-gate` — Action-safety por EFEITO: classifica acao destrutiva e pede confirmacao (T3)
- ✅ `entrypoint-tty-gate` — Entrypoint nao depende de TTY (roda em CI/headless)
- ✅ `input-contract-gate` — Contrato de entrada: spec sem contrato de input declarado falha
- ✅ `knowledge-catalog` — Retroalimentacao do corpus: catalogo + BM25 offline + insights no boot
- ✅ `limits-catalog` — Catalogo LIMITS.md de capacidades provadas (PROVADO|PARCIAL|EM-DESENV), derivado
- ✅ `make-index-tool` — Gerador de indice de documentos/ADRs (make_index)
- ✅ `marketing-honesty-gate` — Gates de honestidade da vitrine (anti-overclaim, claim provado ancorado, versao em sync)
- ✅ `mission-gate` — Declara/confirma product_type + escopo antes de J2+ (mission.md)
- ✅ `nonadmin-profile` — Perfil non-admin: gates anunciados inline quando GPO/EDR veta hooks
- ✅ `onboarding-master-gate` — Popup usar-vs-desenvolver so no MASTER-CANONICO (nao vaza p/ public/premium/gemini)
- ✅ `oracle-bias-canary` — Canario anti-vies de oraculo + estabilidade de decisao
- ✅ `overclaim-lexicon` — Lexico PT-BR de overclaim (absoluto-sem-hedge) usado pelos gates de honestidade
- ✅ `overwrite-guard` — Le o arquivo antes de sobrescrever artefato com conteudo; avisa
- ✅ `parity-cross-platform` — Paridade cross-platform dos canarios (Linux/Mac/Windows) na CI
- ✅ `premium-tier-export` — Tier premium na export-clean (mesma fonte, mantem camada premium; baseline single-source)
- 🟡 `prepush-sync-guard` — Guarda de pre-push: evita push sobre base dessincronizada
- ✅ `project-token-report` — Relatorio de tokens por projeto (custo de sessao)
- ✅ `regulatory-coverage-gate` — Cobertura de perfis regulados declarados pelo discovery (catalogo agnostico)
- ✅ `reorchestration-gate` — PMO maestro: decisao de re-orquestracao na fronteira de bloco (J6)
- ✅ `repo-sync-boot` — Sync do repo no boot (fetch + ahead/behind + pull seguro) antes de file-first
- 🟡 `route-gate` — Lembrete de rota deterministico 1x/sessao (UserPromptSubmit), fail-open
- 🟡 `skill-contract` — Valida o contrato minimo de frontmatter das skills (ADR-013)
- ✅ `spec-depth-gate` — Profundidade minima de spec (linter anti-spec-rasa)
- ✅ `sycophancy-canary` — Canario adversarial anti-sicofancia (nao concordar para agradar)
- ✅ `web-export` — Gerador deterministico das distribuicoes web (publico/premium) a partir da mae

