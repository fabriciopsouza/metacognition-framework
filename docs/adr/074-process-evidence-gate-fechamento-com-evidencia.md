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

## Emenda 2 (2026-06-08 — qa-evidence: mecaniza "o qa-critic rodou")

**Motivação (`[CONFIRMADO]`):** a Decisão original deixou "qa-critic rodou" como **disciplina+oferta**, não fail-closed ("invocação de subagente, sem artefato garantido"). Foi o **maior débito de processo admitido em 2026-06-07** (operei fast-mode, qa-critic 1×). **E havia false-PASS reais nos próprios canários da camada (a)** — o qa-critic adversarial (subagente isolado, 2026-06-08) provou 5: `test_release_checkpoint` casava a versão por substring no arquivo inteiro (versão citada em "Próximo passo" de planejamento dava PASS sem checkpoint real; `1.5.0` casava `11.5.0`); `test_dev_dogfood` tinha piso `glob != []` gameável por placeholder de 4 bytes e detecção master/shadow por 1 booleano. Todos corrigidos.

**Emenda:** o veredito do qa-critic vira **artefato auditável** — `tools/qa_evidence.py` persiste o JSON do subagente (read-only) em `_meta/qa/<bloco>.{json,md}`. Fail-closed no master: **`test_qa_evidence.py`** exige, p/ o release atual, ≥1 artefato com `release==versão` e `recomendacao` aprovativa (forward-only; shadow-aware). "qa-critic rodou" deixa de ser prosa.

## Emenda 3 (2026-06-08 — posture-gate: mecaniza "a postura deep-research/squad foi aplicada")

**Motivação (`[CONFIRMADO]`):** canário verde ≠ pipeline aplicado. Um bloco pode passar e ter pulado discovery/RRC/método-sênior (foi o caso). **Emenda:** o artefato qa-critic de fechamento de release carrega `postura` (discovery + rrc + metodo_senior + `fonte_canonica`), **preenchido pelo qa-critic ADVERSARIAL** (independente — anti-JARVIS, não auto-atestado pelo gerador). Fail-closed: **`test_posture_gate.py`** exige `discovery` não-vazio + `rrc==PASSA` + método-sênior; **gatilho determinístico:** `fonte_canonica=true` (norma/spec/ADR) **força** `metodo_senior='aplicado'` (mecaniza ADR-009/010 — antes era prosa "carrega quando há fonte canônica"). Doutrina única em `.agent/skills/qa-critic/posture.md` (companion; SKILL/checkpoint apontam, não duplicam). **Limite honesto:** a postura é atestada por um agente; o anti-JARVIS é a independência do crítico, não uma prova criptográfica.
