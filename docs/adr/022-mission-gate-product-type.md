# ADR 022 — Mission-gate: product_type declarado/confirmado via hook, gated por execution-modes

- Status: Aceito (qa-critic Sonnet isolado: R1 REPROVADO [ALTO template↔hook] → fixes → R2 APROVADO, ADR-011/018)
- Data: 2026-05-30 · Decisores: dono + squad (architect)
- Onda: runtime-hooks (v1.21.0) · Pesquisa: SPEC Perplexity "ADR-018 — Mission Gate" + prompt do dono (sessão l.553) · Tipo: **EMENDA** (estende discovery/ADR-010/012 + ADR-005)
- Relaciona: ADR-005 (execution-modes), ADR-010/012 (escopo declarado pelo discovery), ADR-023 (app SW/dados que consome o product_type), `discovery/SKILL.md` passo 6.

## Contexto

O framework existe para **culminar em produto** (dono, sessão Perplexity l.421/427: "geralmente culminando em código… o objetivo é facilitar para o usuário final: ide, exe, código ide facilitado com gui"). **Quais papéis especializados ativam** (ux-designer p/ produto com UI, evals-engineer p/ dados/ML — ADR-023) depende do **tipo de produto**. Hoje o tipo de produto não existe como conceito mecânico; o escopo é declarado pelo discovery em **prosa** (ADR-010/012). O dono perguntou diretamente (l.553): *"isso não pode ser disparado, freado com hook? confirmação humana no briefing inicial se autosuficiente, ou durante o processo se avançado/padrão? não dá pra tornar ferramenta?"* — que é o "Mission Gate" da SPEC Perplexity (3 modos BRIEFING/ADVANCE/STANDARD), mapeável sobre os **nossos 3 modos de execução** (ADR-005).

**Guarda de agnosticismo (P12):** a **taxonomia** de tipos de produto (ide-code, executable, gui-app, data-notebook…) e **qual papel cada tipo ativa** são DOMÍNIO → vivem na **aplicação ativa** (ADR-023), **não** no núcleo. O hook do núcleo só enforça "campo declarado + confirmado"; os **valores válidos** vêm da config da aplicação (análogo a `agnostic-denylist.txt`). Sem aplicação → default agnóstico (exige o campo declarado, qualquer valor).

## Decisão (1 frase ativa)

Adicionar `tools/hooks/mission-gate.ps1` (+ `.sh`) que verifica que o `mission.md` do projeto declara `product_type` (e escopo, fundindo com o que o discovery já elicita — ADR-010/012), **confirmado conforme o modo de execução** (ADR-005): **autosuficiente** → confirmar uma vez no briefing; **avançado/padrão** → confirmar antes de avançar para implementação (J2+) via diretriz injetada + fluxo execution-modes (backstop PreToolUse duro DEFERIDO — fase 2); a **taxonomia de tipos e o mapa tipo→papel são da aplicação**, não do núcleo (default agnóstico se ausente).

## Alternativas consideradas (≥3)

1. **Não fazer / manter escopo em prosa (status quo).** Prós: zero código. Contras: tipo de produto e ativação de papéis dependem de disciplina do PMO; "PMO errar o product_type" é o risco nomeado pela SPEC Perplexity. **Rejeitada.**
2. **Hardcodar a taxonomia de product_type no núcleo** (gui-app, notebook, executable…). Prós: hook autossuficiente. Contras: **viola P12** (domínio no núcleo); foi o que a SPEC Perplexity fez. **Rejeitada.**
3. **Gate só no SessionStart** (sem backstop PreToolUse). Prós: simples, sem novo PreToolUse a coexistir com o effect-gate. Contras: se `mission.md` for editado/ficar incompleto depois do SessionStart, não há reconfirmação automática. **Adotado o recorte SessionStart-only no v1** (dentro do desenho da alt 4): a confirmação "antes de J2+" é a diretriz injetada + o fluxo de `execution-modes`; o **backstop PreToolUse duro fica DEFERIDO** (régua §0 — fase 2, só com gatilho real de edição-pós-sessão observada).
4. **Hook mission-gate agnóstico + taxonomia na aplicação + confirmação gated por modo (ESCOLHIDA).** Prós: mecaniza o pedido do dono (l.553), vira espinha de ativação dos papéis (ADR-023), respeita ADR-005, mantém núcleo agnóstico. Contras: depende da aplicação prover a lista de tipos (default agnóstico cobre a ausência); adiciona `mission.md` — mitigado por ser **onde o escopo declarado do discovery passa a morar** (funde, não duplica — régua §0).

## Consequências

**Positivas:** `product_type` vira gate verificável (não boa-vontade do PMO); ativa o papel certo no momento certo; confirmação proporcional ao risco via modo de execução; núcleo segue agnóstico.
**Negativas:** introduz `mission.md` como artefato — aceitável porque absorve a declaração de escopo (ADR-010/012), não cria trilha paralela.
**Riscos:** (a) sobreposição com discovery-escopo se `mission.md` virar artefato separado — **mitigação: `mission.md` É o lar persistente do escopo declarado** (passo 6 do discovery passa a escrevê-lo). (b) confirmação durante o processo pode irritar em projeto trivial — mitigado pelo modo (autosuficiente confirma só 1×) e por product_type opcional quando não há papel especializado a ativar. (c) bug #37210 (permissionDecision deny ignorado p/ alguns tools) — o backstop PreToolUse usa `ask`/contexto, não deny duro, e o gate real é a confirmação humana.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.21.0-runtime-hooks-web` · `2026-05-30` · grep `mission-gate|product_type|mission.md`
- Artefatos: `tools/hooks/mission-gate.ps1` + `.sh` (parse inline `product_type:` + fallback heading; mapa lido por glob `exemplos/*/product-types.txt`, não acoplado a uma distribuição); template `docs/specs/_template/mission.md` (campo inline `product_type:` + escopo declarado); edição `discovery/SKILL.md` passo 6 (item "(f) product_type → grava em mission.md"); wiring `.claude/settings.json` (**SessionStart**; PreToolUse backstop deferido — ver alt 3); canário `tools/test_mission_gate.py` (BRIEFING/ADVANCE/STANDARD inline+heading); a aplicação SW/dados (ADR-023) provê `product-types.txt` + mapa tipo→papel.
