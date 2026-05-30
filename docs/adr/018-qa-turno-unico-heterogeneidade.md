# ADR 018 — QA adversarial de turno único (steelman→ataque→veredito) + heterogeneidade de modelo

- Status: Aceito
- Data: 2026-05-30 · Decisores: dono (briefing v1.14.x) + squad (autônomo)
- Onda: 4 (QA afiado) · Pesquisa: **P6** · Tipo: **EMENDA** (Princípio 13)
- Relaciona: `.agent/skills/qa-critic/SKILL.md`, `_meta/subagent-isolation.md`, ADR-011 (QA bicelular).

## Contexto

A comparação JARVIS sugeriu um "Conclave" de 3 papéis (gerador/defensor/sintetizador). **P6 reprova
a estrutura de 3 papéis** com 3 blocos de evidência convergentes:
- A alavanca causal do adversarial **não é o número de papéis** — é (a) crítico **externo** ao gerador
  e (b) **heterogeneidade de modelo**. O framework já tem (a) via process-critic isolado (ADR-011).
- Multi-agent debate **não supera** self-consistency com compute equiparado (Zhang et al. 2025).
- Conclave **homogêneo** (mesmo modelo, 3 personas) cai em "reforço de viés" ("When Debate Fails", 2025);
  no regulado, 3 papéis aumentam superfície de auditoria sem entregar a independência que GAMP/ALCOA pedem.

O que o Conclave teria de útil é capturável **a custo ~zero**, dentro do qa-critic que já existe:
internalizar **steelman → ataque → veredito** num único turno, e **priorizar heterogeneidade de
modelo** gerador↔crítico (a melhoria que de fato paga). Há ainda o **Self-Critique Paradox** (Snorkel
2025): forçar crítica onde o modelo já acerta **derruba acurácia 15–40%** — logo, QA reforçado é
**condicional**, não sempre.

**Régua §0:** EMENDA — não cria papel nem subagente novo; densifica o protocolo do qa-critic existente
(+1 seção) e torna explícita a heterogeneidade que `_meta/subagent-isolation.md` já tateava. Rejeita o
Conclave (3 papéis) por ônus da prova não cumprido. **Esta é a auto-aplicação:** a própria série
v1.14.x usou qa-critic isolado + `model: sonnet` (heterogêneo ao Opus gerador) e pegou false-PASS real.

## Decisão (1 frase ativa)

Internalizar no `qa-critic` existente o protocolo de **1 turno — steelman → ataque → veredito** (sem
instanciar defensor/sintetizador), **priorizar heterogeneidade de modelo** gerador↔crítico, e disparar
o QA reforçado **condicionalmente** (ambíguo/alto-impacto/regulado — silenciar em rotina de alta confiança).

### Protocolo de turno único (dentro do qa-critic, não papéis novos)
1. **STEELMAN** (obrigatório, mesmo turno): reconstruir a versão mais forte do trabalho + declarar o
   que está demonstravelmente correto. Calibra severidade, evita nitpicking. Custo ~0.
2. **ATAQUE** adversarial: hipótese default = existe bug. Erro de agregação, edge case, premissa não
   confirmada, alucinação de campo/sintaxe, false-PASS (gate que não enforça o que declara).
3. **VEREDITO** binário (aprovar/não-aprovar), **herdando o vocabulário da modalidade ativa** (J4 →
   `APROVADO_LIMPO`/itera; PC → `APROVADO_LIMPO`/`REPROVADO_REWIND J_i` — ADR-011), citando o que
   sobrevive ao ataque e o que precisa de gate humano. **Não inventa um terceiro termo.**

> **Reconciliação com "TODO QA é adversarial" (ADR-011):** o disparo condicional silencia o QA
> **reforçado**, nunca o **básico** (bug-default + validation.md), que é sempre aplicado. Usar "disparo
> condicional" para dispensar QA legítimo é abuso da regra (codificado na skill).

### Heterogeneidade de modelo (a alavanca que paga — Zhang 2025 Heter-MAD)
- O qa-critic roda em **família de modelo diferente** do developer/gerador, quando o ambiente permite
  (`Agent(... model: <distinto>)`). Priorizar isso **sobre** qualquer estrutura de debate.
- No chat (sem troca de modelo), o protocolo de 1 turno vale igual; a heterogeneidade fica indisponível
  e isso é **declarado**, não fingido (mesma honestidade ide↔chat das ondas 1–2).

### Disparo condicional (Self-Critique Paradox — Snorkel 2025)
- **Rotina/alta confiança/determinístico:** validação técnica padrão; **NÃO** forçar QA pesado (forçar
  derruba acurácia 15–40%).
- **Ambíguo / alto-impacto / irreversível / regulado:** QA reforçado (steelman→ataque→veredito) +,
  no irreversível/regulado, gate humano antes do "final".

## Alternativas consideradas
1. **Conclave de 3 papéis (sugestão JARVIS).** Prós: parece mais robusto. Contras: homogêneo reforça
   viés; MAD não supera self-consistency; 3× tokens (viola P8); +superfície de auditoria sem
   independência real. **Rejeitada** (P6 §1–2).
2. **Manter qa-critic como está (status quo).** Prós: zero mudança. Contras: não captura steelman
   (calibração de severidade) nem fixa heterogeneidade como prioridade; QA pesado sempre-ligado cai no
   Self-Critique Paradox. Rejeitada — perde ganho de custo ~zero.
3. **1 turno steelman→ataque→veredito + heterogeneidade + disparo condicional (ESCOLHIDA).** Prós:
   captura o útil do Conclave a custo ~zero; alavanca causal correta; respeita P8 e o paradoxo.
   Contras: heterogeneidade depende do ambiente (declarado).

## Consequências
**Positivas:** severidade calibrada (menos nitpick/falso-positivo); heterogeneidade priorizada onde
mais paga; QA caro só quando vale. **Negativas:** qa-critic SKILL +1 seção (densificação, não papel novo).
**Riscos:** (a) heterogeneidade indisponível no chat **[DESCONHECIDO]** quanto a impacto — declarado.
(b) Par gerador↔crítico ótimo (famílias) **[DESCONHECIDO]** — "a calibrar" (P6 §8); default = qualquer
família distinta da do gerador. (c) Aceitação regulatória de "subagente heterogêneo = revisor
independente" **[DESCONHECIDO]** — dedução, não confirmada por auditor.

## Implementação (ponteiro após aceito)
- Ponteiro: branch `feat/v1.18.0-qa-turno-unico` · `2026-05-30` · grep `steelman|heterogeneidade|Self-Critique|turno único`
- Artefatos: +seção em `.agent/skills/qa-critic/SKILL.md` (protocolo 1 turno + heterogeneidade + disparo
  condicional); nota em `_meta/subagent-isolation.md` (heterogeneidade gerador↔crítico).
- Lit: Zhang et al. 2025 (arXiv 2502.08788 Heter-MAD); "When Debate Fails" 2025 (arXiv 2503.16814);
  Huang et al. 2023 (2310.01798); Kamoi et al. 2024 TACL; Snorkel 2025 (Self-Critique Paradox); CriticGPT (McAleese).
