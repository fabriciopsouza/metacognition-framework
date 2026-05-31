# ADR 024 — `/start-session` como comando registrado (prosa→mecanismo)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono (feedback) + squad (architect)
- Onda: ergonomia (pós-v1.21.0) · Tipo: **EMENDA** (expõe workflow existente; não muda a lógica)
- Relaciona: `.agent/workflows/start-session.md` (SSoT do protocolo), `inject-start-session.ps1` (hook SessionStart), ADR-004/006.

## Contexto

O `CLAUDE.md`, `AGENTS.md` e os guias mandam rodar **`/start-session`** como primeira ação. Mas
`/start-session` **nunca foi um comando registrado** — é um *workflow* (`.agent/workflows/start-session.md`)
+ um *hook* que injeta o protocolo no boot. Resultado: **digitar `/start-session` não funciona**; o que
funciona é dizer **"iniciar"** (linguagem natural — o agente lê o `CLAUDE.md` e roda o protocolo).
**Feedback recorrente do dono:** *"/start-session nunca funcionou comigo; uso 'iniciar' (e funciona)."*
Doc que promete um comando inexistente é o oposto da honestidade do framework — prosa que não executa.

## Decisão (1 frase ativa)

Criar **`.claude/commands/start-session.md`** (comando de slash registrado, auto-descoberto pelo Claude Code)
que dispara o protocolo do `.agent/workflows/start-session.md` (fonte única — o comando **aponta**, não
duplica), mantendo **"iniciar"** como alternativa em linguagem natural — ambos disparam o mesmo protocolo.

## Alternativas consideradas (≥3)

1. **Status quo (prosa).** Prós: zero mudança. Contras: o comando dos docs **não funciona**; o dono tropeça nele toda vez. **Rejeitada — é o gap.**
2. **Trocar `/start-session` por "iniciar" em todos os docs.** Prós: simples. Contras: perde a ergonomia de um comando + "iniciar" é informal; e muitos docs/ADRs históricos citam `/start-session` (re-escrever história). **Rejeitada.**
3. **Registrar o comando (ESCOLHIDA).** Prós: os docs viram **verdade**, o comando passa a funcionar, e **"iniciar" continua valendo** (linguagem natural). Contras: +1 arquivo a manter coerente com o workflow — mitigado: o comando **referencia** o workflow SSoT, com resumo mínimo (não duplica a lógica; régua §0).

## Consequências

**Positivas:** `/start-session` funciona; docs honestos sem re-escrever história; "iniciar" preservado.
**Negativas:** um arquivo a mais que deve apontar para o workflow (não divergir).
**Riscos:** (a) divergência comando↔workflow — mitigada pela referência explícita ao SSoT. (b) coexistência com o hook de SessionStart — sem conflito: o hook é automático no boot, o comando é sob demanda.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/start-session-command` · `2026-05-31` · grep `commands/start-session`
- Artefatos: `.claude/commands/start-session.md` (aponta para o workflow); nota "(ou 'iniciar')" em `CLAUDE.md` e `AGENTS.md`. Workflow e hook inalterados.
