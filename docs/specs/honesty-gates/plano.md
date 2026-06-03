# Plano de Execução — Gates de Honestidade da Vitrine (ADR-059)

> Execução faseada. Cada fase tem **threshold binário** (PASS/FALHA) e **plano de cascata**.
> Princípio transversal: **fail-closed** (artefato/claim ausente = falha, nunca skip) e **zero dep externa**
> (reusar trilho nativo; dep da pesquisa = opção secundária marcada `[opt-in]`).
> Estado atual: **planejado** (nada implementado). Origem: ADR-059 + `research-brief.md`.

## Fase 1 — Estancar o fail-open (G1) · custo ~zero, sem LLM, **prioridade máxima**

**Problema:** `test_marketing_claims.py:24` aponta `PROMPT-CHAT-WEB-v4.3.md` (inexistente); `continue` em arquivo ausente silencia o anti-overclaim no prompt web.

**Passos:**
1. Reescrever a seleção de doc: `glob('PROMPT-CHAT-WEB-v*.md')` + chave de versão **numérica** (`(4,4) > (4,10)`? não — parsear int por componente; lexical erra `v4.10`<`v4.9`). Pegar a mais recente (`[-1]` após sort), nunca `[0]`.
2. **Fail-closed:** lista vazia → `pytest.fail`/exit≠0 com mensagem clara, **nunca** `continue`/`skip`.
3. Reusar `web_export.main_version()` (nativo) para a versão esperada em vez de criar `EXPECTED_PROMPT_VERSION` (régua §0); divergência canário↔main = falha.
4. Varrer a suíte: qualquer `skip`/`importorskip`/`continue` em **canário** (não em teste de ambiente) é débito desta fase.

**Threshold:** zero `skip`/`continue` em canário; o anti-overclaim roda comprovadamente sobre o prompt web da versão de cabeça. **Falha** se a suíte fica verde com o doc esperado ausente.

**Cascata:** correção na fonte (`tools/`); propaga a todas as distribuições no próximo export (o canário é interno, roda na fonte/CI).

## Fase 2 — Gate anti-overclaim na vitrine (G2) · determinístico

**Passos:**
1. Criar `tools/anti_overclaim_gate.py`: split em sentenças; `ABSOLUTES` (não alucina|garante|garantido|elimina|infalível|100% (preciso|seguro|confiável)|sempre|nunca) **sem** `HEDGES` (pode|tende a|em geral|na maioria|busca|visa|projetado para|sob condições|tipicamente|em testes) → violação.
2. **Fundir, não criar pipeline:** chamar o gate no fim de `web_export.py`, **antes** de escrever o artefato, espelhando como `anti_jarvis_gate` já é chamado. Absoluto-sem-hedge → `SystemExit(1)` (aborta export).
3. Estender a headline atual: "agentes que não alucinam" → reescrever com hedge ("que classificam o que sabem e não inventam o que não sabem" — já é o subtítulo) OU registrar exceção auditável.
4. Canário `test_anti_overclaim.py`: injeta sentença-veneno ("o agente nunca alucina") e prova que o gate pega (espelha o teste anti-JARVIS em `test_web_export.py:62-68`).
5. `[opt-in]` Vale (`styles/Honesty/Overclaims.yml`, `level: error`) como linter de prosa em pre-commit **se** o dono quiser feedback no editor — secundário, dep externa.

**Threshold:** todo absoluto na vitrine tem hedge, é removido, ou tem exceção justificada+revisada; o canário-veneno passa.

**Cascata:** o gate roda dentro do `web_export` → cobre `-web` público e `-web-premium` automaticamente. **noadmin:** sem hook, o agente **declara e aplica inline** a checagem de overclaim antes de publicar (gate anunciado, ADR-047). **public/premium não-web:** README/PROMPT já cobertos por `test_marketing_claims` (após F1).

## Fase 3 — Cruzamento claim × LIMITS.md (G3) · determinístico

**Passos:**
1. Atribuir `{#CLAIM-NNN}` estável a cada claim da vitrine (fonte de claims do `web_export`).
2. Adicionar coluna/tabela `claim_id | status | evidência` ao `LIMITS.md` (gerada por `build_limits.py`, não à mão).
3. `test_claims_vs_limits.py` fail-closed: claim órfão (sem status) = falha; claim público com status ≠ `CONFIRMADO` (PROVADO) = falha.
4. **Reusar `build_limits --check`** (golden-file nativo) para drift do par de docs — **não** adicionar Syrupy.

**Threshold:** zero claim público não-CONFIRMADO; zero claim órfão; `--check` reprova divergência.

**Cascata:** `LIMITS.md` já cascateia (gerado); os IDs vão junto no export. public: só claims CONFIRMADOS sobrevivem ao tier público.

## Fase 4 — Eval de discriminação p/ companions sênior (`[EMERGENTE/opt-in]`) · com LLM, **fora do core offline**

> **Não entra agora.** Registrado como caminho; exige ADR próprio com **dependência declarada** (LLM-as-judge no CI). Critério de aceite ANTES de qualquer companion sênior (ux-designer/developer) ser aceito:

**Passos (quando ativado):**
1. Estender `test_discovery_eval.py` (eval nativo raso×sênior **sem** LLM-juiz) com gold-set **pareado** (≥30/classe) da distribuição real, rotulado por especialista, sem contaminação.
2. Se usar LLM-as-judge: pairwise + rubrica (Nielsen/WCAG p/ ux; TDD/contract-tests p/ dev); **mitigar viés** — posição (inverter A/B, exigir consistência), verbosidade (length-control), auto-preferência (juiz≠autor).
3. **Backtest de regressão** sobre saídas anteriores antes de mergear.

**Threshold de aceite do companion (o que destrava ou bloqueia):** preferência sênior >50% com IC excluindo 0,5 **E** AUC ≥0,70 (mínimo; 0,90 ideal) **E** kappa juiz×humano ≥0,41. **Se AUC ≤0,70 ou kappa <0,41 → rejeitar o companion** (não discrimina = inchaço). Carregamento sempre **sob demanda** (sinal de `product_type` UI/software), nunca no core sempre-ativo.

**Cascata:** companion provado entra no premium (full); web (estrutura, sem enforcement-assert); noadmin (sob demanda, gate anunciado); public (core agnóstico — companion como aplicação, fora do núcleo).

## Sequência recomendada

F1 (dias, bug ativo) → F2 (1–2 sem) → F3 (1–2 sem) → F4 só após decisão consciente do dono (ADR próprio). F1–F3 = **um bloco** (qa-critic adversarial ao fim, `test_*` verdes no CI, docops fecha). F4 = bloco separado, gated por dep.

## Riscos / limites

- Léxico não pega paráfrase → lexicon vivo + qa-critic backstop (gap consciente, declarado no ADR-059).
- F4 mede ruído se viés de juiz não for mitigado (UK AISI desencoraja scoring numérico por LLM) → por isso fica EMERGENTE.
- Disciplina de `{#CLAIM-NNN}` exige que toda nova claim na vitrine receba ID (senão F3 acusa órfão — que é o comportamento desejado).
