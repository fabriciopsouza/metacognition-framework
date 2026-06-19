# Por onde começo? — Wayfinding do usuário (ADR-090)

> Guia **user-facing** que te direciona pelo framework — "que modo para a minha situação?".
> Complementa o popup de 1ª abertura (ADR-067). Fonte: `AGENT-FRAMEWORK.md` (roteador) + `CAPABILITIES.md` (o que existe).

## 1. Qual é a sua situação?

| Situação | Por onde começar |
|---|---|
| **Cheguei agora / pasta nova** | Diga **"iniciar"** (ou `/start-session`). O PMO abre, lê briefing/history e te orienta. Se não há `docs/briefing.md`, ele te diz o que preencher (2 arquivos: `briefing.md` + `.agent/rules/00-glossario.md`). |
| **Projeto NOVO (greenfield)** | "iniciar" → discovery faz elicitação do zero. Declare objetivo, escopo, critério de aceite, `product_type`. |
| **Projeto que JÁ EXISTE (brownfield)** | Workflow **`document-project`** (mapeia o existente) → depois discovery elicita só os gaps. Para contexto 1-shot: **`generate-project-context`**. |
| **Vou retomar / passar p/ outra sessão ou IA** | **`generate-project-context`** → 1 doc consumível. Ou `python tools/handoff.py` para o pacote de handoff. |
| **Tarefa pontual (1 arquivo, 1 dúvida)** | Pergunte direto — roteia para **metacognição** (sem cerimônia de squad). |
| **Feature/refactor multi-etapa** | Roteia para **squad** (pmo→discovery→architect→developer→qa-critic→docops). |
| **Aplicar a um domínio (BI, fiscal, dados…)** | Clonar `.agent/skills/_template` (ver `exemplos/README.md`). Domínio vive FORA do núcleo. |

## 2. Que MODO de execução? (ADR-005)
- **default** — confirmo entre blocos (mais controle).
- **avançado** — confirmo só o de alto impacto.
- **autosuficiente** — avanço e reporto (autonomia; mas elicitação de indicador regulado continua vinculante — ADR-089).
> HITL (parar e perguntar) é por modo: default/avançado param na 1ª fricção; autosuficiente auto-recupera dentro de um budget e escala por último (ADR-087).

## 3. O que o framework garante (e o que não)
- **Garante:** classificar o que sabe (CONFIRMADO/INFERIDO/DESCONHECIDO), não inventar, QA adversarial entre etapas, recusar inchar (régua §0), decisões em ADR.
- **Limites honestos:** ver `LIMITS.md` (cada capacidade com status derivado do canário que a prova). No chat web (sem filesystem) os gates viram checkpoints declarados — ver `PROMPT-CHAT-WEB-v4.5.md`.

## 4. Mapa rápido
- Roteador: `AGENT-FRAMEWORK.md` · Núcleo: `_shared/` · Papéis: `.agent/skills/` · Capacidades: `CAPABILITIES.md` · Decisões: `docs/adr/`.
