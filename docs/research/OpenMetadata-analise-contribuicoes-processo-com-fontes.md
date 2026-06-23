# Análise do OpenMetadata — contribuições (ou não) ao nosso processo (com fontes)

> **Por que este doc existe:** o dono pediu avaliar se o [OpenMetadata](https://github.com/open-metadata/OpenMetadata)
> tem contribuições para o nosso processo — **"sempre de forma relevante, determinística e considerando que
> software e análise são meios para o fim agnóstico que seja"**. Esta nota fecha a avaliação para não se
> reperder e evitar reabrir a pergunta. **Conclusão antecipada: nada a importar; a arquitetura do nosso núcleo
> sai validada por convergência externa.** Classificação epistêmica aplicada por afirmação.

## Fontes (acesso 2026-06-22, via WebFetch/WebSearch)

| # | Fonte | URL | O que forneceu |
|---|---|---|---|
| F1 | OpenMetadata (repo/README) | https://github.com/open-metadata/OpenMetadata | posicionamento "Open Context Layer for Data and AI"; features core [CONFIRMADO] |
| F2 | OpenMetadata Standards | https://openmetadatastandards.org/ | 700+ JSON Schemas + RDF/OWL/SHACL/PROV-O extraídos em **repo separado** da plataforma [CONFIRMADO] |
| F3 | Metadata Standard (docs) | https://docs.open-metadata.org/v1.12.x/api-reference/main-concepts/metadata-standard | schema-first, JSON Schema Draft 07/2020-12 [CONFIRMADO] |
| F4 | Atlan — OpenMetadata explained | https://atlan.com/openmetadata-explained/ | RBAC team/role/policy/rule; metadata graph [INFERIDO/ALTA] |
| F5 | `CAPABILITIES.md` (nosso) | CAPABILITIES.md | 73 capacidades; análogos internos [CONFIRMADO] |

> **Limite declarado:** o WebFetch intermedia a leitura por um modelo pequeno — contagens exatas (700+ schemas)
> e nomes de feature ficam **MÉDIA confiança**; o que é estrutural (schema-first, standard÷implementação,
> grafo de metadados) é **ALTA**. Não instalamos nem rodamos o software — análise documental.

## 1. O que o OpenMetadata é [F1; CONFIRMADO]

Plataforma open-source que migrou de "data catalog" para **"Open Context Layer for Data and AI"**: um
**metadata graph schema-first** sobre data assets. Implementação pesada (servidor + MySQL/Postgres +
Elasticsearch + conectores de ingestão). Achado revelador [F2]: **extraíram os schemas/ontologias para um
repo apartado** (`OpenMetadataStandards`) — separando o *standard* da *implementação*.

## 2. Mapa conceito → nosso processo [F1/F5; comparação INFERIDO/ALTA]

A maquinaria é a mesma; muda o **objeto governado**: o OpenMetadata governa **data assets**, nós governamos
**artefatos de processo** (ADRs, capabilities, canários, skills).

| Conceito OpenMetadata | Já temos? | Análogo nosso (verificado em F5) |
|---|---|---|
| Schema-first / standard declarativo | ✅ | `capabilities.json` + `behaviors/manifest.json` + `test_capabilities.py` (anti-drift) |
| Standard ÷ implementação (repos separados) | ✅ (princípio) | núcleo agnóstico `_shared/` ÷ aplicações fora do núcleo (`_template`) |
| Lineage / impact analysis | 🟡 | `adr-changelog-sync`, `capability-index` (feature→{exec,canário,ADR,doc}), `rules-parity-guard` |
| Glossary / business terms | ✅ | `.agent/rules/00-glossario.md` por projeto |
| Classification / domains / data products | ✅ | `product_type`/`mission`, discovery, `risk-gate` |
| Data quality: tests/freshness/volume/incidents/RCA | ✅ | canários fail-closed, qa-critic adversarial, edge-case-hunter, `qa_evidence` ledger, method-audit |
| Governance: review/certification/lifecycle | ✅ | junções J0–J6, high-stakes-gate/HITL, ADR Proposto→Aceito |
| Data contracts (ODCS) / provenance (PROV-O) | 🟡 | `input-contract-gate`, contrato mínimo (`validate_skills`); decisão→fonte→versão (traceability) |
| "Memories attached to assets" | 🟡 | `history.md` (global) + ADRs + memória persistente |

## 3. Veredito sob a régua §0 GANHO LÍQUIDO (ADR-007) + anti-reinvenção (ADR-072)

**Importar features = reinvenção, barrada.** Já temos análogo determinístico para ~todos os conceitos.
Triagem do que sobra:

1. **Validação da nossa arquitetura (ganho = evidência, não código) [CONFIRMADO].** A separação
   *standard ÷ implementação* deles (F2) é o steelman externo da nossa tese "núcleo agnóstico ÷ aplicações".
   Dois projetos independentes (catálogo de dados × framework de agentes) convergiram no **mesmo padrão**
   → sinal de que o padrão é agnóstico ao domínio. **Não adiciona nada ao repo.**

2. **Candidato 🟡 — "impact query" determinística [INFERIDO/MÉDIA].** O *impact analysis* deles ("dado este
   change, o que quebra downstream?") é a única peça que temos **espalhada** (3 canários) e não unificada.
   Honestidade §0: **`run_canaries.py` já É o detector de impacto** — qualquer quebra acende vermelho. Só
   vira ganho líquido se houver dor recorrente real de "não sei o que um change afeta antes de rodar tudo".
   Sem essa dor → **rejeitar como redundante**.

3. **PROV-O formal / ODCS / "memories por asset" → §0-marginal / over-engineering** para repo de dono único.
   **Não trazer.**

## 4. Conclusão

**Nada a importar.** O OpenMetadata é majoritariamente um espelho — aplicado a data assets — da maquinaria que
já temos para artefatos de processo. A única "contribuição" real é **metacognitiva**: prova de convergência
que **valida** a decisão de manter o núcleo agnóstico (standard declarativo + gates anti-drift fail-closed).
Reabrir só se aparecer dor concreta de impact-tracking que a suíte de canários não cubra (então: ADR + §0 + qa-critic).

## Addendum 2026-06-22 — gap NOVO surgido em conversa, com extratos (não fecha a §4; refina a #2/#3)

> A §4 olhou pela lente *features de dados* e concluiu "nada a importar". Esta conversa (sessão `ee8a9a49`)
> surfou um gap **diferente**, sob a lente *credibilidade do processo*, e **com evidência empírica** — por isso
> reabro pontualmente. **Não contradiz a §4** (continua: não importar feature do OM); refina a triagem #2/#3,
> que havia descartado PROV-O/"memories por asset" como over-engineering sem examinar a granularidade *por-turno*.

**Provocação do dono:** "vocês fazem muita coisa na mão e por provocação humana; quero no automático — e eu nem
vejo se você elicita/pesquisa/critica; me prove o contrário com extratos a cada interação."

**Extratos (desta sessão, file-first):** em 4 interações, o único recibo persistido foi `.claude/boot-proof.json`
(22:41, e **manual** após o nag do liveness). `elicitation-gate` / `context-brief-gate` / `qa_evidence` **não
dispararam nenhuma vez** — nenhuma ficha de insumo, nenhum brief, nenhum ledger novo (último `_meta/qa/junctions/`
= `adr-085...jsonl` de sessão **anterior**). Hooks **estão** cabeados (`settings.json`: 5 eventos) e os de
`UserPromptSubmit` disparam (são os banners). **Correção de atribuição:** o "EDR/Kaspersky" foi *hint-de-banner
virando causa* (anti-padrão já catalogado) — é 1 máquina pouco usada e o fallback existe; **a causa real é
arquitetural.**

**Diagnóstico [CONFIRMADO pelos extratos]:** os gates de elicit/pesquisa/crítica são de **MARCO**
(release / junção J0–J6 / pré-implementação-de-risco), **não de TURNO**. Entre dois marcos (dias), todo o
raciocínio acontece **sem gatilho e sem recibo** — exatamente o "tudo na mão" percebido. **Falta a camada de
proveniência por-turno** — o equivalente ao *evento* do OpenMetadata (proveniência por-evento) vs. nossa
proveniência por-marco. Não é bug; é uma camada ausente.

**Candidato [§0 — único net-positivo]:** emissor por-turno (`PostToolUse`/fim-de-turno) que **declara ao vivo +
grava recibo** do elicit/pesquisa/crítica do turno, **reusando `qa_evidence.py` como sink** (granularidade do
turno) **com fallback inline** onde o hook não roda. **NÃO reinventar** `qa_evidence`/`junction-ledger` — estender.
Pré-gate obrigatório: architect (ADR) + qa-critic heterogêneo. Backlog registrado em `history.md → ## Em aberto`.
