---
artefato: context-brief
projeto: <nome do projeto>
entidade: <empresa/cliente/órgão — a entidade real>
dominio: <atividade VERIFICADA no dado/documento, não suposta>
data_geracao: <YYYY-MM-DD>
autor: <agente/role>
status: evidência de discovery (prova da decisão)
confianca_global: <ALTA|MÉDIA|BAIXA — com base nas fontes>
tags: [<dominio>, <entidade>, <regulatorio>, <metodo>, discovery, context-research]
rag_ready: true
estilo_citacao: ABNT
---

# Context-Brief <projeto> — Evidência de Discovery (prova da decisão)

> Persiste, de forma auditável e recuperável (RAG/ABNT/ADR-style), a investigação de contexto
> que fundamenta o desenho da solução. Disparado por sinal de STAKE (`context-signals.txt`, ADR-051).
> Cada afirmação material é classificada **CONFIRMADO** (fonte) / **INFERIDO** / **DESCONHECIDO**.
> Validado por `tools/check_context_brief.py` antes de J2. (Gate prova ESTRUTURA, não qualidade.)

## 0. Sumário executivo (3 fatos que mudam o design)
1. <fato + impacto no design> `[CONFIRMADO|INFERIDO]`
2. ...
3. ...

## 1. Perfil da entidade (eixos de discovery sênior)
| Eixo | Fato | Confiança |
|---|---|---|
| Identidade / controle | <…> | <…> |
| Setor / enquadramento | <…> | <…> |
| Porte (receita/volume/share) | <…> | <…> |
| Cadeia (faz/onde/vende/compra) | <…> | <…> |
| Modelo (B2C/B2B/B2B2C) | <…> | <…> |
| Escopo (nicho vs amplo) | <…> | <…> |
| Como controla o processo medido | <…> | <…> |
| Posição de mercado / concorrência | <…> | <…> |

## 2. Verificação de âncora (vigência + pertinência) — OBRIGATÓRIA
> Cada norma/benchmark citado é **vigente** e **pertinente a ESTE tipo de entidade**?
> Acusar **mesmo quando a escolha foi deliberada** (registro consciente, não acusação de erro).

| Norma / âncora citada | Vigência | Pertinência ao tipo de entidade | Decisão registrada |
|---|---|---|---|
| <norma> | <em vigor? revogada? por quem?> | <aplica a este tipo? ou é de outra atividade → referencial> | <manter/descartar/usar como referência> |

## 3. Materialidade (computada do dado quando possível — foco, não amplitude)
<quanto se perde/vale; número que justifica o rigor> `[CONFIRMADO dos dados]`

## 4. Benchmark de método (vs prática do domínio)
<o método é aderente? pontos fortes/fracos vs alternativas> `[CONFIRMADO|INFERIDO]`

## 5. Lacunas não-bloqueantes a elicitar
(a) … (b) … (c) …

## 6. Fontes (ABNT-style, com data de acesso)
- AUTOR. *Título*. Disponível em: <URL>. Acesso em: <DD mmm. AAAA>.

*Termos proprietários sem fonte pública = DESCONHECIDO declarado, não inventado.*
