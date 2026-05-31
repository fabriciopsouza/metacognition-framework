# ADR 030 — consistency-gate: auditoria de consistência de fechamento (6 dimensões, fail-soft)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: entrada determinística (v1.22.0) · Tipo: novo (1 script de auditoria) — net-gain por **destravar verificação inalcançável** (régua §0 cláusula c): divergências hoje só são pegas por inspeção manual.
- Relaciona: ADR-016 (digest/checkpoint), ADR-019 (sync de repo — unpushed é o espelho do "atrás de origin"), `start-session` §2.5 (retrospective gate), `docops` (fechamento de bloco), decisão travada #5 (resiliência de acesso → dimensão unpushed).

## Contexto

Ao fechar um bloco/release, divergências silenciosas se acumulam e só apareciam por inspeção manual
(ou nunca): versão do README ≠ CHANGELOG; ADR ainda "Proposto" depois do feature mergeado; sem
checkpoint no `history.md`; artefato **transiente** (`docs/_intake/`) esquecido no repo; e — crítico para
"estou divulgando" — **commits não-pushados** (decisão #5: o recovery real é a **conta GitHub**, então
trabalho que não subiu **não está protegido**). Faltava um **espelho mecânico** dessas dimensões.

## Decisão (1 frase ativa)

Criar `tools/hooks/consistency-gate.ps1`: auditoria **fail-soft** que lê o estado do repo e reporta **6
dimensões** — version-sync (README badge × CHANGELOG × tag) · adr-status (Proposto pendente) · checkpoint
(`history.md` cita a versão corrente?) · contagens (duplicata de número de ADR; lacuna é normal, não
flagada) · **unpushed** (commits à frente do upstream) · transients (`docs/_intake/` a remover) — com
**exit code = nº de inconsistências** (0 = limpo) e modo `-Json`, **invocada no fechamento de release
(docops — wirado neste ADR)** [CONFIRMADO]; integração com `/checkpoint` e o retrospective gate é
**planejada** [INFERIDO não-bloqueante]. NÃO auto-wirada no SessionStart (régua §0: não somar custo a toda abertura).

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** Divergências silenciosas; depende de o humano lembrar. **Rejeitada — é o gap.**
2. **Auto-wirar no SessionStart (hook).** Prós: roda sempre. Contras: já há 6 hooks no SessionStart; auditoria com `git rev-list` + varredura de ADRs a CADA abertura soma latência e ruído para um sinal que só importa no fechamento. **Rejeitada** — invocação sob demanda (checkpoint/fechamento) é o ponto certo.
3. **Bloquear (deny) em inconsistência.** Contras: um gate de fechamento que trava o fluxo viola fail-open/anti-loop; a decisão de fechar é humana. **Rejeitada** — reporta + exit code, não bloqueia.
4. **Auditoria fail-soft sob demanda com exit-code (ESCOLHIDA).** Prós: espelho honesto, programável (exit code), zero custo no boot, agnóstico no método. Contras: precisa ser lembrada/invocada (mitigado: amarrada ao /checkpoint e ao retrospective gate).

## Consequências

**Positivas:** fechamento de release ganha um checklist mecânico; "commits não-pushados" deixa de ser
ponto cego (alinha resiliência de acesso, decisão #5); ADRs `Proposto` órfãos e transientes esquecidos
ficam visíveis. **Validado por dogfood** nesta própria branch (pegou 3 ADRs Proposto, checkpoint ausente,
6 transientes) [CONFIRMADO — execução registrada]. **Negativas:** caminhos (README/CHANGELOG/history/adr) são convenção DESTE repo — outro
projeto adapta os ponteiros (método é agnóstico, config não). **Riscos/aprendizado:** o script usa
não-ASCII (acentos, `—`) e PS 5.1 lê fonte sem-BOM em ANSI → **gravado com UTF-8 BOM** (decode correto +
saída limpa); leituras de arquivo usam `-Encoding UTF8` (senão `Versão`→`VersÃ£o` e o regex falha). [aprendizado registrado no ADR para os próximos hooks]

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.22.0-entrada-deterministica` · `2026-05-31` · grep `consistency-gate`
- Artefatos: `tools/hooks/consistency-gate.ps1` (UTF-8 BOM; `-RepoDir`, `-Json`; exit = nº de issues).
  Canário = a própria execução contra o repo (gate repo-aware). Invocação wirada: `.agent/skills/docops/SKILL.md` §Encerramento. Planejado (não wirado): `/checkpoint`, retrospective gate (start-session §2.5).
