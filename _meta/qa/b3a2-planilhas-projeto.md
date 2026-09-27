# QA-evidence — b3a2-planilhas-projeto

- **Data:** 2026-09-27T01:30:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** docs/specs/b3-documentacao-regulada/spec.md (REQ-05, REQ-06, criterios 3a e 3b, T4) e decisoes do dono de 27/09/2026
- **RRC:** PASSA
- **Metodo-senior:** aplicado: modelos reais conferidos com openpyxl; cenarios de perda de resposta reproduzidos em copia; mutacoes

## Substitui vereditos anteriores deste bloco

- rodada 3 · 2026-09-27T01:30:00Z · **aprovar** · sha `None` · agentId `a8c92769abb3f04c3`
  - cobria 15 caminho(s): .agent/skills/discovery/SKILL.md, .claude/global/CLAUDE-global.md, CAPABILITIES.md, CHANGELOG.md …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/planilhas_projeto.py:respostas | resposta iniciada por '=' vira formula no Excel e some (leitura data_only) |
| MEDIA | tools/planilhas_projeto.py:_gravar_spec | arquivo unico em CRLF regravado em LF |
| MEDIA | tools/planilhas_projeto.py:_xl | texto literal <br> digitado pela area vira quebra de linha |
| MEDIA | tools/planilhas_projeto.py:gerar_tipo | recusa igual para causas distintas e sem saida (rotulo mudado; linha removida) |
| BAIXA | tools/planilhas_projeto.py:gerar_tipo (limpeza) | falha no os.remove final sem tratamento |
| MEDIA | tools/test_planilhas_projeto.py:(i) | nenhum caso com Nome e data invalido; mutacao de _nome_e_data sobrevivia |
| BAIXA | tools/planilhas_projeto.py:nova_rodada | --ids repetido gravava a linha duas vezes |

## Verificacoes executadas (anti-fabricacao)

- rodada 1: cenarios de perda de resposta (formula, CRLF, br literal, rotulo mudado, linha removida, falha no meio); 5/5 mutacoes mortas
- rodada 2: correcoes da rodada 1 reproduzidas e fechadas; 4/5 mutacoes mortas (a viva virou caso na rodada 3)
- rodada 3: mutacao de _nome_e_data morta pelo motivo certo; test_planilhas_projeto 68 verificacoes PASS
- canarios pedidos PASS: test_planilhas_projeto, test_spec_unico, test_desenho_processo, test_capabilities, check_core_agnostic, check_rules_parity, test_marketing_claims
- suite completa (autor): 94 PASS, 1 SKIP, 0 FAIL de 95
