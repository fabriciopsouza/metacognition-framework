# Validation — v1.19.0 Sync de repo no boot (ADR-019) — gate binário

| # | Critério | Como verificar | V/F |
|---|---|---|---|
| V1 | `tools/test_repo_sync.py` exit 0 (ou SKIP sem git/pwsh) | rodar | — |
| V2 | Canary prova AUTO-PULL quando seguro (clean+ff) — clone fica behind=0 | V1 (C1) | — |
| V3 | Canary prova AVISO sem tocar quando há modificação rastreada (clone segue behind>0) | V1 (C2) | — |
| V4 | Em dia (behind=0) → hook silencioso (additionalContext vazio) | V1 (C3) | — |
| V5 | Hook NUNCA faz pull não-ff / merge / rebase — canary C4 prova ramo divergiu (não-ff) avisa, não pula | V1 (C4) | — |
| V5b | Untracked NÃO bloqueia auto-pull — canary C5 prova auto-update + untracked preservado | V1 (C5) | — |
| V5c | Sucesso do auto-pull ramificado pelo exit code do pull (não só por behind recalculado) | leitura `$pullRc`/`rc` | — |
| V6 | Falha soft: não-repo / offline / erro → exit 0, nunca bloqueia | leitura (try/catch + exit 0) | — |
| V7 | `.claude/settings.json` é JSON válido e registra check-repo-sync no SessionStart antes do inject | parse + leitura | — |
| V8 | `sync-global.ps1` espelha check-repo-sync.ps1 para ~/.claude/hooks/ | grep | — |
| V9 | `start-session.md` passo 1 manda git fetch + ahead/behind ANTES de reconciliar (superfície chat) | leitura | — |
| V10 | ADR-019 declara honestamente: detecta sempre, corrige só quando seguro; registro global = follow-up [DESCONHECIDO] | leitura | — |
| V11 | Régua §0: 1 hook de propósito único + canary + edições; nenhum papel/subsistema novo | PC | — |
| V12 | (regressão) Contrato de skill 7/7 PASS | `python tools/validate_skills.py` | — |
