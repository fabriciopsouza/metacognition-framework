# Backlog — Gaps e otimizações futuras (FASE C do trabalho noturno 2026-05-27)

> Itens adiados explicitamente do intake do plano de otimização (`docs/_intake/2026-05-27-plano-otimizacao-framework.md`) e dos rounds qa-critic da v1.8.0 e v1.9.0. Cada item registra: **descrição · origem · gatilho de reativação · status atual**.
>
> Política de uso: NÃO implementar daqui sem antes (a) ter dado real de uso justificando a necessidade, OU (b) ter eval do bloco vigente pago. Régua §0 (ADR-007) aplica a cada candidato.

---

## Adversariais arquiteturais aceitos como gap (não correção; mitigação por convenção)

### A1. Race condition no `history.md` (humano vs orquestrador)
- **Origem:** qa-critic round 1 ADR-007 + qa-critic código round 1 v1.9.0 (adversarial).
- **Descrição:** o firewall declara single-writer = orquestrador (PMO), append-only, mas é **convenção textual**. Se o mantenedor edita manualmente o `history.md` por outro PC enquanto o orquestrador faz append em paralelo, há merge conflict não-gerenciado.
- **Mitigação atual:** convenção append-only com timestamp ISO por entrada; resolução via `git merge` padrão.
- **Gatilho para promover a fix técnico:** ≥2 conflitos reais observados em sessões multi-PC do mantenedor.
- **Status:** aceito como limitação conhecida.

### A2. Limite hard `N=2` no algoritmo pesquisa-cascata sem enforcement técnico
- **Origem:** qa-critic código round 1 v1.9.0 (adversarial).
- **Descrição:** o companion declara "LIMITE HARD: N=2 rodadas no máximo" mas é regra textual lida pelo agente. Um agente que não leia o companion completo pode exceder.
- **Mitigação atual:** filtro de entrada do passo 1 já rejeita carregamento indevido; ataque anti-raso obrigatório no passo 7 catalisa o fechamento.
- **Gatilho para promover a fix técnico:** caso real de loop excedendo 2 rodadas observado em campo.
- **Status:** aceito como limitação genérica de framework baseado em regras textuais (não é específico deste companion).

---

## Gaps do intake adiados (intake §3)

### G2. Orquestração multi-spec + Git Working Tree
- **Origem:** intake §3 ("adiar até necessidade comprovada + eval pago").
- **Descrição:** rodar múltiplas specs em paralelo via `git worktree`, cada uma em sub-pasta isolada.
- **Gatilho:** ≥3 specs concorrentes em um mesmo bloco de squad real (não hipotético).

### G3. Gate de análise (analyze) antes de implementar
- **Origem:** intake §3.
- **Descrição:** etapa formal de análise pós-spec e pré-implementação que valida coerência cross-arquivo.
- **Gatilho:** falha de integração entre módulos detectada pelo qa-critic ≥2× no mesmo bloco.

### G4. EARS obrigatório nas specs
- **Origem:** intake §3.
- **Descrição:** sintaxe EARS (Easy Approach to Requirements Syntax) como gate de cada requisito da spec.
- **Gatilho:** ambiguidade de requisito identificada pelo qa-critic ≥3× em specs de domínio.

### G5/G7. Regulado: Golden Datasets / OOS / freeze
- **Origem:** intake §3 ("adiar para bloco regulado").
- **Descrição:** datasets de referência imutáveis + out-of-sample tests + freeze de modelo/spec antes da produção.
- **Gatilho:** primeiro cliente farma/saúde/financeiro do framework (já anotado em `feedback_v170_template_regulado` na memória).

### G6. Flag `--quick` em comandos
- **Origem:** intake §3.
- **Descrição:** modo "rápido" que pula etapas custosas em tarefas pontuais reconhecidas.
- **Gatilho:** ≥3 vezes que o mantenedor pediu skip explícito de etapa em sessão pontual.

### G10. Model Harness Fit (guardrail)
- **Origem:** intake §3 ("adiar — 1 linha de guardrail").
- **Descrição:** verificar coerência entre o modelo escolhido e a complexidade da task antes de delegar.
- **Gatilho:** caso real onde modelo errado (sub/sobre-dimensionado) gerou retrabalho.

### R2/R4/R5. Revisões propostas pelo intake §2
- **R2:** Git Working Tree para isolamento (variante de G2).
- **R4:** Scorer-Critic-Commander — **DESCARTADO** pelo intake §3 (inflação; qa-critic já cobre).
- **R5:** Memory Flush + locking — **SIMPLIFICADO** pelo intake §3 (single-writer elimina o problema; já cobrado via ADR-007 ex-G9).

---

## Pendências documentais (não-bloqueantes)

### D1. Hook project-level project-side `inject-start-session.ps1` redundante com global
- **Origem:** ADR-006 §"Convivência com ADR-004" + qa-critic v1.8.0 C12.
- **Descrição:** após v1.8.0, hook project-level continua existindo como redundância benigna (`additionalContext` duplicado). Cleanup foi adiado para "ADR-007 candidato" — agora renomeado como **ADR-008 candidato**.
- **Gatilho:** v1.8.0 estável em ≥2 PCs (validado por commit/push de outras máquinas do mantenedor).
- **Status:** RESOLVIDO 2026-05-27 via guard em `inject-start-session.ps1` (commit `cd0bc3e`) — hook de projeto faz `exit 0` quando o global existe, preservando o caso pré-bootstrap. Gatilho antecipado por observação direta do mantenedor. NÃO virou ADR (fix trivial, §0); some assim da contenda "ADR-008 candidato" (que fica só com D2/check-execution-mode).

### D2. `check-execution-mode.ps1` permanece project-level (não promovido a global)
- **Origem:** ADR-006 §"Convivência com ADR-005".
- **Descrição:** o gate de modos do ADR-005 continua sendo hook do projeto-framework, não global. Por desenho: o gate reconfirma modo quando o **mecanismo de sync** muda, não quando o usuário abre projeto qualquer.
- **Gatilho:** caso onde o mantenedor abre projetos com mecanismos de sync independentes e precisa de reconfirmação cross-projeto.

### D3. Eval seções G/H/I em design-time
- **Origem:** intake §1.3, §6.
- **Descrição:** eval-set dos papéis está escrito mas não executado em runtime.
- **Gatilho:** intake §5.2 — "pagar a dívida de eval pendente antes de declarar qualquer bloco pronto". Próximo ciclo pago.

### D4. Cross-platform port dos hooks PowerShell
- **Origem:** ADR-001/004/005/006/007 — todos PowerShell-only.
- **Descrição:** porte `.sh` da cadeia de hooks + paridade Linux/macOS.
- **Gatilho:** mantenedor usando Linux/macOS regularmente (hoje só Windows).

---

## Princípio de uso deste backlog

1. Não promover item sem **gatilho disparado em campo** (não em hipótese).
2. Cada promoção exige **ADR próprio** + qa-critic adversarial.
3. Régua §0 aplica: o item promovido deve passar (a)(b)(c) — adição pura é rejeitada.
4. Items DESCARTADOS pelo intake (R4 acima) não são reabertos sem evidência nova contradizendo o motivo do descarte.

## Referências

- Intake: [`docs/_intake/2026-05-27-plano-otimizacao-framework.md`](../_intake/2026-05-27-plano-otimizacao-framework.md)
- ADR-006 §"Convivência com ADR-004" e §"Convivência com ADR-005"
- ADR-007 §"Pendências e follow-ups"
- WORKING-CONTEXT noturno: [`docs/_intake/WORKING-CONTEXT-2026-05-27.md`](../_intake/WORKING-CONTEXT-2026-05-27.md)
