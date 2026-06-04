# ADR 059 — Gates de honestidade da vitrine (G1 drift · G2 anti-overclaim · G3 claim×LIMITS), nativos e fail-closed

- Status: **Aceito** (2026-06-04 — gate de aceite: CI verde 3 SOs + qa-critic; verificação na máquina deferida pelo dono) · Data: 2026-06-03 · Decisores: dono + squad (architect)
- Onda: honestidade mecanizada (alvo v1.42.0) · Tipo: **adição reconciliada** (estende ADR-044 LIMITS + ADR-054 web_export). Atende: análise crítica da vitrine (sessão 2026-06-03) + deep-research do dono.
- Relaciona: ADR-044 (LIMITS gerado por canário), ADR-054/056/057/058 (web_export/cascata), ADR-018 (qa adversarial), ADR-042 (`test_discovery_eval` — eval executado).

## Contexto

A análise da vitrine pública (`fabriciopsouza.github.io/...`) achou **prosa de marketing não-gateada**, contradizendo o rigor do miolo (`LIMITS.md` é gerado por canário e *não pode mentir*). Três gaps concretos:

- **G1 — fail-open silencioso:** `tools/test_marketing_claims.py:24` lista `PROMPT-CHAT-WEB-v4.3.md`; o repo tem `v4.4`. O `if not os.path.isfile(p): continue` (linha 50-51) faz a checagem anti-overclaim **deixar de rodar em silêncio** no prompt web. [CONFIRMADO — `ls` confirma ausência de v4.3.]
- **G2 — vitrine sem gate anti-overclaim:** `web_export.py` tem `anti_jarvis_gate` (anti-asserção-de-enforcement) mas **nada** barra verbo absoluto de capacidade ("não alucina", "garante", "elimina"). A headline do site afirma "agentes que não alucinam" — overclaim vs. o próprio `LIMITS.md` ("alucinação residual não eliminada").
- **G3 — claim×LIMITS não cruzado:** nenhum mecanismo prova que um claim da vitrine tem status compatível em `LIMITS.md`.

Companions sênior (ux-designer/developer) foram pedidos como melhoria; o risco é **inchaço** (régua §0). A deep-research do dono (`research-brief.md`) trouxe método + ferramentas — mas com dep externas (Vale, DeepEval, LLM-as-judge) que colidem com o offline-first.

## Decisão (1 frase ativa)

**Mecanizar os três gates de honestidade da vitrine reusando os trilhos nativos do framework (zero dependência externa) e fail-closed**: G1 = glob+versão-numérica+`pytest.fail` (nunca skip); G2 = estender `anti_jarvis_gate`→detecção de absoluto-sem-hedge no `web_export.py`; G3 = IDs `{#CLAIM-NNN}` + cruzamento com `LIMITS.md` via padrão `build_limits --check`. **LLM-as-judge para companions sênior fica registrado como caminho EMERGENTE/opt-in (ADR futuro com dependência declarada), NÃO entra no core offline agora**; a discriminação sênior, quando vier, estende `test_discovery_eval.py`.

## Alternativas consideradas

1. **Importar a stack da pesquisa as-is (Vale + Syrupy + DeepEval + LLM-as-judge no CI).** Resolve, mas adiciona ≥4 dep externas, quebra offline-first, mete LLM no caminho crítico do CI (custo/latência/"token trap"). **Rejeitada — viola régua §0 e o DNA determinístico.**
2. **Só corrigir G1 (o bug) e parar.** Estanca o fail-open, mas deixa a vitrine sem gate (G2/G3 abertos). **Rejeitada — trata sintoma, não a classe.**
3. **Gates nativos fail-closed, dep externa como opção secundária documentada (ESCOLHIDA).** Cada gap mapeia para um mecanismo que JÁ existe (`anti_jarvis_gate`, `build_limits --check`, `main_version()`, `test_discovery_eval`). Vale/DeepEval ficam citados no `plano.md` como upgrade opt-in, nunca default. Custo: lexicon PT-BR vive e precisa manutenção; léxico não pega paráfrase (gap consciente).

## Consequências

**Positivas:** a vitrine passa a ter o mesmo rigor mecanizado do miolo; o bug fail-open (G1) vira fail-closed (alinhado ao princípio anti-skip-silencioso); zero dep nova (offline-first preservado); companions sênior só entram **com prova de discriminação** (régua §0 protegida por eval, não por fé). **Negativas/limite:** léxico de overclaim pega absoluto explícito, não paráfrase ("jamais comete deslizes") — lexicon vivo + qa-critic adversarial como backstop; o gate G3 exige disciplina de `{#CLAIM-NNN}` na fonte de claims. **Cascata (memória do dono):** os gates nascem no original e replicam — público/premium/web (gate roda no `web_export`)/noadmin (gate anunciado inline, sem hook). **SUPLANTA×EMENDA:** se a decisão de "nativo > externo" mudar (ex.: adotar Vale), é **novo ADR** (muda §Decisão); ajustes de lexicon/threshold são **EMENDA** in-place.

## Implementação (ponteiro)

Plano faseado em `docs/specs/honesty-gates/plano.md` (4 fases, thresholds binários). Resumo: F1 reescreve `test_marketing_claims.py` (glob+fail-closed) — DONE quando zero `skip`/`continue` em canário; F2 `anti_overclaim_gate` no `web_export.py` — DONE quando absoluto-sem-hedge aborta o export; F3 `{#CLAIM-NNN}`+`test_claims_vs_limits.py` — DONE quando zero claim público não-CONFIRMADO; F4 (EMERGENTE, opt-in) eval de discriminação estendendo `test_discovery_eval`. **Status vira Aceito** quando F1-F3 mergeadas com canário verde no CI.
