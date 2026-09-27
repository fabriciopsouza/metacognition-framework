# QA-evidence — isolamento-fisico

- **Data:** 2026-09-27T17:05:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** docs/specs/isolamento-empresas-biblioteca/spec.md (D1, D2, D3, D5) e decisoes do dono de 27/09/2026 (todas a; forma b)
- **RRC:** PASSA
- **Metodo-senior:** aplicado: mudanca conferida byte a byte; mutacoes; biblioteca externa real lida

## Substitui vereditos anteriores deste bloco

- rodada 2 · 2026-09-27T15:00:00Z · **aprovar** · sha `None` · agentId `aede2a2d99a0f1c53`
  - cobria 26 caminho(s): .agent/skills/docops/SKILL.md, CAPABILITIES.md, CHANGELOG.md, capabilities.json …
- rodada 2 · 2026-09-27T15:00:00Z · **aprovar** · sha `5b43c887b044` · agentId `aede2a2d99a0f1c53`
  - cobria 26 caminho(s): .agent/skills/docops/SKILL.md, CAPABILITIES.md, CHANGELOG.md, capabilities.json …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/knowledge_catalog.py:cmd_recall | filtro D3 nao olhava o nome do arquivo do relatorio |
| ALTA | tools/conhecimento.py:verificar | biblioteca ausente dava PASS sem ler nada |
| MEDIA | tools/conhecimento.py:bibliotecas_externas | marcador aberto duas vezes |
| BAIXA | tools/test_conhecimento_isolamento.py | _hash sem teste direto de maiusculas |

## Verificacoes executadas (anti-fabricacao)

- rodada 1: canais de vazamento lidos no codigo; 2 ALTA e 1 MEDIA
- rodada 2: ALTAs fechadas com mutacao; 9 arquivos identicos byte a byte; indice e 27 achados iguais; README do pai; mutacoes 3/4 mortas (a viva virou caso)
- canarios PASS: test_conhecimento_isolamento, test_conhecimento, test_knowledge_catalog, test_capabilities, check_core_agnostic, test_marketing_claims
- suite completa (autor): 96 PASS, 1 SKIP, 0 FAIL de 97
- remocao dos 9 arquivos da natulab carimbada com OID nulo (gate-remocao-revisada)
