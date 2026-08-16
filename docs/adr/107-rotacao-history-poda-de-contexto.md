# ADR 107 — Rotação do history.md: poda de contexto via arquivo-arquivo (últimos N quentes + Em aberto/Aprendizado inteiros)

- Status: **Aceito** · Data: 2026-06-20 · Decisores: dono ("manter últimos 10 + o não-resolvido; nada perdido em outro arquivo") + squad (architect).
- Tipo: higiene de SSoT (history.md, ADR-007) · Política: NOVO (mecaniza prosa existente). Relaciona: ADR-007 (history append-only, newest-first, boot lê o topo), ADR-016/021 (digest/compaction-gate), ADR-029 (context-budget/doc-intake), "Higiene v1.58.1" (poda do `## Em aberto`, que era prosa).

## Contexto

O `history.md` cresceu a **55 checkpoints / ~901 linhas / ~37k tokens** e passou a onerar o contexto imediato a cada boot, disparando o `context-budget` (orçamento 6k). Mas o contrato do ADR-007 já diz que o boot lê **só o checkpoint do TOPO + `## Em aberto` + `## Aprendizado`** — os checkpoints antigos são história fria, melhor servida sob demanda. File-first nos consumidores programáticos confirma: `handoff.py` lê só o topo + `## Em aberto`; `compaction_gate.py` exige ≥1 checkpoint; `check_reorchestration.py` audita o bloco recente. **Nenhum** precisa do corpo histórico inteiro carregado.

## Decisão (1 frase ativa)

Manter no `history.md` **quente** os **últimos N checkpoints cronológicos** (default **N=10**, configurável via `--keep`) + `## Em aberto` + `## Aprendizado` **inteiros**; mover os mais antigos, **na mesma ordem (mais-novo-primeiro) e sem deletar**, para `docs/history/history-archive.md`, por uma tool **determinística e idempotente** (`tools/rotate_history.py`) provada por canário — `prosa→mecanismo` da "Higiene v1.58.1".

## Por que mover (não deletar) e por que tool (não à mão) — régua §0

Passa a régua §0 por **(b) reduz tokens/latência do boot** (~37k → ~8k). **Mover ≠ apagar:** o registro permanece íntegro (arquivo + git); o invariante ADR-007 (append-only, newest-first, boot lê o topo) é **preservado** — o arquivo-arquivo também é append-only/newest-first. À mão seria poda subjetiva e propensa a perda; a tool torna a invariante **verificável** (canário prova `quente + arquivo = original`, zero perda/duplicata, `## Em aberto`/`## Aprendizado` byte-a-byte, idempotência, topo preservado).

## Mecanismo

- **`tools/rotate_history.py`** (`--keep N`, `--dry-run`, `--file`/`--archive` para teste): split em `^## YYYY-MM-DD` (sub-headers tipo `## Aprendizado (append…)` DENTRO de um checkpoint **não** quebram o bloco — trap coberta pelo canário); tail = de `## Em aberto` ao fim, intacto; prepend dos rotacionados no arquivo (mais novos acima); pointer-note sentinela no quente apontando o arquivo + contagem.
- **`tools/test_rotate_history.py`** (canário, auto-descoberto pelo `run_canaries`): as 6 invariantes acima.
- **Capability `history-rotation`** registrada em `capabilities.json` (fail-soft).

## Consequências

**Positivas:** boot ~5× mais barato em tokens; o contrato ADR-007 fica explícito e mecanizado; cadência de poda sob demanda (`python tools/rotate_history.py`), sem perda. **Negativas/limite declarado:** o `check_reorchestration.py` (linter, NÃO `test_*.py`, fora do `run_canaries`) já falhava ANTES desta mudança por casar a string "APROVADO_LIMPO" em **prosa** dentro do `## Aprendizado` — pré-existente e ortogonal; comportamento idêntico antes/depois (flag no `## Em aberto`, fora do escopo desta rotação). A rotação **não é automática** (sem hook PreCompact dedicado): é comando sob demanda — enforcement pleno por hook fica para ADR futuro se a cadência manual derivar.

## Implementação (executada nesta sessão)

Tool + canário + capability + esta ADR + 1ª rotação real (55 → 10 quentes / 45 arquivados). Repo na v1.71.0.
