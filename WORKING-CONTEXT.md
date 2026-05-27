# WORKING-CONTEXT — Sessão noturna 2026-05-27

> **PROPÓSITO**: artefato de recovery para qualquer retomada (mesma sessão, outra
> sessão, outro PC). Atualizado a cada checkpoint atômico via commit + push.
> Quem ler isso primeiro: **siga o §"Próximo passo concreto"**.

## Estado em 2026-05-27 (última atualização: ver `git log -1`)

- **Branch ativa:** `feat/framework-optimization-v180`
- **Modo de execução:** `autosuficiente` (defaultMode=bypassPermissions) — commit/push/merge sem prompts; deny só guard-rails absolutos (push --force, mkfs, Format-Volume).
- **State file:** `~/.claude/framework-mode.json` (history: avancado→autosuficiente em 2026-05-27, motivo HOOK_CHANGED).
- **Mantenedor:** dormindo; quer acordar com trabalho mergeado online + pendências documentadas.

## O que JÁ está mergeado em `main`

- **v1.7.1** (commit `99cf801`, PR #7): `sync-global.ps1` espelha-se como `~/.claude/hooks/framework-sync.ps1` — fecha gap de execução do ADR-005. Modo `avancado` foi ativado primeiro; `autosuficiente` foi escalada via ratchet (HOOK_CHANGED).
- Branches locais limpas (apenas `main` e a branch de trabalho atual).

## O que está EM PROGRESSO nesta branch

1. **Intake do plano de otimização** (commit `1ab6ee8`): `docs/_intake/2026-05-27-plano-otimizacao-framework.md` — documento colado pelo mantenedor; régua §0 (GANHO LÍQUIDO), 9 anti-padrões, G1 (pesquisa-cascata) como único gap real.
2. **ADR-006 untracked** (`docs/adr/006-auto-boot-global-squad-allowlist-owners.md`): auto-boot global + allowlist; status `Proposto (revisto pós-v1.7.1)`; qa-critic round 1 incorporou 4 ressalvas (C5, C6, C8, adversarial extra). **APROVADO pelo mantenedor para implementação** ("o que aprovamos para adr06, sem inflar, sem piorar").

## Próximo passo concreto (quem retomar: comece aqui)

```
1. cd f:/metacognition-framework
2. git status  # verificar branch atual
3. git log --oneline -5  # ver último checkpoint
4. Verificar este WORKING-CONTEXT.md (HEAD == último estado real)
5. Continuar conforme "Roadmap noturno" abaixo a partir do primeiro item NÃO marcado
```

## Roadmap noturno (ordem serializada — uma branch por vez)

### FASE A: ADR-006 (auto-boot global + allowlist) — esta branch

- [x] Intake do plano salvo
- [x] WORKING-CONTEXT criado (este arquivo)
- [ ] **Architect aceita ADR-006**: muda status `Proposto` → `Aceito`; `git add` do arquivo.
- [ ] **Developer implementa v1.8.0** (6 arquivos, escopo enxuto pós-v1.7.1):
  - [ ] `.claude/hooks/inject-start-session-global.template.ps1` (NOVO; fonte versionada)
  - [ ] Estender `.claude/hooks/sync-global.ps1` (+1 cópia: template → instância global)
  - [ ] Estender `bootstrap.ps1` passo 7 (cria `squad-owners.txt`, merge `hooks.SessionStart` em `~/.claude/settings.json`, primeira rodada do sync)
  - [ ] Estender `bootstrap.sh` paridade
  - [ ] `CHANGELOG.md` bloco v1.8.0
  - [ ] `CLAUDE.md` + `AGENTS.md` nota curta "Auto-boot global"
- [ ] **qa-critic adversarial em subagente isolado, rounds até APROVADO LIMPO** (sem ressalvas — instrução explícita do mantenedor).
- [ ] **DocOps** (CHANGELOG fechado, ADR-006 status Aceito).
- [ ] **Commit final + push + PR + merge** (autosuficiente).

### FASE B: ADR-007 (Régua §0 + G1 pesquisa-cascata) — branch separada

- [ ] Voltar para `main`, `git pull --ff-only`.
- [ ] Criar branch `feat/regra-ganho-liquido-discovery-cascata-v190`.
- [ ] Architect: escrever ADR-007 baseado no intake do plano (régua §0 + G1 + ex-G9 + ex-G11).
- [ ] qa-critic rounds até LIMPO.
- [ ] Developer: implementar mudanças mínimas (1 linha §6 AGENT-FRAMEWORK + companion + template + edições cirúrgicas).
- [ ] DocOps + PR + merge.

### FASE C: Documentar backlog (gap futuro)

- [ ] `docs/_backlog/gaps-otimizacao.md` listando: G2 (multi-spec + worktree), G3 (gate analyze), G4 (EARS obrigatório), G5/G7 (regulado), G6 (--quick), G10 (Harness Fit), R2/R4/R5. **Descartados:** G8 (memória auto-evolutiva), R4 (Scorer-Critic-Commander).

### FASE D: Sumário final em main

- [ ] Sumário "Trabalho noturno 2026-05-27" no `WORKING-CONTEXT.md` (este arquivo) com links para os PRs mergeados e backlog.
- [ ] Last push para origin.

## Regras invioláveis (aplicam a TUDO nesta sessão)

1. **Régua §0 (GANHO LÍQUIDO)**: nenhuma adição sem que (a) funda/remova ≥ adiciona, (b) reduza tokens/latência, ou (c) destrave eval. Princípio do intake.
2. **qa-critic adversarial em subagente isolado** após CADA mudança. Rounds até **LIMPO** (não APROVADO_COM_RESSALVAS — APROVADO sem ressalvas, como o mantenedor pediu).
3. **MELHORADOS, não inflados**: heurística persistida em `~/.claude/projects/.../memory/feedback_melhoria_nao_inflamento.md`. Comentários: só WHY não-óbvio.
4. **File-first**: ler antes de editar.
5. **Anti-rename**: nomes aprovados não mudam sem ADR.
6. **Persistência atômica**: cada artefato terminado → commit + push imediato. Sem ficar grande commit no fim.
7. **Anti-alucinação**: se não sei, NÃO SEI direto. Não fabricar.

## Pendências / decisões em aberto que precisam do mantenedor acordado

- (a) **ADR-006 aceito sob princípio "redundância benigna"** com hook project-level (será removido em follow-up ADR-007/008). Pela régua §0 ESTRITA, isso é inflamento; aceito por trade-off de migração. Confirmar quando acordar.
- (b) **`gugastork` na UI do GitHub** (sessão anterior) — investigação pendente. Provável cache do GitHub.
- (c) **ADR-006 numeração**: o intake (§4) propunha `005-discovery-pesquisa-cascata.md`, mas ADR-005 = "Modos de execução" já existe. Documento foi escrito pré-v1.7.0. Renumerado para **ADR-007** no roadmap.
- (d) **`feat/discovery-pesquisa-cascata-v170` (intake §7)** = nossa branch `feat/regra-ganho-liquido-discovery-cascata-v190` (renomeada para refletir realidade).

## Como retomar de outro PC

```powershell
# 1. Clone (se ainda não tem)
gh repo clone fabriciopsouza/metacognition-framework
cd metacognition-framework

# 2. Pull último estado (este arquivo é atualizado a cada checkpoint)
git pull --ff-only

# 3. Checkout branch ativa (ver §"Branch ativa" no topo)
git checkout feat/framework-optimization-v180  # ou main se já mergeou

# 4. Ler este WORKING-CONTEXT (em "Próximo passo concreto")

# 5. Verificar estado do modo (deve ser autosuficiente)
Get-Content ~/.claude/framework-mode.json
```

## Quem leu este arquivo agora? (assinatura por Claude operador)

- **Última leitura/escrita por:** Claude Opus 4.7 (1M context) na sessão "retome adr005 → noturno 2026-05-27"
- **Próxima IA/dev que abrir:** atualize seu nome aqui e siga "Próximo passo concreto".
