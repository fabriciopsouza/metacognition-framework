# ADR 045 — PMO maestro: re-orquestração na fronteira de BLOCO (emenda ao ADR-011)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Tipo: **EMENDA** ao ADR-011 (QA bicelular / junções) — net-gain por **destravar verificação inalcançável** (régua §0 c): hoje nenhum gate confirma que o PMO re-orientou o fluxo após um bloco; o retrospective gate (start-session §2.5) era só prosa.
- Origem: pergunta do dono ("não seria melhor voltar ao PMO a cada gate?"). Relaciona: ADR-011 (forward-only + process-critic), ADR-018 (QA heterogêneo), `start-session` §2.5 (retrospective gate), `pmo`/`docops`.

## Contexto

O dono perguntou se, após cada gate (sempre depois do QA), o trabalho deveria voltar ao PMO, que
redirecionaria/reativaria os processos. Análise adversarial: **voltar ao PMO a CADA gate NÃO compensa** —
(a) **custo**: dobra os hops (`estágio→QA→PMO→próximo`) e o PMO re-decide a cada um; (b) **loop**: o
forward-only entre junções é o circuit-breaker do ADR-011 contra oscilação eterna — um round-trip por
gate reabre essa porta; (c) **gargalo/ponto único**; (d) **redundância**: o PMO já aplica gate
adversarial em J0–J3 e o process-critic já roda no fim do bloco. **Porém**, voltar ao PMO **a cada
BLOCO** (após o process-critic) é valioso e **quase já existe** (retrospective gate é prosa). Falta
formalizar como passo declarado + mecanizar o registro.

## Decisão (1 frase ativa)

Adicionar a junção **J6 — PMO re-orquestração de bloco**: após o process-critic emitir `APROVADO_LIMPO`,
o controle volta ao **PMO** para **UMA** decisão explícita registrada no `history.md` —
`RE-ORQUESTRAÇÃO: <prosseguir | re-priorizar X | rewind J_i | injetar escopo Y | reativar estágio Z>` —
**mantendo o intra-bloco forward-only** (circuit-breaker do ADR-011 intacto; a re-orquestração é na
fronteira de BLOCO, não por gate), com o linter `tools/check_reorchestration.py` verificando que o
**último bloco fechado** registrou a decisão (qualidade da decisão = adversarial/não-mecanizável → LIMITS.md).

## Alternativas consideradas (≥3)

1. **PMO-hub a cada gate (proposta literal do dono).** Custo + loop + gargalo + redundância com J0–J3/PC. **Rejeitada** (análise acima).
2. **Status quo (forward-only + retrospective gate em prosa).** A re-orientação de bloco depende de disciplina; nada a audita. **Rejeitada — é o gap.**
3. **Novo papel "maestro" separado do PMO.** Inflaria o squad; o PMO já é o orquestrador (role_order 0). **Rejeitada** (régua §0).
4. **J6 = decisão única do PMO na fronteira de bloco + linter de registro (ESCOLHIDA).** Prós: captura o valor (re-direção dinâmica, reativação, visibilidade única) na granularidade certa (bloco), preserva o circuit-breaker, mecaniza o registro, reusa PMO + retrospective gate (fusão, não papel novo). Contras: a qualidade da decisão não é mecanizável → declarada.

## Consequências

**Positivas:** a re-orquestração de bloco vira passo declarado (J6) + decisão auditável; o
retrospective gate (próxima sessão) lê a decisão registrada; o circuit-breaker forward-only intra-bloco
é **preservado** (sem risco de loop). **Negativas:** adiciona uma linha por bloco ao `history.md`
(barata). **Riscos/limite declarado:** o linter prova **registro da decisão**, não sua **qualidade** —
re-orquestrar bem é julgamento sênior do PMO (adversarial) → `LIMITS.md`. J6 NÃO é round-trip por gate
(seria a alternativa rejeitada).

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/adr-045-pmo-maestro` · `2026-05-31` · grep `check_reorchestration|RE-ORQUESTRA|J6`
- Artefatos: `tools/check_reorchestration.py` + `tools/test_reorchestration.py` (5 casos sintéticos),
  edição `.agent/workflows/handoff.md` (junção J6 + invariante), `.agent/skills/pmo/SKILL.md` (decisão de
  re-orquestração), `.agent/skills/docops/SKILL.md` §Encerramento (registrar + rodar o linter), dogfood no `history.md`.
- DONE quando: J6 declarado no `/handoff` + linter no CI (via canário) + decisão registrada no bloco corrente. [CONFIRMADO]
