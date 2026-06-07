# ADR-072 — Indice de capacidades: registry SSoT por feature, indice e manifest DERIVADOS, canario anti-drift

- Status: **Aceito** (2026-06-06 — implementado + canario verde no mesmo bloco; modo autosuficiente autorizado pelo dono)
- Data: 2026-06-06
- Decisores: dono + squad
- Onda: discoverability / meta-framework
- Relacionado: ADR-044 (LIMITS.md derivado), ADR-068 (knowledge-catalog/insights no boot), ADR-071 (equivalence_gate por capability_id), ADR-030 (consistency-gate / doc-sync), ADR-007 (regua §0 ganho liquido)

---

## Contexto

Incidente ao vivo (2026-06-06): numa sessao sobre cross-IA, o agente reportou "hub nao provisionado,
equivalence sem CI, isolamento so design" — e o **dono teve que corrigir 5 vezes** ("ja existe",
"verifique", "tratamos disso hoje"). O `cross_ai_gate` (anti-loop, 10 testes), o README do hub, o
`.mailmap`, o handoff real na outbox — **tudo existia e a exploracao nao localizou**. Causa-raiz: o
framework acumula features (24+ executaveis, 70+ ADRs, dezenas de canarios) **sem um indice vivo
feature->recurso**; o agente reexplora a cada sessao e **esquece/redesenha o que ja existe**.

Ja existem 3 indices PARCIAIS, e nenhum resolve: `LIMITS.md` (capacidades, mas vies marketing —
claim provavel, nao "onde mora"); `knowledge_catalog` (licoes de relatorios, nao mapa de recurso);
indice de ADRs (decisoes, nao codigo/teste/guia vivo). **Gap:** um mapa **feature -> {executavel,
canario, ADR, guia, status, ai_owner}**, UM registro por feature, curto, que o agente le no boot.

Risco que mata a ideia (regua §0 / doc-sync ADR-030): indice escrito a mao **DERIVA** e deixa de
ser confiavel — se o agente nao confia, volta a explorar do zero, anulando o proposito.

## Decisao (1 frase ativa)

**Criar um registry SSoT `capabilities.json` (UM registro por feature: `id, title, status, ai_owner,
mechanism, test, adr, doc, cross_ai, tags`); dele DERIVAR sem escrita a mao (a) `CAPABILITIES.md` —
indice curto lido no boot (file-first), (b) o manifest de equivalencia que alimenta o
`equivalence_gate` (paridade cross-IA claude<->gemini), via `tools/build_capabilities.py`; e travar
contra drift com `tools/test_capabilities.py` (canario fail-closed: todo ponteiro existe em disco,
todo `PROVIDES` tem canario, todo `cross_ai` esta no manifest, e o `.md` esta em sync com o registry).**

## Alternativas consideradas

1. **Indice em prosa a mao** (um `.md` mantido manualmente). **Rejeitada** — deriva silenciosamente
   (exatamente o problema doc-sync do ADR-030); indice que mente faz o agente reexplorar.
2. **Reusar so o LIMITS.md.** **Rejeitada** — vies marketing (PROVADO p/ vitrine), nao mapeia
   teste/ADR/guia por feature nem o eixo cross-IA. (O registry **subsome** parte do LIMITS — converge,
   nao soma; regua §0.)
3. **Registry em YAML.** **Rejeitada** — exigiria PyYAML (quebra o contrato zero-dep dos canarios) ou
   um parser fragil; o `parse_simple_yaml` do repo nao suporta lista-de-mapas. JSON e stdlib, a prova
   de balas, e **identico ao schema dos manifests `cross_ai_gate`/`equivalence_gate`** que o registry alimenta.
4. **Registry JSON + derivacao + canario (ESCOLHIDA).** Confiavel (canario fail-closed), curto
   (indice gerado), e unifica 3 usos num mecanismo: discoverability no boot + paridade cross-IA + anti-drift.

## Consequencias

**Positivas:**
- O agente **le `CAPABILITIES.md` no boot** e localiza mecanismo/teste/ADR sem reexplorar — fecha o
  modo de falha do incidente 2026-06-06.
- **Indice confiavel por construcao:** o canario garante que nao aponta p/ arquivo morto e que todo
  `PROVIDES` tem canario — o agente pode confiar e parar de redescobrir.
- **Convergencia cross-IA:** o mesmo registry emite o manifest de equivalencia (capability_id) — claude
  e gemini convergem no MESMO vocabulario de capacidades (alimenta o `equivalence_gate`, ADR-071).
- **Honestidade visivel:** `status` distingue `PROVIDES` (com canario) de `PARTIAL` (mecanismo sem
  canario dedicado) — ex.: `doc-intake`, `consistency-gate`, `route-gate` entram como PARTIAL, sem inflar.

**Negativas / limites (honestidade):**
- O registry e **seed inicial** (24 features); cobertura cresce incrementalmente. Nao pretende ser
  exaustivo no dia 1 — o canario so valida o que esta declarado, nao exige declarar tudo.
- `status` e declarado pelo autor; o canario verifica consistencia (ponteiros, canario p/ PROVIDES),
  nao a *qualidade* do mecanismo. Mentir status PROVIDES->PARTIAL ainda exige o canario passar.

## Implementacao (ponteiro)

`capabilities.json` (SSoT, raiz); `tools/build_capabilities.py` (`--check` anti-drift, `--manifest`);
`tools/test_capabilities.py` (canario, auto-descoberto por `run_canaries.py`); `CAPABILITIES.md`
(DERIVADO — header avisa "nao editar a mao"); leitura no boot via `.agent/workflows/start-session.md`
(passo file-first). **DONE quando:** `build` gera o indice, `--check` falha sob drift, o canario verde,
e o boot le o `CAPABILITIES.md`. Status->Aceito apos canario verde + qa-critic.
