---
name: party-mode
description: "Orquestrar conversa real entre múltiplas personas com perspectivas conflitantes. Ativar quando o PMO ou o dono pede exploração multi-perspectiva, debate de decisão arquitetural, retrospective com vozes distintas, ou menciona 'party mode', 'roundtable' ou 'debate'. NÃO ativar para QA de código (isso é qa-critic + edge-case-hunter) nem para execução de tarefas (isso é developer). Útil especialmente antes de fechar uma ADR ou quando todos parecem concordar demais (groupthink)."
version: 1.0.0
source: "integração externa seletiva — extraído e adaptado para metacognition; proveniência na ADR-081"
last_review: 2026-06-16
role_order: null
consumes:
  - "tópico, decisão ou artefato a explorar com múltiplas perspectivas"
produces:
  - "conversa estruturada entre personas com síntese de insights e pontos de divergência"
pass_criteria: "PASS sse (proxies VERIFICÁVEIS na saída, não julgamento subjetivo): (a) ≥2 personas com falas textualmente distintas (posições não-idênticas, rotuladas por nome); (b) a saída contém OU ≥1 troca de discordância explícita entre personas OU, se houve consenso, um turno rotulado de contrarian/devil's-advocate injetado (presença verificável do rótulo); (c) a síntese final lista takeaways E pontos de divergência não-resolvidos. Nota: party-mode é skill EXPLORATÓRIA (não gate do pipeline) — pass_criteria é proxy de qualidade, não bloqueio binário de junção."
confidence_required: false
shared_refs: []
---

# Party Mode — Exploração Multi-Perspectiva com Personas

## Princípio

**Lê como pessoas conversando, não como relatórios empilhados.** Turnos curtos, reações ao que foi dito, opiniões. O objetivo é conflito genuíno, não consenso — se todos concordam, o modo falhou.

Cada persona é inconfundível pela voz, não apenas pelo nome. Se você esconder os labels, ainda conseguiria saber quem está falando.

**Casos de uso no metacognition:**
- Explorar uma decisão arquitetural antes de fechar ADR
- Retrospective com perspectivas técnica, de processo e de produto
- Validar spec com stakeholders simulados (usuário, engenheiro, negócio)
- Qualquer situação onde um único ângulo parece incompleto

## FLOW

### Passo 1 — Setup

- Identificar o tópico/decisão/artefato a explorar
- Definir 3–4 personas relevantes para o contexto. Exemplos:
  - Decisão arquitetural: Arquiteto pragmático · Engenheiro focado em manutenção · Segurança/compliance · Usuário final
  - Retrospective: Desenvolvedor · PMO · QA adversarial · Stakeholder de negócio
  - Spec review: Especialista de domínio · Engenheiro cético · Usuário novato · Auditor
- Apresentar o elenco (ícone sugerido + nome + papel em uma linha) e perguntar se o dono quer ajustar
- Definir o tema de abertura

### Passo 2 — Rodar a conversa

**Formato de cada turno:**
```
🎭 **[Nome]:** [o que essa persona diz — curto, em voz própria, reagindo ao que foi dito antes]
```

**Regras:**
- 2–4 personas por rodada; variar quem aparece
- Turnos curtos por padrão — persona vai longo SÓ se o dono pedir
- Personas reagem umas às outras, não apenas ao tópico
- Nunca misturar vozes numa síntese durante a conversa — deixar o conflito visível

**Injeção de contrarian (obrigatória se todos concordarem):**
Quando uma rodada termina sem discordância real: introduzir uma persona cética com a instrução explícita de contestar o ponto mais forte do consenso.

### Passo 3 — Seguir o dono

O dono direciona a qualquer momento:
- "Persona X, o que você acha do ponto de Y?" → só X responde, reagindo a Y
- "Aprofundar isso" → a persona do último ponto vai mais fundo (única exceção ao turno curto)
- Novo tópico → novas personas relevantes entram, as que não se encaixam saem
- Silêncio prolongado do dono → perguntar: "continuar, mudar tema, ou encerrar?"

### Passo 4 — Encerrar

Quando o dono sinaliza término (qualquer formulação: "obrigado", "isso é tudo", "encerrar"):
- Síntese dos **principais takeaways** — o que cada perspectiva contribuiu
- **Pontos de divergência não resolvidos** — explícitos, não varridos para debaixo do tapete
- Retornar ao modo normal

## Heterogeneidade de modelo

Quando o ambiente permite spawn de subagentes (`Agent(... model: <distinto>)` no Claude Code — ver `tools/model-policy.json` e ADR-078 para a escada de modelos):
- Spawn paralelo para primeiras impressões independentes (cada persona responde ao tópico sem ver as outras)
- Spawn sequencial quando é preciso que persona B reaja ao que persona A disse de fato
- Sem spawn: agente único vocaliza as personas — válido, porém com menor independência cognitiva; declarar explicitamente ao dono.

## O que NÃO fazer

- Narrar a mecânica ("Temos 4 agentes na sala...") — quebra a imersão
- Todos monologando em paralelo sem reagir uns aos outros
- Síntese prematura antes do conflito se resolver
- Persona de suporte que apenas concorda — nunca é útil

## Integração com advanced-elicitation

Métodos colaborativos do `advanced-elicitation` (categorias `collaboration`, `competitive`) podem invocar o `party-mode` para executar o método com personas reais em vez de perspectivas vocalizadas pelo agente único.
