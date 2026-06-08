# posture.md — Companion: evidência de postura deep-research/squad (ADR-074 emenda 3)

> Carregado sob demanda ao FECHAR bloco substantivo (release / ADR nova / ≥N arquivos).
> Destila a falha recorrente **"pulei a postura deep-research/squad; operei fast-mode"**
> (admitida 2026-06-07; 2ª ocorrência → companion, régua §0: é o lar ÚNICO da doutrina,
> os demais arquivos apontam para cá em vez de duplicar). O **mecanismo** que força isto é
> `tools/test_posture_gate.py` (fail-closed); este companion é a doutrina que ele enforça.

## O que é "postura" (e por que não basta o qa-critic genérico)
Postura = **prova de que o pipeline rodou**, não só de que o código passou. Um bloco pode ter
canários verdes e mesmo assim ter pulado discovery, RRC e método-sênior (foi o caso real). A
evidência vive no **artefato qa-critic aprovativo do release** (`_meta/qa/*.json`, campo `postura`),
**preenchido pelo qa-critic ADVERSARIAL** (subagente isolado) — NÃO auto-atestado pelo gerador
(anti-JARVIS: quem fez o trabalho não certifica a própria postura).

## Campos exigidos (validados por `qa_evidence.validate_postura`)
- `discovery` — path do artefato (research-brief / requirements / context-brief) **OU** `"inline: <justificativa>"` (por que discovery foi inline e o que foi elicitado).
- `rrc` — `"PASSA"` (release exige PASSA) | `"FALHA"` | `"N/A: <razão>"` (só fora de release).
- `metodo_senior` — `"aplicado: <path>"` | `"N/A: <razão>"`.
- `fonte_canonica` (bool) — **gatilho determinístico**: se há norma/spec oficial/ADR nova citada,
  `fonte_canonica=true` **força** `metodo_senior` a começar com `"aplicado"` (não pode ser N/A).
  Atestado pelo qa-critic adversarial (ADR-009/010 mecanizado: antes era prosa "carrega o
  método-sênior quando há fonte canônica"; agora é campo verificável + fail-closed).

## Como o orquestrador produz a evidência (fluxo)
1. No FINAL do bloco, rodar o **process-critic** (qa-critic em subagente isolado, modelo heterogêneo).
2. O subagente é read-only → devolve JSON com `passou/recomendacao/problemas/...` **e o bloco `postura`**.
3. Orquestrador persiste: `python tools/qa_evidence.py --from-json -` (ou `write_artifact`),
   com `release="<versão>"` no veredito de fechamento. `write_artifact` **recusa** release sem postura válida.
4. CI: `test_qa_evidence` (veredito aprovativo existe) + `test_posture_gate` (postura completa) → verde.

**Teste binário:** o release atual tem um `_meta/qa/*.json` com `release==versão`, `recomendacao`
aprovativa e `postura` completa? Não → CI vermelho. Postura deixou de ser disciplina; virou gate.
