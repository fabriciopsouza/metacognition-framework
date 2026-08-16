# ADR-097 — Conformance de TOPOLOGIA HARD: event log do ledger + canário fail-closed (process mining; aciona o squad_gate reservado)

- Status: **Proposto** (2026-06-23 — pedido do dono: "onde sou advisory dá pra ficar hard? tenho CERTEZA de ter pedido isso inúmeras vezes") · Decisores: dono + squad (architect) · pré-gate de código: qa-critic heterogêneo isolado (pendente)
- Tipo: **ESCALADA PREVISTA pelo ADR-094** — NÃO reabre canônico. ADR-094 reservou explicitamente o `squad_gate` "pronto-mas-dormante" como *"escalada disponível se o dono concluir que advisory+reforço não bastam"*; este ADR é o dono acionando essa escalada, **restrita a conformance de TOPOLOGIA** (ordem/presença das junções), NÃO a forçar comportamento adversarial nem hard-block de merge por mérito.
- Relaciona: ADR-094 (mandato adversarial sem block — fronteira preservada), ADR-074 (posture-gate fail-closed por release — padrão reusado), ADR-077 (ledger qa-evidence — fonte do event log), ADR-088 (BYO-CI / canário como required check — camada EDR-proof), ADR-047/060/079 (EDR veta hooks → por que o canário é a camada-mestra), ADR-007 (régua §0), ADR-011/045 (QA bicelular / junções J0–J6).

## Contexto
1. Diagnóstico file-first (benchmark `docs/research/conformance-frameworks-benchmark.md`, 2026-06-23): a conformance do framework é **desigual** — HARD real onde há hook Python/canário (compaction, effect-T3, overwrite, consistency, qa-evidence/posture); **ADVISORY/só-prosa** em `readiness-gate` (J2→J3), `high-stakes-gate` HITL, e junções **J0–J3** (PMO adversarial em prosa). O único rastro mecânico destas é o ledger `qa_evidence.py --junction`, e o CI só reprova se o process-critic auditar no fim do bloco — não em tempo real.
2. Régua de mercado (LangGraph, MS Agent Framework): conformance HARD = o runtime impõe a **topologia** (grafo de estados + checkpoint/interrupt). Nosso motor é o harness do Claude Code — copiamos o *padrão*, reimplementado via ledger+hook+canário.
3. A literatura formal (process mining; van der Aalst; PM4Py) prova que "executado × desenhado" se MEDE objetivamente (fitness/precision), não se argumenta em prosa. Nosso ledger de junções já é um event log incipiente.
4. Limite intrínseco (consistente com ADR-094): **topologia** (ordem, junção pulada, downstream sem upstream PASS) mecaniza 100%; **qualidade de raciocínio** (o PMO desafiou de verdade? a rota está certa?) NÃO se mecaniza — nenhum hook força um LLM a ser cético.

## Decisão (1 frase ativa)
Tornar **auditável-e-fail-closed a conformance de TOPOLOGIA do squad** — uma junção J_n só "abre" se a anterior deixou marca verificável no ledger — imposta em **duas camadas**: (a) **canário fail-closed** sobre o event log normalizado (camada-MESTRA; padrão ADR-074) e (b) **hook PreToolUse** best-effort (camada-rápida, fail-soft onde EDR veta); medida com **process mining** (token-replay — implementação mínima própria por default; PM4Py só se pagar a régua §0). Escopo = só topologia verificável; raciocínio permanece sob o mandato adversarial do ADR-094.

> **Limite de honestidade sobre a palavra "HARD" (qa-critic A1/A3, ADR-011):** neste harness o
> agente escreve o próprio ledger e posta o próprio status de canário (ADR-088 §Consequências (b)
> — auto-atestação). Logo, o máximo alcançável aqui é **"topologia auditável por canário
> fail-closed cujo status é auto-atestado pelo mantenedor"** — NÃO é hard de runtime externo ao
> agente (estilo LangGraph, onde o runtime — não o agente — escreve o checkpoint). É estritamente
> melhor que prosa (vira número auditável e reprodutível por terceiros que re-rodem o canário),
> mas não é constrangimento externo. Hard externo exigiria árbitro neutro (CI neutro restaurado,
> ADR-088; ou runtime escrevendo o log) — fora do escopo deste ADR, registrado como teto conhecido.

## Mecanismo
1. **Event log (estende ADR-077 — régua §0):** o ledger `qa_evidence --junction` HOJE grava `{junction, bloco, artefato, evidencia, data}` (verificado file-first em `tools/qa_evidence.py`, dict `rec` de `append_junction`). **NÃO** tem `resource=modelo` nem `status` explícito (PASS é implícito pelo fato de existir o registro). Portanto, antes do event log: **(i)** estender o schema com `resource` (modelo/agente) e `status` explícito; **(ii)** trocar `evidencia` de string livre para **ponteiro a artefato verificável** (commit hash / sha de arquivo / linha de ledger) — senão a topologia é falsificável pelo próprio agente que a registra (qa-critic A3). Só então normalizar em `(case_id=bloco, activity=J_n.status, timestamp, resource)` (XES/CSV).
2. **Modelo formal:** o fluxo J0–J6 (DENTRO=itera até PASS; ENTRE=forward-only; rewind só via process-critic com `REPROVADO_REWIND J_i`) descrito como modelo conferível (Petri net/BPMN mínimo).
3. **Canário fail-closed (camada-mestra):** `tools/test_conformance.py` — reprova o release se o trace do bloco viola a topologia: junção pulada, ação downstream sem PASS upstream no ledger, rewind não registrado. Padrão idêntico ao `test_posture_gate.py` (ADR-074). EDR-proof (roda no runner de canários, fora do harness — ADR-088).
4. **Hook PreToolUse (camada-rápida, best-effort):** nega ação de papel downstream sem PASS upstream no ledger; **fail-soft** onde EDR veta (não dá falsa sensação de HARD — por isso o canário é a lei).
5. **High-stakes HITL → HARD criptográfico (reusa o que existe):** exigir `hitl_proof` verificável (`verify_hitl_proofs.py`, `git verify-commit`/`verify-tag`) antes de ação T3 em bloco marcado high-stakes. Já existe a verificação; falta cabear como pré-condição.
6. **Métrica:** PM4Py token-replay (fitness/precision por bloco, dashboard) + alignments (diz *onde* divergiu). Limiar de fitness **calibrado empiricamente**.

## Alternativas consideradas
1. **Só hook PreToolUse (sem canário).** REJEITADA: EDR veta hooks (ADR-047/060) → "HARD" que evapora em máquina com Kaspersky = falsa segurança.
2. **Só prosa reforçada (status quo ADR-094).** REJEITADA pelo dono: "advisory parou de funcionar"; além disso não MEDE — não vira número auditável.
3. **Hard-block de merge por MÉRITO adversarial (ativar squad_gate amplo).** REJEITADA: ADR-094 — não-mecanizável e o dono confirmou "antes funcionava sem bloquear". Este ADR ativa o squad_gate **só para topologia**, não para mérito.
4. **Ledger→event log + canário fail-closed (mestra) + hook best-effort + PM4Py (ESCOLHIDA).** EDR-proof na camada que importa, mensurável, reusa infra existente (régua §0), escopo cirúrgico.

## Consequências
**Positivas:** "o fluxo foi respeitado?" deixa de ser julgamento subjetivo e vira **fitness/precision auditável**; fecha o gap *proveniência-por-turno* apontado no addendum OpenMetadata; aciona o squad_gate de forma cirúrgica (só topologia) sem tocar a fronteira do ADR-094; reusa ledger/canário/HITL-proof já existentes.
**Negativas / limite honesto:** (a) limiar de fitness exige **calibração empírica** — traces de agente são ruidosos, `case notion` ambíguo em sessões longas/compactadas; mitigação = **ratchet** com janela definida: **warn por N=5 blocos** (mede sem bloquear, coleta dados de calibração), depois `fail-closed`. (b) modelo BPMN que divirja da realidade viva → falso-bloqueio; mitigação = o modelo é versionado e o canário aponta *onde* desviou, não só reprova. (c) **dependência externa:** PM4Py NÃO é adotado por default (qa-critic M2) — começa com token-replay mínimo próprio; PM4Py entra só via ADR de dependência se a régua §0 pagar. (d) hook camada-rápida não é universal (EDR) — assumido; o canário é a camada-mestra. (e) **teto de auto-atestação (qa-critic A1/A3):** ledger e status de canário são escritos pelo próprio agente — ver bloco de honestidade na §Decisão; este ADR melhora a auditabilidade, não elimina o teto.

## Pendências (a fechar antes de Aceito)
- [decidido] PM4Py NÃO por default → token-replay mínimo próprio; PM4Py só via ADR de dependência (qa-critic M2).
- [decidido] ratchet = warn por N=5 blocos, depois fail-closed (qa-critic M2); limiar inicial de fitness a calibrar nos 5 blocos de warn.
- Estender schema do ledger (`qa_evidence.py append_junction`): `resource` + `status` explícito + `evidencia`→ponteiro verificável (qa-critic A2/A3).
- Especificar e versionar o modelo formal J0–J6 (Petri/BPMN mínimo) — pré-condição do token-replay (qa-critic B1).
- Implementar `tools/conformance.py` + `tools/test_conformance.py` e rodar verde na suíte local — sem isso há intenção de HARD, não HARD (qa-critic A1/M3).

## QA (ADR-011 — registro do round adversarial)
- **qa-critic heterogêneo isolado (sonnet, autor=opus), 2026-06-23:** veredito **REPROVAR** sobre a v1 deste ADR. 3 ALTO (A1 canário fantasma/auto-atestado · A2 ledger sem `resource`, erro file-first · A3 ledger falsificável pelo agente) + 3 MÉDIO + 2 BAIXO. M1: confirmou que NÃO há contradição formal com o ADR-094 (é a escalada prevista), mas o problema real é o "hard que não é hard" (A1/A3). **TODOS incorporados nesta v2:** §Decisão ganhou o bloco de honestidade sobre "HARD"; §Mecanismo-1 corrigido com o schema real do ledger; ratchet N=5 e PM4Py-não-default fixados; pendências de implementação/modelo/schema explicitadas. Permanece **Proposto** até as pendências de implementação fecharem + re-review do qa-critic sobre o código.

## Implementação (após Aceito — tudo aditivo)
- Ponteiro: branch `docs/research-conformance-benchmark` · 2026-06-23 · grep `conformance|event_log|fitness`
- `tools/conformance.py` (normaliza ledger→event log; roda token-replay/alignments) + `tools/test_conformance.py` (canário fail-closed, padrão ADR-074).
- Cabear `verify_hitl_proofs.py` como pré-condição T3 em bloco high-stakes.
- +1 capability `conformance-topology-gate` em `capabilities.json` + `build_capabilities.py` (canário barra órfão).
- CHANGELOG na aceitação (doc-sync fail-closed). Hash de commit: complemento opcional, nunca único (ADR-001/002).
