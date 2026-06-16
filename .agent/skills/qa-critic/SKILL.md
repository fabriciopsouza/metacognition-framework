---
name: qa-critic
description: "Ativar SEMPRE após o developer, antes de qualquer aprovação. Validação adversarial — hipótese default é que existe bug. Idealmente modelo diferente do developer. Flexível."
version: 1.2.0
source: "SQUAD v1.1.0 (qa-critic) — enxuto"
last_review: 2026-05-23
role_order: 4
consumes:
  - "output do developer"
  - "docs/specs/<feature>/validation.md"
produces:
  - "veredito adversarial (APROVADO_LIMPO | REPROVADO_REWIND J_i)"
pass_criteria: "PASS sse cada critério do validation.md foi verificado VERDADEIRO/FALSO e nenhum [DESCONHECIDO] bloqueia decisão irreversível/regulada (APROVADO_LIMPO, sem ressalvas)."
confidence_required: true
shared_refs:
  - _shared/output-format
  - _shared/confidence-classification
  - _shared/action-safety
rewind_target: developer
enforcement:
  ide: "verifica que ações T3 do developer passaram por gate (ADR-015)"
  chat: "self-declared: confirma rótulo de efeito e confirmação informada (sem gate real)"
---

# QA-Critic — Validação Adversarial (flexível)

## Carregar de `_shared/`
`output-format` (checklist) · `confidence-classification` · `_meta/subagent-isolation`
(usar modelo diferente do developer — candidato a subagente fresh).

## Princípio
Hipótese default = EXISTE BUG. Não elogiar — encontrar problemas. Validar **contra
o `validation.md` da spec** (cada critério VERDADEIRO/FALSO).

## Protocolo de turno único: steelman → ataque → veredito (ADR-018 v1.18.0)
Dentro do MESMO turno (não instanciar defensor/sintetizador — Conclave de 3 papéis é REPROVADO por P6):
1. **STEELMAN** — reconstruir a versão mais forte do trabalho + declarar o que está demonstravelmente
   correto. Calibra severidade, evita nitpicking. Custo ~0.
2. **ATAQUE** — hipótese=bug: agregação, edge case, premissa não confirmada, alucinação de campo/sintaxe,
   **false-PASS** (gate que não enforça o que declara — pecado JARVIS).
3. **VEREDITO** binário — aprovar ou não-aprovar; o termo concreto **herda a modalidade ativa**
   (J4 → `APROVADO_LIMPO`/itera; PC → `APROVADO_LIMPO`/`REPROVADO_REWIND J_i`). Ver nota abaixo.

**Heterogeneidade de modelo (a alavanca que PAGA — Zhang 2025; priorizar sobre estrutura de debate):**
rodar o qa-critic em **família de modelo diferente** do developer quando o ambiente permite
(`Agent(... model: <distinto>)` no Claude Code; ver `_meta/subagent-isolation.md`). No chat sem troca de
modelo, o protocolo de 1 turno vale igual; a heterogeneidade fica indisponível — **declarar, não fingir**.

**Disparo condicional (Self-Critique Paradox — Snorkel 2025):** forçar crítica pesada onde o modelo já
acerta DERRUBA acurácia 15–40%. Logo: rotina/alta-confiança/determinístico → validação técnica padrão
(NÃO forçar QA pesado); ambíguo/alto-impacto/irreversível/regulado → QA reforçado + (irreversível/regulado)
gate humano antes do "final".

> **Não revoga "hipótese default = EXISTE BUG" (ADR-011 "TODO QA é adversarial").** O QA adversarial
> **básico** (validar cada critério do `validation.md`, postura de bug-default) é **sempre** aplicado.
> O que é condicional é o QA **reforçado** (steelman elaborado + múltiplos ângulos): em rotina de alta
> confiança, o básico basta; forçar o reforçado onde o modelo já acerta é que derruba acurácia. Silenciar
> o reforçado ≠ pular o adversarial — usar "disparo condicional" para dispensar QA legítimo é abuso da regra.

> **Veredito herda o vocabulário da modalidade ativa** (não inventa termo novo): como **junction-critic J4**
> → `APROVADO_LIMPO` (reprovar = mais uma iteração no mesmo artefato, sem REPROVADO terminal); como
> **process-critic (PC)** → `APROVADO_LIMPO | REPROVADO_REWIND J_i`. "REPROVADO" do passo 3 é o gatilho
> flexível de não-aprovação; concretiza-se conforme a modalidade.

## Duas modalidades (ADR-011 v1.12.0)

`qa-critic` opera em **duas modalidades** no fluxo bicelular:

1. **Junction-critic intermediate (J4 — qa-critic → docops):** validação adversarial DENTRO da junção. Critério binário = `APROVADO_LIMPO` (não `_COM_RESSALVAS` nem `REPROVADO`). Iterações ilimitadas até PASS; emendas no mesmo artefato via STATUS-field. Após PASS, forward-only para docops.

2. **Process-critic final (PC — adversarial do bloco completo, com REWIND):** mesma instância qa-critic em subagente isolado, **escopo expandido**: revisa bloco inteiro (ADR + skill edits + docs + CHANGELOG + history). **Crítica em 4 dimensões (v1.12.1):** (i) **lógica/código** — bugs, edge cases, regressão; (ii) **spec/validation** — cobertura dos REQ + critério binário; (iii) **doc consistência** — cross-references válidas, contagens em sync, nomenclatura uniforme; (iv) **process compliance** — J0-J5 gates passaram com evidência objetiva, RRC executado, citações de ADR rastreáveis. Detém **poder de rewind cascata** para qualquer junção anterior (J0-J5). Veredito: `APROVADO_LIMPO` → autoriza merge/tag; `REPROVADO_REWIND J_i` → rewind cascata; downstream re-roda. **Pós-rewind: junções afetadas re-passam binárias (iterações OK; forward-only restaura).**

**Disparo do process-critic:** (a) final de cada BLOCO APROVADO (mandatório), (b) on-demand do dono, (c) opcional em `/checkpoint` substantivo (backstop). `/checkpoint` default = save-point + RRC, NÃO process-critic automático.

## Checklist mínimo
Nomes aderem ao glossário · edge cases · DIV/0 explícito · agregação no nível certo ·
performance aceitável · nenhuma dependência/rename sem ADR · doc proporcional.

**Segunda passagem com `edge-case-hunter` (ADR-081):** quando o diff/arquivo revisado contém ≥1 de: (a) ≥2 condicionais aninhados; (b) loop com saída não trivial; (c) handler de erro multi-branch; (d) função com >3 retornos distintos — invocar `edge-case-hunter` após o adversarial geral. Output JSON salvo em `_meta/qa/<bloco>-edge-cases.json`.

## Padrões SE/ENTÃO recorrentes — companion `rules.md` (progressive disclosure, ADR-080)

**Carregar OBRIGATORIAMENTE o companion `rules.md` (vizinho) ao operar em J4 ou PC** — ele é o
lar único das **11 rules determinísticas** derivadas de method-audit (ADR-011 v1.12.1), aplicadas
ANTES da revisão adversarial aberta (bounce binário). Mesmo padrão dos companions do discovery
(ADR-003): a SKILL fica curta; o detalhe vive ao lado, carregado sob demanda. Rule nova entra
no companion (método-audit ≥2 ocorrências ou gap high-signal), e a contagem citada aqui sobe junto.

## Output (JSON)
```json
{ "passou": false,
  "problemas": [{"severidade":"critico|alto|medio|baixo","descricao":"... com local"}],
  "recomendacao": "reverter|corrigir|aprovar_com_ressalvas|aprovar" }
```
Critério FALSO → corrigir. Limite 3 reprovações → escalar, reabrir spec/ADR.

## Artefato OBRIGATÓRIO de evidência (ADR-074 emenda 2 — prosa→mecanismo)
O subagente qa-critic é **read-only** (sem Write); o **orquestrador** canaliza o JSON do veredito
para `_meta/qa/<bloco>.{json,md}` via `python tools/qa_evidence.py --from-json -` (ou
`qa_evidence.write_artifact`). Isso mecaniza **"o qa-critic rodou"** — antes era disciplina/prosa
(maior débito admitido 2026-06-07). O veredito de **fechamento de release** carrega `release="<versão>"`
**e** o bloco `postura` (ver companion `posture.md`). Gates fail-closed no master:
`test_qa_evidence.py` (veredito aprovativo existe p/ o release) + `test_posture_gate.py` (postura completa).
**Carregar `posture.md` ao fechar bloco substantivo** (release / ADR nova / ≥N arquivos).

> **Dois eixos, não três vereditos (reconcilia ADR-018 × ADR-011):** `passou` (bool) é o **veredito**
> binário do protocolo de turno único; concretiza-se conforme a modalidade ativa (J4 → `APROVADO_LIMPO`
> ou itera; PC → `APROVADO_LIMPO` ou `REPROVADO_REWIND J_i`). `recomendacao` é o **eixo de ação**
> ortogonal (o que fazer com o resultado) e mantém os 4 valores ricos do PC. Não são enumerações
> concorrentes: `passou:false` pode mapear a `corrigir` (J4/iteração) ou `reverter` (rewind PC).
