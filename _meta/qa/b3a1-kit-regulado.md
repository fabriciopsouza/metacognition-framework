# QA-evidence — b3a1-kit-regulado

- **Data:** 2026-09-26T06:20:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** docs/specs/b3-documentacao-regulada/spec.md (plano aprovado, criterios 1, 2, 4, 5, 6, 8) e fontes.md
- **RRC:** PASSA
- **Metodo-senior:** aplicado: cada achado reproduzido em copia isolada

## Substitui vereditos anteriores deste bloco

> **ATENCAO: este veredito substitui uma REPROVACAO.** Leia os antecedentes antes de tratar o bloco como aprovado.

- rodada 1 · 2026-09-26T05:10:00Z · **corrigir** · sha `464de0bd652b` · agentId `a88a6036673e80027`
  - cobria 19 caminho(s): tools/regulado.py, tools/test_regulado.py, tools/spec_fonte.py, tools/spec_unificar.py …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| CRITICA | tools/regulado.py:111 | requisito escrito com '*' em vez de '-' some do conjunto de requisitos e, sem teste, verificar devolve PASS |
| ALTA | tools/regulado.py:159-173 | Parte F vazia passa com impacto regulado; categoria 4 exige analise de risco |
| MEDIA | tools/agnostic-denylist.txt:20-22 | 'Instrucao Normativa' por extenso nao casa com nenhum padrao |
| MEDIA | tools/agnostic-denylist.txt:22 | falso positivo em ingles: IGNORECASE faz 'in 45/2020' casar com o padrao de IN |
| BAIXA | tools/regulado.py:45-47 | campo duplicado nao e acusado; o motor usa a primeira ocorrencia |
| BAIXA | tools/regulado.py | perfil futuro sem testes_obrigatorios_com_impacto generaliza o achado da Parte F vazia para zero requisitos, zero riscos e zero testes passando |

## Verificacoes executadas (anti-fabricacao)

- reproducao dos 6 cenarios da rodada 1 em copia isolada: todos acusados
- bypass novo: '- REQ-01 - ver REQ-02', REQ em tabela e citacao, IDs colados, bullet duplo -> sem achado
- (?-i:...) compila e funciona com o re.IGNORECASE do check_core_agnostic; denylist lida em utf-8; 28 regras compilam
- template preenchido passa em --planejamento; spec sem impacto passa
- test_regulado, test_core_agnostic, check_core_agnostic, test_spec_unico, test_rules_parity (16/16), test_marketing_claims, audit_enforcement -> PASS
