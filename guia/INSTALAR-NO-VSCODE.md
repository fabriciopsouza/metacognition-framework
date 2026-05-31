# INSTALAR NO VS CODE — Passo a Passo Único

> Leia uma vez, execute na ordem. Ao final, o VS Code estará rodando SÓ este
> framework, sem resíduo de agentes/frameworks antigos.

## ANTES DE COMEÇAR — qual pasta e qual zip

- **O zip certo:** `framework-metacognitivo-v1.4.0.zip` — o que tem **54 arquivos**.
  Confirmação: ao abrir, tem `CLAUDE.md`, `AGENTS.md`, `AGENT-FRAMEWORK.md`,
  `PROMPT-CHAT-WEB-v4.3.md` e as pastas `.claude/` e `guia/` (esta contém o `SETUP.md`)
  na raiz. Ignore/apague qualquer outro zip ou .md solto baixado antes.
- **A pasta:** vamos chamá-la de PASTA-FRAMEWORK. Sugestão de caminho limpo:
  `F:\Frameworks\metacognitivo-v1.4.0\`  (ou a que você já tem em Downloads).

---

## PASSO 1 — Preparar a PASTA-FRAMEWORK (só o que temos aqui)

1. Crie uma pasta nova e vazia (ex.: `F:\Frameworks\metacognitivo-v1.4.0`).
2. Extraia o `framework-metacognitivo-v1.4.0.zip` (54 arquivos) DENTRO dela.
3. Confira que a raiz tem: `CLAUDE.md`, `AGENTS.md`, `AGENT-FRAMEWORK.md`, `README.md`,
   `PROMPT-CHAT-WEB-v4.3.md`, e as pastas `_shared/`, `.agent/`, `.claude/`, `docs/`,
   `_meta/`, `exemplos/`, `guia/` (o `SETUP.md` vive em `guia/SETUP.md`).

Pronto — esta pasta contém SOMENTE o nosso framework. Nada antigo entrou.

---

## PASSO 2 — Remover/neutralizar o framework ANTIGO

> Objetivo: o Claude Code não pode achar duas configs concorrentes.
> NÃO apague trabalho — só a "fiação" antiga (configs de agente/regra).

No seu projeto/pasta ANTIGA (não nesta nova), procure e trate:

| Se encontrar… | O que é | Ação |
|---|---|---|
| `.agent/` (antigo) | squad antigo | renomear: `.agent` → `.agent_BACKUP` |
| `.claude/` (antigo) | config Claude Code antiga | renomear: `.claude` → `.claude_BACKUP` |
| `CLAUDE.md` (antigo) | contexto antigo | renomear: `CLAUDE.md` → `CLAUDE_BACKUP.md` |
| `.cursorrules`, `.windsurfrules`, `.clinerules` | regras de outras IDEs | renomear p/ `*_BACKUP` |
| `AGENTS.md` (antigo) | entrada cross-tool antiga | renomear p/ `AGENTS_BACKUP.md` |

Regra de ouro: renomeie para `_BACKUP` em vez de apagar. Se algo quebrar, você
volta. Depois de confirmar que o novo funciona, pode excluir os `_BACKUP`.

> Se o "antigo" estava em OUTRA pasta de projeto e você não vai usá-la agora,
> simplesmente NÃO a abra no VS Code. Só isso já a mantém fora do caminho.

---

## PASSO 3 — Abrir no VS Code

1. VS Code → **File → Open Folder** → selecione a PASTA-FRAMEWORK do Passo 1.
2. O Claude Code lê o `CLAUDE.md` da raiz automaticamente.
3. (Confirmação visual) No explorador do VS Code você deve ver `.claude/` e `CLAUDE.md`.

---

## PASSO 4 — Primeira sessão

No painel do Claude Code, digite:
```
/start-session
```
O PMO vai abrir a sessão. Se ele avisar que `docs/briefing.md` ou
`.agent/rules/00-glossario.md` estão vazios, é o comportamento CORRETO — preencha-os
para o seu projeto antes de seguir.

---

## PASSO 5 (opcional) — Revisar OUTRO repositório

Sem mexer em nada:
1. **File → Add Folder to Workspace** → selecione o repo a revisar.
2. No Claude Code:
```
@explorer varra a pasta <nome-do-repo-adicionado>, mapeie os .py e extraia as
regras de negócio. Read-only, não altere nada. Devolva só o resumo classificado.
```
3. Para soltar depois: clique direito na pasta → Remove Folder from Workspace.

---

## PASSO 6 (opcional) — Auto-trigger total das skills

Por padrão, os subagentes (`.claude/agents/`) já funcionam. Para as SKILLS
dispararem sozinhas no Claude Code, espelhe-as na pasta nativa:
- Copie cada pasta de skill de `_shared/` e `.agent/skills/` para `.claude/skills/`.
- Mantenha `_shared/` como a verdade; edite só lá. (Detalhe em `.claude/skills/README.md`.)
Sem este passo o framework funciona igual — só não auto-dispara as skills.

---

## CHECKLIST FINAL
- [ ] PASTA-FRAMEWORK tem os 54 arquivos (CLAUDE.md + guia/SETUP.md + .claude/ presentes)
- [ ] Configs antigas renomeadas para *_BACKUP (ou pasta antiga não aberta)
- [ ] VS Code abriu a PASTA-FRAMEWORK
- [ ] `/start-session` respondeu
- [ ] (se for revisar) repo-alvo adicionado via Add Folder to Workspace

Dúvida de qual arquivo abrir? Sempre o `guia/SETUP.md`. Dúvida de qual zip? Sempre o de 54 arquivos.
