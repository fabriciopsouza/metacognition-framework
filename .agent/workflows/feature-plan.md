# /feature-plan <descricao> [--quick] — Plano técnico com Spec + ADR (v1.3)

## Pré-requisito
briefing.md preenchido + glossário com termos relevantes.

## Grau do fluxo — declarar ANTES do passo 1
**`--quick` é o MESMO fluxo com artefato menor, nunca um fluxo paralelo.** O que ele corta é
cerimonial; o que ele mantém é gate. Gatilho **binário** (não é escolha de humor) — só cabe se
as QUATRO forem verdadeiras:

| | Condição |
|---|---|
| 1 | toca ≤ 2 arquivos |
| 2 | não muda contrato (assinatura, schema, nome aprovado, formato de saída) |
| 3 | não é regulado / alto-risco / número que vai a decisão |
| 4 | é reversível — **sem E1 nem E2** do `action-safety` (E1 destrói dado irrecuperável, E2 é irreversível/não-idempotente). *Não* é E5/E6: aqueles são controle de segurança e escopo atípico, e não dizem nada sobre reversibilidade |

**Qualquer uma falsa → escalada automática para o grau completo, ANUNCIADA em 1 linha.**
Escalada não pede permissão; ela é o default retomado. Se descobrir no meio que uma condição
caiu (a "mudança de 2 arquivos" virou 5), escalar ali — não terminar em quick por inércia.

## Sequência — grau COMPLETO (default)
1. **PMO:** confirmar escopo, sinais de complexidade e **classe de confiança**
   (governa o roteamento — `rules/04`).
2. **Criar spec atômica — arquivo único (ADR-117):** copiar
   `docs/specs/_template-spec-unico/spec.md` → `docs/specs/<feature>/spec.md` e preencher a
   Parte A — Requisitos; **depois** que o dono aprovar os requisitos, escrever a Parte B — Aceite
   (critério **binário**) e fazê-la ratificar pelo revisor isolado. Sem Parte B ratificada → não
   avança. O formato antigo (`_template/` → `requirements.md` + `validation.md`) continua aceito
   pelos gates; `python tools/spec_unificar.py <pasta>` converte sem perda.
3. `/handoff architect`
4. **Architect:** 3 alternativas + recomendação + ADR rascunho. O ADR **referencia
   a spec** (vincular decisão → Parte A do `spec.md`, ou `requirements.md`).
5. **PMO:** apresentar ADR + spec ao usuário — aguardar aprovação.
6. ADR aceito → `/implement`.
7. `/handoff docops` — salvar ADR em `docs/adr/NNN-titulo.md`.

## Sequência — grau `--quick`
Um único arquivo `docs/specs/<feature>/spec.md`, três seções, nesta ordem. Não clonar o
`_template/` (são 5 arquivos para uma mudança de 2):

```markdown
# <feature>
## 1. Requisitos
<o quê, e para quem. Cada afirmação classificada CONFIRMADO|INFERIDO|DESCONHECIDO.>
## 2. Decisão
<3 alternativas em 3 linhas + a escolhida e por quê. SEM número de ADR.>
## 3. Tarefas e aceite
<as tarefas, e o critério de aceite BINÁRIO de cada uma — verdadeiro/falso, medível.>
```

Depois: implementar → **qa-critic adversarial, 1 rodada, modelo um degrau abaixo do autor**
(escada `model-policy.json`) → corrigir → CHANGELOG.

**O que `--quick` NÃO corta, e não é negociável:**
- o **critério de aceite binário escrito ANTES do código** (seção 3). É ele que impede o
  requisito de se auto-aprovar — a mesma razão pela qual o grau completo exige a Parte B
  escrita depois da aprovação da Parte A, e ratificada pelo revisor;
- a **rodada de qa-critic**. Um grau que dispensa o crítico é `--no-verify` com nome bonito;
- o **process-critic do ADR-011**, que é obrigatório ao fim de todo BLOCO entregue — e uma
  feature `--quick` é um bloco entregue. Aqui ele não é cortado, é **fundido**: a única rodada
  de qa-critic usa o mesmo subagente isolado (modelo ≠ autor) e carrega **os dois chapéis** —
  o achado substantivo e o checklist de conformidade de processo —, declarando cada um em
  separado no veredito. Fusão, não dispensa;
- o registro no CHANGELOG.

**O que `--quick` corta:** ADR numerado em `docs/adr/` (vira a seção 2), `context-brief.md`,
`data-dictionary.md`, `mission.md`, `readiness-gate`, e **J6** — a decisão de re-orquestração
do PMO (ADR-045), que é outra coisa: J6 roda *depois* do process-critic (ADR-011) dar
`APROVADO_LIMPO`.

> **Limite declarado.** Se a leitura estrita do ADR-011 exigir o process-critic como rodada
> **separada** da de J4, então a fusão acima é uma exceção que precisa de **ADR próprio** —
> workflow não revoga ADR Aceito por edição de arquivo. Enquanto não houver esse ADR, na
> dúvida rode as duas rodadas.

## Critério de saída
- **completo:** ADR com Status "Aceito" (se houve decisão de arquitetura) + Parte B — Aceite do
  `spec.md` (ou `validation.md`) com critérios binários definidos e ratificados.
- **`--quick`:** `spec.md` com as 3 seções + veredito do qa-critic registrado + todo critério
  de aceite da seção 3 medido como VERDADEIRO.
