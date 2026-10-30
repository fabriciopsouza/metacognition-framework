# QA-evidence — adr-133-ux-design

- **Data:** 2026-10-30T16:25:23Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| MEDIA | tools/ux_gate.py desalinhados | r1: alinhamento acusava centralizado e inline |
| MEDIA | tools/ux_gate.py avaliar | r1: retrato malformado saia 1 com traceback |
| MEDIA | tools/ux_gate.py extrair | r1: erro do Playwright saia 1 |
| MEDIA | tools/test_ux_gate.py | r2: falha do Playwright sem canario |
| MEDIA | tools/ux_gate.py coluna | r2: caixa centralizada por flex ou margin auto acusada |
| MEDIA | tools/ux_gate.py centrado | r3: bloco de largura total em pai com padding saia da medida |
| BAIXA | tools/ux_gate.py centrado | r4: barra de rolagem do pai desloca o centro |
| BAIXA | tools/test_ux_gate.py | r4: faltavam casos de padding assimetrico e filho largo |

## Verificacoes executadas (anti-fabricacao)

- python tools/test_ux_gate.py
- python tools/test_core_no_vendor.py
- python tools/test_capabilities.py
- python tools/test_marketing_claims.py
- python tools/test_adr_changelog_sync.py
- sabotagem em copia: centrado contra a borda do pai reprova o teste (f)
