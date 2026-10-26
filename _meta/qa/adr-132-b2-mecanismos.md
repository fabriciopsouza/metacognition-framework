# QA-evidence — adr-132-b2-mecanismos

- **Data:** 2026-10-26
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** —
- **Metodo-senior:** —

## Substitui vereditos anteriores deste bloco

- rodada 1 · 2026-10-26 · **aprovar** · sha `bb483e6ae9b0` · agentId `abeb28d3950e0b377`
  - cobria 14 caminho(s): .claude/global/CLAUDE-global.md, CAPABILITIES.md, CHANGELOG.md, capabilities.json …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| baixo | tools/risk_score.py | espacos residuais na linha de desconhecidos em faixa() |
| baixo | tools/risk_score.py | --help nao diz que --f0 exige --nenhum-gatilho |
| baixo | tools/varrer_irmaos.py | binario ignorado sem declarar o limite |
| baixo | tools/squad_gate.py | tokens/duracao_s nao declarados em CAMPOS_CONHECIDOS travavam o commit (achado pelo proprio gate) |
| baixo | tools/squad_gate.py | redesenho e override_dono ausentes de CAMPOS_CONHECIDOS (pre-existente) |
| baixo | tools/squad_gate.py | gate nao le atestacao.provas: achado em provas fica invisivel (pre-existente) |

## Verificacoes executadas (anti-fabricacao)

- faixa x regra global seção 1
- 132 JSON de _meta/qa no validador novo: 0 recusados
- varrer_irmaos: texto inexistente exit 0, repo invalido exit 2
- 5 canarios do bloco PASS
