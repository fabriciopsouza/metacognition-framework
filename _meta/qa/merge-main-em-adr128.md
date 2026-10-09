# QA-evidence — merge-main-em-adr128

- **Data:** 2026-10-09T02:48:35Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** merge de sincronizacao, sem decisao nova
- **RRC:** PASSA
- **Metodo-senior:** diff cached contra cada pai, contagem de ids do capabilities nos 3 estados, conteudo do arquivo de hashes e regra de export

## Substitui vereditos anteriores deste bloco

- rodada 1 · None · **aprovar** · sha `None` · agentId `a8222c4cc15e6fe14`
  - cobria 23 caminho(s): .agent/skills/docops/SKILL.md, .agent/workflows/start-session.md, .claude/global/CLAUDE-global.md, .claude/hooks/sync-global.ps1 …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| BAIXA | CHANGELOG.md | Data 28/09 do ADR-128 vs commit 29/09; ordem nao cronologica no CHANGELOG; cosmetico |

## Verificacoes executadas (anti-fabricacao)

- git diff --cached origin/main == git show 24e5f4f
- git diff --cached HEAD == git diff HEAD...origin/main
- CHANGELOG sem marcas, 3 entradas
- capabilities ids 114 nos 3
- export-clean STRIP_BEFORE docs/_private
- run_canaries 98 PASS 1 SKIP 0 FAIL (autor)
