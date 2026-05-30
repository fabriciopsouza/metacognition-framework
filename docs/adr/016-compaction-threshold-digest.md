# ADR 016 — Compaction por threshold medido + digest persistente

- Status: Aceito
- Data: 2026-05-30 · Decisores: dono (briefing v1.14.x) + squad (autônomo)
- Onda: 2 (contexto medido) · Pesquisa: **P2** · Tipo: **EMENDA** (Princípio 8, liga ao 14)
- Relaciona: `AGENT-FRAMEWORK.md §2.5`, `.agent/workflows/checkpoint.md`, ADR-012 (handoff cross-sessão).

## Contexto

Hoje o §2.5 dispara compaction por gatilho **qualitativo**: "ao fim de bloco ou quando a sessão
alonga". P2 mostra por que é frágil: a degradação por contexto longo ("context rot", Chroma, 18
modelos incl. Claude 4) é um **gradiente contínuo, não um penhasco** — não há "limite" óbvio para se
aproximar. Resultado: compactar tarde (já degradado) ou cedo (perde contexto) por falta de medida.

P2 recomenda **faixas de ocupação com ações nomeadas**, disparando **cedo** (cedo > tarde). Os
percentuais são **parâmetro [INFERIDO]**: a *forma* (faixas) e a *direção* (cedo) são [CONFIRMADO];
os cortes específicos não são constantes provadas.

**Régua §0:** EMENDA — não cria subsistema. Substitui prosa qualitativa por faixas medidas no §2.5
(alavanca 1) e estende o `checkpoint.md`. O digest **é** o Pacote de handoff (ADR-012/Princípio 14)
com carimbo de faixa — funde dois artefatos, não adiciona um.

## Decisão (1 frase ativa)

Disparar compaction por **faixas de ocupação medida** (🟢<50% / 🟡50–69% / 🟠70–84% / 🔴≥85% —
defaults [INFERIDO] ajustáveis, fronteira inclusiva à esquerda), com **proxy chars÷3 no chat**
(PT-BR técnico, alarme de fumaça), produzindo um **digest persistente** que é o **Pacote de handoff
(§P14) estendido** com campos de compaction + carimbo de faixa (superset, não artefato paralelo).

### Faixas (% do espaço útil = janela nominal − custos fixos de tools/MCP; fronteira inclusiva à esquerda)
| Faixa | Estado | Ação |
|---|---|---|
| < 50% | 🟢 verde | operação normal |
| 50–69% | 🟡 note-taking | gravar decisões/nomenclaturas em artefato persistente (`history.md`/digest) |
| 70–84% | 🟠 digest+handoff | produzir o digest + avisar handoff iminente |
| ≥ 85% | 🔴 compactar | reiniciar janela a partir do digest + 5 arquivos mais recentes |

> Fronteiras sem sobreposição (inclusiva à esquerda): 70% cai em 🟠, 85% cai em 🔴 — sem ambiguidade.

> **Honestidade sobre os números (Princípio 11):** P2 recomenda *faixas crescentes disparando cedo*
> — forma e direção [CONFIRMADO]. Os cortes **50/70/85 são escolha de engenharia nossa, não-calibrada**
> (P2 não prova esses valores vs. 60/75/90) — [INFERIDO], ajustáveis por observação.

### Medida por ambiente (mesma regra, mecanismo diferente)
- **IDE/SDK:** % real (`/context` / status line / `input+cache+output` na API).
- **Chat web (sem tokenizer):** proxy `chars ÷ 3` (PT-BR + técnico; `÷4` do inglês subestima). P2 dá
  ÷3–÷3,5; **adotamos ÷3 como default conservador** (superestima tokens → compacta um pouco mais
  cedo, lado seguro). Erro ±20–40% → alarme de fumaça, não medida exata. Sem o denominador real no
  chat, a faixa % é estimativa grosseira — tratar como alarme por **volume**. [INFERIDO]

### Conteúdo do digest (= §Pacote de handoff ESTENDIDO — superset, não paralelo)
O digest inclui os **5 campos canônicos** do §Pacote (`_shared/metacognition-core`): artefato
consumível+versão · localização repo/commit/PR · acesso/visibilidade · **prompt pronto-para-colar** ·
pendências+premissas. **Extensões de compaction** somam: decisões+fonte+confiança · detalhes caros
(nomes EXATOS) · nomenclatura · ponteiros JIT · 5 arquivos recentes · **carimbo** (versão+timestamp+
faixa + **modo de execução**, para a próxima sessão retomar no regime certo). Template:
`docs/specs/_template-digest/digest.md`. Teste binário (herda ADR-012): a outra sessão começa
**sem perguntar nada de volta**?

## Alternativas consideradas
1. **Manter gatilho qualitativo (status quo).** Prós: zero mudança. Contras: compacta cedo/tarde por
   falta de medida; degradação é gradiente sem "limite" visível. Rejeitada — é o problema (P2 §1).
2. **Compaction nativa do Claude Code só (auto-compact ~85%).** Prós: existe, server-side. Contras:
   só no IDE; não ensina o método ao chat; não garante o conteúdo do digest. Usada como mecanismo no
   IDE, complementada pela política de faixas + digest. Rejeitada como *única* solução.
3. **Faixas medidas + proxy no chat + digest = §Pacote estendido (ESCOLHIDA).** Prós: agnóstico de
   ambiente, cedo>tarde, digest auditável que funde handoff. Contras: percentuais [INFERIDO] (ajustáveis).

## Consequências
**Positivas:** dispara na hora certa (cedo, medido); digest reduz re-leitura pós-reset; funde
continuidade técnica + trilha de auditoria + handoff num só artefato.
**Negativas:** percentuais/divisor não calibrados empiricamente (declarado).
**Riscos:** (a) ÷3 e cortes 50/70/85 **[DESCONHECIDO]** — micro-benchmark validaria (P2 §9); defaults
conservadores. (b) "Espaço útil" no chat sem denominador real → estimativa grosseira (declarado).
(c) Encaixe formal do digest em ALCOA+ **[DESCONHECIDO]** — não-bloqueante fora de GxP.

## Implementação (ponteiro após aceito)
- Ponteiro: branch `feat/v1.16.0-compaction-digest` · `2026-05-30` · grep `faixa|threshold|digest|chars`
- Artefatos: edição `AGENT-FRAMEWORK.md §2.5` (alavanca 1), extensão `.agent/workflows/checkpoint.md`,
  template `docs/specs/_template-digest/digest.md`.
- Lit: Chroma context rot; Anthropic context editing (+39% memory+editing; −84% tokens em 100-turn web).
