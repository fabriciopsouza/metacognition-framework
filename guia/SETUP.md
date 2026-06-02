# SETUP.md — Comece Aqui

> Ponto de entrada. Não duplica os outros guias — aponta para eles.
> Ferramenta-alvo: **Claude Code no VS Code**.

## Os 3 modos de uso

### Modo 1 — Projeto novo (greenfield)
Começar do zero com o framework.
1. Use esta pasta do framework como raiz do projeto novo.
2. Preencha `docs/briefing.md` (objetivo, escopo, critério de aceite) e
   `.agent/rules/00-glossario.md` (3–5 termos iniciais).
3. No Claude Code: `/start-session`.

### Modo 2 — Revisar repo externo (read-only, no lugar)
Entender/analisar outro projeto sem trazer nada.
→ Ver **COMO-REVISAR-OUTRO-REPO.md** (nesta pasta guia/) (multi-root workspace + subagente explorer).
Resumo: abra o framework, *Add Folder to Workspace* → repo-alvo, e delegue ao explorer.

### Modo 3 — Migrar trabalho antigo para a nova estrutura
Trazer o trabalho (código, regras, docs) e **deixar a fiação antiga para trás**.

> REGRA-MÃE: **traz o trabalho, não traz a fiação.**
> Código/regras/dados/notas vêm. `.agent/`, `.claude/`, `.cursorrules`,
> `CLAUDE.md` antigos NÃO vêm — o framework que vale é este.

Passos:
1. **Backup do antigo** (preservação): `mv .agent .agent_BACKUP` no projeto velho.
2. **Trazer só o trabalho** para uma subpasta deste framework, ex.: `trabalho/<repo>/`
   (os `.py`, dados, docs — não as pastas de agente/regra antigas).
3. **Mapear antes de adotar:** delegue ao `explorer` varrer `trabalho/<repo>/` e
   extrair as regras de negócio (read-only). Use o resultado para preencher o
   `briefing.md` e o `00-glossario.md` deste framework.
4. **Registrar nomes** no glossário (anti-rename passa a valer a partir daqui).
5. `/start-session` e seguir o fluxo normal.

---

## Configurar o Claude Code (VS Code) — onde cada peça mora

Locais NATIVOS do Claude Code (verificado na doc oficial):

| Peça | Local nativo | Neste framework |
|---|---|---|
| Contexto sempre-ativo | `CLAUDE.md` (raiz) | ✅ já incluído |
| Skills (lar único) | `.agent/skills/<nome>/SKILL.md` + `_shared/` | **é onde vivem e são editadas — procure aqui**; `.claude/skills/` é espelho OPCIONAL só p/ auto-trigger |
| Subagentes (isolamento real) | `.claude/agents/<nome>.md` | ✅ explorer, qa-critic + _template |
| Hooks (auditoria/enforcement) | settings do Claude Code | ver `_shared/observability` |

Dois caminhos:
- **Quick:** abra a pasta no VS Code. O Claude Code lê `CLAUDE.md`, que aponta para
  `_shared/` e `.agent/skills/`. As skills são lidas quando instruídas. Subagentes
  em `.claude/agents/` já funcionam (explorer, qa-critic).
- **Native (opcional — só auto-trigger):** as skills **funcionam no Quick** (lidas sob demanda).
  Se quiser que elas **auto-disparem**, espelhe as pastas em `.claude/skills/` — preferir **symlink**
  a cópia (cópia duplica e arrisca divergir da fonte; ver `.claude/skills/README.md`). **Não é
  pré-requisito** para o framework operar; `.agent/skills/` segue sendo a verdade. Subagentes já estão nativos.

> Importante (doc oficial): ao usar `--add-dir`, o `.claude/skills/` da pasta
> adicionada é auto-carregado, mas subagentes/comandos `.claude/` NÃO são lidos de
> pastas adicionadas — só da raiz. Por isso os subagentes ficam na raiz do framework.

---

## Ciclo de vida — ativar · migrar · iniciar · finalizar

**Ativar uma skill/subagente**
- Skill: invocada como `/<nome>` ou o Claude carrega quando a `description` casa.
- Subagente: o Claude delega automaticamente pela `description`, ou você chama
  explícito com `@<nome>` (ex.: `@explorer`).

**Migrar (do antigo)**
- Modo 3 acima. Sempre backup antes. Traz trabalho, não fiação.
- Subagente não herda skills → liste em `skills:` na config do subagente.

**Iniciar (sessão)**
- `/start-session` — sempre o primeiro comando. O PMO lê tudo e abre o estado.

**Finalizar (bloco/sessão)**
- `/checkpoint` — grava o estado em `history.md` (compaction + note-taking).
- DocOps fecha o bloco (CHANGELOG + glossário + ADR). Nada fecha sem isso.
- Para soltar um repo-alvo do Modo 2: remova a pasta do workspace. Zero resíduo.

---

## Criar skills e subagentes novos (templates)
- **Skill / aplicação de domínio:** clone `.agent/skills/_template/` → preencha só o
  domínio (referencie `_shared/`). É assim que o AIVI nasceu.
- **Subagente:** clone `.claude/agents/_template.md.txt` (renomeie para `.md` no
  destino) → defina `tools` (menor privilégio), `model` (diferente do principal) e
  `skills` (liste explicitamente). O molde fica como `.md.txt` para não aparecer
  na lista `/agents` (ver `docs/adr/001-ocultar-template-agente.md`).
- **Antes de produção:** escreva o eval-set (`_meta/eval-template.md`), 8–12
  should-trigger + 8–10 should-NOT, e rode (ver `_meta/eval-results-papeis.md`).

## Mapa de documentos
- `SETUP.md` (este) — comece aqui.
- `README.md` — arquitetura e princípios.
- `GUIA-EQUIPE.md` — uso diário, 5 min.
- `COMO-REVISAR-OUTRO-REPO.md` (em guia/) — Modo 2.
- `CHANGELOG.md` — proveniência (mudança → fonte).
