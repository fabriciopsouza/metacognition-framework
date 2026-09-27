# QA-evidence — isolamento-empresas-biblioteca

- **Data:** 2026-09-27T05:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** docs/specs/isolamento-empresas-biblioteca/spec.md (REQ-01 a REQ-05, criterios 1 a 8) e pedido do dono de 27/09/2026
- **RRC:** PASSA
- **Metodo-senior:** aplicado: problemas reproduzidos com duas empresas sinteticas; canais de vazamento testados; mutacoes

## Substitui vereditos anteriores deste bloco

- rodada 2 · 2026-09-27T05:00:00Z · **aprovar** · sha `None` · agentId `addd6d7a6db4e5278`
  - cobria 22 caminho(s): .agent/skills/discovery/SKILL.md, .agent/skills/docops/SKILL.md, .claude/global/CLAUDE-global.md, CAPABILITIES.md …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | docs/_private/conhecimento/conhecimento.json | versao de sistema de empresa no arquivo global |
| ALTA | tools/conhecimento.py:carregar | pasta com maiuscula dava falso PASS |
| MEDIA | tools/conhecimento.py:_verificar_indice | trabalho aberto citava repositorio de outra empresa |
| MEDIA | tools/test_conhecimento_isolamento.py | sem caso alfa/alfa2 |
| MEDIA | tools/conhecimento.py:identificadores_de_empresa | sigla MM reprovava saber puro |
| MEDIA | docs/adr/120 Limites | codigo de 3 letras sem digito nao protegido, limite nao declarado |
| BAIXA | docs/adr/120 Limites | cfg_do_escopo com pasta maiuscula em FS case-sensitive |

## Verificacoes executadas (anti-fabricacao)

- plano: afirmacoes reproduzidas; aceite RATIFICADO-COM-AJUSTES
- codigo 1: vazamento testado em recall, verificar, vencidos, mensagens, PROIBIDOS, indice, trabalhos, ../ e alfa/alfa2; nenhum
- codigo 2: 3 mutacoes das correcoes e a mutacao declarada em capabilities.json, mortas
- canarios PASS: test_conhecimento_isolamento, test_conhecimento, test_knowledge_catalog, test_capabilities, check_core_agnostic, check_rules_parity, test_marketing_claims, test_spec_unico
- suite completa (autor): 95 PASS, 1 SKIP, 0 FAIL de 96
