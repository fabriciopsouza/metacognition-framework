# QA-evidence — adr-133-paineis

- **Data:** 2026-10-31T02:40:17Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/ux_gate.py tamanhos_diferentes | r1: largura comparada em flex com quebra (chip e link de navegacao acusavam) |
| MEDIA | tools/ux_gate.py grupos_de_tipo | r1: icone svg sem classe medido como grafico |
| MEDIA | tools/ux_gate.py e ADR-133 | r1: cartoes em flex sem quebra fora da medida |
| MEDIA | tools/ux_gate.py tamanhos_diferentes | r2: texto de cartoes diferentes comparado como irmao (uniao entre primos valia para toda tag; mesma familia da r1, falso positivo por escopo) |
| MEDIA | docs/adr/133-ux-design-perfis-revisao-gate.md linha 72 | r3: byte de controle no caminho da fonte da emenda |
| BAIXA | .agent/skills/ux-design/SKILL.md regra 4 | r3: 'na linha da referencia' e leitura do autor; 'sem seta' vem do traco 5 |
| BAIXA | tools/ux_gate.py | r4: grid 2fr 1fr com mesma classe acusa (auto/auto); extrator nao exercido em navegador (Playwright ausente) |

## Verificacoes executadas (anti-fabricacao)

- python tools/test_ux_gate.py: PASS
- python tools/audit_enforcement.py --provar --id ux-gate: PROVADO
- sabotagem em copia (scratchpad mutar.py): 23 de 23 mutantes da medida nova mortos
- python tools/test_capabilities.py: PASS (pela QA r4)
- varredura de caractere de controle nas linhas adicionadas da branch: nenhum
- fidelidade das regras 1 a 7 a calibracao-dono.md, secao Calibracao de paineis (QA r3 e r4)
