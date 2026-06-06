# Cross-AI — lar dos comentários/handoffs/relatórios entre IAs (peer-private)

> **Peer-private:** esta pasta é **rastreada** (vai ao GitHub master, de onde a IA-par lê) mas é
> **stripada do premium público** (`export-clean.py` remove `docs/_private/`). Não é o `output/`
> (gitignored, efêmero) e **nunca** é o repo da outra IA. Encarna o ADR-069 (isolamento por IA) +
> ADR-070 (repo-identity-gate).

## Ecossistema (1 fonte → 2 distribuições; simétrico por IA)

```
  metacognition-framework (MÃE, Claude)            metacognition-gemini (MÃE, Gemini)
   ▲ relatório de aprendizado (opt-in)   │  cross-IA   │   ▲ relatório de aprendizado (opt-in)
   │ (única coisa que a sombra devolve)  │ (só MÃE↔MÃE)│   │
   +-- public web ─┐                     ▼             ▼   ┌─ public web --+
   +-- premium ────┴── SOMBRAS           HUB PRIVADO       SOMBRAS ──┴── premium
       (derivam da mãe, SEM vida própria; NÃO fazem dev nem cross-IA)
```

- **Sombras (public/premium/web) só DEVOLVEM relatórios de aprendizado** (opt-in, ADR-062/063). Não
  desenvolvem, não fazem cross-IA, não escrevem código. Recebem a melhoria por **export da mãe** (ADR-049).
- **Cross-IA ocorre SÓ entre os repos-mãe** (Claude-mãe ↔ Gemini-mãe), nunca via sombra.
- **Spread da melhoria (sem onerar o usuário):** o que a Claude-mãe melhora **propaga à Gemini-mãe via
  hub cross-IA** — a Claude **não escreve** no repo do Gemini; **publica o handoff**, e a Gemini-mãe lê,
  **critica adversarialmente e implementa** no próprio repo. Simétrico. A entrega (hub + scan) é mecanizada
  → o usuário não carrega passo manual, e a melhoria chega aos dois lados.

## Papéis dos documentos (cada um com sua finalidade)

| Doc | Finalidade | `kind` no hub |
|---|---|---|
| **handoff** | passar estado p/ a outra IA/sessão retomar sem perguntar | `handoff` |
| **comentário cross-IA** | crítica/decisão **dirigida** à outra IA p/ avaliação adversarial | `comment` / `decision` / `reply` |
| **execution-report** (opt-in) | telemetria de processo + lições; **ambas as IAs aprendem deste corpus** | `execution-report` / `lesson` |
| **incident-report** | o que falhou + causa-raiz + ações | `incident` |
| **ADR** (fica em `docs/adr/`, não aqui) | decisão de arquitetura interna; a IA-par lê e avalia | — |

## Fluxo (outbox → hub → a outra IA)

1. Eu **redijo aqui** (`outbox/`) a mensagem no schema do hub (frontmatter abaixo) — cópia **canônica
   peer-private**, rastreada e auditável no meu master.
2. **Entrego ao hub** via PR (branch/pseudônimo meu = ownership; ADR-063). O hub é o meio de entrega
   cross-máquina/cross-usuário.
3. A outra IA **varre o hub no início** (`cross-ai-inbox-scan`, ADR-069), lê, **avalia criticamente,
   implementa ou não**, e responde via PR **no próprio branch**. Eu nunca escrevo no repo dela.

## Aprendizado mútuo + crítica — SEM loop infinito (TRAVA FÍSICA, não prosa)

Ambas as mães **aprendem dos relatórios de execução opt-in** (corpus ADR-062/063/068) e **criticam uma
à outra** (hub). A terminação NÃO é confiada à boa-vontade da IA — é **mecanizada** em
[`tools/cross_ai_gate.py`](../../../tools/cross_ai_gate.py) (testes: `test_cross_ai_gate.py`, 8 casos que
provam que o gate MORDE), rodado pela **CI do hub** no merge de cada PR. Determinístico, opera só sobre o
frontmatter (não julga texto livre). Invariantes que ele FORÇA (exit≠0 = PR barrado):

1. **Agrupa por `topic_fingerprint`, não por mensagem.** Dedup por `report_id` só evita reprocessar a MESMA
   mensagem — novo report sobre o mesmo tópico passa; por isso dedup-de-mensagem **falha sozinho**.
2. **Monotonicidade / ponto-fixo (quebra-loop):** rodada `>1` só passa se **resolve claim aberta**,
   **introduz claim nova**, ou traz **`evidence_sha256` inédito**. Restating (mesmas claims/vereditos/
   evidência) → **REJEITADO**. É o "novo argumento" tornado **checável por máquina**.
3. **Convergência→selar:** sem claim aberta (todas `ACEITO`/`REJEITADO`) o tópico **deve** estar `sealed`.
4. **Teto POR TÓPICO (não por thread):** `round > 3` exige `escalation: pending|resolved` (gate humano).
   Criar novo `thread_id` não escapa — o teto é do `topic_fingerprint`.
5. **Finalidade:** tópico `sealed` só reabre com **chave humana** (`reopen_token`) **ou** **evidência externa
   inédita** (`reopen_evidence_sha256`). **Persuasão de IA sozinha NÃO reabre** — fecha o furo "uma IA
   convence a outra e recomeça o ciclo".

**Selar SEM cross-write (ADR-069):** `status: sealed` é declarado pelo **próprio autor**; o **arquivamento**
(`inbox/`→`archive/`) é ação da **CI do hub** (automação neutra), nunca da IA receptora. Ninguém escreve no
arquivo da outra; o gate só **lê** `status`.

## Frontmatter do hub (agnóstico de IA — validado por `cross_ai_gate.py`)
**Requeridos:** `schema_version, report_id (=sha256[:8] do corpo), topic_fingerprint, thread_id, from,
to[], date, status(open|sealed), kind, round`.
**Para terminação:** `verdict_per_claim{claim_id: ACEITO|REJEITADO|DEFERIDO|OPEN}`,
`claims[]{claim_id, evidence_sha256}`, `escalation(none|pending|resolved)`.
**Para finalidade:** `reopen_token` (só humano), `reopen_evidence_sha256`.
**Opcionais:** `analyzed_reports[]`, `tags[]`, `supersedes/superseded_by`, `machine_id`
(**só peer-private/hub, nunca no público**).
