# QA-evidence — adr130-hook-wiring-coerente

- **Data:** 2026-09-29T14:37:37Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** pedido do dono 29/09/2026: corrigir na fonte o incidente de hook de 28/09 com os requisitos R1 a R5; default origin/main, branch so com opt-in
- **RRC:** PASSA
- **Metodo-senior:** aplicado: causa raiz em 3 falhas; canarios com home falso e repo git sintetico; 16 verificacoes de mutacao do autor e 10 do revisor por rodada

## Substitui vereditos anteriores deste bloco

- rodada 2 · 2026-09-29T14:37:11Z · **aprovar_com_ressalvas** · sha `bef74efe528d` · agentId `ad08c091ef0199801`
  - cobria 13 caminho(s): tools/hooks/resposta_executiva.py, tools/hooks/ensure-global-wiring.ps1, .claude/hooks/sync-global.ps1, bootstrap.ps1 …

## Problemas

_nenhum_

## Verificacoes executadas (anti-fabricacao)

- test_resposta_executiva PASS (R4a a R4j), --mutacoes PASS 16/16
- test_capabilities, test_consistency_closing, test_marketing_claims, check_core_agnostic, test_rules_parity, audit_enforcement, test_execution_report PASS
- revisor rodada 1: 6/10 mutacoes mortas; rodada 2: 9/10 (MI equivalente, coberta pela M11 do canario)
