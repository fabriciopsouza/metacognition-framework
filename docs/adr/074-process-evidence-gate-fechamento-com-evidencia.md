# ADR-074 — Process-evidence gate: fechamento de bloco com evidência (parte fail-closed + parte oferta)

- Status: **Aceito** (2026-06-07 — parte fail-closed implementada + canário verde; modo autosuficiente)
- Data: 2026-06-07
- Decisores: dono + squad
- Onda: cerne / prosa→mecanismo
- Relacionado: ADR-030 (consistency-gate fail-soft), ADR-011 (QA adversarial / forward-only), ADR-062 (execution-report opt-in), ADR-069 (handoff cross-IA), ADR-070/072 (repo_mode), ADR-073 (enforcement declarado)

---

## Contexto

Dono pediu repetidamente: o **dogfood** (gerar os relatórios — execution-report do *uso*, handoff cross-IA da *melhoria* — e fechar o bloco com qa-critic + checkpoint) tem que ser **PROCESSO, não disciplina minha**. Foi feito MANUAL toda vez. E o gap "release sem fechamento documentado" é **recorrente**: ADR-069/070/071 fecharam sem checkpoint/CHANGELOG (2ª ocorrência; antes, 7 sessões em 2026-06-02 — `consistency-gate` ADR-030 é fail-soft e não disparou).

**Honestidade (o que dá e o que NÃO dá para fail-close):**
- **Determinístico, sempre-exigível →** checkpoint do release + ADR no CHANGELOG. Pode ser **fail-closed**.
- **Não-determinístico / condicional →** qa-critic rodou (invocação de subagente, sem artefato garantido); execution-report e handoff cross-IA são **opt-in** (ADR-062) ou situacionais (só melhoria que vale propagar). Exigir opt-in seria **desonesto**. Estes ficam como **disciplina + OFERTA** no fechamento, não gate.

## Decisão (1 frase ativa)

**O fechamento de bloco tem evidência em duas camadas: (a) FAIL-CLOSED determinístico — `test_adr_changelog_sync` (toda ADR Aceito no CHANGELOG, ADR-073) + `test_release_checkpoint` (a versão mais recente do CHANGELOG tem checkpoint no `history.md`, forward-only); e (b) DISCIPLINA+OFERTA, ciente do `repo_mode` (ADR-070/072) — em DEV: oferecer execution-report (opt-in) + handoff cross-IA (se a melhoria vale propagar) + confirmar que o qa-critic rodou; em USER/shadow: só oferecer relatório opt-in. A camada (b) é prompt no `/checkpoint`, não fail-closed (opt-in não se exige).**

## Alternativas consideradas

1. **Fail-close exigir execution-report + handoff por bloco.** **Rejeitada** — são opt-in/condicionais; exigir mentiria sobre a natureza deles e geraria relatórios vazios.
2. **Exigir checkpoint para TODAS as 57 versões do CHANGELOG.** **Rejeitada** — 22 versões antigas (1.0–1.7) nunca tiveram checkpoint individual; fabricar retroativo é desonesto (régua §0). Forward-only gateia só o release atual.
3. **Duas camadas: fail-closed (determinístico) + oferta (opt-in), repo_mode-aware (ESCOLHIDA).** Honesto sobre o que é exigível.

## Consequências

**Positivas:** "release sem fechamento documentado" vira **CI vermelho** (fecha o gap recorrente). O dogfood dos relatórios deixa de depender de eu lembrar — a **oferta** é parte do `/checkpoint`. Ciente do modo: shadow não é cobrado de dev-report.
**Negativas/limites (honestidade):** a camada (b) NÃO é fail-closed (opt-in/qa-critic não têm artefato determinístico garantido) — é a fronteira honesta do mecanizável; o `consistency-gate` fail-soft (ADR-030) segue como auditoria complementar. Cobertura histórica fica como baseline aceito.

## Implementação (ponteiro)

`tools/test_release_checkpoint.py` (canário fail-closed, auto-descoberto por `run_canaries`); `tools/test_adr_changelog_sync.py` (ADR-073, já existe); a camada de oferta vai no `.agent/workflows/checkpoint.md` (prompt repo_mode-aware). **DONE quando:** release sem checkpoint → CI vermelho; `/checkpoint` oferece os relatórios por modo. Verde no bloco 2026-06-07.

## Emenda (2026-06-07 — correção por crítica do dono: dev-dogfood é DETERMINÍSTICO, não opt-in)

**Motivação (revisão de posição, `[CONFIRMADO]`):** a Decisão original colocou a geração de execution-report + handoff cross-IA como "oferta, não fail-closed (opt-in não se exige)". **O dono corrigiu:** o **opt-in é só a PUBLICAÇÃO pública** (ADR-062/063 — o dono decide publicar telemetria anonimizada no corpus). A **GERAÇÃO do dogfood dev-side num repo-MASTER** (execution-report + handoff cross-IA) é **parte do processo, determinística, não provocada nem convencida**. E **só MASTER (claude/gemini/futuros) gera cross-IA** — shadow nunca.

**Emenda à Decisão:** num repo-master (dev), fechar bloco com release **EXIGE** (fail-closed) os artefatos de dogfood: `test_dev_dogfood.py` (detecta master por `docs/_private/` presente — stripado dos shadows; num shadow PASSA, não cobra cross-IA). CI vermelho num master sem execution-report **ou** sem handoff cross-IA → o agente não pode pular o dogfood "porque o dono não pediu". O **frescor por-release** segue como disciplina do `/checkpoint` (limite honesto); o **EXISTIR** é o piso determinístico que remove o "só gera se provocado". Decisão preservada; camada (a) ganhou o `dev-dogfood-gate`. Auto-aplicado: ESTE bloco gerou os dois artefatos sob o próprio gate.
