# ADR-073 — Enforcement declarado por capacidade: prosa-only vira débito de mecanização VISÍVEL e gated

- Status: **Aceito** (2026-06-06 — implementado + canário verde no mesmo bloco; modo autosuficiente autorizado pelo dono)
- Data: 2026-06-06
- Decisores: dono + squad
- Onda: cerne / prosa→mecanismo
- Relacionado: ADR-072 (índice de capacidades), ADR-030 (consistency-gate), ADR-020 (linter agnosticismo), Princípio 12 do AGENT-FRAMEWORK.md §6 (prosa→mecanismo)

---

## Contexto

**Cerne declarado pelo dono (reforçado várias vezes em 2026-06-06):** *todo processo, gate, regra ou
política deve ser FORÇADO por script/mecanismo determinístico — nunca depender de prosa.* É um padrão
**recorrente**: "toda hora encontramos algo que é só prosa". Prosa não força nada — um agente esquece,
racionaliza ou pula. Gate fail-soft/advisory/doutrina é **prosa disfarçada de mecanismo**.

O Princípio 12 (prosa→mecanismo) já existia, mas **ele mesmo era prosa**: nada tornava VISÍVEL nem
GATED quando uma capacidade era só prosa/advisory. O gap ficava invisível até alguém tropeçar nele
(ex.: nesta sessão, o `consistency-gate` fail-soft "existe mas não dispara"; o `route-gate` advisory
vetado por EDR; o qa-critic rodado por escolha, não por gate).

## Decisão (1 frase ativa)

**Cada capacidade no registry (ADR-072) declara um campo `enforcement` ∈ {`fail-closed`, `physical`,
`ci-ready`, `fail-soft`, `advisory`, `manual`, `prose`, `n/a`}; o canário `test_capabilities.py`
(a) EXIGE `enforcement` em toda capacidade `cross_ai` (prosa-only não pode ser invisível), (b) valida
o enum, e (c) LISTA como "débito de mecanização" toda capacidade abaixo de `fail-closed`/`physical` —
tornando o gap prosa-vs-mecanismo AUDITÁVEL a cada run, nunca silencioso.**

## Alternativas consideradas

1. **Manter o Princípio 12 só em prosa.** Rejeitada — é o próprio problema (prosa sobre evitar prosa).
2. **Reprovar (fail) toda capacidade não-fail-closed.** Rejeitada AGORA — `advisory` é legítimo onde o
   EDR (Kaspersky) veta hooks (ADR-047/060): forçar fail-closed seria desonesto. O honesto é
   **visibilizar o débito** e exigir declaração, não fingir que tudo é fail-closed.
3. **Campo `enforcement` declarado + canário que exige (cross_ai) + lista débito (ESCOLHIDA).** Default
   = mecanismo; exceção (prosa/advisory) = débito explícito com taxonomia, visível a cada CI.

## Consequências

**Positivas:**
- O cerne "prosa→mecanismo" deixa de ser slogan e vira **dado auditável** por run (lista de débito).
- Capacidade `cross_ai` **não pode** entrar sem declarar como é forçada → o gemini-mãe recebe a mesma
  taxonomia (converge via manifest de equivalência, ADR-071/072).
- Direciona trabalho: a fila "prosa→mecanismo" é a lista de `enforcement` fraco, priorizável.

**Negativas / limites (honestidade):**
- O canário **não** mede a *qualidade* do enforcement — confia no valor declarado. Declarar `fail-closed`
  mentindo ainda exige o canário/CI real existir (cruzado com `status=PROVIDES` que exige canário).
- `enforcement` ainda não preenchido em todas as 42 capacidades (só `cross_ai` é obrigatório hoje);
  cobertura do núcleo cresce incrementalmente (régua §0 — não inflar de uma vez).

## Pendências (próximas conversões prosa→mecanismo — backlog priorizado pelo débito)

- **process-evidence gate (candidato a ADR):** `consistency-gate` (hoje `fail-soft`, ADR-030) → ratchet
  para **fail-closed na CI** no subconjunto "PR de bloco exige veredito de qa-critic + checkpoint no
  history.md". Mecaniza "TODO QA é adversarial" e "forward-only após PASS" (ADR-011), que hoje são
  doutrina. Não-preemptivo só na forma; o dono já declarou o princípio — falta a conversão.
- `route-gate`/`mission-gate` advisory onde EDR veta hook → a camada de CI (fail-closed) é o caminho
  robusto independente de hook.

## Implementação (ponteiro)

`capabilities.json` (campo `enforcement` por capacidade); `tools/test_capabilities.py` (check #9 +
bloco "[debito-mecanizacao]"); `tools/build_capabilities.py` (`--show` exibe enforcement). **DONE
quando:** canário exige enforcement em cross_ai, valida enum, e imprime a lista de débito. Verde no
bloco 2026-06-06.
