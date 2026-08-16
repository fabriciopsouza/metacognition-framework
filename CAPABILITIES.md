<!-- GERADO por tools/build_capabilities.py a partir de capabilities.json — NAO editar a mao -->
# CAPABILITIES — indice de capacidades (nivel 1: id + title)

> **88 capacidades** — 77 ✅ PROVIDES · 11 🟡 PARTIAL · 🔗 = cross-IA. Fonte: [capabilities.json](capabilities.json). Canario anti-drift: [test_capabilities.py](tools/test_capabilities.py) (ADR-072).
> **Como usar (file-first, boot):** leia esta lista p/ achar o `id`; o registro completo (mecanismo · canario · ADR · doc) vem por **`python tools/build_capabilities.py --show <id>`** ou `grep -A8 '"<id>"' capabilities.json`. Nao reexplore o repo antes disto.
> **Manutencao:** feature nova -> +1 registro em `capabilities.json` + `python tools/build_capabilities.py`. Canario barra canario orfao (cobertura).

## Cross-IA (claude ↔ gemini — entra no manifest de equivalencia)

- ✅ 🔗 `cross-ai-antiloop-gate` — Trava fisica anti-loop da troca cross-IA (terminacao garantida)
- ✅ 🔗 `cross-ai-hub-tooling` — Scan/manifest/deposit do hub cross-IA (descoberta no boot + deposit validado pelo gate)
- ✅ 🔗 `environment-applicability-gate` — Deteccao de ambiente no boot + aplicabilidade das premissas (APLICA/ESTALE/AUSENTE) cross-session/cross-IA
- ✅ 🔗 `equivalence-gate` — Equivalencia de capacidade entre repos-mae (PROVIDES|JUSTIFIED_ABSENT + hitl_proof)
- ✅ 🔗 `execution-report` — Relatorio de execucao (telemetria de processo + licoes), opt-in anonimizado
- ✅ 🔗 `execution-report-builder` — Builder do relatorio de execucao (dois tiers: telemetria processo + anonimizada)
- 🟡 🔗 `export-shadow-stamp` — Carimbo fisico role=shadow no export (trava contra sombra se passar por master)
- ✅ 🔗 `hitl-proof-verify` — verify_hitl_proofs: CI verifica autenticidade dos hitl_proof via git verify-commit/verify-tag (ADR-071 pendencia)
- ✅ 🔗 `repo-identity-gate` — Classificador de identidade de repo (master|shadow|clone|foreign), ancestry-first
- ✅ 🔗 `web-bundles-coaches` — Coaches cross-IA (planejamento em Gemini/ChatGPT) gerados do dado com canario de drift fail-closed
- ✅ 🔗 `web-prompt-currency` — Guard de currency do prompt chat-web: carimbo 'Alinhado ao vX.Y.Z' nao pode ficar >5 minors atras de main (anti-drift-silencioso do prompt mantido a mao)

## Nucleo (local ao repo-mae)

- ✅ `adr-changelog-sync` — Canario doc-sync: toda ADR Aceito deve estar no CHANGELOG (mecaniza falha recorrente)
- 🟡 `advanced-elicitation` — Elicitacao avancada: catalogo de 77 metodos (convergente #1-69 + divergente CIS #70-76 + tuning-loop #77) com canario de integridade fail-closed; execucao pela skill
- ✅ `agnostic-core-linter` — Linter fail-closed: nucleo nao carrega norma de dominio (agnosticismo)
- ✅ `author-tier-gate` — Gate de tier-autor da sessao: detecta modelo ativo (transcript) + alerta LOUD se autor < baseline (ADR-082)
- ✅ `autonomy-retry-policy` — Dial retry/escalate por MODO (ADR-087): HITL escala na 1a falha; autosuficiente auto-retenta subindo a escada de modelo ate budget, escala por ultimo
- ✅ `boot-self-check` — Self-check de boot consolidado (sync+agnosticismo+boot-scan+versao) com prova checavel
- ✅ `byo-ci-gate` — Gate de merge dirigido pelos canarios LOCAIS (BYO-CI) — a seguranca do GHA sem GHA: posta commit-status verde so com 0 FAIL; branch protection exige o context
- ✅ `canary-runner-bytecode-isolation` — O executor da suite nao pode ser enganado por bytecode velho
- ✅ `capability-index` — Indice de capacidades derivado + canario anti-drift
- ✅ `clean-env-gate` — Teste porta-do-usuario + ambiente limpo (sem residuo de dev na entrega)
- ✅ `compaction-gate` — Bloqueia compaction sem digest persistido (history.md sem checkpoint), fail-open
- ✅ `completeness-gate` — Cobertura escopo-pedido x entrega: quantificador sem criterio em validation falha
- ✅ `conformance-topologia` — Executado x desenhado no fluxo de juncoes: fitness auditavel em vez de julgamento
- ✅ `consistency-closing-ci` — Consistencia de fechamento FAIL-CLOSED no CI (dim do consistency-gate que o hook PS vetado nao enforcava)
- 🟡 `consistency-gate` — Espelho de consistencia no FECHAMENTO, cabeado no evento Stop (7 dimensoes)
- ✅ `context-brief-gate` — Contexto inferido vira ancora de pesquisa mecanizada (reparo do discovery)
- ✅ `context-budget-gate` — context-budget: hook PreToolUse(Read) anuncia FRACIONAR (doc-intake) em fonte grande + tool chamavel
- ✅ `context-budget-hook` — Hook PreToolUse(Read) que anuncia context-budget (mecaniza doc-intake p/ contexto maior; nao-bloqueante, fail-open)
- ✅ `core-no-vendor` — Pureza do nucleo: nenhum nome de PRODUTO/VENDOR externo no conteudo operativo (_shared/.agent/skills/roteador); proveniencia so nos ADRs. Regression-guard do 'repo nao tem produtos' (P12)
- ✅ `decisoes-que-governam` — Colisao entre o pedido e decisao ja registrada vira consulta deterministica
- ✅ `delivery-floor-gate` — Piso de entregabilidade ao humano (teste binario de entrega minima)
- ✅ `dev-dogfood-gate` — Dev-dogfood DETERMINISTA: master fechando bloco DEVE ter execution-report + handoff cross-IA (nao opt-in, shadow-aware)
- ✅ `discovery-eval` — Discovery com eval executado (nao so prosa de plano)
- ✅ `doc-intake` — Parse deterministico offline (pdf/docx/xlsx/...) -> chunks + sha256, sem embeddings
- 🟡 `edge-case-hunter` — Percurso mecanico exaustivo de paths nao tratados — output JSON verificavel
- ✅ `effect-gate` — Action-safety por EFEITO: classifica acao destrutiva e pede confirmacao (T3)
- ✅ `elicitation-gate` — Elicitation-first VINCULANTE antes de implementar sobre indicador/metrica/regra de dominio de risco alto: ficha de insumo (6 campos) nao-skippavel mesmo em autosuficiente (enforcement, nao skill nova)
- ✅ `enforcement-mutation-audit` — Prova de mutacao obrigatoria: capacidade fail-closed declara a sabotagem que deixa seu canario VERMELHO
- ✅ `entrypoint-tty-gate` — Entrypoint nao depende de TTY (roda em CI/headless)
- ✅ `external-work-provenance` — Carimbo de PROCEDENCIA em trabalho executado FORA do repo: PROCEDENCIA.md com framework/versao/commit/sessao deterministicos + status por artefato (MINUTA/PROPOSTA/MIGRADO/APROVADO)
- ✅ `handoff-generator` — Gerador deterministico do Pacote de handoff P14 do estado do repo + sugestao de modelo (papel+risco)
- ✅ `history-rotation` — Rotacao deterministica do history.md — ultimos N checkpoints quentes + Em aberto/Aprendizado inteiros; antigos -> docs/history/history-archive.md (poda de contexto, zero perda, idempotente)
- ✅ `input-contract-gate` — Contrato de entrada: spec sem contrato de input declarado falha
- ✅ `install-verification` — Instalar em qualquer PC com veredito: o que bloqueia, o que avisa, e como resolver cada um
- ✅ `junction-ledger` — Ledger de juncoes J0-J6 (rastro mecanico do gate PASS por juncao; forward-only + J3 exige validation.md ou justificativa)
- ✅ `knowledge-catalog` — Retroalimentacao do corpus: catalogo + BM25 offline + insights no boot
- ✅ `limits-catalog` — Catalogo LIMITS.md de capacidades provadas (PROVADO|PARCIAL|EM-DESENV), derivado
- ✅ `make-index-tool` — Gerador de indice de documentos/ADRs (make_index)
- ✅ `marketing-honesty-gate` — Gates de honestidade da vitrine (anti-overclaim, claim provado ancorado, versao em sync)
- ✅ `mission-gate` — Declara/confirma product_type + escopo antes de J2+ (mission.md)
- ✅ `model-policy` — Politica de modelo como dado: papel x risco -> tier com chain de fallback + escada de heterogeneidade + indisponibilidade declarada (env)
- ✅ `nonadmin-profile` — Perfil non-admin: gates anunciados inline quando GPO/EDR veta hooks
- ✅ `onboarding-master-gate` — Popup usar-vs-desenvolver so no MASTER-CANONICO (nao vaza p/ public/premium/gemini)
- ✅ `oracle-bias-canary` — Canario anti-vies de oraculo + estabilidade de decisao
- ✅ `overclaim-lexicon` — Lexico PT-BR de overclaim (absoluto-sem-hedge) usado pelos gates de honestidade
- ✅ `overwrite-guard` — Le o arquivo antes de sobrescrever artefato com conteudo; avisa
- ✅ `parity-cross-platform` — Paridade cross-platform dos canarios (Linux/Mac/Windows) na CI
- 🟡 `party-mode` — Exploracao multi-perspectiva com personas em conflito deliberado
- ✅ `path-resolves-at-destination` — Referencia a arquivo resolve no cwd do DESTINATARIO: raiz absoluta no Pacote P14 + auditoria de diretorio temporario e link markdown relativo
- ✅ `posture-gate` — posture-gate (fail-closed): release exige evidencia de postura deep-research/squad (discovery+RRC+metodo-senior) atestada pelo qa-critic adversarial (ADR-074 emenda 3)
- ✅ `premium-tier-export` — Tier premium na export-clean (mesma fonte, mantem camada premium; baseline single-source)
- 🟡 `prepush-sync-guard` — Guarda de pre-push: evita push sobre base dessincronizada
- 🟡 `project-docs-standard` — Padrao do conjunto documental de projeto (7 propriedades + conjunto graduado + 4 gates) — PROSA, sem canario proprio
- ✅ `project-onboarding` — Onboarding/wayfinding de projeto por COMPOSICAO (ADR-090): fork greenfield/brownfield no discovery + workflows generate-project-context/document-project (compoem handoff/explorer/docops) + guia user-facing POR-ONDE-COMECAR
- ✅ `project-token-report` — Relatorio de tokens por projeto (custo de sessao)
- ✅ `qa-evidence-gate` — qa-evidence (fail-closed): release exige veredito qa-critic aprovativo persistido em _meta/qa/ (ADR-074 emenda 2)
- ✅ `qa-evidence-integrity` — Canario de integridade da evidencia de QA: .json e .md do mesmo bloco nao podem contar historias opostas
- 🟡 `readiness-gate` — Gate pre-developer: valida alinhamento requirements+ADR antes de J3
- ✅ `regulatory-coverage-gate` — Cobertura de perfis regulados declarados pelo discovery (catalogo agnostico)
- ✅ `release-checkpoint-gate` — Process-evidence (fail-closed): release atual do CHANGELOG tem checkpoint no history (forward-only)
- ✅ `reorchestration-gate` — PMO maestro: decisao de re-orquestracao na fronteira de bloco (J6)
- ✅ `repo-mode-user-vs-dev` — Modo por identidade no boot: shadow=USER (aplica a dominio, nao desenvolve), master=DEV
- ✅ `repo-sync-boot` — Sync do repo no boot: dim.1 vs proprio upstream (pull seguro) + dim.2 ORTOGONAL vs branch de integracao (origin/HEAD) com marker persistente repetido por-turno (ADR-084)
- ✅ `research-evidence` — NAO SEI so vale depois de busca provada: >= K dominios distintos com prova, ou ratificacao humana
- ✅ `risk-gate` — Gating deterministico por risco (prob x impacto -> gate + tier P0-P3); recast externo (ADR-086) sob P15, forma agnostica (categorias = blueprint)
- 🟡 `route-gate` — Lembrete de rota deterministico 1x/sessao (UserPromptSubmit), fail-open
- ✅ `rules-parity-guard` — Anti-drift das 4 regras inviolaveis entre arquivos de autoridade (sem violar SSoT §6.5)
- ✅ `shadow-sync` — Hook que auto-casa o espelho publicado com origin no boot (reset --hard mecanico, so em shadow)
- ✅ `shadow-write-guard` — Write-isolation: NEGA push de shadow E push pra remote != canonical (escreve so no proprio repo; read livre)
- 🟡 `skill-contract` — Valida o contrato minimo de frontmatter das skills (ADR-013)
- ✅ `spec-depth-gate` — Profundidade minima de spec (linter anti-spec-rasa)
- ✅ `squad-enforcement-gate` — Enforcement deterministico do squad: manifesto de papeis + gate com atestacao de isolamento — ADVISORY no CI (ativacao desacoplada, ADR-104)
- ✅ `squad-gate-git-hook` — Instalador do pre-commit que faz o squad-gate rodar sozinho, com escapatoria declarada
- ✅ `sycophancy-canary` — Canario adversarial anti-sicofancia (nao concordar para agradar)
- ✅ `trabalhos-registro` — Registro persistente de trabalhos: handoff sobrevive a sessao e e oferecido ate ser tratado
- 🟡 `validation-reporting` — Metodo de validacao ponto a ponto com reporte legivel por humano que decide
- ✅ `web-export` — Gerador deterministico das distribuicoes web (publico/premium) a partir da mae

