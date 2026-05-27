# /checkpoint — Salvar estado (genérico)

Registra em history.md o estado atual (compaction + structured note-taking —
`_shared/metacognition-core`).

## Formato
```
## YYYY-MM-DD HH:MM — <título do bloco>
Aprovado e funcionando: <itens>
Nomenclaturas estabelecidas: <do glossário>
Decisões permanentes (ADRs): <ADR-NNN: decisão → razão>
Próximo passo: <tarefa + critério de aceite>
Riscos ativos: <risco + mitigação>
```

## Quando
Fim de bloco aprovado · antes de encerrar · ao mudar direção · a cada ≥20 turnos.

## Aprendizado (ex-G9 / ADR-007)
Se gatilho de fracasso disparou (anti-loop, qa-critic reprovou ≥2×, file-first violado, estouro de token, [CONFIRMADO] que se revelou falso) → anotar em `history.md` sob `## Aprendizado`. Single-writer (orquestrador), append-only com timestamp.

**Firewall:** notas de aprendizado são **inertes** — só viram comportamento via skill/regra destilada, aprovada via ADR e mergeada. Nota errada não propaga.
