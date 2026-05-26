# ADR 004 — Auto-boot do squad via SessionStart hook com flag de escape

- **Status:** Aceito (2026-05-26 — pelo mantenedor; aplicado em v1.6.1)
- **Data:** 2026-05-26 · **Decisores:** Fabricio (mantenedor) + Claude (papel `architect`)
- **Substitui:** nenhum · **Substituído por:** nenhum
- **Relaciona-se a:** ADR-001 (auto-sync hook existente em `.claude/settings.json`), ADR-002+ADR-003 (v1.6.0 feature de discovery)

## Contexto

O CLAUDE.md do projeto declara `/start-session` como **primeira ação obrigatória em toda sessão**. Hoje (pré-v1.6.1), isto depende de:
1. O usuário lembrar de digitar o comando.
2. O usuário ler o CLAUDE.md (ou já saber o ritual).

Esquecer o `/start-session` significa pular: leitura de `AGENTS.md`, `.agent/rules/*`, `briefing.md`, `history.md` (últimas 30) e produção de STATUS pelo PMO. Resultado: ações descontextualizadas. Discrepância arquitetural — o sync global, que é mecânico, está automatizado via SessionStart hook (ADR-001 / commit `40d6966`); o boot cognitivo do squad, que é igualmente "primeira ação obrigatória", depende de memória humana.

Usuário levantou: "preciso realmente dar o /start-session pra iniciar o squad? não dá pra automatizar?" — pergunta legítima de coerência.

## Decisão (1 frase ativa)

Adicionar um **2º hook SessionStart** (`inject-start-session.ps1`) que, em paralelo ao `sync-global.ps1` existente, **injeta no contexto inicial** da sessão a orientação de boot do squad — fazendo o Claude executar o PMO `/start-session` antes de qualquer outra ação. **Flag de escape:** se existir `.claude/session.lock` no projeto, o hook detecta e pula a injeção (sessão "rápida" sob controle manual do usuário).

## Alternativas consideradas

| # | Alternativa | Prós | Contras |
|---|---|---|---|
| 1 | **SessionStart hook condicional com flag de escape (escolhida — Opção C da elicitação)** | Default automatiza (zero memória humana). Lock file dá controle por sessão (debug, pergunta pontual). Custo de implementação baixo (~15 min). Reversível: deletar o hook ou o lock | Lock file é estado oculto — quem esquece o lock criado tem boot pulado indefinidamente. Mitigação: `.gitignore` impede vazamento, mas não impede esquecimento local |
| 2 | Automação total sem escape (Opção A) | Mais simples — ~10 min, um único caminho de execução | Sessões rápidas pagam overhead toda vez. Quem só quer ler 1 ADR é forçado a esperar o PMO ler briefing+history+rules |
| 3 | Hook que pré-executa o STATUS (Opção B) | Mais ambicioso — economiza turno do PMO porque entrega o STATUS pronto | Lógica do STATUS vive no hook PowerShell (script com 50+ linhas que precisa parsear briefing, ler ADRs aceitos, montar STATUS). Mais coisa que pode quebrar; difícil de manter |
| 4 | Manter manual (status quo) | Zero esforço; controle cognitivo do humano | Contradiz a declaração de "primeira ação obrigatória" do CLAUDE.md — depender de memória é frágil. Onboarding sofre |
| 5 | Slash command padrão configurada | Conceitualmente limpo | Claude Code não suporta "slash command default" nativamente — não há mecanismo |

## Justificativa

A escolha do mantenedor pela **Opção C** equilibra dois axiomas em tensão:

- **Coerência arquitetural** (o framework declara `/start-session` como obrigatório) — favorece automatização total (#2).
- **Respeito ao caso de uso "sessão rápida"** (debug, pergunta pontual, iteração em arquivo único) — favorece manter manual (#4).

A flag `.claude/session.lock` é o mecanismo de governança: existe lock = sessão sob controle manual; não existe = boot automático. O usuário decide por sessão sem editar settings.

A Opção B foi rejeitada por **complexidade desproporcional**: pré-executar STATUS no hook duplicaria a lógica do PMO em PowerShell, criando um caminho paralelo de manutenção. Melhor deixar o PMO (em PT-BR) fazer seu trabalho com contexto cognitivo do Claude.

## Implementação

### Arquivos criados/alterados na v1.6.1

| Arquivo | Mudança |
|---|---|
| `.claude/hooks/inject-start-session.ps1` | **NOVO** — script que injeta `additionalContext` com conteúdo de `.agent/workflows/start-session.md`. Se `.claude/session.lock` existe, retorna `additionalContext` vazio. Falha "soft" (exit 0 em qualquer erro) |
| `.claude/settings.json` | Adicionado 2º hook SessionStart referenciando o novo script, ordenado APÓS `sync-global.ps1` (sync acontece antes, boot cognitivo depois) |
| `.gitignore` | Adicionada linha `.claude/session.lock` (flag é pessoal por cópia de trabalho — não versionar) |
| `CHANGELOG.md` | Bloco v1.6.1 (PATCH) descreve o auto-boot |

### Como o usuário usa

- **Comportamento padrão** (lock ausente): toda nova sessão entra com PMO já ativado; Claude já responde o STATUS no 1º turno.
- **Pular o auto-boot** (debug, pergunta rápida):
  ```powershell
  New-Item .claude/session.lock -ItemType File -Force
  ```
  Sessões subsequentes pulam o auto-boot até o lock ser deletado.
- **Reativar:**
  ```powershell
  Remove-Item .claude/session.lock
  ```

## Consequências

### Positivas
1. **Coerência com declaração do CLAUDE.md** — `/start-session` deixa de ser "obrigatório no papel, opcional na prática".
2. **Onboarding melhorado:** quem clona o repo e abre sessão pela primeira vez já entra com squad ativo, sem precisar ler o CLAUDE.md primeiro.
3. **Flag de escape simples:** lock file é o mecanismo mais leve possível — sem editar settings, sem flag em linha de comando, sem variável de ambiente.
4. **Reversível:** deletar o hook do settings.json (ou o script) restaura o comportamento manual da v1.6.0 imediatamente.
5. **Paridade com o sync global:** ambos hooks rodam no mesmo SessionStart — sync mecânico + boot cognitivo, ambos automáticos por default.

### Negativas
1. **Lock file órfão:** se o usuário criar o lock e esquecer, todas as sessões futuras pulam o boot até ele perceber. Mitigação: `statusMessage` do hook mostra "delete .claude/session.lock se nao quiser" em toda sessão — visibilidade explícita.
2. **Outro hook para manter:** 2 hooks em vez de 1; quando um deles falhar (timeout, erro), o usuário tem que diagnosticar qual.
3. **Sessões rápidas com lock têm overhead de 1ms para verificar o lock:** irrelevante na prática.

### Riscos
1. **Hook silenciosamente sem efeito** (script renomeado, path quebrado, PowerShell bloqueado): boot não acontece e o usuário só percebe depois. Mitigação: falha "soft" com warning em stderr; teste manual via `powershell.exe -File .claude/hooks/inject-start-session.ps1` mostra o JSON.
2. **`additionalContext` muito grande:** se `start-session.md` crescer para muitas linhas, infla o system prompt de toda sessão. Hoje tem 13 linhas — folga grande. Vigiar.
3. **PowerShell exclusivo:** este framework só funciona no Windows hoje. Se for portar para Linux/macOS, precisará versão `.sh` análoga. Já existe paralelo no `sync-global.ps1` — risco compartilhado.

## Implementação (ponteiro após aceito)

- **Ponteiro:**
  - Branch: `feat/auto-start-session-v161` (a criar pelo developer)
  - Data: 2026-05-26 (aplicado na sessão da v1.6.0)
  - Grep para localizar implementação: `git log --all --grep "v1.6.1" --grep "auto-start-session"`
- **Hash de commit:** opcional como complemento — NUNCA único (lição ADR-001 / ADR-003).
- **Validação:**
  1. Default (sem lock): abrir nova sessão → Claude deve entrar com PMO ativo e produzir STATUS no 1º turno.
  2. Com lock (`New-Item .claude/session.lock`): abrir nova sessão → Claude entra sem instrução de PMO; comportamento livre.
  3. Deletar lock → comportamento default volta.

## Referências

- Script: [`.claude/hooks/inject-start-session.ps1`](../../.claude/hooks/inject-start-session.ps1)
- Workflow injetado: [`.agent/workflows/start-session.md`](../../.agent/workflows/start-session.md)
- Hook irmão (sync mecânico): [`.claude/hooks/sync-global.ps1`](../../.claude/hooks/sync-global.ps1)
- Settings: [`.claude/settings.json`](../../.claude/settings.json)
- CLAUDE.md (declaração "primeira ação obrigatória"): [`CLAUDE.md`](../../CLAUDE.md)
