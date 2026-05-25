# ADR 001 — Ocultar o molde de subagente da lista /agents

- Status: Aceito
- Data: 2026-05-24 · Decisores: Fabricio (mantenedor)

## Contexto
`.claude/agents/_template.md` é um MOLDE para criar subagentes, não um subagente
operável. Por ter extensão `.md` válida na pasta `.claude/agents/`, o Claude Code o
lista em `/agents` como um agente ativável (aparece como `<nome-do-subagente>`),
poluindo a lista e podendo ser invocado por engano. A auto-auditoria do explorer já
havia sinalizado a inconsistência `name: _template-application` × pasta `_template`.

## Decisão (1 frase ativa)
Renomear `.claude/agents/_template.md` para `.claude/agents/_template.md.txt` para que
o Claude Code não o registre como subagente, preservando-o como molde de referência.

## Alternativas consideradas
1. **Renomear para `.md.txt` (escolhida).** Prós: some da lista `/agents`; conteúdo
   permanece versionado e legível; reversível. Contra: extensão dupla é incomum;
   exige este ADR pela regra anti-rename.
2. **Mover o molde para fora de `.claude/agents/`** (ex.: `docs/templates/`). Prós:
   semântica mais limpa. Contra: quebra a vizinhança com os agentes reais que ele
   modela; mais caminhos para manter sincronizados.
3. **Não fazer nada.** Prós: zero esforço. Contra: mantém o ruído na lista `/agents`
   e o risco de invocação acidental — o problema que motivou a decisão.

## Consequências
- Positivas: lista `/agents` limpa (só agentes reais); molde preservado e versionado.
- Negativas: quem procurar `_template.md` precisa saber que virou `.md.txt`.
- Riscos: a instalação GLOBAL (`~/.claude/agents/`) é cópia separada — aplicar a
  mesma renomeação lá para manter paridade, senão a global ainda lista o molde.

## Implementação (commit hash após aceito)
<preencher com o hash do commit que aplica a renomeação>
