# ADR 063 — Repo central de relatórios via PR (contribuidor limitado), pseudônimo, auto-merge com CI que RE-VALIDA

- Status: **Aceito** (2026-06-05 — LIVE-verificado: 2 relatórios no corpus via PR→CI green→merge) · Data: 2026-06-04 · Decisores: dono + squad (architect)
- Onda: telemetria/aprendizado (alvo v1.43.0) · Tipo: **EMENDA da §Decisão do corpus público do ADR-062** (muda o mecanismo de publicação → novo ADR por rastreabilidade). Atende: "receber os relatórios anonimizados de TODOS num repo nosso; quem sincroniza vira contribuidor limitado; armazenados ordenados por usuário/timestamp/execução".
- Relaciona/herda: **ADR-062** (corpus público anonimizado — BASE), **ADR-052** ("o PR é o consentimento"; whitelist de schema; anti-PII), **ADR-020** (denylist/anonimização), **ADR-044** (LIMITS honesto).

## Contexto

O ADR-062 definiu um "repo público compartilhado" para o corpus, mas não o mecanismo de contribuição. O dono quer **receber de todos** num repo central, com contribuidores **limitados** e ordenação por usuário/timestamp/execução.

**Restrição dura do GitHub (a que guia o desenho):** não há ACL por-arquivo nem "write limitado por-usuário" — um colaborador com `write` mexe em qualquer arquivo. O único "limitado" nativo é **contribuição via PR**: qualquer um abre PR (não escreve direto), o repo aceita por merge. Receber de todos **sem confiar cegamente** exige que o **repo central RE-VALIDE** cada PR (o contribuidor pode anonimizar mal).

## Decisão (1 frase ativa)

**Corpus público vira um repo central `metacognition-exec-reports` que recebe relatórios ANONIMIZADOS via PULL REQUEST (contribuidor limitado — só PR, nunca write direto; o ato de PR-ar é tornar-se contribuidor, sem pré-provisionar), organizados em `reports/<pseudônimo>/<ISO-timestamp>__<exec-id>.md`; o CI do repo central RE-VALIDA cada PR (whitelist de schema + gate `sensitive-denylist` + anti-PII — ADR-052/020) e faz AUTO-MERGE só se o CI estiver verde** (o gate é a validação, não a revisão humana). O `<pseudônimo>` é **estável e aleatório por contribuidor** (gerado 1× no opt-in, guardado em `~/.claude/exec-report-consent.json` — **não derivado de e-mail/username**, anti-rainbow; atribuição real é opt-in separado).

## Alternativas consideradas

1. **Colaboradores com `write` direto.** "Limitado" não é aplicável (mexem em tudo); confiança cega no anonimizador do contribuidor. **Rejeitada.**
2. **Repo privado por colaborador (decisão Q1 original do ADR-062).** Não dá "receber de TODOS num lugar ordenado"; mantida só para o FULL não-anonimizado (privado de cada um). **Refinada, não revogada.**
3. **Pseudônimo derivado de hash(e-mail/username).** Reversível por rainbow (quem sabe o e-mail acha o pseudônimo). **Rejeitada → pseudônimo aleatório local.**
4. **Central via PR + pseudônimo aleatório + CI-revalida + auto-merge (ESCOLHIDA).** Limited-contributor nativo, recebe de todos com segurança (CI é o gate), privacy-by-default, escala (auto-merge).

## Consequências

**Positivas:** o dono recebe de todos, ordenado por pseudônimo/timestamp/execução, **sem pré-adicionar ninguém** (PR = entrada); "receber de todos" é **seguro** porque o CI central re-valida (não confia no anonimizador do contribuidor); privacy-by-default (pseudônimo aleatório ≠ identidade; atribuição é opt-in); auto-merge escala (o gate verde é a autoridade). **Negativas/limite:** criar o repo central + ligar o auto-merge é ação `gh`/settings do dono (o framework gera o conteúdo + o PR + o workflow de CI-validador como template); **PR público é irreversível** (uma vez aberto, o conteúdo entra no histórico git mesmo se fechado) → por isso o `learnings_public` é **fail-closed ANTES** de abrir o PR, e o CI central é a 2ª barreira; o pseudônimo protege a identidade mas o **conteúdo** ainda pode vazar se anonimização+denylist falharem (limite não-exaustivo já declarado, ADR-062/LIMITS). **Limites residuais (declarados, pós-qa-critic):** (a) **squatting** de pseudônimo alheio é inviável (pseudônimo é aleatório de 12 hex — não-adivinhável); (b) **pollution** (adicionar lixo SOB um pseudônimo aleatório próprio) é spam de baixo valor — o CI é append-only (ninguém edita/deleta o de outro) + anti-PII; lixo o dono poda; (c) **anonimização↔ownership é tensão fundamental** (pseudônimo aleatório sem auth = sem prova-de-dono; é o preço do anonimato — a integridade vem do append-only, não de ACL por-dono); (d) PII por regex é não-exaustiva (ADR-062/LIMITS); (e) **EXTERNAL-push** para o repo privado-por-colaborador (ADR-062) **não está mecanizado** — gap herdado, deferido (owner infra). **SUPLANTA×EMENDA:** muda o modelo de acesso/pseudônimo → novo ADR.

## Implementação (ponteiro)

- `execution_report.py`: `--init-consent` (gera `~/.claude/exec-report-consent.json` com `consent:true` + `pseudonym` aleatório — o ato de rodar é o opt-in informado); `publish_pseudonym()` (lê o pseudônimo); `central_report_path(pseudonym, ts, exec)` → `reports/<pseudo>/<ts>__<exec>.md`. Reusa `learnings_public` (fail-closed) + `has_publish_consent`.
- **Template de CI do repo central** (`tools/templates/central-reports-ci.yml`): em PR, valida só os arquivos adicionados em `reports/**` com `validate_external_report` + denylist; verde → auto-merge; vermelho → barra.
- `docs/REPORTS-CONTRIBUTION.md`: fluxo PR + pseudônimo + auto-merge + CI-revalida.
- **Owner infra (gh):** `gh repo create metacognition-exec-reports --public`; dropar o workflow; ligar auto-merge. **DONE quando:** um PR com relatório limpo auto-mergeia; um com PII é barrado pelo CI. Status→Aceito após verificação + merge.
