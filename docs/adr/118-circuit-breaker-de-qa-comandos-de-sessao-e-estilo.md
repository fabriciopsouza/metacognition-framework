# ADR-118 — Circuit breaker de QA, comandos de sessão, estilo corporativo e plano que não expira

- **Status:** Aceito
- **Data:** 2026-09-26
- **Decisores:** dono (Fabricio) — plano B4 aprovado em 25/09/2026 com D1–D3; conciliação de 25/09:
  *"validade dos comandos não invalida o plano/planejado [...] TEM que ser feito, ou submetido a decisão"*.
  Autoria: Opus 5.5.
- **Relação:** emenda o ADR-028 (Emenda 1). Reusa ADR-073 (débito visível), `tools/trabalhos.py`,
  ADR-087 (orçamento de retry), ADR-116 (regra global).

## Contexto

1. Laço autor ↔ revisor sem teto: o ADR-116 levou 5 rodadas; a 3ª reprovação seguida só levou a
   redesenho por decisão do autor, não por mecanismo.
2. O `qa_evidence` já guardava o histórico de rodadas (`substitui`), mas as rodadas reprovadas não
   eram registradas: só o veredito final.
3. O dono exige estilo corporativo direto e o editor aplica estilo explicativo; o ADR-028 só colocava
   o processo acima do estilo do editor.
4. Pedido do dono: comandos de sessão (`economia de tokens`, `sem circuit breaker`, `sem limite de
   rodadas de QA`) sem que eles apaguem plano aprovado.
5. `check_field_mapping` aceitava `confirmação: pendente` como confirmado (achado ao usar o gate no
   plano B3).

## Decisão

1. **Circuit breaker no `tools/qa_evidence.py`**, lido do histórico de rodadas do bloco:
   - D1: 3 rodadas seguidas sem aprovação → a próxima gravação é recusada;
   - D2: 2 rodadas seguidas sem aprovação com os mesmos achados (severidade + local) → idem;
   - a rodada que dispara é gravada (reprovação nunca se perde); **aprovação sempre entra** e zera a
     sequência;
   - destrava com `--redesenho` (≥ 20 caracteres e ≥ 4 palavras distintas) ou `--override-dono`
     (frase literal do dono com data de calendário válida dd/mm/aaaa), gravados no artefato no momento
     do ato; ambos reiniciam a contagem; texto trivial não destrava;
   - ao armar, o `main` avisa e declara débito em `tools/trabalhos.py` (`circuit-breaker-<bloco>`).
2. **Toda rodada de QA é registrada**, inclusive reprovação — sem isso o breaker não conta.
3. **Regra global, seções 4–6** (`.claude/global/CLAUDE-global.md`): estilo corporativo direto acima do
   estilo do editor; fontes sempre em arquivo; plano aprovado não expira; comandos de sessão valem só
   na sessão e nunca apagam plano. 4 cláusulas novas no `check_rules_parity` (14 no total).
4. **Override por argumento, não por estado de sessão:** sem arquivo de estado; a ordem do dono entra
   no próprio registro da rodada (procedência registrada no ato).
5. **`check_field_mapping`:** "confirmação:" seguida de estado de espera (pendente, a confirmar,
   aguardando, não, ?, <...>) não conta como confirmação.

## Alternativas descartadas

- Arquivo `.claude/sessao-overrides.json` lido pelos gates: estado a mais, validade de sessão sem
  identificador confiável; o argumento no registro resolve com menos.
- Ledger novo de rodadas: o campo `substitui` já guarda a cadeia.
- Limite só em prosa na skill `qa-critic` ("3 reprovações → escalar"): já existia e não segurou.

## Régua §0

Funde no `qa_evidence` (histórico existente) e na regra global existente; nenhum arquivo de estado
novo. Ganho: laço de QA com teto verificável; PASS falso do mapeamento de campo eliminado.

## Prova

- `tools/test_qa_evidence.py` — circuit breaker, 14 casos (o 14º fixa o limite declarado): D1 recusa a 4ª; redesenho destrava e zera;
  D2 recusa após 2 rodadas iguais; ordem do dono destrava; aprovação zera; aprovação entra com o breaker
  armado; override sem data ou com data impossível, redesenho trivial ou de palavra repetida não
  destravam; reprovação nunca some.
- `tools/test_spec_unico.py` (i) — 5 estados de espera reprovam; confirmação real passa.
- `tools/test_rules_parity.py` — 14 cláusulas, 14 reprovadas quando apagadas.
- Fotografia dos 4 gates de especificação nas 11 especificações antigas: 0 diferenças.

## Limites

- Estilo: o output-style vem do prompt do harness; efeito da regra global verificado manualmente.
- `economia de tokens` é comportamento de resposta, sem gate.
- O breaker cobre o laço de QA registrado no `qa_evidence`; troca entre IAs já tem o
  `cross-ai-antiloop-gate`.
- "Toda rodada é gravada" é regra de **processo** (skill e subagente `qa-critic`, workflow `implement`,
  regra global), não gate: rodada não gravada não conta. O destravamento prova forma (data real;
  redesenho com 4+ palavras distintas), não autoria nem conteúdo.

## Estado do QA

| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 3 | Sonnet isolado, primeiro plano (a79731900e69330f2) | PASS-COM-RESSALVAS | bypasses da rodada 2 recusados; casos legítimos gravam; 1 MÉDIA: a frase do limite estava duplicada, idêntica, em 5 arquivos (fonte única violada); 2 declarados: tokens curtos e data antiga destravam (dentro do limite do ADR) | cada um dos 5 com 1 linha de referência a este ADR; caso de teste que fixa o limite declarado (14 casos). Edição pós-rodada: só texto e teste, sem mudança de código |
| 2 | Sonnet isolado, primeiro plano (ab67c3c3bc4cbf5b7) | PASS-COM-RESSALVAS | os 6 da rodada 1 confirmados por reprodução; 2 MÉDIA novos: data "99/99/9999" e redesenho de 20 "x" destravavam; 1 BAIXA: texto do limite otimista | data de calendário real; ≥ 4 palavras distintas; limite reescrito; 13 casos |
| 1 | Sonnet isolado, primeiro plano (aa6d78150a6035586) | FAIL | 1 CRÍTICA: o breaker recusava a própria aprovação. 3 MÉDIA: override de texto livre; débito anunciado mesmo com falha do registro; "não se aplica" × "n/a" com vereditos opostos. 2 BAIXA: regra antiga em prosa duplicada em 5 lugares; "toda rodada gravada" sem declaração de limite | aprovação sempre entra; destravar exige ≥ 20 caracteres ou data; `returncode` conferido; regex unifica n/a; prosa trocada por referência ao mecanismo; limite declarado. 11 casos no canário |
