# ADR-071 — Equivalência-convergência entre repos-mãe (gate por capacidade + HITL-proof)

- Status: **Aceito** (ratificado por HITL no merge — 2026-06-06)
- Data: 2026-06-06
- Decisores: dono + squad (architect)
- Baseado em: recapitulação do dono (sessão 2026-06-06); 2 rodadas de qa-critic adversarial
- Relacionado: ADR-069 (isolamento por IA + hub), ADR-011 (QA adversarial + SUPLANTA×EMENDA), ADR-041 (anti-sicofância), ADR-007 (régua §0), ADR-063 (corpus via PR)

---

## Contexto

ADR-069 fez as IAs-mãe (claude, gemini, futuras) trocarem melhorias via hub, mas **nada garante
que elas permaneçam EQUIVALENTES**. Sem reconciliador, derivam: uma adota uma melhoria, a outra
esquece, e deixam de ter a mesma funcionalidade/eficiência. O objetivo do dono é que os repos-mãe
sejam **SEMPRE funcionalmente equivalentes**; divergência sistemática só é aceitável como decisão
**humana, consciente e registrada** (ADR + HITL), não como esquecimento silencioso.

Uma v1 deste gate (comparando ADOÇÃO por `improvement_id` literal, com `hitl: true` booleano) foi
**reprovada pelo qa-critic adversarial** por dois furos de design:
1. **Equivalência literal força import de solução que não encaixa** — se a outra IA já cobre a
   capacidade por mecanismo próprio, exigir que ela adote o *id* da primeira é burocracia/pressão.
2. **`hitl: true` é teatro** — booleano auto-declarado, forjável pela própria IA; não é prova de
   ratificação humana.

## Decisão (1 frase ativa)

**Equivalência é de CAPACIDADE (resultado), não de implementação: quando ≥1 mãe PROVÊ uma capacidade,
toda outra mãe deve PROVÊ-LA por qualquer mecanismo OU declarar ausência JUSTIFICADA com ADR +
`hitl_proof` (referência a artefato que só o humano produz — commit/tag assinado pelo dono ou PR
aprovado, verificável) + motivação (ganho subjetivo/finalidade, não só régua §0); ausência
não-justificada ou IA omissa → `equivalence_gate.py` FLAGA e exige ADR+HITL.**

## Alternativas consideradas

### Alt A (ESCOLHIDA): gate por capacidade + HITL-proof, divergência→ADR+HITL
**Prós:** equivalência funcional sem forçar implementação alheia (a IA provê por qualquer `mechanism`);
HITL deixa de ser booleano forjável e vira prova verificável (commit assinado / PR aprovado — a CI
verifica autenticidade via `git verify-commit`); critério de decisão mais rico que §0 (motivação
obrigatória); IA omissa detectada (exige `known_ais`). Determinístico, checável por máquina.
**Contras:** o gate sozinho (lendo o manifest) não cripto-verifica o `hitl_proof` — exige presença;
a **autenticidade** é verificada por um passo de CI (limite honesto declarado).

### Alt B (v1, REPROVADA): adoção por `improvement_id` literal + `hitl` booleano
**Contras:** força import literal (qa-critic ALTO); HITL forjável (qa-critic ALTO). Substituída.

### Alt C: confiar que cada IA mantém paridade por boa-vontade (prosa)
**Contras:** é exatamente o que falha — deriva silenciosa. Contra "prosa→mecanismo" (ADR-021/027).

### Alt D: forçar implementação idêntica (mesmo código) nas duas mães
**Contras:** quebra a autonomia arquitetural; uma solução boa numa pode não encaixar na outra;
contra o agnosticismo. Equivalência é de capacidade, não de código.

## Mecanismo (enforcement CONDICIONAL — honesto, qa-critic)

`tools/equivalence_gate.py` (testes: `test_equivalence_gate.py`, **12 casos que mordem**). Lê o manifest
unificado do hub: `capabilities[] = {capability_id, ai, status, mechanism, adr_ref, hitl_proof, motivation}`
com `status ∈ {PROVIDES, ABSENT, JUSTIFIED_ABSENT}`. Para cada capacidade com ≥1 `PROVIDES`, toda mãe
em `known_ais` precisa `PROVIDES` ou `JUSTIFIED_ABSENT` completo; senão FLAGA (exit 2). Correções do
qa-critic v2→v2.1 já no gate:
- **Catálogo canônico** (`capability_catalog` opcional, enum FECHADO): id fora dele FLAGA — fecha o furo
  do **vocabulário divergente** (`anti-loop` vs `loop-prevention` não mascaram mais não-cobertura).
- **`hitl_proof` valida FORMATO** (`commit:<sha>|tag:<t>|pr:<n>|approved-pr:<ref>`) — mata `'fake'`/booleano.
- **Duplicata** `(capability_id, ai)` conflitante FLAGA (não sobrescreve silenciosamente).
- **Omissa total** (IA sem nenhum registro) = 1 flag, sem flood por-capacidade.

**LIMITE HONESTO (não over-claim):** o enforcement PLENO exige (a) passo de CI rodando este gate sobre o
hub + `git verify-commit` na autenticidade do `hitl_proof`, e (b) o hub provisionado — **ambos PENDENTES**.
Até lá o gate prova FORMA, não a assinatura humana. **É lógica pronta-para-cravar, não trava plena ainda.**

## Consequências

**Positivas:**
- Repos-mãe convergem para paridade funcional sem pressão de import de implementação alheia.
- HITL é prova, não booleano; divergência sistemática é decisão humana **registrada** (ADR-011).
- Critério de adoção inclui ganho subjetivo/motivação do usuário, não só §0.
- Cada IA registra só no próprio repo; o gate lê o agregado do hub (ADR-069). Agnóstico de IA.

**Negativas / Limites (honestidade):**
- Verificação criptográfica do `hitl_proof` é da **CI**, não do gate isolado (declarado).
- Depende do hub provisionado + de cada mãe publicar suas `capabilities` (sem isso, omissa→FLAGA).
- Definir o conjunto canônico de `capability_id` é trabalho contínuo (catálogo de capacidades).

## Implementação (ponteiro após aceito)
- branch `feat/adr-071-equivalence-wip` · data `2026-06-06`
- artefatos: `tools/equivalence_gate.py` (v2, por capacidade), `tools/test_equivalence_gate.py` (9 casos)
- grep: `equivalence_gate`, `capability_id`, `hitl_proof`, `JUSTIFIED_ABSENT`
- Pendência: passo de CI que rode `git verify-commit` sobre os `hitl_proof`; catálogo de `capability_id`.
