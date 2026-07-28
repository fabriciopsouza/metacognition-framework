# ADR 096 — HITL mecanizado: corte `score ≥ 6` com exit code próprio (fecha o wire do ADR-086)

- Status: **Aceito** quanto à DECISÃO (2026-07-26 — corte escolhido pelo dono, resposta literal *">=6"* à pergunta "onde fica o corte") · Decisores: dono + squad (architect) · **pré-gate qa-critic heterogêneo: RODADO em 2026-07-28** (Fable, subagente isolado em worktree; 1ª passada REJEITOU com um CRÍTICO, 2ª passada `aprovar_com_ressalvas` — apêndice ao final)
- Tipo: **extensão que mecaniza prosa** (P15). Régua §0 (ADR-007): **não é adição** — zero arquivo novo, zero capability nova; estende `tools/risk_score.py` (capability `risk-gate` existente) e seu canário. Satisfaz a cláusula (c): destrava decisão hoje implícita ("posso passar adiante sem humano?") tornando-a mecanismo com código de saída legível por hook.
- Relaciona: **ADR-086** (fecha o item B4, que ficou em "podem consumir"), ADR-085 (recast TEA/BMAD), ADR-022 (mission/high-stakes), ADR-011/074 (QA bicelular / qa-evidence), ADR-092 (camada de enforcement), `action-safety` (T3 por efeito)

## Contexto

O ADR-086 entregou o **cálculo** (`risco = prob × impacto` → `gate` + `tier`) e o canário exaustivo. O item **B4 (wire)** ficou declarado como possibilidade: *"`qa-evidence`/`readiness-gate` **podem** consumir o `gate_agregado` como dado"*. Verificado empiricamente nesta sessão (grep por `risk_score|gate_agregado|CONCERNS` em `tools/`): **nenhum consumidor existe** — as únicas ocorrências são o próprio tool, seu canário e prosa em `_shared/high-stakes-gate/SKILL.md`.

Consequência prática: o item 4 do high-stakes-gate — *"hand-off **bloqueado** até revisão humana"* — seguia sendo **prosa**. Nada bloqueava. Um agente podia rodar o `risk_score`, ler `gate_agregado: CONCERNS`, e seguir adiante; e mesmo que quisesse respeitar, o tool sai com `exit 0` em todos os vereditos (por desenho do ADR-086: "o veredito É a saída"). Um hook não tem o que ler.

Faltava, portanto, **um corte** (a partir de qual score o humano é obrigatório) e **um mecanismo** (algo que um hook/CI consiga barrar).

## Decisão

**(1) Corte do HITL = `score ≥ 6`** — `HITL_MIN_SCORE = 6`. Alcança 2×3, 3×2 e 3×3. Escolha do dono entre três opções apresentadas (≥6 · ≥4 · regra de impacto absoluto).

**(2) HITL é eixo ORTOGONAL ao gate, não um rebatismo dele.** O `gate` (FAIL/CONCERNS/ADVISORY/NONE) classifica **severidade** e permanece **intacto** — é a taxonomia do recast TEA (ADR-086 B2). O campo novo `hitl` (bool, por item) e `hitl_requerido` (agregado worst-case) respondem outra pergunta: *"posso passar adiante sem humano?"*. Colapsar `6 → FAIL` teria destruído a faixa CONCERNS e feito o canário exaustivo mentir sobre a matriz.

**(3) Enforcement por exit code próprio:** `--gate-exit` → **exit 2** quando `hitl_requerido`. Contrato legível por hook: **0 = liberado · 1 = entrada inválida (fail-closed) · 2 = HITL requerido**. Sem a flag, comportamento do ADR-086 preservado (exit 0, veredito no stdout) — compatibilidade **aditiva**: os vereditos e as chaves antigas são idênticos, e o stdout ganha três campos novos (`hitl` por item, `hitl_requerido`, `hitl_min_score`). Não é bit-a-bit, e como não existe consumidor, nada quebra.

**(4) Precedência fail-closed > gate:** entrada inválida **com** `--gate-exit` sai **1**, não 2. Travado por canário.

**(5) Canário estendido** (`tools/test_risk_score.py`): coluna `hitl` na tabela-verdade exaustiva dos 9 combos, agregação worst-case do HITL, guarda `HITL_MIN_SCORE == 6` (o corte só muda por ADR, não por deriva), e a matriz dos 6 casos de exit code.

**(6) `_shared/high-stakes-gate/SKILL.md` v1.1.0** — item 4 passa a citar o comando e o exit code, e **declara a lacuna** (abaixo).

## Alternativas consideradas

1. **Colapsar `6 → FAIL`.** Simples, mas destrói a faixa CONCERNS e contradiz o ADR-086 B2 (a desambiguação do TEA). Perde-se a distinção "bloqueia release" vs "exige plano de mitigação". **Rejeitada.**
2. **Usar `exit 1` também para o bloqueio.** Tornaria JSON malformado indistinguível de "gate barrou" — o chamador não saberia se conserta a entrada ou busca aprovação. **Rejeitada** (é o oposto de fail-closed legível).
3. **Corte em `≥ 4`.** Mais conservador: qualquer coisa com impacto 3 praticamente sempre gateia. Mais atrito. **Rejeitada pelo dono.**
4. **Regra de impacto absoluto** (impacto = 3 gateia sempre, independente da probabilidade). **Recomendada pelo autor, rejeitada pelo dono** em favor do corte multiplicativo. Consequência declarada abaixo — registrada aqui para que a escolha seja auditável, não para relitigar.
5. **Classificador de risco por LLM.** Não-determinístico. **Rejeitada** (mesmo motivo dos ADR-086 e ADR-039).

## Consequências

**Positivas:** o HITL do high-stakes-gate deixa de ser prosa e vira mecanismo — um hook, um `/handoff` ou um CI byo (ADR-088) consegue barrar lendo um código de saída. Fecha o B4 do ADR-086 sem duplicar mecanismo. Zero novo arquivo de tool e zero nova capability (régua §0 satisfeita por extensão). Compatibilidade com o ADR-086 preservada por default.

**Negativa / limite DECLARADO — a lacuna do corte multiplicativo:** `1 × 3 = 3` **não trava**. Ou seja, **raro × catastrófico passa livre**. Essa é exatamente a forma dos incidentes históricos do dono registrados na memória do projeto (segredo de produção em log; teste gravando em estado global do Windows que vazou para outro projeto): probabilidade percebida baixa, dano alto e irreversível. O corte foi escolhido com essa consequência posta na mesa.

**Mitigação de segunda linha (não elimina a lacuna, reduz pouco):** o `action-safety` gateia por **efeito**, não por score. Mas a cobertura mecânica é estreita, e isso foi dimensionado pelo qa-critic: o `effect_gate.py` só inspeciona `Bash` e `PowerShell`, é **fail-open** em erro interno e com o arquivo de regras ausente, e reconhece padrões inequívocos — o julgamento T3 pleno continua sendo prosa do agente. Os mecanismos são ortogonais e a cobertura conjunta é maior que a de cada um, mas **para um item `1×3` cujo dano não se manifesta como comando de shell casando com padrão, nenhum dos dois pega**.

**Risco residual explícito:** item **raro × catastrófico e reversível** não é pego por nenhum dos dois (score 3 < 6; efeito não é T3). Se um incidente desse formato ocorrer, este ADR deve ser revisitado — e a alternativa 4 é o candidato natural.

**Não-feito nesta sessão (declarado, não presumido) — atualizado em 28/07:** `history.md`, evidência em `_meta/qa/` e o release. Fechados em 28/07: `CHANGELOG.md` (entrada 1.74.0), `capabilities.json` (regerado; sem bytes alterados, coerente com a régua §0 — a extensão não cria capability) e o pré-gate `qa-critic` heterogêneo, documentado no apêndice abaixo. O espelho `~/.claude/skills/high-stakes-gate/` só reflete a v1.1.0 após o próximo `framework-sync.ps1` (SessionStart neste repo).

## Pré-gate qa-critic — rodado em 2026-07-28 (Fable, subagente isolado em worktree)

**Veredito da 1ª submissão: REJEITAR.** Um CRÍTICO reproduzível, corrigido abaixo. `CHANGELOG.md` e `capabilities.json` deixaram de estar na lista de não-feito acima (fechados em 28/07); permanecem abertos `history.md`, evidência em `_meta/qa/` e o release.

**A1 — CRÍTICO, corrigido.** Erro de uso do `argparse` saía com **exit 2**, o código reservado a "HITL requerido". `--prob abc`, valor faltando e typo de flag eram indistinguíveis de bloqueio legítimo: um hook registraria "aguardando humano" como evidência de item que **nunca foi avaliado**. É exatamente a confusão que a Alternativa 2 declara ter rejeitado — e a implementação a cometia pela porta dos fundos. Corrigido com `_ParserFailClosed`, subclasse que remapeia `error()` para exit 1. Travado no canário (bloco `g`, 3 casos) e provado por mutação: revertendo para `SystemExit(2)`, o canário falha nos três.

**A2 — MÉDIO, corrigido.** O canário aferia **só o `returncode`**, nunca o `stdout`. Mutação removendo `hitl_requerido` do JSON **passava** — e o `high-stakes-gate/SKILL.md` manda o consumidor ler exatamente esse campo. Corrigido com o bloco `h`, que valida a forma do JSON e a coerência de `hitl_min_score` com a constante. Provado por mutação: removendo o campo, o canário falha.

**A5 — BAIXO, corrigido.** `--items` com lista de não-dicts (`[1,2]`, `["prob impact"]`) atravessava o guard — o operador `in` casa substring em `str` — e estourava `TypeError` cru. O exit 1 vinha do interpretador **por acidente**, não por desenho fail-closed. Corrigido com guarda de tipo antes do teste de chave.

**A3 — MÉDIO, aceito sem correção, com o texto ajustado.** A mitigação de segunda linha existe mecanicamente (`effect_gate.py`, `effect-rules.json`, canário, capability PROVIDES), mas é mais estreita que a prosa sugeria: só inspeciona `Bash`/`PowerShell`, é **fail-open** em erro interno e com rules ausente, e o julgamento T3 pleno continua sendo prosa do agente. A frase original descrevia a política, não a cobertura. **Consequência:** para um item `1×3` cujo dano não se manifesta como comando de shell casando com padrão, **nenhum** mecanismo pega. O risco residual já estava declarado; agora está declarado com o tamanho certo.

**A4 — BAIXO, aceito.** "Compatibilidade retroativa total" é **aditiva**, não bit-a-bit: o stdout ganhou três campos mesmo sem a flag. Como não existe consumidor (confirmado por grep, que também valida a premissa do ADR), nada quebra — mas a palavra "total" era imprecisa.

**Verificado sem achado pelo revisor:** tabela-verdade e bordas (9 combos, score 6 trava, 4 e 3 não travam, multi-itens, lista vazia, campo faltando, fora de faixa, string, bool, float, NaN, JSON malformado, arquivo inexistente) · precedência fail-closed > gate pelo caminho `--items`, inclusive lista com item score 9 **e** item inválido nas duas ordens → exit 1 sem JSON parcial · ortogonalidade: a tabela EXPECT nova é idêntica em score/gate/tier à do ADR-086, nenhum veredito mudou de valor.
