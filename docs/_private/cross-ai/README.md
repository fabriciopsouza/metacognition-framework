# Cross-AI — lar dos comentários/handoffs/relatórios entre IAs (peer-private)

> **Peer-private:** esta pasta é **rastreada** (vai ao GitHub master, de onde a IA-par lê) mas é
> **stripada do premium público** (`export-clean.py` remove `docs/_private/`). Não é o `output/`
> (gitignored, efêmero) e **nunca** é o repo da outra IA. Encarna o ADR-069 (isolamento por IA) +
> ADR-070 (repo-identity-gate).

## Ecossistema (1 fonte → 2 distribuições; simétrico por IA)

```
metacognition-framework (MASTER, Claude)        metacognition-gemini (MASTER, Gemini)
      |  fonte única (ADR-049)                         |  mesmo ecossistema
      +--> public web (anônimo)                        +--> public web
      +--> premium (deriva do master, SEM vida própria)+--> premium
                         \                             /
                          \----- HUB PRIVADO ---------/
                           (troca cross-IA via PR; cada IA escreve só
                            no próprio branch/pseudônimo — ninguém escreve
                            no repo da outra; ADR-069)
```

- **Premium deriva do master** — nunca recebe conteúdo manual; é espelho via `export-clean.py`/`web_export.py`.
- **Gemini é simétrico** — tem master próprio que alimenta o web+premium dele. Tudo aqui vale para os dois lados.

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

## Aprendizado mútuo + crítica — SEM loop infinito (regra de terminação)

Ambas as IAs **aprendem dos relatórios de execução opt-in** (corpus ADR-062/063/068) e **criticam uma
à outra** (hub). Para a crítica mútua **terminar** (não virar ping-pong eterno):

1. **DAG anti-reanálise:** toda mensagem lista `analyzed_reports[]` (ids que responde). Nunca reanalisar
   um `report_id` já em `.cross-ai-seen.json` (idempotência por sessão). Dedup ≠ terminação — ver abaixo.
2. **Regra do "novo argumento" (espelha o anti-loop §0):** uma crítica sobre uma `claim` só gera nova
   mensagem se traz **argumento NOVO**. Repetir a mesma objeção 2× sem novo argumento → **não responder**;
   selar ou escalar. (É o "se eu perguntar 'posso prosseguir?' 2× → pare e reformule" aplicado a cross-IA.)
3. **Convergência por verdito:** cada `claim` recebe `ACEITO | REJEITADO | DEFERIDO | AVANCA_COM_RESSALVA`.
   Thread **sela** (`status: sealed`) quando todas as claims estão ACEITO/REJEITADO **ou** em DEFERIDO
   estável (concordar em discordar, registrado).
4. **Teto de rodadas:** **máx. 3 rodadas** por thread. Na 3ª sem convergência → **escala ao dono** (HITL
   decide) e **sela**. Circuit-breaker forward-only (espelha a arquitetura bicelular J0-J5, ADR-011).
5. **Postura preservada:** "nunca aceitar na 1ª passagem" (ADR-011) é sobre **rigor**, não sobre eternizar
   — o teto + novo-argumento garantem que rigor não vira loop.

## Frontmatter do hub (agnóstico de IA — ver ADR-069 §Layout)
`schema_version, report_id (=sha256[:8] do corpo, stampado no merge), thread_id, from, to[], date,
status(open|sealed), kind`. Opcionais: `analyzed_reports[]`, `verdict_per_claim{}`, `tags[]`,
`round` (1..3), `supersedes/superseded_by`, `machine_id` (**só peer-private/hub, nunca no público**).
