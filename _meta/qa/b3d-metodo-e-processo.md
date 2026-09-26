# QA-evidence — b3d-metodo-e-processo

- **Data:** 2026-09-26T21:20:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** docs/specs/b3-documentacao-regulada/spec.md (REQ-13 a 15, criterios 14 a 16) e decisoes do dono de 26/09
- **RRC:** PASSA
- **Metodo-senior:** aplicado: renderizacao conferida no Edge; comandos do metodo conferidos

## Substitui vereditos anteriores deste bloco

> **ATENCAO: este veredito substitui uma REPROVACAO.** Leia os antecedentes antes de tratar o bloco como aprovado.

- rodada 1 · 2026-09-26T20:00:00Z · **corrigir** · sha `3e387610b3fa` · agentId `a49653d3ca8d24d01`
  - cobria 18 caminho(s): .agent/workflows/start-session.md, CAPABILITIES.md, CHANGELOG.md, CLAUDE.md …
- rodada 2 · 2026-09-26T20:40:00Z · **corrigir** · sha `3e387610b3fa` · agentId `aff590f529ac52cce`
  - cobria 18 caminho(s): .agent/workflows/start-session.md, CAPABILITIES.md, CHANGELOG.md, CLAUDE.md …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| CRITICA | tools/doc_intake.py:evidencia_registrar | manifesto corrompido derruba o registrar com traceback |
| ALTA | tools/desenho_processo.py:main | docx aberto no Word derruba a regravacao e deixa html/md/docx inconsistentes |
| MEDIA | tools/desenho_processo.py:_papeis | papel com caixa ou acento diferente vira raia separada |
| BAIXA | tools/doc_intake.py:evidencia_main | acentos corrompidos no console Windows |
| ALTA | tools/desenho_processo.py:main (fase de escrita) | falha ao escrever os novos gerados nao volta ao estado anterior |

## Verificacoes executadas (anti-fabricacao)

- falha na escrita reproduzida: tres anteriores intactos, sem .anterior, sem traceback
- primeira geracao com falha e docx nao gerado: pasta limpa, rc=1
- correcoes das rodadas 1 e 2 de pe
- 7 canarios PASS
