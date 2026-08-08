# AGENTS.md — Framework Metacognitivo Agêntico

> Entrada cross-tool (Cursor/Windsurf/Cline/Aider/Codex…). Equivale ao `CLAUDE.md`.
> **Dieta ADR-080:** só REGRA OPERACIONAL aqui; motivação/história/detalhe na ADR/skill apontada.

Roteador: AGENT-FRAMEWORK.md (v2.3) · Núcleo SSoT: _shared/ ·
Papéis: .agent/skills/ (pmo · discovery · architect · developer · qa-critic · docops · explorer ·
_template) · Regras: .agent/rules/ · Workflows: .agent/workflows/.

## Regras sempre ativas
Ver .agent/rules/ (todas referenciam _shared/).

## Primeira ação obrigatória
/start-session (ou "iniciar") — abre pelo PMO (rules + briefing + history; ADR-024).

## Regras invioláveis (de _shared/, não redefinir)
1. Classificar afirmação relevante: CONFIRMADO | INFERIDO | DESCONHECIDO.
2. Anti-rename: não renomear nome aprovado sem ADR.
3. File-first: ler/inspecionar antes de assumir.
4. NÃO SEI direto — nunca inventar.

## Operação (regra ativa + ponteiro)
- **Rota antes de agir (ADR-027):** pontual→metacognição · multi-etapa→squad ·
  alto-risco/regulado→ +high-stakes-gate. Surface-and-reconcile antes de cumprir; override de
  gate só explícito com custo informado (ADR-051). Output-style ≠ processo (ADR-028).
- **Modos de execução (ADR-005):** default · avançado · autosuficiente (ratchet forward-only,
  `~/.claude/framework-mode.json`). Detalhe: `_shared/execution-modes/SKILL.md`.
- **Gates portáteis + causa VERIFICADA (ADR-101):** wiring gerado de `tools/gates-manifest.json`
  para o projeto **e o global** (`python tools/wire_gates.py --check|--install-global`) — é o que
  faz os gates existirem em qualquer repo, não só no repo-mãe. Gate que não rodou →
  **diagnostique**, nunca presuma veto de EDR (mede-se: `boot_check.py --init-env`, ADR-093/094).
  Só com veto CONFIRMADO vale o NON-ADMIN (ADR-047): anunciar, declarar e aplicar inline.
  Detalhe: `guia/MODO-NON-ADMIN.md`.
- **Encerramento é gate (ADR-101):** hook `Stop` (`closing_gate.py`) bloqueia parada incompleta —
  commit/push/PR, correlato, raiz poluída, checkpoint. Pedido explícito do dono se confirma na hora
  e se **termina**; parar no fim não é opção. Escape declarado: `.claude/.closing.ack`.
- **Correlato obrigatório (ADR-101):** `.agent/correlations.json` declara o que muda junto;
  `python tools/correlated.py --check` reprova meia-atualização. Tem que ser tudo.
- **Auto-boot global (ADR-006):** owner do `origin` em `~/.claude/squad-owners.txt` acorda o squad;
  pular via `.claude/session.lock`.
- **Régua §0 (ADR-007):** adição pura rejeitada — só (a) funde/remove ≥ adiciona, (b) reduz
  tokens/latência, (c) destrava eval editando existente.
- **Discovery declara o escopo (ADR-010):** lote ao dono — regulado? alto-impacto? semântica?
  gaps não-bloqueantes (flagar)? alimenta outra sessão? product_type→`mission.md`. Sem declaração →
  defaults agnósticos; anti-vazamento cross-projeto. Fonte canônica citada → `metodo-senior.md`
  (9 passos + RRC).
- **Handoff cross-sessão (ADR-012/053):** declarado → Pacote P14 obrigatório via J5 (teste binário:
  próxima sessão/humano começa sem perguntar?). Gerador: `python tools/handoff.py` (ADR-076) +
  modelo por `tools/model-policy.json` (ADR-078).
- **QA bicelular (ADR-011/045):** J0–J6 binárias forward-only; process-critic isolado (modelo ≠
  autor) fecha bloco com rewind; TODO QA adversarial; rastro por junção via
  `python tools/qa_evidence.py --junction J_n ...` (ADR-077).
- **Runtime gates:** compaction (ADR-021) · mission (ADR-022) · route (ADR-027) · doc-intake
  (ADR-029) · consistency/version-claim/raiz-limpa (ADR-030/077/079) · qa-evidence/posture (ADR-074)
  · **closing · correlated · boot-brief (ADR-101)**.

## Índice de capacidades
**Antes de afirmar que falta algo, LEIA `CAPABILITIES.md`** (ADR-072/073). Feature nova → registro
em `capabilities.json`. Write-isolation ADR-070.

## Aplicações
Domínios (BI, regulado, etc.) NÃO ficam no núcleo — clonar `.agent/skills/_template` e viver FORA.
Ver `exemplos/README.md`.

## Roteador base
https://raw.githubusercontent.com/fabriciopsouza/metacognition-framework/main/AGENT-FRAMEWORK.md
