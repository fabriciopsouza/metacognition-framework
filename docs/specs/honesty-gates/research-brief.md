---
papel: discovery
sub_modo: pesquisa-cascata
pergunta_principal: "Como mecanizar gates de honestidade da vitrine (G1 drift, G2 anti-overclaim, G3 claim×LIMITS) e um eval de discriminação que justifique companions sênior sem inchar?"
rodadas: 1
data: 2026-06-03
status: revisado
---

# Research Brief — Gates de Honestidade Mecanizados

> **PROVENIÊNCIA (CONFIRMADO).** Esta pesquisa foi **fornecida pelo dono** (relatório de deep-research externo),
> não produzida nem verificada por este agente. As citações regulatórias (FTC, datas, valores),
> acadêmicas (Zheng et al. NeurIPS 2023, Wright & Augenstein EMNLP 2021) e de produto
> (Vale, DeepEval, Promptfoo, Inspect, Braintrust) estão **classificadas como INFERIDO** até verificação
> independente — **não as cite como CONFIRMADO** sem checar a fonte primária. As tags `[CONSOLIDADO]`/
> `[EMERGENTE]`/`[EM DISPUTA]` são **do autor da pesquisa** e foram preservadas. A §5 (Reconciliação) é
> análise **deste squad** (architect), não da pesquisa.

## 1. Pergunta principal

Os três gaps de honestidade da vitrine identificados na sessão anterior (G1 drift de versão silencia o canário; G2 site sem gate anti-overclaim; G3 claim×`LIMITS.md` não cruzado) são resolvíveis com mecanismo determinístico? E sob que critério um companion sênior (ux-designer/developer) entra **sem violar a régua §0**?

## 1.5 Escopo declarado pelo discovery

### (a) Regulado?
- `[INFERIDO]` A pesquisa cita FTC ("Keep your AI claims in check", 2023; "Operation AI Comply", 2024; caso accessiBe US$1M, 2025) e NIST AI RMF como **lastro de por que** o anti-overclaim importa. **Não é** norma que o framework precise *certificar* — é contexto de risco para a vitrine. Vigência: cenário regulatório 2025–2026 em fluxo (a própria pesquisa adverte).
- **Origem:** via deep-research do dono.

### (b) Alto-risco?
- **Sim (reputacional/legal), baixo-risco técnico.** Overclaim na vitrine pública é exposição de marca + risco regulatório (precedente accessiBe). A correção (gates) é reversível e barata. → puxa atenção, não `high-stakes-gate` de runtime.

### (c) Regras com semântica?
- **Sim:** "fail-closed vs fail-open" é regra com semântica (o *como* importa). Skip silencioso de canário = mentira por omissão — exatamente o que o framework existe para barrar.

### (d) Gaps não-bloqueantes?
- LLM-as-judge sem mitigação de viés mede ruído (§4). Tratado como **EMERGENTE/opt-in**, fora do core offline — não bloqueia G1/G2/G3.
- Léxico ≠ semântica: regex pega absoluto explícito, não paráfrase ("jamais comete deslizes"). Gap consciente; lexicon vivo.

**Gates downstream:** (a) informativo, não dispara certificação; (b) atenção de marca; sem afirmativo de runtime-stake → defaults agnósticos + ADR-059.

## 2. Decomposição

1. Como tornar o canário de marketing fail-closed em vez de fail-open (G1)?
2. Como barrar absoluto-sem-hedge na vitrine de forma determinística (G2)?
3. Como cruzar cada claim público com seu status em `LIMITS.md` (G3)?
4. Sob que prova estatística um companion sênior "discrimina" (e merece existir)?
5. Que ferramentas/CI sustentam isso sem quebrar o offline-first?

## 3. Achados (tags de maturidade do autor da pesquisa, preservadas)

### G1 — Drift de versão que silencia canários
- `if not path.exists(): continue` / `pytest.skip` é **fail-open**: quando `PROMPT-CHAT-WEB-v4.3.md`→`v4.4`, o arquivo fixo some e o teste passa vazio. Doc do pytest: skip/xfail "não falham a suíte por padrão".
- **Fix [CONSOLIDADO]:** (a) resolver versão por `glob('PROMPT-CHAT-WEB-v*.md')` + chave de versão **numérica** (lexical falha: `v4.10`<`v4.9`); nunca `[0]` (glob não garante ordem). (b) `pytest.fail` em lista vazia (fail-closed). (c) `EXPECTED_PROMPT_VERSION` de controle → divergência = falha. (d) `xfail(strict=True)`: xpass inesperado **falha** (detecta problema "conhecido" silenciosamente resolvido).

### G2 — Gate anti-overclaim na vitrine
- **Lastro [INFERIDO]:** FTC trata claim absoluto de IA sem substanciação como enganoso; precedente accessiBe (alegava "WCAG compliance automático", US$1M, voto 5-0). Verbos-alvo: "garante", "qualquer", "elimina", "automaticamente", "não alucina".
- **Método 2 etapas:** (1) **léxico determinístico** de absolutos-sem-hedge no build — pesquisa sugere **Vale** (linter de prosa syntax-aware, regra YAML `existence`, `level: error`, exit≠0) ou **proselint/write-good** (hedging/weasel, mas não-extensível). (2) **gate Python no `web_export.py`** análogo ao `anti_jarvis_gate`: split em sentenças, `ABSOLUTES.search and not HEDGES.search` → `SystemExit(1)` antes de publicar. (3) opcional `[EMERGENTE]`: classificador de "exaggeration" (Wright & Augenstein EMNLP 2021, MT-PET sobre RoBERTa, força-de-claim ordinal) — **não** para CI (lento, custo LLM).

### G3 — Cruzamento claim × LIMITS.md
- **Método [CONSOLIDADO]:** Matriz de Rastreabilidade (RTM). Cada claim recebe **ID estável** (`{#CLAIM-NNN}`); `LIMITS.md` carrega tabela `claim_id|status|evidência`. Canário fail-closed: claim órfão (sem status) = falha; claim público com status ≠ CONFIRMADO = falha. Snapshot/golden-file (Syrupy: **falha quando snapshot não existe**) detecta drift do par de docs.

### Eval de discriminação (companions sênior)
- **Critério de aceite:** só aceitar companion se um eval **comprovadamente separa** saída sênior×rasa.
- **Receita:** (1) gold-set **pareado** da distribuição real, rotulado por especialista, sem contaminação (≥30/classe p/ AUC; ~9–30 calibra juiz). (2) LLM-as-judge **pairwise** + rubrica (Nielsen/WCAG p/ UX; TDD/contract-tests p/ eng). (3) **mitigar vieses** (senão mede ruído): posição (inverter A/B, exigir consistência; swing 10–15pt), verbosidade (length-control à la AlpacaEval2; 15–30pt), auto-preferência (juiz≠autor; ~10–25%). (4) **provar discriminação:** preferência sênior >50% com IC excluindo 0,5; AUC ≥0,90 excelente / ≥0,70 mínimo; kappa juiz×humano ≥0,41. (5) backtest de regressão. `[EMERGENTE/EM DISPUTA]` — UK AISI **desencoraja** LLM para scoring numérico de qualidade.

### Ferramentas (todas `[INFERIDO]` — confirmar API vigente)
- pytest puro (G1/G3 — sem LLM), Vale (G2 léxico), Syrupy (snapshot), DeepEval (G-Eval, pytest-nativo), Promptfoo (YAML, llm-rubric, red-team NIST/OWASP), Inspect (model-roles anti-self-pref), Braintrust (gate de merge nativo).
- **CI fail-closed:** evitar `continue-on-error: true`; cuidado com check "skipped but required" por path-filter; garantir exit≠0. Léxico/drift → pre-commit **e** CI; LLM-as-judge → só CI (sampling + threshold + cache p/ custo; "token trap").

## 4. Caveats (do autor da pesquisa)

- LLM-as-judge é frágil sem mitigação (vieses sistemáticos quantificados); UK AISI desencoraja scoring numérico → tratar como EMERGENTE, validar contra humano.
- Tamanho de gold-set: ~9–30 calibra, mas AUC/kappa significativo pede mais; reportar IC.
- Léxico ≠ semântica (paráfrase escapa); lexicon vivo + classificador como complemento.
- Regulação não é checklist mecânico; gate reduz risco, não substitui revisão jurídica/humana.
- Snapshot exige disciplina (`--snapshot-update` mal-usado re-aprova drift).

## 5. Reconciliação com o DNA do framework (análise do squad — architect)

> **Este é o filtro régua §0.** A pesquisa recomenda dep externas; o framework é offline-first, determinístico,
> sem embeddings, Python+PowerShell, "NÃO MEDIDO nunca fabrica". Mapeamento nativo > importação:

| Pesquisa propõe | Mecanismo NATIVO equivalente | Decisão |
|---|---|---|
| Vale (binário Go) p/ G2 | `anti_jarvis_gate` (regex Python, já existe) | **Estender o gate Python.** Vale = opção secundária, não default (dep externa). |
| Syrupy p/ G3 snapshot | `build_limits.py --check` (golden-file, já existe) | **Reusar `--check`.** Não adicionar Syrupy. |
| DeepEval/LLM-as-judge p/ discriminação | `test_discovery_eval.py` (eval raso×sênior **sem** LLM-juiz, já existe) | **Estender o eval nativo.** LLM-as-judge = EMERGENTE/opt-in, fora do core offline. |
| `EXPECTED_PROMPT_VERSION` arquivo de controle | `web_export.main_version()` (deriva versão do main, já existe) | **Reusar.** Não criar arquivo de controle novo. |

**Conclusão:** G1/G2/G3 são implementáveis **com zero dep externa**, reusando trilhos existentes (régua §0 satisfeita: funde, não adiciona). O eval LLM-as-judge fica **registrado como caminho EMERGENTE** (ADR futuro com dependência declarada), não entra agora.

## 6. Handoff

Alimenta: **ADR-059** (decisão) + `plano.md` (execução faseada). Consumível por outra sessão/PC sem perguntar de volta (este brief + ADR + plano são autocontidos).
