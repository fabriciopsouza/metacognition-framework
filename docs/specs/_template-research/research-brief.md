---
papel: discovery
sub_modo: pesquisa-cascata
pergunta_principal: "<pergunta de fundo que destrava a spec>"
rodadas: <1 ou 2>
data: <YYYY-MM-DD>
status: rascunho | revisado | fechado
---

# Research Brief — <Tópico>

> Template do output obrigatório do sub-modo `pesquisa-cascata` (G1 / ADR-007).
> Clonar este diretório (`docs/specs/_template-research/`) para
> `docs/specs/<nome-do-tema>/` e preencher.

## 1. Pergunta principal

<Pergunta de fundo a responder. Concreta o suficiente para guiar a busca.>

## 1.5 Escopo declarado pelo discovery (ADR-010 — obrigatório quando há sinal de contexto especializado)

> Lote temático do passo 6 do `discovery/SKILL.md`. **Modo A (Transcribe-mode determinístico):** se briefing tem declaração nominal explícita + sustentada em ≥2 lugares + stakeholder nomeado + sem contradição → transcrever do briefing (citar trechos). **Modo B (Interview-mode, default):** preencher abaixo via elicitação com dono.

### (a) Regulado?
Este projeto opera sob alguma norma/convenção externa? Quais especificamente? Vigência?
- `[CONFIRMADO|INFERIDO|DESCONHECIDO]` <norma 1> — <vigência> · fonte: <doc/dono>
- ...
- **Origem da declaração:** [via briefing — citar trecho] | [via interview com dono]

### (b) Alto-risco?
Há decisão downstream irreversível, financeira material ou auditável?
- Sim/Não + justificativa: <...>

### (c) Regras com semântica?
Há regra de negócio onde o "como" importa tanto quanto o "quê" (anti-fraude, audit trail, fairness, etc.)?
- Sim/Não + lista concreta: <...>

### (d) Gaps não-bloqueantes?
Dimensões/dados sabidos ausentes mas não impedem entrega?
- <gap 1> · impacto se não tratado: <...> · decisão dono: manter gap / tratar follow-up
- ...

**Gates downstream disparados:**
- (a) afirmativo com norma → `high-stakes-gate` + reforço sênior (`metodo-senior.md`)
- (b) afirmativo → `high-stakes-gate` + roteamento reflexivo (`04-confidence-routing`)
- (c) afirmativo → reforço sênior
- Sem afirmativos → defaults agnósticos.

## 2. Decomposição (3-5 sub-perguntas multi-hop)

1. <sub-pergunta 1>
2. <sub-pergunta 2>
3. <sub-pergunta 3>
4. <sub-pergunta 4 — opcional>
5. <sub-pergunta 5 — opcional>

## 3. Fontes consultadas

| Fonte | Tipo | Autoridade | Relevância | Acessada via |
|---|---|---|---|---|
| <link/path> | doc oficial / paper / blog / repo | alta / média / baixa | direta / lateral | explorer |
| ... | | | | |

## 4. Achados classificados

### CONFIRMADO (alta confiança, fonte direta)
- <achado 1> — Fonte: <ref §X>
- ...

### INFERIDO (cruzamento de fontes ou raciocínio sólido sem prova direta)
- <achado 2> — Base: <fontes cruzadas + lógica>
- ...

### DESCONHECIDO (lacuna explícita)
- <lacuna 1> — Sugestão de validação: <onde/como obter>
- ...

## 5. Gaps críticos (bloqueiam decisão de spec)

- <gap 1>: <impacto> · <plano de mitigação ou validação>
- ...

## 6. Ataque anti-raso (R3 do intake — obrigatório)

Persona read-only ataca os achados antes do fechamento. Registrar perguntas-ataque e respostas:

| Pergunta adversarial | Resposta / Mitigação |
|---|---|
| Há lacuna não declarada? | <sim/não — qual> |
| Viés de confirmação? | <fonte oposta consultada?> |
| Fonte fraca? | <robustez/alternativa> |
| Alternativa rejeitada sem registro? | <qual + razão> |
| ... | ... |

## 7. Antecipações (sênior — ADR-009)

Coisas pertinentes que o dono **não pediu** mas podem morder (premissas frágeis, riscos não-óbvios, alternativas não-avaliadas, vieses do recorte). **Seção obrigatória** quando o reforço transversal sênior está ativo (companion `metodo-senior.md`).

- <antecipação 1>: <por que importa>
- ...

### 7.1 Gaps não-bloqueantes (sênior — ADR-010 §sub-princípio i)

Gaps detectados que NÃO bloqueiam entrega mas existem (cobertura parcial de fonte, dimensão sem dados mas dispensável, etc.). **Silenciar gap não-bloqueante = perda de assertividade sênior.** Apresentar explicitamente:

| Gap | Impacto se não tratado | Decisão registrada do dono |
|---|---|---|
| <descrição do gap> | <consequência prevista> | manter gap / tratar follow-up |
| ... | | |

## 8. Backlog de elicitação (sênior — ADR-009)

Fatos pertinentes **não-documentados** que precisam vir do dono — não calar gaps. **Seção obrigatória** quando o reforço transversal sênior está ativo.

| # | Pergunta | Por que importa | Forma da resposta |
|---|---|---|---|
| Q1 | <pergunta> | <impacto> | <formato esperado> |
| ... | | | |

## 9. Recomendação ao orquestrador

Escolher UMA:

- **Continuar para spec via `discovery` (método universal)** — pergunta principal respondida; `requirements.md` é o próximo artefato.
- **Enviar direto ao `architect`** — achados são suficientes para decisão arquitetural; ADR é o próximo artefato.
- **Mais elicitação** — pergunta principal não foi respondida (gaps críticos restantes); rodar nova rodada de pesquisa-cascata (até N=2) ou voltar ao usuário.

## 10. Metadados

- **Rodadas executadas:** <1 ou 2 — limite hard do passo 5 do algoritmo>
- **Falhas do explorer:** <sub-perguntas que retornaram vazio + tratamento>
- **Tempo de elaboração:** <opcional>
- **Próximo papel:** <discovery | architect>
