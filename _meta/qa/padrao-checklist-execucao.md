# QA-evidence — padrao-checklist-execucao

- **Data:** 2026-10-29
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** —
- **Metodo-senior:** —

## Substitui vereditos anteriores deste bloco

- rodada 1 · 2026-10-29 · **aprovar_com_ressalvas** · sha `5fe68d6b40b4` · agentId `ae671a1ef29fd962c`
  - cobria 4 caminho(s): _shared/output-format/SKILL.md, .claude/global/CLAUDE-global.md, PROMPT-CHAT-WEB-v4.5.md, CHANGELOG.md

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| baixo | _shared/output-format/SKILL.md | lacunas do molde: Substituido sem apagar linha, nome do print, erros em aberto, colunas do Historico |
| baixo | PROMPT-CHAT-WEB-v4.5.md | linha longa e sem alternativa a arquivo no chat |
| baixo | _shared/output-format/SKILL.md | item 10 com justificativa no lugar de regra |

## Verificacoes executadas (anti-fabricacao)

- Parte C x molde v2 lido do xlsx e do gerador
- agnosticismo (isolamento entre empresas)
- ponteiros regra global e prompt web
- conflito com Partes A e B
- CHANGELOG x diff
- canarios escrita e web PASS (autor)
