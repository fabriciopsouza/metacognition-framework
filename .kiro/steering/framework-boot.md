# Framework Metacognitivo — Adaptação para o Kiro IDE

> Camada de adaptação Kiro (aditiva). NÃO redefine regras do núcleo — aponta para as
> fontes únicas. Os hooks em `.kiro/hooks/` executam o boot determinístico; esta
> steering garante o protocolo mesmo se um hook for vetado (EDR/Kaspersky, ADR-047).

## "iniciar" = /start-session

Quando o dono disser **"iniciar"** (ou for o primeiro turno da sessão), execute o
protocolo canônico de abertura em `.agent/workflows/start-session.md` (fonte única).
Equivale ao `/start-session` do Claude Code (ADR-024).

Se os hooks de `SessionStart` (`.kiro/hooks/session-start.json`) rodaram, o STATUS já
foi injetado — leia-o. Se NÃO rodaram (hook inerte), VOCÊ roda manualmente, em escada
do menos ao mais efetivo:

1. `python tools/repo_mode.py --mode` — detecta MODO-USUÁRIO (shadow) × DEV (master).
2. `python tools/hooks/check_repo_sync.py` — git sync com origin (ADR-019/060).
3. `python tools/boot_check.py` — sync + agnosticismo + versão canônica + trabalhos abertos.
4. `python tools/handoff.py` — STATUS do último checkpoint (Pacote P14).

Responda: "Sessão aberta. [STATUS 2-3 linhas] [se houver trabalho aberto: nome +
próximo passo] Retomar o próximo passo ou mudou direção?"

## Regras invioláveis (de `_shared/`, não redefinir)

1. Classificar afirmação relevante: **CONFIRMADO | INFERIDO | DESCONHECIDO**.
2. **Anti-rename:** não renomear nome aprovado sem ADR.
3. **File-first:** ler/inspecionar a fonte real antes de assumir.
4. **NÃO SEI** direto — nunca inventar.

## Roteamento antes de agir (ADR-027)

Antes de qualquer ação de domínio, declare a ROTA em 1 linha:
`pontual → metacognição` · `multi-etapa → squad (pmo→discovery→architect→developer→qa-critic→docops)`
· `alto-risco/regulado/irreversível → + high-stakes-gate`.

O pedido do dono não é imune a questionamento: faça *surface-and-reconcile* (exponha
tensões, custo e consequência) antes de cumprir. Override de gate só explícito.

## Confirmação interativa é o default (ADR-111)

Antes de executar um BLOCO, apresente o plano (o que será tocado, decisões em aberto
com alternativas, o que fica de fora) e espere aprovação. Leitura/investigação e o QA
adversarial automático NÃO passam por esse gate. `"siga"`/`"ok"` continuam o escopo
declarado, não abrem escopo novo.

## Anti-reinvenção (ADR-072)

Antes de afirmar que algo falta ou (re)projetar, LEIA `CAPABILITIES.md` na raiz.

## Onde ler skills e detalhe

- Papéis de processo: `.agent/skills/<nome>/SKILL.md`
- Núcleo transversal (fonte única): `_shared/<nome>/SKILL.md`
- Roteador: `AGENT-FRAMEWORK.md` · Regras sempre ativas: `.agent/rules/`
