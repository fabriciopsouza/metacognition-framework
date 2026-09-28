# QA-evidence — b3b-perfil-farma-anvisa

- **Data:** 2026-09-28T17:16:43Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** docs/specs/b3-documentacao-regulada/spec.md (T6) aprovado pelo dono em 26/09/2026; escopo medicamentos pelo dono em 28/09/2026
- **RRC:** PASSA
- **Metodo-senior:** aplicado: citacoes do mapa conferidas contra o texto oficial baixado (IN 134, IN 138, RDC 658, Guia 33); 11 mutacoes no verificador do mapa, todas mortas; limite (forma, nao conteudo) declarado no ADR

## Problemas

_nenhum_

## Verificacoes executadas (anti-fabricacao)

- test_regulado (h) com 8 sabotagens, test_capabilities, test_consistency_closing, plano.py verificar, check_core_agnostic PASS
- todas as citacoes literais do mapa conferidas nos .txt oficiais, sem divergencia
- rodada 1: 5 mutacoes, 4 mortas (encoding corrigido depois); rodada 2: 6 mutacoes, todas mortas
