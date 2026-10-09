# QA-evidence — adr128-perfil-anp-combustiveis

- **Data:** 2026-09-29T21:38:34Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** decisoes do dono D1-D4 de 28/09/2026 registradas no ADR-128; D5 (export publico) pendente e registrada
- **RRC:** PASSA
- **Metodo-senior:** aplicado: leitura primaria das normas, mapa peca->norma com marca de confianca, marcas rebaixadas a INFERIDO onde a copia nao tem URL de origem

## Problemas

_nenhum_

## Verificacoes executadas (anti-fabricacao)

- test_regulado, test_plano, test_knowledge_catalog, test_capabilities, test_consistency_closing, check_core_agnostic, audit_enforcement PASS; regulado.py mapa PASS
- rodada 5: 20/25 mutacoes mortas; rodada 6: 12/13; rodada 7: 5/9 (sobreviventes sem efeito de seguranca, 3 mortas depois pelo teste direto dos metadados)
