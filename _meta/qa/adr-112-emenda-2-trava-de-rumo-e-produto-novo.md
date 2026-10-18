# QA-evidence — adr-112-emenda-2-trava-de-rumo-e-produto-novo

- **Data:** 2026-10-18T12:20:26Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Steelman
a checagem poderia reprovar projetos externos do dono; nenhum hook a chama fora deste repo

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| BAIXA | tools/plano.py:221 | atende: p1 minusculo reprovava com mensagem enganosa |
| BAIXA | tools/plano.py:LEGADO_SEM_PEDIDO | legado por nome de pasta |
| BAIXA | .agent/skills/discovery/SKILL.md | 5 perguntas x poucas por vez sem frase de ligacao |
| BAIXA | capabilities.json:2262 | nota do plano.py nao cita a checagem 9 |

## Verificacoes executadas (anti-fabricacao)

- critico: test_plano, plano verificar, test_regulado, test_capabilities PASS; grep sem chamador externo de plano.verificar
- autor: test_plano PASS apos ressalvas; check_rules_parity, test_consistency_closing, test_resposta_executiva PASS
