# QA-evidence — adr-116-regras-globais-do-dono

- **Data:** 2026-09-25T16:18:09Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** inline: causa MEDIDA antes de desenhar - qa-critic ja global em ~/.claude/agents, ~/.claude/CLAUDE.md inexistente; a ordem do dono so vivia no CLAUDE.md do repo
- **RRC:** PASSA
- **Metodo-senior:** N/A: bloco de mecanismo do proprio framework, sem fonte canonica externa

## Substitui vereditos anteriores deste bloco

- rodada 5 · 2026-09-25T16:16:18Z · **aprovar_com_ressalvas** · sha `262e605799b9` · agentId `ab7689ff9656c4b9e`
  - cobria 13 caminho(s): .claude/global/CLAUDE-global.md, .claude/hooks/sync-global.ps1, CAPABILITIES.md, CHANGELOG.md …
- rodada 5 · 2026-09-25T16:17:23Z · **aprovar_com_ressalvas** · sha `262e605799b9` · agentId `ab7689ff9656c4b9e`
  - cobria 13 caminho(s): .claude/global/CLAUDE-global.md, .claude/hooks/sync-global.ps1, CAPABILITIES.md, CHANGELOG.md …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | bootstrap.py instalar_regras_globais | rodada 4: escrita em arquivo somente-leitura levantava PermissionError e abortava o bootstrap sem PowerShell; agora devolve falha-escrita, codigo 3 |
| MEDIA | tools/check_rules_parity.py GLOBAL_CALLERS / GLOBAL_INSTALLER_PY_CALL | rodada 4: a chamada escrita dentro de string (Write-Host/print) enganava o canario; regex ancoradas no inicio do comando |
| BAIXA | bootstrap.py + ADR-116 + CHANGELOG | rodada 4: quebra mista nao era preservada como o texto dizia; implementado estilo dominante e texto corrigido |
| BAIXA | tools/check_rules_parity.py | rodada 5, nota de manutencao: chamada Python em coluna 0 nao seria detectada; refatorar o PS para nao capturar a saida daria falso alarme (direcao segura). Registrado no ADR-116. Aceito como nota de manutencao: nao ha chamada em coluna 0 no codigo, e o falso alarme bloqueia em vez de deixar passar. |
| MEDIA | processo da revisao | rodada 5: a revisora violou a regra de so-leitura na worktree; o autor conferiu por hash que nao houve alteracao de conteudo |

## Verificacoes executadas (anti-fabricacao)

- python tools/test_rules_parity.py -> PASS (revisora, 2x) e autor
- python tools/check_rules_parity.py -> PASS; com a chamada do sync-global comentada -> FAIL/drift (revisora)
- python tools/test_capabilities.py -> PASS, 101 capacidades, 61 com mutacao
- USERPROFILE/HOME temporario, CLAUDE.md chmod 0444 -> falha-escrita, exit 3, sem traceback (revisora)
- USERPROFILE/HOME temporario, CLAUDE.md com quebra mista -> instalado, 43 CRLF, 0 LF avulso (revisora)
- 16 variacoes de regex contra GLOBAL_INSTALLER_PY_CALL e GLOBAL_CALLERS, incluindo linhas reais extraidas do repo -> sem falso negativo na direcao que importa (revisora)
- sabotagem do autor: except OSError -> ZeroDivisionError faz o teste de somente-leitura falhar; estilo dominante desligado faz o teste de quebra mista falhar; restaurado e verde (autor)
- post-violacao: hash sem CR de original, worktree e indice identicos nos 5 arquivos (autor)
