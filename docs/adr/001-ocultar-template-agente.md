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
- Commit: `9a74f66f93563be2c9183a74db41d34d30d39098` (branch `feat/discovery-v150`).
- Nota histórica: o hash original deste commit (`c8bb35c4…`) foi reescrito porque o commit saiu com autor placeholder (`seu-email@exemplo.com`, herdado do `.gitconfig` global pré-existente). Após detectado, o git config foi corrigido para o email real do mantenedor e a branch passou por `git rebase HEAD~2 --exec "git commit --amend --reset-author"` (autoria refeita; conteúdo idêntico). Este ADR registra o hash pós-correção. Lição: validar `git config user.email` antes do primeiro commit em sessões assistidas.
- Aplicação: rename detectado pelo git como `R .claude/agents/_template.md -> .claude/agents/_template.md.txt` (100% similaridade — histórico preservado). Sweep de referência órfã aplicado em `guia/SETUP.md` no mesmo commit.
- Verificação adversarial: qa-critic (subagente isolado) rodou dois rounds; ambos confirmaram que `.claude/agents/_template.md.txt` está presente, `.claude/agents/_template.md` removido, e a regra anti-rename foi respeitada via este ADR.
- Pendência aberta — RESOLVIDA neste mesmo PR via auto-sync: o risco "instalação GLOBAL é cópia separada" agora tem owner = hook `SessionStart` em `.claude/settings.json` (script `.claude/hooks/sync-global.ps1`). A cada início de sessão no projeto do framework, o hook espelha `_shared/`, `.agent/skills/` e `.claude/agents/*.md` (NÃO `*.md.txt`) para `~/.claude/skills/` e `~/.claude/agents/`. Isso elimina a divergência manual entre a fonte versionada (repo) e a instância executável (global). O molde `_template.md.txt` fica EXCLUÍDO do sync por design — a mesma proteção que motivou este ADR vale também para o global.
