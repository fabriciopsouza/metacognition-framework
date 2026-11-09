# QA-evidence — adr-131-d2-empresa-sem-veto

- **Data:** 2026-11-09T11:39:37Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Substitui vereditos anteriores deste bloco

- rodada 1 · 2026-11-06T21:11:13Z · **aprovar_com_ressalvas** · sha `cd40e45d21f2` · agentId `a20672f948f7659b3`
  - cobria 6 caminho(s): .agent/skills/qa-critic/SKILL.md, CHANGELOG.md, capabilities.json, docs/adr/131-trabalhadores-externos-orquestrados.md …
- rodada 1 · 2026-11-06T21:11:35Z · **aprovar_com_ressalvas** · sha `cd40e45d21f2` · agentId `a20672f948f7659b3`
  - cobria 6 caminho(s): .agent/skills/qa-critic/SKILL.md, CHANGELOG.md, capabilities.json, docs/adr/131-trabalhadores-externos-orquestrados.md …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| BAIXA | docs/adr/131-trabalhadores-externos-orquestrados.md linhas 27 e 35 | veto escrito sem marca de revogado |
| BAIXA | __pycache__/ na raiz do worktree | nao rastreado; fora do commit por caminho explicito |
| BAIXA | docs/adr/131 emenda | fala de 25/10/2026 sem fonte conferida pelo revisor; citada em docs/DEBITOS.md do orquestrador-multi-ia |

## Verificacoes executadas (anti-fabricacao)

- python tools/test_trabalhador_externo.py: PASS
- python tools/test_audit_enforcement.py: 37/37
- python tools/test_capabilities.py: PASS
- tools/test_squad_gate.py: 85 PASS e 14 FAIL em copia sem .git, identico a base cd40e45
- sabotagens S1 a S5 em copia: todas reprovam
