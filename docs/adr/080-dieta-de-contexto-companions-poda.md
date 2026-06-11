# ADR 080 — Dieta de contexto: CLAUDE.md/AGENTS.md por ponteiro, rules do qa-critic em companion, cadência de poda no J6 e rule #11 (testes nunca puláveis em silêncio)

- Status: **Aceito** (2026-06-11 — gate: qa-critic adversarial Sonnet isolado, 2 rounds J4; R1 pegou a ÚNICA regressão da dieta [palavra-chave do test_nonadmin] → fix → R2 aprovativo; `check_rules_parity` + `check_core_agnostic` PASS) · Data: 2026-06-11 · Decisores: dono (aprovação explícita "Siga até o final" sobre plano que marcava P9/P12 como SUGESTÃO) + squad
- Onda: F3+F4 do plano (`docs/_private/reports/avaliacao-processo-framework-2026-06-11.md`, P8/P9/P11/P12) · Tipo: **remoção/fusão** pela régua §0(a)+(b) — corta ~9.5KB pagos em todo turno de toda sessão, sem remover regra operacional nenhuma.
- Relaciona: ADR-003 (progressive disclosure — padrão estendido ao qa-critic), ADR-007 (régua §0 — P11 é a régua aplicada a si mesma), ADR-011/077 (rules e ledger — lar da #11), ADR-017 (telemetria `sem-disparo` — insumo da poda).

## Contexto

O `CLAUDE.md` (12.7KB) virou **acreção histórica**: ~12 seções versionadas (v1.7→v1.46) que resumem ADRs já linkadas — pago em **todo turno de toda sessão**, violando o próprio princípio 5 (ninguém recopia regra) e a régua §0. O `qa-critic/SKILL.md` (13KB) carregava as 10 rules SE/ENTÃO em toda ativação, embora elas só sejam aplicadas em J4/PC. A telemetria 17-B (`sem-disparo`) existia sem **cadência** de revisão — o framework só adicionava gates. E a cláusula "testes (se aplicável)" do J3, mesmo com o ledger P4 (ADR-077), aceitava justificativa genérica.

## Decisão (1 frase ativa)

**(P9)** Reescrever `CLAUDE.md` (12.7→5KB) e `AGENTS.md` (6.6→3.5KB) no formato **regra-operacional + ponteiro** (motivação/história vivem na ADR; seção "Operação" com 1–3 linhas por regra; regras invioláveis intactas — `check_rules_parity` PASS); **(P12)** mover as rules SE/ENTÃO do qa-critic para o companion **`rules.md`** (progressive disclosure, carregado obrigatoriamente em J4/PC — SKILL 13→9KB); **(P8)** criar a **rule #11**: código executável com ausência de testes justificada genericamente no ledger J3 ("trivial"/"N/A" sem motivo específico, ou >2 arquivos de código sem teste) → REPROVADO — com smoke do entrypoint exigido pela aplicação quando `product_type` executável; **(P11)** dar **cadência à poda**: a cada 5 releases, a decisão J6 do PMO revisa a telemetria 17-B e propõe fusão/remoção de regra `andaime` com `sem-disparo` ≥ 5–10 via ADR.

## Alternativas consideradas

1. **Status quo (CLAUDE.md acumulando 1 seção por release).** Custo de token cresce monotonicamente; em ~10 releases o arquivo dobraria. **Rejeitada.**
2. **Mover o CLAUDE.md inteiro para ponteiro único ("leia AGENT-FRAMEWORK").** Perde as regras que o agente precisa ANTES de conseguir navegar (rota, invioláveis, capabilities-first) — barato demais para ser seguro. **Rejeitada.**
3. **Dieta regra+ponteiro com seção Operação consolidada (ESCOLHIDA).** Cada regra ativa em 1–3 linhas; quem precisa do porquê segue a ADR. Mesmo padrão para o companion do qa-critic (precedente ADR-003 já validado no discovery).

## Consequências

**Positivas:** ~9.5KB a menos **por turno** (CLAUDE.md/AGENTS.md) + ~4KB por ativação do qa-critic; regra nova de release passa a custar 1–3 linhas, não 1 seção; a poda deixa de ser aspiração (cadência auditável no J6); a cláusula mais frouxa da cadeia spec-driven (testes "se aplicável") fecha com critério. **Negativas/limite (declarado):** leitores do CLAUDE.md perdem o resumo histórico inline (mitigado: CHANGELOG/ADRs são o lar disso); companion exige disciplina de carga em J4/PC (mitigado: instrução OBRIGATÓRIA no SKILL + o process-critic audita); a contagem de rules agora vive no companion (rule #1 anti-stale-count cobre).

## Implementação (ponteiro)

`CLAUDE.md` + `AGENTS.md` (dieta; `check_rules_parity` + `check_core_agnostic` PASS) · `.agent/skills/qa-critic/rules.md` (novo lar, 11 rules) + `SKILL.md` (ponteiro) · `.agent/skills/pmo/SKILL.md` §J6 (cadência de poda) · rule #11 no companion.
