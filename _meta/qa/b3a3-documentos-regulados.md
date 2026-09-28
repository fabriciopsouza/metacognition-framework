# QA-evidence — b3a3-documentos-regulados

- **Data:** 2026-09-28T02:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** docs/specs/b3-documentacao-regulada/spec.md (REQ-09 a REQ-12, criterios 10 a 13) e decisoes do dono de 27 e 28/09/2026
- **RRC:** PASSA
- **Metodo-senior:** aplicado: criterios da spec reproduzidos; parsing adversarial; mutacoes

## Substitui vereditos anteriores deste bloco

- rodada 3 · 2026-09-28T02:00:00Z · **aprovar** · sha `None` · agentId `a4e1e3c6b8d6d9ded`
  - cobria 15 caminho(s): CAPABILITIES.md, CHANGELOG.md, capabilities.json, docs/adr/124-documentos-do-kit-regulado-gerados-pelo-perfil.md …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| CRITICA | tools/documento_regulado.py:montar | REQ com descricao vazia fazia o seguinte sumir da ERU |
| MEDIA | tools/documento_regulado.py:desvios | sinonimos de reprovado escapavam do desvio |
| MEDIA | tools/documento_regulado.py:requisitos | REQ repetido em silencio sem secao de testes |
| MEDIA | tools/regulado.py:duplicados_reqs | regra de repetido duplicada em dois arquivos |
| BAIXA | tools/documento_regulado.py:gerar | falha de gravacao virava traceback, sem caso de teste |

## Verificacoes executadas (anti-fabricacao)

- rodada 1: FAIL por REQ sumindo da ERU; corrigido na causa
- rodada 2: CRITICA e enum fechados com mutacao morta
- rodada 3: repetido e gravacao confirmados; mutacao morta
- suite completa (autor): 97 PASS, 1 SKIP, 0 FAIL de 98
