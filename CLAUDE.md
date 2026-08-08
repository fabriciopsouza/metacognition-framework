# CLAUDE.md — Entrada do Framework no Claude Code

> Claude Code lê este arquivo nativamente. É o ponto de entrada — versão Claude Code do
> AGENTS.md (cross-tool). **Dieta ADR-080:** aqui vive só a REGRA OPERACIONAL; motivação,
> história e detalhe vivem na ADR/skill apontada (fonte única — não recopiar).

## Estrutura
- Roteador: `AGENT-FRAMEWORK.md` (v2.3) — decide o modo (contexto × complexidade).
- Núcleo SSoT: `_shared/` — regras transversais (fonte única; nunca duplicar).
- Papéis de processo (skills): `.agent/skills/` — pmo, discovery, architect, developer,
  qa-critic, docops, explorer, _template. Subagentes reais: `.claude/agents/`.
- Regras sempre ativas: `.agent/rules/` · Workflows: `.agent/workflows/`.
- Aplicações de domínio vivem FORA do núcleo (clonar `.agent/skills/_template`); ver `exemplos/README.md`.

## Primeira ação obrigatória em toda sessão
/start-session **(ou diga "iniciar")** — abre pelo PMO (rules + briefing + history; ADR-024).
Por projeto preencha só `docs/briefing.md` + `.agent/rules/00-glossario.md`.

## Regras invioláveis (de _shared/, não redefinir)
1. Classificar afirmação relevante: CONFIRMADO | INFERIDO | DESCONHECIDO.
2. Anti-rename: não renomear nome aprovado sem ADR.
3. File-first: ler/inspecionar antes de assumir.
4. NÃO SEI direto — nunca inventar.

## Operação (regras ativas + ponteiro do detalhe)
- **Rota antes de agir (ADR-027):** declarar em 1 linha — pontual→metacognição ·
  multi-etapa→squad (pmo→discovery→architect→developer→qa-critic→docops) ·
  alto-risco/regulado→ +`high-stakes-gate`. O pedido do dono não é imune a questionamento:
  surface-and-reconcile com custo/consequência; override de gate só explícito (ADR-051).
  Output-style governa TOM, nunca o processo (ADR-028).
- **Modos de execução (ADR-005):** default · avançado · autosuficiente, ratchet forward-only
  em `~/.claude/framework-mode.json`. Detalhe: `_shared/execution-modes/SKILL.md`.
- **Gates portáteis + causa VERIFICADA (ADR-101):** o wiring é gerado de `tools/gates-manifest.json`
  para o projeto **e para o global** (`python tools/wire_gates.py --check|--install-global`) — é o que
  faz os gates existirem em QUALQUER repo, não só neste. Gate que não rodou → **diagnostique**
  (`--check`), nunca presuma veto de EDR: a premissa é medida (`boot_check.py --init-env`, ADR-093/094).
  Só com veto CONFIRMADO vale o modo non-admin (ADR-047): anunciar, declarar e aplicar inline cada
  gate. Detalhe: `guia/MODO-NON-ADMIN.md`.
- **Encerramento é gate, não intenção (ADR-101):** o hook `Stop` (`closing_gate.py`) mede o estado
  real e **bloqueia parada incompleta** — commit/push/PR pendente, correlato não atualizado, raiz
  poluída, sem checkpoint. Pedido explícito do dono se confirma na hora e se **termina**; parar no
  fim não é opção. Libera com `.claude/.closing.ack` declarando o porquê.
- **Correlato é obrigatório (ADR-101):** `.agent/correlations.json` declara o que muda junto;
  `python tools/correlated.py --check` reprova "atualizou metade do par". Tem que ser tudo.
- **Auto-boot global (ADR-006):** squad acorda quando owner do `origin` bate com
  `~/.claude/squad-owners.txt`. Pular: `.claude/session.lock` (projeto) ou `~/.claude/session.lock`.
- **Régua §0 — GANHO LÍQUIDO (ADR-007, princípio 10):** adição pura é rejeitada; só passa se
  (a) funde/remove ≥ adiciona, (b) reduz tokens/latência, ou (c) destrava eval editando existente.
- **Discovery declara o escopo (ADR-010, princípio 12):** núcleo agnóstico, sem norma hardcoded.
  Lote obrigatório ao dono: (a) regulado/normas? (b) alto-impacto? (c) regra com semântica?
  (d) gaps não-bloqueantes (flagar, não silenciar)? (e) alimenta outra sessão? (f) product_type
  → `mission.md`. Sem declaração → defaults agnósticos; anti-vazamento cross-projeto.
  Fonte canônica citada → carregar `metodo-senior.md` (9 passos + RRC; ADR-009/010).
- **Handoff cross-sessão (ADR-012/053, princípio 14):** declarado em 6(e) → Pacote P14
  obrigatório via J5; teste binário: a próxima sessão/humano começa sem perguntar nada?
  Gerador determinístico: `python tools/handoff.py` (ADR-076) + modelo sugerido por
  `tools/model-policy.json` (ADR-078).
- **QA bicelular (ADR-011/045, princípio 13):** junções J0–J6 com gate binário (`/handoff`
  workflow); DENTRO: itera até PASS · ENTRE: forward-only; process-critic (qa-critic subagente
  isolado, modelo ≠ autor — escada ADR-078) fecha todo BLOCO com poder de rewind; TODO QA é
  adversarial; SUPLANTA×EMENDA por seção do ADR. **Cada PASS deixa rastro:**
  `python tools/qa_evidence.py --junction J_n ...` (ledger, ADR-077).
- **Runtime gates (ADR-021/022/027/029/030/077):** compaction-gate · mission-gate · route-gate ·
  doc-intake (`tools/doc_intake.py`) · consistency (version-claim/override/raiz-limpa em
  `tools/test_consistency_closing.py`) · qa-evidence/posture fail-closed por release (ADR-074) ·
  env-applicability (ADR-093 — boot cruza `.agent/environment.json` × realidade viva: APLICA/ESTALE/AUSENTE).

## Índice de capacidades — anti-reinvenção (ADR-072/073)
**Antes de afirmar que algo falta ou (re)projetar, LEIA [`CAPABILITIES.md`](CAPABILITIES.md)**
(drill-down: `python tools/build_capabilities.py --show <id>`). Feature nova → +1 registro em
`capabilities.json`; canário barra órfão. Write-isolation: cada repo escreve só em si (ADR-070).
Doc-sync: ADR Aceito deve estar no CHANGELOG (fail-closed).

## Como ler skills
**Lar único:** `.agent/skills/<nome>/SKILL.md` (processo) e `_shared/<nome>/SKILL.md` (núcleo) —
procure AQUI se uma skill "sumiu"; carregue o SKILL.md relevante antes de agir. `.claude/skills/`
é espelho OPCIONAL de auto-trigger (não duplicar por cópia — régua §0); ver `guia/SETUP.md`.

## Roteador base
https://raw.githubusercontent.com/fabriciopsouza/metacognition-framework/main/AGENT-FRAMEWORK.md
