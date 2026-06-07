# PLANO — Completar a infra cross-IA + gate de evidência de processo (2026-06-06)

> Estado: tooling determinístico **pronto e testado** (ver `CAPABILITIES.md` tags `cross-ai`).
> O que falta é **provisionamento + enforcement server-side** — exige o dono (gh ausente nesta
> máquina; SSH ok). Princípio: a trava física honesta vive **no remoto** (branch protection),
> não no cliente local (vetável por EDR). Eu **nunca** escrevo no `metacognition-gemini`.

## Já entregue (fail-closed/ci-ready/physical, nesta máquina)
- `cross_ai_gate.py` — anti-loop, 10 testes (terminação garantida). `enforcement: ci-ready`.
- `repo_identity.py` — identidade ancestry-first (+ fix SSH↔HTTPS). `advisory`.
- `equivalence_gate.py` — equivalência por capacidade + hitl_proof. `ci-ready`.
- `cross_ai_hub.py` — scan/manifest/deposit (scan zero-dep no boot). `manual`.
- `export-clean.py` — carimbo `role=shadow` (trava física). `physical`.
- Índice (`capabilities.json`/`build_capabilities.py`) emite o **manifest de equivalência** cross-IA.

## Ações do DONO (server-side — destravam o enforcement real)

### 1. Provisionar o hub privado (1×)
- Criar repo **privado** `fabriciopsouza/metacognition-hub` (vazio).
- Estrutura inicial: `inbox/`, `archive/`, `INDEX.md`. (O `cross_ai_hub.py deposit` cria os date-shards.)
- Clonar localmente; apontar o tooling com `--hub <path>` (ou definir caminho padrão).
- **CI do hub:** workflow que roda `python tools/cross_ai_hub.py gate <repo>` (= `cross_ai_gate`) em
  cada PR → **required check** (merge barrado se anti-loop falhar). É o enforcement do anti-loop.

### 2. Branch protection (a "trava física" honesta — server-side, não-bypassável local)
- Em **`metacognition-framework`** (main) e no **hub**: exigir PR + required status checks
  (`run_canaries` + `cross_ai_gate` no hub) + ≥1 review. Bloqueia push direto e merge sem gate verde.
- **CODEOWNERS por `ai_owner`** (opcional) — reforça quem revisa.

### 3. Deploy keys escopadas por repo (isolamento de credencial = físico)
- Chave que pode push em `metacognition-framework` **não** pode push em `metacognition-gemini` e
  vice-versa. (O CI de publish já usa deploy key por alvo — estender ao fluxo cross-IA.)
- Reforço local já aplicado: `settings.local.json` **deny** em `*metacognition-gemini*`.

### 4. Wirar os gates como required checks na CI (fail-closed)
- `.github/workflows/ci.yml` já roda `run_canaries` (inclui `test_capabilities`, `test_cross_ai_*`,
  `test_equivalence_gate`). Marcar como **required** na branch protection.
- Adicionar step `equivalence_gate` com `git verify-commit` do `hitl_proof` (pendência ADR-071).

## Status (2026-06-07 — fechado via API, token PAT pontual do dono)
Feito por `api.github.com` (sem `gh`; token `repo` lido de `.env` gitignored, não impresso, a revogar):
- ✅ **GitHub Releases** v1.46.0 / v1.47.0 / v1.48.0 (corpo do CHANGELOG; a vitrine linka os `.zip`).
- ✅ **Hub privado** `metacognition-hub` criado (auto_init) + estrutura `inbox/` + `archive/` + README (ADR-069).
- ✅ **Branch protection** em `main`: require PR + required checks (`canários (ubuntu/macos/windows-latest)`) + sem force-push/deleção. **`enforce_admins=false`** (escape do owner até validarmos 1 ciclo de PR verde; depois flipar p/ `true` = "nunca commit direto" pleno).
- ⏳ **Pendente:** wirar a **CI do hub** (`cross_ai_gate` como required check — precisa copiar o tooling p/ o hub) + `equivalence_gate --git verify-commit`. Deploy keys do publish já funcionam (premium remote avançou no último push).

## Próxima conversão prosa→mecanismo (candidato a ADR — priorizado pelo débito)
**Process-evidence gate** — ratchet do `consistency-gate` (hoje `fail-soft`, ADR-030) → **fail-closed
na CI** no subconjunto: PR de bloco exige (a) veredito de qa-critic, (b) checkpoint no `history.md`,
(c) status de ADR coerente. Mecaniza "TODO QA é adversarial" + "forward-only após PASS" (ADR-011),
hoje doutrina. Razão: 2ª ocorrência confirmada do padrão "gate fail-soft não disparou no fechamento"
(2026-06-02 e 2026-06-06). Cerne [[feedback-prosa-vira-mecanismo]].

## Teste binário de pronto
Outra sessão (claude OU gemini) abre, roda `cross_ai_hub.py scan <hub> --me <id>`, vê os handoffs
abertos **sem perguntar nada**, critica via qa-critic, responde por PR no próprio repo — e nenhuma IA
escreve no repo da outra. Quando isso roda fim-a-fim com o hub provisionado + branch protection = pronto.
